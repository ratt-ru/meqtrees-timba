//# Solver.cc: Base class for an expression node
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$


// Needed for Aips++ array and matrix assignments for DMI
#define AIPSPP_HOOKS

#include <MEQ/Request.h>
#include <MEQ/Vells.h>
#include <MEQ/Function.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Forest.h>
#include <MeqNodes/Solver.h>
#include <MeqNodes/Condeq.h>
#include <MeqNodes/ParmTable.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/Arrays/Matrix.h>
#include <casa/Arrays/Vector.h>
#include <DMI/List.h>

#include <iostream>

using namespace std;

using namespace casa;

namespace Meq {

InitDebugContext(Solver,"MeqSolver");

const HIID FTileSize = AidTile|AidSize;

const HIID FSolverResult = AidSolver|AidResult;
const HIID FIncrementalSolutions = AidIncremental|AidSolutions;

const HIID FIterationSymdeps = AidIteration|AidSymdeps;
const HIID FIterationDependMask = AidIteration|AidDepend|AidMask;

const HIID FDebugLevel = AidDebug|AidLevel;
const HIID FIterations = AidIterations;
const HIID FConverged  = AidConverged;

const HIID FMetricsArray  = AidMetrics|AidArray;
const HIID FDebugArray  = AidDebug|AidArray;

#if LOFAR_DEBUG
const int DefaultDebugLevel = 100;
#else
const int DefaultDebugLevel = 0;
#endif

//##ModelId=400E53550260
Solver::Solver()
: eval_mode_(1),
  flag_mask_        (-1),
  do_save_funklets_ (false),
  do_last_update_   (false),
  use_svd_          (true),
  max_num_iter_     (3),
  min_epsilon_      (0),
  debug_lvl_        (DefaultDebugLevel),
  parm_group_       (AidParm),
  solver_           (1),
  strides_          (0)
{
  // set Solver dependencies
  iter_symdeps_.assign(1,FIteration);
  const HIID symdeps[] = { FDomain,FResolution,FDataset,FIteration };
  setKnownSymDeps(symdeps,4);
  const HIID symdeps1[] = { FDomain,FResolution,FDataset };
  setActiveSymDeps(symdeps1,3);
  // enable multithreading
  enableMultiThreadedPolling();
}

//##ModelId=400E53550261
Solver::~Solver()
{
  if( strides_ )
    delete [] strides_;
}

//##ModelId=400E53550263
TypeId Solver::objectType() const
{
  return TpMeqSolver;
}







// do nothing here -- we'll do it manually in getResult()
//##ModelId=400E5355026B
int Solver::pollChildren (Result::Ref &resref,const Request &request)
{
  // block off spid discovery requests completely.
  // For all evaluation requests, we handle child polling for 
  // them separately in getResult().
  if( request.requestType() == RequestType::DISCOVER_SPIDS ||
      request.evalMode() >= 0 )
    return 0;
  // Other requests passed on to the children as is. 
  // (These never make it to our getResult())
  else
    return Node::pollChildren(resref,request);
}











int Solver::populateSpidMap (const DMI::Record &spidmap_rec,const Cells &cells)
{
  parm_uks_.clear();
  spids_.clear();
  // convert spid map record into internal spid map, and count up the unknowns
  for( DMI::Record::const_iterator iter = spidmap_rec.begin(); 
      iter != spidmap_rec.end(); iter++ )
  {
    // each spidmap entry is expected to be a record
    const DMI::Record &rec = iter.ref().as<DMI::Record>();
        VellSet::SpidType spid = iter.id()[0].id();  // spid is first element of HIID
    // insert entry into spid table
    SpidInfo & spi = spids_[spid];     
    spi.uk_index  = num_unknowns_;
    spi.nuk = 1;
    // OK, figure out tiling
    memset(spi.tile_size,0,sizeof(spi.tile_size));
    int sz;
    const int *ptiles = rec[FTileSize].as_po<int>(sz);
    if( ptiles )
    {
      int rank = std::min(sz,Axis::MaxAxis);
      int stride = 1;
      for( int i=rank-1; i>=0; i-- )
      {
        int tsz = spi.tile_size[i] = ptiles[i];
        spi.tile_stride[i] = stride;
        // is this axis tiled by the spid?
        if( tsz )
        {
          int nc = cells.ncells(i);
          int ntiles = nc/tsz + ((nc%tsz)?1:0);     // a minimum of 1 tile always
          spi.nuk *= ntiles;
          stride *= ntiles;
        }
      }
    }
    // increment count of unknowns
    num_unknowns_ += spi.nuk;
    // add unknown's indices to map for this nodeindex
    ParmUkInfo & pui = parm_uks_[rec[FNodeIndex].as<int>()];
    pui.spidset[spid] = std::pair<int,int>(spi.uk_index,spi.uk_index+spi.nuk);
    pui.nuk += spi.nuk;
  }
  return num_unknowns_;
}













// This is a helper function for fillEquations(). Note that this function 
// encapsulates the only difference in the code between the double
// and the complex case. This allows us to have a single templated 
// definition of fillEquations() below which works for both cases.
template<typename T>
inline void Solver::fillEqVectors (int npert,int uk_index[],
      const T &diff,const std::vector<Vells::ConstStridedIterator<T> > &deriv_iter)
{
  // fill vectors of derivatives for each unknown 
  for( int i=0; i<npert; i++ )
    deriv_real_ [i] = *deriv_iter[i];
  if( Debug(4) )
  {
    cdebug(4)<<"equation: ";
    for( int i=0; i<npert; i++ )
      ::Debug::getDebugStream()<<uk_index[i]<<":"<<deriv_real_[i]<<" "; 
    ::Debug::getDebugStream()<<" -> "<<diff<<endl;
  }
  // add equation to solver
  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
  solver_.makeNorm(npert,uk_index,&deriv_real_[0],1.,diff);
  num_equations_++;
}













// Specialization for complex case: each value produces two equations
template<>
inline void Solver::fillEqVectors (int npert,int uk_index[],
      const dcomplex &diff,const std::vector<Vells::ConstStridedIterator<dcomplex> > &deriv_iter)
{
  // fill vectors of derivatives for each unknown 
  for( int i=0; i<npert; i++ )
  {
    deriv_real_[i] = (*deriv_iter[i]).real();
    deriv_imag_[i] = (*deriv_iter[i]).imag();
  }
  if( Debug(4) )
  {
    cdebug(4)<<"equation: ";
    for( int i=0; i<npert; i++ )
    { 
      ::Debug::getDebugStream()<<uk_index[i]<<":"<<deriv_real_[i]<<","<<deriv_imag_[i]<<" "; 
    }
    ::Debug::getDebugStream()<<" -> "<<diff<<endl;
  }
  // add equation to solver
  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
  solver_.makeNorm(npert,uk_index,&deriv_real_[0],1.,diff.real());
  num_equations_++;
  solver_.makeNorm(npert,uk_index,&deriv_imag_[0],1.,diff.imag());
  num_equations_++;
}










template<typename T>
void Solver::fillEquations (const VellSet &vs)
{
  int npert = vs.numSpids();
  FailWhen(npert>num_spids_,ssprintf("child %d returned %d spids, but only "
            "%d were reported during spid discovery",cur_child_,npert,num_spids_));
  const Vells &diffval = vs.getValue();

  // ok, this is where it gets hairy. The main val and each pertval 
  // could, in principle, have a different set of variability axes 
  // (that is, their shape along any axis can be equal to 1, to indicate
  // no variability). This is the same problem we deal with in Vells 
  // math, only on a grander scale, since here N+2 Vells have to 
  // be iterated over simultaneously (1 driving term, N derivatives,
  // 1 flag vells). Fortunately Vells math provides some help here
  // in the form of strided iterators
  SpidInfo *pspi[npert];    // spid map for each derivative looked up in advance
  Vells::Shape outshape;          // output shape: superset of input shapes
  // fill in shape arrays for computeStrides() below
  const Vells::Shape * shapes[npert+2];
  int uk_index[npert];            // index of current unknown per each 
  // derivative (since we may have multiple unknowns per spid due to tiling,
  // we keep track of the current one when filling equations)
  shapes[0] = &( diffval.shape() );
  shapes[1] = &( diffval.flagShape() ); // returns null shape if no flags
  int j=2;
  // go over derivatives, find spids in map, fill in shapes
  for( int i=0; i<npert; i++,j++ )
  {
    // find spid in map, and save pointer to map entry
    VellSet::SpidType spid = vs.getSpid(i);
    SpidMap::iterator iter = spids_.find(vs.getSpid(i));
    FailWhen(iter == spids_.end(),ssprintf("child %d returned spid %d that was "
            "not reported during spid discovery",cur_child_,spid));
    SpidInfo &spi = iter->second;
    pspi[i] = &spi;
    // init various indices
    uk_index[i] = spi.uk_index;
    for( int ii=0; ii<Axis::MaxAxis; ii++ )
    {
      spi.tile_index[ii] = 0;
      spi.tile_uk0[ii] = spi.uk_index;
    }
    // get shape of derivative
    shapes[j] = &( vs.getPerturbedValue(i).shape() );
  }
  // compute output shape (the union of all input shapes), and
  // strides for all vells 
  Vells::computeStrides(outshape,strides_,npert+2,shapes,"Solver::getResult");
  int outrank = outshape.size();
  // create strided iterators for all vells
  Vells::ConstStridedIterator<T> diff_iter(diffval,strides_[0]);
  Vells::ConstStridedFlagIterator flag_iter(diffval,strides_[1]);
  std::vector<Vells::ConstStridedIterator<T> > deriv_iter(npert);
  j=2;
  for( int i=0; i<npert; i++,j++ )
    deriv_iter[i] = Vells::ConstStridedIterator<T>(vs.getPerturbedValue(i),strides_[j]);
  // create counter for output shape
  Vells::DimCounter counter(outshape);
  // now start generating equations. repeat while counter is valid
  // (we break out below, when incrementing the counter)
  while( true )
  {
    // fill equations only if unflagged...
    if( !(*flag_iter&flag_mask_) )
      fillEqVectors(npert,uk_index,*diff_iter,deriv_iter);
    // increment counter and all iterators
    int ndim = counter.incr(); 
    if( !ndim )    // break out when counter is finished
      break;
    diff_iter.incr(ndim);
    flag_iter.incr(ndim);
    for( int ipert=0; ipert<npert; ipert++ )
    {
      deriv_iter[ipert].incr(ndim);
      // if this is a tiled spid, we need to figure out whether we
      // have changed tiles, and what the new uk_index is
      SpidInfo &spi = *pspi[ipert];
      if( spi.nuk > 1 )
      {
        // ndim tells us how many dimensions we have advanced over
        // (with the last dimension iterating the fastest)
        // That is, index N-ndim has been incremented, while indices
        // N-ndim+1 ... N-1 have been reset to 0. Work out our tile
        // numbers appropriately
        int idim = outrank - ndim;  // idim=N-ndim, the incremented dimension
        // Reset unknown index for this dimension to beginning of slice.
        // tile_uki0[i] is the index of the start of the slice for the
        // current values of tile indices 0...i-1.
        int uk0 = spi.tile_uk0[idim];
        if( spi.tile_size[idim] )
        {
          int ti = spi.tile_index[idim] = counter.counter(idim) / spi.tile_size[idim];
          // work out start of slice for indices 0...idim-1,idim
          uk0 += ti * spi.tile_stride[idim];
        }
        // this is the new uk_index then
        uk_index[ipert] = uk0;
        // reset the remaining tile indices to 0, and update
        // their slice starting points
        for( idim++; idim < outrank; idim++ )
        {
          spi.tile_uk0[idim] = uk0;
          spi.tile_index[idim] = 0;
        }
      }
    }
  }
}        






// helper method to flatten a list of records into an array
template<class T>
ObjRef flattenScalarList (const DMI::List &list,const HIID &field)
{
  // presize the array to list size
  LoShape shape(list.size());
  DMI::NumArray * parr = new DMI::NumArray(typeIdOf(T),shape);
  ObjRef res(parr);
  blitz::Array<T,1> &arr = parr->getArray<T,1>();
  // go through list and fill with data
  DMI::List::const_iterator iter = list.begin();
  for( int n=0; iter != list.end(); iter++,n++ )
    arr(n) = iter->as<DMI::Record>()[field].as<T>(0);
  return res;
}

template<class T,int N>
ObjRef flattenArrayList (const DMI::List &list,const HIID &field)
{
  // figure out maximum shape of output array
  blitz::TinyVector<int,N> maxshape(1);
  DMI::List::const_iterator iter = list.begin();
  // go through list and compare shapes
  for( ; iter != list.end(); iter++ )
  {
    DMI::Record::Hook harr(iter->as<DMI::Record>(),field);
    if( harr.exists() )
    {
      const LoShape &shp = harr.as<DMI::NumArray>().shape();
      FailWhen(shp.size() != N,"array rank mismatch when flattening list for field "+field.toString());
      for( int i=0; i<N; i++ )
        maxshape[i] = std::max(maxshape[i],shp[i]);
    }
  }
  // preallocate array
  LoShape outshape;
  outshape.resize(N+1);
  outshape[0] = list.size();
  for( int i=0; i<N; i++ )
    outshape[i+1] = maxshape[i];
  DMI::NumArray * parr = new DMI::NumArray(typeIdOf(T),outshape);
  ObjRef res(parr);
  T * pdata = static_cast<T*>(parr->getDataPtr());
  int stride = blitz::product(maxshape);
  // go through list again and fill with data
  for( iter = list.begin(); iter != list.end(); iter++,pdata+=stride )
  {
    DMI::Record::Hook harr(iter->as<DMI::Record>(),field);
    if( harr.exists() )
    {
      const blitz::Array<T,N> & subarr = harr.as<DMI::NumArray>().getConstArray<T,N>();
      // get slice of output to write to
      blitz::Array<T,N> outslice(pdata,maxshape,blitz::neverDeleteData);
      // subdomain of output to write to (in case this array is smaller)
      blitz::RectDomain<N> dom(subarr.lbound(),subarr.ubound());
      outslice(dom) = subarr;
    }
  }
  return res;
}



// Get the result for the given request.
//##ModelId=400E53550270
int Solver::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &,
                       const Request &request, bool newreq)
{
  // Use single derivative by default, or a higher mode if specified in request
  AtomicID rqtype = RequestType::EVAL_SINGLE;
  if( std::max(eval_mode_,request.evalMode()) > 1 )
    rqtype = RequestType::EVAL_DOUBLE;
  // The result has no planes, all solver information is in extra fields
  Result& result = resref <<= new Result(0);
  DMI::Record &solveResult = result[FSolverResult] <<= new DMI::Record;
  // Keep a copy of the solver result in the state record, so that per-iteration metrics
  // can be tracked while debugging
  wstate()[FSolverResult].replace() <<= &solveResult;
  DMI::List & metricsList = solveResult[FMetrics] <<= new DMI::List;
  DMI::List * pDebugList = 0;
  if( debug_lvl_>0 )
    solveResult["Debug"] <<= pDebugList = new DMI::List;
  // get the request ID -- we're going to be incrementing the iteration index
  RequestId rqid = request.id();
  RqId::setSubId(rqid,iter_depmask_,0);      // current ID starts at 0
  RequestType::setType(rqid,rqtype);
  RequestId next_rqid = rqid;  
  RqId::incrSubId(next_rqid,iter_depmask_);  // next ID is iteration 1
  // Now, generate a request to set parms solvable and discover spids
  // (a) setup our solvables
  // (b) do spid discovery
  Request::Ref reqref;
  Request &req = reqref <<= new Request(request.cells(),rqid);
  req.setRequestType(RequestType::DISCOVER_SPIDS);
  // rider of original request gets sent up along with it
  req.copyRider(request);
  // do we have a solvables spec in our state record?
  const DMI::Record *solvables = state()[FSolvable].as_po<DMI::Record>();
  if( solvables )
  {
    DMI::Record& rider = Rider::getRider(reqref);
    rider[parm_group_].replace() <<= wstate()[FSolvable].as_wp<DMI::Record>();
  } 
  else 
  {
    // no solvables specified -- clear the group record, and assume parms have been
    // set solvable externally somehow
    Rider::getGroupRec(reqref,parm_group_,Rider::NEW_GROUPREC);
  }
  reqref().validateRider();
  // send up request to figure out spids. We can poll syncronously since there's
  // nothing for us to do until all children have returned
  timers_.getresult.stop();
  int retcode = Node::pollChildren(resref,*reqref);
  timers_.getresult.start();
  if( retcode&(RES_FAIL|RES_WAIT) )
    return retcode;
  // Node's standard discoverSpids() implementation merges all child spids together
  // into a result object. This is exactly what we need here
  Result::Ref tmpres;
  Node::discoverSpids(tmpres,child_results_,req);
  // discard child results
  for( uint i=0; i<child_results_.size(); i++ ){
    child_results_[i].detach();
  }
  // ****   ALL SPIDS DISCOVERED   ***
  // ok, now we should have a spid map
  num_unknowns_ = 0;
  if( tmpres.valid() )
  {
    const DMI::Record * pspid_map = tmpres[FSpidMap].as_po<DMI::Record>();
    if( pspid_map )
    {
      // insert a copy of spid map record into the solver result
      solveResult[FSpidMap].replace() <<= pspid_map;
      // populate our map from the record
      populateSpidMap(*pspid_map,request.cells());
    }
  }
  if( !num_unknowns_ )
  {
    // no unknowns/spids discovered, so may as well fail...
    Throw("spid discovery did not return any solvable parameters");
  }
  num_spids_ = spids_.size();
  {
  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
  solver_.set(num_unknowns_);
  }
  cdebug(2)<<"solver initialized for "<<num_unknowns_<<" unknowns\n";
  
  // resize temporaries used in fillEquations()
  deriv_real_.resize(num_unknowns_);
  deriv_imag_.resize(num_unknowns_);
  // ISO C++ won't allow a vector of Strides, hence this old-style kludge
  if( strides_ )
    delete [] strides_;
  strides_ = new Vells::Strides[num_spids_+2];
  // and other stuff used during solution
  Vector<double> solution(num_unknowns_);   // solution vector from solver
  
  // matrix of incremental solutions -- allocate directly in solver
  // result so that it stays visible in our state record (handy
  // when debugging trees, for instance)
  DMI::NumArray & allSolNA = solveResult[FIncrementalSolutions] 
        <<= new DMI::NumArray(Tpdouble,LoShape(max_num_iter_,num_unknowns_));
  LoMat_double & incr_solutions = allSolNA.getArray<double,2>();
  
  // OK, now create the "real" request object. This will be modified from 
  // iteration to iteration, so we keep it attached to reqref and rely on COW
  reqref <<= new Request(request.cells());
  int  step;
  bool converged=false;
  for( step=0; step < max_num_iter_ && !converged; step++ ) 
  {
    // increment the solve-dependent parts of the request ID
    rqid = next_rqid;
    RqId::incrSubId(next_rqid,iter_depmask_);
    // set request Ids in the request object
    reqref().setId(rqid);
    reqref().setNextId(next_rqid);
    num_equations_ = 0;
    // start async child poll
    timers_.getresult.stop();
    setExecState(CS_ES_POLLING);
    startAsyncPoll(*reqref);
    int rescode;
    Result::Ref child_res;
    // wait for child results until all have been polled (await will return -1 when this is the case)
    std::list<Result::Ref> child_fails;  // any fails accumulated here
    while( (cur_child_ = awaitChildResult(rescode,child_res,*reqref)) >= 0 )
    {
      // tell child to hold cache if it doesn't depend on iteration
      getChild(cur_child_).holdCache(!(rescode&iter_depmask_));
      // has the child failed? 
      if( rescode&RES_FAIL )
      {
        child_fails.push_back(child_res);
        continue;
      }
      // has the child asked us to wait?
      if( rescode&RES_WAIT )  // this never happens, so ok to return for now
        return rescode;
      // treat each vellset in the result independently
      for( int ivs = 0; ivs < child_res->numVellSets(); ivs++ )
      {
        const VellSet &vs = child_res->vellSet(ivs);
        // ignore failed or null vellsets
        if( vs.isFail() || vs.isNull() )
          continue;
        timers_.getresult.start();
        if( vs.getValue().isReal() )
          fillEquations<double>(vs);
        else
          fillEquations<dcomplex>(vs);
        timers_.getresult.stop();
      }
    } // end of while loop over children
    setExecState(CS_ES_EVALUATING);
    timers_.getresult.start();
    FailWhen(!num_equations_,"no equations were generated");
    cdebug(4)<<"accumulated "<<num_equations_<<" equations\n";
    // Solve the equation.
    DMI::Record * pSolRec = new DMI::Record;
    metricsList.addBack(pSolRec);
    DMI::Record * pDebug = 0;
    if( pDebugList ){
      pDebugList->addBack(pDebug = new DMI::Record);
    }

    // ****   CALL SOLVE AND CHECK CONVERGENCE  ****
    //    double fit = solve(solution,reqref,*pSolRec,pDebug,do_save_funklets_ && step == max_num_iter_-1);
    
    //always add save_funklets command, let parm decide (only save if converged)
    double fit = solve(solution,reqref,*pSolRec,pDebug,do_save_funklets_);
    

    converged = ((abs(fit) <= min_epsilon_) && fit <= 0.0);
    
    // copy solutions vector to allSolutions row
    incr_solutions(step,LoRange::all()) = B2A::refAipsToBlitz<double,1>(solution);
  } // end of FOR loop over solver iterations
  // send up one final update if needed
  if( do_last_update_ && (step == max_num_iter_ || converged))
  {
    // reqref will have already been populated with updates by solve() above.
    // However, we want to clear out the cells to avoid re-evaluation, so
    // we create another request object here and copy over the rider
    Request::Ref lastref;
    Request &lastreq = lastref <<= new Request;
    lastreq.setId(next_rqid);
    lastreq.setRequestType(RequestType::PARM_UPDATE);
    // note that this is not a service request, since it doesn't imply 
    // any state changes
    lastreq.copyRider(*reqref);
    lastreq.setNextId(request.nextId());
    ParmTable::lockTables();
    timers_.getresult.stop();
    Node::pollChildren(resref, lastreq);
    timers_.getresult.start();
    ParmTable::unlockTables();
  }
  solveResult[FConverged] = converged;
  solveResult[FIterations]= step;
  // if we broke out of the loop because of some other criterion, we need
  // to crop the incremental solutions matrix to [0:step-1,*]
  if( step < max_num_iter_ )
  {
    // create new array and copy subarray of incremental solutions into it
    DMI::NumArray::Ref arr_ref;
    arr_ref <<= new NumArray(Tpdouble,LoShape(step,num_unknowns_));
    arr_ref().getArray<double,2>() = incr_solutions(LoRange(0,step),LoRange::all());
    // replace incr_solutions in solver result
    solveResult[FIncrementalSolutions].replace() <<= arr_ref;
  }
  // finally, to make life easier for DataCollect and HistoryCollect nodes, reformat all
  // metrics and debug fields from lists into arrays, where the first axis is the number of
  // iterations
  DMI::Record::Ref metrics_ref;
  DMI::Record &metrics = metrics_ref <<= new DMI::Record;
  metrics[FRank]   = flattenScalarList<int>(metricsList,FRank);
  metrics[FFit]    = flattenScalarList<double>(metricsList,FFit);
  metrics[FErrors] = flattenArrayList<double,1>(metricsList,FErrors);
  metrics[FFlag]   = flattenScalarList<bool>(metricsList,FFlag);
  metrics[FMu]     = flattenScalarList<double>(metricsList,FMu);
  metrics[FStdDev] = flattenScalarList<double>(metricsList,FStdDev);
  solveResult[FMetricsArray] = metrics_ref;
  
  if( pDebugList )
  {
    DMI::Record::Ref debug_ref;
    DMI::Record &dbgrec = debug_ref <<= new DMI::Record;
    dbgrec["$nEq"] = flattenArrayList<double,2>(*pDebugList,"$nEq");
    dbgrec["$known"] = flattenArrayList<double,1>(*pDebugList,"$known");
    dbgrec["$constr"] = flattenArrayList<double,2>(*pDebugList,"$constr");
    dbgrec["$er"] = flattenArrayList<double,1>(*pDebugList,"$er");
    dbgrec["$piv"] = flattenArrayList<int,1>(*pDebugList,"$piv");
    dbgrec["$sEq"] = flattenArrayList<double,2>(*pDebugList,"$sEq");
    dbgrec["$sol"] = flattenArrayList<double,1>(*pDebugList,"$sol");
    dbgrec["$prec"] = flattenScalarList<double>(*pDebugList,"$prec");
    dbgrec["$nonlin"] = flattenScalarList<double>(*pDebugList,"$nonlin");
    solveResult[FDebugArray] = debug_ref;
  }
  
  // clear state dependencies possibly introduced by parms
  has_state_dep_ = false;
  // return flag to indicate result is independent of request type
  // (i.e. return result from cache for all requests regardless of
  // type)
  return Node::RES_IGNORE_TYPE;
}










// helper function to copy a triangular matrix (from solver object)
// to a proper square matrix
template<class T>
static DMI::NumArray::Ref triMatrix (T *tridata,int n)
{
  DMI::NumArray::Ref out(new DMI::NumArray(typeIdOf(T),LoShape(n,n)));
  blitz::Array<T,2> & arr = out().getArray<T,2>();
  for( int row=0; row<n; row++ )
  {
    int len = n-row;
    arr(row,LoRange(0,len-1)) = blitz::Array<T,1>(tridata,LoShape1(len),blitz::neverDeleteData);
    tridata += len;
  }
  return out;
}












//====================>>>  Solver::solve  <<<====================

double Solver::solve (Vector<double>& solution,Request::Ref &reqref,
                    DMI::Record& solRec,DMI::Record * pDebugRec,
                    bool saveFunklets)
{
  reqref().clearRider();
  solution = 0;
  // It looks as if in LSQ solveLoop and getCovariance
  // interact badly (maybe both doing an invert).
  // So make a copy to separate them.
  uint rank;
  double fit;
  Matrix<double> covar;
  Vector<double> errors;

  // Make a copy of the solver for the actual solve.
  // This is needed because the solver does in-place transformations.
  ////  FitLSQ solver = solver_;
  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
  bool solFlag = solver_.solveLoop (fit, rank, solution, use_svd_);

  // {
  LSQaips tmpSolver(solver_);
    // both of these calls produce SEGV in certain situations; commented out until
    // Wim or Ger fixes it
    //cdebug(1) << "result_covar = solver_.getCovariance (covar);" << endl;
    //bool result_covar = solver_.getCovariance (covar);
   //cdebug(1) << "result_errors = solver_.getErrors (errors);" << endl;
   bool result_errors = tmpSolver.getErrors (errors);
    //cdebug(1) << "result_errors = " << result_errors << endl;
 // }
  
  
  cdebug(4)<<"solution after: " << solution << ", rank " << rank << endl;
  // Put the statistics in a record the result.
  solRec[FRank]   = int(rank);
  solRec[FFit]    = fit;
  solRec[FErrors] = errors;
  //solRec[FCoVar ] = covar; 
  solRec[FFlag]   = solFlag; 
  solRec[FMu]     = solver_.getWeightedSD();
  solRec[FStdDev] = solver_.getSD();
  //  solRec[FChi   ] = solver_.getChi());
  // Put debug info
  if( pDebugRec )
  {
    DMI::Record &dbg = *pDebugRec;
    uint nun,np,ncon,ner,rank;
    double * nEq,*known,*constr,*er,*sEq,*sol,prec,nonlin;
    uint * piv;
    solver_.debugIt(nun,np,ncon,ner,rank,nEq,known,constr,er,piv, sEq,sol,prec,nonlin);
    if( nEq )
      dbg["$nEq"] = triMatrix(nEq,nun);
    dbg["$known"] = LoVec_double(known,LoShape1(np),blitz::neverDeleteData);
    if( ncon )
      dbg["$constr"] = LoMat_double(constr,LoShape2(ncon,nun),blitz::neverDeleteData,blitz::ColumnMajorArray<2>());
    dbg["$er"] = LoVec_double(er,LoShape1(ner),blitz::neverDeleteData);
    dbg["$piv"] = LoVec_int(reinterpret_cast<int*>(piv),LoShape1(np),blitz::neverDeleteData);
    if( sEq )
      dbg["$sEq"] = triMatrix(sEq,np);
    dbg["$sol"] = LoVec_double(sol,LoShape1(np),blitz::neverDeleteData);
    dbg["$prec"] = prec;
    dbg["$nonlin"] = nonlin;
  }


  //check if converged;
  bool converged = ((abs(fit) <= min_epsilon_) && fit <= 0.0);
  
  // Put the solution in the rider:
  //    [FRider][<parm_group>][CommandByNodeIndex][<parmid>]
  // will contain a DMI::Record for each parm 
  DMI::Record& grouprec = Rider::getCmdRec_ByNodeIndex(reqref,parm_group_,
                                                       Rider::NEW_GROUPREC);
  
  for( ParmUkMap::const_iterator iparm = parm_uks_.begin(); 
       iparm != parm_uks_.end(); iparm++ )
  {
    int nodeindex = iparm->first;
    // create command record for this parm
    DMI::Record & cmdrec = grouprec[nodeindex] <<= new DMI::Record;
    const ParmUkInfo & pui = iparm->second;
    // create vector of updates and get pointer to its data
    DMI::NumArray &arr = cmdrec[FUpdateValues] <<= new DMI::NumArray(Tpdouble,LoShape(pui.nuk));
    double *pupd = static_cast<double*>(arr.getDataPtr());
    int j=0;
    // fill updates for this node's spids, by fetching them from the solution 
    // vector via the spid set indices
    for( SpidSet::const_iterator ii = pui.spidset.begin(); ii != pui.spidset.end(); ii++ )
    {
      const std::pair<int,int> & uks = ii->second;
      for( int iu = uks.first; iu < uks.second; iu++ )
        pupd[j++] = solution(iu);
    }
    // add save command if requested
    if( saveFunklets  && converged)
      cmdrec[FSaveFunklets] = true;
    cmdrec[FConverged] = converged;

  }
  // make sure the request rider is validated
  reqref().validateRider();
  ParmTable::unlockTables();
  return fit;
}











//##ModelId=400E53550267
void Solver::setStateImpl (DMI::Record::Ref & newst,bool initializing)
{
  Node::setStateImpl(newst,initializing);
  // get the parm group
  newst[FParmGroup].get(parm_group_,initializing);
  // get symdeps for iteration and solution
  // recompute depmasks if active sysdeps change
  if( newst[FIterationSymdeps].get_vector(iter_symdeps_,initializing) || initializing )
    wstate()[FIterationDependMask] = iter_depmask_ = computeDependMask(iter_symdeps_);
  // now reset the dependency mask if specified; this will override
  // possible modifications made above
  newst[FIterationDependMask].get(iter_depmask_,initializing);

  // get eval mode
  newst[FEvalMode].get(eval_mode_,initializing);
  // get debug flag
  newst[FDebugLevel].get(debug_lvl_,initializing);
  // get other solver parameters
  newst[FFlagMask].get(flag_mask_,initializing);
  newst[FSaveFunklets].get(do_save_funklets_,initializing);  
  newst[FLastUpdate].get(do_last_update_,initializing);  
  newst[FUseSVD].get(use_svd_,initializing);  
  newst[FNumIter].get(max_num_iter_,initializing);  
  newst[FEpsilon].get(min_epsilon_,initializing);
}


} // namespace Meq

//# Instantiate the makeNorm template.
#include <scimath/Fitting/LSQFit2.cc>
template void casa::LSQFit::makeNorm<double, double*, int*>(unsigned,
int* const&, double* const&, double const&, double const&, bool, bool);


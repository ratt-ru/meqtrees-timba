//# Solver.cc: Base class for an expression node
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
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
#include <MEQ/MTPool.h>
#include <MEQ/Rider.h>
#include <MeqNodes/Solver.h>
#include <MeqNodes/Condeq.h>
#include <MeqNodes/Parm.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/Arrays/Matrix.h>
#include <casa/Arrays/Vector.h>
#include <DMI/List.h>
#ifndef HAVE_PARMDB
#include <MeqNodes/ParmTableUtils.h>
#endif
#include <iostream>


#include <fstream>
#include <complex>

using namespace std;

using namespace casa;

namespace Meq {

InitDebugContext(Solver,"MeqSolver");

// various solver fields

const HIID
    // Solver staterec fields

    FParmGroup       = AidParm|AidGroup,

    // various solver parameters
    FEpsilon         = AidEpsilon,          // convergence criterion, if fit parameter drops below this value, we have converged
    // new option for Apr 2006 LSQFit updates
    FEpsilonDeriv    = AidEpsilon|AidDeriv,
    // new option for Apr 2006 LSQFit updates
    FBalancedEquations = AidBalanced|AidEquations,

    FUseSVD          = AidUseSVD,           // use SVD? passed to LSQFit
    FColinFactor     = AidColin|AidFactor,  // collinearity factor, passed to LSQFit::set(double,double)
    FLMFactor        = AidLM|AidFactor,     // LM factor, passed to LSQFit::set(double,double)
    FNumIter         = AidNum|AidIter,      // max number of iterations
    // FSavePolcs already defined above
    FLastUpdate      = AidLast|AidUpdate,
    FConvergenceQuota = AidConvergence|AidQuota,
    FFlushTables     = AidFlush|AidTables,

    FInterruptSolution = AidInterrupt|AidSolution,

    FMTSolve         = AidMT|AidSolve,

    // Solver result rider
    FMetrics         = AidMetrics,
    FNumUnknowns     = AidNum|AidUnknowns,
    FRank            = AidRank,
    FFit             = AidFit,
    FErrors          = AidErrors,
    FCoVar           = AidCoVar,
    FFlag            = AidFlag,
    FMu              = AidMu,
    FStdDev          = AidStdDev,
    FChi             = AidChi,
    FChi0            = AidChi|0,
    FReady           = AidReady,            // ready code, new Apr 06
    FReadyString     = AidReady|AidString,  // ready string, new Apr 06

    FDebug           = AidDebug;

// various state fields
const HIID FSolverResult = AidSolver|AidResult;
const HIID FIncrementalSolutions = AidIncremental|AidSolutions;

const HIID FIterationSymdeps = AidIteration|AidSymdeps;

const HIID FDebugLevel = AidDebug|AidLevel;
const HIID FIterations = AidIterations;

const HIID FMetricsArray  = AidMetrics|AidArray;
const HIID FDebugArray  = AidDebug|AidArray;

// solver events (published depending on debug level)
const HIID FSolverBegin = AidSolver|AidBegin;
const HIID FSolverIter  = AidSolver|AidIter;
const HIID FSolverEnd   = AidSolver|AidEnd;

const HIID FNumTiles     = AidNum|AidTiles;
const HIID FNumSpids     = AidNum|AidSpids;
const HIID FNumConverged = AidNum|AidConverged;


const HIID  FDebugFile       = AidDebug|AidFile;

#if LOFAR_DEBUG
const int DefaultDebugLevel = 0;
#else
const int DefaultDebugLevel = 0;
#endif

//##ModelId=400E53550260
Solver::Solver()
: eval_mode_(1),
  flag_mask_        (-1),
  do_save_funklets_ (false),
  do_last_update_   (false),
  do_flush_tables_  (true),
  max_num_iter_     (3),
  conv_quota_       (0.8),
  debug_lvl_        (DefaultDebugLevel),
  parm_group_       (AidParm),
  strides_          (0)
{
  // set ddefault settings
  settings_.use_svd       = true;
  settings_.epsilon       = 0;
  settings_.epsilon_deriv = 0;
  settings_.is_balanced   = false;
  settings_.colin_factor  = 1e-8;
  settings_.lm_factor     = 1e-3;
  // set Solver dependencies
  iter_symdeps_.assign(1,FIteration);
  const HIID symdeps1[] = { FDomain,FResolution,FDataset };
  setActiveSymDeps(symdeps1,3);
  // enable multithreading by default if available
  enableMultiThreadedPolling();
  mt_solve_ = true;

  interrupt_ = false;
  write_debug_= false;
}

//##ModelId=400E53550261
Solver::~Solver()
{
  if( strides_ )
    delete [] strides_;
  stopWorkerThreads();
}

//##ModelId=400E53550263
TypeId Solver::objectType() const
{
  return TpMeqSolver;
}







// do nothing here -- we'll do it manually in getResult()
//##ModelId=400E5355026B
int Solver::pollChildren (Result::Ref &resref,
                          std::vector<Result::Ref> &childres,
                          const Request &request)
{
  // block off spid discovery and evaluation requests completely.
  // For evaluation requests, we handle child polling separately in getResult().
  if( request.requestType() == RequestType::DISCOVER_SPIDS ||
      request.evalMode() >= 0 )
    return 0;
  // Other requests passed on to the children as is.
  // (These never make it to our getResult())
  else
    return Node::pollChildren(resref,childres,request);
}


// initializes a Tiling object
void Solver::Tiling::init (const DimVector &tsz,const DimVector &shape)
{
  tile_size = tsz;
  cur_tile = 0;
  active = false;
  total_tiles = 1;
  for( int i=Axis::MaxAxis-1; i>=0; i-- )
  {
    int nc = shape[i];
    if( nc )
    {
      int tsz = tile_size[i];
      // is this axis tiled?
      if( tsz )
        num_tiles[i] = nc/tsz + ((nc%tsz)?1:0); // a minimum of 1 tile always
      else
      {
        num_tiles[i] = 1;
        tile_size[i] = nc;
      }
      tile_stride[i] = total_tiles;
      total_tiles *= num_tiles[i];
    }
  }
}

bool Solver::Tiling::advance (int idim)
{
  int old_tile = cur_tile;
  // ndim tells us how many dimensions we have advanced over
  // (with the last dimension iterating the fastest)
  // That is, index idim has been incremented, while indices
  // idim+1 ... N-1 have been reset to 0. cur_tile still points
  // to the _last_ tile of the sub-cube in dimensions  [idim+1,...,N-1]

  // See if we've gone to the next tile along this dimension
  // (i.e. next sub-cube).
  if( ++dimcount[idim] >= tile_size[idim] )
  {
    dimcount[idim] = 0;
    cur_tile++;
  }
  // no, so we need to reset cur_tile to the _first_ tile of
  // the sub-cube in dimensions  [idim+1,...,N-1]. The size
  // of that sub-cube is just our own stride
  else
    cur_tile -= (tile_stride[idim]-1);
  // Now reset the rolled-over dimensions.
  for( idim++; idim < Axis::MaxAxis; idim++ )
    dimcount[idim] = 0;

  return cur_tile != old_tile;
}

DMI::Record::Ref Solver::Tiling::asRecord () const
{
  DMI::Record::Ref ref(DMI::ANONWR);
  ref()["Num.Tiles"] = num_tiles.asHIID();
  ref()["Tile.Size"] = tile_size.asHIID();
  ref()["Tile.Stride"] = tile_stride.asHIID();
  ref()["Total.Tiles"] = total_tiles;
  ref()["Super.Tile"] = super_tile;
  return ref;
}

DMI::Record::Ref Solver::SpidInfo::asRecord () const
{
  DMI::Record::Ref ref(DMI::ANONWR);
  ref()["Nodeindex"] = nodeindex;
  ref()["Tiling"] = ptiling->tile_size.asHIID();
  ref()["Num.Tiles"] = nuk;
  ref()["SS.Uk.Index"] = ssuki;
  return ref;
}

int Solver::populateSpidMap (const DMI::Record &spidmap_rec,const Cells &cells)
{
  parm_uks_.clear();
  spids_.clear();
  tilings_.clear();
  subsolvers_.clear();
  solvegroups_.clear();
  // we also work out the solver tile sizes. Each solver tile encompasses a
  // whole number of spid sub-tiles, so the solver tile size along each axis
  // is the least common multiple (LCM) of all the spid tile sizes. Start
  // by finding the largest subtile along each axis. At the end of the for()
  // loop below, max_tiling[i] will be the largest subtile size, or 0 if the
  // axis is not tiled by any parm.
  DimVector num_cells;
  int maxrank=0;         // last axis defined in cells
  for( int i=0; i<Axis::MaxAxis; i++ )
    if( cells.isDefined(i) )
      num_cells[maxrank=i] = cells.ncells(i);
  // this will hold the largest tile size found for each dimension,
  // and eventually be the solver tiling
  DimVector solver_tilesize;
  // convert spid map record into internal spid map, and count up the unknowns
  for( DMI::Record::const_iterator iter = spidmap_rec.begin();
      iter != spidmap_rec.end(); iter++ )
  {
    // each spidmap entry is expected to be a record
    const DMI::Record &rec = iter.ref().as<DMI::Record>();
    VellSet::SpidType spid = iter.id()[0].id();  // spid is first element of HIID
    // insert entry into spid table
    SpidInfo & spi = spids_[spid];
    spi.nodeindex = rec[FNodeIndex].as<int>();
    // figure out solvegroup number
    const string & sg = rec[FSolveGroup].as<string>("");
    SolveGroups::const_iterator sgiter = solvegroups_.find(sg);
    // insert new solvegroup if not found, else reuse number
    if( sgiter == solvegroups_.end() )
    {
      spi.solvegroup = numSolveGroups();
      solvegroups_[sg] = spi.solvegroup;
    }
    else
      spi.solvegroup = sgiter->second;
    // OK, figure out the tiling
    DimVector tilesize(num_cells);
    int ntsz;
    const int *ptsz = rec[FTileSize].as_po<int>(ntsz);
    // normalize the tile sizes (make sure we have at least 1 tile along
    // each dim present in the Cells, and that dims not defined in Cells
    // are not tiled)
    bool specified = true;
    for( int i=0; i<Axis::MaxAxis; i++ )
    {
      if( i>=ntsz )
        specified = false;
      if( num_cells[i] )
      {
        if( specified && ptsz[i] )
        {
          tilesize[i] = ptsz[i];
          solver_tilesize[i] = std::max(solver_tilesize[i],ptsz[i]);
        }
        else
          solver_tilesize[i] = num_cells[i];
      }
      else
      {
        FailWhen(specified && ptsz[i],ssprintf("spid %d is tiled along axis %s that is not defined in the Cells",
                 spid,Axis::axisId(i).toString().c_str()));
      }
    }
    // now see if this tiling is already in the map, and insert if not
    TilingMap::iterator iter = tilings_.find(tilesize);
    Tiling * ptiling;
    if( iter == tilings_.end() )
    {
      ptiling = &( tilings_[tilesize] );
      ptiling->init(tilesize,num_cells);
    }
    else
      ptiling = &( iter->second );
    // put pointer to tiling into SpidInfo, and figure out # of unknowns
    spi.ptiling = ptiling;
    spi.nuk = ptiling->total_tiles;
    // increment total count of unknowns
    num_unknowns_ += spi.nuk;
    // add to the total number of unknowns for this nodeindex
    // (this initializes the parm_uk entry as needed)
    parm_uks_[spi.nodeindex].nuk += spi.nuk;
  }
  FailWhen(!num_unknowns_,"spid discovery did not return any solvable parameters");
  // now work out the solver tile sizes. Each solver tile encompasses a
  // whole number of spid sub-tiles, so the solver tile size along each axis
  // is the least common multiple (LCM) of all the spid tile sizes.
  // solver_tilesize currently holds the largest tile size along each axis.
  int stride = 1;  // current stride (== # of subsolvers at end of loop)
  for( int iaxis=0; iaxis <= maxrank; iaxis++ )
  {
    int nc = num_cells[iaxis];
    if( nc )
    {
      int maxtile = solver_tilesize[iaxis];
      // find least common multiple tilesize by checking increasing tile sizes
      // (maxtile, maxtile*2, maxtile*3, ...), until we hit the ncells limit
      int lcm = maxtile;
      for( ; lcm < nc ; lcm += maxtile )
      {
        // check for divisibility by each tiling's tilesize
        TilingMap::const_iterator iter = tilings_.begin();
        for( ; iter != tilings_.end(); iter++ )
        {
          int tsz = iter->first[iaxis];   // map key is tile size
          DbgAssert(tsz);        // loop above should ensure this is >0 for nc!=0
          if( lcm%tsz )       // break out if not a multiple
            break;
        }
        // did the loop complete? if so, then we have the lcm, else keep looking
        if( iter == tilings_.end() )
          break;
      }
      // ok, at this point lcm is the tiling for this axis, but limit it to ncells
      solver_tilesize[iaxis] = std::min(lcm,nc);
    }
  }
  // solver_tilesize now gives the solver tiling, insert it into map if needed
  {
  TilingMap::iterator iter = tilings_.find(solver_tilesize);
  if( iter == tilings_.end() )
  {
    psolver_tiling_ = &( tilings_[solver_tilesize] );
    psolver_tiling_->init(solver_tilesize,num_cells);
  }
  else
    psolver_tiling_ = &( iter->second );
  }
  // allocate required number of subsolvers
  subsolvers_.resize(numSubtiles() * numSolveGroups());
  // now for each spid tiling, figure out what solver tile a given spid
  // subtile belongs to
  for( TilingMap::iterator iter = tilings_.begin(); iter != tilings_.end(); iter++ )
  {
    Tiling & tiling = iter->second;
    tiling.super_tile.resize(tiling.total_tiles);
    if( &tiling == psolver_tiling_ )  // is this the solver tiling itself?
    {
      // initialize with identity vector
      for( int i=0; i<tiling.total_tiles; i++ )
        tiling.super_tile[i] = i;
    }
    else  // else this a subtiling, so do the hard arithmetic
    {
      // the 'subtiling' object describes how the solver tiles tile
      // our subtiling
      DimVector subtile_size;
      for( int i=0; i<=maxrank; i++ )
        subtile_size[i] = solver_tilesize[i]/tiling.tile_size[i] +
                          ((solver_tilesize[i]%tiling.tile_size[i])?1:0);
      Tiling subtiling(subtile_size,tiling.num_tiles);
      subtiling.activate();
      // init a DimCounter for our tiling's shape
      LoShape subtiling_shape;
      subtiling_shape.resize(maxrank+1);
      for( int i=0; i<=maxrank; i++ )
        subtiling_shape[i] = tiling.num_tiles[i];
      Vells::DimCounter counter(subtiling_shape);
      for( int i=0; i<tiling.total_tiles; i++ )
      {
        tiling.super_tile[i] = subtiling.cur_tile;
        int ndim = counter.incr();
        if( ndim )  // ndim is the number of incremented dimensions, counting from end
          subtiling.advance(maxrank-ndim+1);
        else // we must have reached the end
        {
          DbgAssert(i==tiling.total_tiles-1);
        }
      }
    }
  }
#ifdef USE_DEBUG
  DMI::Record & inforec = wstate()["Tiling.Info"] <<= new DMI::Record;
  // put tilings into state record
  DMI::Record & trec = inforec["$Tilings"] <<= new DMI::Record;
  for( TilingMap::const_iterator iter = tilings_.begin(); iter != tilings_.end(); iter++ )
    trec[iter->first.asHIID()] = iter->second.asRecord();
  inforec["Solver.Tiling"] = solver_tilesize.asHIID();
#endif
  // now figure out what unknown in each subsolver corresponds to each spid

//* // use this code to allocate unknonws in the same order as the older
//* // (pre-tiled) Solver
//*  for( DMI::Record::const_iterator iter = spidmap_rec.begin();
//*      iter != spidmap_rec.end(); iter++ )
  for( SpidMap::iterator iter = spids_.begin(); iter != spids_.end(); iter++ )
  {
//*   const DMI::Record &rec = iter.ref().as<DMI::Record>();
//*   VellSet::SpidType spid = iter.id()[0].id();  // spid is first element of HIID
//*   SpidInfo &spi = spids_[spid];
    SpidType spid = iter->first;
    SpidInfo &spi = iter->second;
    Tiling &tiling = *( spi.ptiling );
    spi.ssuki.resize(spi.nuk);
    Subsolver * pss = psubsolver(0,spi.solvegroup);
    // Now work out how the spid tiles map to subsolver unknowns
    // Each spid tile receives a single unknown in the corresponding subsolver.
    // uk0[] and nuk[] keep track of which unknown index we started allocating
    // from, and how many we allocated
    int uk0[numSubtiles()];
    int nuk[numSubtiles()];
    for( int i=0; i<numSubtiles(); i++ )
    {
      uk0[i] = -1;
      nuk[i] = 0;
    }
    // allocate the unknowns
    for( int i=0; i<spi.nuk; i++ )
    {
      int isolver = tiling.super_tile[i];
      DbgAssert(isolver>=0 && isolver<numSubtiles());
      if( uk0[isolver] < 0 )
        uk0[isolver] = pss[isolver].nuk;
      spi.ssuki[i] = pss[isolver].nuk++;
      nuk[isolver]++;
    }
    // update the parm-to-unknowns map
    LoMat_int &slice = parm_uks_[spi.nodeindex].spidset[spid];
    slice.resize(numSubtiles(),2);
    for( int i=0; i<numSubtiles(); i++ )
    {
      DbgAssert(uk0[i]>=0 && nuk[i]); // each tile's subsolver MUST have some unknowns
      slice(i,0) = uk0[i];
      slice(i,1) = uk0[i]+nuk[i];
    }
  }
#ifdef USE_DEBUG
  // put spid_map info into state record
  DMI::Record & spidmaprec = inforec["Spid.Map"] <<= new DMI::Record;
  for( SpidMap::const_iterator iter = spids_.begin(); iter != spids_.end(); iter++ )
    spidmaprec[iter->first] = iter->second.asRecord();
  // put uk_map info into state record
  DMI::Record & pmaprec = inforec["Parm.Map"] <<= new DMI::Record;
  for( ParmUkMap::const_iterator iter = parm_uks_.begin(); iter != parm_uks_.end(); iter++ )
  {
    DMI::Record & pmap = pmaprec[iter->first] <<= new DMI::Record;
    const ParmUkInfo &pui = iter->second;
    pmap["Num.Unknowns"] = pui.nuk;
    DMI::Record & spidset = pmap["Spid.Set"] <<= new DMI::Record;
    for( SpidSet::const_iterator iter = pui.spidset.begin(); iter != pui.spidset.end(); iter++ )
      spidset[iter->first] = iter->second;
  }
  // final sanity checks
  int nuk = 0;
  for( int i=0; i<numSubsolvers(); i++ )
    nuk += subsolvers_[i].nuk;
  Assert(nuk==num_unknowns_);
#endif

  return num_unknowns_;
}


inline bool isvalid (double num)
{ return !( isnan(num) || isinf(num) ); }

inline bool isvalid (dcomplex num)
{ return isvalid(creal(num)) && isvalid(cimag(num)); }

// This is a helper function for fillEquations(). Note that this function
// encapsulates the only difference in the code between the double
// and the complex case. This allows us to have a single templated
// definition of fillEquations() below which works for both cases.
template<typename T>
inline void Solver::fillEqVectors (int itile,int npert,SpidInfo *pspi[],
      const T &,const std::vector<Vells::ConstStridedIterator<T> > &,double)
{
  STATIC_CHECK(0,unsupported_template_type_for_fillEqVectors);
}

template<>
inline void Solver::fillEqVectors (int itile,int npert,SpidInfo *pspi[],
      const double &diff,const std::vector<Vells::ConstStridedIterator<double> > &deriv_iter,double weight)
{
  bool valid = isvalid(diff);
  for( int i=0; i<numSolveGroups(); i++ )
    sgd_[i].nderiv = 0;
  // fill vectors of derivatives for each unknown
  for( int i=0; i<npert && valid; i++ )
  {
    SolveGroupData &sgd = sgd_[pspi[i]->solvegroup];
    valid &= isvalid( sgd.deriv_real[sgd.nderiv] = *deriv_iter[i] );
    sgd.uk_index[sgd.nderiv] = pspi[i]->ssuki[itile];
    sgd.nderiv++;
  }
  if( !valid )
  {
    if( Debug(3) )
    {
      cdebug(3)<<"equation for: ";
        for( int i=0; i<npert; i++ )
          ::Debug::getDebugStream()<<pspi[i]->ssuki[itile]<<" ";
        ::Debug::getDebugStream()<<"contains NANs or INFs, omitting\n";
    }
    return;
  }
  for( int sg=0; sg<numSolveGroups(); sg++ )
  {
    SolveGroupData &sgd = sgd_[sg];
    if( sgd.nderiv )
    {
      Subsolver &ss = *psubsolver(itile,sg);
      if( !ss.converged )
      {
        // add equation to solver
        ss.solver.makeNorm(sgd.nderiv,&(sgd.uk_index[0]),&(sgd.deriv_real[0]),weight,diff);
        ss.neq++;
        num_equations_++;
      }
    }
  }
}


// Specialization for complex case: each value produces two equations
template<>
inline void Solver::fillEqVectors (int itile,int npert,SpidInfo *pspi[],
      const dcomplex &diff,const std::vector<Vells::ConstStridedIterator<dcomplex> > &deriv_iter,double weight)
{
  double re_diff = creal(diff);
  double im_diff = cimag(diff);
  // valid flag checks for inf or nan in equations
  bool valid = isvalid(re_diff) && isvalid(im_diff);
  for( int i=0; i<numSolveGroups(); i++ )
    sgd_[i].nderiv = 0;
  // fill vectors of derivatives for each unknown
  for( int i=0; i<npert && valid; i++ )
  {
    SolveGroupData &sgd = sgd_[pspi[i]->solvegroup];
    valid &= isvalid( sgd.deriv_real[sgd.nderiv] = creal(*deriv_iter[i]) );
    valid &= isvalid( sgd.deriv_imag[sgd.nderiv] = cimag(*deriv_iter[i]) );
    sgd.uk_index[sgd.nderiv] = pspi[i]->ssuki[itile];
    sgd.nderiv++;
  }
  if( !valid )
  {
    if( Debug(3) )
    {
      cdebug(3)<<"equation for: ";
      for( int i=0; i<npert; i++ )
        ::Debug::getDebugStream()<<pspi[i]->ssuki[itile]<<" ";
      ::Debug::getDebugStream()<<"contains NANs or INFs, omitting\n";
    }
    num_invalid++;
    return;
  }
  // add equation to solvers
  for( int sg=0; sg<numSolveGroups(); sg++ )
  {
    SolveGroupData &sgd = sgd_[sg];
    if( sgd.nderiv )
    {
      Subsolver &ss = *psubsolver(itile,sg);
      if( !ss.converged )
      {
        ss.solver.makeNorm(sgd.nderiv,&(sgd.uk_index[0]),&(sgd.deriv_real[0]),weight,re_diff);
        ss.solver.makeNorm(sgd.nderiv,&(sgd.uk_index[0]),&(sgd.deriv_imag[0]),weight,im_diff);
        ss.neq += 2;
        num_equations_ += 2;
      }
      else
        num_converged++;
    }
  }
}

template<typename T>
void Solver::fillEquations (const VellSet &vs)
{
  int npert = vs.numSpids();
  FailWhen(npert>num_spids_,ssprintf("child %d returned %d spids, but only "
            "%d were reported during spid discovery",cur_child_,npert,num_spids_));
  const Vells &diffval = vs.getValue();
  // set pweight to point to the weight Vells, else to Unity
  const Vells * pweight = vs.hasDataWeights() ? &( vs.dataWeights() ) : &( Vells::Unity() );

  // ok, this is where it gets hairy. The main val and each pertval
  // could, in principle, have a different set of variability axes
  // (that is, their shape along any axis can be equal to 1, to indicate
  // no variability). This is the same problem we deal with in Vells
  // math, only on a grander scale, since here N+3 Vells have to
  // be iterated over simultaneously (1 driving term, N derivatives,
  // 1 flag vells, 1 weights vells). Fortunately Vells math provides some
  // help here in the form of strided iterators
  Vells::Shape outshape;          // output shape: superset of input shapes
  // fill in shape arrays for computeStrides() below
  const Vells::Shape * shapes[npert+4];
  // ***** OPTIMIZATION OPPORTUNITY ALERT *****
  // Consider the case of an equation with 1 or more collapsed dimensions;
  // and assume these dimensions are tiled by subsolvers. This equation
  // then needs to be added to every subsolver! This seems like too much of
  // a pain, so I'm going to take the easy way out: use StridedIterators
  // to explicitly re-expand the collapsed dimensions.
  // To achieve this, I add the cells shape to the shapes[] array
  // fed to Vells::computeStrides() below. The resulting output_shape is
  // then always identical to the cells_shape (since no axes are collapsed),
  // and strided iterators for an equation will iterate in-place as needed
  // to yield the right number of equations.
  // (Note that this also takes care of properly weighting equations with
  // collapsed dimensions.)
  // This may not be the most efficient way to do this, but consider this:
  // most equations don't have ANY collapsed axes (i.e. either the rhs or
  // the lhs have some variation along each given axis), in which case
  // this does not introduce any inefficiency.
  shapes[0] = &( cells_shape_ ); // ensure output shape is cells shape

  // index of current unknown per each derivative per each subsolver
  // (since we may have multiple unknowns per spid due to tiling,
  // we keep track of the current one when filling equations)
  shapes[1] = &( diffval.shape() );
  shapes[2] = &( diffval.flagShape() ); // returns null shape if no flags
  shapes[3] = &( pweight->shape() );
  int j=4;
  // deactivate all tilings, then reactivate the ones for active spids
  for( TilingMap::iterator iter = tilings_.begin(); iter != tilings_.end(); iter++ )
    iter->second.active = false;
  // activate the solver's tiling
  psolver_tiling_->activate();
  // go over derivatives, fill in shapes, get pointers to tilings and such
  Tiling *   ptiling[npert];    // shorthand pointers to SpidInfo...
  SpidInfo * pspi[npert];       //    ...and TilingInfo per derivative
  int uk_index[npert];          // current unknown number per derivative
  for( int i=0; i<npert; i++,j++ )
  {
    SpidType spid = vs.getSpid(i);
    SpidMap::iterator iter = spids_.find(spid);
    FailWhen(iter == spids_.end(),ssprintf("child %d returned spid %d that was "
             "not reported during spid discovery",cur_child_,spid));
    pspi[i]     = &( iter->second );
    (ptiling[i] = pspi[i]->ptiling)->activate();
    // get shape of derivative
    shapes[j] = &( vs.getPerturbedValue(i).shape() );
  }
  // compute output shape (the union of all input shapes), and
  // strides for all vells
  Vells::computeStrides(outshape,strides_,npert+4,shapes,"Solver::getResult");
  int outrank = outshape.size();
  // create strided iterators for all vells
  Vells::ConstStridedIterator<T> diff_iter(diffval,strides_[1]);
  Vells::ConstStridedFlagIterator flag_iter(diffval,strides_[2]);
  Vells::ConstStridedIterator<double> weight_iter(*pweight,strides_[3]);
  std::vector<Vells::ConstStridedIterator<T> > deriv_iter(npert);
  j=4;
  for( int i=0; i<npert; i++,j++ )
    deriv_iter[i] = Vells::ConstStridedIterator<T>(vs.getPerturbedValue(i),strides_[j]);
  // create counter for output shape
  Vells::DimCounter counter(outshape);
  // now start generating equations. repeat while counter is valid
  // (we break out below, when incrementing the counter)
  int nfill=0,niter=0;
  num_invalid=num_converged=0;
  while( true )
  {
    niter++;
    // fill equations only if unflagged and weighted
    if( !(*flag_iter&flag_mask_) && *weight_iter > 0 )
    {
      nfill++;
      fillEqVectors(psolver_tiling_->cur_tile,npert,pspi,*diff_iter,deriv_iter,*weight_iter);
    }
    // increment counter and all iterators
    int ndim = counter.incr();
    if( !ndim )    // break out when counter is finished
      break;
    diff_iter.incr(ndim);
    flag_iter.incr(ndim);
    weight_iter.incr(ndim);
    for( int ipert=0; ipert<npert; ipert++ )
      deriv_iter[ipert].incr(ndim);
    // now for each tiling in use, advance its counters
    for( TilingMap::iterator iter = tilings_.begin(); iter != tilings_.end(); iter++ )
    {
      Tiling &ti = iter->second;
      // note that ndim tells us how many dimensions from the END of the
      // output hypercube have been incremented. So the outer incremented
      // dimension is N-ndim, so this is what we pass to Tiling::advance()
      if( ti.active )
        ti.advance(outshape.size()-ndim);
    }
  }
//  if( !num_equations_ )
//  {
//    cerr<<"No equations: "<<niter<<" points iterated, "<<nfill<<"fill calls\n";
//    cerr<<"Invalid/converged fills:"<<num_invalid<<" "<<num_converged<<endl;
//  }
}



// helper method to flatten a list of records into an array
template<class T>
static ObjRef flattenScalarList (const DMI::List &list,const HIID &field)
{
  // presize the array to list size
  LoShape shape(list.size());
  DMI::NumArray * parr = new DMI::NumArray(typeIdOf(T),shape);
  ObjRef res(parr);
  blitz::Array<T,1> &arr = parr->getArray<T,1>();
  // go through list and fill with data
  DMI::List::const_iterator iter = list.begin();
  for( int n=0; iter != list.end(); iter++,n++ )
    if( iter->valid() )
      arr(n) = iter->as<Container>()[field].as<T>(0);
  return res;
}

template<class T,int N>
static ObjRef flattenArrayList (const DMI::List &list,const HIID &field)
{
  // figure out maximum shape of output array
  blitz::TinyVector<int,N> maxshape(1);
  DMI::List::const_iterator iter = list.begin();
  // go through list and compare shapes
  for( ; iter != list.end(); iter++ )
    if( iter->valid() )
    {
      DMI::Record::Hook harr(iter->as<Container>(),field);
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
    if( iter->valid() )
    {
      DMI::Record::Hook harr(iter->as<Container>(),field);
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

  //SBY open file
  ofstream logfile_;
  if (write_debug_) {
   logfile_.open(debug_filename_.c_str(), ios::out | ios::app);
  }

  iter_depmask_ = symdeps().getMask(iter_symdeps_);
  cells_shape_ = request.cells().shape();
  // Use single derivative by default, or a higher mode if specified in request
  AtomicID rqtype = RequestType::EVAL_SINGLE;
  if( std::max(eval_mode_,request.evalMode()) > 1 )
    rqtype = RequestType::EVAL_DOUBLE;
  interrupt_ = false; // clear interrupt flag
  // The result has no planes, all solver information is in extra fields
  resref <<= new Result(0);
  // solver result has to be kept by countedref, since we may be publishing
  // it as we go along, so we're not allowed to keep a local pointer (else
  // COW will break).
  DMI::Record::Ref solveResult(DMI::ANONWR);
  DMI::List::Ref metricsList,debugList;
  if( debug_lvl_ >= 0 )
    metricsList <<= new DMI::List;
  if( debug_lvl_ >= 3 )
    debugList <<= new DMI::List;
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
  std::vector<Result::Ref> child_results;
  timers().getresult.stop();
  timers().children.start();
  int retcode = Node::pollChildren(resref,child_results,*reqref);
  timers().children.stop();
  timers().getresult.start();
  if( retcode&(RES_FAIL|RES_WAIT|RES_ABORT) )
    return retcode;
  // Node's standard discoverSpids() implementation merges all child spids together
  // into a result object. This is exactly what we need here
  Result::Ref tmpres;
  Node::discoverSpids(tmpres,child_results,req);
  // discard child results
  child_results.clear();
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
      // populate our map from the record and work out tilings
      populateSpidMap(*pspid_map,request.cells());
#ifdef USE_DEBUG
#endif
    }
  }
  if( !num_unknowns_ )
  {
    // no unknowns/spids discovered, so may as well fail...
    Throw("spid discovery did not return any solvable parameters");
  }
  num_spids_ = spids_.size();
  // post a Solver.Begin event
  DMI::Record::Ref evrec(DMI::ANONWR);
  if( debug_lvl_ >= 0 )
  {
    evrec[FNumUnknowns] = num_unknowns_;
    evrec[FNumTiles] = numSubsolvers();
    evrec[FNumSpids] = num_spids_;
    evrec[FNode] = name();
    postEvent(FSolverBegin,evrec);
  }
  Timestamp last_post_event; // keep track of when the most recent event was posted

  // allocate matrix of incremental solutions -- allocate directly in solver
  // result so that it stays visible in our state record (handy
  // when debugging trees, for instance). Note that we don't care about COW
  // here since the array structure does not change, only data is filled in
  DMI::NumArray & allSolNA = solveResult[FIncrementalSolutions]
        <<= new DMI::NumArray(Tpdouble,LoShape(max_num_iter_,num_unknowns_));
  LoMat_double & incr_solutions = allSolNA.getArray<double,2>();
  // now go over allocated subsolvers and init them
  int uk0 = 0;
  settings_.max_iter = max_num_iter_; // this is the same for all solvers
  for( int i=0; i<numSubsolvers(); i++ )
    subsolvers_[i].initSolution(uk0,incr_solutions,settings_,metricsList.valid(),debugList.valid());
  cdebug(2)<<numSubsolvers()<<" sub-solvers initialized for "<<num_unknowns_<<" unknowns\n";
  // how many subsolvers need to converge
  need_conv_ = std::min(numSubsolvers(),int(ceil(numSubsolvers()*conv_quota_)));
  num_conv_ = 0;
  // resize temporaries used in fillEquations()
  sgd_.resize(numSolveGroups());
  for( int i=0; i<numSolveGroups(); i++ )
  {
    sgd_[i].uk_index.resize(num_unknowns_);
    sgd_[i].deriv_real.resize(num_unknowns_);
    sgd_[i].deriv_imag.resize(num_unknowns_);
  }
  // ISO C++ won't allow a vector of Strides, hence this old-style kludge
  if( strides_ )
    delete [] strides_;
  strides_ = new Vells::Strides[num_spids_+4];
  // OK, now create the "real" request object. This will be modified from
  // iteration to iteration, so we keep it attached to reqref and rely on COW
  reqref <<= new Request(request.cells());
  bool converged = false;
  bool no_equations = false;
  for( cur_iter_=0; cur_iter_ < max_num_iter_ && !converged && !interrupt_; cur_iter_++ )
  {
    // generate a Solver.Iter event after the 0th iteration
    if( cur_iter_ && debug_lvl_ >= 0 )
    {
      // check that we don't "spam" the channel by comparing timestamps,
      // and issuing no more than 3 events per second (unless debug level
      // is high enough that we send it anyway)
      if( debug_lvl_ >= 2 || Timestamp::delta(last_post_event).seconds() > .3 )
      {
        last_post_event = Timestamp::now();
        postEvent(FSolverIter,evrec);
      }
    }
    // increment the solve-dependent parts of the request ID
    rqid = next_rqid;
    RqId::incrSubId(next_rqid,iter_depmask_);
    // set request Ids in the request object
    reqref().setId(rqid);
    reqref().setNextId(next_rqid);
    num_equations_ = 0;
    // start async child poll
    timers().getresult.stop();
    setExecState(CS_ES_POLLING);
    timers().children.start();
    children().startAsyncPoll(*reqref,currentRequestDepth()+1);
    if( forest().abortFlag() )
      return RES_ABORT;
    int rescode;
    Result::Ref child_res;
    int nch_returned=0;
    int nvs_returned=0;
    // wait for child results until all have been polled (await will return -1 when this is the case)
    std::list<Result::Ref> child_fails;  // any fails accumulated here
    while( (cur_child_ = children().awaitChildResult(rescode,child_res,*reqref)) >= 0 )
    {
      nch_returned++;
      if( forest().abortFlag() )
        return RES_ABORT;
      // tell child to hold cache if it doesn't depend on iteration
      children().getChild(cur_child_).holdCache(!(rescode&iter_depmask_));
      // skip children with fails or missing data
      if( rescode&(RES_FAIL|RES_MISSING|RES_WAIT) )
        continue;
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
        nvs_returned++;
        timers().getresult.start();
        if( vs.getValue().isReal() )
          fillEquations<double>(vs);
        else
          fillEquations<dcomplex>(vs);
        timers().getresult.stop();
      }
    } // end of while loop over children
    timers().children.stop();
    if( forest().abortFlag() )
      return RES_ABORT;
    setExecState(CS_ES_EVALUATING);
    // **for debug purposes, count number of converged solvers
//    int nc1=0;
//    for( int i=0; i<numSubsolvers(); i++ )
//      if( subsolvers_[i].converged )
//        nc1++;
//    cerr<<rqid.toString()<<" iter "<<cur_iter_<<" start: "<<nc1<<" subsolvers have converged\n";
//    cerr<<"Main thread is "<<Thread::self()<<endl;
//    FailWhen(!num_equations_,"no equations were generated");
    if( !num_equations_ )
    {
      DMI::Record *prec;
      ObjRef ref(prec=new DMI::Record);
      (*prec)[FRequestId] = rqid;
      (*prec)[AidIter] = cur_iter_;
      postMessage(Debug::ssprintf("No solver equations were generated for request ID %s. Perhaps "
          "all input data is flagged, or no parameters were set to solvable.",rqid.toString().c_str()),
          ref);
      no_equations = true;
      break;
    }
    timers().getresult.start();
    cdebug(4)<<"accumulated "<<num_equations_<<" equations\n";
    // now for the subsolvers loop
    int nremain = numSubsolvers() - num_conv_; // how many have not converged yet
    num_conv_ = 0;
    // call all subsolvers and count how many have converged
    // use mt solving if enabled, and if >1 subsolver has not yet converged
    if( !worker_threads_.empty() && nremain > 1 )
    {
      num_conv_ = 0;
      activateSubsolverWorkers();
    }
    else // single-threaded loop
    {
      for( int i=0; i<numSubsolvers(); i++ )
      {
        Subsolver &ss = subsolvers_[i];
        if( ss.solve(cur_iter_) )
          num_conv_++;
        cdebug(5)<<"subsolver "<<i<<" fit is "<<ss.fit<<", converged "<<ss.converged<<endl;
      }
    }
    cdebug(4)<<num_conv_<<" subsolvers have converged ("<<need_conv_<<" needed)\n";
    converged = num_conv_ >= need_conv_;
//    nc1=0;
//    for( int i=0; i<numSubsolvers(); i++ )
//      if( subsolvers_[i].converged )
//        nc1++;
//    cerr<<rqid.toString()<<" iter "<<cur_iter_<<" end: "<<nc1<<" "<<num_conv_<<" subsolvers have converged\n";
    // collect incremental solutions
    for( int i=0; i<numSubsolvers(); i++ )
      subsolvers_[i].copySolutions(incr_solutions,cur_iter_);
    // fill in updates in request object
    fillRider(reqref,do_save_funklets_&&(converged || interrupt_ || (cur_iter_ >= max_num_iter_-1)),converged);
    //fillRider(reqref,do_save_funklets_,converged);
    // fill in metrics and debug info
    DMI::Vec * pmetvec = 0;
    if( metricsList.valid() )
      metricsList().addBack(pmetvec = new DMI::Vec(TpDMIRecord,numSubsolvers()));
    DMI::Vec * pdbgvec = 0;
    if( debugList.valid() )
      debugList().addBack(pdbgvec = new DMI::Vec(TpDMIRecord,numSubsolvers()));
    for( int i=0; i<numSubsolvers(); i++ )
    {
      if( pmetvec && subsolvers_[i].metrics.valid() )
        pmetvec->put(i,subsolvers_[i].metrics);
      if( pdbgvec && subsolvers_[i].debugrec.valid() )
        pdbgvec->put(i,subsolvers_[i].debugrec);
    }
    // fill in a Solver.Iter event (will be posted at top of loop,
    // if we don't loop again, then Solver.End will be sent below instead)
    if( debug_lvl_ >= 0 )
    {
      double sumfit = 0;
      double sumchi0 = 0;
      int sumrank = 0;
      for( int i=0; i<numSubsolvers(); i++ )
      {
        sumrank += subsolvers_[i].rank;
        sumfit += subsolvers_[i].fit;
        sumchi0 += subsolvers_[i].chi0;
      }
      // generate event as needed
      evrec[FNumConverged] = num_conv_;
      evrec[FConverged]  = converged;
      evrec[FIterations] = cur_iter_+1;
      evrec[FRank] = sumrank;
      evrec[FFit] = sumfit/numSubsolvers();
      evrec[FChi0] = sumchi0/numSubsolvers();
      // attach more info with higher debug levels
      if( debug_lvl_ >= 1 && pmetvec )
        evrec[FMetrics] <<= pmetvec;
      if( debug_lvl_ >= 4 && pdbgvec )
        evrec[FDebug] <<= pdbgvec;
    }
    // stick metrics and debug records into solver result
    if( metricsList.valid() )
      solveResult()[FMetrics].replace() = metricsList;
    if( debugList.valid() )
      solveResult()[FDebug].replace() = debugList;
    // stick solver result into node state
    wstate()[FSolverResult].replace() = solveResult;
  } // end of FOR loop over solver iterations
  // post a Solver.End event (which is simply a copy of the latest iteration event)
  if( debug_lvl_ >= 0 )
    postEvent(FSolverEnd,evrec);
  if( forest().abortFlag() )
    return 0;
  ///////////////////////////////////////
  //SBY: loop over child results to save them
  if (write_debug_)
  {
    int rescode;
    Result::Ref child_res;
    // wait for child results until all have been polled (await will return -1 when this is the case)
    int numc=children().numChildren();
    logfile_<<numc;
    for(int ich=0; ich<numc; ich++)
    {
      children().getChild(ich).execute(child_res,reqref,currentRequestDepth()+1);
      double sumc=0; //for a tensor, sum the result
      for( int ivs = 0; ivs < child_res->numVellSets(); ivs++ )
      {
            const VellSet &vs = child_res->vellSet(ivs);
            // ignore failed or null vellsets
            if( vs.isFail() || vs.isNull() ) {
              continue;
            }
            //SBY: write vs to file
            const Vells &invl=vs.getValue();
            const Vells &ivl=Meq::VellsMath::mean(Meq::VellsMath::sqr(Meq::VellsMath::abs(invl)));
            double *indata=const_cast<double*>(ivl.realStorage());
            blitz::Array<double,2> A(indata,blitz::shape(ivl.extent(0),ivl.extent(1)),blitz::neverDeleteData);
            //reshape to a column vector
            sumc+=blitz::mean(A);

      }
      logfile_<<" "<<sumc;
    }
    logfile_<<std::endl;
  }
  //////////////////////////////////////
  // send up one final update if needed
  if( do_last_update_ && (cur_iter_ == max_num_iter_ || interrupt_ || converged))
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

#ifndef HAVE_PARMDB
    ParmTableUtils::lockTables();
#endif

    timers().getresult.stop();
    Node::pollChildren(resref,child_results,lastreq);
    child_results.clear();
    timers().getresult.start();
#ifndef HAVE_PARMDB
    ParmTableUtils::unlockTables();
    if( do_flush_tables_ )
      ParmTableUtils::flushTables();
#endif
  }
  if( forest().abortFlag() )
    return RES_ABORT;
  solveResult()[FConverged]  = converged;
  solveResult()[FIterations] = cur_iter_;
  // if we broke out of the loop because of some other criterion, we need
  // to crop the incremental solutions matrix to [0:cur_iter_-1,*]
  if( cur_iter_ < max_num_iter_ )
  {
    // create new array and copy subarray of incremental solutions into it
    DMI::NumArray::Ref arr_ref;
    arr_ref <<= new NumArray(Tpdouble,LoShape(cur_iter_,num_unknowns_));
    arr_ref().getArray<double,2>() = incr_solutions(LoRange(0,cur_iter_),LoRange::all());
    // replace incr_solutions in solver result
    solveResult[FIncrementalSolutions].replace() <<= arr_ref;
  }

  // finally, to make life easier for DataCollect and HistoryCollect nodes, reformat all
  // metrics and debug fields from lists into arrays, where the first axis is the number of
  // iterations
  if( metricsList.valid() )
  {
    DMI::Vec &allmetrics = solveResult()[FMetricsArray] <<= new DMI::Vec(TpDMIRecord,numSubsolvers());
    for( int i=0; i<numSubsolvers(); i++ )
    {
      DMI::Record & metrics = allmetrics[i] <<= new DMI::Record;
      metrics[FRank]   = flattenScalarList<int>(*metricsList,AtomicID(i)|AidSlash|FRank);
      metrics[FFit]    = flattenScalarList<double>(*metricsList,AtomicID(i)|AidSlash|FFit);
      metrics[FChi]    = flattenScalarList<double>(*metricsList,AtomicID(i)|AidSlash|FChi);
      metrics[FChi0]   = flattenScalarList<double>(*metricsList,AtomicID(i)|AidSlash|FChi0);
      metrics[FCoVar]  = flattenArrayList<double,2>(*metricsList,AtomicID(i)|AidSlash|FCoVar);
      metrics[FErrors] = flattenArrayList<double,1>(*metricsList,AtomicID(i)|AidSlash|FErrors);
      metrics[FFlag]   = flattenScalarList<bool>(*metricsList,AtomicID(i)|AidSlash|FFlag);
      metrics[FMu]     = flattenScalarList<double>(*metricsList,AtomicID(i)|AidSlash|FMu);
      metrics[FStdDev] = flattenScalarList<double>(*metricsList,AtomicID(i)|AidSlash|FStdDev);
    }
  }
  if( debugList.valid() )
  {
    DMI::Vec &alldbg = solveResult()[FDebugArray] <<= new DMI::Vec(TpDMIRecord,numSubsolvers());
    for( int i=0; i<numSubsolvers(); i++ )
    {
      DMI::Record & dbgrec = alldbg[i] <<= new DMI::Record;
      dbgrec["$nEq"] = flattenArrayList<double,2>(*debugList,AtomicID(i)|AidSlash|"$nEq");
      dbgrec["$known"] = flattenArrayList<double,1>(*debugList,AtomicID(i)|AidSlash|"$known");
      dbgrec["$constr"] = flattenArrayList<double,2>(*debugList,AtomicID(i)|AidSlash|"$constr");
      dbgrec["$er"] = flattenArrayList<double,1>(*debugList,AtomicID(i)|AidSlash|"$er");
      dbgrec["$piv"] = flattenArrayList<int,1>(*debugList,AtomicID(i)|AidSlash|"$piv");
      dbgrec["$sEq"] = flattenArrayList<double,2>(*debugList,AtomicID(i)|AidSlash|"$sEq");
      dbgrec["$sol"] = flattenArrayList<double,1>(*debugList,AtomicID(i)|AidSlash|"$sol");
      dbgrec["$prec"] = flattenScalarList<double>(*debugList,AtomicID(i)|AidSlash|"$prec");
      dbgrec["$nonlin"] = flattenScalarList<double>(*debugList,AtomicID(i)|AidSlash|"$nonlin");
    }
  }

  //SBY close file
  if (write_debug_)
    logfile_.close();

  // insert solver result into result object and into state
  wstate()[FSolverResult].replace() = solveResult;
  resref()[FSolverResult] = solveResult;
  // clear state dependencies possibly introduced by parms
  clearStateDependency();
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

void Solver::Subsolver::initSolution (int &uk0_,LoMat_double &incr_sol,
                              const SolverSettings &set,bool usemetrics,bool usedebug)
{
  settings = set;
  Assert1(nuk);
  solver.set(nuk);
  solver.set(settings.colin_factor,settings.lm_factor);
#ifndef USE_OLD_LSQFIT
  solver.setMaxIter(settings.max_iter);
  solver.setEpsValue(settings.epsilon);
  solver.setEpsDerivative(settings.epsilon_deriv);
  solver.setBalanced(settings.is_balanced);
  cdebug1(1)<<"solver settings: "
      <<settings.max_iter<<" "
      <<settings.epsilon<<" "
      <<settings.epsilon_deriv<<" "
      <<settings.is_balanced<<endl;
#endif
  solution.resize(nuk);
  uk0 = uk0_;
//  incr_solutions.reference(incr_sol(LoRange::all(),LoRange(uk0,uk0+nuk-1)));
  uk0_ += nuk;
  sol_range = LoRange(uk0,uk0+nuk-1);
  // init other members
  use_debug = usedebug;
  use_metrics = usemetrics;
  converged = false;
  chi0 = chi = 0;
  neq = 0;
  rank = 0;
}

bool Solver::Subsolver::solve (int step)
{
  solution = 0;
  // if converged or no equations were generated, do nothing
  if( converged || !neq )
    return true;
  // reset neq -- will be re-incremented when filling equations
  neq = 0;
  // get debug info -- only valid before a solveLoop() call
  uint nun=0,np=0,ncon=0,ner=0,rank_dbg=0;
  double * nEq,*known,*constr,*er,*sEq,*sol,prec,nonlin;
  uint * piv;
  solver.debugIt(nun,np,ncon,ner,rank_dbg,nEq,known,constr,er,piv,sEq,sol,prec,nonlin);
  // compute input chi^2
  chi0 = 0;
  if( er )
    chi0 = er[2]/std::max(int(er[0])+nuk,1);
  //    chi0 = er[LSQFit::SUMLL]/std::max(er[LSQFit::NC]+nuk,1);
  // place debug info in record, if so asked
  if( use_debug )
  {
    DMI::Record &dbg = debugrec <<= new DMI::Record;
    if( nEq )
      dbg["$nEq"] = triMatrix(nEq,nun);
    if( known )
      dbg["$known"] = LoVec_double(known,LoShape1(np),blitz::neverDeleteData);
    if( ncon )
      dbg["$constr"] = LoMat_double(constr,LoShape2(ncon,nun),blitz::neverDeleteData,blitz::ColumnMajorArray<2>());
    if( er )
      dbg["$er"] = LoVec_double(er,LoShape1(ner),blitz::neverDeleteData);
    if( piv )
      dbg["$piv"] = LoVec_int(reinterpret_cast<int*>(piv),LoShape1(np),blitz::neverDeleteData);
    if( sEq )
      dbg["$sEq"] = triMatrix(sEq,np);
    if( sol )
      dbg["$sol"] = LoVec_double(sol,LoShape1(np),blitz::neverDeleteData);
    dbg["$prec"] = prec;
    dbg["$nonlin"] = nonlin;
  }

  // do a solution loop
  solFlag = solver.solveLoop(fit,rank,solution,settings.use_svd);

  cdebug1(4)<<"solution after: " << solution << ", rank " << rank << endl;
  // workaround for LSQFit::debugIt() bug: if solution ready immediately
  // after first step, rank is uninitialized
  if( solver.isReady() && !step )
    rank = 0;
  chi = solver.getChi();

  if( use_metrics )
  {
    // Put the statistics in a record of the result.
    DMI::Record & mrec = metrics <<= new DMI::Record;
  #ifndef USE_OLD_LSQFIT
    mrec[FReady]  = solver.isReady();
    mrec[FReadyString] = solver.readyText();
  #endif
    mrec[FRank]   = int(rank);
    mrec[FFit]    = fit;
  //  mrec[FErrors] = errors;
    mrec[FFlag]   = solFlag;
    mrec[FMu]     = solver.getWeightedSD();
    mrec[FStdDev] = solver.getSD();
    mrec[FNumUnknowns] = nuk;
    mrec[FChi   ] = chi;
    mrec[FChi0  ] = chi0;
  }

// getCovariance() and getErrors() seem to destroy the matrix.
// so comment them out for now. The right way is to make a copy of the LSQFit
// object, and get it from there. Since this is potentially expensive,
// only do it under the use_debug clause.
//   // fill errors and covariance matrices
  if( use_debug && use_metrics )
  {
    LSQFit tmp(solver);
    DMI::NumArray &errors = metrics()[FErrors] <<= new DMI::NumArray(Tpdouble,LoShape(nuk),DMI::NOZERO);
    DMI::NumArray &covar = metrics()[FCoVar] <<= new DMI::NumArray(Tpdouble,LoShape(nuk,nuk),DMI::NOZERO);
    tmp.getCovariance(static_cast<double*>(covar.getDataPtr()));
    tmp.getErrors(static_cast<double*>(errors.getDataPtr()));
  }

  // check if converged;
#ifdef USE_OLD_LSQFIT
  converged = ((abs(fit) <= settings.epsilon) && fit <= 0.0);
#else
  converged = solver.isReady();
#endif

//  // copy solution to incr_solutions matrix
//  incr_solutions(step,LoRange::all()) = B2A::refAipsToBlitz<double,1>(solution);

  return converged;
}

void Solver::fillRider (Request::Ref &reqref,bool save_funklets,bool converged)
{
  reqref().clearRider();
  // Put the solution in the rider:
  //    [FRider][<parm_group>][CommandByNodeIndex][<parmid>]
  // will contain a DMI::Record for each parm
  DMI::Record& grouprec = Rider::getCmdRec_ByNodeIndex(reqref,parm_group_,
                                                       Rider::NEW_GROUPREC);

  for( ParmUkMap::const_iterator iparm = parm_uks_.begin();
       iparm != parm_uks_.end(); iparm++ )
  {
    int nodeindex = iparm->first;
    // create UpdateParm command for this parm
    DMI::Record & toprec = grouprec[nodeindex] <<= new DMI::Record;
    DMI::Record & cmdrec = toprec[FUpdateParm] <<= new DMI::Record;
    const ParmUkInfo & pui = iparm->second;
    // create vector of updates and get pointer to its data
    DMI::NumArray &arr = cmdrec[FIncrUpdate] <<= new DMI::NumArray(Tpdouble,LoShape(pui.nuk));
    double *pupd = static_cast<double*>(arr.getDataPtr());
    int j=0;
    // fill updates for this node's spids, by fetching them from the solution
    // vector via the spid set indices
    for( SpidSet::const_iterator ii = pui.spidset.begin(); ii != pui.spidset.end(); ii++ )
    {
      Subsolver *pss = psubsolver(0,spids_[ii->first].solvegroup);
      const LoMat_int &slice = ii->second;
      for( int itile=0; itile<numSubtiles(); itile++ )
      {
        for( int i=slice(itile,0); i<slice(itile,1); i++ )
          pupd[j++] = pss[itile].solution(i);
      }
    }
    // add save command if requested
    if( save_funklets )
      cmdrec[FSaveFunklets] = true;
    cmdrec[FConverged] = converged;
  }
  // make sure the request rider is validated
  reqref().validateRider();

}











//##ModelId=400E53550267
void Solver::setStateImpl (DMI::Record::Ref & newst,bool initializing)
{
  Node::setStateImpl(newst,initializing);
  // get the parm group
  newst[FParmGroup].get(parm_group_,initializing);
  // get symdeps for iteration
  newst[FIterationSymdeps].get_vector(iter_symdeps_,initializing);

  // get eval mode
  newst[FEvalMode].get(eval_mode_,initializing);
  // get debug flag
  newst[FDebugLevel].get(debug_lvl_,initializing);
  // get other solver parameters
  newst[FFlagMask].get(flag_mask_,initializing);
  newst[FSaveFunklets].get(do_save_funklets_,initializing);
  newst[FFlushTables].get(do_flush_tables_,initializing);
  newst[FLastUpdate].get(do_last_update_,initializing);
  newst[FNumIter].get(max_num_iter_,initializing);
  newst[FConvergenceQuota].get(conv_quota_,initializing);
  newst[FUseSVD].get(settings_.use_svd,initializing);
  newst[FEpsilon].get(settings_.epsilon,initializing);
  newst[FEpsilonDeriv].get(settings_.epsilon_deriv,initializing);
  newst[FBalancedEquations].get(settings_.is_balanced,initializing);
  newst[FColinFactor].get(settings_.colin_factor,initializing);
  newst[FLMFactor].get(settings_.lm_factor,initializing);

  newst[FInterruptSolution].get(interrupt_);

  newst[FMTSolve].get(mt_solve_,initializing);
  if( mt_solve_ && worker_threads_.empty() )
    startWorkerThreads();
  else if( !mt_solve_ )
    stopWorkerThreads();
  //// SBY open file for writing, and write all names of children
  if (newst[FDebugFile].get(debug_filename_,initializing)) {
    write_debug_=true;
    ofstream logfile_;
    logfile_.open(debug_filename_.c_str(), ios::out | ios::app);
    //write names of condeqs to file first
    if (!initializing) {
    int numc=children().numChildren();
    logfile_<<numc<<" ";
    for(int ich=0; ich<numc; ich++) {
     logfile_<<" "<<children().getChild(ich).name();
    }
    logfile_<<std::endl;
    }
  }
  ////////////////////////////////////
}

void Solver::startWorkerThreads ()
{
  // do nothing if -mt is not configured
  int nt = MTPool::num_threads();
  if( nt<2 )
    return;
  // start workers
  wt_flush_tables_ = wt_solve_loop_ = false;
  wt_num_active_ = 0;
  cdebug(0)<<"starting "<<nt-1<<" worker threads\n";
  worker_threads_.resize(nt-1);
  wt_info_.resize(nt-1);
  wt_active_.resize(nt-1);
  wt_active_.assign(nt-1,false);
  for( int i=0; i<nt-1; i++ )
  {
    wt_info_[i].solver = this;
    wt_info_[i].wt_num = i;
    worker_threads_[i] = Thread::create(runWorkerThread,&(wt_info_[i]));
  }
}

void Solver::stopWorkerThreads ()
{
  if( worker_threads_.empty() )
    return;
  cdebug(0)<<"stopping worker threads\n";
  // set mt_solve_ to false and wake all workers
  Thread::Mutex::Lock lock(worker_cond_);
  mt_solve_ = false;
  worker_cond_.broadcast();
  lock.release();
  // rejoin
  cdebug(1)<<"rejoining worker threads\n";
  for( uint i=0; i<worker_threads_.size(); i++ )
    worker_threads_[i].join();
  worker_threads_.clear();
}

// static function starts up a worker thread
void * Solver::runWorkerThread (void *pinfo_void)
{
  WorkerThreadInfo *pinfo = static_cast<WorkerThreadInfo*>(pinfo_void);
  return pinfo->solver->workerLoop(pinfo->wt_num);
}

// Activates all worker threads to process subsolvers.
// Process what we can in this thread too, and return when all jobs are
// complete.
// Any exceptions generated by the subsolvers are stored, and
// eventually rethrown from here
void Solver::activateSubsolverWorkers ()
{
  // init queue and clear error list
  Thread::Mutex::Lock lock(worker_cond_);
  Thread::Mutex::Lock lock1(worker_exit_cond_);
  cdebug(3)<<"T"<<Thread::self()<<" activating workers"<<endl;
  wt_num_ss_ = 0;
  wt_exceptions_.clear();
  // wakeup threads, we expect all to be active
  wt_solve_loop_ = true;
  wt_num_active_ = worker_threads_.size();
  wt_active_.assign(wt_active_.size(),true);
  worker_cond_.broadcast();
  // go into our own loop to start processing subsolvers
  processSolversLoop(lock);
  lock.release();
  // wait for worker threads to become inactive
  bool active = true;
  while( active )
  {
    worker_exit_cond_.wait();
    // if amny thread is still active, flag will be re-raised
    active = false;
    for( uint i=0; i<wt_active_.size(); i++ )
      if( wt_active_[i] )
      {
        active = true;
        break;
      }
  }
  cdebug(3)<<"T"<<Thread::self()<<" all workers finished"<<endl;
  // if any exceptions have accumulated, throw them
  if( !wt_exceptions_.empty() )
    throw wt_exceptions_;
}

// If a worker thread is available, wakes it up to flush parm tables
// Otherwise flushes table directly in here.
void Solver::flushTablesInWorkerThread ()
{
#ifndef HAVE_PARMDB
  // if no worker threads available, flush tables
  if( worker_threads_.empty() )
  {
    ParmTableUtils::flushTables();
  }
  // else wake a worker
  else
  {
    Thread::Mutex::Lock lock(worker_cond_);
    cdebug(3)<<"T"<<Thread::self()<<" activating a worker to flush tables"<<endl;
    wt_flush_tables_ = true;
    worker_cond_.signal();
  }
#endif
}


// processes subsolvers in a loop, until all complete, or an exception
// occurs. On entry, lock is a lock on worker_cond_.
void Solver::processSolversLoop (Thread::Mutex::Lock &lock)
{
  cdebug(3)<<"T"<<Thread::self()<<" subsolver loop started"<<endl;
  // loop until all subsolvers are processed
  while( wt_num_ss_ < numSubsolvers() )
  {
    // at this point we hold a lock on worker_cond_. We only ever release
    // it on the inside, when we go to process a subsolver
    // grab a non-converged subsolver
    cdebug(3)<<"T"<<Thread::self()<<" grabbing subsolver "<<wt_num_ss_<<endl;
    Subsolver &ss = subsolvers_[wt_num_ss_++];
    // if solver is converged, grab the next one (but do clear its solution vector)
    if( ss.converged )
    {
      ss.solution = 0;
      num_conv_++;
//      cerr<<"processSolversLoop: thread "<<Thread::self()<<" already converged, num_conv "<<num_conv_<<endl;
      continue;
    }
    // release lock to give the other threads a chance to grab their own
    lock.release();
    // process the subsolver
    bool converged = false;
    try
    {
      converged = ss.solve(cur_iter_);
    }
    // break out on error
    catch( std::exception &exc )
    {
      lock.lock(worker_cond_);
      wt_exceptions_.add(exc);
      break;
    }
    // relock worker_cond_
    lock.lock(worker_cond_);
    if( converged )
    {
      num_conv_++;
//      cerr<<"processSolversLoop: thread "<<Thread::self()<<" converged, num_conv "<<num_conv_<<endl;
    }
  }
  // at this point we have a lock on worker_cond
  wt_solve_loop_ = false;
  cdebug(3)<<"T"<<Thread::self()<<" subsolver loop finished"<<endl;
}

void * Solver::workerLoop (int wt_num)
{
  Thread::Mutex::Lock lock(worker_cond_);
  while( true )
  {
    // wait on condition variable until awoken with active subsolvers,
    // or with worker threads being stopped
    while( mt_solve_ && !wt_active_[wt_num] && !wt_flush_tables_ )
      worker_cond_.wait();
    // stop condition
    if( !mt_solve_ )
      return 0;
    // flush parmtables
    if( wt_flush_tables_ )
    {
#ifndef HAVE_PARMDB
      ParmTableUtils::flushTables();
#endif
      wt_flush_tables_ = false;
    }
    // do a solving loop
    if( wt_solve_loop_ )
      processSolversLoop(lock);
    if( wt_active_[wt_num] )
    {
      // release lock, lock exit condition variable, mark ourselves as inactive
      lock.release();
      lock.lock(worker_exit_cond_);
      wt_active_[wt_num] = false;
      int num_active = 0;
      for( uint i=0; i<wt_active_.size(); i++ )
        if( wt_active_[i] )
          num_active++;
//      cerr<<"Thread "<<Thread::self()<<" exiting: "<<num_active<<" threads still active"<<endl;
      if( !num_active )
        worker_exit_cond_.broadcast();
      // reacquire lock on condition variable
      lock.release();
      lock.lock(worker_cond_);
    }
  }
}


} // namespace Meq

//# Instantiate the makeNorm template.
#ifndef HAVE_CASACORE
#include <scimath/Fitting/LSQFit2.cc>
template void casa::LSQFit::makeNorm<double, double*, int*>(unsigned,
int* const&, double* const&, double const&, double const&, bool, bool);
#endif

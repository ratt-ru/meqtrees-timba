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

#include <iostream>

using namespace std;

using namespace casa;

namespace Meq {

InitDebugContext(Solver,"MeqSolver");

const HIID FSolverResult = AidSolver|AidResult;
const HIID FIncrementalSolutions = AidIncremental|AidSolutions;

const HIID FIterationSymdeps = AidIteration|AidSymdeps;
const HIID FIterationDependMask = AidIteration|AidDepend|AidMask;

//##ModelId=400E53550260
Solver::Solver()
: itsSolver          (1),
  itsNrEquations     (0),
  itsDefNumIter      (1),
  itsDefEpsilon      (1e-8),
  itsDefUseSVD       (true),
  itsDefClearMatrix  (true),
  itsDefInvertMatrix (true),
  itsDefSaveFunklets (true),
  itsDefLastUpdate   (false),
  itsParmGroup       (AidParm)
{
  resetCur();
  // Set this flag, so setCurState will be called in first getResult.
  itsResetCur = true;
  // set Solver dependencies
  iter_symdeps_.assign(1,FIteration);
  const HIID symdeps[] = { FDomain,FResolution,FDataset,FIteration };
  setKnownSymDeps(symdeps,4);
  const HIID symdeps1[] = { FDomain,FResolution,FDataset };
  setActiveSymDeps(symdeps1,3);
}

//##ModelId=400E53550261
Solver::~Solver()
{}

//##ModelId=400E53550263
TypeId Solver::objectType() const
{
  return TpMeqSolver;
}

//##ModelId=400E53550265
void Solver::checkChildren()
{
  // count the number of Condeq nodes
  itsNumCondeqs = 0;
  itsIsCondeq.resize(numChildren());
  for (int i=0; i<numChildren(); i++) 
    if( itsIsCondeq[i] = ( getChild(i).objectType() == TpMeqCondeq ) )
      itsNumCondeqs++;
  FailWhen(!itsNumCondeqs,"Solver node must have at least one Condeq child");
}

// do nothing here -- we'll do it manually in getResult()
//##ModelId=400E5355026B
int Solver::pollChildren (std::vector<Result::Ref> &chres,
                          Result::Ref &resref,const Request &request)
{
  // a request that has cells in it is a solve request -- do not pass it to the
  // children, as we'll be doing our own polling in getResult() below
  if( request.hasCells() )
    return 0;
  // A cell-less request contains commands and states only, and thus it should
  // passed on to the children as is. (This request will never make it to our
  // getResult())
  else
    return Node::pollChildren(chres,resref,request);
}

// Process rider for the given request
// (this will be called prior to getResult() on the same request)
int Solver::processCommands (const DMI::Record &rec,Request::Ref &reqref)
{
  const Request &request = *reqref;
  int retcode = Node::processCommands(rec,reqref); // required
  // Get new current values (use default if not given).
  itsCurNumIter   = rec[FNumIter].as<int>(itsDefNumIter);
  if (itsCurNumIter < 1) itsCurNumIter = 1;
  itsCurEpsilon   = rec[FEpsilon].as<double>(itsDefEpsilon);
  itsCurUseSVD    = rec[FUseSVD].as<bool>(itsDefUseSVD);
  itsCurSaveFunklets = rec[FSaveFunklets].as<bool>(itsDefSaveFunklets);
  itsCurLastUpdate = rec[FLastUpdate].as<bool>(itsDefLastUpdate);
  bool clearGiven  = rec[FClearMatrix].get(itsCurClearMatrix);
  bool invertGiven = rec[FInvertMatrix].get(itsCurInvertMatrix);
  // Take care that these current values are used in getResult (if called).
  itsResetCur = false;
  cdebug(1)<<"Solver rider: "
           <<itsCurNumIter<<','
           <<itsCurEpsilon<<','
           <<itsCurUseSVD<<','
           <<clearGiven<<':'<<itsCurClearMatrix<<','
           <<invertGiven<<':'<<itsCurInvertMatrix<<','
           <<itsCurSaveFunklets<<','
           <<itsCurLastUpdate<<endl;
  // Update wstate.
  setCurState();
  // getResult won't be called if the request has no cells.
  // So process here if clear or invert has to be done.
  if (! request.hasCells()) {
    // Remove all spids if the matrix has to be cleared.
    if (clearGiven && itsCurClearMatrix) {
      itsSpids.clear();
    } else if (invertGiven && itsCurInvertMatrix) {
      Vector<double> solution(itsSpids.size());
      DMI::Record::Ref solRef;
      DMI::Record& solRec = solRef <<= new DMI::Record;
      std::vector<Result::Ref> child_results;
      Result::Ref resref;
      solve(solution,reqref,solRec,resref,child_results,
            false,true);
    }
    // Take care that current gets reset to default if no
    // processCommands is called for the next getResult.
    itsResetCur = true;
  }
  return retcode;
}

// Get the result for the given request.
//##ModelId=400E53550270
int Solver::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &,
                       const Request &request, bool newreq)
{
  // a cell-less request contains commands and states only, and thus it should
  // passed on to the children as is (since we override pollChildren() to do
  // nothing) ad nothing else done
  if( !request.hasCells() )
  {
    return Node::pollChildren(child_results_,resref,request);
  }
  // Reset current values if needed.
  // That is possible if a getResult is done without a processCommands
  // (thus without a rider in the request).
  if (itsResetCur) {
    resetCur();
    setCurState();
  }
  // Use single derivative by default, or higher mode if specified in request
  int eval_mode = std::max(request.evalMode(),int(Request::DERIV_SINGLE));
  // The result has 1 plane.
  Result& result = resref <<= new Result(0);
//  VellSet& vellset = result.setNewVellSet(0);
  DMI::Record &solveResult = result[FSolverResult] <<= new DMI::Record;
  DMI::Vec& metricsList = solveResult[FMetrics] <<= new DMI::Vec(TpDMIRecord,1);
  // Allocate variables needed for the solution.
  uint nspid = 0;
  vector<int> spids;
  Vector<double> solution;
  std::vector<Thread::Mutex::Lock> child_reslock(numChildren());
  // get the request ID -- we're going to be incrementing the part of it 
  // corresponding to our symdeps
  RequestId rqid = request.id();
  RqId::setSubId(rqid,iter_depmask_,0);
  RequestId next_rqid = rqid;
  RqId::incrSubId(next_rqid,iter_depmask_);
  // Create a new request and attach the solvable parm specification if needed.
  // We'll keep the request object via reference; note that
  // solve()/fillSolution() may subsequently create new request objects
  // and attach them to this ref; so we can't just say Request &req = reqref()
  // and use req from then on, as the request object is likely to change.
  // Instead, all operations will go via the ref.
  Request::Ref reqref;
  reqref <<= new Request(request.cells(),Request::DISCOVER_SPIDS,rqid);
  // rider of original request gets sent up the first time
  reqref().copyRider(request);
  reqref().setServiceFlag(true);
  if( state()[FSolvable].exists() ) {
    DMI::Record& rider = Rider::getRider(reqref);
    rider[itsParmGroup].replace() <<= wstate()[FSolvable].as_wp<DMI::Record>();
  } else {
    // no solvables specified -- clear the group record
    Rider::getGroupRec(reqref,itsParmGroup,Rider::NEW_GROUPREC);
  }
  reqref().validateRider();
  // send up request to figure out spids
  int retcode = Node::pollChildren(child_results_,resref,*reqref);
  if( retcode&(RES_FAIL|RES_WAIT) )
    return retcode;
  // merge all child spids together using Node's standard function
  Result::Ref tmpres;
  Node::discoverSpids(tmpres,child_results_,*reqref);
  // ok, now we should have a spid map:
  const DMI::Record * spid_map = tmpres[FSpidMap].as_po<DMI::Record>();
  if( spid_map )
  {
    // for the time being, just stuff it into our state record
    wstate()[FSpidMap].replace() <<= spid_map;
  }
  else
  {
    // no spids discovered, so may as well fail...
    Throw("no spids discovered by this solver");
  }
  // clear everything from the request and set eval mode properly
  reqref().setServiceFlag(false);
  reqref().clearRider();
  reqref().setEvalMode(eval_mode);
  // Take care that the matrix is cleared if needed.
  if (itsCurClearMatrix) 
      itsSpids.clear();
  // Iterate as many times as needed.
  // matrix of solutions kept here
  LoMat_double allSolutions;
  int step;
  for (step=0; step<itsCurNumIter; step++) 
  {
    // increment the solve-dependent parts of the request ID
    rqid = next_rqid;
    RqId::incrSubId(next_rqid,iter_depmask_);
    reqref().setId(rqid);
    reqref().setNextId(next_rqid);
    // clear/unlock child results
    for( int i=0; i<numChildren(); i++ )
    {
	    child_reslock[i].release();
      child_results_[i].detach();
    }
    int retcode = Node::pollChildren(child_results_, resref, *reqref);
    // tell children to only hold cache if it doesn't depend on iteration
    holdChildCaches(true,iter_depmask_);
    
    setExecState(CS_ES_EVALUATING);
    for( int i=0; i<numChildren(); i++ )
      if( child_results_[i].valid() )
        child_reslock[i].relock(child_results_[i]->mutex());
    // a fail or a wait is returned immediately
    if( retcode&(RES_FAIL|RES_WAIT) )
      return retcode;
    // else process 
    vector<const VellSet*> chvellsets;
    chvellsets.reserve(numChildren() * child_results_[0]->numVellSets());
    // Find the set of all spids from all condeq results.
    for (uint i=0; i<child_results_.size(); i++)
      if( itsIsCondeq[i] )
      {
        for (int iplane=0; iplane<child_results_[i]->numVellSets(); iplane++) 
        {
          if (! child_results_[i]->vellSet(iplane).isFail()) 
          {
            chvellsets.push_back (&(child_results_[i]->vellSet(iplane)));
          }
        }
      }
    int npertsets;
    spids = Function::findSpids (npertsets,chvellsets);
    nspid = spids.size();
    // It first time, initialize the solver.
    // Otherwise check if spids are still the same and initialize
    // solver for the 2nd step and so.
    if (itsSpids.empty()) {
      AssertStr( nspid > 0,
                 "No solvable parameters found in solver " << name() );
      itsSolver.set (nspid);
      itsNrEquations = 0;
      itsSpids = spids;
    } else {
      AssertStr( itsSpids == spids,
                 "Different spids while solver is not restarted" );
      if (step > 0) {
        itsNrEquations = 0;
      }
    }
    
    // Now feed the solver with equations from the results.
    // Define the vector with derivatives (for real and imaginary part).
    vector<double> derivReal(nspid);
    vector<double> derivImag(nspid);

    // To be used as an index array for quickly feeding the equations
    // to the solver.
    vector<int>    derivIndex(nspid);
    
    // Loop through all results and fill the deriv vectors.
    for (uint i=0; i<chvellsets.size(); i++) {
      const VellSet& chresult = *chvellsets[i];
      bool isReal = chresult.getValue().isReal();

      // Get nr of elements in the values.
      int nrval = chresult.getValue().nelements();

      // Get pointer to all perturbed values.
      int index=0;
      
      const VellsFlagType* isFlagged=0;
      bool hasFlags = chresult.hasDataFlags();
      
      if(hasFlags){
        AssertStr( chresult.dataFlags().nelements() == nrval,"Number of flags is not equal to number of data points");
        isFlagged = chresult.dataFlags().begin<VellsFlagType>();
      }


      if (isReal) {
        //------------ If Real -----------

        const double* values = chresult.getValue().realStorage();
        vector<const double*> perts(nspid, 0);
        for (uint j=0; j<nspid; j++) {
          int inx = chresult.isDefined (spids[j], index);
          if (inx >= 0) {
            Assert(chresult.getPerturbedValue(inx).nelements() == nrval);
            perts[j] = chresult.getPerturbedValue(inx).realStorage();
          }
        }// for j...
       
        
        // Generate an equation for each value element.
        // An equation contains the value and all derivatives.
        for (int j=0; j<nrval; j++) {
          if(!hasFlags || (hasFlags && !isFlagged[j])){
            int numDerivatives=0;
            for (uint spid=0; spid<perts.size(); spid++) {
              if (perts[spid]) {
                derivReal[numDerivatives] = perts[spid][j];
                derivIndex[numDerivatives] = spid;
                numDerivatives++;
              }
            }// for spid...

            
            //====  THE EQUATION  ===
            itsSolver.makeNorm (numDerivatives, &derivIndex[0], &derivReal[0], 1., values[j]);
            itsNrEquations++;


          }// if not flagged
        } // for j...
        
      } else {
      //------------ If Complex ------------

        const dcomplex* values = chresult.getValue().complexStorage();
        vector<const dcomplex*> perts(nspid, 0);
        for (uint j=0; j<nspid; j++) {
          int inx = chresult.isDefined (spids[j], index);
          if (inx >= 0) {
            Assert(chresult.getPerturbedValue(inx).nelements() == nrval );
            perts[j] = chresult.getPerturbedValue(inx).complexStorage();
          }
        }
        // Generate an equation for each value element.
        // An equation contains the value and all derivatives.
        double val;
        for (int j=0; j<nrval; j++) {
          if(!hasFlags || (hasFlags && !isFlagged[j])){
            int numDerivatives=0;
            for (uint spid=0; spid<perts.size(); spid++) {
              if (perts[spid]) {
                derivReal[numDerivatives] = perts[spid][j].real();
                derivImag[numDerivatives] = perts[spid][j].imag();
                derivIndex[numDerivatives] = spid;
                numDerivatives++;
              }
            }// for spid...

            //====  THE EQUATIONS  ====
            val = values[j].real();
            itsSolver.makeNorm (numDerivatives, &derivIndex[0],
                                &derivReal[0], 1., val);
            itsNrEquations++;

            val = values[j].imag();
            itsSolver.makeNorm (numDerivatives, &derivIndex[0],
                                &derivImag[0], 1., val);
            itsNrEquations++;


          } // if not Flagged
        } // For j...

      }// If isReal / else

    }// Loop over VellSets


    // Size the solutions vector.
    // Fill it with zeroes and stop if no invert will be done.
    if (step == itsCurNumIter-1  &&  !itsCurInvertMatrix) {
      if (step == 0) {
        allSolutions.resize(1,nspid);
        allSolutions = 0.;
      }
      break;
    }
    solution.resize(nspid);
    // Solve the equation.
    DMI::Record& solRec = metricsList[step] <<= new DMI::Record;
    // request for last iteration is processed separately
    bool lastIter = itsCurLastUpdate && step==itsCurNumIter-1;
    solve(solution, reqref, solRec, resref, child_results_,
          itsCurSaveFunklets,lastIter);
    // send up one final update if needed
    if( lastIter )
    {
      // increment the solve-dependent parts of the request ID one last time
      Request &lastreq = reqref <<= new Request;
      RqId::incrSubId(rqid,iter_depmask_);
      lastreq.setId(rqid);
      lastreq.setServiceFlag(True);
      lastreq.setNextId(request.nextId());
      ParmTable::lockTables();
      // unlock all child results
      for( int i=0; i<numChildren(); i++ )
      {
	      child_reslock[i].release();
        child_results_[i].detach();
      }
      Node::pollChildren(child_results_, resref, lastreq);
    }
    // Unlock all parm tables used.
    ParmTable::unlockTables();
    // copy solutions vector to allSolutions row
    allSolutions.resizeAndPreserve(step+1,nspid);
    allSolutions(step,LoRange::all()) = B2A::refAipsToBlitz<double,1>(solution);
  }
  // Put the spids in the result.
  solveResult[FSpids] = spids;
  solveResult[FIncrementalSolutions] = new DMI::NumArray(allSolutions);
  return 0;
}








//====================>>>  Solver::solve  <<<====================

void Solver::solve (Vector<double>& solution,Request::Ref &reqref,
                    DMI::Record& solRec, Result::Ref& resref,
                    std::vector<Result::Ref>& child_results,
                    bool saveFunklets, bool lastIter)
{
  // Do some checks and initialize.
  int nspid = itsSpids.size();
  Assert(int(solution.nelements()) == nspid);
  ///  AssertStr(itsNrEquations >= nspid, "Only " << itsNrEquations
  ///             << " equations for "
  ///             << nspid << " solvable parameters in solver " << name());
  solution = 0;
  if (lastIter) 
  {
    // generate a command-only (no cells) request for the last update
    reqref <<= new Request;
    reqref[FRider] <<= new DMI::Record;
  }
  Request &req = reqref();
  req.clearRider();
  // It looks as if in LSQ solveLoop and getCovariance
  // interact badly (maybe both doing an invert).
  // So make a copy to separate them.
  uint rank;
  double fit;
  Matrix<double> covar;
  Vector<double> errors;

  // Make a copy of the solver for the actual solve.
  // This is needed because the solver does in-place transformations.
  ////  FitLSQ solver = itsSolver;
  bool solFlag = itsSolver.solveLoop (fit, rank, solution, itsCurUseSVD);

  // {
  LSQaips tmpSolver(itsSolver);
    // both of these calls produce SEGV in certain situations; commented out until
    // Wim or Ger fixes it
    //cdebug(1) << "result_covar = itsSolver.getCovariance (covar);" << endl;
    //bool result_covar = itsSolver.getCovariance (covar);
   //cdebug(1) << "result_errors = itsSolver.getErrors (errors);" << endl;
   bool result_errors = tmpSolver.getErrors (errors);
    //cdebug(1) << "result_errors = " << result_errors << endl;
 // }
  
  
  cdebug(4) << "Solution after:  " << solution << endl;
  // Put the statistics in a record the result.
  solRec[FRank]   = int(rank);
  solRec[FFit]    = fit;
  solRec[FErrors] = errors;
  //solRec[FCoVar ] = covar; 
  solRec[FFlag]   = solFlag; 
  solRec[FMu]     = itsSolver.getWeightedSD();
  solRec[FStdDev] = itsSolver.getSD();
  //  solRec[FChi   ] = itsSolver.getChi());
  
  // Put the solution in the rider:
  //    [FRider][<parm_group>][CommandByNodeIndex][<parmid>]
  // will contain a DMI::Record for each parm 
  DMI::Record& dr1 = Rider::getCmdRec_ByNodeIndex(reqref,itsParmGroup,
                                                 Rider::NEW_GROUPREC);
  fillSolution (dr1,itsSpids, solution, saveFunklets);
  // make sure the request rider is validated
  req.validateRider();
  ParmTable::unlockTables();
}












//##ModelId=400E53550276
void Solver::fillSolution (DMI::Record& rec, const vector<int>& spids,
                           const Vector<double>& solution, bool save_polc)
{
  // Split the solution into vectors for each parm.
  // Reserve enough space in the vector.
  vector<double> parmSol;
  uint nspid = spids.size();
  parmSol.reserve (nspid);
  int lastParmid = spids[0] / 256;
  for (uint i=0; i<nspid; i++) {
    if (spids[i]/256 != lastParmid) {
      DMI::Record& drp = rec[lastParmid] <<= new DMI::Record;
      drp[FUpdateValues] = parmSol;
      lastParmid = spids[i] / 256;
      parmSol.resize(0);
      if( save_polc )
        drp[FSaveFunklets] = true;
    }
    parmSol.push_back (solution[i]);
  }
  DMI::Record& drp = rec[lastParmid] <<= new DMI::Record;
  drp[FUpdateValues] = parmSol;
  if( save_polc )
    drp[FSaveFunklets] = true;
}

//##ModelId=400E53550267
void Solver::setStateImpl (DMI::Record::Ref & newst,bool initializing)
{
  Node::setStateImpl(newst,initializing);
  // get the parm group
  newst[FParmGroup].get(itsParmGroup,initializing);
  // get symdeps for iteration and solution
  // recompute depmasks if active sysdeps change
  if( newst[FIterationSymdeps].get_vector(iter_symdeps_,initializing) || initializing )
    wstate()[FIterationDependMask] = iter_depmask_ = computeDependMask(iter_symdeps_);
  // now reset the dependency mask if specified; this will override
  // possible modifications made above
  newst[FIterationDependMask].get(iter_depmask_,initializing);
  
  // get default solve job description
  DMI::Record *pdef = newst[FDefault].as_wpo<DMI::Record>();
  // if no default record at init time, create a new one
  if( !pdef && initializing )
    newst[FDefault] <<= pdef = new DMI::Record; 
  else
    itsResetCur = true;
  if( pdef )
  {
    DMI::Record &def = *pdef;
    if( def[FNumIter].get(itsDefNumIter,initializing) &&
        itsDefNumIter < 1 )
      def[FNumIter] = itsDefNumIter = 1;
    def[FClearMatrix].get(itsDefClearMatrix,initializing);
    def[FInvertMatrix].get(itsDefInvertMatrix,initializing);
    def[FSaveFunklets].get(itsDefSaveFunklets,initializing);
    def[FLastUpdate].get(itsDefLastUpdate,initializing);
    def[FEpsilon].get(itsDefEpsilon,initializing);
    def[FUseSVD].get(itsDefUseSVD,initializing);
  }
}

void Solver::resetCur()
{
  itsCurNumIter      = itsDefNumIter;
  itsCurInvertMatrix = itsDefInvertMatrix;
  itsCurClearMatrix  = itsDefClearMatrix;
  itsCurSaveFunklets    = itsDefSaveFunklets;
  itsCurLastUpdate   = itsDefLastUpdate;
  itsCurEpsilon      = itsDefEpsilon;
  itsCurUseSVD       = itsDefUseSVD;
  itsResetCur = false;
}

void Solver::setCurState()
{
  wstate()[FNumIter]      = itsCurNumIter;
  wstate()[FClearMatrix]  = itsCurClearMatrix;
  wstate()[FInvertMatrix] = itsCurInvertMatrix;
  wstate()[FSaveFunklets]    = itsCurSaveFunklets;
  wstate()[FLastUpdate]   = itsCurLastUpdate;
  wstate()[FEpsilon]      = itsCurEpsilon;
  wstate()[FUseSVD]       = itsCurUseSVD;
}

} // namespace Meq

//# Instantiate the makeNorm template.
#include <scimath/Fitting/LSQFit2.cc>
template void casa::LSQFit::makeNorm<double, double*, int*>(unsigned,
int* const&, double* const&, double const&, double const&, bool, bool);


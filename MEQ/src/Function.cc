//# Function.cc: Base class for an expression node
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

#include "Function.h"
#include "Request.h"
    

namespace Meq {

using Debug::ssprintf;

Function::Function()
{}

Function::~Function()
{}

TypeId Function::objectType() const
{
  return TpMeqFunction;
}

void Function::checkChildren()
{
  if (itsChildren.size() == 0) {
    int nch = numChildren();
    itsChildren.resize (nch);
    for (int i=0; i<nch; i++) {
      itsChildren[i] = &(getChild(i));
    }
  }
}

bool Function::convertChildren (int nchild)
{
  if (itsChildren.size() > 0) {
    return false;
  }
  testChildren(nchild);
  Function::checkChildren();
  return true;
 }

bool Function::convertChildren (const vector<HIID>& childNames, int nchild)
{
  if (itsChildren.size() > 0) {
    return false;
  }
  if (nchild == 0) {
    nchild = childNames.size();
  }
  testChildren(nchild);
  int nch = numChildren();
  itsChildren.resize (nch);
  int nhiid = childNames.size();
  // Do it in order of the HIIDs given.
  for (int i=0; i<nhiid; i++) {
    itsChildren[i] = &(getChild(childNames[i]));
  }
  // It is possible that there are more children than HIIDs.
  // In that case the remaining children are appended at the end.
  if (nch > nhiid) {
    int inx = nhiid;
    for (int i=0; i<nch; i++) {
      Node * ptr = &(getChild(childNames[i]));
      bool fnd = false;
      for (int j=0; j<nhiid; j++) {
	if (ptr == itsChildren[j]) {
	  fnd = true;
	}
      }
      if (!fnd) {
	itsChildren[inx++] = ptr;
      }
    }
  }
  return true;
}

void Function::testChildren (int nchild) const
{
  if (nchild > 0) {
    FailWhen(numChildren()!=nchild,
        Debug::ssprintf("node has %d children, requires %d",numChildren(),nchild));
  } else if (nchild < 0) {
    FailWhen(numChildren() <= -nchild,
        Debug::ssprintf("node has %d children, requires at least %d",numChildren(),-nchild+1));
  }
}

void Function::testChildren (const vector<TypeId>& types) const
{
  int nch = std::min (types.size(), itsChildren.size());
  for (int i=0; i<nch; i++) {
    AssertStr (itsChildren[i]->objectType() == types[i],
	       "expected type " << types[i] << ", but found "
	       << itsChildren[i]->objectType());
  }
}

int Function::getResultImpl (ResultSet::Ref &resref, const Request& request, bool)
{
  int nrch = itsChildren.size();
  FailWhen(nrch<=0,"node has no children" );
  vector<ResultSet::Ref> child_results;
  // collect child_results from children
  int flag = getChildResults(child_results,request);
  // return flag is at least one child wants to wait. If all children have 
  // failed, continue anyway: fails will be collected below.
  if( flag != Node::RES_FAIL && flag&Node::RES_WAIT) 
    return flag;
  // figure out the number of child planes
  int nplanes = child_results[0]->numResults();
  for( int i=1; i<nrch; i++ )
    nplanes = std::max(nplanes,child_results[i]->numResults());
  // Create result set and attach to the ref that was passed in
  ResultSet & resultset = resref <<= new ResultSet(request,nplanes);
//  resultset.setCells(request.cells());
  vector<Result*> child_res(nrch);
  vector<Vells*>  values(nrch);
  int nfails = 0;
  for( int iplane = 0; iplane < nplanes; iplane++ )
  {
    // initialize result for this plane
    Result &result = resultset.setNewResult(iplane);
    // collect vector of pointers to child results, and vector of pointers 
    // to main value. If some child is out of results, generate a fail. If 
    // any child results are fails, collect them for propagation
    for( int i=0; i<nrch; i++ )
    {
      if( iplane >= child_results[i]->numResults() )
      {
        MakeFailResult(result,ssprintf("child %d: not enough result planes",child_results[i]->numResults()));
      }
      else 
      {
        child_res[i] = &(child_results[i]().result(iplane));
        if( child_res[i]->isFail() ) 
        { // collect fails from child result
          for( int j=0; j<child_res[i]->numFails(); j++ )
            result.addFail(&child_res[i]->getFail(j));
        }
        else
          values[i] = &(child_res[i]->getValueRW());
      }
    }
    // continue evaluation only if no fails popped up
    if( !result.isFail() )
    {
      // catch exceptions during evaluation and stuff them into fails
      try
      {
        // Find all spids from the children.
        vector<int> spids = findSpids(child_res);
        // allocate new result object with given number of spids, add to set
        result.setSpids(spids);
        // Evaluate the main value.
        LoShape shape = resultShape(values);
        result.setValue(evaluate(request,shape,values));
        // Evaluate all perturbed values.
        vector<Vells*> perts(nrch);
        vector<int> indices(nrch, 0);
        for (unsigned int j=0; j<spids.size(); j++) 
        {
          perts = values;
          for (int i=0; i<nrch; i++) 
          {
            int inx = child_res[i]->isDefined (spids[j], indices[i]);
            if (inx >= 0) {
	            perts[i] = &(child_res[i]->getPerturbedValueRW(inx));
            }
          }
          result.setPerturbedValue(j,evaluate(request,shape,values));
        }
      }
      catch( std::exception &x )
      {
        MakeFailResult(result,
            string("exception occurred while evaluating a Function node getResult: ")
            + x.what());
      }
    }
    // count the # of fails
    if( result.isFail() )
      nfails++;
  }
  // return RES_FAIL is all planes have failed
  if( nfails == nplanes )
    return RES_FAIL;
  return flag;
}

LoShape Function::resultShape (const vector<Vells*>& values)
{
  Assert (values.size() > 0);
  int nx = values[0]->nx();
  int ny = values[0]->ny();
  for (unsigned int i=0; i<values.size(); i++) {
    nx = std::max(nx, values[i]->nx());
    ny = std::max(ny, values[i]->ny());
  }
  return makeLoShape(nx,ny);
}

void Function::evaluateVells (Vells&, const Request&, const vector<Vells*>&)
{
  AssertMsg (false, "evaluate or getResultImpl not implemented in class "
	     "derived from MeqFunction");
}

vector<int> Function::findSpids (const vector<Result*> &results) const
{
  // Determine the maximum number of spids.
  int nrspid = 0;
  int nrch = results.size();
  for (int i=0; i<nrch; i++) {
    nrspid += results[i]->getNumSpids();
  }
  // Allocate a vector of that size.
  // Exit immediately if nothing to be done.
  vector<int> spids(nrspid);
  if (nrspid == 0) {
    return spids;
  }
  // Merge all spids by doing that child by child.
  // The merged spids are stored from the end of the spids vector, so
  // eventually all resulting spids are at the beginning of the vector.
  int stinx = nrspid;          // start at end
  nrspid = 0;                  // no resulting spids yet
  // Loop through all children.
  for (int ch=0; ch<nrch; ch++) {
    const Result &resch = *results[ch];
    int nrchsp = resch.getNumSpids();
    if (nrchsp > 0) {
      // Only handle a child with spids.
      // Get a direct pointer to its spids (is faster).
      int inx = stinx;       // index where previous merge result starts.
      int lastinx = inx + nrspid;
      stinx -= nrchsp;       // index where new result is stored.
      int inxout = stinx;
      int lastspid = -1;
      // Loop through all spids of the child.
      for (int i=0; i<nrchsp; i++) {
	      // Copy spids until exceeding current child's spid.
        int spid = resch.getSpid(i);
        while (inx < lastinx  &&  spids[inx] <= spid) {
          lastspid = spids[inx++];
          spids[inxout++] = lastspid;
	      }
        // Only store child's spid if different.
	      if (spid != lastspid) {
          spids[inxout++] = spid;
        }
      }
      // Copy possible remaining spids.
      while (inx < lastinx) {
        spids[inxout++] = spids[inx++];
      }
      nrspid = inxout - stinx;
    }
  }
  spids.resize(nrspid);
  return spids;
}

} // namespace Meq

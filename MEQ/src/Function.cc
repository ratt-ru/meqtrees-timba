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

int Function::getResult (Result::Ref &resref,
                         const std::vector<Result::Ref> &childres,
                         const Request &request,bool)
{
  // figure out the max number of child planes
  int nrch = numChildren();
  Assert(nrch>0);
  int nplanes = childres[0]->numVellSets();
  for( int i=1; i<nrch; i++ )
    nplanes = std::max(nplanes,childres[i]->numVellSets());
  // Create result and attach to the ref that was passed in
  Result & result = resref <<= new Result(request,nplanes);
  vector<VellSet*> child_vs(nrch);
  vector<Vells*>  values(nrch);
  int nfails = 0;
  for( int iplane = 0; iplane < nplanes; iplane++ )
  {
    // create a vellset for this plane
    VellSet &vellset = result.setNewVellSet(iplane);
    // collect vector of pointers to child vellsets #iplane, and a vector of 
    // pointers to their main values. If a child has fewer vellsets, generate 
    // a fail -- unless the child returned exactly 1 vellset, in which
    // case it is reused repeatedly. If any child vellsets are fails, collect 
    // them for propagation
    for( int i=0; i<nrch; i++ )
    {
      int nvs = childres[i]->numVellSets();
      if( nvs != 1 && iplane >= nvs )
      {
        MakeFailVellSet(vellset,ssprintf("child %d: only %d vellsets",i,nvs));
      }
      else 
      {
        child_vs[i] = &(childres[i]().vellSet(nvs==1?0:iplane));
        if( child_vs[i]->isFail() ) 
        { // collect fails from child vellset
          for( int j=0; j<child_vs[i]->numFails(); j++ )
            vellset.addFail(&child_vs[i]->getFail(j));
        }
        else
          values[i] = &(child_vs[i]->getValueRW());
      }
    }
    // continue evaluation only if no fails popped up
    if( !vellset.isFail() )
    {
      // catch exceptions during evaluation and stuff them into fails
      try
      {
        // Find all spids from the children.
        vector<int> spids = findSpids(child_vs);
        // allocate new vellset object with given number of spids, add to set
        vellset.setSpids(spids);
        // Evaluate the main value.
        LoShape shape = resultShape(values);
        vellset.setValue(evaluate(request,shape,values).makeNonTemp());
        // Evaluate all perturbed values.
        vector<Vells*> perts(nrch);
        vector<int> indices(nrch, 0);
        for (unsigned int j=0; j<spids.size(); j++) 
        {
          double perturbation;
          perts = values;
          for (int i=0; i<nrch; i++) 
          {
            int inx = child_vs[i]->isDefined(spids[j], indices[i]);
            if (inx >= 0) {
	            perts[i] = &(child_vs[i]->getPerturbedValueRW(inx));
              perturbation = child_vs[i]->getPerturbation(inx);
            }
          }
          vellset.setPerturbedValue(j,evaluate(request,shape,perts).makeNonTemp());
          vellset.setPerturbation(j,perturbation);
        }
      }
      catch( std::exception &x )
      {
        MakeFailVellSet(vellset,
            string("exception in Function::getResult: ")
            + x.what());
      }
    } // endif( !vellset.isFail() )
    // count the # of fails
    if( vellset.isFail() )
      nfails++;
  }
  // return RES_FAIL is all planes have failed
  if( nfails == nplanes )
    return RES_FAIL;
  // return 0 flag, since we don't add any dependencies of our own
  return 0;
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
  AssertMsg (false, "evaluate or getResult not implemented in class "
	     "derived from MeqFunction");
}

vector<int> Function::findSpids (const vector<VellSet*> &results)
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
    const VellSet &resch = *results[ch];
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

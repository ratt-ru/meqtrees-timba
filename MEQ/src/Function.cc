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

#include <MEQ/Function.h>
    

namespace MEQ {

Function::Function()
{}

Function::~Function()
{}

void Function::init (DataRecord::Ref::Xfer& initrec)
{
}

void Function::setState (const DataRecord& rec)
{
}

string Function::sdebug (int detail, const string& prefix,
			 const char* name) const
{
  return Node::sdebug (detail, prefix, name);
}

int Function::getResult (Result::Ref &resref, const Request& request)
{
  int nrch = itsChildren.size();
  vector<Result::Ref> results;
  int flag = 0;
  for (int i=0; i<nrch; i++) {
    Result* res = new Result();
    results.push_back (Result::Ref(res, DMI::WRITE||DMI::ANON));
    flag |= itsChildren[i]->getResult (results[i], request);
    results[i].persist();
  }
  if (flag & Node::RES_WAIT) {
    return flag;
  }
  // Evaluate the main value.
  // Find all spids from the children.
  vector<int> spids = findSpids (results);
  return flag;
}

Vells Function::evaluate (const Request&, const vector<Vells*>&)
{
  AssertMsg (False, "evaluate or getResult not implemented in class "
	     "derived from MeqFunction");
}

vector<int> Function::findSpids (const vector<Result::Ref>& results) const
{
  // Determine the maximum number of spids.
  int nrspid = 0;
  int nrch = results.size();
  for (int i=0; i<nrch; i++) {
    nrspid += results[i]->getSpids().size();
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
    const vector<int>& chspids = results[ch]->getSpids();
    int nrchsp = chspids.size();
    if (nrchsp > 0) {
      // Only handle a child with spids.
      // Get a direct pointer to its spids (is faster).
      const int* chsp = &(chspids[0]);
      int inx = stinx;       // index where previous merge result starts.
      int lastinx = inx + nrspid;
      stinx -= nrchsp;       // index where new result is stored.
      int inxout = stinx;
      int lastspid = -1;
      // Loop through all spids of the child.
      for (int i=0; i<nrchsp; i++) {
	// Copy spids until exceeding current child's spid.
	int spid = chsp[i];
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
  spids.resize (nrspid);
  return spids;
}

} // namespace MEQ

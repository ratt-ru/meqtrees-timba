//# Freq.cc: Give the frequencies
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

#include <MeqNodes/Freq.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>

namespace Meq {    

const HIID FDomain = AidDomain;

//##ModelId=400E53050214
Freq::Freq()
{ 
  const HIID symdeps[] = { FDomain,FResolution };
  setActiveSymDeps(symdeps,2);
}

//##ModelId=400E53050215
Freq::~Freq()
{}

//##ModelId=400E53050217
void Freq::init (DataRecord::Ref::Xfer &initrec, Forest* frst)
{
  Node::init(initrec,frst);
  FailWhen(numChildren(),"Freq node cannot have children");
}

//##ModelId=400E5305021D
int Freq::getResult (Result::Ref &resref, 
                     const std::vector<Result::Ref> &,
                     const Request &request,bool newreq)
{
  // Get cells.
  const Cells& cells = request.cells();
  int nfreq = cells.ncells(FREQ);
  int ntime = cells.ncells(TIME);
  const LoVec_double &freq = cells.center(FREQ);
  // Create result object and attach to the ref that was passed in.
  resref <<= new Result(1,request);         // 1 plane
  VellSet& vs = resref().setNewVellSet(0);  
  LoMat_double& arr = vs.setReal (nfreq,ntime);
  // Evaluate the main value.
  for( int i=0; i<ntime; i++ ) 
    arr(blitz::Range::all(),i) = freq;
  // result depends on domain; is updated if request is new.
  return 0;
}

} // namespace Meq

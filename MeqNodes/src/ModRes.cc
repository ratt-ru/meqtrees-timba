//# ModRes.cc: modifies request resolutions
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

#include <MeqNodes/ModRes.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/ResampleMachine.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

namespace Meq {

const HIID FFactor = AidFactor;
const HIID FNumCells = AidNum|AidCells;
const HIID FCacheCells = AidCache|AidCells;
const HIID FCacheRequestId = AidCache|AidRequest|AidId;

//##ModelId=400E5355029C
ModRes::ModRes()
: Node(1) // 1 child expected
{
  // our own result depends on domain & resolution
}

//##ModelId=400E5355029D
ModRes::~ModRes()
{}

void ModRes::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
	std::vector<int> numcells;
	if (rec[FNumCells].get_vector(numcells)) {
#ifdef VERBOSE
		cout<<"Initializing "<<numcells.size()<<" Cells ";
		for (int i=0;i<numcells.size();i++) cout<<numcells[i]<<", ";
		cout<<endl;
#endif
		if (numcells.size()>0) {
		do_resample_=1;
		nx_=numcells[0];
		}
		if (numcells.size()>1)
		ny_=numcells[1];
	}
}

int ModRes::pollChildren (std::vector<Result::Ref> &chres,
                          Result::Ref &resref,
                          const Request &request)
{
   if ( do_resample_ && request.hasCells()) {
		//modify request cells
	  //if flag_bit!=0, change the request 
		 Request::Ref newreq(request);
  const Cells &incells = request.cells();

	int nx=incells.center(0).extent(0);
	int ny=incells.center(1).extent(0);
	//determine the resampling to be done
	int nx1=nx_;//(int)((double)nx*flag_density);
	int ny1=ny_;//(int)((double)ny*flag_density);
	//sanity check
	if (nx1<1) nx1=1;
	if (ny1<1) ny1=1;
#ifdef VERBOSE
	cout<<"Resampling Request new size "<<nx1<<" x "<<ny1<<" "<<flag_density<<endl;
#endif
  Cells::Ref outcells1; 
 	Cells &outcells = outcells1<<=new Cells(request.cells().domain(),nx1,ny1);
	//FIXME: can cache the current cells
  newreq().setCells(outcells);
     return Node::pollChildren(chres,resref,newreq);
		} else {
		//do nothing
     return Node::pollChildren(chres,resref,request);
		}
	// will not get here
	return 0;

} 

int ModRes::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &childres,
                       const Request &request,bool)
{
  Assert(childres.size()==1);
  resref=childres[0];
  return 0;
}

} // namespace Meq

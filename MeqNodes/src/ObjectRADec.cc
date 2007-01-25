//# ObjectRADec.cc: Give the frequencies
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
//# $Id: ObjectRADec.cc 3343 2006-04-03 16:02:29Z smirnov $

#include <MeqNodes/ObjectRADec.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

#include <measures/Measures/MBaseline.h>
#include <measures/Measures/MPosition.h>
#include <measures/Measures/MEpoch.h>
#include <measures/Measures/MeasConvert.h>
#include <measures/Measures/MeasTable.h>

using namespace casa;

namespace Meq {    

const HIID FObjName= AidObj|AidName;

ObjectRADec::ObjectRADec()
  : Node(0)
{ 
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

ObjectRADec::~ObjectRADec()
{}

void ObjectRADec::setStateImpl (DMI::Record::Ref& rec, bool initializing)
{
  Node::setStateImpl(rec,initializing);
  rec[FObjName].get(oname_,initializing);
  std::cout<<oname_<<std::endl;
}

int ObjectRADec::getResult (Result::Ref &resref, 
                     const std::vector<Result::Ref> &,
                     const Request &request,bool newreq)
{
  // Get cells.
  const Cells& cells = request.cells();
  // Create result object and attach to the ref that was passed in.
  resref <<= new Result(1);                // 1 plane
  VellSet& vs = resref().setNewVellSet(0);  // create new object for plane 0
  vs.setValue(new Vells(0.));
  resref().setCells(cells);


   Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex

    
    for (int ci=1; ci<12; ci++) {
    MVEpoch dat = 51116.1+ci*30; //days

    MEpoch mdat(dat, MEpoch::Ref(MEpoch::UTC));
    MeasFrame frame;
    frame.set(mdat);
    MDirection::Ref sunr(MDirection::VENUS, frame);
    MDirection sn(sunr);
    MDirection::Convert sc0(sn, MDirection::Ref(MDirection::J2000));
    MDirection::Convert sc1(sn, MDirection::Ref(MDirection::JNAT));
    MDirection::Convert sc2(sn, MDirection::Ref(MDirection::APP));
    std::cout << "Sun   J2000:  " << sc0().getValue().getAngle("deg") << std::endl;
    std::cout << "Sun   JNAT:  " << sc1().getValue().getAngle("deg") << std::endl;
    std::cout << "Sun   APP:  " << sc2().getValue().getAngle("deg") << std::endl;
    }


  // result depends on domain; is updated if request is new.
  return 0;
}

} // namespace Meq

//# ObjectRADec.cc: Give the frequencies
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

#include <MeqNodes/ObjectRADec.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casacore/measures/Measures/MCDirection.h>
#include <casacore/measures/Measures/MBaseline.h>
#include <casacore/measures/Measures/MPosition.h>
#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/MeasConvert.h>
#include <casacore/measures/Measures/MeasTable.h>

using namespace casacore;

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
  if (!oname_.compare("sun") || !oname_.compare("SUN")) {
    type_=MDirection::SUN;
  } else if (!oname_.compare("jupiter") || !oname_.compare("JUPITER")) {
    type_=MDirection::JUPITER;
  } else if (!oname_.compare("moon") || !oname_.compare("MOON")) {
    type_=MDirection::MOON;
  } else if (!oname_.compare("mercury") || !oname_.compare("MERCURY")) {
    type_=MDirection::MERCURY;
  } else if (!oname_.compare("mars") || !oname_.compare("MARS")) {
    type_=MDirection::MARS;
  } else if (!oname_.compare("saturn") || !oname_.compare("SATURN")) {
    type_=MDirection::SATURN;
  } else if (!oname_.compare("uranus") || !oname_.compare("URANUS")) {
    type_=MDirection::URANUS;
  } else if (!oname_.compare("neptune") || !oname_.compare("NEPTUNE")) {
    type_=MDirection::NEPTUNE;
  } else if (!oname_.compare("venus") || !oname_.compare("VENUS")) {
    type_=MDirection::VENUS;
  } else if (!oname_.compare("pluto") || !oname_.compare("PLUTO")) {
    type_=MDirection::PLUTO;
  } else if (!oname_.compare("itrf") || !oname_.compare("ITRF")) {
    type_=MDirection::ITRF;
  } else if (!oname_.compare("topo") || !oname_.compare("TOPO")) {
    type_=MDirection::TOPO;
  } else {
    type_=MDirection::J2000;
  }
}

int ObjectRADec::getResult (Result::Ref &resref, 
                     const std::vector<Result::Ref> &,
                     const Request &request,bool newreq)
{
  // Get cells.
  const Cells& cells = request.cells();

  FailWhen(!cells.isDefined(Axis::TIME),"Meq::ObjectRADec: no time axis in request, can't compute RA,Dec");
  Vells::Shape shape(cells.shape());
  //collapse all but time axis
  int ntime=shape[Axis::TIME];
  for (unsigned int ci=0;ci<shape.size();ci++) {
   shape[ci]=1;
  }
  shape[Axis::TIME]=ntime;

  // Create result object and attach to the ref that was passed in.
  resref <<= new Result(2);                // 1: RA, 2: Dec
  VellSet& vs0 = resref().setNewVellSet(0);  
  vs0.setValue(new Vells(0.,shape));
  VellSet& vs1 = resref().setNewVellSet(1); 
  vs1.setValue(new Vells(0.,shape));
  resref().setCells(cells);


  double tscale=1/(3600.0*24.0);
   Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex


    double *ra=(const_cast<Vells&>(vs0.getValue())).realStorage();
    double *dec=(const_cast<Vells&>(vs1.getValue())).realStorage();
    const blitz::Array<double,1> arrtime=cells.center(Axis::TIME);

    Quantum<double> qepoch(arrtime(0)*tscale, "d");
    MVEpoch dat(qepoch); //days
    MEpoch mdat(dat, MEpoch::Ref(MEpoch::UTC));
    MeasFrame frame;
    frame.set(mdat);
    MDirection::Ref sunr(type_, frame);
    MDirection sn(sunr);
    MDirection::Convert sc0(sn, MDirection::Ref(MDirection::J2000));
    //MDirection::Ref sunr(MDirection::MOON, frame);
    for (int ci=0; ci<ntime; ci++) {
      qepoch.setValue(arrtime(ci)*tscale);
      dat=qepoch;
      mdat.set(dat);
      frame.set(mdat);
      MDirection sc(sc0());
      //std::cout << "OBJ J2000:  " << sc.getValue().getAngle("deg") << std::endl;
      Vector<Double> radec=sc.getValue().getAngle("rad").getValue();
      ra[ci]=radec(0);
      dec[ci]=radec(1);
    }

  // result depends on domain; is updated if request is new.
  return 0;
}

} // namespace Meq

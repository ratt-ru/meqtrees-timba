//# AzEl.cc: Calculate AzEl from J2000 ra, dec
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

#include <MeqNodes/AzEl.h>
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
#include <casa/Quanta/MVuvw.h>

using namespace casa;

namespace Meq {
  
const HIID FObservatory = AidObservatory;

const HIID child_labels[] = { AidRA,AidDec};
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

const HIID FDomain = AidDomain;

InitDebugContext(AzEl,"MeqAzEl");


AzEl::AzEl()
: Function(num_children,child_labels)
{
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
// obs_name_ = "WSRT";
//obs_name_ = "VLA";
  obs_name_ = "";
}

AzEl::~AzEl()
{}

// Obtain an observatory - if a name is supplied
// use a 'global observatory position' to calculate AzEl.
// Otherwise AzEl will be calculated for individual
// station positions.
void AzEl::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Function::setStateImpl(rec,initializing);
  cdebug(4) << "in setStateImpl "<<endl;
  rec[FObservatory].get(obs_name_,initializing);
  cdebug(4) << "observatory name:  " << obs_name_ << endl;
}

int AzEl::getResult (Result::Ref &resref, 
                    const std::vector<Result::Ref> &childres,
                    const Request &request,bool newreq)
{
  // Check that child results are all OK (no fails, 1 vellset per child)
  string fails;
  for( int i=0; i<num_children; i++ )
  {
    int nvs = childres[i]->numVellSets();
    if( nvs != 1 )
      Debug::appendf(fails,"child %s: expecting single VellsSet, got %d;",
          child_labels[i].toString().c_str(),nvs);
    if( childres[i]->hasFails() )
      Debug::appendf(fails,"child %s: has fails",child_labels[i].toString().c_str());
  }
  if( !fails.empty() )
    NodeThrow1(fails);
  // Get RA and DEC for conversion
  const Vells& vra  = childres[0]->vellSet(0).getValue();
  const Vells& vdec = childres[1]->vellSet(0).getValue();
  // For the time being we only support scalars
  Assert( vra.isScalar() && vdec.isScalar() );

  // create a frame for an Observatory, or a telescope station
  MeasFrame Frame; // create default frame 

  if (obs_name_.size() == 0) {
    // create frame for individual telescope station
    const Vells& vx  = childres[3]->vellSet(0).getValue();
    const Vells& vy  = childres[4]->vellSet(0).getValue();
    const Vells& vz  = childres[5]->vellSet(0).getValue();
    Assert( vx.isScalar() && vy.isScalar() && vz.isScalar() );
    double x0 = vx.getScalar<double>();
    double y0 = vy.getScalar<double>();
    double z0 = vz.getScalar<double>();
    MPosition stnpos(MVPosition(x0,y0,z0),MPosition::ITRF);
    Frame.set(stnpos); // tie this frame to station position
  } else {
    // create frame for an observatory
    MPosition Obs;
    MeasTable::Observatory(Obs,obs_name_);
    Frame.set(Obs);  // tie this frame to a known observatory
  }  

  const Cells& cells = request.cells();
  // Allocate a 2-plane result for Az and El
  Result &result = resref <<= new Result(2);
  // Get RA and DEC of location to be transformed to AzEl (default is J2000).
  // assume input ra and dec are in radians
  MVDirection sourceCoord(vra.getScalar<double>(),vdec.getScalar<double>());

  FailWhen(!cells.isDefined(Axis::TIME),"Meq::AzEl: no time axis in request, can't compute AzEl");
  int ntime = cells.ncells(Axis::TIME);
  const LoVec_double & time = cells.center(Axis::TIME);
  Axis::Shape shape = Axis::vectorShape(Axis::TIME,ntime);
  double * Az = result.setNewVellSet(0).setReal(shape).realStorage();
  double * El = result.setNewVellSet(1).setReal(shape).realStorage();
  Quantum<double> qepoch(0, "s");
  qepoch.setValue(time(0));
  MEpoch mepoch(qepoch, MEpoch::UTC);
  Frame.set (mepoch);
  for( int i=0; i<ntime; i++) 
  {
    qepoch.setValue (time(i));
    mepoch.set (qepoch);
    Frame.set (mepoch);
    // convert ra, dec to Az El at given time
    MDirection az_el_out(MDirection::Convert(sourceCoord,MDirection::Ref(MDirection::AZEL,Frame))());
    //Gawd - what a mouthfull - luckily some old ACSIS code provided the
    //rigth incantation for the following line!
    Vector<Double> az_el = az_el_out.getValue().getAngle("rad").getValue();
    Az[i] = az_el(0);
    El[i] = az_el(1);
  }
  resref().setCells(cells);
  return 0;
}

} // namespace Meq

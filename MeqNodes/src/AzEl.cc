//# AzEl.cc: Calculate AzEl from J2000 ra, dec
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

#include <MeqNodes/AzEl.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <measures/Measures/MCBaseline.h>
#include <measures/Measures/MCDirection.h>
#include <measures/Measures/MBaseline.h>
#include <measures/Measures/MPosition.h>
#include <measures/Measures/MEpoch.h>
#include <measures/Measures/MeasConvert.h>
#include <measures/Measures/MeasTable.h>
#include <casa/Quanta/MVuvw.h>

using namespace casa;

namespace Meq {
  
const HIID FObservatory = AidObservatory;

const HIID child_labels[] = { AidRADec,AidXYZ };
//const HIID child_labels[] = { AidRA,AidDec};

const HIID FDomain = AidDomain;

//The node should assume that only the first child (RADec) is mandatory
AzEl::AzEl()
: TensorFunction(2,child_labels,1)
{
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

AzEl::~AzEl()
{}

// Obtain an observatory - if a name is supplied
// use a 'global observatory position' to calculate AzEl.
// Otherwise AzEl will be calculated for individual
// station positions.
void AzEl::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);

  if(rec->hasField(FObservatory))
      {
        rec[FObservatory].get(obs_name_,initializing);
      }
}


void AzEl::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &,const Request &request)
{
  // NB: for the time being we only support scalar child results, 
  // and so we ignore the child cells, and only use the request cells
  // (while checking that they have a time axis)
  const Cells &cells = request.cells();
  FailWhen(!cells.isDefined(Axis::TIME),"Meq::AzEl: no time axis in request, can't compute AzEls");
  ref.attach(cells);
}


LoShape AzEl::getResultDims (const vector<const LoShape *> &input_dims)
{
  Assert(input_dims.size()>=1);
  // child 0 (RaDec0): expected 2-vector
  const LoShape &dim0 = *input_dims[0];
  FailWhen(dim0.size()!=1 || dim0[0]!=2,"child '"+child_labels[0].toString()+"': 2-vector expected");
  if( obs_name_.empty() )
    {
      // children 1 (XYZ): expecting 3-vector, if any
      const LoShape &dim1 = *input_dims[1];
      FailWhen(dim1.size()!=1 || dim1[0]!=3,"child '"+child_labels[1].toString()+"': 3-vector expected");
    }
  // result is a 3-vector
  return LoShape(2);
}



void AzEl::evaluateTensors (std::vector<Vells> & out,   
                            const std::vector<std::vector<const Vells *> > &args)
{
  // create a frame for an Observatory, or a telescope station
  MeasFrame Frame; // create default frame 

  // thanks to checks in getResultDims(), we can expect all 
  // vectors to have the right sizes
  // Get RA and DEC, and station positions
  const Vells& vra  = *(args[0][0]);
  const Vells& vdec = *(args[0][1]);
  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex

  if( obs_name_.empty() )
    {
      const Vells& vx   = *(args[1][0]);
      const Vells& vy   = *(args[1][1]);
      const Vells& vz   = *(args[1][2]);
  
      // NB: for the time being we only support scalars
      Assert( vra.isScalar() && vdec.isScalar() &&
          vx.isScalar() && vy.isScalar() && vz.isScalar() );

      double x = vx.getScalar<double>();
      double y = vy.getScalar<double>();
      double z = vz.getScalar<double>();
      MPosition stnpos(MVPosition(x,y,z),MPosition::ITRF);
      Frame.set(stnpos); // tie this frame to station position
  }
  else
  {
      // NB: for the time being we only support scalars
      Assert( vra.isScalar() && vdec.isScalar() );
      // create frame for an observatory
      MPosition Obs;
      MeasTable::Observatory(Obs,obs_name_);
      Frame.set(Obs);  // tie this frame to a known observatory
  }

  const Cells& cells = resultCells();
  // Get RA and DEC of location to be transformed to AzEl (default is J2000).
  // assume input ra and dec are in radians
  MVDirection sourceCoord(vra.getScalar<double>(),vdec.getScalar<double>());

  FailWhen(!cells.isDefined(Axis::TIME),"Meq::AzEl: no time axis in request, can't compute AzEl");
  int ntime = cells.ncells(Axis::TIME);
  const LoVec_double & time = cells.center(Axis::TIME);
  Axis::Shape shape = Axis::vectorShape(Axis::TIME,ntime);
  out[0] = Vells(0.0,shape,false);
  out[1] = Vells(0.0,shape,false);
  double * Az = out[0].realStorage();
  double * El = out[1].realStorage();
  Quantum<double> qepoch(0, "s");
  qepoch.setValue(time(0));
  MEpoch mepoch(qepoch, MEpoch::UTC);
  Frame.set (mepoch);
  MDirection::Convert azel_converter = MDirection::Convert(sourceCoord,MDirection::Ref(MDirection::AZEL,Frame));
  for( int i=0; i<ntime; i++) 
  {
    qepoch.setValue (time(i));
    mepoch.set (qepoch);
    Frame.set (mepoch);
    // convert ra, dec to Az El at given time
    MDirection az_el_out(azel_converter());
    //Gawd - what a mouthful - luckily some old ACSIS code provided the
    //right incantation for the following line!
    Vector<Double> az_el = az_el_out.getValue().getAngle("rad").getValue();
    Az[i] = az_el(0);
    El[i] = az_el(1);
  }
}

} // namespace Meq

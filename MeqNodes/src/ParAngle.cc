//# ParAngle.cc: Calculate the parallactic angle for an observation
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
//# $Id: ParAngle.cc 3568 2006-05-15 14:11:19Z smirnov $

#include <MeqNodes/ParAngle.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <measures/Measures/MBaseline.h>
#include <measures/Measures/MPosition.h>
#include <measures/Measures/MeasTable.h>
#include <measures/Measures/MEpoch.h>
#include <measures/Measures/ParAngleMachine.h>

using namespace casa;

namespace Meq {
  
const HIID FObservatory = AidObservatory;

const HIID child_labels[] = { AidRADec,AidXYZ };

const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);


//The node should assume that only the first child (RADec) is mandatory
ParAngle::ParAngle()
: TensorFunction(2,child_labels,1)
{
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

ParAngle::~ParAngle()
{}

// Obtain an observatory - if a name is supplied
// use a 'global observatory position' to calculate the parallactic Angle.
// Otherwise the parallactic angle will be calculated for individual
// station positions.
void ParAngle::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);

  if(rec->hasField(FObservatory))
      {
        rec[FObservatory].get(obs_name_,initializing);
      }
}

void ParAngle::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &,const Request &request)
{
  // NB: for the time being we only support scalar child results, 
  // and so we ignore the child cells, and only use the request cells
  // (while checking that they have a time axis)
  const Cells &cells = request.cells();
  FailWhen(!cells.isDefined(Axis::TIME),"Meq::ParAngle: no time axis in request, can't compute ParAngles");
  ref.attach(cells);
}

LoShape ParAngle::getResultDims (const vector<const LoShape *> &input_dims)
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
  // result is a 1-D vector
  return LoShape(1);
}

void ParAngle::evaluateTensors (std::vector<Vells> & out,   
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
//    cerr<<"xyz:"<<x<<","<<y<<","<<z<<endl;
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
  // Get RA and DEC of location where Parallactic Angle is to be 
  // calculated (default is J2000).
  // assume input ra and dec are in radians
  double ra=vra.getScalar<double>(),dec=vdec.getScalar<double>();
  MVDirection sourceCoord(vra.getScalar<double>(),vdec.getScalar<double>());
  // create corresponding MDirection
  MDirection sourceDir(sourceCoord);
//  cerr<<"radec:"<<x<<","<<y<<","<<z<<endl;

  FailWhen(!cells.isDefined(Axis::TIME),"Meq::ParAngle: no time axis in request, can't compute ParAngle");
  int ntime = cells.ncells(Axis::TIME);
  const LoVec_double & time = cells.center(Axis::TIME);
  Axis::Shape shape = Axis::vectorShape(Axis::TIME,ntime);
  out[0] = Vells(0.0,shape,false);
  double * ParAng = out[0].realStorage();
  Quantum<double> qepoch(0, "s");
  qepoch.setValue(time(0));
  MEpoch mepoch(qepoch, MEpoch::UTC);
  Frame.set (mepoch);

  // create Parallactic Angle machine
  ParAngleMachine pam(sourceDir);
  pam.set(Frame);
//  pam.setInterval(0.04);
  pam.setInterval(0);
  for( int i=0; i<ntime; i++) 
  {
    qepoch.setValue (time(i));
//    mepoch.set (qepoch);
//    Frame.set (mepoch);
    ParAng[i] = pam(qepoch).get("rad").getValue();
  }
}

} // namespace Meq

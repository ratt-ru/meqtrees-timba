//# RADec.cc: Calculate RADec from J2000 ra, dec
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
//# $Id: RADec.cc 3988 2006-09-19 21:17:35Z twillis $

#include <MeqNodes/RADec.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <measures/Measures/MCDirection.h>
#include <measures/Measures/MBaseline.h>
#include <measures/Measures/MPosition.h>
#include <measures/Measures/MEpoch.h>
#include <measures/Measures/MeasConvert.h>
#include <measures/Measures/MeasTable.h>
#include <casa/Quanta/MVuvw.h>

using namespace casa;

namespace Meq {
  
const HIID FAzEl= AidAz|AidEl;
const HIID FObservatory = AidObservatory;

const HIID child_labels[] = { FAzEl,AidXYZ };
//const HIID child_labels[] = { AidRA,AidDec};
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);


RADec::RADec()
: TensorFunction(2,child_labels)
{
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

RADec::~RADec()
{}

void RADec::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request)
{
  // copy cells of first child
  if( childres[0]->hasCells() )
    ref.attach(childres[0]->cells());
  else
    ref.attach(request.cells());
  // check that we now have a time axis
  FailWhen(!ref->isDefined(Axis::TIME),"Meq::RADec: no time axis in child result or in request, can't compute RA/Dec");
  // create vells from time axis
  Vells::Shape shape;
  Axis::degenerateShape(shape,ref->rank());
  int nc = shape[Axis::TIME] = ref->ncells(Axis::TIME);
  time_vells_ = Vells(0,shape,false);
  memcpy(time_vells_.realStorage(),ref->center(Axis::TIME).data(),nc*sizeof(double));
}


LoShape RADec::getResultDims (const vector<const LoShape *> &input_dims)
{
  Assert(input_dims.size()>=1);
  // child 0 (RaDec0): expected 2-vector
  const LoShape &dim0 = *input_dims[0];
  FailWhen(dim0.size()!=1 || dim0[0]!=2,"child '"+child_labels[0].toString()+"': 2-vector expected");
  // children 1 (XYZ): expecting 3-vector, if any
  const LoShape &dim1 = *input_dims[1];
  FailWhen(dim1.size()!=1 || dim1[0]!=3,"child '"+child_labels[1].toString()+"': 3-vector expected");
  // result is a 3-vector
  return LoShape(2);
}



void RADec::evaluateTensors (std::vector<Vells> & out,   
                            const std::vector<std::vector<const Vells *> > &args)
{
  // thanks to checks in getResultDims(), we can expect all 
  // vectors to have the right sizes
  // Get RA and DEC, and station positions
  const Vells& vaz  = *(args[0][0]);
  const Vells& vel = *(args[0][1]);
  const Vells& vx   = *(args[1][0]);
  const Vells& vy   = *(args[1][1]);
  const Vells& vz   = *(args[1][2]);
  
  // NB: for the time being we only support scalars
  Assert(vx.isScalar() && vy.isScalar() && vz.isScalar());

  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
  // create a frame for an Observatory, or a telescope station
  MeasFrame Frame; // create default frame 
  
  double x = vx.getScalar<double>();
  double y = vy.getScalar<double>();
  double z = vz.getScalar<double>();
  MPosition stnpos(MVPosition(x,y,z),MPosition::ITRF);
  Frame.set(stnpos); // tie this frame to station position

  // we iterate over ra, dec, and time so compute output shape
  // and strides accordingly
  Vells::Shape outshape;
  Vells::Strides strides[3];
  const Vells::Shape * inshapes[3] = { &(time_vells_.shape()),&(vaz.shape()),&(vel.shape()) };  
  Vells::computeStrides(outshape,strides,3,inshapes,"RADec");

  // setup input iterators
  Vells::ConstStridedIterator<double> iter_time(time_vells_,strides[0]);
  Vells::ConstStridedIterator<double> iter_az(vaz,strides[1]);
  Vells::ConstStridedIterator<double> iter_el(vel,strides[2]);

  out[0] = Vells(0.0,outshape,false);
  out[1] = Vells(0.0,outshape,false);
  double * pra = out[0].realStorage();
  double * pdec = out[1].realStorage();
  double time0 = *iter_time-1;     

  Quantum<double> qepoch(0, "s");
  qepoch.setValue(time0);
  MEpoch mepoch(qepoch, MEpoch::UTC);
  Frame.set(mepoch);
  MDirection::Convert radec_converter = MDirection::Convert(MDirection::Ref(MDirection::AZEL,Frame),MDirection::Ref(MDirection::J2000));
  Vector<Double> azel(2);

  // now iterate
  Vells::DimCounter counter(outshape);
  while( true )
  {
    if( *iter_time != time0 )
    {
      qepoch.setValue(time0=*iter_time);
      mepoch.set(qepoch);
      Frame.set(mepoch);       
    }
    azel(0) = *iter_az;
    azel(1) = *iter_el;
    // convert ra, dec to Az El at given time
    MDirection radec_out(radec_converter(azel));
    //Gawd - what a mouthful - luckily some old ACSIS code provided the
    //right incantation for the following line!
    Vector<Double> radec = radec_out.getValue().getAngle("rad").getValue();
    *(pra++) = radec(0);
    *(pdec++) = radec(1);
    
    // increment counter
    int ndim = counter.incr();
    if( !ndim )    // break out when counter is finished
      break;
    iter_time.incr(ndim);
    iter_az.incr(ndim);
    iter_el.incr(ndim);
  }
}

} // namespace Meq

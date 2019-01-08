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
#include <casacore/measures/Measures/MCBaseline.h>
#include <casacore/measures/Measures/MCDirection.h>
#include <casacore/measures/Measures/MBaseline.h>
#include <casacore/measures/Measures/MPosition.h>
#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/MeasConvert.h>
#include <casacore/measures/Measures/MeasTable.h>
#include <casacore/casa/Quanta/MVuvw.h>

using namespace casacore;

namespace Meq {
  
const HIID FObservatory = AidObservatory;

const HIID child_labels[] = { AidRADec,AidXYZ };
//const HIID child_labels[] = { AidRA,AidDec};

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


void AzEl::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request)
{
  // copy cells of first child
  if( childres[0]->hasCells() )
    ref.attach(childres[0]->cells());
  else
    ref.attach(request.cells());
  // check that we now have a time axis
  FailWhen(!ref->isDefined(Axis::TIME),"Meq::AzEl: no time axis in child result or in request, can't compute AzEls");
  // create vells from time axis
  Vells::Shape shape;
  Axis::degenerateShape(shape,ref->rank());
  int nc = shape[Axis::TIME] = ref->ncells(Axis::TIME);
  time_vells_ = Vells(0,shape,false);
  memcpy(time_vells_.realStorage(),ref->center(Axis::TIME).data(),nc*sizeof(double));
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
  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
  // create a frame for an Observatory, or a telescope station
  MeasFrame Frame; // create default frame 

  // thanks to checks in getResultDims(), we can expect all 
  // vectors to have the right sizes
  // Get RA and DEC, and station positions
  const Vells& vra  = *(args[0][0]);
  const Vells& vdec = *(args[0][1]);

  if( obs_name_.empty() )
  {
    const Vells& vx   = *(args[1][0]);
    const Vells& vy   = *(args[1][1]);
    const Vells& vz   = *(args[1][2]);
    // NB: for the time being we only support scalars for xyz
    Assert(vx.isScalar() && vy.isScalar() && vz.isScalar() );
    double x = vx.getScalar<double>();
    double y = vy.getScalar<double>();
    double z = vz.getScalar<double>();
    MPosition stnpos(MVPosition(x,y,z),MPosition::ITRF);
    Frame.set(stnpos); // tie this frame to station position
  }
  else
  {
    // create frame for an observatory
    MPosition Obs;
    MeasTable::Observatory(Obs,obs_name_);
    Frame.set(Obs);  // tie this frame to a known observatory
  }

  // we iterate over ra, dec, and time so compute output shape
  // and strides accordingly
  Vells::Shape outshape;
  Vells::Strides strides[3];
  const Vells::Shape * inshapes[3] = { &(time_vells_.shape()),&(vra.shape()),&(vdec.shape()) };  
  Vells::computeStrides(outshape,strides,3,inshapes,"AzEl");

  // setup input iterators
  Vells::ConstStridedIterator<double> iter_time(time_vells_,strides[0]);
  Vells::ConstStridedIterator<double> iter_ra(vra,strides[1]);
  Vells::ConstStridedIterator<double> iter_dec(vdec,strides[2]);

  out[0] = Vells(0.0,outshape,false);
  out[1] = Vells(0.0,outshape,false);
  double * paz = out[0].realStorage();
  double * pel = out[1].realStorage();
  double time0 = *iter_time-1;     

  Quantum<double> qepoch(0, "s");
  qepoch.setValue(time0);
  MEpoch mepoch(qepoch, MEpoch::UTC);
  Frame.set(mepoch);
  MDirection::Convert azel_converter = MDirection::Convert(MDirection::Ref(MDirection::J2000),MDirection::Ref(MDirection::AZEL,Frame));
  Vector<Double> radec(2);

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
    radec(0) = *iter_ra;
    radec(1) = *iter_dec;
    // convert ra, dec to Az El at given time
    MDirection az_el_out(azel_converter(radec));
    //Gawd - what a mouthful - luckily some old ACSIS code provided the
    //right incantation for the following line!
    Vector<Double> az_el = az_el_out.getValue().getAngle("rad").getValue();
    *(paz++) = az_el(0);
    *(pel++) = az_el(1);
    
    // increment counter
    int ndim = counter.incr();
    if( !ndim )    // break out when counter is finished
      break;
    iter_time.incr(ndim);
    iter_ra.incr(ndim);
    iter_dec.incr(ndim);
  }
}

} // namespace Meq

//# EMFPar.cc: Calculate EMFPar from J2000 ra, dec
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
//# $Id: EMFPar.cc 7012 2009-07-09 14:03:39Z sarod $

#include <MeqNodes/EMFPar.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casacore/measures/Measures/MDirection.h>
#include <casacore/measures/Measures/MPosition.h>
#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/EarthMagneticMachine.h>
#include <casacore/measures/Measures/MeasTable.h>

using namespace casacore;

namespace Meq {
  
const HIID FObservatory = AidObservatory;

const HIID child_labels[] = { AidAzEl,AidXYZ };
//const HIID child_labels[] = { AidRA,AidDec};

// 2 children, only the first one is mandatory
EMFPar::EMFPar()
: TensorFunction(2,child_labels,1)
{
  height_.resize(1);
  height_[0] = 200000; // 200km default height
}

EMFPar::~EMFPar()
{}

void EMFPar::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);
  rec[AidH].get_vector(height_,initializing);
  rec[FObservatory].get(obs_name_,initializing);
}

void EMFPar::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &)
{
  // start with cells of azel
  ref.attach(childres[0]->cells());
}

LoShape EMFPar::getResultDims (const vector<const LoShape *> &input_dims)
{
  // azel is a 2-vector
  const LoShape &dim0 = *input_dims[0];
  FailWhen(dim0.size()!=1 || dim0[0]!=2,"child '"+child_labels[0].toString()+"': 2-vector expected");
  // check xyz if no observatory name
  if( obs_name_.empty() )
  {
    FailWhen(input_dims.size()!=2,"no xyz child and no Observatory field provided");
    // xyz is a 3-vector
    const LoShape &dim1 = *input_dims[1];
    FailWhen(dim1.size()!=1 || dim1[0]!=3,"child '"+child_labels[1].toString()+"': 3-vector expected");
  }
  // result is same dimension as height vector
  LoShape dim(1);
  dim[0] = height_.size();
  return dim;
}

void EMFPar::evaluateTensors (std::vector<Vells> & out,   
                            const std::vector<std::vector<const Vells *> > &args)
{

  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex

  // az/el values from first child
  const Vells& vaz  = *(args[0][0]);
  const Vells& vel = *(args[0][1]);

  MeasFrame frame;
  if( obs_name_.empty() )
  {
    // position from second child
    const Vells& vx   = *(args[1][0]);
    const Vells& vy   = *(args[1][1]);
    const Vells& vz   = *(args[1][2]);

    // NB: for the time being we only support scalar xyz
    FailWhen(!(vx.isScalar() && vy.isScalar() && vz.isScalar()),"expected a scalar for xyz position");
    double x = vx.getScalar<double>();
    double y = vy.getScalar<double>();
    double z = vz.getScalar<double>();
    MPosition pos(MVPosition(x,y,z),MPosition::ITRF);
    frame.set(pos); 
  }
  else
  {
    MPosition pos;
    MeasTable::Observatory(pos,obs_name_);
    frame.set(pos); 
  }

  // we iterate over azimuth and elevation, so compute output shape
  // and strides accordingly
  Vells::Shape outshape;
  Vells::Strides strides[2];
  const Vells::Shape * inshapes[2] = { &(vaz.shape()),&(vel.shape()) };  
  Vells::computeStrides(outshape,strides,2,inshapes,"EMFPar");

  // setup input iterators
  Vells::ConstStridedIterator<double> iter_az(vaz,strides[0]);
  Vells::ConstStridedIterator<double> iter_el(vel,strides[1]);

  // setup output Vells for each height layer
  int nh = out.size();
  double * pout[nh];
  for( int i=0; i<nh; i++ )
  {
    out[i] = Vells(0,outshape,true);
    pout[i] = out[i].realStorage();
  }

  // setup EarthMagneticMachine
  // use epoch=0 since EMF model is independent of time in the az/el frame
  MEpoch mepoch(Quantum<double>(0,"s"),MEpoch::UTC);
  frame.set(mepoch);
  // second (az/el) and third argument (h) doesn't matter, 
  // as it will be overridden later in getLOSValue()
  MDirection dir(MVDirection(0,0),MDirection::AZEL);
  EarthMagneticMachine emm(dir.getRef(),MVDirection(0,0),frame);

  // now iterate
  Vells::DimCounter counter(outshape);
  while( true )
  {
    // set az/el
    emm.set(MVDirection(*iter_az,*iter_el));
    // get line-of-sight EMF component at each height
    for( int i=0; i<nh; i++ )
    {
      *pout[i] = emm.getLOSField(height_[i],"G").getValue("G");
      pout[i]++;
    }
    // increment counter
    int ndim = counter.incr();
    if( !ndim )    // break out when counter is finished
      break;
    iter_az.incr(ndim);
    iter_el.incr(ndim);
  }
}

} // namespace Meq

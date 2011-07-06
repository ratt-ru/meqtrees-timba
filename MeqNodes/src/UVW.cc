//# UVW.cc: Calculate station UVW from station position and phase center
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

#include <DMI/AID-DMI.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MeqNodes/UVW.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <measures/Measures/MCBaseline.h>
#include <measures/Measures/MBaseline.h>
#include <measures/Measures/MPosition.h>
#include <measures/Measures/MEpoch.h>
#include <measures/Measures/MeasConvert.h>
#include <measures/Measures/MeasTable.h>
#include <casa/Quanta/MVuvw.h>

using namespace casa;

namespace Meq {

const HIID child_labels[] = { AidRADec,AidXYZ,AidXYZ|0  };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);


//##ModelId=400E535502D1
UVW::UVW()
: TensorFunction(num_children,child_labels),include_derivatives_(false)
{
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

//##ModelId=400E535502D2
UVW::~UVW()
{}

void UVW::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  rec[AidInclude|AidDeriv].get(include_derivatives_,initializing);
}

void UVW::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &,const Request &request)
{
  // NB: for the time being we only support scalar child results,
  // and so we ignore the child cells, and only use the request cells
  // (while checking that they have a time axis)
  const Cells &cells = request.cells();
  FailWhen(!cells.isDefined(Axis::TIME),"Meq::UVW: no time axis in request, can't compute UVWs");
  ref.attach(cells);
}


LoShape UVW::getResultDims (const vector<const LoShape *> &input_dims)
{
  Assert(input_dims.size()==3);
  // child 0 (RaDec0): expected 2-vector
  const LoShape &dim = *input_dims[0];
  FailWhen(dim.size()!=1 || dim[0]!=2,"child '"+child_labels[0].toString()+"': 2-vector expected");
  // children 1/2 (XYZ/XYZ_0): expecting 3-vectors
  for( int i=1; i<3; i++ )
  {
    const LoShape &dim = *input_dims[i];
    FailWhen(dim.size()!=1 || dim[0]!=3,"child '"+child_labels[i].toString()+"': 3-vector expected");
  }
  // result is a 3-vector
  if( include_derivatives_ )
    return LoShape(2,3);
  else
    return LoShape(3);
}

void UVW::evaluateTensors (std::vector<Vells> & out,
     const std::vector<std::vector<const Vells *> > &args )
{
  // thanks to checks in getResultDims(), we can expect all
  // vectors to have the right sizes

  // Get RA and DEC of phase center, and station positions
  const Vells& vra  = *(args[0][0]);
  const Vells& vdec = *(args[0][1]);
  const Vells& vstx = *(args[1][0]);
  const Vells& vsty = *(args[1][1]);
  const Vells& vstz = *(args[1][2]);
  const Vells& vx0  = *(args[2][0]);
  const Vells& vy0  = *(args[2][1]);
  const Vells& vz0  = *(args[2][2]);

  // NB: for the time being we only support scalars
  Assert( vra.isScalar() && vdec.isScalar() &&
      	  vstx.isScalar() && vsty.isScalar() && vstz.isScalar() &&
      	  vx0.isScalar() && vy0.isScalar() && vz0.isScalar() );

  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex

  // get the 0 position (array center, presumably)
  double x0 = vx0.getScalar<double>();
  double y0 = vy0.getScalar<double>();
  double z0 = vz0.getScalar<double>();
  MPosition zeropos(MVPosition(x0,y0,z0),MPosition::ITRF);

  // Get RA and DEC of phase center (as J2000).
  MVDirection phaseRef(vra.getScalar<double>(),vdec.getScalar<double>());

  // Set output shape
  const Cells& cells = resultCells();
  int ntime = cells.ncells(Axis::TIME);
  const LoVec_double & time = cells.center(Axis::TIME);
  Axis::Shape shape = Axis::vectorShape(Axis::TIME,ntime);
  for( uint i=0; i<out.size(); i++ )
    out[i] = Vells(0.0,shape,false);
  double * pU = out[0].realStorage();
  double * pV = out[1].realStorage();
  double * pW = out[2].realStorage();
  double *pdU,*pdV,*pdW;
  if( include_derivatives_ )
  {
    pdU = out[3].realStorage();
    pdV = out[4].realStorage();
    pdW = out[5].realStorage();
  }

  // Calculate the UVW coordinates using the AIPS++ code.
  MVPosition mvpos(vstx.getScalar<double>()-x0,
                   vsty.getScalar<double>()-y0,
                   vstz.getScalar<double>()-z0);
  MVBaseline mvbl(mvpos);
  MBaseline mbl(mvbl, MBaseline::ITRF);
  Quantum<double> qepoch(0, "s");
  qepoch.setValue(time(0));
  MEpoch mepoch(qepoch, MEpoch::UTC);
  MeasFrame frame(zeropos);
  frame.set (MDirection(phaseRef, MDirection::J2000));
  frame.set (mepoch);
  mbl.getRefPtr()->set(frame);      // attach frame
  MBaseline::Convert mcvt(mbl, MBaseline::J2000);
  for( int i=0; i<ntime; i++)
  {
    qepoch.setValue (time(i));
    mepoch.set (qepoch);
    frame.set (mepoch);
    const MVBaseline& bas2000 = mcvt().getValue();
    MVuvw uvw2000 (bas2000, phaseRef);
    const Vector<double>& xyz = uvw2000.getValue();
    pU[i] = xyz(0);
    pV[i] = xyz(1);
    pW[i] = xyz(2);
    if( include_derivatives_ )
    {
      qepoch.setValue (time(i)+1);
      mepoch.set (qepoch);
      frame.set (mepoch);
      const MVBaseline& bas2000 = mcvt().getValue();
      MVuvw uvw2000 (bas2000, phaseRef);
      const Vector<double>& xyz1 = uvw2000.getValue();
      pdU[i] = xyz1(0) - pU[i];
      pdV[i] = xyz1(1) - pV[i];
      pdW[i] = xyz1(2) - pW[i];
    }
  }
}

} // namespace Meq

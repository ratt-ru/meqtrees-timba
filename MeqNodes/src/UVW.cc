//# UVW.cc: Calculate station UVW from station position and phase center
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

#include <MeqNodes/UVW.h>
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

namespace Meq {

const HIID child_labels[] = { AidRA,AidDec,AidX,AidY,AidZ,AidX|0,AidY|0,AidZ|0  };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

const HIID FDomain = AidDomain;

//##ModelId=400E535502D1
UVW::UVW()
: Function(num_children,child_labels)
{
  const HIID symdeps[] = { FDomain,FResolution };
  setActiveSymDeps(symdeps,2);
  // ***BUG***
  // Use the Dwingeloo position for the frame.
  // must pass in real position somehow, later
//  Assert (MeasTable::Observatory(itsEarthPos, "DWL"));
  ///  itsRefU = itsU;
}

//##ModelId=400E535502D2
UVW::~UVW()
{}

//##ModelId=400E535502D6
int UVW::getResult (Result::Ref &resref, 
                    const std::vector<Result::Ref> &childres,
                    const Request &request,bool newreq)
{
  // Check that child results are all OK (no fails, 1 vellset per child)
  string fails;
  std::vector<Thread::Mutex::Lock> childvs_lock(num_children);
  std::vector<Thread::Mutex::Lock> childval_lock(num_children);
  for( int i=0; i<num_children; i++ )
  {
    int nvs = childres[i]->numVellSets();
    if( nvs != 1 )
      Debug::appendf(fails,"child %s: expecting single VellsSet, got %d;",
          child_labels[i].toString().c_str(),nvs);
    if( childres[i]->hasFails() )
      Debug::appendf(fails,"child %s: has fails",child_labels[i].toString().c_str());
    childvs_lock[i].relock(childres[i]->vellSet(0).mutex());
    childval_lock[i].relock(childres[i]->vellSet(0).getValue().getDataArray().mutex());
  }
  if( !fails.empty() )
    NodeThrow1(fails);
  // Get RA and DEC of phase center, and station positions
  const Vells& vra  = childres[0]->vellSet(0).getValue();
  const Vells& vdec = childres[1]->vellSet(0).getValue();
  const Vells& vstx = childres[2]->vellSet(0).getValue();
  const Vells& vsty = childres[3]->vellSet(0).getValue();
  const Vells& vstz = childres[4]->vellSet(0).getValue();
  const Vells& vx0  = childres[5]->vellSet(0).getValue();
  const Vells& vy0  = childres[6]->vellSet(0).getValue();
  const Vells& vz0  = childres[7]->vellSet(0).getValue();
  // For the time being we only support scalars
  Assert( vra.isScalar() && vdec.isScalar() &&
      	  vstx.isScalar() && vsty.isScalar() && vstz.isScalar() && 
      	  vx0.isScalar() && vy0.isScalar() && vz0.isScalar() );

  // get the 0 position (array center, presumably)
  double x0 = vx0.as<double>();
  double y0 = vy0.as<double>();
  double z0 = vz0.as<double>();
  MPosition zeropos(MVPosition(x0,y0,z0),MPosition::ITRF);
      
  const Cells& cells = request.cells();
  // Allocate a 3-plane result for U, V, and W
  Result &result = resref <<= new Result(3,request);
  // Get RA and DEC of phase center (as J2000).
  MVDirection phaseRef(vra.as<double>(),vdec.as<double>());
  // Set correct size of values.
  int nfreq = cells.ncells(FREQ);
  int ntime = cells.ncells(TIME);
  const LoVec_double & time = cells.center(TIME);
  LoMat_double& matU = result.setNewVellSet(0).setReal(nfreq,ntime);
  LoMat_double& matV = result.setNewVellSet(1).setReal(nfreq,ntime);
  LoMat_double& matW = result.setNewVellSet(2).setReal(nfreq,ntime);
  // Calculate the UVW coordinates using the AIPS++ code.
  MVPosition mvpos(vstx.as<double>()-x0,vsty.as<double>()-y0,vstz.as<double>()-z0);
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
  for( int i=0; i<ntime; i++) {
    qepoch.setValue (time(i));
    mepoch.set (qepoch);
    frame.set (mepoch);
    const MVBaseline& bas2000 = mcvt().getValue();
    MVuvw uvw2000 (bas2000, phaseRef);
    const Vector<double>& xyz = uvw2000.getValue();
    for (int j=0; j<nfreq; j++) 
    {
      matU(j,i) = xyz(0);
      matV(j,i) = xyz(1);
      matW(j,i) = xyz(2);
    }
  }
  return 0;
}

} // namespace Meq

//# LST.cc: Calculate LST from observation Modified Julian Date
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

#include <MeqNodes/LST.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <measures/Measures/MBaseline.h>
#include <measures/Measures/MPosition.h>
#include <measures/Measures/MCEpoch.h>
#include <measures/Measures/MEpoch.h>
#include <measures/Measures/MeasConvert.h>
#include <measures/Measures/MeasTable.h>
#include <casa/Quanta/MVuvw.h>

using namespace casa;

namespace Meq {
  
const HIID FObservatory = AidObservatory;

const HIID child_labels[] = { AidXYZ };

const HIID FDomain = AidDomain;

//The node should assume that only the first child (XYZ) is needed
//if the 'observatory' field is not supplied.
LST::LST()
: TensorFunction(1,child_labels,0)
{
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

LST::~LST()
{}

// Obtain an observatory - if a name is supplied
// use a 'global observatory position' to calculate LST.
// Otherwise LST will be calculated for individual
// station positions.
void LST::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);

  if(rec->hasField(FObservatory))
      {
        rec[FObservatory].get(obs_name_,initializing);
      }
}


void LST::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &,const Request &request)
{
  // NB: for the time being we only support scalar child results, 
  // and so we ignore the child cells, and only use the request cells
  // (while checking that they have a time axis)
  const Cells &cells = request.cells();
  FailWhen(!cells.isDefined(Axis::TIME),"Meq::LST: no time axis in request, can't compute LSTs");
  ref.attach(cells);
}

LoShape LST::getResultDims (const vector<const LoShape *> &input_dims)
{
  if( obs_name_.empty() )
    {
      Assert(input_dims.size()>=1);
      // children 0 (XYZ): expecting 3-vector, if any
      const LoShape &dim0 = *input_dims[0];
      FailWhen(dim0.size()!=1 || dim0[0]!=3,"child '"+child_labels[0].toString()+"': 3-vector expected");
    }

  // result is a 1-D vector
  return LoShape(1);
}

void LST::evaluateTensors (std::vector<Vells> & out,   
                            const std::vector<std::vector<const Vells *> > &args)
{
  // create a frame for an Observatory, or a telescope station
  MeasFrame Frame; // create default frame 

  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex

  if( obs_name_.empty() )
    {
      const Vells& vx   = *(args[0][0]);
      const Vells& vy   = *(args[0][1]);
      const Vells& vz   = *(args[0][2]);
  
      // NB: for the time being we only support scalars
      Assert( vx.isScalar() && vy.isScalar() && vz.isScalar() );

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

  const Cells& cells = resultCells();
  FailWhen(!cells.isDefined(Axis::TIME),"Meq::LST: no time axis in request, can't compute LST");
  int ntime = cells.ncells(Axis::TIME);
  const LoVec_double & time = cells.center(Axis::TIME);
  Axis::Shape shape = Axis::vectorShape(Axis::TIME,ntime);
  out[0] = Vells(0.0,shape,false);
  double * LST = out[0].realStorage();
  Quantum<double> qepoch(0, "s");
  qepoch.setValue(time(0));
  MEpoch mepoch(qepoch, MEpoch::UTC);
  Frame.set(mepoch);
  for( int i=0; i<ntime; i++) 
  {
    qepoch.setValue (time(i));
    mepoch.set (qepoch);
    Frame.set (mepoch);
    MEpoch::Convert(mepoch, MEpoch::Ref(MEpoch::LAST,Frame))().getValue();
    Frame.getLASTr(LST[i]);
  }
}

} // namespace Meq

//# LongLat.cc: Converts a xyz vector to long,lat,length. 
//# If WGS84 = True (default) the geodetic Long Lat is calculated. 
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


#include <MeqNodes/LongLat.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <measures/Measures/MPosition.h>
#include <measures/Measures/MCPosition.h>
#include <measures/Measures/MeasConvert.h>

namespace Meq {

using namespace VellsMath;


const HIID FUseW = AidUse|AidW;

const HIID child_labels[] = { AidXYZ };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);


using Debug::ssprintf;

//##ModelId=400E535502D1
LongLat::LongLat()
  : TensorFunction(num_children,child_labels,1),_use_WGS84(0)
{
}

//##ModelId=400E535502D2
LongLat::~LongLat()
{}


  //get use_w field, if >0 first convert WGS84 coordinates
void LongLat::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);

  if(rec->hasField(FUseW))
      {
        rec[FUseW].get(_use_WGS84,initializing);
      }
}


LoShape LongLat::getResultDims (const vector<const LoShape *> &input_dims)
{
  Assert(input_dims.size()==1);
  // input is a 3-vectors
  const LoShape &dim = *input_dims[0];
  FailWhen(dim.size()!=1 || dim[0]!=3,"child '"+child_labels[0].toString()+"': 3-vector expected");
  // result is a 3-vector
  return LoShape(3);
}
    

void LongLat::evaluateTensors (std::vector<Vells> & out,   
     const std::vector<std::vector<const Vells *> > &args )
{
  // thanks to checks in getResultDims(), we can expect all 
  // vectors to have the right sizes
  
  // phase center position
  const Vells & vx  = *(args[0][0]);
  const Vells & vy = *(args[0][1]);
  const Vells & vz = *(args[0][2]);
  
  // NB: for the time being we only support scalars
  Assert(vx.isScalar() && vy.isScalar() && vz.isScalar() );
  
  double x = vx.getScalar<double>();
  double y = vy.getScalar<double>();
  double z = vz.getScalar<double>();

  // outputs
  Vells & Long = out[0];
  Vells & Lat = out[1];
  Vells & Length = out[2];
  const casa::MVPosition vpos(x,y,z);
  const casa::MPosition pos(vpos,casa::MPosition::ITRF);
  casa::Vector<casa::Double> ang;
  casa::Double length;
  if(_use_WGS84)
    {  
      casa::MPosition::Convert loc2(pos, casa::MPosition::WGS84);
      casa::MPosition locwgs84(loc2());
      ang= locwgs84.getAngle().getValue();
      length = locwgs84.getValue().getLength().getValue();
    }
  else
    {
      ang= pos.getAngle().getValue();
      length = pos.getValue().getLength().getValue();
    }
  Long = Vells(ang(0));
  Lat = Vells(ang(1));
  Length = Vells(length);  //if use_wgs84 length is in fact heigth aabove earth surface
}



} // namespace Meq

//# LMN.cc: Calculate source LMN from source position and phase center
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

#include <MeqNodes/LMN.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

namespace Meq {

using namespace VellsMath;

const HIID child_labels[] = { AidRADec|0,AidRADec, AidPA };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

const HIID FDomain = AidDomain;

using Debug::ssprintf;

//##ModelId=400E535502D1
LMN::LMN()
: TensorFunction(num_children,child_labels,2)
{
}

//##ModelId=400E535502D2
LMN::~LMN()
{}

LoShape LMN::getResultDims (const vector<const LoShape *> &input_dims)
{
  Assert(input_dims.size()==2 || input_dims.size()==3);
  // inputs are 2-vectors
  for( int i=0; i<2; i++ )
  {
    const LoShape &dim = *input_dims[i];
    FailWhen(dim.size()!=1 || dim[0]!=2,"child '"+child_labels[i].toString()+"': 2-vector expected");
  }
  if (input_dims.size() == 3)
  {
    const LoShape &dim = *input_dims[2]; 
    FailWhen(dim.size()>1 || (dim.size()==1 && dim[0]>1),"child '"+child_labels[2].toString()+"': scalar expected");
  }
  // result is a 3-vector
  return LoShape(3);
}
    
void LMN::evaluateTensors (std::vector<Vells> & out,   
     const std::vector<std::vector<const Vells *> > &args )
{
  // thanks to checks in getResultDims(), we can expect all 
  // vectors to have the right sizes
  
  // phase center position
  const Vells & vra0  = *(args[0][0]);
  const Vells & vdec0 = *(args[0][1]);
  // source position
  const Vells & vra   = *(args[1][0]);
  const Vells & vdec  = *(args[1][1]);
  const Vells * pa_radians = 0;
  if( args.size()>2 && !args[2].empty() )
    pa_radians = args[2][0];
  // outputs
  Vells & L = out[0];
  Vells & M = out[1];
  Vells & N = out[2];

  // Note: nominally we would most likely use a non-zero value for 
  // the incoming pa_radians when pa == parallactic angle. 
  if ( !pa_radians ) {
    L = cos(vdec) * sin(vra-vra0);
    M = sin(vdec) * cos(vdec0) - cos(vdec) * sin(vdec0) * cos(vra-vra0);
    N = sqrt(1 - sqr(L) - sqr(M));
  } 
  else {
    Vells L1 = cos(vdec) * sin(vra-vra0);
    Vells M1 = sin(vdec) * cos(vdec0) - cos(vdec) * sin(vdec0) * cos(vra-vra0);
    // perform 2D rotation consistent with parallactic angle definition
    // see http://mathworld.wolfram.com/RotationMatrix.html, eqn 3
    L = L1 * cos(*pa_radians) + M1 * sin(*pa_radians);
    M = (-1.0) * L1 * sin(*pa_radians) + M1 * cos(*pa_radians);
    N = sqrt(1 - sqr(L) - sqr(M));
  }
}

} // namespace Meq

//# Norm.cc: Takes Frobenius norm (sqrt-of-sum-squares) of a tensor
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

#include <MeqNodes/Norm.h>

#include <MEQ/Vells.h>

using namespace Meq::VellsMath;

namespace Meq {    

//##ModelId=400E53550241
Norm::Norm()
: TensorFunction(1)
{}

//##ModelId=400E53550242
Norm::~Norm()
{}

LoShape Norm::getResultDims (const vector<const LoShape *> &)
{
  // result is always scalar
  return LoShape();
}


void Norm::evaluateTensors (std::vector<Vells> & out,   
     const std::vector<std::vector<const Vells *> > &args )
{
  out[0] = Vells();
  const std::vector<const Vells *> &argvec = args[0];
  for( uint i=0; i<argvec.size(); i++ )
    out[0] += sqr(*argvec[i]);
  out[0] = sqrt(out[0]);
}

} // namespace Meq

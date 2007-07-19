//# StdDev.cc: sqrt(abs(mean(sqr(v))-sqr(mean(v)))),or standard deviation
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

#include <MeqNodes/StdDev.h>

#include <MEQ/Vells.h>

using namespace Meq::VellsMath;

namespace Meq {    

StdDev::StdDev()
 : ReductionFunction(1)
{
}

StdDev::~StdDev()
{}

Vells StdDev::evaluate (const Request&,const LoShape &,
		     const vector<const Vells*>& values)
{
  // only one child ever expected -- see constructor 
  if( hasReductionAxes() )  // reduce along axes 
  {
    Vells vmean = apply(VellsMath::mean,*values[0],flagmask_[0]);
    Vells vmeansq = apply(VellsMath::mean,sqr(*values[0]),flagmask_[0]);
    return sqrt(vmeansq - sqr(vmean));
  }
  else                      // reduce to single value
  {
    Vells vmean = mean(*values[0],flagmask_[0]);
    Vells vmeansq = mean(sqr(*values[0]),flagmask_[0]);
    return sqrt(vmeansq - sqr(vmean));
  }
}

} // namespace Meq

//# Mean.cc: Take mean of a node
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

#include <MeqNodes/Mean.h>

#include <MEQ/Vells.h>

using namespace Meq::VellsMath;

namespace Meq {    


//##ModelId=400E53550246
Vells Mean::evaluate (const Request&,const LoShape &shape,
		     const vector<const Vells*>& values)
{
  if( values.size() == 1 )
    return mean(*(values[0]),flagmask_);
  else
  {
    int sum_nel=0;
    Vells res(0.);
    for( uint i=0; i<values.size(); i++ )
    {
      int nel = int( nelements(*(values[i]),shape,flagmask_).as<double>() );
      res += mean(*(values[i]),flagmask_) * nel;
      sum_nel += nel; 
    }
    return sum_nel ? res/sum_nel : Vells(0.);
  }
}

} // namespace Meq

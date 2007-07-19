//# Min.cc: Determine minimum of a node
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

#include <MeqNodes/Min.h>

#include <MEQ/Vells.h>

using namespace Meq::VellsMath;

namespace Meq {    

Min::Min ()
{
  allowMissingData();
}

  
//##ModelId=400E53550246
Vells Min::evaluate (const Request&,const LoShape &,
		     const vector<const Vells*>& values)
{
  // if dealing with a single child, reduce
  if( values.size() == 1 )
  {
    if( hasReductionAxes() )  // reduce along axes 
      return apply(VellsMath::min,*values[0],flagmask_[0]);
    else                      // reduce to single value
      return min(*(values[0]),flagmask_[0]);
  }
  else // else take mean across all Vells
  // NB: BUG! flags not treated properly here
  {
    bool has_res = false;
    Vells res;
    for( uint i=0; i<values.size(); i++ )
      if( values[i] )
      {
        if( has_res )
          res = min(res,*values[i],flagmask_[0],flagmask_[i]);
        else
        {
          res = *values[i]; 
          has_res = true;
        }
      }
    return res;
  }
}


} // namespace Meq

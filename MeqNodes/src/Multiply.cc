//# Multiply.cc: Multiply 2 or more nodes
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

#include <MeqNodes/Multiply.h>

namespace Meq {    


//##ModelId=400E530A0105
Multiply::Multiply()
{
  allowMissingData();
}

//##ModelId=400E530A0106
Multiply::~Multiply()
{}

void Multiply::evaluateFlags (Vells::Ref &out,const Request &req,const LoShape &shp,const vector<const VellSet *> &pvs)
{
  // if any argument is a null, then output is unflagged
  for( uint i=0; i<pvs.size(); i++ )
    if( pvs[i] && pvs[i]->isNull() )
      return;
  // else defer to normal routine
  Function::evaluateFlags(out,req,shp,pvs);
}

//##ModelId=400E530A010A
Vells Multiply::evaluate (const Request&, const LoShape&,
			  const vector<const Vells*>& values)
{
  if( values.empty() )
    return Vells::Unity();  // or should this be 0?
  Vells result(values[0] ? *values[0] : Vells::Unity() );
  for( uint i=1; i<values.size(); i++ )
    if( values[i] )
      result *= *(values[i]);
  return result;
}


} // namespace Meq

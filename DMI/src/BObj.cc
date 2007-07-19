//  DMI::BObj.cc: abstract prototype for blockable objects
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#include "DynamicTypeManager.h"
#include "BObj.h"


// //##ModelId=3BFE5FE103C5
// DMI::CountedRefTarget * DMI::BObj::clone (int flags, int depth) const
// {
//   BlockSet bset;
//   toBlock(bset);
//   if( flags&DMI::DEEP || depth>0 )
//     bset.privatizeAll(flags);
//   return DynamicTypeManager::construct(objectType(),bset);
// }
// 
//##ModelId=3E9BD915025A
void DMI::BObj::print (std::ostream &str) const
{
  str << objectType(); 
}


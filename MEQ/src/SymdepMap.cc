//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include "SymdepMap.h"
    
namespace Meq
{
 
DMI::Record::Ref SymdepMap::toRecord () const
{
  DMI::Record::Ref recref;
  DMI::Record &rec = recref <<= new DMI::Record;
  for( DepMap::const_iterator iter = map_.begin(); iter != map_.end(); iter++ )
    rec[iter->first] = iter->second;
  return recref;
}
  
   
int SymdepMap::set (const HIID &symdep,int mask)
{
  map_[symdep] = mask;
  return active_mask_ = getMask(active_set_);
}

int SymdepMap::load (const DMI::Record &rec)
{
  map_.clear();
  for( DMI::Record::const_iterator iter = rec.begin(); iter != rec.end(); iter++ )
    map_[iter.id()] = rec[iter.id()].as<int>();
  return active_mask_ = getMask(active_set_);
}

int SymdepMap::load (const DepMap &map)
{
  map_ = map;
  return active_mask_ = getMask(active_set_);
}

//## returns mask for a given set of dependencies
int SymdepMap::getMask (const HIID deps[],int ndeps) const
{
  int mask = 0;
  for( int i=0; i<ndeps; i++ )
  {
    DepMap::const_iterator iter = map_.find(deps[i]);
    if( iter != map_.end() )
      mask |= iter->second;
  }
  return mask;
}


//## sets the set of active dependencies, and recomputes mask
int SymdepMap::setActive (const HIID deps[],int ndeps)
{
  active_set_.resize(ndeps);
  active_set_.assign(deps,deps+ndeps);
  return active_mask_ = getMask(deps,ndeps);
}
  
};

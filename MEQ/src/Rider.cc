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

#include "Rider.h"

namespace Meq
{
        
template<class Container,class Subcontainer>
static Subcontainer & getOrInsert (Container &container,
                                   const HIID &field,
                                   Type2Type<Subcontainer> = Type2Type<Subcontainer>(),
                                   bool replace=false)
{
  int dum;
  Subcontainer *ptr;
  DMI::Container::Hook hook(container,field);
  if( replace )
    hook.replace() <<= ptr = new Subcontainer;
  else if( hook.exists() )
    ptr = hook.as_wp(dum,Type2Type<Subcontainer>());
  else
    hook <<= ptr = new Subcontainer;
  return *ptr;
}

//## Inits (if necessary) and returns a the subrecord rec[id]
DMI::Record & Rider::getOrInit (DMI::Record &rec,const HIID &id)
{
  return getOrInsert(rec,id,Type2Type<DMI::Record>());
}


// Clears the rider from the request, if any.
// Reqref will be privatized for writing if needed.
void Rider::clear (Request::Ref &reqref)
{
  DMI::Record::Hook rhook(reqref,FRider);
  if( rhook.exists() )
    rhook.remove();
}

DMI::Record & Rider::getRider (Request::Ref &reqref,int flags)
{
  return getOrInsert(reqref,FRider,Type2Type<DMI::Record>(),flags&NEW_RIDER);
}

// Inits (if necessary) and returns the group command record for 'group'.
// Reqref will be privatized for writing if needed.
// If the NEW_RIDER flag is given, always creates a new rider.
// If the NEW_GROUPREC flag is given, always creates a new GCR.
DMI::Record & Rider::getGroupRec (Request::Ref &reqref,const HIID &group,int flags)
{
  return getOrInsert(getRider(reqref,flags),group,Type2Type<DMI::Record>(),
            flags&(NEW_GROUPREC|NEW_RIDER));
}
    
// Inits (if necessary) and returns the command_all subrecord for the given group.
// Reqref will be privatized for writing if needed.
// If the NEW_RIDER flag is given, always creates a new rider.
// If the NEW_GROUPREC flag is given, always creates a new GCR.
// If the NEW_CMDREC flag is given, always creates a new command subrecord.
DMI::Record & Rider::getCmdRec_All (Request::Ref &reqref,const HIID &group,int flags)
{
  // get or insert Rider subrecord
  DMI::Record &cmdrec = getGroupRec(reqref,group,flags);
  return getOrInsert(cmdrec,FCommandAll,Type2Type<DMI::Record>(),flags&NEW_ALL);
}
    
// Inits (if necessary) and returns the command_by_nodeindex subrecord for 
// the given group. Reqref will be privatized for writing if needed.
// If the NEW_RIDER flag is given, always creates a new rider.
// If the NEW_GROUPREC flag is given, always creates a new GCR.
// If the NEW_CMDREC flag is given, always creates a new command subrecord.
DMI::Record & Rider::getCmdRec_ByNodeIndex (Request::Ref &reqref,const HIID &group,int flags)
{
  // get or insert Rider subrecord
  DMI::Record &cmdrec = getGroupRec(reqref,group,flags);
  return getOrInsert(cmdrec,FCommandByNodeIndex,Type2Type<DMI::Record>(),flags&NEW_ALL);
}

// Inits (if necessary) and returns the command_by_list subrecord (field) for 
// the given group. Reqref will be privatized for writing if needed.
// If the NEW_RIDER flag is given, always creates a new rider.
// If the NEW_GROUPREC flag is given, always creates a new GCR.
// If the NEW_CMDREC flag is given, always creates a new command subrecord.
DMI::Vec & Rider::getCmdRec_ByList (Request::Ref &reqref,const HIID &group,int flags)
{
  // get or insert Rider subrecord
  DMI::Record &cmdrec = getGroupRec(reqref,group,flags);
  return getOrInsert(cmdrec,FCommandByNodeIndex,Type2Type<DMI::Vec>(),flags&NEW_ALL);
}
    
} // namespace Meq

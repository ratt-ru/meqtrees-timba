//#  Node_Riders.cc: request rider-related methods of the MeqNode class
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#include "Node.h"
#include "MeqVocabulary.h"
#include <DMI/BlockSet.h>
#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
#include <algorithm>

namespace Meq {


using Debug::ssprintf;
    
void Node::processRequestRider (Request::Ref &reqref) 
{
  // since processCommands() is allowed to modify the request
  // (thus invoking copy-on-write), hold on to the old request in this ref 
  Request::Ref oldreq(reqref,DMI::COPYREF|DMI::READONLY);
  const Request &req = *reqref;
  if( !req.hasRider() )
    return;
  cdebug(3)<<"  processing request rider"<<endl;
  const DataRecord &rider = req[FRider].as<DataRecord>();
  for( uint i=0; i<node_groups_.size(); i++ )
  {
    DataRecord::Hook hgroup(rider,node_groups_[i]);
    if( hgroup.exists() )
    {
      cdebug(3)<<"    found CSR for group "<<node_groups_[i]<<endl;
      DataRecord::Ref group = hgroup.ref();
      // check for command_all entry
      {
        DataRecord::Hook hlist(group,FCommandAll);
        if( hlist.exists() )
        {
          cdebug(4)<<"    found "<<FCommandAll<<", calling processCommands()"<<endl;
          processCommands(hlist.as<DataRecord>(),reqref);
        }
      }
      // process command_by_list (pattern matching list)
      {
        DataRecord::Hook hlist(group,FCommandByList);
        if( hlist.exists() )
        {
          // access list as a NestableContainer (this can be a DataField or
          // a DataList, either should work fine)
          const NestableContainer &list = *(
                hlist.ref().ref_cast<NestableContainer>());
          cdebug(3)<<"      checking "<<list.size()<<" list entries"<<endl;
          bool matched = false;
          for( int i=0; i<list.size() && !matched; i++ )
          {
            const DataRecord &entry = list[i].as<DataRecord>();
            std::vector<string> names;
            std::vector<int> indices;
            DataRecord::Hook hnames(entry,FName),
                 hindices(entry,FNodeIndex);
            if( hnames.exists() ) // get list of names, if any
              names = hnames;
            if( hindices.exists() ) // get list of node indices, if any
              indices = hindices;
            cdebug(4)<<"        "<<indices.size()<<" indices, "
                     <<names.size()<<" names"<<endl;
            // check for node name or node index match
            matched = ( std::find(indices.begin(),indices.end(),nodeIndex())
                          != indices.end() ||
                        std::find(names.begin(),names.end(),name())
                          != names.end() ||
                        ( names.empty() && indices.empty() ) );
            // call appropriate handlers if node was matched
            if( matched )
            {
              cdebug(4)<<"        node matched, calling processCommands()"<<endl;
              processCommands(entry,reqref);
            }
          }
          if( !matched ) {
            cdebug(3)<<"      no matches in list"<<endl;
          }
        }
      }
      // process command_by_nodeindex list
      {
        DataRecord::Hook hlist(group,FCommandByNodeIndex);
        if( hlist.exists() && hlist[nodeIndex()].exists() )
        {
          cdebug(4)<<"    found "<<FCommandByNodeIndex<<"["<<nodeIndex()<<"], calling processCommands()"<<endl;
          processCommands(hlist.as<DataRecord>(),reqref);
        }
      }
    }
  }
}

template<class Container,class Subcontainer>
static Subcontainer & getOrInsert (Container &container,
                                   const HIID &field,
                                   Type2Type<Subcontainer> = Type2Type<Subcontainer>(),
                                   bool replace=false)
{
  int dum;
  Subcontainer *ptr;
  NestableContainer::Hook hook(container,field);
  if( replace )
    hook.replace() <<= ptr = new Subcontainer;
  else if( hook.exists() )
    ptr = hook.as_wp(dum,Type2Type<Subcontainer>());
  else
    hook <<= ptr = new Subcontainer;
  return *ptr;
}

//## Inits (if necessary) and returns a the subrecord rec[id]
DataRecord & Node::Rider::getOrInit (DataRecord &rec,const HIID &id)
{
  return getOrInsert(rec,id,Type2Type<DataRecord>());
}


// Clears the rider from the request, if any.
// Reqref will be privatized for writing if needed.
void Node::Rider::clear (Request::Ref &reqref)
{
  DataRecord::Hook rhook(reqref,FRider);
  if( rhook.exists() )
    rhook.remove();
}

DataRecord & Node::Rider::getRider (Request::Ref &reqref,int flags)
{
  return getOrInsert(reqref,FRider,Type2Type<DataRecord>(),flags&NEW_RIDER);
}

// Inits (if necessary) and returns the group command record for 'group'.
// Reqref will be privatized for writing if needed.
// If the NEW_RIDER flag is given, always creates a new rider.
// If the NEW_GROUPREC flag is given, always creates a new GCR.
DataRecord & Node::Rider::getGroupRec (Request::Ref &reqref,const HIID &group,int flags)
{
  return getOrInsert(getRider(reqref,flags),group,Type2Type<DataRecord>(),
            flags&(NEW_GROUPREC|NEW_RIDER));
}
    
// Inits (if necessary) and returns the command_all subrecord for the given group.
// Reqref will be privatized for writing if needed.
// If the NEW_RIDER flag is given, always creates a new rider.
// If the NEW_GROUPREC flag is given, always creates a new GCR.
// If the NEW_CMDREC flag is given, always creates a new command subrecord.
DataRecord & Node::Rider::getCmdRec_All (Request::Ref &reqref,const HIID &group,int flags)
{
  // get or insert Rider subrecord
  DataRecord &cmdrec = getGroupRec(reqref,group,flags);
  return getOrInsert(cmdrec,FCommandAll,Type2Type<DataRecord>(),flags&NEW_ALL);
}
    
// Inits (if necessary) and returns the command_by_nodeindex subrecord for 
// the given group. Reqref will be privatized for writing if needed.
// If the NEW_RIDER flag is given, always creates a new rider.
// If the NEW_GROUPREC flag is given, always creates a new GCR.
// If the NEW_CMDREC flag is given, always creates a new command subrecord.
DataRecord & Node::Rider::getCmdRec_ByNodeIndex (Request::Ref &reqref,const HIID &group,int flags)
{
  // get or insert Rider subrecord
  DataRecord &cmdrec = getGroupRec(reqref,group,flags);
  return getOrInsert(cmdrec,FCommandByNodeIndex,Type2Type<DataRecord>(),flags&NEW_ALL);
}

// Inits (if necessary) and returns the command_by_list subrecord (field) for 
// the given group. Reqref will be privatized for writing if needed.
// If the NEW_RIDER flag is given, always creates a new rider.
// If the NEW_GROUPREC flag is given, always creates a new GCR.
// If the NEW_CMDREC flag is given, always creates a new command subrecord.
DataField & Node::Rider::getCmdRec_ByList (Request::Ref &reqref,const HIID &group,int flags)
{
  // get or insert Rider subrecord
  DataRecord &cmdrec = getGroupRec(reqref,group,flags);
  return getOrInsert(cmdrec,FCommandByNodeIndex,Type2Type<DataField>(),flags&NEW_ALL);
}
    
void Node::Rider::addSymDepMask (Request::Ref &reqref,
      const HIID &symdep,int mask,const HIID &group)
{
  DataRecord &cmdrec = getCmdRec_All(reqref,group);
  DataRecord &deprec = getOrInsert(cmdrec,FAddDepMask,Type2Type<DataRecord>());
  DataRecord::Hook hook(deprec,symdep);
  if( hook.exists() )
    hook.as_wr<int>() |=  mask;
  else
    hook = mask;
}



} // namespace Meq

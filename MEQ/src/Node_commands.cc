//#  Node_commands.cc: commands and request rider-related methods of the Node class
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
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
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <DMI/NumArray.h>
#include <algorithm>

namespace Meq {


using Debug::ssprintf;


// process Node-specific commands
int Node::processCommand (Result::Ref &,
                          const HIID &command,
                          DMI::Record::Ref &args,
                          const RequestId &,
                          int verbosity)
{
  int retcode = RES_OK;
  if( command == FState )
  {
    setState(args);
    if( verbosity>0 )
      postMessage("node state updated");
  }
  else if( command == HIID("Set.State") )
  {
    DMI::Record::Ref state = args[FState].remove();
    setState(state);
    if( verbosity>0 )
      postMessage("node state updated");
  }
  else if( command == HIID("Clear.Cache") )
  {
    bool recursive = args.valid() && args[FRecursive].as<bool>(false);
    clearCache(recursive,time(0));
    if( verbosity>0 )
      postMessage(recursive ? "cache cleared recursively" : "cache cleared");
  }
  else if( command == HIID("Clear.Cache.Recursive") )
  {
    clearCache(true,time(0));
    if( verbosity>0 )
      postMessage("cache cleared recursively");
  }
  else if( command == HIID("Set.Publish.Level") )
  {
    int level = args.valid() ? args[FLevel].as<int>(1) : 1;
    setPublishingLevel(level);
    if( verbosity>0 )
      postMessage(level?"publishing snapshots":"not publishing snapshots");
  }
  else if( command == HIID("Set.Breakpoint") )
  {
    int bp = Node::breakpointMask(Node::CS_ES_REQUEST);
    if( args.valid() )
      bp = args[FBreakpoint].as<int>(bp);
    bool oneshot = args.valid() && args[FSingleShot].as<bool>(false);
    setBreakpoint(bp,oneshot);
    if( verbosity>0 )
      postMessage(ssprintf("set %sbreakpoint %X; new bp mask is %X",
                           oneshot?"one-shot ":"",
                           bp,getBreakpoints(oneshot)));
  }
  else if( command == HIID("Clear.Breakpoint") )
  {
    int bp = BP_ALL;
    if( args.valid() )
      bp = args[FBreakpoint].as<int>(bp);
    bool oneshot = args.valid() && args[FSingleShot].as<bool>(false);
    clearBreakpoint(bp,oneshot);
    if( verbosity>0 )
      postMessage(ssprintf("cleared %sbreakpoint %X; new bp mask is %X",
                           oneshot?"one-shot ":"",
                           bp,getBreakpoints(oneshot)));
  }
  else
    return 0; // command not found
  // if we got here the command was valid
  return retcode;
}


int Node::processCommands (Result::Ref &resref,const DMI::Record &list,const RequestId &rqid)
{
  int retcode = 0;
  for( DMI::Record::const_iterator iter = list.begin(); iter != list.end(); iter++ )
  {
    const HIID &command = iter.id();
    // skip fields called "name" and "nodeindex" since they are not commands
    // but rather selection fields for the command_by_list rider
    if( command == FName || command == FNodeIndex )
      continue;
    // assignment will throw an error if not referencing a DMI::Record
    DMI::Record::Ref args = iter.ref();
    retcode |= processCommand(resref,command,args,rqid,0);
  }
  return retcode;
}

int Node::processRequestRider (Result::Ref &resref,const Request &req)
{
  if( !req.hasRider() )
    return 0;
  int retcode = 0;
  cdebug(3)<<"  processing request rider"<<endl;
  const DMI::Record &rider = req.rider();
  for( uint i=0; i<node_groups_.size(); i++ )
  {
    if( !rider.hasField(node_groups_[i]) )
      continue;
    cdebug(3)<<"    found CSR for group "<<node_groups_[i]<<endl;
    const DMI::Record &group = rider.as<DMI::Record>(node_groups_[i]);
    // check for command_all entry
    if( group.hasField(FCommandAll) )
    {
      cdebug(4)<<"    found "<<FCommandAll<<", calling processCommands()"<<endl;
      retcode |= processCommands(resref,group.as<DMI::Record>(FCommandAll),req.id());
    }
    // process command_by_list (pattern matching list)
    if( group.hasField(FCommandByList) )
    {
      // access list as a DMI::Container (this can be a DMI::Vec or
      // a DMI::List, either should work fine)
      const DMI::Container &list = group.as<DMI::Container>(FCommandByList);
      cdebug(3)<<"      checking "<<list.size()<<" list entries"<<endl;
      bool matched = false;
      for( int i=0; i<list.size() && !matched; i++ )
      {
        const DMI::Record &entry = list[i].as<DMI::Record>();
        std::vector<string> names;
        std::vector<int> indices;
        DMI::Record::Hook hnames(entry,FName),
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
          retcode |= processCommands(resref,entry,req.id());
        }
      }
      if( !matched )
      {
        cdebug(3)<<"      no matches in list"<<endl;
      }
    }
    if( group.hasField(FCommandByNodeIndex) )
    // process command_by_nodeindex list
    {
      const DMI::Record &entry = group.as<DMI::Record>(FCommandByNodeIndex);
      HIID ni(nodeIndex());
      if( entry.hasField(ni) )
      {
        cdebug(4)<<"    found "<<FCommandByNodeIndex<<"["<<nodeIndex()<<"], calling processCommands()"<<endl;
        retcode |= processCommands(resref,entry.as<DMI::Record>(ni),req.id());
      }
    }
  }
  return retcode;
}

} // namespace Meq

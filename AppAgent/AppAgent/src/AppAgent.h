//  AppAgent.h: abstract interface for an application agent
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
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

#ifndef _APPAGENT_APPAGENT_H
#define _APPAGENT_APPAGENT_H 1

#include "Common/Debug.h"
#include "DMI/DataRecord.h"    
  
#pragma aidgroup AppAgent
#pragma aid AppAgent Event
    
//##ModelId=3DF9FEEC0043
//##Documentation
//## AppAgent is an abstract interface class for an "application agent". An
//## agent sits between an application and a data source or sink. The AppAgent
//## interface hides the details of a particular data source: it can be a
//## measurement set, a pipeline, a test file, etc.
//## 
//## Agents talk to an application by exchanging events. Each event has an id
//## (a HIID), and can contain an arbitrary DataRecord.
class AppAgent
{
  public:
    //##ModelId=3DF9FEEC0066
      virtual ~AppAgent ()
      {}
  
    //##ModelId=3DF9FEEC0068
    //##Documentation
    //## Agent initialization method. Called by the application to initialize
    //## or reinitialize an agent. Agent parameters are supplied via a
    //## DataRecord.
      virtual bool init (const DataRecord::Ref &data) = 0;
      
      // closes the agent (can be reopened with init())
    //##ModelId=3DF9FEEC006D
    //##Documentation
    //## Applications call close() when they're done speaking to an agent.
      virtual void close ()
      {}
  
    //##ModelId=3DF9FEEC0073
    //##Documentation
    //## Requests the next event from an agent. The event's id and DataRecord
    //## are returned via the first two parameters. If no event is currently
    //## pending, the agent should either block & wait for an event (for
    //## wait=True), or return False (for wait=False). On success, True is
    //## returned.
      virtual bool getEvent   (HIID &,DataRecord::Ref &,bool wait = False)
      { return False; }

    //##ModelId=3DF9FEEC0078
    //##Documentation
    //## Returns True if there is an event pending that matches the specified
    //## mask (default - no mask - matches any event). If the agent maintains
    //## an ordered event queue, then outOfSeq=True can be specified to look
    //## ahead into the queue.
      virtual bool hasEvent   (const HIID &mask = HIID(),bool outOfSeq = False)
      { return False; };

    //##ModelId=3DF9FEEC006F
    //##Documentation
    //## Posts an event on behalf of the application.
      virtual void postEvent  (const HIID &,const DataRecord::Ref & = DataRecord::Ref() )
      {};

    //##ModelId=3DF9FEEC006B
    //##Documentation
    //## Flushes any output events (commits to disk, or sends out to OCTOPUSSY,
    //## or whatever)
      virtual void flush ()
      {}
      
      
    //##ModelId=3E00AFAE01D7
      virtual string sdebug ( int detail = 1,const string &prefix = "",
                              const char *name = 0 ) const
      { return "AppAgent"; }

    //##ModelId=3E00AFB100F5
      const char * debug ( int detail = 1,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
};
    
    
#endif
    

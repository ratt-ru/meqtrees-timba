//  VisInputAgent.h: agent for input of VisTiles
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

#ifndef _VISAGENT_INPUTAGENT_H
#define _VISAGENT_INPUTAGENT_H 1
    
#include <AppAgent/AppAgent.h>
#include <AppAgent/AppEventAgentBase.h>
#include <AppAgent/VisAgentVocabulary.h>
#include <AppAgent/DataStreamMap.h>
#include <VisCube/VTile.h>

namespace AppAgent
{    
using namespace DMI;
class AppEventSink;

namespace VisAgent 
{
using namespace VisCube;
      
//##ModelId=3DF9FECD0169
//##Documentation
//## VisInputAgent is an specialized agent representing an input stream of
//## visibility data. Applications that work with visibilities talk to
//## VisInputAgents.
//## 
//## VisInputAgent  is an abstract interface. Specific visibility data sources
//## (e.g.: input from an AIPS++ MS, input from a BOIO file, input from an
//## OCTOPUSSY WorkProcess) are implemented as derived classes.
//## 
//## A visibility stream is represented by a header (a DMI::Record), followed by
//## a number of VisCube::VTiles. 
class InputAgent : public AppEventAgentBase
{
  public:
    //##ModelId=3E41433F01DD
    explicit InputAgent (const HIID &initf = AidInput);
    //##ModelId=3E41433F037E
    InputAgent (AppEventSink &sink, const HIID &initf = AidInput,int flags=0);
    //##ModelId=3E50FAB702CB
    InputAgent (AppEventSink *sink, const HIID &initf = AidInput,int flags=0);
    
    //##ModelId=3E42350F01EB
    //##Documentation
    //## Agent initialization method. Called by the application to initialize
    //## or reinitialize an agent. Agent parameters are supplied via a
    //## DMI::Record.
      virtual bool init (const DMI::Record &data);
      
    //##ModelId=3EB242F5014F
    //##Documentation
    //## Gets next object from input stream. 
    //## All other get...() methods below are implemented in terms of this.
    //## Returns: HEADER/TILE/FOOTER if an object has been retrieved
    //##          WAIT      object has not yet arrived (for wait==NOWAIT)
    //##          CLOSED    stream closed
    //##          OUTOFSEQ  next object in stream is not of requested type
      virtual int getNext ( HIID &id,       // returns ID of object
                            ObjRef &ref,    // object will be attached to this ref
                            int expect_type = 0,  // if specified, only returns a specific type of object
                            int wait = AppEvent::WAIT );
                            
    //##ModelId=3EB242F5031B
    //##Documentation
    //## Checks if an object is waiting in the stream. Return value: same as
    //## would have been returned by getNext(id,ref,0,NOWAIT).
      virtual int hasNext () const;
      
    //##ModelId=3EB242F6001C
    //##Documentation
    //## Alias for getNext() when you don't need an ID
      int getNext (ObjRef &ref,int expect_type = 0,int wait = AppEvent::WAIT)
      { 
        HIID dum; 
        return getNext(dum,ref,expect_type,wait); 
      }
  
    //##ModelId=3EB242F50368
    //## Checks if an object of a specific type is waiting in the stream. 
    //## Return value: same as would have been returned by 
    //## getNext(id,ref,expect_type,NOWAIT).
      int hasNext (int expect_type) const
      {
        int res = hasNext();
        return res == expect_type ? AppEvent::SUCCESS :
               ( res <= 0 ? res : AppEvent::OUTOFSEQ );
      }
      
    //##ModelId=3DF9FECF0310
    //##Documentation
    //## Gets visibilities header from input stream. If wait=true, blocks until
    //## one has arrived.
    //## Returns: SUCCESS   on success
    //##          WAIT      header has not yet arrived (only for wait=false)
    //##          CLOSED    stream closed
    //##          OUTOFSEQ  next object in stream is not a header (i.e. a tile)
      template<class RefType>
      int getSpecificType (RefType &obj,int typecode,int wait = AppEvent::WAIT)
      { 
        ObjRef ref;
        int res = getNext(ref,typecode,wait);
        if( res != typecode ) 
          return res;
        obj = ref; 
        return AppEvent::SUCCESS;
      }
        
    //##ModelId=3DF9FECF0310
      int getHeader   (DMI::Record::Ref &hdr,int wait = AppEvent::WAIT)
      { return getSpecificType(hdr,HEADER,wait); }
      
    //##ModelId=3DF9FECF03A9
      int getNextTile (VTile::Ref &tile,int wait = AppEvent::WAIT)
      { return getSpecificType(tile,DATA,wait); }
      
    //##ModelId=3EB242F601A6
      int getFooter   (DMI::Record::Ref &ftr,int wait = AppEvent::WAIT)
      { return getSpecificType(ftr,FOOTER,wait); }
  
    //##ModelId=3DF9FED0005A
    //##Documentation
    //## Checks if a header is waiting in the stream. 
      int hasHeader   () const
      { return hasNext(HEADER); }
      
    //##ModelId=3DF9FED00076
    //##Documentation
    //## Checks if a tile is waiting in the stream. 
      int hasTile     () const
      { return hasNext(DATA); }
      
    //##ModelId=3EB2434D0000
    //## Checks if a footer is waiting in the stream. 
      int hasFooter   () const
      { return hasNext(FOOTER); }
      
    //##ModelId=3EB2434D0054
    //##Documentation
    //## Tells the agent to suspend the input stream. Agents are not obliged to
    //## implement this. An application can use suspend() to "advise" the input
    //## agent that it is not keeping up with the input data rate; the agent
    //## can use this to determine it queuing or load balancing strategy.
      virtual void suspend     ();
      
    //##ModelId=3EB2434D008D
    //##Documentation
    //## Resumes a stream after a suspend(). 
      virtual void resume      ();
      
    //##ModelId=3EB2434D00CB
      bool suspended() const;
      
    //##ModelId=3EB2434D0107
    //##Documentation
    //## Returns the number of tiles queued up in a stream. Agents are not
    //## obliged to implement this. Control agents are meant to use this method
    //## in combination with suspend()/resume() to control the data flow. 
      virtual int  numPendingTiles ()
      { return hasTile() == AppEvent::SUCCESS ? 1 : 0; }
      
    //##ModelId=3EB2434D014F
      virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
      
    //##ModelId=3EB2434D0301
      DefineRefTypes(InputAgent,Ref);
      
    //##ModelId=3F5F43660038
      LocalDebugContext;

  private:
    //##ModelId=3EB2434E0015
    InputAgent();

    //##ModelId=3EB2434E0066
    InputAgent(const InputAgent& right);

    //##ModelId=3EB2434E012C
    InputAgent& operator=(const InputAgent& right);
    
    //##ModelId=3EB2434C031D
    bool suspended_;
    
    //##ModelId=3EB2434C03A0
    static DataStreamMap & datamap;
};

//##ModelId=3EB2434D00CB
inline bool InputAgent::suspended() const
{
    return suspended_;
}

} // namespace VisAgent

};
 
#endif


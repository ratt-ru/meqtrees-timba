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

#ifndef OCTOAGENT_SRC_EVENTCHANNEL_H_HEADER_INCLUDED_833D2E92
#define OCTOAGENT_SRC_EVENTCHANNEL_H_HEADER_INCLUDED_833D2E92

#include <DMI/Record.h>
#include <AppAgent/EventChannel.h>
#include <OCTOPUSSY/WPInterface.h>
#include <AppAgent/AID-AppAgent.h>
    
#include <map>
    
#pragma aidgroup AppAgent
#pragma aid Agent Map Receive Post In Out
#pragma aid Default Scope Unmapped Prefix Local Host Global
#pragma aid Priority Lowest Lower Low Normal High Higher
    
namespace AppAgent
{
  
const HIID
    FEventMapIn       = AidEvent|AidMap|AidIn,
    FEventMapOut      = AidEvent|AidMap|AidOut,

    FDefaultScope     = AidDefault | AidScope,
    FDefaultPriority  = AidDefault | AidPriority,
    
    FDefaultPrefix    = AidDefault | AidPrefix;
  
class OctoEventMux;

//##ModelId=3DF9FECD014B
class OctoChannel : public EventChannel
{
  public:
    //##ModelId=3E42934901EB
    LocalDebugContext;  
  
    //##ModelId=3E26DA36005C
    OctoChannel ();
    //##ModelId=3E26DA3602F4
    OctoChannel (OctoEventMux& mux,int flags = DMI::WRITE);
    //##ModelId=3E26DA370170
    virtual ~OctoChannel();

        //##ModelId=3E51161B0216
    virtual bool isAsynchronous() const
    { return true; }

    //##ModelId=3E091DDD02B8
    void attach (OctoEventMux& mux,int flags = DMI::WRITE);
    
    //##ModelId=3E27F30B019B
    //##Documentation
    //## Agent initialization method. This sets the receive and post maps
    //## from data[map_field_name][FMapReceive] and
    //##      data[map_field_name][FMapPost]
    virtual int init (const DMI::Record &data);

    //##ModelId=3E50E88903AD
    //##Documentation
    //## Applications call close() when they're done speaking to an agent.
    virtual void close (const string &str="");
    
    //##ModelId=3E0A295102A5
    //##Documentation
    //## Sets up a mapping of input events to message IDs
    void setReceiveMap (const DMI::Record &map);
    //##ModelId=3E0A296A02C8
    //##Documentation
    //## Sets up a mapping of output events to message IDs
    void setPostMap (const DMI::Record &map);

    //##ModelId=3E26CBBC03E4
    bool mapReceiveEvent  (HIID &out,const HIID &in) const;
    //##ModelId=3E2FEAD10188
    bool mapPostEvent     (HIID &out,const HIID &in,AtomicID category) const;
    
    //##ModelId=3E8C47930062
    //##Documentation
    //## Advertises the fact that an app is interested in a specific
    //## event or set of events (wildcards may be employed). This corresponds
    //## to subscribing to events in the OctoAgent implementation.
    virtual void solicitEvent (const HIID &mask);
    
    //##ModelId=3E096F2103B3
    //##Documentation
    //## Gets next event from proxy's message queue. This version will return
    //## any type of payload, not just DMI::Records, hence the ObjRef data
    //## argument.
    virtual int getEvent (HIID &id,ObjRef &data,const HIID &mask,
                          int wait = AppEvent::WAIT,
                          HIID &source = _dummy_hiid );
    
    //##ModelId=3E0918BF02F0
    //##Documentation
    //## Checks for event in proxy WP's message queue.
    virtual int hasEvent (const HIID &mask = HIID(),HIID &out=_dummy_hiid);

    //##ModelId=3E2FD67D0246
    //##Documentation
    //## Publishes an event as a message on behalf of the proxy. 
    virtual void postEvent (const HIID &id,
                            const ObjRef &data = ObjRef(),
                            AtomicID category = AidNormal,
                            const HIID &destination = HIID() );
    
    //##ModelId=3E8C47930088
    //##Documentation
    //## Checks whether a specific event is bound to any output. I.e., checks
    //## for subscribers to the event.
    virtual bool isEventBound (const HIID &id,AtomicID category);
    
    //##ModelId=3E3FC3E00194
    void setMultiplexId (int id);
    
    //##ModelId=3E26E2F901E3
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    
    //##ModelId=3E428EA60051
    DefineRefTypes(OctoChannel,Ref);
    

  protected:
    // helper functions for parsing the event maps. These look up default
    // arguments in the maps
    //##ModelId=3E0A34E7020E
    int getDefaultScope    (const DMI::Record &map);
    //##ModelId=3E0A4C7B0006
    int getDefaultPriority (const DMI::Record &map);
    
    // checks ID for scope or priority prefix, strips it off and interprets
    // as integer value. If no valid prefix is found, returns input value.
    //##ModelId=3E0A34E801D6
    int resolveScope       (HIID &id,int scope);
    //##ModelId=3E0A4C7D007A
    int resolvePriority    (HIID &id,int priority);

  private:
    //##ModelId=3E42745302E3
    OctoChannel (const OctoChannel& right);
    //##ModelId=3E26DA370287
    OctoChannel & operator=(const OctoChannel& right);
    
    //##ModelId=3E4274530119
    typedef struct { HIID id; int scope,priority; } EventMapEntry;
    //##ModelId=3E427453014D
    typedef std::map<HIID,EventMapEntry> EventMap;
    //##ModelId=3E4274530181
    typedef EventMap::const_iterator EMCI;
    
    //##ModelId=3E42937F03D7
    //##Documentation
    //## Maps message IDs to input events
    EventMap receive_map;
    
    //##ModelId=3E429380001C
    //## Maps posted events to message IDs
    EventMap post_map;

    //##ModelId=3E0A29D202D1
    //##Documentation
    //## true if events without a mapping are to be published anyway 
    //## (as unmapped_prefix.event_id, with unmapped_scope and _priority)
    bool publish_unmapped_events;
    //##ModelId=3E0A367402F0
    HIID default_receive_prefix;
    //##ModelId=3F5F4364028A
    HIID default_post_prefix;
    // map of specific per-category event prefixes
    typedef std::map<AtomicID,HIID> CategoryPrefixes;
    CategoryPrefixes category_post_prefix;
    //##ModelId=3E0A3A980187
    int default_receive_scope;
    //##ModelId=3E9BD63F035D
    int default_post_scope;
    //##ModelId=3E0A4C7A0008
    int default_post_priority;
    
    //##ModelId=3E428C4D0237
    OctoEventMux *multiplexer;
    
    //##ModelId=3E3FC3DF031A
    int my_multiplex_id;
    
    // dummy default argument for functions
    //##ModelId=3E26D477006C
    static DMI::Record _dum;
  
};

//##ModelId=3E3FC3E00194
inline void OctoChannel::setMultiplexId (int id)
{
  my_multiplex_id = id;
}


};
#endif /* OCTOAGENT_SRC_OCTOAGENT_H_HEADER_INCLUDED_833D2E92 */

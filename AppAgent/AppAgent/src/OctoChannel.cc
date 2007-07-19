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

#include "OctoEventMux.h"
#include "OctoChannel.h"
#include "DMI/Record.h"

namespace AppAgent
{

using namespace Octopussy;        
  
InitDebugContext(OctoChannel,"OctoChannel");
    
DMI::Record OctoChannel::_dum;

//##ModelId=3E26DA36005C
OctoChannel::OctoChannel()
    : multiplexer(0),my_multiplex_id(-1)
{
}

//##ModelId=3E26DA3602F4
OctoChannel::OctoChannel (OctoEventMux& mux,int flags)
    : multiplexer(0),my_multiplex_id(-1)
{
  attach(mux,flags);
}

//##ModelId=3E26DA370170
OctoChannel::~OctoChannel()
{
}
  
//##ModelId=3E091DDD02B8
void OctoChannel::attach (OctoEventMux& mux,int flags)
{
  FailWhen(multiplexer,"already attached to multiplexer");
  cdebug(2)<<"attaching to multiplexer "<<mux.sdebug(1)<<endl;
  multiplexer = &mux;
  mux.addChannel(this,flags);
}

//##ModelId=3E27F30B019B
int OctoChannel::init (const DMI::Record &data)
{
  if( EventChannel::init(data) < 0 )
    return state();
  FailWhen(!multiplexer,"no mux attached");
  cdebug(1)<<"initializing"<<endl;
  multiplexer->init();
// setup input event map
  if( data[FEventMapIn].exists() )
    setReceiveMap(data[FEventMapIn].as<DMI::Record>());
  else
  {
    cdebug(1)<<"no input event map\n";
  }
// setup output event map
  if( data[FEventMapOut].exists() )
    setPostMap(data[FEventMapOut].as<DMI::Record>());
  else
  {
    cdebug(1)<<"no output event map\n";
  }
  return setState(OPEN);
}

//##ModelId=3E50E88903AD
void OctoChannel::close (const string &str)
{
  if( multiplexer )
    multiplexer->close();
  EventChannel::close(str);
}

//##ModelId=3E26CAE001BA
bool OctoChannel::mapReceiveEvent (HIID &out, const HIID &in) const
{
  // check the receive map
  EMCI iter = receive_map.find(in);
  if( iter != receive_map.end() )
  {
    out = iter->second.id; // found it
    return true;
  }
  // not explicitly mapped -- have we got a matching default prefix then
  if( default_receive_prefix.size() && in.prefixedBy(default_receive_prefix) )
  {
    // strip off prefix and return
    out = in.subId(default_receive_prefix.size());
    return true;
  }
  else
    return false;
}

//##ModelId=3E2FEAD10188
bool OctoChannel::mapPostEvent (HIID &out,const HIID &in,AtomicID category) const
{
  // is the event explicitly in the post map?
  EMCI iter = post_map.find(category|in);
  if( iter != post_map.end() )
  {
    out = iter->second.id;
    return true;
  }
  // have we got a category-specific prefix?
  CategoryPrefixes::const_iterator icat = category_post_prefix.find(category);
  if( icat != category_post_prefix.end() )
  {
    if( !icat->second.empty() )
    {
      out = icat->second | in;
      return true;
    }
    else
      return false;
  }
  // have we got a default prefix?
  if( !default_post_prefix.empty() )
  {
    out = default_post_prefix | in;
    return true;
  }
  else
    return false;
}

//##ModelId=3E8C47930062
void OctoChannel::solicitEvent (const HIID &)
{
  // check if mask is a real 
}

//##ModelId=3E096F2103B3
int OctoChannel::getEvent (HIID &id,ObjRef &data,const HIID &mask,int wait,HIID &source)
{
  FailWhen(!multiplexer,"no mux attached");
  int res = multiplexer->getEvent(id,data,mask,wait,source,my_multiplex_id);
  if( res == AppEvent::SUCCESS )
    recordInputEvent(id,data,source);
  return res;      
}

//##ModelId=3E0918BF02F0
int OctoChannel::hasEvent (const HIID &mask,HIID &out)
{
  FailWhen(!multiplexer,"no mux attached");
  return multiplexer->hasEvent(mask,out,my_multiplex_id);
}

//##ModelId=3E2FD67D0246
void OctoChannel::postEvent (const HIID &id,const ObjRef &data,
                             AtomicID category,const HIID &dest)
{
  cdebug(3)<<"postEvent("<<id<<")\n";
  recordOutputEvent(id,data,category,dest);
  // find event in output map
  EMCI iter = post_map.find(category|id);
  Message::Ref mref;
  int scope;
  if( iter == post_map.end() )
  {
    HIID msgid;
    // not found in explicit map - do we have a category-specific prefix?
    CategoryPrefixes::const_iterator iter = category_post_prefix.find(category);
    if( iter != category_post_prefix.end() )
    {
      if( iter->second.empty() ) // null prefix means do not post
      {
        cdebug(3)<<"unmapped event posted, dropping\n";
        return;
      }
      msgid = iter->second | id;
    }
    else // else check for default prefix
    {
      if( default_post_prefix.empty() )
      {
        cdebug(3)<<"unmapped event posted, dropping\n";
        return;
      }
      msgid = default_post_prefix | id;
    }
    mref <<= new Message(msgid,default_post_priority);
    scope = default_post_scope;
  }
  else // get ID and scope from map
  {
    // is it specifically mapped to null ID? ignore then
    if( iter->second.id.empty() )
    {
      cdebug(3)<<"event disabled in output map, dropping"<<endl;
      return;
    }
    mref <<= new Message(iter->second.id,iter->second.priority);
    scope = iter->second.scope;
  }
  // attach payload to message
  mref().payload() = data;
  if( dest.size() )
  {
    cdebug(3)<<"sending "<<mref->sdebug(2)<<", to "<<dest<<endl;
    multiplexer->send(mref,dest);
  }
  else
  {
    cdebug(3)<<"publishing as "<<mref->sdebug(2)<<", scope "<<scope<<endl;
    multiplexer->publish(mref,scope);
  }
}

//##ModelId=3E8C47930088
bool OctoChannel::isEventBound (const HIID &id,AtomicID cat)
{
  HIID out;
  // event not mapped at all? Return false
  if( !mapPostEvent(out,id,cat) )
    return false;
  // else true
  // BUG! actually we need a haveSubscribers() call here
  return true;
}


//##ModelId=3E0A34E7020E
int OctoChannel::getDefaultScope (const DMI::Record &map)
{
  // looks at map to determine the default publish or subscribe scope
  if( map[FDefaultScope].exists() )
  {
    // publish scope can be specified as string or int
    if( map[FDefaultScope].type() == Tpstring )
    {
      string str = map[FDefaultScope].as<string>(); // .upcase();
      if( str == "LOCAL" )
        return Message::LOCAL;
      else if( str == "HOST" )
        return Message::HOST;
      else if( str == "GLOBAL" )
        return Message::GLOBAL;
      else
      {
        Throw("illegal "+FDefaultScope.toString()+" value: "+str);
      }
    }
    else
      return map[FDefaultScope].as<int>(); 
  }
  return Message::GLOBAL;
}

//##ModelId=3E0A34E801D6
int OctoChannel::resolveScope (HIID &id,int scope)
{
  // determine scope by looking at first element of ID. Strip off the specifier
  // if it is valid; if not, return default scope value.
  AtomicID first = id.front();
  if( first == AidGlobal )
  {
    scope = Message::GLOBAL; id.pop_front();
  }
  else if( first == AidHost )
  {
    scope = Message::HOST; id.pop_front();
  }
  else if( first == AidLocal )
  {
    scope = Message::LOCAL; id.pop_front();
  }
  return scope;
}

//##ModelId=3E0A4C7D007A
int OctoChannel::resolvePriority (HIID &id,int priority)
{
  // determine scope by looking at first element of ID. Strip off the specifier
  // if it is valid; if not, return default scope value.
  AtomicID first = id.front();
  switch( first.id() )
  {
    case AidLowest_int:   priority = Message::PRI_LOWEST;  break;
    case AidLower_int:    priority = Message::PRI_LOWER;   break;
    case AidLow_int:      priority = Message::PRI_LOW;     break;
    case AidNormal_int:   priority = Message::PRI_NORMAL;  break;
    case AidHigh_int:     priority = Message::PRI_HIGH;    break;
    case AidHigher_int:   priority = Message::PRI_HIGHER;  break;
    default:              return priority;
  }
  id.pop_front();
  return priority;
}

//##ModelId=3E0A4C7B0006
int OctoChannel::getDefaultPriority (const DMI::Record &map)
{
  // looks at map to determine the default priority
  if( !map[FDefaultPriority].exists() )
    return Message::PRI_NORMAL;
  // if specified as a HIID, AtomicID or string, then interpret as a HIID
  // (has to end up as a single-element HIID suitable for resolvePriority(),
  // above)
  HIID id; 
  if( map[FDefaultPriority].type() == TpDMIHIID )
    id = map[FDefaultPriority].as<HIID>();
  else if( map[FDefaultPriority].type() == TpDMIAtomicID )
    id = map[FDefaultPriority].as<AtomicID>();
  else if( map[FDefaultPriority].type() == Tpstring )
    id = map[FDefaultPriority].as<string>();
  // if none of those, then try to interpret as an integer
  else
    return map[FDefaultPriority].as<int>(Message::PRI_NORMAL);
  // use resolvePriority() above to map to a priority constant
  int pri = resolvePriority(id,Message::PRI_NORMAL);
  // ID must be empty now, else error
  FailWhen(!id.empty(),"illegal "+FDefaultPriority.toString());
  return pri;
}

//##ModelId=3E0A295102A5
void OctoChannel::setReceiveMap (const DMI::Record &map)
{
  receive_map.clear();
  // interpret Default.Scope argument
  int defscope = getDefaultScope(map);
  // check for a default subscribe prefix
  default_receive_prefix = map[FDefaultPrefix].as<HIID>(HIID());
  default_receive_scope  = resolveScope(default_receive_prefix,defscope); 
  if( default_receive_prefix.size() )
  {
    cdebug(1)<<"subscribing with default receive prefix: "<<default_receive_prefix<<".*\n";
    multiplexer->subscribe(default_receive_prefix|AidWildcard,default_receive_scope);
  }
  // translate map, and subscribe multiplexer to all input events
  TypeId type; int size;
  int nevents = 0;
  for( DMI::Record::const_iterator iter = map.begin(); iter != map.end(); iter++ )
  {
    const HIID & event = iter.id();
    const ObjRef & ncref = iter.ref();
    // ignore Default.Scope and Prefix arguments
    if( event == FDefaultScope || event == FDefaultPrefix )
      continue;
    const DMI::Container &nc = *ncref.ref_cast<DMI::Container>();
    // all other fields must be event IDs (HIIDs)
    FailWhen(nc.type() != TpDMIHIID,"illegal input map entry "+event.toString());
    for( int i=0; i<nc.size(); i++ )
    {
      HIID msgid = nc[i];
      int scope = resolveScope(msgid,defscope);
      // add to event map and subscribe
      EventMapEntry &ee = receive_map[msgid];
      ee.id = event; ee.scope = scope; 
      multiplexer->subscribe(msgid,scope);
      nevents++;
      cdebug(2)<<"subscribing to "<<msgid<<" (scope "<<scope<<") for event "<<event<<endl;
    }
  }
  dprintf(1)("subscribed to %d explicit input events\n",nevents);
}

//##ModelId=3E0A296A02C8
void OctoChannel::setPostMap (const DMI::Record &map)
{
  post_map.clear();
  // interpret Default.Scope argument
  int defscope = getDefaultScope(map);
  // interpret Default.Priority argument
  int defpri = getDefaultPriority(map);
  // get default posting prefix
  default_post_prefix   = map[FDefaultPrefix].as<HIID>(HIID());
  // get per-category prefixes
  category_post_prefix.clear();
  for( uint i=0; i<sizeof(EventCategories)/sizeof(EventCategories[0]); i++ )
  {
    HIID prefix;
    if( map[EventCategories[i]|AidPrefix].get(prefix) )
      category_post_prefix[EventCategories[i]] = prefix;
  }
  // get other defaults
  default_post_scope    = resolveScope(default_post_prefix,defscope); 
  default_post_priority = resolvePriority(default_post_prefix,defpri); 
  if( default_post_prefix.size() )
  {
    cdebug(1)<<"default posting prefix: "<<default_post_prefix<<endl;
  }
  // translate the map
  publish_unmapped_events = false;
  TypeId type; int size;
  int nevents = 0;
  for( DMI::Record::const_iterator iter = map.begin(); iter != map.end(); iter++ )
  {
    const HIID & id = iter.id();
    const ObjRef & ref = iter.ref();
    // ignore arguments interpreted above
    if( id == FDefaultScope || id == FDefaultPriority || 
        ( id.size() == 2 && id[1] == AidPrefix ) ) 
      continue;
    const DMI::Container &nc = ref.as<DMI::Container>();
    FailWhen(nc.type() != TpDMIHIID || nc.size() != 1,"illegal output map entry "+id.toString());
    HIID msgid = nc[HIID()].as<HIID>();
    int scope = resolveScope(msgid,defscope);
    int priority = resolvePriority(msgid,defpri);
    EventMapEntry &ee = post_map[id];
    ee.id = msgid; ee.scope = scope; ee.priority = priority;
    nevents++;
    if( msgid.empty() )
    {
      cdebug(2)<<"disabling output event "<<id<<endl;
    }
    else
    {
      cdebug(2)<<"mapping event "<<id<<" to message "<<msgid
               <<" (S"<<scope<<"P"<<priority<<")\n";
    }
  }
  dprintf(1)("mapped %d output events\n",nevents);
}

string OctoChannel::sdebug (int detail, const string &prefix, const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"OctoChannel",this);
  }
  if( detail >= 1 || detail == -1 )
  {
    out += "mux:" + multiplexer->sdebug(abs(detail)-1,prefix);
  }
  return out;
}


}

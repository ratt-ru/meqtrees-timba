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

#include "DMI/DynamicTypeManager.h"
#include "DMI/Packer.h"
#include "Message.h"

namespace Octopussy
{

#ifdef ENABLE_LATENCY_STATS
  CHECK_CONFIG_CC(LatencyStats,yes);
#else
  CHECK_CONFIG_CC(LatencyStats,no);
  DummyLatencyVector Message::latency;
#endif
//##ModelId=3C8CB2CE00DC



// Class Message 

Message::Message()
  : flags_(0),priority_(0),state_(0),hops_(0)
{
}

//##ModelId=3C7B9C490384
Message::Message(const Message &right,int flags,int depth)
    : DMI::BObj()
{
  cloneOther(right,flags,depth);
}

//##ModelId=3C7B9D3B02C3
Message::Message (const HIID &id1, DMI::BObj *pload, int flags, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1),payload_(pload,flags)
{
}



//##ModelId=3C7B9D59014A
Message::Message (const HIID &id1, const ObjRef &pload, int flags, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1),payload_(pload,flags)
{
}

//##ModelId=3C7BB3BD0266
Message::Message (const HIID &id1, SmartBlock *bl, int flags, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1),block_(bl,flags)
{
}

//##ModelId=3DB936A5029F
Message::Message (const HIID &id1, const BlockRef &bl, int flags, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1),block_(bl,flags)
{
}

//##ModelId=3DB936A7019E
Message::Message (const HIID &id1, const char *data, size_t sz, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1)
{
  SmartBlock *bl = new SmartBlock(sz);
  block_ <<= bl;
  memcpy(bl->data(),data,sz);
}

//##ModelId=3DB936B40140
Message::Message (const HIID &id1, const DMI::BObj *pload, int flags, int pri)
   : priority_(pri),state_(0),hops_(0),id_(id1),payload_(pload,flags)
{
}

//##ModelId=3DB936B80024
Message::Message (const HIID &id1, const SmartBlock *bl, int flags, int pri)
   : priority_(pri),state_(0),hops_(0),id_(id1),block_(bl,flags)
{
}

//##ModelId=3DB936A90143
Message::~Message()
{
}


//##ModelId=3DB936A901E3
Message & Message::operator= (const Message &right)
{
  if( &right != this )
    cloneOther(right);
  return *this;
}

//##ModelId=3C7B9DDE0137
DMI::BObj & Message::operator <<= (DMI::BObj *pload)
{
  payload_ <<= pload;
  return *pload;
}

//##ModelId=3C7B9DF20014
Message & Message::operator <<= (ObjRef &pload)
{
  payload_ <<= pload;
  return *this;
}

//##ModelId=3C7B9E0A02AD
SmartBlock & Message::operator <<= (SmartBlock *bl)
{
  block_ <<= bl;
  return *bl;
}

//##ModelId=3C7B9E1601CE
Message & Message::operator <<= (BlockRef &bl)
{
  block_ <<= bl;
  return *this;
}

//##ModelId=3C7E32BE01E0
CountedRefTarget* Message::clone (int flags, int depth) const
{
  return new Message(*this,flags,depth);
}

//##ModelId=3C7E32C1022B
void Message::cloneOther (const Message &other,int flags, int depth)
{
  id_ = other.id_;
  flags_ = other.flags_;
  priority_ = other.priority_;
  from_ = other.from_;
  to_ = other.to_;
  state_ = other.state_;
  hops_ = other.hops_;
  //  timestamp_ = other.timestamp_;
#ifdef ENABLE_LATENCY_STATS
  latency = other.latency;
#endif
  payload_.copy(other.payload_,flags,depth);
  block_.copy(other.block_,flags,depth);
}

//##ModelId=3C960F1B0373
int Message::fromBlock (BlockSet& set)
{
  int blockcount = 1;
  // get and unpack header
  BlockRef href;
  set.pop(href);
  const HeaderBlock & hdr = *href->pdata<HeaderBlock>();
  int expect_blockcount = BObj::checkHeader(&hdr);
  FailWhen(href->size() < sizeof(HeaderBlock) ||
           href->size() != sizeof(HeaderBlock) + 
            hdr.idsize + hdr.fromsize + hdr.tosize + hdr.latsize,"corrupt header block");
  priority_ = hdr.priority;
  state_    = hdr.state;
  hops_     = hdr.hops;
  flags_    = hdr.flags;
  const char *buf = href->cdata() + sizeof(HeaderBlock);
  id_.unpack(buf,hdr.idsize);     buf += hdr.idsize;
  from_.unpack(buf,hdr.fromsize); buf += hdr.fromsize;
  to_.unpack(buf,hdr.tosize);     buf += hdr.tosize;
#ifdef ENABLE_LATENCY_STATS
  if( hdr.latsize )
    latency.unpack(buf,hdr.latsize);
  else
    latency.clear();
#else
  // if we get a message with latency stats but we're not compiled to support 
  // them, then they'll simply be ignored
#endif
  //  got a data block?
  if( hdr.has_block )
  {
    set.pop(block_);
    blockcount++;
  }
  else
    block_.detach();
  // got a payload?
  if( hdr.payload_type )
  {
    int nb0 = set.size();
    payload_ = DynamicTypeManager::construct(hdr.payload_type,set);
    FailWhen(!payload_.valid(),"failed to construct payload of type "+TypeId(hdr.payload_type).toString());
    blockcount += nb0 - set.size();
  }
  else
    payload_.detach();
  FailWhen(expect_blockcount!=blockcount,"total block count mismatch in header");
  return blockcount;
}

//##ModelId=3C960F20037A
int Message::toBlock (BlockSet &set) const
{
  // create a header block
  size_t idsize = id_.packSize(),
         tosize = to_.packSize(),
         fromsize = from_.packSize(),
#ifdef ENABLE_LATENCY_STATS
         latsize = latency.packSize(),
#else
         latsize = 0,
#endif
         hsize = idsize + tosize + fromsize + latsize;
  
  SmartBlock *hdrblock = new SmartBlock(sizeof(HeaderBlock)+hsize);
  BlockRef bref(hdrblock,DMI::ANON|DMI::WRITE); 
  HeaderBlock & hdr = *hdrblock->pdata<HeaderBlock>();
  hdr.priority  = priority_;
  hdr.state     = state_;
  hdr.flags     = flags_;
  hdr.hops      = hops_;
  hdr.idsize    = idsize;
  hdr.fromsize  = fromsize;
  hdr.tosize    = tosize;
  hdr.latsize   = latsize;
  hdr.has_block = block_.valid(); 
  hdr.payload_type = payload_.valid() ? payload_->objectType() : NullType;
  char *buf = hdrblock->cdata() + sizeof(HeaderBlock);
  buf += id_.pack(buf,hsize);      
  buf += from_.pack(buf,hsize);    
  buf += to_.pack(buf,hsize);      
#ifdef ENABLE_LATENCY_STATS
  buf += latency.pack(buf,hsize);
#endif
  
  // attach to set
  set.push(bref);
  int blockcount = 1;
  if( block_.valid() )
  {
    set.push(block_);
    blockcount++;
  } 
  if( payload_.valid() )
    blockcount += payload_->toBlock(set);
  
  BObj::fillHeader(&hdr,blockcount);
  return blockcount;
}


//##ModelId=3E301BB10085
DMI::Record & Message::withRecord (Message::Ref &ref,const HIID &id)
{
  Message *pmsg = new Message(id);
  ref <<= pmsg;
  return (*pmsg) <<= new DMI::Record;
}

// second form initializes record with a Text field
//##ModelId=3E301BB10140
DMI::Record & Message::withRecord (Message::Ref &ref,const HIID &id,const string &text)
{
  DMI::Record &rec = withRecord(ref,id);
  rec[AidText] = text;
  return rec;
}

//##ModelId=3DB936C40273
string Message::sdebug ( int detail,const string &prefix,const char *name ) const
{
  string out;
  if( detail>=0 ) // basic detail
  {
    out = name?name:"Message";
    out += "/" + id_.toString('.');
    if( detail>3 )
      out += Debug::ssprintf("/%08x",this);
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    Debug::appendf(out,"%s->%s p:%d s:%x",
        from_.toString().c_str(),to_.toString().c_str(),priority_,state_);
    if( hops_ )
      Debug::appendf(out,"hc:%d",(int)hops_);
    if( detail == 1 )
    {
      Debug::appendf(out,payload_.valid() ? "w/payload" : "",
                         block_.valid() ? "w/block" : "");
    }
  }
  if( detail >=2 || detail <= -2) // high detail
  {
    if( out.length() )
      out += "\n"+prefix;
    if( payload_.valid() )
      out += "  payload: "+payload_.sdebug(abs(detail)-1,prefix+"    ");
    else
      out += "  no payload";
    if( block_.valid() )
      out += "\n"+prefix+"  block: "+block_.sdebug(abs(detail)-1,prefix+"    ");
    else
      out += "  no block";
  }
  return out;
}

};

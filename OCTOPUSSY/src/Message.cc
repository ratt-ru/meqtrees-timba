#include "DMI/DynamicTypeManager.h"
#include "DMI/Packer.h"

// Message
#include "OCTOPUSSY/Message.h"

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
Message::Message(const Message &right)
    : BlockableObject()
#ifdef ENABLE_LATENCY_STATS
    ,latency(right.latency)
#endif
{
  (*this) = right;
}

//##ModelId=3C7B9D3B02C3
Message::Message (const HIID &id1, BlockableObject *pload, int flags, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1)
{
  payload_.attach(pload,flags|DMI::PERSIST|DMI::WRITE);
}



//##ModelId=3C7B9D59014A
Message::Message (const HIID &id1, const ObjRef &pload, int flags, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1)
{
  if( flags&DMI::COPYREF )
    payload_.copy(pload,flags|DMI::PERSIST|DMI::WRITE);
  else
    payload_.xfer(pload).persist();
}

//##ModelId=3C7BB3BD0266
Message::Message (const HIID &id1, SmartBlock *bl, int flags, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1)
{
  block_.attach(bl,flags|DMI::PERSIST|DMI::WRITE);
}

//##ModelId=3DB936A5029F
Message::Message (const HIID &id1, const BlockRef &bl, int flags, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1)
{
  if( flags&DMI::COPYREF )
    block_.copy(bl,flags|DMI::PERSIST|DMI::WRITE);
  else
    block_.xfer(bl).persist();
}

//##ModelId=3DB936A7019E
Message::Message (const HIID &id1, const char *data, size_t sz, int pri)
   : flags_(0),priority_(pri),state_(0),hops_(0),id_(id1)
{
  SmartBlock *bl = new SmartBlock(sz);
  block_.attach( bl,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  memcpy(bl->data(),data,sz);
}

//##ModelId=3DB936B40140
Message::Message (const HIID &id1, const BlockableObject *pload, int flags, int pri)
   : priority_(pri),state_(0),hops_(0),id_(id1)
{
  payload_.attach(pload,flags|DMI::PERSIST|DMI::READONLY);
}

//##ModelId=3DB936B80024
Message::Message (const HIID &id1, const SmartBlock *bl, int flags, int pri)
   : priority_(pri),state_(0),hops_(0),id_(id1)
{
  block_.attach(bl,flags|DMI::PERSIST|DMI::READONLY);
}

//##ModelId=3DB936A90143
Message::~Message()
{
}


//##ModelId=3DB936A901E3
Message & Message::operator=(const Message &right)
{
  if( &right != this )
  {
    id_ = right.id_;
    flags_ = right.flags_;
    priority_ = right.priority_;
    from_ = right.from_;
    to_ = right.to_;
    state_ = right.state_;
    hops_ = right.hops_;
  //  timestamp_ = right.timestamp_;
    payload_.copy(right.payload_,DMI::PRESERVE_RW|DMI::PERSIST);
    block_.copy(right.block_,DMI::PRESERVE_RW|DMI::PERSIST);
  }
  return *this;
}

//##ModelId=3C7B9DDE0137
BlockableObject & Message::operator <<= (BlockableObject *pload)
{
  payload_.attach(pload,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  return *pload;
}

//##ModelId=3C7B9DF20014
Message & Message::operator <<= (ObjRef &pload)
{
  payload_.xfer(pload).persist();
  return *this;
}

//##ModelId=3C7B9E0A02AD
SmartBlock & Message::operator <<= (SmartBlock *bl)
{
  block_.attach(bl,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  return *bl;
}

//##ModelId=3C7B9E1601CE
Message & Message::operator <<= (BlockRef &bl)
{
  block_.xfer(bl).persist();
  return *this;
}

//##ModelId=3C7E32BE01E0
CountedRefTarget* Message::clone (int flags, int depth) const
{
  Message *newmsg = new Message(*this);
  newmsg->privatize(flags,depth);
  return newmsg;
}

//##ModelId=3C7E32C1022B
void Message::privatize (int flags, int depth)
{
  if( flags&DMI::DEEP || depth>0 )
  {
    if( payload_.valid() )
      payload_.privatize(flags,depth-1);
    if( block_.valid() )
      block_.privatize(flags,depth-1);
  }
}

//##ModelId=3C960F1B0373
int Message::fromBlock (BlockSet& set)
{
  int blockcount = 1;
  // get and unpack header
  BlockRef href;
  set.pop(href);
  const HeaderBlock & hdr = *static_cast<const HeaderBlock*>(href->data());
  FailWhen(href->size() < sizeof(HeaderBlock) ||
           href->size() != sizeof(HeaderBlock) + 
           hdr.idsize + hdr.fromsize + hdr.tosize + hdr.latsize,"corrupt header block");
  priority_ = hdr.priority;
  state_    = hdr.state;
  hops_     = hdr.hops;
  flags_    = hdr.flags;
  const char *buf = static_cast<const char*>(href->data()) + sizeof(HeaderBlock);
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
    BlockableObject *obj = DynamicTypeManager::construct(hdr.payload_type);
    blockcount += obj->fromBlock(set);
    payload_.attach(obj,DMI::ANON|DMI::WRITE);
  }
  else
    payload_.detach();
  
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
  HeaderBlock & hdr = *static_cast<HeaderBlock*>(hdrblock->data());
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
  char *buf = static_cast<char*>(hdrblock->data()) + sizeof(HeaderBlock);
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
    set.pushNew().copy(block_,DMI::PRESERVE_RW);
    blockcount++;
  } 
  if( payload_.valid() )
    blockcount += payload_->toBlock(set);
  return blockcount;
}


//##ModelId=3E301BB10085
DataRecord & Message::withDataRecord (Message::Ref &ref,const HIID &id)
{
  Message *pmsg = new Message(id);
  ref <<= pmsg;
  return (*pmsg) <<= new DataRecord;
}

// second form initializes record with a Text field
//##ModelId=3E301BB10140
DataRecord & Message::withDataRecord (Message::Ref &ref,const HIID &id,const string &text)
{
  DataRecord &rec = withDataRecord(ref,id);
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
    out += "/" + id_.toString();
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

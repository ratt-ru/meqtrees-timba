//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7B7F2F024A.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7B7F2F024A.cm

//## begin module%3C7B7F2F024A.cp preserve=no
//## end module%3C7B7F2F024A.cp

//## Module: Message%3C7B7F2F024A; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\Message.cc

//## begin module%3C7B7F2F024A.additionalIncludes preserve=no
//## end module%3C7B7F2F024A.additionalIncludes

//## begin module%3C7B7F2F024A.includes preserve=yes
#include "DMI/DynamicTypeManager.h"
//## end module%3C7B7F2F024A.includes

// Message
#include "OCTOPUSSY/Message.h"
//## begin module%3C7B7F2F024A.declarations preserve=no
//## end module%3C7B7F2F024A.declarations

//## begin module%3C7B7F2F024A.additionalDeclarations preserve=yes
//## end module%3C7B7F2F024A.additionalDeclarations


// Class Message 

Message::Message()
  //## begin Message::Message%3C7B6A2D01F0_const.hasinit preserve=no
  //## end Message::Message%3C7B6A2D01F0_const.hasinit
  //## begin Message::Message%3C7B6A2D01F0_const.initialization preserve=yes
  : hops_(0)
  //## end Message::Message%3C7B6A2D01F0_const.initialization
{
  //## begin Message::Message%3C7B6A2D01F0_const.body preserve=yes
  //## end Message::Message%3C7B6A2D01F0_const.body
}

Message::Message(const Message &right)
  //## begin Message::Message%3C7B6A2D01F0_copy.hasinit preserve=no
  //## end Message::Message%3C7B6A2D01F0_copy.hasinit
  //## begin Message::Message%3C7B6A2D01F0_copy.initialization preserve=yes
    : BlockableObject()
  //## end Message::Message%3C7B6A2D01F0_copy.initialization
{
  //## begin Message::Message%3C7B6A2D01F0_copy.body preserve=yes
  (*this) = right;
  //## end Message::Message%3C7B6A2D01F0_copy.body
}

Message::Message (const HIID &id1, BlockableObject *pload, int flags, int pri)
  //## begin Message::Message%3C7B9C490384.hasinit preserve=no
  //## end Message::Message%3C7B9C490384.hasinit
  //## begin Message::Message%3C7B9C490384.initialization preserve=yes
   : priority_(pri),state_(0),hops_(0),id_(id1)
  //## end Message::Message%3C7B9C490384.initialization
{
  //## begin Message::Message%3C7B9C490384.body preserve=yes
  payload_.attach(pload,flags|DMI::PERSIST|DMI::WRITE);
  //## end Message::Message%3C7B9C490384.body
}

Message::Message (const HIID &id1, ObjRef &pload, int flags, int pri)
  //## begin Message::Message%3C7B9D0A01FB.hasinit preserve=no
  //## end Message::Message%3C7B9D0A01FB.hasinit
  //## begin Message::Message%3C7B9D0A01FB.initialization preserve=yes
   : priority_(pri),state_(0),hops_(0),id_(id1)
  //## end Message::Message%3C7B9D0A01FB.initialization
{
  //## begin Message::Message%3C7B9D0A01FB.body preserve=yes
  if( flags&DMI::COPYREF )
    payload_.copy(pload,flags|DMI::PERSIST|DMI::WRITE);
  else
    payload_.xfer(pload).persist();
  //## end Message::Message%3C7B9D0A01FB.body
}

Message::Message (const HIID &id1, SmartBlock *bl, int flags, int pri)
  //## begin Message::Message%3C7B9D3B02C3.hasinit preserve=no
  //## end Message::Message%3C7B9D3B02C3.hasinit
  //## begin Message::Message%3C7B9D3B02C3.initialization preserve=yes
   : priority_(pri),state_(0),hops_(0),id_(id1)
  //## end Message::Message%3C7B9D3B02C3.initialization
{
  //## begin Message::Message%3C7B9D3B02C3.body preserve=yes
  block_.attach(bl,flags|DMI::PERSIST|DMI::WRITE);
  //## end Message::Message%3C7B9D3B02C3.body
}

Message::Message (const HIID &id1, BlockRef &bl, int flags, int pri)
  //## begin Message::Message%3C7B9D59014A.hasinit preserve=no
  //## end Message::Message%3C7B9D59014A.hasinit
  //## begin Message::Message%3C7B9D59014A.initialization preserve=yes
   : priority_(pri),state_(0),hops_(0),id_(id1)
  //## end Message::Message%3C7B9D59014A.initialization
{
  //## begin Message::Message%3C7B9D59014A.body preserve=yes
  if( flags&DMI::COPYREF )
    block_.copy(bl,flags|DMI::PERSIST|DMI::WRITE);
  else
    block_.xfer(bl).persist();
  //## end Message::Message%3C7B9D59014A.body
}

Message::Message (const HIID &id1, const char *data, size_t sz, int pri)
  //## begin Message::Message%3C7BB3BD0266.hasinit preserve=no
  //## end Message::Message%3C7BB3BD0266.hasinit
  //## begin Message::Message%3C7BB3BD0266.initialization preserve=yes
   : priority_(pri),state_(0),hops_(0),id_(id1)
  //## end Message::Message%3C7BB3BD0266.initialization
{
  //## begin Message::Message%3C7BB3BD0266.body preserve=yes
  SmartBlock *bl = new SmartBlock(sz);
  block_.attach( bl,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  memcpy(bl->data(),data,sz);
  //## end Message::Message%3C7BB3BD0266.body
}


Message::~Message()
{
  //## begin Message::~Message%3C7B6A2D01F0_dest.body preserve=yes
  //## end Message::~Message%3C7B6A2D01F0_dest.body
}


Message & Message::operator=(const Message &right)
{
  //## begin Message::operator=%3C7B6A2D01F0_assign.body preserve=yes
  if( &right != this )
  {
    id_ = right.id_;
    priority_ = right.priority_;
    from_ = right.from_;
    to_ = right.to_;
    state_ = right.state_;
  //  timestamp_ = right.timestamp_;
    payload_.copy(right.payload_,DMI::PRESERVE_RW|DMI::PERSIST);
    block_.copy(right.block_,DMI::PRESERVE_RW|DMI::PERSIST);
  }
  return *this;
  //## end Message::operator=%3C7B6A2D01F0_assign.body
}



//## Other Operations (implementation)
Message & Message::operator <<= (BlockableObject *pload)
{
  //## begin Message::operator <<=%3C7B9DDE0137.body preserve=yes
  payload_.attach(pload,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  return *this;
  //## end Message::operator <<=%3C7B9DDE0137.body
}

Message & Message::operator <<= (ObjRef &pload)
{
  //## begin Message::operator <<=%3C7B9DF20014.body preserve=yes
  payload_.xfer(pload).persist();
  return *this;
  //## end Message::operator <<=%3C7B9DF20014.body
}

Message & Message::operator <<= (SmartBlock *bl)
{
  //## begin Message::operator <<=%3C7B9E0A02AD.body preserve=yes
  block_.attach(bl,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  return *this;
  //## end Message::operator <<=%3C7B9E0A02AD.body
}

Message & Message::operator <<= (BlockRef &bl)
{
  //## begin Message::operator <<=%3C7B9E1601CE.body preserve=yes
  block_.xfer(bl).persist();
  return *this;
  //## end Message::operator <<=%3C7B9E1601CE.body
}

CountedRefTarget* Message::clone (int flags, int depth) const
{
  //## begin Message::clone%3C7E32BE01E0.body preserve=yes
  Message *newmsg = new Message(*this);
  newmsg->privatize(flags,depth);
  return newmsg;
  //## end Message::clone%3C7E32BE01E0.body
}

void Message::privatize (int flags, int depth)
{
  //## begin Message::privatize%3C7E32C1022B.body preserve=yes
  if( flags&DMI::DEEP || depth>0 )
  {
    if( payload_.valid() )
      payload_.privatize(flags,depth-1);
    if( block_.valid() )
      block_.privatize(flags,depth-1);
  }
  //## end Message::privatize%3C7E32C1022B.body
}

NestableContainer::Hook Message::setBranch (const HIID &id, int flags)
{
  //## begin Message::setBranch%3CB42D0201B4.body preserve=yes
  FailWhen( !payload_.valid() || !payload_->isNestable(),"payload is not a container" ); 
  // privatize payload if required (or if not writable)
  if( flags&DMI::PRIVATIZE ||
      !payload_.isWritable() || 
      dynamic_cast<NestableContainer&>(payload_.dewr()).isWritable() )
    payload_.privatize(DMI::WRITE,0);
  NestableContainer *nc = dynamic_cast<NestableContainer*>(payload_.dewr_p());
  Assert(nc);
  return nc->setBranch(id,flags);
  //## end Message::setBranch%3CB42D0201B4.body
}

int Message::fromBlock (BlockSet& set)
{
  //## begin Message::fromBlock%3C960F1B0373.body preserve=yes
  int blockcount = 1;
  // get and unpack header
  BlockRef href;
  set.pop(href);
  const HeaderBlock & hdr = *static_cast<const HeaderBlock*>(href->data());
  FailWhen(href->size() < sizeof(HeaderBlock) ||
           href->size() != sizeof(HeaderBlock) + 
           hdr.idsize + hdr.fromsize + hdr.tosize,"corrupt header block");
  priority_ = hdr.priority;
  state_    = hdr.state;
  hops_     = hdr.hops;
  const char *buf = static_cast<const char*>(href->data()) + sizeof(HeaderBlock);
  id_.unpack(buf,hdr.idsize);     buf += hdr.idsize;
  from_.unpack(buf,hdr.fromsize); buf += hdr.fromsize;
  to_.unpack(buf,hdr.tosize);
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
  //## end Message::fromBlock%3C960F1B0373.body
}

int Message::toBlock (BlockSet &set) const
{
  //## begin Message::toBlock%3C960F20037A.body preserve=yes
  // create a header block
  size_t idsize = id_.packSize(),
         tosize = to_.packSize(),
         fromsize = from_.packSize(),
         hsize = idsize+tosize+fromsize;
  SmartBlock *hdrblock = new SmartBlock(sizeof(HeaderBlock)+hsize);
  BlockRef bref(hdrblock,DMI::ANON|DMI::WRITE); 
  HeaderBlock & hdr = *static_cast<HeaderBlock*>(hdrblock->data());
  hdr.priority  = priority_;
  hdr.state     = state_;
  hdr.hops      = hops_;
  hdr.idsize    = idsize;
  hdr.fromsize  = fromsize;
  hdr.tosize    = tosize;
  hdr.has_block = block_.valid(); 
  hdr.payload_type = payload_.valid() ? payload_->objectType() : NullType;
  char *buf = static_cast<char*>(hdrblock->data()) + sizeof(HeaderBlock);
  buf += id_.pack(buf,hsize);      
  buf += from_.pack(buf,hsize);    
  to_.pack(buf,hsize);      
  
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
  //## end Message::toBlock%3C960F20037A.body
}

// Additional Declarations
  //## begin Message%3C7B6A2D01F0.declarations preserve=yes
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
  //## end Message%3C7B6A2D01F0.declarations
//## begin module%3C7B7F2F024A.epilog preserve=yes
//## end module%3C7B7F2F024A.epilog

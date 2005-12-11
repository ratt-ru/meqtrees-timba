#define NC_SKIP_HOOKS 1
    
#include "DynamicTypeManager.h"
#include "Record.h"
#include "Vec.h"

    // register as a nestable container
static DMI::Container::Register reg(TpDMIRecord,true);

//##ModelId=3E9BD9150075
static const DMI::ObjRef NullObjRef;

//##ModelId=3C5820AD00C6
DMI::Record::Record ()
  : Container()
{
  dprintf(2)("default constructor\n");
}

//##ModelId=3C5820C7031D
DMI::Record::Record (const Record &other, int flags, int depth)
  : Container()
{
  dprintf(2)("copy constructor, cloning from %s\n",other.debug(1));
  cloneOther(other,flags,depth,true);
}

//##ModelId=3DB93482018E
DMI::Record::~Record()
{
  dprintf(2)("destructor\n");
}

void DMI::Record::clear ()
{
  dprintf(2)("clear()\n");
  fields.clear();
}

//##ModelId=3DB93482022F
DMI::Record & DMI::Record::operator = (const Record &right)
{
  if( &right != this )
  {
    dprintf(2)("assignment op, cloning from %s\n",right.debug(1));
    cloneOther(right,0,0,false);
  }
  return *this;
}

//##ModelId=400E4D6903B8
void DMI::Record::merge (const Record &other,bool overwrite,int flags)
{
  if( &other != this )
  {
    Thread::Mutex::Lock _nclock(mutex());
#ifdef USE_THREADS
    Thread::Mutex::Lock lock2(other.mutex());
#endif
    dprintf(2)("merge(%s,%d,%d)\n",other.debug(1),int(overwrite),flags);
    for( CFMI oiter = other.fields.begin(); oiter != other.fields.end(); oiter++ )
    {
      // try to insert entry with other's key into map 
      std::pair<HIID,Field> entry;
      entry.first = oiter->first; 
      std::pair<FMI,bool> res = fields.insert(entry);
      Field &fld = res.first->second;
      // fld now points to the new (or existing entry). Attach content
      FailWhen(!res.second && overwrite && fld.protect,"can't overwrite protected field "+entry.first.toString('.'));
      if( res.second || overwrite )
      {
        if( fld.ref != oiter->second.ref )
          fld.ref.unlock().copy(oiter->second.ref,flags).lock();
        fld.protect = oiter->second.protect;
      }
    }
  }
}

//##ModelId=3BFBF5B600EB
DMI::Record::Field & DMI::Record::addField (const HIID &id, ObjRef &ref, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("add(%s,[%s],%x)\n",id.toString('.').c_str(),ref->debug(1),flags);
  FailWhen( !id.size(),"null field id" );
  // find/insert field
  Field & field = fields[id];
  if( field.ref.valid() )
  {
    FailWhen(field.protect && flags&HONOR_PROTECT,"can't replace protected field "+id.toString('.'));
    FailWhen(!(flags&DMI::REPLACE), "field "+id.toString('.')+" already exists" );
    field.ref.unlock();
  }
  // now insert into map
  if( flags&XFER )
    field.ref.xfer(ref,flags).lock();
  else 
    field.ref.copy(ref,flags).lock();
  field.protect = flags&Record::PROTECT;
  return field;
}

void DMI::Record::protectField   (const HIID &id,bool protect)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("protectField(%s)\n",id.toString('.').c_str());
  FailWhen( !id.size(),"null field id" );
  Field * pf =  findField(id);
  FailWhen(!pf,"field "+id.toString('.')+" not found");
  pf->protect = protect;
}

//##ModelId=3BB311C903BE
DMI::ObjRef DMI::Record::removeField (const HIID &id,bool ignore_fail,int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("remove(%s)\n",id.toString('.').c_str());
  FailWhen( !id.size(),"null field id" );
  Field * pf =  findField(id);
  if( pf )
  {
    FailWhen(pf->protect && flags&HONOR_PROTECT,"can't removed protected field "+id.toString('.'));
    ObjRef ref(pf->ref.unlock(),DMI::XFER);
    fields.erase(id);
    dprintf(2)("  removing %s\n",ref->debug(1));
    return ref;
  }
  FailWhen(!ignore_fail,"field "+id.toString('.')+" not found");
  return ObjRef();
}

//##ModelId=3C57CFFF005E
DMI::ObjRef DMI::Record::get (const HIID &id,bool ignore_fail) const
{
  FailWhen( !id.size(),"null field id" );
  Thread::Mutex::Lock _nclock(mutex());
  CFMI iter = fields.find(id);
  if( iter == fields.end() )
  {
    FailWhen(!ignore_fail,"field "+id.toString('.')+" not found" );
    return ObjRef();
  }
  return iter->second.ref;
}

//##ModelId=3C58216302F9
int DMI::Record::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("fromBlock(%s)\n",set.debug(2));
  int nref = 1;
  fields.clear();
  // pop and cache the header block as headref
  BlockRef headref;
  set.pop(headref);
  size_t hsize = headref->size();
  FailWhen( hsize < sizeof(Header),"malformed header block" );
  const char *chead = headref->cdata();
  const Header *phead = headref->pdata<Header>();
  int blockcount = BObj::checkHeader(phead);
  // get # of fields
  int nfields = phead->num_fields;
  const BlockFieldInfo *fieldinfo = phead->fields;
  size_t off_hids = sizeof(Header) + sizeof(BlockFieldInfo)*nfields; // IDs start at this offset
  FailWhen( hsize < off_hids,"malformed header block" );
  dprintf(2)("fromBlock: %d header bytes, %d fields expected\n",hsize,nfields);
  // get fields one by one
  for( int i=0; i<nfields; i++,fieldinfo++ )
  {
    // extract ID from header block
    int idsize = fieldinfo->idsize;
    FailWhen( hsize < off_hids+idsize,"malformed header block" );
    HIID id(chead+off_hids,idsize);
    off_hids += idsize;
    // create field container object
    int bc = fieldinfo->blockcount;
    ObjRef ref;
    if( bc )
    {
      int nb0 = set.size();
      FailWhen(!nb0,"Record::fromBlock: unexpectedly ran out of blocks");
      // create object
      try
      {
        ref = DynamicTypeManager::construct(0,set);
        FailWhen(!ref.valid(),"item construct failed" );
      }
      catch( std::exception &exc )
      {
        string msg = string("error unpacking: ") + exc.what();
        ref <<= new DMI::Vec(Tpstring,-1,&msg);
      }
      int nb = nb0 - set.size();
      FailWhen(nb!=bc,"block count mismatch in header");
      nref += nb;
      dprintf(3)("%s [%s] used %d blocks\n",id.toString('.').c_str(),ref->sdebug(1).c_str(),nb);
    }
    else
    {
      dprintf(3)("%s is an empty field\n",id.toString('.').c_str()); 
    }
    // move to field
    Field & field = fields[id];
    field.ref.xfer(ref).lock();
    field.protect = false;
  }
  FailWhen(nref!=blockcount,"total block count mismatch in header");
  dprintf(2)("fromBlock: %d total blocks used\n",nref);
  validateContent(true);
  return nref;
}

//##ModelId=3C5821630371
int DMI::Record::toBlock (BlockSet &set) const
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("toBlock\n");
  int nref = 1;
  // compute header size
  size_t hdrsize = sizeof(Header) + sizeof(BlockFieldInfo)*fields.size(), 
         idsize = 0;
  for( CFMI iter = fields.begin(); iter != fields.end(); iter++ )
    idsize += iter->first.packSize();
  // allocate new header block
  SmartBlock *header = new SmartBlock(hdrsize+idsize);
  BlockRef headref(header);
  set.push(headref);
  // store header info
  Header *hdr  = header->pdata<Header>();
  char *iddata   = header->cdata() + hdrsize;
  hdr->num_fields = fields.size();
  dprintf(2)("toBlock: %d header bytes, %d fields\n",hdrsize+idsize,fields.size());
  // store IDs and convert everything
  BlockFieldInfo *fieldinfo = hdr->fields;
  for( CFMI iter = fields.begin(); iter != fields.end(); iter++,fieldinfo++ )
  {
    iddata += fieldinfo->idsize = iter->first.pack(iddata,idsize);
    int nr1;
    if( iter->second.ref.valid() )
      nr1 = fieldinfo->blockcount = iter->second.ref->toBlock(set);
    else
      nr1 = fieldinfo->blockcount = 0; // null field
    nref += nr1;
    dprintf(3)("%s [%s] generated %d blocks\n",
        iter->first.toString('.').c_str(),iter->second.ref->sdebug(1).c_str(),nr1);
  }
  BObj::fillHeader(hdr,nref);
  dprintf(2)("toBlock: %d total blocks generated\n",nref);
  return nref;
}

//##ModelId=3C58218900EB
DMI::CountedRefTarget * DMI::Record::clone (int flags, int depth) const
{
  dprintf(2)("cloning new DMI::Record\n");
  return new Record(*this,flags,depth);
}

//##ModelId=3C58239503D1
void DMI::Record::cloneOther (const Record &other,int flags,int depth,bool constructing)
{
  Thread::Mutex::Lock _nclock(mutex());
  Thread::Mutex::Lock _nclock1(other.mutex());
  fields.clear();
  // copy all field refs, then privatize them if depth>0.
  for( CFMI iter = other.fields.begin(); iter != other.fields.end(); iter++ )
  {
    Field & field = fields[iter->first];
    field.ref.copy(iter->second.ref,flags,depth);
    field.protect = iter->second.protect;
  }
  validateContent(!constructing);
}

//##ModelId=3C56B00E0182
int DMI::Record::get (const HIID &id,ContentInfo &info, 
                      bool nonconst,int flags) const
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen(!id.size(),"null field id");
  bool writing = flags&DMI::WRITE;
  Assert1(nonconst || !writing);
  CFMI iter;
  // "AidHash" followed by a single numeric index is field #
  if( id.size() == 2 && id[0] == AidHash && id[1].index() >= 0 )
  {
    uint nf = id[1].index();
    if( nf == fields.size() )
      return 0;
    FailWhen( nf > fields.size(),"record field number out of range");
    // advance to specified field
    for( uint i=0; i<nf && iter != fields.end(); i++,iter++ );
  }
  else // else HIID is field name
    iter = fields.find(id);
  // Field not found? return 0
  if( iter == fields.end() )
    return 0;
  FailWhen(writing && iter->second.protect,"can't write to protected field "+id.toString('.'));
  ObjRef &ref = const_cast<ObjRef&>(iter->second.ref);
  if( writing )
    ref.dewr();  // causes copy-on-write as needed
  info.ptr = &ref;
  info.writable = nonconst;
  info.tid = TpDMIObjRef;
  info.obj_tid = ref.valid() ? ref->objectType() : NullType;
  info.size = 1;
  return 1;
}

//##ModelId=3C7A16BB01D7
int DMI::Record::insert (const HIID &id,ContentInfo &info)
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen( !id.size(),"null field id" );
  FailWhen( fields.find(id) != fields.end(),"field "+id.toString('.')+" already exists" );
  TypeId tid = info.obj_tid;
  // Dynamic objects are inserted via ref
  if( info.tid == TpDMIObjRef )
  {
    Field & field = fields[id];
    field.protect = false;
    info.ptr = &field.ref;
    info.tid = TpDMIObjRef;
    info.writable = true;
    info.size = 1;
    return 1;
  }
  // everything else is wrapped into a scalar DMI::Vec
  else     
  {
    Vec *pv = new Vec(tid,-1); // -1 means scalar
    ObjRef ref(pv);
    insert(id,ref);
    // do a get() on the vector itself to get address, etc.
    return pv->get(0,info,true,DMI::ASSIGN|DMI::WRITE);
  }
}

//##ModelId=3C877D140036
int DMI::Record::remove (const HIID &id)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("remove(%s)\n",id.toString('.').c_str());
  FailWhen( !id.size(),"null field id" );
  // find and remove
  CFMI iter = fields.find(id);
  if( iter != fields.end() )
  {
    FailWhen(iter->second.protect,"can't remove protected field "+id.toString('.'));
    dprintf(2)("  removing %s\n",iter->second.ref.debug(1));
    fields.erase(iter->first);
    return 1;
  }
  return 0;
}

//##ModelId=3C7A16C4023F
int DMI::Record::size (TypeId tid) const
{
  if( !tid || tid == TpDMIObjRef )
    return fields.size();
  return -1;
}


//##ModelId=3DB9348501B1
string DMI::Record::sdebug ( int detail,const string &prefix,const char *name ) const
{
  Thread::Mutex::Lock _nclock(mutex());
  string out;
  if( detail>=0 ) // basic detail
  {
    out = name ? string(name) : objectType().toString();
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    out += ssprintf("/%p %d fields",(void*)this,fields.size());
    out += " / refs "+CountedRefTarget::sdebug(-1);
  }
  if( detail >= 2 || detail <= -2 )   // high detail
  {
    // append debug info from CountedRefTarget
    string str = CountedRefTarget::sdebug(-2,prefix+"          ");
    if( str.length() )
      out += "\n"+prefix+"       refs "+str;
    for( CFMI iter = fields.begin(); iter != fields.end(); iter++ )
    {
      if( out.length() )
        out += "\n"+prefix+"  ";
      out += iter->first.toString('.')+(iter->second.protect?"#: " :": ");
      string out1;
      try
      {
        out1 = iter->second.ref.valid() 
            ? iter->second.ref->sdebug(abs(detail)-1,prefix+"          ")
            : "(invalid ref)";
      }
      catch( std::exception &x )
      {
        out = string("sdebug_exc: ")+x.what();
      }
      out += out1;
    }
  }
  return out;
}

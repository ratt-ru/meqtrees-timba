#define NC_SKIP_HOOKS 1
    
#include "DynamicTypeManager.h"
#include "DataRecord.h"
#include "DataField.h"

    // register as a nestable container
static NestableContainer::Register reg(TpDataRecord,True);

//##ModelId=3E9BD9150075
typedef NestableContainer::Ref NCRef;    
const NCRef NullNCRef;

//##ModelId=3C5820AD00C6
DataRecord::DataRecord (int flags)
  : NestableContainer()
{
  dprintf(2)("default constructor\n");
}

//##ModelId=3C5820C7031D
DataRecord::DataRecord (const DataRecord &other, int flags, int depth)
  : NestableContainer()
{
  dprintf(2)("copy constructor, cloning from %s\n",other.debug(1));
  cloneOther(other,flags,depth);
}

//##ModelId=3DB93482018E
DataRecord::~DataRecord()
{
  dprintf(2)("destructor\n");
}

//##ModelId=3DB93482022F
DataRecord & DataRecord::operator=(const DataRecord &right)
{
  if( &right != this )
  {
    dprintf(2)("assignment op, cloning from %s\n",right.debug(1));
    cloneOther(right,DMI::PRESERVE_RW,0);
  }
  return *this;
}

//##ModelId=400E4D6903B8
void DataRecord::merge (const DataRecord &other,bool overwrite,int flags)
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
      pair<HIID,NCRef> entry;
      entry.first = oiter->first; 
      pair<FMI,bool> res = fields.insert(entry);
      // res.first now points to the new (or existing entry). Attach content
      if( res.second || overwrite )
      {
        NCRef &ref = res.first->second;
        if( &ref != &(oiter->second) )
          res.first->second.unlock().copy(oiter->second,flags);
      }
    }
  }
}

//##ModelId=3BFBF5B600EB
void DataRecord::add (const HIID &id, const NCRef &ref, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("add(%s,[%s],%x)\n",id.toString().c_str(),ref->debug(1),flags);
  FailWhen( !id.size(),"null HIID" );
  FailWhen( fields.find(id) != fields.end(), "field already exists" );
  // insert into map
  if( flags&DMI::COPYREF )
    fields[id].copy(ref,flags);
  else
    fields[id] = ref;
}

//##ModelId=3C5FF0D60106
void DataRecord::add (const HIID &id,NestableContainer *pnc, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("add(%s,[%s],%x)\n",id.toString().c_str(),pnc->debug(1),flags);
  FailWhen( !id.size(),"null HIID" );
  FailWhen( fields.find(id) != fields.end(), "field already exists" );
  fields[id].attach(pnc,flags);
}

//##ModelId=3BFCD4BB036F
void DataRecord::replace (const HIID &id, const NCRef &ref, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("replace(%s,[%s],%x)\n",id.toString().c_str(),ref->debug(1),flags);
//  FailWhen( ref->objectType() != TpDataField && ref->objectType() != TpDataArray,
//            "illegal field object" );
  FailWhen( !id.size(),"null HIID" );
  if( flags&DMI::COPYREF )
    fields[id].unlock().copy(ref,flags).lock();
  else
    fields[id].unlock().xfer(ref).lock();
}

//##ModelId=3C5FF10102CA
void DataRecord::replace (const HIID &id, NestableContainer *pnc, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("replace(%s,[%s],%x)\n",id.toString().c_str(),pnc->debug(1),flags);
//  FailWhen( ref->objectType() != TpDataField && ref->objectType() != TpDataArray,
//            "illegal field object" );
  FailWhen( !id.size(),"null HIID" );
  fields[id].unlock().attach(pnc,flags).lock();
}


//##ModelId=3BB311C903BE
NCRef DataRecord::removeField (const HIID &id,bool ignore_fail)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("remove(%s)\n",id.toString().c_str());
  FailWhen( !id.size(),"null HIID" );
  FMI iter = fields.find(id);
  if( iter != fields.end() )
  {
    NCRef ref(iter->second.unlock());
    fields.erase(iter->first);
    dprintf(2)("  removing %s\n",ref->debug(1));
    return ref;
  }
  FailWhen(!ignore_fail,"field "+id.toString()+" not found");
  return NCRef();
}

//##ModelId=3C57CFFF005E
NCRef DataRecord::field (const HIID &id) const
{
  Thread::Mutex::Lock _nclock(mutex());
  HIID rest; bool dum;
  const NCRef &ref( resolveField(id,rest,dum,False) );
  FailWhen( !ref.valid(),"field "+id.toString()+" not found" );
  FailWhen( rest.size(),id.toString()+" does not resolve to a complete field" );
  return ref.copy(DMI::READONLY);
}

//##ModelId=3BFBF49D00A1
NCRef DataRecord::fieldWr (const HIID &id, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  HIID rest; bool dum;
  const NCRef &ref( resolveField(id,rest,dum,True) );
  FailWhen( !ref.valid(),"field "+id.toString()+" not found" );
  FailWhen( rest.size(),id.toString()+" does not resolve to a complete field" );
  return ref.copy(flags);
}

//##ModelId=3C552E2D009D
const NCRef & DataRecord::resolveField (const HIID &id, HIID& rest, bool &can_write, bool must_write) const
{
  FailWhen( !id.size(),"null HIID" );
  CFMI iter = fields.find(id);
  if( iter == fields.end() )
  {
    rest = id;
    return NullNCRef;
  }
  can_write = iter->second.isWritable();
  FailWhen( must_write && !can_write,"r/w access violation" );
  rest.clear();
  return iter->second;
}

//##ModelId=3C58216302F9
int DataRecord::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("fromBlock(%s)\n",set.debug(2));
  int nref = 1;
  fields.clear();
  // pop and cache the header block as headref
  BlockRef headref;
  set.pop(headref);
  size_t hsize = headref->size();
  FailWhen( hsize < sizeof(int),"malformed header block" );
  // get # of fields
  const char *head = static_cast<const char*>( headref->data() );
  const int *hdata = reinterpret_cast<const int *>( head );
  int nfields = *hdata++;
  const BlockFieldInfo *fieldinfo = reinterpret_cast<const BlockFieldInfo *>(hdata);
  size_t off_hids = sizeof(int) + sizeof(BlockFieldInfo)*nfields; // IDs start at this offset
  FailWhen( hsize < off_hids,"malformed header block" );
  dprintf(2)("fromBlock: %d header bytes, %d fields expected\n",hsize,nfields);
  // get fields one by one
  for( int i=0; i<nfields; i++,fieldinfo++ )
  {
    // extract ID from header block
    int idsize = fieldinfo->idsize;
    FailWhen( hsize < off_hids+idsize,"malformed header block" );
    HIID id(head+off_hids,idsize);
    off_hids += idsize;
    // create field container object
    NestableContainer *field = dynamic_cast<NestableContainer *>
        ( DynamicTypeManager::construct(fieldinfo->ftype) );
    FailWhen( !field,"cast failed: perhaps field is not a container?" );
    NCRef ref(field,DMI::ANONWR);
    // unblock and set the writable flag
    int nr = field->fromBlock(set);
    nref += nr;
    fields[id] = ref;
    dprintf(3)("%s [%s] used %d blocks\n",
          id.toString().c_str(),field->sdebug(1).c_str(),nr);
  }
  dprintf(2)("fromBlock: %d total blocks used\n",nref);
  validateContent();
  return nref;
}

//##ModelId=3C5821630371
int DataRecord::toBlock (BlockSet &set) const
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("toBlock\n");
  int nref = 1;
  // compute header size
  size_t hdrsize = sizeof(int) + sizeof(BlockFieldInfo)*fields.size(), 
         datasize = 0;
  for( CFMI iter = fields.begin(); iter != fields.end(); iter++ )
    datasize += iter->first.packSize();
  // allocate new header block
  SmartBlock *header = new SmartBlock(hdrsize+datasize);
  BlockRef headref(header,DMI::ANONWR);
  // store header info
  int  *hdr    = static_cast<int *>(header->data());
  char *data   = static_cast<char *>(header->data()) + hdrsize;
  *hdr++ = fields.size();
  BlockFieldInfo *fieldinfo = reinterpret_cast<BlockFieldInfo *>(hdr);
  set.push(headref);
  dprintf(2)("toBlock: %d header bytes, %d fields\n",hdrsize+datasize,fields.size());
  // store IDs and convert everything
  for( CFMI iter = fields.begin(); iter != fields.end(); iter++,fieldinfo++ )
  {
    data += fieldinfo->idsize = iter->first.pack(data,datasize);
    fieldinfo->ftype = iter->second->objectType();
    int nr1 = iter->second->toBlock(set);
    nref += nr1;
    dprintf(3)("%s [%s] generated %d blocks\n",
        iter->first.toString().c_str(),iter->second->sdebug(1).c_str(),nr1);
  }
  dprintf(2)("toBlock: %d total blocks generated\n",nref);
  return nref;
}

//##ModelId=3C58218900EB
CountedRefTarget* DataRecord::clone (int flags, int depth) const
{
  dprintf(2)("cloning new DataRecord\n");
  return new DataRecord(*this,flags,depth);
}

//##ModelId=3C582189019F
void DataRecord::privatize (int flags, int depth)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("privatizing DataRecord\n");
  if( flags&DMI::DEEP || depth>0 )
  {
    for( FMI iter = fields.begin(); iter != fields.end(); iter++ )
    {
      const HIID &id = iter->first;
      dprintf(4)("  privatizing field %s\n",id.toString().c_str());
      iter->second.privatize(flags|DMI::LOCK,depth-1);
    }
    // since things may have changed around, revalidate content
    validateContent();
  }
}

//##ModelId=3C58239503D1
void DataRecord::cloneOther (const DataRecord &other, int flags, int depth)
{
  Thread::Mutex::Lock _nclock(mutex());
  Thread::Mutex::Lock _nclock1(other.mutex());
  fields.clear();
  // copy all field refs, then privatize them if depth>0.
  // For ref.copy(), clear the DMI::WRITE flag and use DMI::PRESERVE_RW instead.
  // (When depth>0, DMI::WRITE will take effect anyways via privatize().
  //  When depth=0, we must preserve the write permissions of the contents.)
  for( CFMI iter = other.fields.begin(); iter != other.fields.end(); iter++ )
  {
    NCRef & ref( fields[iter->first].copy(iter->second,
                (flags&~DMI::WRITE)|DMI::PRESERVE_RW|DMI::LOCK) );
    if( flags&DMI::DEEP || depth>0 )
      ref.privatize(flags|DMI::LOCK,depth-1);
    
  }
  validateContent();
}

//##ModelId=3C56B00E0182
int DataRecord::get (const HIID &id,ContentInfo &info, 
                     bool nonconst,int flags) const
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen(!id.size(),"null field id");
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
  
  NestableContainer::Ref &ref = const_cast<NestableContainer::Ref&>(iter->second);
  bool no_write = flags&DMI::WRITE && !nonconst;
  // return const violation if not writable; the exception is when access to
  // object is requested and ref is writable
  if( no_write && !(flags&DMI::NC_DEREFERENCE && ref.isWritable()) )
    return -1;
  info.ptr = &ref;
  info.writable = nonconst;
  info.tid = TpObjRef;
  info.obj_tid = ref.valid() ? ref->objectType() : NullType;
  info.size = 1;
  return 1;
}

//##ModelId=3C7A16BB01D7
int DataRecord::insert (const HIID &id,ContentInfo &info)
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen( !id.size(),"null HIID" );
  FailWhen( fields.find(id) != fields.end(),"field "+id.toString()+" already exists" );
  TypeId tid = info.obj_tid;
  // Containers are inserted directly
  if( isNestable(tid) )
  {
    info.ptr = &fields[id];
    info.tid = TpObjRef;
    info.writable = True;
    info.size = 1;
    return 1;
  }
  // everything else is inserted as a scalar DataField
  else     
  {
    NestableContainer *pf = new DataField(tid,-1); // -1 means scalar
    fields[id].attach(pf,DMI::ANONWR|DMI::LOCK);
    // do a get() on the field to obtain info
    return pf->get(0,info,DMI::NC_ASSIGN|DMI::WRITE);
  }
}

//##ModelId=3C877D140036
int DataRecord::remove (const HIID &id)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("remove(%s)\n",id.toString().c_str());
  FailWhen( !id.size(),"null HIID" );
  // find and remove
  CFMI iter = fields.find(id);
  if( iter != fields.end() )
  {
    dprintf(2)("  removing %s\n",iter->second.debug(1));
    fields.erase(iter->first);
    return 1;
  }
  return 0;
}

//##ModelId=3C7A16C4023F
int DataRecord::size (TypeId tid) const
{
  if( !tid || tid == TpObjRef )
    return fields.size();
  return -1;
}

//##ModelId=3CA20AD703A4
bool DataRecord::getFieldIter (DataRecord::Iterator& iter, HIID& id, NCRef &ref) const
{
  if( iter.iter == fields.end() )
  {
#ifdef USE_THREADS
    iter.lock.release();
#endif
    return False;
  }
  id = iter.iter->first;
  ref.copy(iter.iter->second,DMI::PRESERVE_RW);
  iter.iter++;
  return True;
}

//##ModelId=3DB9348501B1
string DataRecord::sdebug ( int detail,const string &prefix,const char *name ) const
{
  static int nesting=0;
  Thread::Mutex::Lock _nclock(mutex());
  if( nesting++>1000 )
  {
    cerr<<"Too many nested DataRecord::sdebug() calls";
    abort();
  }
  string out;
  if( detail>=0 ) // basic detail
  {
    Debug::appendf(out,"%s/%08x",name?name:objectType().toString().c_str(),(int)this);
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    out += Debug::ssprintf("%d fields",fields.size());
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
      out += iter->first.toString()+": ";
      string out1;
      try
      {
        out1 = iter->second.valid() 
            ? iter->second->sdebug(abs(detail)-1,prefix+"          ")
            : "(invalid ref)";
      }
      catch( std::exception &x )
      {
        out = string("sdebug_exc: ")+x.what();
      }
      out += out1;
    }
  }
  nesting--;
  return out;
}

//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC82005C.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC82005C.cm

//## begin module%3C10CC82005C.cp preserve=no
//## end module%3C10CC82005C.cp

//## Module: DataRecord%3C10CC82005C; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\DataRecord.cc

//## begin module%3C10CC82005C.additionalIncludes preserve=no
//## end module%3C10CC82005C.additionalIncludes

//## begin module%3C10CC82005C.includes preserve=yes
//## end module%3C10CC82005C.includes

// DataRecord
#include "DataRecord.h"
//## begin module%3C10CC82005C.declarations preserve=no
//## end module%3C10CC82005C.declarations

//## begin module%3C10CC82005C.additionalDeclarations preserve=yes
// register as a nestable container
static NestableContainer::Register reg(TpDataRecord,True);
const DataFieldRef NullDataFieldRef;
//## end module%3C10CC82005C.additionalDeclarations


// Class DataRecord 

DataRecord::DataRecord (int flags)
  //## begin DataRecord::DataRecord%3C5820AD00C6.hasinit preserve=no
  //## end DataRecord::DataRecord%3C5820AD00C6.hasinit
  //## begin DataRecord::DataRecord%3C5820AD00C6.initialization preserve=yes
  : NestableContainer(flags&DMI::WRITE!=0)
  //## end DataRecord::DataRecord%3C5820AD00C6.initialization
{
  //## begin DataRecord::DataRecord%3C5820AD00C6.body preserve=yes
  dprintf(2)("default constructor\n");
  //## end DataRecord::DataRecord%3C5820AD00C6.body
}

DataRecord::DataRecord (const DataRecord &other, int flags, int depth)
  //## begin DataRecord::DataRecord%3C5820C7031D.hasinit preserve=no
  //## end DataRecord::DataRecord%3C5820C7031D.hasinit
  //## begin DataRecord::DataRecord%3C5820C7031D.initialization preserve=yes
  : NestableContainer(flags&DMI::WRITE!=0 || (flags&DMI::PRESERVE_RW!=0 && other.isWritable()))
  //## end DataRecord::DataRecord%3C5820C7031D.initialization
{
  //## begin DataRecord::DataRecord%3C5820C7031D.body preserve=yes
  dprintf(2)("copy constructor, cloning from %s\n",other.debug(1));
  cloneOther(other,flags,depth);
  //## end DataRecord::DataRecord%3C5820C7031D.body
}


DataRecord::~DataRecord()
{
  //## begin DataRecord::~DataRecord%3BB3112B0027_dest.body preserve=yes
  dprintf(2)("destructor\n");
  //## end DataRecord::~DataRecord%3BB3112B0027_dest.body
}


DataRecord & DataRecord::operator=(const DataRecord &right)
{
  //## begin DataRecord::operator=%3BB3112B0027_assign.body preserve=yes
  if( &right != this )
  {
    dprintf(2)("assignment op, cloning from %s\n",right.debug(1));
    cloneOther(right,DMI::PRESERVE_RW,0);
  }
  return *this;
  //## end DataRecord::operator=%3BB3112B0027_assign.body
}



//## Other Operations (implementation)
void DataRecord::add (const HIID &id, const DataFieldRef &ref, int flags)
{
  //## begin DataRecord::add%3BFBF5B600EB.body preserve=yes
  dprintf(2)("add(%s,[%s],%x)\n",id.toString().c_str(),ref->debug(1),flags);
  FailWhen( !id.size(),"null HIID" );
  FailWhen( id.back().index()>=0,"unexpected trailing index in "+id.toString());
  FailWhen( !isWritable(),"r/w access violation" );
  // check that id does not conflict with existing IDs (including
  // recursive containers)
  for( int i=0; i<id.length(); i++ )
  {
    FailWhen( fields.find( id.subId(0,i) ) != fields.end(), 
        "add: conflicts with existing field "+id.subId(0,i).toString() );
  }
  // insert into map
  if( flags&DMI::COPYREF )
    fields[id].copy(ref,flags);
  else
    fields[id] = ref;
  //## end DataRecord::add%3BFBF5B600EB.body
}

DataFieldRef DataRecord::removeField (const HIID &id)
{
  //## begin DataRecord::removeField%3BB311C903BE.body preserve=yes
  dprintf(2)("remove(%s)\n",id.toString().c_str());
  FailWhen( !id.size(),"null HIID" );
  FailWhen( !isWritable(),"r/w access violation" );
  // is it our field -- just remove it
  CFMI iter = fields.find(id);
  if( iter != fields.end() )
  {
    DataFieldRef ref(iter->second);
    fields.erase(iter->first);
    dprintf(2)("  removing %s\n",ref->debug(1));
    return ref;
  }
  Throw("field "+id.toString()+" not found");
  return DataFieldRef();
  //## end DataRecord::removeField%3BB311C903BE.body
}

void DataRecord::replace (const HIID &id, const DataFieldRef &ref, int flags)
{
  //## begin DataRecord::replace%3BFCD4BB036F.body preserve=yes
  dprintf(2)("replace(%s,[%s],%x)\n",id.toString().c_str(),ref->debug(1),flags);
  FailWhen( !id.size(),"null HIID" );
  FailWhen( !isWritable(),"r/w access violation" );
  // is it our field -- just remove it
  CFMI iter = fields.find(id);
  if( iter != fields.end() )
  {
    if( flags&DMI::COPYREF )
      fields[id].copy(ref,flags);
    else
      fields[id] = ref;
    return;
  }
  //## end DataRecord::replace%3BFCD4BB036F.body
}

DataFieldRef DataRecord::field (const HIID &id) const
{
  //## begin DataRecord::field%3C57CFFF005E.body preserve=yes
  HIID rest; bool dum;
  const DataFieldRef &ref( resolveField(id,rest,dum,False) );
  FailWhen( !ref.valid(),"field "+id.toString()+" not found" );
  FailWhen( rest.size(),id.toString()+" does not resolve to a complete field" );
  return ref.copy(DMI::READONLY);
  //## end DataRecord::field%3C57CFFF005E.body
}

bool DataRecord::isDataField (const HIID &id) const
{
  //## begin DataRecord::isDataField%3C57D02B0148.body preserve=yes
  HIID rest; bool dum;
  try { 
    const DataFieldRef &ref( resolveField(id,rest,dum,False) );
    return ref.valid() && !rest.size();
  } catch (Debug::Error &x) {
    return False;
  }
  //## end DataRecord::isDataField%3C57D02B0148.body
}

DataFieldRef DataRecord::fieldWr (const HIID &id, int flags)
{
  //## begin DataRecord::fieldWr%3BFBF49D00A1.body preserve=yes
  FailWhen( !isWritable(),"r/w access violation" );
  HIID rest; bool dum;
  const DataFieldRef &ref( resolveField(id,rest,dum,True) );
  FailWhen( !ref.valid(),"field "+id.toString()+" not found" );
  FailWhen( rest.size(),id.toString()+" does not resolve to a complete field" );
  return ref.copy(flags);
  //## end DataRecord::fieldWr%3BFBF49D00A1.body
}

const DataFieldRef & DataRecord::resolveField (const HIID &id, HIID& rest, bool &can_write, bool must_write) const
{
  //## begin DataRecord::resolveField%3C552E2D009D.body preserve=yes
  FailWhen( !id.size(),"null HIID" );
  CFMI iter = fields.find(id);
  if( iter == fields.end() )
  {
    rest = id;
    return NullDataFieldRef;
  }
  can_write = iter->second->isWritable();
  FailWhen( must_write && !can_write,"r/w access violation" );
  rest.clear();
  return iter->second;
  
//   // This macro checks must_write against a writable property, and
//   // updates the can_write variable. 
//   #define CanWrite(x) { FailWhen(must_write && !x,"r/w access violation"); if( !x ) can_write = False; }
//   can_write = True;
//   CanWrite( isWritable() );
//   rest = id;
//   const DataRecord *subrec = this; // current level in hierarchy
//   const DataFieldRef *curref = 0;
//   // examine the slash-separated sub-ids one by one
//   while( rest.size() )
//   {
//     // strip off leading sub-id and look in record
//     HIID id1 = rest.popLeadSubId();
//     if( !id1.size() ) // nothing popped -- try again (rest is probably empty now, too)
//       continue;
//     //
//     if( curref )
//     {
//       FailWhen( (*curref)->type() != TpDataRecord,id.toString()+" refers to an invalid subrecord" );
//     }
//     // try to find the sub-id
//     CFMI iter = subrec->fields.find(id1);
//     if( iter != subrec->fields.end() ) // found it? 
//     {
//       CanWrite( iter->second->isWritable() );
//       curref = &iter->second;
//       continue;
//     }
//   }
//   // if last atom is an index ("a.b.c.1"), assume it's an index into the field,
//   // so strip it off and try again
//   int idlen = id.size(),index = id.back().index();
//   if( idlen > 1 && index >= 0 )
//   {
//     CFMI iter = fields.find( id.subId(0,-2) );
//     if( iter != fields.end() ) 
//     {
//       rest.push_back( id.back() );
//       CanWrite( iter->second->isWritable() );
//       return iter->second;
//     }
//   }
//   // otherwise, try to recurse into sub-records, by trying all sub-ids
//   // ("a", then "a.b", etc.) one by one
//   // the idlast iterator points at one past the end of the current sub-id
//   for( int iatom=0; iatom<idlen; iatom++ )
//   {
//     // look for a field corresponding to the sub-id
//     iter = fields.find( id.subId(0,iatom) );
//     if( iter != fields.end() ) // found field?
//     {
//       CanWrite( iter->second->isWritable() );
//       // if next atom of remainder is an index, use that as an index into the field
//       HIID subid = id.subId(iatom+1,-1);
//       // is it a sub-record? Recurse into it
//       if( iter->second->type() == TpDataRecord ) 
//       {
//         int index = subid.popLeadIndex();
//         return ((DataRecord*)iter->second->get(index))->resolveField(subid,rest,must_write);
//       }
//       // else it's the final field, so return it
//       rest = subid;
//       return iter->second;
//     }
//   }
//   // nothing was found -- return invalid ref
//   return NullDataFieldRef;
  //## end DataRecord::resolveField%3C552E2D009D.body
}

int DataRecord::fromBlock (BlockSet& set)
{
  //## begin DataRecord::fromBlock%3C58216302F9.body preserve=yes
  dprintf(2)("fromBlock(%s)\n",set.debug(2));
  int nref = 1;
  fields.clear();
  // pop and cache the header block as headref
  BlockRef headref;
  set.pop(headref);
  size_t hsize = headref->size();
  FailWhen( hsize < sizeof(int),"malformed header block" );
  // get # of fields
  const char *head = (const char*)headref->data();
  const int *hdata = (const int *)head;
  int nfields = *hdata++;
  size_t off_hids = sizeof(int)*(1+nfields); // IDs start at this offset
  FailWhen( hsize < off_hids,"malformed header block" );
  dprintf(2)("fromBlock: %d header bytes, %d fields expected\n",hsize,nfields);
  // get fields one by one
  for( int i=0; i<nfields; i++ )
  {
    // extract ID from header block
    int idsize = *hdata++;
    FailWhen( hsize < off_hids+idsize,"malformed header block" );
    HIID id(head+off_hids,idsize);
    off_hids += idsize;
    // unblock and add the field
    DataField *df = new DataField( isWritable() ? DMI::WRITE : 0 );
    int nr = df->fromBlock(set);
    nref += nr;
    fields[id].attach(df,DMI::ANON|DMI::WRITE|DMI::LOCK);
    dprintf(3)("%s [%s] used %d blocks\n",
          id.toString().c_str(),fields[id]->debug(1),nr);
  }
  dprintf(2)("fromBlock: %d total blocks used\n",nref);
  return nref;
  //## end DataRecord::fromBlock%3C58216302F9.body
}

int DataRecord::toBlock (BlockSet &set) const
{
  //## begin DataRecord::toBlock%3C5821630371.body preserve=yes
  dprintf(2)("toBlock\n");
  int nref = 1;
  // compute header size
  size_t hdrsize = sizeof(size_t)*(1+fields.size()), datasize = 0;
  for( CFMI iter = fields.begin(); iter != fields.end(); iter++ )
    datasize += iter->first.packSize();
  // allocate new header block
  SmartBlock *header = new SmartBlock(hdrsize+datasize);
  // store header info
  size_t *hdr   = static_cast<size_t *>(header->data());
  char   *data  = static_cast<char *>(header->data()) + hdrsize;
  *hdr++ = fields.size();
  set.push( BlockRef(header,DMI::WRITE|DMI::ANON) );
  dprintf(2)("toBlock: %d header bytes, %d fields\n",hdrsize+datasize,fields.size());
  // store IDs and convert everything
  for( CFMI iter = fields.begin(); iter != fields.end(); iter++ )
  {
    data += *(hdr++) = iter->first.pack(data,datasize);
    int nr1 = iter->second->toBlock(set);
    nref += nr1;
    dprintf(3)("%s [%s] generated %d blocks\n",
        iter->first.toString().c_str(),iter->second->debug(1),nr1);
  }
  dprintf(2)("toBlock: %d total blocks generated\n",nref);
  return nref;
  //## end DataRecord::toBlock%3C5821630371.body
}

CountedRefTarget* DataRecord::clone (int flags, int depth) const
{
  //## begin DataRecord::clone%3C58218900EB.body preserve=yes
  dprintf(2)("cloning new DataRecord\n");
  return new DataRecord(*this,flags,depth);
  //## end DataRecord::clone%3C58218900EB.body
}

void DataRecord::privatize (int flags, int depth)
{
  //## begin DataRecord::privatize%3C582189019F.body preserve=yes
  dprintf(2)("privatizing DataRecord\n");
  setWritable( (flags&DMI::WRITE)!=0 );
  if( flags&DMI::DEEP || depth>0 )
  {
    for( FMI iter = fields.begin(); iter != fields.end(); iter++ )
      iter->second.privatize(flags|DMI::LOCK,depth-1);
  }
  //## end DataRecord::privatize%3C582189019F.body
}

void DataRecord::cloneOther (const DataRecord &other, int flags, int depth)
{
  //## begin DataRecord::cloneOther%3C58239503D1.body preserve=yes
  fields.clear();
  setWritable( (flags&DMI::WRITE)!=0 || (flags&DMI::PRESERVE_RW && other.isWritable()) );
  // copy all field refs, then privatize them if depth>0.
  // For ref.copy(), clear the DMI::WRITE flag and use DMI::PRESERVE_RW instead.
  // (When depth>0, DMI::WRITE will take effect anyways via privatize().
  //  When depth=0, we must preserve the write permissions of the contents.)
  for( CFMI iter = other.fields.begin(); iter != other.fields.end(); iter++ )
  {
    DataFieldRef & ref( fields[iter->first].copy(iter->second,
            (flags&~DMI::WRITE)|DMI::PRESERVE_RW|DMI::LOCK) );
    if( flags&DMI::DEEP || depth>0 )
      ref.privatize(flags|DMI::LOCK,depth-1);
    
  }
  //## end DataRecord::cloneOther%3C58239503D1.body
}

const void * DataRecord::get (const HIID &id, TypeId& tid, bool& can_write, TypeId check_tid, int flags) const
{
  //## begin DataRecord::get%3C56B00E0182.body preserve=yes
  FailWhen(flags&DMI::NC_SCALAR,"can't access DataRecord in scalar mode");
  FailWhen( !id.size(),"null field id" );
  CFMI iter = fields.find(id);
  if( iter == fields.end() )
    return 0;
  // This condition checks that we're not auto-privatizing a readonly container
  // (so that we can cast away const, below)
  // do unconditional privatize if required
  if( flags&DMI::PRIVATIZE )
  {
    FailWhen(!isWritable(),"can't autoprivatize in readonly record");
    const_cast<DataFieldRef*>(&iter->second)->privatize(flags&(DMI::READONLY|DMI::WRITE|DMI::DEEP)); 
  }
  // writability is first determined by the field ref itself, plus the field
  // An invalid ref is considered writable (we'll check for our own writability
  // below)
  can_write = !iter->second.valid() || 
      ( iter->second.isWritable() && iter->second->isWritable() );
  // default is to return an objref to the field
  if( !check_tid || check_tid == TpObjRef )
  {
    // since we're returning an objref, writability to the ref is limited
    // by our own writability too
    can_write &= isWritable();
    FailWhen(flags&DMI::WRITE && !can_write,"write access violation"); 
    tid = TpObjRef;
    return &iter->second;
  }
  else // else a DataField (or Object) must have been explicitly requested
  {
    FailWhen(flags&DMI::WRITE && !can_write,"write access violation"); 
    FailWhen(check_tid != TpDataField && check_tid != TpObject,
        "type mismatch: expecting "+check_tid.toString()+", got DataField" );
    tid = TpDataField;
    return &iter->second.deref();
  }
  //## end DataRecord::get%3C56B00E0182.body
}

void * DataRecord::insert (const HIID &id, TypeId tid, TypeId &real_tid)
{
  //## begin DataRecord::insert%3C7A16BB01D7.body preserve=yes
  FailWhen( !id.size(),"null HIID" );
  FailWhen( fields.find(id) != fields.end(),"field "+id.toString()+" already exists" );
  if( tid == TpDataField || !tid ) // inserting a new DataField?
  {
    real_tid = tid;
    return &fields[id];
  }
  else     // inserting new DataField contents?
  {
    real_tid = tid;
    DataField *pf = new DataField(tid,-1);
    fields[id].attach(pf,DMI::ANON|DMI::WRITE|DMI::LOCK);
    TypeId dum1; bool dum2;
    return const_cast<void*>( pf->getn(0,dum1,dum2,0,True) );
  }
  //## end DataRecord::insert%3C7A16BB01D7.body
}

bool DataRecord::remove (const HIID &id)
{
  //## begin DataRecord::remove%3C877D140036.body preserve=yes
  dprintf(2)("remove(%s)\n",id.toString().c_str());
  FailWhen( !id.size(),"null HIID" );
  FailWhen( !isWritable(),"r/w access violation" );
  // is it our field -- just remove it
  CFMI iter = fields.find(id);
  if( iter != fields.end() )
  {
    dprintf(2)("  removing %s\n",iter->second.debug(1));
    fields.erase(iter->first);
    return True;
  }
  return False;
  //## end DataRecord::remove%3C877D140036.body
}

bool DataRecord::getFieldIter (DataRecord::Iterator& iter, HIID& id, TypeId& type, int& size) const
{
  //## begin DataRecord::getFieldIter%3CA20AD703A4.body preserve=yes
  if( iter == fields.end() )
    return False;
  id = iter->first;
  type = iter->second->type();
  size = iter->second->size();
  iter++;
  return True;
  //## end DataRecord::getFieldIter%3CA20AD703A4.body
}

// Additional Declarations
  //## begin DataRecord%3BB3112B0027.declarations preserve=yes
  //## end DataRecord%3BB3112B0027.declarations

//## begin module%3C10CC82005C.epilog preserve=yes
string DataRecord::sdebug ( int detail,const string &prefix,const char *name ) const
{
  static int nesting=0;
  if( nesting++>1000 )
  {
    cerr<<"Too many nested DataRecord::sdebug() calls";
    abort();
  }
  string out;
  if( detail>=0 ) // basic detail
  {
    Debug::appendf(out,"%s/%08x",name?name:"DataRecord",(int)this);
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    Debug::append(out,isWritable()?"RW ":"RO ");
    out += Debug::ssprintf("%d fields",fields.size());
    out += " / refs "+CountedRefTarget::sdebug(-1);
  }
  if( detail >= 2 || detail <= -2 )   // high detail
  {
    // append debug info from CountedRefTarget
    string str = CountedRefTarget::sdebug(-2,prefix+"      ");
    if( str.length() )
      out += "\n"+prefix+"  refs: "+str;
    for( CFMI iter = fields.begin(); iter != fields.end(); iter++ )
    {
      if( out.length() )
        out += "\n"+prefix+"  ";
      out += iter->first.toString()+": ";
      out += iter->second->sdebug(abs(detail)-1,prefix+"          ");
    }
  }
  nesting--;
  return out;
}
//## end module%3C10CC82005C.epilog

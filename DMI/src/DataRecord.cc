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
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DataRecord.cc

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
  //## end DataRecord::DataRecord%3C5820AD00C6.initialization
{
  //## begin DataRecord::DataRecord%3C5820AD00C6.body preserve=yes
  dprintf(2)("default constructor\n");
  writable = (flags&DMI::WRITE) != 0;
  //## end DataRecord::DataRecord%3C5820AD00C6.body
}

DataRecord::DataRecord (const DataRecord &other, int flags)
  //## begin DataRecord::DataRecord%3C5820C7031D.hasinit preserve=no
  //## end DataRecord::DataRecord%3C5820C7031D.hasinit
  //## begin DataRecord::DataRecord%3C5820C7031D.initialization preserve=yes
    : NestableContainer()
  //## end DataRecord::DataRecord%3C5820C7031D.initialization
{
  //## begin DataRecord::DataRecord%3C5820C7031D.body preserve=yes
  dprintf(2)("copy constructor, cloning from %s\n",other.debug(1));
  cloneOther(other,flags);
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
  dprintf(2)("assignment op, cloning from %s\n",right.debug(1));
  cloneOther(right);
  return *this;
  //## end DataRecord::operator=%3BB3112B0027_assign.body
}



//## Other Operations (implementation)
void DataRecord::add (const HIID &id, const DataFieldRef &ref, int flags)
{
  //## begin DataRecord::add%3BFBF5B600EB.body preserve=yes
  dprintf(2)("add(%s,[%s],%x)\n",id.toString().c_str(),ref->debug(1),flags);
  FailWhen( !id.size(),"null HIID" );
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

DataFieldRef DataRecord::remove (const HIID &id)
{
  //## begin DataRecord::remove%3BB311C903BE.body preserve=yes
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
  // otherwise, treat it as subrecord.field
  for( int i=0; i<id.length(); i++ )
  {
    HIID subid = id.subId(0,i);
    FMI iter = fields.find( subid );
    if( iter != fields.end() )
    {
      FailWhen( iter->second->type() != TpDataRecord,
                "remove(id): "+subid.toString()+" is not a sub-record" );
      FailWhen( !iter->second->isWritable(),"r/w access violation" ); 
      // if first item is an index, pop it off and use it
      int index = subid.popLeadIndex();
      // call remove on the sub-record
      return ((DataRecord*)iter->second->get(index))->remove(subid);
    }
  }
  Throw("field "+id.toString()+" not found");
  //## end DataRecord::remove%3BB311C903BE.body
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
  // otherwise, treat it as subrecord.field
  for( int i=0; i<id.length(); i++ )
  {
    HIID subid = id.subId(0,i);
    FMI iter = fields.find( subid );
    if( iter != fields.end() )
    {
      FailWhen( iter->second->type() != TpDataRecord,
                "remove(id): "+subid.toString()+" is not a sub-record" );
      FailWhen( !iter->second->isWritable(),"r/w access violation" ); 
      // if first item is an index, pop it off and use it
      int index = subid.popLeadIndex();
      // call replace on the sub-record
      ((DataRecord*)iter->second->get(index))->replace(subid,ref,flags);
    }
  }
  //## end DataRecord::replace%3BFCD4BB036F.body
}

DataFieldRef DataRecord::field (const HIID &id) const
{
  //## begin DataRecord::field%3C57CFFF005E.body preserve=yes
  HIID rest; bool dum;
  const DataFieldRef &ref( resolveField(id,rest,dum,False) );
  FailWhen( !ref.isValid(),"field "+id.toString()+" not found" );
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
    return ref.isValid() && !rest.size();
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
  FailWhen( !ref.isValid(),"field "+id.toString()+" not found" );
  FailWhen( rest.size(),id.toString()+" does not resolve to a complete field" );
  return ref.copy(flags);
  //## end DataRecord::fieldWr%3BFBF49D00A1.body
}

bool DataRecord::select (const HIIDSet &id)
{
  //## begin DataRecord::select%3C55761002CD.body preserve=yes
  return True;
  //## end DataRecord::select%3C55761002CD.body
}

void DataRecord::clearSelection ()
{
  //## begin DataRecord::clearSelection%3C5576100331.body preserve=yes
  //## end DataRecord::clearSelection%3C5576100331.body
}

int DataRecord::selectionToBlock (BlockSet& set)
{
  //## begin DataRecord::selectionToBlock%3C557610038B.body preserve=yes
  return 0;
  //## end DataRecord::selectionToBlock%3C557610038B.body
}

const DataFieldRef & DataRecord::resolveField (const HIID &id, HIID& rest, bool &can_write, bool must_write) const
{
  //## begin DataRecord::resolveField%3C552E2D009D.body preserve=yes
  FailWhen( !id.size(),"null HIID" );
  // This macro checks must_write against a writable property, and
  // updates the can_write variable. 
  #define CanWrite(x) { FailWhen(must_write && !x,"r/w access violation"); if( !x ) can_write = False; }
  can_write = True;
  CanWrite( isWritable() );
  rest.resize(0);
  // try to find field "a.b.c" directly
  CFMI iter = fields.find(id);
  if( iter != fields.end() )
  {
    CanWrite( iter->second->isWritable() );
    return iter->second;
  }
  // if last atom is an index ("a.b.c.1"), assume it's an index into the field,
  // so strip it off and try again
  int idlen = id.size(),index = id.back().index();
  if( idlen > 1 && index >= 0 )
  {
    iter = fields.find( id.subId(0,-2) );
    if( iter != fields.end() ) 
    {
      rest.push_back( id.back() );
      CanWrite( iter->second->isWritable() );
      return iter->second;
    }
  }
  // otherwise, try to recurse into sub-records, by trying all sub-ids
  // ("a", then "a.b", etc.) one by one
  // the idlast iterator points at one past the end of the current sub-id
  for( int iatom=0; iatom<idlen; iatom++ )
  {
    // look for a field corresponding to the sub-id
    iter = fields.find( id.subId(0,iatom) );
    if( iter != fields.end() ) // found field?
    {
      CanWrite( iter->second->isWritable() );
      // if next atom of remainder is an index, use that as an index into the field
      HIID subid = id.subId(iatom+1,-1);
      // is it a sub-record? Recurse into it
      if( iter->second->type() == TpDataRecord ) 
      {
        int index = subid.popLeadIndex();
        return ((DataRecord*)iter->second->get(index))->resolveField(subid,rest,must_write);
      }
      // else it's the final field, so return it
      rest = subid;
      return iter->second;
    }
  }
  // nothing was found -- return invalid ref
  return NullDataFieldRef;
  //## end DataRecord::resolveField%3C552E2D009D.body
}

const void * DataRecord::get (const HIID &id, TypeId& tid, bool& can_write, TypeId check_tid, bool must_write) const
{
  //## begin DataRecord::get%3C56B00E0182.body preserve=yes
  HIID rest;
  const DataFieldRef & ref( resolveField(id,rest,can_write,must_write) );
  // nothing found... return 0
  if( !ref.isValid() )
    return 0;
  // if remainder contains an index into the field, get it out
  int index = rest.popLeadIndex();
  // trim leading delimiters from remaining id
  while( rest.popLeadDelim() ) {};
  // nothing remains, so field completely resolved -- get its data
  if( !rest.size() )
  {
    tid = ref->type();
    FailWhen( check_tid && tid != check_tid, "field type mismatch" );
    return ref->get(index);
  }
  // else not completely resolved -- then field has to be a container
  else
  {
    // check that it is a sub-container
    FailWhen( !isNestable(ref->type()),
        id.toString() + ": sub-field is not a valid container (remainder is "+
        rest.toString()+")" );
    // recurse inside for rest of id sequence
    return ((NestableContainer*)(ref->get(index)))->get(rest,tid,can_write,check_tid,must_write);
  }
  //## end DataRecord::get%3C56B00E0182.body
}

bool DataRecord::getFieldInfo (const HIID &id, TypeId &tid, bool& can_write, bool no_throw) const
{
  //## begin DataRecord::getFieldInfo%3C57C63F03E4.body preserve=yes
  try {
    HIID rest; 
    const DataFieldRef & ref( resolveField(id,rest,can_write,False) );
    // nothing found... return 0
    if( !ref.isValid() )
      return False;
    // if remainder contains an index into the field, get it out
    int index = rest.popLeadIndex();
    // remove any delimiters
    rest.popLeadDelim();
    // nothing remains, so field completely resolved -- return its type
    if( !rest.size() )
    {
      tid = ref->type();
      return True;
    }
    // else not completely resolved -- then field has to be a container
    else
    {
      // check that it is a sub-container
      if( !isNestable(ref->type()) )
        Throw( id.toString() + ": sub-field is not a valid container" );
      // recurse inside for rest of id sequence
      return ((NestableContainer*)(ref->get(index)))->getFieldInfo(rest,tid,can_write,no_throw);
    }
  } catch( Debug::Error &x ) {
    if( no_throw )
      return False;
    throw(x);
  }
  return False;
  //## end DataRecord::getFieldInfo%3C57C63F03E4.body
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
  size_t hsize = sizeof(int)*(1+fields.size());
  for( CFMI iter = fields.begin(); iter != fields.end(); iter++ )
    hsize += iter->first.byteSize();
  // allocate new header block
  SmartBlock *header = new SmartBlock(hsize);
  // store header info
  int *hdata = (int *)(header->data());
  char *hids = sizeof(int)*(1+fields.size()) + (char*)hdata;
  *hdata++ = fields.size();
  set.push( BlockRef(header,DMI::WRITE|DMI::ANON) );
  dprintf(2)("toBlock: %d header bytes, %d fields\n",hsize,fields.size());
  // store IDs and convert everything
  for( CFMI iter = fields.begin(); iter != fields.end(); iter++ )
  {
    *hdata = iter->first.byteSize();
    iter->first.copy(hids);
    hids += *hdata;
    hdata++;
    int nr1 = iter->second->toBlock(set);
    nref += nr1;
    dprintf(3)("%s [%s] generated %d blocks\n",
        iter->first.toString().c_str(),iter->second->debug(1),nr1);
  }
  dprintf(2)("toBlock: %d total blocks generated\n",nref);
  return nref;
  //## end DataRecord::toBlock%3C5821630371.body
}

CountedRefTarget* DataRecord::clone (int flags) const
{
  //## begin DataRecord::clone%3C58218900EB.body preserve=yes
  dprintf(2)("cloning new DataRecord\n");
  return new DataRecord(*this,flags);
  //## end DataRecord::clone%3C58218900EB.body
}

void DataRecord::privatize (int flags)
{
  //## begin DataRecord::privatize%3C582189019F.body preserve=yes
  dprintf(2)("privatizing DataRecord\n");
  writable = (flags&DMI::WRITE)!=0;
  if( flags&DMI::DEEP )
  {
    for( FMI iter = fields.begin(); iter != fields.end(); iter++ )
      iter->second.privatize(flags|DMI::LOCK);
  }
  //## end DataRecord::privatize%3C582189019F.body
}

void DataRecord::cloneOther (const DataRecord &other, int flags)
{
  //## begin DataRecord::cloneOther%3C58239503D1.body preserve=yes
  fields.clear();
  writable = (flags&DMI::WRITE)!=0;
  // copy all field refs
  for( CFMI iter = other.fields.begin(); iter != other.fields.end(); iter++ )
  {
    DataFieldRef & ref( fields[iter->first].copy(iter->second,flags|DMI::LOCK) );
    if( flags&DMI::DEEP )
      ref.privatize(flags|DMI::LOCK);
  }
  //## end DataRecord::cloneOther%3C58239503D1.body
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


// Detached code regions:
#if 0
//## begin DataRecord::add%3C5FF0D60106.body preserve=yes
  add(id,DataFieldRef(pfld,flags));
//## end DataRecord::add%3C5FF0D60106.body

#endif

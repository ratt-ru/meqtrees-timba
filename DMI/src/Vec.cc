//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820126.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820126.cm

//## begin module%3C10CC820126.cp preserve=no
//## end module%3C10CC820126.cp

//## Module: DataField%3C10CC820126; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: f:\lofar8\oms\LOFAR\cep\cpa\pscf\src\DataField.cc

//## begin module%3C10CC820126.additionalIncludes preserve=no
//## end module%3C10CC820126.additionalIncludes

//## begin module%3C10CC820126.includes preserve=yes
#include "DynamicTypeManager.h"
#include "DataRecord.h"
//## end module%3C10CC820126.includes

// DataField
#include "DataField.h"
//## begin module%3C10CC820126.declarations preserve=no
//## end module%3C10CC820126.declarations

//## begin module%3C10CC820126.additionalDeclarations preserve=yes
static int nullheader_data[] = {0,0};
static SmartBlock nullheader_block( nullheader_data,sizeof(nullheader_data),DMI::NO_DELETE );
static BlockRef nullheader(nullheader_block,DMI::EXTERNAL|DMI::LOCK|DMI::READONLY);
static ObjRef NullRef;
static NestableContainer::Register reg(TpDataField,True);
//## end module%3C10CC820126.additionalDeclarations


// Class DataField 

DataField::DataField (int flags)
  //## begin DataField::DataField%3C3D64DC016E.hasinit preserve=no
  //## end DataField::DataField%3C3D64DC016E.hasinit
  //## begin DataField::DataField%3C3D64DC016E.initialization preserve=yes
  : NestableContainer(flags&DMI::WRITE!=0),
    mytype(0),mysize(0),selected(False)
  //## end DataField::DataField%3C3D64DC016E.initialization
{
  //## begin DataField::DataField%3C3D64DC016E.body preserve=yes
  dprintf(2)("default constructor\n");
  //## end DataField::DataField%3C3D64DC016E.body
}

DataField::DataField (const DataField &right, int flags)
  //## begin DataField::DataField%3C3EE3EA022A.hasinit preserve=no
  //## end DataField::DataField%3C3EE3EA022A.hasinit
  //## begin DataField::DataField%3C3EE3EA022A.initialization preserve=yes
    : NestableContainer(flags&DMI::WRITE!=0),mytype(0)
  //## end DataField::DataField%3C3EE3EA022A.initialization
{
  //## begin DataField::DataField%3C3EE3EA022A.body preserve=yes
  dprintf(2)("copy constructor (%s,%x)\n",right.debug(),flags);
  cloneOther(right,flags);
  //## end DataField::DataField%3C3EE3EA022A.body
}

DataField::DataField (TypeId tid, int num, int flags)
  //## begin DataField::DataField%3BFA54540099.hasinit preserve=no
  //## end DataField::DataField%3BFA54540099.hasinit
  //## begin DataField::DataField%3BFA54540099.initialization preserve=yes
    : NestableContainer(flags&DMI::WRITE!=0),
      mytype(0),mysize(0),selected(False)
  //## end DataField::DataField%3BFA54540099.initialization
{
  //## begin DataField::DataField%3BFA54540099.body preserve=yes
  dprintf(2)("constructor(%s,%d,%x)\n",tid.toString().c_str(),num,flags);
  init(tid,num);
  //## end DataField::DataField%3BFA54540099.body
}


DataField::~DataField()
{
  //## begin DataField::~DataField%3BB317D8010B_dest.body preserve=yes
  dprintf(2)("destructor\n");
  clear();
  //## end DataField::~DataField%3BB317D8010B_dest.body
}


DataField & DataField::operator=(const DataField &right)
{
  //## begin DataField::operator=%3BB317D8010B_assign.body preserve=yes
  dprintf(2)("assignment of %s\n",right.debug());
  FailWhen( valid(),"field is already initialized" );
  clear();
  cloneOther(right);
  return *this;
  //## end DataField::operator=%3BB317D8010B_assign.body
}



//## Other Operations (implementation)
DataField & DataField::init (TypeId tid, int num, const void *data)
{
  //## begin DataField::init%3C6161190193.body preserve=yes
  dprintf(2)("init(%s,%d,%x)\n",tid.toString().c_str(),num,(int)data);
  // if null type, then reset the field to uninit state
  if( !tid )
  {
    mytype = 0;
    mysize = 0;
    writable = scalar = True;
    return *this;
  }
  FailWhen( valid(),"field is already initialized" );
  if( num==-1 )
  {
    num = 1;
    scalar = True;
  }
  else
    scalar = False;
  FailWhen( num<0,"illegal field size" );
  // obtain type information, check that type is supported
  const TypeInfo & typeinfo( TypeInfo::find(tid) );
  FailWhen( !typeinfo.category,"unknown data type "+tid.toString() );
  FailWhen( typeinfo.category == TypeInfo::OTHER && tid != Tpstring,
            "unsupported data type "+tid.toString() );
  mytype = tid;
  mysize = max(num,1);
  // NUMERIC & BINARY type categories are treated as binary objects
  // of a fixed type, which can be bitwise-copied
  binary_type = typeinfo.category==TypeInfo::NUMERIC || 
                typeinfo.category==TypeInfo::BINARY;
  dynamic_type = !binary_type && mytype != Tpstring;

  if( mytype == Tpstring )  // init string field
  {
    FailWhen(data && num>1,Debug::ssprintf("can't init field string[%d] with data",num));
    headref.attach( new SmartBlock( sizeof(int)*(2+mysize) ),
                    DMI::WRITE|DMI::ANON|DMI::LOCK );
    strvec.resize(mysize);
    strvec_modified = False;
    if( data && mysize>0 )
      strvec[0] = string( static_cast<const char *>(data) );
  }
  else if( binary_type )    // init binary field
  {
    typesize = typeinfo.size;
    // allocate header and copy data
    SmartBlock *header = new SmartBlock( sizeof(int)*2 + typesize*mysize);
    headref.attach( header,DMI::WRITE|DMI::ANON|DMI::LOCK);
    if( data )
      memcpy(sizeof(int)*2 + (char*)header->data(),data,typesize*mysize);
    else
      memset(sizeof(int)*2 + (char*)header->data(),0,typesize*mysize);
  }
  else  // init dynamic object
  {
    Assert(dynamic_type);
    FailWhen(data,Debug::ssprintf("can't init field %s[%d] with data",tid.toString().c_str(),num) );
    
    headref.attach( new SmartBlock( sizeof(int)*(2+mysize),DMI::ZERO ),
                    DMI::WRITE|DMI::ANON|DMI::LOCK );
    objects.resize(mysize);
    blocks.resize(mysize);
    objstate.resize(mysize);
    objstate.assign(mysize,UNINITIALIZED);
  }
  headerType() = mytype;
  headerSize() = mysize;
  // make header block non-writable
  if( !isWritable() )
    headref.change(DMI::READONLY);
  return *this;
  //## end DataField::init%3C6161190193.body
}

void DataField::resize (int newsize)
{
  //## begin DataField::resize%3C62961D021B.body preserve=yes
  FailWhen( newsize<=0,"can't resize to <=0" );
  FailWhen( !valid(),"uninitialized DataField" );
  FailWhen( !isWritable(),"field is read-only" );
  FailWhen( !isWritable(),"field is read-only" );
  mysize = newsize;
  if( newsize > 1 )
    scalar = False;
  if( mytype == Tpstring )
  {
    headref().resize( sizeof(int)*(2+newsize) );
    strvec.resize(newsize);
    strvec_modified = True;
  }
  else if( binary_type )
    headref().resize( sizeof(int)*2 + typesize*newsize );
  else
  {
    Assert( dynamic_type );
    objects.resize(newsize);
    blocks.resize(newsize);
    objstate.resize(newsize);
    // note that when resizing upwards, this implicitly fills the empty
    // objstates with 0 = UNINITIALIZED
  }
  mysize = newsize;
  //## end DataField::resize%3C62961D021B.body
}

void DataField::clear (int flags)
{
  //## begin DataField::clear%3C3EAB99018D.body preserve=yes
  if( valid() )
  {
    dprintf(2)("clearing\n");
    if( headref.valid() )
      headref.unlock().detach();
    strvec.resize(0);
    if( objects.size() ) objects.resize(0);
    if( blocks.size() ) blocks.resize(0);
    objstate.resize(0);
    mytype = 0;
    selected = False;
    writable = (flags&DMI::WRITE)!=0;
  }
  //## end DataField::clear%3C3EAB99018D.body
}

bool DataField::isValid (int n)
{
  //## begin DataField::isValid%3C3EB9B902DF.body preserve=yes
  if( !valid() )
    return False;
  checkIndex(n);
  if( dynamic_type ) 
    return objstate[n] != UNINITIALIZED;
  else
    return True; // built-ins always valid
  //## end DataField::isValid%3C3EB9B902DF.body
}

ObjRef DataField::objwr (int n, int flags)
{
  //## begin DataField::objwr%3C0E4619019A.body preserve=yes
  FailWhen( !valid(),"uninitialized DataField");
  FailWhen( !isWritable(),"field is read-only" );
  checkIndex(n);
  if( !dynamic_type )
    return NullRef;
  return resolveObject(n,True).copy(flags);
  //## end DataField::objwr%3C0E4619019A.body
}

DataField & DataField::put (int n, ObjRef &ref, int flags)
{
  //## begin DataField::put%3C7A305F0071.body preserve=yes
  dprintf(2)("putting @%d: %s\n",n,ref.debug(2));
  ObjRef &ref2 = prepareForPut( ref->objectType(),n,flags );
  // grab the ref, and mark object as modified
  if( flags&DMI::COPYREF )
    ref2.copy(ref,flags);
  else
    ref2 = ref;
  return *this;
  //## end DataField::put%3C7A305F0071.body
}

ObjRef DataField::objref (int n) const
{
  //## begin DataField::objref%3C3C8D7F03D8.body preserve=yes
  FailWhen( !valid(),"uninitialized DataField");
  checkIndex(n);
  if( !dynamic_type )
    return NullRef;
  // return a copy as a read-only ref
  return resolveObject(n,False).copy(DMI::READONLY);
  //## end DataField::objref%3C3C8D7F03D8.body
}

int DataField::fromBlock (BlockSet& set)
{
  //## begin DataField::fromBlock%3C3D5F2001DC.body preserve=yes
  dprintf1(2)("%s: fromBlock\n",debug());
  clear(isWritable()?DMI::WRITE:DMI::READONLY);
  int npopped = 1;
  // get header block, privatize & cache it as headref
  set.pop(headref);  
  size_t hsize = headref->size();
  FailWhen( hsize < sizeof(int)*2,"malformed header block" );
  headref.privatize((isWritable()?DMI::WRITE:0)|DMI::LOCK);
  // get type and size from header
  mytype = headerType();
  mysize = headerSize();
  if( mysize == -1 )
  {
    mysize = 1;
    scalar = True;
  }
  else
    scalar = False;
  if( !mytype )  // uninitialized field
    return 1;
  // obtain type information, check that type is supported
  const TypeInfo & typeinfo( TypeInfo::find(mytype) );
  FailWhen( !typeinfo.category,"unknown data type "+mytype.toString() );
  FailWhen( typeinfo.category == TypeInfo::OTHER && mytype != Tpstring,
            "unsupported data type "+mytype.toString() );
  // NUMERIC & BINARY type categories are treated as binary objects
  // of a fixed type, which can be bitwise-copied
  binary_type = typeinfo.category==TypeInfo::NUMERIC || 
                typeinfo.category==TypeInfo::BINARY;
  dynamic_type = !binary_type && mytype != Tpstring;

  // For strings, the header will contain N string lengths 
  // (as ints), followed by the strings themselves
  if( mytype == Tpstring )
  {
    FailWhen( hsize < sizeof(int)*(2+mysize),"incorrect block size" );
    strvec.resize(mysize);
    // assign the strings
    char *hdata = (char*)headref->data();        // start of header
    size_t istr0 = sizeof(int)*(2+mysize);   // char position of start of first string
    int i=0;
    for( VSI iter = strvec.begin(); iter != strvec.end(); iter++ )
    {
      size_t len = ((int*)hdata)[2+i];
      FailWhen( istr0+len > hsize,"incorrect block size");
      iter->assign(hdata+istr0,len);
      istr0 += len;
    }
    strvec_modified = False; 
  }
  // for built-in types, the header block simply contains the data. 
  else if( binary_type )
  {
    typesize = typeinfo.size;
    dprintf(2)("fromBlock: built-in type %s[%d]\n",mytype.toString().c_str(),mysize);
    FailWhen( hsize != sizeof(int)*2 + typesize*mysize,
                "incorrect block size" );
  }
  else  // else dynamic type: the header contains info on # of blocks to follow
  {
    Assert( dynamic_type );
    dprintf(2)("fromBlock: dynamic type %s[%d]\n",mytype.toString().c_str(),mysize);
    FailWhen( hsize != sizeof(int)*(2 + mysize),"incorrect block size" );
    objects.resize(mysize);
    blocks.resize(mysize);
    objstate.resize(mysize);
    objstate.assign(mysize,INBLOCK);
  // get blocks from set and privatize them as appropriate
  // do not unblock objects, as that is done at dereference time
    for( int i=0; i<mysize; i++ ) 
    {
      npopped += headerBlockSize(i);
      if( headerBlockSize(i) )
      {
        dprintf(3)("fromBlock: [%d] taking over %d blocks\n",i,headerBlockSize(i));
        set.popMove(blocks[i],headerBlockSize(i));
        dprintf(3)("fromBlock: [%d] will privatize %d blocks\n",i,blocks[i].size());
        blocks[i].privatizeAll(isWritable()?DMI::WRITE:0);
      }
      else // no blocks assigned to this object => is uninitialized
        objstate[i] = UNINITIALIZED;
    }
    dprintf(2)("fromBlock: %d blocks were popped\n",npopped);
  }
  return npopped;
  //## end DataField::fromBlock%3C3D5F2001DC.body
}

int DataField::toBlock (BlockSet &set) const
{
  //## begin DataField::toBlock%3C3D5F2403CC.body preserve=yes
  if( !valid() )
  {
    dprintf1(2)("%s: toBlock=0 (field empty)\n",debug());
    return 0;
  }
  dprintf1(2)("%s: toBlock\n",debug());
  int npushed = 1,tmp; // 1 header block as a minimum
  // if dealing with strings, and they have been modified, the 
  // header block needs to be rebuilt
  if( mytype == Tpstring && strvec_modified )
  {
    // allocate and attach header block
    int hsize = sizeof(int)*(2+mysize);
    for( CVSI iter = strvec.begin(); iter != strvec.end(); iter++ )
      hsize += iter->length();
    headref.attach( new SmartBlock(hsize),
                    DMI::WRITE|DMI::ANON|DMI::LOCK );
    // write basic fields
    headerType() = mytype;
    headerSize() = scalar ? -mysize : mysize;
    // write out lengths and string data into header block
    int *plen = &headerBlockSize(0);
    char *pdata = (char*)(plen + mysize);
    for( CVSI iter = strvec.begin(); iter != strvec.end(); iter++ )
    {
      int len = *plen = iter->length();
      iter->copy(pdata,len); 
      pdata += len;
      plen++;
    }
    strvec_modified = False;
    // if read-only, downgrade block reference
    if( !isWritable() )
      headref.change(DMI::READONLY);
  }
  // push out the header block
  headerType() = mytype;
  headerSize() = scalar ? -mysize : mysize;
  set.push(headref.copy(DMI::READONLY));
  // for dynamic types, do a toBlock on the objects, if needed
  if( dynamic_type )
  {
    for( int i=0; i<mysize; i++ )
    {
      switch( objstate[i] )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            dprintf(3)("toBlock: [%d] is uninitialized, 0 blocks\n",i);
            headerBlockSize(i) = 0;
            break;
        // then simply copy the blockset
        // if modified, do a toBlock on the object
        case MODIFIED:
            blocks[i].clear();
            tmp = objects[i]->toBlock(blocks[i]);
            dprintf(3)("toBlock: [%d] was modified, converted to %d blocks\n",i,tmp);
            // if no other write refs to the object exist, mark it
            // as unmodified again
            if( objects[i].hasOtherWriters() )
              objstate[i] = UNBLOCKED;
            // fall thru below to add blocks to set
        // if still in block, or unblocked but not modified,
        case INBLOCK:
        case UNBLOCKED:
            dprintf(3)("toBlock: [%d] copying %d blocks\n",i,blocks[i].size());
            set.pushCopy(blocks[i]);
            npushed += headerBlockSize(i) = blocks[i].size();
            break;
        default:
            Throw("illegal object state");
      }
    }
  } 
  dprintf(2)("toBlock: %d blocks pushed\n",npushed);
  return npushed;
  //## end DataField::toBlock%3C3D5F2403CC.body
}

ObjRef & DataField::resolveObject (int n, bool write) const
{
  //## begin DataField::resolveObject%3C3D8C07027F.body preserve=yes
  switch( objstate[n] )
  {
    // uninitialized object - create default
    case UNINITIALIZED:
         dprintf(3)("resolveObject(%d): creating new %s\n",n,mytype.toString().c_str());
         objects[n].attach( DynamicTypeManager::construct(mytype),
                           (isWritable()?DMI::WRITE:DMI::READONLY)|
                           DMI::ANON|DMI::LOCK );
         objstate[n] = MODIFIED;
         return objects[n];
         
    // object hasn't been unblocked
    case INBLOCK:
         // if write access requested, simply unblock it
         if( write )
         {
           dprintf(3)("resolveObject(%d): unblocking %s\n",n,mytype.toString().c_str());
           objects[n].attach( DynamicTypeManager::construct(mytype,blocks[n]),
                             (isWritable()?DMI::WRITE:DMI::READONLY)|
                             DMI::ANON|DMI::LOCK );
           // verify that no blocks were left over
           FailWhen( blocks[n].size()>0,"block count mismatch" );
           objstate[n] = MODIFIED;
         }
         // For r/o access, we want to cache a copy of the blockset.
         // This is in case the object doesn't get modified down the road, 
         // so we can just re-use the blockset in a future toBlock()
         else
         {
           // make copy, retaining r/w privileges, and marking the 
           // source as r/o
           dprintf(3)("resolveObject(%d): read access, preserving old blocks\n",n);
           BlockSet set( blocks[n],DMI::PRESERVE_RW|DMI::MAKE_READONLY ); 
           // create object and attach a reference
           dprintf(3)("resolveObject(%d): unblocking %s\n",n,mytype.toString().c_str());
           objects[n].attach( DynamicTypeManager::construct(mytype,set),
                             (isWritable()?DMI::WRITE:DMI::READONLY)|
                             DMI::ANON|DMI::LOCK );
           // verify that no blocks were left over
           FailWhen( set.size()>0,"block count mismatch" );
           // mark object as unblocked but not modified 
           objstate[n] = UNBLOCKED; 
         }
         return objects[n];

    // object exists, hasn't been modified
    case UNBLOCKED:
         if( write )
         {
           // requesting write access to a previously unmodified object:
           // flush cached blocks and mark as modified
           blocks[n].clear();
           objstate[n] = MODIFIED;
         }
         return objects[n];
    
    // object exists and has been modified - simply return the ref
    case MODIFIED:
         return objects[n];
    
    default:
         Throw("illegal object state");
  }
  return objects[n];
  //## end DataField::resolveObject%3C3D8C07027F.body
}

CountedRefTarget* DataField::clone (int flags) const
{
  //## begin DataField::clone%3C3EC77D02B1.body preserve=yes
  return new DataField(*this,flags);
  //## end DataField::clone%3C3EC77D02B1.body
}

void DataField::cloneOther (const DataField &other, int flags)
{
  //## begin DataField::cloneOther%3C3EE42D0136.body preserve=yes
  // setup misc fields
  FailWhen( valid(),"field is already initialized" );
  mytype = other.type();
  mysize = other.size();
  binary_type = other.binary_type;
  dynamic_type = other.dynamic_type;
  typesize = other.typesize;
  writable = (flags&DMI::WRITE)!=0;
  selected = False;
  // copy & privatize the header ref
  headref.copy(other.headref).privatize(flags|DMI::LOCK);
  // handle built-in types -- only strings need to be copied
  if( mytype == Tpstring ) 
  {
    strvec = other.strvec;
    strvec_modified = other.strvec_modified;
  }
  else if( dynamic_type )   // handle dynamic types
  {
    objstate = other.objstate;
    for( int i=0; i<mysize; i++ )
    {
      switch( objstate[i] )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            break;
        // if still in block, then copy & privatize the blockset
        case INBLOCK:
            blocks[i] = other.blocks[i]; // blockset copy (=ref.copy)
            if( flags&DMI::DEEP )
              blocks[i].privatizeAll(flags);
            break;
        // otherwise, privatize the object reference
        case UNBLOCKED:
        case MODIFIED:
            objects[i].copy(other.objects[i],flags|DMI::LOCK);
            if( flags&DMI::DEEP );
              objects[i].privatize(flags|DMI::LOCK);
            break;
        default:
            Throw("illegal object state");
      }
    }
  }
  //## end DataField::cloneOther%3C3EE42D0136.body
}

void DataField::privatize (int flags)
{
  //## begin DataField::privatize%3C3EDEBC0255.body preserve=yes
  writable = (flags&DMI::WRITE) != 0;
  if( !valid() )
    return;
  // privatize the header reference
  headref.privatize(DMI::WRITE|DMI::LOCK);
  // if deep privatization is required, then for dynamic objects, 
  // privatize the field contents as well
  if( flags&DMI::DEEP && dynamic_type )
  {
    for( int i=0; i<mysize; i++ )
    {
      switch( objstate[i] )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            break;
        // if still in block, then privatize the blockset
        case INBLOCK:
            blocks[i].privatizeAll(flags);
            break;
        // otherwise, privatize the object reference
        case UNBLOCKED:
        case MODIFIED:
            objects[i].privatize(flags|DMI::LOCK);
            break;
        default:
            Throw("illegal object state");
      }
    }
  }
  //## end DataField::privatize%3C3EDEBC0255.body
}

const void * DataField::get (const HIID &id, TypeId& tid, bool& can_write, TypeId check_tid, bool must_write) const
{
  //## begin DataField::get%3C7A19790361.body preserve=yes
  // null HIID implies access to first element
  if( !id.size() )
    return getn(0,tid,can_write,check_tid,must_write);
  // single-index HIID implies get[n]
  if( id.size()==1 && id.front().index()>=0 )
    return getn(id.front().index(),tid,can_write,check_tid,must_write);
  FailWhen( !valid(),"field not initialized" );
  FailWhen( !size(),"uninitialized DataField" );
  FailWhen( !scalar,"non-scalar field, explicit index expected" );
  FailWhen( !isNestable(type()),"contents not a container" );
  // resolve to pointer to container
  const NestableContainer *nc = dynamic_cast<const NestableContainer *>
      (&resolveObject(0,must_write).deref());
  Assert(nc);
  // defer to get[id] on container
  return nc->get(id,tid,can_write,check_tid,must_write);
  //## end DataField::get%3C7A19790361.body
}

const void * DataField::getn (int n, TypeId& tid, bool& can_write, TypeId check_tid, bool must_write) const
{
  //## begin DataField::getn%3C7A1983024D.body preserve=yes
  FailWhen( !valid(),"field not initialized" );
  FailWhen( n<0 || n>size(),"n out of range" );
  if( n == size() )
    return 0;
  can_write = isWritable();
  FailWhen(must_write && !can_write,"write access violation"); 
  if( type() == Tpstring ) // string type -- types must match
  {
    FailWhen( check_tid && check_tid != Tpstring,
        "type mismatch: expecting "+check_tid.toString()+", got "+type().toString());
    tid = Tpstring;
    if( must_write )
      strvec_modified = True;
    return &strvec[n];
  }
  else if( binary_type ) // binary type
  {
    // types must match, or TpNumeric can match any numeric type
    FailWhen( check_tid && check_tid != type() &&
              (check_tid != TpNumeric || !isNumericType(type())),
        "type mismatch: expecting "+check_tid.toString()+", got "+type().toString());
    tid = type();
    return n*typesize + (char*)headerData();
  }
  else // dynamic type
  {
    if( !check_tid || check_tid == TpObjRef ) // default is to return a reference
    {
      tid = TpObjRef;
      return &resolveObject(n,must_write);
    }
    else // else types must match, or TpObject can be specified as 
    {    //    a special case that forces dereferencing
      FailWhen( check_tid != type() && check_tid != TpObject,
          "type mismatch: expecting "+check_tid.toString()+", got "+type().toString());
      tid = type();
      return &resolveObject(n,must_write).deref();
    }
  }
  //## end DataField::getn%3C7A1983024D.body
}

void * DataField::insert (const HIID &id, TypeId tid, TypeId &real_tid)
{
  //## begin DataField::insert%3C7A198A0347.body preserve=yes
  dprintf(2)("insert(%s,%s)\n",id.toString().c_str(),tid.toString().c_str());
  FailWhen( !id.size(),"null HIID" );
  if( id.size()==1 && id.front().index()>=0 )
    return insertn(id.front().index(),tid,real_tid);
  FailWhen( !valid() || !size(),"field not initialized or empty" );
  FailWhen( !scalar,"non-scalar field, explicit index expected" );
  FailWhen( !isNestable(type()),"contents not a container" );
  // resolve to pointer to container
  dprintf(2)("insert: deferring to child %s\n",type().toString().c_str());
  NestableContainer *nc = dynamic_cast<NestableContainer *>
      (&resolveObject(0,True).dewr());
  Assert(nc);
  // defer to insert[id] on container
  return nc->insert(id,tid,real_tid);
  //## end DataField::insert%3C7A198A0347.body
}

void * DataField::insertn (int n, TypeId tid, TypeId &real_tid)
{
  //## begin DataField::insertn%3C7A19930250.body preserve=yes
  // empty field? init with one element
  dprintf(2)("insertn(%d,%s)\n",n,tid.toString().c_str());
  if( !valid() )
  {
    FailWhen( n,Debug::ssprintf("can't insert at [%d]",n) );
    FailWhen( !tid || tid==TpObjRef || tid==TpObject || tid==TpNumeric,
             "can't initialize without type" );
    init(real_tid=tid,-1); // init as scalar field
  }
  else // else extend field if inserting at end
  {
    FailWhen( n != size(),Debug::ssprintf("can't insert at [%d]",n) );
    resize( size()+1 );
    real_tid = type();
  }
  // now return pointer to datum
  if( type() == Tpstring )
  {
    FailWhen( tid && tid != type(),"can't insert "+tid.toString());
    strvec_modified = True;
    return &strvec[n];
  }
  else if( binary_type )
  {
    FailWhen( tid && tid!=type() && (!isNumericType(tid) || !isNumericType(type())),
        "can't insert "+tid.toString());
    return n*typesize + (char*)headerData();
  }
  else // dynamic type
  {
    FailWhen(tid && tid!=type(),"can't insert "+tid.toString());
    return &resolveObject(n,True);
  }
  //## end DataField::insertn%3C7A19930250.body
}

bool DataField::remove (const HIID &id)
{
  //## begin DataField::remove%3C877E1E03BE.body preserve=yes
  dprintf(2)("remove(%s)\n",id.toString().c_str());
  FailWhen( !id.size(),"null HIID" );
  if( id.size()==1 && id.front().index()>=0 )
    return removen(id.front().index());
  FailWhen( !valid() || !size(),"field not initialized or empty" );
  FailWhen( !scalar,"non-scalar field, explicit index expected" );
  FailWhen( !isNestable(type()),"contents not a container" );
  // resolve to pointer to container
  dprintf(2)("remove: deferring to child %s\n",type().toString().c_str());
  NestableContainer *nc = dynamic_cast<NestableContainer *>
      (&resolveObject(0,True).dewr());
  Assert(nc);
  // defer to remove(id) on container
  return nc->remove(id);
  //## end DataField::remove%3C877E1E03BE.body
}

bool DataField::removen (int n)
{
  //## begin DataField::removen%3C877E260301.body preserve=yes
  // empty field? init with one element
  dprintf(2)("removen(%d)\n",n);
  FailWhen( !valid() || !size(),"field not initialized or empty" );
  FailWhen( n!=size()-1,"can only remove from end of field" );
  dprintf(2)("removen: resizing to %d elements\n",n);
  resize(n);
  return True;
  //## end DataField::removen%3C877E260301.body
}

// Additional Declarations
  //## begin DataField%3BB317D8010B.declarations preserve=yes

ObjRef & DataField::prepareForPut (TypeId tid,int n,int flags)
{
  FailWhen( !isWritable(),"field is read-only" );
  if( !valid() ) // invalid field?
  {
    if( flags&DMI::AUTOEXTEND && !n )
      init(tid,1);   // empty field auto-extended to 1
    else
      Throw("uninitialized DataField");
  }
  else
  {
    FailWhen( tid != mytype, "type mismatch in put("+tid.toString()+")" );
    if( n == size() && flags&DMI::AUTOEXTEND )
      resize(n+1);  // auto-resize if inserting at last+1
    else
      checkIndex(n);
  }
  // grab the ref, and mark object as modified
  blocks[n].clear();
  objstate[n] = MODIFIED;
  return objects[n];
}

string DataField::sdebug ( int detail,const string &prefix,const char *name ) const
{
  static int nesting=0;
  if( nesting++>1000 )
  {
    cerr<<"Too many nested DataField::sdebug() calls";
    abort();
  }
  string out;
  if( detail>=0 ) // basic detail
  {
    Debug::appendf(out,"%s/%08x",name?name:"DataField",(int)this);
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    Debug::append(out,isWritable()?"RW ":"RO ");
    if( !type() )
      out += "empty";
    else
      out += type().toString()+Debug::ssprintf(":%d",size());
    out += " / refs "+CountedRefTarget::sdebug(-1);
  }
  if( detail >= 2 || detail <= -2 )   // high detail
  {
    // append debug info from CountedRefTarget
    string str = CountedRefTarget::sdebug(-2,prefix+"      ");
    if( str.length() )
      out += "\n"+prefix+"  refs: "+str;
  }
  if( dynamic_type && (detail >= 2 || detail <= -2) && size()>0 )   // high detail
  {
    // append object list
    for( int i=0; i<size(); i++ )
    {
      if( out.length() )
        out += "\n"+prefix;
      switch( objstate[i] )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            out += "    "+Debug::ssprintf("%d: uninitialized",i);
            break;
        case INBLOCK:
            out += "    "+Debug::ssprintf("%d: in block: ",i)
                         +blocks[i].sdebug(abs(detail)-1,prefix+"    ");
            break;
        case UNBLOCKED:
            out += "    "+Debug::ssprintf("%d: unblocked [",i)
                         +blocks[i].sdebug(abs(detail)-1,prefix+"    ")
                         +"], to"
                         +objects[i].sdebug(abs(detail)-1,prefix+"    ");
            break;
        case MODIFIED:
            out += "    "+Debug::ssprintf("%d: modified ",i)
                         +objects[i].sdebug(abs(detail)-1,prefix+"    ");
            break;
        default:
            Throw("illegal object state");
      }
    }
  }
  nesting--;
  return out;
}

  //## end DataField%3BB317D8010B.declarations
//## begin module%3C10CC820126.epilog preserve=yes
// Data

//## end module%3C10CC820126.epilog


// Detached code regions:
#if 0
//## begin DataField::remove%3C3EC3470153.body preserve=yes
  FailWhen( !valid(),"uninitialized DataField");
  FailWhen( !isWritable(),"field is read-only" );
  checkIndex(n);
  if( !dynamic_type )
    return NullRef;
  // transfer object reference
  ObjRef ret = resolveObject(n,True);
  objstate[n] = UNINITIALIZED;
  dprintf(2)("removing @%d: %s\n",n,ret.debug(2));
  return ret;
//## end DataField::remove%3C3EC3470153.body

//## begin DataField::put%3C3C84A40176.body preserve=yes
  dprintf(2)("putting @%d: %s\n",n,obj.debug(2));
  ObjRef &ref = prepareForPut( obj->objectType(),n,flags );
  // grab the ref, and mark object as modified
  if( flags&DMI::COPYREF )
    ref.copy(obj,flags);
  else
    ref = obj;
  return *this;
//## end DataField::put%3C3C84A40176.body

//## begin DataField::get%3C5FB272037E.body preserve=yes
//   FailWhen( !valid(),"uninitialized DataField");
//   tid = mytype;
//   FailWhen( check_tid && check_tid != tid,"type mismatch (expected "+check_tid.toString()+")" ); 
//   can_write = isWritable();
//   FailWhen( must_write && !can_write,"r/w access violation" );
//   
//   checkIndex(n);
//   if( mytype == Tpstring ) // string? return the string
//   {
//     strvec_modified |= can_write; // mark as modified
//     return &strvec[n];
//   }
//   else if( binary_type )
//   {
//     // else return pointer to item
//     return n*typesize + (char*)headerData();
//   }
//   else
//   {
//     if( must_write )
//       return &resolveObject(n,True).dewr();
//     else
//       return &resolveObject(n,False).deref();
//   }
//## end DataField::get%3C5FB272037E.body

#endif

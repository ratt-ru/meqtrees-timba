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
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DataField.cc

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

//## end module%3C10CC820126.additionalDeclarations


// Class DataField::ConstHook 

// Additional Declarations
  //## begin DataField::ConstHook%3C614FDE0039.declarations preserve=yes
  //## end DataField::ConstHook%3C614FDE0039.declarations

// Class DataField::Hook 

// Additional Declarations
  //## begin DataField::Hook%3C62A13101C9.declarations preserve=yes
  //## end DataField::Hook%3C62A13101C9.declarations

// Class DataField 

DataField::DataField (int flags)
  //## begin DataField::DataField%3C3D64DC016E.hasinit preserve=no
  //## end DataField::DataField%3C3D64DC016E.hasinit
  //## begin DataField::DataField%3C3D64DC016E.initialization preserve=yes
  : mytype(0),mysize(0),selected(False),writable((flags&DMI::WRITE)!=0)
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
    : BlockableObject(),mytype(0)
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
    : mytype(0),mysize(0),writable((flags&DMI::WRITE)!=0)
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
  FailWhen( valid(),"field is already initialized" );
  FailWhen( num<0,"illegal field size" );
  // if null type, then reset the field to uninit state
  if( !tid )
  {
    mytype = 0;
    mysize = 0;
    writable = True;
    return *this;
  }
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

const void * DataField::get (int n, TypeId& tid, bool& can_write, TypeId check_tid, bool must_write) const
{
  //## begin DataField::get%3C5FB272037E.body preserve=yes
  FailWhen( !valid(),"uninitialized DataField");
  tid = mytype;
  FailWhen( check_tid && check_tid != tid,"type mismatch (expected "+check_tid.toString()+")" ); 
  can_write = isWritable();
  FailWhen( must_write && !can_write,"r/w access violation" );
  
  checkIndex(n);
  if( mytype == Tpstring ) // string? return the string
  {
    strvec_modified |= can_write; // mark as modified
    return &strvec[n];
  }
  else if( binary_type )
  {
    // else return pointer to item
    return n*typesize + (char*)headerData();
  }
  else
  {
    if( must_write )
      return &resolveObject(n,True).dewr();
    else
      return &resolveObject(n,False).deref();
  }
  //## end DataField::get%3C5FB272037E.body
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

DataField & DataField::put (const ObjRef &obj, int n, int flags)
{
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
}

ObjRef DataField::remove (int n)
{
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
    headerSize() = mysize;
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

// provide standard methods for DataAccessors
DataField & DataField::attach_object (BlockableObject *obj,int flags,int n)
{
  // fail if uninitialized but indexed with >0
  dprintf(2)("attaching @%d: %s\n",n,obj->sdebug(2).c_str());
  FailWhen(n>0 && !valid(),"indexing into uninitialized DataField");
  if( n<0 )  // n<0 implies call from DataField context (rather than
  {          // Hook context), so assume 0 and do some extra checks
    n=0;
    FailWhen(size()>1,"can't assign scalar "+obj->objectType().toString()
                            +" to vector field" );
  }
  ObjRef &ref = prepareForPut( obj->objectType(),n,flags|DMI::AUTOEXTEND );
  ref.attach(obj,flags);
  return *this;
}

DataField::operator ObjRef ()
{
  FailWhen(!valid() || !size(),"uninitialized DataField");
  FailWhen(size()>1,"can't convert "+sdebug()+" to scalar ObjRef");
  FailWhen( !DynamicTypeManager::isRegistered(type()),
            "field does not contain a dynamic object");
  int flags = isWritable() ? DMI::PRESERVE_RW : DMI::READONLY;
  return resolveObject(0,True).copy(flags);
}

DataField::operator ObjRef () const
{
  FailWhen(!valid() || !size(),"uninitialized DataField");
  FailWhen(size()>1,"can't convert "+sdebug()+" to scalar ObjRef");
  FailWhen( !DynamicTypeManager::isRegistered(type()),
            "field does not contain a dynamic object");
  return resolveObject(0,False).copy(DMI::READONLY);
}

      // dereferences to a subrecord (throws exception if contents are not a DataRecord)

const DataRecord * DataField::getSubRecord( bool write,int n ) const
{
  FailWhen( !valid(),"uninitialized DataField" );
  FailWhen( mytype != TpDataRecord,"field does not contain a DataRecord" );
  checkIndex(n);
  // resolve object and downcast to DataRecord
  const DataRecord *rec = dynamic_cast<const DataRecord *>
            (&resolveObject(n,write).deref());
  Assert(rec);
  return rec;
}

// operator -> on a DataField accesses the contents as a record.
// It will either produce a DataRecord*, or throw an exception
// if the field does not contain one.
const DataRecord * DataField::operator -> () const
{
  FailWhen( mysize > 1,"unexpected '->' operator on vector field" );
  return getSubRecord(False,0);
}

DataRecord * DataField::operator -> ()
{
  FailWhen( mysize > 1,"unexpected '->' operator on vector field" );
  return const_cast<DataRecord*>( getSubRecord(True,0) );
}

// [ HIID ] on a DataField is the same as applying [] to a subrecord
// in the field, and is an error if the field does not contain a datarecord.
// So we just resolve the field to a subrecord via the '->' operator defined
// above, and call operator [] on that record.
DataField & DataField::operator [] ( const HIID &id )
{
  return (*this)->operator [](id);
}

const DataField & DataField::operator [] ( const HIID &id ) const
{
  return (*this)->operator [](id);
}

// -> and [HIID] on a Hook do similar things
const DataRecord * DataField::ConstHook::operator -> () const
{
  FailWhen1(addressed,"illegal use of '&' operator");
  return parent->getSubRecord(False,max(index,0));
}

const DataField & DataField::ConstHook::operator [] ( const HIID &id ) const
{
  return (*this)->operator [](id);
}

DataRecord * DataField::Hook::operator -> () const
{
  FailWhen1(addressed,"illegal use of '&' operator");
  return const_cast<DataRecord*>( parent->getSubRecord(True,max(index,0)) );
}

DataField & DataField::Hook::operator [] ( const HIID &id ) const
{
  return (*this)->operator [](id);
}
      
const void * DataField::put_scalar( const void *data,TypeId tid,int n )
{
  // fail if uninitialized but indexed with >0
  FailWhen(n>0 && !valid(),"indexing into uninitialized DataField");
  if( n<0 )  // n<0 implies call from DataField context (rather than
  {          // Hook context), so assume 0 and do some extra checks
    n=0;
    FailWhen(size()>1,"can't assign scalar "+tid.toString()
                            +" to vector field" );
  }
  // if field is uninitialized, init with single scalar
  if( !valid() )
  {
    init(tid,1,data);
    return get(0,0,False);
  }
  // auto-resize if putting at end of vector
  if( n == size() )
    resize(n+1);
  checkIndex(n);
  if( binary_type ) // binary type: convert or bitwise copy
  {
    const void *ptr = get(n,0,True);
    if( tid != mytype ) // convert [if allowed]...
      convertScalar(data,tid,const_cast<void*>(ptr),mytype);
    else // else just copy
      memcpy(const_cast<void*>(ptr),data,typesize);
    return ptr;
  }
  else if( mytype == Tpstring ) // string: special case
  {
    FailWhen( tid != Tpstring,"can't assign scalar "+tid.toString()+" to "+sdebug() );
    strvec[n] = * static_cast<const string*>(data);
    strvec_modified = True;
    return &strvec[n];
  }
  else
    Throw("can't assign "+tid.toString()+" to "+sdebug());
  return 0;
}


DataField::Hook::operator ObjRef () const
{
  FailWhen1(addressed,"illegal use of '&' operator");
  FailWhen1( !DynamicTypeManager::isRegistered(parent->type()),
            "field does not contain a dynamic object");
  int flags = parent->isWritable() ? DMI::PRESERVE_RW : DMI::READONLY;
  return parent->resolveObject(0,True).copy(flags);
}

DataField::ConstHook::operator ObjRef () const
{
  FailWhen1(addressed,"illegal use of '&' operator");
  FailWhen1( !DynamicTypeManager::isRegistered(parent->type()),
            "field does not contain a dynamic object");
  return parent->resolveObject(0,False).copy(DMI::READONLY);
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

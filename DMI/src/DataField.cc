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
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\DataField.cc

//## begin module%3C10CC820126.additionalIncludes preserve=no
//## end module%3C10CC820126.additionalIncludes

//## begin module%3C10CC820126.includes preserve=yes
#include "DynamicTypeManager.h"
#include "DataRecord.h"
#include "Packer.h"
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
    spvec(0),mytype(0),mysize(0),selected(False)
  //## end DataField::DataField%3C3D64DC016E.initialization
{
  //## begin DataField::DataField%3C3D64DC016E.body preserve=yes
  dprintf(2)("default constructor\n");
  spvec = 0;
  //## end DataField::DataField%3C3D64DC016E.body
}

DataField::DataField (const DataField &right, int flags, int depth)
  //## begin DataField::DataField%3C3EE3EA022A.hasinit preserve=no
  //## end DataField::DataField%3C3EE3EA022A.hasinit
  //## begin DataField::DataField%3C3EE3EA022A.initialization preserve=yes
    : NestableContainer(flags&DMI::WRITE!=0),
    spvec(0),mytype(0)
  //## end DataField::DataField%3C3EE3EA022A.initialization
{
  //## begin DataField::DataField%3C3EE3EA022A.body preserve=yes
  dprintf(2)("copy constructor (%s,%x)\n",right.debug(),flags);
  cloneOther(right,flags,depth);
  //## end DataField::DataField%3C3EE3EA022A.body
}

DataField::DataField (TypeId tid, int num, int flags)
  //## begin DataField::DataField%3BFA54540099.hasinit preserve=no
  //## end DataField::DataField%3BFA54540099.hasinit
  //## begin DataField::DataField%3BFA54540099.initialization preserve=yes
    : NestableContainer(flags&DMI::WRITE!=0),
      spvec(0),mytype(0),mysize(0),selected(False)
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
  if( &right != this )
  {
    dprintf(2)("assignment of %s\n",right.debug());
    FailWhen( valid(),"field is already initialized" );
    clear();
    cloneOther(right,0,0);
  }
  return *this;
  //## end DataField::operator=%3BB317D8010B_assign.body
}



//## Other Operations (implementation)
DataField & DataField::init (TypeId tid, int num, const void *data)
{
  //## begin DataField::init%3C6161190193.body preserve=yes
  //
  // NB: shared memory flags ought to be passed into the SmartBlock
  //
  
  dprintf(2)("init(%s,%d,%x)\n",tid.toString().c_str(),num,(int)data);
  // if null type, then reset the field to uninit state
  if( !tid )
  {
    clear();
    scalar = True;
    setWritable(True);
    return *this;
  }
  FailWhen( valid(),"field is already initialized" );
  if( num == -1 )
  {
    num = 1;
    scalar = True;
  }
  else
    scalar = False;
  FailWhen( num<0,"illegal field size" );
  // obtain type information, check that type is supported
  typeinfo = TypeInfo::find(tid);
  FailWhen( !typeinfo.category,"unknown data type "+tid.toString() );
  binary_type = dynamic_type = False;
  mytype = tid;
  mysize = max(num,1);
  typeinfo.size = typeinfo.size;
  switch( typeinfo.category )
  {
  // NUMERIC & BINARY type categories are treated as binary objects
  // of a fixed type, which can be bitwise-copied
    case TypeInfo::NUMERIC:
    case TypeInfo::BINARY:
    {  
        binary_type = True;
        // allocate header and copy data
        SmartBlock *header = new SmartBlock( sizeof(int)*2 + typeinfo.size*mysize);
        headref.attach(header,DMI::WRITE|DMI::ANON|DMI::LOCK);
        if( data )
          memcpy(sizeof(int)*2 + static_cast<char*>(header->data()),data,typeinfo.size*mysize);
        else
          memset(sizeof(int)*2 + static_cast<char*>(header->data()),0,typeinfo.size*mysize);
        break;
    }
    case TypeInfo::DYNAMIC: 
    {
        dynamic_type = True;
        FailWhen(data,Debug::ssprintf("can't init field of type %s with data",tid.toString().c_str(),num) );
        headref.attach( new SmartBlock( sizeof(int)*(2+mysize),DMI::ZERO ),
                        DMI::WRITE|DMI::ANON|DMI::LOCK );
        objects.resize(mysize);
        blocks.resize(mysize);
        objstate.resize(mysize);
        objstate.assign(mysize,UNINITIALIZED);
        break;
    }    
    case TypeInfo::SPECIAL: 
    {
        FailWhen(!typeinfo.fnew || !typeinfo.fdelete || !typeinfo.fcopy ||
            !typeinfo.fpack || !typeinfo.funpack || !typeinfo.fpacksize,
            "incomplete registry information for"+tid.toString() ); 
        headref.attach( new SmartBlock( sizeof(int)*(2+mysize) ),
                        DMI::WRITE|DMI::ANON|DMI::LOCK );
        // use the new function to allocate vector of objects
        spvec = (*typeinfo.fnew)(mysize);
        spdelete = typeinfo.fdelete;
        // if init data is supplied, use the copy function to init the vector
        if( data )
        {
          const char *from = static_cast<const char *>(data);
          char *to = static_cast<char *>(spvec);
          for( int i=0; i<mysize; i++,from+=typeinfo.size,to+=typeinfo.size )
            (*typeinfo.fcopy)(to,from);
        }
        spvec_modified = False;
        break;
    }
    default:
        Throw("unsupported data type "+tid.toString());  
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
  int minsize = min(mysize,newsize);
  mysize = newsize;
  if( newsize > 1 )
    scalar = False;
  if( binary_type )
    headref().resize( sizeof(int)*2 + typeinfo.size*newsize );
  else if( dynamic_type )
  {
    objects.resize(newsize);
    blocks.resize(newsize);
    objstate.resize(newsize);
    // note that when resizing upwards, this implicitly fills the empty
    // objstates with 0 = UNINITIALIZED
  }
  else  // special type -- resize & copy
  {
    void *newvec = (*typeinfo.fnew)(newsize);
    if( minsize )
    {
      const char *from = static_cast<char *>(spvec);
      char *to = static_cast<char *>(newvec);
      for( int i=0; i<minsize; i++,from+=typeinfo.size,to+=typeinfo.size )
        (*typeinfo.fcopy)(to,from);
    }
    (*typeinfo.fdelete)(spvec);
    spvec = newvec;
    spvec_modified = True;
  }
  mysize = newsize;
  //## end DataField::resize%3C62961D021B.body
}

void DataField::clear (int flags)
{
  //## begin DataField::clear%3C3EAB99018D.body preserve=yes
  if( spvec )
  {
    Assert(spdelete);
    (*spdelete)(spvec);
    spvec = 0;
  }
  if( valid() )
  {
    dprintf(2)("clearing\n");
    if( headref.valid() )
      headref.unlock().detach();
    if( objects.size() ) objects.resize(0);
    if( blocks.size() ) blocks.resize(0);
    objstate.resize(0);
    mytype = 0;
    selected = False;
    setWritable( (flags&DMI::WRITE)!=0 );
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
  clear(isWritable() ? DMI::WRITE : DMI::READONLY);
  int npopped = 1;
  // get header block, privatize & cache it as headref
  set.pop(headref.unlock());  
  size_t hsize = headref->size();
  // first two ints in header block are type and size
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
  typeinfo = TypeInfo::find(mytype);
  binary_type = dynamic_type = False;
  switch( typeinfo.category )
  {
    case TypeInfo::NUMERIC:
    case TypeInfo::BINARY:  // numeric/binary types are stored directly in the header
      binary_type = True;
      dprintf(2)("fromBlock: built-in type %s[%d]\n",mytype.toString().c_str(),mysize);
      FailWhen( hsize != sizeof(int)*2 + typeinfo.size*mysize,
                  "incorrect block size" );
      break;
    
    case TypeInfo::SPECIAL: // special types need to be unpacked from header
      FailWhen(!typeinfo.fnew || !typeinfo.fdelete || !typeinfo.fcopy ||
          !typeinfo.fpack || !typeinfo.funpack || !typeinfo.fpacksize,
          "incomplete registry information for"+mytype.toString() ); 
      int n;
      // use the unpack method to unpack the objects. Note that old spvec
      // has already been deleted by call to clear(), above.
      // funpack will allocate an array for us with new[n].
      spvec = (*typeinfo.funpack)(
                static_cast<const char*>(headref->data()) + sizeof(int)*2,
                hsize - sizeof(int)*2,n);
      spdelete = typeinfo.fdelete;
      FailWhen( n != mysize,"size mismatch after unpacking" );
      spvec_modified = False; 
      break;
        
    case TypeInfo::DYNAMIC: // dynamic type: header contains info on # of blocks to follow
      dynamic_type = True;
      dprintf(2)("fromBlock: dynamic type %s[%d]\n",mytype.toString().c_str(),mysize);
      FailWhen( hsize != sizeof(int)*(2 + mysize),"incorrect block size" );
      objects.resize(mysize);
      blocks.resize(mysize);
      objstate.resize(mysize);
      objstate.assign(mysize,INBLOCK);
      // Get blocks from set
      // Do not unblock objects, as that is done at dereference time
      // Note that we don't privatize the blocks, so field contents may
      // be shared and/or read-only
      for( int i=0; i<mysize; i++ ) 
      {
        npopped += headerBlockSize(i);
        if( headerBlockSize(i) )
        {
          dprintf(3)("fromBlock: [%d] taking over %d blocks\n",i,headerBlockSize(i));
          set.popMove(blocks[i],headerBlockSize(i));
          // dprintf(3)("fromBlock: [%d] will privatize %d blocks\n",i,blocks[i].size());
          //          blocks[i].privatizeAll(isWritable()?DMI::WRITE:0,True);
        }
        else // no blocks assigned to this object => is uninitialized
          objstate[i] = UNINITIALIZED;
      }
      dprintf(2)("fromBlock: %d blocks were popped\n",npopped);
      break;
        
    default:
        Throw("unsupported data type "+mytype.toString());  
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
  // if dealing with special types, and they have been modified, the 
  // header block needs to be rebuilt
  if( !dynamic_type && !binary_type && spvec_modified )
  {
    // allocate and attach header block
    size_t hsize = sizeof(int)*2 + 
            (*typeinfo.fpacksize)(spvec,mysize);
    headref.unlock().attach( new SmartBlock(hsize),
                    DMI::WRITE|DMI::ANON|DMI::LOCK );
    // write basic fields
    headerType() = mytype;
    headerSize() = scalar ? -mysize : mysize;
    hsize -= sizeof(int)*2;
    // pack object data into header block
    (*typeinfo.fpack)(spvec,mysize,
        static_cast<char*>(headref().data()) + sizeof(int)*2,hsize);
    spvec_modified = False;
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

ObjRef & DataField::resolveObject (int n, bool write, int autoprivatize) const
{
  //## begin DataField::resolveObject%3C3D8C07027F.body preserve=yes
  FailWhen(autoprivatize && !isWritable(),"can't autoprivatize in readonly field");
  FailWhen(write && autoprivatize&DMI::PRIVATIZE && autoprivatize&DMI::READONLY,
        "write access and unconditional read-only privatize requested at the same time" )
  switch( objstate[n] )
  {
    // uninitialized object - create default
    case UNINITIALIZED:
        dprintf(3)("resolveObject(%d): creating new %s\n",n,mytype.toString().c_str());
        objects[n].attach( DynamicTypeManager::construct(mytype),
                          (isWritable()?DMI::WRITE:DMI::READONLY)|
                          DMI::ANON|DMI::LOCK );
        objstate[n] = MODIFIED;
        // unconditionally privatize if so requested
        if( autoprivatize&DMI::PRIVATIZE )
          objects[n].privatize(autoprivatize&~DMI::PRIVATIZE); 
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
        // unconditionally privatize if so requested
        if( autoprivatize&DMI::PRIVATIZE )
          objects[n].privatize(autoprivatize&~DMI::PRIVATIZE); 
        return objects[n];

    // object exists (unblocked and maybe modified)
    case UNBLOCKED:
    case MODIFIED:
    {
        ObjRef &ref = objects[n];
        // unconditionally privatize if requested
        if( autoprivatize&DMI::PRIVATIZE )
          ref.privatize((autoprivatize&~DMI::PRIVATIZE)|(write?DMI::WRITE:0)); 
        // do we need to write to it?
        else if( write )
        {
          if( !ref.isWritable() ) // auto-privatize if required
          {
            FailWhen( !autoprivatize&DMI::WRITE,"write access violation" );
            ref.privatize(autoprivatize);
          }
          // flush cached blocks if any
          blocks[n].clear();
          objstate[n] = MODIFIED;
        }
        return ref;
    }
    
    default:
        Throw("unexpected object state");
  }
  //## end DataField::resolveObject%3C3D8C07027F.body
}

CountedRefTarget* DataField::clone (int flags, int depth) const
{
  //## begin DataField::clone%3C3EC77D02B1.body preserve=yes
  return new DataField(*this,flags,depth);
  //## end DataField::clone%3C3EC77D02B1.body
}

void DataField::cloneOther (const DataField &other, int flags, int depth)
{
  //## begin DataField::cloneOther%3C3EE42D0136.body preserve=yes
  // setup misc fields
  FailWhen( valid(),"field is already initialized" );
  mytype = other.type();
  mysize = other.size();
  binary_type = other.binary_type;
  dynamic_type = other.dynamic_type;
  typeinfo = other.typeinfo;
  setWritable( (flags&DMI::WRITE)!=0 );
  selected = False;
  // copy & privatize the header ref
  headref.copy(other.headref).privatize(flags|DMI::LOCK);
  if( dynamic_type )   // handle dynamic types
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
            if( flags&DMI::DEEP || depth>0 )
              blocks[i].privatizeAll(flags);
            break;
        // otherwise, privatize the object reference
        case UNBLOCKED:
        case MODIFIED:
  // For ref.copy(), clear the DMI::WRITE flag and use DMI::PRESERVE_RW instead.
  // (When depth>0, DMI::WRITE will take effect anyways via privatize().
  //  When depth=0, we must preserve the write permissions of the contents.)
            objects[i].copy(other.objects[i],
                    (flags&~DMI::WRITE)|DMI::PRESERVE_RW|DMI::LOCK);
            if( flags&DMI::DEEP || depth>0 );
              objects[i].privatize(flags|DMI::LOCK,depth-1);
            break;
        default:
            Throw("illegal object state");
      }
    }
  }
  // handle special types -- need to be copied
  else if( !binary_type )
  {
    if( spvec )
      (*spdelete)(spvec);
    spvec = (*typeinfo.fnew)(mysize);
    spdelete = typeinfo.fdelete;
    if( mysize )
    {
      const char *from = static_cast<char *>(other.spvec);
      char *to = static_cast<char *>(spvec);
      for( int i=0; i<mysize; i++,from+=typeinfo.size,to+=typeinfo.size )
        (*typeinfo.fcopy)(to,from);
    }
    spvec_modified = other.spvec_modified;
  }
  // for binary types, do nothing since they're already in the header block
  //## end DataField::cloneOther%3C3EE42D0136.body
}

void DataField::privatize (int flags, int depth)
{
  //## begin DataField::privatize%3C3EDEBC0255.body preserve=yes
  setWritable( (flags&DMI::WRITE)!=0 );
  if( !valid() )
    return;
  // privatize the header reference
  headref.privatize(DMI::WRITE|DMI::LOCK);
  // if deep privatization is required, then for dynamic objects, 
  // privatize the field contents as well
  if( dynamic_type && ( flags&DMI::DEEP || depth>0 ) )
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
            objects[i].privatize(flags|DMI::LOCK,depth-1);
            break;
        default:
            Throw("illegal object state");
      }
    }
  }
  //## end DataField::privatize%3C3EDEBC0255.body
}

const void * DataField::get (const HIID &id, TypeId& tid, bool& can_write, TypeId check_tid, bool must_write, int autoprivatize) const
{
  //## begin DataField::get%3C7A19790361.body preserve=yes
  // null HIID implies access to first element
  if( !id.size() )
    return getn(0,tid,can_write,check_tid,must_write);
  // single-index HIID implies get[n]
  if( id.size()==1 && id.front().index()>=0 )
    return getn(id.front().index(),tid,can_write,check_tid,must_write,autoprivatize);
  FailWhen( !valid(),"field not initialized" );
  FailWhen( !size(),"uninitialized DataField" );
  FailWhen( !isNestable(type()),"contents not a container" );
  FailWhen( !scalar,"non-scalar field, explicit index expected" );
  // resolve to pointer to container
  const NestableContainer *nc = dynamic_cast<const NestableContainer *>
      (&resolveObject(0,must_write,autoprivatize).deref());
  Assert(nc);
  // defer to get[id] on container
  return nc->get(id,tid,can_write,check_tid,must_write,autoprivatize);
  //## end DataField::get%3C7A19790361.body
}

const void * DataField::getn (int n, TypeId& tid, bool& can_write, TypeId check_tid, bool must_write, int autoprivatize) const
{
  //## begin DataField::getn%3C7A1983024D.body preserve=yes
  FailWhen( !valid(),"field not initialized" );
  FailWhen( n<0 || n>size(),"n out of range" );
  if( n == size() )
    return 0;
  can_write = isWritable();
  FailWhen(must_write && !can_write,"write access violation"); 
  if( binary_type ) // binary type
  {
    // types must match, or TpNumeric can match any numeric type
    FailWhen( check_tid && check_tid != type() &&
              (check_tid != TpNumeric || !TypeInfo::isNumeric(type())),
        "type mismatch: expecting "+check_tid.toString()+", got "+type().toString());
    tid = type();
    return n*typeinfo.size + (char*)headerData();
  }
  else if( dynamic_type )
  {
    if( !check_tid || check_tid == TpObjRef ) // default is to return a reference
    {
      tid = TpObjRef;
      return &resolveObject(n,must_write,autoprivatize);
    }
    else // else types must match, or TpObject can be specified as 
    {    //    a special case that forces dereferencing
      FailWhen( check_tid != type() && check_tid != TpObject,
          "type mismatch: expecting "+check_tid.toString()+", got "+type().toString());
      tid = type();
      return &resolveObject(n,must_write,autoprivatize).deref();
    }
  }
  else   // special type -- types must match
  {
    FailWhen( check_tid && check_tid != type(),
        "type mismatch: expecting "+type().toString()+" got "+check_tid.toString());
    tid = type();
    if( must_write )
      spvec_modified = True;
    return static_cast<char*const>(spvec) + n*typeinfo.size;
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
  if( binary_type )
  {
    FailWhen( tid && tid!=type() && 
              (!TypeInfo::isNumeric(tid) || !TypeInfo::isNumeric(type())),
        "can't insert "+tid.toString());
    return n*typeinfo.size + (char*)headerData();
  }
  else if( dynamic_type )
  {
    FailWhen(tid && tid!=type(),"can't insert "+tid.toString());
    return &resolveObject(n,True);
  }
  else // special type
  {
    FailWhen( tid && tid != type(),"can't insert "+tid.toString()+" into field of type "+type().toString());
    spvec_modified = True;
    return static_cast<char*>(spvec) + n*typeinfo.size;
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
    if( !n )
      init(tid,1);   // empty field auto-extended to 1
    else
      Throw("uninitialized DataField");
  }
  else
  {
    FailWhen( tid != mytype, "type mismatch in put("+tid.toString()+")" );
    if( n == size() )
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
//     vec_modified |= can_write; // mark as modified
//     return &strvec[n];
//   }
//   else if( binary_type )
//   {
//     // else return pointer to item
//     return n*typeinfo.size + (char*)headerData();
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

//  DataField.cc: DataField implementation
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#define NC_SKIP_HOOKS 1
#include "DataField.h"
#include "DynamicTypeManager.h"
#include "Packer.h"

static int nullheader_data[] = {0,0};
static SmartBlock nullheader_block( nullheader_data,sizeof(nullheader_data),DMI::NO_DELETE );
static BlockRef nullheader(nullheader_block,DMI::EXTERNAL|DMI::LOCK|DMI::READONLY);
static ObjRef NullRef;
static NestableContainer::Register reg(TpDataField,True);

//##ModelId=3C3D64DC016E
DataField::DataField (int flags)
  : spvec(0),mytype(0),mysize_(0),selected(False)
{
  dprintf(2)("default constructor\n");
  spvec = 0;
}

//##ModelId=3C3EE3EA022A
DataField::DataField (const DataField &right, int flags, int depth)
    : NestableContainer(),spvec(0),mytype(0)
{
  dprintf(2)("copy constructor (%s,%x)\n",right.debug(),flags);
  cloneOther(right,flags,depth);
}

//##ModelId=3BFA54540099
DataField::DataField (TypeId tid, int num, int flags, const void *data)
    : spvec(0),mytype(0),mysize_(0),selected(False)
{
  dprintf(2)("constructor(%s,%d,%x)\n",tid.toString().c_str(),num,flags);
  init(tid,num,data);
}

//##ModelId=3DB9346F0095
DataField::~DataField()
{
  dprintf(2)("destructor\n");
  clear();
}

//##ModelId=3DB9346F017B
DataField & DataField::operator=(const DataField &right)
{
  if( &right != this )
  {
    Thread::Mutex::Lock _nclock(mutex());
    dprintf(2)("assignment of %s\n",right.debug());
// removed for now since it seems like a useless limitation
// OMS 01/10/03
//    FailWhen( valid(),"field is already initialized" );
    clear();
    if( right.valid() )
      cloneOther(right,0,0);
  }
  return *this;
}



//##ModelId=3C6161190193
DataField & DataField::init (TypeId tid, int num, const void *data)
{
  //
  // NB: shared memory flags ought to be passed into the SmartBlock
  //
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("init(%s,%d,%x)\n",tid.toString().c_str(),num,(int)data);
  // if null type, then reset the field to uninit state
  if( !tid )
  {
    clear();
    scalar = True;
    return *this;
  }
  bool wantscalar = False;
  if( num == -1 )
  {
    num = 1;
    wantscalar = True;
  }
  // already initialized? 
  if( valid () )
  {
    // Check that type/size matches
    FailWhen(mytype!=tid || mysize_!=num || wantscalar!=scalar,"field already initialized" );
    // do nothing...
    if( !data )
      return *this;
    // .. unless new contents are specified, in which case clear & reinitialize
    clear();
  }
  FailWhen( num<0,"illegal field size" );
  // obtain type information, check that type is supported
  typeinfo = TypeInfo::find(tid);
  FailWhen( !typeinfo.category,"unknown data type "+tid.toString() );
  binary_type = dynamic_type = container_type = False;
  mytype = tid;
  mysize_ = max(num,1);
  scalar = wantscalar;
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
        SmartBlock *header = new SmartBlock( sizeof(int)*2 + typeinfo.size*mysize_);
        headref.attach(header,DMI::WRITE|DMI::ANON|DMI::LOCK);
        if( data )
          memcpy(sizeof(int)*2 + static_cast<char*>(header->data()),data,typeinfo.size*mysize_);
        else
          memset(sizeof(int)*2 + static_cast<char*>(header->data()),0,typeinfo.size*mysize_);
        break;
    }
    case TypeInfo::DYNAMIC: 
    {
        dynamic_type = True;
        container_type = isNestable(tid);
        FailWhen(data,Debug::ssprintf("can't init field of type %s with data",tid.toString().c_str(),num) );
        headref.attach( new SmartBlock( sizeof(int)*(2+mysize_),DMI::ZERO ),
                        DMI::WRITE|DMI::ANON|DMI::LOCK );
        objects.resize(mysize_);
        blocks.resize(mysize_);
        objstate.resize(mysize_);
        objstate.assign(mysize_,UNINITIALIZED);
        break;
    }    
    case TypeInfo::SPECIAL: 
    {
        FailWhen(!typeinfo.fnew || !typeinfo.fdelete || !typeinfo.fcopy ||
            !typeinfo.fpack || !typeinfo.funpack || !typeinfo.fpacksize,
            "incomplete registry information for"+tid.toString() ); 
        headref.attach( new SmartBlock( sizeof(int)*(2+mysize_) ),
                        DMI::WRITE|DMI::ANON|DMI::LOCK );
        // use the new function to allocate vector of objects
        spvec = (*typeinfo.fnew)(mysize_);
        spdelete = typeinfo.fdelete;
        // if init data is supplied, use the copy function to init the vector
        if( data )
        {
          const char *from = static_cast<const char *>(data);
          char *to = static_cast<char *>(spvec);
          for( int i=0; i<mysize_; i++,from+=typeinfo.size,to+=typeinfo.size )
            (*typeinfo.fcopy)(to,from);
        }
        spvec_modified = True;
        break;
    }
    default:
        Throw("unsupported data type "+tid.toString());  
  }

  headerType() = mytype;
  headerSize() = mysize_;
  return *this;
}

//##ModelId=3C62961D021B
void DataField::resize (int newsize)
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen( newsize<=0,"can't resize to <=0" );
  FailWhen( !valid(),"uninitialized DataField" );
  int minsize = min(mysize_,newsize);
  if( newsize > 1 )
    scalar = False;
  if( binary_type )
    headref().resize( sizeof(int)*2 + typeinfo.size*newsize );
  else if( dynamic_type )
  {
    // this is horribly inefficient, but we really must keep the object
    // references locked. Hence, unlock first...
    if( newsize>mysize_ )
      for( vector<ObjRef>::iterator iter = objects.begin(); iter != objects.end(); iter++ )
        iter->unlock();
    // resize (since this involves a ref assignment)
    objects.resize(newsize);
    // relock
    if( newsize>mysize_ )
      for( vector<ObjRef>::iterator iter = objects.begin(); iter != objects.end(); iter++ )
        iter->lock();
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
  mysize_ = newsize;
}

//##ModelId=3C3EAB99018D
void DataField::clear ()
{
  Thread::Mutex::Lock _nclock(mutex());
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
  }
}

//##ModelId=3C3EB9B902DF
bool DataField::isValid (int n)
{
  Thread::Mutex::Lock _nclock(mutex());
  if( !valid() )
    return False;
  checkIndex(n);
  if( dynamic_type ) 
    return objstate[n] != UNINITIALIZED;
  else
    return True; // built-ins always valid
}

//##ModelId=3C0E4619019A
ObjRef DataField::objwr (int n, int flags)
{
  // set a write-lock regardless because we're going to be manipulating
  // counte
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen( !valid(),"uninitialized DataField");
  checkIndex(n);
  if( !dynamic_type )
    return NullRef;
  return resolveObject(n,DMI::WRITE).copy(flags);
}

//##ModelId=3C7A305F0071
DataField & DataField::put (int n, ObjRef &ref, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("putting @%d: %s\n",n,ref.debug(2));
  ObjRef &ref2 = prepareForPut( ref->objectType(),n );
  // grab the ref, and mark object as modified
  if( flags&DMI::COPYREF )
    ref2.copy(ref,flags);
  else
    ref2 = ref;
  return *this;
}

//##ModelId=400E4D6803D9
DataField & DataField::put (int n, BlockableObject* obj, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("putting @%d: %s\n",n,obj->debug(2));
  prepareForPut( obj->objectType(),n ).unlock().attach(obj,flags).lock();
  return *this;
}


//##ModelId=3C3C8D7F03D8
ObjRef DataField::objref (int n) const
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen( !valid(),"uninitialized DataField");
  checkIndex(n);
  if( !dynamic_type )
    return NullRef;
  // return a copy as a read-only ref
  return resolveObject(n,DMI::READONLY).copy(DMI::READONLY);
}

//##ModelId=3C3D5F2001DC
int DataField::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf1(2)("%s: fromBlock\n",debug());
  clear();
  int npopped = 1;
  // get header block, privatize & cache it as headref
  set.pop(headref.unlock());  
  size_t hsize = headref->size();
  // first two ints in header block are type and size
  FailWhen( hsize < sizeof(int)*2,"malformed header block" );
  headref.privatize(DMI::WRITE|DMI::LOCK);
  // get type and size from header
  mytype = headerType();
  mysize_ = headerSize();
  if( mysize_ == -1 )
  {
    mysize_ = 1;
    scalar = True;
  }
  else
    scalar = False;
  if( !mytype )  // uninitialized field
    return 1;
  // obtain type information, check that type is supported
  typeinfo = TypeInfo::find(mytype);
  binary_type = dynamic_type = container_type = False;
  switch( typeinfo.category )
  {
    case TypeInfo::NUMERIC:
    case TypeInfo::BINARY:  // numeric/binary types are stored directly in the header
      binary_type = True;
      dprintf(2)("fromBlock: built-in type %s[%d]\n",mytype.toString().c_str(),mysize_);
      FailWhen( hsize != sizeof(int)*2 + typeinfo.size*mysize_,
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
      FailWhen( n != mysize_,"size mismatch after unpacking" );
      spvec_modified = False; 
      break;
        
    case TypeInfo::DYNAMIC: // dynamic type: header contains info on # of blocks to follow
      dynamic_type = True;
      container_type = isNestable(mytype);
      dprintf(2)("fromBlock: dynamic type %s[%d]\n",mytype.toString().c_str(),mysize_);
      FailWhen( hsize != sizeof(int)*(2 + mysize_),"incorrect block size" );
      objects.resize(mysize_);
      blocks.resize(mysize_);
      objstate.resize(mysize_);
      objstate.assign(mysize_,INBLOCK);
      // Get blocks from set
      // Do not unblock objects, as that is done at dereference time
      // Note that we don't privatize the blocks, so field contents may
      // be shared and/or read-only
      for( int i=0; i<mysize_; i++ ) 
      {
        npopped += headerBlockSize(i);
        if( headerBlockSize(i) )
        {
          dprintf(3)("fromBlock: [%d] taking over %d blocks\n",i,headerBlockSize(i));
          set.popMove(blocks[i],headerBlockSize(i));
        }
        else // no blocks assigned to this object => is uninitialized
          objstate[i] = UNINITIALIZED;
      }
      dprintf(2)("fromBlock: %d blocks were popped\n",npopped);
      break;
        
    default:
        Throw("unsupported data type "+mytype.toString());  
  }
  validateContent();
  return npopped;
}

//##ModelId=3C3D5F2403CC
int DataField::toBlock (BlockSet &set) const
{
  // write-lock, since we modify internal fields
  Thread::Mutex::Lock _nclock(mutex());
  if( !valid() )
  {
    dprintf1(2)("%s: toBlock=1 (field empty)\n",debug());
    // for empty fields, use null block of two integers to represent them
    static SmartBlock nullBlock(sizeof(int)*2,DMI::ZERO);
    set.push(BlockRef(&nullBlock,DMI::EXTERNAL|DMI::READONLY));
    return 1;
  }
  dprintf1(2)("%s: toBlock\n",debug());
  int npushed = 1,tmp; // 1 header block as a minimum
  // if dealing with special types, and they have been modified, the 
  // header block needs to be rebuilt
  if( !dynamic_type && !binary_type && spvec_modified )
  {
    // allocate and attach header block
    size_t hsize = sizeof(int)*2 + 
            (*typeinfo.fpacksize)(spvec,mysize_);
    headref.unlock().attach( new SmartBlock(hsize),
                    DMI::WRITE|DMI::ANON|DMI::LOCK );
    // write basic fields
    headerType() = mytype;
    headerSize() = scalar ? -mysize_ : mysize_;
    hsize -= sizeof(int)*2;
    // pack object data into header block
    (*typeinfo.fpack)(spvec,mysize_,
        static_cast<char*>(headref().data()) + sizeof(int)*2,hsize);
    spvec_modified = False;
  }
  // for dynamic types, check that the header block is still consistent
  if( dynamic_type )
  {
    size_t hsize = sizeof(int)*(2+mysize_);
    if( !headref.valid() || headref->size() != hsize )
      headref.unlock().attach(new SmartBlock(hsize,DMI::ZERO),DMI::ANONWR|DMI::LOCK);
  }
  // fill and push out header block
  headerType() = mytype;
  headerSize() = scalar ? -mysize_ : mysize_;
  set.push(headref.copy(DMI::READONLY));
  // for dynamic types, do a toBlock on the objects, if needed
  if( dynamic_type )
  {
    for( int i=0; i<mysize_; i++ )
    {
      if( !objects[i].valid() )
        objstate[i] = UNINITIALIZED;
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
}

//##ModelId=3C3D8C07027F
ObjRef & DataField::resolveObject (int n, int flags) const
{
  Thread::Mutex::Lock _nclock(mutex());
  switch( objstate[n] )
  {
    // uninitialized object - create default
    case UNINITIALIZED:
    {
        dprintf(3)("resolveObject(%d): creating new %s\n",n,mytype.toString().c_str());
        objects[n].attach( DynamicTypeManager::construct(mytype),
                           (flags&DMI::WRITE)|DMI::ANON|DMI::LOCK);
        objstate[n] = MODIFIED;
        // ignore autoprivatize since this is a new object
        return objects[n];
    }
    // object hasn't been unblocked
    case INBLOCK:
    {
        // if write access requested, simply unblock it
        if( flags&DMI::WRITE )
        {
          dprintf(3)("resolveObject(%d): unblocking %s\n",n,mytype.toString().c_str());
          objects[n].attach( DynamicTypeManager::construct(mytype,blocks[n]),
                            DMI::ANONWR|DMI::LOCK );
          // verify that no blocks were left over
          FailWhen( blocks[n].size()>0,"block count mismatch" );
          objstate[n] = MODIFIED;
        }
        // For r/o access, we want to cache a copy of the blockset.
        // This is in case the object doesn't get modified down the road, 
        // so we can just re-use the blockset in a future toBlock()
        else
        {
          // make copy, retaining r/w privileges, and marking the source as r/o
          dprintf(3)("resolveObject(%d): read access, preserving old blocks\n",n);
          BlockSet set( blocks[n],DMI::PRESERVE_RW|DMI::MAKE_READONLY ); 
          // create object and attach a reference
          dprintf(3)("resolveObject(%d): unblocking %s\n",n,mytype.toString().c_str());
          objects[n].attach(DynamicTypeManager::construct(mytype,set),
                            DMI::READONLY|DMI::ANON|DMI::LOCK);
          // verify that no blocks were left over
          FailWhen( set.size()>0,"block count mismatch" );
          // mark object as unblocked but not modified 
          objstate[n] = UNBLOCKED; 
        }
        // privatize if so requested
        if( flags&DMI::PRIVATIZE )
          objects[n].privatize(flags&(DMI::READONLY|DMI::WRITE|DMI::DEEP)); 
        return objects[n];
      }
    // object exists (unblocked and maybe modified)
    case UNBLOCKED:
    case MODIFIED:
    {
        ObjRef &ref = objects[n];
        // not valid? Mark as uninitialized and try again
        if( !ref.valid() )
        {
          objstate[n] = UNINITIALIZED;
          return resolveObject(n,flags);
        }
        // privatize if requested
        if( flags&DMI::PRIVATIZE )
          ref.privatize(flags&(DMI::READONLY|DMI::WRITE|DMI::DEEP)); 
        // do we need to write to it?
        else if( flags&DMI::WRITE )
        {
          if( !ref.isWritable() )
            ref.privatize(DMI::WRITE);
          blocks[n].clear();
          objstate[n] = MODIFIED;
        }
        return ref;
    }
    default:
        Throw("unexpected object state");
  }
}

//##ModelId=3C3EC77D02B1
CountedRefTarget* DataField::clone (int flags, int depth) const
{
  return new DataField(*this,flags,depth);
}

//##ModelId=3C3EE42D0136
void DataField::cloneOther (const DataField &other, int flags, int depth)
{
  Thread::Mutex::Lock _nclock(mutex());
  Thread::Mutex::Lock _nclock1(other.mutex());
  // setup misc fields
  FailWhen( valid(),"field is already initialized" );
  if( !other.valid() )
    return;
  mytype = other.type();
  mysize_ = other.mysize();
  scalar = other.scalar;
  binary_type = other.binary_type;
  dynamic_type = other.dynamic_type;
  container_type = other.container_type;
  typeinfo = other.typeinfo;
  selected = False;
  // copy & privatize the header ref
  headref.copy(other.headref).privatize(DMI::WRITE|DMI::LOCK);
  if( dynamic_type )   // handle dynamic types
  {
    objstate = other.objstate;
    objects.clear();
    objects.resize(mysize_);
    blocks.clear();
    blocks.resize(mysize_);
    for( int i=0; i<mysize_; i++ )
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
    spvec = (*typeinfo.fnew)(mysize_);
    spdelete = typeinfo.fdelete;
    if( mysize_ )
    {
      const char *from = static_cast<char *>(other.spvec);
      char *to = static_cast<char *>(spvec);
      for( int i=0; i<mysize_; i++,from+=typeinfo.size,to+=typeinfo.size )
        (*typeinfo.fcopy)(to,from);
    }
    spvec_modified = other.spvec_modified;
  }
  validateContent();
  // for binary types, do nothing since they're already in the header block
}

//##ModelId=3C3EDEBC0255
void DataField::privatize (int flags, int depth)
{
  Thread::Mutex::Lock _nclock(mutex());
  if( !valid() )
    return;
  // privatize the header reference (always writable)
  headref.privatize(DMI::WRITE|DMI::LOCK);
  // if deep privatization is required, then for dynamic objects, 
  // privatize the field contents as well
  if( dynamic_type && ( flags&DMI::DEEP || depth>0 ) )
  {
    for( int i=0; i<mysize_; i++ )
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
  // revalidate content if necessary
  validateContent();
}

//##ModelId=3D05E2F301D2
int DataField::size (TypeId tid) const
{
  Thread::Mutex::Lock _nclock(mutex());
  // if types do not match (or tid=0), and we're scalar, and have
  // a subcontainer, then defer to its size()
  if( tid != mytype && scalar && mysize() == 1 && container_type )
  {
    const NestableContainer *nc = dynamic_cast<const NestableContainer *>
      (resolveObject(0,0).deref_p());
    Assert(nc);
    return nc->size(tid);
  }
  // else return our own size
  if( !tid || tid == mytype ||
      ( tid == TpObjRef && dynamic_type ) || 
      ( TypeInfo::isNumeric(tid) && TypeInfo::isNumeric(mytype) ) )
    return mysize();
  return -1;
}

    // from old get():
//   // other types of HIID are supported only when we contain a single, scalar
//   // container. 
//   Thread::Mutex::Lock _nclock(mutex());
//   FailWhen( !valid() || !mysize(),"field not initialized" );
//   FailWhen( !scalar,"non-scalar field, explicit numeric subscript expected" );
//   FailWhen( !isNestable(type()),"contents not a container" );
//   // Resolve to pointer to container
//   // Unless privatize is required, we resolve the container without the
//   // DMI::WRITE flag, since it's only the writability of its contents that
//   // matters -- nc->get() below will check that.
//   int contflags = flags&DMI::PRIVATIZE ? flags : flags &= ~DMI::WRITE;
//   const NestableContainer *nc = dynamic_cast<const NestableContainer *>
//       (&resolveObject(0,contflags).deref());
//   Assert(nc);
//   // defer to get[id] on container 
//   return nc->get(id,info,check_tid,flags);

//##ModelId=3C7A19790361
int DataField::get (const HIID &id,ContentInfo &info,bool nonconst,int flags) const
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen( !valid(),"field not initialized" );
  int n;  // number of item being accessed
  // null HIID implies scalar-mode access -- map to getn(0)
  if( id.empty() )
  {
    n = 0;
    info.size = mysize();
  }
  // numeric (single-index) HIID implies item #n
  else if( id.size() == 1 && id.front().index() >= 0 )
  {
    n = id.front().index();
    info.size = 1;
  }
  else
  { // transparent lookup into field contents, maybe time to phase it out?
  // disable this for now -- use [0][id] rathern than [id] to explicitly 
  // index into contents. I can re-enable it later if it becomes a problem.
  // see commented section above
    Throw("transparent indexing into scalar DataFields is no longer supported. "
          "See DataField::get()" );
  }
  FailWhen( n<0 || n>mysize(),"index "+id.toString()+"is out of range" );
  if( n == mysize() ) // can insert at end
    return 0;
  info.writable = nonconst;
  bool nowrite = flags&DMI::WRITE && !nonconst; // write requested but not avail?
  // handle case of dynamic types 
  if( dynamic_type )
  {
    // since dynamic objects are non-contiguous, prohibit vector access
    FailWhen(info.size>1,"DataField of "+type().toString()+"s can't be accessed in vector mode");
    // if not asking for object itself, then writability is equivalent to
    // non-constness
    if( !(flags&DMI::NC_DEREFERENCE) && nowrite )
      return -1;
    // object hasn't been initialized? Implicitly initialize if requested
    // for writing
    if( objstate[n] == UNINITIALIZED )
    {
//      if( !(flags&DMI::WRITE) )   // only reading requested? return 0
//        return 0;
      if( nowrite )               // can't init object if not writable
        return -1;
      // if we're not going to assign to the object, then we need to
      // init an empty one -- resolveObject() will do that for us
      if( !(flags&DMI::NC_ASSIGN) )  
        resolveObject(n,flags&DMI::WRITE);
    }
    // object hasn't been unblocked yet? Then we need to unblock it first
    // DMI::WRITE will ensure that object is attached for writing as needed.
    else if( objstate[n] == INBLOCK )
      resolveObject(n,flags&DMI::WRITE);
    // else check ref writability, if caller needs access to the object itself
    else if( flags&DMI::NC_DEREFERENCE && nowrite && 
             objects[n].valid() && !objects[n].isWritable() )
    {
      return -1;
    }
    // return ref to object; mark it as modified if expected to write
    if( flags&DMI::WRITE )
    {
      blocks[n].clear();
      objstate[n] = MODIFIED;
    }
    info.tid = TpObjRef;
    info.obj_tid = type();
    info.ptr = &objects[n];
  }
  else // binary or special type
  {
    // writability determined by non-constness
    if( flags&DMI::WRITE && !nonconst ) 
      return -1;
    info.tid = info.obj_tid = type();
    if( binary_type ) // binary type: data in header block
    {
      info.ptr = static_cast<const char*>(headerData()) + n*typeinfo.size;
    }
    else        // special type: data in separate spvec
    {
      if( flags&DMI::WRITE )
        spvec_modified = True;
      info.ptr = static_cast<const char*>(spvec) + n*typeinfo.size;
    }
  }
  // got here? success
  return 1; 
}
    // from old insert():
    //     FailWhen( !valid() || !mysize(),"field not initialized or empty" );
    //     FailWhen( !scalar,"non-scalar field, explicit index expected" );
    //     FailWhen( !isNestable(type()),"contents not a container" );
    //     // resolve to pointer to container
    //     dprintf(2)("insert: deferring to child %s\n",type().toString().c_str());
    //     NestableContainer *nc = dynamic_cast<NestableContainer *>
    //         (&resolveObject(0,True).dewr());
    //     Assert(nc);
    //     // defer to insert[id] on container
    //     return nc->insert(id,tid,real_tid);

//##ModelId=3C7A198A0347
int DataField::insert (const HIID &id,ContentInfo &info)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("insert(%s,%s)\n",id.toString().c_str(),info.tid.toString().c_str());
  int n;
  // determine index
  if( id.empty() )
  {
    FailWhen(valid(),"null HIID" );
    n = 0;
  }
  else if( id.size()==1 && id.front().index()>=0 )
    n = id.front().index();
  else
  {
  // disable this for now -- use [0][id] rathern than [id] to explicitly 
  // index into contents. I can re-enable it later if it becomes a problem.
  // see commented section above
    Throw("transparent indexing into scalar DataFields is no longer supported. "
          "See DataField::get()" );
  }
  // check types
  // insert item
  TypeId real_tid = info.tid = info.obj_tid;
  info.size = 1;
  info.writable = True;
  if( !valid() ) // empty field? must insert at #0
  {
    FailWhen(n,Debug::ssprintf("can't insert at [%d]",n));
    FailWhen(!real_tid,"can't initialize DataField without type");
    init(real_tid,-1); // init as scalar field
  }
  else // else extend field, but only if inserting at end
  {
    FailWhen(n != mysize(),Debug::ssprintf("can't insert at [%d]",n) );
    if( real_tid )
    {
      FailWhen(type()!=real_tid && !TypeInfo::isConvertible(real_tid,type()),
            "inserting "+real_tid.toString()+" into a DataField of "+type().toString());
    }
    info.tid = info.obj_tid = type();
    resize( mysize()+1 );
  }
  if( binary_type )
  {
    info.ptr = static_cast<char*>(headerData()) + n*typeinfo.size;
  }
  else if( dynamic_type )
  {
    info.tid = TpObjRef;
    objstate[n] = MODIFIED;
    info.ptr = &objects[n];
  }
  else // special type
  {
    spvec_modified = True;
    info.ptr = static_cast<char*>(spvec) + n*typeinfo.size;
  }
  return 1;
}

//##ModelId=3C877E1E03BE
int DataField::remove (const HIID &id)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("remove(%s)\n",id.toString().c_str());
  FailWhen(id.empty(),"null HIID");
  if( id.size()==1 && id.front().index()>=0 )
  {
    int n = id.front().index();
    Thread::Mutex::Lock _nclock(mutex());
    dprintf(2)("removen(%d)\n",n);
    FailWhen( !valid() || !mysize(),"field not initialized or empty" );
    FailWhen( n != mysize()-1,"can only remove from end of field" );
    dprintf(2)("removen: resizing to %d elements\n",n);
    resize(n);
    return 1;
  }
  else
  {
  // disable this for now -- use [0][id] rathern than [id] to explicitly 
  // index into contents. I can re-enable it later if it becomes a problem.
    Throw("transparent indexing into scalar DataFields is no longer supported. "
          "See DataField::get()" );
//     FailWhen( !valid() || !mysize(),"field not initialized or empty" );
//     FailWhen( !scalar,"non-scalar field, explicit index expected" );
//     FailWhen( !isNestable(type()),"contents not a container" );
//     // resolve to pointer to container
//     dprintf(2)("remove: deferring to child %s\n",type().toString().c_str());
//     NestableContainer *nc = dynamic_cast<NestableContainer *>
//         (&resolveObject(0,True).dewr());
//     Assert(nc);
//     // defer to remove(id) on container
//     return nc->remove(id);
  }
}

//##ModelId=3DB9347800CF
ObjRef & DataField::prepareForPut (TypeId tid,int n ) 
{
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
    if( n == mysize() )
      resize(n+1);  // auto-resize if inserting at last+1
    else
      checkIndex(n);
  }
  // grab the ref, and mark object as modified
  blocks[n].clear();
  objstate[n] = MODIFIED;
  return objects[n];
}

//##ModelId=3DB934730394
string DataField::sdebug ( int detail,const string &prefix,const char *name ) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  static int nesting=0;
  if( nesting++>1000 )
  {
    cerr<<"Too many nested DataField::sdebug() calls";
    abort();
  }
  Thread::Mutex::Lock _nclock(mutex());
  string out;
  if( detail>=0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:objectType().toString().c_str(),(int)this);
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    if( !type() )
      append(out,"empty");
    else
      appendf(out,"%s:%d",type().toString().c_str(),mysize());
    append(out,"/ refs",CountedRefTarget::sdebug(-1));
  }
  if( detail >= 2 || detail <= -2 )   // high detail
  {
    // append debug info from CountedRefTarget
    string str = CountedRefTarget::sdebug(-2,prefix+"      ");
    if( str.length() )
      out += "\n"+prefix+"  refs: "+str;
  }
  if( mysize()>0 && dynamic_type && (detail >= 2 || detail <= -2) )   // high detail
  {
    // append object list
    for( int i=0; i<mysize(); i++ )
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



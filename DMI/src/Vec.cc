//  DMI::Vec.cc: DMI::Vec implementation
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
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
#include "Vec.h"
#include "DynamicTypeManager.h"
#include "Packer.h"

static int nullheader_data[] = {0,0};
static DMI::SmartBlock nullheader_block( nullheader_data,sizeof(nullheader_data),DMI::EXTERNAL );
static DMI::BlockRef nullheader(nullheader_block,DMI::EXTERNAL|DMI::LOCK|DMI::READONLY);
static DMI::Container::Register reg(TpDMIVec,true);

//##ModelId=3C3D64DC016E
DMI::Vec::Vec ()
  : spvec(0),mytype(0),mysize_(0)
{
  dprintf(2)("default constructor\n");
  spvec = 0;
}

//##ModelId=3C3EE3EA022A
DMI::Vec::Vec (const Vec &right, int flags, int depth,TypeId realtype)
    :Container(),spvec(0),mytype(0),mysize_(0)
{
  dprintf(2)("copy constructor (%s,%x)\n",right.debug(),flags);
  cloneOther(right,flags,depth,true,realtype);
}

//##ModelId=3BFA54540099
DMI::Vec::Vec (TypeId tid, int num, const void *data,TypeId realtype)
    : spvec(0),mytype(0),mysize_(0)
{
  dprintf(2)("constructor(%s,%d)\n",tid.toString().c_str(),num);
  init(tid,num,data,realtype);
}

//##ModelId=3DB9346F0095
DMI::Vec::~Vec()
{
  dprintf(2)("destructor\n");
  clear();
}

//##ModelId=3DB9346F017B
DMI::Vec & DMI::Vec::operator = (const DMI::Vec &right)
{
  if( &right != this )
  {
    Thread::Mutex::Lock _nclock(mutex());
    dprintf(2)("assignment of %s\n",right.debug());
    clear();
    if( right.valid() )
      cloneOther(right,0,0,false,objectType());
  }
  return *this;
}

void DMI::Vec::makeNewHeader (size_t extra_size) const
{
  headref_ <<= new SmartBlock(sizeof(HeaderBlock) + extra_size);
  phead_ = static_cast<HeaderBlock*>(headref_().data());
}

//##ModelId=3C6161190193
DMI::Vec & DMI::Vec::init (TypeId tid, int num, const void *data,TypeId realtype)
{
  //
  // NB: shared memory flags ought to be passed into the SmartBlock
  //
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("init(%s,%d,%p)\n",tid.toString().c_str(),num,(void*)data);
  // if null type, then reset the field to uninit state
  if( !tid )
  {
    clear();
    scalar = true;
    return *this;
  }
  bool wantscalar = false;
  if( num == -1 )
  {
    num = 1;
    wantscalar = true;
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
  binary_type = dynamic_type = container_type = false;
  mytype = tid;
  mysize_ = std::max(num,1);
  scalar = wantscalar;
  typeinfo.size = typeinfo.size;
  switch( typeinfo.category )
  {
  // NUMERIC & BINARY type categories are treated as binary objects
  // of a fixed type, which can be bitwise-copied. The data is kept directly
  // inside one block with the header info. Allocate and attach this block here.
    case TypeInfo::NUMERIC:
    case TypeInfo::BINARY:
    {  
        binary_type = true;
        // allocate header and copy data
        size_t datasize = typeinfo.size*mysize_;
        makeNewHeader(datasize);
        BObj::fillHeader(phead_,1,realtype?realtype:objectType());
        phead_->type = mytype;
        phead_->size = scalar ? -mysize_ : mysize_;
        if( data )
          memcpy(phead_->data,data,datasize);
        else
          memset(phead_->data,0,datasize);
        break;
    }
    case TypeInfo::DYNAMIC: 
    {
        dynamic_type = true;
        container_type = isNestable(tid);
        FailWhen(data,Debug::ssprintf("can't init field of type %s with data",tid.toString().c_str(),num) );
        elems_.resize(mysize_);
        break;
    }    
    case TypeInfo::SPECIAL: 
    {
        FailWhen(!typeinfo.fnew || !typeinfo.fdelete || !typeinfo.fcopy ||
            !typeinfo.fpack || !typeinfo.funpack || !typeinfo.fpacksize,
            "incomplete registry information for"+tid.toString() ); 
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
        break;
    }
    default:
        Throw("unsupported data type "+tid.toString());  
  }
  return *this;
}

// called to ensure writability
void DMI::Vec::makeWritable ()
{
  if( !valid() )
    return;
  // binary types store data with the header block, so deref it for writing
  // to let COW do its thing
  if( binary_type )
    phead_ = static_cast<HeaderBlock*>(headref_().data());
  else // else simply toss out the cached header block
  {
    headref_.detach();
    phead_ = 0;
  }
}

//##ModelId=3C62961D021B
void DMI::Vec::resize (int newsize)
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen( newsize<=0,"can't resize to <=0" );
  FailWhen( !valid(),"uninitialized DMI::Vec" );
  int minsize = std::min(mysize_,newsize);
  makeWritable();
  if( newsize > 1 )
    scalar = false;
  if( binary_type )
  {
    headref_().resize(sizeof(HeaderBlock)+typeinfo.size*newsize);
    phead_ = static_cast<HeaderBlock*>(headref_().data());
    phead_->size = newsize;
  }
  else if( dynamic_type )
  {
    // this is horribly inefficient, but we really must keep the object
    // references locked. Hence, unlock first...
    if( newsize>mysize_ )
      for( ElementVector::iterator iter = elems_.begin(); iter != elems_.end(); iter++ )
        iter->ref.unlock();
    // resize (since this involves a ref assignment)
    elems_.resize(newsize);
    // relock
    if( newsize>mysize_ )
      for( ElementVector::iterator iter = elems_.begin(); iter != elems_.end(); iter++ )
        iter->ref.lock();
    // note that when resizing upwards, this implicitly fills the empty
    // element states with 0 = UNINITIALIZED
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
  }
  mysize_ = newsize;
}

//##ModelId=3C3EAB99018D
void DMI::Vec::clear ()
{
  Thread::Mutex::Lock _nclock(mutex());
  emptyhdr_.detach();
  if( spvec )
  {
    Assert(spdelete);
    (*spdelete)(spvec);
    spvec = 0;
  }
  if( valid() )
  {
    dprintf(2)("clearing\n");
    headref_.detach();
    elems_.clear();
    mytype = 0;
    mysize_ = 0;
  }
}

//##ModelId=3C3EB9B902DF
bool DMI::Vec::isValid (int n) const
{
  Thread::Mutex::Lock _nclock(mutex());
  if( !valid() )
    return false;
  checkIndex(n);
  if( dynamic_type ) 
    return elems_[n].state != UNINITIALIZED;
  else
    return true; // built-ins always valid
}

//##ModelId=3C3C8D7F03D8
DMI::ObjRef DMI::Vec::getObj (int n) const
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen( !valid(),"uninitialized DMI::Vec");
  checkIndex(n);
  if( !dynamic_type )
    return ObjRef();
  // return a copy as a read-only ref
  return resolveObject(n);
}

//##ModelId=3C7A305F0071
void DMI::Vec::put (int n,ObjRef &ref,int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  makeWritable();
  dprintf(2)("putting @%d: %s\n",n,ref.debug(2));
  ObjRef &ref2 = prepareForPut(ref->objectType(),n);
  // grab the ref, and mark object as modified
  if( flags&DMI::XFER )
    ref2.unlock().xfer(ref,flags).lock();
  else
    ref2.unlock().copy(ref,flags).lock();
}

//##ModelId=3C3D5F2001DC
int DMI::Vec::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf1(2)("%s: fromBlock\n",debug());
  clear();
  int npopped = 1;
  // get header block, privatize & cache it as headref_
  set.pop(headref_);  
  size_t hsize = headref_->size();
  phead_ = static_cast<HeaderBlock*>(const_cast<void*>(headref_->data()));
  // verify BObj header
  int blockcount = BObj::checkHeader(phead_);
  // first two ints in header block are type and size
  FailWhen( hsize < sizeof(HeaderBlock),"malformed header block" );
  // get type and size from header
  mytype  = phead_->type;
  mysize_ = phead_->size;
  if( mysize_ == -1 )
  {
    mysize_ = 1;
    scalar = true;
  }
  else
    scalar = false;
  if( !mytype )  // uninitialized field
    return 1;
  // obtain type information, check that type is supported
  typeinfo = TypeInfo::find(mytype);
  binary_type = dynamic_type = container_type = false;
  switch( typeinfo.category )
  {
    case TypeInfo::NUMERIC:
    case TypeInfo::BINARY:  // numeric/binary types are stored directly in the header
      binary_type = true;
      dprintf(2)("fromBlock: built-in type %s[%d]\n",mytype.toString().c_str(),mysize_);
      FailWhen( hsize != sizeof(HeaderBlock) + typeinfo.size*mysize_,
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
                phead_->data,
                hsize - sizeof(HeaderBlock),n);
      spdelete = typeinfo.fdelete;
      FailWhen( n != mysize_,"size mismatch after unpacking" );
      break;
        
    case TypeInfo::DYNAMIC: // dynamic type: header contains info on # of blocks to follow
      dynamic_type = true;
      container_type = isNestable(mytype);
      dprintf(2)("fromBlock: dynamic type %s[%d]\n",mytype.toString().c_str(),mysize_);
      FailWhen( hsize != sizeof(HeaderBlock)+sizeof(int)*mysize_,"incorrect block size" );
      elems_.resize(mysize_);
      // Get blocks from set
      // Do not unblock objects, as that is done at dereference time
      // Note that we don't privatize the blocks, so field contents may
      // be shared and/or read-only
      {
        const int * blockcounts = reinterpret_cast<const int*>(phead_->data);
        for( int i=0; i<mysize_; i++ ) 
        {
          int nbl = blockcounts[i];
          if( nbl )
          {
            npopped += nbl;
            dprintf(3)("fromBlock: [%d] taking over %d blocks\n",i,nbl);
            set.popMove(elems_[i].bset,nbl);
            elems_[i].state = INBLOCK;
          }
          else // no blocks assigned to this object => is uninitialized
            elems_[i].state = UNINITIALIZED;
        }
      }
      dprintf(2)("fromBlock: %d blocks were popped\n",npopped);
      break;
        
    default:
        Throw("unsupported data type "+mytype.toString());
  }
  FailWhen(npopped != blockcount,"mismatching block count in header block");
  validateContent(true);
  return npopped;
}

const DMI::BlockRef & DMI::Vec::emptyObjectBlock () const
{
  if( !emptyhdr_.valid() )
  {
    emptyhdr_ <<= new SmartBlock(sizeof(BObj::Header),DMI::ZERO);
    BObj::Header * hdr = emptyhdr_().pdata<Header>();
    hdr->tid = mytype;
    hdr->blockcount = 1;
  }
  return emptyhdr_;
}

//##ModelId=3C3D5F2403CC
int DMI::Vec::toBlock (BlockSet &set) const
{
  // write-lock, since we modify internal fields
  Thread::Mutex::Lock _nclock(mutex());
  if( !valid() )
  {
    dprintf1(2)("%s: toBlock=1 (field empty)\n",debug());
    // for empty fields, use null block 
    BlockRef ref(new SmartBlock(sizeof(HeaderBlock),DMI::ZERO));
    BObj::fillHeader(ref().pdata<HeaderBlock>(),1);
    set.push(ref);
    return 1;
  }
  dprintf1(2)("%s: toBlock\n",debug());
  int npushed = 1; // 1 header block as a minimum
  // we may be forming a header block on-the-fly below,
  // so push out a placeholder ref here, and attach header to it later
  BlockRef & href_placeholder = set.pushNew();
  bool new_header = false;
  // since any access for writing (see makeWritable()) invalidates
  // the header block, this is a sufficient check to see if it needs
  // rebuilding. 
  if( dynamic_type ) // kludge for now, because there's still a bug somewhere with the cached block
    headref_.detach();
  if( !headref_.valid() )
  {
    // binary types always have a valid & consistent block
    Assert1(!binary_type);
    new_header = true;
    if( dynamic_type ) // dynamic type contains header + block counts
      makeNewHeader(sizeof(int)*mysize_);
    else // special type, header + data
    {
      // allocate and attach header block
      size_t datasize = (*typeinfo.fpacksize)(spvec,mysize_);
      makeNewHeader(datasize);
      // pack object data into header block
      (*typeinfo.fpack)(spvec,mysize_,phead_->data,datasize);
    }
    phead_->type = mytype;
    phead_->size = scalar ? -mysize_ : mysize_;
  }
  // for dynamic types, do a toBlock on the objects as needed
  if( dynamic_type )
  {
    int * blockcounts = reinterpret_cast<int*>(phead_->data);
    for( int i=0; i<mysize_; i++ )
    {
      int nb;
      Element &elem = elems_[i];
      switch( elem.state )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            dprintf(3)("toBlock: [%d] is uninitialized, no blocks\n",i);
            // set.push(emptyObjectBlock());
            nb = 0;
            break;
        case INBLOCK:
            nb = elem.bset.size();
            dprintf(3)("toBlock: [%d] still cached in %d blocks, copying\n",i,nb);
            set.pushCopy(elem.bset);
            break;
        case UNBLOCKED:
        case MODIFIED:
            elem.bset.clear();
            if( elem.ref.valid() )
            {
              nb = elem.ref->toBlock(set);
              dprintf(3)("toBlock: [%d] converted to %d blocks\n",i,nb);
            }
            else
            {
              dprintf(3)("toBlock: [%d] is uninitialized, 0 blocks\n",i);
              elem.state = UNINITIALIZED;
              // set.push(emptyObjectBlock());
              nb = 0;
            }
            break;
        default:
            Throw("inconsistent object state");
      }
      // store or check block count in header
      npushed += nb;
      if( new_header )
        blockcounts[i] = nb;
      else
      {
        FailWhen(blockcounts[i]!=nb,"inconsistency in cached header block");
      }
    }
  }
  // if new header, fill BObj data, else just check total block count
  if( new_header )
    BObj::fillHeader(phead_,npushed);
  else
  {
    FailWhen(phead_->blockcount != npushed,"inconsistency in cached header block");
  }
  // finally, attach header block in placeholder
  href_placeholder = headref_;
  dprintf(2)("toBlock: %d blocks pushed\n",npushed);
  return npushed;
}

//##ModelId=3C3D8C07027F
DMI::ObjRef & DMI::Vec::resolveObject (int n) const
{
  Thread::Mutex::Lock _nclock(mutex());
  Element &elem = elems_[n];
  switch( elem.state )
  {
    // uninitialized object - create default
    case UNINITIALIZED:
    {
        dprintf(3)("resolveObject(%d): creating new %s\n",n,mytype.toString().c_str());
        elem.ref.attach(DynamicTypeManager::construct(mytype),DMI::LOCK);
        elem.state = MODIFIED;
        headref_.detach(); // in case we implicitly initialized
        phead_ = 0;
        return elem.ref;
    }
    // object hasn't been unblocked
    case INBLOCK:
    {
        dprintf(3)("resolveObject(%d): unblocking %s\n",n,mytype.toString().c_str());
        elem.ref = DynamicTypeManager::construct(0,elem.bset);
        elem.ref.lock();
        // verify that no blocks were left over
        FailWhen( elem.bset.size()>0,"block count mismatch" );
        elem.bset.clear();
        elem.state = MODIFIED;
        return elem.ref;
    }
    // object exists (unblocked and maybe modified)
    case UNBLOCKED:
    case MODIFIED:
    {
        // not valid? Mark as uninitialized and try again
        if( !elem.ref.valid() )
        {
          elem.state = UNINITIALIZED;
          return resolveObject(n);
        }
        return elem.ref;
    }
    default:
        Throw("unexpected object state");
  }
}

//##ModelId=3C3EC77D02B1
DMI::CountedRefTarget* DMI::Vec::clone (int flags, int depth) const
{
  return new DMI::Vec(*this,flags,depth);
}

//##ModelId=3C3EE42D0136
void DMI::Vec::cloneOther (const DMI::Vec &other,int flags,int depth,bool constructing,TypeId realtype)
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
  // copy the header ref and reset pointer
  headref_.copy(other.headref_,flags,depth);
  phead_ = headref_.valid() 
           ? const_cast<HeaderBlock*>(headref_->pdata<HeaderBlock>())
           : 0;
  // re-write type to headref if needed
  if( !realtype )
    realtype = objectType();
  if( realtype != other.objectType() )
  {
    phead_ = headref_().pdata<HeaderBlock>();
    BObj::fillHeader(phead_,phead_->blockcount,realtype);
  }
  if( dynamic_type )   // handle dynamic types
  {
    elems_.clear();
    elems_ = other.elems_;
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
  }
  validateContent(!constructing);
  // for binary types, do nothing since they're already in the header block
}

//##ModelId=3D05E2F301D2
int DMI::Vec::size (TypeId tid) const
{
  Thread::Mutex::Lock _nclock(mutex());
  // if types do not match (or tid=0), and we're scalar, and have
  // a subcontainer, then defer to its size()
  if( tid != mytype && scalar && mysize() == 1 && container_type )
  {
    const BObj * pobj = resolveObject(0).deref_p();
    const Container * pnc = dynamic_cast<const Container *>(pobj);
    if( pnc )
      return pnc->size(tid);
    else
      Throw("can't access "+pobj->objectType().toString()+" as "+tid.toString());
  }
  // else return our own size
  if( !tid || tid == mytype ||
      ( tid == TpDMIObjRef && dynamic_type ) || 
      ( TypeInfo::isNumeric(tid) && TypeInfo::isNumeric(mytype) ) )
    return mysize();
  return -1;
}

//##ModelId=3C7A19790361
int DMI::Vec::get (const HIID &id,ContentInfo &info,bool nonconst,int flags) const
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen( !valid(),"field not initialized" );
  if( flags&(DMI::WRITE|DMI::ASSIGN) )
  {
    Assert1(nonconst);
    const_cast<Vec*>(this)->makeWritable();
  }
  int n;  // number of item being accessed
  // null HIID implies scalar-mode access
  if( id.empty() )
  {
    n = 0;
    info.size = mysize();
  }
  // numeric (single-index) HIID implies item #n
  else 
  {
    FailWhen(id.size()>1,"illegal DMI::Vec index: "+id.toString());
    n = id.front().index();
    FailWhen(n<0,"illegal DMI::Vec index: "+id.toString());
    FailWhen(n>mysize(),"index "+id.toString()+"is out of range" );
    info.size = 1;
  }
    
  if( n == mysize() ) // can insert at end, return 0 to indicate
    return 0;
  // handle case of dynamic types 
  if( dynamic_type )
  {
    // since dynamic objects are non-contiguous, prohibit vector access
    FailWhen(info.size>1,"DMI::Vec of "+type().toString()+"s can't be accessed in vector mode");
    // object hasn't been initialized? If not assigning, then return 0
    Element &elem = elems_[n];
    if( elem.state == UNINITIALIZED )
    {
// invalid objects automatically initialized to empty on first access
//      if( !(flags&DMI::ASSIGN) )
//        return 0;
      resolveObject(n);
    }
    // object hasn't been unblocked yet? Then we need to unblock it first
    else if( elem.state == INBLOCK )
      resolveObject(n);
    // return ref to object; mark it as modified if expected to write,
    // dereference once to insure COW
    if( flags&DMI::WRITE )
    {
      elem.ref.dewr();
      elem.bset.clear();
      elem.state = MODIFIED;
    }
    info.tid = TpDMIObjRef;
    info.obj_tid = type();
    info.ptr = &elem.ref;
  }
  else // binary or special type
  {
    info.tid = info.obj_tid = type();
    if( binary_type ) // binary type: data in header block
    {
      // block cow is ensured by makeWritable() call above
      info.ptr = phead_->data + n*typeinfo.size;
    }
    else        // special type: data in separate spvec
      info.ptr = static_cast<const char*>(spvec) + n*typeinfo.size;
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
    //     DMI::Container *nc = dynamic_cast<DMI::Container *>
    //         (&resolveObject(0,true).dewr());
    //     Assert(nc);
    //     // defer to insert[id] on container
    //     return nc->insert(id,tid,real_tid);

//##ModelId=3C7A198A0347
int DMI::Vec::insert (const HIID &id,ContentInfo &info)
{
  Thread::Mutex::Lock _nclock(mutex());
  makeWritable();
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
    Throw("illegal DMI::Vec index: "+id.toString());
  // check types
  // insert item
  TypeId real_tid = info.tid = info.obj_tid;
  info.size = 1;
  info.writable = true;
  if( !valid() ) // empty field? must insert at #0
  {
    FailWhen(n,Debug::ssprintf("can't insert at [%d]",n));
    FailWhen(!real_tid,"can't initialize DMI::Vec without type");
    init(real_tid,-1); // init as scalar field
  }
  else // else extend field, but only if inserting at end
  {
    FailWhen(n != mysize(),Debug::ssprintf("can't insert at [%d]",n) );
    if( real_tid )
    {
      FailWhen(type()!=real_tid && !TypeInfo::isConvertible(real_tid,type()),
            "inserting "+real_tid.toString()+" into a DMI::Vec of "+type().toString());
    }
    info.tid = info.obj_tid = type();
    resize( mysize()+1 );
  }
  if( binary_type )
  {
    info.ptr = phead_->data + n*typeinfo.size;
  }
  else if( dynamic_type )
  {
    info.tid = TpDMIObjRef;
    elems_[n].state = MODIFIED;
    info.ptr = &elems_[n].ref;
  }
  else // special type
  {
    info.ptr = static_cast<char*>(spvec) + n*typeinfo.size;
  }
  return 1;
}

//##ModelId=3C877E1E03BE
int DMI::Vec::remove (const HIID &id)
{
  Thread::Mutex::Lock _nclock(mutex());
  makeWritable();
  dprintf(2)("remove(%s)\n",id.toString().c_str());
  FailWhen(id.empty(),"null HIID");
  if( id.size()==1 && id.front().index()>=0 )
  {
    int n = id.front().index();
    dprintf(2)("removen(%d)\n",n);
    FailWhen( !valid() || !mysize(),"field not initialized or empty" );
    FailWhen( n != mysize()-1,"can only remove from end of field" );
    dprintf(2)("removen: resizing to %d elements\n",n);
    resize(n);
    return 1;
  }
  else
    Throw("illegal DMI::Vec index: "+id.toString());
}

//##ModelId=3DB9347800CF
DMI::ObjRef & DMI::Vec::prepareForPut (TypeId tid,int n) 
{
  if( !valid() ) // invalid field?
  {
    if( !n )
      init(tid,1);   // empty field auto-extended to 1
    else
      Throw("uninitialized DMI::Vec");
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
  Element & elem = elems_[n];
  elem.bset.clear();
  elem.state = MODIFIED;
  return elem.ref;
}

//##ModelId=3DB934730394
string DMI::Vec::sdebug ( int detail,const string &prefix,const char *name ) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  Thread::Mutex::Lock _nclock(mutex());
  string out;
  if( detail>=0 ) // basic detail
  {
    out = name ? string(name) : objectType().toString();
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    out += ssprintf("/%p",(void*)this);
    if( !type() )
      appendf(out,"empty");
    else
      appendf(out,"%s:%d",type().toString().c_str(),mysize());
    append(out,"/",CountedRefTarget::sdebug(-1));
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
      const Element & elem = elems_[i];
      switch( elem.state )
      {
        case UNINITIALIZED: // if uninitialized, then do nothing
            out += "    "+Debug::ssprintf("%d: uninitialized",i);
            break;
        case INBLOCK:
            out += "    "+Debug::ssprintf("%d: in block: ",i)
                         +elem.bset.sdebug(abs(detail)-1,prefix+"    ");
            break;
        case UNBLOCKED:
            out += "    "+Debug::ssprintf("%d: unblocked [",i)
                         +elem.bset.sdebug(abs(detail)-1,prefix+"    ")
                         +"], to"
                         +elem.ref.sdebug(abs(detail)-1,prefix+"    ");
            break;
        case MODIFIED:
            out += "    "+Debug::ssprintf("%d: modified ",i)
                         +elem.ref.sdebug(abs(detail)-1,prefix+"    ");
            break;
        default:
            Throw("illegal object state");
      }
    }
  }
  return out;
}




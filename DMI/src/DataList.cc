//#  DataList.cc: list of containers
//#
//#  Copyright (C) 2002-2004
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#define NC_SKIP_HOOKS 1
    
#include "DynamicTypeManager.h"
#include "DataList.h"
#include "DataField.h"

    // register as a nestable container
static NestableContainer::Register reg(TpDataList,True);
typedef NestableContainer::Ref NCRef;

DataList::DataList (int)
  : NestableContainer()
{
  dprintf(2)("default constructor\n");
}

DataList::DataList (const DataList &other, int flags, int depth)
  : NestableContainer()
{
  dprintf(2)("copy constructor, cloning from %s\n",other.debug(1));
  cloneOther(other,flags,depth);
}

DataList::~DataList()
{
  dprintf(2)("destructor\n");
}

DataList & DataList::operator=(const DataList &right)
{
  if( &right != this )
  {
    dprintf(2)("assignment op, cloning from %s\n",right.debug(1));
    cloneOther(right,DMI::PRESERVE_RW,0);
  }
  return *this;
}

const NCRef & DataList::applyIndexConst (int n) const
{
  FailWhen(items.empty(),"index out of range");
  if( n<0 )
  {
    ItemList::const_reverse_iterator riter = items.rbegin();
    for( ;n<0; n++,riter++ )
      { FailWhen( riter == items.rend(),"index out of range"); }
    return *riter;
  }
  else 
  {
    ItemList::const_iterator iter = items.begin();
    for( ;n>0; n--,iter++ )
      { FailWhen( iter == items.end(),"index out of range"); }
    FailWhen( iter == items.end(),"index out of range");
    return *iter;
  }
}

DataList::ItemList::iterator DataList::applyIndexIter (int n)
{
  if( n<0 )
  {
    ItemList::reverse_iterator riter = items.rbegin();
    for( ;n<0; n++,riter++ )
      { FailWhen( riter == items.rend(),"index out of range"); }
    return riter.base();
  }
  else 
  {
    ItemList::iterator iter = items.begin();
    for( ;n>0; n--,iter++ )
      { FailWhen( iter == items.end(),"index out of range"); }
    return iter;
  }
}

void DataList::replace (int n, const NCRef &ref, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("replace(%d,[%s],%x)\n",n,ref->debug(1),flags);
  if( flags&DMI::COPYREF )
    applyIndex(n).unlock().copy(ref,flags).lock();
  else
    applyIndex(n).unlock().xfer(ref).lock();
}

void DataList::replace (int n, NestableContainer *pnc, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("replace(%d,[%s],%x)\n",n,pnc->debug(1),flags);
  applyIndex(n).unlock().attach(pnc,flags).lock();
}

void DataList::addFront (const NCRef &ref, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("addFront([%s],%x)\n",ref->debug(1),flags);
  // insert into map
  if( flags&DMI::COPYREF )
    items.push_front(ref.copy(flags));
  else
    items.push_front(ref);
}

void DataList::addFront (NestableContainer *pnc, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("addFront([%s],%x)\n",pnc->debug(1),flags);
  items.push_front(NCRef(pnc,flags));
}

void DataList::addBack (const NCRef &ref, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("addBack([%s],%x)\n",ref->debug(1),flags);
  // insert into map
  if( flags&DMI::COPYREF )
    items.push_back(ref.copy(flags));
  else
    items.push_back(ref);
}

void DataList::addBack (NestableContainer *pnc, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("addBack([%s],%x)\n",pnc->debug(1),flags);
  items.push_back(NCRef(pnc,flags));
}


void DataList::append (const DataList &other,int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  Thread::Mutex::Lock _nclock2(other.mutex());
  for( ItemList::const_iterator iter = other.items.begin(); iter != other.items.end(); iter++ )
    items.push_back(iter->copy(flags));
}

void DataList::append (DataList &other,int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  Thread::Mutex::Lock _nclock2(other.mutex());
  for( ItemList::iterator iter = other.items.begin(); iter != other.items.end(); iter++ )
    items.push_back(iter->copy(flags));
}

NCRef DataList::remove (int n)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("remove(%d)\n",n);
  ItemList::iterator iter = applyIndexIter(n);
  FailWhen(iter == items.end(),"index out of range");
  NCRef ref(iter->unlock());
  dprintf(2)("  removing %s\n",ref->debug(1));
  items.erase(iter);
  return ref;
}

NCRef DataList::getItem (int n) const
{
  Thread::Mutex::Lock _nclock(mutex());
  return applyIndexConst(n).copy(DMI::READONLY);
}

NCRef DataList::getItemWr (int n, int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  return applyIndex(n).copy(flags);
}

int DataList::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("fromBlock(%s)\n",set.debug(2));
  int nref = 1;
  items.clear();
  // pop and cache the header block as headref
  BlockRef headref;
  set.pop(headref);
  size_t hsize = headref->size();
  FailWhen( hsize < sizeof(int),"malformed header block" );
  // get # of fields
  const int *hdata = reinterpret_cast<const int *>( headref->data() );
  int nfields = *hdata++;
  FailWhen( hsize != sizeof(int)*(nfields+1),"malformed header block" );
  dprintf(2)("fromBlock: %d header bytes, %d fields expected\n",hsize,nfields);
  // get fields one by one
  for( int i=0; i<nfields; i++ )
  {
    NCRef ref;
    int ftype = *hdata++;
    if( ftype )
    {
      // create field container object
      NestableContainer *field = dynamic_cast<NestableContainer *>
          ( DynamicTypeManager::construct(ftype) );
      FailWhen( !field,"cast failed: perhaps field is not a container?" );
      ref <<= field;
      // unblock and set the writable flag
      int nr = field->fromBlock(set);
      nref += nr;
      dprintf(3)("%d [%s] used %d blocks\n",i,field->sdebug(1).c_str(),nr);
    }
    else
    { 
      dprintf(3)("%d is an empty item\n",i); 
    }
    items.push_back(ref);
  }
  dprintf(2)("fromBlock: %d total blocks used\n",nref);
  validateContent();
  return nref;
}

int DataList::toBlock (BlockSet &set) const
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("toBlock\n");
  int nref = 1;
  // compute header size
  int numitems = numItems();
  size_t hdrsize = sizeof(int)*(numitems+1);
  // allocate new header block
  SmartBlock *header = new SmartBlock(hdrsize);
  BlockRef headref(header,DMI::ANONWR);
  // store header info
  int  *hdr = static_cast<int *>(header->data());
  *hdr++ = numitems;
  set.push(headref);
  dprintf(2)("toBlock: %d header bytes, %d fields\n",hdrsize,numitems);
  // store IDs and convert everything
  ItemList::const_iterator iter = items.begin();
  int i=0;
  for( ; iter != items.end(); iter++,i++ )
  {
    Assert(i<numitems);
    if( iter->valid() )
    {
      *hdr++ = (*iter)->objectType();
      int nr1 = (*iter)->toBlock(set);
      nref += nr1;
      dprintf(3)("%d [%s] generated %d blocks\n",i,iter->sdebug(1).c_str(),nr1);
    }
    else
    {
      *hdr++ = 0;
      dprintf(3)("%d is an empty item\n",i);
    }
  }
  Assert(i==numitems);
  dprintf(2)("toBlock: %d total blocks generated\n",nref);
  return nref;
}

CountedRefTarget* DataList::clone (int flags, int depth) const
{
  dprintf(2)("cloning new DataList\n");
  return new DataList(*this,flags,depth);
}

void DataList::privatize (int flags, int depth)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("privatizing DataList\n");
  if( flags&DMI::DEEP || depth>0 )
  {
    ItemList::iterator iter = items.begin();
    for( ; iter != items.end(); iter++ )
      if( iter->valid() )
      {
        dprintf(4)("  privatizing a %s\n",(*iter)->objectType().toString().c_str());
        iter->privatize(flags|DMI::LOCK,depth-1);
      }
      else
      {
        dprintf(4)("  skipping empty item");
      }
    // since things may have changed around, revalidate content
    validateContent();
  }
}

void DataList::cloneOther (const DataList &other, int flags, int depth)
{
  Thread::Mutex::Lock _nclock(mutex());
  Thread::Mutex::Lock _nclock1(other.mutex());
  items.clear();
  // copy all field refs, then privatize them if depth>0.
  // For ref.copy(), clear the DMI::WRITE flag and use DMI::PRESERVE_RW instead.
  // (When depth>0, DMI::WRITE will take effect anyways via privatize().
  //  When depth=0, we must preserve the write permissions of the contents.)
  ItemList::const_iterator iter = other.items.begin();
  for( ; iter != other.items.end(); iter++ )
  {
    items.push_back(NCRef());
    items.back().copy(*iter,(flags&~DMI::WRITE)|DMI::PRESERVE_RW|DMI::LOCK);
    if( flags&DMI::DEEP || depth>0 )
      items.back().privatize(flags|DMI::LOCK,depth-1);
  }
  validateContent();
}

int DataList::get (const HIID &id,ContentInfo &info, 
                   bool nonconst,int flags) const
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen(id.empty(),"null index");
  FailWhen(id.size()>1,"invalid index");
  AtomicID index = id.front();
  int n = index;
  // insert allowed @end of list, return 0 if @end
  if( n == numItems() )
    return 0;
  // else resolve n to a valid item
  const NCRef &ref = applyIndexConst(n);
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

int DataList::insert (const HIID &id,ContentInfo &info)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("insert(%s)\n",id.toString().c_str());
  FailWhen(id.empty(),"null index");
  FailWhen(id.size()>1,"invalid index");
  ItemList::iterator iter = applyIndexIter(id[0]);
  TypeId tid = info.obj_tid;
  iter = items.insert(iter,NCRef());
  // Containers are inserted directly
  if( isNestable(tid) )
  {
    info.ptr = &(*iter);
    info.tid = TpObjRef;
    info.writable = True;
    info.size = 1;
    return 1;
  }
  // everything else is inserted as a scalar DataField
  else
  {
    NestableContainer *pf = new DataField(tid,-1); // -1 means scalar
    iter->attach(pf,DMI::ANONWR|DMI::LOCK);
    // do a get() on the field to obtain info
    return pf->get(0,info,DMI::NC_ASSIGN|DMI::WRITE);
  }
}

int DataList::remove (const HIID &id)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("remove(%s)\n",id.toString().c_str());
  FailWhen(id.empty(),"null index");
  FailWhen(id.size()>1,"invalid index");
  // find and remove
  remove(int(id[0]));
  return 1;
}

int DataList::size (TypeId tid) const
{
  if( !tid || tid == TpObjRef )
    return items.size();
  return -1;
}

string DataList::sdebug ( int detail,const string &prefix,const char *name ) const
{
  static int nesting=0;
  Thread::Mutex::Lock _nclock(mutex());
  if( nesting++>1000 )
  {
    cerr<<"Too many nested DataList::sdebug() calls";
    abort();
  }
  string out;
  if( detail>=0 ) // basic detail
  {
    Debug::appendf(out,"%s/%08x",name?name:objectType().toString().c_str(),(int)this);
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    out += Debug::ssprintf("%d items",numItems());
    out += " / refs "+CountedRefTarget::sdebug(-1);
  }
  if( detail >= 2 || detail <= -2 )   // high detail
  {
    // append debug info from CountedRefTarget
    string str = CountedRefTarget::sdebug(-2,prefix+"          ");
    if( str.length() )
      out += "\n"+prefix+"       refs "+str;
    ItemList::const_iterator iter = items.begin();
    for( ; iter != items.end(); iter++ )
    {
      if( out.length() )
        out += "\n"+prefix+"  ";
      string out1;
      try
      {
        out1 = iter->valid() 
            ? iter->sdebug(abs(detail)-1,prefix+"          ")
            : "(empty)";
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

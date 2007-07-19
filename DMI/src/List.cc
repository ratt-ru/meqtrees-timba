//#  DMI::List.cc: list of containers
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
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
#include "List.h"
#include "Vec.h"

// register as a nestable container
static DMI::Container::Register reg(TpDMIList,true);

DMI::List::List ()
  : DMI::Container()
{
  dprintf(2)("default constructor\n");
}

DMI::List::List (const List &other, int flags, int depth)
  : DMI::Container()
{
  dprintf(2)("copy constructor, cloning from %s\n",other.debug(1));
  cloneOther(other,flags,depth,true);
}

DMI::List::~List()
{
  dprintf(2)("destructor\n");
}

DMI::List & DMI::List::operator = (const List &right)
{
  if( &right != this )
  {
    dprintf(2)("assignment op, cloning from %s\n",right.debug(1));
    cloneOther(right,0,0,false);
  }
  return *this;
}

DMI::List::ItemList::const_iterator DMI::List::applyIndexConst (int n) const
{
  if( n<0 )
  {
    ItemList::const_reverse_iterator riter = items.rbegin();
    n++;
    while( n<0 && riter != items.rend() )
      ++n,++riter;
    FailWhen(n,"index out of range"); 
    return riter.base();
  }
  else 
  {
    ItemList::const_iterator iter = items.begin();
    while( n>0 )
    {
      n--;
      iter++;
      FailWhen(iter == items.end(),"index out of range"); 
    }
    return iter;
  }
}

// if inserting=true, then we want to insert BEFORE the given position
//    thus: -1 == end(), -2 == end()-1, etc.
// if inserting=false, then we want to replace AT the given position
//    thus: -1 == end()-1, -2 == end()-2, etc.
DMI::List::ItemList::iterator DMI::List::applyIndex (int n,bool inserting) 
{
  ItemList::iterator iter;
  if( n<0 )
  {
    ItemList::reverse_iterator riter = items.rbegin();
    if( inserting ) // do one less iteration when inserting, so that -1==end() (which ==rbegin())
      n++;
    while( n<0 && riter != items.rend() )
      ++n,++riter;
    FailWhen(n,"index out of range"); 
    return riter.base();
  }
  else 
  {
    ItemList::iterator iter = items.begin();
    while( n>0 && iter != items.end() )
      --n,++iter;
    FailWhen(n || (!inserting && iter == items.end()),"index out of range"); 
    return iter;
  }
}

void DMI::List::put (int n,ObjRef &ref,int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  bool replace = flags&DMI::REPLACE;
  ItemList::iterator iter = applyIndex(n,!replace);
  if( replace )
  {
    if( flags&DMI::XFER )
      iter->unlock().xfer(ref,flags).lock();
    else
      iter->unlock().copy(ref,flags).lock();
  }
  else
    items.insert(iter,flags&DMI::XFER ? ref.xfer(flags) : ref.copy(flags) );
}

void DMI::List::append (const List &other,int flags)
{
  Thread::Mutex::Lock _nclock(mutex());
  Thread::Mutex::Lock _nclock2(other.mutex());
  for( ItemList::const_iterator iter = other.items.begin(); iter != other.items.end(); iter++ )
    items.push_back(iter->copy(flags));
}

DMI::ObjRef DMI::List::remove (int n)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("remove(%d)\n",n);
  ItemList::iterator iter = applyIndex(n,false);
  ObjRef ref(iter->unlock());
  dprintf(2)("  removing %s\n",ref->debug(1));
  items.erase(iter);
  return ref;
}

DMI::ObjRef DMI::List::get (int n) const
{
  Thread::Mutex::Lock _nclock(mutex());
  return *applyIndexConst(n);
}

int DMI::List::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("fromBlock(%s)\n",set.debug(2));
  int nref = 1;
  items.clear();
  // pop the header block
  BlockRef headref;
  set.pop(headref);
  size_t hsize = headref->size();
  FailWhen( hsize < sizeof(Header),"malformed header block" );
  // get # of fields
  const Header *hdata = static_cast<const Header *>( headref->data() );
  int blockcount = BObj::checkHeader(hdata);
  int nfields = hdata->num_items;
  FailWhen(hsize != sizeof(Header)+sizeof(int)*nfields,"malformed header block");
  dprintf(2)("fromBlock: %d header bytes, %d fields expected\n",hsize,nfields);
  // get fields one by one
  for( int i=0; i<nfields; i++ )
  {
    items.push_back(ObjRef());
    int bc = hdata->item_bc[i];
    if( bc )
    {
      int nb0 = set.size();
      FailWhen(!nb0,"unexpectedly ran out of blocks");
      // create object
      try
      {
        items.back() = DynamicTypeManager::construct(0,set);
        FailWhen(!items.back().valid(),"item construct failed" );
      }
      catch( std::exception &exc )
      {
        string msg = string("error unpacking: ") + exc.what();
        items.back() <<= new DMI::Vec(Tpstring,-1,&msg);
      }
      catch( ... )
      {
        static string msg = "error unpacking: unkown exception";
        items.back() <<= new DMI::Vec(Tpstring,-1,&msg);
      }
      int nb = nb0 - set.size();
      FailWhen(nb!=bc,"block count mismatch in header");
      nref += nb;
      dprintf(3)("%d [%s] used %d blocks\n",i,items.back()->sdebug(1).c_str(),nb);
    }
    else
    {
      dprintf(3)("%d is an empty item\n",i); 
    }
  }
  FailWhen(nref!=blockcount,"total block count mismatch in header");
  dprintf(2)("fromBlock: %d total blocks used\n",nref);
  validateContent(true);
  return nref;
}

int DMI::List::toBlock (BlockSet &set) const
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("toBlock\n");
  int nref = 1;
  // compute header size
  int numitems = numItems();
  size_t hdrsize = sizeof(Header) + sizeof(int)*numitems;
  // allocate new header block
  SmartBlock *header = new SmartBlock(hdrsize);
  BlockRef headref(header);
  // store header info
  Header *hdr = static_cast<Header*>(header->data());
  hdr->num_items = numitems;
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
      nref += hdr->item_bc[i] = iter->deref().toBlock(set);
      dprintf(3)("%d [%s] generated %d blocks\n",i,iter->sdebug(1).c_str(),hdr->item_bc[i]);
    }
    else
    {
      hdr->item_bc[i] = 0;
      dprintf(3)("%d is an empty item\n",i);
    }
  }
  BObj::fillHeader(hdr,nref);
  Assert(i==numitems);
  dprintf(2)("toBlock: %d total blocks generated\n",nref);
  return nref;
}

DMI::CountedRefTarget* DMI::List::clone (int flags, int depth) const
{
  dprintf(2)("cloning new DMI::List\n");
  return new DMI::List(*this,flags,depth);
}

void DMI::List::cloneOther (const DMI::List &other,int flags,int depth,bool constructing)
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
    items.push_back(ObjRef());
    items.back().copy(*iter,flags,depth).lock();
  }
  validateContent(!constructing);
}

int DMI::List::get (const HIID &id,ContentInfo &info, 
                   bool nonconst,int flags) const
{
  Thread::Mutex::Lock _nclock(mutex());
  FailWhen(id.empty(),"null index");
  FailWhen(id.size()>1,"invalid index");
  Assert1(nonconst || !(flags&DMI::WRITE));
  AtomicID index = id.front();
  int n = index;
  // insert allowed @end of list, return 0 if @end
  if( n == numItems() )
    return 0;
  // else resolve n to a valid item
  ObjRef &ref = const_cast<ObjRef&>(*applyIndexConst(n));
  if( flags&WRITE )
    ref.dewr();  // causes copy-on-write as needed
  info.ptr = &ref;
  info.writable = nonconst;
  info.tid = TpDMIObjRef;
  info.obj_tid = ref.valid() ? ref->objectType() : NullType;
  info.size = 1;
  return 1;
}

int DMI::List::insert (const HIID &id,ContentInfo &info)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("insert(%s)\n",id.toString().c_str());
  FailWhen(id.empty(),"null index");
  FailWhen(id.size()>1,"invalid index");
  ItemList::iterator iter = applyIndex(id[0],true);
  TypeId tid = info.obj_tid;
  iter = items.insert(iter,ObjRef());
  // Objects are inserted directly
  if( info.tid == TpDMIObjRef )
  {
    info.ptr = &(*iter);
    info.tid = TpDMIObjRef;
    info.writable = true;
    info.size = 1;
    return 1;
  }
  // everything else is inserted as a scalar DMI::Vec
  else
  {
    Container *pf = new DMI::Vec(tid,-1); // -1 means scalar
    iter->attach(pf).lock();
    // do a get() on the field to obtain info
    return pf->get(0,info,DMI::ASSIGN|DMI::WRITE);
  }
}

int DMI::List::remove (const HIID &id)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf(2)("remove(%s)\n",id.toString().c_str());
  FailWhen(id.empty(),"null index");
  FailWhen(id.size()>1,"invalid index");
  // find and remove
  remove(int(id[0]));
  return 1;
}

int DMI::List::size (TypeId tid) const
{
  if( !tid || tid == TpDMIObjRef )
    return items.size();
  return -1;
}

string DMI::List::sdebug ( int detail,const string &prefix,const char *name ) const
{
  Thread::Mutex::Lock _nclock(mutex());
  string out;
  if( detail>=0 ) // basic detail
  {
    out = name ? string(name) : objectType().toString();
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    out += ssprintf("/%p %d items / %s refs",(void*)this,numItems(),
                    CountedRefTarget::sdebug(-1).c_str());
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
  return out;
}

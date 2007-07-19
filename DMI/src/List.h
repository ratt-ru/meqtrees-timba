//#  List.h: list of containers
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

#ifndef DMI_List_h
#define DMI_List_h 1

#include <DMI/DMI.h>
#include <DMI/Container.h>
#include <DMI/ObjectAssignerMacros.h>
#include <DMI/Allocators.h>

#pragma type #DMI::List

namespace DMI
{

//##Documentation
//## DMI::List is a list of containers

class List : public Container
{
  public:
      // No need to supply realtype to List constructor: the header block
      // is always re-generated within toBlock(), hence the right type is
      // always stored.
      
      List ();

      List (const List &other, int flags = 0, int depth = 0);

      ~List();

      List & operator= (const List &right);

      //##Documentation
      //## Returns the class TypeId
      virtual TypeId objectType () const
      { return TpDMIList; }
      
      //##Documentation
      //## put(n,...) puts object into list.
      //## if DMI::REPLACE flag is not specified:
      //##    inserts object before the specified position in list.
      //##    0: at front of list, -1: at back of list, -2: as second-last, etc.
      //## if DMI::REPLACE flag is specified:
      //##    replaces object at specified position in list.
      //##    0: first object, -1: last object, -2: second-last, etc.
      DMI_DeclareObjectAssigner(put,int);
      
      //##Documentation
      //## insert(n,...): alias for put() w/o DMI::REPLACE
      DMI_DeclareObjectAssigner(insert,int);
      
      //##Documentation
      //## replace(n,...): alias for put() with DMI::REPLACE
      DMI_DeclareObjectAssigner(replace,int);
      
      //##Documentation
      //## addFront(...) and addBack(...) insert at the beginning/end of list.
      DMI_DeclareObjectAssigner(addFront,Null);
      DMI_DeclareObjectAssigner(addBack,Null);
      
      
      //## appends everything from other list to end of this one
      //## Refs to fields are copy()d using the supplied flags.
      void append (const List &other,int flags=0);

      int numItems  () const
      { return items.size(); }
      
      ObjRef get    (int n) const;
      
      ObjRef remove (int n);

      //## accesses item #n as an object of the specified type,
      //## or throws an exception on mismatch
      template<class T>
      const T & as (int n,Type2Type<T> =Type2Type<T>()) const
      {
        Thread::Mutex::Lock lock(mutex());
        return (*applyIndexConst(n)).as<T>();
      }
      
      //## accesses item #n as a writable object of the specified type,
      //## or throws an exception on mismatch
      template<class T>
      T & as (int n,Type2Type<T> =Type2Type<T>()) 
      {
        Thread::Mutex::Lock lock(mutex());
        return (*applyIndex(n,false)).as<T>();
      }

      virtual int insert (const HIID &id,ContentInfo &info);

      virtual int remove (const HIID &id);

      virtual int size (TypeId tid = 0) const;

    // Additional Public Declarations
      typedef CountedRef<List> Ref;

      //##Documentation
      //## Creates object from a set of block references. Appropriate number of
      //## references are removed from the head of the BlockSet. Returns # of
      //## refs removed.
      virtual int fromBlock (BlockSet& set);

      //##Documentation
      //## Stores an object into a set of blocks. Appropriate number of refs
      //## added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

      //##Documentation
      //## Abstract method for cloning an object. Should return pointer to new
      //## object. Flags: WRITE if writable clone is required, DEEP
      //## for deep cloning (i.e. contents of object will be cloned as well).
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

      void cloneOther (const List &other, int flags, int depth, bool constructing);

      
            // debug info method
      string sdebug ( int detail = 0,const string &prefix = "",
                      const char *name = 0 ) const;

  protected:
      //##Documentation
      virtual int get (const HIID &id,ContentInfo &info,bool nonconst,int flags) const;

      //##Documentation
      //## Resolves HIID to a field. Sets can_write to true if field is writable. If
      //## must_write is true, throws an exception if something along the way
      //## is not writable.
      const ObjRef & resolveField (const HIID &id,bool &can_write, bool must_write = false) const;

  private:
      class Header : public BObj::Header
      {
        public: 
            int num_items;
            int item_bc[];
      };
      
      typedef std::list<ObjRef,DMI_Allocator<ObjRef> > ItemList;
      
      // Helper functions to apply an index (n).
      // If n<0, counts backwards from end of list as follows:
      //    if inserting=true, then n==-1 is end(); otherwise n==-1 is last item in list
      // If inserting is false, iterator always points to valid element
      ItemList::const_iterator applyIndexConst (int n) const;
      
      ItemList::iterator applyIndex (int n,bool inserting);
      
      ItemList items;
      
  public:
      typedef ItemList::const_iterator const_iterator;
      typedef ItemList::iterator iterator;
      
      // a List iterator simply iterates over refs in the list.
      // *iter will be an ObjRef
      const_iterator begin () const { return items.begin(); }
      const_iterator end () const   { return items.end(); }
      iterator begin ()             { return items.begin(); }
      iterator end ()               { return items.end(); }
};

inline void List::insert (int n,ObjRef &ref,int flags)
{ 
  put(n,ref,flags&~DMI::REPLACE); 
};

inline void List::replace (int n,ObjRef &ref,int flags)
{ 
  put(n,ref,flags|DMI::REPLACE); 
};

inline void List::addFront (ObjRef &ref,int flags)
{ 
  put(0,ref,flags); 
};

inline void List::addBack (ObjRef &ref,int flags)
{ 
  put(-1,ref,flags); 
};

};
#endif



//#  DataList.h: list of containers
//#
//#  Copyright (C) 2002-2003
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

#ifndef DMI_DataList_h
#define DMI_DataList_h 1

#include <DMI/DMI.h>
#include <DMI/NestableContainer.h>

#pragma type #DataList

//##Documentation
//## DataList is a list of containers

class DataList : public NestableContainer
{
  public:
      explicit DataList (int flags = DMI::WRITE);

      DataList (const DataList &other, int flags = DMI::PRESERVE_RW, int depth = 0);

      ~DataList();

      DataList & operator= (const DataList &right);

      //##Documentation
      //## Returns the class TypeId
      virtual TypeId objectType () const
      { return TpDataList; }

      void addFront (const NCRef &ref, int flags = DMI::XFER);
      void addFront (NestableContainer *pnc, int flags = DMI::ANONWR);
      void addFront (const NestableContainer *pnc, int flags = DMI::ANONRO)
      { addFront(const_cast<NestableContainer*>(pnc),(flags&~DMI::WRITE)|DMI::READONLY); }
          
      void addBack  (const NCRef &ref, int flags = DMI::XFER);
      void addBack  (NestableContainer *pnc, int flags = DMI::ANONWR);
      void addBack  (const NestableContainer *pnc, int flags = DMI::ANONRO)
      { addBack(const_cast<NestableContainer*>(pnc),(flags&~DMI::WRITE)|DMI::READONLY); }

      void replace  (int n, const NCRef &ref, int flags = DMI::XFER);
      void replace  (int n, NestableContainer *pnc, int flags = DMI::ANONWR);

      void replace  (int n, const NestableContainer *pnc, int flags = DMI::ANONRO)
      { replace(n,const_cast<NestableContainer*>(pnc),(flags&~DMI::WRITE)|DMI::READONLY); }

      // appends everything from other list to end of this one, as read-only
      void append (const DataList &other,int flags=DMI::READONLY);
      // same version, but preserves writability
      void append (DataList &other,int flags=DMI::PRESERVE_RW);

      int numItems  () const
      { return items.size(); }
      
      NCRef getItem   (int n) const;

      NCRef getItemWr (int n, int flags = DMI::PRESERVE_RW);
      
      NCRef remove    (int n);

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
      //## object. Flags: DMI::WRITE if writable clone is required, DMI::DEEP
      //## for deep cloning (i.e. contents of object will be cloned as well).
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

      //##Documentation
      //## Virtual method for privatization of an object. If the object
      //## contains other refs, they should be privatized by this method. The
      //## DMI::DEEP flag should be passed on to child refs, for deep
      //## privatization.
      virtual void privatize (int flags = 0, int depth = 0);

      void cloneOther (const DataList &other, int flags, int depth);

      virtual int insert (const HIID &id,ContentInfo &info);

      virtual int remove (const HIID &id);

      virtual int size (TypeId tid = 0) const;

    // Additional Public Declarations
      DefineRefTypes(DataList,Ref);

      // debug info method
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;

  protected:
      //##Documentation
      virtual int get (const HIID &id,ContentInfo &info,bool nonconst,int flags) const;


      //##Documentation
      //## Resolves HIID to a field. Sets can_write to True if field is writable. If
      //## must_write is True, throws an exception if something along the way
      //## is not writable.
      const NCRef & resolveField (const HIID &id,HIID &rest,bool &can_write, bool must_write = False) const;

  private:
      typedef std::list<NCRef> ItemList;
      
      const NCRef & applyIndexConst (int n) const;
      
      NCRef &       applyIndex      (int n)
      { return const_cast<NCRef&>(applyIndexConst(n)); }
      
      ItemList::iterator applyIndexIter (int n);
      
      ItemList items;
};

DefineRefTypes(DataList,DataListRef);

// Class DataList 


#endif



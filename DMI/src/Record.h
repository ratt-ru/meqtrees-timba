//#  Record.h: record of containers
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

#ifndef DMI_Record_h
#define DMI_Record_h 1

#include <DMI/DMI.h>
#include <DMI/Container.h>
#include <DMI/ObjectAssignerMacros.h>
#include <DMI/HashMap.h>
#include <DMI/Allocators.h>

#include <functional>

#pragma type #DMI::Record

namespace DMI_hash_namespace
{

template<>
struct hash<DMI::HIID> 
{
  size_t operator () (const DMI::HIID &x) const
  {
    size_t h = 0;
    int bits = 0;
    for( DMI::HIID::const_iterator p = x.begin(); p < x.end(); ++p )
    {
      uint a = p->id();
      h ^= (a<<bits) | (a>>(32-bits));
      bits = (bits+8)%32;
    }
    return h;
  }
};

};

//##ModelId=3BB3112B0027
//##Documentation
//## DMI::Record is a record container class

namespace DMI
{

class Record : public Container
{
  public:
      
      class Field
      {
        public:
          Field ()
            : protected_(false)
          {}
        
          Field (const Field &other)
          { copy(other); }
          
          Field & operator = (const Field &other)
          { return copy(other); }
        
          // copies other field into this one
          Field & copy (const Field &other,int flags=0,int depth=0);

          // Protected fields cannot be removed or modified via public methods
          // (i.e. these fields can only be managed by derived classes)
          bool isProtected () const
          { return protected_;}
        
          // raises/clears the protected flag
          void protect (bool prot=true) 
          { protected_ = prot; }
          
          // clears the protected flag
          void unprotect () 
          { protected_ = false; }
          
          // true if field has contents
          bool valid () const
          { return ref_.valid() || !bset_.empty(); }
          
          // attaches object to field
          void attach (ObjRef &ref,int flags);
          
          // attaches a packed object (i.e. a BlockSet) to field
          // If num_blocks<0, attaches whole bset
          // else pops the first num_blocks from bset
          void fromBlock (BlockSet &bset,int num_blocks=-1);
          
          // packs field content into blockset, adding blocks to end
          // of set. Returns the number of blocks packed.
          int toBlock (BlockSet &bset) const;
          
          // clears field
          void clear ()
          { ref_.detach(); bset_.clear(); }
          
          // returns ref to object
          const ObjRef & ref () const
          { 
            if( !ref_.valid() ) 
              makeObject(); 
            return ref_; 
          }
          
          // returns non-const ref to object
          ObjRef & ref ()
          { 
            if( !ref_.valid() ) 
              makeObject(); 
            return ref_; 
          }
          
          // clears the field, but xfers the ref into out
          void xfer (ObjRef &out)
          {
            makeObject();
            out.xfer(ref_);
            clear();
          }
          
        private:
          void makeObject () const;
            
          ObjRef   ref_;
          BlockSet bset_;
          bool     protected_;
      };
      
  protected:
      typedef DMI_Allocator<Field> FieldAllocator;

      typedef hash_map<HIID,Field,DMI_hash_namespace::hash<HIID>,std::equal_to<HIID>,FieldAllocator > FieldMap; 
  
      
  public:
      typedef CountedRef<Record> Ref;
  
      typedef enum 
      {
        // this flag when passed to addField will create a protected field.
        // a protected field may not be written to or changed via the public
        // access methods
        PROTECT         =0x10000000,  
        // this flag is implictly added by all public access methods
        // so that field protection is honored.
        // The private/protected methods do not add this flag, and thus
        // subclasses can override field protection
        HONOR_PROTECT   =0x20000000,  
      } RecordFlags;
  
      // No need to supply realtype to Record constructor: the header block
      // is always re-generated within toBlock(), hence the right type is
      // always stored.
      //##ModelId=3C5820AD00C6
      Record ();

      //##ModelId=3C5820C7031D
      Record (const Record &other, int flags = 0, int depth = 0);

    //##ModelId=3DB93482018E
      ~Record();

    //##ModelId=3DB93482022F
      Record & operator = (const Record &right);
      
      void clear ();

      //##ModelId=3C58248C0232
      //##Documentation
      //## Returns the class TypeId
      virtual TypeId objectType () const;
      
    //##ModelId=400E4D6B00B9
      bool hasField (const HIID &id) const
      { return fields.find(id) != fields.end(); }

      //##ModelId=3C57CFFF005E
      ObjRef get (const HIID &id,bool ignore_fail=false) const;
      
      template<class T>
      const T & as (const HIID &id,Type2Type<T> =Type2Type<T>()) const
      {
        Thread::Mutex::Lock lock(mutex());
        const Field * pf = findField(id);
        FailWhen(!pf,"field "+id.toString()+" not found");
        return pf->ref().as<T>();
      }
      
      template<class T>
      T & as (const HIID &id,Type2Type<T> =Type2Type<T>()) 
      {
        Thread::Mutex::Lock lock(mutex());
        Field * pf = findField(id);
        FailWhen(!pf,"field "+id.toString()+" not found");
        FailWhen(pf->isProtected(),"field "+id.toString()+" is protected for writing");
        return pf->ref().as<T>();
      }
      
      template<class T>
      const T * as_po (const HIID &id,Type2Type<T> =Type2Type<T>()) const
      {
        Thread::Mutex::Lock lock(mutex());
        const Field * pf = findField(id);
        if( !pf )
          return 0;
        return &( pf->ref().as<T>() );
      }
      
      template<class T>
      T * as_po (const HIID &id,Type2Type<T> =Type2Type<T>()) 
      {
        Thread::Mutex::Lock lock(mutex());
        Field * pf = findField(id);
        if( !pf )
          return 0;
        FailWhen(pf->isProtected(),"field "+id.toString()+" is protected for writing");
        return &( pf->ref().as<T>() );
      }
      
    //##ModelId=400E4D6903B8
      //##Documentation
      //## merges other record into this one (adds all its fields).
      //## If overwrite is true, overwrites existing fields, else skips
      //## them. Refs to fields are copy()d using the supplied flags.
      void merge (const Record &other,bool overwrite=true,int flags=0); 
      

      //##Documentation
      //## add(...) inserts a new field into container.
      //## The DMI::REPLACE flag allows overwriting of existing fields
      //## (default is to throw exception).
      //## The DMI::PROTECT flag inserts a protected field: a protected
      //## field cannot be modified or removed (this is useful for derived
      //## classes that enforce a fixed record structure)
      DMI_DeclareObjectAssigner(add,HIID);
      
      //##Documentation
      //## insert(n,...): alias for add() w/o DMI::REPLACE
      DMI_DeclareObjectAssigner(insert,HIID);
      
      //##Documentation
      //## replace(n,...): alias for add() with DMI::REPLACE
      DMI_DeclareObjectAssigner(replace,HIID);
      
      //##Documentation
      //## marks a field as protected
      void protectField   (const HIID &id,bool protect=true);
      //##Documentation
      //## marks a field as unprotected
      void unprotectField (const HIID &id)
      { protectField(id,false); }
      
      //##ModelId=3BB311C903BE
      //##Documentation
      //## Removes data field from container and returns a ref to the removed
      //## field. Throws exception if no such field and ignore_fail=false
      ObjRef removeField (const HIID &id,bool ignore_fail=false)
      { return removeField(id,ignore_fail,HONOR_PROTECT); }

      //##ModelId=3C7A16BB01D7
      virtual int insert (const HIID &id,ContentInfo &info);

      //##ModelId=3C877D140036
      virtual int remove (const HIID &id);

      //##ModelId=3C7A16C4023F
      virtual int size (TypeId tid = 0) const;

      //##ModelId=3C58216302F9
      //##Documentation
      //## Creates object from a set of block references. Appropriate number of
      //## references are removed from the head of the BlockSet. Returns # of
      //## refs removed.
      virtual int fromBlock (BlockSet& set);

      //##ModelId=3C5821630371
      //##Documentation
      //## Stores an object into a set of blocks. Appropriate number of refs
      //## added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

      //##ModelId=3C58218900EB
      //##Documentation
      //## Abstract method for cloning an object. Should return pointer to new
      //## object. Flags: DMI::DEEP for deep cloning (i.e. contents of object  
      //## will be cloned as well).
      virtual CountedRefTarget * clone (int flags = 0, int depth = 0) const;

      //##ModelId=3C58239503D1
      void cloneOther (const Record &other, int flags, int depth, bool constructing);

      // debug info method
    //##ModelId=3DB9348501B1
      string sdebug ( int detail = 0,const string &prefix = "",
                      const char *name = 0 ) const;
      
    //##ModelId=3DB9343B029A
      class ConstIterator : public FieldMap::const_iterator
      {
        private:
          friend class Record;
#ifdef USE_THREADS
        //##ModelId=3DB934810398
          Thread::Mutex::Lock lock;
#endif
          ConstIterator (const Record &record);       // construct begin-iter
          ConstIterator (const Record &record,bool);  // constructs end-iter
          
          FieldMap::const_iterator::operator *;
          FieldMap::const_iterator::operator ->;
                    
        public:
          const HIID & id () const
          { return (*this)->first; }
            
          bool isProtected () const
          { return (*this)->second.isProtected(); }
        
          const ObjRef & ref () const
          { return (*this)->second.ref(); }
          
          const Field & field () const
          { return (*this)->second; }
      };
      
    //##ModelId=3DB9343B029A
      class Iterator : public FieldMap::iterator
      {
        private:
          friend class Record;
#ifdef USE_THREADS
        //##ModelId=3DB934810398
          Thread::Mutex::Lock lock;
#endif
          Iterator (Record &record);       // construct begin-iter
          Iterator (Record &record,bool);  // constructs end-iter
          
          FieldMap::iterator::operator *;
          FieldMap::iterator::operator ->;
                    
        public:
          const HIID & id () const
          { return (*this)->first; }
            
          bool isProtected () const
          { return (*this)->second.isProtected(); }
        
          const ObjRef & ref () const
          { return (*this)->second.ref(); }
          
          Field & field () 
          { return (*this)->second; }
          
          void protect (bool protect=true)
          { (*this)->second.protect(protect); }

          void unprotect (bool unprotect=true)
          { (*this)->second.protect(!unprotect); }
      };
      
      friend class ConstIterator;
      friend class Iterator;
      typedef ConstIterator const_iterator;
      typedef Iterator iterator;
      
      ConstIterator begin () const
      { return ConstIterator(*this); }
      
      Iterator begin ()
      { return Iterator(*this); }
      
      ConstIterator end () const
      { return ConstIterator(*this,true); }
      
      Iterator end ()
      { return Iterator(*this,true); }


  protected:
      // implements an as<> operation that overrides protection
      template<class T>
      T & as1 (const HIID &id,Type2Type<T> =Type2Type<T>()) 
      {
        Thread::Mutex::Lock lock(mutex());
        Field * pf = findField(id);
        FailWhen(!pf,"field "+id.toString()+" not found");
        return pf->ref().as<T>();
      }
      
      // implements the add operation
      Field & addField (const HIID &id, ObjRef &ref, int flags);
  
      Field & addField (const HIID &id, BObj *obj, int flags)
      { ObjRef ref(obj,flags); return addField(id,ref,flags); }
      
      Field & addField (const HIID &id, const BObj *obj, int flags)
      { ObjRef ref(obj,flags); return addField(id,ref,flags); }
      
      Field & addField (const HIID &id, const ObjRef &ref, int flags)
      { ObjRef ref1(ref,flags); return addField(id,ref1,flags); }
  
      ObjRef removeField (const HIID &id,bool ignore_fail,int flags);
      
      Field * findField (const HIID &id)
      {
        FMI iter = fields.find(id);
        return iter == fields.end() ? 0 : &(iter->second);
      }
      
      const Field * findField (const HIID &id) const
      {
        CFMI iter = fields.find(id);
        return iter == fields.end() ? 0 : &(iter->second);
      }
      
      //##ModelId=3C56B00E0182
      //##Documentation
      virtual int get (const HIID &id,ContentInfo &info,bool nonconst,int flags) const;

      //##ModelId=3C552E2D009D
      //##Documentation
      //## Resolves HIID to a field. Sets can_write to true if field is writable. If
      //## must_write is true, throws an exception if something along the way
      //## is not writable.
      const ObjRef & resolveField (const HIID &id,bool &can_write, bool must_write = false) const;
      
      //##ModelId=3E9BD86202A0
      FieldMap fields;

    // Additional Implementation Declarations
    //##ModelId=3DB9343B02FE
      typedef FieldMap::iterator FMI;
    //##ModelId=3DB9343B03D1
      typedef FieldMap::const_iterator CFMI;
    //##ModelId=3DB9343C00B1
      typedef FieldMap::value_type FMV;
      
    //##ModelId=3E9BD8620215
      typedef struct { int idsize; int blockcount; } BlockFieldInfo;
      
      class Header : public BObj::Header
      {
        public: 
          int             num_fields;
          BlockFieldInfo  fields[];
      };
};


//##ModelId=3C58248C0232
inline TypeId Record::objectType () const
{
  return TpDMIRecord;
}

//##ModelId=3DB9348103A0
inline Record::ConstIterator::ConstIterator (const Record &rec)
  : FieldMap::const_iterator(rec.fields.begin())
#ifdef USE_THREADS
    ,lock(rec.mutex())
#endif
{
}

//##ModelId=3DB9348103A0
inline Record::ConstIterator::ConstIterator (const Record &rec,bool)
  : FieldMap::const_iterator(rec.fields.end())
{
}

inline Record::Iterator::Iterator (Record &rec)
  : FieldMap::iterator(rec.fields.begin())
#ifdef USE_THREADS
    ,lock(rec.mutex())
#endif
{}

inline Record::Iterator::Iterator (Record &rec,bool)
  : FieldMap::iterator(rec.fields.end())
#ifdef USE_THREADS
    ,lock(rec.mutex())
#endif
{}

inline void Record::add (const HIID &id,ObjRef &ref,int flags)
{ addField(id,ref,flags|HONOR_PROTECT); };

inline void Record::insert (const HIID &id,ObjRef &ref,int flags)
{ addField(id,ref,(flags&~DMI::REPLACE)|HONOR_PROTECT); };

inline void Record::replace (const HIID &id,ObjRef &ref,int flags)
{ addField(id,ref,flags|DMI::REPLACE|HONOR_PROTECT); };

}; // namespace DMI


#endif



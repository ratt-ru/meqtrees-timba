#ifndef DMI_DataRecord_h
#define DMI_DataRecord_h 1

#include <DMI/DMI.h>
#include <DMI/NestableContainer.h>
#include <DMI/HIID.h>
#include <DMI/DataField.h>

#pragma type #DataRecord

//##ModelId=3BB3112B0027
//##Documentation
//## DataRecord is the main container class of DMI.

class DataRecord : public NestableContainer
{
  public:
      friend class DataField;
    //##ModelId=3DB9343B029A
      class Iterator
      {
        private:
        //##ModelId=3DB934810397
          map<HIID,NCRef>::const_iterator iter;
#ifdef USE_THREADS
        //##ModelId=3DB934810398
          Thread::Mutex::Lock lock;
#endif
        //##ModelId=3DB9348103A0
          Iterator( const DataRecord &record );
          
          friend class DataRecord;
      };
      
      friend class Iterator;

  public:
      //##ModelId=3C5820AD00C6
      explicit DataRecord (int flags = DMI::WRITE);

      //##ModelId=3C5820C7031D
      DataRecord (const DataRecord &other, int flags = DMI::PRESERVE_RW, int depth = 0);

    //##ModelId=3DB93482018E
      ~DataRecord();

    //##ModelId=3DB93482022F
      DataRecord & operator=(const DataRecord &right);

      //##ModelId=3C58248C0232
      //##Documentation
      //## Returns the class TypeId
      virtual TypeId objectType () const;

      //##ModelId=3BFBF5B600EB
      void add (const HIID &id, const NCRef &ref, int flags = DMI::XFER);

      //##ModelId=3C5FF0D60106
      void add (const HIID &id, NestableContainer *pfld, int flags = DMI::WRITE|DMI::ANON);

      //##ModelId=3BB311C903BE
      //##Documentation
      //## Removes data field from container and returns a ref to the removed
      //## field
      NCRef removeField (const HIID &id);

      //##ModelId=3BFCD4BB036F
      void replace (const HIID &id, const NCRef &ref, int flags = DMI::XFER);

      //##ModelId=3C5FF10102CA
      void replace (const HIID &id, NestableContainer *pfld, int flags = DMI::WRITE|DMI::ANON);

      //##ModelId=3C57D02B0148
      //##Documentation
      //## Returns true if id refers to a valid DataField (i.e., that can be
      //## fetched with field()). Throws no exceptions.
      bool isDataField (const HIID &id) const;
    //##ModelId=3E9BD86203AC
      //##Documentation
      //## Returns true if id refers to a valid DataArray (i.e., that can be
      //## fetched with field()). Throws no exceptions.
      bool isDataArray (const HIID &id) const;

      //##ModelId=3C57CFFF005E
      NCRef field (const HIID &id) const;
      
      //##ModelId=3BFBF49D00A1
      NCRef fieldWr (const HIID &id, int flags = DMI::PRESERVE_RW);

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
      //## object. Flags: DMI::WRITE if writable clone is required, DMI::DEEP
      //## for deep cloning (i.e. contents of object will be cloned as well).
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

      //##ModelId=3C582189019F
      //##Documentation
      //## Virtual method for privatization of an object. If the object
      //## contains other refs, they should be privatized by this method. The
      //## DMI::DEEP flag should be passed on to child refs, for deep
      //## privatization.
      virtual void privatize (int flags = 0, int depth = 0);

      //##ModelId=3C58239503D1
      void cloneOther (const DataRecord &other, int flags, int depth);

      //##ModelId=3C56B00E0182
      //##Documentation
      //## Implemetation of standard function for deep-dereferencing of
      //## contents.
      //## See NestableContainer for semantics.
      virtual const void * get (const HIID &id, ContentInfo &info, TypeId check_tid = 0, int flags = 0) const;

      //##ModelId=3C7A16BB01D7
      virtual void * insert (const HIID &id, TypeId tid, TypeId &real_tid);

      //##ModelId=3C877D140036
      //##Documentation
      //## Implementation of remove() for Hooks (see NestableContainer).
      virtual bool remove (const HIID &id);

      //##ModelId=3C7A16C4023F
      virtual int size (TypeId tid = 0) const;

      //##ModelId=3CA20ACE00F8
      DataRecord::Iterator initFieldIter () const;

      //##ModelId=3CA20AD703A4
      bool getFieldIter (DataRecord::Iterator& iter, HIID& id, NCRef &ref) const;

    // Additional Public Declarations
    //##ModelId=3DB9348401EB
      DefineRefTypes(DataRecord,Ref);
      
      // debug info method
    //##ModelId=3DB9348501B1
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      
  protected:

      //##ModelId=3C552E2D009D
      //##Documentation
      //## Resolves HIID to a field. Sets can_write to True if field is writable. If
      //## must_write is True, throws an exception if something along the way
      //## is not writable.
      const NCRef & resolveField (const HIID &id,HIID &rest,bool &can_write, bool must_write = False) const;

  private:
    // Data Members for Associations

      //##ModelId=3E9BD86202A0
      map<HIID,NCRef> fields;

    // Additional Implementation Declarations
    //##ModelId=3DB9343B02FE
      typedef map<HIID,NCRef>::iterator FMI;
    //##ModelId=3DB9343B03D1
      typedef map<HIID,NCRef>::const_iterator CFMI;
    //##ModelId=3DB9343C00B1
      typedef map<HIID,NCRef>::value_type FMV;
      
    //##ModelId=3E9BD8620215
      typedef struct { int idsize; int ftype; } BlockFieldInfo;
};

DefineRefTypes(DataRecord,DataRecordRef);

// Class DataRecord 


//##ModelId=3C58248C0232
inline TypeId DataRecord::objectType () const
{
  return TpDataRecord;
}

//##ModelId=3C5FF0D60106
inline void DataRecord::add (const HIID &id, NestableContainer *pfld, int flags)
{
  add(id,NCRef(pfld,flags));
}

//##ModelId=3C5FF10102CA
inline void DataRecord::replace (const HIID &id,  NestableContainer *pfld, int flags)
{
  replace(id,NCRef(pfld,flags));
}

//##ModelId=3CA20ACE00F8
inline DataRecord::Iterator DataRecord::initFieldIter () const
{
  
  return Iterator(*this);
}

//##ModelId=3DB9348103A0
inline DataRecord::Iterator::Iterator (const DataRecord &rec)
#ifdef USE_THREADS
    : lock(rec.mutex())
#endif
{
  iter = rec.fields.begin();
}


#endif



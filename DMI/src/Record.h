//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820052.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820052.cm

//## begin module%3C10CC820052.cp preserve=no
//## end module%3C10CC820052.cp

//## Module: DataRecord%3C10CC820052; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\DataRecord.h

#ifndef DataRecord_h
#define DataRecord_h 1

//## begin module%3C10CC820052.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC820052.additionalIncludes

//## begin module%3C10CC820052.includes preserve=yes
#pragma type #DataRecord
//## end module%3C10CC820052.includes

// NestableContainer
#include "NestableContainer.h"
// HIID
#include "HIID.h"
// DataField
#include "DataField.h"
//## begin module%3C10CC820052.declarations preserve=no
//## end module%3C10CC820052.declarations

//## begin module%3C10CC820052.additionalDeclarations preserve=yes
//## end module%3C10CC820052.additionalDeclarations


//## begin DataRecord%3BB3112B0027.preface preserve=yes
//## end DataRecord%3BB3112B0027.preface

//## Class: DataRecord%3BB3112B0027
//	DataRecord is the main container class of DMI.
//## Category: DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BFCD23E02FB;HIID { -> }

class DataRecord : public NestableContainer  //## Inherits: <unnamed>%3BFCD87E039E
{
  //## begin DataRecord%3BB3112B0027.initialDeclarations preserve=yes
  public:
      friend DataField;
      typedef map<HIID,DataFieldRef>::const_iterator Iterator;
  //## end DataRecord%3BB3112B0027.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: DataRecord%3C5820AD00C6
      DataRecord (int flags = DMI::WRITE);

      //## Operation: DataRecord%3C5820C7031D
      DataRecord (const DataRecord &other, int flags = 0, int depth = 0);

    //## Destructor (generated)
      ~DataRecord();

    //## Assignment Operation (generated)
      DataRecord & operator=(const DataRecord &right);


    //## Other Operations (specified)
      //## Operation: objectType%3C58248C0232
      //	Returns the class TypeId
      virtual TypeId objectType () const;

      //## Operation: add%3BFBF5B600EB
      void add (const HIID &id, const DataFieldRef &ref, int flags = DMI::XFER);

      //## Operation: add%3C5FF0D60106
      void add (const HIID &id, DataField *pfld, int flags = DMI::WRITE|DMI::ANON);

      //## Operation: removeField%3BB311C903BE
      //	Removes data field from container and returns a ref to the removed
      //	field
      DataFieldRef removeField (const HIID &id);

      //## Operation: replace%3BFCD4BB036F
      void replace (const HIID &id, const DataFieldRef &ref, int flags = DMI::XFER);

      //## Operation: replace%3C5FF10102CA
      void replace (const HIID &id, DataField *pfld, int flags = DMI::WRITE|DMI::ANON);

      //## Operation: field%3C57CFFF005E
      DataFieldRef field (const HIID &id) const;

      //## Operation: isDataField%3C57D02B0148
      //	Returns true if id refers to a valid DataField (i.e., that can be
      //	fetched with field()). Throws no exceptions.
      bool isDataField (const HIID &id) const;

      //## Operation: fieldWr%3BFBF49D00A1
      DataFieldRef fieldWr (const HIID &id, int flags = DMI::PRESERVE_RW);

      //## Operation: fromBlock%3C58216302F9
      //	Creates object from a set of block references. Appropriate number of
      //	references are removed from the head of the BlockSet. Returns # of
      //	refs removed.
      virtual int fromBlock (BlockSet& set);

      //## Operation: toBlock%3C5821630371
      //	Stores an object into a set of blocks. Appropriate number of refs
      //	added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

      //## Operation: clone%3C58218900EB; C++
      //	Abstract method for cloning an object. Should return pointer to new
      //	object. Flags: DMI::WRITE if writable clone is required, DMI::DEEP
      //	for deep cloning (i.e. contents of object will be cloned as well).
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

      //## Operation: privatize%3C582189019F
      //	Virtual method for privatization of an object. If the object
      //	contains other refs, they should be privatized by this method. The
      //	DMI::DEEP flag should be passed on to child refs, for deep
      //	privatization.
      virtual void privatize (int flags = 0, int depth = 0);

      //## Operation: cloneOther%3C58239503D1
      void cloneOther (const DataRecord &other, int flags, int depth);

      //## Operation: get%3C56B00E0182
      //	Implemetation of standard function for deep-dereferencing of
      //	contents.
      //	See NestableContainer for semantics.
      virtual const void * get (const HIID &id, TypeId& tid, bool& can_write, TypeId check_tid = 0, bool must_write = False) const;

      //## Operation: insert%3C7A16BB01D7
      virtual void * insert (const HIID &id, TypeId tid, TypeId &real_tid);

      //## Operation: remove%3C877D140036
      //	Implementation of remove() for Hooks (see NestableContainer).
      virtual bool remove (const HIID &id);

      //## Operation: size%3C7A16C4023F
      virtual int size () const;

      //## Operation: type%3C7A16CB023F
      virtual TypeId type () const;

      //## Operation: initFieldIter%3CA20ACE00F8
      DataRecord::Iterator initFieldIter () const;

      //## Operation: getFieldIter%3CA20AD703A4
      bool getFieldIter (DataRecord::Iterator& iter, HIID& id, TypeId& type, int& size) const;

    // Additional Public Declarations
      //## begin DataRecord%3BB3112B0027.public preserve=yes
      // debug info method
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      
      //## end DataRecord%3BB3112B0027.public
  protected:

    //## Other Operations (specified)
      //## Operation: resolveField%3C552E2D009D
      //	Resolves HIID to a field using longest-match, returns remaining
      //	atoms in rest, and sets can_write to True if field is writable. If
      //	must_write is True, throws an exception if something along the way
      //	is not writable.
      const DataFieldRef & resolveField (const HIID &id, HIID& rest, bool &can_write, bool must_write = False) const;

    // Additional Protected Declarations
      //## begin DataRecord%3BB3112B0027.protected preserve=yes
      //## end DataRecord%3BB3112B0027.protected

  private:
    // Additional Private Declarations
      //## begin DataRecord%3BB3112B0027.private preserve=yes
      //## end DataRecord%3BB3112B0027.private

  private: //## implementation
    // Data Members for Associations

      //## Association: PSCF::<unnamed>%3BE123050350
      //## Role: DataRecord::fields%3BE123060149
      //## begin DataRecord::fields%3BE123060149.role preserve=no  private: DataField { -> 0..nVHgN}
      map<HIID,DataFieldRef> fields;
      //## end DataRecord::fields%3BE123060149.role

    // Additional Implementation Declarations
      //## begin DataRecord%3BB3112B0027.implementation preserve=yes
      typedef map<HIID,DataFieldRef>::iterator FMI;
      typedef map<HIID,DataFieldRef>::const_iterator CFMI;
      typedef map<HIID,DataFieldRef>::value_type FMV;
      //## end DataRecord%3BB3112B0027.implementation
};

//## begin DataRecord%3BB3112B0027.postscript preserve=yes
//## end DataRecord%3BB3112B0027.postscript

// Class DataRecord 


//## Other Operations (inline)
inline TypeId DataRecord::objectType () const
{
  //## begin DataRecord::objectType%3C58248C0232.body preserve=yes
  return TpDataRecord;
  //## end DataRecord::objectType%3C58248C0232.body
}

inline void DataRecord::add (const HIID &id, DataField *pfld, int flags)
{
  //## begin DataRecord::add%3C5FF0D60106.body preserve=yes
  add(id,DataFieldRef(pfld,flags));
  //## end DataRecord::add%3C5FF0D60106.body
}

inline void DataRecord::replace (const HIID &id, DataField *pfld, int flags)
{
  //## begin DataRecord::replace%3C5FF10102CA.body preserve=yes
  replace(id,DataFieldRef(pfld,flags));
  //## end DataRecord::replace%3C5FF10102CA.body
}

inline int DataRecord::size () const
{
  //## begin DataRecord::size%3C7A16C4023F.body preserve=yes
  return fields.size();
  //## end DataRecord::size%3C7A16C4023F.body
}

inline TypeId DataRecord::type () const
{
  //## begin DataRecord::type%3C7A16CB023F.body preserve=yes
  return NullType;
  //## end DataRecord::type%3C7A16CB023F.body
}

inline DataRecord::Iterator DataRecord::initFieldIter () const
{
  //## begin DataRecord::initFieldIter%3CA20ACE00F8.body preserve=yes
  return fields.begin();
  //## end DataRecord::initFieldIter%3CA20ACE00F8.body
}

//## begin module%3C10CC820052.epilog preserve=yes
//## end module%3C10CC820052.epilog


#endif

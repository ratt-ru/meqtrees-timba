//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820124.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820124.cm

//## begin module%3C10CC820124.cp preserve=no
//## end module%3C10CC820124.cp

//## Module: DataField%3C10CC820124; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DataField.h

#ifndef DataField_h
#define DataField_h 1

//## begin module%3C10CC820124.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC820124.additionalIncludes

//## begin module%3C10CC820124.includes preserve=yes
#include "TID.h"
//## end module%3C10CC820124.includes

// BlockSet
#include "BlockSet.h"
// BlockableObject
#include "BlockableObject.h"
//## begin module%3C10CC820124.declarations preserve=no
//## end module%3C10CC820124.declarations

//## begin module%3C10CC820124.additionalDeclarations preserve=yes

#pragma typegroup Global
#pragma types DataField
//## end module%3C10CC820124.additionalDeclarations


//## begin DataField%3BB317D8010B.preface preserve=yes
//## end DataField%3BB317D8010B.preface

//## Class: DataField%3BB317D8010B
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BEBD95D007B;BlockSet { -> }

class DataField : public BlockableObject  //## Inherits: <unnamed>%3C1F711B0122
{
  //## begin DataField%3BB317D8010B.initialDeclarations preserve=yes
  //## end DataField%3BB317D8010B.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: DataField%3C3D64DC016E
      explicit DataField (int flags = DMI::WRITE);

      //## Operation: DataField%3C3EE3EA022A
      DataField (const DataField &right, int flags = 0);

      //## Operation: DataField%3BFA54540099
      //	Constructs an empty data field
      DataField (TypeId tid, int num = 1, int flags = DMI::WRITE);

    //## Destructor (generated)
      ~DataField();

    //## Assignment Operation (generated)
      DataField & operator=(const DataField &right);


    //## Other Operations (specified)
      //## Operation: objectType%3C3EC27F0227
      //	Returns the class TypeId
      virtual TypeId objectType () const;

      //## Operation: destroy%3C3EAB99018D
      void destroy ();

      //## Operation: isValid%3C3EB9B902DF
      bool isValid (int n = 0);

      //## Operation: get%3C5FB272037E
      const void * get (int n, TypeId& tid, bool& can_write, TypeId check_tid, bool must_write) const;

      //## Operation: get%3C56B1DA0057
      const void * get (int n = 0, TypeId check = 0, Bool must_write = False) const;

      //## Operation: operator []%3BFCFA1503B1
      const void* operator [] (int n) const;

      //## Operation: getWr%3BFCFA2902FB
      void* getWr (int n = 0, TypeId check = 0);

      //## Operation: operator []%3C5FBBEA015C
      void * operator [] (int n);

      //## Operation: objwr%3C0E4619019A
      ObjRef objwr (int n = 0, int flags = DMI::PRESERVE_RW);

      //## Operation: objref%3C3C8D7F03D8
      ObjRef objref (int n = 0) const;

      //## Operation: put%3C3C84A40176
      //	Inserts an object (by ref) into field at poisition n. This will
      //	transfer the ref to the field, so pass in a ref.copy() if you need
      //	to retain one.
      void put (const ObjRef &obj, int n = 0, int flags = DMI::XFER);

      //## Operation: remove%3C3EC3470153
      //	Removes object from field at position n, and returns ref to it.
      ObjRef remove (int n = 0);

      //## Operation: fromBlock%3C3D5F2001DC
      //	Creates object from a set of block references. Appropriate number of
      //	references are removed from the head of the BlockSet. Returns # of
      //	refs removed.
      virtual int fromBlock (BlockSet& set);

      //## Operation: toBlock%3C3D5F2403CC
      //	Stores an object into a set of blocks. Appropriate number of refs
      //	added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

      //## Operation: clone%3C3EC77D02B1; C++
      //	Clones a data field. (See CountedRefTarget::clone() for semantics)
      virtual CountedRefTarget* clone (int flags = 0) const;

      //## Operation: cloneOther%3C3EE42D0136
      void cloneOther (const DataField &other, int flags = 0);

      //## Operation: privatize%3C3EDEBC0255
      //	Makes a private snapshot of the field, by privatizing all contents.
      //	Use DMI::WRITE to make a writable field.
      void privatize (int flags = 0);

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: mytype%3BB317E3002B
      const TypeId type () const;

      //## Attribute: mysize%3C3D60C103DA
      const int size () const;

      //## Attribute: selected%3BEBE89602BC
      const bool isSelected () const;

      //## Attribute: writable%3BFCD90E0110
      const bool isWritable () const;

    // Additional Public Declarations
      //## begin DataField%3BB317D8010B.public preserve=yes
      typedef CountedRef<DataField> Ref;
      
      // templated getf() and getfwr() methods provide an alternative interface
      template<class T> const T * getf( int n = 0 ) const
      { return (const T *) get(n,type2id(T)); }
      
      template<class T> T * getfwr( int n = 0 ) 
      { return (T *) getWr(n,type2id(T)); }

      // debug info method
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      
      //## end DataField%3BB317D8010B.public
  protected:

    //## Other Operations (specified)
      //## Operation: resolveObject%3C3D8C07027F
      ObjRef & resolveObject (int n, bool write) const;

    // Additional Protected Declarations
      //## begin DataField%3BB317D8010B.protected preserve=yes
      //## end DataField%3BB317D8010B.protected

  private:
    // Additional Private Declarations
      //## begin DataField%3BB317D8010B.private preserve=yes
      // verifies that index is in range
      void checkIndex ( int n ) const;
      
      // header block, maintained as a SmartBlock. Contains type and size
      // info. For built-in types, also contains the data block itself.
      // For dynamic objects, contains info on # of blocks per each object
      mutable BlockRef headref;
      
      // state of each object - still in block / unblocked / modified
      typedef enum { UNINITIALIZED,INBLOCK,UNBLOCKED,MODIFIED } ObjectState;
      mutable vector<int> objstate;

      // vector of strings, for the special case of a Tpstring field
      vector<string> strvec;
      mutable bool strvec_modified; // flag: has been modified
      typedef vector<string>::iterator VSI;
      typedef vector<string>::const_iterator CVSI;
      
      // flag: field contains a built-in type
      bool built_in;
      
      // inlines for accessing the header block
      int & headerType () const { return ((int*)headref->data())[0]; }
      int & headerSize () const { return ((int*)headref->data())[1]; }
      int & headerBlockSize (int n) const { return ((int*)headref->data())[2+n]; }
      void * headerData () const { return &headerBlockSize(0); }
      
      //## end DataField%3BB317D8010B.private
  private: //## implementation
    // Data Members for Class Attributes

      //## begin DataField::mytype%3BB317E3002B.attr preserve=no  public: TypeId {U} 
      TypeId mytype;
      //## end DataField::mytype%3BB317E3002B.attr

      //## begin DataField::mysize%3C3D60C103DA.attr preserve=no  public: int {U} 
      int mysize;
      //## end DataField::mysize%3C3D60C103DA.attr

      //## begin DataField::selected%3BEBE89602BC.attr preserve=no  public: bool {U} 
      bool selected;
      //## end DataField::selected%3BEBE89602BC.attr

      //## begin DataField::writable%3BFCD90E0110.attr preserve=no  public: bool {U} 
      bool writable;
      //## end DataField::writable%3BFCD90E0110.attr

    // Data Members for Associations

      //## Association: PSCF::DMI::<unnamed>%3BEBD9640021
      //## Role: DataField::blocks%3BEBD96601BE
      //## begin DataField::blocks%3BEBD96601BE.role preserve=no  private: BlockSet {0..* -> 0..*VHgN}
      mutable vector<BlockSet> blocks;
      //## end DataField::blocks%3BEBD96601BE.role

      //## Association: PSCF::DMI::<unnamed>%3BEBD97703D5
      //## Role: DataField::objects%3BEBD9780228
      //## begin DataField::objects%3BEBD9780228.role preserve=no  private: BlockableObject {0..* -> 0..*RHN}
      mutable vector<ObjRef> objects;
      //## end DataField::objects%3BEBD9780228.role

    // Additional Implementation Declarations
      //## begin DataField%3BB317D8010B.implementation preserve=yes
      //## end DataField%3BB317D8010B.implementation

};

//## begin DataField%3BB317D8010B.postscript preserve=yes
typedef DataField::Ref DataFieldRef;
//## end DataField%3BB317D8010B.postscript

// Class DataField 


//## Other Operations (inline)
inline TypeId DataField::objectType () const
{
  //## begin DataField::objectType%3C3EC27F0227.body preserve=yes
  return TpDataField;
  //## end DataField::objectType%3C3EC27F0227.body
}

inline const void * DataField::get (int n, TypeId check, Bool must_write) const
{
  //## begin DataField::get%3C56B1DA0057.body preserve=yes
  TypeId dum1; bool dum2;
  return get(n,dum1,dum2,check,must_write);
  //## end DataField::get%3C56B1DA0057.body
}

inline const void* DataField::operator [] (int n) const
{
  //## begin DataField::operator []%3BFCFA1503B1.body preserve=yes
  return get(n);
  //## end DataField::operator []%3BFCFA1503B1.body
}

inline void* DataField::getWr (int n, TypeId check)
{
  //## begin DataField::getWr%3BFCFA2902FB.body preserve=yes
  return (void*)get(n,check,True);
  //## end DataField::getWr%3BFCFA2902FB.body
}

inline void * DataField::operator [] (int n)
{
  //## begin DataField::operator []%3C5FBBEA015C.body preserve=yes
  return getWr(n);
  //## end DataField::operator []%3C5FBBEA015C.body
}

//## Get and Set Operations for Class Attributes (inline)

inline const TypeId DataField::type () const
{
  //## begin DataField::type%3BB317E3002B.get preserve=no
  return mytype;
  //## end DataField::type%3BB317E3002B.get
}

inline const int DataField::size () const
{
  //## begin DataField::size%3C3D60C103DA.get preserve=no
  return mysize;
  //## end DataField::size%3C3D60C103DA.get
}

inline const bool DataField::isSelected () const
{
  //## begin DataField::isSelected%3BEBE89602BC.get preserve=no
  return selected;
  //## end DataField::isSelected%3BEBE89602BC.get
}

inline const bool DataField::isWritable () const
{
  //## begin DataField::isWritable%3BFCD90E0110.get preserve=no
  return writable;
  //## end DataField::isWritable%3BFCD90E0110.get
}

//## begin module%3C10CC820124.epilog preserve=yes
inline void DataField::checkIndex ( int n ) const
{
  FailWhen( n < 0 || n >= mysize,"index out of range");
}
//## end module%3C10CC820124.epilog


#endif

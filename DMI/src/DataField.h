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
#include "TID-base.h"
//## end module%3C10CC820124.additionalIncludes

//## begin module%3C10CC820124.includes preserve=yes
//## end module%3C10CC820124.includes

// BlockSet
#include "BlockSet.h"
// BlockableObject
#include "BlockableObject.h"
//## begin module%3C10CC820124.declarations preserve=no
//## end module%3C10CC820124.declarations

//## begin module%3C10CC820124.additionalDeclarations preserve=yes
// declare the standard types
#pragma typegroup Global
#pragma types char=10 uchar=11 short=12 ushort=13 int=14 uint=15 
#pragma types long=16 ulong=17 float=18 double=19 ldouble=20 string=21

#pragma types mytype

// these constants are used to tell them apart 
const int StdTypeFirst=10,StdTypeLast=21;
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
    //## Constructors (generated)
      DataField();

      DataField(const DataField &right);

    //## Constructors (specified)
      //## Operation: DataField%3BFA54540099
      //	Constructs an empty data field
      DataField (TypeId tid, int num = 0, Bool writable = False);

    //## Destructor (generated)
      ~DataField();

    //## Assignment Operation (generated)
      DataField & operator=(const DataField &right);


    //## Other Operations (specified)
      //## Operation: len%3BFCF8E101C3
      int len ();

      //## Operation: get%3BFCF8E50287
      const void* get (int n = 0, TypeId check = 0);

      //## Operation: operator []%3BFCFA1503B1
      const void* operator [] (int n);

      //## Operation: getWr%3BFCFA2902FB
      void* getWr (int n = 0, TypeId check = 0);

      //## Operation: objref%3C0E4619019A
      ObjRef objref (int n = 0);

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: mytype%3BB317E3002B
      const TypeId type () const;

      //## Attribute: selected%3BEBE89602BC
      const Bool isSelected () const;

      //## Attribute: writable%3BFCD90E0110
      const Bool isWritable () const;

    // Additional Public Declarations
      //## begin DataField%3BB317D8010B.public preserve=yes
      typedef CountedRef<DataField> Ref;
      //## end DataField%3BB317D8010B.public

  protected:
    // Additional Protected Declarations
      //## begin DataField%3BB317D8010B.protected preserve=yes
      //## end DataField%3BB317D8010B.protected

  private:
    // Additional Private Declarations
      //## begin DataField%3BB317D8010B.private preserve=yes
      //## end DataField%3BB317D8010B.private

  private: //## implementation
    // Data Members for Class Attributes

      //## begin DataField::mytype%3BB317E3002B.attr preserve=no  public: TypeId {U} 
      TypeId mytype;
      //## end DataField::mytype%3BB317E3002B.attr

      //## begin DataField::selected%3BEBE89602BC.attr preserve=no  public: Bool {U} 
      Bool selected;
      //## end DataField::selected%3BEBE89602BC.attr

      //## begin DataField::writable%3BFCD90E0110.attr preserve=no  public: Bool {U} 
      Bool writable;
      //## end DataField::writable%3BFCD90E0110.attr

    // Data Members for Associations

      //## Association: PSCF::DMI::<unnamed>%3BEBD9640021
      //## Role: DataField::blocks%3BEBD96601BE
      //## begin DataField::blocks%3BEBD96601BE.role preserve=no  private: BlockSet {0..* -> 0..*VHgN}
      vector<BlockSet> blocks;
      //## end DataField::blocks%3BEBD96601BE.role

      //## Association: PSCF::DMI::<unnamed>%3BEBD97703D5
      //## Role: DataField::objects%3BEBD9780228
      //## begin DataField::objects%3BEBD9780228.role preserve=no  private: BlockableObject {0..* -> 0..*RHN}
      vector<ObjRef> objects;
      //## end DataField::objects%3BEBD9780228.role

    // Additional Implementation Declarations
      //## begin DataField%3BB317D8010B.implementation preserve=yes
      //## end DataField%3BB317D8010B.implementation

};

//## begin DataField%3BB317D8010B.postscript preserve=yes
typedef DataField::Ref DataFieldRef;
//## end DataField%3BB317D8010B.postscript

// Class DataField 

//## Get and Set Operations for Class Attributes (inline)

inline const TypeId DataField::type () const
{
  //## begin DataField::type%3BB317E3002B.get preserve=no
  return mytype;
  //## end DataField::type%3BB317E3002B.get
}

inline const Bool DataField::isSelected () const
{
  //## begin DataField::isSelected%3BEBE89602BC.get preserve=no
  return selected;
  //## end DataField::isSelected%3BEBE89602BC.get
}

inline const Bool DataField::isWritable () const
{
  //## begin DataField::isWritable%3BFCD90E0110.get preserve=no
  return writable;
  //## end DataField::isWritable%3BFCD90E0110.get
}

//## begin module%3C10CC820124.epilog preserve=yes
//## end module%3C10CC820124.epilog


#endif

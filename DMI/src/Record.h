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
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DataRecord.h

#ifndef DataRecord_h
#define DataRecord_h 1

//## begin module%3C10CC820052.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC820052.additionalIncludes

//## begin module%3C10CC820052.includes preserve=yes
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
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BFCD23E02FB;HIID { -> }

class DataRecord : public NestableContainer  //## Inherits: <unnamed>%3BFCD87E039E
{
  //## begin DataRecord%3BB3112B0027.initialDeclarations preserve=yes
  //## end DataRecord%3BB3112B0027.initialDeclarations

  public:
    //## Constructors (generated)
      DataRecord();

      DataRecord(const DataRecord &right);

    //## Destructor (generated)
      ~DataRecord();

    //## Assignment Operation (generated)
      DataRecord & operator=(const DataRecord &right);


    //## Other Operations (specified)
      //## Operation: field%3BFBF49D00A1
      DataFieldRef & field (const HIID &id);

      //## Operation: operator []%3BFBF55C02A4
      DataFieldRef & operator [] (const HIID &id);

      //## Operation: add%3BFBF5B600EB
      Bool add (const HIID &id, DataFieldRef &ref);

      //## Operation: remove%3BB311C903BE
      Bool remove (const HIID &id);

      //## Operation: replace%3BFCD4BB036F
      Bool replace (const HIID &id, DataFieldRef &ref);

      //## Operation: enableWrite%3BFCF8C00234
      Bool enableWrite (const HIID &id);

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: writable%3BFCD97F01DA
      const Bool isWritable () const;

    // Additional Public Declarations
      //## begin DataRecord%3BB3112B0027.public preserve=yes
      //## end DataRecord%3BB3112B0027.public

  protected:
    // Additional Protected Declarations
      //## begin DataRecord%3BB3112B0027.protected preserve=yes
      //## end DataRecord%3BB3112B0027.protected

  private:
    // Additional Private Declarations
      //## begin DataRecord%3BB3112B0027.private preserve=yes
      //## end DataRecord%3BB3112B0027.private

  private: //## implementation
    // Data Members for Class Attributes

      //## begin DataRecord::writable%3BFCD97F01DA.attr preserve=no  public: Bool {U} 
      Bool writable;
      //## end DataRecord::writable%3BFCD97F01DA.attr

    // Data Members for Associations

      //## Association: PSCF::<unnamed>%3BE123050350
      //## Role: DataRecord::fields%3BE123060149
      //## begin DataRecord::fields%3BE123060149.role preserve=no  private: DataField { -> 0..nVHgN}
      map<HIID,DataFieldRef> fields;
      //## end DataRecord::fields%3BE123060149.role

    // Additional Implementation Declarations
      //## begin DataRecord%3BB3112B0027.implementation preserve=yes
      //## end DataRecord%3BB3112B0027.implementation

};

//## begin DataRecord%3BB3112B0027.postscript preserve=yes
//## end DataRecord%3BB3112B0027.postscript

// Class DataRecord 

//## Get and Set Operations for Class Attributes (inline)

inline const Bool DataRecord::isWritable () const
{
  //## begin DataRecord::isWritable%3BFCD97F01DA.get preserve=no
  return writable;
  //## end DataRecord::isWritable%3BFCD97F01DA.get
}

//## begin module%3C10CC820052.epilog preserve=yes
//## end module%3C10CC820052.epilog


#endif

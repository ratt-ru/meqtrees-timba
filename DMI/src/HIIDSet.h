//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC8203CD.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC8203CD.cm

//## begin module%3C10CC8203CD.cp preserve=no
//## end module%3C10CC8203CD.cp

//## Module: HIIDSet%3C10CC8203CD; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\HIIDSet.h

#ifndef HIIDSet_h
#define HIIDSet_h 1

//## begin module%3C10CC8203CD.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC8203CD.additionalIncludes

//## begin module%3C10CC8203CD.includes preserve=yes
#include <set>
//## end module%3C10CC8203CD.includes

// HIID
#include "HIID.h"
//## begin module%3C10CC8203CD.declarations preserve=no
//## end module%3C10CC8203CD.declarations

//## begin module%3C10CC8203CD.additionalDeclarations preserve=yes
//## end module%3C10CC8203CD.additionalDeclarations


//## begin HIIDSet%3BFBAC350085.preface preserve=yes
//## end HIIDSet%3BFBAC350085.preface

//## Class: HIIDSet%3BFBAC350085
//	A set of multiple hierarchical IDs
//	(may include masks, etc.)
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class HIIDSet 
{
  //## begin HIIDSet%3BFBAC350085.initialDeclarations preserve=yes
  //## end HIIDSet%3BFBAC350085.initialDeclarations

  public:
    //## Constructors (generated)
      HIIDSet();

      HIIDSet(const HIIDSet &right);

    //## Constructors (specified)
      //## Operation: HIIDSet%3BFBAE2403DA
      HIIDSet (const HIID& id);

    //## Destructor (generated)
      ~HIIDSet();

    //## Assignment Operation (generated)
      HIIDSet & operator=(const HIIDSet &right);


    //## Other Operations (specified)
      //## Operation: add%3C1DF8510016
      HIIDSet & add (const HIID &id);

      //## Operation: add%3BFBAE330345
      HIIDSet & add (const HIIDSet &other);

      //## Operation: operator +=%3C1DF87E0288
      HIIDSet & operator += (const HIID &id);

      //## Operation: operator +=%3BFBAEDF037E
      HIIDSet & operator += (const HIIDSet &other);

      //## Operation: remove%3BFBAF14023A
      HIIDSet & remove (const HIIDSet &other);

      //## Operation: remove%3C1DFB650236
      HIIDSet & remove (const HIID &id);

      //## Operation: operator -=%3C1DF89A021A
      HIIDSet & operator -= (const HIID &id);

      //## Operation: operator -=%3BFBAF2A01E2
      HIIDSet & operator -= (const HIIDSet &other);

      //## Operation: contains%3BFBAE650315
      Bool contains (const HIID& id) const;

    // Additional Public Declarations
      //## begin HIIDSet%3BFBAC350085.public preserve=yes
      //## end HIIDSet%3BFBAC350085.public

  protected:
    // Additional Protected Declarations
      //## begin HIIDSet%3BFBAC350085.protected preserve=yes
      //## end HIIDSet%3BFBAC350085.protected

  private:
    // Additional Private Declarations
      //## begin HIIDSet%3BFBAC350085.private preserve=yes
      //## end HIIDSet%3BFBAC350085.private

  private: //## implementation
    // Data Members for Associations

      //## Association: PSCF::DMI::<unnamed>%3C0F8F610325
      //## Role: HIIDSet::contents%3C0F8F6202E1
      //## begin HIIDSet::contents%3C0F8F6202E1.role preserve=no  private: HIID { -> 0..*VHgN}
      set<HIID> contents;
      //## end HIIDSet::contents%3C0F8F6202E1.role

    // Additional Implementation Declarations
      //## begin HIIDSet%3BFBAC350085.implementation preserve=yes
      typedef set<HIID>::value_type SVal;
      typedef set<HIID>::iterator SI;
      typedef set<HIID>::const_iterator CSI;
      //## end HIIDSet%3BFBAC350085.implementation
};

//## begin HIIDSet%3BFBAC350085.postscript preserve=yes
//## end HIIDSet%3BFBAC350085.postscript

// Class HIIDSet 


//## Other Operations (inline)
inline HIIDSet & HIIDSet::operator += (const HIID &id)
{
  //## begin HIIDSet::operator +=%3C1DF87E0288.body preserve=yes
  return add(id);
  //## end HIIDSet::operator +=%3C1DF87E0288.body
}

inline HIIDSet & HIIDSet::operator += (const HIIDSet &other)
{
  //## begin HIIDSet::operator +=%3BFBAEDF037E.body preserve=yes
  return add(other);
  //## end HIIDSet::operator +=%3BFBAEDF037E.body
}

inline HIIDSet & HIIDSet::operator -= (const HIID &id)
{
  //## begin HIIDSet::operator -=%3C1DF89A021A.body preserve=yes
  return remove(id);
  //## end HIIDSet::operator -=%3C1DF89A021A.body
}

inline HIIDSet & HIIDSet::operator -= (const HIIDSet &other)
{
  //## begin HIIDSet::operator -=%3BFBAF2A01E2.body preserve=yes
  return remove(other);
  //## end HIIDSet::operator -=%3BFBAF2A01E2.body
}

//## begin module%3C10CC8203CD.epilog preserve=yes
//## end module%3C10CC8203CD.epilog


#endif

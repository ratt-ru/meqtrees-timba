//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820355.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820355.cm

//## begin module%3C10CC820355.cp preserve=no
//## end module%3C10CC820355.cp

//## Module: HIID%3C10CC820355; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\HIID.h

#ifndef HIID_h
#define HIID_h 1

//## begin module%3C10CC820355.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC820355.additionalIncludes

//## begin module%3C10CC820355.includes preserve=yes
//## end module%3C10CC820355.includes

// AtomicID
#include "AtomicID.h"
//## begin module%3C10CC820355.declarations preserve=no
//## end module%3C10CC820355.declarations

//## begin module%3C10CC820355.additionalDeclarations preserve=yes
//## end module%3C10CC820355.additionalDeclarations


//## begin HIID%3BE96FE601C5.preface preserve=yes
//## end HIID%3BE96FE601C5.preface

//## Class: HIID%3BE96FE601C5
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class HIID 
{
  //## begin HIID%3BE96FE601C5.initialDeclarations preserve=yes
  //## end HIID%3BE96FE601C5.initialDeclarations

  public:
    //## Constructors (generated)
      HIID();

      HIID(const HIID &right);

    //## Constructors (specified)
      //## Operation: HIID%3BE9774C003C
      HIID (AtomicID aid);

    //## Assignment Operation (generated)
      HIID & operator=(const HIID &right);

    //## Equality Operations (generated)
      Bool operator==(const HIID &right) const;

      Bool operator!=(const HIID &right) const;

    //## Relational Operations (generated)
      Bool operator<(const HIID &right) const;

      Bool operator>(const HIID &right) const;

      Bool operator<=(const HIID &right) const;

      Bool operator>=(const HIID &right) const;

    //## Subscription Operation (generated)
      AtomicID operator[](const int index) const;


    //## Other Operations (specified)
      //## Operation: add%3BE977510397
      HIID & add (HIID &other);

      //## Operation: add%3BE97792003D
      HIID & add (AtomicID aid);

      //## Operation: length%3C1A187E018C
      int length () const;

      //## Operation: matches%3BE9792B0135
      bool matches (const HIID &other) const;

      //## Operation: toString%3C0F8BD5004F
      string toString () const;

    // Additional Public Declarations
      //## begin HIID%3BE96FE601C5.public preserve=yes
      //## end HIID%3BE96FE601C5.public

  protected:
    // Additional Protected Declarations
      //## begin HIID%3BE96FE601C5.protected preserve=yes
      //## end HIID%3BE96FE601C5.protected

  private:
    // Additional Private Declarations
      //## begin HIID%3BE96FE601C5.private preserve=yes
      //## end HIID%3BE96FE601C5.private

  private: //## implementation
    // Data Members for Associations

      //## Association: PSCF::<unnamed>%3BE970280256
      //## Role: HIID::atoms%3BE970290094
      //## begin HIID::atoms%3BE970290094.role preserve=no  private: AtomicID { -> 0..nVHgN}
      vector<AtomicID> atoms;
      //## end HIID::atoms%3BE970290094.role

    // Additional Implementation Declarations
      //## begin HIID%3BE96FE601C5.implementation preserve=yes
      typedef vector<AtomicID>::iterator AtomsIter;
      typedef vector<AtomicID>::const_iterator AtomsConstIter;
      //## end HIID%3BE96FE601C5.implementation
};

//## begin HIID%3BE96FE601C5.postscript preserve=yes
//## end HIID%3BE96FE601C5.postscript

// Class HIID 

inline HIID::HIID()
  //## begin HIID::HIID%3BE96FE601C5_const.hasinit preserve=no
  //## end HIID::HIID%3BE96FE601C5_const.hasinit
  //## begin HIID::HIID%3BE96FE601C5_const.initialization preserve=yes
   : atoms()
  //## end HIID::HIID%3BE96FE601C5_const.initialization
{
  //## begin HIID::HIID%3BE96FE601C5_const.body preserve=yes
  //## end HIID::HIID%3BE96FE601C5_const.body
}

inline HIID::HIID(const HIID &right)
  //## begin HIID::HIID%3BE96FE601C5_copy.hasinit preserve=no
  //## end HIID::HIID%3BE96FE601C5_copy.hasinit
  //## begin HIID::HIID%3BE96FE601C5_copy.initialization preserve=yes
    : atoms(right.atoms)
  //## end HIID::HIID%3BE96FE601C5_copy.initialization
{
  //## begin HIID::HIID%3BE96FE601C5_copy.body preserve=yes
  //## end HIID::HIID%3BE96FE601C5_copy.body
}

inline HIID::HIID (AtomicID aid)
  //## begin HIID::HIID%3BE9774C003C.hasinit preserve=no
  //## end HIID::HIID%3BE9774C003C.hasinit
  //## begin HIID::HIID%3BE9774C003C.initialization preserve=yes
    : atoms(1,aid)
  //## end HIID::HIID%3BE9774C003C.initialization
{
  //## begin HIID::HIID%3BE9774C003C.body preserve=yes
  //## end HIID::HIID%3BE9774C003C.body
}


inline HIID & HIID::operator=(const HIID &right)
{
  //## begin HIID::operator=%3BE96FE601C5_assign.body preserve=yes
  atoms = right.atoms;
  return *this;
  //## end HIID::operator=%3BE96FE601C5_assign.body
}


inline Bool HIID::operator==(const HIID &right) const
{
  //## begin HIID::operator==%3BE96FE601C5_eq.body preserve=yes
  return atoms == right.atoms;
  //## end HIID::operator==%3BE96FE601C5_eq.body
}

inline Bool HIID::operator!=(const HIID &right) const
{
  //## begin HIID::operator!=%3BE96FE601C5_neq.body preserve=yes
  return atoms != right.atoms;
  //## end HIID::operator!=%3BE96FE601C5_neq.body
}


inline Bool HIID::operator<(const HIID &right) const
{
  //## begin HIID::operator<%3BE96FE601C5_ls.body preserve=yes
  return atoms < right.atoms;
  //## end HIID::operator<%3BE96FE601C5_ls.body
}

inline Bool HIID::operator>(const HIID &right) const
{
  //## begin HIID::operator>%3BE96FE601C5_gt.body preserve=yes
  return atoms > right.atoms;
  //## end HIID::operator>%3BE96FE601C5_gt.body
}

inline Bool HIID::operator<=(const HIID &right) const
{
  //## begin HIID::operator<=%3BE96FE601C5_lseq.body preserve=yes
  return atoms <= right.atoms;
  //## end HIID::operator<=%3BE96FE601C5_lseq.body
}

inline Bool HIID::operator>=(const HIID &right) const
{
  //## begin HIID::operator>=%3BE96FE601C5_gteq.body preserve=yes
  return atoms >= right.atoms;
  //## end HIID::operator>=%3BE96FE601C5_gteq.body
}


inline AtomicID HIID::operator[](const int index) const
{
  //## begin HIID::operator[]%3BE96FE601C5_ind.body preserve=yes
  return atoms[index];
  //## end HIID::operator[]%3BE96FE601C5_ind.body
}



//## Other Operations (inline)
inline HIID & HIID::add (AtomicID aid)
{
  //## begin HIID::add%3BE97792003D.body preserve=yes
  atoms.push_back(aid);
  return *this;
  //## end HIID::add%3BE97792003D.body
}

inline int HIID::length () const
{
  //## begin HIID::length%3C1A187E018C.body preserve=yes
  return atoms.size();
  //## end HIID::length%3C1A187E018C.body
}

//## begin module%3C10CC820355.epilog preserve=yes
//## end module%3C10CC820355.epilog


#endif


// Detached code regions:
#if 0
//## begin HIID::superIdOf%3BE979240121.body preserve=yes
  return other.subIdOf(*this);
//## end HIID::superIdOf%3BE979240121.body

#endif

//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC810157.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC810157.cm

//## begin module%3C10CC810157.cp preserve=no
//## end module%3C10CC810157.cp

//## Module: AtomicID%3C10CC810157; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\AtomicID.h

#ifndef AtomicID_h
#define AtomicID_h 1

//## begin module%3C10CC810157.additionalIncludes preserve=no
#include "Common.h"
#include <map>
//## end module%3C10CC810157.additionalIncludes

//## begin module%3C10CC810157.includes preserve=yes
//## end module%3C10CC810157.includes

// Registry
#include "Registry.h"
//## begin module%3C10CC810157.declarations preserve=no
//## end module%3C10CC810157.declarations

//## begin module%3C10CC810157.additionalDeclarations preserve=yes
#pragma aidgroup Basic
#pragma aid A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
//## end module%3C10CC810157.additionalDeclarations


//## begin AtomicID%3BE970170297.preface preserve=yes
//## end AtomicID%3BE970170297.preface

//## Class: AtomicID%3BE970170297
//	Atomic identifier (numeric, but with a mapping mechanism to symbolic
//	IDs)
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C5A791101CC;UniRegistry { -> }

class AtomicID 
{
  //## begin AtomicID%3BE970170297.initialDeclarations preserve=yes
  //## end AtomicID%3BE970170297.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: AtomicID%3BE970C40246
      AtomicID (int n = 0);

      //## Operation: AtomicID%3C5E74CB0112
      //	Constructs AtomicID by its name
      AtomicID (const string &str);

      //## Operation: AtomicID%3C68D5220318
      AtomicID (const char *str);

    //## Equality Operations (generated)
      Bool operator==(const AtomicID &right) const;

      Bool operator!=(const AtomicID &right) const;

    //## Relational Operations (generated)
      Bool operator<(const AtomicID &right) const;

      Bool operator>(const AtomicID &right) const;

      Bool operator<=(const AtomicID &right) const;

      Bool operator>=(const AtomicID &right) const;


    //## Other Operations (specified)
      //## Operation: operator int%3C0F8D1102B6
      operator int () const;

      //## Operation: operator =%3C1A1A9000DD
      AtomicID & operator = (int n);

      //## Operation: operator !%3C596562005C
      bool operator ! ();

      //## Operation: isAny%3C1A28850258
      bool isAny () const;

      //## Operation: isWildcard%3C1A288F0342
      bool isWildcard () const;

      //## Operation: index%3C553EC402AA
      //	If AtomicID corresponds to an index, returns that index, else
      //	returns -1
      int index () const;

      //## Operation: matches%3C1DFD1A0235
      bool matches (const AtomicID &other) const;

      //## Operation: toString%3BE9709700A7
      string toString () const;

      //## Operation: findName%3C68D5ED01F8
      static int findName (const string &str);

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: aid%3BE9706902BD
      const int id () const;

    // Additional Public Declarations
      //## begin AtomicID%3BE970170297.public preserve=yes
      //## end AtomicID%3BE970170297.public
  protected:
    // Additional Protected Declarations
      //## begin AtomicID%3BE970170297.protected preserve=yes
      //## end AtomicID%3BE970170297.protected

  private:
    // Additional Private Declarations
      //## begin AtomicID%3BE970170297.private preserve=yes
      DeclareBiRegistry(AtomicID,int,string);
      //## end AtomicID%3BE970170297.private
  private: //## implementation
    // Data Members for Class Attributes

      //## begin AtomicID::aid%3BE9706902BD.attr preserve=no  public: int {U} 
      int aid;
      //## end AtomicID::aid%3BE9706902BD.attr

    // Additional Implementation Declarations
      //## begin AtomicID%3BE970170297.implementation preserve=yes
      //## end AtomicID%3BE970170297.implementation

};

//## begin AtomicID%3BE970170297.postscript preserve=yes
const AtomicID AidNull(0),
               AidAny(-1),
               AidWildcard(-2),
               AidDot(-3);
//## end AtomicID%3BE970170297.postscript

//## begin AidIndex%3C553F440092.preface preserve=yes
//## end AidIndex%3C553F440092.preface

//## Class: AidIndex%3C553F440092
//	AidIndex is a helper class which may be used to create an AtomicID
//	corresponding to an array index
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class AidIndex : public AtomicID  //## Inherits: <unnamed>%3C553F570201
{
  //## begin AidIndex%3C553F440092.initialDeclarations preserve=yes
  //## end AidIndex%3C553F440092.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: AidIndex%3C553F7100D2
      AidIndex (int index = 0);

    // Additional Public Declarations
      //## begin AidIndex%3C553F440092.public preserve=yes
      //## end AidIndex%3C553F440092.public

  protected:
    // Additional Protected Declarations
      //## begin AidIndex%3C553F440092.protected preserve=yes
      //## end AidIndex%3C553F440092.protected

  private:
    // Additional Private Declarations
      //## begin AidIndex%3C553F440092.private preserve=yes
      //## end AidIndex%3C553F440092.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin AidIndex%3C553F440092.implementation preserve=yes
      //## end AidIndex%3C553F440092.implementation

};

//## begin AidIndex%3C553F440092.postscript preserve=yes
//## end AidIndex%3C553F440092.postscript

// Class AtomicID 

inline AtomicID::AtomicID (int n)
  //## begin AtomicID::AtomicID%3BE970C40246.hasinit preserve=no
  //## end AtomicID::AtomicID%3BE970C40246.hasinit
  //## begin AtomicID::AtomicID%3BE970C40246.initialization preserve=yes
    : aid(n)
  //## end AtomicID::AtomicID%3BE970C40246.initialization
{
  //## begin AtomicID::AtomicID%3BE970C40246.body preserve=yes
  //## end AtomicID::AtomicID%3BE970C40246.body
}

inline AtomicID::AtomicID (const string &str)
  //## begin AtomicID::AtomicID%3C5E74CB0112.hasinit preserve=no
  //## end AtomicID::AtomicID%3C5E74CB0112.hasinit
  //## begin AtomicID::AtomicID%3C5E74CB0112.initialization preserve=yes
  : aid( findName(str) )
  //## end AtomicID::AtomicID%3C5E74CB0112.initialization
{
  //## begin AtomicID::AtomicID%3C5E74CB0112.body preserve=yes
  //## end AtomicID::AtomicID%3C5E74CB0112.body
}

inline AtomicID::AtomicID (const char *str)
  //## begin AtomicID::AtomicID%3C68D5220318.hasinit preserve=no
  //## end AtomicID::AtomicID%3C68D5220318.hasinit
  //## begin AtomicID::AtomicID%3C68D5220318.initialization preserve=yes
  : aid( findName(str) )
  //## end AtomicID::AtomicID%3C68D5220318.initialization
{
  //## begin AtomicID::AtomicID%3C68D5220318.body preserve=yes
  //## end AtomicID::AtomicID%3C68D5220318.body
}


inline Bool AtomicID::operator==(const AtomicID &right) const
{
  //## begin AtomicID::operator==%3BE970170297_eq.body preserve=yes
  return aid == right.aid;
  //## end AtomicID::operator==%3BE970170297_eq.body
}

inline Bool AtomicID::operator!=(const AtomicID &right) const
{
  //## begin AtomicID::operator!=%3BE970170297_neq.body preserve=yes
  return aid != right.aid;
  //## end AtomicID::operator!=%3BE970170297_neq.body
}


inline Bool AtomicID::operator<(const AtomicID &right) const
{
  //## begin AtomicID::operator<%3BE970170297_ls.body preserve=yes
  return aid < right.aid;
  //## end AtomicID::operator<%3BE970170297_ls.body
}

inline Bool AtomicID::operator>(const AtomicID &right) const
{
  //## begin AtomicID::operator>%3BE970170297_gt.body preserve=yes
  return aid > right.aid;
  //## end AtomicID::operator>%3BE970170297_gt.body
}

inline Bool AtomicID::operator<=(const AtomicID &right) const
{
  //## begin AtomicID::operator<=%3BE970170297_lseq.body preserve=yes
  return aid <= right.aid;
  //## end AtomicID::operator<=%3BE970170297_lseq.body
}

inline Bool AtomicID::operator>=(const AtomicID &right) const
{
  //## begin AtomicID::operator>=%3BE970170297_gteq.body preserve=yes
  return aid >= right.aid;
  //## end AtomicID::operator>=%3BE970170297_gteq.body
}



//## Other Operations (inline)
inline AtomicID::operator int () const
{
  //## begin AtomicID::operator int%3C0F8D1102B6.body preserve=yes
  return aid;
  //## end AtomicID::operator int%3C0F8D1102B6.body
}

inline AtomicID & AtomicID::operator = (int n)
{
  //## begin AtomicID::operator =%3C1A1A9000DD.body preserve=yes
  aid = n;
  return *this;
  //## end AtomicID::operator =%3C1A1A9000DD.body
}

inline bool AtomicID::operator ! ()
{
  //## begin AtomicID::operator !%3C596562005C.body preserve=yes
  return !aid;
  //## end AtomicID::operator !%3C596562005C.body
}

inline bool AtomicID::isAny () const
{
  //## begin AtomicID::isAny%3C1A28850258.body preserve=yes
  return aid == (int) AidAny; 
  //## end AtomicID::isAny%3C1A28850258.body
}

inline bool AtomicID::isWildcard () const
{
  //## begin AtomicID::isWildcard%3C1A288F0342.body preserve=yes
  return aid == (int) AidWildcard; 
  //## end AtomicID::isWildcard%3C1A288F0342.body
}

inline int AtomicID::index () const
{
  //## begin AtomicID::index%3C553EC402AA.body preserve=yes
  return aid >= 0 ? aid : -1;
  //## end AtomicID::index%3C553EC402AA.body
}

inline bool AtomicID::matches (const AtomicID &other) const
{
  //## begin AtomicID::matches%3C1DFD1A0235.body preserve=yes
  return isAny() || isWildcard() ||
         other.isAny() || other.isWildcard() ||
         aid == other.aid;
  //## end AtomicID::matches%3C1DFD1A0235.body
}

//## Get and Set Operations for Class Attributes (inline)

inline const int AtomicID::id () const
{
  //## begin AtomicID::id%3BE9706902BD.get preserve=no
  return aid;
  //## end AtomicID::id%3BE9706902BD.get
}

// Class AidIndex 

inline AidIndex::AidIndex (int index)
  //## begin AidIndex::AidIndex%3C553F7100D2.hasinit preserve=no
  //## end AidIndex::AidIndex%3C553F7100D2.hasinit
  //## begin AidIndex::AidIndex%3C553F7100D2.initialization preserve=yes
  : AtomicID( index )
  //## end AidIndex::AidIndex%3C553F7100D2.initialization
{
  //## begin AidIndex::AidIndex%3C553F7100D2.body preserve=yes
  //## end AidIndex::AidIndex%3C553F7100D2.body
}


//## begin module%3C10CC810157.epilog preserve=yes
//## end module%3C10CC810157.epilog


#endif

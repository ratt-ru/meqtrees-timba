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

//## begin module%3C10CC810157.declarations preserve=no
//## end module%3C10CC810157.declarations

//## begin module%3C10CC810157.additionalDeclarations preserve=yes
// This macros registers Atomic IDs. A script will scan your code
// for invocations, and create include/.cc files defining the AIDs.
#define RegisterAid(aid)
// By default, everything is placed into AID.h, but by invoking:
#define RegisterAidGroup(group)
// you can place subsequent AIDs into AID-group.h.
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



class AtomicID 
{
  //## begin AtomicID%3BE970170297.initialDeclarations preserve=yes
  //## end AtomicID%3BE970170297.initialDeclarations

  public:
    //## begin AtomicID::Register%3C1DB25B039C.preface preserve=yes
    //## end AtomicID::Register%3C1DB25B039C.preface

    //## Class: Register%3C1DB25B039C
    //## Category: PSCF::DMI%3BEAB1F2006B; Global
    //## Subsystem: DMI%3C10CC810155
    //## Persistence: Transient
    //## Cardinality/Multiplicity: n



    class Register 
    {
      //## begin AtomicID::Register%3C1DB25B039C.initialDeclarations preserve=yes
      //## end AtomicID::Register%3C1DB25B039C.initialDeclarations

      public:
        //## Constructors (specified)
          //## Operation: Register%3C1DB26B00CD
          Register (int id, const string &name);

        // Additional Public Declarations
          //## begin AtomicID::Register%3C1DB25B039C.public preserve=yes
          //## end AtomicID::Register%3C1DB25B039C.public

      protected:
        // Additional Protected Declarations
          //## begin AtomicID::Register%3C1DB25B039C.protected preserve=yes
          //## end AtomicID::Register%3C1DB25B039C.protected

      private:
        //## Constructors (generated)
          Register();

          Register(const Register &right);

        // Additional Private Declarations
          //## begin AtomicID::Register%3C1DB25B039C.private preserve=yes
          //## end AtomicID::Register%3C1DB25B039C.private

      private: //## implementation
        // Additional Implementation Declarations
          //## begin AtomicID::Register%3C1DB25B039C.implementation preserve=yes
          //## end AtomicID::Register%3C1DB25B039C.implementation

    };

    //## begin AtomicID::Register%3C1DB25B039C.postscript preserve=yes
    //## end AtomicID::Register%3C1DB25B039C.postscript

    //## Constructors (generated)
      AtomicID();

      AtomicID(const AtomicID &right);

    //## Constructors (specified)
      //## Operation: AtomicID%3BE970C40246
      AtomicID (int n);

    //## Destructor (generated)
      ~AtomicID();

    //## Assignment Operation (generated)
      AtomicID & operator=(const AtomicID &right);

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

      //## Operation: isAny%3C1A28850258
      Bool isAny () const;

      //## Operation: isWildcard%3C1A288F0342
      Bool isWildcard () const;

      //## Operation: matches%3C1DFD1A0235
      Bool matches (const AtomicID &other) const;

      //## Operation: toString%3BE9709700A7
      string toString () const;

      //## Operation: registerName%3C1A2B2101E8
      static void registerName (int n, const string &name);

  public:
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
      //## end AtomicID%3BE970170297.private

  private: //## implementation
    // Data Members for Class Attributes

      //## Attribute: id%3BE9706902BD
      //## begin AtomicID::id%3BE9706902BD.attr preserve=no  private: int {U} 
      int id;
      //## end AtomicID::id%3BE9706902BD.attr

      //## Attribute: names%3BEBE9870055
      //## begin AtomicID::names%3BEBE9870055.attr preserve=no  private: static map<int,string> {U} 
      static map<int,string> names;
      //## end AtomicID::names%3BEBE9870055.attr

    // Additional Implementation Declarations
      //## begin AtomicID%3BE970170297.implementation preserve=yes
      typedef map<int,string>::iterator MI;
      typedef map<int,string>::const_iterator CMI;
      //## end AtomicID%3BE970170297.implementation
};

//## begin AtomicID%3BE970170297.postscript preserve=yes
const AtomicID AidNull(0),
               AidAny(-1),
               AidWildcard(-2);
//## end AtomicID%3BE970170297.postscript

// Class AtomicID::Register 

// Class AtomicID 

inline AtomicID::AtomicID()
  //## begin AtomicID::AtomicID%3BE970170297_const.hasinit preserve=no
  //## end AtomicID::AtomicID%3BE970170297_const.hasinit
  //## begin AtomicID::AtomicID%3BE970170297_const.initialization preserve=yes
    : id(0)
  //## end AtomicID::AtomicID%3BE970170297_const.initialization
{
  //## begin AtomicID::AtomicID%3BE970170297_const.body preserve=yes
  //## end AtomicID::AtomicID%3BE970170297_const.body
}

inline AtomicID::AtomicID(const AtomicID &right)
  //## begin AtomicID::AtomicID%3BE970170297_copy.hasinit preserve=no
  //## end AtomicID::AtomicID%3BE970170297_copy.hasinit
  //## begin AtomicID::AtomicID%3BE970170297_copy.initialization preserve=yes
    : id(right.id)
  //## end AtomicID::AtomicID%3BE970170297_copy.initialization
{
  //## begin AtomicID::AtomicID%3BE970170297_copy.body preserve=yes
  //## end AtomicID::AtomicID%3BE970170297_copy.body
}

inline AtomicID::AtomicID (int n)
  //## begin AtomicID::AtomicID%3BE970C40246.hasinit preserve=no
  //## end AtomicID::AtomicID%3BE970C40246.hasinit
  //## begin AtomicID::AtomicID%3BE970C40246.initialization preserve=yes
    : id(n)
  //## end AtomicID::AtomicID%3BE970C40246.initialization
{
  //## begin AtomicID::AtomicID%3BE970C40246.body preserve=yes
  //## end AtomicID::AtomicID%3BE970C40246.body
}


inline AtomicID::~AtomicID()
{
  //## begin AtomicID::~AtomicID%3BE970170297_dest.body preserve=yes
  //## end AtomicID::~AtomicID%3BE970170297_dest.body
}


inline AtomicID & AtomicID::operator=(const AtomicID &right)
{
  //## begin AtomicID::operator=%3BE970170297_assign.body preserve=yes
  id = right.id;
  return *this;
  //## end AtomicID::operator=%3BE970170297_assign.body
}


inline Bool AtomicID::operator==(const AtomicID &right) const
{
  //## begin AtomicID::operator==%3BE970170297_eq.body preserve=yes
  return id == right.id;
  //## end AtomicID::operator==%3BE970170297_eq.body
}

inline Bool AtomicID::operator!=(const AtomicID &right) const
{
  //## begin AtomicID::operator!=%3BE970170297_neq.body preserve=yes
  return id != right.id;
  //## end AtomicID::operator!=%3BE970170297_neq.body
}


inline Bool AtomicID::operator<(const AtomicID &right) const
{
  //## begin AtomicID::operator<%3BE970170297_ls.body preserve=yes
  return id < right.id;
  //## end AtomicID::operator<%3BE970170297_ls.body
}

inline Bool AtomicID::operator>(const AtomicID &right) const
{
  //## begin AtomicID::operator>%3BE970170297_gt.body preserve=yes
  return id > right.id;
  //## end AtomicID::operator>%3BE970170297_gt.body
}

inline Bool AtomicID::operator<=(const AtomicID &right) const
{
  //## begin AtomicID::operator<=%3BE970170297_lseq.body preserve=yes
  return id <= right.id;
  //## end AtomicID::operator<=%3BE970170297_lseq.body
}

inline Bool AtomicID::operator>=(const AtomicID &right) const
{
  //## begin AtomicID::operator>=%3BE970170297_gteq.body preserve=yes
  return id >= right.id;
  //## end AtomicID::operator>=%3BE970170297_gteq.body
}



//## Other Operations (inline)
inline AtomicID::operator int () const
{
  //## begin AtomicID::operator int%3C0F8D1102B6.body preserve=yes
  return id;
  //## end AtomicID::operator int%3C0F8D1102B6.body
}

inline AtomicID & AtomicID::operator = (int n)
{
  //## begin AtomicID::operator =%3C1A1A9000DD.body preserve=yes
  id = n;
  return *this;
  //## end AtomicID::operator =%3C1A1A9000DD.body
}

inline Bool AtomicID::isAny () const
{
  //## begin AtomicID::isAny%3C1A28850258.body preserve=yes
  return id == (int) AidAny; 
  //## end AtomicID::isAny%3C1A28850258.body
}

inline Bool AtomicID::isWildcard () const
{
  //## begin AtomicID::isWildcard%3C1A288F0342.body preserve=yes
  return id == (int) AidWildcard; 
  //## end AtomicID::isWildcard%3C1A288F0342.body
}

inline Bool AtomicID::matches (const AtomicID &other) const
{
  //## begin AtomicID::matches%3C1DFD1A0235.body preserve=yes
  return id<0 || other.id<0 || id == other.id;
  //## end AtomicID::matches%3C1DFD1A0235.body
}

//## begin module%3C10CC810157.epilog preserve=yes
//## end module%3C10CC810157.epilog


#endif



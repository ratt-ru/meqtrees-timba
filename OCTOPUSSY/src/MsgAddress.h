//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7B7F2F037E.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7B7F2F037E.cm

//## begin module%3C7B7F2F037E.cp preserve=no
//## end module%3C7B7F2F037E.cp

//## Module: MsgAddress%3C7B7F2F037E; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\MsgAddress.h

#ifndef MsgAddress_h
#define MsgAddress_h 1

//## begin module%3C7B7F2F037E.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C7B7F2F037E.additionalIncludes

//## begin module%3C7B7F2F037E.includes preserve=yes
#include "OCTOPUSSY/AID-OCTOPUSSY.h"
//## end module%3C7B7F2F037E.includes

// HIID
#include "DMI/HIID.h"
//## begin module%3C7B7F2F037E.declarations preserve=no
//## end module%3C7B7F2F037E.declarations

//## begin module%3C7B7F2F037E.additionalDeclarations preserve=yes
#pragma aidgroup OCTOPUSSY
#pragma aid Dispatcher Local Publish
//## end module%3C7B7F2F037E.additionalDeclarations


//## begin WPID%3C8F9A340206.preface preserve=yes
//## end WPID%3C8F9A340206.preface

//## Class: WPID%3C8F9A340206
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class WPID : public HIID  //## Inherits: <unnamed>%3C8F9A5B0343
{
  //## begin WPID%3C8F9A340206.initialDeclarations preserve=yes
  //## end WPID%3C8F9A340206.initialDeclarations

  public:
    //## Constructors (generated)
      WPID();

    //## Constructors (specified)
      //## Operation: WPID%3C8F9AC70027
      WPID (AtomicID wpc, AtomicID inst = 0);


    //## Other Operations (specified)
      //## Operation: wpclass%3C8F9AA503C1
      AtomicID wpclass () const;

      //## Operation: inst%3C8F9AAB0103
      AtomicID inst () const;

    // Additional Public Declarations
      //## begin WPID%3C8F9A340206.public preserve=yes
      static const size_t byte_size = 2*sizeof(int);
      //## end WPID%3C8F9A340206.public
  protected:
    // Additional Protected Declarations
      //## begin WPID%3C8F9A340206.protected preserve=yes
      //## end WPID%3C8F9A340206.protected

  private:
    // Additional Private Declarations
      //## begin WPID%3C8F9A340206.private preserve=yes
      //## end WPID%3C8F9A340206.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin WPID%3C8F9A340206.implementation preserve=yes
      //## end WPID%3C8F9A340206.implementation

};

//## begin WPID%3C8F9A340206.postscript preserve=yes
//## end WPID%3C8F9A340206.postscript

//## begin MsgAddress%3C7B6F790197.preface preserve=yes
//## end MsgAddress%3C7B6F790197.preface

//## Class: MsgAddress%3C7B6F790197
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class MsgAddress : public WPID  //## Inherits: <unnamed>%3C8F9A8F0199
{
  //## begin MsgAddress%3C7B6F790197.initialDeclarations preserve=yes
  //## end MsgAddress%3C7B6F790197.initialDeclarations

  public:
    //## Constructors (generated)
      MsgAddress();

    //## Constructors (specified)
      //## Operation: MsgAddress%3C7B6FAE00FD
      MsgAddress (AtomicID wpc, AtomicID wpinst = 0, AtomicID proc = AidLocal, AtomicID host = AidLocal);

      //## Operation: MsgAddress%3C8F9B8E0087
      MsgAddress (const WPID& wpid, AtomicID proc = AidLocal, AtomicID host = AidLocal);


    //## Other Operations (specified)
      //## Operation: wpid%3C8F9BC10135
      WPID wpid () const;

      //## Operation: process%3C7B6FF7033D
      AtomicID & process ();

      //## Operation: process%3C90700001B4
      const AtomicID & process () const;

      //## Operation: host%3C7B6FFC0330
      AtomicID & host ();

      //## Operation: host%3C9070080170
      const AtomicID & host () const;

    // Additional Public Declarations
      //## begin MsgAddress%3C7B6F790197.public preserve=yes
      HIID peerid () const
      { return process()|host(); }
      
      static const size_t byte_size = 4*sizeof(int);
      //## end MsgAddress%3C7B6F790197.public
  protected:
    // Additional Protected Declarations
      //## begin MsgAddress%3C7B6F790197.protected preserve=yes
      //## end MsgAddress%3C7B6F790197.protected

  private:
    // Additional Private Declarations
      //## begin MsgAddress%3C7B6F790197.private preserve=yes
      //## end MsgAddress%3C7B6F790197.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin MsgAddress%3C7B6F790197.implementation preserve=yes
      //## end MsgAddress%3C7B6F790197.implementation

};

//## begin MsgAddress%3C7B6F790197.postscript preserve=yes
//## end MsgAddress%3C7B6F790197.postscript

// Class WPID 

inline WPID::WPID()
  //## begin WPID::WPID%3C8F9A340206_const.hasinit preserve=no
  //## end WPID::WPID%3C8F9A340206_const.hasinit
  //## begin WPID::WPID%3C8F9A340206_const.initialization preserve=yes
  //## end WPID::WPID%3C8F9A340206_const.initialization
{
  //## begin WPID::WPID%3C8F9A340206_const.body preserve=yes
  //## end WPID::WPID%3C8F9A340206_const.body
}

inline WPID::WPID (AtomicID wpc, AtomicID inst)
  //## begin WPID::WPID%3C8F9AC70027.hasinit preserve=no
  //## end WPID::WPID%3C8F9AC70027.hasinit
  //## begin WPID::WPID%3C8F9AC70027.initialization preserve=yes
    : HIID(wpc)
  //## end WPID::WPID%3C8F9AC70027.initialization
{
  //## begin WPID::WPID%3C8F9AC70027.body preserve=yes
  add(inst);
  //## end WPID::WPID%3C8F9AC70027.body
}



//## Other Operations (inline)
inline AtomicID WPID::wpclass () const
{
  //## begin WPID::wpclass%3C8F9AA503C1.body preserve=yes
  return (*this)[0];
  //## end WPID::wpclass%3C8F9AA503C1.body
}

inline AtomicID WPID::inst () const
{
  //## begin WPID::inst%3C8F9AAB0103.body preserve=yes
  return (*this)[1];
  //## end WPID::inst%3C8F9AAB0103.body
}

// Class MsgAddress 

inline MsgAddress::MsgAddress()
  //## begin MsgAddress::MsgAddress%3C7B6F790197_const.hasinit preserve=no
  //## end MsgAddress::MsgAddress%3C7B6F790197_const.hasinit
  //## begin MsgAddress::MsgAddress%3C7B6F790197_const.initialization preserve=yes
  //## end MsgAddress::MsgAddress%3C7B6F790197_const.initialization
{
  //## begin MsgAddress::MsgAddress%3C7B6F790197_const.body preserve=yes
  resize(4);
  //## end MsgAddress::MsgAddress%3C7B6F790197_const.body
}

inline MsgAddress::MsgAddress (AtomicID wpc, AtomicID wpinst, AtomicID proc, AtomicID host)
  //## begin MsgAddress::MsgAddress%3C7B6FAE00FD.hasinit preserve=no
  //## end MsgAddress::MsgAddress%3C7B6FAE00FD.hasinit
  //## begin MsgAddress::MsgAddress%3C7B6FAE00FD.initialization preserve=yes
    : WPID(wpc,wpinst)
  //## end MsgAddress::MsgAddress%3C7B6FAE00FD.initialization
{
  //## begin MsgAddress::MsgAddress%3C7B6FAE00FD.body preserve=yes
  add(proc);
  add(host);
  //## end MsgAddress::MsgAddress%3C7B6FAE00FD.body
}

inline MsgAddress::MsgAddress (const WPID& wpid, AtomicID proc, AtomicID host)
  //## begin MsgAddress::MsgAddress%3C8F9B8E0087.hasinit preserve=no
  //## end MsgAddress::MsgAddress%3C8F9B8E0087.hasinit
  //## begin MsgAddress::MsgAddress%3C8F9B8E0087.initialization preserve=yes
    : WPID(wpid)
  //## end MsgAddress::MsgAddress%3C8F9B8E0087.initialization
{
  //## begin MsgAddress::MsgAddress%3C8F9B8E0087.body preserve=yes
  add(proc);
  add(host);
  //## end MsgAddress::MsgAddress%3C8F9B8E0087.body
}



//## Other Operations (inline)
inline WPID MsgAddress::wpid () const
{
  //## begin MsgAddress::wpid%3C8F9BC10135.body preserve=yes
  return WPID(wpclass(),inst());
  //## end MsgAddress::wpid%3C8F9BC10135.body
}

inline AtomicID & MsgAddress::process ()
{
  //## begin MsgAddress::process%3C7B6FF7033D.body preserve=yes
  return (*this)[2];
  //## end MsgAddress::process%3C7B6FF7033D.body
}

inline const AtomicID & MsgAddress::process () const
{
  //## begin MsgAddress::process%3C90700001B4.body preserve=yes
  return (*this)[2];
  //## end MsgAddress::process%3C90700001B4.body
}

inline AtomicID & MsgAddress::host ()
{
  //## begin MsgAddress::host%3C7B6FFC0330.body preserve=yes
  return (*this)[3];
  //## end MsgAddress::host%3C7B6FFC0330.body
}

inline const AtomicID & MsgAddress::host () const
{
  //## begin MsgAddress::host%3C9070080170.body preserve=yes
  return (*this)[3];
  //## end MsgAddress::host%3C9070080170.body
}

//## begin module%3C7B7F2F037E.epilog preserve=yes
//## end module%3C7B7F2F037E.epilog


#endif

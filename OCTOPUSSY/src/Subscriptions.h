//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C999E140208.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C999E140208.cm

//## begin module%3C999E140208.cp preserve=no
//## end module%3C999E140208.cp

//## Module: Subscriptions%3C999E140208; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\Subscriptions.h

#ifndef Subscriptions_h
#define Subscriptions_h 1

//## begin module%3C999E140208.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C999E140208.additionalIncludes

//## begin module%3C999E140208.includes preserve=yes
#include <list>
//## end module%3C999E140208.includes

// HIID
#include "DMI/HIID.h"
// MsgAddress
#include "OCTOPUSSY/MsgAddress.h"
// Message
#include "OCTOPUSSY/Message.h"
//## begin module%3C999E140208.declarations preserve=no
//## end module%3C999E140208.declarations

//## begin module%3C999E140208.additionalDeclarations preserve=yes
//## end module%3C999E140208.additionalDeclarations


//## begin Subscriptions%3C999C8400AF.preface preserve=yes
//## end Subscriptions%3C999C8400AF.preface

//## Class: Subscriptions%3C999C8400AF
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C99C776028F;MsgAddress { -> }
//## Uses: <unnamed>%3C99C78F0168;HIID { -> }
//## Uses: <unnamed>%3C99C7CF0084;Message { -> }

class Subscriptions 
{
  //## begin Subscriptions%3C999C8400AF.initialDeclarations preserve=yes
  //## end Subscriptions%3C999C8400AF.initialDeclarations

  public:
    //## Constructors (generated)
      Subscriptions();


    //## Other Operations (specified)
      //## Operation: add%3C999D010361
      bool add (const HIID& id, const MsgAddress &scope);

      //## Operation: remove%3C999D40033A
      bool remove (const HIID &id);

      //## Operation: clear%3C999E0B0223
      void clear ();

      //## Operation: size%3C99C0BB0378
      int size () const;

      //## Operation: merge%3C999D64004D
      bool merge (const Subscriptions &other);

      //## Operation: matches%3C999D780005
      bool matches (const Message &msg) const;

      //## Operation: pack%3C99AC2F01DF
      //	Stores HIID into raw data block
      size_t pack (void* block, size_t &nleft) const;

      //## Operation: unpack%3C99AC2F022F
      void unpack (const void* block, size_t sz);

      //## Operation: packSize%3C99AC2F027F
      //	Returns # of bytes required to store the HIID
      size_t packSize () const;

    // Additional Public Declarations
      //## begin Subscriptions%3C999C8400AF.public preserve=yes
      //## end Subscriptions%3C999C8400AF.public

  protected:
    // Additional Protected Declarations
      //## begin Subscriptions%3C999C8400AF.protected preserve=yes
      //## end Subscriptions%3C999C8400AF.protected

  private:
    // Additional Private Declarations
      //## begin Subscriptions%3C999C8400AF.private preserve=yes
      //## end Subscriptions%3C999C8400AF.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin Subscriptions%3C999C8400AF.implementation preserve=yes
      typedef struct { HIID mask; MsgAddress scope; } SubElement;
      typedef list<SubElement> SubSet;
      SubSet subs;
      typedef SubSet::iterator SSI;
      typedef SubSet::const_iterator CSSI;

      // this always keep track of the pack-size of the set.
      // it is updated by add() and remove().
      size_t pksize;
      //## end Subscriptions%3C999C8400AF.implementation
};

//## begin Subscriptions%3C999C8400AF.postscript preserve=yes
//## end Subscriptions%3C999C8400AF.postscript

// Class Subscriptions 


//## Other Operations (inline)
inline int Subscriptions::size () const
{
  //## begin Subscriptions::size%3C99C0BB0378.body preserve=yes
  return subs.size();
  //## end Subscriptions::size%3C99C0BB0378.body
}

inline size_t Subscriptions::packSize () const
{
  //## begin Subscriptions::packSize%3C99AC2F027F.body preserve=yes
  return pksize;
  //## end Subscriptions::packSize%3C99AC2F027F.body
}

//## begin module%3C999E140208.epilog preserve=yes
//## end module%3C999E140208.epilog


#endif

//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C95AADB0101.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C95AADB0101.cm

//## begin module%3C95AADB0101.cp preserve=no
//## end module%3C95AADB0101.cp

//## Module: GWServerWP%3C95AADB0101; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\GWServerWP.h

#ifndef GWServerWP_h
#define GWServerWP_h 1

//## begin module%3C95AADB0101.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C95AADB0101.additionalIncludes

//## begin module%3C95AADB0101.includes preserve=yes
//## end module%3C95AADB0101.includes

// Socket
#include "OCTOPUSSY/Net/Socket.h"
// GatewayWP
#include "OCTOPUSSY/GatewayWP.h"
// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
//## begin module%3C95AADB0101.declarations preserve=no
//## end module%3C95AADB0101.declarations

//## begin module%3C95AADB0101.additionalDeclarations preserve=yes
#pragma aid Gateway GWServerWP GWClientWP GatewayWP
//## end module%3C95AADB0101.additionalDeclarations


//## begin GWServerWP%3C8F942502BA.preface preserve=yes
//## end GWServerWP%3C8F942502BA.preface

//## Class: GWServerWP%3C8F942502BA
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C90BEFA02E4;GatewayWP { -> }

class GWServerWP : public WorkProcess  //## Inherits: <unnamed>%3C8F943E01B2
{
  //## begin GWServerWP%3C8F942502BA.initialDeclarations preserve=yes
  //## end GWServerWP%3C8F942502BA.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: GWServerWP%3C8F95710177
      GWServerWP (int port1 = -1);

      //## Operation: GWServerWP%3CC95151026E
      GWServerWP (const string &path = "", int port1 = -1);

    //## Destructor (generated)
      ~GWServerWP();


    //## Other Operations (specified)
      //## Operation: init%3CC951680113
      virtual void init ();

      //## Operation: start%3C90BE4A029B
      virtual bool start ();

      //## Operation: stop%3C90BE880037
      virtual void stop ();

      //## Operation: timeout%3C90BE8E000E
      virtual int timeout (const HIID &);

      //## Operation: input%3C95B4DC031C
      virtual int input (int , int );

      //## Operation: receive%3CC951890246
      virtual int receive (MessageRef &mref);

    // Additional Public Declarations
      //## begin GWServerWP%3C8F942502BA.public preserve=yes
      void advertiseServer();
      
      //## end GWServerWP%3C8F942502BA.public
  protected:
    // Additional Protected Declarations
      //## begin GWServerWP%3C8F942502BA.protected preserve=yes
      // tries to open server socket
      void tryOpen ();
      //## end GWServerWP%3C8F942502BA.protected
  private:
    //## Constructors (generated)
      GWServerWP(const GWServerWP &right);

    //## Assignment Operation (generated)
      GWServerWP & operator=(const GWServerWP &right);

    // Additional Private Declarations
      //## begin GWServerWP%3C8F942502BA.private preserve=yes
      //## end GWServerWP%3C8F942502BA.private

  private: //## implementation
    // Data Members for Class Attributes

      //## Attribute: port%3C90BE3503C7
      //## begin GWServerWP::port%3C90BE3503C7.attr preserve=no  public: int {U} 
      int port;
      //## end GWServerWP::port%3C90BE3503C7.attr

      //## Attribute: hostname%3CC951EA0214
      //## begin GWServerWP::hostname%3CC951EA0214.attr preserve=no  private: string {U} 
      string hostname;
      //## end GWServerWP::hostname%3CC951EA0214.attr

    // Data Members for Associations

      //## Association: OCTOPUSSY::<unnamed>%3C922571000B
      //## Role: GWServerWP::sock%3C92257101CE
      //## begin GWServerWP::sock%3C92257101CE.role preserve=no  private: Socket { -> 0..1RHgN}
      Socket *sock;
      //## end GWServerWP::sock%3C92257101CE.role

    // Additional Implementation Declarations
      //## begin GWServerWP%3C8F942502BA.implementation preserve=yes
      int type;  // Socket::TCP or Socket::UNIX
      MessageRef advertisement;
      int open_retries;
      //## end GWServerWP%3C8F942502BA.implementation
};

//## begin GWServerWP%3C8F942502BA.postscript preserve=yes
//## end GWServerWP%3C8F942502BA.postscript

// Class GWServerWP 

//## begin module%3C95AADB0101.epilog preserve=yes
//## end module%3C95AADB0101.epilog


#endif

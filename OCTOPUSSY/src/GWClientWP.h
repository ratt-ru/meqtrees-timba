//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C95AADB016E.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C95AADB016E.cm

//## begin module%3C95AADB016E.cp preserve=no
//## end module%3C95AADB016E.cp

//## Module: GWClientWP%3C95AADB016E; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\GWClientWP.h

#ifndef GWClientWP_h
#define GWClientWP_h 1

//## begin module%3C95AADB016E.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C95AADB016E.additionalIncludes

//## begin module%3C95AADB016E.includes preserve=yes
#include <list>
//## end module%3C95AADB016E.includes

// Socket
#include "OCTOPUSSY/Net/Socket.h"
// GatewayWP
#include "OCTOPUSSY/GatewayWP.h"
// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
//## begin module%3C95AADB016E.declarations preserve=no
//## end module%3C95AADB016E.declarations

//## begin module%3C95AADB016E.additionalDeclarations preserve=yes
#pragma aid Reconnect FailConnect Reopen Server List Hosts Ports
//## end module%3C95AADB016E.additionalDeclarations


//## begin GWClientWP%3C95A941002E.preface preserve=yes
//## end GWClientWP%3C95A941002E.preface

//## Class: GWClientWP%3C95A941002E
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C95AA83029E;GatewayWP { -> }

class GWClientWP : public WorkProcess  //## Inherits: <unnamed>%3C95A941009C
{
  //## begin GWClientWP%3C95A941002E.initialDeclarations preserve=yes
  public:
      typedef struct { string    host;
                       int       port;
                       int       type;
                       Socket   *sock;
                       int       state; 
                       Timestamp retry,fail,give_up;
                       bool      reported_failure;
      // When we spawn a child gateway, we watch for its bye message
      // to know when to start connecting again. This holds its address.
                       MsgAddress gw;
              } Connection;
  //## end GWClientWP%3C95A941002E.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: GWClientWP%3CD0167B021B
      GWClientWP (const string &host = "", int port = 0, int type = Socket::TCP);

    //## Destructor (generated)
      ~GWClientWP();


    //## Other Operations (specified)
      //## Operation: init%3CA1C0C300FA
      virtual void init ();

      //## Operation: start%3C95A941008B
      bool start ();

      //## Operation: stop%3C95A9410092
      void stop ();

      //## Operation: timeout%3C95A9410093
      int timeout (const HIID &id);

      //## Operation: receive%3C95A9410095
      int receive (MessageRef& mref);

    // Additional Public Declarations
      //## begin GWClientWP%3C95A941002E.public preserve=yes
      typedef enum { STOPPED=0,WAITING=1,CONNECTING=2,CONNECTED=3 } States;
      //## end GWClientWP%3C95A941002E.public
  protected:
    // Additional Protected Declarations
      //## begin GWClientWP%3C95A941002E.protected preserve=yes
      // maintain connection list
      Connection &  addConnection    (const string &host,int port,int type);
      bool          removeConnection (const string &host,int port);
      GWClientWP::Connection * find (const string &host, const string &port);
      GWClientWP::Connection * find (const MsgAddress &gw);
      
      // begins connecting
      void activate ();
      // tries to open and connect the socket
      void tryConnect ( Connection &cx );
      
      Timestamp now;
      bool reconnect_timeout_set;
      
      ObjRef peerref;
      DataRecord & peerlist;
      //## end GWClientWP%3C95A941002E.protected
  private:
    //## Constructors (generated)
      GWClientWP(const GWClientWP &right);

    //## Assignment Operation (generated)
      GWClientWP & operator=(const GWClientWP &right);

    // Additional Private Declarations
      //## begin GWClientWP%3C95A941002E.private preserve=yes
      //## end GWClientWP%3C95A941002E.private

  private: //## implementation
    // Data Members for Class Attributes

      //## Attribute: hostname%3CC951FA0127
      //## begin GWClientWP::hostname%3CC951FA0127.attr preserve=no  private: string {U} 
      string hostname;
      //## end GWClientWP::hostname%3CC951FA0127.attr

    // Data Members for Associations

      //## Association: OCTOPUSSY::<unnamed>%3C95A941009D
      //## Role: GWClientWP::conns%3C95A941009E
      //## begin GWClientWP::conns%3C95A941009E.role preserve=no  private: Socket { -> 0..*RHgN}
      list<Connection> conns;
      //## end GWClientWP::conns%3C95A941009E.role

    // Additional Implementation Declarations
      //## begin GWClientWP%3C95A941002E.implementation preserve=yes
      typedef list<Connection>::iterator CLI;
      typedef list<Connection>::const_iterator CCLI;
      //## end GWClientWP%3C95A941002E.implementation
};

//## begin GWClientWP%3C95A941002E.postscript preserve=yes
//## end GWClientWP%3C95A941002E.postscript

// Class GWClientWP 

//## begin module%3C95AADB016E.epilog preserve=yes
//## end module%3C95AADB016E.epilog


#endif

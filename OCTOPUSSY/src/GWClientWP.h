#ifndef GWClientWP_h
#define GWClientWP_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include <list>
#include "OCTOPUSSY/MTGatewayWP.h"

// Socket
#include "Common/Net/Socket.h"

// GatewayWP
#include "OCTOPUSSY/GatewayWP.h"
// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
//class Socket;
#pragma aid Reconnect FailConnect Reopen Server List Hosts Ports


//##ModelId=3C95A941002E

class GWClientWP : public WorkProcess
{
  public:
    //##ModelId=3DB936500103
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

  public:
      //##ModelId=3CD0167B021B
      GWClientWP (const string &host = "", int port = 0, int type = Socket::TCP);

    //##ModelId=3DB9367B00EA
      ~GWClientWP();


      //##ModelId=3CA1C0C300FA
      virtual void init ();

      //##ModelId=3C95A941008B
      bool start ();

      //##ModelId=3C95A9410092
      void stop ();

      //##ModelId=3C95A9410093
      int timeout (const HIID &id);

      //##ModelId=3C95A9410095
      int receive (MessageRef& mref);

    // Additional Public Declarations
    //##ModelId=3DB93650012B
      typedef enum { STOPPED=0,WAITING=1,CONNECTING=2,CONNECTED=3 } States;
  protected:
    // Additional Protected Declarations
      // maintain connection list
    //##ModelId=3DB9367B0126
      Connection &  addConnection    (const string &host,int port,int type);
    //##ModelId=3DB9367B02B6
      bool          removeConnection (const string &host,int port);
    //##ModelId=3DB9367C000F
      GWClientWP::Connection * find (const string &host, const string &port);
    //##ModelId=3DB9367C01F7
      GWClientWP::Connection * find (const MsgAddress &gw);
      
      // begins connecting
    //##ModelId=3DB9367C0305
      void activate ();
      // tries to open and connect the socket
    //##ModelId=3DB9367C037D
      void tryConnect ( Connection &cx );
      
    //##ModelId=3DB9367A0374
      Timestamp now;
    //##ModelId=3DB9367A03A5
      bool reconnect_timeout_set;
      
    //##ModelId=3DB9367B0021
      ObjRef peerref;
    //##ModelId=3DB9367B009A
      DataRecord & peerlist;
  private:
    //##ModelId=3DB9367D00C2
      GWClientWP(const GWClientWP &right);

    //##ModelId=3DB9367D029F
      GWClientWP & operator=(const GWClientWP &right);

  private:
    // Data Members for Class Attributes

      //##ModelId=3CC951FA0127
      string hostname;

    // Data Members for Associations

      //##ModelId=3DB958F20327
      list<Connection> conns;

    // Additional Implementation Declarations
    //##ModelId=3DB936500167
      typedef list<Connection>::iterator CLI;
    //##ModelId=3DB936500199
      typedef list<Connection>::const_iterator CCLI;
};

// Class GWClientWP 


#endif

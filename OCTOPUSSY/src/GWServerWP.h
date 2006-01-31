#ifndef OCTOPUSSY_GWServerWP_h
#define OCTOPUSSY_GWServerWP_h 1

#include <TimBase/Net/Socket.h>
#include <DMI/DMI.h>
#include <OCTOPUSSY/MTGatewayWP.h>
#include <OCTOPUSSY/GatewayWP.h>
#include <OCTOPUSSY/WorkProcess.h>

#pragma aid Gateway GWServerWP GWClientWP GatewayWP

namespace Octopussy
{

//##ModelId=3C8F942502BA

class GWServerWP : public WorkProcess
{
  public:
      //##ModelId=3C8F95710177
      GWServerWP (int port1 = -1);

      //##ModelId=3CC95151026E
      GWServerWP (const string &path = "", int port1 = -1);

    //##ModelId=3DB9367E019C
      ~GWServerWP();


      //##ModelId=3CC951680113
      virtual void init ();

      //##ModelId=3C90BE4A029B
      virtual bool start ();

      //##ModelId=3C90BE880037
      virtual void stop ();

      //##ModelId=3C90BE8E000E
      virtual int timeout (const HIID &);

      //##ModelId=3C95B4DC031C
      virtual int input (int , int );

      //##ModelId=3CC951890246
      virtual int receive (Message::Ref &mref);

    // Additional Public Declarations
    //##ModelId=3DB9367E033E
      void advertiseServer();
      
  protected:
    // Additional Protected Declarations
      // tries to open server socket
    //##ModelId=3DB9367E037A
      void tryOpen ();
  private:
    //##ModelId=3DB9367F000A
      GWServerWP(const GWServerWP &right);

    //##ModelId=3DB9367F0104
      GWServerWP & operator=(const GWServerWP &right);

  private:
    // Data Members for Class Attributes

      //##ModelId=3C90BE3503C7
      int port;

      //##ModelId=3CC951EA0214
      string hostname;

    // Data Members for Associations

      //##ModelId=3C92257101CE
      Socket *sock;

    // Additional Implementation Declarations
    //##ModelId=3DB9367E0051
      int type;  // Socket::TCP or Socket::UNIX
    //##ModelId=3DB9367E00D5
      Message::Ref advertisement;
    //##ModelId=3DB9367E0110
      int open_retries;
};

// Class GWServerWP 


};
#endif

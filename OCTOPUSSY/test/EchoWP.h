#ifndef EchoWP_h
#define EchoWP_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include "OCTOPUSSY/LatencyVector.h"

// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
#pragma aidgroup Testing
#pragma aid EchoWP Ping Pong
#pragma aid Reply Timestamp Invert Data Count Process
#include "AID-Testing.h"


//##ModelId=3C7E498E00D1
class EchoWP : public WorkProcess
{
  public:
      //##ModelId=3C7E49B60327
      EchoWP (int pingcount = 0);

    //##ModelId=3DB936790173
      ~EchoWP();


      //##ModelId=3C7F884A007D
      virtual void init ();

      //##ModelId=3C7E4AC70261
      virtual bool start ();

      //##ModelId=3C7E49AC014C
      virtual int receive (MessageRef& mref);

      //##ModelId=3C98CB600343
      virtual int timeout (const HIID &);

  protected:
    // Additional Protected Declarations
    //##ModelId=3DB93677029C
      int pcount,blocksize,pipeline,fill;
    //##ModelId=3DB9367703C9
      int process,threads;
  
    //##ModelId=3DB936780095
      long   bytecount,msgcount;
    //##ModelId=3DB936780167
      double ts,timecount;
#ifdef ENABLE_LATENCY_STATS
    //##ModelId=3DB958F202CA
      LatencyVector pinglat,ponglat;
    //##ModelId=3DB93678033E
      int nping,npong;
    //##ModelId=3DB93679005A
      double ping_ts,pong_ts;
#endif
      
    //##ModelId=3DB93679023B
      void stepCounters ( size_t nb,const Timestamp &stamp );
  
    //##ModelId=3DB9367903B8
      void sendPing (int pc);
  private:
    //##ModelId=3DB9367A00E8
      EchoWP(const EchoWP &right);

    //##ModelId=3DB9367A01F6
      EchoWP & operator=(const EchoWP &right);

};

// Class EchoWP 


#endif

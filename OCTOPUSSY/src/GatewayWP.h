#ifndef GatewayWP_h
#define GatewayWP_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

// Socket
#include "Common/Net/Socket.h"
using LOFAR::Socket;
// Subscriptions
#include "OCTOPUSSY/Subscriptions.h"
// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
#pragma aid Subscriptions Init Heartbeat


//##ModelId=3C90BEF001E5
class GatewayWP : public WorkProcess
{
  public:
      //##ModelId=3C95C53D00AE
      GatewayWP (LOFAR::Socket* sk);

    //##ModelId=3DB93683017B
      ~GatewayWP();


      //##ModelId=3CC9500602CC
      virtual void init ();

      //##ModelId=3C90BF460080
      virtual bool start ();

      //##ModelId=3C90BF4A039D
      virtual void stop ();

      //##ModelId=3C90BF5C001E
      //##Documentation
      //## Returns True if this WP will forward this non-local message.
      virtual bool willForward (const Message &msg) const;

      //##ModelId=3C90BF63005A
      virtual int receive (MessageRef& mref);

      //##ModelId=3C90BF6702C3
      virtual int timeout (const HIID &id);

      //##ModelId=3C90BF6F00ED
      virtual int input (int fd, int flags);

  protected:
    // Additional Protected Declarations
      // packet header structure
    //##ModelId=3DB9365001F3
      typedef struct { char  signature[3];
                       uchar type;
                       long  content; 
                     } PacketHeader;
                       
      // data block trailer structure
    //##ModelId=3DB936500225
      typedef struct { int  seq;
                       long checksum;
                       int  msgsize;
                     } DataTrailer;
                       
      
    //##ModelId=3DB936500261
      typedef enum { MT_PING=0,MT_DATA=1,MT_ACK=2,MT_RETRY=3,
                     MT_ABORT=4,MT_MAXTYPE=4 } PacketTypes;
      
    //##ModelId=3DB936500293
      typedef enum { IDLE=0,HEADER=1,BLOCK=2,TRAILER=3 } DataState;
      
    //##ModelId=3DB9365002C6
      typedef enum { INITIALIZING = 0, 
                     CONNECTED    = 1, 
                     CONN_ERROR   = 2, 
                     CLOSING      = 3  } PeerState;
      
      // closes down the gateway
    //##ModelId=3DB93684000A
      void shutdown ();
      
      // Helper functions to get/set the state
      // The read/write/peer states are maintained in the first, second and
      // third byte of the overall WP state.
    //##ModelId=3DB9368400AA
      int readState () const     { return state()&0xFF; };
    //##ModelId=3DB936840186
      int writeState () const    { return (state()&0xFF00)>>8; };
    //##ModelId=3DB936850065
      int peerState () const     { return (state()&0xFF0000)>>16; };
      
    //##ModelId=3DB936850169
      void setReadState  (int st)  { setState((state()&~0xFF)|st,True); };
    //##ModelId=3DB93685030E
      void setWriteState (int st)  { setState((state()&~0xFF00)|(st<<8),True); };
    //##ModelId=3DB9368700BB
      void setPeerState  (int st)  { setState((state()&~0xFF0000)|(st<<16)); };
      
      // Helper functions for reading from socket
    //##ModelId=3DB9368702B9
      int requestResync   ();   // ask remote to abort & resync
    //##ModelId=3DB936870382
      int requestRetry    ();   // ask remote to resend last message
    //##ModelId=3DB936880062
      int readyForHeader  ();   // start looking for header
    //##ModelId=3DB9368801BC
      int readyForTrailer ();   // peraprte to receive trailer
    //##ModelId=3DB93688028E
      int readyForData    (const PacketHeader &hdr); // prepare to receive data block
    //##ModelId=3DB9368900C3
      void processIncoming();   // unblocks and sends off incoming message
      
      // parses the initialization message
    //##ModelId=3DB9368901C7
      void processInitMessage( const void *block,size_t blocksize );
    
      // Helper functions for writing to socket
    //##ModelId=3DB9368B0224
      void prepareMessage (MessageRef &mref);
    //##ModelId=3DB9368D008D
      void prepareHeader  ();
    //##ModelId=3DB9368D01A5
      void prepareData    ();
    //##ModelId=3DB9368D02C7
      void prepareTrailer ();
      
      // remote info
    //##ModelId=3DB9367F0264
      AtomicID rhost,rprocess;
      
      // incoming/outgoing packet header
    //##ModelId=3DB9367F02D2
      PacketHeader header,wr_header;
      // read buffer for data trailer
    //##ModelId=3DB9367F0340
      DataTrailer  trailer,wr_trailer;
      // max size of xmitted block. Anything bigger than that will cause
      // an error (should be in shared memory!)
    //##ModelId=3DB9367F03B7
      static const int MaxBlockSize = 512*1024*1024;
      
      // reading state
    //##ModelId=3DB93680005C
      DataState readstate;
    //##ModelId=3DB9368000A1
      char *read_buf;
    //##ModelId=3DB93680012E
      int   read_buf_size,
            nread,
            read_junk;
    //##ModelId=3DB9368002E6
      long  read_checksum,
            incoming_checksum;
    //##ModelId=3DB9368100C3
      BlockSet read_bset;
      
      // writing state
    //##ModelId=3DB936810109
      DataState writestate;
    //##ModelId=3DB936810158
      const char *write_buf;
    //##ModelId=3DB936810216
      int   write_buf_size,nwritten;
    //##ModelId=3DB936810375
      long  write_checksum;
    //##ModelId=3DB93682004C
      BlockSet write_queue;
    //##ModelId=3DB936820152
      int   write_seq;                 // sequence number
    //##ModelId=3DB93682022E
      int   write_msgsize;
    //##ModelId=3DB9368202F7
      MessageRef pending_msg;          // one pending write-slot
      
      // timestamps for pings
    //##ModelId=3DB936820365
      Timestamp last_read,last_write,last_write_to;      
      // this is is the status monitor
    //##ModelId=3DB936500302
      typedef struct {
        int  counter;
        unsigned long long read,written;
        double ts;
      } StatMon;
    //##ModelId=3DB936830096
      StatMon statmon;
      
  private:
    //##ModelId=3DB9368D03D6
      GatewayWP();

    //##ModelId=3DB9368E00DE
      GatewayWP(const GatewayWP &right);

    //##ModelId=3DB936900094
      GatewayWP & operator=(const GatewayWP &right);

    // Additional Private Declarations
    //##ModelId=3DB9368300F0
      DataRecord *peerlist;
  private:
    // Data Members for Associations

      //##ModelId=3C9225740345
      LOFAR::Socket *sock;

      //##ModelId=3DB958F203BF
      map<MsgAddress,Subscriptions> remote_subs;

    // Additional Implementation Declarations
    //##ModelId=3DB936500334
      typedef map<MsgAddress,Subscriptions>::iterator RSI;
    //##ModelId=3DB93650037A
      typedef map<MsgAddress,Subscriptions>::const_iterator CRSI;
};

// Class GatewayWP 


#endif

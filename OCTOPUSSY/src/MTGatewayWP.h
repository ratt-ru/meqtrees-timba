#ifndef MTGatewayWP_h
#define MTGatewayWP_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#ifdef USE_THREADS

#include "Common/Thread.h"
#include "Common/Thread/Condition.h"
#include <deque>
using std::deque;
//##ModelId=3DB958F10261

// Socket
#include "Common/Net/Socket.h"
using namespace LOFAR;

// Subscriptions
#include "OCTOPUSSY/Subscriptions.h"
// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"

#pragma aid Subscriptions Init Heartbeat


class MTGatewayWP : public WorkProcess  //## Inherits: <unnamed>%3C90BF100390
{

  public:
    //##ModelId=3DB958F403D0
      MTGatewayWP (Socket* sk);

    //##ModelId=3DB958F5004C
      ~MTGatewayWP();


    //##ModelId=3DB958F5004D
      virtual void init ();

    //##ModelId=3DB958F5004F
      virtual bool start ();

    //##ModelId=3DB958F50051
      virtual void stop ();

    //##ModelId=3DB958F50053
      //	Returns True if this WP will forward this non-local message
      virtual bool willForward (const Message &msg) const;

    //##ModelId=3DB958F500B8
      virtual int receive (MessageRef& mref);

    //##ModelId=3DB958F5011C
      virtual int timeout (const HIID &id);

    // Additional Public Declarations

  protected:
    // Additional Protected Declarations
    //##ModelId=3DB958F10268
      // packet header structure
      typedef struct { char  signature[3];
                       uchar type;
                       long  content; 
                     } PacketHeader;
                       
      // data block trailer structure
    //##ModelId=3DB958F1026E
      typedef struct { int  seq;
                       long checksum;
                       int  msgsize;
                     } DataTrailer;
                       
      
    //##ModelId=3DB958F10273
      typedef enum { MT_PING=0,MT_DATA=1,MT_ACK=2,MT_RETRY=3,
                     MT_ABORT=4,MT_MAXTYPE=4 } PacketTypes;
      
    //##ModelId=3DB958F10278
      typedef enum { IDLE=0,HEADER=1,BLOCK=2,TRAILER=3 } DataState;
      
    //##ModelId=3DB958F1027D
      typedef enum { INITIALIZING = 0, 
                     CONNECTED    = 1, 
                     CONN_ERROR   = 2, 
                     CLOSING      = 3  } PeerState;
      
      // closes down the gateway
    //##ModelId=3DB958F50181
      void shutdown ();
      
      // Helper functions to get/set the state
      // The read/write/peer states are maintained in the first, second and
      // third byte of the overall WP state.
    //##ModelId=3DB958F50182
      int readState () const     { return state()&0xFF; };
    //##ModelId=3DB958F50185
      int writeState () const    { return (state()&0xFF00)>>8; };
    //##ModelId=3DB958F50187
      int peerState () const     { return (state()&0xFF0000)>>16; };
      
    //##ModelId=3DB958F5018A
      void setReadState  (int st)  { setState((state()&~0xFF)|st,True); };
    //##ModelId=3DB958F501EF
      void setWriteState (int st)  { setState((state()&~0xFF00)|(st<<8),True); };
    //##ModelId=3DB958F50253
      void setPeerState  (int st)  { setState((state()&~0xFF0000)|(st<<16)); };
      
      // Helper functions for reading from socket
    //##ModelId=3DB958F502B8
      int requestResync   ();   // ask remote to abort & resync
    //##ModelId=3DB958F502BA
      int requestRetry    ();   // ask remote to resend last message
    //##ModelId=3DB958F502BC
      int readyForHeader  ();   // start looking for header
    //##ModelId=3DB958F502BD
      int readyForTrailer ();   // peraprte to receive trailer
    //##ModelId=3DB958F502BF
      int readyForData    (const PacketHeader &hdr,BlockSet &bset); // prepare to receive data block
      
    //##ModelId=3DB958F50385
      void processIncoming(MessageRef &mref);   // sends off incoming message
      
      // reports write error and terminates writer thread
    //##ModelId=3DB958F60001
      void reportWriteError ();
          
      // parses the initialization message
    //##ModelId=3DB958F60003
      int  processInitMessage( const void *block,size_t blocksize );
    
      // Helper functions for writing to socket
    //##ModelId=3DB958F600CB
      void transmitMessage (MessageRef &mref);
      
      // remote info
    //##ModelId=3DB958F301AD
      AtomicID rhost,rprocess;
      
      // max size of xmitted block. Anything bigger than that will cause
      // an error (should be in shared memory!)
    //##ModelId=3DB958F301CA
      static const int MaxBlockSize = 512*1024*1024;
      
      // this is is the status monitor
    //##ModelId=3DB958F10283
      typedef struct {
        Thread::Mutex stat_mutex;
        int counter;
        double ts;
        unsigned long long read,written; 
        Timestamp last_read,last_write,time_not_reading;
        Thread::Mutex read_mutex,write_mutex;
      } StatMon;
    //##ModelId=3DB958F301D8
      StatMon statmon;
      
    //##ModelId=3DB958F6012F
      bool mtStart     (Thread::ThrID);
    //##ModelId=3DB958F6017B
      void stopWorkers ();
  private:
    //##ModelId=3DB958F6017C
      MTGatewayWP();

    //##ModelId=3DB958F6017E
      MTGatewayWP(const MTGatewayWP &right);

    //##ModelId=3DB958F601E2
      MTGatewayWP & operator=(const MTGatewayWP &right);

    // Additional Private Declarations
    //##ModelId=3DB958F301EA
      // list of peers
      DataRecord *peerlist;

      // separate reader threads are run
    //##ModelId=3DB958F60246
      static void * start_readerThread (void *pwp);
    //##ModelId=3DB958F602AB
      void * readerThread ();
      
    //##ModelId=3DB958F301FE
      static const int NumWriterThreads = 2, NumReaderThreads = 2;
    //##ModelId=3DB958F3022F
      Thread::ThrID reader_threads[NumReaderThreads];
      
      // mutex for global gateway states
    //##ModelId=3DB958F3024A
      Thread::Mutex gwmutex;
      
      // write state
    //##ModelId=3DB958F30264
      Thread::Mutex writer_mutex;
    //##ModelId=3DB958F30280
      bool writing;
    //##ModelId=3DB958F302AA
      Timestamp write_timestamp;
    //##ModelId=3DB958F302C8
      int write_seq;
    //##ModelId=3DB958F302F7
      PacketHeader wr_header;
      
      // queue for reader thread(s)
      // we have a pool (at least two) reader threads. Only one
      // may be reading something, hence the reader_mutex
    //##ModelId=3DB958F30319
      Thread::Mutex reader_mutex;
    //##ModelId=3DB958F3033F
      DataState readstate;
    //##ModelId=3DB958F30366
      char *read_buf;
    //##ModelId=3DB958F303A3
      int nread,read_buf_size;
    //##ModelId=3DB958F40036
      int read_checksum;
    //##ModelId=3DB958F40076
      Timestamp start_message_read,
      // these timestamps keep timing stats on how long we spend w/o any
      // threads reading the socket
          ts_stopread;
    //##ModelId=3DB958F400CC
      bool reading_socket,first_message_read; 
      
      // incoming packet header & trailer
    //##ModelId=3DB958F4015E
      PacketHeader header;
    //##ModelId=3DB958F4018E
      DataTrailer  trailer;
      
      // this is the initialization message, prepared in start()
    //##ModelId=3DB958F401C1
      MessageRef initmsg;
    //##ModelId=3DB958F401F6
      bool initmsg_sent;
      
    //##ModelId=3DB958F4024E
      bool shutdown_done;
      
    //##ModelId=3DB958F402A7
      static const char * PacketSignature;
      
  private:
    //##ModelId=3DB958F40301
    // Data Members for Associations

      Socket *sock;
    //##ModelId=3DB958F40337

      map<MsgAddress,Subscriptions> remote_subs;
    //##ModelId=3DB958F40396

    // Additional Implementation Declarations
      Thread::Mutex remote_subs_mutex;
    //##ModelId=3DB958F10288
      typedef map<MsgAddress,Subscriptions>::iterator RSI;
    //##ModelId=3DB958F1028D
      typedef map<MsgAddress,Subscriptions>::const_iterator CRSI;
      
};


// Class MTGatewayWP 

#endif // USE_THREADS


#endif

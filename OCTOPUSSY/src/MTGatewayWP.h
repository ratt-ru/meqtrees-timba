//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C90BFDD0236.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C90BFDD0236.cm

//## begin module%3C90BFDD0236.cp preserve=no
//## end module%3C90BFDD0236.cp

//## Module: MTGatewayWP%3C90BFDD0236; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\MTGatewayWP.h

#ifndef MTGatewayWP_h
#define MTGatewayWP_h 1

//## begin module%3C90BFDD0236.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C90BFDD0236.additionalIncludes

//## begin module%3C90BFDD0236.includes preserve=yes
#ifdef USE_THREADS

#include "Common/Thread.h"
#include "Common/Thread/Condition.h"
#include <deque>
using std::deque;
//##ModelId=3DB958F10261
//## end module%3C90BFDD0236.includes

// Socket
#include "OCTOPUSSY/Net/Socket.h"
// Subscriptions
#include "OCTOPUSSY/Subscriptions.h"
// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
//## begin module%3C90BFDD0236.declarations preserve=no
//## end module%3C90BFDD0236.declarations

//## begin module%3C90BFDD0236.additionalDeclarations preserve=yes
#pragma aid Subscriptions Init Heartbeat
//## end module%3C90BFDD0236.additionalDeclarations


//## begin MTGatewayWP%3C90BEF001E5.preface preserve=yes
//## end MTGatewayWP%3C90BEF001E5.preface

//## Class: MTGatewayWP%3C90BEF001E5
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class MTGatewayWP : public WorkProcess  //## Inherits: <unnamed>%3C90BF100390
{
  //## begin MTGatewayWP%3C90BEF001E5.initialDeclarations preserve=yes
  //## end MTGatewayWP%3C90BEF001E5.initialDeclarations

  public:
    //##ModelId=3DB958F403D0
    //## Constructors (specified)
      //## Operation: MTGatewayWP%3C95C53D00AE
      MTGatewayWP (Socket* sk);

    //##ModelId=3DB958F5004C
    //## Destructor (generated)
      ~MTGatewayWP();


    //##ModelId=3DB958F5004D
    //## Other Operations (specified)
      //## Operation: init%3CC9500602CC
      virtual void init ();

    //##ModelId=3DB958F5004F
      //## Operation: start%3C90BF460080
      virtual bool start ();

    //##ModelId=3DB958F50051
      //## Operation: stop%3C90BF4A039D
      virtual void stop ();

    //##ModelId=3DB958F50053
      //## Operation: willForward%3C90BF5C001E
      //	Returns True if this WP will forward this non-local message
      virtual bool willForward (const Message &msg) const;

    //##ModelId=3DB958F500B8
      //## Operation: receive%3C90BF63005A
      virtual int receive (MessageRef& mref);

    //##ModelId=3DB958F5011C
      //## Operation: timeout%3C90BF6702C3
      virtual int timeout (const HIID &id);

    // Additional Public Declarations
      //## begin MTGatewayWP%3C90BEF001E5.public preserve=yes
      //## end MTGatewayWP%3C90BEF001E5.public

  protected:
    // Additional Protected Declarations
    //##ModelId=3DB958F10268
      //## begin MTGatewayWP%3C90BEF001E5.protected preserve=yes
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
      //## end MTGatewayWP%3C90BEF001E5.protected
  private:
    //##ModelId=3DB958F6017C
    //## Constructors (generated)
      MTGatewayWP();

    //##ModelId=3DB958F6017E
      MTGatewayWP(const MTGatewayWP &right);

    //##ModelId=3DB958F601E2
    //## Assignment Operation (generated)
      MTGatewayWP & operator=(const MTGatewayWP &right);

    // Additional Private Declarations
    //##ModelId=3DB958F301EA
      //## begin MTGatewayWP%3C90BEF001E5.private preserve=yes
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
      
      //## end MTGatewayWP%3C90BEF001E5.private
  private:
    //##ModelId=3DB958F40301
    //## implementation
    // Data Members for Associations

      //## Association: OCTOPUSSY::<unnamed>%3C9225740182
      //## Role: MTGatewayWP::sock%3C9225740345
      //## begin MTGatewayWP::sock%3C9225740345.role preserve=no  private: Socket { -> 0..1RHgN}
      Socket *sock;
    //##ModelId=3DB958F40337
      //## end MTGatewayWP::sock%3C9225740345.role

      //## Association: OCTOPUSSY::<unnamed>%3C9B06A30088
      //## Role: MTGatewayWP::remote_subs%3C9B06A303D1
      //## begin MTGatewayWP::remote_subs%3C9B06A303D1.role preserve=no  private: Subscriptions { -> 0..*VHgN}
      map<MsgAddress,Subscriptions> remote_subs;
    //##ModelId=3DB958F40396
      //## end MTGatewayWP::remote_subs%3C9B06A303D1.role

    // Additional Implementation Declarations
      //## begin MTGatewayWP%3C90BEF001E5.implementation preserve=yes
      Thread::Mutex remote_subs_mutex;
    //##ModelId=3DB958F10288
      typedef map<MsgAddress,Subscriptions>::iterator RSI;
    //##ModelId=3DB958F1028D
      typedef map<MsgAddress,Subscriptions>::const_iterator CRSI;
      
      //## end MTGatewayWP%3C90BEF001E5.implementation
};

//## begin MTGatewayWP%3C90BEF001E5.postscript preserve=yes
//## end MTGatewayWP%3C90BEF001E5.postscript

// Class MTGatewayWP 

//## begin module%3C90BFDD0236.epilog preserve=yes
#endif // USE_THREADS
//## end module%3C90BFDD0236.epilog


#endif

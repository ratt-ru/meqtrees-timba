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
    //## Constructors (specified)
      //## Operation: MTGatewayWP%3C95C53D00AE
      MTGatewayWP (Socket* sk);

    //## Destructor (generated)
      ~MTGatewayWP();


    //## Other Operations (specified)
      //## Operation: init%3CC9500602CC
      virtual void init ();

      //## Operation: start%3C90BF460080
      virtual bool start ();

      //## Operation: stop%3C90BF4A039D
      virtual void stop ();

      //## Operation: willForward%3C90BF5C001E
      //	Returns True if this WP will forward this non-local message
      virtual bool willForward (const Message &msg) const;

      //## Operation: receive%3C90BF63005A
      virtual int receive (MessageRef& mref);

      //## Operation: timeout%3C90BF6702C3
      virtual int timeout (const HIID &id);

    // Additional Public Declarations
      //## begin MTGatewayWP%3C90BEF001E5.public preserve=yes
      //## end MTGatewayWP%3C90BEF001E5.public

  protected:
    // Additional Protected Declarations
      //## begin MTGatewayWP%3C90BEF001E5.protected preserve=yes
      // packet header structure
      typedef struct { char  signature[3];
                       uchar type;
                       long  content; 
                     } PacketHeader;
                       
      // data block trailer structure
      typedef struct { int  seq;
                       long checksum;
                       int  msgsize;
                     } DataTrailer;
                       
      
      typedef enum { MT_PING=0,MT_DATA=1,MT_ACK=2,MT_RETRY=3,
                     MT_ABORT=4,MT_MAXTYPE=4 } PacketTypes;
      
      typedef enum { IDLE=0,HEADER=1,BLOCK=2,TRAILER=3 } DataState;
      
      typedef enum { INITIALIZING = 0, 
                     CONNECTED    = 1, 
                     CONN_ERROR   = 2, 
                     CLOSING      = 3  } PeerState;
      
      // closes down the gateway
      void shutdown ();
      
      // Helper functions to get/set the state
      // The read/write/peer states are maintained in the first, second and
      // third byte of the overall WP state.
      int readState () const     { return state()&0xFF; };
      int writeState () const    { return (state()&0xFF00)>>8; };
      int peerState () const     { return (state()&0xFF0000)>>16; };
      
      void setReadState  (int st)  { setState((state()&~0xFF)|st,True); };
      void setWriteState (int st)  { setState((state()&~0xFF00)|(st<<8),True); };
      void setPeerState  (int st)  { setState((state()&~0xFF0000)|(st<<16)); };
      
      // Helper functions for reading from socket
      int requestResync   ();   // ask remote to abort & resync
      int requestRetry    ();   // ask remote to resend last message
      int readyForHeader  ();   // start looking for header
      int readyForTrailer ();   // peraprte to receive trailer
      int readyForData    (const PacketHeader &hdr,BlockSet &bset); // prepare to receive data block
      
      void processIncoming(MessageRef &mref);   // sends off incoming message
      
      // reports write error and terminates writer thread
      void reportWriteError ();
          
      // parses the initialization message
      int  processInitMessage( const void *block,size_t blocksize );
    
      // Helper functions for writing to socket
      void transmitMessage (MessageRef &mref);
      
      // remote info
      AtomicID rhost,rprocess;
      
      // max size of xmitted block. Anything bigger than that will cause
      // an error (should be in shared memory!)
      static const int MaxBlockSize = 512*1024*1024;
      
      // this is is the status monitor
      typedef struct {
        Thread::Mutex stat_mutex;
        int counter;
        double ts;
        unsigned long long read,written; 
        Timestamp last_read,last_write;
        Thread::Mutex read_mutex,write_mutex;
      } StatMon;
      StatMon statmon;
      
      bool mtStart     (Thread::ThrID);
      void stopWorkers ();
      //## end MTGatewayWP%3C90BEF001E5.protected
  private:
    //## Constructors (generated)
      MTGatewayWP();

      MTGatewayWP(const MTGatewayWP &right);

    //## Assignment Operation (generated)
      MTGatewayWP & operator=(const MTGatewayWP &right);

    // Additional Private Declarations
      //## begin MTGatewayWP%3C90BEF001E5.private preserve=yes
      // list of peers
      DataRecord *peerlist;

      // separate reader threads are run
      static void * start_readerThread (void *pwp);
      void * readerThread ();
      
      static const int NumWriterThreads = 2, NumReaderThreads = 2;
      Thread::ThrID reader_threads[NumReaderThreads];
      
      // mutex for global gateway states
      Thread::Mutex gwmutex;
      
      // write state
      Thread::Mutex writer_mutex;
      bool writing;
      Timestamp write_timestamp;
      int write_seq;
      PacketHeader wr_header;
      
      // queue for reader thread(s)
      // we have a pool (at least two) reader threads. Only one
      // may be reading something, hence the reader_mutex
      Thread::Mutex reader_mutex;
      DataState readstate;
      char *read_buf;
      int nread,read_buf_size;
      int read_checksum;
      // incoming packet header & trailer
      PacketHeader header;
      DataTrailer  trailer;
      
      // this is the initialization message, prepared in start()
      MessageRef initmsg;
      bool initmsg_sent;
      
      bool shutdown_done;
      
      static const char * PacketSignature;
      
      //## end MTGatewayWP%3C90BEF001E5.private
  private: //## implementation
    // Data Members for Associations

      //## Association: OCTOPUSSY::<unnamed>%3C9225740182
      //## Role: MTGatewayWP::sock%3C9225740345
      //## begin MTGatewayWP::sock%3C9225740345.role preserve=no  private: Socket { -> 0..1RHgN}
      Socket *sock;
      //## end MTGatewayWP::sock%3C9225740345.role

      //## Association: OCTOPUSSY::<unnamed>%3C9B06A30088
      //## Role: MTGatewayWP::remote_subs%3C9B06A303D1
      //## begin MTGatewayWP::remote_subs%3C9B06A303D1.role preserve=no  private: Subscriptions { -> 0..*VHgN}
      map<MsgAddress,Subscriptions> remote_subs;
      //## end MTGatewayWP::remote_subs%3C9B06A303D1.role

    // Additional Implementation Declarations
      //## begin MTGatewayWP%3C90BEF001E5.implementation preserve=yes
      Thread::Mutex remote_subs_mutex;
      typedef map<MsgAddress,Subscriptions>::iterator RSI;
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

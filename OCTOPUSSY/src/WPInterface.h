//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C8F268F00DE.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C8F268F00DE.cm

//## begin module%3C8F268F00DE.cp preserve=no
//## end module%3C8F268F00DE.cp

//## Module: WPInterface%3C8F268F00DE; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\WPInterface.h

#ifndef WPInterface_h
#define WPInterface_h 1

//## begin module%3C8F268F00DE.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C8F268F00DE.additionalIncludes

//## begin module%3C8F268F00DE.includes preserve=yes
#include <list>
#include <set>
#include <queue>
#include "OctopussyConfig.h"
#include "Common/Config.h"
#include "Common/Thread.h"
#include "Common/Thread/Condition.h"
//## end module%3C8F268F00DE.includes

// CountedRefTarget
#include "DMI/CountedRefTarget.h"
// Subscriptions
#include "OCTOPUSSY/Subscriptions.h"
// OctopussyDebugContext
#include "OCTOPUSSY/OctopussyDebugContext.h"
// Message
#include "OCTOPUSSY/Message.h"

class Dispatcher;

//## begin module%3C8F268F00DE.declarations preserve=no
//## end module%3C8F268F00DE.declarations

//## begin module%3C8F268F00DE.additionalDeclarations preserve=yes
// standard event messages
#pragma aid WP Event Timeout Input Signal Subscribe
// hello/bye/state messages for WPs
#pragma aid Hello Bye State

// some service messages
const HIID 
  MsgHello(AidWP|AidHello),
  MsgBye(AidWP|AidBye),
  MsgWPState(AidWP|AidState),
  MsgSubscribe(AidWP|AidSubscribe);

//## end module%3C8F268F00DE.additionalDeclarations


//## begin WPInterface%3C7B6A3702E5.preface preserve=yes
//## end WPInterface%3C7B6A3702E5.preface

//## Class: WPInterface%3C7B6A3702E5; Abstract
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C7E133B016D;Message { -> }

class WPInterface : public OctopussyDebugContext, //## Inherits: <unnamed>%3C7FA31F00CE
                    	public SingularRefTarget  //## Inherits: <unnamed>%3C8CDD980366
{
  //## begin WPInterface%3C7B6A3702E5.initialDeclarations preserve=yes
  public:
      // each WP has its own local debug context (subcontext of Octopussy)
      
      Debug::Context DebugContext; 
      ::Debug::Context & getDebugContext() { return DebugContext; };
      const ::Debug::Context & getDebugContext() const { return DebugContext; };
      
      class QueueEntry 
      {
        public:
          MessageRef mref; 
          int priority; 
          ulong tick; 
#ifdef ENABLE_LATENCY_STATS
          Timestamp ts;  // timestamp of when message was enqueued (auto-initialized to ::now)
#ifdef USE_THREADS
          Thread::ThrID thrid; // enqueuing thread
#endif
#endif
          
          QueueEntry()
              : priority(0),tick(0)
#if defined(ENABLE_LATENCY_STATS) && defined(USE_THREADS)
              ,thrid(Thread::self())
#endif
              {}
          QueueEntry(const MessageRef &mref_,int pri,ulong tick_)
              : mref(mref_),priority(pri),tick(tick_)
#if defined(ENABLE_LATENCY_STATS) && defined(USE_THREADS)
              ,thrid(Thread::self())
#endif
              {}
      };
                     
      typedef list<QueueEntry> MessageQueue;
  //## end WPInterface%3C7B6A3702E5.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: WPInterface%3C7CBB10027A
      WPInterface (AtomicID wpc);

    //## Destructor (generated)
      virtual ~WPInterface();


    //## Other Operations (specified)
      //## Operation: wpname%3C83541601B4
      string wpname () const;

      //## Operation: wpid%3C9062180079
      const WPID & wpid () const;

      //## Operation: setAddress%3C98C3600396
      void setAddress (const MsgAddress &addr);

      //## Operation: attach%3C7CBAED007B
      void attach (Dispatcher* pdsp);

      //## Operation: isAttached%3C7CBBD101E1
      bool isAttached () const;

      //## Operation: do_init%3C99B0070017
      void do_init ();

      //## Operation: do_start%3C99B00B00D1
      bool do_start ();

      //## Operation: do_stop%3C99B00F0254
      void do_stop ();

      //## Operation: getPollPriority%3CB55EEA032F
      //	Rreturns a polling priority for this WP. Normally, this is just the
      //	priority of the top message in the queue (plus the queue age), or <0
      //	for no poll required. However, subclasses may choose to redefine
      //	this if they employ a some custom polling scheme.
      //	This method is called once per WP per polling loop.
      virtual int getPollPriority (ulong tick);

      //## Operation: do_poll%3C8F13B903E4
      bool do_poll (ulong tick);

      //## Operation: enqueue%3C8F204A01EF
      //	Places ref into the receive queue. Note that the ref is transferred.
      //  If placing at head and setrepoll is True, sets the repoll flag.
      //  Returns value of repoll flag
      bool enqueue (const MessageRef &msg,ulong tick,bool setrepoll=True);

      //## Operation: dequeue%3C8F204D0370
      //	Removes from queue messages matching the id. Returns True if WP
      //	needs to be repolled.
      //	If ref is non-0, then removes the first matching message, and
      //	attaches ref to it. If ref is 0, removes all matching messages.
      bool dequeue (const HIID &id, MessageRef *ref = 0);

      //## Operation: dequeue%3C8F205103D0
      //	Dequeues the message at the given position.  If ref is non-0, then
      //	attaches ref to the message. Returns True if WP needs to be repolled.
      bool dequeue (int pos, MessageRef *ref = 0);

      //## Operation: searchQueue%3C8F205601EC
      //	Finds first message in queue, starting at pos (0=top),  with
      //	matching id. Returns position of message, or -1 if not found. If ref
      //	is specified, then attaches it to the message.
      int searchQueue (const HIID &id, int pos = 0, MessageRef *ref = 0);

      //## Operation: topOfQueue%3C8F206C0071
//      const WPInterface::QueueEntry * topOfQueue () const;

      //## Operation: queueLocked%3C8F207902AB
      bool queueLocked () const;

      //## Operation: willForward%3C9079A00325
      //	Returns True if this WP will forward this non-local message.
      virtual bool willForward (const Message &) const;

      //## Operation: subscribe%3C7CB9B70120
      bool subscribe (const HIID &id, int scope = Message::GLOBAL);

      //## Operation: subscribe%3C99AB6E0187
      bool subscribe (const HIID &id, const MsgAddress &scope);

      //## Operation: unsubscribe%3C7CB9C50365
      bool unsubscribe (const HIID &id);

      //## Operation: send%3C7CB9E802CF
      //	Sends message to specified address. Note that the ref is taken over
      //	by this call, then privatized for writing. See Dispatcher::send()
      //	for more details.
      int send (MessageRef msg, MsgAddress to);

      //## Operation: send%3CBDAD020297
      int send (const HIID &id, MsgAddress to, int priority = Message::PRI_NORMAL);

      //## Operation: publish%3C7CB9EB01CF
      //	Publishes message with the specified scope. Note that the ref is
      //	taken over by this call, then privatized for writing. This method is
      //	just a shorthand for send(), with "Publish" in some parts of the
      //	address, as determined by scope).
      int publish (MessageRef msg, int scope = Message::GLOBAL);

      //## Operation: publish%3CBDACCC028F
      int publish (const HIID &id, int scope = Message::GLOBAL, int priority = Message::PRI_NORMAL);

      //## Operation: setState%3CBED9EF0197
      void setState (int newstate, bool delay_publish = False);

      //## Operation: log%3CA0457F01BD
      void log (string str, int level = 0, AtomicID type = LogNormal);

      //## Operation: lprintf%3CA0738D007F
      void lprintf (int level, int type, const char *format, ... );

      //## Operation: lprintf%3CA0739F0247
      void lprintf (int level, const char *format, ... );

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: address%3C7CBA880058
      const MsgAddress& address () const;

      //## Attribute: needRepoll%3C8F18B40315
      bool needRepoll () const;
      bool setNeedRepoll (bool value);

      //## Attribute: state%3C8F256E024B
      int state () const;

      //## Attribute: running%3CE0C01601F8
      bool isRunning () const;

      //## Attribute: logLevel%3CA07E5F00D8
      static int logLevel ();
      static void setLogLevel (int value);

    //## Get and Set Operations for Associations (generated)

      //## Association: OCTOPUSSY::<unnamed>%3C7E14150352
      //## Role: WPInterface::dsp%3C7E1416017C
      Dispatcher * dsp () const;

      //## Association: OCTOPUSSY::<unnamed>%3C999CBF01D6
      //## Role: WPInterface::subscriptions%3C999CC00015
      const Subscriptions& getSubscriptions () const;

    // Additional Public Declarations
      //## begin WPInterface%3C7B6A3702E5.public preserve=yes
      bool isLocal (const MsgAddress &addr)
      { return addr.peerid() == address().peerid(); };
      bool isLocal (const Message &msg)
      { return isLocal(msg.from()); }
      bool isLocal (const MessageRef &mref)
      { return isLocal(mref->from()); }
      
      // returns True if head of queue is the same as pmsg
      bool compareHeadOfQueue( const Message *pmsg );
      
#ifdef USE_THREADS
      bool isThreaded () const;
      Thread::Condition & queueCondition ();
      
      int numWorkers() const;
      Thread::ThrID workerID (int n) const;
#endif
      
      Declare_sdebug(virtual);
      Declare_debug( );
      //## end WPInterface%3C7B6A3702E5.public
  protected:
      //## Operation: init%3C7F882B00E6
      virtual void init ();

      //## Operation: start%3C7E4A99016B
      virtual bool start ();

      //## Operation: stop%3C7E4A9C0133
      virtual void stop ();

      //## Operation: poll%3CB55D0E01C2
      virtual bool poll (ulong );
      
      //## Operation: receive%3C7CC0950089
      virtual int receive (MessageRef &mref);

      //## Operation: timeout%3C7CC2AB02AD
      virtual int timeout (const HIID &id);

      //## Operation: input%3C7CC2C40386
      virtual int input (int fd, int flags);

      //## Operation: signal%3C7DFD240203
      virtual int signal (int signum);
      
    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: autoCatch%3CBED3720012
      //	If set, then all exceptions inside the WP's callbacks will be caught
      //	and ignored.
      bool autoCatch () const;
      void setAutoCatch (bool value);

    //## Get and Set Operations for Associations (generated)

      //## Association: OCTOPUSSY::<unnamed>%3CA1A1AB0346
      //## Role: WPInterface::queue%3CA1A1AC01AD
      const WPInterface::MessageQueue& queue () const;

    // Additional Protected Declarations
      //## begin WPInterface%3C7B6A3702E5.protected preserve=yes
      Subscriptions& getSubscriptions ();
      
      WPInterface::MessageQueue & queue ();
      
      // condition variable & mutex for message queue
      Thread::Condition queue_cond;
      
#ifdef USE_THREADS
      // This creates a new worker thread for the WP
      Thread::ThrID createWorker ();
      // this wakes up one or all worker threads by signalling or broadcasting
      // on the condition variable
      int wakeWorker (bool everyone=False);
      // this forces a repoll (sets the repoll flag), and wakes up a worker
      // (or alll workers)
      int repollWorker (bool everyone=False);
      
      // this is for the multithreaded version of poll. This takes one message
      // from the queue and delivers it to timeout/input/signal/receive.
      // The lock argument must be a valid lock on the queue_cond mutex.
      int deliver (Thread::Mutex::Lock &lock);
      
      // this is called my the default implementation of worker
      // whenever the WP is woken up on a queue event.
      // Default version simply delivers all messages from the queue.
      // The lock argument is a valid lock on the queue_cond mutex,
      // it may be released inside wakeup, but must be reacquired
      // before returning control.
      // Return True if OK, or False to terminate the thread
      virtual bool mtWakeup (Thread::Mutex::Lock &lock);
      // This is called to initialize a worker thread. Return False to 
      // terminate thread. Worker threads are initialized sequentially, and
      // startup will not complete until all workers have completed the 
      // initialization.
      virtual bool mtInit (Thread::ThrID) { return True; };
      // This is called for every worker thread once all threads have been
      // started. Return False to terminate thread.
      virtual bool mtStart (Thread::ThrID) { return True; };
      // This is called by the default runWorker() before exiting a worker thread.
      virtual void mtStop (Thread::ThrID) {};
      // this is called in a multithreaded WP's stop sequence, before
      // re-joining all the worker threads and calling stop()
      virtual void stopWorkers () {};
      
      
#endif
      
      // publishes a message containing all current subscriptions
      void publishSubscriptions ();
      
      bool full_lock,receive_lock;
      
      
      const OctopussyConfig & config;
      
      //## end WPInterface%3C7B6A3702E5.protected
  private:
    //## Constructors (generated)
      WPInterface();

      WPInterface(const WPInterface &right);

    //## Assignment Operation (generated)
      WPInterface & operator=(const WPInterface &right);

    // Additional Private Declarations
      //## begin WPInterface%3C7B6A3702E5.private preserve=yes
      // enqueues message _in front_ of all messages with lesser or equal priority
      // This is used for the HOLD result code (i.e. to leave message at head of
      // queue, unless something with higher priority has arrived while we were
      // processing it)
      bool enqueueFront (const MessageRef &msg,ulong tick,bool setrepoll=True);
      
#ifdef USE_THREADS      
      // This is the entrypoint for every worker thread.
      // Runs a simple loop, waiting on the queue condition variable, and 
      // exiting when stop_workerThreads is raised.
      void runWorker ();
      
      // this is an mt-workprocess's worker thread
      void * workerThread ();
      static void * start_workerThread (void *pwp);
      
      // a number of worker threads may be run
      static const int MaxWorkerThreads=16;
      Thread::ThrID worker_threads[MaxWorkerThreads];
      int num_worker_threads,num_initialized_workers;
      // condition variables used to manage worker init & WP startup
      Thread::Condition worker_cond,startup_cond;
#ifdef ENABLE_LATENCY_STATS
      // these two functions are called when a worker thread enters or exits
      // a queue-wait state
      void addWaiter    ();
      void removeWaiter ();
      void reportWaiters ();
      // this keeps track of how many workers are waiting on the queue
      int num_waiting_workers;
      struct { 
        struct { Timestamp start,total; } none,some,multi,all;
        Timestamp last_report;
      } tsw;
#else
      // when compiled w/o latency stats, the two functions map to nothing
      void addWaiter ()     {}
      void removeWaiter ()  {}
#endif
      
#endif

#ifdef ENABLE_LATENCY_STATS    
      // timings for latency stats (i.e., time interval between enqueue
      // and deliver), for single-threaded and multithreaded cases
      Timestamp tot_qlat,tot_qlat_mt;
      int nlat,nlat_mt;
      double last_lat_report;
#endif
      
      //## end WPInterface%3C7B6A3702E5.private

  private: //## implementation
    // Data Members for Class Attributes

      //## begin WPInterface::address%3C7CBA880058.attr preserve=no  public: MsgAddress {U} 
      MsgAddress address_;
      //## end WPInterface::address%3C7CBA880058.attr

      //## begin WPInterface::needRepoll%3C8F18B40315.attr preserve=no  public: bool {U} 
      bool needRepoll_;
      //## end WPInterface::needRepoll%3C8F18B40315.attr

      //## begin WPInterface::state%3C8F256E024B.attr preserve=no  public: int {U} 
      int state_;
      //## end WPInterface::state%3C8F256E024B.attr

      //## begin WPInterface::running%3CE0C01601F8.attr preserve=no  public: bool {U} 
      bool running;
      //## end WPInterface::running%3CE0C01601F8.attr

      //## begin WPInterface::autoCatch%3CBED3720012.attr preserve=no  protected: bool {U} 
      bool autoCatch_;
      //## end WPInterface::autoCatch%3CBED3720012.attr

      //## begin WPInterface::logLevel%3CA07E5F00D8.attr preserve=no  public: static int {U} 2
      static int logLevel_;
      //## end WPInterface::logLevel%3CA07E5F00D8.attr

    // Data Members for Associations

      //## Association: OCTOPUSSY::<unnamed>%3C7E14150352
      //## begin WPInterface::dsp%3C7E1416017C.role preserve=no  public: Dispatcher {0..* -> 1RFHN}
      Dispatcher *dsp_;
      //## end WPInterface::dsp%3C7E1416017C.role

      //## Association: OCTOPUSSY::<unnamed>%3C999CBF01D6
      //## begin WPInterface::subscriptions%3C999CC00015.role preserve=no  public: Subscriptions { -> 1VHgN}
      Subscriptions subscriptions;
      //## end WPInterface::subscriptions%3C999CC00015.role

      //## Association: OCTOPUSSY::<unnamed>%3CA1A1AB0346
      //## begin WPInterface::queue%3CA1A1AC01AD.role preserve=no  protected: MessageRef { -> 0..*VHgN}
      WPInterface::MessageQueue queue_;
      //## end WPInterface::queue%3CA1A1AC01AD.role

    // Additional Implementation Declarations
      //## begin WPInterface%3C7B6A3702E5.implementation preserve=yes
      bool raiseNeedRepoll (bool value)
      { return needRepoll_ |= value; }
      
      bool started;
      
      WPID wpid_;
      
      typedef MessageQueue::iterator MQI;
      typedef MessageQueue::const_iterator CMQI;
      typedef MessageQueue::reverse_iterator MQRI;
      typedef MessageQueue::const_reverse_iterator CMQRI;
      
      //## end WPInterface%3C7B6A3702E5.implementation
};

//## begin WPInterface%3C7B6A3702E5.postscript preserve=yes
typedef CountedRef<WPInterface> WPRef;
//## end WPInterface%3C7B6A3702E5.postscript

// Class WPInterface 


//## Other Operations (inline)
inline string WPInterface::wpname () const
{
  //## begin WPInterface::wpname%3C83541601B4.body preserve=yes
  return address_.wpclass().toString();
  //## end WPInterface::wpname%3C83541601B4.body
}

inline const WPID & WPInterface::wpid () const
{
  //## begin WPInterface::wpid%3C9062180079.body preserve=yes
  return wpid_;
  //## end WPInterface::wpid%3C9062180079.body
}

inline void WPInterface::setAddress (const MsgAddress &addr)
{
  //## begin WPInterface::setAddress%3C98C3600396.body preserve=yes
  address_ = addr;
  wpid_ = WPID(addr.wpclass(),addr.inst());
  //## end WPInterface::setAddress%3C98C3600396.body
}

inline bool WPInterface::isAttached () const
{
  //## begin WPInterface::isAttached%3C7CBBD101E1.body preserve=yes
  return dsp() != 0;
  //## end WPInterface::isAttached%3C7CBBD101E1.body
}

inline bool WPInterface::willForward (const Message &) const
{
  //## begin WPInterface::willForward%3C9079A00325.body preserve=yes
  return False;
  //## end WPInterface::willForward%3C9079A00325.body
}

inline bool WPInterface::subscribe (const HIID &id, int scope)
{
  //## begin WPInterface::subscribe%3C7CB9B70120.body preserve=yes
  return subscribe(
           id,MsgAddress(
                AidAny,AidAny,
                scope <= Message::PROCESS ? address().process() : AidAny,
                scope <= Message::HOST    ? address().host() : AidAny 
              ) 
         );
  //## end WPInterface::subscribe%3C7CB9B70120.body
}

//## Get and Set Operations for Class Attributes (inline)

inline const MsgAddress& WPInterface::address () const
{
  //## begin WPInterface::address%3C7CBA880058.get preserve=no
  return address_;
  //## end WPInterface::address%3C7CBA880058.get
}

inline bool WPInterface::needRepoll () const
{
  //## begin WPInterface::needRepoll%3C8F18B40315.get preserve=no
  return needRepoll_;
  //## end WPInterface::needRepoll%3C8F18B40315.get
}

inline bool WPInterface::setNeedRepoll (bool value)
{
  //## begin WPInterface::setNeedRepoll%3C8F18B40315.set preserve=no
  needRepoll_ = value;
  return value;
  //## end WPInterface::setNeedRepoll%3C8F18B40315.set
}

inline int WPInterface::state () const
{
  //## begin WPInterface::state%3C8F256E024B.get preserve=no
  return state_;
  //## end WPInterface::state%3C8F256E024B.get
}

inline bool WPInterface::isRunning () const
{
  //## begin WPInterface::isRunning%3CE0C01601F8.get preserve=no
  return running;
  //## end WPInterface::isRunning%3CE0C01601F8.get
}

inline bool WPInterface::autoCatch () const
{
  //## begin WPInterface::autoCatch%3CBED3720012.get preserve=no
  return autoCatch_;
  //## end WPInterface::autoCatch%3CBED3720012.get
}

inline void WPInterface::setAutoCatch (bool value)
{
  //## begin WPInterface::setAutoCatch%3CBED3720012.set preserve=no
  autoCatch_ = value;
  //## end WPInterface::setAutoCatch%3CBED3720012.set
}

inline int WPInterface::logLevel ()
{
  //## begin WPInterface::logLevel%3CA07E5F00D8.get preserve=no
  return logLevel_;
  //## end WPInterface::logLevel%3CA07E5F00D8.get
}

inline void WPInterface::setLogLevel (int value)
{
  //## begin WPInterface::setLogLevel%3CA07E5F00D8.set preserve=no
  logLevel_ = value;
  //## end WPInterface::setLogLevel%3CA07E5F00D8.set
}

//## Get and Set Operations for Associations (inline)

inline Dispatcher * WPInterface::dsp () const
{
  //## begin WPInterface::dsp%3C7E1416017C.get preserve=no
  return dsp_;
  //## end WPInterface::dsp%3C7E1416017C.get
}

inline const Subscriptions& WPInterface::getSubscriptions () const
{
  //## begin WPInterface::getSubscriptions%3C999CC00015.get preserve=no
  return subscriptions;
  //## end WPInterface::getSubscriptions%3C999CC00015.get
}

inline const WPInterface::MessageQueue& WPInterface::queue () const
{
  //## begin WPInterface::queue%3CA1A1AC01AD.get preserve=no
  return queue_;
  //## end WPInterface::queue%3CA1A1AC01AD.get
}

//## begin module%3C8F268F00DE.epilog preserve=yes
inline Subscriptions& WPInterface::getSubscriptions () 
{ return subscriptions; };

inline WPInterface::MessageQueue & WPInterface::queue () 
{ return queue_; }

#ifdef USE_THREADS
inline Thread::Condition & WPInterface::queueCondition ()
{
  return queue_cond;
}

inline bool WPInterface::isThreaded () const
{ 
  return num_worker_threads > 0; 
}

inline int WPInterface::numWorkers () const
{
  return num_worker_threads; 
}

inline Thread::ThrID WPInterface::workerID (int i) const
{
  return worker_threads[i];
}


#endif
//## end module%3C8F268F00DE.epilog


#endif


#ifndef OCTOPUSSY_WPInterface_h
#define OCTOPUSSY_WPInterface_h 1

#include <Common/Thread.h>
#include <Common/Thread/Condition.h>
#include <DMI/CountedRefTarget.h>
#include <OCTOPUSSY/OctopussyConfig.h>
#include <OCTOPUSSY/Subscriptions.h>
#include <OCTOPUSSY/OctopussyDebugContext.h>
#include <OCTOPUSSY/Message.h>

#include <list>
#include <set>
#include <queue>

class Dispatcher;

// standard event messages
#pragma aid WP Event Timeout Input Signal Subscribe
// hello/bye/state messages for WPs
#pragma aid Hello Bye State Type Level

// some service messages
const HIID 
  MsgHello(AidWP|AidHello),
  MsgBye(AidWP|AidBye),
  MsgWPState(AidWP|AidState),
  MsgSubscribe(AidWP|AidSubscribe);

//##ModelId=3C7B6A3702E5

class WPInterface : public OctopussyDebugContext,
                    	public SingularRefTarget
{
  public:
      // each WP has its own local debug context (subcontext of Octopussy)
      
    //##ModelId=3E08EC000224
      Debug::Context DebugContext; 
    //##ModelId=3DB936E60219
      ::Debug::Context & getDebugContext() { return DebugContext; };
    //##ModelId=3DB936E6030A
      const ::Debug::Context & getDebugContext() const { return DebugContext; };
      
    //##ModelId=3DB93652029F
      class QueueEntry 
      {
        public:
        //##ModelId=3DB936DC005D
          MessageRef mref; 
        //##ModelId=3DB936DC0067
          int priority; 
        //##ModelId=3E08EC000211
          ulong tick; 
#ifdef ENABLE_LATENCY_STATS
        //##ModelId=3E08EC000217
          Timestamp ts;  // timestamp of when message was enqueued (auto-initialized to ::now)
#ifdef USE_THREADS
        //##ModelId=3E08EC00021C
          Thread::ThrID thrid; // enqueuing thread
#endif
#endif
          
        //##ModelId=3DB936DC00CB
          QueueEntry()
              : priority(0),tick(0)
#if defined(ENABLE_LATENCY_STATS) && defined(USE_THREADS)
              ,thrid(Thread::self())
#endif
              {}
        //##ModelId=3DB936DC00CC
          QueueEntry(const MessageRef &mref_,int pri,ulong tick_)
              : mref(mref_),priority(pri),tick(tick_)
#if defined(ENABLE_LATENCY_STATS) && defined(USE_THREADS)
              ,thrid(Thread::self())
#endif
              {}
      };
                     
    //##ModelId=3DB936520303
      typedef list<QueueEntry> MessageQueue;
      
    //##ModelId=3DB9365203CB
      typedef enum { ENQ_NOREPOLL = 1, ENQ_NOSIGNAL = 2 } EnqueueFlags;
      
    //##ModelId=3DB9365300A1
      typedef enum { FLUSH = 1, YIELD = 2 } SendFlags;
      
      friend class Dispatcher;
      
  public:
      //##ModelId=3C7CBB10027A
      WPInterface (AtomicID wpc);

    //##ModelId=3DB936E700B2
      virtual ~WPInterface();


      //##ModelId=3C83541601B4
      string wpname () const;

      //##ModelId=3C9062180079
      const WPID & wpid () const;

      //##ModelId=3C98C3600396
      void setAddress (const MsgAddress &addr);

      //##ModelId=3C7CBAED007B
      void attach (Dispatcher* pdsp);

      //##ModelId=3C7CBBD101E1
      bool isAttached () const;

      void enablePolling  ();
      void disablePolling ();
      bool pollingEnabled () const;
      
      //##ModelId=3C99B0070017
      void do_init ();

      //##ModelId=3C99B00B00D1
      bool do_start ();

      //##ModelId=3C99B00F0254
      void do_stop ();

      //##ModelId=3CB55EEA032F
      //##Documentation
      //## Rreturns a polling priority for this WP. Normally, this is just the
      //## priority of the top message in the queue (plus the queue age), or <0
      //## for no poll required. However, subclasses may choose to redefine
      //## this if they employ a some custom polling scheme.
      //## This method is called once per WP per polling loop.
      virtual int getPollPriority (ulong tick);

      //##ModelId=3C8F13B903E4
      bool do_poll (ulong tick);

      //##ModelId=3C8F204A01EF
      //##Documentation
      //## Places ref into the receive queue. Note that the ref is transferred.
      //## If placing at head and ENQ_NOREPOLL flag is not set, sets the repoll flag.
      //## With USE_THREADS, also signals on the queue condition variable, unless
      //## the ENQ_NOSIGNAL flag is set.
      //## Returns <0 if no repoll is required, else the queue priority if it is.
      int  enqueue (const MessageRef &msg,ulong tick,int flags = 0);

      //##ModelId=3C8F204D0370
      //##Documentation
      //## Removes from queue messages matching the id. Returns True if WP
      //## needs to be repolled.
      //## If ref is non-0, then removes the first matching message, and
      //## attaches ref to it. If ref is 0, removes all matching messages.
      bool dequeue (const HIID &id, MessageRef *ref = 0);

      //##ModelId=3C8F205103D0
      //##Documentation
      //## Dequeues the message at the given position.  If ref is non-0, then
      //## attaches ref to the message. Returns True if WP needs to be repolled.
      bool dequeue (int pos, MessageRef *ref = 0);

      //##ModelId=3C8F205601EC
      //##Documentation
      //## Finds first message in queue, starting at pos (0=top),  with
      //## matching id. Returns position of message, or -1 if not found. If ref
      //## is specified, then attaches it to the message.
      int searchQueue (const HIID &id, int pos = 0, MessageRef *ref = 0);

      //##ModelId=3C8F206C0071
      //##Documentation
      //## const WPInterface::QueueEntry * topOfQueue () const;

      //## Operation: queueLocked%3C8F207902AB
      bool queueLocked () const;

      //##ModelId=3C9079A00325
      //##Documentation
      //## Returns True if this WP will forward this non-local message.
      virtual bool willForward (const Message &) const;

      //##ModelId=3C7CB9B70120
      bool subscribe (const HIID &id, int scope = Message::GLOBAL);

      //##ModelId=3C99AB6E0187
      bool subscribe (const HIID &id, const MsgAddress &scope);

      //##ModelId=3C7CB9C50365
      bool unsubscribe (const HIID &id);

      //##ModelId=3C7CB9E802CF
      //##Documentation
      //## Sends message to specified address. Note that the ref is taken over
      //## by this call, then privatized for writing. See Dispatcher::send()
      //## for more details.
      int send (MessageRef msg, MsgAddress to, int flags = 0 );

      //##ModelId=3CBDAD020297
      int send (const HIID &id, MsgAddress to, int flags = 0, int priority = Message::PRI_NORMAL);

      //##ModelId=3C7CB9EB01CF
      //##Documentation
      //## Publishes message with the specified scope. Note that the ref is
      //## taken over by this call, then privatized for writing. This method is
      //## just a shorthand for send(), with "Publish" in some parts of the
      //## address, as determined by scope).
      int publish (MessageRef msg, int flags = 0, int scope = Message::GLOBAL);

      //##ModelId=3CBDACCC028F
      int publish (const HIID &id, int flags = 0, int scope = Message::GLOBAL, int priority = Message::PRI_NORMAL);

      //##ModelId=3CBED9EF0197
      void setState (int newstate, bool delay_publish = False);

      //##ModelId=3CA0457F01BD
      void log (string str, int level = 0, AtomicID type = AidLogNormal);

      //##ModelId=3CA0738D007F
      void lprintf (int level, int type, const char *format, ... );

      //##ModelId=3CA0739F0247
      void lprintf (int level, const char *format, ... );

    //##ModelId=3DB936EC0016
      const MsgAddress& address () const;

    //##ModelId=3DB936EC01C5
      bool needRepoll () const;
    //##ModelId=3DB936EC0391
      bool setNeedRepoll (bool value);

    //##ModelId=3DB936ED0311
      int state () const;

    //##ModelId=3DB936EE00EB
      bool isRunning () const;

    //##ModelId=3DB936F00120
      Dispatcher * dsp () const;

    //##ModelId=3DB936F00301
      const Subscriptions& getSubscriptions () const;

    // Additional Public Declarations
    //##ModelId=3DB936F10104
      bool isLocal (const MsgAddress &addr)
      { return addr.peerid() == address().peerid(); };
    //##ModelId=3DB936F200D3
      bool isLocal (const Message &msg)
      { return isLocal(msg.from()); }
    //##ModelId=3DB936F30167
      bool isLocal (const MessageRef &mref)
      { return isLocal(mref->from()); }
      
      // returns True if head of queue is the same as pmsg
    //##ModelId=3DB936F40172
      bool compareHeadOfQueue( const Message *pmsg );
      
    //##ModelId=3DB936EE02C2
      static int logLevel ();
    //##ModelId=3DB936EF00B1
      static void setLogLevel (int value);

      
#ifdef USE_THREADS
    //##ModelId=3DB936F50188
      bool isThreaded () const;
    //##ModelId=3DB936F5039B
      Thread::Condition & queueCondition ();
      
    //##ModelId=3DB936F60107
      int numWorkers() const;
    //##ModelId=3DB936F6032E
      Thread::ThrID workerID (int n) const;
#endif
      
    //##ModelId=3DB936F80042
      virtual Declare_sdebug();
    //##ModelId=3DB936F803A9
      Declare_debug();
      
    //##ModelId=3DB937010095
      WPInterface::MessageQueue & queue ();
      
  protected:
      void detach ()
      { dsp_ = 0; }
      
      //##ModelId=3C7F882B00E6
      virtual void init ();

      //##ModelId=3C7E4A99016B
      virtual bool start ();

      //##ModelId=3C7E4A9C0133
      virtual void stop ();

      //##ModelId=3CB55D0E01C2
      virtual bool poll (ulong );
      
      //##ModelId=3CB55D0E01C2
      virtual void notify ();
      
      //##ModelId=3C7CC0950089
      virtual int receive (MessageRef &mref);

      //##ModelId=3C7CC2AB02AD
      virtual int timeout (const HIID &id);

      //##ModelId=3C7CC2C40386
      virtual int input (int fd, int flags);

      //##ModelId=3C7DFD240203
      virtual int signal (int signum);
      
    //##ModelId=3DB936FD007B
      bool autoCatch () const;
    //##ModelId=3DB936FE0004
      void setAutoCatch (bool value);

    //##ModelId=3DB936FF01DC
      const WPInterface::MessageQueue& queue () const;

    // Additional Protected Declarations
    //##ModelId=3DB937000170
      Subscriptions& getSubscriptions ();
      // condition variable & mutex for message queue
    //##ModelId=3E08EC00025E
      Thread::Condition queue_cond;
      
#ifdef USE_THREADS
      // This creates a new worker thread for the WP
    //##ModelId=3DB9370200EC
      Thread::ThrID createWorker ();
      // this wakes up one or all worker threads by signalling or broadcasting
      // on the condition variable
    //##ModelId=3DB9370203A9
      int wakeWorker (bool everyone=False);
      // this forces a repoll (sets the repoll flag), and wakes up a worker
      // (or alll workers)
    //##ModelId=3DB937050309
      int repollWorker (bool everyone=False);
      
      // this is for the multithreaded version of poll. This takes one message
      // from the queue and delivers it to timeout/input/signal/receive.
      // The lock argument must be a valid lock on the queue_cond mutex.
    //##ModelId=3DB937070121
      int deliver (Thread::Mutex::Lock &lock);
      
      // this is called my the default implementation of worker
      // whenever the WP is woken up on a queue event.
      // Default version simply delivers all messages from the queue.
      // The lock argument is a valid lock on the queue_cond mutex,
      // it may be released inside wakeup, but must be reacquired
      // before returning control.
      // Return True if OK, or False to terminate the thread
    //##ModelId=3DB9370803D5
      virtual bool mtWakeup (Thread::Mutex::Lock &lock);
      // This is called to initialize a worker thread. Return False to 
      // terminate thread. Worker threads are initialized sequentially, and
      // startup will not complete until all workers have completed the 
      // initialization.
    //##ModelId=3DB9370B0099
      virtual bool mtInit (Thread::ThrID) { return True; };
      // This is called for every worker thread once all threads have been
      // started. Return False to terminate thread.
    //##ModelId=3DB9370E00C4
      virtual bool mtStart (Thread::ThrID) { return True; };
      // This is called by the default runWorker() before exiting a worker thread.
    //##ModelId=3DB937100008
      virtual void mtStop (Thread::ThrID) {};
      // this is called in a multithreaded WP's stop sequence, before
      // re-joining all the worker threads and calling stop()
    //##ModelId=3DB9371200F5
      virtual void stopWorkers () {};
      
      
#endif
      
      // publishes a message containing all current subscriptions
    //##ModelId=3DB937130361
      void publishSubscriptions ();
      
    //##ModelId=3DB936DC039C
      bool full_lock,receive_lock;
      
      
    //##ModelId=3DB936DE006B
      const OctopussyConfig & config;
      
  private:
    //##ModelId=3DB93715004D
      WPInterface();

    //##ModelId=3DB9371502EC
      WPInterface(const WPInterface &right);

    //##ModelId=3DB937180016
      WPInterface & operator=(const WPInterface &right);

    // Additional Private Declarations
      // enqueues message _in front_ of all messages with lesser or equal priority
      // This is used for the HOLD result code (i.e. to leave message at head of
      // queue, unless something with higher priority has arrived while we were
      // processing it)
    //##ModelId=3DB937190389
      bool enqueueFront (const MessageRef &msg,ulong tick,bool setrepoll=True);
      
      // helper function used by enqueue() to raise a repoll condition
      void notifyOfRepoll (bool do_signal);
      
#ifdef USE_THREADS      
      // This is the entrypoint for every worker thread.
      // Runs a simple loop, waiting on the queue condition variable, and 
      // exiting when stop_workerThreads is raised.
    //##ModelId=3DB9371F00D6
      void runWorker ();
      
      // this is an mt-workprocess's worker thread
    //##ModelId=3DB937200087
      void * workerThread ();
    //##ModelId=3DB937210093
      static void * start_workerThread (void *pwp);
      
      // a number of worker threads may be run
    //##ModelId=3DB936DE013C
      static const int MaxWorkerThreads=16;
    //##ModelId=3E08EC00028B
      Thread::ThrID worker_threads[MaxWorkerThreads];
    //##ModelId=3DB936DF006B
      int num_worker_threads,num_initialized_workers;
      // condition variables used to manage worker init & WP startup
    //##ModelId=3E08EC0002B9
      Thread::Condition worker_cond,startup_cond;
#ifdef ENABLE_LATENCY_STATS
      // these two functions are called when a worker thread enters or exits
      // a queue-wait state
    //##ModelId=3DB937230313
      void addWaiter    ();
    //##ModelId=3DB937250068
      void removeWaiter ();
    //##ModelId=3DB937260023
      void reportWaiters ();
      // this keeps track of how many workers are waiting on the queue
    //##ModelId=3DB936E0038D
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
    //##ModelId=3E08EC000321
      Timestamp tot_qlat,tot_qlat_mt;
    //##ModelId=3DB936E202D2
      int nlat,nlat_mt;
    //##ModelId=3DB936E4002C
      double last_lat_report;
#endif
      

  private:
    // Data Members for Class Attributes

      //##ModelId=3DB958F70188
      MsgAddress address_;

      //##ModelId=3C8F18B40315
      bool needRepoll_;

      //##ModelId=3C8F256E024B
      int state_;

      //##ModelId=3CE0C01601F8
      bool running;

      //##ModelId=3CBED3720012
      //##Documentation
      //## If set, then all exceptions inside the WP's callbacks will be caught
      //## and ignored.
      bool autoCatch_;

      //##ModelId=3CA07E5F00D8
      static int logLevel_;

    // Data Members for Associations

      //##ModelId=3C7E1416017C
      Dispatcher *dsp_;

      //##ModelId=3C999CC00015
      Subscriptions subscriptions;

      //##ModelId=3CA1A1AC01AD
      WPInterface::MessageQueue queue_;

    // Additional Implementation Declarations
    //##ModelId=3DB937270171
      bool raiseNeedRepoll (bool value)
      { return needRepoll_ |= value; }
      
    //##ModelId=3DB936E5027C
      bool started;
      
    //##ModelId=3DB936E6012A
      WPID wpid_;
      
      bool polling_enabled;

    //##ModelId=3DB936530174
      typedef MessageQueue::iterator MQI;
    //##ModelId=3DB93653023C
      typedef MessageQueue::const_iterator CMQI;
    //##ModelId=3DB936530336
      typedef MessageQueue::reverse_iterator MQRI;
    //##ModelId=3DB936540017
      typedef MessageQueue::const_reverse_iterator CMQRI;
      
};

//##ModelId=3DB9365401C1
typedef CountedRef<WPInterface> WPRef;

// Class WPInterface 


//##ModelId=3C83541601B4
inline string WPInterface::wpname () const
{
  return address_.wpclass().toString();
}

//##ModelId=3C9062180079
inline const WPID & WPInterface::wpid () const
{
  return wpid_;
}

//##ModelId=3C98C3600396
inline void WPInterface::setAddress (const MsgAddress &addr)
{
  address_ = addr;
  wpid_ = WPID(addr.wpclass(),addr.inst());
}

//##ModelId=3C7CBBD101E1
inline bool WPInterface::isAttached () const
{
  return dsp() != 0;
}

//##ModelId=3C9079A00325
inline bool WPInterface::willForward (const Message &) const
{
  return False;
}

//##ModelId=3C7CB9B70120
inline bool WPInterface::subscribe (const HIID &id, int scope)
{
  return subscribe(
           id,MsgAddress(
                AidAny,AidAny,
                scope <= Message::PROCESS ? address().process() : AidAny,
                scope <= Message::HOST    ? address().host() : AidAny 
              ) 
         );
}

//##ModelId=3DB936EC0016
inline const MsgAddress& WPInterface::address () const
{
  return address_;
}

//##ModelId=3DB936EC01C5
inline bool WPInterface::needRepoll () const
{
  return needRepoll_;
}

//##ModelId=3DB936EC0391
inline bool WPInterface::setNeedRepoll (bool value)
{
  needRepoll_ = value;
  return value;
}

//##ModelId=3DB936ED0311
inline int WPInterface::state () const
{
  return state_;
}

//##ModelId=3DB936EE00EB
inline bool WPInterface::isRunning () const
{
  return running;
}

//##ModelId=3DB936FD007B
inline bool WPInterface::autoCatch () const
{
  return autoCatch_;
}

//##ModelId=3DB936FE0004
inline void WPInterface::setAutoCatch (bool value)
{
  autoCatch_ = value;
}

//##ModelId=3DB936EE02C2
inline int WPInterface::logLevel ()
{
  return logLevel_;
}

//##ModelId=3DB936EF00B1
inline void WPInterface::setLogLevel (int value)
{
  logLevel_ = value;
}

//##ModelId=3DB936F00120
inline Dispatcher * WPInterface::dsp () const
{
  return dsp_;
}

//##ModelId=3DB936F00301
inline const Subscriptions& WPInterface::getSubscriptions () const
{
  return subscriptions;
}

//##ModelId=3DB936FF01DC
inline const WPInterface::MessageQueue& WPInterface::queue () const
{
  return queue_;
}

//##ModelId=3DB937000170
inline Subscriptions& WPInterface::getSubscriptions () 
{ return subscriptions; };

//##ModelId=3DB937010095
inline WPInterface::MessageQueue & WPInterface::queue () 
{ return queue_; }

#ifdef USE_THREADS
//##ModelId=3DB936F5039B
inline Thread::Condition & WPInterface::queueCondition ()
{
  return queue_cond;
}

//##ModelId=3DB936F50188
inline bool WPInterface::isThreaded () const
{ 
  return num_worker_threads > 0; 
}

//##ModelId=3DB936F60107
inline int WPInterface::numWorkers () const
{
  return num_worker_threads; 
}

//##ModelId=3DB936F6032E
inline Thread::ThrID WPInterface::workerID (int i) const
{
  return worker_threads[i];
}
#endif

inline void WPInterface::enablePolling  ()
{
  polling_enabled = True;
}

inline void WPInterface::disablePolling ()
{
  polling_enabled = False;
}

inline bool WPInterface::pollingEnabled () const
{
  return polling_enabled;
}



#endif


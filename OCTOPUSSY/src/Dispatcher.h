#ifndef Dispatcher_h
#define Dispatcher_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include <signal.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <stack>
#include <map>
#include "DMI/Timestamp.h"
#include "OCTOPUSSY/OctopussyConfig.h"
#include "Common/Thread.h"
#include "Common/Thread/Condition.h"

// DataRecord
#include "DMI/DataRecord.h"
// WPInterface
#include "OCTOPUSSY/WPInterface.h"
// OctopussyDebugContext
#include "OCTOPUSSY/OctopussyDebugContext.h"
// Message
#include "OCTOPUSSY/Message.h"


#pragma aid Argv

// Event flags
const int EV_CONT = 0,      // continuous event (keeps firing until removed)
          EV_ONESHOT = 1,   // one-shot event (clears itself first time it fires)
          EV_DISCRETE = 2,  // signal: deliver discrete events for each signal
          // (default is to not generate a signal if one is already enqueued)
          EV_IGNORE   = 4,  // signal: do not deliver messages, but do 
                            // catch the signal
                            
// NB: when a WP does an addSignal with EV_IGNORE, it will not receive any 
// messages, but the signal will be caught by Dispatcher's handler, and its
// counters (if supplied to addInput)  will be incremented
                            
          // for addInput:
          EV_FDREAD       = 0x100,  // report when fd available for reading
          EV_FDWRITE      = 0x200,  // report when fd available for writing
          EV_FDEXCEPTION  = 0x400,  // report when exception on fd
          EV_FDALL        = 0x700;  // mask of all flags for inputs




//##ModelId=3C7B6A3E00A0

class Dispatcher : public OctopussyDebugContext
{
  public:
    //##ModelId=3DB958F1039C
      Debug::Context DebugContext; 
    //##ModelId=3DB936630116
      ::Debug::Context & getDebugContext() { return DebugContext; };
      
      // iterator type (for iterate(), below)
    //##ModelId=3DB9364D020D
      class WPIter
      {
        public:
        //##ModelId=3DB9365403AB
          map<WPID,WPRef>::const_iterator iter;
        //##ModelId=3DB9365403AD
          Thread::Mutex::Lock lock;
          
        //##ModelId=3DB9365403BF
          WPIter(const map<WPID,WPRef>::const_iterator &iter1,Thread::Mutex &mutex)
              : iter(iter1),lock(mutex)
          {}
          
        //##ModelId=3DB9365403CA
          void release() { lock.release(); }
      };

  public:
      //##ModelId=3C7CD444039C
      Dispatcher (AtomicID process, AtomicID host, int hz = 100);

      //##ModelId=3CD012B70209
      Dispatcher (int hz = 100);

    //##ModelId=3DB9366301DE
      ~Dispatcher();


      //##ModelId=3C8CDDFD0361
      const MsgAddress & attach (WPRef &wpref);

      //##ModelId=3C7B885A027F
      const MsgAddress & attach (WPInterface* wp, int flags);

      //##ModelId=3C8CA2BD01B0
      void detach (WPInterface* wp, bool delay = False);

      //##ModelId=3C8CDE320231
      void detach (const WPID &id, bool delay = False);

      //##ModelId=3C95C73F022A
      //##Documentation
      //## Marks a WP as a "forwarder", i.e., can deliver messages to remote
      //## hosts.
      void declareForwarder (WPInterface *wp);

      //##ModelId=3C7DFF770140
      void start ();

      //##ModelId=3C7E0270027B
      void stop ();

      //##ModelId=3C7B8867015B
      //##Documentation
      //## Sends message to specified address. The ref must be writable.
      //## Read-only copies will be placed into the appropriate queue(s).
      int send (MessageRef &mref, const MsgAddress &to);

      //##ModelId=3C7B888E01CF
      //##Documentation
      //## Polls inputs, checks timeouts, and delivers any queued messages.
      //## Does not block.
      //## This method should be called by WPs when busy with long jobs.
      void poll (int maxloops = -1);

      //##ModelId=3C8C87AF031F
      //##Documentation
      //## Goes into polling loop. Shoud be called after start() to run the
      //## system. Returns when a SIGINT is received, or after someone has
      //## called stopPolling().
      void pollLoop ();

      //##ModelId=3CE0BD3F0026
      bool yield ();

      //##ModelId=3CA09EB503C1
      void stopPolling ();

      //##ModelId=3C7D28C30061
      void addTimeout (WPInterface* pwp, const Timestamp &period, const HIID &id, int flags, int priority);

      //##ModelId=3C7D28E3032E
      void addInput (WPInterface* pwp, int fd, int flags, int priority);

      //##ModelId=3C7DFF4A0344
      void addSignal (WPInterface* pwp, int signum, int flags, int priority);

      //##ModelId=3C7D28F202F3
      bool removeTimeout (WPInterface* pwp, const HIID &id);

      //##ModelId=3C7D2947002F
      bool removeInput (WPInterface* pwp, int fd, int flags);

      //##ModelId=3C7DFF57025C
      bool removeSignal (WPInterface* pwp, int signum);

      //##ModelId=3C9B05E0027D
      int numWPs () const;

      //##ModelId=3C98D4530076
      //##Documentation
      //## Returns an iterator pointing to the first WP in the list. Use with
      //## iterate().
      Dispatcher::WPIter initWPIter ();

      //##ModelId=3C98D47B02B9
      //##Documentation
      //## Gets info for WP pointed to by iterator and  increments the
      //## iterator. Returns False when iterator becomes invalid.
      bool getWPIter (Dispatcher::WPIter &iter, WPID &wpid, const WPInterface *&pwp);

      //##ModelId=3CBEDDD8001A
      void addLocalData (const HIID &id, ObjRef ref);

      //##ModelId=3CBEE41702F4
      DataField & addLocalData (const HIID &id);

      //##ModelId=3CC405480057
      NestableContainer::Hook localData (const HIID &id);

      //##ModelId=3CC00549020D
      bool hasLocalData (const HIID &id);

    //##ModelId=3DB9366302D9
      const MsgAddress& getAddress () const;

    //##ModelId=3DB936640031
      const vector<string>& getCommandLine () const;

    //##ModelId=3DB93664019A
      ulong getTick () const;

    //##ModelId=3DB936640302
      const DataRecord& localData () const;

    // Additional Public Declarations
      // pointer to static dispatcher object
    //##ModelId=3DB936550230
      static Dispatcher * dispatcher;

#ifdef USE_THREADS
      // this starts the dispatcher running in its own thread (use instead
      // of normal start()). You can use stop() later to stop the thread.
    //##ModelId=3DB93665008D
      Thread::ThrID startThread ();
#endif
      
      
      // returns count of received signals (updated in signal handler)
    //##ModelId=3DB93665017D
      static int signalCounter (int sig);
      
      // returns set of all signals for which handlers may be set up
      // (in a multithreaded environment, all other threads should block these
      // signals)
    //##ModelId=3DB936660106
      static const sigset_t * validSignals ();
      
      // internal data structures
      // EventInfo is a base struct for all system events.
      // Contains pointer to WPI, plus a template for the event message
    //##ModelId=3DB9364D0267
      class EventInfo
      {
        public:
        //##ModelId=3DB9365403CC
        WPInterface *  pwp;
        //##ModelId=3DB9365403DE
                MessageRef msg;
                
        //##ModelId=3DB936550009
                EventInfo( WPInterface *pwpi,const HIID &id,int priority )
                           : pwp(pwpi),
                             msg( new Message(AidEvent|id,priority),
                                  DMI::ANON|DMI::WRITE ) 
                           { 
                             msg().setFrom(pwp->dsp()->getAddress());
                             msg().setTo(pwp->address());
                           };
      };
    //##ModelId=3DB9364D02AD
      class TimeoutInfo : public EventInfo
      {
        public:
        //##ModelId=3DB936550029
        Timestamp period,next;
        //##ModelId=3DB936550045
                int       flags;
        //##ModelId=3DB936550050
                HIID      id;
        //##ModelId=3DB936550064
                TimeoutInfo( WPInterface *pwp,const HIID &id,int priority )
                    : EventInfo(pwp,AidTimeout|id,priority) {};
      };
    //##ModelId=3DB9364D02F3
      class InputInfo : public EventInfo
      {
        public:
        //##ModelId=3DB93655008C
        int         fd,flags;
        //##ModelId=3DB936550098
                MessageRef  last_msg;
        //##ModelId=3DB9365500AA
                InputInfo( WPInterface *pwp,const HIID &id,int priority )
                    : EventInfo(pwp,AidInput|id,priority) {};
      };
    //##ModelId=3DB9364D0343
      class SignalInfo : public EventInfo
      {
        public:
        //##ModelId=3DB9365500B6
        int       signum,flags;
        //##ModelId=3DB9365500BF
                SignalInfo( WPInterface *pwp,const HIID &id,int priority )
                    : EventInfo(pwp,AidSignal|id,priority) {};
      };
      
      // hostId and processId
    //##ModelId=3DB93666028D
      AtomicID hostId () const        { return getAddress().host(); }
    //##ModelId=3DB936670021
      AtomicID processId () const     { return getAddress().process(); }
      
      // map of WP classes
    //##ModelId=3DB9365502C6
      map<AtomicID,int> wp_instances;
      
      // helper function: returns true if id1 is Broadcast or Publish 
    //##ModelId=3DB9366701A8
      bool wildcardAddr( AtomicID id1 )
      { return id1 == AidPublish || id1 == AidAny; }
      // helper function: returns true if id1 is wilcard or ==id2
    //##ModelId=3DB9366800EB
      bool matchAddr( AtomicID id1,AtomicID id2 )
      { return wildcardAddr(id1) || id1 == id2; }
      
    //##ModelId=3DB93669029B
      Declare_sdebug( );
    //##ModelId=3DB93669036D
      Declare_debug( );
  protected:
    // Additional Protected Declarations
      // flag: dispatcher is running
    //##ModelId=3DB936560029
      bool running;
      // flag: repoll required
    //##ModelId=3DB9365601EC
      bool repoll;
      // flag: stop the poll loop
    //##ModelId=3DB9365603B8
      static bool stop_polling;
      // flag: we are inside the pollLoop() or start() method
    //##ModelId=3DB9365701B1
      bool in_pollLoop,in_start;
      // This is the current poll depth (i.e., depth of nested polls)
      // when <0, means no poll() calls should be made.
    //##ModelId=3DB93658018A
      int poll_depth;
      
#ifdef USE_THREADS
      // ID of main dispatcher thread (poll thread)
    //##ModelId=3DB93658036C
      Thread::ThrID main_thread;
      // ID of event processing thread
    //##ModelId=3DB936590038
      Thread::ThrID event_thread;
      
      // repoll condition variable (poll thread sleeps on this)
    //##ModelId=3DB9365900E2
      Thread::Condition repoll_cond;
      
    //##ModelId=3DB9366A004E
      static void * start_eventThread (void *pdsp);
    //##ModelId=3DB9366B015E
      void * eventThread ();

    //##ModelId=3DB9366B033E
      static void * start_pollThread (void *pdsp);
    //##ModelId=3DB9366D00DC
      void * pollThread ();
#endif
        
      // set of raised signal_map/all handled signal_map
    //##ModelId=3DB9365901A0
      static sigset_t raisedSignals,allSignals;
      // original sigactions for all signal_map
    //##ModelId=3DB9365A0179
      static struct sigaction *orig_sigaction[_NSIG];
      // static signal handler
    //##ModelId=3DB9366D02BD
      static void signalHandler (int signum,siginfo_t *siginfo,void *);
      // heartbeat timer 
    //##ModelId=3DB9365A038C
      int heartbeat_hz;
      
      // timeout list
    //##ModelId=3DB9364D0389
      typedef list<TimeoutInfo> TOIL;
    //##ModelId=3DB9365B01AE
      TOIL timeouts;
    //##ModelId=3DB9364E004C
      typedef TOIL::iterator TOILI;
    //##ModelId=3DB9364E00E2
      typedef TOIL::const_iterator CTOILI;
    //##ModelId=3DB9365B0275
      Timestamp next_to;  // next pending timeout
#ifdef USE_THREADS
    //##ModelId=3DB9365B0329
      struct timeval next_timeout_tv,*pnext_timeout_tv;
#endif
      
      // inputs list
    //##ModelId=3DB9364E0178
      typedef list<InputInfo> IIL;
    //##ModelId=3DB9365C035E
      IIL inputs;
    //##ModelId=3DB9364E020E
      typedef IIL::iterator IILI;
    //##ModelId=3DB9364E02A5
      typedef IIL::const_iterator CIILI;
    //##ModelId=3DB9364E033B
      typedef struct fdsets { fd_set r,w,x; } FDSets;
    //##ModelId=3DB9365D002A
      FDSets fds_watched,fds_active;
    //##ModelId=3DB9365D01B1
      Thread::Mutex fds_watched_mutex;
    //##ModelId=3DB9365D026E
      int max_fd,num_active_fds;
    //##ModelId=3DB9365E032D
      Timestamp next_select,inputs_poll_period;
      // rebuilds watched fds according to inputs list
      // If remove is specified, all entries for the WP are removed from the
      // list (remove & rebuild).
    //##ModelId=3DB9367001CA
      void rebuildInputs ( WPInterface *remove = 0 );
      
      // signal_map map
    //##ModelId=3DB9364E03DB
      typedef multimap<int,SignalInfo> SigMap;
    //##ModelId=3DB9365F00D5
      SigMap signal_map;
    //##ModelId=3DB9364F007F
      typedef SigMap::iterator SMI;
    //##ModelId=3DB9364F0115
      typedef SigMap::const_iterator CSMI;
    //##ModelId=3DB9364F01CA
      typedef SigMap::value_type     SMPair;
      // rebuilds sigsets and sets up sigactions according to signal_map map
      // If remove is specified, all entries for the WP are removed from the
      // list (remove & rebuild)..
    //##ModelId=3DB936710244
      void rebuildSignals (WPInterface *remove = 0);
      
      // checks all signals, timeouts and inputs, sets & returns repoll flag
    //##ModelId=3DB9367202F9
      bool checkEvents ();
      
      // enqueues a message for a particular WP (this is handled differently
      // for single-threaded and multi-threaded versions, hence a separate method)
    //##ModelId=3DB936730142
      void enqueue (WPInterface *pwp,const Message::Ref &ref);
      
  private:
    //##ModelId=3DB9367500EB
      Dispatcher(const Dispatcher &right);

    //##ModelId=3DB936760197
      Dispatcher & operator=(const Dispatcher &right);


      //##ModelId=3CD014D00180
      void init ();

  private:
    // Data Members for Class Attributes

      //##ModelId=3DB958F103DB
      MsgAddress address;

      //##ModelId=3CA031080328
      vector<string> commandLine;

      //##ModelId=3DB958F20028
      ulong tick;

    // Data Members for Associations

      //##ModelId=3DB958F2005D
      map<WPID,WPRef> wps;

      //##ModelId=3DB958F200E5
      map<WPID,WPInterface*> gateways;

      //##ModelId=3CBEDD61016D
      DataRecord localData_;

    // Additional Implementation Declarations
    //##ModelId=3DB9364F0260
      typedef map<WPID,WPRef>::iterator WPI;
    //##ModelId=3DB9364F02F6
      typedef map<WPID,WPRef>::const_iterator CWPI;
    //##ModelId=3DB9364F0396
      typedef map<WPID,WPInterface*>::iterator GWI;
    //##ModelId=3DB93650004F
      typedef map<WPID,WPInterface*>::const_iterator CGWI;
      
      // WPs detached with delay=True are placed into this stack,
      // which is flushed only at a level-0 repoll 
    //##ModelId=3DB9365F0355
      stack<WPRef> detached_wps;
      // WPs attached during Dispatcher::start() temporarily go here.
      // This is done to avoid upsetting the iterators.
    //##ModelId=3DB9366001B2
      stack<WPRef> attached_wps;
      
      // configuration
    //##ModelId=3DB936610006
      const OctopussyConfig & config;
      
      // signal counters
    //##ModelId=3DB9366100D7
      static const int max_signals = 1024;
    //##ModelId=3DB936610326
      static int signal_counter[max_signals];
      
      // mutex to protect various data structures
    //##ModelId=3DB936620198
      Thread::Mutex wpmutex,tomutex,inpmutex,sigmutex;
};

// Class Dispatcher 


//##ModelId=3C9B05E0027D
inline int Dispatcher::numWPs () const
{
  return wps.size();
}

//##ModelId=3DB9366302D9
inline const MsgAddress& Dispatcher::getAddress () const
{
  return address;
}

//##ModelId=3DB936640031
inline const vector<string>& Dispatcher::getCommandLine () const
{
  return commandLine;
}

//##ModelId=3DB93664019A
inline ulong Dispatcher::getTick () const
{
  return tick;
}

//##ModelId=3DB936640302
inline const DataRecord& Dispatcher::localData () const
{
  return localData_;
}

//##ModelId=3DB93665017D
inline int Dispatcher::signalCounter (int sig)
{
  return sig < 0 || sig >= max_signals ? 0 : signal_counter[sig];
}


#endif

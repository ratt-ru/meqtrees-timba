//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7B7F300041.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7B7F300041.cm

//## begin module%3C7B7F300041.cp preserve=no
//## end module%3C7B7F300041.cp

//## Module: Dispatcher%3C7B7F300041; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\Dispatcher.h

#ifndef Dispatcher_h
#define Dispatcher_h 1

//## begin module%3C7B7F300041.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C7B7F300041.additionalIncludes

//## begin module%3C7B7F300041.includes preserve=yes
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
//## end module%3C7B7F300041.includes

// DataRecord
#include "DMI/DataRecord.h"
// WPInterface
#include "OCTOPUSSY/WPInterface.h"
// OctopussyDebugContext
#include "OCTOPUSSY/OctopussyDebugContext.h"
// Message
#include "OCTOPUSSY/Message.h"


//## begin module%3C7B7F300041.declarations preserve=no
//## end module%3C7B7F300041.declarations

//## begin module%3C7B7F300041.additionalDeclarations preserve=yes
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


//## end module%3C7B7F300041.additionalDeclarations


//## begin Dispatcher%3C7B6A3E00A0.preface preserve=yes
//## end Dispatcher%3C7B6A3E00A0.preface

//## Class: Dispatcher%3C7B6A3E00A0
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: 1..1



//## Uses: <unnamed>%3C7E128D0235;Message { -> }
//## Uses: <unnamed>%3C7E136D0350;WPInterface { -> F}

class Dispatcher : public OctopussyDebugContext  //## Inherits: <unnamed>%3C7FA32C016D
{
  //## begin Dispatcher%3C7B6A3E00A0.initialDeclarations preserve=yes
  public:
      Debug::Context DebugContext; 
      ::Debug::Context & getDebugContext() { return DebugContext; };
      
      // iterator type (for iterate(), below)
      class WPIter
      {
        public:
          map<WPID,WPRef>::const_iterator iter;
          Thread::Mutex::Lock lock;
          
          WPIter(const map<WPID,WPRef>::const_iterator &iter1,Thread::Mutex &mutex)
              : iter(iter1),lock(mutex)
          {}
          
          void release() { lock.release(); }
      };
  //## end Dispatcher%3C7B6A3E00A0.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: Dispatcher%3C7CD444039C
      Dispatcher (AtomicID process, AtomicID host, int hz = 100);

      //## Operation: Dispatcher%3CD012B70209
      Dispatcher (int hz = 100);

    //## Destructor (generated)
      ~Dispatcher();


    //## Other Operations (specified)
      //## Operation: attach%3C8CDDFD0361
      const MsgAddress & attach (WPRef &wpref);

      //## Operation: attach%3C7B885A027F
      const MsgAddress & attach (WPInterface* wp, int flags);

      //## Operation: detach%3C8CA2BD01B0
      void detach (WPInterface* wp, bool delay = False);

      //## Operation: detach%3C8CDE320231
      void detach (const WPID &id, bool delay = False);

      //## Operation: declareForwarder%3C95C73F022A
      //	Marks a WP as a "forwarder", i.e., can deliver messages to remote
      //	hosts.
      void declareForwarder (WPInterface *wp);

      //## Operation: start%3C7DFF770140
      void start ();

      //## Operation: stop%3C7E0270027B
      void stop ();

      //## Operation: send%3C7B8867015B
      //	Sends message to specified address. The ref must be writable.
      //	Read-only copies will be placed into the appropriate queue(s).
      int send (MessageRef &mref, const MsgAddress &to);

      //## Operation: poll%3C7B888E01CF
      //	Polls inputs, checks timeouts, and delivers any queued messages.
      //	Does not block.
      //	This method should be called by WPs when busy with long jobs.
      void poll (int maxloops = -1);

      //## Operation: pollLoop%3C8C87AF031F
      //	Goes into polling loop. Shoud be called after start() to run the
      //	system. Returns when a SIGINT is received, or after someone has
      //	called stopPolling().
      void pollLoop ();

      //## Operation: yield%3CE0BD3F0026
      bool yield ();

      //## Operation: stopPolling%3CA09EB503C1
      void stopPolling ();

      //## Operation: addTimeout%3C7D28C30061
      void addTimeout (WPInterface* pwp, const Timestamp &period, const HIID &id, int flags, int priority);

      //## Operation: addInput%3C7D28E3032E
      void addInput (WPInterface* pwp, int fd, int flags, int priority);

      //## Operation: addSignal%3C7DFF4A0344
      void addSignal (WPInterface* pwp, int signum, int flags, int priority);

      //## Operation: removeTimeout%3C7D28F202F3
      bool removeTimeout (WPInterface* pwp, const HIID &id);

      //## Operation: removeInput%3C7D2947002F
      bool removeInput (WPInterface* pwp, int fd, int flags);

      //## Operation: removeSignal%3C7DFF57025C
      bool removeSignal (WPInterface* pwp, int signum);

      //## Operation: numWPs%3C9B05E0027D
      int numWPs () const;

      //## Operation: initWPIter%3C98D4530076
      //	Returns an iterator pointing to the first WP in the list. Use with
      //	iterate().
      Dispatcher::WPIter initWPIter ();

      //## Operation: getWPIter%3C98D47B02B9
      //	Gets info for WP pointed to by iterator and  increments the
      //	iterator. Returns False when iterator becomes invalid.
      bool getWPIter (Dispatcher::WPIter &iter, WPID &wpid, const WPInterface *&pwp);

      //## Operation: addLocalData%3CBEDDD8001A
      void addLocalData (const HIID &id, ObjRef ref);

      //## Operation: addLocalData%3CBEE41702F4
      DataField & addLocalData (const HIID &id);

      //## Operation: localData%3CC405480057
      NestableContainer::Hook localData (const HIID &id);

      //## Operation: hasLocalData%3CC00549020D
      bool hasLocalData (const HIID &id);

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: address%3C7CD390002C
      const MsgAddress& getAddress () const;

      //## Attribute: commandLine%3CA031080328
      const vector<string>& getCommandLine () const;

      //## Attribute: tick%3CA1A2B70107
      ulong getTick () const;

    //## Get and Set Operations for Associations (generated)

      //## Association: OCTOPUSSY::<unnamed>%3CBEDD600298
      //## Role: Dispatcher::localData%3CBEDD61016D
      const DataRecord& localData () const;

    // Additional Public Declarations
      //## begin Dispatcher%3C7B6A3E00A0.public preserve=yes
      // pointer to static dispatcher object
      static Dispatcher * dispatcher;

#ifdef USE_THREADS
      // this starts the dispatcher running in its own thread (use instead
      // of normal start()). You can use stop() later to stop the thread.
      Thread::ThrID startThread ();
#endif
      
      
      // returns count of received signals (updated in signal handler)
      static int signalCounter (int sig);
      
      // returns set of all signals for which handlers may be set up
      // (in a multithreaded environment, all other threads should block these
      // signals)
      static const sigset_t * validSignals ();
      
      // internal data structures
      // EventInfo is a base struct for all system events.
      // Contains pointer to WPI, plus a template for the event message
      class EventInfo
      {
        public: WPInterface *  pwp;
                MessageRef msg;
                
                EventInfo( WPInterface *pwpi,const HIID &id,int priority )
                           : pwp(pwpi),
                             msg( new Message(AidEvent|id,priority),
                                  DMI::ANON|DMI::WRITE ) 
                           { 
                             msg().setFrom(pwp->dsp()->getAddress());
                             msg().setTo(pwp->address());
                           };
      };
      class TimeoutInfo : public EventInfo
      {
        public: Timestamp period,next;
                int       flags;
                HIID      id;
                TimeoutInfo( WPInterface *pwp,const HIID &id,int priority )
                    : EventInfo(pwp,AidTimeout|id,priority) {};
      };
      class InputInfo : public EventInfo
      {
        public: int         fd,flags;
                MessageRef  last_msg;
                InputInfo( WPInterface *pwp,const HIID &id,int priority )
                    : EventInfo(pwp,AidInput|id,priority) {};
      };
      class SignalInfo : public EventInfo
      {
        public: int       signum,flags;
                SignalInfo( WPInterface *pwp,const HIID &id,int priority )
                    : EventInfo(pwp,AidSignal|id,priority) {};
      };
      
      // hostId and processId
      AtomicID hostId () const        { return getAddress().host(); }
      AtomicID processId () const     { return getAddress().process(); }
      
      // map of WP classes
      map<AtomicID,int> wp_instances;
      
      // helper function: returns true if id1 is Broadcast or Publish 
      bool wildcardAddr( AtomicID id1 )
      { return id1 == AidPublish || id1 == AidAny; }
      // helper function: returns true if id1 is wilcard or ==id2
      bool matchAddr( AtomicID id1,AtomicID id2 )
      { return wildcardAddr(id1) || id1 == id2; }
      
      Declare_sdebug( );
      Declare_debug( );
      //## end Dispatcher%3C7B6A3E00A0.public
  protected:
    // Additional Protected Declarations
      //## begin Dispatcher%3C7B6A3E00A0.protected preserve=yes
      // flag: dispatcher is running
      bool running;
      // flag: repoll required
      bool repoll;
      // flag: stop the poll loop
      static bool stop_polling;
      // flag: we are inside the pollLoop() or start() method
      bool in_pollLoop,in_start;
      // This is the current poll depth (i.e., depth of nested polls)
      // when <0, means no poll() calls should be made.
      int poll_depth;
      
#ifdef USE_THREADS
      // ID of main dispatcher thread (poll thread)
      Thread::ThrID main_thread;
      // ID of event processing thread
      Thread::ThrID event_thread;
      
      // repoll condition variable (poll thread sleeps on this)
      Thread::Condition repoll_cond;
      
      // this the struct timeval corresponding to the next pending timeout
      struct timeval next_to_tv,
            // this either points to it, or is NULL
            *pnext_to_tv;
      
      static void * start_eventThread (void *pdsp);
      void * eventThread ();

      static void * start_pollThread (void *pdsp);
      void * pollThread ();
#endif
        
      // set of raised signal_map/all handled signal_map
      static sigset_t raisedSignals,allSignals;
      // original sigactions for all signal_map
      static struct sigaction *orig_sigaction[_NSIG];
      // static signal handler
      static void signalHandler (int signum,siginfo_t *siginfo,void *);
      // heartbeat timer 
      int heartbeat_hz;
      
      // timeout list
      typedef list<TimeoutInfo> TOIL;
      TOIL timeouts;
      typedef TOIL::iterator TOILI;
      typedef TOIL::const_iterator CTOILI;
      Timestamp next_to;  // next pending timeout
#ifdef USE_THREADS
      struct timeval next_timeout_tv,*pnext_timeout_tv;
#endif
      
      // inputs list
      typedef list<InputInfo> IIL;
      IIL inputs;
      typedef IIL::iterator IILI;
      typedef IIL::const_iterator CIILI;
      typedef struct fdsets { fd_set r,w,x; } FDSets;
      FDSets fds_watched,fds_active;
      Thread::Mutex fds_watched_mutex;
      int max_fd,num_active_fds;
      Timestamp next_select,inputs_poll_period;
      // rebuilds watched fds according to inputs list
      // If remove is specified, all entries for the WP are removed from the
      // list (remove & rebuild).
      void rebuildInputs ( WPInterface *remove = 0 );
      
      // signal_map map
      typedef multimap<int,SignalInfo> SigMap;
      SigMap signal_map;
      typedef SigMap::iterator SMI;
      typedef SigMap::const_iterator CSMI;
      typedef SigMap::value_type     SMPair;
      // rebuilds sigsets and sets up sigactions according to signal_map map
      // If remove is specified, all entries for the WP are removed from the
      // list (remove & rebuild)..
      void rebuildSignals (WPInterface *remove = 0);
      
      // checks all signals, timeouts and inputs, sets & returns repoll flag
      bool checkEvents ();
      
      // enqueues a message for a particular WP (this is handled differently
      // for single-threaded and multi-threaded versions, hence a separate method)
      void enqueue (WPInterface *pwp,const Message::Ref &ref);
      
      //## end Dispatcher%3C7B6A3E00A0.protected
  private:
    //## Constructors (generated)
      Dispatcher(const Dispatcher &right);

    //## Assignment Operation (generated)
      Dispatcher & operator=(const Dispatcher &right);


    //## Other Operations (specified)
      //## Operation: init%3CD014D00180
      void init ();

    // Additional Private Declarations
      //## begin Dispatcher%3C7B6A3E00A0.private preserve=yes
      //## end Dispatcher%3C7B6A3E00A0.private

  private: //## implementation
    // Data Members for Class Attributes

      //## begin Dispatcher::address%3C7CD390002C.attr preserve=no  public: MsgAddress {U} 
      MsgAddress address;
      //## end Dispatcher::address%3C7CD390002C.attr

      //## begin Dispatcher::commandLine%3CA031080328.attr preserve=no  public: vector<string> {U} 
      vector<string> commandLine;
      //## end Dispatcher::commandLine%3CA031080328.attr

      //## begin Dispatcher::tick%3CA1A2B70107.attr preserve=no  public: ulong {U} 
      ulong tick;
      //## end Dispatcher::tick%3CA1A2B70107.attr

    // Data Members for Associations

      //## Association: OCTOPUSSY::<unnamed>%3C7E14150352
      //## Role: Dispatcher::wps%3C7E1416010E
      //## begin Dispatcher::wps%3C7E1416010E.role preserve=no  protected: WPInterface {1 -> 0..*RHN}
      map<WPID,WPRef> wps;
      //## end Dispatcher::wps%3C7E1416010E.role

      //## Association: OCTOPUSSY::<unnamed>%3C907A5C03B2
      //## Role: Dispatcher::gateways%3C907A5D01E6
      //## begin Dispatcher::gateways%3C907A5D01E6.role preserve=no  protected: WPInterface { -> 0..*RHN}
      map<WPID,WPInterface*> gateways;
      //## end Dispatcher::gateways%3C907A5D01E6.role

      //## Association: OCTOPUSSY::<unnamed>%3CBEDD600298
      //## begin Dispatcher::localData%3CBEDD61016D.role preserve=no  public: DataRecord { -> 1VHgN}
      DataRecord localData_;
      //## end Dispatcher::localData%3CBEDD61016D.role

    // Additional Implementation Declarations
      //## begin Dispatcher%3C7B6A3E00A0.implementation preserve=yes
      typedef map<WPID,WPRef>::iterator WPI;
      typedef map<WPID,WPRef>::const_iterator CWPI;
      typedef map<WPID,WPInterface*>::iterator GWI;
      typedef map<WPID,WPInterface*>::const_iterator CGWI;
      
      // WPs detached with delay=True are placed into this stack,
      // which is flushed only at a level-0 repoll 
      stack<WPRef> detached_wps;
      // WPs attached during Dispatcher::start() temporarily go here.
      // This is done to avoid upsetting the iterators.
      stack<WPRef> attached_wps;
      
      // configuration
      const OctopussyConfig & config;
      
      // signal counters
      static const int max_signals = 1024;
      static int signal_counter[max_signals];
      
      // mutex to protect various data structures
      Thread::Mutex wpmutex,tomutex,inpmutex,sigmutex;
      //## end Dispatcher%3C7B6A3E00A0.implementation
};

//## begin Dispatcher%3C7B6A3E00A0.postscript preserve=yes
//## end Dispatcher%3C7B6A3E00A0.postscript

// Class Dispatcher 


//## Other Operations (inline)
inline int Dispatcher::numWPs () const
{
  //## begin Dispatcher::numWPs%3C9B05E0027D.body preserve=yes
  return wps.size();
  //## end Dispatcher::numWPs%3C9B05E0027D.body
}

//## Get and Set Operations for Class Attributes (inline)

inline const MsgAddress& Dispatcher::getAddress () const
{
  //## begin Dispatcher::getAddress%3C7CD390002C.get preserve=no
  return address;
  //## end Dispatcher::getAddress%3C7CD390002C.get
}

inline const vector<string>& Dispatcher::getCommandLine () const
{
  //## begin Dispatcher::getCommandLine%3CA031080328.get preserve=no
  return commandLine;
  //## end Dispatcher::getCommandLine%3CA031080328.get
}

inline ulong Dispatcher::getTick () const
{
  //## begin Dispatcher::getTick%3CA1A2B70107.get preserve=no
  return tick;
  //## end Dispatcher::getTick%3CA1A2B70107.get
}

//## Get and Set Operations for Associations (inline)

inline const DataRecord& Dispatcher::localData () const
{
  //## begin Dispatcher::localData%3CBEDD61016D.get preserve=no
  return localData_;
  //## end Dispatcher::localData%3CBEDD61016D.get
}

//## begin module%3C7B7F300041.epilog preserve=yes
inline int Dispatcher::signalCounter (int sig)
{
  return sig < 0 || sig >= max_signals ? 0 : signal_counter[sig];
}
//## end module%3C7B7F300041.epilog


#endif

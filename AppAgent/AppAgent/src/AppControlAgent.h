#ifndef APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
#define APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
    
#include <Common/Thread/Condition.h>
#include <DMI/DataRecord.h>
#include <DMI/CountedRefTraits.h>
#include <AppAgent/AppEventAgentBase.h>
#include <AppAgent/AID-AppAgent.h>
    
#include <functional>
    
class AppEventAgentBase;
class AppEventSink;
class DataRecord;

#pragma aid App Control Parameters Event Init Start Stop Pause Resume Halt
#pragma aid Always Wait Start Throw Error Notify Auto Exit Delay State String
#pragma aid Status Request Field Value ID Paused Command Update

namespace AppEvent 
{
  //##ModelId=3E8C1A5B0010
  typedef enum
  {
    // additional return codes for AppControlAgent::getCommand()
    NEWSTATE =     100,   // got state-changing command
    PAUSED   =     -100,  // got pause command
    RESUMED  =     -101,  // got resume command

  } AppControl_EventCodes;
};
    
namespace AppControlAgentVocabulary
{
  using namespace AppEventSinkVocabulary;
  
  const HIID 
//      FControlParams   = AidControl|AidParameters,
      // init record fields
      FWaitStart       = AidWait|AidStart,
      FDelayInit       = AidDelay|AidInit,
      FAutoExit        = AidAuto|AidExit,
      
      // state & status request/reply fields
      FRequestId       = AidRequest|AidID,  
      FState           = AidState,
      FPaused          = AidPaused,
      FStateString     = AidState|AidString,
      FField           = AidField,
      FValue           = AidValue,
      
      // standard prefix for app control events
      ControlPrefix    = AidApp|AidControl,
      
      ControlEventMask = ControlPrefix|AidWildcard,
      
      // events controlling state
      InitEvent        = ControlPrefix|AidInit,
      StartEvent       = ControlPrefix|AidStart,
      StopEvent        = ControlPrefix|AidStop,
      PauseEvent       = ControlPrefix|AidPause,
      ResumeEvent      = ControlPrefix|AidResume,
      HaltEvent        = ControlPrefix|AidHalt,
      
      // state & status request events
      StateRequest     = ControlPrefix|AidRequest|AidState,
      StatusRequest    = ControlPrefix|AidRequest|AidStatus,

      // notifications posted by the control agent
      StateNotifyEvent  = AidApp|AidNotify|AidState,          // new state
      StatusNotifyEvent = AidApp|AidStatus,                   // full status record
      StatusUpdateEvent = AidApp|AidUpdate|AidStatus,         // update in status
      InitNotifyEvent   = AidApp|AidNotify|AidInit,           // initialized
      StopNotifyEvent   = AidApp|AidNotify|AidStop,           // stopped
      
      CommandErrorNotifyEvent = AidApp|AidNotify|AidCommand|AidError;
};

    
//##ModelId=3DFF2FC1009C
class AppControlAgent : public AppEventAgentBase
{
  public:
//     class NotifiedHook : public NestableContainer::Hook
//     {
//       friend AppControlAgent;
//       
//       protected:
//           NotifiedHook (NestableContainer &parent,const HIID &id,AppControlAgent *invoker);
//           ~NotifiedHook ();
//       
//       private:
//           NotifiedHook ();
//           NotifiedHook (const NotifiedHook &);
//           void operator = (const NotifiedHook &);
//           
//           HIID id;
//           AppControlAgent *agent;
//     };
//       
      
    //##ModelId=3E40EDC3036F
    explicit AppControlAgent (const HIID &initf = AidControl);
    //##ModelId=3E394E4F02D2
    AppControlAgent(AppEventSink & sink, const HIID & initf = AidControl);
    //##ModelId=3E50FA3702B9
    AppControlAgent(AppEventSink *sink, int dmiflags, const HIID &initf = AidControl);
    
    //##ModelId=3E3FF3FA00C0
    //##Documentation
    //## Agent initialization method. This should be called by whoever
    //## has instantiated the agent & application. The initrec will be
    //## cached, and returned to the application once it calls start()
    virtual bool preinit (DataRecord::Ref::Xfer &initrec);
    
    //##ModelId=3E510A600340
    //##Documentation
    //## Applications call close() when they're done speaking to an agent.
    virtual void close ();
    
    //##ModelId=3E8C1A5C030E
    //##Documentation
    //## Waits for a start event if one has been configured; sets state
    //## to RUNNING and returns an init record   
    virtual int start (DataRecord::Ref &initrec);

    //##ModelId=3E8C3DDB02CA
    virtual void solicitCommand (const HIID &mask);
    
    //##ModelId=3E3957E10329
    virtual int getCommand (HIID &id,DataRecord::Ref &data,int wait = AppEvent::WAIT);
    
    //##ModelId=3E4112CC0139
    virtual int hasCommand() const;
    
    //##ModelId=3E4274C60015
    //##Documentation
    //## Posts an event on behalf of the application.
    virtual void postEvent (const HIID &id,const ObjRef::Xfer &data = ObjRef(),const HIID &dest = HIID());
    //##ModelId=3E4274C601C8
    void postEvent (const HIID &id,const DataRecord::Ref::Xfer &data,const HIID &dest = HIID());
    //##ModelId=3E4274C60230
    void postEvent (const HIID &id,const string &text,const HIID &dest = HIID());
    
    //##ModelId=3E8C209A01E7
    //##Documentation
    //## Checks whether a specific event is bound to any output. I.e., if the
    //## event would be simply discarded when posted, returns False; otherwise,
    //## returns True.
    virtual bool isEventBound (const HIID &id);

    //##ModelId=3E394E080055
    //##Documentation
    //## Changes state. If unpause=True, removes the paused flag
    virtual int setState (int newstate,bool unpase=False);
    
    //##ModelId=3EB2425300E4
    int pause ();
    
    //##ModelId=3EB24253013A
    int resume ();
    
    //##ModelId=3E40FAF50397
    virtual int setErrorState (const string& msg);
    
    //##ModelId=3E394E960305
    virtual int state() const;
    //##ModelId=3E394E9C01D7
    virtual string stateString() const;
    
    //##ModelId=3E5650EE0209
    const DataRecord & status() const;
    
    //##ModelId=3E9D78BA02FD
    //##Documentation
    //## Blocks the calling thread until the control agent enters a state
    //## for which predicate(state) == True
    template<class Pred>
    void waitUntil (Pred predicate) const;
    
    //##Documentation
    //## Same as waitUntil() above, but has a timeout in secobds.
    //## Returns True if wait was successful, or False on timeout.    
    template<class Pred>
    bool waitUntil (Pred predicate,double seconds) const;
    
    //##ModelId=3E5368C003DC
    //##Documentation
    //## Alias for waiting until state == waitstate
    void waitUntilEntersState (int waitstate) const;
    //##ModelId=3E53696202BE
    //##Documentation
    //## Alias for waiting until state == waitstate
    bool waitUntilEntersState (int waitstate, double seconds) const;
    
    //##ModelId=3E536C9E028F
    //##Documentation
    //## Alias for waiting until state != waitstate
    void waitUntilLeavesState (int waitstate) const;
    //##ModelId=3E536C9F009F
    //##Documentation
    //## Alias for waiting until state != waitstate
    bool waitUntilLeavesState (int waitstate, double seconds) const;
  
    
    //##ModelId=3E3A74D40114
    bool isPaused() const;
    
    //##ModelId=3E3AA17103E6
    Thread::Mutex & mutex () const;
    //##ModelId=3E53687B0065
    Thread::Condition & stateCondition() const;
    
    //##ModelId=3E40FEA700DF
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3E5505A90042
    LocalDebugContext;
    
    //##ModelId=3E9BD63D029D
    DefineRefTypes(AppControlAgent,Ref);
    
  protected:
    //##ModelId=3E40F90F02BA
    //##Documentation
    //## hide init method from applications. Must use preinit() and start()
    //## instead
    bool init (const DataRecord &data);
  
    //##ModelId=3E3A9E520156
    int checkStateEvent (const HIID &id,const DataRecord::Ref::Copy &data);
    
    //##ModelId=3EB24253018C
    virtual int processCommand (const HIID &id,const DataRecord::Ref &data,
                                const HIID &source);

    //##ModelId=3EB2425303B2
    void postCommandError (const string &msg,const HIID &id,
                           const DataRecord::Ref::Xfer &data,
                           const HIID &source);
    
    // posts the current state as an event
    //##ModelId=3E9BD63E00DD
    void postState  (const HIID &rqid = HIID(), const HIID &dest = HIID());
    
    // posts (sub-field) of the status record as an event
    //##ModelId=3EB24254039F
    void postStatus (const HIID &field = HIID(),const HIID &rqid = HIID(),const HIID &dest = HIID());
    
    //##ModelId=3EB2425501DA
    void postStatusUpdate (const HIID &subrec,const HIID &field,DataRecord::Ref::Xfer &rec);
    
//    //##ModelId=3E5650FE024A
//    DataRecord & statusRec();
  
  private:
    //##ModelId=3E394E1E0267
    int state_;
    //##ModelId=3E40FB0B0172
    string errmsg_;
    //##ModelId=3E3A74B70078
    bool paused_;
    //##ModelId=3E5505A9039F
    bool auto_exit_;
    //##ModelId=3E8C1A5B0227
    bool waitstart_;
    //##ModelId=3E8C1A5B03D2
    bool rethrow_;
    //##ModelId=3E5650D900AE
    DataRecord * pstatus_;
    
    //##ModelId=3E8C1A5C00A2
    DataRecord::Ref status_ref_;

    //##ModelId=3E8C1A5C0133
    DataRecord::Ref initrec_ref_;
    //##ModelId=3E8C1A5C01C5
    bool initrec_used_;
    
    //##ModelId=3E3A9E510382
    mutable Thread::Condition state_condition_;
    //##ModelId=3E4CD0B00081
    std::vector<int> input_flags_;
    //##ModelId=3E4CD1450162
    std::vector<int> input_term_states_;

    //##ModelId=3E4CCF420044
    std::vector<AppEventAgentBase::Ref> inputs;
    
    
  private: // implements different setStatus versions
    //##ModelId=3EB24256003F
    DataRecord & makeUpdateRecord (DataRecord::Ref &ref,const HIID &subrec)
    {
      ref <<= new DataRecord;
      if( subrec.empty() )
        return ref();
      else
        return ref()[subrec] <<= new DataRecord;
    }
      
        
    template<class T,class is1,class is2,class is3,class is4>
    void setStatus (const HIID &,const HIID &,T,is1,is2,is3,is4)
    {
      // this template should never ever be invoked: everything HAS to go to 
      // one of the specializations below
      STATIC_CHECK(false,Cannot_pass_this_type_to_setStatus);
    }

    template<class T,class is3,class is4>
    void setStatus (const HIID &subrec,const HIID &field,
          const T &value,
          Int2Type<false>,   // is counted ref
          Int2Type<false>,   // is ref/pointer to BO
          is3,is4            // ignored
        )
    {
      (subrec.empty() ? (*pstatus_)[field] : (*pstatus_)[subrec][field]) 
          .replace() = value;
      DataRecord::Ref ref;
      makeUpdateRecord(ref,subrec)[field] = value;
      postStatusUpdate(subrec,field,ref);
    }

    template<class T,class is3,class is4>
    void setStatus (const HIID &subrec,const HIID &field,
          const CountedRef<T> &value,
          Int2Type<true>,    // is counted ref
          Int2Type<false>,   // is ref/pointer to BO
          is3,is4            // ignored
        )
    {
      (subrec.empty() ? (*pstatus_)[field] : (*pstatus_)[subrec][field])
          .replace() = value.copy(DMI::PRESERVE_RW);
      DataRecord::Ref ref;
      makeUpdateRecord(ref,subrec)[field] = value.copy(DMI::READONLY);
      postStatusUpdate(subrec,field,ref);
    }

    template<class T,int isPointer,int isConst>
    void setStatus (const HIID &subrec,const HIID &field,
          T value,
          Int2Type<false>,      // is counted ref
          Int2Type<true>,       // is ref/pointer to BO
          Int2Type<isPointer>,  // is it a pointer
          Int2Type<isConst>     // is it const
        )
    {
      int flags = (isPointer?DMI::ANON:0) | (isConst?DMI::READONLY:DMI::WRITE);
      (subrec.empty() ? (*pstatus_)[field] : (*pstatus_)[subrec][field])
          .replace() <<= ObjRef(value,flags);
      DataRecord::Ref ref;
      makeUpdateRecord(ref,subrec)[field] <<= ObjRef(value,flags);
      postStatusUpdate(subrec,field,ref);
    }

  public:
        
    template<class T>
    inline void setStatus (const HIID &subrec,const HIID &field,const T &value)
    {
      setStatus(subrec,field,value,
          Int2Type< CountedRefTraits<T>::isCountedRef >(),
          Int2Type< SUPERSUBCLASS(BlockableObject,T) >(),
          Int2Type< false >(),
          Int2Type< true >()
          );
    }
    
    //##ModelId=3EB242560217
    inline void setStatus (const HIID &subrec,const HIID &field,const BlockableObject * value)
    {
      setStatus(subrec,field,value,
          Int2Type<false>(),
          Int2Type<true>(),
          Int2Type<true>(),
          Int2Type<true>()
          );
    }
    
    //##ModelId=3EB242590024
    inline void setStatus (const HIID &subrec,const HIID &field,BlockableObject * value)
    {
      setStatus(subrec,field,value,
          Int2Type<false>(),
          Int2Type<true>(),
          Int2Type<true>(),
          Int2Type<false>()
          );
    }
    
    template<class T>
    inline void setStatus (const HIID &field,T value )
    {
      setStatus(HIID(),field,value);
    }
};

//##ModelId=3E5650EE0209
inline const DataRecord & AppControlAgent::status () const
{
  return *pstatus_;
}

//##ModelId=3E9D78BA02FD
//inline DataRecord & AppControlAgent::wstatus ()
//{
//  return *pstatus_;
//}

// inline AppControlAgent::NotifiedHook AppControlAgent::wstatus (const HIID &field_id)
// {
//  return NotifiedHook(statusRec(),field_id,this);
// }
 
    
//##ModelId=3E3A74D40114
inline bool AppControlAgent::isPaused() const
{
  return paused_;
}

//##ModelId=3E3AA17103E6
inline Thread::Mutex & AppControlAgent::mutex () const
{
  return state_condition_;
}

//##ModelId=3E53687B0065
inline Thread::Condition & AppControlAgent::stateCondition() const
{
  return state_condition_;
}

template<class Pred>
void AppControlAgent::waitUntil (Pred predicate) const
{
  Thread::Mutex::Lock lock(state_condition_);
  while( !predicate(state_) )
    state_condition_.wait();
}

template<class Pred>
bool AppControlAgent::waitUntil (Pred predicate,double seconds) const
{
  Timestamp endtime = Timestamp::now() + Timestamp(seconds);
  Thread::Mutex::Lock lock(state_condition_);
  while( !predicate(state_) && Timestamp::now() < endtime )
    state_condition_.wait((endtime-Timestamp::now()).seconds());
  return predicate(state_);
}

#endif /* APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733 */


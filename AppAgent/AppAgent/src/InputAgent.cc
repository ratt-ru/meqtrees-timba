#include "InputAgent.h"
 
namespace AppAgent
{
      
       
// ensures singleton initialization of the VisAgent datamaps
void VisAgent::datamap_VisAgent_init ()
{
  Thread::Mutex::Lock lock;
  if( !datamap_VisAgent.isInitialized(lock) )
  {
    datamap_VisAgent
            .add(HEADER,VisEventMask(HEADER),TpDMIRecord,false)
            .add(DATA,VisEventMask(DATA),TpVisCubeVTile,true)
            .add(FOOTER,VisEventMask(FOOTER),TpDMIRecord,false);
    datamap_VisAgent.initialize();
  }
}

namespace VisAgent 
{

InitDebugContext(InputAgent,"VisAgentIn");
 
  
using namespace AppEvent;
  
static int dum = aidRegistry_AppAgent();

DataStreamMap datamap_VisAgent;

//##ModelId=3EB2434C03A0
DataStreamMap & InputAgent::datamap = datamap_VisAgent;

//##ModelId=3E41433F01DD
InputAgent::InputAgent (const HIID &initf)
  : AppEventAgentBase(initf)
{
  datamap_VisAgent_init();
}

//##ModelId=3E41433F037E
InputAgent::InputAgent (AppEventSink &sink, const HIID &initf,int flags)
  : AppEventAgentBase(sink,initf,flags)
{
  datamap_VisAgent_init();
}

//##ModelId=3E50FAB702CB
InputAgent::InputAgent (AppEventSink *sink, const HIID &initf,int flags)
  : AppEventAgentBase(sink,initf,flags)
{
  datamap_VisAgent_init();
}

//##ModelId=3E42350F01EB
bool InputAgent::init (const DMI::Record &data)
{
  suspended_ = false;
  return AppEventAgentBase::init(data);
}


//##ModelId=3EB242F5014F
int InputAgent::getNext (HIID &id,ObjRef &ref,int expect_type,int wait)
{
  int res;
  // get any object
  if( expect_type <= 0 )
  {
    // loop forever until we get a valid data event 
    HIID event;
    while( (res = sink().getEvent(event,ref,VisEventMask(),wait)) == SUCCESS )
    {
      // split into class and identifier
      int code = VisEventType(event);
      id = VisEventInstance(event);
      // find this event in the data map
      const DataStreamMap::Entry &entry = datamap.find(code);
      if( entry.code ) // found valid entry?
      {
        // no data checking for this event? Return success already
        if( entry.datatype == TpNull )
          return entry.code;
        if( ref.valid() ) // got data with event? check type 
        {
          if( ref->objectType() == entry.datatype )
            return entry.code;
          // else datatype mismatch, fall through for another event
          cdebug(2)<<"datatype mismatch in event "<<event<<", dropping\n";
        }
        else // no data with event
        {
          if( !entry.data_required ) // ... and none required, OK
            return entry.code;
          // else fall through for another go
          cdebug(2)<<"missing data in event "<<event<<", dropping\n";
        }
      }
      else
      {
        cdebug(2)<<"unmapped event: "<<event<<", dropping\n";
      }
      // loop back for another try
    }
  }
  else // get a specific kind of object
  {
    const DataStreamMap::Entry &entry = datamap.find(expect_type);
    FailWhen( !entry.code,"unmapped data category "+codeToString(expect_type) );
    while( (res = sink().getEvent(id,ref,entry.eventmask,wait)) == SUCCESS )
    {
      // no data checking for this event? Return success already
      if( entry.datatype == TpNull )
        return entry.code;
      if( ref.valid() ) // got data with event? check type 
      {
        if( ref->objectType() == entry.datatype )
          return entry.code;
        // else datatype mismatch, fall through for another event
        cdebug(2)<<"datatype mismatch in event "<<id<<", dropping\n";
      }
      else // no data with event
      {
        if( !entry.data_required ) // ... and none required, OK
          return entry.code;
        // else fall through for another go
        cdebug(2)<<"missing data in event "<<id<<", dropping\n";
      }
      // loop back for another try
    }
  }
  return res;
}

//##ModelId=3EB242F5031B
int InputAgent::hasNext () const
{
  HIID id;
  int res = sink().hasEvent(VisEventMask(),id);
  if( res != SUCCESS )
    return res;
  const DataStreamMap::Entry &entry = datamap.find(VisEventType(id));
  if( !entry.code )
    return OUTOFSEQ;
  return entry.code;
}

//##ModelId=3EB2434D0054
void InputAgent::suspend ()
{
  if( !suspended_ )
  {
    sink().postEvent(SuspendEvent);
    sink().clearEventFlag();
    suspended_ = true; 
  }
}

//##ModelId=3EB2434D008D
void InputAgent::resume ()
{
  sink().postEvent(ResumeEvent);
  sink().raiseEventFlag();
  suspended_ = false;
}

//##ModelId=3EB2434D014F
string InputAgent::sdebug (int detail, const string &prefix, const char *name) const
{
  string out = AppEventAgentBase::sdebug(detail,prefix,name?name:"VisAgent::Input");
  if( suspended_ && ( detail > 1 || detail == -1 ) )
    out += " (suspended)";
  return out;
}


} // namespace VisAgent
}

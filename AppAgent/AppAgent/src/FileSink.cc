#include "FileSink.h"
    
using namespace AppState;
using namespace AppEvent;

//##ModelId=3EB916630067
FileSink::FileSink ()
    : AppEventSink(HIID()),state_(INIT)
{
}

void FileSink::putOnStream (const HIID &id,const ObjRef::Xfer &ref)
{
  raiseEventFlag();    // we now generate events
  input_stream_.push_back(StreamEntry());
  input_stream_.back().id = id;
  input_stream_.back().ref.xfer(ref);
}

//##ModelId=3EB9169701B4
int FileSink::getEvent (HIID &id, ObjRef &data, const HIID &mask, int wait, HIID &source)
{
  int res = hasEvent(mask,id);
  if( res == AppEvent::SUCCESS )
  {
    // pop first stream entry 
    StreamEntry &entry = input_stream_.front();
    id = entry.id;
    data = entry.ref;
    input_stream_.pop_front();
  }
  else if( res == OUTOFSEQ && wait == BLOCK )
      // boo-boo, can't block here since we'd never get an event to unblock us...
    Throw("blocking for an event here would block indefinitely");
  return res;
}

//##ModelId=3EB916A5000E
int FileSink::hasEvent (const HIID &mask, HIID &out) const
{
//  // if suspended, then return a wait code
//  if( suspended() ) 
//    return waitOtherEvents(NOWAIT);
  if( input_stream_.empty() )
  {
    // cast away const here since refilling the stream may require non-const access
    // to data members. This is easier than making everything mutable
    int res = const_cast<FileSink*>(this)->refillStream();
    if( res != AppEvent::SUCCESS )
    {
      clearEventFlag();   // empty stream = no more events from us
      return res;
    }
  }
  out = input_stream_.front().id;
  if( mask.empty() || mask.matches(out) )
    return AppEvent::SUCCESS;
  else
    return AppEvent::OUTOFSEQ;
}

int FileSink::setState (int newstate)
{
  return state_ = newstate;
}
    
//##ModelId=3EC2461203CD
int FileSink::setErrorState (const string &error)
{
  error_string_ = error;
  return state_ = AppState::ERROR;
}

//##ModelId=3E2C2999029A
string FileSink::stateString() const
{
  switch( state() )
  {
    case INIT:
      return "INIT";
    case RUNNING:
      return "OK";
    case CLOSED:
      return "CLOSED";
    case AppState::ERROR:
      return "ERROR: " + error_string_;
    default:
      return AtomicID(state()>0?-state():state()).toString();
  }
}

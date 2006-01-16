#include "FileChannel.h"
#include <DMI/Exception.h>
    
namespace AppAgent
{    

using namespace AppEvent;

void FileChannel::putOnStream (const HIID &id,const ObjRef &ref,const HIID &source)
{
  raiseEventFlag();    // we now generate events
  input_stream_.push_back(StreamEntry());
  StreamEntry &se = input_stream_.back();
  se.id = id;
  se.source = source;
  se.ref = ref;
}

//##ModelId=3EB9169701B4
int FileChannel::getEvent (HIID &id,ObjRef &data,const HIID &mask,int wait,HIID &source)
{
  int res = hasEvent(mask,id);
  if( res == AppEvent::SUCCESS )
  {
    // pop first stream entry 
    const StreamEntry &se = input_stream_.front();
    id = se.id;
    data = se.ref;
    source = se.source;
    input_stream_.pop_front();
    recordInputEvent(id,data,HIID());
  }
  else if( res == OUTOFSEQ )
  {
    if( wait == BLOCK )
    {
        // boo-boo, can't block here since we'd never get an event to unblock us...
      Throw("blocking on an event here would block indefinitely");
    }
    else
      return waitOnFlag(WAIT);
  }
  else if( res == WAIT )
  {
    if( wait == WAIT )
      return waitOnFlag(WAIT);
    else if( wait == BLOCK )
    {
        // boo-boo, can't block here since we'd never get an event to unblock us...
      Throw("blocking on an event here would block indefinitely");
    }
  }
  return res;
}

//##ModelId=3EB916A5000E
int FileChannel::hasEvent (const HIID &mask, HIID &out) 
{
  if( input_stream_.empty() )
  {
      // cast away const here since refilling the stream may require non-const access
      // to data members. This is easier than making everything mutable
    int res = const_cast<FileChannel*>(this)->refillStream();
    if( res != AppEvent::SUCCESS )
      clearEventFlag();   // empty stream = no more events from us
    if( res == AppEvent::CLOSED )
      close();
    return res;
  }
  out = input_stream_.front().id;
  if( mask.empty() || mask.matches(out) )
    return AppEvent::SUCCESS;
  else
    return AppEvent::OUTOFSEQ;
}

};

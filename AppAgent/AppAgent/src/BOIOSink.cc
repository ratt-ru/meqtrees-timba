#include "BOIOSink.h"

InitDebugContext(BOIOSink,"BOIOSink");

static int dum = aidRegistry_AppAgent();
    
using namespace AppEvent;
    
//##ModelId=3E53C59D00EB
bool BOIOSink::init (const DataRecord &data)
{
  string file = data[FBOIOFile].as_string("");  
  FailWhen(!file.length(),FBOIOFile.toString()+" not specified");
  char mode = toupper( data[FBOIOMode].as_string("R")[0] );  
  if( mode == 'R' )
  {
    boio.open(file,BOIO::READ);
    cdebug(1)<<"opened file "<<file<<" for reading\n";
  }
  else if( mode == 'W' )
  {
    boio.open(file,BOIO::WRITE);
    cdebug(1)<<"opened file "<<file<<" for writing\n";
  }    
  else if( mode == 'A' )
  {
    boio.open(file,BOIO::APPEND);
    cdebug(1)<<"opened file "<<file<<" for appending\n";
  }
  else
  {
    Throw("unknown file access mode: "+mode);
  }
  cached_event = False;
  return True;
}

//##ModelId=3E53C5A401E1
void BOIOSink::close()
{
  boio.close();
}

    
//##ModelId=3E53C5B401CB
int BOIOSink::getEvent (HIID &id, ObjRef &data, const HIID &mask, int wait)
{
  int res = hasEvent(mask);
  // have a cached, matching event? Return it
  if( res == SUCCESS )
  {
    id = cached_id;
    data = cached_data;
    cached_event = False;
    return SUCCESS;
  }
  // else no matching event -- call base waitOtherEvents() to see what's up
  else if( res == OUTOFSEQ && wait == BLOCK )
      // boo-boo, can't block here since we never get an event to unblock us...
    Throw("blocking for an event here would block indefinitely");
  return res;
}

//##ModelId=3E53C5BB0014
int BOIOSink::hasEvent (const HIID &mask) const
{
  while( !cached_event )
  {
    if( boio.fileMode() != BOIO::READ )
      return CLOSED;
    ObjRef ref;
    TypeId tid = boio.read(ref);
    if( tid == 0 )
    {
      cdebug(1)<<"EOF on BOIO file, closing"<<endl;
      boio.close();
      return CLOSED;
    }
    else if( tid != TpDataRecord )
    {
      cdebug(2)<<"unexpected object ("<<tid<<") in BOIO file, ignoring"<<endl;
      // go back for another event
      continue;
    }
    // else process the DataRecord
    try
    {
      DataRecord &rec = ref.ref_cast<DataRecord>().dewr();
      cached_id    = rec[AidEvent].as_HIID();
      if( rec[AidData].exists() )
        rec[AidData].detach(&cached_data);
      else
        cached_data.detach();
      cached_event = True;
    }
    catch( std::exception &exc )
    {
      cdebug(2)<<"error getting event from BOIO: "<<exc.what()<<endl;
      // go back for another event
    }
  }
  // we now have a cached event
  return mask.matches(cached_id) ? SUCCESS : OUTOFSEQ;
}

//##ModelId=3E53C5C2003E
void BOIOSink::postEvent (const HIID &id, const ObjRef::Xfer &data)
{
  if( boio.fileMode() == BOIO::WRITE || boio.fileMode() == BOIO::APPEND )
  {
    cdebug(3)<<"storing event "<<id<<endl;
    DataRecord rec;
    rec[AidEvent] = id;
    if( data.valid() )
      rec[AidData] <<= data;
    boio << ObjRef(rec,DMI::EXTERNAL);
  }
  else
  {
    cdebug(3)<<"no file open for writing, dropping event "<<id<<endl;
  }
}

//##ModelId=3E53C5CE0339
string BOIOSink::sdebug(int detail, const string &prefix, const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"BOIOSink",(int)this);
  }
  if( detail >= 1 || detail == -1 )
  {
    append(out,boio.stateString());
  }
  
  return out;
}

#include "BOIOSink.h"

InitDebugContext(BOIOSink,"BOIOSink");

static int dum = aidRegistry_AppAgent();
    
using namespace AppEvent;
using namespace AppState;
    
//##ModelId=3E53C59D00EB
bool BOIOSink::init (const DataRecord &data)
{
  string file = data[FBOIOFile].as<string>("");  
  FailWhen(!file.length(),FBOIOFile.toString()+" not specified");
  char mode = toupper( data[FBOIOMode].as<string>("R")[0] );  
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
  setState(RUNNING);
  return True;
}

//##ModelId=3E53C5A401E1
void BOIOSink::close()
{
  setState(CLOSED);
  boio.close();
}

//##ModelId=3EC23EF30079
int BOIOSink::refillStream()
{
  if( boio.fileMode() != BOIO::READ )
    return CLOSED;
  for(;;)
  {
    ObjRef ref;
    TypeId tid = boio.readAny(ref);
    if( tid == 0 )
    {
      cdebug(1)<<"EOF on BOIO file, closing"<<endl;
      setState(CLOSED);
      boio.close();
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
      HIID id = rec[AidEvent].as<HIID>();
      ObjRef dataref;
      if( rec[AidData].exists() )
        rec[AidData].detach(&dataref);
      putOnStream(id,dataref);
      return SUCCESS;
    }
    catch( std::exception &exc )
    {
      cdebug(2)<<"error getting event from BOIO: "<<exc.what()<<endl;
      // go back for another event
    }
  }
}

//##ModelId=3E8C252801E8
bool BOIOSink::isEventBound (const HIID &)
{
  return True;
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

#define AIPSPP_HOOKS 1
    
#include <sys/time.h> 
#include <sys/types.h> 
#include <unistd.h> 
#include <aips/Glish.h>
#include <aips/Arrays/Array.h>
#include <aips/Arrays/ArrayMath.h>

#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
#include <DMI/DynamicTypeManager.h>

#include <DMI/AIPSPP-Hooks.h>

// GlishClientWP
#include "OCTOGlish/GlishClientWP.h"

// array conversion utilities
#include "OCTOGlish/BlitzToAips.h"

static int dum = aidRegistry_OCTOGlish();
//##ModelId=3CB562BB0226
//##ModelId=3DB9369503DE
//##ModelId=3DB9369600AA


// Class GlishClientWP 

GlishClientWP::GlishClientWP (GlishSysEventSource *src, bool autostp, AtomicID wpc)
  : WorkProcess(wpc),evsrc(src),autostop_(autostp)
{
  connected = evsrc->connected();
  has_events = False;
}


//##ModelId=3DB9369201C7
GlishClientWP::~GlishClientWP()
{
  if( evsrc )
    delete evsrc;
}

void GlishClientWP::init ()
{
  dprintf(2)("init: waiting for glish start event\n");
  glish_started = False;
  while( !glish_started )
  {
    GlishSysEvent event = evsrc->nextGlishEvent();
    handleEvent(event);
  }
  dprintf(2)("init complete\n");
}

void GlishClientWP::handleEvent (GlishSysEvent &event)
{
  dprintf(2)("got event '%s'\n", event.type().c_str());
  Bool result = True;       // AIPS++ Bool for event result

  if( event.type() == "shutdown" ) // shutdown event
  {
    shutdown();
  }
  else 
  {
    try // catch all event processing exceptions
    {
      // all other events must carry a GlishRecord
      FailWhen(event.valType() != GlishValue::RECORD,"event value not a record");
      // get the record out and process stuff
      GlishRecord rec = event.val();
      GlishArray tmp;
      if( event.type() == "start" )
      {
        FailWhen( glish_started,"unexpected start event" );
        glish_started = True;
      }
      else if( event.type() == "subscribe" )
      {
        FailWhen( rec.nelements() != 2,"illegal event value" );
        String idstr; int scope;
        tmp = rec.get(0); tmp.get(idstr);
        tmp = rec.get(1); tmp.get(scope);
        HIID id(idstr);
        FailWhen( !id.size(),"null HIID in subscribe" );
        subscribe(id,scope);
      }
      else if( event.type() == "unsubscribe" )
      {
        FailWhen( rec.nelements() != 1,"illegal event value" );
        String idstr; 
        tmp = rec.get(0); tmp.get(idstr);
        HIID id(idstr);
        FailWhen( !id.size(),"null HIID in unsubscribe" );
        unsubscribe(id);
      }
      else if( event.type() == "send" )
      {
        FailWhen(!glish_started,"got send event before start event");
        String tostr; 
        FailWhen(!rec.attributeExists("to"),"missing 'to' attribute");
        tmp = rec.getAttribute("to"); tmp.get(tostr);
        HIID to(tostr);
        FailWhen(!to.size(),"bad 'to' attribute");
        AtomicID wpi,process=AidLocal,host=AidLocal;
        if( to.size() > 1 )  wpi = to[1];
        if( to.size() > 2 )  process = to[2];
        if( to.size() > 3 )  host = to[3];
        MessageRef ref = glishRecToMessage(rec);
        setState(ref->state());
        dprintf(4)("sending message: %s\n",ref->sdebug(10).c_str());
        send(ref,MsgAddress(to[0],wpi,process,host));
      }
      else if( event.type() == "publish" )
      {
        FailWhen(!glish_started,"got publish event before start event");
        int scope;
        FailWhen( !rec.attributeExists("scope"),"missing 'scope' attribute");
        tmp = rec.getAttribute("scope"); tmp.get(scope);
        MessageRef ref = glishRecToMessage(rec);
        setState(ref->state());
        dprintf(4)("publishing message: %s\n",ref->sdebug(10).c_str());
        publish(ref,scope);
      }
      else if( event.type() == "log" )
      {
        FailWhen(!glish_started,"got log event before start event");
        FailWhen( rec.nelements() != 3,"illegal event value" );
        String msg,typestr; int level;
        tmp = rec.get(0); tmp.get(msg);
        tmp = rec.get(1); tmp.get(level);
        tmp = rec.get(2); tmp.get(typestr);
        AtomicID type(typestr);
        log(msg,level,type);
      }
      else
        Throw("unknown event");
    } // end try 
    catch ( std::exception &exc ) 
    {
      dprintf(1)("error processing glish event, ignoring: %s\n",exc.what());
      result = False;
    }
  }
  // if we fell through to here, return the reply
  if( evsrc->replyPending() )
    evsrc->reply(GlishArray(result));
}

//##ModelId=3CBA97E70232
bool GlishClientWP::start ()
{
  fd_set fdset;
  FD_ZERO(&fdset);
  if( evsrc->addInputMask(&fdset) )
  {
    for( int fd=0; fd<FD_SETSIZE; fd++ )
      if( FD_ISSET(fd,&fdset) )
      {
        dprintf(2)("adding input for fd %d\n",fd);
        addInput(fd,EV_FDREAD);
      }
  }
  else
  {
    dprintf(2)("no input fds indicated by GlishEventSource\n");
  }
  // add a timeout to keep checking for connectedness
  addTimeout(2.0,HIID(),EV_CONT);
  
  return False;
}

//##ModelId=3CBABEA10165
void GlishClientWP::stop ()
{
  if( evsrc && connected )
    evsrc->postEvent("exit",GlishValue());
}

//##ModelId=3CBACB920259
int GlishClientWP::input (int , int )
{
  if( !evsrc->connected() )
  {
    // got disconnected?
    if( connected )
      dprintf(1)("disconnected from Glish process\n");
    shutdown();
  }
  else
  {
    GlishSysEvent event;
    // The event loop
    // loop until the mex # of events is reached, or no more events
    for( int i=0; i < MaxEventsPerPoll; i++ )
      if( !evsrc->nextGlishEvent(event,0) )
      {
        has_events=False; // no events? reset flag and exit
        break;
      }
      else   // else process the event
      {
        handleEvent(event);
      } // end of event loop
  }
  return Message::ACCEPT;
}

//##ModelId=3CBACFC6013D
int GlishClientWP::timeout (const HIID &)
{
  // fake an input all to check for connectedness, etc.
  return input(0,0);
}

//##ModelId=3CB5622B01ED
int GlishClientWP::receive (MessageRef &mref)
{
  // if no connection, then just ignore it
  if( !evsrc->connected() )
  {
    dprintf(2)("not connected, ignoring [%s]\n",mref->sdebug(1).c_str());
    return Message::ACCEPT;
  }
  // wrap the message into a record and post it
  GlishRecord rec;
  if( messageToGlishRec(mref.deref(),rec) )
  {
    evsrc->postEvent("receive",rec);
  }
  else
  {
    dprintf(1)("unable to convert [%s] to glish record\n",mref->sdebug(1).c_str());
  }
  return Message::ACCEPT;
}

//##ModelId=3CB57C8401D6
MessageRef GlishClientWP::glishRecToMessage (const GlishRecord &glrec)
{
  // get message attributes
  FailWhen( !glrec.attributeExists("id") ||
            !glrec.attributeExists("priority"),"missing 'id' or 'priority' attribute");
  String idstr; 
  int priority,state=0;
  GlishArray tmp;
  tmp = glrec.getAttribute("id"); tmp.get(idstr);
  tmp = glrec.getAttribute("priority"); tmp.get(priority);
  if( glrec.attributeExists("state") )
  {
    tmp = glrec.getAttribute("state"); tmp.get(state);
  }
  // setup message & ref
  HIID id(idstr);
  Message &msg = *new Message(id,priority);
  MessageRef ref(msg,DMI::ANON|DMI::WRITE);
  ref().setState(state);
  // do we have a payload?
  if( glrec.attributeExists("payload") )
  {
    String typestr; 
    tmp = glrec.getAttribute("payload"); tmp.get(typestr);
    TypeId tid(typestr);
    // data record is unwrapped explicitly
    if( tid == TpDataRecord )
    {
      DataRecord *rec = new DataRecord;
      msg <<= rec;
      glishToRec(glrec,*rec);
    }
    else // else try to unblock the object
    {
      msg <<= blockRecToObject(glrec);
    }
  }
  // do we have a data block as well?
  if( glrec.attributeExists("datablock") )
  {
    Array<uChar> data;
    tmp = glrec.getAttribute("datablock"); tmp.get(data);
    size_t sz = data.nelements();
    SmartBlock *block = new SmartBlock(sz);
    msg <<= block;
    if( sz )
    {
      bool del;
      const uChar *pdata = data.getStorage(del);
      memcpy(block->data(),pdata,sz);
      data.freeStorage(pdata,del);
    }
  }
  return ref;
}

//##ModelId=3CB57CA00280
bool GlishClientWP::messageToGlishRec (const Message &msg, GlishRecord &glrec)
{
  glrec.addAttribute("id",GlishArray(msg.id().toString()));
  glrec.addAttribute("to",GlishArray(msg.id().toString()));
  glrec.addAttribute("from",GlishArray(msg.from().toString()));
  glrec.addAttribute("priority",GlishArray(msg.priority()));
  glrec.addAttribute("state",GlishArray(msg.state()));
  // convert payload
  if( msg.payload().valid() )
  {
    TypeId tid = msg.payload()->objectType();
    glrec.addAttribute("payload",GlishArray(tid.toString()));
    // records are converted
    if( tid == TpDataRecord )
    {
      const DataRecord *rec = dynamic_cast<const DataRecord *>(msg.payload().deref_p());
      Assert(rec);
      recToGlish(*rec,glrec);
    }
    else
    {
      objectToBlockRec(msg.payload().deref(),glrec);
    }
  }
  // copy data block, if any
  if( msg.block().valid() )
  {
    size_t sz = msg.datasize();
    glrec.addAttribute("datasize",GlishArray((int)sz));
    if( sz )
      glrec.addAttribute("data",GlishArray(Array<uChar>(IPosition(1,sz),
		static_cast<uChar*>(const_cast<void*>(msg.data())),COPY)));
  }
  
  return True;
}

// helper function to convert a container into a Glish array
static bool makeGlishArray (GlishArray &arr,const NestableContainer &nc,TypeId tid,bool isIndex )
{
  switch( tid.id() )
  {
    case Tpbool_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Bool>());
        break;
    case Tpuchar_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<uChar>());
        break;
    case Tpshort_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Short>());
        break;
    case Tpint_int:
    {
        Array<Int> intarr = nc[HIID()].as_AipsArray<Int>();
        if( isIndex )
          intarr += 1;
        arr = GlishArray(intarr);
        break;
    }
    case Tpfloat_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Float>());
        break;
    case Tpdouble_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Double>());
        break;
    case Tpfcomplex_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Complex>());
        break;
    case Tpdcomplex_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<DComplex>());
        break;
    case Tpstring_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<String>());
        break;
    default:
        return False; // non-supported type
  }
  return True;
}


// Additional Declarations
//##ModelId=3DB9369202CC
void GlishClientWP::recToGlish (const DataRecord &rec, GlishRecord& glrec)
{
  DataRecord::Iterator iter = rec.initFieldIter();
  HIID id;
  TypeId type;
  int size;
  while( rec.getFieldIter(iter,id,type,size) )
  {
    const DataField &field = rec[id].as_DataField();
    #ifdef USE_THREADS
    // obtain mutex on the datafield
    Thread::Mutex::Lock lock(field.mutex());
    #endif
    string name = id.toString();
    GlishRecord subrec;
    bool isIndex = ( id[id.size()-1] == AidIndex );
    
    // Mapping of DataFields:
    // (a) primitive Glish type: maps field to 1D array or scalar
    // (b) 1 DataRecord: maps field to a record
    // (c) >1 DataRecords: maps field to a record of records
    // (d) 1 DataArray, Glish type: map field to array
    // (e) 1 DataArray, non-Glish type: map field to blockset
    // (f) >1 DataArrays: map to record of arrays (or blocksets)
    // (g) otherwise, map to blockset
    
    // (b) (c): subrecords are mapped recursively 
    if( type == TpDataRecord )
    {
      if( size == 1 )  // one record mapped directly
      {
        recToGlish(field[HIID()].as_DataRecord(),subrec);
      }
      else // array of records mapped as record of records
      {
        subrec.addAttribute("field_of_records",GlishArray(size));
        for( int i=0; i<size; i++ )
        {
          GlishRecord subsubrec;
          recToGlish(field[i].as_DataRecord(),subsubrec);
          char num[32];
          sprintf(num,"%d",i);
          subrec.add(num,subsubrec);
        }
      }
      glrec.add(name,subrec);
    }
    // case (d) (e) (f)
    else if( type == TpDataArray )
    {
      // single array maps to single array or blockset,
      // array of arrays mapped as record of arrays. 
      GlishRecord subrec;
      // if size>1, then we'll add the arrays to subrec rather than the current record
      GlishRecord *prec = size>1 ? &subrec : &glrec;
      for( int i=0; i<size; i++ )
      {
        GlishArray arr;
        string subname = size == 1 ? name : Debug::ssprintf("%d",i);
        // try to map array to glish array
        const DataArray &dataarray = field[i].as_DataArray();
        if( makeGlishArray(arr,dataarray,dataarray.elementType(),isIndex) )
        {
          arr.addAttribute("is_dataarray",GlishArray(True));
          prec->add(subname,arr);
        }
        else // if failed, map to blockset
        {
          GlishRecord blockrec;
          objectToBlockRec(dataarray,blockrec);
          prec->add(subname,blockrec);
        }
      }
      if( size > 1 )
      {
        subrec.addAttribute("field_of_arrays",GlishArray(size));
        glrec.add(name,subrec);
      }
    }
    // case (a): map to array (or (g) if not a Glish type)
    else if( TypeInfo::isNumeric(type) || type == Tpstring )
    {
      GlishArray arr;
      // try to map to a Glish array
      if( makeGlishArray(arr,field,type,isIndex) )
      {
        arr.addAttribute("is_datafield",GlishArray(True));
        glrec.add(name,arr);
      }
      else // if failed, map to blockset
      {
        objectToBlockRec(field,subrec);
        glrec.add(name,subrec);
      }
    }
    else // case (g): map to block record
    {
      objectToBlockRec(field,subrec);
      glrec.add(name,subrec);
    }
  } // end of iteration over fields
}



// helper function to create a DataField from a GlishArray
template<class T> 
static void newDataField (DataField::Ref &ref,const GlishArray &arr)
{
  Array<T> array;
  arr.get(array);
  bool del;
  const T * data = array.getStorage(del);
  ref <<= new DataField(typeIdOf(T),array.nelements(),DMI::WRITE,data);
  array.freeStorage(data,del);
}

// helper template to create a new DataArray from a GlishArray
// of the template argument type
template<class T> 
static void newDataArray (DataArray::Ref &ref,const GlishArray &arr)
{
  Array<T> array;
  arr.get(array);
  ref <<= new DataArray(array,DMI::WRITE);
}

// helper function creates a DataArray from a GlishArray
static DataArray::Ref makeDataArray (const GlishArray &arr,bool isIndex)
{
  DataArray::Ref ref;
  switch( arr.elementType() )
  {
    case GlishArray::BOOL:      
        newDataArray<Bool>(ref,arr);
        return ref;
        
    case GlishArray::BYTE:
        newDataArray<uChar>(ref,arr);
        return ref;
        
    case GlishArray::SHORT:
        newDataArray<Short>(ref,arr);
        return ref;
    
    case GlishArray::INT: // explicitly adjust for index
    {
        Array<Int> array;
        arr.get(array);
        if( isIndex )
          array -= 1;
        ref <<= new DataArray(array);
        return ref;
    }
    
    case GlishArray::FLOAT:
        newDataArray<Float>(ref,arr);
        return ref;
    
    case GlishArray::DOUBLE:
        newDataArray<Double>(ref,arr);
        return ref;
    
    case GlishArray::COMPLEX:
        newDataArray<Complex>(ref,arr);
        return ref;
    
    case GlishArray::DCOMPLEX:
        newDataArray<DComplex>(ref,arr);
        return ref;
    
    case GlishArray::STRING: 
        newDataArray<String>(ref,arr);
        return ref;
    
    default:
        dprintf(2)("warning: unknown Glish array type %d, ignoring\n",arr.elementType());
        ref <<= new DataArray;
        return ref;
  }
}

// helper function creates a DataField from a GlishArray (must be 1D)
static DataField::Ref makeDataField (const GlishArray &arr,bool isIndex)
{
  DataField::Ref ref;
  switch( arr.elementType() )
  {
    case GlishArray::BOOL:      
        newDataField<Bool>(ref,arr);
        return ref;
    case GlishArray::BYTE:
        newDataField<uChar>(ref,arr);
        return ref;
    case GlishArray::SHORT:
        newDataField<Short>(ref,arr);
        return ref;
    
    case GlishArray::INT: // explicitly adjust for index
    {
        Array<Int> array;
        arr.get(array);
        if( isIndex )
          array -= 1;
        bool del;
        const Int * data = array.getStorage(del);
        ref <<= new DataField(Tpint,array.nelements(),DMI::WRITE,data);
        array.freeStorage(data,del);
        return ref;
    }
    
    case GlishArray::FLOAT:
        newDataField<Float>(ref,arr);
        return ref;
    
    case GlishArray::DOUBLE:
        newDataField<Double>(ref,arr);
        return ref;
    
    case GlishArray::COMPLEX:
        newDataField<Complex>(ref,arr);
        return ref;
    
    case GlishArray::DCOMPLEX:
        newDataField<DComplex>(ref,arr);
        return ref;
    
    case GlishArray::STRING: 
    {
        Vector<String> array;
        arr.get(array);
        ref <<= new DataField(Tpstring,array.nelements(),DMI::WRITE);
        DataField &field = ref.dewr();
        for( uint i=0; i < array.nelements(); i++ )
          field[i] = array(i);
        return ref;
    }
    
    default:
        dprintf(2)("warning: unknown Glish array type %d, ignoring\n",arr.elementType());
        ref <<= new DataField;
        return ref;
  }
}


//##ModelId=3DB936940034
void GlishClientWP::glishToRec (const GlishRecord &glrec, DataRecord& rec)
{
  for( uint i=0; i < glrec.nelements(); i++ )
  {
    string field_name = glrec.name(i);
    try // handle failed fields gracefully
    {
      HIID id = field_name;
      GlishValue val = glrec.get(i);
      bool isIndex = ( id[id.size()-1] == AidIndex );

      // arrays are mapped to DataArrays; 1D arrays may also map to a DataField.
      // If the record was produced here (see recToGlish, above), this is 
      // indicated by the 'is_datafield'/'is_dataarray' attribute. If this is 
      // not present, use DataArray by default.
      if( val.type() == GlishValue::ARRAY )
      {
        GlishArray arr = val;
        IPosition shape = arr.shape();
        // 1D array marked with "is_datafiled" attribute maps to DataField
        if( shape.nelements() == 1 && val.attributeExists("is_datafield") )
          rec[id] <<= makeDataField(arr,isIndex);
        else // other arrays map to DataArrays
          rec[id] <<= makeDataArray(arr,isIndex);
      }
      else // it's a record
      {
        GlishRecord glsubrec = val;
        // is it a non-Glish object passed as a block record?
        if( glsubrec.attributeExists("blocktype")  )
        {
          rec[id] <<= blockRecToObject(glsubrec);
        }
        // is it a record of records?
        else if( glsubrec.attributeExists("field_of_records")  )
        {
          int nrec; GlishArray tmp;
          tmp = glsubrec.getAttribute("field_of_records"); tmp.get(nrec);
          // create field of records
          DataField *field = new DataField(TpDataRecord,nrec);
          rec[id] <<= field;
          // recursively interpret them one by one
          // do a try-catch, so that errors are gracefully ignored
          for( int i=0; i<nrec; i++ )
          {
            try
            {
              GlishValue val = glsubrec.get(i);
              FailWhen(val.type() != GlishValue::RECORD,"field is not a sub-record" );
              glishToRec(val,(*field)[i]);
            }
            catch( std::exception &exc )
            {
              dprintf(2)("warning: ignoring field %s[%d] (got exception: %s)\n",
                  field_name.c_str(),i,exc.what());
            }
          }
        }
        // is it a record of arrays?
        else if( glsubrec.attributeExists("field_of_arrays")  )
        {
          int narr; GlishArray tmp;
          tmp = glsubrec.getAttribute("field_of_arrays"); tmp.get(narr);
          // create field of arrays
          DataField *field = new DataField(TpDataArray,narr);
          rec[id] <<= field;
          // interpret them one by one
          // do a try-catch, so that errors are gracefully ignored
          for( int i=0; i<narr; i++ )
          {
            try
            {
              GlishValue val = glsubrec.get(i);
              if( val.type() == GlishValue::ARRAY )
                (*field)[i] <<= makeDataArray(val,isIndex);
              else // array of incompatible type must be a block record
                (*field)[i] <<= blockRecToObject(val);
            }
            catch( std::exception &exc )
            {
              dprintf(2)("warning: ignoring field %s[%d] (got exception: %s)\n",
                  field_name.c_str(),i,exc.what());
            }
          }
        }
        // else single record, add to field and interpret recursively
        else 
        {
          DataRecord *subrec = new DataRecord;
          rec[id] <<= subrec;
          glishToRec(glsubrec,*subrec);
        }
      }
    }
    catch( std::exception &exc )
    {
      dprintf(2)("warning: ignoring field %s (got exception: %s)\n",
          field_name.c_str(),exc.what());
    }
  }
}

//##ModelId=3DB93695024D
BlockableObject * GlishClientWP::blockRecToObject (const GlishRecord &rec)
{
  FailWhen( !rec.attributeExists("blocktype"),"missing 'blocktype' attribute" );
  String typestr;
  GlishArray tmp = rec.getAttribute("blocktype"); tmp.get(typestr);
  TypeId tid(typestr);
  FailWhen( !tid,"illegal blocktype "+static_cast<string>(typestr) );
  // extract blockset form record
  BlockSet set;
  for( uint i=0; i<rec.nelements(); i++ )
  {
    Array<uChar> arr;
    tmp = rec.get(i); tmp.get(arr);
    // create SmartBlock and copy data from array
    size_t sz = arr.nelements();
    SmartBlock *block = new SmartBlock(sz);
    set.pushNew().attach(block,DMI::WRITE|DMI::ANON);
    if( sz )
    {
      Bool del;
      const uChar * data = arr.getStorage(del);
      memcpy(block->data(),data,sz);
      arr.freeStorage(data,del);
    }
  }
  // create object & return
  return DynamicTypeManager::construct(tid,set);
}

//##ModelId=3DB936930231
void GlishClientWP::objectToBlockRec (const BlockableObject &obj,GlishRecord &rec )
{
  BlockSet set;
  obj.toBlock(set);
  rec.addAttribute("blocktype",GlishArray(obj.objectType().toString()));
  int i=0;
  while( set.size() )
  {
    char num[32];
    sprintf(num,"%d",i++);
    rec.add("num",Array<uChar>(IPosition(1,set.front()->size()),
                static_cast<uChar*>(const_cast<void*>(set.front()->data())),COPY));
    set.pop();
  }
}

//##ModelId=3DB9369900E1
void GlishClientWP::shutdown ()
{
  dprintf(1)("shutting down\n");
  connected = False;
  setState(-1);
  removeInput(-1);
  removeTimeout("*");
  if( autostop() )
  {
    dprintf(1)("autostop is on: stopping the system\n");
    dsp()->stopPolling();
  }
  else
  {
    dprintf(1)("detaching\n");
    detachMyself();
  }
}

GlishClientWP * makeGlishClientWP (int argc,const char *argv[] )
{
  // stupid glish wants non-const argv
  GlishSysEventSource *evsrc = 
      new GlishSysEventSource(argc,const_cast<char**>(argv));
  AtomicID wpc = AidGlishClientWP;
  // scan arguments for an override
  string wpcstr;
  for( int i=1; i<argc; i++ )
  {
    if( string(argv[i]) == "-wpc" && i < argc-1 )
    {
      wpcstr = argv[i+1];
      break;
    }
  }
  if( wpcstr.length() )
    wpc = AtomicID(wpcstr);
  return new GlishClientWP(evsrc,wpc);
}



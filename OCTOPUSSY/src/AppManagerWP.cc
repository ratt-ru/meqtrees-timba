#include "AppManagerWP.h"

using namespace AppManagerVocabulary;

    
//##ModelId=3E316F2A020D
AppManagerWP::AppManagerWP ()
    : WorkProcess(AidAppManagerWP)
{
}

//##ModelId=3E316F2A01FE
void AppManagerWP::init ()
{
  subscribe(MsgLaunch,Message::GLOBAL);
  subscribe(MsgHalt,Message::GLOBAL);
}

//##ModelId=3E316F2A0200
bool AppManagerWP::start()
{
  MessageRef ref;
  Message::withDataRecord(ref,MsgStarted,"AppManager started");
  publish(ref);
  return False;
}

//##ModelId=3E316F2A0202
void AppManagerWP::stop()
{
  MessageRef ref;
  Message::withDataRecord(ref,MsgStopped,"AppManager stopped");
  publish(ref);
  appmap.clear();
}

//##ModelId=3E316F2A0204
int AppManagerWP::receive (MessageRef &mref)
{
  HIID fail_id;
  try
  {
    const HIID &id = mref->id();
    // handle launch command
    if( id.matches(MsgLaunch) )
    {
      fail_id = MsgLaunchFailed;
      // privatize the message for writing
      mref.privatize(DMI::WRITE,0);
      Message &msg = mref.dewr();
      // any fails here are reported back to sender
      const DataRecord &rec = msg.record();
      // get app id from record
      AtomicID appid;
      TypeId type = rec[AidID].type();
      if( type == Tpstring )
        appid = AtomicID(rec[AidID].as_string());
      else if( type == TpAtomicID )
        appid = rec[AidID].as_AtomicID();
      else
      {
        // throw exception
        Throw("Bad ID field in "+mref->id().toString()+" message");
      }
      FailWhen(!isRegistered(appid),"unregistered application "+appid.toString()); 
      // get statup parameters 
      DataRecord::Ref initrec;
      if( rec[AidParameters].exists() )
        initrec = rec[AidParameters].ref().ref_cast<DataRecord>();
      // create the WP or app
      AppMapEntry entry;
      if( !construct(entry.wpref,appid,initrec) )
      {
        Throw("constructor failed for "+appid.toString()); 
      }
      // attach to dispatcher
      WPRef wpref(entry.wpref,DMI::WRITE|DMI::COPYREF);
      MsgAddress wpaddr = dsp()->attach(wpref);
      WPID wpid = wpaddr.wpid();
      // report success to creator
      Message::Ref mref2;
      DataRecord &rec2 = Message::withDataRecord(mref2,MsgLaunched);
      rec2[AidAddress] = wpaddr;
      rec2[AidText] = "Launched app "+wpid.toString(); 
      send(mref2,msg.from());
      // add to map 
      entry.started = False;
      entry.creator = msg.from();
      appmap[wpid] = entry;
    }
    // handle stop command 
    else if( id.matches(MsgHalt) )
    {
      fail_id = MsgHaltFailed;
      WPID wpid(id[id.length()-2],id[id.length()-1]);
      AMI iter = appmap.find(wpid);
      FailWhen( iter == appmap.end(),"app "+wpid.toString()+" not running here" );
      // detach the app
      //   NB: check permissions perhaps?
      MsgAddress wpaddr = iter->second.wpref->address();
      dsp()->detach(wpid);
      // report success to creator
      Message::Ref mref2;
      DataRecord &rec2 = Message::withDataRecord(mref2,MsgHalted);
      rec2[AidAddress] = wpaddr;
      rec2[AidText] = "Halted app "+wpid.toString(); 
      send(mref2,mref->from());
    }
  }
  catch( std::exception &exc )
  {
    // re-throw if no "Failed" message was set up
    if( !fail_id.length() )
      throw(exc);
    // send all exceptions back to sender as "Failed" messages
    // if no payload, insert a DataRecord
    mref.privatize(DMI::WRITE,0);
    Message &msg = mref.dewr();
    if( msg.payloadType() != TpDataRecord )
      msg <<= new DataRecord;
    else
      msg.payload().privatize(DMI::WRITE,0);
    // insert the exception text into the message payload
    if( msg[AidText].exists() )
      msg[AidText].remove();
    msg[AidText] = exc.what();
    // return to sender
    msg.setId(fail_id);
    send(mref,msg.from());
  }
  
  return Message::ACCEPT;
}


#include "VisRepeater.h"

using namespace AppControlAgentVocabulary;
using namespace VisRepeaterVocabulary;
using namespace VisVocabulary;
using namespace AppState;
using namespace VisAgent;

InitDebugSubContext(VisRepeater,ApplicationBase,"VisRepeater");

//##ModelId=3F5F4366018C
void VisRepeater::postDataEvent (const HIID &event,const string &msg,DataRecord::Ref::Xfer &rec)
{
  if( !rec.valid() )
    rec <<= new DataRecord;
  if( !vdsid_.empty() )
    rec()[FVDSID] = vdsid_;
  if( !datatype_.empty() )
    rec()[FDataType] = datatype_;
  if( msg.length() )
    rec()[AidText] = msg;
  control().postEvent(event|datatype_|vdsid_,rec);
}

//##ModelId=3E392C570286
void VisRepeater::run ()
{
  verifySetup(True);
  DataRecord::Ref initrec;
  // keep running as long as start() on the control agent succeeds
  while( control().start(initrec) == RUNNING )
  {
    // [re]initialize i/o agents with record returned by control
    cdebug(1)<<"initializing I/O agents\n";
    if( !input().init(*initrec) )
    {
      control().postEvent(InputInitFailed);
      control().setState(STOPPED);
      continue;
    }
    if( !output().init(*initrec) )
    {
      control().postEvent(OutputInitFailed);
      control().setState(STOPPED);
      continue;
    }
    auto_pause_ = (*initrec)[FAutoPause].as<bool>(False);
    bool output_open = True;
    int ntiles = 0;
    state_ = FOOTER;
    vdsid_.clear();
    control().setStatus(StStreamState,"none");
    control().setStatus(StNumTiles,0);
    control().setStatus(StVDSID,vdsid_);
    // run main loop
    while( control().state() > 0 )  // while in a running state
    {
      HIID id;
      DataRecord::Ref eventrec;
      eventrec.detach();
      ObjRef ref;
      int outstat = AppEvent::SUCCESS;
      cdebug(4)<<"looking for data chunk\n";
      int intype = input().getNext(id,ref,0,AppEvent::WAIT);
      if( intype > 0 )
      {
        if( output_open )
        {
          bool write = True;
          HIID event;
          string message;
          // check that type is consistent with state
          switch( intype )
          {
            case HEADER:
            {
              cdebug(2)<<"received HEADER "<<id<<endl;
              // if not expecting a header, post warning event
              if( state_ != FOOTER )
              {
                cdebug(2)<<"header interrupts previous data set "<<vdsid_<<endl;
                postDataEvent(DataSetInterrupt,"unexpected header, interrupting data set",eventrec);
              }
              datatype_ = HIID();
              eventrec <<= new DataRecord;
              if( ref.valid() )
              {
                header_ = ref.copy();
                eventrec()[AidHeader] <<= ref.copy();
                if( ref->objectType() == TpDataRecord )
                {
                  const DataRecord &rec = *ref.ref_cast<DataRecord>();
                  datatype_ = rec[FDataType].as<HIID>(HIID());
                  cdebug(2)<<"header: "<<rec.sdebug(5);
                }
              }
              else
                header_.detach();
              state_ = HEADER;
              event = DataSetHeader;
              message = "received header for dataset "+id.toString();
              if( !datatype_.empty() )
                message += ", " + datatype_.toString();
              control().setStatus(StStreamState,"HEADER");
              control().setStatus(StNumTiles,ntiles=0);
              control().setStatus(StVDSID,vdsid_ = id);
              control().setStatus(FDataType,datatype_);
              break;
            }
            case DATA:
            {
              if( state_ != HEADER && state_ != DATA )
              {
                write = False;
                cdebug(3)<<"DATA "<<id<<" out of sequence, state is "<<AtomicID(-state_)<<", dropping\n";
              }
              else
              {
                if( state_ == HEADER )
                  control().setStatus(StStreamState,"DATA");
                ntiles++;
                if( !(ntiles%100) )
                  control().setStatus(StNumTiles,ntiles);
                state_ = DATA;
              }
              break;
            } 
            case FOOTER:
            {
              if( state_ == HEADER || state_ == DATA )
              {
                eventrec <<= new DataRecord;
                if( header_.valid() )
                  eventrec()[AidHeader] <<= header_.copy();
                if( ref.valid() )
                  eventrec()[AidFooter] <<= ref.copy();
                if( id == vdsid_ )
                {
                  cdebug(2)<<"received FOOTER "<<id<<endl;
                  state_ = FOOTER;
                  event = DataSetFooter;
                  message = ssprintf("received footer for dataset %s, %d tiles written",
                      id.toString().c_str(),ntiles);
                  control().setStatus(StStreamState,"FOOTER");
                  control().setStatus(StNumTiles,ntiles);
                  if( auto_pause_ )
                  {
                    control().postEvent(AutoPauseNotify,"repeater auto-paused after footer");
                    control().pause();
                  }
                }
                else
                {
                  write = False;
                  cdebug(3)<<"FOOTER "<<id<<" does not match dataset "<<vdsid_<<", dropping\n";
                  postDataEvent(FooterMismatch,"footer id "+id.toString()+" does not match",eventrec);
                }
              }
              else
              {
                write = False;
                cdebug(3)<<"FOOTER "<<id<<" out of sequence, state is "<<AtomicID(-state_)<<", dropping\n";
              }
              break;
            }
            default:
            {
               cdebug(3)<<"unrecognized input type in event "<<id<<", dropping"<<endl;
               write = False;
            }
          }
          if( write )
          {
            cdebug(3)<<"writing to output: "<<AtomicID(-intype)<<", id "<<id<<endl;
            outstat = output().put(intype,ref);
            if( !event.empty() )
              postDataEvent(event,message,eventrec);
          }
        }
        else
        {
          cdebug(3)<<"received "<<AtomicID(-intype)<<", id "<<id<<", output is closed\n";
        }
      }
      // handle i/o errors
      // error on the output stream? report event but keep things moving
      if( output_open )
      {
        if( outstat == AppEvent::ERROR )
        {
          cdebug(2)<<"error on output: "<<output().stateString()<<endl;
          postDataEvent(OutputErrorEvent,output().stateString(),eventrec);
          control().setState(OUTPUT_ERROR);
          output_open = False;
        }
        else if( outstat != AppEvent::SUCCESS )
        {
          // this is possible if we never got a header from the input, and 
          // the output wants a header
          cdebug(2)<<"warning: output stream returned "<<outstat<<endl;
          if( outstat == AppEvent::OUTOFSEQ )
            postDataEvent(OutputSequenceEvent,"output is out of sequence",eventrec);
        }
      }
      // error on the input stream? terminate the transaction
      if( intype == AppEvent::ERROR )
      {
        cdebug(2)<<"error on input: "<<input().stateString()<<endl;
        postDataEvent(InputErrorEvent,input().stateString(),eventrec);
        control().setState(INPUT_ERROR);
        continue;
      }
      // closed the input stream? terminate the transaction
      else if( intype == AppEvent::CLOSED )
      {
        cdebug(2)<<"input closed: "<<input().stateString()<<endl;
        postDataEvent(InputClosedEvent,input().stateString(),eventrec);
        control().setState(INPUT_CLOSED);
        continue;
      }
      // check for commands from the control agent
      HIID cmdid;
      DataRecord::Ref cmddata;
      control().getCommand(cmdid,cmddata,AppEvent::WAIT);
      // .. but ignore them since we only watch for state changes anyway
    }
    // broke out of main loop -- close i/o agents
    input().close();
    output().close();
    // go back up for another start() call
  }
  cdebug(1)<<"exiting with control state "<<control().stateString()<<endl;
  control().close();
}

//##ModelId=3E392EE403C8
string VisRepeater::stateString () const
{
  Thread::Mutex::Lock lock(control().mutex());
  int st = state();
  string str = control().stateString();
  
  if( st == OUTPUT_ERROR )
    str = "OUTPUT_ERROR"+str;
  else if( st == INPUT_CLOSED )
    str = "INPUT_CLOSED"+str;
  else if( st == INPUT_ERROR )
    str = "INPUT_ERROR"+str;
  
  return str;
}

//##ModelId=3E3FEB5002A5
string VisRepeater::sdebug(int detail, const string &prefix, const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"VisRepeater",(int)this);
  }
  if( detail >= 1 || detail == -1 )
  {
    append(out,"st:" + stateString());
  }
  if( detail >= 2 || detail == -2 )
  {
    append(out,"[" + input().stateString() + ","
                    + output().stateString() + "]" );
  }
  if( detail >= 3 || detail == -3 )
  {
    out += "\n" + prefix + "  input: " + input().sdebug(abs(detail)-2,prefix+"    ");
    out += "\n" + prefix + "  output: " + output().sdebug(abs(detail)-2,prefix+"    ");
    out += "\n" + prefix + "  control: " + control().sdebug(abs(detail)-2,prefix+"    ");
  }
  return out;
}


#include "VisRepeater.h"

using namespace AppControlAgentVocabulary;
using namespace VisRepeaterVocabulary;
using namespace AppState;

InitDebugSubContext(VisRepeater,ApplicationBase,"VisRepeater");

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
    bool output_open = True;
    // run main loop
    while( control().state() > 0 )  // while in a running state
    {
      HIID id;
      ObjRef ref;
      int outstat = AppEvent::SUCCESS;
      cdebug(4)<<"looking for data chunk\n";
      int intype = input().getNext(id,ref,0,AppEvent::WAIT);
      if( intype > 0 )
      {
        if( output_open )
        {
          cdebug(3)<<"received "<<AtomicID(-intype)<<", id "<<id<<", copying to output\n";
          outstat = output().put(intype,ref);
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
          control().postEvent(OutputErrorEvent,output().stateString());
          control().setState(OUTPUT_ERROR);
          output_open = False;
        }
        else if( outstat != AppEvent::SUCCESS )
        {
          // this is possible if we never got a header from the input, and 
          // the output wants a header
          cdebug(2)<<"warning: output stream returned "<<outstat<<endl;
          if( outstat == AppEvent::OUTOFSEQ )
          {
            control().postEvent(OutputSequenceEvent,"output is out of sequence");
          }
        }
      }
      // error on the input stream? terminate the transaction
      if( intype == AppEvent::ERROR )
      {
        cdebug(2)<<"error on input: "<<input().stateString()<<endl;
        control().postEvent(InputErrorEvent,input().stateString());
        control().setState(INPUT_ERROR);
        continue;
      }
      // closed the input stream? terminate the transaction
      else if( intype == AppEvent::CLOSED )
      {
        cdebug(2)<<"input closed: "<<input().stateString()<<endl;
        control().postEvent(InputClosedEvent,input().stateString());
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


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
      DataRecord::Ref header;
      VisTile::Ref tile;
      int instat,outstat = AppEvent::SUCCESS;
      // try getting a tile first (this is the more frequent case)
      cdebug(4)<<"looking for tile\n";
      instat = input().getNextTile(tile,AppEvent::WAIT);
      if( instat == AppEvent::SUCCESS )
      { // got a tile? See what to do with it
        
        // note that if the output stream has been closed, then the data is 
        // simply ignored
        cdebug(3)<<"received tile "<<tile->tileId()<<", copying to output\n";
        if( output_open )
          outstat = output().putNextTile(tile);
      }
      else if( instat == AppEvent::OUTOFSEQ ) // out of sequence? Look for a header instead
      {
        cdebug(4)<<"looking for header\n";
        instat = input().getHeader(header,AppEvent::WAIT);
        if( instat == AppEvent::SUCCESS )
        { // got one? place on output stream, unless closed
          cdebug(3)<<"received header, copying to output\n";
          if( output_open )
            outstat = output().putHeader(header);
        }
      }
      // handle i/o errors
      // error on the output stream? report event but keep things moving
      if( output_open )
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
      // error on the input stream? terminate the transaction
      if( instat == AppEvent::ERROR )
      {
        cdebug(2)<<"error on input: "<<input().stateString()<<endl;
        control().postEvent(InputErrorEvent,input().stateString());
        control().setState(INPUT_ERROR);
        continue;
      }
      // closed the input stream? terminate the transaction
      else if( instat == AppEvent::CLOSED )
      {
        cdebug(2)<<"input closed: "<<input().stateString()<<endl;
        control().postEvent(InputClosedEvent,input().stateString());
        control().setState(INPUT_CLOSED);
        continue;
      }
      // -----------------------------------------------
      // check control agent for any other state changes
      HIID id;
      DataRecord::Ref data;
      cdebug(4)<<"checking control agent\n";
      if( control().getCommand(id,initrec,AppEvent::WAIT) == AppEvent::PAUSED )
      {
        // if paused, then suspend the input stream, and block completely until
        // control gets unpaused (i.e. a RESUME command is received, or the
        // state changes)
        cdebug(3)<<"entering suspend mode";
        input().suspend();
        while( control().isPaused() )
          control().getCommand(id,initrec,AppEvent::BLOCK);
        input().resume();
        cdebug(3)<<"resuming from suspend mode";
      }
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


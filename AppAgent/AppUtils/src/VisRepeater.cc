#include "VisRepeater.h"

using namespace AppControlAgentVocabulary;
using namespace VisRepeaterVocabulary;

using namespace AppState;

InitDebugSubContext(VisRepeater,ApplicationBase,"VisRepeater");
    
//##ModelId=3E392B78035E
VisRepeater::VisRepeater(VisAgent::InputAgent& in, VisAgent::OutputAgent& out, AppControlAgent& ctrl)
    : input(in),output(out),control(ctrl)
{
}

//##ModelId=3E392C570286
void VisRepeater::run (DataRecord::Ref &initrec)
{
  for(;;)
  {
    // initialize all agents
    cdebug(1)<<"initializing\n";
    input.init(*initrec);
    output.init(*initrec);
    control.init(*initrec);
    control.setState(RUNNING);
    // keep track of changes in the output stream state, to report errors
    // if closed
    bool output_open = True;
    // run main loop
    while( control.state() > 0 )  // while in a running state
    {
      DataRecord::Ref header;
      VisTile::Ref tile;
      int instat,outstat = AppEvent::SUCCESS;
      // try getting a tile first (this is the more frequent case)
      instat = input.getNextTile(tile,AppEvent::WAIT);
      if( instat == AppEvent::SUCCESS )
      { // got one? place on output stream
        // note that if the output stream has been closed, then the data is 
        // simply ignored
        cdebug(3)<<"received tile, copying to output\n";
        if( output_open )
          outstat = output.putNextTile(tile);
      }
      else if( instat == AppEvent::OUTOFSEQ ) // out of sequence? Look for a header instead
      {
        instat = input.getHeader(header,AppEvent::WAIT);
        if( instat == AppEvent::SUCCESS )
        { // got one? place on output stream, unless closed
          cdebug(3)<<"received header, copying to output\n";
          if( output_open )
            outstat = output.putHeader(header);
        }
      }
      // error on the output stream? report event but keep things moving
      if( output_open )
        if( outstat == AppEvent::ERROR )
        {
          cdebug(2)<<"error on output: "<<output.stateString()<<endl;
          control.postEvent(OutputErrorEvent,output.stateString());
          control.setState(OUTPUT_ERROR);
          output_open = False;
        }
        else if( outstat != AppEvent::SUCCESS )
        {
          // this is possible if we never got a header from the input, and 
          // the output wants a header
          cdebug(2)<<"warning: output stream returned "<<outstat<<endl;
          if( outstat == AppEvent::OUTOFSEQ )
          {
            control.postEvent(OutputSequenceEvent,"output is out of sequence");
          }
        }
      // error on the input stream? terminate the transaction
      if( instat == AppEvent::ERROR )
      {
        cdebug(2)<<"error on input: "<<input.stateString()<<endl;
        control.postEvent(InputErrorEvent,input.stateString());
        control.setState(INPUT_ERROR);
      }
      // closed the input stream? terminate the transaction
      else if( instat == AppEvent::CLOSED )
      {
        cdebug(2)<<"input closed: "<<input.stateString()<<endl;
        control.postEvent(InputClosedEvent,input.stateString());
        control.setState(INPUT_CLOSED);
      }
      // check control agent for any other state changes
      HIID id;
      DataRecord::Ref data;
      if( control.getCommand(id,initrec,AppEvent::WAIT) == AppEvent::PAUSED )
      {
        // if paused, then suspend the input stream, and block completely until
        // control gets unpaused (i.e. a RESUME command is received, or the
        // state changes)
        cdebug(3)<<"entering suspend mode";
        input.suspend();
        while( control.isPaused() )
          control.getCommand(id,initrec,AppEvent::BLOCK);
        input.resume();
        cdebug(3)<<"resuming from suspend mode";
      }
    }
    // broke out of main loop -- close i/o agents
    input.close();
    output.close();
    // otherwise, wait for INIT state to do another run. Block in the control
    // agent until the state changes. If it changes to HALTED, return
    while( control.state() != INIT )
    {
      cdebug(1)<<"state is now "<<state()<<endl;
      // break out if control is halted
      if( control.state() == HALTED )
      {
        cdebug(1)<<"halting"<<endl;
        control.close();
        return;
      }
      HIID id;
      control.getCommand(id,initrec,AppEvent::BLOCK);
    }
  }
}

//##ModelId=3E392EDF034C
int VisRepeater::state () const
{
  return control.state();
}

//##ModelId=3E392EE403C8
string VisRepeater::stateString () const
{
  Thread::Mutex::Lock lock(control.mutex());
  int st = state();
  string str = control.stateString();
  
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
    append(out,"[" + input.stateString() + ","
                    + output.stateString() + "]" );
  }
  if( detail >= 3 || detail == -3 )
  {
    out += "\n" + prefix + "  input: " + input.sdebug(abs(detail)-2,prefix+"    ");
    out += "\n" + prefix + "  output: " + output.sdebug(abs(detail)-2,prefix+"    ");
    out += "\n" + prefix + "  control: " + control.sdebug(abs(detail)-2,prefix+"    ");
  }
  return out;
}


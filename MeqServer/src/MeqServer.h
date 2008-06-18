//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#ifndef MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D
#define MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D
 
#include <DMI/Events.h>
#include <MEQ/Forest.h>
#include <AppAgent/EventChannel.h>
#include <MeqServer/AID-MeqServer.h>

#pragma aidgroup MeqServer    
#pragma aid MeqClient
#pragma aid Node Name NodeIndex MeqServer Meq CWD Proc MPI Num 
#pragma aid Create Delete Get Set State Request Resolve Child Children List Batch
#pragma aid App Command Args Result Data Processing Error Message Code
#pragma aid Execute Clear Cache Save Load Forest Recursive Forest Header Version 
#pragma aid Publish Results Enable Disable Event Id Silent Idle Stream 
#pragma aid Debug Breakpoint Single Shot Step Continue Until Stop Level
#pragma aid Get Forest Status Stack Running Changed All Disabled Publishing
#pragma aid Python Init TDL Script File Source Serial String Session
#pragma aid Idle Executing Exec Debug Constructing Updating Sync Stopped
    
namespace Meq
{
  const HIID  
    FArgs             = AidArgs,
    FSilent           = AidSilent,
    FCommandIndex     = AidCommand|AidIndex,
    FSync             = AidSync,
      
    FFileName         = AidFile|AidName,
      
    FEnable           = AidEnable,
    FEventId          = AidEvent|AidId,
    FEventData        = AidEvent|AidData,
    
      
    EvNodeStatus      = AidNode|AidStatus,
    
    EvDebugStop       = AidDebug|AidStop;
  
  

//##ModelId=3F5F195E013B
//##Documentation
class MeqServer : public DMI::EventRecepient
{
  public:
    //##ModelId=3F5F195E0140
    MeqServer ();
  
    // attaches a control channel to this MeqServer
    void attachControl (const AppAgent::EventChannel::Ref &channel)
    { control_channel_ = channel; }
    
    virtual ~MeqServer ();

    //##ModelId=3F608106021C
    // runs command processing loop until Halt command is received or control 
    // channel is closed
    virtual void run ();
    
    // Generic command interface. Executes the given command with the given
    // arguments. Two modes are available for dispensing with the command 
    // results and reporting errors.
    // If post_results=true:
    //    Command results are posted to the output channel. Any exceptions
    //    are caught and also posted, so none will be thrown by this
    //    function. Return value is undefined.
    // If post_results=false:
    //    Command results are returned via a record ref. If command is sync
    //    (i.e. has been placed on exec queue), this will be an empty record.
    //    Any errors will be thrown as exceptions.
    // If wait_for_async_queue is True and a sync command is being executed,
    // waits for the async queue to finish
    //  NB: I'm no longer sure why I added that option, or why the default was true --
    //  this caused all async commands to block during request execution. Changed the
    //  default to False as of 14/08/07.
    DMI::Record::Ref executeCommand (const HIID &cmd,DMI::Record::Ref &args,bool post_results=false,bool wait_for_async_queue=false);

    // halts the meqserver
    void halt (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    // sets current directory
    void setCurrentDir (DMI::Record::Ref &out,DMI::Record::Ref &in);
    // sets session name
    void setSessionName (DMI::Record::Ref &out,DMI::Record::Ref &in);
    // sets state
    void setForestState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    // gets status + state record
    void getForestState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    // gets status only
    void getForestStatus (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    //##ModelId=3F61920F01A8
    void createNode   (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void createNodeBatch (DMI::Record::Ref &out,DMI::Record::Ref &in);
    #ifdef HAVE_MPI
    void createNodeBatch_Mpi (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void getNodeList_Mpi  (DMI::Record::Ref &out,DMI::Record::Ref &in);
    #endif
    //##ModelId=3F61920F01FA
    void deleteNode   (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F024E
    void nodeGetState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F02A4
    void nodeSetState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F98D91A03B9
    void initNode     (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void initNodeBatch(DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F98D91B0064
    void getNodeList  (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    void getNodeIndex (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    //##ModelId=400E5B6C015E
    void nodeExecute  (DMI::Record::Ref &out,DMI::Record::Ref &in);
/*    //##ModelId=400E5B6C0247
    void saveForest (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=400E5B6C02B3
    void loadForest (DMI::Record::Ref &out,DMI::Record::Ref &in);*/
    //##ModelId=400E5B6C0324
    void clearForest (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    void disablePublishResults (DMI::Record::Ref &out,DMI::Record::Ref &in);

    void executeAbort (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    void setForestBreakpoint  (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void clearForestBreakpoint(DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    void debugSetLevel      (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void debugInterrupt     (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void debugSingleStep    (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void debugNextNode      (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void debugContinue      (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void debugUntilNode     (DMI::Record::Ref &out,DMI::Record::Ref &in);

    // public interface to execute a command. 
    // Executes command and returns result in a record (unless command
    // is async, in which case and invalid ref is returned). Errors
    // are indicated by throwing an exception.
    DMI::Record::Ref executeCommand (const HIID &cmd,ObjRef &argref);
    
    // returns control channel
    AppAgent::EventChannel & control ()
    { return control_channel_(); }
    
    // callback for receiving an event
    virtual int receiveEvent (const EventIdentifier &evid,const ObjRef &,void *);

    // posts a message or error event (with type==AidError) on the control channel
    void postMessage (const std::string &msg,const HIID &type = AidMessage,AtomicID category = AidNormal);
    
    // error messages are posted with a type of Error and a Normal category by default
    void postError (const std::string &msg,AtomicID category = AidNormal)
    { postMessage(msg,AidError,category); }
    
    // posts an error message corresponding to exception
    // error messages are posted with a type of Error and a Normal category by default
    void postError (const std::exception &exc,AtomicID category = AidNormal);
    
    // posts a generic event on the control channel
    void postEvent (const HIID &type,const ObjRef &data = ObjRef());
    void postEvent (const HIID &type,const DMI::Record::Ref &data);
    
    
    // returns forest object
    Forest & getForest ()
    { return forest; }
    
    //##ModelId=3F5F195E0156
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3F5F195E013F
    LocalDebugContext;

  private:
    // publishes state message to control channel
    void publishState ();  
      
    // sets new app state, returns old state
    // If !quiet and state has changed, calls publishState
    AtomicID setState (AtomicID state,bool quiet=false);
    
    AtomicID state () const
    { return state_; }
      
    //##ModelId=3F6196800325
    NodeFace & resolveNode (bool &getstate,const DMI::Record &rec);

    void reportNodeStatus  (Node &node,int oldstat,int newstat);

    void processBreakpoint (Node &node,int bpmask,bool global);
    
    // fills a record with forest_status (level>0) and 
    // and forest_state (level>1). If level==0, does nothing.
    void fillForestStatus  (DMI::Record &rec,int level=1);
    
    // fills a record with app state fields
    void fillAppState (DMI::Record &rec);
      
    // control channel
    AppAgent::EventChannel::Ref control_channel_;
    
    //##ModelId=3F5F218F02BD
    Forest forest;
    
    // current script name
    string script_name_;
    // current session name
    string session_name_;
    
    int forest_serial;
    int incrementForestSerial ()
    { 
      if( ++forest_serial < 1 )
        forest_serial = 1;
      return forest_serial;
    }
  
    //##ModelId=3F61920F0158
    typedef void (MeqServer::*PtrCommandMethod)(DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F016E
    typedef std::map<HIID,PtrCommandMethod> CommandMap;
    //##ModelId=3F61920F0193
    // Map of sync commands.
    // Sync commands are generally slow, and must be executed serially, 
    // so they're handled by a separate exec thread (see below)
    CommandMap sync_commands;
    // Map of async commands.
    // Async commands are fast, and are executed directly in the 
    // control thread.
    CommandMap async_commands;
    
    const Node * debug_next_node;
    const Node * debug_bp_node;
    int forest_breakpoint_;
    
    // flag: clear stop flag once the current command completes
    bool clear_stop_flag_; 
    
    // true as long as we're not exiting
    bool running_;
    
    // true while we're executing a node
    bool executing_;
    
    // node execution thread
    Thread::ThrID exec_thread_;
    
    // queue of commands to execute, empty if nothing is executing
    typedef struct 
    {
      PtrCommandMethod proc;  // command method, 0 for Node::processCommand()
      DMI::Record::Ref args;  // command arguments
      bool silent;            // silent flag (if true, no result event is produced, unless an error occurs)
      HIID command;           // command ID
      HIID reply;             // reply ID
    } ExecQueueEntry;
    
    typedef std::list<ExecQueueEntry> ExecQueue;
    ExecQueue exec_queue_;
    
    // condition variable indicating changes to queue or to running_ status
    Thread::Condition exec_cond_;
    
    // helper function used both by the exec thread and the main thread.
    // This executes the command specified by the given queue entry
    // (passed as non-const because args may be taken over).
    // If savestate=true, saves/restores the current MeqServer state().
    // If post_results=true:
    //    Command results are posted to the output channel. Any exceptions
    //    are caught and also posted, so none will be thrown by this
    //    function. Return value is undefined.
    // If post_results=false:
    //    Command results are returned via a record ref. If command is sync
    //    (i.e. has been placed on exec queue), this will be an empty record.
    //    Some control commands will also return an empty record.
    //    Any errors will be thrown as exceptions.
    DMI::Record::Ref execCommandEntry (ExecQueueEntry &qe,bool savestate,bool post_results);
    
    // helper function for execCommandEntry(). Executes a generic node 
    // command by calling Node::processCommand() with the command and args
    // found in qe. qe.command[0] must be "Node" (the actual command passed to
    // the node is qe.command[1:]). qe.args are taken over, hence qe
    // is passed in as non-const. The 'out' record is populated with
    // with the command result (if any). Errors are reported by throwing
    // exceptions.
    // The return value is 'true' if out contains something to be posted
    // as an output event (usually an error report), or false if things
    // quietly succeed.
    bool execNodeCommand (DMI::Record::Ref &out,ExecQueueEntry &qe);
   
    // method that runs the exec thread loop
    void * runExecutionThread ();
    // static function to start MeqServer's exec thread
    static void * startExecutionThread (void *mqs);
    
    
    // mutex for accessing the control agent
    Thread::Mutex control_mutex_;
    
    // MeqServer state
    AtomicID state_;
    
    
    // Global MeqServer singleton
    static MeqServer *mqs_;
    
    static void mqs_reportNodeStatus (Node &node,int oldstat,int newstat);

    static void mqs_processBreakpoint (Node &node,int bpmask,bool global);
    
    static void mqs_postEvent (const HIID &type,const ObjRef &data);
    
};

}; // namespace Meq

#endif /* MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D */

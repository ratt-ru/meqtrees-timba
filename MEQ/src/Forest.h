//#  Forest.h: MeqForest class
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$
#ifndef MEQ_SRC_FOREST_H_HEADER_INCLUDED_C53FA569
#define MEQ_SRC_FOREST_H_HEADER_INCLUDED_C53FA569

#include <MEQ/Node.h>
#include <MEQ/SymdepMap.h>
#include <MEQ/Request.h>
#include <MEQ/MeqVocabulary.h>
#include <DMI/HashMap.h>
#include <DMI/BOIO.h>
#include <vector>
#include <map>

#pragma aid Create Delete
#pragma aid Axes Symdeps Debug Level Profiling Enabled Cwd Append File Timestamp

namespace Meq
{
using namespace DMI;

//##ModelId=3F5F21740281
class Forest
{
  public:
    typedef enum {
      NL_NODEINDEX        = 1,
      NL_NAME             = 2,
      NL_CLASS            = 4,
      NL_CHILDREN         = 8,
      NL_CONTROL_STATUS   = 16,
      NL_PROFILING_STATS  = 32,
      NL_DEFAULT   = NL_NODEINDEX|NL_NAME|NL_CLASS|NL_CONTROL_STATUS,
    } NodeListContent;
    
    //##ModelId=3F60697A00ED
    Forest();

    // deletes all nodes
    //##ModelId=400E53050193
    void clear();

    //##ModelId=3F5F572601B2
    //##Documentation
    //## Creates a node using the given init record. The class of the node is
    //## determined by initrec["Class"].
    //## Returns ref to node.
    NodeFace & create (int &node_index, DMI::Record::Ref &initrec,
                       bool reinitializing=false);

    //##ModelId=3F5F5CA300E0
    //##Documentation
    //## Removes the node with the given index.
    int remove (int node_index);

    //##ModelId=3F5F5B4F01BD
    //##Documentation
    //## Returns node specified by index
    NodeFace & get (int node_index);

    //##ModelId=3F7048570004
    //##Documentation
    //## Returns ref to repository's countedref, specified by index
    const NodeFace::Ref & getRef (int node_index);

    //##ModelId=3F5F5B9D016A
    bool valid (int node_index) const;

    //##ModelId=3F5F5BB2032C
    //##Documentation
    //## Finds node by name, returns index (<0 if not found)
    int findIndex (const string& name) const;

    //##ModelId=3F60549B02FE
    //##Documentation
    //## Finds node by name, returns reference to node. Throws exception if not
    //## found.
    NodeFace & findNode(const string &name);

    //##ModelId=400E530501C2
    int maxNodeIndex () const
    { return nodes.size()-1; }

    // fills DMI::Record with list of valid nodes, including information
    // specified by content
    int getNodeList (DMI::Record &list,int content = NL_DEFAULT);

    DMI::Record::Ref state () const;

    // sets forest state from rec. If complete = true,
    // sets complete state, else only overwrites the fields specified in rec
    void setState (DMI::Record::Ref &rec,bool complete = false);

    // Increments specified component of request ID, specified by symdep
    // A running count is maintained for all symdeps
    void incrRequestId (RequestId &rqid,const HIID &symdep);

    // Same for a set of symdeps
    void incrRequestId (RequestId &rqid,const std::vector<HIID> &symdeps)
    {
      for( uint i=0; i<symdeps.size(); i++)
        incrRequestId(rqid,symdeps[i]);
    }

    // Returns the current symdep map
    const SymdepMap & symdeps () const
    { return symdeps_; }

    // Looks up the depmask for a symdep
    int getDependMask (const HIID &symdep) const
    {
      return symdeps().getMask(symdep);
    }

    int getStateDependMask () const
    { return depmask_state_; }

    // returns or sets the default cache policy
    int cachePolicy () const
    { return cache_policy_; }

    void setCachePolicy (int pol)
    { cache_policy_ = pol; }

    // returns or sets the default log policy
    int logPolicy () const
    { return log_policy_; }

    void setLogPolicy (int pol)
    { log_policy_ = pol; }

    // flushes log file, if any is present
    void flushLog ();

    // closes log file, if any is present
    void closeLog ();

    // enables/disables node execution profiling
    bool profilingEnabled () const
    { return profiling_enabled_; }

    void enableProfiling (bool enable)
    { profiling_enabled_ = enable; }

    Thread::Condition & stopFlagCond ()
    { return stop_flag_cond_; }

    // In mt-mode, one thread can hit a breakpoint while the others are
    // still running. To prevent them from running away, we call this
    // function to raise a stop flag. All other nodes hitting this flag
    // will then stop.
    void raiseStopFlag ();

    // Nodes call this to see if another thread is sitting at a breakpoint.
    bool isStopFlagRaised () const
    { return stop_flag_; }

    // Once the user chooses to continue, call this function to clear the
    // stop flag. This will also signal all stopped threads to restart
    void clearStopFlag ();

    // Thread hitting the stop flag call this method to wait for it to
    // clear
    void waitOnStopFlag () const;

    // set a global (forest-wide) breakpoint
    void setBreakpoint (int bpmask,bool single_shot=false);

    // clears global breakpoint(s)
    void clearBreakpoint (int bpmask,bool single_shot=false);


    // these methods are used by nodes to notify of their control state.
    // At debug level 0, we only report state changes involving
    //                   breakpoints and failed results
    // At debug level 1, also post changes to result status
    // At debug level 2 or force_update is true, all state changes are reported
    void newControlStatus (Node &node,int oldst,int newst,bool force_update=false)
    {
      if( !node_status_callback )
        return;
      int changemask = oldst^newst;
      bool result = changemask&Node::CS_RES_MASK;
      bool fail = result && ( (oldst&Node::CS_RES_MASK) == Node::CS_RES_FAIL ||
                              (newst&Node::CS_RES_MASK) == Node::CS_RES_FAIL  );
      if( force_update ||
          changemask && ( debug_level_>1 || fail ||
                          (debug_level_>0 && result ) ||
                          changemask&Node::CS_MASK_BREAKPOINTS ) )
        (*node_status_callback)(node,oldst,newst);
    }

    // called by a node when its breakpoint is hit
    void processBreakpoint (Node &node,int bpmask,bool global);

    // called by a node at any runstate change to check for global
    // breakpoints
    bool checkGlobalBreakpoints (int bpmask)
    {
      if( breakpoints_ss&bpmask )
      {
        breakpoints_ss = 0;
        return true;
      }
      return (breakpoints&bpmask) != 0;
    }

    // set debugging callbacks
    void setDebuggingCallbacks (void (*stat)(Node&,int,int),void (*bp)(Node&,int,bool))
    {
      node_status_callback      = stat;
      node_breakpoint_callback  = bp;
    }

    // set event callback
    void setEventCallback (void (*cb)(const HIID &,const ObjRef &))
    {
      event_callback = cb;
    }

    // posts an event via the callback
    void postEvent (const HIID &type,const ObjRef &data)
    {
      if( event_callback )
        (*event_callback)(type,data);
    }

    void postMessage (const std::string &msg,const HIID &type=HIID(AidMessage));
    void postError   (const std::exception &exc);
    void postError   (const std::string &msg)
    { postMessage(msg,AidError); }

    // writes result of a node to the logger
    void logNodeResult (const Node &node,const Request &req,const Result &res);

    int debugLevel () const
    { return debug_level_; }

    void setDebugLevel (int level)
    { debug_level_ = level; }

    void raiseAbortFlag ()
    { abort_flag_ = true; }

    void clearAbortFlag ()
    { abort_flag_ = false; }

    bool abortFlag () const
    { return abort_flag_; }

    const bool & getAbortFlag () const
    { return abort_flag_; }

    Thread::Mutex & forestMutex () const
    { return forest_mutex_; }

    //##ModelId=3F60697A0078
    LocalDebugContext;

    //##ModelId=400E530501D7
    string sdebug (int=0) const { return getDebugContext().name(); }

  private:
    mutable Thread::Mutex forest_mutex_;

    // forest state management
    DMI::Record & wstate ()
    { return staterec_(); }

    void initDefaultState ();
    void setStateImpl (DMI::Record::Ref &rec);

    mutable DMI::Record::Ref staterec_;

    int breakpoints;
    int breakpoints_ss;

    bool abort_flag_;

    bool stop_flag_;
    Thread::Condition stop_flag_cond_;

    int debug_level_;

    void (*node_status_callback)(Node&,int,int);
    void (*node_breakpoint_callback)(Node&,int,bool);
    void (*event_callback)(const HIID &,const ObjRef &);

    //##ModelId=3F60697903A7
    typedef std::vector<NodeFace::Ref> Repository;
    //##ModelId=3F5F439203E2
    Repository nodes;

    int num_valid_nodes;

    //##ModelId=3F60697A00A3
    static const int RepositoryChunkSize = 8192;

    //##ModelId=3F60697903C1
    typedef hash_map<string,int> NameMap;
    //##ModelId=3F60697A00D5
    NameMap name_map;

    SymdepMap symdeps_;

    //## for incrRequestId, this map keeps track of the current index
    //## for each symdep
    std::map<HIID,int> symdep_counts;

    int depmask_state_;

    // helper function to convert SymdepMap to Record
    void fillSymDeps (DMI::Record &rec,const SymdepMap &map);

    // default cache policy for nodes
    int cache_policy_;

    // default log policy for nodes (see Meq::Node::LOG_POLICY for enums)
    int log_policy_;

    // logger object
    BOIO logger_;
    // name of log file
    string log_filename_;
    // if true, log file will be open in append mode
    bool log_append_;
    // mutex to serialize access to the logger
    Thread::Mutex log_mutex_;

    // is profiling enabled?
    bool profiling_enabled_;
};

} // namespace Meq



#endif

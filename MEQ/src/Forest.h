//#  Forest.h: MeqForest class
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
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
#ifndef MeqSERVER_SRC_FOREST_H_HEADER_INCLUDED_C53FA569
#define MeqSERVER_SRC_FOREST_H_HEADER_INCLUDED_C53FA569

#include <MEQ/Node.h>
#include <MEQ/Request.h>
#include <MEQ/MeqVocabulary.h>
#include <DMI/HashMap.h>
#include <vector>
#include <map>

#pragma aid Create Delete
#pragma aid Axes Symdeps Debug Level Profiling Enabled Cwd

namespace Meq 
{ 
using namespace DMI;

//##ModelId=3F5F21740281
class Forest
{
  public:
    typedef std::map<HIID,int> SymdepMap;
  
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
    Node & create (int &node_index, DMI::Record::Ref &initrec,
                   bool reinitializing=false);
  
    //##ModelId=3F5F5CA300E0
    //##Documentation
    //## Removes the node with the given index.
    int remove (int node_index);
  
    //##ModelId=3F5F5B4F01BD
    //##Documentation
    //## Returns node specified by index
    Node & get (int node_index);
    
    //##ModelId=3F7048570004
    //##Documentation
    //## Returns ref to repository's countedref, specified by index
    const Node::Ref & getRef (int node_index);
  
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
    Node & findNode(const string &name);
    
    //##ModelId=400E530501C2
    int maxNodeIndex () const
    { return nodes.size()-1; }
    
    // fills DMI::Record with list of valid nodes, including information
    // specified by content
    int getNodeList (DMI::Record &list,int content = NL_DEFAULT);
    
    const DMI::Record & state () const
    { return *staterec_; }
    
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
    const SymdepMap & getSymdepMasks () const
    { return symdep_map; }
    
    // Looks up the depmask for a symdep
    int getDependMask (const HIID &symdep) const
    { 
      SymdepMap::const_iterator iter = symdep_map.find(symdep);
      FailWhen(iter==symdep_map.end(),"unknown symdep "+symdep.toString());
      return iter->second;
    }
    
    int getStateDependMask () const
    { return depmask_state_; }
    
    // returns or sets the default cache policy
    int cachePolicy () const
    { return cache_policy_; }
    
    void setCachePolicy (int pol) 
    { cache_policy_ = pol; }
    
    // enables/disables node execution profiling
    bool profilingEnabled () const
    { return profiling_enabled_; }
    
    void enableProfiling (bool enable) 
    { profiling_enabled_ = enable; }
    
    // these methods are used by nodes to notify of their control state, 
    // trip breakpoints, etc.
    void newControlStatus (Node &node,int oldst,int newst)
    {
      if( node_status_callback && debug_level_>0 )
        (*node_status_callback)(node,oldst,newst);
    }

    // called by a node when its breakpoint is hit
    void processBreakpoint (Node &node,int bpmask,bool global)
    {
      if( node_breakpoint_callback )
        (*node_breakpoint_callback)(node,bpmask,global);
    }

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
    
    // sets global breakpoint(s)
    void setBreakpoint (int bpmask,bool single_shot=false)
    {
      if( single_shot )
        breakpoints_ss |= bpmask;
      else
        breakpoints |= bpmask;
    }
    
    // clears global breakpoint(s)
    void clearBreakpoint (int bpmask,bool single_shot=false)
    {
      if( single_shot )
        breakpoints_ss &= ~bpmask;
      else
        breakpoints &= ~bpmask;
    }

    // changes or gets the debug level
    void setDebugLevel (int level)
    { debug_level_ = level; }
    
    int debugLevel () const
    { return debug_level_; }
    
    // set debugging callbacks
    void setDebuggingCallbacks (void (*stat)(Node&,int,int),void (*bp)(Node&,int,bool))
    {
      node_status_callback      = stat;
      node_breakpoint_callback  = bp;
    }

    //##ModelId=3F60697A0078
    LocalDebugContext;
    
    //##ModelId=400E530501D7
    string sdebug (int=0) const { return getDebugContext().name(); }

  private:
    // forest state management
    DMI::Record & wstate ()
    { return staterec_(); }  
  
    void initDefaultState ();
    void setStateImpl (DMI::Record::Ref &rec);
      
    DMI::Record::Ref staterec_;  
      
    int breakpoints;
    int breakpoints_ss;
    
    int debug_level_;
    
    void (*node_status_callback)(Node&,int,int);
    void (*node_breakpoint_callback)(Node&,int,bool);
  
      
    //##ModelId=3F60697903A7
    typedef std::vector<Node::Ref> Repository;
    //##ModelId=3F5F439203E2
    Repository nodes;
    
    int num_valid_nodes;
    
    //##ModelId=3F60697A00A3
    static const int RepositoryChunkSize = 8192;
  
    //##ModelId=3F60697903C1
    typedef hash_map<string,int> NameMap;
    //##ModelId=3F60697A00D5
    NameMap name_map;
    
    typedef std::map<HIID,int> SymdepMap;
    SymdepMap symdep_map;
    
    SymdepMap symdep_counts;
    
    SymdepMap known_symdeps;
    
    int depmask_state_;
    
    // helper function to convert SymdepMap to Record
    void fillSymDeps (DMI::Record &rec,const SymdepMap &map);
    
    // default cache policy for nodes
    int cache_policy_;
    
    // is profiling enabled?
    bool profiling_enabled_;
};

} // namespace Meq



#endif /* MeqSERVER_SRC_NODEREPOSITORY_H_HEADER_INCLUDED_C53FA569 */

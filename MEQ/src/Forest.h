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
#include <MEQ/EventGenerator.h>
#include <vector>
#include <map>

#pragma aid Create Delete

namespace Meq {

//##ModelId=3F5F21740281
class Forest
{
  public:
    typedef enum {
      NL_NODEINDEX = 1,
      NL_NAME      = 2,
      NL_CLASS     = 4,
      NL_CHILDREN  = 8,
          
      NL_DEFAULT   = NL_NODEINDEX|NL_NAME|NL_CLASS,
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
    //## Returns node index.
    const Node::Ref & create (int &node_index, DataRecord::Ref::Xfer &initrec,
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
    
    // fills DataRecord with list of valid nodes, including information
    // specified by content
    int getNodeList (DataRecord &list,int content = NL_DEFAULT);
    
    //##ModelId=3F9937F601A5
    //##Documentation
    //## Assigns ID to request object. WIll assign new ID if the cells
    //## differ from the previous request, otherwise will re-use IDs
    const HIID & assignRequestId (Request &req);
    
    // manage subscriptions to various events
    // "Create" and "Delete" are the only ones known for now
    void addSubscriber    (const HIID &evtype,const EventSlot &slot)
    { getEventGenerator(evtype).addSlot(slot); }
    
    void removeSubscriber (const HIID &evtype,const EventSlot &slot)
    { getEventGenerator(evtype).removeSlot(slot); }
    
    void removeSubscriber (const HIID &evtype,const EventRecepient *recpt)
    { getEventGenerator(evtype).removeSlot(recpt); }

    //##ModelId=3F60697A0078
    LocalDebugContext;
    
    //##ModelId=400E530501D7
    string sdebug (int=0) const { return getDebugContext().name(); }

  private:
    //##ModelId=3F60697903A7
    typedef std::vector<Node::Ref> Repository;
    //##ModelId=3F5F439203E2
    Repository nodes;
    
    int num_valid_nodes;
    
    //##ModelId=3F60697A00A3
    static const int RepositoryChunkSize = 8192;
  
    //##ModelId=3F60697903C1
    typedef std::map<string,int> NameMap;
    //##ModelId=3F60697A00D5
    NameMap name_map;
    
    //##ModelId=400E5305015A
    HIID last_req_id;
    //##ModelId=400E53050170
    Meq::Cells::Ref last_req_cells;
    
    EventGenerator evgen_create;
    EventGenerator evgen_delete;
    
    EventGenerator & getEventGenerator (const HIID &evtype);
    
};

} // namespace Meq



#endif /* MeqSERVER_SRC_NODEREPOSITORY_H_HEADER_INCLUDED_C53FA569 */

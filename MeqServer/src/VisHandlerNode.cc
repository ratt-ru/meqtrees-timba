#include "VisHandlerNode.h"
#include "AID-MeqServer.h"
#include <MEQ/Cells.h>

namespace Meq {

InitDebugContext(VisHandlerNode,"MeqVisHandler");
  
//##ModelId=3F98DAE60319
VisHandlerNode::VisHandlerNode (int nchildren,const HIID *labels,int nmandatory)
 : Node(nchildren,labels,nmandatory),
   data_id(-1)
{}

//##ModelId=3F98DAE60336
void VisHandlerNode::setDataId (int id)    
{ 
  wstate()[FDataId] = data_id = id;
}

//##ModelId=400E5B6E01FA
void VisHandlerNode::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  if( initializing )
  {
    requiresInitField(rec,FStation1Index);
    requiresInitField(rec,FStation2Index);
  }
  else
  {
    protectStateField(rec,FStation1Index);
    protectStateField(rec,FStation2Index);
  }
  Node::setStateImpl(rec,initializing);
}

}

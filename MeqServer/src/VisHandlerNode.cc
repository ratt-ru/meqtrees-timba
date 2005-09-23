#include "VisHandlerNode.h"
#include "AID-MeqServer.h"
#include <MEQ/Cells.h>
#include <VisCube/VisVocabulary.h>

namespace Meq 
{

InitDebugContext(VisHandlerNode,"MeqVisHandler");
  
//##ModelId=3F98DAE60319
VisHandlerNode::VisHandlerNode (int nchildren,const HIID *labels)
 : Node(nchildren,labels),
   data_id(-1)
{
}

//##ModelId=400E5B6E01FA
void VisHandlerNode::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  if( initializing )
  {
    int st1 = rec[FStation1Index];
    int st2 = rec[FStation2Index];
    data_id = VisVocabulary::ifrNumber(st1,st2);
    ifr_id = AtomicID(st1)|AtomicID(st2);
  }
  else
  {
    protectStateField(rec,FStation1Index);
    protectStateField(rec,FStation2Index);
  }
}

}

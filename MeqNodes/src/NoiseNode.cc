#include <MeqNodes/NoiseNode.h>
#include <MEQ/Request.h>
#include <MEQ/Cells.h>

namespace Meq {    

void NoiseNode::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get/init axes parameter
  rec[FAxesIndex].get_vector(axes_,initializing);
}

Vells::Shape NoiseNode::getShape (const Request &req )
{
  const Vells::Shape &reqshape = req.cells().shape();
  Vells::Shape shape = reqshape;
  // if axes are supplied, reset all unspecified dimensions to 1, else use 
  // shape of input cells
  if( !axes_.empty() )
  {
    for( uint i=0; i<shape.size(); i++ )
      shape[i] = 1;
    for( uint i=0; i<axes_.size(); i++ )
      if( i<shape.size() )
        shape[i] = reqshape[i];
  }
  return shape;
}  

};

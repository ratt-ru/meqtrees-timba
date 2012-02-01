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

#include <MeqNodes/NoiseNode.h>
#include <MEQ/Request.h>
#include <MEQ/Cells.h>

namespace Meq {    

NoiseNode::NoiseNode (int nchildren,const HIID *labels,int nmandatory)
: TensorFunction(nchildren,labels,nmandatory)
{
}
  
  
void NoiseNode::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get/init axes parameter
  rec[FAxesIndex].get_vector(axes_,initializing);
  // get/init dims
  rec[FDims].get_vector(dims_,initializing);
}

void NoiseNode::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &res,const Request &request)
{
  TensorFunction::computeResultCells(ref,res,request);
  LoShape reqshape;
  if( request.hasCells() )
  {
    shape_ = reqshape = request.cells().shape();
  }
  else
  {
    shape_.resize(1);
    shape_[0] = 1;
  }
  // if axes are supplied, reset all unspecified dimensions to 1, else use 
  // shape of input cells
  if( !axes_.empty() )
  {
    for( uint i=0; i<shape_.size(); i++ )
      shape_[i] = 1;
    for( uint i=0; i<axes_.size(); i++ )
    {
      uint iax = axes_[i];
      if( iax<shape_.size() && iax<reqshape.size() )
        shape_[iax] = reqshape[iax];
    }
  }
}

LoShape NoiseNode::getResultDims (const vector<const LoShape *> &)
{
  return dims_;
}

void NoiseNode::evaluateTensors (std::vector<Vells> & out,const std::vector<std::vector<const Vells *> > &children)
{
  for( uint i=0; i<out.size(); i++ )
    out[i] = fillNoise(shape_,children);
}

};

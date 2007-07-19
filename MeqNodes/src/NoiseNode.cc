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

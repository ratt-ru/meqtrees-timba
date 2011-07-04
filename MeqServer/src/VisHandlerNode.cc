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
    int st1=0,st2=1;
    rec[FStation1Index].get(st1,initializing);
    rec[FStation2Index].get(st2,initializing);
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

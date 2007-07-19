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

#ifndef MEQSERVER_SRC_PYFUNCTIONNODE_H
#define MEQSERVER_SRC_PYFUNCTIONNODE_H
    
#include <MeqServer/PyNode.h>

#pragma types #Meq::PyFunctionNode

namespace Meq {
  
//##ModelId=3F98DAE503C9
class PyFunctionNode : public PyNode
{
  public:
    PyFunctionNode ();
  
    virtual ~PyFunctionNode ();
    
    //##ModelId=3F98DAE60222
    virtual TypeId objectType() const
    { return TpMeqPyFunctionNode; }
    
    //##ModelId=3F9FF6AA016C
    LocalDebugContext;

  protected:
    //##ModelId=3F9FF6AA0300
    virtual Vells evaluate (const Request &req,const LoShape &shape,const vector<const Vells*>&);
  
    //##ModelId=3F9FF6AA03D2
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
    // "evaluate" method
    OctoPython::PyObjectRef pynode_evaluate_;
    
    // previous request object and its corresponding Python form
    ObjRef prev_request_;
    OctoPython::PyObjectRef py_prev_request_;
};

}

#endif

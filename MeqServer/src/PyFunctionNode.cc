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

#include "PyFunctionNode.h"
#include <MeqServer/MeqPython.h>

namespace Meq {

using namespace OctoPython;
  
InitDebugContext(PyFunctionNode,"MeqPyFunctionNode");

PyFunctionNode::PyFunctionNode()
  : PyNode()
{
}

PyFunctionNode::~PyFunctionNode()
{
}



//##ModelId=3F9918390169
void PyFunctionNode::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
//   PyNode::setStateImpl(rec,initializing);
//   if( initializing )
//   {
//     pynode_evaluate_ = PyObject_GetAttrString(*pynode_obj_,"evaluate");
//     FailWhen(!pynode_evaluate_,"Python-side class does not provide an evaluate() method");
//   }
}

Vells PyFunctionNode::evaluate (const Request &req,const LoShape &,const vector<const Vells*> &pvells)
{
//   // if a new request object shows up, convert it to Python (but just once)
//   if( !prev_request_.valid() ||
//       prev_request_.deref_p() != &( req ) )
//   {
//     prev_request_.attach(req);
//     py_prev_request_  = OctoPython::pyFromDMI(req);
//   }
//   // convert child vells
//   PyObjectRef vells_tuple = PyTuple_New(pvells.size());
//   for( uint i=0; i<pvells.size(); i++ )
//   {
//     PyObjectRef chres;
//     if( pvells[i] )
//       chres = OctoPython::pyFromDMI(*pvells[i]);
//     else
//       chres << Py_None;  // increments ref count
//     PyTuple_SET_ITEM(*vells_tuple,i,chres.steal()); // SET_ITEM steals our ref
//   }
//   // call Python function
//   PyObjectRef args = Py_BuildValue("(OO)",*py_prev_request_,*vells_tuple);
//   FailWhen(!args,"failed to build args tuple");
//   // call evaluate() method
//   PyObjectRef retval = PyObject_CallObject(*pynode_evaluate_,*args);
//   ObjRef objref;
//   if( retval )
//     OctoPython::pyToDMI(objref,*retval);
//   FailWhen(!objref || objref->objectType() != TpMeqVells,
//         "Python-side evaluate() did not return a valid Result object");
//   return objref.as<Vells>();
}

}

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
  PyNode::setStateImpl(rec,initializing);
  if( initializing )
  {
    pynode_evaluate_ = PyObject_GetAttrString(*pynode_obj_,"evaluate");
    FailWhen(!pynode_evaluate_,"Python-side class does not provide an evaluate() method");
  }
}

Vells PyFunctionNode::evaluate (const Request &req,const LoShape &,const vector<const Vells*> &pvells)
{
  // if a new request object shows up, convert it to Python (but just once)
  if( !prev_request_.valid() ||
      prev_request_.deref_p() != &( req ) )
  {
    prev_request_.attach(req);
    py_prev_request_  = OctoPython::pyFromDMI(req);
  }
  // convert child vells
  PyObjectRef vells_tuple = PyTuple_New(pvells.size());
  for( uint i=0; i<pvells.size(); i++ )
  {
    PyObjectRef chres;
    if( pvells[i] )
      chres = OctoPython::pyFromDMI(*pvells[i]);
    else
      chres << Py_None;  // increm,ents ref count
    PyTuple_SET_ITEM(*vells_tuple,i,chres.steal()); // SET_ITEM steals our ref
  }
  // call Python function
  PyObjectRef args = Py_BuildValue("(OO)",*py_prev_request_,*vells_tuple);
  FailWhen(!args,"failed to build args tuple");
  // call evaluate() method
  PyObjectRef retval = PyObject_CallObject(*pynode_evaluate_,*args);
  ObjRef objref;
  if( retval )
    OctoPython::pyToDMI(objref,*retval);
  FailWhen(!objref || objref->objectType() != TpMeqVells,
        "Python-side evaluate() did not return a valid Result object");
  return objref.as<Vells>();
}

}

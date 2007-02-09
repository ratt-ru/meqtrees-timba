#include "PyNode.h"
#include <MeqServer/MeqPython.h>
#include <OCTOPython/OctoPython.h>

namespace Meq {

using namespace OctoPython;
  
InitDebugContext(PyNode,"MeqPyNode");

const HIID FClassName = AidClass|AidName; 
const HIID FModuleName = AidModule|AidName;


PyNode::PyNode()
  : Node()
{
}

PyNode::~PyNode()
{
}



//##ModelId=3F9918390169
void PyNode::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  if( initializing )
  {
    string classname  = rec[FClassName].as<string>(); 
    string modulename = rec[FModuleName].as<string>(""); 
    pynode_obj_ = MeqPython::createPyNode(*this,classname,modulename);
    if( !pynode_obj_ )
    {
      PyErr_Print();
      Throw("Failed to create PyNode object "+modulename+"."+classname);
    }
    // clear errors when fetching these attributes, as they are optional
    pynode_setstate_ = PyObject_GetAttrString(*pynode_obj_,"set_state_impl");
    PyErr_Clear();
    pynode_getresult_ = PyObject_GetAttrString(*pynode_obj_,"get_result");
    PyErr_Clear();
  }
  else
  {
    if( rec[FClassName].exists() or rec[FModuleName].exists() )
      Throw(FClassName.toString()+" or "+FModuleName.toString()+" can only be specified at node init time");
  }
  // call the python object's set_state() method
  if( pynode_setstate_ )
  {
    PyObjectRef staterec = OctoPython::pyFromDMI(rec);
    PyErr_Clear();
    PyObjectRef args = Py_BuildValue("(Oi)",*staterec,int(initializing));
    FailWhen(!args,"failed to build args tuple");
    PyObjectRef val = PyObject_CallObject(*pynode_setstate_,*args);
    if( !val )
    {
      PyErr_Print();
      Throw("Python-side set_state() method failed");
    }
    // now, if the set_state_impl method returned a non-false object,
    // this must be a record of state fields to be merged into 'rec'
    if( PyObject_IsTrue(*val) )
    {
      ObjRef objref;
      OctoPython::pyToDMI(objref,*val);
      const DMI::Record &newrec = objref.as<DMI::Record>();
      rec().merge(newrec,true);
    }
  }
}

//##ModelId=3F9509770277
int PyNode::getResult (Result::Ref &resref, 
                     const std::vector<Result::Ref> &childres,
                     const Request &request,bool)
{
  FailWhen(!pynode_getresult_,"no Python-side get_result() method defined");
  
  // form up Python tuple of child results
  PyObjectRef chres_tuple = PyTuple_New(childres.size());
  for( uint i=0; i<childres.size(); i++ )
  {
    PyObjectRef chres = OctoPython::pyFromDMI(*childres[i]);
    PyTuple_SET_ITEM(*chres_tuple,i,chres.steal()); // SET_ITEM steals our ref
  }
  // convert request
  PyObjectRef pyreq = OctoPython::pyFromDMI(request);
  PyErr_Clear();
  // build argument list
  PyObjectRef args = Py_BuildValue("(OO)",*chres_tuple,*pyreq);
  FailWhen(!args,"failed to build args tuple");
  // call get_result() method
  PyObjectRef retval = PyObject_CallObject(*pynode_getresult_,*args);
  if( !retval )
  {
    PyErr_Print();
    Throw("Python-side get_result() method failed");
  }
  // else extract return value
  // by default we treat retval as a Result object
  PyObject * pyobj_result = *retval;
  int retcode = 0;
  // ...but it can also be a tuple of (Result,retcode)...
  if( PySequence_Check(*retval) && !PyMapping_Check(*retval) )
  {
    if( PySequence_Length(*retval) != 2 )
      Throw("Python-side get_result() returned an ill-formed value");
    if( !PyArg_ParseTuple(*retval,"(Oi)",&pyobj_result,&retcode) )
    {
      PyErr_Print();
      Throw("Python-side get_result() returned an ill-formed value");
    }
  }
  // None corresponds to empty result
  if( pyobj_result == Py_None )
    resref <<= new Result;
  // ...else convert to result object
  else
  {
    ObjRef objref;
    OctoPython::pyToDMI(objref,pyobj_result);
    FailWhen(!objref || objref->objectType() != TpMeqResult,
        "Python-side get_result() did not return a valid Result object");
    resref = objref;
  }
  return retcode;
}


}

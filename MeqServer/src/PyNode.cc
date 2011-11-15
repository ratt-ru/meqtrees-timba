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

#include "PyNode.h"
#include <MeqServer/MeqPython.h>
#include <OCTOPython/OctoPython.h>

namespace Meq {

using namespace OctoPython;

InitDebugContext(PyNodeImpl,"MeqPyNode");

//const HIID FClassName = AidClass|AidName;
const HIID FModuleName = AidModule|AidName;

LOFAR::Exception getPyException ()
{
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  PyObject *etype,*evalue,*etb;
  PyErr_Fetch(&etype,&evalue,&etb); // we get a new ref
  // if NULL, then no error has occurred, return empty list
  if( !etype )
    return LOFAR::Exception("python error has gone missing");
  // convert to string
  PyObjectRef estr = PyObject_Str(evalue);
  // restore & print error indicator (takes away our ref)
  PyErr_Restore(etype,evalue,etb);
  PyErr_Print();
  return LOFAR::Exception(DMI::ExceptionList::Elem(PyString_AsString(*estr)));
}


PyNodeImpl::PyNodeImpl (Node *node)
: pnode_(node)
{
}

string PyNodeImpl::sdebug (int detail,const string &prefix,const char *name) const
{
  return pnode_->sdebug(detail,prefix,name);
}


//##ModelId=3F9918390169
void PyNodeImpl::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  PyThreadBeginTry;
  if( initializing )
  {
    string classname  = rec[FClassName].as<string>();
    string modulename = rec[FModuleName].as<string>("");
    pynode_obj_ = MeqPython::createPyNode(*pnode_,classname,modulename);
    PyFailWhen(!pynode_obj_,"Failed to create PyNode object "+modulename+"."+classname);
    // clear errors when fetching these attributes, as they are optional
    pynode_setstate_ = PyObject_GetAttrString(*pynode_obj_,"set_state_impl");
    PyErr_Clear();
    pynode_getresult_ = PyObject_GetAttrString(*pynode_obj_,"get_result");
    PyErr_Clear();
    pynode_discoverspids_ = PyObject_GetAttrString(*pynode_obj_,"discover_spids");
    PyErr_Clear();
    pynode_processcommand_ = PyObject_GetAttrString(*pynode_obj_,"process_command");
    PyErr_Clear();
    pynode_modifychildreq_ = PyObject_GetAttrString(*pynode_obj_,"modify_child_request");
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
    PyFailWhen(!args,"failed to build args tuple");
    PyObjectRef val = PyObject_CallObject(*pynode_setstate_,*args);
    PyFailWhen(!val,"Python-side set_state() method failed");
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
  PyThreadEndCatch;
}

//##ModelId=3F9509770277
int PyNodeImpl::getResult (Result::Ref &resref,
                           const std::vector<Result::Ref> &childres,
                           const Request &request,bool)
{
  FailWhen(!pynode_getresult_,"no Python-side get_result() method defined");
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  int retcode = 0;
  PyThreadBeginTry;
  // form up Python tuple of arguments
  PyObjectRef args_tuple = PyTuple_New(childres.size()+1);
  // convert request
  PyTuple_SET_ITEM(*args_tuple,0,convertRequest(request)); // SET_ITEM steals the new ref
  // add child results
  for( uint i=0; i<childres.size(); i++ )
  {
    PyObjectRef chres = OctoPython::pyFromDMI(*childres[i]);
    PyTuple_SET_ITEM(*args_tuple,i+1,chres.steal()); // SET_ITEM steals our ref
  }
  // call get_result() method
  PyObjectRef retval = PyObject_CallObject(*pynode_getresult_,*args_tuple);
  PyFailWhen(!retval,"Python-side get_result() method failed");
  // else extract return value
  // by default we treat retval as a Result object
  PyObject * pyobj_result = *retval;
  // ...but it can also be a tuple of (Result,retcode)...
  if( PySequence_Check(*retval) && !PyMapping_Check(*retval) )
  {
    if( PySequence_Length(*retval) != 2 )
      Throw("Python-side get_result() returned an ill-formed value");
    PyFailWhen(!PyArg_ParseTuple(*retval,"(Oi)",&pyobj_result,&retcode),
                "Python-side get_result() returned an ill-formed value");
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
  PyThreadEndCatch;
  return retcode;
}

//##ModelId=3F9509770277
int PyNodeImpl::discoverSpids (Result::Ref &resref,
                           const std::vector<Result::Ref> &childres,
                           const Request &request)
{
  FailWhen(!pynode_discoverspids_,"no Python-side discover_spids() method defined");
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  int retcode = 0;
  PyThreadBeginTry;
  // form up Python tuple of arguments
  PyObjectRef args_tuple = PyTuple_New(childres.size()+1);
  // convert request
  PyTuple_SET_ITEM(*args_tuple,0,convertRequest(request)); // SET_ITEM steals the new ref
  // add child results
  for( uint i=0; i<childres.size(); i++ )
  {
    PyObjectRef chres = OctoPython::pyFromDMI(*childres[i]);
    PyTuple_SET_ITEM(*args_tuple,i+1,chres.steal()); // SET_ITEM steals our ref
  }
  // call discover_spids() method
  PyObjectRef retval = PyObject_CallObject(*pynode_discoverspids_,*args_tuple);
  PyFailWhen(!retval,"Python-side discover_spids() method failed");
  // else extract return value
  // by default we treat retval as a Result object
  PyObject * pyobj_result = *retval;
  // ...but it can also be a tuple of (Result,retcode)...
  if( PySequence_Check(*retval) && !PyMapping_Check(*retval) )
  {
    if( PySequence_Length(*retval) != 2 )
      Throw("Python-side discover_spids() returned an ill-formed value");
    PyFailWhen(!PyArg_ParseTuple(*retval,"(Oi)",&pyobj_result,&retcode),
                "Python-side discover_spids() returned an ill-formed value");
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
        "Python-side discover_spids() did not return a valid Result object");
    resref = objref;
  }
  PyThreadEndCatch;
  return retcode;
}

//##ModelId=3F9509770277
int PyNodeImpl::processCommand (Result::Ref &resref,
                                const HIID &command,
                                DMI::Record::Ref &args,
                                const RequestId &rqid,
                                int verbosity)
{
  if( !pynode_processcommand_ )
    return 0;
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  int retcode = 0;
  PyThreadBeginTry;
  // build argumnent tuple
  PyObjectRef args_tuple = Py_BuildValue("sNNi",
    command.toString().c_str(),
    OctoPython::pyFromRecord(*args),  // new ref, stolen by N
    OctoPython::pyFromHIID(command),  // new ref, stolen by N
    verbosity);
  // call process_command() method
  PyObjectRef retval = PyObject_CallObject(*pynode_processcommand_,*args_tuple);
  PyFailWhen(!retval,"Python-side process_command() method failed");
  // else extract return value -- may be a None, a single int, a single result,
  // or a tuple of (Result,int)
  PyObject * pyobj_result = *retval;
  // None returned
  if( pyobj_result == Py_None )
  {
    retcode = 0;
    pyobj_result = 0;
  }
  // single number returned
  else if( PyNumber_Check(pyobj_result) )
  {
    retcode = PyInt_AsLong(pyobj_result);
    pyobj_result = 0;
  }
  // else can be a sequence of (Result,int)
  else if( PySequence_Check(*retval) && !PyMapping_Check(*retval) )
  {
    if( PySequence_Length(*retval) != 2 )
      Throw("Python-side discover_spids() returned an ill-formed value");
    PyFailWhen(!PyArg_ParseTuple(*retval,"(Oi)",&pyobj_result,&retcode),
                "Python-side discover_spids() returned an ill-formed value");
  }
  // else treat  as result
  // now if we have a result, try to convert
  if( pyobj_result )
  {
    ObjRef objref;
    OctoPython::pyToDMI(objref,pyobj_result);
    FailWhen(!objref || objref->objectType() != TpMeqResult,
        "Python-side discover_spids() did not return a valid Result object");
    resref = objref;
  }
  PyThreadEndCatch;
  return retcode;
}

const Request & PyNodeImpl::modifyChildRequest (Request::Ref &newreq,const Request &req)
{
  FailWhen(!pynode_modifychildreq_,"no Python-side modify_child_request() method defined");
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  PyThreadBeginTry;
  // form up Python tuple of arguments
  PyObjectRef args_tuple = PyTuple_New(1);
  // convert request
  PyTuple_SET_ITEM(*args_tuple,0,convertRequest(req)); // SET_ITEM steals the new ref
  // call modify_child_request() method
  PyObjectRef retval = PyObject_CallObject(*pynode_modifychildreq_,*args_tuple);
  PyFailWhen(!retval,"Python-side modify_child_request() method failed");
  // extract return value
  // if None, then return the old request
  PyObject * pyobj_result = *retval;
  if( pyobj_result == Py_None )
    return req;
  // else treat retval as a Request object
  ObjRef objref;
  OctoPython::pyToDMI(objref,pyobj_result);
  FailWhen(!objref || objref->objectType() != TpMeqRequest,
      "Python-side modify_child_request() did not return a valid Request object");
  newreq.xfer(objref);
  PyThreadEndCatch;
  return *newreq;
}


PyObject * PyNodeImpl::convertRequest (const Request &req)
{
  // if a new request object shows up, convert it to Python, and cache
  // for later reuse
  if( !prev_request_.valid() ||
      prev_request_.deref_p() != &( req ) ||
      prev_request_->id() != req.id() )
  {
    prev_request_.attach(req);
    py_prev_request_  = OctoPython::pyFromDMI(req);
    PyErr_Clear();
  }
  // return new ref
  return py_prev_request_ ? py_prev_request_.new_ref() : 0;
}

PyNode::PyNode()
  : Node(),impl_(this)
{
}

PyNode::~PyNode()
{
}

void PyNode::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  impl_.setStateImpl(rec,initializing);
}


int PyNode::getResult (Result::Ref &resref,
                       const std::vector<Result::Ref> &childres,
                       const Request &request,bool newreq)
{
  return impl_.getResult(resref,childres,request,newreq);
}

int PyNode::discoverSpids (Result::Ref &resref,
                       const std::vector<Result::Ref> &childres,
                       const Request &request)
{
  if( impl_.pynode_discoverspids_ )
    return impl_.discoverSpids(resref,childres,request);
  else
    return Node::discoverSpids(resref,childres,request);
}

int PyNode::processCommand (Result::Ref &resref,
                            const HIID &command,
                            DMI::Record::Ref &args,
                            const RequestId &rqid,
                            int verbosity)
{
  return impl_.processCommand(resref,command,args,rqid,verbosity) |
         Node::processCommand(resref,command,args,rqid,verbosity);
}

int PyNode::pollChildren (Result::Ref &resref,
                          std::vector<Result::Ref> &childres,
                          const Request &req)
{
  if( impl_.pynode_modifychildreq_ )
  {
    Request::Ref newreq;
    return Node::pollChildren(resref,childres,impl_.modifyChildRequest(newreq,req));
  }
  else
    return Node::pollChildren(resref,childres,req);
}


}

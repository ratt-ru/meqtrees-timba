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

#include "PyTensorFuncNode.h"
#include <MeqServer/MeqPython.h>

namespace Meq {

using namespace OctoPython;

PyTensorFuncImpl::PyTensorFuncImpl(Node *pnode)
 : PyNodeImpl(pnode)
{
}

void PyTensorFuncImpl::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request)
{
  Assert(pynode_compute_result_cells_);
  // form up Python tuple of arguments
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  ObjRef objref;
  PyThreadBeginTry;
  PyObjectRef args_tuple = PyTuple_New(childres.size()+1);
  // convert request
  PyObjectRef pyreq = OctoPython::pyFromDMI(request);
  PyErr_Clear();
  PyTuple_SET_ITEM(*args_tuple,0,pyreq.steal()); // SET_ITEM steals our ref
  // add child results
  for( uint i=0; i<childres.size(); i++ )
  {
    PyObjectRef chres = OctoPython::pyFromDMI(*childres[i]);
    PyTuple_SET_ITEM(*args_tuple,i+1,chres.steal()); // SET_ITEM steals our ref
  }
  // call Python method
  PyObjectRef retval = PyObject_CallObject(*pynode_compute_result_cells_,*args_tuple);
  PyFailWhen(!retval,"Python-side compute_result_cells() method failed");
  // convert result to a Cells
  OctoPython::pyToDMI(objref,*retval);
  FailWhen(!objref || objref->objectType() != TpMeqCells,
      "Python-side compute_result_cells() did not return a valid Cells object");
  PyThreadEndCatch;
  ref = objref;
}

LoShape PyTensorFuncImpl::getResultDims (const vector<const LoShape *> &input_dims)
{
  Assert(pynode_get_result_dims_);
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  LoShape resdims;
  PyThreadBeginTry;
  // form up Python tuple of dims
  PyObjectRef dims_tuple = PyTuple_New(input_dims.size());
  for( uint i=0; i<input_dims.size(); i++ )
  {
    const LoShape & dims = *input_dims[i];
    PyObjectRef pydims = PyTuple_New(dims.size());
    for( uint j=0; j<dims.size(); j++ )
      PyTuple_SET_ITEM(*pydims,j,PyInt_FromLong(dims[j]));
    PyTuple_SET_ITEM(*dims_tuple,i,pydims.steal()); // SET_ITEM steals our ref
  }
  // call Python method
  PyObjectRef retval = PyObject_CallObject(*pynode_get_result_dims_,*dims_tuple);
  PyFailWhen(!retval,"Python-side get_result_dims() method failed");
  // convert result to a LoShape
  FailWhen(!PySequence_Check(*retval),
      "Python-side get_result_dims() method must return a sequence of numbers");
  int ndims = PySequence_Length(*retval);
  resdims = LoShape(ndims);
  for( int i=0; i<ndims; i++ )
  {
    PyObjectRef item = PySequence_GetItem(*retval,i);
    resdims[i] = PyInt_AsLong(*item);
    PyCheckError("Python-side get_result_dims() method must return a sequence of numbers");
  }
  PyThreadEndCatch;
  return resdims;
}

void PyTensorFuncImpl::evaluateTensors (std::vector<Vells> & out,
              const std::vector<std::vector<const Vells *> > &args )
{
  Assert(pynode_evaluate_tensors_);
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  PyThreadBeginTry;
// form up Python tuple of argument tuples
  PyObjectRef args_tuple = PyTuple_New(args.size());
  for( uint i=0; i<args.size(); i++ )
  {
    const std::vector<const Vells*> & argvec = args[i];
    PyObjectRef pyargvec = PyTuple_New(argvec.size());
    for( uint j=0; j<argvec.size(); j++ )
    {
      PyObjectRef pyvells = OctoPython::pyFromDMI(*argvec[j]);
      PyTuple_SET_ITEM(*pyargvec,j,pyvells.steal()); // SET_ITEM steals our ref
    }
    PyTuple_SET_ITEM(*args_tuple,i,pyargvec.steal()); // SET_ITEM steals our ref
  }
  // call Python method
  PyObjectRef retval = PyObject_CallObject(*pynode_evaluate_tensors_,*args_tuple);
  PyFailWhen(!retval,"Python-side evaluate_tensors() method failed");
  // convert result to a vector of vells
  FailWhen(!PySequence_Check(*retval),
      "Python-side evaluate_tensors() method must return a sequence of numbers");
  uint nout = PySequence_Length(*retval);
  FailWhen(nout!=out.size(),
      ssprintf("Python-side evaluate_tensors() method returned %d items while %d were expected",nout,out.size()));
  for( uint i=0; i<nout; i++ )
  {
    PyObjectRef item = PySequence_GetItem(*retval,i);
    ObjRef objref;
    OctoPython::pyToDMI(objref,*retval);
    FailWhen(!objref || objref->objectType() != TpMeqVells,
        ssprintf("Python-side evaluate_tensors() method returned a non-Vells at position %d",i));
    out[i] = objref.as<Vells>();
  }
  PyThreadEndCatch;
}

void PyTensorFuncImpl::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Thread::Mutex::Lock lock(MeqPython::python_mutex);
  PyThreadBeginTry;
  PyNodeImpl::setStateImpl(rec,initializing);
  if( initializing )
  {
    pynode_evaluate_tensors_ = PyObject_GetAttrString(*pynode_obj_,"evaluate_tensors");
    PyFailWhen(!pynode_obj_,"Python-side class does not provide an evaluate_tensors() method");
    pynode_compute_result_cells_ =
        PyObject_GetAttrString(*pynode_obj_,"compute_result_cells");
    PyErr_Clear();
    pynode_get_result_dims_ =
        PyObject_GetAttrString(*pynode_obj_,"get_result_dims");
    PyErr_Clear();
  }
  PyThreadEndCatch;
}



PyTensorFuncNode::PyTensorFuncNode()
 : impl_(this)
{
}

PyTensorFuncNode::~PyTensorFuncNode()
{
}

void PyTensorFuncNode::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request)
{
  if( impl_.pynode_compute_result_cells_ )
    return impl_.computeResultCells(ref,childres,request);
  else
    return TensorFunction::computeResultCells(ref,childres,request);
}

LoShape PyTensorFuncNode::getResultDims (const vector<const LoShape *> &input_dims)
{
  if( impl_.pynode_get_result_dims_)
    return impl_.getResultDims(input_dims);
  else
    return TensorFunction::getResultDims(input_dims);
}

void PyTensorFuncNode::evaluateTensors (std::vector<Vells> & out,
              const std::vector<std::vector<const Vells *> > &args )
{
  impl_.evaluateTensors(out,args);
}

void PyTensorFuncNode::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);
  impl_.setStateImpl(rec,initializing);
}


}

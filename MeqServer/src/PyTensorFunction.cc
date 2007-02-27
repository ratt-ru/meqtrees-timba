#include "PyTensorFunction.h"
#include <MeqServer/MeqPython.h>

namespace Meq {

using namespace OctoPython;
  

PyTensorFunction::PyTensorFunction()
 : impl_(this)
{
}

PyTensorFunction::~PyTensorFunction()
{
}



//##ModelId=3F9918390169
void PyTensorFunction::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);
  if( initializing )
  {
    pynode_evaluate_tensors_ = PyObject_GetAttrString(*pynode_obj_,"evaluate_tensors");
    if( !pynode_obj_ )
    {
      PyErr_Print();
      Throw("Python-side class does not provide an evaluate_tensors() method");
    }
    pynode_compute_result_cells_ =
        PyObject_GetAttrString(*pynode_obj_,"compute_result_cells");
    PyErr_Clear();
    pynode_get_result_dims_ = 
        PyObject_GetAttrString(*pynode_obj_,"get_result_dims");
    PyErr_Clear();
  }
}

}

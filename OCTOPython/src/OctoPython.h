#include <Python.h>
#include <OCTOPUSSY/Message.h>
#include <exception>
    
#pragma aidgroup OctoPython
#pragma aid Python
    
namespace OctoPython
{
  // exception thrown by this module
  extern PyObject *PyExc_OctoPythonError;
  
  // Python hiid and message classes
  typedef struct {
    PyObject *hiid,*message;
  } PyClassObjects;
  
  extern PyClassObjects py_class;
  
  // ProxyWP type structure
  extern PyTypeObject PyProxyWPType;
  
  
  // ================== helper functions =====================================
  
  // converts sequence of ints (or any other object supporting iterators)
  // to HIID
  int convertSeqToHIID (HIID &id,PyObject *seq);
  // converts HIID to sequence (from which a real python hiid can be made)
  PyObject * convertHIIDToSeq (const HIID &id);
  
  // ================== data conversion layer ================================
    
  // converts between HIID and Python hiid objects
  PyObject * pyFromHIID (const HIID &id);
  inline int pyToHIID   (HIID &id,PyObject *pyobj)
  { return convertSeqToHIID(id,pyobj); }
  
  // converts between Message and Python message objects
  PyObject * pyFromMessage (const Message &msg);
  int        pyToMessage   (MessageRef &msg,PyObject *pyobj);
  
  
  // ================== error reporting ======================================
    
  // various setError() methods to set up Python exceptions
  inline void setError (PyObject *errobj,const char *msg)
  { PyErr_SetString(errobj,msg); };
  
  inline void setError (PyObject *errobj,const std::exception &exc)
  { PyErr_SetString(errobj,exc.what()); };

  inline void setError (PyObject *errobj,const std::string &str)
  { PyErr_SetString(errobj,str.c_str()); };
  
};

// helper macro: raises Python exception PyExc_"err"Error with the given message;
// issues a return statement with the specified value
#define returnError(value,err,msg) \
  { OctoPython::setError(PyExc_##err##Error,msg); return value; }

// helper macro: returns Py_None
#define returnNone { Py_INCREF(Py_None); return Py_None; }

// helper macro: inserts standard catch-blocks which map C++ exceptions
// to python exceptions of type OctoPython.
// These include a return statement with the specified value.
#define catchStandardErrors(retval) \
  catch ( std::exception &exc ) { /*cerr<<"caught "<<exc.what()<<endl;*/ returnError(retval,OctoPython,exc); } \
  catch ( ... )                 { /*cerr<<"caught unknown exc\n";     */ returnError(retval,OctoPython,"uknown exception"); }

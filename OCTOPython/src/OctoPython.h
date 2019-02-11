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

#ifndef OCTOPYTHON_OCTOPYTHON_H
#define OCTOPYTHON_OCTOPYTHON_H 1
#include <MeqServer/py3compat.h>    
#include <Python.h>
#include <OCTOPUSSY/Message.h>
#include <DMI/Record.h>
#include <DMI/NumArray.h>
#include <DMI/Exception.h>

#include <exception>
    
#pragma aidgroup OctoPython
#pragma aid Python
    
namespace OctoPython
{
  using namespace Octopussy;
  using std::string;
  LocalDebugContext_ns;
  
  
  inline std::string sdebug (int=0) { return "8Python"; }
  
  // -----------------------------------------------------------------------
  // Data conversion functions
  // -----------------------------------------------------------------------
  
  // This is the LazyObjRef type used to store record fields and defer
  // their unpacking until the first time they're accessed
  typedef struct 
  {
      PyObject_HEAD
      DMI::Record::Field field;
      int flags;
  } LazyObjRef;
  
  // error policy for data conversion functions
  typedef enum { EP_THROW=1,EP_RETNULL=2,EP_CONV_ERROR=4,EP_ALL=7,
                 FL_SHAREDATA=8 } ErrorPolicyAndFlags;
  
  // initializes octopython module -- can also be called from elsewhere
  // when embedding the interpreter
  PyObject * initOctoPythonModule ();
  // initializes conversion layer (needed for numarray mostly)
  void initDataConv ();
  
  // converts sequence of ints (or any other object supporting iterators)
  // to HIID
  int convertSeqToHIID (HIID &id,PyObject *seq);
  // converts HIID to sequence (from which a real python hiid can be made)
  // returns _NEW REFERENCE_ to sequence
  PyObject * convertHIIDToSeq (const HIID &id);
  
  // Build Python object from any DMI object
  // Returns _NEW REFERENCE_ to Python object. Errors are handled via one
  // of three policies:
  // EP_THROW: throw an exception (if a Python error is also raised, this 
  //    will be a PythonException, otherwise some other std::exception). 
  // EP_RETNULL: return NULL (and always raise a Python error)
  // EP_CONV_ERROR: return a dmitypes.conv_error instance describing the
  //    conversion error, and clear any Python errors. 
  // Note that unrecoverable errors will be thrown as exceptions regardless
  // of policy (i.e., failure to allocate an object, etc.)
  PyObject * pyFromDMI      (const DMI::BObj &,int flags=EP_THROW);
  
  // Build Python objects from specific DMI objects, return _NEW REFERENCE_.
  // These function follow a EP_THROW error policy.
  PyObject * pyFromRecord   (const DMI::Record &,int flags=0);
  PyObject * pyFromList     (const DMI::List &,int flags=0);
  PyObject * pyFromVec      (const DMI::Vec &,int flags=0);
  PyObject * pyFromArray    (const DMI::NumArray &,int flags=0);
  PyObject * pyFromMessage  (const Message &,int flags=0);
  PyObject * pyFromHIID     (const HIID &);
  // simple helper for std::strings, returns NEW REF
  inline PyObject * pyFromString (const std::string &str)
  { return PyString_FromString(str.c_str()); }
  
  // Build DMI objects from Python objects.
  // Returns 1 on success, or throws an exception on 
  // error (if a Python exception is also raised, this will be a 
  // PythonException, otherwise another std::exception)
  // The input object's ref count is untouched
  int pyToDMI     (ObjRef &objref,PyObject *obj,
                   TypeId objtype=TypeId(0),DMI::Vec *pvec0=0,int pvec_pos=0);
  int pyToRecord  (DMI::Record::Ref &rec,PyObject *pyobj);
  int pyToArray   (DMI::NumArray::Ref &arr,PyObject *pyobj);
  int pyToMessage (Message::Ref &msg,PyObject *pyobj);
  inline int pyToHIID   (HIID &id,PyObject *pyobj)
  { return convertSeqToHIID(id,pyobj); }
  
  // Creates a conversion-error object with the given message
  // If a Python error has been raised, this error is copied into the
  // object and cleared.
  // Will throw a C++ exception if things go really wrong.
  // Returns _NEW REFERENCE_ to Python object. 
  PyObject * pyConvError (const string &msg);
  
  
  
  // -----------------------------------------------------------------------
  // PyObject reference class
  // A wrapper around PyObject * which maintains and cleans up Py_REFs 
  // automatically
  // -----------------------------------------------------------------------
  class PyObjectRef 
  {
    private:
      PyObject *pobj;

    public:
      // A Ref is constructed from a PyObject *.
      // By default, this should be a NEW REFERENCE. If constructed from
      // a borrowed reference, set the second argument to true to have the
      // ref count incremented.
      PyObjectRef (PyObject *p=0,bool incref=false)
      : pobj(p) 
      { if( incref ) Py_XINCREF(pobj); }

      // Copy constructor increments the ref count
      PyObjectRef (const PyObjectRef &other)
      : pobj(other.pobj) 
      { Py_XINCREF(pobj); }
      
      // Assignment decrements old ref, increments new ref count
      PyObjectRef & operator = (const PyObjectRef &other)
      { Py_XDECREF(pobj); pobj = other.pobj; Py_XINCREF(pobj); return *this; }
      
      // Assignment of PyObject * decrements old ref, does not increment
      // new ref. So, only NEW REFERENCES should be assigned. 
      PyObjectRef & operator = (PyObject *p)
      { Py_XDECREF(pobj); pobj = p; return *this; }
      
      // <<, of PyObject * decrements old ref, and increments new ref 
      // new ref. So, only BORROWED REFERENCES should be <<'d. 
      PyObjectRef & operator << (PyObject *p)
      { Py_XDECREF(pobj); pobj = p; Py_XINCREF(pobj); return *this; }
      

      // Destructor decrements the ref count
      ~PyObjectRef ()
      { Py_XDECREF(pobj); }
      
      // detach -- detaches object
      void detach ()
      { Py_XDECREF(pobj); pobj = 0; }
      
      // Ref is true if pointer is valid
      operator bool () const          { return pobj!=0; }
      bool operator ! () const        { return pobj==0; }
      
      // obj() returns PyObject *
      PyObject * obj () const   { return pobj; }
      
      // _obj() returns internal pointer by-ref, use with care
      PyObject * & _obj () { return pobj; }

      // new_ref() increments ref count and returns pointer
      // (useful for calling functions that steal a ref when we want
      // to retain a ref of our own).
      PyObject * new_ref ()     { Py_XINCREF(pobj); return pobj; }

      // steal() returns pointer and sets internal pointer to 0.
      // This is useful for returning a PyObject* from functions
      // that are meant to return a NEW REFERENCE. Also, if you're calling
      // a function that steals a ref and you don't want to retain the object,
      // use this method.
      // Note that if you return a PyObject as ref.steal(), then your
      // function will return a new reference on success, or automatically
      // deallocate the object if an exception is thrown, which is the exact
      // behaviour we want most of the time.
      PyObject * steal ()     { PyObject *p=pobj; pobj=0; return p; }

      // The * and -> operators returns the PyObject *
      // (so you can index into the object via ref->ob_field)
      PyObject * operator * ()   { return pobj; }
      PyObject * operator -> ()  { return pobj; }

      // The ~ operator is equivalent to steal()
      PyObject * operator ~ ()   { return steal(); }

  };

  // -----------------------------------------------------------------------
  // Exceptions and error reporting
  // -----------------------------------------------------------------------
    
  // Various setError() methods to set up Python exceptions
  // These will set up the given Python exception, with the supplied
  // string as data.
  // The first argument is an error object, its ref count does not
  // need to be incremented.
  inline void setError (PyObject *errobj,const char *msg)
  { PyErr_SetString(errobj,msg); };
  
  inline void setError (PyObject *errobj,const std::exception &exc)
  { PyErr_SetString(errobj,exc.what()); };

  inline void setError (PyObject *errobj,const std::string &str)
  { PyErr_SetString(errobj,str.c_str()); };
  
  inline void setError (PyObjectRef &errobj,const char *msg)
  { PyErr_SetString(*errobj,msg); };
  
  inline void setError (PyObjectRef &errobj,const std::exception &exc)
  { PyErr_SetString(*errobj,exc.what()); };

  inline void setError (PyObjectRef &errobj,const std::string &str)
  { PyErr_SetString(*errobj,str.c_str()); };
  
  // PythonException:
  // Throwing a PythonException is the standard way to propagate errors
  // from the Python/C API, via OctoPython and back to Python.
  // This has two constructor forms:
  // PythonException(pyerr,...) will call PyErr_SetString(pyerr,...), thus
  //   raising a Python exception.
  // PythonException(...) will not call anything. This is meant to be thrown
  //   when a Python exception has already been raised elsewhere.
  // Upon catching a PythonException, the caller may always assume that a
  // meaningful Python exception has been raised via a PyErr_ call.
  class PythonException : public LOFAR::Exception
  {
    private:
      static std::string set (PyObject *errobj,const char *msg)
      {
        std::string errstr = std::string(errobj->ob_type->tp_name) + ": " + msg;
        cdebug(2)<<"raising "<<errstr<<std::endl;
        PyErr_SetString(errobj,msg);
        return errstr;
      }
      
    public:
      PythonException(const std::string &msg)
        : LOFAR::Exception(msg)
      { // this should only be called when there's already a PyErr raised!
        Assert(PyErr_Occurred()); 
      }
        
      PythonException (PyObject *errobj,const char *msg)
        : LOFAR::Exception(set(errobj,msg))
      {}
  
      PythonException (PyObject *errobj,const std::exception &exc)
        : LOFAR::Exception(set(errobj,exc.what()))
      {}

      PythonException (PyObject *errobj,const std::string &str)
        : LOFAR::Exception(set(errobj,str.c_str()))
      {}
      
      ~PythonException() throw()
      {}
      
  };
  
  // -----------------------------------------------------------------------
  // Various globals
  // -----------------------------------------------------------------------
  // OctoPython error
  extern PyObjectRef PyExc_OctoPythonError;
  // Data conversion exception
  extern PyObjectRef PyExc_DataConvError;
  
  
  // Python class objects from dmitypes (used as constructors and
  // for asinstance() comparisons)
  typedef struct 
  {
    PyObjectRef hiid,message,record,dmilist,array_class,conv_error,
                dmi_type,dmi_typename,dmi_coerce;
  } DMISymbols;
  extern DMISymbols py_dmisyms;

  // LazyObjRef type structure
  extern PyTypeObject PyLazyObjRefType;
  
  // ProxyWP type structure
  extern PyTypeObject PyProxyWPType;
  
  // ThreadCond type structure
  extern PyTypeObject PyThreadCondType;
  

  
  // these are used in the macros below to save/release thread state.
  // redefine to
  //   #define PyThreadBegin   PyGILState_STATE gilstate = PyGILState_Ensure();
  //   #define PyThreadEnd     PyGILState_Release(gilstate);
  // to support threaded Python in your code
  #define PyThreadBegin
  #define PyThreadEnd

  // throwError() macro
  // Raises Python exception PyExc_"err"Error with the given 
  // message; throws a PythonException exception.
  // Note that if a Python exception is already raised, this prints it and
  // then OVERRIDES it.
  #define throwError(err,msg) \
  { if( PyErr_Occurred() ) PyErr_Print(); \
    throw OctoPython::PythonException(PyExc_##err##Error,msg); }
  
  // throwErrorQuiet() macro
  // Raises Python exception PyExc_"err"Error with the given 
  // message; throws a PythonException exception.
  // Note that if a Python exception is already raised, this OVERRIDES it.
  #define throwErrorQuiet(err,msg) \
    throw OctoPython::PythonException(PyExc_##err##Error,msg)
    
  // throwErrorOpt() macro
  // If a Python exception is already raised, simply throws a PythonException 
  // with message. Otherwise, works just like throwError().
  // This behaviour is actually complementary to throwError():
  // if a Python exception is already raised, this RETAINS it.
  #define throwErrorOpt(err,msg) \
    if( PyErr_Occurred() ) { throw OctoPython::PythonException(msg); } \
    else { throwError(err,msg); }

  // returnError() macro
  // Raises Python exception PyExc_"err"Error with the given 
  // message; issues a return statement with the specified value
  #define returnError(value,err,msg) \
    { OctoPython::setError(PyExc_##err##Error,msg);  PyThreadEnd; return value; }
  
  // catchStandardErrors() macro
  // Inserts standard catch-blocks. All exceptions are caught. A 
  // PythonException indicates that a Python exception has already been raised,
  // so it is basically ignored. All other exceptions cause a Python exception
  // of type OctoPython to be raised.
  // All exceptions result in a return statement with retval.
  #define catchStandardErrors(retval) \
    catch ( std::exception &exc ) \
      { cdebug(2)<<"caught exception: "<<exceptionToString(exc); returnError(retval,OctoPython,exc); } \
    catch ( ... )  \
      { cdebug(2)<<"caught unknown exception\n";  returnError(retval,OctoPython,"unknown exception"); }
      
  #define catchStandardErrors(retval) \
    catch ( std::exception &exc ) \
      { cdebug(2)<<"caught exception: "<<exceptionToString(exc); returnError(retval,OctoPython,exc); } \
    catch ( ... )  \
      { cdebug(2)<<"caught unknown exception\n";  returnError(retval,OctoPython,"unknown exception"); }

  // helper macro: returns a new ref to Py_None
  #define returnNone { Py_INCREF(Py_None); PyThreadEnd; return Py_None; }


};

#endif

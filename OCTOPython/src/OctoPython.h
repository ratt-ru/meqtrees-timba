#include <Python.h>
#include <OCTOPUSSY/Message.h>
#include <DMI/DataRecord.h>
#include <DMI/DataArray.h>

#include <exception>
    
#pragma aidgroup OctoPython
#pragma aid Python
    
namespace OctoPython
{
  using std::string;
  LocalDebugContext_ns;
  inline std::string sdebug (int=0) { return "8Python"; }
  
  // -----------------------------------------------------------------------
  // Various declarations
  // -----------------------------------------------------------------------
  // OctoPython error
  extern PyObject *PyExc_OctoPythonError;
  // Data conversion exception
  extern PyObject *PyExc_DataConvError;
  
  // Python class objects from dmitypes (used as constructors and
  // for asinstance() comparisons)
  typedef struct {
    PyObject *hiid,*message,*record,*srecord,*array_class,*conv_error;
  } PyClassObjects;
  extern PyClassObjects py_class;
  // ProxyWP type structure
  extern PyTypeObject PyProxyWPType;
  
  
  // -----------------------------------------------------------------------
  // Data conversion functions
  // -----------------------------------------------------------------------
  typedef enum { EP_THROW,EP_RETNULL,EP_CONV_ERROR } ErrorPolicy;
  
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
  PyObject * pyFromDMI      (const BlockableObject &,int err_policy=EP_THROW);
  
  // Build Python objects from specific DMI objects, return _NEW REFERENCE_.
  // These function follow a EP_THROW error policy.
  PyObject * pyFromRecord   (const DataRecord &);
  PyObject * pyFromField    (const DataField &);
  PyObject * pyFromArray    (const DataArray &);
  PyObject * pyFromMessage  (const Message &);
  PyObject * pyFromHIID     (const HIID &);
  // simple helper for std::strings
  inline PyObject * pyFromString (const std::string &str)
  { return PyString_FromString(str.c_str()); }
  
  // Build DMI objects from Python objects.
  // Returns 1 on success, or throws an exception on 
  // error (if a Python exception is also raised, this will be a 
  // PythonException, otherwise another std::exception)
  int pyToDMI     (ObjRef &objref,PyObject *obj,int sepos=0,int seqlen=0);
  int pyToRecord  (DataRecord::Ref &msg,PyObject *pyobj);
  int pyToArray   (DataArray::Ref &arr,PyObject *pyobj);
  int pyToMessage (MessageRef &msg,PyObject *pyobj);
  inline int pyToHIID   (HIID &id,PyObject *pyobj)
  { return convertSeqToHIID(id,pyobj); }
  
  // Creates a conversion-error object with the given message
  // If a Python error has been raised, this error is copied into the
  // object and cleared.
  // Will throw a C++ exception if things go really wrong.
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
      // new ref (we assume we're assigning a new ref!)
      PyObjectRef & operator = (PyObject *p)
      { Py_XDECREF(pobj); pobj = p; return *this; }

      // Destructor decrements the ref count
      ~PyObjectRef ()
      { Py_XDECREF(pobj); }

      // Ref is true if pointer is valid
      operator bool () const          { return pobj!=0; }
      bool operator ! () const        { return pobj==0; }
      
      // obj() returns PyObject *
      PyObject * obj () const   { return pobj; }

      // new_ref() increments ref count and returns pointer
      // (useful for calling functions that steal a ref)
      PyObject * new_ref ()     { Py_XINCREF(pobj); return pobj; }

      // steal() returns pointer and sets internal pointer to 0.
      // This is useful for returning a PyObject* from functions
      // that are meant to return a NEW REFERENCE.
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
  inline void setError (PyObject *errobj,const char *msg)
  { PyErr_SetString(errobj,msg); };
  
  inline void setError (PyObject *errobj,const std::exception &exc)
  { PyErr_SetString(errobj,exc.what()); };

  inline void setError (PyObject *errobj,const std::string &str)
  { PyErr_SetString(errobj,str.c_str()); };
  
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
  class PythonException : public std::exception
  {
    private:
      static std::string set (PyObject *errobj,const char *msg)
      {
        std::string errstr = std::string(errobj->ob_type->tp_name) + ": " + msg;
        cdebug(2)<<"raising "<<errstr<<endl;
        PyErr_SetString(errobj,msg);
        return errstr;
      }
        
      std::string message;
      
    public:
      PythonException(const std::string &msg)
        : message(msg)
      { // this should only be called when there's already a PyErr raised!
        Assert(PyErr_Occurred()); 
      }
        
      PythonException (PyObject *errobj,const char *msg)
        : message(set(errobj,msg))
      {}
  
      PythonException (PyObject *errobj,const std::exception &exc)
        : message(set(errobj,exc.what()))
      {}

      PythonException (PyObject *errobj,const std::string &str)
        : message(set(errobj,str.c_str()))
      {}
      
      ~PythonException() throw()
      {}
      
      virtual const char* what() const throw()
      { return message.c_str(); }
  };

  // throwError() macro
  // Raises Python exception PyExc_"err"Error with the given 
  // message; throws a PythonException exception.
  // Note that if a Python exception is already raised, this OVERRIDES it.
  #define throwError(err,msg) \
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
    { OctoPython::setError(PyExc_##err##Error,msg); return value; }
  
  // catchStandardErrors() macro
  // Inserts standard catch-blocks. All exceptions are caught. A 
  // PythonException indicates that a Python exception has already been raised,
  // so it is basically ignored. All other exceptions cause a Python exception
  // of type OctoPython to be raised.
  // All exceptions result in a return statement with retval.
  #define catchStandardErrors(retval) \
    catch ( OctoPython::PythonException &exc ) \
      { cdebug(2)<<"caught python exc: "<<exc.what()<<endl; return retval; } \
    catch ( std::exception &exc ) \
      { cdebug(2)<<"caught "<<exc.what()<<endl; returnError(retval,OctoPython,exc); } \
    catch ( ... )  \
      { cdebug(2)<<"caught unknown exception\n";  returnError(retval,OctoPython,"uknown exception"); }

  // helper macro: returns Py_None
  #define returnNone { Py_INCREF(Py_None); return Py_None; }


};

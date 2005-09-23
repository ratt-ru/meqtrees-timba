#include <MeqServer/MeqServer.h>    
#include "MeqPython.h"

#include <stdio.h>
#include <list>
    
InitDebugContext(MeqPython,"MeqPy");

namespace MeqPython
{
  
using namespace OctoPython;

PyObject * PyExc_MeqServerError;

static bool meq_initialized = false;
static bool python_initialized = false;
static MeqServer *pmqs = 0;

typedef std::list<PyObjectRef> HandlerList; 
static HandlerList header_handlers;
  
extern "C" 
{

// -----------------------------------------------------------------------
// mqexec ()
// -----------------------------------------------------------------------
static PyObject * mqexec (PyObject *, PyObject *args)
{
  char * command;
  PyObject *cmdrec = 0;
  if( !PyArg_ParseTuple(args, "s|O", &command,&cmdrec) )
    return NULL;
  if( !pmqs )
    returnError(NULL,MeqServer,"meqserver not initialized");
  // catch all exceptions below
  try 
  {
    cdebug(3)<<"mqexec: command string is "<<command<<endl;
    HIID cmd(command);
    cdebug(2)<<"mqexec: command is "<<cmd<<endl;
    ObjRef args;
    FailWhen(!pyToDMI(args,cmdrec),"arg conversion failed");
    DMI::Record::Ref retval = pmqs->executeCommand(cmd,args);
    return pyFromDMI(*retval);
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// add_header_handler ()
// -----------------------------------------------------------------------
static PyObject * add_header_handler (PyObject *, PyObject *args)
{
  PyObject *handler = 0;
  if( !PyArg_ParseTuple(args, "O", &handler) )
  if( !PyCallable_Check(handler) )
    returnError(NULL,MeqServer,"meqserver.set_header_handler(): handler not callable");
  header_handlers.push_back(handler);
  returnNone;
}

// -----------------------------------------------------------------------
// clear_header_handlers ()
// -----------------------------------------------------------------------
static PyObject * clear_header_handlers (PyObject *, PyObject *args)
{
  if( !PyArg_ParseTuple(args,"") )
    return NULL;
  header_handlers.clear();
  returnNone;
}

// -----------------------------------------------------------------------
// Module initialization
// -----------------------------------------------------------------------
static PyMethodDef MeqMethods[] = {
    { "mqexec", mqexec, METH_VARARGS, 
             "issues a MeqServer command" },
    { "add_header_handler", add_header_handler, METH_VARARGS, 
             "sets up a handler for visibility headers" },
    { "clear_header_handlers", clear_header_handlers, METH_VARARGS, 
             "removes all handlers for visibility headers" },
    { NULL, NULL, 0, NULL}        /* Sentinel */
};


} // extern "C"

// -----------------------------------------------------------------------
// runFile
// runs a python script
// -----------------------------------------------------------------------
void runFile (MeqServer *pm,const string &filename)
{
  destroyMeqPython();
  initMeqPython(pm);
  FILE *fp = fopen(filename.c_str(),"r");
  FailWhen(!fp,"can't open file: "+filename);
  PyRun_SimpleFile(fp,filename.c_str());
  fclose(fp);
  if( PyErr_Occurred() )
  {
    PyErr_Print();
    Throw("error running python script "+filename);
  }
}

// -----------------------------------------------------------------------
// importModule
// imports a Python module
// -----------------------------------------------------------------------
void importModule (MeqServer *pm,const string &name)
{
  initMeqPython(pm);
  PyObject * mod = PyImport_ImportModule(const_cast<char*>(name.c_str()));
  if( !mod )
  {
    PyErr_Print();
    Throw("import of python module "+name+" failed");
  }
}

// -----------------------------------------------------------------------
// processVisHeader
// processes a visibility header by calling a handler, if set
// -----------------------------------------------------------------------
void processVisHeader (MeqServer *pm,const DMI::Record &headrec)
{
  initMeqPython(pm);
  if( header_handlers.empty() )
    return;
  PyObjectRef pyheadrec = pyFromDMI(headrec);
  FailWhen(!pyheadrec,"failed to convert VisHeader to python");
  PyObjectRef args = Py_BuildValue("(O)",*pyheadrec);
  FailWhen(!args,"failed to build args tuple");
  for( HandlerList::iterator iter = header_handlers.begin();
       iter != header_handlers.end(); iter++ )
  {
    PyObjectRef val = PyObject_CallObject(**iter,*args);
    if( !val )
      PyErr_Print();
  }
}


// -----------------------------------------------------------------------
// initMeqPython
// -----------------------------------------------------------------------
void initMeqPython (MeqServer *mq)
{
  pmqs = mq;
  if( meq_initialized )
    return;
  meq_initialized = true;
  // init Python
  if( !python_initialized )
  {
    Py_Initialize();
    python_initialized = true;
  }
  // import the octopython module to init everything
  PyObject * timbamod = PyImport_ImportModule("Timba");
  if( !timbamod )
  {
    Throw("Python meqserver: import of Timba module failed");
  }
  PyObject * octomod = PyImport_ImportModule("Timba.octopython");
  if( !octomod )
  {
    Throw("Python meqserver: import of octopython module failed");
  }
  
  // register ourselves as a module
  PyObject *module = Py_InitModule3("meqserver", MeqMethods,
            "interface to the MeqServer object");
  if( !module )
  {
    Throw("Python meqserver: module init failed");
  }
  
  PyExc_MeqServerError = PyErr_NewException("meqserver.MeqServer", NULL, NULL);
  Py_INCREF(PyExc_MeqServerError);
  PyModule_AddObject(module,"MeqServerError",PyExc_OctoPythonError);
  
  // drop out on error
  if( PyErr_Occurred() )
    Throw("Python meqserver: module init failed");
}

// -----------------------------------------------------------------------
// destroyMeqPython
// -----------------------------------------------------------------------
void destroyMeqPython ()
{
  if( python_initialized )
  {
    header_handlers.clear();
    Py_Finalize();
    python_initialized = false;
  }
}

} // namespace MeqPython


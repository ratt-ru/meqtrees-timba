#include <MeqServer/MeqServer.h>    
#include "MeqPython.h"

#include <stdio.h>
#include <list>
    
InitDebugContext(MeqPython,"MeqPy");

namespace MeqPython
{
  
using namespace OctoPython;

static bool meq_initialized = false;
static MeqServer *pmqs = 0;

static PyObject 
      *process_init_record,
      *process_vis_header,
      *process_vis_tile,
      *process_vis_footer;
  
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
    returnError(NULL,OctoPython,"meqserver not initialized");
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
// Module initialization
// -----------------------------------------------------------------------
static PyMethodDef MeqMethods[] = {
    { "mqexec", mqexec, METH_VARARGS, 
             "issues a MeqServer command" },
    { NULL, NULL, 0, NULL}        /* Sentinel */
};


} // extern "C"


// -----------------------------------------------------------------------
// callPyFunc
// helper method to call a python function
// -----------------------------------------------------------------------
static PyObjectRef callPyFunc (PyObject *func,const BObj &arg)
{
  PyObjectRef pyarg = pyFromDMI(arg);
  FailWhen(!pyarg,"failed to convert argument to python");
  PyErr_Clear();
  PyObjectRef allargs = Py_BuildValue("(O)",*pyarg);
  FailWhen(!allargs,"failed to build args tuple");
  PyObjectRef val = PyObject_CallObject(func,*allargs);
  if( !val )
    PyErr_Print();
  return val;
}

// -----------------------------------------------------------------------
// processInitRecord
// processes a visibility header by calling a handler, if set
// -----------------------------------------------------------------------
void processInitRecord (const DMI::Record &rec)
{
  if( process_init_record )
  {
    cdebug(1)<<"calling init_record handler"<<endl;
    PyObjectRef res = callPyFunc(process_init_record,rec);
    if( !res )
      Throw("Python meqserver: visheader handler failed");
  }
}

// -----------------------------------------------------------------------
// processVisHeader
// processes a visibility header by calling a handler, if set
// -----------------------------------------------------------------------
void processVisHeader (const DMI::Record &rec)
{
  if( process_vis_header )
  {
    cdebug(1)<<"calling vis_header handler"<<endl;
    PyObjectRef res = callPyFunc(process_vis_header,rec);
    if( !res )
      Throw("Python meqserver: visheader handler failed");
  }
}

// -----------------------------------------------------------------------
// processVisTile
// processes a visibility tile by calling a handler, if set
// -----------------------------------------------------------------------
void processVisTile (const VisCube::VTile &)
{
//// disable for now, since VisTiles have no python representation
//   if( process_vis_tile )
//   {
//     cdebug(1)<<"calling vis_tile handler"<<endl;
//     PyObjectRef res = callPyFunc(process_vis_tile,tile);
//     if( !res )
//       Throw("Python meqserver: vistile handler failed");
//   }
}

// -----------------------------------------------------------------------
// processVisFooter
// processes a visibility footer by calling a handler, if set
// -----------------------------------------------------------------------
void processVisFooter (const DMI::Record &rec)
{
  if( process_vis_footer )
  {
    cdebug(1)<<"calling vis_header handler"<<endl;
    PyObjectRef res = callPyFunc(process_vis_footer,rec);
    if( !res )
      Throw("Python meqserver: visfooter handler failed");
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
  Py_Initialize();
  // register ourselves as a module
  PyObject *module = Py_InitModule3("meqserver_interface", MeqMethods,
            "interface to the MeqServer object");
  if( !module )
  {
    PyErr_Print();
    Throw("Python meqserver: meqserver_interface module init failed");
  }
  
  // import the octopython module to init everything
  PyObject * kernelmod = PyImport_ImportModule("Timba.meqkernel");
  if( !kernelmod )
  {
    PyErr_Print();
    Throw("Python meqserver: import of Timba.meqkernel module failed");
  }
  // get optional handlers
  process_init_record = PyObject_GetAttrString(kernelmod,"process_init");
  PyErr_Clear();
  cdebug(1)<<"init handler is "<<process_init_record<<endl;
  process_vis_header = PyObject_GetAttrString(kernelmod,"process_vis_header");
  PyErr_Clear();
  process_vis_tile   = PyObject_GetAttrString(kernelmod,"process_vis_tile");
  PyErr_Clear();
  process_vis_footer = PyObject_GetAttrString(kernelmod,"process_vis_footer");
  PyErr_Clear();
  cdebug(1)<<"vis handlers are "<<process_vis_header<<" "
      <<process_vis_tile<<" "<<process_vis_footer<<endl;
  
  // set verbosity level
  PyObject *setverbose = PyObject_GetAttrString(kernelmod,"set_verbose");
  PyErr_Clear();
  if( setverbose )
  {
    PyObjectRef val = PyObject_CallFunction(setverbose,"(i)",int(DebugLevel));
    if( PyErr_Occurred() )
      PyErr_Print();
  }
  
  // drop out on error
  if( PyErr_Occurred() )
  {
    cdebug(1)<<"python error, report follows"<<endl;
    PyErr_Print();
    Throw("Python meqserver: module init failed");
  }
}

// -----------------------------------------------------------------------
// destroyMeqPython
// -----------------------------------------------------------------------
void destroyMeqPython ()
{
  if( meq_initialized )
  {
    Py_Finalize();
    meq_initialized = false;
  }
}

} // namespace MeqPython


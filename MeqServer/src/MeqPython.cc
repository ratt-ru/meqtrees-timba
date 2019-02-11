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
#include <MeqServer/py3compat.h>
#include "MeqPython.h"
#include <MeqServer/MeqServer.h>
#include <MeqServer/MeqUtils.h>
#include <MeqServer/PyNode.h>

#include <stdio.h>
#include <list>
#include <DMI/DynamicTypeManager.h>

InitDebugContext(MeqPython,"MeqPy");
namespace MeqPython
{

using namespace OctoPython;


bool use_memprof = false;

static bool meq_initialized = false;
static MeqServer *pmqs = 0;

static PyObject
      *create_pynode,
      *process_init_record,
      *process_vis_header,
      *process_vis_tile,
      *process_vis_footer,
      *force_module_reload;

extern "C" {

  struct module_state {
      PyObject *error;
  };

  #if PY_MAJOR_VERSION >= 3
    #define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
    static int myextension_traverse(PyObject *m, visitproc visit, void *arg) {
      Py_VISIT(GETSTATE(m)->error);
      return 0;
    }

    static int myextension_clear(PyObject *m) {
      Py_CLEAR(GETSTATE(m)->error);
      return 0;
    }
  #else
    #define GETSTATE(m) (&_state)
    static struct module_state _state;
  #endif

}

extern "C"
{

Thread::Mutex python_mutex;


// -----------------------------------------------------------------------
// mqexec ()
// Python method to execute an arbitrary MeqServer command
// -----------------------------------------------------------------------
static PyObject * mqexec (PyObject *, PyObject *args)
{
  char * command;
  PyObject *cmdrec = 0;
  int silent;
  PyThreadBegin;
  if( !PyArg_ParseTuple(args, "s|Oi", &command,&cmdrec,&silent) )
  {
    PyThreadEnd;
    return NULL;
  }
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
    DMI::Record::Ref cmdrec(DMI::ANONWR);
    cmdrec[AidArgs] = args;
    cmdrec[AidSilent] = bool(silent);
    args.detach();
    DMI::Record::Ref retval = pmqs->executeCommand(cmd,cmdrec,false,false); 
    // 1st false = post_reply = do not post reply but return it here
    // 2nd false = wait_for_async_queue = do not wait on queue, since
    //   being invoked from Python, we may be part of the queue anyway
    PyObject *ret = pyFromDMI(*retval);
    PyThreadEnd;
    return ret;
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// get_node_state_field ()
// Python method to access node state
// -----------------------------------------------------------------------
static PyObject * get_node_state_field (PyObject *, PyObject *args)
{
  PyObject * node_baton;
  char * field_str;
  PyThreadBegin;
  if( !PyArg_ParseTuple(args, "Os",&node_baton,&field_str) )
  {
    PyThreadEnd;
    return NULL;
  }
  // catch all exceptions below
  try
  {
    #if PY_MAJOR_VERSION >= 3
      FailWhen(!PyCapsule_CheckExact(node_baton),"get_node_state_field: first argument must be a valid node baton");
      Node * pnode = static_cast<Node*>(PyCapsule_GetPointer(node_baton, nullptr));
    #else
      FailWhen(!PyCObject_Check(node_baton),"get_node_state_field: first argument must be a valid node baton");
      Node * pnode = static_cast<Node*>(PyCObject_AsVoidPtr(node_baton));
    #endif
    
    FailWhen(!pnode,"get_node_state_field: first argument must be a valid node baton");
    HIID field(field_str);
    cdebug(3)<<"get_node_state_field: node '"<<pnode->name()<<" field "<<field<<endl;
    ObjRef ref = pnode->syncState()[field].ref();
    PyObject *ret = pyFromDMI(*ref);
    PyThreadEnd;
    return ret;
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// set_node_state_field ()
// Python method to change node state
// -----------------------------------------------------------------------
PyObject * PyNodeAccessor::set_node_state_field (PyObject *, PyObject *args)
{
  PyObject *node_baton, *value;
  char * field_str;
  PyThreadBegin;
  if( !PyArg_ParseTuple(args, "OsO",&node_baton,&field_str,&value) )
  {
    PyThreadEnd;
    return NULL;
  }
  // catch all exceptions below
  try
  {
    #if PY_MAJOR_VERSION >= 3
      FailWhen(!PyCapsule_CheckExact(node_baton),"set_node_state_field: first argument must be a valid node baton");
      Node * pnode = static_cast<Node*>(PyCapsule_GetPointer(node_baton, nullptr));
    #else
      FailWhen(!PyCObject_Check(node_baton),"set_node_state_field: first argument must be a valid node baton");
      Node * pnode = static_cast<Node*>(PyCObject_AsVoidPtr(node_baton));
    #endif
    FailWhen(!pnode,"set_node_state_field: first argument must be a valid node baton");
    HIID field(field_str);
    cdebug(3)<<"set_node_state_field: node '"<<pnode->name()<<" field "<<field<<endl;
    ObjRef ref;
    pyToDMI(ref,value);
    pnode->wstate()[field].replace() = ref;
    returnNone;
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// set_node_active_symdeps ()
// Python method to change a node's symdeps
// -----------------------------------------------------------------------
PyObject * PyNodeAccessor::set_node_active_symdeps (PyObject *, PyObject *args)
{
  PyObject *node_baton,*symdep_list;
  char * field_str;
  PyThreadBegin;
  if( !PyArg_ParseTuple(args, "OO",&node_baton,&symdep_list) )
  {
    PyThreadEnd;
    return NULL;
  }
  // catch all exceptions below
  try
  {
    #if PY_MAJOR_VERSION >= 3
      FailWhen(!PyCapsule_CheckExact(node_baton),"set_node_active_symdeps: first argument must be a valid node baton");
      Node * pnode = static_cast<Node*>(PyCapsule_GetPointer(node_baton, nullptr));
    #else
      FailWhen(!PyCObject_Check(node_baton),"set_node_active_symdeps: first argument must be a valid node baton");
      Node * pnode = static_cast<Node*>(PyCObject_AsVoidPtr(node_baton));
    #endif
    
    FailWhen(!pnode,"set_node_acrive_symdeps: first argument must be a valid node baton");
    FailWhen(!PySequence_Check(symdep_list),"set_node_active_symdeps: second argument must be a list of symdeps");
    int ndep = PySequence_Length(symdep_list);
    std::vector<HIID> symdeps(ndep);
    for( int i=0; i<ndep; i++ )
    {
      PyObjectRef item = PySequence_GetItem(symdep_list,i);
      symdeps[i] = HIID(PyString_AsString(*item));
      cdebug(3)<<"set_node_active_symdeps: node '"<<pnode->name()<<" symdeps "<<symdeps[i]<<endl;
    }
    pnode->setActiveSymDeps(symdeps);
    returnNone;
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// get_forest_state_field ()
// Python method to access forest state
// -----------------------------------------------------------------------
static PyObject * get_forest_state_field (PyObject *, PyObject *args)
{
  char * field_str;
  PyThreadBegin;
  if( !PyArg_ParseTuple(args, "s",&field_str) )
  {
    PyThreadEnd;
    return NULL;
  }
  if( !pmqs )
    returnError(NULL,OctoPython,"meqserver not initialized");
  // catch all exceptions below
  try
  {
    HIID field(field_str);
    cdebug(3)<<"get_forest_state_field: field "<<field<<endl;
    ObjRef ref = pmqs->getForest().state()[field].ref();
    PyObject *ret = pyFromDMI(*ref);
    PyThreadEnd;
    return ret;
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
    { "get_node_state_field", get_node_state_field, METH_VARARGS,
             "returns one field of the node state" },
    { "set_node_state_field", PyNodeAccessor::set_node_state_field, METH_VARARGS,
             "sets one field of the node state" },
    { "get_forest_state_field", get_forest_state_field, METH_VARARGS,
             "returns one field of the forest state" },
    { "set_node_active_symdeps", PyNodeAccessor::set_node_active_symdeps, METH_VARARGS,
             "sets the current set of a node's symdeps" },
    { NULL, NULL, 0, NULL}        /* Sentinel */
};


} // extern "C"


// -----------------------------------------------------------------------
// callPyFunc
// helper method to call a python function
// -----------------------------------------------------------------------
static PyObjectRef callPyFunc (PyObject *func,const BObj &arg)
{
  Thread::Mutex::Lock lock(python_mutex);
  PyThreadBegin;
  PyObjectRef pyarg = pyFromDMI(arg);
  FailWhen(!pyarg,"failed to convert argument to python");
  PyErr_Clear();
  PyObjectRef allargs = Py_BuildValue("(O)",*pyarg);
  FailWhen(!allargs,"failed to build args tuple");
  PyObjectRef val = PyObject_CallObject(func,*allargs);
  if( !val && PyErr_Occurred() )
    PyErr_Print();
  PyThreadEnd;
  return val;
}

// -----------------------------------------------------------------------
// createPyNode
// creates a PyNode object associated with the given C++ PyNode
// -----------------------------------------------------------------------
PyObjectRef createPyNode (Meq::Node &pynode,const string &classname,const string &modulename)
{
  Thread::Mutex::Lock lock(python_mutex);
  #if PY_MAJOR_VERSION >= 3
    PyObjectRef pynode_baton = PyCapsule_New(&pynode, nullptr, [](_object* x){if (x != 0) {delete x;}});
  #else
    PyObjectRef pynode_baton = PyCObject_FromVoidPtr(&pynode,0);
  #endif
  PyObjectRef args = Py_BuildValue("(Osss)",*pynode_baton,pynode.name().c_str(),classname.c_str(),modulename.c_str());
  FailWhen(!args,"failed to build args tuple");
  PyObjectRef val = PyObject_CallObject(create_pynode,*args);
  if( !val )
  {
    string err;
    if( PyErr_Occurred() )
    {
      PyObject *type,*value,*tb;
      PyErr_Fetch(&type,&value,&tb);
      PyObjectRef pystr = PyObject_Str(value); 
      PyErr_Restore(type,value,tb);
      PyErr_Print();
      // get string content
      err = string(": ") + PyString_AsString(*pystr);
    }
    Throw("failed to create PyNode of class "+classname+" ("+modulename+")"+err);
  }
  return val;
}


// -----------------------------------------------------------------------
// testConversion
// testing method to find bugs in the conversion layer -- converts BObj
// to python object, then throws away the python object
// -----------------------------------------------------------------------
void testConversion (const BObj &arg)
{
  // built new object via a BlockSet
  BlockSet blockset;
  arg.toBlock(blockset);
  ObjRef newobj = DynamicTypeManager::construct(0,blockset);
  PyObjectRef pyarg = pyFromDMI(*newobj);
  pyarg.detach();
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
    PyThreadBegin;
    bool res = callPyFunc(process_init_record,rec);
    PyThreadEnd;
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
    PyThreadBegin;
    bool res = callPyFunc(process_vis_header,rec);
    PyThreadEnd;
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
    PyThreadBegin;
    bool res = callPyFunc(process_vis_footer,rec);
    PyThreadEnd;
    if( !res )
      Throw("Python meqserver: visfooter handler failed");
  }
}

// -----------------------------------------------------------------------
// forceModuleReload
// forces all modules imported by meqkernel.py to be reloaded
// next time they are accessed
// -----------------------------------------------------------------------
void forceModuleReload ()
{
  Thread::Mutex::Lock lock(python_mutex);
  cdebug(1)<<"calling force_module_reload()"<<endl;
  PyThreadBegin;
  PyObjectRef res = PyObject_CallObject(force_module_reload,NULL);
  if( PyErr_Occurred() )
    PyErr_Print();
  PyThreadEnd;
}


// -----------------------------------------------------------------------
// initMeqPython
// -----------------------------------------------------------------------
#if PY_MAJOR_VERSION >= 3
    #define initMeqPython PyInit_MeqPython
    PyMODINIT_FUNC PyInit_MeqPython(MeqServer *mq)
#else
    PyMODINIT_FUNC initMeqPython (MeqServer *mq)
#endif
{
  #define INITERROR return NULL;
  PyObject *module = nullptr;
  pmqs = mq;
  if( meq_initialized )
    INITERROR
  meq_initialized = true;
  // init Python threads -- this acquires the GIL
  PyEval_InitThreads();
  Py_Initialize();
  PyThreadBegin;
  // release GIL in exception handler
  try
  {
    // import memory profiler, if asked to
    if( use_memprof )
    {
      PyObject * mprofmod = PyImport_ImportModule("memory_profiler");
      cerr<<"initialized memory_profiler"<<endl;
    }

    // import the octopython and mequtils modules -- we don't want Python to pull
    // in the shared lib, but would rather use our (linked in) version. Doing
    // anything else causes problems with C++ RTTI symbols.
    OctoPython::initOctoPythonModule();
    MeqUtils::initMeqUtilsModule();

    // register ourselves as a module
    #if PY_MAJOR_VERSION < 3
      module = Py_InitModule3("meqserver_interface", MeqMethods,
                "interface to the MeqServer object");
    #else
      static struct PyModuleDef meqserver_interface =
        {
          PyModuleDef_HEAD_INIT,
          "meqserver_interface", /* name of module */
          "interface to the MeqServer object\n", /* module documentation, may be NULL */
          sizeof(struct module_state),  /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
          MeqMethods,
          NULL,
          myextension_traverse,
          myextension_clear,
          NULL
        };
      module = PyModule_Create(&meqserver_interface);
    #endif
    if( !module ) {
      Throw("Py_InitModule3(\"meqpython\") failed");
      INITERROR;
    }
    struct module_state *st = GETSTATE(module);
    st->error = PyErr_NewException("meqpython.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

    PyObject * kernelmod = PyImport_ImportModule("Timba.meqkernel");
    if( !kernelmod )
    {
      PyErr_Print();
      Throw("Python meqserver: import of Timba.meqkernel module failed");
    }
    create_pynode        = PyObject_GetAttrString(kernelmod,"create_pynode");
    if( PyErr_Occurred() )
      PyErr_Print();
      Throw("create_pynode failed");
    if( !create_pynode )
      Throw("Timba.meqkernel.create_pynode not found");
    force_module_reload  = PyObject_GetAttrString(kernelmod,"force_module_reload");
    if( PyErr_Occurred() )
      PyErr_Print();
    if( !force_module_reload )
      Throw("Timba.meqkernel.force_module_reload not found");

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
  // save thread state and release the GIL before exiting (since we acquired it with PyEval_InitThreads() above)
  catch( std::exception &exc )
  {
    PyThreadEnd;
    PyEval_SaveThread();
    Py_FatalError(exc.what());
    #if PY_MAJOR_VERSION >= 3
      return NULL;
    #endif
  }
  PyGILState_Release(gilstate);
  PyEval_SaveThread();
  #if PY_MAJOR_VERSION >= 3
    return module;
  #endif
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


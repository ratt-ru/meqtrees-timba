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

static bool meq_initialized = false;
static MeqServer *pmqs = 0;

static PyObject
      *create_pynode,
      *process_init_record,
      *process_vis_header,
      *process_vis_tile,
      *process_vis_footer,
      *force_module_reload;

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
  if( !PyArg_ParseTuple(args, "s|Oi", &command,&cmdrec,&silent) )
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
    DMI::Record::Ref cmdrec(DMI::ANONWR);
    cmdrec[AidArgs] = args;
    cmdrec[AidSilent] = bool(silent);
    args.detach();
    DMI::Record::Ref retval = pmqs->executeCommand(cmd,cmdrec,false); // false=do not post reply but return it here
    return pyFromDMI(*retval);
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
  if( !PyArg_ParseTuple(args, "Os",&node_baton,&field_str) )
    return NULL;
  // catch all exceptions below
  try
  {
    FailWhen(!PyCObject_Check(node_baton),"get_node_state_field: first argument must be a valid node baton");
    Node * pnode = static_cast<Node*>(PyCObject_AsVoidPtr(node_baton));
    FailWhen(!pnode,"get_node_state_field: first argument must be a valid node baton");
    HIID field(field_str);
    cdebug(3)<<"get_node_state_field: node '"<<pnode->name()<<" field "<<field<<endl;
    ObjRef ref = pnode->syncState()[field].ref();
    return pyFromDMI(*ref);
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
  if( !PyArg_ParseTuple(args, "OsO",&node_baton,&field_str,&value) )
    return NULL;
  // catch all exceptions below
  try
  {
    FailWhen(!PyCObject_Check(node_baton),"set_node_state_field: first argument must be a valid node baton");
    Node * pnode = static_cast<Node*>(PyCObject_AsVoidPtr(node_baton));
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
  if( !PyArg_ParseTuple(args, "OO",&node_baton,&symdep_list) )
    return NULL;
  // catch all exceptions below
  try
  {
    FailWhen(!PyCObject_Check(node_baton),"set_node_active_symdeps: first argument must be a valid node baton");
    Node * pnode = static_cast<Node*>(PyCObject_AsVoidPtr(node_baton));
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
  if( !PyArg_ParseTuple(args, "s",&field_str) )
    return NULL;
  if( !pmqs )
    returnError(NULL,OctoPython,"meqserver not initialized");
  // catch all exceptions below
  try
  {
    HIID field(field_str);
    cdebug(3)<<"get_forest_state_field: field "<<field<<endl;
    ObjRef ref = pmqs->getForest().state()[field].ref();
    return pyFromDMI(*ref);
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
  PyObjectRef pyarg = pyFromDMI(arg);
  FailWhen(!pyarg,"failed to convert argument to python");
  PyErr_Clear();
  PyObjectRef allargs = Py_BuildValue("(O)",*pyarg);
  FailWhen(!allargs,"failed to build args tuple");
  PyObjectRef val = PyObject_CallObject(func,*allargs);
  if( !val && PyErr_Occurred() )
    PyErr_Print();
  return val;
}

// -----------------------------------------------------------------------
// createPyNode
// creates a PyNode object associated with the given C++ PyNode
// -----------------------------------------------------------------------
PyObjectRef createPyNode (Meq::Node &pynode,const string &classname,const string &modulename)
{
  Thread::Mutex::Lock lock(python_mutex);
  PyObjectRef pynode_baton = PyCObject_FromVoidPtr(&pynode,0);
  PyObjectRef args = Py_BuildValue("(Osss)",*pynode_baton,pynode.name().c_str(),classname.c_str(),modulename.c_str());
  FailWhen(!args,"failed to build args tuple");
  PyObjectRef val = PyObject_CallObject(create_pynode,*args);
  if( !val )
  {
    if( PyErr_Occurred() )
      PyErr_Print();
    Throw("failed to create PyNode of class "+classname+" ("+modulename+")");
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
// forceModuleReload
// forces all modules imported by meqkernel.py to be reloaded
// next time they are accessed
// -----------------------------------------------------------------------
void forceModuleReload ()
{
  Thread::Mutex::Lock lock(python_mutex);
  cdebug(1)<<"calling force_module_reload()"<<endl;
  PyObjectRef res = PyObject_CallObject(force_module_reload,NULL);
  if( PyErr_Occurred() )
    PyErr_Print();
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

  // import the octopython and mequtils modules -- we don't want Python to pull
  // in the shared lib, but would rather use our (linked in) version. Doing
  // anything else causes problems with C++ RTTI symbols.
  OctoPython::initOctoPythonModule();
  MeqUtils::initMeqUtilsModule();

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

  create_pynode        = PyObject_GetAttrString(kernelmod,"create_pynode");
  if( PyErr_Occurred() )
    PyErr_Print();
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


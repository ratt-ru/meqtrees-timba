#include <DMI/Global-Registry.h>
#include <OCTOPUSSY/Octopussy.h>
#include <OCTOPUSSY/OctopussyConfig.h>
#include <OCTOPUSSY/ReflectorWP.h>
#include "OctoPython.h"

InitDebugContext(OctoPython,"OctoPython");

namespace OctoPython
{

static int dum = aidRegistry_Global();

PyObject * PyExc_OctoPythonError;
PyObject * PyExc_DataConvError;


extern "C" {
  
// -----------------------------------------------------------------------
// set_debug
// -----------------------------------------------------------------------
static PyObject * set_debug (PyObject *, PyObject *args)
{
  // two arguments
  char *name;
  int level;
  if( !PyArg_ParseTuple(args, "si", &name,&level) )
    return NULL;
  
  Debug::setLevel(name,level);
  
  // return None
  returnNone;
}

// -----------------------------------------------------------------------
// string_to_hiid
// -----------------------------------------------------------------------
static PyObject * string_to_hiid (PyObject *, PyObject *args)
{
  char *str;
  char *sepset = ".";
  if( !PyArg_ParseTuple(args, "s|s", &str,&sepset) )
    return NULL;
  HIID id;
  try
  {
    return convertHIIDToSeq(HIID(str,0,sepset));
  }
  catchStandardErrors(NULL);
}
  
// -----------------------------------------------------------------------
// hiid_to_string
// -----------------------------------------------------------------------
static PyObject * hiid_to_string (PyObject *, PyObject *args)
{
  PyObject *list;
  char sep = '.';
  if( !PyArg_ParseTuple(args, "O|c", &list,&sep) )
    return NULL;
  HIID id;
  try
  {
    convertSeqToHIID(id,list);
  }
  catchStandardErrors(NULL);
  
  return PyString_FromString(id.toString(sep).c_str());
}

// -----------------------------------------------------------------------
// hiid_matches
// -----------------------------------------------------------------------
static PyObject * hiid_matches (PyObject *, PyObject *args)
{
  PyObject *l1,*l2;
  if( !PyArg_ParseTuple(args, "OO", &l1,&l2) )
    return NULL;
  bool match;
  try
  {
    HIID id1,id2;
    convertSeqToHIID(id1,l1);
    convertSeqToHIID(id2,l2);
    match = id1.matches(id2);
  }
  catchStandardErrors(NULL);
  
  return PyInt_FromLong(match);
}

static bool octopussy_initialized = false;
  
// -----------------------------------------------------------------------
// init_octopussy ()
// -----------------------------------------------------------------------
static PyObject * init_octopussy (PyObject *, PyObject *args)
{
  int start_gateways;

  if( !PyArg_ParseTuple(args, "i", &start_gateways) )
    return NULL;
  if( octopussy_initialized )
    returnError(NULL,OctoPython,"octopussy already initialized");
  // catch all exceptions below
  try 
  {
    cdebug(1)<<"=================== initializing OCTOPUSSY =====================\n";
    const char * argv[] = { "octopython" };
    OctopussyConfig::initGlobal(1,argv);
    Octopussy::init(start_gateways);
  }
  catchStandardErrors(NULL);
  octopussy_initialized = true;
  returnNone;
}

// -----------------------------------------------------------------------
// start_octopussy ()
// -----------------------------------------------------------------------
static PyObject * start_octopussy (PyObject *, PyObject *args)
{
  int wait_start;
  Thread::ThrID thread_id;
  if( !PyArg_ParseTuple(args, "i", &wait_start) )
    return NULL;
  if( !octopussy_initialized )
    returnError(NULL,OctoPython,"octopussy not initialized, call init first");
  // catch all exceptions below
  try 
  {
    cdebug(1)<<"=================== starting OCTOPUSSY thread =================\n";
    thread_id = Octopussy::initThread(wait_start);
    // unblock the SIGALRM signal in Python's thread
    // (Dispatcher::start() normally blocks it)
    Thread::signalMask(SIG_UNBLOCK,SIGALRM);
  }
  catchStandardErrors(NULL);
  
  return Py_BuildValue("i",int(thread_id));
}

// -----------------------------------------------------------------------
// stop_octopussy ()
// -----------------------------------------------------------------------
static PyObject * stop_octopussy (PyObject *, PyObject *args)
{
  if( !PyArg_ParseTuple(args,"") )
    return NULL;
  // catch all exceptions below
  try 
  {
    cout<<"=================== stopping OCTOPUSSY ========================\n";
    Octopussy::stopThread();
  }
  catchStandardErrors(NULL);
  
  returnNone;
};  

// -----------------------------------------------------------------------
// start_reflector ()
// -----------------------------------------------------------------------
static PyObject * start_reflector (PyObject *, PyObject *args)
{
  char *wpid = 0;
  if( !PyArg_ParseTuple(args,"|s",wpid) )
    return NULL;
  // catch all exceptions below
  try 
  {
    if( !Octopussy::isRunning() )
      returnError(NULL,OctoPython,"OCTOPUSSY not initialized");
    AtomicID wpc = wpid ? AtomicID(wpid) : AidReflectorWP;
    WPRef wpref;
    wpref <<= new ReflectorWP(wpc);
    MsgAddress addr = Octopussy::dispatcher().attach(wpref);
    // Get and return address
    cdebug(2)<<"started ReflectorWP: "<<addr<<endl;
    return pyFromHIID(addr);
  }
  catchStandardErrors(NULL);
};  


// -----------------------------------------------------------------------
// Module initialization
// -----------------------------------------------------------------------
static PyMethodDef OctoMethods[] = {
    { "set_debug", set_debug, METH_VARARGS, 
                    "sets a debug level" },
    { "init", init_octopussy, METH_VARARGS, 
                    "initializes OCTOPUSSY" },
    { "start", start_octopussy, METH_VARARGS, 
                    "starts OCTOPUSSY thread (and event loop)" },
    { "stop", stop_octopussy, METH_VARARGS, 
                    "stops current OCTOPUSSY thread" },
    { "str_to_hiid", string_to_hiid, METH_VARARGS, 
                    "converts string to hiid-compatible tuple" },
    { "hiid_to_str", hiid_to_string, METH_VARARGS, 
                    "converts hiid-type sequence to string" },
    { "hiid_matches", hiid_matches, METH_VARARGS, 
                    "tests if two hiids match" },
    { "start_reflector",start_reflector,METH_VARARGS,
                    "starts a RelectorWP (usually for testing)" },
        
    { NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initoctopython ()
{
  Debug::Context::initialize();
  
  // init proxywp type
  if( PyType_Ready(&PyProxyWPType) < 0 ||
      PyType_Ready(&PyThreadCondType) < 0 )
    return;
  
  // init the module
  PyObject *module = Py_InitModule3("octopython", OctoMethods,
        "C++ support module for octopussy.py");
  if( !module )
    return;
  
  // init the DataConversion layer
  initDataConv();
  
  // add types
  PyObject * proxy_type = (PyObject *)&PyProxyWPType;
  Py_INCREF(proxy_type);
  PyModule_AddObject(module, "proxy_wp", proxy_type);
  
  PyObject * tc_type = (PyObject *)&PyThreadCondType;
  Py_INCREF(tc_type);
  PyModule_AddObject(module, "thread_condition", tc_type);
  
  // get references to class objects from dmitypes
  PyObject * dmimod = PyImport_ImportModule("dmitypes");
  if( !dmimod )
  {
    Py_FatalError("octopython init error: import dmitypes failed");
    return;
  }
  PyObject * dmidict = PyModule_GetDict(dmimod);
  if( !dmidict )
  {
    Py_FatalError("octopython init error: can't access dmitypes dict");
    return;
  }
  
  #define GetConstructor(cls) \
    if( ! ( py_class.cls = PyDict_GetItemString(dmidict,#cls) ) ) \
      { Py_FatalError("octopython: name dmitypes." #cls " not found"); return; } \
    Py_INCREF(py_class.cls);
  
  GetConstructor(hiid);
  GetConstructor(message);
  GetConstructor(record);
  GetConstructor(srecord);
  GetConstructor(array_class);
  GetConstructor(conv_error);
  
  // register an exception object
  PyExc_OctoPythonError = PyErr_NewException("octopython.OctoPythonError", NULL, NULL);
  PyExc_DataConvError = PyErr_NewException("octopython.DataConvError", NULL, NULL);
  Py_INCREF(PyExc_OctoPythonError);
  Py_INCREF(PyExc_DataConvError);
  PyModule_AddObject(module, "OctoPythonError", PyExc_OctoPythonError);
  PyModule_AddObject(module, "DataConvError", PyExc_DataConvError);
  
  // build AID dictionaries
  PyObject * aid_map = PyDict_New(),
           * aid_rmap = PyDict_New();
  Py_INCREF(aid_map);
  Py_INCREF(aid_rmap);
  const AtomicID::Registry::Map &map = AtomicID::getRegistryMap();
  AtomicID::Registry::Map::const_iterator iter = map.begin();
  for( ; iter != map.end(); iter++ )
  {
    PyObject * aidint = PyInt_FromLong(iter->first);
    PyObject * aidstr = PyString_FromString(iter->second.c_str());
    PyDict_SetItem(aid_map,aidint,aidstr);
    PyDict_SetItem(aid_rmap,aidstr,aidint);
  }
  // add AID dicts to module's symbols
  PyModule_AddObject(module,"aid_map",aid_map);
  PyModule_AddObject(module,"aid_rmap",aid_rmap);
  
  // drop out on error
  if( PyErr_Occurred() )
    Py_FatalError("can't initialize module octopython");
}


} // extern "C"

} // namesapce OctoPython


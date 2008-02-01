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

#include <OCTOPUSSY/Octopussy.h>
#include <DMI/Global-Registry.h>
#include <OCTOPUSSY/OctopussyConfig.h>
#include <OCTOPUSSY/GWClientWP.h>
#include <OCTOPUSSY/GWServerWP.h>
#include <OCTOPUSSY/ReflectorWP.h>
#include "OctoPython.h"

InitDebugContext(OctoPython,"OctoPython");

namespace OctoPython
{

static int dum = aidRegistry_Global();

PyObjectRef PyExc_OctoPythonError;
PyObjectRef PyExc_DataConvError;

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
    return convertHIIDToSeq(HIID(str,true,sepset));  // return NEW REF
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
  
  return PyString_FromString(id.toString(sep).c_str()); // return NEW REF
}

// -----------------------------------------------------------------------
// hiid_matches
// -----------------------------------------------------------------------
static PyObject * hiid_matches (PyObject *, PyObject *args)
{
  PyObject *l1,*l2;
  if( !PyArg_ParseTuple(args, "OO", &l1,&l2) )  // ref count not increased
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
  
  return PyInt_FromLong(match); // returns NEW REF
}

static bool octopussy_initialized = false;
  
// -----------------------------------------------------------------------
// init_octopussy ()
// -----------------------------------------------------------------------
static PyObject * init_octopussy (PyObject *, PyObject *args)
{
  int client = 0,tcp_port = -1;
  char * local_sock = 0;

  if( !PyArg_ParseTuple(args,"|iis",&client,&tcp_port,&local_sock) )
    return NULL;
  if( octopussy_initialized )
    returnError(NULL,OctoPython,"octopussy already initialized");
  // catch all exceptions below
  try 
  {
    cdebug(1)<<"=================== initializing OCTOPUSSY =====================\n";
    const char * argv[] = { "octopython" };
    OctopussyConfig::initGlobal(1,argv);
    Octopussy::init(false);  // start_gw=false, we init our own below:
    if( client )
      Octopussy::dispatcher().attach(new Octopussy::GWClientWP);
    if( tcp_port >= 0 )
      Octopussy::dispatcher().attach(new Octopussy::GWServerWP(tcp_port));
    if( local_sock )
      Octopussy::dispatcher().attach(new Octopussy::GWServerWP(local_sock,-1));
    
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
  
  return Py_BuildValue("i",int(thread_id)); // return NEW REF
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
// get_server_ports()
// -----------------------------------------------------------------------
static PyObject * get_server_ports (PyObject *, PyObject *)
{
  // catch all exceptions below
  try 
  {
    int port = Octopussy::GWServerWP::getGlobalPort();
    std::string sock = Octopussy::GWServerWP::getGlobalSocket();
    return Py_BuildValue("(is)",port,sock.c_str());
  }
  catchStandardErrors(NULL);
  
  returnNone;
}  

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
    { "get_server_ports", get_server_ports, METH_NOARGS, 
                "returns tuple of (port,socket), corresponding to the current OCTOPUSSY "
                "TCP server port (0 if none) and local server socket ('' if none)." },
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


// -----------------------------------------------------------------------
// initoctopython
// standard entrypoint called by Python when loading the module from an .so
// -----------------------------------------------------------------------
PyMODINIT_FUNC initoctopython ()
{
  Debug::Context::initialize();
  try
  {
    initOctoPythonModule();
  }
  catch (std::exception &exc)
  {
    Py_FatalError(exc.what());
  }
}


} // extern "C"


// -----------------------------------------------------------------------
// initOctoPythonModule
// initializes and registers the module. This function can be called
// from the standard initoctopython() above (when loading module as an
// .so), or directly, when using an embedded interpreter.
// Errors are thrown as exceptions
// -----------------------------------------------------------------------
void initOctoPythonModule ()
{
  // init datatypes
  if( PyType_Ready(&PyProxyWPType) < 0 ||
      PyType_Ready(&PyThreadCondType) < 0 ||
      PyType_Ready(&PyLazyObjRefType) )
    Throw("failed to register octopython datatypes");
  
  // init the module
  PyObject *module = Py_InitModule3("octopython", OctoMethods,
        "C++ support module for octopussy.py");
  if( !module )
    Throw("Py_InitModule3(\"octopython\") failed");
  
  // init the DataConversion layer
  initDataConv();
  
  // add types
  PyModule_AddObject(module, "proxy_wp",(PyObject *)&PyProxyWPType); // steals ref
  PyModule_AddObject(module, "thread_condition",(PyObject *)&PyThreadCondType); // steals ref
  PyModule_AddObject(module, "lazy_objref",(PyObject *)&PyLazyObjRefType); // steals ref
  
  PyObject * timbamod = PyImport_ImportModule("Timba");  // returns new ref
  // since AddObject steals a ref, increment the counter
  Py_INCREF(module);
  PyModule_AddObject(timbamod,"octopython",module);
  
  if( !timbamod )
  {
    PyErr_Print();
    Throw("octopython init error: import of Timba module failed");
  }
  PyObject * dmimod = PyImport_ImportModule("Timba.dmi"); // returns new ref
  if( !dmimod )
  {
    PyErr_Print();
    Throw("octopython init error: import of Timba.dmi module failed");
  }
  PyObject * dmidict = PyModule_GetDict(dmimod); // borrowed ref
  if( !dmidict )
  {
    Throw("octopython init error: can't access Timba.dmi module dict");
  }
  
  // PyDict_GetItemString returns borrowed ref, so increment ref count
  #define GetSym(cls) \
    if( ! ( py_dmisyms.cls << PyDict_GetItemString(dmidict,#cls) ) ) \
      { Throw("octopython: symbol dmi." #cls " not found"); }
  
  GetSym(hiid);
  GetSym(message);
  GetSym(record);
  GetSym(dmilist);
  GetSym(array_class);
  GetSym(conv_error);
  GetSym(dmi_type);
  GetSym(dmi_typename);
  GetSym(dmi_coerce);
  
  #undef GetSym
  
  // register an exception object
  // returns new reference, so assign directly
  PyExc_OctoPythonError = PyErr_NewException("octopython.OctoPythonError", NULL, NULL);
  PyExc_DataConvError = PyErr_NewException("octopython.DataConvError", NULL, NULL);
  // AddObject steals a ref, so pass in a new one
  PyModule_AddObject(module, "OctoPythonError", PyExc_OctoPythonError.new_ref());
  PyModule_AddObject(module, "DataConvError", PyExc_DataConvError.new_ref());
  
  // build AID dictionaries
  // _New() returns new ref
  PyObjectRef aid_map(PyDict_New()),aid_rmap(PyDict_New());
  const AtomicID::Registry::Map &map = AtomicID::getRegistryMap();
  AtomicID::Registry::Map::const_iterator iter = map.begin();
  for( ; iter != map.end(); iter++ )
  {
    // new refs returned, so assign
    PyObjectRef aidint(PyInt_FromLong(iter->first));
    PyObjectRef aidstr(PyString_FromString(iter->second.c_str()));
    // SetItem does not steal a ref but increments ref counts
    PyDict_SetItem(*aid_map,*aidint,*aidstr);
    PyDict_SetItem(*aid_rmap,*aidstr,*aidint);
  }
  // add AID dicts to module's symbols
  PyModule_AddObject(module,"aid_map",~aid_map);  // steals ref
  PyModule_AddObject(module,"aid_rmap",~aid_rmap); // steals ref
  
  // drop out on error
  if( PyErr_Occurred() )
  {
    PyErr_Print();
    Throw("can't initialize module octopython");
  }
}




} // namespace OctoPython


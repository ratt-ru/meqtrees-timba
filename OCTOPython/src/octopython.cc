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
// start_octopussy ()
// -----------------------------------------------------------------------
static PyObject * start_octopussy (PyObject *, PyObject *args)
{
  int start_gateways,wait_start;
  Thread::ThrID thread_id;

  if( !PyArg_ParseTuple(args, "ii", &start_gateways,&wait_start) )
    return NULL;
  // catch all exceptions below
  try 
  {
    cout<<"=================== initializing OCTOPUSSY =====================\n";
    const char * argv[] = { "octopython" };
    OctopussyConfig::initGlobal(1,argv);
    Octopussy::init(start_gateways);
    cout<<"=================== starting OCTOPUSSY thread =================\n";
    thread_id = Octopussy::initThread(wait_start);
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
    { "start", start_octopussy, METH_VARARGS, 
                    "starts an OCTOPUSSY thread" },
    { "stop", stop_octopussy, METH_VARARGS, 
                    "stops current OCTOPUSSY thread" },
    { "str_to_hiid", string_to_hiid, METH_VARARGS, 
                    "converts string to hiid-compatible tuple" },
    { "hiid_to_str", hiid_to_string, METH_VARARGS, 
                    "converts hiid-type sequence to string" },
    { "start_reflector",start_reflector,METH_VARARGS,
                    "starts a RelectorWP (usually for testing)" },
        
    { NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initoctopython_c ()
{
  Debug::Context::initialize();
  
  // init proxywp type
  if( PyType_Ready(&PyProxyWPType) < 0)
    return;
  
  // init the module
  PyObject *module = Py_InitModule3("octopython_c", OctoMethods,
        "C++ support module for octopussy.py");
  if( !module )
    return;
  
  // init the DataConversion layer
  initDataConv();
  
  // add type
  PyObject * proxy_type = (PyObject *)&PyProxyWPType;
  Py_INCREF(proxy_type);
  PyModule_AddObject(module, "proxy_wp", proxy_type);
//  PyObject_SetAttrString(proxy_type,"testattr",PyInt_FromLong(123));
  
  // get references to class objects from dmitypes
  PyObject * dmimod = PyImport_ImportModule("dmitypes");
  if( !dmimod )
  {
    Py_FatalError("octopython_c init error: import dmitypes failed");
    return;
  }
  PyObject * dmidict = PyModule_GetDict(dmimod);
  if( !dmidict )
  {
    Py_FatalError("octopython_c init error: can't access dmitypes dict");
    return;
  }
  
  #define GetConstructor(cls) \
    if( ! ( py_class.cls = PyDict_GetItemString(dmidict,#cls) ) ) \
      { Py_FatalError("octopython_c: name dmitypes." #cls " not found"); return; } \
    Py_INCREF(py_class.cls);
  
  GetConstructor(hiid);
  GetConstructor(message);
  GetConstructor(record);
  GetConstructor(srecord);
  GetConstructor(array_class);
  GetConstructor(conv_error);
  
  // register an exception object
  PyExc_OctoPythonError = PyErr_NewException("octopython_c.OctoPythonError", NULL, NULL);
  PyExc_DataConvError = PyErr_NewException("octopython_c.DataConvError", NULL, NULL);
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
    Py_FatalError("can't initialize module octopython_c");
}


} // extern "C"

} // namesapce OctoPython

/*

#include <AppUtils/VisRepeater.h>
#include <MeqServer/MeqServer.h>
#include <MeqServer/AID-MeqServer.h>

typedef std::vector<string> StrVec;
typedef StrVec::iterator SVI;
typedef StrVec::const_iterator SVCI;

using namespace MSVisAgent;
using namespace OctoAgent;
using namespace AppControlAgentVocabulary;

bool setupApp (ApplicationBase::Ref &app,const string &str)
{
  if( str.length() < 6 )
    return False;
  string name = str.substr(0,5);
  string spec = str.substr(5);
  // select application based on spec string
  AtomicID wpclass;
  if( name == "-meq:" )
  {
    cout<<"=================== creating MeqServer =-==================\n";
    app <<= new Meq::MeqServer;
    wpclass = AidMeqServer;
  }
  else if( name == "-rpt:" )
  {
    cout<<"=================== creating repeater =====================\n";
    app <<= new VisRepeater;
    wpclass = AidRepeater;
  }
  else 
    return False;
  
  // split spec string at ":" character
  StrVec specs;
  uint ipos = 0, len = spec.length();
  while( ipos < len )
  {
    uint ipos1 = spec.find(':',ipos);
    if( ipos1 == string::npos )
      ipos1 = len;
    specs.push_back(spec.substr(ipos,ipos1-ipos));
    ipos = ipos1 + 1;
  }
  // print it out
  cout<<"=== app spec: ";
  for( uint i=0; i<specs.size(); i++ )
      cout<<"\""<<specs[i]<<"\" ";
  cout<<endl;
  FailWhen(specs.size() != 3,"invalid app spec: "+spec);
  
  // initialize parameter record
  DataRecord::Ref recref;
  DataRecord &rec = recref <<= new DataRecord;
  // init errors will be thrown as exceptions
  rec[FThrowError] = True;
  // setup control agent for delayed initialization
  rec[AidControl] <<= new DataRecord;
  rec[AidControl][FDelayInit] = True;
  rec[AidControl][FEventMapIn] <<= new DataRecord;
  rec[AidControl][FEventMapIn][FDefaultPrefix] = HIID(specs[2])|AidIn;
  rec[AidControl][FEventMapOut] <<= new DataRecord;
  rec[AidControl][FEventMapOut][FDefaultPrefix] = HIID(specs[2])|AidOut;

  // create agents
  OctoAgent::EventMultiplexer::Ref mux;
    mux <<= new OctoAgent::EventMultiplexer(wpclass);
  // input agent
  VisAgent::InputAgent::Ref in;
  if( specs[0] == "M" )
    in <<= new VisAgent::InputAgent(new MSVisAgent::MSInputSink,DMI::ANONWR);
  else if( specs[0] == "B" )
    in <<= new VisAgent::InputAgent(new BOIOSink,DMI::ANONWR);
  else if( specs[0] == "O" )
    in <<= new VisAgent::InputAgent(mux().newSink());
  else
    Throw("invalid input type: "+spec[0]);
  // output agent
  VisAgent::OutputAgent::Ref out;
  if( specs[1] == "M" )
    out <<= new VisAgent::OutputAgent(new MSVisAgent::MSOutputSink,DMI::ANONWR);
  else if( specs[1] == "B" )
    out <<= new VisAgent::OutputAgent(new BOIOSink,DMI::ANONWR);
  else if( specs[1] == "O" )
    out <<= new VisAgent::OutputAgent(mux().newSink());
  else
    Throw("invalid output type: "+spec[1]);
  // control agent
  AppControlAgent::Ref control;
  control <<= new AppControlAgent(mux().newSink());
  // attach flags to non-octopussy agents
  if( specs[0] != "O" )
    in().attach(mux().eventFlag());
  if( specs[1] != "O" )
    out().attach(mux().eventFlag());
  // attach agents to app and mux to OCTOPUSSY
  app()<<in<<out<<control;
  Octopussy::dispatcher().attach(mux,DMI::WRITE);
  // preinitialize control
  control().preinit(recref);
  
  return True;
}




*/

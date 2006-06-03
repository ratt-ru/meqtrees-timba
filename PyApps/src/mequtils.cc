#include <OCTOPUSSY/Octopussy.h>
#include <OCTOPython/OctoPython.h>
#include <MEQ/Axis.h>
// #include <AppAgent/BOIOSink.h>
// #include <MSVisAgent/MSInputSink.h>
// #include <MSVisAgent/MSOutputSink.h>
// #include <OctoAgent/EventMultiplexer.h>
// #include <AppUtils/VisRepeater.h>
// #include <MeqServer/MeqServer.h>
// #include <MeqServer/AID-MeqServer.h>
// 
// using namespace MSVisAgent;
// using namespace OctoAgent;
// using namespace AppControlAgentVocabulary;

using namespace OctoPython;

namespace PyAppLauncher
{
LocalDebugContext_ns;
inline std::string sdebug (int=0) { return "PyApp"; }

//std::vector<ApplicationBase::Ref> apps;
// std::vector<Thread::ThrID> app_threads;

const char appname_meqserver[] = "meqserver";
const char appname_repeater[] = "repeater";

static int dum = aidRegistry_Meq();

static PyObject * reap_apps (PyObject *, PyObject *)
{
//   if( !PyArg_ParseTuple(args,"") )
//     return NULL;
//   for( uint i=0; i<app_threads.size(); i++ )
//   {
//     app_threads[i].join();
//     apps[i].detach();
//   }
//   apps.clear();
//   app_threads.clear();
  
  returnNone;
}


static PyObject * launch_app (PyObject *, PyObject *)
{
  returnError(NULL,OctoPython,"launch_app currently disabled");
//     
//   char *appname;
//   char inagent,outagent;
//   PyObject *controlrec;
//   
//   if( !PyArg_ParseTuple(args,"sccO",&appname,&inagent,&outagent,&controlrec) )
//     return NULL;
//   inagent = toupper(inagent);
//   outagent = toupper(outagent);
//  
//   if( !Octopussy::isRunning() )
//     returnError(NULL,OctoPython,"OCTOPUSSY not initialized");
//   
//   Thread::ThrID thrid;
//   
//   try
//   {
//     ApplicationBase::Ref app;
//     // select application based on spec string
//     string name(appname);
//     AtomicID wpclass;
//     cdebug(1)<<"launch_app "<<name<<"("<<inagent<<outagent<<")\n";
//     if( name == appname_meqserver )
//     {
//       cdebug(1)<<"launching a MeqServer\n";
//       app <<= new Meq::MeqServer;
//       wpclass = AidMeqServer;
//     }
//     else if( name == appname_repeater )
//     {
//       cdebug(1)<<"launching a Repeater\n";
//       app <<= new VisRepeater;
//       wpclass = AidRepeater;
//     }
//     else 
//       returnError(NULL,Value,"unknown app name");
// 
//     // initialize parameter record
//     DataRecord::Ref recref;
//     if( pyToRecord(recref,controlrec)<=0 )
//       returnError(NULL,Value,"error converting control record");
//       
//     // create agents
//     OctoAgent::EventMultiplexer::Ref mux;
//       mux <<= new OctoAgent::EventMultiplexer(wpclass);
//     // input agent
//     VisAgent::InputAgent::Ref in;
//     switch( inagent )
//     {
//       case 'M':
//         in <<= new VisAgent::InputAgent(new MSVisAgent::MSInputSink,DMI::ANONWR);
//         break;
//       case 'B':
//         in <<= new VisAgent::InputAgent(new BOIOSink,DMI::ANONWR);
//         break;
//       case 'O':
//         in <<= new VisAgent::InputAgent(mux().newSink());
//         break;
//       default:
//         returnError(NULL,Value,"illegal input agent specifier");
//     }
//     // output agent
//     VisAgent::OutputAgent::Ref out;
//     switch( outagent )
//     {
//       case 'M':
//         out <<= new VisAgent::OutputAgent(new MSVisAgent::MSOutputSink,DMI::ANONWR);
//         break;
//       case 'B':
//         out <<= new VisAgent::OutputAgent(new BOIOSink,DMI::ANONWR);
//         break;
//       case 'O':
//         out <<= new VisAgent::OutputAgent(mux().newSink());
//         break;
//       default:
//         returnError(NULL,Value,"illegal output agent specifier");
//     }
//     // control agent
//     AppControlAgent::Ref control;
//     control <<= new AppControlAgent(mux().newSink());
//     // attach flags to non-octopussy agents
//     if( inagent != 'O' )
//       in().attach(mux().eventFlag());
//     if( outagent != 'O' )
//       out().attach(mux().eventFlag());
//     // attach agents to app and mux to OCTOPUSSY
//     app()<<in<<out<<control;
//     Octopussy::dispatcher().attach(mux,DMI::WRITE);
//     // preinitialize control
//     control().preinit(recref);
//     
//     // launch app thread
//     thrid = app().runThread(true);
//     
//     apps.push_back(app);
//     app_threads.push_back(thrid);
//   }
//   catchStandardErrors(NULL);
//   
//   return PyInt_FromLong(thrid);
}

static PyObject * set_axis_list (PyObject *, PyObject *args)
{
  PyObject * axislist;
  // ref count of object is not increased, so do not attach ref
  if( !PyArg_ParseTuple(args,"O",&axislist) )
    return NULL;

  try
  {
    // make sure argument is a sequence
    if( !PySequence_Check(axislist) )
      returnError(NULL,Type,"sequence of axis ids expected");

    // convert to vector of HIIDs
    int naxis = PySequence_Length(axislist);
    if( naxis > Meq::Axis::MaxAxis )
      returnError(NULL,Value,"too many axis ids specified");

    std::vector<HIID> axis_map(naxis);

    for( int i=0; i<naxis; i++ )
    {
      PyObjectRef item = PySequence_GetItem(axislist,i);
      PyObjectRef itemstr = PyObject_Str(*item);
      // null HIIDs are represented as "(null)", which doesn't convert
      // to HIID. Just in case, catch all conversion errors and use a null id
      HIID id;
      try         { id = HIID(PyString_AsString(*itemstr)); }
      catch(...)  { id.clear(); }
      axis_map[i] = id;
    }
    // now set the axis map
    Meq::Axis::setAxisMap(axis_map);
  }
  catchStandardErrors(NULL);
  
  returnNone;
}

  
// -----------------------------------------------------------------------
// Module initialization
// -----------------------------------------------------------------------
static PyMethodDef AppMethods[] = {
    { "launch_app",launch_app,METH_VARARGS,
          "starts an application thread" },
    { "reap_apps",reap_apps,METH_VARARGS,
          "waits for all application threads to finish" },
    { "set_axis_list",set_axis_list,METH_VARARGS,
          "changes the axis list" },
    { NULL, NULL, 0, NULL} };       /* Sentinel */
  
extern "C" 
{    
    
PyMODINIT_FUNC initmequtils ()
{
  Debug::Context::initialize();
  
  // init the module
  PyObject *module = Py_InitModule3("mequtils", AppMethods,
        "various utilities for python-side meqkernel support");
  if( !module )
    return;
  
  PyObject *octomod = PyImport_ImportModule("Timba.octopython");
  if( !octomod )
  {
    Py_FatalError("unable to import Timba.octopython");
    return;
  }
  
  // register an exception object
  PyObject *applist = Py_BuildValue("(ss)",appname_meqserver,appname_repeater);
  PyModule_AddObject(module, "application_names", applist);
  
  // drop out on error
  if( PyErr_Occurred() )
    Py_FatalError("can't initialize module octopython");
}


} // extern "C"

} // namespace PyAppLauncher

InitDebugContext(PyAppLauncher,"PyApp");



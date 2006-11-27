#include <OCTOPython/OctoPython.h>
#include <MEQ/Axis.h>
    
namespace MeqUtils
{
using namespace OctoPython;

LocalDebugContext_ns;
inline std::string sdebug (int=0) { return "MeqUtils"; }

static int dum = aidRegistry_Meq();

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
static PyMethodDef MeqUtilMethods[] = {
    { "set_axis_list",set_axis_list,METH_VARARGS,
          "changes the axis list" },
    { NULL, NULL, 0, NULL} };       /* Sentinel */

        
void initMeqUtilsModule ()
{
  Debug::Context::initialize();
  
  // init the module
  PyObject *module = Py_InitModule3("mequtils",MeqUtilMethods,
        "various utilities for python-side meqkernel support");
  if( !module )
    Throw("Py_InitModule3(\"mequtils\") failed");
  
  PyObjectRef timbamod = PyImport_ImportModule("Timba");  
  PyModule_AddObject(*timbamod,"mequtils",module);
  
  // drop out on error
  if( PyErr_Occurred() )
    Throw("can't initialize module mequtils");
}
  

extern "C" 
{    
    
PyMODINIT_FUNC initmequtils ()
{
  Debug::Context::initialize();
  
  try
  {
    initMeqUtilsModule();
  }
  catch( std::exception &exc )
  {
    Py_FatalError(exc.what());
  }
}


} // extern "C"


} // namespace MeqUtils

InitDebugContext(MeqUtils,"MeqUtils");



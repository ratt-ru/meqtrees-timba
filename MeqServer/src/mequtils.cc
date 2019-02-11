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

#include <OCTOPython/OctoPython.h>
#include <MEQ/Axis.h>
#include <DMI/BOIO.h>
#include <ctype.h>

namespace MeqUtils
{
using namespace OctoPython;

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

LocalDebugContext_ns;
inline std::string sdebug (int=0) { return "MeqUtils"; }

static int dum = aidRegistry_Meq();

static PyObject * get_axis_number (PyObject *, PyObject *args)
{
  PyObject * axis_id;
  // ref count of object is not increased, so do not attach ref
  if( !PyArg_ParseTuple(args,"O",&axis_id) )
    return NULL;
  try
  {
    // convert ID to string, then to HIID
    HIID id;
    if( PyString_Check(axis_id) )
      id = HIID(PyString_AsString(axis_id));
    else
    {
      PyObjectRef objstr(PyObject_Str(axis_id));
      id = HIID(PyString_AsString(*objstr));
    }
    // look up in map
    int iaxis = Meq::Axis::axis(id);
    return PyInt_FromLong(iaxis);
  }
  catchStandardErrors(NULL);
  returnNone;
}

static PyObject * add_axis (PyObject *, PyObject *args)
{
  PyObject * axis_id;
  // ref count of object is not increased, so do not attach ref
  if( !PyArg_ParseTuple(args,"O",&axis_id) )
    return NULL;
  try
  {
    // convert ID to string, then to HIID
    HIID id;
    if( PyString_Check(axis_id) )
      id = HIID(PyString_AsString(axis_id));
    else
    {
      PyObjectRef objstr(PyObject_Str(axis_id));
      id = HIID(PyString_AsString(*objstr));
    }
    // look up in map
    Meq::Axis::addAxis(id);
    returnNone;
  }
  catchStandardErrors(NULL);
  returnNone;
}


static PyObject * get_axis_id (PyObject *, PyObject *args)
{
  int axis_num;
  // ref count of object is not increased, so do not attach ref
  if( !PyArg_ParseTuple(args,"i",&axis_num) )
    return NULL;
  try
  {
    const HIID & id = Meq::Axis::axisId(axis_num);
    string str = id.toString('_');
    for( int i=0; i<str.length(); i++ )
      str[i] = tolower(str[i]);
    return PyString_FromString(str.c_str());
  }
  catchStandardErrors(NULL);
  returnNone;
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

#if PY_MAJOR_VERSION >= 3
  static void deleteBoioObject (_object *ptr)
  {
    if( ptr )
      delete ptr;
  }
#else
  static void deleteBoioObject (void *ptr)
  {
    BOIO *pboio = static_cast<BOIO*>(ptr);
    if( pboio )
      delete pboio;
  }
#endif

static PyObject * open_boio (PyObject *, PyObject *args)
{
  char * filename;
  if( !PyArg_ParseTuple(args,"s",&filename) )
    return NULL;

  try
  {
    // create BOIO object
    BOIO *pboio = new BOIO(filename);
    // return as a PyCObject
    #if PY_MAJOR_VERSION >= 3
      return PyCapsule_New(pboio, nullptr, deleteBoioObject);
    #else
      return PyCObject_FromVoidPtr(pboio, deleteBoioObject);
    #endif
  }
  catchStandardErrors(NULL);

  returnNone;
}

static PyObject * read_boio (PyObject *, PyObject *args)
{
  PyObject * pyboio;
  // ref count of object is not increased, so do not attach ref
  if( !PyArg_ParseTuple(args,"O",&pyboio) )
    return NULL;

  try
  {
    // extract pointer to BOIO object
    #if PY_MAJOR_VERSION >= 3
      FailWhen(!PyCapsule_CheckExact(pyboio),"argument is not a valid boio object");
      BOIO *pboio = static_cast<BOIO*>(PyCapsule_GetPointer(pyboio, nullptr));
    #else
      FailWhen(!PyCObject_Check(pyboio),"argument is not a valid boio object");
      BOIO *pboio = static_cast<BOIO*>(PyCObject_AsVoidPtr(pyboio));
    #endif
    
    FailWhen(!pboio,"argument is not a valid boio object");
    // read next entry
    ObjRef entry;
    if( !pboio->readAny(entry) )
      returnNone;
    return pyFromDMI(*entry);
  }
  catchStandardErrors(NULL);

  returnNone;
}



// -----------------------------------------------------------------------
// Module initialization
// -----------------------------------------------------------------------
static PyMethodDef MeqUtilMethods[] = {
    { "get_axis_number",get_axis_number,METH_VARARGS,
          "returns axis associated with given ID" },
    { "get_axis_id",get_axis_id,METH_VARARGS,
          "returns axis ID for given axis number" },
    { "set_axis_list",set_axis_list,METH_VARARGS,
          "changes the axis list" },
    { "add_axis",add_axis,METH_VARARGS,
          "adds an axis definition" },
    { "open_boio",open_boio,METH_VARARGS,
          "opens a BOIO file for reading" },
    { "read_boio",read_boio,METH_VARARGS,
          "reads one entry from BOIO file, returns None at end of file" },
    { NULL, NULL, 0, NULL} };       /* Sentinel */


PyObject* initMeqUtilsModule ()
{
  Debug::Context::initialize();

  // init the module
  #define INITERROR return NULL;
  #if PY_MAJOR_VERSION < 3
    PyObject *module = Py_InitModule3("mequtils",MeqUtilMethods,
          "various utilities for python-side meqkernel support");
  #else
    static struct PyModuleDef mequtils =
        {
          PyModuleDef_HEAD_INIT,
          "mequtils", /* name of module */
          "various utilities for python-side meqkernel support\n", /* module documentation, may be NULL */
          sizeof(struct module_state),  /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
          MeqUtilMethods,
          NULL,
          myextension_traverse,
          myextension_clear,
          NULL
        };
    PyObject *module = PyModule_Create(&mequtils);
  #endif
  if( !module ) {
    Throw("Py_InitModule3(\"mequtils\") failed");
    INITERROR;
  }
  struct module_state *st = GETSTATE(module);
  st->error = PyErr_NewException("mequtils.Error", NULL, NULL);
  if (st->error == NULL) {
      Py_DECREF(module);
      INITERROR;
  }
  PyObjectRef timbamod = PyImport_ImportModule("Timba");
  Py_INCREF(module); // AddObject will steal a ref, so increment it
  PyModule_AddObject(*timbamod,"mequtils",module);

  PyModule_AddObject(module,"max_axis",PyInt_FromLong(Meq::Axis::MaxAxis));

  // drop out on error
  if( PyErr_Occurred() ){
    Throw("can't initialize module mequtils");
    INITERROR;
  }
  return module;
}


extern "C"
{
#if PY_MAJOR_VERSION >= 3
  PyMODINIT_FUNC PyInit_mequtils ()
#else
  PyMODINIT_FUNC initmequtils ()
#endif
{
  Debug::Context::initialize();
  try
  {
    PyObject* res = initMeqUtilsModule();
    #if PY_MAJOR_VERSION >= 3
      return res;
    #endif
  }
  catch( std::exception &exc )
  {
    Py_FatalError(exc.what());
    #if PY_MAJOR_VERSION >= 3
      return NULL;
    #endif
  }
}


} // extern "C"


} // namespace MeqUtils

InitDebugContext(MeqUtils,"MeqUtils");



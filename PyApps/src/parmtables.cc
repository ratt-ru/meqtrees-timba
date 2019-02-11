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
#include <MEQ/FastParmTable.h>
#include <MEQ/Domain.h>

#include <set>

namespace ParmTables
{

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

using namespace OctoPython;
using namespace Meq;

LocalDebugContext_ns;
inline std::string sdebug (int=0) { return "MeqUtils"; }

static int dum = aidRegistry_Meq();

#ifdef HAVE_FASTPARMTABLE

typedef struct 
{
    PyObject_HEAD
    PyObjectRef domain_list;
    FastParmTable *table;
} PyFPT;

// -----------------------------------------------------------------------
// dealloc
// destructor
// -----------------------------------------------------------------------
static void
PyFPT_dealloc(PyFPT* self)
{
  if( self->table )
    delete self->table;
  self->domain_list.detach();
  #if PY_MAJOR_VERSION >= 3
  //not defined
  #else
    self->ob_type->tp_free((PyObject*)self);
  #endif
}

// -----------------------------------------------------------------------
// new
// allocator
// -----------------------------------------------------------------------
static PyObject *
PyFPT_new (PyTypeObject *type, PyObject *, PyObject *)
{
  PyFPT *self = (PyFPT *)type->tp_alloc(type, 0);
  if( self != NULL )
    self->table = 0;
  return (PyObject *)self;
}

static int
PyFPT_init(PyFPT *self, PyObject *args, PyObject *)
{
  char * tablename;
  int write = 1;
  if( !PyArg_ParseTuple(args,"s|i",&tablename,&write) )
    return -1;
  try
  {
    self->table = new FastParmTable(tablename,write);
  }
  catchStandardErrors(-1);
  return 0;
}

// -----------------------------------------------------------------------
// domain_list()
// creates (if needed) and returns list of domains in table
// -----------------------------------------------------------------------
static PyObject * PyFPT_domain_list (PyFPT * self)
{
  try
  {
    // build domain list if it doesn't yet exist
    if( !self->domain_list )
    {
      const FastParmTable::DomainList &list = self->table->domainList();
      PyObjectRef pylist = PyList_New(list.size());
      for( uint i=0; i<list.size(); i++ )
      {
        Domain::Ref domref;
        list[i].makeDomain(domref);
        ObjRef ref = domref;
        // pyFromDMI returns new ref, SET_ITEM steals it
        PyList_SET_ITEM(*pylist,i,pyFromDMI(ref));
      }
      self->domain_list = pylist;
    }
    // return new ref to domain list
    return self->domain_list.new_ref();
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// name_list()
// returns list (actually, set) of names of every funklet in the table
// -----------------------------------------------------------------------
static PyObject * PyFPT_name_list (PyFPT* self)
{
  Thread::Mutex::Lock lock(self->table->mutex());
  try
  {
    std::set<string> nameset;
    string name;
    int domain_index;
    // iterate over all funklets
    bool have_funklet = self->table->firstFunklet(name,domain_index);
    while( have_funklet )
    {
      nameset.insert(name);
      have_funklet = self->table->nextFunklet(name,domain_index);
    }
    // make Python set
    PyObjectRef namelist = PySet_New(0);
    for( std::set<string>::const_iterator iter = nameset.begin(); iter != nameset.end(); iter++ )
      PySet_Add(*namelist,PyString_FromString(iter->c_str()));
    // return new ref to funklet list, stealing ours
    return ~namelist;
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// funklet_list()
// returns list of 3-tuples of (name,domain_index,domain) for every
// funklet in the table
// -----------------------------------------------------------------------
static PyObject * PyFPT_funklet_list (PyFPT* self)
{
  Thread::Mutex::Lock lock(self->table->mutex());
  try
  {
    PyObjectRef domain_list = PyFPT_domain_list(self);
    PyObjectRef funklist = PyList_New(0);
    string name;
    int domain_index;
    // iterate over all funklets
    bool have_funklet = self->table->firstFunklet(name,domain_index);
    while( have_funklet )
    {
      // Get domain object. For illegal domain indices, use a None domain.
      // note that we borrow a ref in both cases, BuildValue will increment
      // the ref count for us (because of "O" in the format string)
      PyObject *pydom;
      if( domain_index<0 || domain_index >= PyList_Size(*domain_list) )
        pydom = Py_None;
      else
        pydom = PyList_GetItem(*domain_list,domain_index);
      // make 3-tupple of name,domain index,domain
      PyObjectRef entry = Py_BuildValue("siO",name.c_str(),domain_index,pydom);
      PyList_Append(*funklist,*entry);
      have_funklet = self->table->nextFunklet(name,domain_index);
    }
    // return new ref to funklet list, stealing ours
    return ~funklist;
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// funklet_dict()
// returns a nested dict of {'name':{domain_index:domain}} for every
// funklet in the table.
// -----------------------------------------------------------------------
static PyObject * PyFPT_funklet_dict (PyFPT* self)
{
  Thread::Mutex::Lock lock(self->table->mutex());
  try
  {
    PyObjectRef domain_list = PyFPT_domain_list(self);
    PyObjectRef funkdict = PyDict_New();
    string name;
    int domain_index;
    // iterate over all funklets
    bool have_funklet = self->table->firstFunklet(name,domain_index);
    while( have_funklet )
    {
      // get/create domain dict for funklet
      PyObject *domdict = PyDict_GetItemString(*funkdict,name.c_str()); 
      if( !domdict )
      {
        PyObjectRef newdict = PyDict_New();
        domdict = *newdict;
        // this will increment the refcount, so domdict remains valid
        PyDict_SetItemString(*funkdict,name.c_str(),domdict);
      }
      // Get a domain object. For illegal domain indices, use a None domain.
      // Note that we borrow a ref in both cases; ref count will be incremented
      // by PyDict_SetItem
      PyObject * pydom;
      if( domain_index<0 || domain_index >= PyList_Size(*domain_list) )
        pydom = Py_None;
      else
        pydom = PyList_GetItem(*domain_list,domain_index);
      // Make key from domain index
      PyObjectRef key = PyInt_FromLong(domain_index);
      // insert into domain dict
      PyDict_SetItem(domdict,*key,pydom);
      // go on to next funklet
      have_funklet = self->table->nextFunklet(name,domain_index);
    }
    // return new ref to funklet list, stealing ours
    return ~funkdict;
  }
  catchStandardErrors(NULL);
  returnNone;
}


// -----------------------------------------------------------------------
// get_funklets_for_domain()
// returns a list of funklets overlapping a domain
// -----------------------------------------------------------------------
static PyObject * PyFPT_get_funklets_for_domain (PyFPT* self,PyObject *args)
{
  PyObject *pydom;
  char *name;
  if( !PyArg_ParseTuple(args,"sO",&name,&pydom) )
    return NULL;
  try
  {
    // check that domain argument is correct
    ObjRef ref;
    pyToDMI(ref,pydom);
    if( !ref.valid() || ref->objectType() != TpMeqDomain )
      Throw("get_funklets_from_domain(): second argument must be a valid domain record");
    const Domain &domain = ref.as<Domain>();
    std::vector<Funklet::Ref> funks;
    int nfunk = self->table->getFunklets(funks,name,domain);
    // convert funklets to list
    PyObjectRef funklist = PyList_New(nfunk);
    for( int i=0; i<nfunk; i++ )
      // pyFromDMI returns new ref, SET_ITEM steals it
      PyList_SET_ITEM(*funklist,i,pyFromDMI(funks[i]));
    // return new ref to funklet list, stealing ours
    return ~funklist;
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// get_funklet()
// returns a single funklet, specified by name and domain, or None
// if not found
// -----------------------------------------------------------------------
static PyObject * PyFPT_get_funklet (PyFPT* self,PyObject *args)
{
  char *name;
  int dom_index;
  if( !PyArg_ParseTuple(args,"si",&name,&dom_index) )
    return NULL;
  try
  {
    Funklet::Ref funk;
    // PyFromDMI returns new ref
    if( self->table->getFunklet(funk,name,dom_index) )
      return pyFromDMI(funk);
    else
      returnNone;
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// put_funklet()
// stores funklet
// -----------------------------------------------------------------------
static PyObject * PyFPT_put_funklet (PyFPT* self,PyObject *args)
{
  PyObject *pyfunk;
  char *name;
  if( !PyArg_ParseTuple(args,"sO",&name,&pyfunk) )
    return NULL;
  try
  {
    // check that funklet argument is correct
    ObjRef ref;
    pyToDMI(ref,pyfunk);
    if( !ref.valid() || !dynamic_cast<const Funklet *>(ref.deref_p()) )
      Throw("put_funklet(): second argument must be a valid funklet record");
    const Funklet &funklet = ref.as<Funklet>();
    uint ndom0 = self->table->domainList().size();
    self->table->putCoeff(name,funklet);
    // we may have created a new domain: update our domain list
    if( self->domain_list )
    {
      const FastParmTable::DomainList &domlist = self->table->domainList();
      for( uint i=ndom0; i<domlist.size(); i++ )
      {
        Domain::Ref domref;
        domlist[i].makeDomain(domref);
        ObjRef ref = domref;
        PyObjectRef pydom = pyFromDMI(ref);
        PyList_Append(*self->domain_list,*pydom);
      }
    }
    returnNone;
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// delete_funklet()
// deletes one funklet (by name/domain), or all funklets by name
// -----------------------------------------------------------------------
static PyObject * PyFPT_delete_funklet (PyFPT* self,PyObject *args)
{
  char *name;
  int dom_index = -1;
  if( !PyArg_ParseTuple(args,"s|i",&name,&dom_index) )
    return NULL;
  try
  {
    if( dom_index<0 )
      self->table->deleteAllFunklets(name);
    else
      self->table->deleteFunklet(name,dom_index);
  }
  catchStandardErrors(NULL);
  returnNone;
}



static PyMethodDef PyFPT_methods[] = {
    {"name_list",(PyCFunction)PyFPT_name_list, METH_NOARGS,
                  "return a list (or set) of unique funklet names in the table" },
    {"domain_list",(PyCFunction)PyFPT_domain_list, METH_NOARGS,
                  "return a list of domains in the table" },
    {"funklet_list",(PyCFunction)PyFPT_funklet_list, METH_NOARGS,
                  "return a list of (name,domain index,domain) tuples for all funklets "
                  "in the table" },
    {"funklet_dict",(PyCFunction)PyFPT_funklet_dict, METH_NOARGS,
                  "return a dict of funklets in the table. Dict keys are funklet "
                  "names, dict values are themselves dicts: their keys are domain "
                  "indices, and their values are domains"},
    {"get_funklets_for_domain", (PyCFunction)PyFPT_get_funklets_for_domain, METH_VARARGS,
                  "get_funklets_for_domain(name,domain): "
                  "gets all funklets overlapping the given domain." },
    {"get_funklet",(PyCFunction)PyFPT_get_funklet, METH_VARARGS,
                  "get_funklet(name,domain_index): "
                  "retrieves funklet for name and domain index. "
                  "Returns None if no such funklet in table."},
    {"put_funklet",(PyCFunction)PyFPT_put_funklet, METH_VARARGS,
                  "put_funklet(name,funklet): "
                  "stores a new funklet in the table." },
    {"delete_funklet",(PyCFunction)PyFPT_delete_funklet, METH_VARARGS,
                  "delete_funklet(name[,domain_index]): "
                  "deletes a funklet. If domain_index is not given, deletes all " 
                  "funklets matching the name."},
    {NULL}  /* Sentinel */
};

PyTypeObject PyFPTType = {
    PyVarObject_HEAD_INIT(NULL, 0) //This will work in both python 2.7 and >3
    "parmtables.FastParmTable",      /*tp_name*/
    sizeof(PyFPT),          /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)PyFPT_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "FastParmTable interface",       /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    PyFPT_methods,         /* tp_methods */
    0, /*PyProxyWP_members,*/  /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)PyFPT_init,  /* tp_init */
    0,                         /* tp_alloc */
    PyFPT_new,             /* tp_new */
};


#endif // HAVE_FASTPARMTABLE

// -----------------------------------------------------------------------
// Module initialization
// -----------------------------------------------------------------------
static PyMethodDef ParmTableMethods[] = {
    { NULL, NULL, 0, NULL} };       /* Sentinel */


PyObject* initParmTablesModule ()
{
  Debug::Context::initialize();
  #define INITERROR return NULL;
  // import the octopython module to init everything
  PyObject * octomod = PyImport_ImportModule("Timba.octopython");
  if( !octomod )
  {
    PyErr_Print();
    Throw("import of Timba.octopython module failed");
    INITERROR;
  }

  #ifdef HAVE_FASTPARMTABLE
    if( PyType_Ready(&PyFPTType) < 0 ) {
      Throw("failed to register FastParmTable datatype");
      INITERROR;
    }
  #endif
    
  // init the module
  #if PY_MAJOR_VERSION < 3
    PyObject *module = Py_InitModule3("parmtables",ParmTableMethods,
          "support for manipulating ParmTables");
  #else
    static struct PyModuleDef parmtables =
        {
          PyModuleDef_HEAD_INIT,
          "parmtables", /* name of module */
          "support for manipulating ParmTables\n", /* module documentation, may be NULL */
          sizeof(struct module_state),  /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
          ParmTableMethods,
          NULL,
          myextension_traverse,
          myextension_clear,
          NULL
        };
    PyObject *module = PyModule_Create(&parmtables);
  #endif
  if( !module ) {
    Throw("Py_InitModule3(\"parmtables\") failed");
    INITERROR;
  }
  struct module_state *st = GETSTATE(module);
  st->error = PyErr_NewException("parmtables.Error", NULL, NULL);
  if (st->error == NULL) {
      Py_DECREF(module);
      INITERROR;
  }
  PyObjectRef timbamod = PyImport_ImportModule("Timba");
  Py_INCREF(module); // AddObject will steal a ref, so increment it
  PyModule_AddObject(*timbamod,"parmtables",module);

  #ifdef HAVE_FASTPARMTABLE
    PyModule_AddObject(module, "FastParmTable",(PyObject *)&PyFPTType); // steals ref
  #endif
  
  // drop out on error
  if( PyErr_Occurred() ) {
    Throw("can't initialize module parmtables");
    INITERROR;
  }
  return module;
}


extern "C"
{
  #if PY_MAJOR_VERSION >= 3
    PyMODINIT_FUNC PyInit_parmtables ()
  #else
    PyMODINIT_FUNC initparmtables ()
  #endif
  {
    Debug::Context::initialize();

    try
    {
      PyObject* res = initParmTablesModule();
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
InitDebugContext(ParmTables,"parmtables");


#include <DMI/Record.h>
#include <Python.h>
#include "OctoPython.h"
#include "AID-OctoPython.h"
//#include "structmember.h"

namespace OctoPython
{
    


// -----------------------------------------------------------------------
// dealloc
// destructor
// -----------------------------------------------------------------------
static void
LazyObjRef_dealloc (LazyObjRef* self)
{
  self->field.clear();
  self->ob_type->tp_free((PyObject*)self);
}

// -----------------------------------------------------------------------
// new
// allocator
// -----------------------------------------------------------------------
static PyObject *
LazyObjRef_new (PyTypeObject *type, PyObject *, PyObject *)
{
  LazyObjRef *self;

  self = (LazyObjRef *)type->tp_alloc(type, 0);
  // do a placement-new to initialize the Record::Field
  if( self != NULL ) 
    new( &(self->field) ) DMI::Record::Field;

  return (PyObject *)self;
}

// // -----------------------------------------------------------------------
// // init
// // does nothing for now
// // -----------------------------------------------------------------------
// static int
// LazyObjRef_init(LazyObjRef *, PyObject *args, PyObject *kwds)
// {
//   static char *kwlist[] = {};
//   if( ! PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist) )
//       return -1; 
//   return 0;
// }
// 

// -----------------------------------------------------------------------
// resolve
// resolves Field into real object, doing fromBlock'ing as necessary
// returns NEW reference to object
// -----------------------------------------------------------------------
static PyObject * LazyObjRef_resolve (LazyObjRef* self)
{
  try
  {
    // return None for invalid field
    if( !self->field.valid() )
      returnNone;
    PyObjectRef obj = pyFromDMI(self->field.ref().deref());
    // returns NEW ref, stealing from ours
    return ~obj;
  }
  catchStandardErrors(NULL);
  returnNone;
}


// -----------------------------------------------------------------------
// members/data structures init
// -----------------------------------------------------------------------

static PyMethodDef LazyObjRef_methods[] = {
    {"resolve",     (PyCFunction)LazyObjRef_resolve, METH_NOARGS,
                  "resolves lazy ref into object, returns object" },
    {NULL}  /* Sentinel */
};

PyTypeObject PyLazyObjRefType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "octopython.lazy_objref",      /*tp_name*/
    sizeof(LazyObjRef),          /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)LazyObjRef_dealloc, /*tp_dealloc*/
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
    "LazyObjRef objects",       /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    LazyObjRef_methods,         /* tp_methods */
    0, /*LazyObjRef_members,*/  /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
//    (initproc)LazyObjRef_init,  /* tp_init */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    LazyObjRef_new,             /* tp_new */
};
                            
} // namespace OctoPython

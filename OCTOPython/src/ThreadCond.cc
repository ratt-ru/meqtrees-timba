#define MAKE_LOFAR_SYMBOLS_GLOBAL 1

#include <Common/Thread/Condition.h>
#include <Python.h>
#include "OctoPython.h"
#include "AID-OctoPython.h"
//#include "structmember.h"

namespace OctoPython
{
    
typedef struct 
{
    PyObject_HEAD
    PyObject *address;
    Thread::Condition cond;
    bool verbose;
} PyThreadCond;

// -----------------------------------------------------------------------
// dealloc
// destructor
// -----------------------------------------------------------------------
static void
TC_dealloc(PyThreadCond* self)
{
  self->ob_type->tp_free((PyObject*)self);
}

// -----------------------------------------------------------------------
// new
// allocator
// -----------------------------------------------------------------------
static PyObject *
TC_new (PyTypeObject *type, PyObject *, PyObject *)
{
  PyThreadCond *self;

  self = (PyThreadCond *)type->tp_alloc(type, 0);

  return (PyObject *)self;
}


// -----------------------------------------------------------------------
// init
// initializer
// -----------------------------------------------------------------------
static int
TC_init(PyThreadCond *self, PyObject *args, PyObject *kwds)
{
  static char *kwlist[] = {"verbose", NULL};
  int verb;
  if( ! PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist, &verb) )
      return -1; 
  self->verbose = verb;
  if( verb )
    cerr<<"PyThreadCond("<<self<<"): initialized\n";
    
  return 0;
}

static PyObject * TC_lock (PyThreadCond* self)
{
  if( self->verbose ) 
    cerr<<"PyThreadCond("<<self<<","<<Thread::ThrID::self()<<"): locking...\n";
  int res = self->cond.lock();
  if( self->verbose ) 
    cerr<<"PyThreadCond("<<self<<","<<Thread::ThrID::self()<<"): lock: "<<res<<endl;
  return PyInt_FromLong(res);
}

static PyObject * TC_unlock (PyThreadCond* self)
{
  int res = self->cond.unlock();
  if( self->verbose ) 
    cerr<<"PyThreadCond("<<self<<","<<Thread::ThrID::self()<<"): unlock: "<<res<<endl;
  return PyInt_FromLong(res);
}

static PyObject * TC_signal (PyThreadCond* self)
{
  int res = self->cond.signal();
  if( self->verbose ) 
    cerr<<"PyThreadCond("<<self<<","<<Thread::ThrID::self()<<"): signal: "<<res<<endl;
  return PyInt_FromLong(res);
}

static PyObject * TC_broadcast (PyThreadCond* self)
{
  int res = self->cond.broadcast();
  if( self->verbose ) 
    cerr<<"PyThreadCond("<<self<<","<<Thread::ThrID::self()<<"): broadcast: "<<res<<endl;
  return PyInt_FromLong(res);
}

static PyObject * TC_wait (PyThreadCond* self,PyObject *args)
{
  PyObject * py_to = 0;
  if( !PyArg_ParseTuple(args,"|O",&py_to) )
    return NULL;
  double timeout = -1;
  if( py_to && py_to != Py_None )
  {
    timeout = PyFloat_AsDouble(py_to);
    if( PyErr_Occurred() )
      return NULL;
  }
  if( self->verbose ) 
    cerr<<"PyThreadCond("<<self<<","<<Thread::ThrID::self()<<"): waiting, timeout "<<timeout<<endl;
  int res = timeout<0 ? self->cond.wait() : self->cond.wait(timeout);
  if( self->verbose ) 
    cerr<<"PyThreadCond("<<self<<","<<Thread::ThrID::self()<<"): wait: "<<res<<endl;
  return PyInt_FromLong(res);
}

// -----------------------------------------------------------------------
// members/data structures init
// -----------------------------------------------------------------------

static PyMethodDef TC_methods[] = {
    {"lock",      (PyCFunction)TC_lock, METH_NOARGS,
                  "locks mutex" },
    {"unlock",    (PyCFunction)TC_unlock, METH_NOARGS,
                  "unlocks mutex" },
    {"signal",    (PyCFunction)TC_signal, METH_NOARGS,
                  "signals condition" },
    {"broadcast", (PyCFunction)TC_broadcast, METH_NOARGS,
                  "broadcasts condition" },
    {"wait",      (PyCFunction)TC_wait, METH_VARARGS,
                  "waits on condition" },
    {NULL}  /* Sentinel */
};

PyTypeObject PyThreadCondType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "octopython.thread_condition", /*tp_name*/
    sizeof(PyThreadCond),          /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)TC_dealloc,    /*tp_dealloc*/
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
    "Thread condition variable",       /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    TC_methods,         /* tp_methods */
    0, /*PyThreadCond_members,*/  /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)TC_init,  /* tp_init */
    0,                         /* tp_alloc */
    TC_new,             /* tp_new */
};
                            
} // namespace OctoPython

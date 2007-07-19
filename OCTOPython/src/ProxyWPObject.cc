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

#include <DMI/DMI.h>
#include <OCTOPUSSY/Octopussy.h>
#include <OCTOPUSSY/OctoproxyWP.h>
#include <Python.h>
#include "OctoPython.h"
#include "AID-OctoPython.h"
//#include "structmember.h"

namespace OctoPython
{
    
typedef struct 
{
    PyObject_HEAD
    PyObjectRef address;
    WPRef       wpref;
} PyProxyWP;

// -----------------------------------------------------------------------
// dealloc
// destructor
// -----------------------------------------------------------------------
static void
PyProxyWP_dealloc(PyProxyWP* self)
{
  self->address.detach();
  self->ob_type->tp_free((PyObject*)self);
}

// -----------------------------------------------------------------------
// new
// allocator
// -----------------------------------------------------------------------
static PyObject *
PyProxyWP_new (PyTypeObject *type, PyObject *, PyObject *)
{
  PyProxyWP *self;

  self = (PyProxyWP *)type->tp_alloc(type, 0);
  if( self != NULL ) 
    self->address = PyString_FromString("");

  return (PyObject *)self;
}


// -----------------------------------------------------------------------
// init
// initializer
// -----------------------------------------------------------------------
static int
PyProxyWP_init(PyProxyWP *self, PyObject *args, PyObject *kwds)
{
  static char *kwlist[] = {"wpid", NULL};
  char *wpid;
  if( ! PyArg_ParseTupleAndKeywords(args, kwds, "|s", kwlist, &wpid) )
      return -1; 
  try
  {
    if( !Octopussy::isRunning() )
      returnError(-1,OctoPython,"OCTOPUSSY not initialized");
    AtomicID wpc = wpid ? AtomicID(wpid) : AidPython;
    // Is OCTOPUSSY running? attach new proxy WP to it
    if( !Octopussy::isRunning() )
      returnError(-1,OctoPython,"OCTOPUSSY not initialized");
    self->wpref <<= new Octoproxy::ProxyWP(wpc);
    Octopussy::dispatcher().attach(self->wpref.dewr_p(),DMI::ANONWR);
    // Get address -- new ref returned, so assign
    self->address = pyFromHIID(self->wpref->address());
  }
  catchStandardErrors(-1);
  return 0;
}

//static PyMemberDef PyProxyWP_members[] = 
//{
//    {"address", T_OBJECT_EX, offsetof(PyProxyWP,address), 0,
//     "address of proxy WP"},
//    {NULL}  /* Sentinel */
//};

// -----------------------------------------------------------------------
// address accessor
// -----------------------------------------------------------------------
static PyObject * PyProxyWP_address (PyProxyWP* self)
{
  return self->address.new_ref();
}

// helper function, converts scope string to Message::Scope constant
static int resolveScope (const char *chscope)
{
  switch( chscope[0] )
  {
    case 'g': return Message::GLOBAL;  
    case 'h': return Message::HOST;    
    case 'l': return Message::LOCAL;   
  }
  throwError(Value,"illegal scope argument");
}

// -----------------------------------------------------------------------
// subscribe
// -----------------------------------------------------------------------
static PyObject * PyProxyWP_subscribe (PyProxyWP* self,PyObject *args)
{
  PyObject *mask_seq;
  char *chscope;
  if( !PyArg_ParseTuple(args,"Os",&mask_seq,&chscope) )
    return NULL;
  try
  {
    // convert arguments
    int scope = resolveScope(chscope);
    HIID id; 
    pyToHIID(id,mask_seq);
    // subscribe
    self->wpref().subscribe(id,scope);
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// unsubscribe
// -----------------------------------------------------------------------
static PyObject * PyProxyWP_unsubscribe (PyProxyWP* self,PyObject *args)
{
  PyObject *mask_seq;
  if( !PyArg_ParseTuple(args,"O",&mask_seq) )
    return NULL;
  try
  {
    HIID id;
    pyToHIID(id,mask_seq);
    self->wpref().unsubscribe(id);
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// send
// -----------------------------------------------------------------------
static PyObject * PyProxyWP_send (PyProxyWP* self,PyObject *args)
{
  PyObject *py_msg,*py_dest;
  if( !PyArg_ParseTuple(args,"OO",&py_msg,&py_dest) )
    return NULL;
  try
  {
    HIID dest;
    Message::Ref msg;
    pyToHIID(dest,py_dest);
    pyToMessage(msg,py_msg);
    self->wpref().send(msg,dest);
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// publish
// -----------------------------------------------------------------------
static PyObject * PyProxyWP_publish (PyProxyWP* self,PyObject *args)
{
  PyObject *py_msg;
  char *chscope;
  if( !PyArg_ParseTuple(args,"Os",&py_msg,&chscope) )
    return NULL;
  try
  {
    Message::Ref msg; 
    int scope = resolveScope(chscope);
    pyToMessage(msg,py_msg);
    self->wpref().publish(msg,0,scope);
  }
  catchStandardErrors(NULL);
  returnNone;
}

// -----------------------------------------------------------------------
// num_pending
// returns # of messages in WPs queue
// -----------------------------------------------------------------------
static PyObject * PyProxyWP_num_pending (PyProxyWP* self,PyObject *args)
{
  if( !PyArg_ParseTuple(args,"") )
    return NULL;
  try
  {
    WPInterface &wp = self->wpref();
    if( !wp.isRunning() )
      returnError(NULL,OctoPython,"proxy wp no longer running");
    Thread::Mutex::Lock lock(wp.queueCondition());
    int res = wp.queue().size();
    return PyInt_FromLong(res);
  }
  catchStandardErrors(NULL);
}

// -----------------------------------------------------------------------
// receive
// returns first message from WP's queue
// -----------------------------------------------------------------------
static PyObject * PyProxyWP_receive (PyProxyWP* self,PyObject *args)
{
  double timeout=-1;
  if( !PyArg_ParseTuple(args,"|d",&timeout) )
    return NULL;
  try
  {
    Message::Ref mref;
    WPInterface &wp = self->wpref();
    Thread::Mutex::Lock lock(wp.queueCondition());
    while( wp.queue().empty() )
    {
      if( !wp.isRunning() )
        returnError(NULL,OctoPython,"proxy wp no longer running");
      // timeout>=0: return None if queue is empty
      if( timeout>=0 )
      {
        if( timeout>0 )
          wp.queueCondition().wait(timeout);
        if( wp.queue().empty() )
          returnNone;
      }
      else // timeout<0: wait indefinitely
        wp.queueCondition().wait();
    }
    // pop first message and return it
    mref = wp.queue().front().mref;
    wp.queue().pop_front();
    return pyFromMessage(*mref); // returns NEW REF
  }
  catchStandardErrors(NULL);
}

// -----------------------------------------------------------------------
// receive_all
// returns entire queue as a list, or none if queue is empty
// -----------------------------------------------------------------------
static PyObject * PyProxyWP_receive_all (PyProxyWP* self,PyObject *args)
{
  if( !PyArg_ParseTuple(args,"") )
    return NULL;
  try
  {
    Message::Ref mref;
    WPInterface &wp = self->wpref();
    if( !wp.isRunning() )
      returnError(NULL,OctoPython,"proxy wp no longer running");
    if( wp.queue().empty() )
      returnNone; 
    Thread::Mutex::Lock lock(wp.queueCondition());
    int n = wp.queue().size();
    if( !n )
      returnNone; 
    PyObjectRef pylist = PyList_New(n); // returns NEW REF
    for( int i=0; i<n; i++ )
    {
      mref = wp.queue().front().mref;
      wp.queue().pop_front();
      // pyFromMessage() returns new ref, PyList_SET_ITEM steals it
      PyList_SET_ITEM(*pylist,i,pyFromMessage(*mref));
    }
    return ~pylist;
  }
  catchStandardErrors(NULL);
}


// -----------------------------------------------------------------------
// receive_threaded
// returns first message from WP's queue (threaded version)
// -----------------------------------------------------------------------
static PyObject * PyProxyWP_receive_threaded (PyProxyWP* self,PyObject *args)
{
  double timeout=-1;
  if( !PyArg_ParseTuple(args,"|d",&timeout) )
    return NULL;
  try
  {
    Message::Ref mref;
    WPInterface &wp = self->wpref();
    Thread::Mutex::Lock lock(wp.queueCondition());
    if( !wp.isRunning() )
    {
      returnError(NULL,OctoPython,"proxy wp no longer running");
    }
    // else already have something in queue -- get it out
    else if( !wp.queue().empty() )
    {
      mref = wp.queue().front().mref;
      wp.queue().pop_front();
      lock.release();
    }
    else if( timeout != 0 ) // queue is empty but we can wait
    {
      // release GIL
      Py_BEGIN_ALLOW_THREADS 
      // need to release the queue lock before attempting to reacquire GIL
      // (deadlock with send thread may occur otherwise), hence releasing
      // the queue lock is also our exit condition
      while( lock.locked() )
      {
        // timeout>0: wait with timeout
        if( timeout>0 )
          wp.queueCondition().wait(timeout);
        else if( timeout<0 ) // timeout<0: wait indefinitely
          wp.queueCondition().wait();
        // check that WP is not stopped
        if( !wp.isRunning() )
          lock.release();
        // is queue still empty?
        else if( wp.queue().empty() )
        {
          if( timeout>0 ) // we had a limited timeout, so release lock to exit loop
            lock.release();
          // else go back for one more wait
        }
        else // something in queue, hurrah!
        {
          mref = wp.queue().front().mref;
          wp.queue().pop_front();
          lock.release();
        }
      }
      Py_END_ALLOW_THREADS 
    }
    // wp not running, return error
    if( !wp.isRunning() )
    {
      returnError(NULL,OctoPython,"proxy wp no longer running");
    }
    // no message received, return None
    else if( !mref.valid() )  
    {
      returnNone;
    }
    // got a message, return it
    return pyFromMessage(*mref);     // returns new ref
  }
  catchStandardErrors(NULL);
}

// -----------------------------------------------------------------------
// members/data structures init
// -----------------------------------------------------------------------

static PyMethodDef PyProxyWP_methods[] = {
    {"address",     (PyCFunction)PyProxyWP_address, METH_NOARGS,
                  "return the proxy wp's address" },
    {"subscribe",   (PyCFunction)PyProxyWP_subscribe, METH_VARARGS,
                  "add subscription" },
    {"unsubscribe", (PyCFunction)PyProxyWP_unsubscribe, METH_VARARGS,
                  "remove subscription" },
    {"send",        (PyCFunction)PyProxyWP_send, METH_VARARGS,
                  "send message" },
    {"publish",     (PyCFunction)PyProxyWP_publish, METH_VARARGS,
                  "publish message" },
    {"num_pending", (PyCFunction)PyProxyWP_num_pending, METH_VARARGS,
                  "number of pending messages in queue" },
    {"receive",     (PyCFunction)PyProxyWP_receive, METH_VARARGS,
                  "receives message from queue" },
    {"receive_all", (PyCFunction)PyProxyWP_receive_all, METH_VARARGS,
                  "receives all messages from queue" },
    {"receive_threaded",(PyCFunction)PyProxyWP_receive_threaded, METH_VARARGS,
                  "receives message from queue (threaded version)" },
    {NULL}  /* Sentinel */
};

PyTypeObject PyProxyWPType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "octopython.proxy_wp",      /*tp_name*/
    sizeof(PyProxyWP),          /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)PyProxyWP_dealloc, /*tp_dealloc*/
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
    "PyProxyWP objects",       /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    PyProxyWP_methods,         /* tp_methods */
    0, /*PyProxyWP_members,*/  /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)PyProxyWP_init,  /* tp_init */
    0,                         /* tp_alloc */
    PyProxyWP_new,             /* tp_new */
};
                            
} // namespace OctoPython

#include "OctoPython.h"
#include <OCTOPUSSY/Message.h>
    
namespace OctoPython {    
    
PyClassObjects py_class = {0,0};

// -----------------------------------------------------------------------
// convertSeqToHIID
// converts sequence of ints (or any other object supporting iterators)
// to HIID
// -----------------------------------------------------------------------
int convertSeqToHIID (HIID &id,PyObject *list)
{
  PyObject *iter = PyObject_GetIter(list);
  if( !iter )
    return -1;
  // check that this is a sequence
  id.clear();
  PyObject *item;
  while( ( item = PyIter_Next(iter) ) != 0 && !PyErr_Occurred() )
  {
    id.add(AtomicID(PyInt_AsLong(item)));
    Py_DECREF(item);
  }
  Py_DECREF(iter);
  return PyErr_Occurred() ? -1 : 1;
}

// -----------------------------------------------------------------------
// convertHIIDToSeq
// Converts HIID to Python-compatible sequence of ints
// -----------------------------------------------------------------------
PyObject * convertHIIDToSeq (const HIID &id)
{
  // build up tuple
  PyObject *list = PyTuple_New(id.size());
  for( uint i=0; i<id.size(); i++ )
    PyTuple_SET_ITEM(list,i,PyInt_FromLong(id[i].id()));
  return list;
}

// -----------------------------------------------------------------------
// pyFromHIID
// -----------------------------------------------------------------------
PyObject * pyFromHIID (const HIID &id)
{
  // build up tuple
  PyObject *hiid_seq = convertHIIDToSeq(id);
  // call hiid constructor
  PyObject *args = PyTuple_New(1);
  PyTuple_SET_ITEM(args,0,hiid_seq);
  return PyObject_CallObject(py_class.hiid,args);
}


// -----------------------------------------------------------------------
// pyFromMessage
// -----------------------------------------------------------------------
PyObject * pyFromMessage (const Message &msg)
{
  // create message object
  PyObject *args = PyTuple_New(3);
  PyTuple_SET_ITEM(args,0,pyFromHIID(msg.id()));
  PyTuple_SET_ITEM(args,1,Py_None);
  PyTuple_SET_ITEM(args,2,PyInt_FromLong(msg.priority()-Message::PRI_NORMAL));
  PyObject *py_msg = PyObject_CallObject(py_class.message,args);
  if( !py_msg )
    return NULL;
  // create additional attributes
  PyObject_SetAttrString(py_msg,"from",pyFromHIID(msg.from()));
  PyObject_SetAttrString(py_msg,"to",pyFromHIID(msg.to()));
  PyObject_SetAttrString(py_msg,"state",PyInt_FromLong(msg.state()));
  PyObject_SetAttrString(py_msg,"hops",PyInt_FromLong(msg.hops()));
  return py_msg;
}

// -----------------------------------------------------------------------
// pyToMessage
// -----------------------------------------------------------------------
int pyToMessage (Message::Ref &msg,PyObject *pyobj)
{
  PyObject_Print(pyobj,stdout,Py_PRINT_RAW);
  if( !PyObject_IsInstance(pyobj,py_class.message) )
    returnError(-1,Type,"object is not of type message");
  // get message ID
  PyObject *py_msgid = PyObject_GetAttrString(pyobj,"msgid");
  HIID msgid;
  if( !py_msgid || pyToHIID(msgid,py_msgid)<0 )
    returnError(-1,Attribute,"missing or bad msgid attribute");
  // get message priority
  int priority = 0;
  PyObject *py_priority = PyObject_GetAttrString(pyobj,"priority");
  if( py_priority )
    priority = PyInt_AsLong(py_priority);
  // get message payload
  // ignore for now
  if( PyErr_Occurred() )
    return -1;
  // create message object
  msg <<= new Message(msgid,Message::PRI_NORMAL + priority);
  
  // map additional attributes, if they exist
  HIID addr;
  PyObject * py_from  = PyObject_GetAttrString(pyobj,"from");
  if( py_from && pyToHIID(addr,py_from)>0 )
    msg().setFrom(addr);
  PyObject * py_to    = PyObject_GetAttrString(pyobj,"to");
  if( py_to && pyToHIID(addr,py_to)>0 )
    msg().setTo(addr);
  PyObject * py_state = PyObject_GetAttrString(pyobj,"state");
  if( py_state )
    msg().setState(PyInt_AsLong(py_state));
  PyObject * py_hops  = PyObject_GetAttrString(pyobj,"hops");
  if( py_hops )
    msg().setHops(PyInt_AsLong(py_hops));
  // clear errors at this point, since they only relate to optional attrs
  PyErr_Clear();
  return 1;
}




};

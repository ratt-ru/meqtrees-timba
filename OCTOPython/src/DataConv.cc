#include "OctoPython.h"
#include <OCTOPUSSY/Message.h>
#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
#include <DMI/DynamicTypeManager.h>
#define Bool NumarrayBool
#include <numarray/libnumarray.h>
#undef Bool

using Debug::ssprintf;
        
namespace OctoPython {    
    
PyClassObjects py_class = {0,0,0,0,0,0};

const char dmi_type_tag[] = "__dmi_type";

// -----------------------------------------------------------------------
// convertSeqToHIID
// converts sequence of ints (or any other object supporting iterators)
// to HIID
// -----------------------------------------------------------------------
int convertSeqToHIID (HIID &id,PyObject *list)
{
  PyObjectRef iter = PyObject_GetIter(list);
  if( !iter )
    throwError(Type,"can't convert non-iterable object to HIID");
  // check that this is a sequence
  id.clear();
  PyObjectRef item;
  while( ( item = PyIter_Next(*iter) ) != 0 && !PyErr_Occurred() )
  {
    int aid = int( PyInt_AsLong(*item) );
    if( !PyErr_Occurred() )
      id.add(AtomicID(aid));
  }
  if( PyErr_Occurred() )
    throwErrorOpt(Type,"error converting to hiid"); 
  return 1;
}

// -----------------------------------------------------------------------
// convertHIIDToSeq
// Converts HIID to Python-compatible sequence of ints
// -----------------------------------------------------------------------
PyObject * convertHIIDToSeq (const HIID &id)
{
  // build up tuple
  PyObjectRef list = PyTuple_New(id.size());
  for( uint i=0; i<id.size(); i++ )
    PyTuple_SET_ITEM(*list,i,PyInt_FromLong(id[i].id()));
  return ~list;
}

// -----------------------------------------------------------------------
// pyFromHIID
// -----------------------------------------------------------------------
PyObject * pyFromHIID (const HIID &id)
{
  // put hiid-sequence into tuple of args
  PyObjectRef args = Py_BuildValue("(N)",convertHIIDToSeq(id)); 
  // call hiid constructor
  return PyObject_CallObject(py_class.hiid,*args);
}

// -----------------------------------------------------------------------
// pyToMessage
// -----------------------------------------------------------------------
int pyToMessage (Message::Ref &msg,PyObject *pyobj)
{
//  PyObject_Print(pyobj,stdout,Py_PRINT_RAW);
  if( !PyObject_IsInstance(pyobj,py_class.message) )
    throwError(Type,"object is not of type message");
  // get message ID
  PyObjectRef py_msgid = PyObject_GetAttrString(pyobj,"msgid");
  if( !py_msgid ) 
    throwError(Attribute,"missing or bad msgid attribute");
  HIID msgid;
  pyToHIID(msgid,*py_msgid);
  // get message priority
  int priority = 0;
  PyObjectRef py_priority = PyObject_GetAttrString(pyobj,"priority");
  if( py_priority )
    priority = PyInt_AsLong(*py_priority);
  
  // create message object
  msg <<= new Message(msgid,Message::PRI_NORMAL + priority);
  
  // get message payload
  PyObjectRef py_payload = PyObject_GetAttrString(pyobj,"payload");
  if( py_payload && *py_payload != Py_None )
  {
    ObjRef ref;
    pyToDMI(ref,*py_payload);
    msg() <<= ref;
  }
  // NB: Use PyBuffer objects for SmartBlock payloads
  
  // map additional attributes, if they exist
  HIID addr;
  PyObjectRef py_from  = PyObject_GetAttrString(pyobj,"from");
  if( py_from && pyToHIID(addr,*py_from)>0 )
    msg().setFrom(addr);
  PyObjectRef py_to    = PyObject_GetAttrString(pyobj,"to");
  if( py_to && pyToHIID(addr,*py_to)>0 )
    msg().setTo(addr);
  PyObjectRef py_state = PyObject_GetAttrString(pyobj,"state");
  if( py_state )
    msg().setState(PyInt_AsLong(*py_state));
  PyObjectRef py_hops  = PyObject_GetAttrString(pyobj,"hops");
  if( py_hops )
    msg().setHops(PyInt_AsLong(*py_hops));
  // clear errors at this point, since they only relate to optional attrs
  PyErr_Clear();
  return 1;
}

inline string ObjStr (const PyObject *obj) 
{
  return Debug::ssprintf("%s @%x",obj->ob_type->tp_name,(int)obj);
}

// createSubclass:
// Helper templated function. If the dmi_type_tag attribute exists, it is 
// interpreted as a type string, and an object of that type is created and 
// returned  (must be a subclass of Base). Otherwise, a Base is created. 
// If val::dmi_actual_type is not a legal type string, or not a subclass of Base,
// an exception is thrown.
template<class Base>
static Base * createSubclass (PyObject *pyobj)
{
  Base *pbase;
  // the dmi_type_tag attribute specifies a subclass 
  PyObjectRef dmitype = PyObject_GetAttrString(pyobj,const_cast<char*>(dmi_type_tag));
  if( dmitype )
  {
    char *typestr = PyString_AsString(*dmitype);
    if( !typestr )
      throwError(Value,string(dmi_type_tag)+" attribute is not a string");
    dprintf(4)("real object type is %s\n",typestr);
    BlockableObject * bo = DynamicTypeManager::construct(TypeId(typestr));
    pbase = dynamic_cast<Base *>(bo);
    if( !pbase )
    {
      delete bo;
      throwError(Type,string(typestr)+"is not a subclass of "+TpOfPtr(pbase).toString());
    }
  }
  else // no type tag, allocate a base type
  {
    PyErr_Clear();  // clear "no such attribute" error
    pbase = new Base;
  }
  dprintf(5)("%s created at address %x\n",pbase->objectType().toString().c_str(),(int)pbase);
  return pbase;
}

// -----------------------------------------------------------------------
// pyToRecord
// -----------------------------------------------------------------------
int pyToRecord (DataRecord::Ref &rec,PyObject *pyobj)
{
  string objstr = 
      Debug(3) ? "PyToRecord("+ObjStr(pyobj)+"): " : string();
  int num_original = PyMapping_Length(pyobj);
  int num_assigned = 0;
  cdebug(3)<<objstr<<"converting mapping of "<<num_original<<" items\n";
  PyObjectRef py_keylist = PyMapping_Keys(pyobj);
  if( !py_keylist )
    throwErrorOpt(Type,"no key list returned");
  rec <<= createSubclass<DataRecord>(pyobj);
  int numkeys = PySequence_Length(*py_keylist);
  // loop over dict keys
  for( int ikey=0; ikey<numkeys; ikey++ )
  {
    PyErr_Clear();
    PyObjectRef py_key = PySequence_GetItem(*py_keylist,ikey);
    if( !py_key )
      throwErrorOpt(Key,ssprintf("can't get key #%s",ikey));
    // key must be a string, ensure this here
    char *key = PyString_AsString(*py_key);
    if( !key )
    {
      cdebug(4)<<objstr<<"skipping key "<<ikey<<": not a string"<<endl;
      continue;
    }
    string keystr(key);
    // convert string to HIID
    HIID id; 
    bool failed = false;
    try { id = HIID(keystr,0,"._"); }
    catch (...) { failed=true; }
    if( failed )
    {
      cdebug(4)<<objstr<<"skipping key " <<keystr<<" ("<<ikey<<"): not a HIID"<<endl;
      continue;
    }
    // attempt to convert value to DMI object
    PyObjectRef pyval = PyMapping_GetItemString(pyobj,const_cast<char*>(keystr.c_str()));
    if( !pyval )
    {
      cdebug(4)<<objstr<<"skipping key " <<keystr<<" ("<<ikey<<"): failed to get value"<<endl;
      continue;
    }
    // try to convert the value and assign it to record field
    cdebug(4)<<objstr<<"converting key " <<keystr<<" ("<<ikey<<")\n";
    ObjRef ref;
    try 
    { 
      pyToDMI(ref,*pyval); 
      rec()[id] <<= ref;
      cdebug(4)<<objstr<<"assigned value for key " <<keystr<<" ("<<ikey<<")\n";
      num_assigned++;
    }
    // catch various failures and ignore them
    catch( std::exception &exc )
    { cdebug(4)<<objstr<<"skipping key " <<keystr<<" ("<<ikey<<"): failed to convert value: "<<exc.what()<<endl; }
    catch( ... )
    { cdebug(4)<<objstr<<"skipping key " <<keystr<<" ("<<ikey<<"): failed to convert value: unknown exception\n"; }
  }
  PyErr_Clear();
  cdebug(3)<<objstr<<"assigned "<<num_assigned<<" of "<<num_original<<" fields\n";
  rec().validateContent();
  return 1;
}

// Helper functions map NumarrayType enums to TypeIds
// Note that only a limited subset of element types is supported by DMI
static TypeId numarrayToTypeId (int num)
{
  switch( num )
  {
    case tBool:       return Tpbool;   
    case tUInt8:      return Tpuchar;
    case tInt16:      return Tpshort;
    case tInt32:      return Tpint;
    case tFloat32:    return Tpfloat;
    case tFloat64:    return Tpdouble;
    case tComplex32:  return Tpfcomplex;
    case tComplex64:  return Tpdcomplex;
    default:
      throwError(Type,ssprintf("numarray type %d not supported by dmi",num));
  }
}

static NumarrayType typeIdToNumarray (TypeId tid)
{
  switch( tid.id() )
  {
    case Tpbool_int:      return tBool;   
    case Tpuchar_int:     return tUInt8;
    case Tpshort_int:     return tInt16;
    case Tpint_int:       return tInt32;
    case Tpfloat_int:     return tFloat32;
    case Tpdouble_int:    return tFloat64;
    case Tpfcomplex_int:  return tComplex32;
    case Tpdcomplex_int:  return tComplex64;
    default:
      throwError(Type,"dmi type "+tid.toString()+" no supported by numarray");
  }
}

// -----------------------------------------------------------------------
// pyToArray
// -----------------------------------------------------------------------
int pyToArray (DataArray::Ref &arr,PyObject *pyobj)
{
  // get input array object
  PyArrayObject *pyarr = NA_InputArray(pyobj,tAny,NUM_C_ARRAY);
  PyObjectRef pyarr_ref((PyObject*)pyarr); // for auto-cleanup
  if( !pyarr ) 
    throwErrorOpt(Type,"NA_InputArray fails, perhaps object is not an array");
  // figure out array shape
  uint ndim = pyarr->nd;
  if( ndim>MaxLorrayRank )
    throwError(Type,ssprintf("array of rank %d, maximum supported is %d",ndim,MaxLorrayRank));
  LoShape shape(ndim|LoShape::SETRANK);
  for( uint i=0; i<ndim; i++ )
    shape[i] = pyarr->dimensions[i];
  TypeId tid = numarrayToTypeId(pyarr->descr->type_num);
  ulong nb = ulong(pyarr->itemsize)*shape.product();
  // create DataArray
  cdebug(3)<<"pyToArray("<<ObjStr(pyobj)<<": type "<<tid<<", shape "<<shape<<", "<<nb<<" bytes\n";
  arr <<= new DataArray(tid,shape);
  memcpy(arr().getDataPtr(),NA_OFFSETDATA(pyarr),nb);

  // success
  return 1;
}

// -----------------------------------------------------------------------
// makeField
// helper function to init/reuse a DataField, depending on the seqpos/seqlen 
// arguments.
// If seqlen>0, will check that objref contains a DF. If seqpos=0, will init
// that field with 'type', else check for type mismatch. 
// If seqlen=0, will simply init a scalar DF of the given type.
// Returns DF &, or throws/raises a TypeError on type mismatch.
// Can also throw something on other failure.
// -----------------------------------------------------------------------
static DataField & makeField (ObjRef &objref,int seqpos,int seqlen,TypeId type)
{
  string objstr = 
      Debug(4) ? ssprintf("PyToDMI-mf(%s,%d,%d): ",type.toString().c_str(),seqpos,seqlen) : string();
  DataField *pdf; 
  if( seqlen )
  {
    pdf = dynamic_cast<DataField *>(objref.dewr_p());
    FailWhen(!pdf,"seqlen>0 but objref is not a DataField");
    if( !seqpos )
    {
      cdebug(4)<<objstr<<"initializing new df("<<type<<","<<seqlen<<")\n";
      pdf->init(type,seqlen);
    }
    else if( pdf->type() != type )
    {
      cdebug(4)<<objstr<<"error assigning "<<type<<" to df("<<pdf->type()<<")\n";
      throwError(Type,"pyToDMI: mixed-type sequences not supported");
    }
  }
  else
  {
    cdebug(4)<<objstr<<"creating scalar df("<<type<<")\n";
    objref <<= pdf = new DataField(type);
  }
  return *pdf;
}

// -----------------------------------------------------------------------
// pyToDMI
// converts a Python object to a DMI object
// May be called in two modes, depending on whether the object is
// part of a sequence or not:
// (a) seqlen=0: create new container to hold object, return via objref.
//     This is for objects not part of a sequence.
// (b) seqlen>0: object is part of a sequence; objref must already contain
//     a DataField.
//     If seqpos=0, init the DataField with the object type and store at #0
//     If seqpos>0, check for type consistency, and store at #seqpos.
// -----------------------------------------------------------------------
int pyToDMI (ObjRef &objref,PyObject *obj,int seqpos,int seqlen)
{
  string objstr = 
      Debug(3) ? "PyToDMI("+ObjStr(obj)+"): " : string();
  cdebug(3)<<objstr<<"called for seq "<<seqpos<<"/"<<seqlen<<endl;
  // dmi_supported_types =
  // (int,long,float,complex,str,hiid,array_class,record,message);
  Assert(!seqpos || seqpos<seqlen);
  // this is really a switch calling different kinds of object builders
  if( PyInt_Check(obj) )
  {
    makeField(objref,seqpos,seqlen,Tpint)[seqpos] = int( PyInt_AS_LONG(obj) );
  }
  else if( PyLong_Check(obj) )
  {
    makeField(objref,seqpos,seqlen,Tplong)[seqpos] = PyLong_AsLong(obj);
    // check for overflow
    if( PyErr_Occurred() )
    {
      if( PyErr_ExceptionMatches(PyExc_OverflowError) )
        throwErrorOpt(Overflow,"overflow in long type");
      throwErrorOpt(Type,"unexpected error: "+string(PyErr_Occurred()->ob_type->tp_name));
    }
  }
  else if( PyFloat_Check(obj) )
  {
    makeField(objref,seqpos,seqlen,Tpdouble)[seqpos] = PyFloat_AS_DOUBLE(obj);
  }
  else if( PyComplex_Check(obj) )
  {
    Py_complex pc = PyComplex_AsCComplex(obj);
    makeField(objref,seqpos,seqlen,Tpdcomplex)[seqpos] = dcomplex(pc.real,pc.imag);
  }
  else if( PyString_Check(obj) )
  {
    makeField(objref,seqpos,seqlen,Tpstring)[seqpos] = PyString_AS_STRING(obj);
  }
  else if( PyObject_IsInstance(obj,py_class.record) ) // try to convert mappings to DataRecords
  {
    DataRecord::Ref rec;
    pyToRecord(rec,obj);
    if( seqlen )
      makeField(objref,seqpos,seqlen,TpDataRecord)[seqpos] <<= rec;
    else
      objref <<= rec;
  }
  else if( PyObject_IsInstance(obj,py_class.hiid) )
  {
    HIID id;
    pyToHIID(id,obj);
    makeField(objref,seqpos,seqlen,TpHIID)[seqpos] = id;
  }
  else if( PyObject_IsInstance(obj,py_class.array_class) )
  {
    DataArray::Ref arr;
    pyToArray(arr,obj);
    if( seqlen )
      makeField(objref,seqpos,seqlen,TpDataArray)[seqpos] <<= arr;
    else
      objref <<= arr;
  }
  else if( PyObject_IsInstance(obj,py_class.message) )
  {
    Message::Ref msg;
    pyToMessage(msg,obj);
    if( seqlen )
      makeField(objref,seqpos,seqlen,TpDataArray)[seqpos] <<= msg;
    else
      objref <<= msg;
  }
  else if( PySequence_Check(obj) )  // process a sequence
  {
    // check if we're actually an item in another sequence
    DataField *pdf,*pdf0=0; 
    ObjRef dfref; // this is where the sequence is stored
    if( seqlen )
    {
      pdf0 = &( makeField(objref,seqpos,seqlen,TpDataField) );
      dfref <<= pdf = new DataField;
    }
    else
    {
      objref <<= pdf = new DataField;
      dfref <<= pdf;
    }
    // pdf now points to a new DataField for our sequence.
    int len = PySequence_Size(obj);
    cdebug(3)<<objstr<<"converting seq of "<<len<<" objects\n";
    // if len=0, we'll be left with an uninitialized DF, which is exactly
    // what we use to represent an empty sequence
    for( int i=0; i<len; i++ )
    {
      cdebug(4)<<objstr<<"converting seq element "<<i<<endl;
      PyObjectRef item = PySequence_GetItem(obj,i);
      pyToDMI(dfref,*item,i,len);
      // We do not trap any exceptions here:
      // Failure to convert any item in the sequence (=exception) will be
      // passed up to caller (i.e. entire sequence will fail).
    }
    // success, sequence converted: insert into parent sequence, if required
    if( pdf0 )
      (*pdf0)[seqpos] <<= pdf;
    cdebug(3)<<objstr<<"successfully converted seq of "<<len<<" objects\n";
  }
  else // non-supported type
  {
    string type = obj->ob_type->tp_name;
    cdebug(3)<<objstr<<"type "<<type<<" not supported"<<endl;
    throwError(Type,"dmi: type "+type+" not supported");
  }
  // success, objref should be filled
  Assert(objref.valid());
  return 1;
}


// inline helper functions for pyFromField below
inline PyObject * PyComplex_FromDComplex (const dcomplex &x)
{
  return PyComplex_FromDoubles(x.real(),x.imag());
}

inline PyObject * pyFromObjRef (const ObjRef &ref)
{
  return pyFromDMI(*ref);
}

// -----------------------------------------------------------------------
// pyFromField
// converts a DataField to a Python scalar or tuple
// -----------------------------------------------------------------------
PyObject * pyFromField (const DataField &df)
{
  // empty/uninit field -- return empty tuple
  if( !df.valid() )
  {
    cdebug(3)<<"pyFromDF: null DataField, returning ()\n";
    return PyTuple_New(0);
  }
  TypeId type = df.type();
  const TypeInfo &typeinfo = TypeInfo::find(type);
  int num = df.size();
  PyObjectRef tuple;
  if( df.isScalar() ) // scalar field: will be returned directly
  {
    cdebug(3)<<"pyFromDF: will return scalar "<<type<<endl;
  }
  else   // non-scalar field: allocate a tuple
  {
    tuple = PyTuple_New(num);
    if( !tuple )
      throwErrorOpt(Runtime,"failed to create a tuple");
    cdebug(3)<<"pyFromDF: creating tuple of "<<num<<" "<<type<<"s\n";
  }
  // Define macro to extract field contents and assign to tuple, or else
  // return immediately.
  // Note that all the PyFuncs called here return a new reference,
  // while PyTuple_SET_ITEM  steals a reference, so we don't bother
  // with ref counts.
  #define extractField(pyfunc,hookfunc) \
    { if( tuple ) { \
        cdebug(4)<<"using "<<num<<" " #pyfunc "(df[i]." #hookfunc "())\n"; \
        for( int i=0; i<num; i++ ) \
          PyTuple_SET_ITEM(*tuple,i,pyfunc(df[i].hookfunc())); \
      } else { \
        cdebug(4)<<"using scalar " #pyfunc "(df." #hookfunc "())\n"; \
        return pyfunc(df[HIID()].hookfunc()); } }
  // now proceed depending on object type
  if( typeinfo.category == TypeCategories::NUMERIC )
  {
    if( type <= Tpbool && type >= Tplong )
      extractField(PyInt_FromLong,as<long>)
    else if( type <= Tpulong && type >= Tplonglong )
      extractField(PyLong_FromLongLong,as<longlong>)
    else if( type == Tpulonglong )
      extractField(PyLong_FromLongLong,as<ulonglong>)
    else if( type <= Tpfloat && type >= Tpldouble )
      extractField(PyFloat_FromDouble,as<double>)
    else if( type <= Tpfcomplex && type >= Tpdcomplex )
      extractField(PyComplex_FromDComplex,as<dcomplex>)
    else
      throwError(Runtime,"unexpected numeric DMI type "+type.toString());
  }
  else if( type == Tpstring )
    extractField(pyFromString,as<string>)
  else if( type == TpHIID )
    extractField(pyFromHIID,as<HIID>)
  else if( typeinfo.category == TypeCategories::DYNAMIC )
    extractField(pyFromObjRef,ref)
  else
    throwError(Type,"DMI type "+type.toString()+" not supported by Python");
  // if we got here, we've formed a tuple
  // (scalars should have been returned directly from the if-else blocks above)
  Assert(tuple);
  return ~tuple; // return new ref, stealing from ours
}

// -----------------------------------------------------------------------
// pyFromRecord
// converts a DataRecord to a Python record instance
// -----------------------------------------------------------------------
PyObject * pyFromRecord (const DataRecord &dr)
{
  cdebug(3)<<"pyFromRecord: converting DataRecord"<<endl;
  PyObjectRef pyrec = PyObject_CallObject(py_class.record,NULL);
  if( !pyrec )
    throwErrorOpt(Runtime,"failed to create a record instance");
  // insert __dmi_type tag, if object is a subclass of record
  TypeId objtype = dr.objectType();
  if( objtype != TpDataRecord )
  {
    cdebug(3)<<"pyFromRecord: actual DMI type is "<<objtype<<endl;
    PyObjectRef type = PyString_FromString(const_cast<char*>(objtype.toString().c_str()));
    if( PyObject_SetAttrString(*pyrec,const_cast<char*>(dmi_type_tag),*type) < 0 )
      throwErrorOpt(Runtime,"failed to set attribute");
  }
  DataRecord::Iterator iter = dr.initFieldIter();
  HIID id; NestableContainer::Ref content;
  while( dr.getFieldIter(iter,id,content) )
  {
    cdebug(4)<<"pyFromRecord: "<<id<<" contains "<<content->objectType()<<endl;
    string idstr = id.toString('_');
    PyObjectRef value = pyFromDMI(*content,EP_CONV_ERROR);
    if( value )
    {
      cdebug(4)<<"pyFromRecord: setting field "<<idstr<<" from "<<content->objectType()<<endl;
      // this does not steal our ref
      PyDict_SetItemString(*pyrec,const_cast<char*>(idstr.c_str()),*value);
    }
    else
    {
      cdebug(4)<<"pyFromRecord: conversion from "<<content->objectType()<<" failed, skipping field "<<idstr<<endl;
      // set error value?
    }
  }
  cdebug(3)<<"pyFromRecord: converted "<<PyDict_Size(*pyrec)<<" fields\n";
  return ~pyrec;
}

// -----------------------------------------------------------------------
// pyFromArray
// converts a DataArray to a Numarray instance
// -----------------------------------------------------------------------
PyObject * pyFromArray (const DataArray &da)
{
  // get rank & shape into terms that Numarray understands
  int rank = da.rank();
  maybelong dims[rank];
  for( int i=0; i<rank; i++ )
    dims[i] = da.shape()[i];
  NumarrayType typecode = typeIdToNumarray(da.elementType());
  PyObjectRef pyarr = (PyObject*)
      NA_vNewArray(const_cast<void*>(da.getConstDataPtr()),typecode,rank,dims);
  return ~pyarr;
}

// -----------------------------------------------------------------------
// pyFromMessage
// -----------------------------------------------------------------------
PyObject * pyFromMessage (const Message &msg)
{
  // get payload
  PyObjectRef py_payload;
  const ObjRef &payload = msg.payload();
  if( payload.valid() )
    py_payload = pyFromDMI(*payload,EP_CONV_ERROR); 
  else
    py_payload = PyObjectRef(Py_None); // grab new ref to None
  
  // create message object
  PyObjectRef args = Py_BuildValue("(NNN)",
      pyFromHIID(msg.id()),
      ~py_payload,  // steal our ref since "N" is used
      PyInt_FromLong(msg.priority()-Message::PRI_NORMAL));
  if( !args )
    throwErrorOpt(Runtime,"failed to build args tuple");
  
  PyObjectRef py_msg = PyObject_CallObject(py_class.message,*args);
  if( !py_msg )
    throwErrorOpt(Runtime,"failed to create a message instance");
  
  // create additional attributes
  // we use PyObjectRefs here because the functions return new refs,
  // so ref counts do need to be decremented after calling SetAttrString.
  PyObject_SetAttrString(*py_msg,"from",PyObjectRef(pyFromHIID(msg.from())).obj());
  PyObject_SetAttrString(*py_msg,"to",PyObjectRef(pyFromHIID(msg.to())).obj());
  PyObject_SetAttrString(*py_msg,"state",PyObjectRef(PyInt_FromLong(msg.state())).obj());
  PyObject_SetAttrString(*py_msg,"hops",PyObjectRef(PyInt_FromLong(msg.hops())).obj());
  return ~py_msg;
}

// -----------------------------------------------------------------------
// pyFromDMI
// converts a DMI object (DataField, DataRecord, DataArray, Message)
// into a Python object.
// May be called in two modes, depending on whether the object is
// part of a sequence or not:
// (a) seqlen=0: create new container to hold object, return via objref.
//     This is for objects not part of a sequence.
// (b) seqlen>0: object is part of a sequence; objref must already contain
//     a DataField.
//     If seqpos=0, init the DataField with the object type and store at #0
//     If seqpos>0, check for type consistency, and store at #seqpos.
// -----------------------------------------------------------------------
PyObject * pyFromDMI (const BlockableObject &obj,int err_policy)
{
  try
  {
    TypeId type = obj.objectType();
    if( type == TpDataRecord )
      return pyFromRecord(dynamic_cast<const DataRecord &>(obj));
    else if( type == TpDataField )
      return pyFromField(dynamic_cast<const DataField &>(obj));
    else if( type == TpDataArray )
      return pyFromArray(dynamic_cast<const DataArray &>(obj));
    else if( type == TpMessage )
      return pyFromMessage(dynamic_cast<const Message &>(obj));
    else
      throwError(Type,"dmi type "+type.toString()+" not supported");
  }
  catch( std::exception &exc )
  {
    if( err_policy == EP_RETNULL )
    {
      cdebug(2)<<"pyFromDMI: exception "<<exc.what()<<", returning NULL\n";
      if( !PyErr_Occurred() )
        returnError(NULL,DataConv,exc);
      return NULL;
    }
    else if( err_policy == EP_CONV_ERROR )
    {
      cdebug(2)<<"pyFromDMI: exception "<<exc.what()<<", returning conv_error\n";
      return pyConvError(exc.what());
    }
    else // re-throw
    {
      cdebug(2)<<"pyFromDMI: exception "<<exc.what()<<", re-throwing\n";
      throw exc;
    }
  }
}

// -----------------------------------------------------------------------
// pyConvError
// Create a conv_error description
// -----------------------------------------------------------------------
PyObject * pyConvError (const string &msg)
{
  // create message object
  PyObjectRef args = Py_BuildValue("NO",
        pyFromString(msg), // new ref 
        PyErr_Occurred() ? PyErr_Occurred() : Py_None); // borrowed ref
  if( !args )
    throwErrorOpt(Runtime,"failed to build args tuple");
  PyErr_Clear();
  PyObjectRef converr = PyObject_Call(py_class.conv_error,*args,NULL);
  if( !converr )
    throwErrorOpt(Runtime,"failed to create a conv_error instance");
  return ~converr;
}


// -----------------------------------------------------------------------
// initDataConv()
// -----------------------------------------------------------------------
void initDataConv ()
{
  if( sizeof(Bool) != sizeof(NumarrayBool) )
  {
    Py_FatalError("C++ bool != numarray bool, conversion code must be added");
  }
  import_libnumarray();
}

}; // namespace OctoPython

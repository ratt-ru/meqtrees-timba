#define AIPSPP_HOOKS 1
    
#include <sys/time.h> 
#include <sys/types.h> 
#include <unistd.h> 
    
#include <aips/Glish.h>
#include <aips/Arrays/Array.h>
#include <aips/Arrays/ArrayMath.h>

#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
#include <DMI/DynamicTypeManager.h>
#include <DMI/AIPSPP-Hooks.h>
#include <DMI/Global-Registry.h>
#include <DMI/NCIter.h>

#include "AID-OCTOGlish.h"
#include "BlitzToAips.h"
#include "GlishUtil.h"

    
// creates a "Failed" GlishValue, used to indicate failed conversions
GlishArray GlishUtil::makeFailField ( const String &msg )
{
  GlishArray arr(msg);
  arr.addAttribute("failed_field",GlishArray(True));
  return arr;
}

// helper function to convert a container into a Glish array
bool GlishUtil::makeGlishArray (GlishArray &arr,const NestableContainer &nc,TypeId tid,bool isIndex )
{
  switch( tid.id() )
  {
    case Tpbool_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Bool>());
        break;
    case Tpuchar_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<uChar>());
        break;
    case Tpshort_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Short>());
        break;
    case Tpint_int:
    {
        Array<Int> intarr = nc[HIID()].as_AipsArray<Int>();
        if( isIndex )
          intarr += 1;
        arr = GlishArray(intarr);
        break;
    }
    case Tpfloat_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Float>());
        break;
    case Tpdouble_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Double>());
        break;
    case Tpfcomplex_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<Complex>());
        break;
    case Tpdcomplex_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<DComplex>());
        break;
    case Tpstring_int:
        arr = GlishArray(nc[HIID()].as_AipsArray<String>());
        break;
    case TpHIID_int:
    {
        NCConstIter<HIID> nci(nc[HIID()]);
        Vector<String> vec(nci.size());
        for( int i=0; i<nci.size(); i++,nci++ )
          vec[i] = strlowercase( (*nci).toString() );
        arr = GlishArray(vec);
        arr.addAttribute("is_hiid",GlishArray(True));
        break;
    }
    default:
        return False; // non-supported type
  }
  return True;
}


//##ModelId=3DB9369202CC
// converts DataRecord to GlishRecord
GlishRecord GlishUtil::recToGlish (const DataRecord &rec)
{
  #ifdef USE_THREADS
  Thread::Mutex::Lock lock(rec.mutex());
  #endif
  GlishRecord glrec;
  DataRecord::Iterator iter = rec.initFieldIter();
  HIID id;
  NestableContainer::Ref ncref;
  // iterate over all fields in record
  while( rec.getFieldIter(iter,id,ncref) )
  {
    // map HIID to record field name
    string name = strlowercase( id.toString('_') );
    // is it an index field (i.e. base needs to be adjusted?)
    bool adjustIndex = ( id.back() == AidIndex );
    try
    {
      glrec.add(name,objectToGlishValue(*ncref,adjustIndex));
    }
    // catch all exceptions and convert them to "fail" fields
    catch( std::exception &exc )
    {
      glrec.add(name,makeFailField(exc.what()));
    }
    catch( AipsError &err )
    {
      glrec.add(name,makeFailField(err.getMesg()));
    }
    catch( ... )
    {
      glrec.add(name,makeFailField("unknown exception"));
    }
  }
  return glrec;
}

// Converts a BlockableObject to a GlishValue.
//    (if adjustIndex is true, int values will be incremented by 1.)
// DataArrays, DataRecords and DataFields are converted to arrays & records
// All other object types are converted to blocksets.
GlishValue GlishUtil::objectToGlishValue (const BlockableObject &obj,bool adjustIndex)
{
  TypeId type = obj.objectType();
  // Mapping of objects:
  // 1. DataArray
  //    1.1. Glish type: map field to array
  //    1.2. non-Glish type: map field to blockset
  // 2. DataRecord: map to a subrecord
  // 3. DataField:
  //    3.1. Glish type: maps field to 1D array or scalar
  //    3.2. Container type: recursively map to record of records 
  //    3.3. Other type: map to blockset
  // 4. All others: map to blockset
  if( type == TpDataArray )  // (case 1)
  {
    const DataArray &dataarray = dynamic_cast<const DataArray &>(obj);
    Thread::Mutex::Lock lock(dataarray.mutex());
    GlishArray arr;
    // convert to array and add (case 1.1)
    if( makeGlishArray(arr,dataarray,dataarray.elementType(),adjustIndex) )
    {
      arr.addAttribute("is_dataarray",GlishArray(True));
      return arr;
    }
  }
  else if( type == TpDataRecord ) // (case 2)
  {
    const DataRecord &rec = dynamic_cast<const DataRecord &>(obj);
    Thread::Mutex::Lock lock(rec.mutex());
    return recToGlish(rec);
  }
  else if( type == TpDataField ) // (case 3)
  {
    const DataField &datafield = dynamic_cast<const DataField &>(obj);
    Thread::Mutex::Lock lock(datafield.mutex());
    TypeId fieldtype = datafield.type();
    // a numeric/string/HIID type? (case 3.1)
    if( TypeInfo::isNumeric(fieldtype) || fieldtype == Tpstring || fieldtype == TpHIID )
    {
      GlishArray arr;
      // try to map to a Glish array
      if( makeGlishArray(arr,datafield,fieldtype,adjustIndex) )
      {
        arr.addAttribute("is_datafield",GlishArray(True));
        return arr;
      }
    }
    else if( NestableContainer::isNestable(fieldtype) ) // case (3.2)
    {
      // map to record of records, with fields "0", "1", etc.
      GlishRecord subrec;
      for( int i=0; i<datafield.mysize(); i++ )
      {
        ObjRef ref = datafield.objref(i);
        string name = ssprintf("%d",i);
        subrec.add(ssprintf("%d",i),objectToGlishValue(*ref,adjustIndex));
      }
      subrec.addAttribute("is_datafield",GlishArray(True));
      return subrec;
    }
  }
  // catch-all for failed mappings: converts to a blockset
  return objectToBlockRec(obj);
}

// helper function to create a DataField from a GlishArray
template<class T> 
void GlishUtil::newDataField (ObjRef &ref,const GlishArray &arr)
{
  Array<T> array;
  arr.get(array);
  bool del;
  const T * data = array.getStorage(del);
  ref <<= new DataField(typeIdOf(T),array.nelements(),DMI::WRITE,data);
  array.freeStorage(data,del);
}

// helper template to create a new DataArray from a GlishArray
// of the template argument type
template<class T> 
void GlishUtil::newDataArray (ObjRef &ref,const GlishArray &arr)
{
  Array<T> array;
  arr.get(array);
  ref <<= new DataArray(array,DMI::WRITE);
}

// helper function creates a DataArray from a GlishArray
ObjRef GlishUtil::makeDataArray (const GlishArray &arr,bool isIndex)
{
  ObjRef ref;
  switch( arr.elementType() )
  {
    case GlishArray::BOOL:      
        newDataArray<Bool>(ref,arr);
        return ref;
        
    case GlishArray::BYTE:
        newDataArray<uChar>(ref,arr);
        return ref;
        
    case GlishArray::SHORT:
        newDataArray<Short>(ref,arr);
        return ref;
    
    case GlishArray::INT: // explicitly adjust for index
    {
        Array<Int> array;
        arr.get(array);
        if( isIndex )
          array -= 1;
        ref <<= new DataArray(array);
        return ref;
    }
    
    case GlishArray::FLOAT:
        newDataArray<Float>(ref,arr);
        return ref;
    
    case GlishArray::DOUBLE:
        newDataArray<Double>(ref,arr);
        return ref;
    
    case GlishArray::COMPLEX:
        newDataArray<Complex>(ref,arr);
        return ref;
    
    case GlishArray::DCOMPLEX:
        newDataArray<DComplex>(ref,arr);
        return ref;
    
    case GlishArray::STRING: 
        Throw("oops, we shouldn't be here");
        // newDataField<String>(ref,arr);
        return ref;
    
    default:
        dprintf(2)("warning: unknown Glish array type %d, ignoring\n",arr.elementType());
        ref <<= new DataArray;
        return ref;
  }
}

// helper function creates a DataField from a GlishArray (must be 1D)
ObjRef GlishUtil::makeDataField (const GlishArray &arr,bool isIndex)
{
  ObjRef ref;
  switch( arr.elementType() )
  {
    case GlishArray::BOOL:      
        newDataField<Bool>(ref,arr);
        return ref;
    case GlishArray::BYTE:
        newDataField<uChar>(ref,arr);
        return ref;
    case GlishArray::SHORT:
        newDataField<Short>(ref,arr);
        return ref;
    
    case GlishArray::INT: // explicitly adjust for index
    {
        Array<Int> array;
        arr.get(array);
        if( isIndex )
          array -= 1;
        bool del;
        const Int * data = array.getStorage(del);
        ref <<= new DataField(Tpint,array.nelements(),DMI::WRITE,data);
        array.freeStorage(data,del);
        return ref;
    }
    
    case GlishArray::FLOAT:
        newDataField<Float>(ref,arr);
        return ref;
    
    case GlishArray::DOUBLE:
        newDataField<Double>(ref,arr);
        return ref;
    
    case GlishArray::COMPLEX:
        newDataField<Complex>(ref,arr);
        return ref;
    
    case GlishArray::DCOMPLEX:
        newDataField<DComplex>(ref,arr);
        return ref;
    
    case GlishArray::STRING: 
    {
        Vector<String> array;
        arr.get(array);
        bool is_hiid = arr.attributeExists("is_hiid");
        DataField *field = new DataField(is_hiid ? TpHIID : Tpstring,array.nelements(),DMI::WRITE);
        ref <<= field;
        if( is_hiid )
        {
          for( uint i=0; i < array.nelements(); i++ )
            (*field)[i] = HIID(array(i));
        }
        else
        {
          for( uint i=0; i < array.nelements(); i++ )
            (*field)[i] = array(i);
        }
        return ref;
    }
    
    default:
        dprintf(2)("warning: unknown Glish array type %d, ignoring\n",arr.elementType());
        ref <<= new DataField;
        return ref;
  }
}

// Converts any glish value to an object
// (DataRecord, DataArray or DataField)
ObjRef GlishUtil::glishValueToObject (const GlishValue &val,bool adjustIndex)
{
  if( val.type() == GlishValue::ARRAY )
  {
    GlishArray arr = val;
    IPosition shape = arr.shape();
    // string arrays, or 1D arrays marked with the "is_datafield" or 
    // "is_hiid" attribute map to DataField
    if( ( shape.nelements() == 1 && ( val.attributeExists("is_datafield") || 
                                      val.attributeExists("is_hiid") ) )
        || arr.elementType() == GlishArray::STRING )
      return makeDataField(arr,adjustIndex);
    else // other arrays map to DataArrays
      return makeDataArray(arr,adjustIndex);
  }
  else // it's a record
  {
    GlishRecord glrec = val;
    // is it a non-Glish object passed as a block record?
    if( glrec.attributeExists("blocktype")  )
    {
      return ObjRef( blockRecToObject(glrec),DMI::ANONWR );
    }
    // is it a DataField (that was passed in as a record of values)
    else if( glrec.attributeExists("is_datafield")  )
    {
      // the attribute should be a string indicating the object type
      String typestr;
      GlishArray tmp = glrec.getAttribute("is_datafield"); tmp.get(typestr);
      TypeId fieldtype(typestr);
      // create a field and populate it with the objects recursively
      ObjRef fieldref;
      DataField *field = new DataField(fieldtype,glrec.nelements());
      fieldref <<= field;
      for( uint i=0; i < glrec.nelements(); i++ )
      {
        try 
        {
          (*field)[i] <<= glishValueToObject(glrec.get(i),adjustIndex);
        }
        catch( std::exception &exc )
        {
          dprintf(2)("warning: ignoring field [%d] (got exception: %s)\n",
              i,exc.what());
        }
        catch( AipsError &err )
        {
          dprintf(2)("warning: ignoring field [%d] (got exception: %s)\n",
              i,err.getMesg().c_str());
        }
        catch( ... )
        {
          dprintf(2)("warning: ignoring field [%d] (got unknown exception)\n",i);
        }
      }
      return fieldref;
    }
    // else it's a plain old DataRecord
    else
    {
      ObjRef recref;
      DataRecord *rec = new DataRecord;
      recref <<= rec;
      for( uint i=0; i < glrec.nelements(); i++ )
      {
        string field_name = glrec.name(i);
        try // handle failed fields gracefully
        {
          HIID id(field_name,"_");
          GlishValue subval = glrec.get(i);
          bool isIndex = ( id[id.size()-1] == AidIndex );
          (*rec)[id] <<= glishValueToObject(subval,isIndex);
        }
        catch( std::exception &exc )
        {
          dprintf(2)("warning: ignoring field %s[%d] (got exception: %s)\n",
              field_name.c_str(),i,exc.what());
        }
        catch( AipsError &err )
        {
          dprintf(2)("warning: ignoring field %s[%d] (got exception: %s)\n",
              field_name.c_str(),i,err.getMesg().c_str());
        }
        catch( ... )
        {
          dprintf(2)("warning: ignoring field %s[%d] (got unknown exception)\n",
              field_name.c_str(),i);
        }
      }
      return recref;
    }
  }
}

//##ModelId=3DB936930231
// Converts object to blockset representation (i.e. a glish record of
// byte arrays corresponding to the blocks)
GlishRecord GlishUtil::objectToBlockRec (const BlockableObject &obj)
{
  GlishRecord rec;
  BlockSet set;
  obj.toBlock(set);
  rec.addAttribute("blocktype",GlishArray(obj.objectType().toString()));
  int i=0;
  while( set.size() )
  {
    char num[32];
    sprintf(num,"%d",i++);
    rec.add(num,Array<uChar>(IPosition(1,set.front()->size()),
                static_cast<uChar*>(const_cast<void*>(set.front()->data())),COPY));
    set.pop();
  }
  return rec;
}

//##ModelId=3DB93695024D
BlockableObject * GlishUtil::blockRecToObject (const GlishRecord &rec)
{
  FailWhen( !rec.attributeExists("blocktype"),"missing 'blocktype' attribute" );
  String typestr;
  GlishArray tmp = rec.getAttribute("blocktype"); tmp.get(typestr);
  TypeId tid(typestr);
  FailWhen( !tid,"illegal blocktype "+static_cast<string>(typestr) );
  // extract blockset form record
  BlockSet set;
  for( uint i=0; i<rec.nelements(); i++ )
  {
    Array<uChar> arr;
    tmp = rec.get(i); tmp.get(arr);
    // create SmartBlock and copy data from array
    size_t sz = arr.nelements();
    SmartBlock *block = new SmartBlock(sz);
    set.pushNew().attach(block,DMI::WRITE|DMI::ANON);
    if( sz )
    {
      Bool del;
      const uChar * data = arr.getStorage(del);
      memcpy(block->data(),data,sz);
      arr.freeStorage(data,del);
    }
  }
  // create object & return
  return DynamicTypeManager::construct(tid,set);
}


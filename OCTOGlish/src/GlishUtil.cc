#define AIPSPP_HOOKS 1
    
#include <sys/time.h> 
#include <sys/types.h> 
#include <unistd.h> 
    
#include <aips/Glish.h>
#include <aips/Arrays/Array.h>
#include <aips/Arrays/ArrayMath.h>

#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataList.h>
#include <DMI/DataArray.h>
#include <DMI/DynamicTypeManager.h>
#include <DMI/AIPSPP-Hooks.h>
#include <DMI/Global-Registry.h>
#include <DMI/NCIter.h>

#include "AID-OCTOGlish.h"
#include "BlitzToAips.h"
#include "GlishUtil.h"

InitDebugContext(GlishUtil::GlishUtilDebugContext,"Glish");

namespace GlishUtil {
  inline string sdebug (int=0,const string & = "",const char * = 0) { return "Glish"; }
};

// creates a "Failed" GlishValue, used to indicate failed conversions
GlishArray GlishUtil::makeFailField ( const String &msg )
{
  GlishArray arr(msg);
  arr.addAttribute("dmi_failed_field",GlishArray(True));
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
        arr.addAttribute("dmi_is_hiid",GlishArray(True));
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
    // convert HIID to record field name
    string name = strlowercase( id.toString('_') );
    bool adjustIndex = False;
    // if a single numeric index, convert to anon field form "#xxx"
    if( id.size() == 1 && id.front().index() >= 0 )
      name = '#'+name;
    else
      // is it an ".Index" field (i.e. base needs to be adjusted?)
      adjustIndex = id.back() == AidIndex;
    try
    {
      glrec.add(name,objectToGlishValue(*ncref,adjustIndex));
    }
    // catch all exceptions and convert them to "fail" fields
    catch( std::exception &exc )
    {
      glrec.add(name,makeFailField(exc.what()));
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
  string type_string = type.toString();
  string type_isattr = "dmi_is_" + strlowercase(type_string);
  // Mapping of objects:
  // 1. DataRecord or descendant: map to a record
  // 2. DataField or descendant:
  //    2.1. Glish type: maps field to 1D array or scalar
  //    2.2. Container type: recursively map to record of records 
  //    2.3. Other type: map to blockset (see 4)
  //    2.4. Invalid (empty) field: maps to [] array
  // 3. DataArray
  //    3.1. Glish type: map field to array
  //    3.2. non-Glish type: map to blockset (see 5)
  // 4. DataList or descendant: maps to record with attributes
  // 5. All others: map to a blockset with appropriate attributes
  if( dynamic_cast<const DataRecord *>(&obj) ) // (case DataRecord)
  {
    const DataRecord &rec = dynamic_cast<const DataRecord &>(obj);
#ifdef USE_THREADS
    Thread::Mutex::Lock lock(rec.mutex());
#endif
    GlishValue val = recToGlish(rec);
    val.addAttribute("dmi_actual_type",GlishArray(type_string));
    val.addAttribute("dmi_is_datarecord",GlishArray(True));
    return val;
  }
  else if( dynamic_cast<const DataField *>(&obj) ) // (case DataField)
  {
    const DataField &datafield = dynamic_cast<const DataField &>(obj);
#ifdef USE_THREADS
    Thread::Mutex::Lock lock(datafield.mutex());
#endif
    TypeId fieldtype = datafield.type();
    // an invalid field? (case 2.4)
    if( !datafield.valid() )
    {
      return GlishArray(Array<Int>());
    }
    // a numeric/string/HIID type? (case 2.1)
    else if( TypeInfo::isNumeric(fieldtype) || fieldtype == Tpstring || fieldtype == TpHIID )
    {
      GlishArray arr;
      // try to map to a Glish array
      if( makeGlishArray(arr,datafield,fieldtype,adjustIndex) )
      {
        arr.addAttribute("dmi_actual_type",GlishArray(type_string));
        arr.addAttribute("dmi_datafield_content_type",GlishArray(datafield.type().toString()));
        arr.addAttribute("dmi_is_datafield",GlishArray(True));
        return arr;
      }
    }
    else if( NestableContainer::isNestable(fieldtype) ) // case (2.2)
    {
      // map to record of records, with fields "#1", "#2", etc.
      GlishRecord subrec;
      for( int i=0; i<datafield.mysize(); i++ )
      {
        ObjRef ref = datafield.objref(i);
        subrec.add(ssprintf("#%d",i+1),objectToGlishValue(*ref,adjustIndex));
      }
      subrec.addAttribute("dmi_actual_type",GlishArray(type_string));
      subrec.addAttribute("dmi_datafield_content_type",GlishArray(datafield.type().toString()));
      subrec.addAttribute("dmi_is_datafield",GlishArray(True));
      return subrec;
    }
  }
  else if( dynamic_cast<const DataList *>(&obj) )  // (case DataList)
  {
    const DataList &datalist = dynamic_cast<const DataList &>(obj);
#ifdef USE_THREADS
    Thread::Mutex::Lock lock(datalist.mutex());
#endif
    // map to record, with fields "#1", "#2", etc.
    GlishRecord rec;
    for( int i=0; i<datalist.numItems(); i++ )
    {
      NestableContainer::Ref ref = datalist.getItem(i);
      rec.add(ssprintf("#%d",i+1),objectToGlishValue(*ref,adjustIndex));
    }
    rec.addAttribute("dmi_actual_type",GlishArray(type_string));
    rec.addAttribute("dmi_is_datalist",GlishArray(True));
    return rec;
  }
  else if( dynamic_cast<const DataArray *>(&obj) )  // (case DataArray)
  {
    const DataArray &dataarray = dynamic_cast<const DataArray &>(obj);
#ifdef USE_THREADS
    Thread::Mutex::Lock lock(dataarray.mutex());
#endif
    GlishArray arr;
    // convert to array and add (case 3.1)
    if( makeGlishArray(arr,dataarray,dataarray.elementType(),adjustIndex) )
    {
      arr.addAttribute("dmi_actual_type",GlishArray(type.toString()));
      return arr;
    }
  }
  // catch-all for (4) and all failed mappings: converts to a blockset
  return objectToBlockRec(obj);
}

// helper function to create a DataField from a GlishArray
template<class T> 
void GlishUtil::initDataField (DataField &field,const GlishArray &arr)
{
  Array<T> array;
  arr.get(array);
  bool del;
  const T * data = array.getStorage(del);
  field.init(typeIdOf(T),array.nelements(),data);
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
        // initDataField<String>(arr,arr);
        return ref;
    
    default:
        dprintf(2)("warning: unknown Glish array type %d, ignoring\n",arr.elementType());
        ref <<= new DataArray;
        return ref;
  }
}

// helper function creates a DataField from a GlishArray (must be 1D)
void GlishUtil::makeDataField (DataField &field,const GlishArray &arr,bool isIndex)
{
  ObjRef ref;
  switch( arr.elementType() )
  {
    case GlishArray::BOOL:      
        initDataField<Bool>(field,arr);
        break;
    case GlishArray::BYTE:
        initDataField<uChar>(field,arr);
        break;
    case GlishArray::SHORT:
        initDataField<Short>(field,arr);
        break;
    // INT arrays may need to be explicitly adjust for index base
    case GlishArray::INT: 
    {
        Array<Int> array;
        arr.get(array);
        if( isIndex )
          array -= 1;
        bool del;
        const Int * data = array.getStorage(del);
        field.init(Tpint,array.nelements(),data);
        array.freeStorage(data,del);
        break;
    }
    case GlishArray::FLOAT:
        initDataField<Float>(field,arr);
        break;
    case GlishArray::DOUBLE:
        initDataField<Double>(field,arr);
        break;
    case GlishArray::COMPLEX:
        initDataField<Complex>(field,arr);
        break;
    case GlishArray::DCOMPLEX:
        initDataField<DComplex>(field,arr);
        break;
    case GlishArray::STRING: 
    {
        Vector<String> array;
        arr.get(array);
        bool is_hiid = arr.attributeExists("dmi_is_hiid");
        field.init(is_hiid?TpHIID:Tpstring,array.nelements());
        if( is_hiid )
        {
          for( uint i=0; i < array.nelements(); i++ )
            field[i] = HIID(array(i));
        }
        else
        {
          for( uint i=0; i < array.nelements(); i++ )
            field[i] = array(i);
        }
        break;
    }
    
    default:
        dprintf(2)("warning: unsupported Glish array type %d, ignoring\n",arr.elementType());
  }
}

// createSubclass:
// Helper templated function. If val::dmi_actual_type exists, it is interpreted
// as a type string, and an object of that type is created and returned 
// (must be a subclass of Base). Otherwise, a Base is created & returned. 
// If val::dmi_actual_type is not a legal type string, or not a subclass of Base,
// an exception is thrown.
// The ref is attached to the newly created object.
template<class Base>
Base * GlishUtil::createSubclass (ObjRef &ref,const GlishValue &val)
{
  Base *pbase;
  // the dmi_actual_type attribute specifies a subclass 
  if( val.attributeExists("dmi_actual_type" ) )
  {
    String typestr;
    GlishArray tmp = val.getAttribute("dmi_actual_type"); tmp.get(typestr);
    dprintf(4)("real object type is %s\n",typestr.c_str());
    BlockableObject * bo = DynamicTypeManager::construct(TypeId(typestr));
    ref <<= bo;
    pbase = dynamic_cast<Base *>(bo);
    FailWhen(!pbase,string(typestr)+"is not a subclass of "+TpOfPtr(pbase).toString());
  }
  else
  {
    ref <<= pbase = new Base;
  }
  dprintf(5)("%s created at address %x\n",pbase->objectType().toString().c_str(),(int)pbase);
  return pbase;
}

// Converts any glish value to an object
// (DataRecord, DataArray or DataField)
ObjRef GlishUtil::glishValueToObject (const GlishValue &val,bool adjustIndex)
{
  ObjRef ref; 
  if( val.type() == GlishValue::ARRAY )
  {
    GlishArray arr = val;
    IPosition shape = arr.shape();
    // empty arrays map to null DataFields
    if( shape.nelements() == 1 && shape[0] == 0 )
    {
      dprintf(4)("converting empty GlishArray to empty DataField\n");
      return ObjRef(new DataField,DMI::ANONWR);
    }
    // string arrays, or 1D arrays marked as a datafield (or as with the
    // "dmi_is_hiid" attribute) always map to a DataField
    else if( ( shape.nelements() == 1 && 
            ( val.attributeExists("dmi_datafield_content_type") || 
              val.attributeExists("dmi_is_datafield") || 
              val.attributeExists("dmi_is_hiid") ) )
          || arr.elementType() == GlishArray::STRING )
    {
      dprintf(4)("converting GlishArray of %d elements to DataField\n",
                  shape.product());
      DataField *field = GlishUtil::createSubclass<DataField>(ref,val);
      makeDataField(*field,arr,adjustIndex);
      // validate the field (no-op for DataField itself, but may be meaningful for subclasses)
      field->validateContent(); 
      return ref;
    }
    else // all other arrays map to DataArrays
    {
      dprintf(4)("converting GlishArray of %d elements to DataArray\n",
                  shape.product());
      return makeDataArray(arr,adjustIndex);
    }
  }
  else // it's a record
  {
    GlishRecord glrec = val;
    // is it a non-Glish object passed as a block record?
    if( glrec.attributeExists("dmi_blocktype")  )
    {
      dprintf(4)("interpreting glish record (%d fields) as a blockset\n",
                  glrec.nelements());
      return ObjRef( blockRecToObject(glrec),DMI::ANONWR );
    }
    // is it a DataField (that was passed in as a record of values)
    else if( glrec.attributeExists("dmi_is_datafield")  )
    {
      // the attribute should be a string indicating the object type
      String typestr;
      GlishArray tmp = glrec.getAttribute("dmi_datafield_content_type"); tmp.get(typestr);
      dprintf(4)("converting glish record (%d fields) to DataField(%s)\n",
                  glrec.nelements(),typestr.c_str()); 
      TypeId fieldtype(typestr);
      // create a field and populate it with the objects recursively
      DataField *field = GlishUtil::createSubclass<DataField>(ref,val);
      field->init(fieldtype,glrec.nelements());
      for( uint i=0;i<glrec.nelements(); i++ )
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
        catch( ... )
        {
          dprintf(2)("warning: ignoring field [%d] (got unknown exception)\n",i);
        }
      }
      field->validateContent();
      return ref;
    }
    // is it a DataList (that was passed in as a record of values)
    else if( glrec.attributeExists("dmi_is_datalist")  )
    {
      // the attribute should be a string indicating the object type
      dprintf(4)("converting glish record (%d fields) to DataList\n",
                  glrec.nelements()); 
      // create a list and populate it with the objects recursively
      DataList *list = GlishUtil::createSubclass<DataList>(ref,val);
      for( uint i=0;i<glrec.nelements(); i++ )
      {
        try 
        {
          (*list)[i] <<= glishValueToObject(glrec.get(i),adjustIndex);
        }
        catch( std::exception &exc )
        {
          dprintf(2)("warning: ignoring field [%d] (got exception: %s)\n",
              i,exc.what());
        }
        catch( ... )
        {
          dprintf(2)("warning: ignoring field [%d] (got unknown exception)\n",i);
        }
      }
      list->validateContent();
      return ref;
    }
    // else it's a plain old DataRecord
    else
    {
      dprintf(4)("converting glish record to DataRecord\n");
      DataRecord *rec = GlishUtil::createSubclass<DataRecord>(ref,val);
      for( uint i=0; i < glrec.nelements(); i++ )
      {
        string field_name = glrec.name(i);
        try // handle failed fields gracefully
        {
          GlishValue subval = glrec.get(i);
//          const Value & val = *(subval.value());
//          dprintf(4)("record field [%s]: glish_type %d\n",field_name.c_str(),val.Type());
          if( !subval.ok() || subval.isUnset() )
          {
            dprintf(4)("record field [%s]: !ok or isUnset, skipping\n",field_name.c_str());
            continue;
          }
          // check for ignore flag and skip field if it is set
          if( subval.attributeExists("dmi_ignore") )
          {
            bool ignore = False;
            GlishArray tmp = subval.getAttribute("dmi_ignore"); 
            tmp.get(ignore);
            if( ignore )
            {
              dprintf(4)("record field [%s]: dmi_ignore set, skipping\n",field_name.c_str());
              continue;
            }
          }
          dprintf(4)("record field [%s]\n",field_name.c_str());
          HIID id;
          // check for numbered fields, of the form /[*#][0-9]+/
          bool isnumber = ( field_name[0] == '*' || field_name[0] == '#' )
              && field_name.length()>1 
              && field_name.find_first_not_of("0123456789",1) == string::npos;
          // convert to HIID
          bool isIndex = False;
          if( isnumber )
          {
            id = HIID(AtomicID(atoi(field_name.c_str()+1)));
          }
          else
          {
            id = HIID(field_name,0,"_");
            isIndex = ( id[id.size()-1] == AidIndex );
          }
          dprintf(4)("maps to HIID '%s'\n",id.toString().c_str());
          (*rec)[id] <<= glishValueToObject(subval,isIndex);
        }
        catch( std::exception &exc )
        {
          dprintf(2)("warning: ignoring field %s[%d] (got exception: %s)\n",
              field_name.c_str(),i,exc.what());
        }
        catch( ... )
        {
          dprintf(2)("warning: ignoring field %s[%d] (got unknown exception)\n",
              field_name.c_str(),i);
        }
      }
      rec->validateContent();
      return ref;
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
  rec.addAttribute("dmi_blocktype",GlishArray(obj.objectType().toString()));
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
  FailWhen( !rec.attributeExists("dmi_blocktype"),"missing 'dmi_blocktype' attribute" );
  String typestr;
  GlishArray tmp = rec.getAttribute("dmi_blocktype"); tmp.get(typestr);
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
  dprintf(4)("constructing %s from %d blocks\n",tid.toString().c_str(),set.size());
  // create object & return
  return DynamicTypeManager::construct(tid,set);
}



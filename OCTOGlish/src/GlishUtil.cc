#define AIPSPP_HOOKS 1
    
#include <sys/time.h> 
#include <sys/types.h> 
#include <unistd.h> 
    
#include <tasking/Glish.h>
#include <casa/Arrays/Array.h>
#include <casa/Arrays/ArrayMath.h>

#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <DMI/List.h>
#include <DMI/NumArray.h>
#include <DMI/DynamicTypeManager.h>
#include <DMI/AIPSPP-Hooks.h>
#include <DMI/Global-Registry.h>
#include <DMI/ContainerIter.h>
#include <DMI/Exception.h>
#include <Common/BlitzToAips.h>

#include "AID-OCTOGlish.h"
#include "GlishUtil.h"

// using namespace LOFAR;
using namespace DMI;
using namespace casa;

InitDebugContext(GlishUtil::GlishUtilDebugContext,"Glish");

namespace GlishUtil {
  inline string sdebug (int=0,const string & = "",const char * = 0) { return "Glish"; }
};

static bool isIndexString (const string &str)
{
  const string index = strlowercase(AidIndex.toString());
  const uint index_len = index.length();
  int pos = str.length() - index_len;
  if( pos == 0 )
    return strlowercase(str) == index;
  else if( pos > 0 )
    return strlowercase(str.substr(pos)) == index;
  else
    return false;
}


// creates a "Failed" casa::GlishValue, used to indicate failed conversions
GlishArray GlishUtil::makeFailField ( const String &msg )
{
  GlishArray arr(msg);
  arr.addAttribute("dmi_failed_field",GlishArray(true));
  return arr;
}

GlishArray GlishUtil::makeMissingValue ()
{
  GlishArray arr(False);
  arr.addAttribute("dmi_none_value",GlishArray(true));
  return arr;
}

GlishArray GlishUtil::makeEmptyObject (TypeId tid)
{
  GlishArray arr(False);
  arr.addAttribute("dmi_empty_object",GlishArray(tid.toString()));
  return arr;
}

// helper function to convert a container into a Glish array
bool GlishUtil::makeGlishArray (GlishArray &arr,const DMI::Container &nc,TypeId tid,bool isIndex )
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
    case TpDMIHIID_int:
    {
        ConstContainerIter<HIID> nci(nc[HIID()]);
        Vector<String> vec(nci.size());
        for( int i=0; i<nci.size(); i++,nci++ )
          vec[i] = strlowercase( (*nci).toString() );
        arr = GlishArray(vec);
        arr.addAttribute("dmi_is_dmihiid",GlishArray(true));
        break;
    }
    default:
        return false; // non-supported type
  }
  return true;
}


//##ModelId=3DB9369202CC
// converts DMI::Record to GlishRecord
GlishRecord GlishUtil::recToGlish (const DMI::Record &rec)
{
  #ifdef USE_THREADS
  Thread::Mutex::Lock lock(rec.mutex());
  #endif
  GlishRecord glrec;
  for( DMI::Record::const_iterator iter = rec.begin(); iter != rec.end(); iter++ )
  {
    const HIID &id = iter.id();
    const ObjRef & content = iter.ref(); 
    // convert HIID to record field name
    string name;
    // if a single numeric index, convert to anon field form "#xxx"
    if( id.size() == 1 && id.front().index() >= 0 )
      name = Debug::ssprintf("#%d",id.front().index()+1);
    else
      name = strlowercase( id.toString('_',false) ); // do not mark literals with "$"
    bool adjustIndex = isIndexString(name);
    try
    {
      if( content.valid() )
        glrec.add(name,objectToGlishValue(*content,adjustIndex));
      else
        glrec.add(name,makeMissingValue());
    }
    // catch all exceptions and convert them to "fail" fields
    catch( std::exception &exc )
    {
      glrec.add(name,makeFailField(exceptionToString(exc)));
    }
    catch( ... )
    {
      glrec.add(name,makeFailField("unknown exception"));
    }
  }
  return glrec;
}

// Converts a DMI::BObj to a casa::GlishValue.
//    (if adjustIndex is true, int values will be incremented by 1.)
// DMI::NumArrays, DMI::Records and DMI::Vecs are converted to arrays & records
// All other object types are converted to blocksets.
casa::GlishValue GlishUtil::objectToGlishValue (const DMI::BObj &obj,bool adjustIndex)
{
  TypeId type = obj.objectType();
  string type_string = type.toString();
  string type_isattr = "dmi_is_" + strlowercase(type_string);
  // Mapping of objects:
  // 1. DMI::Record or descendant: map to a record
  // 2. DMI::Vec or descendant:
  //    2.1. Glish type: maps field to 1D array or scalar
  //    2.2. Object type: recursively map to record of stuff
  //    2.3. Other type: map to blockset (see 4)
  //    2.4. Invalid (empty) field: maps to [] array
  // 3. DMI::NumArray
  //    3.1. Glish type: map field to array
  //    3.2. non-Glish type: map to blockset (see 5)
  // 4. DMI::List or descendant: maps to record with attributes
  // 5. All others: map to a blockset with appropriate attributes
  if( dynamic_cast<const DMI::Record *>(&obj) ) // (case DMI::Record)
  {
    const DMI::Record &rec = dynamic_cast<const DMI::Record &>(obj);
#ifdef USE_THREADS
    Thread::Mutex::Lock lock(rec.mutex());
#endif
    casa::GlishValue val = recToGlish(rec);
    val.addAttribute("dmi_actual_type",GlishArray(type_string));
    val.addAttribute("dmi_is_dmirecord",GlishArray(true));
    return val;
  }
  else if( dynamic_cast<const DMI::Vec *>(&obj) ) // (case DMI::Vec)
  {
    const DMI::Vec &vec = dynamic_cast<const DMI::Vec &>(obj);
#ifdef USE_THREADS
    Thread::Mutex::Lock lock(vec.mutex());
#endif
    TypeId fieldtype = vec.type();
    bool scalar = vec.isScalar();
    // an invalid field? (case 2.4)
    if( !vec.valid() )
    {
      return GlishArray(Array<Int>());
    }
    // a numeric/string/HIID type? (case 2.1)
    else if( TypeInfo::isNumeric(fieldtype) || fieldtype == Tpstring || fieldtype == TpDMIHIID )
    {
      GlishArray arr;
      // try to map to a Glish array
      if( makeGlishArray(arr,vec,fieldtype,adjustIndex) )
      {
        arr.addAttribute("dmi_actual_type",GlishArray(type_string));
        arr.addAttribute("dmi_vec_content_type",GlishArray(vec.type().toString()));
        arr.addAttribute("dmi_is_dmivec",GlishArray(true));
        arr.addAttribute("dmi_vec_is_scalar",GlishArray(scalar));
        return arr;
      }
    }
    else if( TypeInfo::isDynamic(fieldtype) ) // case (2.2)
    {
      // map to record of records, with fields "#1", "#2", etc.
      GlishRecord subrec;
      for( int i=0; i<vec.mysize(); i++ )
      {
        ObjRef ref = vec.getObj(i);
        if( ref.valid() )
          subrec.add(ssprintf("#%d",i+1),objectToGlishValue(*ref,adjustIndex));
        else
          subrec.add(ssprintf("#%d",i+1),makeMissingValue());
      }
      subrec.addAttribute("dmi_actual_type",GlishArray(type_string));
      subrec.addAttribute("dmi_vec_content_type",GlishArray(vec.type().toString()));
      subrec.addAttribute("dmi_is_dmivec",GlishArray(true));
      subrec.addAttribute("dmi_vec_is_scalar",GlishArray(scalar));
      return subrec;
    }
  }
  else if( dynamic_cast<const DMI::List *>(&obj) )  // (case DMI::List)
  {
    const DMI::List &list = dynamic_cast<const DMI::List &>(obj);
#ifdef USE_THREADS
    Thread::Mutex::Lock lock(list.mutex());
#endif
    // map to record, with fields "#1", "#2", etc.
    GlishRecord rec;
    for( int i=0; i<list.numItems(); i++ )
    {
      DMI::ObjRef ref = list.get(i);
      if( ref.valid() )
        rec.add(ssprintf("#%d",i+1),objectToGlishValue(*ref,adjustIndex));
      else
        rec.add(ssprintf("#%d",i+1),makeMissingValue());
    }
    rec.addAttribute("dmi_actual_type",GlishArray(type_string));
    rec.addAttribute("dmi_is_dmilist",GlishArray(true));
    return rec;
  }
  else if( dynamic_cast<const DMI::NumArray *>(&obj) )  // (case DMI::NumArray)
  {
    const DMI::NumArray &dataarray = dynamic_cast<const DMI::NumArray &>(obj);
#ifdef USE_THREADS
    Thread::Mutex::Lock lock(dataarray.mutex());
#endif
    GlishArray arr;
    // convert to array and add (case 3.1)
    if( dataarray.valid() )
    {
      if( makeGlishArray(arr,dataarray,dataarray.elementType(),adjustIndex) )
      {
        arr.addAttribute("dmi_actual_type",GlishArray(type.toString()));
        return arr;
      }
    }
//    else
//      return makeEmptyObject(obj.objectType());
  }
  // catch-all for (4) and all failed mappings: converts to a blockset
  return objectToBlockRec(obj);
}

// createSubclass:
// Helper templated function. If val::dmi_actual_type exists, it is interpreted
// as a type string, and an object of that type is created and returned 
// (must be a subclass of Base). Otherwise, a Base is created & returned. 
// If val::dmi_actual_type is not a legal type string, or not a subclass of Base,
// an exception is thrown.
// The ref is attached to the newly created object.
template<class Base>
Base * GlishUtil::createSubclass (ObjRef &ref,const casa::GlishValue &val)
{
  Base *pbase;
  // the dmi_actual_type attribute specifies a subclass 
  if( val.attributeExists("dmi_actual_type" ) )
  {
    String typestr;
    GlishArray tmp = val.getAttribute("dmi_actual_type"); tmp.get(typestr);
    dprintf(4)("real object type is %s\n",typestr.c_str());
    DMI::BObj * bo = DynamicTypeManager::construct(TypeId(typestr));
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

// helper function to create a DMI::Vec from a GlishArray
template<class T> 
void GlishUtil::initDMIVec (DMI::Vec &field,const GlishArray &arr,bool isScalar)
{
  Array<T> array;
  arr.get(array);
  bool del;
  const T * data = array.getStorage(del);
  int nel = array.nelements() == 1 && isScalar ? -1 : array.nelements();
  field.init(typeIdOf(T),nel,data);
  array.freeStorage(data,del);
}


template<class T> 
inline void initDMINumArray (ObjRef &ref,const casa::Array<T> &array,const GlishArray &val)
{
  DMI::NumArray & numarr = *GlishUtil::createSubclass<DMI::NumArray>(ref,val);
  // init numarray with AIPS++ type and shape
  numarr.init(array);
  // validate content
  numarr.validateContent(true);
}

// helper template to create a new DMI::NumArray from a GlishArray
// of the template argument type
template<class T> 
void GlishUtil::newDMINumArray (ObjRef &ref,const GlishArray &arr)
{
  Array<T> array;
  arr.get(array);
  initDMINumArray(ref,array,arr);
}

// helper function creates a DMI::NumArray from a GlishArray
ObjRef GlishUtil::makeDMINumArray (const GlishArray &arr,bool isIndex)
{
  ObjRef ref;
  switch( arr.elementType() )
  {
    case GlishArray::BOOL:      
        newDMINumArray<Bool>(ref,arr);
        return ref;
        
    case GlishArray::BYTE:
        newDMINumArray<uChar>(ref,arr);
        return ref;
        
    case GlishArray::SHORT:
        newDMINumArray<Short>(ref,arr);
        return ref;
    
    case GlishArray::INT: // explicitly adjust for index
    {
        Array<Int> array;
        arr.get(array);
        if( isIndex )
          array -= 1;
        initDMINumArray(ref,array,arr);
        return ref;
    }
    
    case GlishArray::FLOAT:
        newDMINumArray<Float>(ref,arr);
        return ref;
    
    case GlishArray::DOUBLE:
        newDMINumArray<Double>(ref,arr);
        return ref;
    
    case GlishArray::COMPLEX:
        newDMINumArray<Complex>(ref,arr);
        return ref;
    
    case GlishArray::DCOMPLEX:
        newDMINumArray<DComplex>(ref,arr);
        return ref;
    
    case GlishArray::STRING: 
        Throw("oops, we shouldn't be here");
        // initDMIVec<String>(arr,arr);
        return ref;
    
    default:
        dprintf(2)("warning: unknown Glish array type %d, ignoring\n",arr.elementType());
        createSubclass<DMI::NumArray>(ref,arr);
        return ref;
  }
}

// helper function creates a DMI::Vec from a GlishArray (must be 1D)
void GlishUtil::makeDMIVec (DMI::Vec &field,const GlishArray &arr,bool isIndex,bool isScalar)
{
  ObjRef ref;
  switch( arr.elementType() )
  {
    case GlishArray::BOOL:      
        initDMIVec<Bool>(field,arr,isScalar);
        break;
    case GlishArray::BYTE:
        initDMIVec<uChar>(field,arr,isScalar);
        break;
    case GlishArray::SHORT:
        initDMIVec<Short>(field,arr,isScalar);
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
        int nel = array.nelements() == 1 && isScalar ? -1 : int(array.nelements());
        field.init(Tpint,nel,data);
        array.freeStorage(data,del);
        break;
    }
    case GlishArray::FLOAT:
        initDMIVec<Float>(field,arr,isScalar);
        break;
    case GlishArray::DOUBLE:
        initDMIVec<Double>(field,arr,isScalar);
        break;
    case GlishArray::COMPLEX:
        initDMIVec<Complex>(field,arr,isScalar);
        break;
    case GlishArray::DCOMPLEX:
        initDMIVec<DComplex>(field,arr,isScalar);
        break;
    case GlishArray::STRING: 
    {
        Vector<String> array;
        arr.get(array);
        bool is_hiid = arr.attributeExists("dmi_is_dmihiid");
        if( !is_hiid && arr.attributeExists("dmi_vec_content_type") )
        {
          String typestr;
          GlishArray tmp = arr.getAttribute("dmi_vec_content_type"); 
          tmp.get(typestr);
          is_hiid |= ( strlowercase(typestr) == "dmihiid" );
        }
        int nel = array.nelements() == 1 && isScalar ? -1 : int(array.nelements());
        field.init(is_hiid?TpDMIHIID:Tpstring,nel);
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

// Converts any glish value to an object
// (DMI::Record, DMI::NumArray or DMI::Vec)
ObjRef GlishUtil::glishValueToObject (const casa::GlishValue &val,bool adjustIndex)
{
  ObjRef ref; 
  Bool isScalar = true;
  if( val.attributeExists("dmi_vec_is_scalar") )
  {
    GlishArray tmp = val.getAttribute("dmi_vec_is_scalar"); 
    tmp.get(isScalar);
  }
  if( val.type() == casa::GlishValue::ARRAY )
  {
    GlishArray arr = val;
    IPosition shape = arr.shape();
    // empty arrays map to null DMI::Vecs
    if( shape.nelements() == 1 && shape[0] == 0 )
    {
      dprintf(4)("converting empty GlishArray to empty DMI::Vec\n");
      return ObjRef(new DMI::Vec);
    }
    // missing (NONE) values map to null ObjRefs
    else if( shape.nelements() == 1 && shape[0] == 1 &&  
             arr.elementType() == GlishArray::BOOL && 
             val.attributeExists("dmi_none_value") )
    {
      return ObjRef();
    }
    // string arrays, or 1D arrays marked as a vec (or as with the
    // "dmi_is_hiid" attribute) always map to a DMI::Vec
    else if( ( shape.nelements() == 1 && 
            ( val.attributeExists("dmi_vec_content_type") || 
              val.attributeExists("dmi_is_dmivec") || 
              val.attributeExists("dmi_is_dmihiid") ) )
          || arr.elementType() == GlishArray::STRING )
    {
      dprintf(4)("converting GlishArray of %d elements to DMI::Vec\n",
                  shape.product());
      // if dmi_is_vec is set, then it may be in fact a subclass of
      // DMI::Vec. If not set, then this is some value that's going
      // to be encapsulated in a DMI::Vec, so create one directly.
      DMI::Vec *field;
      if( val.attributeExists("dmi_is_dmivec") )
        field = GlishUtil::createSubclass<DMI::Vec>(ref,val);
      else
        ref <<= field = new DMI::Vec;
      makeDMIVec(*field,arr,adjustIndex,isScalar);
      // validate the field (no-op for DMI::Vec itself, but may be meaningful for subclasses)
      field->validateContent(true); 
      return ref;
    }
    else // all other arrays map to DMI::NumArrays
    {
      dprintf(4)("converting GlishArray of %d elements to DMI::NumArray\n",
                  shape.product());
      return makeDMINumArray(arr,adjustIndex);
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
      return blockRecToObject(glrec);
    }
    // is it a DMI::Vec (that was passed in as a record of values)
    else if( glrec.attributeExists("dmi_is_dmivec")  )
    {
      // the attribute should be a string indicating the object type
      String typestr;
      GlishArray tmp = glrec.getAttribute("dmi_vec_content_type"); tmp.get(typestr);
      dprintf(4)("converting glish record (%d fields) to DMI::Vec(%s)\n",
                  glrec.nelements(),typestr.c_str()); 
      TypeId fieldtype(typestr);
      // create a field and populate it with the objects recursively
      DMI::Vec *field = GlishUtil::createSubclass<DMI::Vec>(ref,val);
      int nel = glrec.nelements() == 1 && isScalar ? -1 : int(glrec.nelements());
      field->init(fieldtype,nel);
      for( uint i=0;i<glrec.nelements(); i++ )
      {
        try 
        {
          field->put(i,glishValueToObject(glrec.get(i),adjustIndex));
        }
        catch( std::exception &exc )
        {
          dprintf(2)("warning: ignoring field [%d] (got exception: %s)\n",
              i,exceptionToString(exc).c_str());
        }
        catch( ... )
        {
          dprintf(2)("warning: ignoring field [%d] (got unknown exception)\n",i);
        }
      }
      field->validateContent(true);
      return ref;
    }
    // is it a DMI::List (that was passed in as a record of values)
    else if( glrec.attributeExists("dmi_is_dmilist")  )
    {
      // the attribute should be a string indicating the object type
      dprintf(4)("converting glish record (%d fields) to DMI::List\n",
                  glrec.nelements()); 
      // create a list and populate it with the objects recursively
      DMI::List *list = GlishUtil::createSubclass<DMI::List>(ref,val);
      for( uint i=0;i<glrec.nelements(); i++ )
      {
        try 
        {
          list->addBack(glishValueToObject(glrec.get(i),adjustIndex));
        }
        catch( std::exception &exc )
        {
          dprintf(2)("warning: ignoring field [%d] (got exception: %s)\n",
              i,exceptionToString(exc).c_str());
        }
        catch( ... )
        {
          dprintf(2)("warning: ignoring field [%d] (got unknown exception)\n",i);
        }
      }
      list->validateContent(true);
      return ref;
    }
    // else it's a plain old DMI::Record
    else
    {
      dprintf(4)("converting glish record to DMI::Record\n");
      DMI::Record *rec = GlishUtil::createSubclass<DMI::Record>(ref,val);
      for( uint i=0; i < glrec.nelements(); i++ )
      {
        string field_name = glrec.name(i);
        try // handle failed fields gracefully
        {
          casa::GlishValue subval = glrec.get(i);
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
            bool ignore = false;
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
          bool isIndex = false;
          if( isnumber )
          {
            id = HIID(AtomicID(atoi(field_name.c_str()+1)-1));
          }
          else
          {
            id = HIID(field_name,true,"_"); // allow litreal HIIDs
            isIndex = isIndexString(field_name);
          }
          dprintf(4)("maps to HIID '%s'\n",id.toString('.').c_str());
          rec->replace(id,glishValueToObject(subval,isIndex));
        }
        catch( std::exception &exc )
        {
          dprintf(2)("warning: ignoring field %s[%d] (got exception: %s)\n",
              field_name.c_str(),i,exceptionToString(exc).c_str());
        }
        catch( ... )
        {
          dprintf(2)("warning: ignoring field %s[%d] (got unknown exception)\n",
              field_name.c_str(),i);
        }
      }
      rec->validateContent(true);
      return ref;
    }
  }
}

//##ModelId=3DB936930231
// Converts object to blockset representation (i.e. a glish record of
// byte arrays corresponding to the blocks)
GlishRecord GlishUtil::objectToBlockRec (const DMI::BObj &obj)
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
DMI::ObjRef GlishUtil::blockRecToObject (const GlishRecord &rec)
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
    set.pushNew() <<= block;
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



#ifndef TypeInfo_h
#define TypeInfo_h 1

#include <DMI/TID-DMI.h>
#include <DMI/TypeId.h>
#include <DMI/TypeIterMacros.h>

// The TypeInfo class is basically a simple struct containing information
// on various types. 
//##ModelId=3DB949AE01B8
class TypeInfo : public TypeCategories {
  public:
      // ...stored here:
    //##ModelId=3E9BD91A023C
      Category category;
    //##ModelId=3DB949B00054
      size_t   size;
      // function pointer types (new method, delete method, copy method,
      // pack method, unpack method, packSize method: see Packer.h)
    //##ModelId=3DB949AE01C3
      typedef void * (*NewMethod)(int);
    //##ModelId=3DB949AE01C8
      typedef void (*DeleteMethod)(void*);
    //##ModelId=3DB949AE01CD
      typedef void (*CopyMethod)(void*,const void*);
    //##ModelId=3DB949AE01D2
      typedef size_t (*PackMethod)(const void *,int,void *,size_t &);
    //##ModelId=3DB949AE01D7
      typedef void * (*UnpackMethod)(const void *,size_t,int &);
    //##ModelId=3DB949AE01DC
      typedef size_t (*PackSizeMethod)(const void *,int n);

    //##ModelId=3DB949B0005A
      NewMethod fnew;
    //##ModelId=3DB949B00063
      DeleteMethod fdelete;
    //##ModelId=3DB949B0006D
      CopyMethod fcopy;
    //##ModelId=3DB949B00078
      PackMethod fpack;
    //##ModelId=3DB949B00082
      UnpackMethod funpack;
    //##ModelId=3DB949B0008D
      PackSizeMethod fpacksize;
      
      // default constructor / constructor with no methods
    //##ModelId=3DB949B00097
      TypeInfo( Category cat = NONE,size_t sz=0 )
        : category(cat),size(sz),fnew(0),fdelete(0),fcopy(0),
          fpack(0),funpack(0),fpacksize(0) {};
      // constructor with full methods
    //##ModelId=3DB949B000A2
      TypeInfo( Category cat,size_t sz,
                NewMethod nm,DeleteMethod dm,CopyMethod cm, 
                PackMethod pm,UnpackMethod um,PackSizeMethod sm ) 
        : category(cat),size(sz),fnew(nm),fdelete(dm),fcopy(cm),
          fpack(pm),funpack(um),fpacksize(sm) {};
      
      // operator == required for registry
    //##ModelId=3DB949B000CA
      bool operator == ( const TypeInfo &other ) const
      { return !memcmp(this,&other,sizeof(*this)); }
      
    //##ModelId=3DB949B000D2
      bool operator != ( const TypeInfo &other ) const
      { return !( *this == other ); }
      
      //  Looks up type info in the registry
    //##ModelId=3DB949B000DA
      static const TypeInfo & find ( TypeId tid );
      
      // Returns True if type is numeric or dynamic
    //##ModelId=3DB949B000E3
      static bool isNumeric   (TypeId tid);
    //##ModelId=3DB949B000EB
      static bool isDynamic   (TypeId tid);
    //##ModelId=3DB949B000F3
      static bool isArrayable (TypeId tid);
    //##ModelId=3DB949B000FB
      static bool isArray     (TypeId tid);
      
    //##ModelId=3DB949B0010B
      static TypeId typeOfArrayElem (TypeId arr);
    //##ModelId=3E9BD91A0261
      static uint   rankOfArray     (TypeId arr);
      
      // can one type be converted to another?
      // only defined for numerics, for now
    //##ModelId=4017F63303AC
      static bool isConvertible (TypeId from,TypeId to)
      { return from == to || ( isNumeric(from) && isNumeric(to) ); }
      
      // do the conversion, return True on success, False if not convertible
    //##ModelId=4017F63303BF
      static bool convert (const void *from,TypeId from,void *to,TypeId to);
};
 
// This is a helper class hosting a registry for TypeInfos
//##ModelId=3DB949AE01E7
class TypeInfoReg
{
  public:
      // this declares a registry (see Registry.h)
    //##ModelId=3DB949B00119
      DeclareRegistry(TypeInfoReg,TypeId,TypeInfo);
      friend class TypeInfo;
};
    
//##ModelId=3DB949B000DA
inline const TypeInfo & TypeInfo::find ( TypeId tid )
{ return TypeInfoReg::registry.find(tid); }
        

inline TypeId TypeInfo::typeOfArrayElem (TypeId arr)
{
  return - ((-arr.id())%32) - 32;
}

//##ModelId=3E9BD91A0261
inline uint TypeInfo::rankOfArray (TypeId arr)
{
  return (-arr.id())/32 - 1;
}

// returns True if a type is built-in
//##ModelId=3DB949B000E3
inline bool TypeInfo::isNumeric (TypeId tid)
{ 
  return tid.id() >= TpFirstNumeric && tid.id() <= TpLastNumeric; 
}

// returns True if a type is supported by Array
//##ModelId=3DB949B000F3
inline bool TypeInfo::isArrayable (TypeId tid)
{ 
  return isNumeric(tid) || tid == Tpstring;
}

// returns True if a type is an Array_type
//##ModelId=3DB949B000FB
inline bool TypeInfo::isArray (TypeId tid)
{ 
  TypeId elem = typeOfArrayElem(tid);
  int rank = rankOfArray(tid);
  return rank>0 && rank<=11 && isArrayable(elem);
}

// returns True if type is dynamic
//##ModelId=3DB949B000EB
inline bool TypeInfo::isDynamic (TypeId tid) 
{ 
  return find(tid).category == TypeInfo::DYNAMIC;  
}


// These macros repeatedly invokes Do(type,arg) for all types in a specific
// type set. Useful for making bulk definitions.
#define ForAllSignedNumerics(Do,arg) \
  Do(char,arg) Do(short,arg) Do(int,arg) Do(long,arg)
#define ForAllUnsignedNumerics(Do,arg) \
  Do(bool,arg) Do(uchar,arg) Do(ushort,arg) Do(uint,arg) Do(ulong,arg)
#define ForAllFloats(Do,arg) \
  Do(float,arg) Do(double,arg) Do(ldouble,arg)
// Same macro, but inserts commas in between
#define ForAllSignedNumerics1(Do,arg) \
  Do(char,arg),Do(short,arg),Do(int,arg),Do(long,arg)
#define ForAllUnsignedNumerics1(Do,arg) \
  Do(bool,arg),Do(uchar,arg),Do(ushort,arg),Do(uint,arg),Do(ulong,arg)
#define ForAllFloats1(Do,arg) \
  Do(float,arg),Do(double,arg),Do(ldouble,arg)

// A type converter function converts between built-in types
//##ModelId=3DB949AE01A9
typedef void (*TypeConverter)(const void *from,void *to);

// This is a matrix of converters for the built-in scalar types.
extern TypeConverter _typeconverters[16][16];

// Inline function to convert scalars  
//##ModelId=4017F63303BF
inline bool TypeInfo::convert ( const void *from,TypeId frid,void *to,TypeId toid )
{
  if( !TypeInfo::isNumeric(frid) || !TypeInfo::isNumeric(toid) )
    return False;
  (*_typeconverters[Tpbool.id()-frid][Tpbool.id()-toid])(from,to);
  return True;
}

// define the typeIdOfPtr() helper function, returning a TypeId for a given type
// (passed in as a T*).
template<class T>
inline TypeId TpOfPtr (const T*)
{ return DMITypeTraits<T>::typeId; }
   
// Similar function, but returns typeid of elements for an array pointer argument
template<class T,int N> 
inline TypeId TpOfArrayElem (const blitz::Array<T,N> *) 
{ return DMITypeTraits<T>::typeId; };

// These are more convenient macros (only need a type as an argument)
#define typeIdOf(type) TpOfPtr((type*)0)
#define typeIdOfArray(type,N) TpArray(typeIdOf(type),N)
#define typeIdOfArrayElem(type) TpOfArrayElem((type*))

#endif

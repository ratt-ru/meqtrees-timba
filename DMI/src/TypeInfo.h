#ifndef TypeInfo_h
#define TypeInfo_h 1

#include "DMI/TID-DMI.h"
#include "DMI/TypeId.h"
#include "DMI/TypeIterMacros.h"

// The TypeInfo class is basically a simple struct containing information
// on various types. 
class TypeInfo {
  public:
      // enum of type categories
      typedef enum { NONE=0,NUMERIC=1,BINARY=2,DYNAMIC=3,SPECIAL=4,INTERMEDIATE=5,OTHER=6 } Category;
      // ...stored here:
      Category category;
      size_t   size;
      // function pointer types (new method, delete method, copy method,
      // pack method, unpack method, packSize method: see Packer.h)
      typedef void * (*NewMethod)(int);
      typedef void (*DeleteMethod)(void*);
      typedef void (*CopyMethod)(void*,const void*);
      typedef size_t (*PackMethod)(const void *,int,void *,size_t &);
      typedef void * (*UnpackMethod)(const void *,size_t,int &);
      typedef size_t (*PackSizeMethod)(const void *,int n);

      NewMethod fnew;
      DeleteMethod fdelete;
      CopyMethod fcopy;
      PackMethod fpack;
      UnpackMethod funpack;
      PackSizeMethod fpacksize;
      
      // default constructor / constructor with no methods
      TypeInfo( Category cat = NONE,size_t sz=0 )
        : category(cat),size(sz),fnew(0),fdelete(0),fcopy(0),
          fpack(0),funpack(0),fpacksize(0) {};
      // constructor with full methods
      TypeInfo( Category cat,size_t sz,
                NewMethod nm,DeleteMethod dm,CopyMethod cm, 
                PackMethod pm,UnpackMethod um,PackSizeMethod sm ) 
        : category(cat),size(sz),fnew(nm),fdelete(dm),fcopy(cm),
          fpack(pm),funpack(um),fpacksize(sm) {};
      
      // operator == required for registry
      bool operator == ( const TypeInfo &other ) const
      { return !memcmp(this,&other,sizeof(*this)); }
      
      bool operator != ( const TypeInfo &other ) const
      { return !( *this == other ); }
      
      //  Looks up type info in the registry
      static const TypeInfo & find ( TypeId tid );
      
      // Returns True if type is numeric or dynamic
      static bool isNumeric   (TypeId tid);
      static bool isDynamic   (TypeId tid);
      static bool isArrayable (TypeId tid);
      static bool isArray     (TypeId tid);
      
      static TypeId elemToArr (TypeId elem);
      static TypeId arrToElem (TypeId arr);
};
 
// This is a helper class hosting a registry for TypeInfos
class TypeInfoReg
{
  public:
      // this declares a registry (see Registry.h)
      DeclareRegistry(TypeInfoReg,TypeId,TypeInfo);
      friend TypeInfo;
};
    
inline const TypeInfo & TypeInfo::find ( TypeId tid )
{ return TypeInfoReg::registry.find(tid); }
        

// These functions convert the TypeId of a numeric type to/from an
// Array_type
inline TypeId TypeInfo::elemToArr (TypeId elem)
{ return elem.id() + tpElemToArrayOffset; }

inline TypeId TypeInfo::arrToElem (TypeId arr)
{ return arr.id() - tpElemToArrayOffset; }


// returns True if a type is built-in
inline bool TypeInfo::isNumeric (TypeId tid)
{ 
  return tid.id() >= TpFirstNumeric && tid.id() <= TpLastNumeric; 
}

// returns True if a type is supported by Array
inline bool TypeInfo::isArrayable (TypeId tid)
{ 
  #define __compare(type,arg) (tid == Tp##type)
  return DoForAllArrayTypes2(__compare,,||);
  #undef __compare
}

// returns True if a type is an Array_type
inline bool TypeInfo::isArray (TypeId tid)
{ 
  return isArrayable( arrToElem(tid) );
}

// returns True if type is dynamic
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
typedef void (*TypeConverter)(const void *from,void *to);

// This is a matrix of converters for the built-in scalar types.
extern TypeConverter _typeconverters[16][16];

// Inline function to convert scalars  
inline bool convertScalar ( const void *from,TypeId frid,void *to,TypeId toid )
{
  if( !TypeInfo::isNumeric(frid) || !TypeInfo::isNumeric(toid))
    return False;
  (*_typeconverters[Tpchar.id()-frid][Tpchar.id()-toid])(from,to);
  return True;
}

// define the typeIdOfPtr() helper function, returning a TypeId for a given type
// (passed in as a T*).
// This is used in various places where we want to convert a type to a TypeId
// at compile-time
#define __typeIdOfPtr(T,arg) inline TypeId TpOfPtr (const T *) { return Tp##T; };
DoForAllNumericTypes(__typeIdOfPtr,);
 __typeIdOfPtr(string,);

// This is a more convenient macro form
#define typeIdOf(type) TpOfPtr((type*)0)

// Similar function, but returns Tptype for an Array_type* argument
#define __typeIdOfArrayElem(T,arg) inline TypeId TpOfArrayElem (const Array_##T *) { return Tp##T; };
DoForAllArrayTypes(__typeIdOfArrayElem,);

// Similar function, but returns TpArray_type for a type * argument
#define __typeIdOfArray(T,arg) inline TypeId TpOfArrayPtr (const T *) { return TpArray_##T; };
DoForAllArrayTypes(__typeIdOfArray,);

// These are more convenient macros (only need a type)
#define typeIdOf(type) TpOfPtr((type*)0)
#define typeIdOfArray(type) TpOfArrayPtr((type*)0)



#endif

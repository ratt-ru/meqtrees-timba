#ifndef TypeInfo_h
#define TypeInfo_h 1

#include "TID-DMI.h"

// The TypeInfo class is basically a simple struct containing information
// on various types. 
class TypeInfo {
  public:
      // enum of type categories
      typedef enum { NONE=0,NUMERIC=1,BINARY=2,DYNAMIC=3,SPECIAL=4,OTHER=5 } Category;
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
      
      //  Looks up type info in the registry
      static const TypeInfo & find ( TypeId tid );
      
      // Returns True if type is numeric or dynamic
      static bool isNumeric (TypeId tid);
      static bool isDynamic (TypeId tid);
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
        
// // These macros convert a type name or an expression into a TypeId.
// // They use the auto-generated typeIdOf() inlines.
// #define type2id(type) typeIdOfPtr((type*)0)
// #define expr2id(expr) typeIdOf(expr)
// 
// these constants are used to distinguish built-ins from other types
// (note that actual numeric values are all negative)
const int StdTypeFirst=Tpbool,StdTypeLast=Tpchar;

// returns True if a type is built-in
inline bool TypeInfo::isNumeric (TypeId tid)
{ 
  return tid.id() >= StdTypeFirst && tid.id() <= StdTypeLast; 
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

#endif

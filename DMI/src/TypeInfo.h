#ifndef TypeInfo_h
#define TypeInfo_h 1

#include "TID.h"

// The TypeInfo class is basically a simple struct containing information
// on various types. 
class TypeInfo {
  public:
      // enum of type categories
      typedef enum { NONE=0,NUMERIC=1,BINARY=2,DYNAMIC=3,OTHER=4 } Category;
      // ...stored here:
      Category category;
      size_t   size;
      
      // default constructor
      TypeInfo( Category cat = NONE,size_t sz=0 ) : category(cat),size(sz) {};
      
      // operator == required for registry
      bool operator == ( const TypeInfo &other ) const
      { return category == other.category && size == other.size; }
      
      //  Looks up type info in the registry
      static const TypeInfo & find ( TypeId tid );
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
        
// These macros convert a type name or an expression into a TypeId.
// They use the auto-generated typeIdOf() inlines.
#define type2id(type) typeIdOfPtr((type*)0)
#define expr2id(expr) typeIdOf(expr)

// these constants are used to distinguish built-ins from other types
// (note that actual numeric values are all negative)
const int StdTypeFirst=Tpbool,StdTypeLast=Tpchar;

// returns True if a type is built-in
inline bool isNumericType (int tid) 
  { return tid >= StdTypeFirst && tid <= StdTypeLast; }

// returns True if type is dynamic
inline bool isDynamicType (int tid)
  { return tid==TpDataRecord || tid==TpDataField; }

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
extern TypeConverter _typeconverters[12][12];

// Inline function to convert scalars  
inline bool convertScalar ( const void *from,TypeId frid,void *to,TypeId toid )
{
  if(!isNumericType(frid) || !isNumericType(toid))
    return False;
  (*_typeconverters[Tpchar.id()-frid][Tpchar.id()-toid])(from,to);
  return True;
}

#endif

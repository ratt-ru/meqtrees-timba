#ifndef DMI_TypeIterMacros_h
#define DMI_TypeIterMacros_h 1
    
#include "lofar_config.h"
    
// 
// This file defines "type iterator" macros, i.e. macros that will repeat
// a certain bit of code for every type in a category.
//
    
// This macro is used internally to expand the iterator definitions 
// pulled in from every package. Any new packages should be
// added to the list here.
#define DoForSomeTypes(Which,Do,arg); \
          DoForSomeTypes_DMI(Which,Do,arg); \
          DoForSomeTypes_OCTOPUSSY(Which,Do,arg) ;\
          DoForSomeTypes_UVD(Which,Do,arg); \
          DoForSomeTypes_VisDM(Which,Do,arg); 
        
// DMI types are always pulled in
#include "DMI/TypeIter-DMI.h"
#define DoForSomeTypes_DMI(Which,Do,arg) \
          DoForAll##Which##Types_DMI(Do,arg,;)
    
// Pull in iterators definitions from each configured dependency package. 
// If package is not configured, define dummy iterators for it.
// New packages should be added here in the same manner

#ifdef HAVE_LOFAR_OCTOPUSSY
  #include "OCTOPUSSY/TypeIter-OCTOPUSSY.h"
  #define DoForSomeTypes_OCTOPUSSY(Which,Do,arg) \
            DoForAll##Which##Types_OCTOPUSSY(Do,arg,;);
#else
  #define DoForSomeTypes_OCTOPUSSY(Which,Do,arg) 
#endif
    
#ifdef HAVE_LOFAR_UVD
  #include "UVD/TypeIter-UVD.h"
  #define DoForSomeTypes_UVD(Which,Do,arg) \
            DoForAll##Which##Types_UVD(Do,arg,;);
#else
  #define DoForSomeTypes_UVD(Which,Do,arg) 
#endif
    
#ifdef HAVE_LOFAR_VISDM
  #include "VisDM/TypeIter-VisDM.h"
  #define DoForSomeTypes_VisDM(Which,Do,arg) \
            DoForAll##Which##Types_VisDM(Do,arg,;);
#else
  #define DoForSomeTypes_VisDM(Which,Do,arg) 
#endif


// Now define the macros themselves

#define DoForAllNumericTypes(Do,arg) \
          DoForSomeTypes(Numeric,Do,arg)
          
#define DoForAllBinaryTypes(Do,arg) \
          DoForSomeTypes(Binary,Do,arg)
          
#define DoForAllDynamicTypes(Do,arg) \
          DoForSomeTypes(Dynamic,Do,arg)
          
#define DoForAllIntermediateTypes(Do,arg) \
          DoForSomeTypes(Intermediate,Do,arg)
          
#define DoForAllSpecialTypes(Do,arg) \
          DoForSomeTypes(Special,Do,arg)
          
#define DoForAllOtherTypes(Do,arg) \
          DoForSomeTypes(Other,Do,arg)

#endif

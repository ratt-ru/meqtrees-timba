#ifndef DMI_CountedRefTraits_h
#define DMI_CountedRefTraits_h 1
    
#include <DMI/TypeId.h>
#include <DMI/CountedRef.h>
    
namespace DMI
{
    
template<class T>
class CountedRefTraits : public DMITypeTraits<T>
{
  public:
    enum { isCountedRef  = false };
    typedef void TargetType; 
};

// a partial specialization of the traits for CountedRefs
template<class T>
class CountedRefTraits< CountedRef<T> > : public DMITypeTraits< CountedRef<T> >
{
  public:
    enum { isCountedRef  = true };
    typedef T TargetType; 
};
    
};
#endif

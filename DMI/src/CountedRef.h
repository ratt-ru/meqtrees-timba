//	f:\lofar\dvl\lofar\cep\cpa\pscf\src

#ifndef CountedRef_h
#define CountedRef_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

// CountedRefBase
#include "DMI/CountedRefBase.h"

//##ModelId=3BEFECFF0287
//##Documentation
//## This is a type-specific interface to the counted reference
//## mechanism, providing most of the same functions as CountedRefBase,
//## but tailored for type T.  Refer to CountedRefBase for all details.
template <class T>
class CountedRef : private CountedRefBase
{
  public:
    //##ModelId=3BF9396D01A7
      CountedRef();

    //##ModelId=3BF93C020247
      CountedRef(const CountedRef<T> &right);

      //##ModelId=3BF93D620128
      //##Documentation
      //## Generic copy constructor -- see same method in CountedRefBase.
      CountedRef (const CountedRef<T>& other, int flags, int depth = 1);

      //##ModelId=3BF93F8D0054
      explicit CountedRef (T& targ, int flags = 0);

      //##ModelId=3BF93F9702C5
      explicit CountedRef (const T& targ, int flags = 0);

      //##ModelId=3DB934560267
      explicit CountedRef (T* targ, int flags = 0);

      //##ModelId=3DB934570236
      explicit CountedRef (const T* targ, int flags = 0);

    //##ModelId=3DB934580238
      CountedRef<T> & operator=(const CountedRef<T> &right);

    //##ModelId=3DB934590080
      bool operator==(const CountedRef<T> &right) const;

    //##ModelId=3DB934590329
      bool operator!=(const CountedRef<T> &right) const;


      //##ModelId=3C8F61C80241
      const T* deref_p () const;

      //##ModelId=3BEFED870110
      //##Documentation
      //## Dereferences to const target.
      const T& deref () const;

      //##ModelId=3BF55FDC0049
      //##Documentation
      //## Overloaded deref op, so that ref->method() can be used to call
      //## target's const methods.
      const T* operator -> () const;

      //##ModelId=3C5FBE030173
      const T& operator * () const;

      //##ModelId=3C8F61D10199
      T* dewr_p () const;

      //##ModelId=3BEFF73602B0
      //##Documentation
      //## Dereferences to non-const object.
      T& dewr () const;

      //##ModelId=3C0F806901C1
      //##Documentation
      //## Dereferences to non-const object. Use e.g. ref().method() to call
      //## target's non-const methods.
      T& operator () () const;

      //##ModelId=3C0F808100DF
      //##Documentation
      //## Conversion operators to T& and T* do. implicit dereferencing.
      operator const T& () const;

      //##ModelId=3C0F80A50055
      operator const T* () const;

      //##ModelId=3C0F80B501D4
      operator T& () const;

      //##ModelId=3C0F80C0020C
      operator T* () const;

      //##ModelId=3BF93A170291
      //##Documentation
      //## Copies ref -- see CountedRefBase::copy().
      CountedRef<T> copy (int flags = 0) const;

      //##ModelId=3C1F2DB802D2
      CountedRef<T> & copy (const CountedRef<T>& other, int flags = 0);

      //##ModelId=3C1F2DD30353
      CountedRef<T> & xfer (const CountedRef<T>& other);

      //##ModelId=3C17A06901DC
      //##Documentation
      //## Privatizes a ref -- see CountedRefBase::privatize().
      CountedRef<T>& privatize (int flags = 0, int depth = 0);

      //##ModelId=3C187F270346
      //##Documentation
      //## Locks ref -- see CountedRefBase::lock().
      CountedRef<T>& lock ();

      //##ModelId=3C187F2E0291
      //##Documentation
      //## Unlocks ref -- see CountedRefBase::unlock().
      CountedRef<T>& unlock ();

      //##ModelId=3C501A15015C
      CountedRef<T>& persist ();

      //##ModelId=3C501A1C01FD
      CountedRef<T>& unpersist ();

      //##ModelId=3C1897A5032E
      //##Documentation
      //## Changes ref properties -- see CountedRefBase::change().
      CountedRef<T>& change (int flags);

      //##ModelId=3C1897B50178
      //##Documentation
      //## Makes exclusive writer -- see  CountedRefBase::setExclusiveWrite()
      CountedRef<T>& setExclusiveWrite ();

      //##ModelId=3BFA4DF4027D
      //##Documentation
      //## Various methods to attach to target object. See CountedRef
      //## Base::attach(). Const target forces READONLY ref.
      CountedRef<T> & attach (T& targ, int flags = 0);

      //##ModelId=3BFA4E070216
      CountedRef<T> & attach (const T& targ, int flags = 0);

      //##ModelId=3C179D9E027E
      CountedRef<T> & attach (T* targ, int flags = 0);

      //##ModelId=3C179DA9016B
      CountedRef<T> & attach (const T* targ, int flags = 0);

      //##ModelId=3CBEE39B0011
      CountedRef<T> & operator <<= (const T* targ);

      //##ModelId=3CBEE3AC0105
      CountedRef<T> & operator <<= (T* targ);

    // Additional Public Declarations
      // Constructor for implicitly allocating a new anonymous target.
      // Flags must contain DMI::ANON, else exception is thrown.
      // T must have a default constructor.
      // Use, e.g.: CountedRef<T> ref(DMI::ANONWR);
    //##ModelId=3DB9345A02BD
      explicit CountedRef (int flags); 
      
      // make public some methods of CountedRefBase which would otherwise
      // be hidden by private inheritance
    //##ModelId=3DB934500207
      CountedRefBase::valid;
    //##ModelId=3DB9345003DE
      CountedRefBase::detach;
    //##ModelId=3DB934510135
      CountedRefBase::isLocked;
    //##ModelId=3DB934510276
      CountedRefBase::isWritable;
    //##ModelId=3DB9345103B6
      CountedRefBase::isExclusiveWrite;
    //##ModelId=3DB934520105
      CountedRefBase::isAnonObject;
    //##ModelId=3DB934520250
      CountedRefBase::hasOtherWriters;
    //##ModelId=3DB934520390
      CountedRefBase::verify; 
    //##ModelId=3DB934530111
      CountedRefBase::debug;
    //##ModelId=3DB93453025B
      CountedRefBase::sdebug;
      
      // add upcast/downcast methods for conversion between ref types
      // upcast() 
      template<class U>
      CountedRef<U> & ref_cast ()
      { 
        FailWhen( target && !dynamic_cast<U*>(target),"illegal ref conversion"); 
        return *reinterpret_cast<CountedRef<U> *>(this); 
      }
      
      template<class U>
      const CountedRef<U> & ref_cast () const
      {
        FailWhen( target && !dynamic_cast<const U*>(target),"illegal ref conversion"); 
        return *reinterpret_cast<const CountedRef<U> *>(this); 
      }
      
  protected:
    // Additional Protected Declarations
    //##ModelId=3DB934540014
      CountedRefBase::target;
};

// Parameterized Class CountedRef 

//##ModelId=3BF9396D01A7
template <class T>
inline CountedRef<T>::CountedRef()
  : CountedRefBase()
{
}

//##ModelId=3BF93C020247
template <class T>
inline CountedRef<T>::CountedRef(const CountedRef<T> &right)
  : CountedRefBase(right)
{
}

//##ModelId=3BF93D620128
template <class T>
inline CountedRef<T>::CountedRef (const CountedRef<T>& other, int flags, int depth)
  : CountedRefBase(other,flags,depth)
{
}

//##ModelId=3BF93F8D0054
template <class T>
inline CountedRef<T>::CountedRef (T& targ, int flags)
  : CountedRefBase()
{
  attach(&targ,flags);
}

//##ModelId=3BF93F9702C5
template <class T>
inline CountedRef<T>::CountedRef (const T& targ, int flags)
  : CountedRefBase()
{
  attach(&targ,flags|DMI::READONLY);
}

//##ModelId=3DB934560267
template <class T>
inline CountedRef<T>::CountedRef (T* targ, int flags)
  : CountedRefBase()
{
  if( !flags&DMI::EXTERNAL )
    flags |= DMI::ANON;
  attach(targ,flags);
}

//##ModelId=3DB934570236
template <class T>
inline CountedRef<T>::CountedRef (const T* targ, int flags)
  : CountedRefBase()
{
  if( !flags&DMI::EXTERNAL )
    flags |= DMI::ANON;
  attach(targ,flags|DMI::READONLY);
}


//##ModelId=3DB934580238
template <class T>
inline CountedRef<T> & CountedRef<T>::operator=(const CountedRef<T> &right)
{
  (*(CountedRefBase*)this) = *(CountedRefBase*)&right;
  return *this;
//  dprintf(5)("      CountedRefBase/%08x assignment: %08x\n",(int)this,(int)&right);
//  return xfer((CountedRef<T>&)right);
}



//##ModelId=3C8F61C80241
template <class T>
inline const T* CountedRef<T>::deref_p () const
{
  return static_cast<const T*>( getTarget() );
}

//##ModelId=3BEFED870110
template <class T>
inline const T& CountedRef<T>::deref () const
{
  return *deref_p();
}

template <class T>
inline const T* CountedRef<T>::operator -> () const
{
  return deref_p();
}

//##ModelId=3C5FBE030173
template <class T>
inline const T& CountedRef<T>::operator * () const
{
  return deref();
}

//##ModelId=3C8F61D10199
template <class T>
inline T* CountedRef<T>::dewr_p () const
{
  return static_cast<T*>(getTargetWr());
}

//##ModelId=3BEFF73602B0
template <class T>
inline T& CountedRef<T>::dewr () const
{
  return *dewr_p();
}

//##ModelId=3C0F806901C1
template <class T>
inline T& CountedRef<T>::operator () () const
{
  return dewr();
}

//##ModelId=3C0F808100DF
template <class T>
inline CountedRef<T>::operator const T& () const
{
  return deref();
}

//##ModelId=3C0F80A50055
template <class T>
inline CountedRef<T>::operator const T* () const
{
  return deref_p();
}

//##ModelId=3C0F80B501D4
template <class T>
inline CountedRef<T>::operator T& () const
{
  return dewr();
}

//##ModelId=3C0F80C0020C
template <class T>
inline CountedRef<T>::operator T* () const
{
  return dewr_p();
}

//##ModelId=3BF93A170291
template <class T>
inline CountedRef<T> CountedRef<T>::copy (int flags) const
{
  return CountedRef<T>(*this,flags|DMI::COPYREF);
}

//##ModelId=3C1F2DB802D2
template <class T>
inline CountedRef<T> & CountedRef<T>::copy (const CountedRef<T>& other, int flags)
{
  CountedRefBase::copy(other,flags);
  return *this;
}

//##ModelId=3C1F2DD30353
template <class T>
inline CountedRef<T> & CountedRef<T>::xfer (const CountedRef<T>& other)
{
  CountedRefBase::xfer(other);
  return *this;
}

//##ModelId=3C17A06901DC
template <class T>
inline CountedRef<T>& CountedRef<T>::privatize (int flags, int depth)
{
// This simply defers to the base class Tclone(). It is provided here
// so that specifc types may implement specific kind of cloning.
  CountedRefBase::privatize(flags,depth);
  return *this;
}

//##ModelId=3C187F270346
template <class T>
inline CountedRef<T>& CountedRef<T>::lock ()
{
  CountedRefBase::lock();
  return *this;
}

//##ModelId=3C187F2E0291
template <class T>
inline CountedRef<T>& CountedRef<T>::unlock ()
{
  CountedRefBase::unlock();
  return *this;
}

//##ModelId=3C501A15015C
template <class T>
inline CountedRef<T>& CountedRef<T>::persist ()
{
  CountedRefBase::persist();
  return *this;
}

//##ModelId=3C501A1C01FD
template <class T>
inline CountedRef<T>& CountedRef<T>::unpersist ()
{
  CountedRefBase::unpersist();
  return *this;
}

//##ModelId=3C1897A5032E
template <class T>
inline CountedRef<T>& CountedRef<T>::change (int flags)
{
  CountedRefBase::change(flags);
  return *this;
}

//##ModelId=3C1897B50178
template <class T>
inline CountedRef<T>& CountedRef<T>::setExclusiveWrite ()
{
  CountedRefBase::setExclusiveWrite();
  return *this;
}

//##ModelId=3BFA4DF4027D
template <class T>
inline CountedRef<T> & CountedRef<T>::attach (T& targ, int flags)
{
  return attach(&targ,flags);
}

//##ModelId=3BFA4E070216
template <class T>
inline CountedRef<T> & CountedRef<T>::attach (const T& targ, int flags)
{
  return attach(&targ,flags);
}

//##ModelId=3C179D9E027E
template <class T>
inline CountedRef<T> & CountedRef<T>::attach (T* targ, int flags)
{
  CountedRefBase::attach(targ,flags);
  return *this;
}

//##ModelId=3C179DA9016B
template <class T>
inline CountedRef<T> & CountedRef<T>::attach (const T* targ, int flags)
{
  CountedRefBase::attach(targ,flags);
  return *this;
}

// Parameterized Class CountedRef 

//##ModelId=3DB934590080
template <class T>
bool CountedRef<T>::operator==(const CountedRef<T> &right) const
{
  return target != 0 && target == right.target;
}

//##ModelId=3DB934590329
template <class T>
bool CountedRef<T>::operator!=(const CountedRef<T> &right) const
{
  return !(*this == right);
}



//##ModelId=3CBEE39B0011
template <class T>
inline CountedRef<T> & CountedRef<T>::operator <<= (const T* targ)
{
  return attach(targ,DMI::ANON|DMI::READONLY);
}

//##ModelId=3CBEE3AC0105
template <class T>
inline CountedRef<T> & CountedRef<T>::operator <<= (T* targ)
{
  return attach(targ,DMI::ANON|DMI::WRITE);
}

//##ModelId=3DB9345A02BD
template <class T>
inline CountedRef<T>::CountedRef (int flags)
  : CountedRefBase()
{
  FailWhen(!flags&DMI::ANON,"DMI::ANON must be specified in constructor");
  attach(new T,flags);
}

// Template for copying STL containers of CountedRefs. Uses iterators
// to copy() every ref in the source container, passing the supplied flags
// to ref.copy(). For this implementation to work, destination
// Dcontainer must support the explicit resize operation.
template<class SrcCont,class DestCont>
void copyRefContainer (DestCont &dest,const SrcCont &src,int flags=DMI::PRESERVE_RW)
{
  dest.resize(src.size());
  typename SrcCont::const_iterator si = src.begin();
  typename DestCont::iterator di = dest.begin();
  for( ; si != src.end(); si++,di++ )
    di->copy(*si,flags);
}

// The DefineRefTypes macro generates typedefs for refs to specific types.
// E.g.: DefineRefType(SmartBlock,BlockRef) will define
//    BlockRef (as CountedRef<SmartBlock>), 
#define DefineRefTypes(type,reftype) typedef CountedRef<type> reftype; 


#endif


// Detached code regions:
#if 0
    : CountedRef<T>(ref,DMI::COPYREF|DMI::LOCKED)

    : CountedRef<T>(ref,flags)

#endif

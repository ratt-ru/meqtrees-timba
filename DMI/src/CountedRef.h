//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC810321.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC810321.cm

//## begin module%3C10CC810321.cp preserve=no
//## end module%3C10CC810321.cp

//## Module: CountedRef%3C10CC810321; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\CountedRef.h

#ifndef CountedRef_h
#define CountedRef_h 1

//## begin module%3C10CC810321.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC810321.additionalIncludes

//## begin module%3C10CC810321.includes preserve=yes
//## end module%3C10CC810321.includes

// CountedRefBase
#include "CountedRefBase.h"
//## begin module%3C10CC810321.declarations preserve=no
//## end module%3C10CC810321.declarations

//## begin module%3C10CC810321.additionalDeclarations preserve=yes
//## end module%3C10CC810321.additionalDeclarations


//## begin CountedRef%3BEFECFF0287.preface preserve=yes
//## end CountedRef%3BEFECFF0287.preface

//## Class: CountedRef%3BEFECFF0287; Parameterized Class
//	This is a type-specific interface to the counted reference
//	mechanism, providing most of the same functions as CountedRefBase,
//	but tailored for type T.  Refer to CountedRefBase for all details.
//## Category: DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



template <class T>
class CountedRef : private CountedRefBase  //## Inherits: private%3C0CE1250396
{
  //## begin CountedRef%3BEFECFF0287.initialDeclarations preserve=yes
  //## end CountedRef%3BEFECFF0287.initialDeclarations

  public:
    //## Constructors (generated)
      CountedRef();

      CountedRef(const CountedRef< T > &right);

    //## Constructors (specified)
      //## Operation: CountedRef%3BF9396D01A7; C++
      //	Generic copy constructor -- see same method in CountedRefBase.
      CountedRef (const CountedRef<T>& other, int flags, int depth = 1);

      //## Operation: CountedRef%3BF93C020247; C++
      explicit CountedRef (T& targ, int flags = 0);

      //## Operation: CountedRef%3BF93D620128; C++
      explicit CountedRef (const T& targ, int flags = 0);

      //## Operation: CountedRef%3BF93F8D0054; C++
      explicit CountedRef (T* targ, int flags = 0);

      //## Operation: CountedRef%3BF93F9702C5; C++
      explicit CountedRef (const T* targ, int flags = 0);

    //## Assignment Operation (generated)
      CountedRef< T > & operator=(const CountedRef< T > &right);

    //## Equality Operations (generated)
      bool operator==(const CountedRef< T > &right) const;

      bool operator!=(const CountedRef< T > &right) const;


    //## Other Operations (specified)
      //## Operation: deref_p%3C8F61C80241
      const T* deref_p () const;

      //## Operation: deref%3BEFED870110; C++
      //	Dereferences to const target.
      const T& deref () const;

      //## Operation: operator ->%3BF55FDC0049; C++
      //	Overloaded deref op, so that ref->method() can be used to call
      //	target's const methods.
      const T* operator -> () const;

      //## Operation: operator *%3C5FBE030173
      const T& operator * () const;

      //## Operation: dewr_p%3C8F61D10199
      T* dewr_p ();

      //## Operation: dewr%3BEFF73602B0; C++
      //	Dereferences to non-const object.
      T& dewr ();

      //## Operation: operator%3C0F806901C1; C++
      //	Dereferences to non-const object. Use e.g. ref().method() to call
      //	target's non-const methods.
      T& operator () ();

      //## Operation: operator const T&%3C0F808100DF; C++
      //	Conversion operators to T& and T* do. implicit dereferencing.
      operator const T& () const;

      //## Operation: operator const T*%3C0F80A50055; C++
      operator const T* () const;

      //## Operation: operator T&%3C0F80B501D4; C++
      operator T& ();

      //## Operation: operator T*%3C0F80C0020C; C++
      operator T* ();

      //## Operation: copy%3BF93A170291; C++
      //	Copies ref -- see CountedRefBase::copy().
      CountedRef<T> copy (int flags = 0) const;

      //## Operation: copy%3C1F2DB802D2
      CountedRef<T> & copy (const CountedRef<T>& other, int flags = 0);

      //## Operation: xfer%3C1F2DD30353
      CountedRef<T> & xfer (CountedRef<T>& other);

      //## Operation: privatize%3C17A06901DC; C++
      //	Privatizes a ref -- see CountedRefBase::privatize().
      CountedRef<T>& privatize (int flags = 0, int depth = 0);

      //## Operation: lock%3C187F270346; C++
      //	Locks ref -- see CountedRefBase::lock().
      CountedRef<T>& lock ();

      //## Operation: unlock%3C187F2E0291; C++
      //	Unlocks ref -- see CountedRefBase::unlock().
      CountedRef<T>& unlock ();

      //## Operation: persist%3C501A15015C
      CountedRef<T>& persist ();

      //## Operation: unpersist%3C501A1C01FD
      CountedRef<T>& unpersist ();

      //## Operation: change%3C1897A5032E; C++
      //	Changes ref properties -- see CountedRefBase::change().
      CountedRef<T>& change (int flags);

      //## Operation: setExclusiveWrite%3C1897B50178; C++
      //	Makes exclusive writer -- see  CountedRefBase::setExclusiveWrite()
      CountedRef<T>& setExclusiveWrite ();

      //## Operation: attach%3BFA4DF4027D; C++
      //	Various methods to attach to target object. See CountedRef
      //	Base::attach(). Const target forces READONLY ref.
      CountedRef<T> & attach (T& targ, int flags = 0);

      //## Operation: attach%3BFA4E070216; C++
      CountedRef<T> & attach (const T& targ, int flags = 0);

      //## Operation: attach%3C179D9E027E; C++
      CountedRef<T> & attach (T* targ, int flags = 0);

      //## Operation: attach%3C179DA9016B; C++
      CountedRef<T> & attach (const T* targ, int flags = 0);

    // Additional Public Declarations
      //## begin CountedRef%3BEFECFF0287.public preserve=yes
      // make public some methods of CountedRefBase which would otherwise
      // be hidden by private inheritance
      CountedRefBase::valid;
      CountedRefBase::detach;
      CountedRefBase::isLocked;
      CountedRefBase::isWritable;
      CountedRefBase::isExclusiveWrite;
      CountedRefBase::isAnonObject;
      CountedRefBase::hasOtherWriters;
      CountedRefBase::debug;
      CountedRefBase::sdebug;
      //## end CountedRef%3BEFECFF0287.public
  protected:
    // Additional Protected Declarations
      //## begin CountedRef%3BEFECFF0287.protected preserve=yes
      CountedRefBase::target;
      //## end CountedRef%3BEFECFF0287.protected

  private:
    // Additional Private Declarations
      //## begin CountedRef%3BEFECFF0287.private preserve=yes
      //## end CountedRef%3BEFECFF0287.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin CountedRef%3BEFECFF0287.implementation preserve=yes
      //## end CountedRef%3BEFECFF0287.implementation

};

//## begin CountedRef%3BEFECFF0287.postscript preserve=yes
//## end CountedRef%3BEFECFF0287.postscript

// Parameterized Class CountedRef 

template <class T>
inline CountedRef<T>::CountedRef()
  //## begin CountedRef::CountedRef%3BEFECFF0287_const.hasinit preserve=no
  //## end CountedRef::CountedRef%3BEFECFF0287_const.hasinit
  //## begin CountedRef::CountedRef%3BEFECFF0287_const.initialization preserve=yes
  : CountedRefBase()
  //## end CountedRef::CountedRef%3BEFECFF0287_const.initialization
{
  //## begin CountedRef::CountedRef%3BEFECFF0287_const.body preserve=yes
  //## end CountedRef::CountedRef%3BEFECFF0287_const.body
}

template <class T>
inline CountedRef<T>::CountedRef(const CountedRef<T> &right)
  //## begin CountedRef::CountedRef%3BEFECFF0287_copy.hasinit preserve=no
  //## end CountedRef::CountedRef%3BEFECFF0287_copy.hasinit
  //## begin CountedRef::CountedRef%3BEFECFF0287_copy.initialization preserve=yes
  : CountedRefBase(right)
  //## end CountedRef::CountedRef%3BEFECFF0287_copy.initialization
{
  //## begin CountedRef::CountedRef%3BEFECFF0287_copy.body preserve=yes
  //## end CountedRef::CountedRef%3BEFECFF0287_copy.body
}

template <class T>
inline CountedRef<T>::CountedRef (const CountedRef<T>& other, int flags, int depth)
  //## begin CountedRef::CountedRef%3BF9396D01A7.hasinit preserve=no
  //## end CountedRef::CountedRef%3BF9396D01A7.hasinit
  //## begin CountedRef::CountedRef%3BF9396D01A7.initialization preserve=yes
  : CountedRefBase(other,flags,depth)
  //## end CountedRef::CountedRef%3BF9396D01A7.initialization
{
  //## begin CountedRef::CountedRef%3BF9396D01A7.body preserve=yes
  //## end CountedRef::CountedRef%3BF9396D01A7.body
}

template <class T>
inline CountedRef<T>::CountedRef (T& targ, int flags)
  //## begin CountedRef::CountedRef%3BF93C020247.hasinit preserve=no
  //## end CountedRef::CountedRef%3BF93C020247.hasinit
  //## begin CountedRef::CountedRef%3BF93C020247.initialization preserve=yes
  : CountedRefBase()
  //## end CountedRef::CountedRef%3BF93C020247.initialization
{
  //## begin CountedRef::CountedRef%3BF93C020247.body preserve=yes
  attach(&targ,flags);
  //## end CountedRef::CountedRef%3BF93C020247.body
}

template <class T>
inline CountedRef<T>::CountedRef (const T& targ, int flags)
  //## begin CountedRef::CountedRef%3BF93D620128.hasinit preserve=no
  //## end CountedRef::CountedRef%3BF93D620128.hasinit
  //## begin CountedRef::CountedRef%3BF93D620128.initialization preserve=yes
  : CountedRefBase()
  //## end CountedRef::CountedRef%3BF93D620128.initialization
{
  //## begin CountedRef::CountedRef%3BF93D620128.body preserve=yes
  attach(&targ,flags|DMI::READONLY);
  //## end CountedRef::CountedRef%3BF93D620128.body
}

template <class T>
inline CountedRef<T>::CountedRef (T* targ, int flags)
  //## begin CountedRef::CountedRef%3BF93F8D0054.hasinit preserve=no
  //## end CountedRef::CountedRef%3BF93F8D0054.hasinit
  //## begin CountedRef::CountedRef%3BF93F8D0054.initialization preserve=yes
  : CountedRefBase()
  //## end CountedRef::CountedRef%3BF93F8D0054.initialization
{
  //## begin CountedRef::CountedRef%3BF93F8D0054.body preserve=yes
  if( !flags&DMI::EXTERNAL )
    flags |= DMI::ANON;
  attach(targ,flags);
  //## end CountedRef::CountedRef%3BF93F8D0054.body
}

template <class T>
inline CountedRef<T>::CountedRef (const T* targ, int flags)
  //## begin CountedRef::CountedRef%3BF93F9702C5.hasinit preserve=no
  //## end CountedRef::CountedRef%3BF93F9702C5.hasinit
  //## begin CountedRef::CountedRef%3BF93F9702C5.initialization preserve=yes
  : CountedRefBase()
  //## end CountedRef::CountedRef%3BF93F9702C5.initialization
{
  //## begin CountedRef::CountedRef%3BF93F9702C5.body preserve=yes
  if( !flags&DMI::EXTERNAL )
    flags |= DMI::ANON;
  attach(targ,flags|DMI::READONLY);
  //## end CountedRef::CountedRef%3BF93F9702C5.body
}


template <class T>
inline CountedRef<T> & CountedRef<T>::operator=(const CountedRef<T> &right)
{
  //## begin CountedRef::operator=%3BEFECFF0287_assign.body preserve=yes
  (*(CountedRefBase*)this) = *(CountedRefBase*)&right;
  return *this;
//  dprintf(5)("      CountedRefBase/%08x assignment: %08x\n",(int)this,(int)&right);
//  return xfer((CountedRef<T>&)right);
  //## end CountedRef::operator=%3BEFECFF0287_assign.body
}



//## Other Operations (inline)
template <class T>
inline const T* CountedRef<T>::deref_p () const
{
  //## begin CountedRef::deref_p%3C8F61C80241.body preserve=yes
  return static_cast<const T*>( getTarget() );
  //## end CountedRef::deref_p%3C8F61C80241.body
}

template <class T>
inline const T& CountedRef<T>::deref () const
{
  //## begin CountedRef::deref%3BEFED870110.body preserve=yes
  return *deref_p();
  //## end CountedRef::deref%3BEFED870110.body
}

template <class T>
inline const T* CountedRef<T>::operator -> () const
{
  //## begin CountedRef::operator ->%3BF55FDC0049.body preserve=yes
  return deref_p();
  //## end CountedRef::operator ->%3BF55FDC0049.body
}

template <class T>
inline const T& CountedRef<T>::operator * () const
{
  //## begin CountedRef::operator *%3C5FBE030173.body preserve=yes
  return deref();
  //## end CountedRef::operator *%3C5FBE030173.body
}

template <class T>
inline T* CountedRef<T>::dewr_p ()
{
  //## begin CountedRef::dewr_p%3C8F61D10199.body preserve=yes
  return static_cast<T*>(getTargetWr());
  //## end CountedRef::dewr_p%3C8F61D10199.body
}

template <class T>
inline T& CountedRef<T>::dewr ()
{
  //## begin CountedRef::dewr%3BEFF73602B0.body preserve=yes
  return *dewr_p();
  //## end CountedRef::dewr%3BEFF73602B0.body
}

template <class T>
inline T& CountedRef<T>::operator () ()
{
  //## begin CountedRef::operator%3C0F806901C1.body preserve=yes
  return dewr();
  //## end CountedRef::operator%3C0F806901C1.body
}

template <class T>
inline CountedRef<T>::operator const T& () const
{
  //## begin CountedRef::operator const T&%3C0F808100DF.body preserve=yes
  return deref();
  //## end CountedRef::operator const T&%3C0F808100DF.body
}

template <class T>
inline CountedRef<T>::operator const T* () const
{
  //## begin CountedRef::operator const T*%3C0F80A50055.body preserve=yes
  return deref_p();
  //## end CountedRef::operator const T*%3C0F80A50055.body
}

template <class T>
inline CountedRef<T>::operator T& ()
{
  //## begin CountedRef::operator T&%3C0F80B501D4.body preserve=yes
  return dewr();
  //## end CountedRef::operator T&%3C0F80B501D4.body
}

template <class T>
inline CountedRef<T>::operator T* ()
{
  //## begin CountedRef::operator T*%3C0F80C0020C.body preserve=yes
  return dewr_p();
  //## end CountedRef::operator T*%3C0F80C0020C.body
}

template <class T>
inline CountedRef<T> CountedRef<T>::copy (int flags) const
{
  //## begin CountedRef::copy%3BF93A170291.body preserve=yes
  return CountedRef<T>(*this,flags|DMI::COPYREF);
  //## end CountedRef::copy%3BF93A170291.body
}

template <class T>
inline CountedRef<T> & CountedRef<T>::copy (const CountedRef<T>& other, int flags)
{
  //## begin CountedRef::copy%3C1F2DB802D2.body preserve=yes
  CountedRefBase::copy(other,flags);
  return *this;
  //## end CountedRef::copy%3C1F2DB802D2.body
}

template <class T>
inline CountedRef<T> & CountedRef<T>::xfer (CountedRef<T>& other)
{
  //## begin CountedRef::xfer%3C1F2DD30353.body preserve=yes
  CountedRefBase::xfer(other);
  return *this;
  //## end CountedRef::xfer%3C1F2DD30353.body
}

template <class T>
inline CountedRef<T>& CountedRef<T>::privatize (int flags, int depth)
{
  //## begin CountedRef::privatize%3C17A06901DC.body preserve=yes
// This simply defers to the base class clone(). It is provided here
// so that specifc types may implement specific kind of cloning.
  CountedRefBase::privatize(flags,depth);
  return *this;
  //## end CountedRef::privatize%3C17A06901DC.body
}

template <class T>
inline CountedRef<T>& CountedRef<T>::lock ()
{
  //## begin CountedRef::lock%3C187F270346.body preserve=yes
  CountedRefBase::lock();
  return *this;
  //## end CountedRef::lock%3C187F270346.body
}

template <class T>
inline CountedRef<T>& CountedRef<T>::unlock ()
{
  //## begin CountedRef::unlock%3C187F2E0291.body preserve=yes
  CountedRefBase::unlock();
  return *this;
  //## end CountedRef::unlock%3C187F2E0291.body
}

template <class T>
inline CountedRef<T>& CountedRef<T>::persist ()
{
  //## begin CountedRef::persist%3C501A15015C.body preserve=yes
  CountedRefBase::persist();
  return *this;
  //## end CountedRef::persist%3C501A15015C.body
}

template <class T>
inline CountedRef<T>& CountedRef<T>::unpersist ()
{
  //## begin CountedRef::unpersist%3C501A1C01FD.body preserve=yes
  CountedRefBase::unpersist();
  return *this;
  //## end CountedRef::unpersist%3C501A1C01FD.body
}

template <class T>
inline CountedRef<T>& CountedRef<T>::change (int flags)
{
  //## begin CountedRef::change%3C1897A5032E.body preserve=yes
  CountedRefBase::change(flags);
  return *this;
  //## end CountedRef::change%3C1897A5032E.body
}

template <class T>
inline CountedRef<T>& CountedRef<T>::setExclusiveWrite ()
{
  //## begin CountedRef::setExclusiveWrite%3C1897B50178.body preserve=yes
  CountedRefBase::setExclusiveWrite();
  return *this;
  //## end CountedRef::setExclusiveWrite%3C1897B50178.body
}

template <class T>
inline CountedRef<T> & CountedRef<T>::attach (T& targ, int flags)
{
  //## begin CountedRef::attach%3BFA4DF4027D.body preserve=yes
  return attach(&targ,flags);
  //## end CountedRef::attach%3BFA4DF4027D.body
}

template <class T>
inline CountedRef<T> & CountedRef<T>::attach (const T& targ, int flags)
{
  //## begin CountedRef::attach%3BFA4E070216.body preserve=yes
  return attach(&targ,flags);
  //## end CountedRef::attach%3BFA4E070216.body
}

template <class T>
inline CountedRef<T> & CountedRef<T>::attach (T* targ, int flags)
{
  //## begin CountedRef::attach%3C179D9E027E.body preserve=yes
  CountedRefBase::attach(targ,flags);
  return *this;
  //## end CountedRef::attach%3C179D9E027E.body
}

template <class T>
inline CountedRef<T> & CountedRef<T>::attach (const T* targ, int flags)
{
  //## begin CountedRef::attach%3C179DA9016B.body preserve=yes
  CountedRefBase::attach(targ,flags);
  return *this;
  //## end CountedRef::attach%3C179DA9016B.body
}

// Parameterized Class CountedRef 

template <class T>
bool CountedRef<T>::operator==(const CountedRef<T> &right) const
{
  //## begin CountedRef::operator==%3BEFECFF0287_eq.body preserve=yes
  return target != 0 && target == right.target;
  //## end CountedRef::operator==%3BEFECFF0287_eq.body
}

template <class T>
bool CountedRef<T>::operator!=(const CountedRef<T> &right) const
{
  //## begin CountedRef::operator!=%3BEFECFF0287_neq.body preserve=yes
  return !(*this == right);
  //## end CountedRef::operator!=%3BEFECFF0287_neq.body
}


// Additional Declarations
  //## begin CountedRef%3BEFECFF0287.declarations preserve=yes
  //## end CountedRef%3BEFECFF0287.declarations

//## begin module%3C10CC810321.epilog preserve=yes
// The DefineRefTypes macro generates typedefs for refs to specific types.
// E.g.: DefineRefType(SmartBlock,BlockRef) will define
//    BlockRef (as CountedRef<SmartBlock>), 
#define DefineRefTypes(type,reftype) typedef CountedRef<type> reftype; 

//## end module%3C10CC810321.epilog


#endif


// Detached code regions:
#if 0
//## begin LockedCountedRef::LockedCountedRef%3C15FE870221.initialization preserve=yes
    : CountedRef<T>(ref,DMI::COPYREF|DMI::LOCKED)
//## end LockedCountedRef::LockedCountedRef%3C15FE870221.initialization

//## begin LockedCountedRef::LockedCountedRef%3C3C41170106.initialization preserve=yes
    : CountedRef<T>(ref,flags)
//## end LockedCountedRef::LockedCountedRef%3C3C41170106.initialization

#endif

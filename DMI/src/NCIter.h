//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3D1C711B0168.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3D1C711B0168.cm

//## begin module%3D1C711B0168.cp preserve=no
//## end module%3D1C711B0168.cp

//## Module: NCIter%3D1C711B0168; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar9\oms\LOFAR\src-links\DMI\NCIter.h

#ifndef NCIter_h
#define NCIter_h 1

//## begin module%3D1C711B0168.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3D1C711B0168.additionalIncludes

//## begin module%3D1C711B0168.includes preserve=yes
//## end module%3D1C711B0168.includes

// NestableContainer
#include "DMI/NestableContainer.h"
//## begin module%3D1C711B0168.declarations preserve=no
//## end module%3D1C711B0168.declarations

//## begin module%3D1C711B0168.additionalDeclarations preserve=yes
//## end module%3D1C711B0168.additionalDeclarations


//## begin NCBaseIter%3D217687023B.preface preserve=yes
//## end NCBaseIter%3D217687023B.preface

//## Class: NCBaseIter%3D217687023B
//	This is a dummy parent class. It is only there to facilitate the
//	friend declarations in NestableCOntainer.
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class NCBaseIter 
{
  //## begin NCBaseIter%3D217687023B.initialDeclarations preserve=yes
  //## end NCBaseIter%3D217687023B.initialDeclarations

  public:
    // Additional Public Declarations
      //## begin NCBaseIter%3D217687023B.public preserve=yes
      //## end NCBaseIter%3D217687023B.public

  protected:
    // Additional Protected Declarations
      //## begin NCBaseIter%3D217687023B.protected preserve=yes
// The base iter class is only there to enable the friend declaration in
// NestableContainer::ConstHook
      static const void *get_pointer(
          int &sz,
          const NestableContainer::ConstHook &hook,
          TypeId tid,
          bool write,
          Thread::Mutex::Lock *lock )
       {
         return hook.get_pointer(sz,tid,write,False,0,lock);
       }
      //## end NCBaseIter%3D217687023B.protected
  private:
    // Additional Private Declarations
      //## begin NCBaseIter%3D217687023B.private preserve=yes
      //## end NCBaseIter%3D217687023B.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin NCBaseIter%3D217687023B.implementation preserve=yes
      //## end NCBaseIter%3D217687023B.implementation

};

//## begin NCBaseIter%3D217687023B.postscript preserve=yes
//## end NCBaseIter%3D217687023B.postscript

//## begin NCConstIter%3D1C6DE50373.preface preserve=yes
//## end NCConstIter%3D1C6DE50373.preface

//## Class: NCConstIter%3D1C6DE50373; Parameterized Class
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3D1C797B019D;NestableContainer::ConstHook { -> }

template <class T>
class NCConstIter : public NCBaseIter  //## Inherits: <unnamed>%3D21769303BF
{
  //## begin NCConstIter%3D1C6DE50373.initialDeclarations preserve=yes
  //## end NCConstIter%3D1C6DE50373.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: NCConstIter%3D1C770701E0
      NCConstIter (const NestableContainer::ConstHook &hook);

      //## Operation: NCConstIter%3D1C772202E3
      NCConstIter (const NestableContainer::ConstHook &hook, bool );

    //## Equality Operations (generated)
      bool operator==(const NCConstIter< T > &right) const;

      bool operator!=(const NCConstIter< T > &right) const;

    //## Relational Operations (generated)
      bool operator<(const NCConstIter< T > &right) const;

      bool operator>(const NCConstIter< T > &right) const;

      bool operator<=(const NCConstIter< T > &right) const;

      bool operator>=(const NCConstIter< T > &right) const;

    //## Dereference Operation (generated)
      T operator*() const;


    //## Other Operations (specified)
      //## Operation: operator ++%3D1C704C00C0
      NCConstIter<T> & operator ++ ();

      //## Operation: operator ++%3D217902039D
      NCConstIter<T> operator ++ (int );

      //## Operation: operator --%3D1C70560146
      NCConstIter<T> & operator -- ();

      //## Operation: operator --%3D2179150123
      NCConstIter<T>  operator -- (int );

      //## Operation: reset%3D1C707102C2
      void reset ();

      //## Operation: end%3D1C708903B7
      bool end () const;

      //## Operation: release%3D1C70A202FE
      void release ();

      //## Operation: next%3D21763A03D5
      T next ();

    // Additional Public Declarations
      //## begin NCConstIter%3D1C6DE50373.public preserve=yes
      int size () const;
      int nleft () const;
      //## end NCConstIter%3D1C6DE50373.public

  protected:
    //## Constructors (generated)
      NCConstIter();

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: ptr%3D1C6F480058
      T* ptr () const;

      //## Attribute: start_ptr%3D1C6F5002E4
      T* start_ptr () const;

      //## Attribute: end_ptr%3D1C6F550237
      T* end_ptr () const;

    // Data Members for Class Attributes

      //## begin NCConstIter::ptr%3D1C6F480058.attr preserve=no  protected: T* {UA} 
      T* ptr_;
      //## end NCConstIter::ptr%3D1C6F480058.attr

      //## begin NCConstIter::start_ptr%3D1C6F5002E4.attr preserve=no  protected: T* {UA} 
      T* start_ptr_;
      //## end NCConstIter::start_ptr%3D1C6F5002E4.attr

      //## begin NCConstIter::end_ptr%3D1C6F550237.attr preserve=no  protected: T* {UA} 
      T* end_ptr_;
      //## end NCConstIter::end_ptr%3D1C6F550237.attr

      //## Attribute: lock%3D1C71AB013D
      //## begin NCConstIter::lock%3D1C71AB013D.attr preserve=no  protected: Thread::Mutex::Lock {UA} 
      Thread::Mutex::Lock lock;
      //## end NCConstIter::lock%3D1C71AB013D.attr

    // Additional Protected Declarations
      //## begin NCConstIter%3D1C6DE50373.protected preserve=yes
      //## end NCConstIter%3D1C6DE50373.protected

  private:
    // Additional Private Declarations
      //## begin NCConstIter%3D1C6DE50373.private preserve=yes
      //## end NCConstIter%3D1C6DE50373.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin NCConstIter%3D1C6DE50373.implementation preserve=yes
      //## end NCConstIter%3D1C6DE50373.implementation

};

//## begin NCConstIter%3D1C6DE50373.postscript preserve=yes
//## end NCConstIter%3D1C6DE50373.postscript

//## begin NCIter%3D1C6E010174.preface preserve=yes
//## end NCIter%3D1C6E010174.preface

//## Class: NCIter%3D1C6E010174; Parameterized Class
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3D1C798101AF;NestableContainer::Hook { -> }

template <class T>
class NCIter : public NCConstIter<T>  //## Inherits: <unnamed>%3D1C6E740101
{
  //## begin NCIter%3D1C6E010174.initialDeclarations preserve=yes
  //## end NCIter%3D1C6E010174.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: NCIter%3D1C7A120398
      NCIter (const NestableContainer::Hook &hook);

      //## Operation: NCIter%3D1C7A190302
      NCIter (const NestableContainer::Hook &hook, bool );


    //## Other Operations (specified)
      //## Operation: operator =%3D1C72040109
      T operator = (T value);

      //## Operation: next%3D21765800D5
      T next (T value);

    // Additional Public Declarations
      //## begin NCIter%3D1C6E010174.public preserve=yes
      //## end NCIter%3D1C6E010174.public

  protected:
    // Additional Protected Declarations
      //## begin NCIter%3D1C6E010174.protected preserve=yes
      //## end NCIter%3D1C6E010174.protected

  private:
    //## Constructors (generated)
      NCIter();

    // Additional Private Declarations
      //## begin NCIter%3D1C6E010174.private preserve=yes
      //## end NCIter%3D1C6E010174.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin NCIter%3D1C6E010174.implementation preserve=yes
      //## end NCIter%3D1C6E010174.implementation

};

//## begin NCIter%3D1C6E010174.postscript preserve=yes
//## end NCIter%3D1C6E010174.postscript

// Class NCBaseIter 

// Parameterized Class NCConstIter 

template <class T>
inline NCConstIter<T>::NCConstIter()
  //## begin NCConstIter::NCConstIter%3D1C6DE50373_const.hasinit preserve=no
  //## end NCConstIter::NCConstIter%3D1C6DE50373_const.hasinit
  //## begin NCConstIter::NCConstIter%3D1C6DE50373_const.initialization preserve=yes
  //## end NCConstIter::NCConstIter%3D1C6DE50373_const.initialization
{
  //## begin NCConstIter::NCConstIter%3D1C6DE50373_const.body preserve=yes
  //## end NCConstIter::NCConstIter%3D1C6DE50373_const.body
}

template <class T>
inline NCConstIter<T>::NCConstIter (const NestableContainer::ConstHook &hook)
  //## begin NCConstIter::NCConstIter%3D1C770701E0.hasinit preserve=no
  //## end NCConstIter::NCConstIter%3D1C770701E0.hasinit
  //## begin NCConstIter::NCConstIter%3D1C770701E0.initialization preserve=yes
  //## end NCConstIter::NCConstIter%3D1C770701E0.initialization
{
  //## begin NCConstIter::NCConstIter%3D1C770701E0.body preserve=yes
  int sz;
  ptr_ = start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),False,&lock)));
  end_ptr_ = start_ptr_ + sz;
  //## end NCConstIter::NCConstIter%3D1C770701E0.body
}

template <class T>
inline NCConstIter<T>::NCConstIter (const NestableContainer::ConstHook &hook, bool )
  //## begin NCConstIter::NCConstIter%3D1C772202E3.hasinit preserve=no
  //## end NCConstIter::NCConstIter%3D1C772202E3.hasinit
  //## begin NCConstIter::NCConstIter%3D1C772202E3.initialization preserve=yes
  //## end NCConstIter::NCConstIter%3D1C772202E3.initialization
{
  //## begin NCConstIter::NCConstIter%3D1C772202E3.body preserve=yes
  int sz;
  ptr_ = start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),False,0)));
  end_ptr_ = start_ptr_ + sz;
  //## end NCConstIter::NCConstIter%3D1C772202E3.body
}


template <class T>
inline bool NCConstIter<T>::operator==(const NCConstIter<T> &right) const
{
  //## begin NCConstIter::operator==%3D1C6DE50373_eq.body preserve=yes
  return ptr() == right.ptr();
  //## end NCConstIter::operator==%3D1C6DE50373_eq.body
}

template <class T>
inline bool NCConstIter<T>::operator!=(const NCConstIter<T> &right) const
{
  //## begin NCConstIter::operator!=%3D1C6DE50373_neq.body preserve=yes
  return ptr() != right.ptr();
  //## end NCConstIter::operator!=%3D1C6DE50373_neq.body
}


template <class T>
inline bool NCConstIter<T>::operator<(const NCConstIter<T> &right) const
{
  //## begin NCConstIter::operator<%3D1C6DE50373_ls.body preserve=yes
  return ptr() < right.ptr();
  //## end NCConstIter::operator<%3D1C6DE50373_ls.body
}

template <class T>
inline bool NCConstIter<T>::operator>(const NCConstIter<T> &right) const
{
  //## begin NCConstIter::operator>%3D1C6DE50373_gt.body preserve=yes
  return ptr() > right.ptr();
  //## end NCConstIter::operator>%3D1C6DE50373_gt.body
}

template <class T>
inline bool NCConstIter<T>::operator<=(const NCConstIter<T> &right) const
{
  //## begin NCConstIter::operator<=%3D1C6DE50373_lseq.body preserve=yes
  return ptr() <= right.ptr();
  //## end NCConstIter::operator<=%3D1C6DE50373_lseq.body
}

template <class T>
inline bool NCConstIter<T>::operator>=(const NCConstIter<T> &right) const
{
  //## begin NCConstIter::operator>=%3D1C6DE50373_gteq.body preserve=yes
  return ptr() >= right.ptr();
  //## end NCConstIter::operator>=%3D1C6DE50373_gteq.body
}


template <class T>
inline T NCConstIter<T>::operator*() const
{
  //## begin NCConstIter::operator*%3D1C6DE50373_deref.body preserve=yes
  return *ptr_;
  //## end NCConstIter::operator*%3D1C6DE50373_deref.body
}



//## Other Operations (inline)
template <class T>
inline NCConstIter<T> & NCConstIter<T>::operator ++ ()
{
  //## begin NCConstIter::operator ++%3D1C704C00C0.body preserve=yes
  ++ptr_;
  return *this;
  //## end NCConstIter::operator ++%3D1C704C00C0.body
}

template <class T>
inline NCConstIter<T> NCConstIter<T>::operator ++ (int )
{
  //## begin NCConstIter::operator ++%3D217902039D.body preserve=yes
  NCConstIter<T> dum = *this;
  ++ptr_;
  return dum;
  //## end NCConstIter::operator ++%3D217902039D.body
}

template <class T>
inline NCConstIter<T> & NCConstIter<T>::operator -- ()
{
  //## begin NCConstIter::operator --%3D1C70560146.body preserve=yes
  --ptr_;
  return *this;
  //## end NCConstIter::operator --%3D1C70560146.body
}

template <class T>
inline NCConstIter<T>  NCConstIter<T>::operator -- (int )
{
  //## begin NCConstIter::operator --%3D2179150123.body preserve=yes
  NCConstIter<T> dum = *this;
  --ptr_;
  return dum;
  //## end NCConstIter::operator --%3D2179150123.body
}

template <class T>
inline void NCConstIter<T>::reset ()
{
  //## begin NCConstIter::reset%3D1C707102C2.body preserve=yes
  ptr_ = start_ptr();
  //## end NCConstIter::reset%3D1C707102C2.body
}

template <class T>
inline bool NCConstIter<T>::end () const
{
  //## begin NCConstIter::end%3D1C708903B7.body preserve=yes
  return ptr() >= end_ptr();
  //## end NCConstIter::end%3D1C708903B7.body
}

template <class T>
inline void NCConstIter<T>::release ()
{
  //## begin NCConstIter::release%3D1C70A202FE.body preserve=yes
  lock.release();
  //## end NCConstIter::release%3D1C70A202FE.body
}

template <class T>
inline T NCConstIter<T>::next ()
{
  //## begin NCConstIter::next%3D21763A03D5.body preserve=yes
  return *ptr_++;
  //## end NCConstIter::next%3D21763A03D5.body
}

//## Get and Set Operations for Class Attributes (inline)

template <class T>
inline T* NCConstIter<T>::ptr () const
{
  //## begin NCConstIter::ptr%3D1C6F480058.get preserve=no
  return ptr_;
  //## end NCConstIter::ptr%3D1C6F480058.get
}

template <class T>
inline T* NCConstIter<T>::start_ptr () const
{
  //## begin NCConstIter::start_ptr%3D1C6F5002E4.get preserve=no
  return start_ptr_;
  //## end NCConstIter::start_ptr%3D1C6F5002E4.get
}

template <class T>
inline T* NCConstIter<T>::end_ptr () const
{
  //## begin NCConstIter::end_ptr%3D1C6F550237.get preserve=no
  return end_ptr_;
  //## end NCConstIter::end_ptr%3D1C6F550237.get
}

// Parameterized Class NCIter 

template <class T>
inline NCIter<T>::NCIter (const NestableContainer::Hook &hook)
  //## begin NCIter::NCIter%3D1C7A120398.hasinit preserve=no
  //## end NCIter::NCIter%3D1C7A120398.hasinit
  //## begin NCIter::NCIter%3D1C7A120398.initialization preserve=yes
  //## end NCIter::NCIter%3D1C7A120398.initialization
{
  //## begin NCIter::NCIter%3D1C7A120398.body preserve=yes
  int sz;
  ptr_ = start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),True,&lock)));
  end_ptr_ = start_ptr_ + sz;
  //## end NCIter::NCIter%3D1C7A120398.body
}

template <class T>
inline NCIter<T>::NCIter (const NestableContainer::Hook &hook, bool )
  //## begin NCIter::NCIter%3D1C7A190302.hasinit preserve=no
  //## end NCIter::NCIter%3D1C7A190302.hasinit
  //## begin NCIter::NCIter%3D1C7A190302.initialization preserve=yes
  //## end NCIter::NCIter%3D1C7A190302.initialization
{
  //## begin NCIter::NCIter%3D1C7A190302.body preserve=yes
  int sz;
  ptr_ = start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),True,0)));
  end_ptr_ = start_ptr_ + sz;
  //## end NCIter::NCIter%3D1C7A190302.body
}



//## Other Operations (inline)
template <class T>
inline T NCIter<T>::operator = (T value)
{
  //## begin NCIter::operator =%3D1C72040109.body preserve=yes
  return *ptr_ = value;
  //## end NCIter::operator =%3D1C72040109.body
}

template <class T>
inline T NCIter<T>::next (T value)
{
  //## begin NCIter::next%3D21765800D5.body preserve=yes
  return *ptr_++ = value;
  //## end NCIter::next%3D21765800D5.body
}

//## begin module%3D1C711B0168.epilog preserve=yes
template <class T>
int NCConstIter<T>::size () const
{
  return end_ptr_ - start_ptr_;
}

template <class T>
int NCConstIter<T>::nleft () const
{
  return ptr_ - start_ptr_;
}


#define __declare_iter(T,arg) typedef NCConstIter<T> NCConstIter_##T; typedef NCIter<T> NCIter_##T;
DoForAllNumericTypes(__declare_iter,);
#undef __declare_iter
//## end module%3D1C711B0168.epilog


#endif

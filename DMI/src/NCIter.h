//	f:\lofar\dvl\lofar\cep\cpa\pscf\src

#ifndef NCIter_h
#define NCIter_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

// NestableContainer
#include "DMI/NestableContainer.h"

//##ModelId=3DB951DC0395
//##Documentation
//## This is a dummy parent class. It is only there to facilitate the
//## friend declarations in NestableCOntainer.
class NCBaseIter 
{
  protected:
// The base iter class is only there to enable the friend declaration in
// NestableContainer::Hook
    //##ModelId=3DB951DD037D
      static const void *get_pointer(
          int &sz,
          const NestableContainer::Hook &hook,
          TypeId tid,
          bool write,
          Thread::Mutex::Lock *lock )
       {
         return hook.get_pointer(sz,tid,write,False,0,lock);
       }
};

//##ModelId=3DB951DC03A6

template <class T>
class NCConstIter : public NCBaseIter
{
  public:
      //##ModelId=3DB951DD03D7
      NCConstIter (const NestableContainer::Hook &hook);

      //##ModelId=3DB951DE0007
      NCConstIter (const NestableContainer::Hook &hook, bool );

    //##ModelId=3DB951DE0031
      bool operator==(const NCConstIter< T > &right) const;

    //##ModelId=3DB951DE004B
      bool operator!=(const NCConstIter< T > &right) const;

    //##ModelId=3DB951DE0064
      bool operator<(const NCConstIter< T > &right) const;

    //##ModelId=3DB951DE007D
      bool operator>(const NCConstIter< T > &right) const;

    //##ModelId=3DB951DE0096
      bool operator<=(const NCConstIter< T > &right) const;

    //##ModelId=3DB951DE00AF
      bool operator>=(const NCConstIter< T > &right) const;

    //##ModelId=3DB951DE00C9
      T operator*() const;


      //##ModelId=3DB951DE00CB
      NCConstIter<T> & operator ++ ();

      //##ModelId=3DB951DE00CC
      NCConstIter<T> operator ++ (int );

      //##ModelId=3DB951DE00DF
      NCConstIter<T> & operator -- ();

      //##ModelId=3DB951DE00E0
      NCConstIter<T>  operator -- (int );

      //##ModelId=3DB951DE00F3
      void reset ();

      //##ModelId=3DB951DE00F4
      bool end () const;

      //##ModelId=3DB951DE00F7
      void release ();

      //##ModelId=3DB951DE00F8
      T next ();

    // Additional Public Declarations
    //##ModelId=3DB951DE00F9
      int size () const;
    //##ModelId=3DB951DE00FB
      int nleft () const;

  protected:
    //##ModelId=3DB951DE00FD
      NCConstIter();

    //##ModelId=3DB951DE00FF
      T* ptr () const;

    //##ModelId=3DB951DE0101
      T* start_ptr () const;

    //##ModelId=3DB951DE0103
      T* end_ptr () const;

    // Data Members for Class Attributes

      //##ModelId=3DB951DD0396
      T* ptr_;

      //##ModelId=3DB951DD03A2
      T* start_ptr_;

      //##ModelId=3DB951DD03B1
      T* end_ptr_;

      //##ModelId=3DB951DD03C3
      Thread::Mutex::Lock lock;

};

//##ModelId=3DB951DC03BA

template <class T>
class NCIter : public NCConstIter<T>
{
  public:
      //##ModelId=3DB951DE0126
      NCIter (const NestableContainer::Hook &hook);

      //##ModelId=3DB951DE0128
      NCIter (const NestableContainer::Hook &hook, bool );


      //##ModelId=3DB951DE012B
      T operator = (T value);

      //##ModelId=3DB951DE012D
      T next (T value);

  private:
    //##ModelId=3DB951DE012F
      NCIter();

};

// Class NCBaseIter 

// Parameterized Class NCConstIter 

//##ModelId=3DB951DE00FD
template <class T>
inline NCConstIter<T>::NCConstIter()
{
}

//##ModelId=3DB951DD03D7
template <class T>
inline NCConstIter<T>::NCConstIter (const NestableContainer::Hook &hook)
{
  int sz;
  ptr_ = start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),False,&lock)));
  end_ptr_ = start_ptr_ + sz;
}

//##ModelId=3DB951DE0007
template <class T>
inline NCConstIter<T>::NCConstIter (const NestableContainer::Hook &hook, bool )
{
  int sz;
  ptr_ = start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),False,0)));
  end_ptr_ = start_ptr_ + sz;
}


//##ModelId=3DB951DE0031
template <class T>
inline bool NCConstIter<T>::operator==(const NCConstIter<T> &right) const
{
  return ptr() == right.ptr();
}

//##ModelId=3DB951DE004B
template <class T>
inline bool NCConstIter<T>::operator!=(const NCConstIter<T> &right) const
{
  return ptr() != right.ptr();
}


//##ModelId=3DB951DE0064
template <class T>
inline bool NCConstIter<T>::operator<(const NCConstIter<T> &right) const
{
  return ptr() < right.ptr();
}

template <class T>
inline bool NCConstIter<T>::operator>(const NCConstIter<T> &right) const
{
  return ptr() > right.ptr();
}

//##ModelId=3DB951DE0096
template <class T>
inline bool NCConstIter<T>::operator<=(const NCConstIter<T> &right) const
{
  return ptr() <= right.ptr();
}

//##ModelId=3DB951DE00AF
template <class T>
inline bool NCConstIter<T>::operator>=(const NCConstIter<T> &right) const
{
  return ptr() >= right.ptr();
}


//##ModelId=3DB951DE00C9
template <class T>
inline T NCConstIter<T>::operator*() const
{
  return *ptr_;
}



//##ModelId=3DB951DE00CB
template <class T>
inline NCConstIter<T> & NCConstIter<T>::operator ++ ()
{
  ++ptr_;
  return *this;
}

//##ModelId=3DB951DE00CC
template <class T>
inline NCConstIter<T> NCConstIter<T>::operator ++ (int )
{
  NCConstIter<T> dum = *this;
  ++ptr_;
  return dum;
}

//##ModelId=3DB951DE00DF
template <class T>
inline NCConstIter<T> & NCConstIter<T>::operator -- ()
{
  --ptr_;
  return *this;
}

//##ModelId=3DB951DE00E0
template <class T>
inline NCConstIter<T>  NCConstIter<T>::operator -- (int )
{
  NCConstIter<T> dum = *this;
  --ptr_;
  return dum;
}

//##ModelId=3DB951DE00F3
template <class T>
inline void NCConstIter<T>::reset ()
{
  ptr_ = start_ptr();
}

//##ModelId=3DB951DE00F4
template <class T>
inline bool NCConstIter<T>::end () const
{
  return ptr() >= end_ptr();
}

//##ModelId=3DB951DE00F7
template <class T>
inline void NCConstIter<T>::release ()
{
  lock.release();
}

//##ModelId=3DB951DE00F8
template <class T>
inline T NCConstIter<T>::next ()
{
  return *ptr_++;
}

//##ModelId=3DB951DE00FF
template <class T>
inline T* NCConstIter<T>::ptr () const
{
  return ptr_;
}

//##ModelId=3DB951DE0101
template <class T>
inline T* NCConstIter<T>::start_ptr () const
{
  return start_ptr_;
}

//##ModelId=3DB951DE0103
template <class T>
inline T* NCConstIter<T>::end_ptr () const
{
  return end_ptr_;
}

// Parameterized Class NCIter 

//##ModelId=3DB951DE0126
template <class T>
inline NCIter<T>::NCIter (const NestableContainer::Hook &hook)
{
  int sz;
  ptr_ = start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),True,&lock)));
  end_ptr_ = start_ptr_ + sz;
}

//##ModelId=3DB951DE0128
template <class T>
inline NCIter<T>::NCIter (const NestableContainer::Hook &hook, bool )
{
  int sz;
  ptr_ = start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),True,0)));
  end_ptr_ = start_ptr_ + sz;
}



//##ModelId=3DB951DE012B
template <class T>
inline T NCIter<T>::operator = (T value)
{
  return *ptr_ = value;
}

//##ModelId=3DB951DE012D
template <class T>
inline T NCIter<T>::next (T value)
{
  return *ptr_++ = value;
}

//##ModelId=3DB951DE00F9
template <class T>
int NCConstIter<T>::size () const
{
  return end_ptr_ - start_ptr_;
}

//##ModelId=3DB951DE00FB
template <class T>
int NCConstIter<T>::nleft () const
{
  return ptr_ - start_ptr_;
}


#define __declare_iter(T,arg) typedef NCConstIter<T> NCConstIter_##T; typedef NCIter<T> NCIter_##T;
DoForAllNumericTypes(__declare_iter,);
__declare_iter(string,arg);
#undef __declare_iter


#endif

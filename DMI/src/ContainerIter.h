//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#ifndef DMI_ContainerIter_h
#define DMI_ContainerIter_h 1

#include <DMI/Container.h>

namespace DMI
{
    
//##ModelId=3DB951DC0395
//##Documentation
//## This parent class only provides the get_pointer() function
//## and a lock. It is there to facilitate the friend declarations in 
//## Container::Hook
class BaseContainerIter 
{
  public:
      void release ();
      
  protected:
    //##ModelId=3DB951DD037D
      const void * get_pointer(int &sz,const Container::Hook &hook,
          TypeId tid,bool write,bool set_lock)
       {
         return hook.get_pointer(sz,tid,write,false,0,set_lock?&lock_:0);
       }
       
    Thread::Mutex::Lock lock_;
};

//##ModelId=3DB951DC03A6

template <class T>
class ConstContainerIter : public BaseContainerIter
{
  public:
      //##ModelId=3DB951DE0007
      ConstContainerIter (const Container::Hook &hook, bool set_lock=true);

    //##ModelId=3DB951DE0031
      bool operator==(const ConstContainerIter< T > &right) const;

    //##ModelId=3DB951DE004B
      bool operator!=(const ConstContainerIter< T > &right) const;

    //##ModelId=3DB951DE0064
      bool operator<(const ConstContainerIter< T > &right) const;

    //##ModelId=3DB951DE007D
      bool operator>(const ConstContainerIter< T > &right) const;

    //##ModelId=3DB951DE0096
      bool operator<=(const ConstContainerIter< T > &right) const;

    //##ModelId=3DB951DE00AF
      bool operator>=(const ConstContainerIter< T > &right) const;

    //##ModelId=3DB951DE00C9
      T operator*() const;


      //##ModelId=3DB951DE00CB
      ConstContainerIter<T> & operator ++ ();

      //##ModelId=3DB951DE00CC
      ConstContainerIter<T> operator ++ (int );

      //##ModelId=3DB951DE00DF
      ConstContainerIter<T> & operator -- ();

      //##ModelId=3DB951DE00E0
      ConstContainerIter<T>  operator -- (int );

      //##ModelId=3DB951DE00F3
      void reset ();

      //##ModelId=3DB951DE00F4
      bool end () const;

      //##ModelId=3DB951DE00F7

      //##ModelId=3DB951DE00F8
      T next ();

    // Additional Public Declarations
    //##ModelId=3DB951DE00F9
      int size () const;
    //##ModelId=3DB951DE00FB
      int nleft () const;

  protected:
    //##ModelId=3DB951DE00FD
      ConstContainerIter();

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

};

//##ModelId=3DB951DC03BA

template <class T>
class ContainerIter : public ConstContainerIter<T>
{
  public:
      //##ModelId=3DB951DE0128
      ContainerIter (const Container::Hook &hook, bool set_lock=true);


      //##ModelId=3DB951DE012B
      T operator = (T value);

      //##ModelId=3DB951DE012D
      T next (T value);

  private:
    //##ModelId=3DB951DE012F
      ContainerIter();

};

// Class NCBaseIter 

// Parameterized Class ConstContainerIter 

//##ModelId=3DB951DE00FD
template <class T>
inline ConstContainerIter<T>::ConstContainerIter()
{
}

//##ModelId=3DB951DD03D7
template <class T>
inline ConstContainerIter<T>::ConstContainerIter (const Container::Hook &hook,bool set_lock)
{
  int sz;
  ptr_ = start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),false,set_lock)));
  end_ptr_ = start_ptr_ + sz;
}

//##ModelId=3DB951DE0031
template <class T>
inline bool ConstContainerIter<T>::operator==(const ConstContainerIter<T> &right) const
{
  return ptr() == right.ptr();
}

//##ModelId=3DB951DE004B
template <class T>
inline bool ConstContainerIter<T>::operator!=(const ConstContainerIter<T> &right) const
{
  return ptr() != right.ptr();
}


//##ModelId=3DB951DE0064
template <class T>
inline bool ConstContainerIter<T>::operator<(const ConstContainerIter<T> &right) const
{
  return ptr() < right.ptr();
}

template <class T>
inline bool ConstContainerIter<T>::operator>(const ConstContainerIter<T> &right) const
{
  return ptr() > right.ptr();
}

//##ModelId=3DB951DE0096
template <class T>
inline bool ConstContainerIter<T>::operator<=(const ConstContainerIter<T> &right) const
{
  return ptr() <= right.ptr();
}

//##ModelId=3DB951DE00AF
template <class T>
inline bool ConstContainerIter<T>::operator>=(const ConstContainerIter<T> &right) const
{
  return ptr() >= right.ptr();
}


//##ModelId=3DB951DE00C9
template <class T>
inline T ConstContainerIter<T>::operator*() const
{
  return *ptr_;
}



//##ModelId=3DB951DE00CB
template <class T>
inline ConstContainerIter<T> & ConstContainerIter<T>::operator ++ ()
{
  ++ptr_;
  return *this;
}

//##ModelId=3DB951DE00CC
template <class T>
inline ConstContainerIter<T> ConstContainerIter<T>::operator ++ (int )
{
  ConstContainerIter<T> dum = *this;
  ++ptr_;
  return dum;
}

//##ModelId=3DB951DE00DF
template <class T>
inline ConstContainerIter<T> & ConstContainerIter<T>::operator -- ()
{
  --ptr_;
  return *this;
}

//##ModelId=3DB951DE00E0
template <class T>
inline ConstContainerIter<T>  ConstContainerIter<T>::operator -- (int )
{
  ConstContainerIter<T> dum = *this;
  --ptr_;
  return dum;
}

//##ModelId=3DB951DE00F3
template <class T>
inline void ConstContainerIter<T>::reset ()
{
  ptr_ = start_ptr();
}

//##ModelId=3DB951DE00F4
template <class T>
inline bool ConstContainerIter<T>::end () const
{
  return ptr() >= end_ptr();
}

//##ModelId=3DB951DE00F7
inline void BaseContainerIter::release ()
{
  lock_.release();
}

//##ModelId=3DB951DE00F8
template <class T>
inline T ConstContainerIter<T>::next ()
{
  return *ptr_++;
}

//##ModelId=3DB951DE00FF
template <class T>
inline T* ConstContainerIter<T>::ptr () const
{
  return ptr_;
}

//##ModelId=3DB951DE0101
template <class T>
inline T* ConstContainerIter<T>::start_ptr () const
{
  return start_ptr_;
}

//##ModelId=3DB951DE0103
template <class T>
inline T* ConstContainerIter<T>::end_ptr () const
{
  return end_ptr_;
}

// Parameterized Class ContainerIter 

//##ModelId=3DB951DE0128
template <class T>
inline ContainerIter<T>::ContainerIter (const Container::Hook &hook, bool set_lock)
{
  int sz;
  ConstContainerIter<T>::ptr_ = ConstContainerIter<T>::start_ptr_ = 
      static_cast<T*>(const_cast<void*>(get_pointer(sz,hook,typeIdOf(T),true,set_lock)));
  ConstContainerIter<T>::end_ptr_ = ConstContainerIter<T>::start_ptr_ + sz;
}



//##ModelId=3DB951DE012B
template <class T>
inline T ContainerIter<T>::operator = (T value)
{
  return *ConstContainerIter<T>::ptr_ = value;
}

//##ModelId=3DB951DE012D
template <class T>
inline T ContainerIter<T>::next (T value)
{
  return *ConstContainerIter<T>::ptr_++ = value;
}

//##ModelId=3DB951DE00F9
template <class T>
int ConstContainerIter<T>::size () const
{
  return ConstContainerIter<T>::end_ptr_ - ConstContainerIter<T>::start_ptr_;
}

//##ModelId=3DB951DE00FB
template <class T>
int ConstContainerIter<T>::nleft () const
{
  return ConstContainerIter<T>::ptr_ - ConstContainerIter<T>::start_ptr_;
}


//#define __declare_iter(T,arg) typedef ConstContainerIter<T> ConstContainerIter_##T; typedef ContainerIter<T> ContainerIter_##T;
//DoForAllNumericTypes(__declare_iter,);
//__declare_iter(string,arg);
//#undef __declare_iter


};
#endif

//#  Key.h: Thread key class.
//#
//#  Copyright (C) 2002-2004
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef LOFAR_COMMON_THREAD_KEY_H
#define LOFAR_COMMON_THREAD_KEY_H

//# Includes
#include <Common/Thread/Thread.h>

namespace LOFAR
{
  namespace Thread 
  {
#ifdef USE_THREADS

    //##ModelId=3D1049B402A5
    class Key 
    {
    public:
      //##ModelId=3DB935A10284
      typedef void* Data;
      //##ModelId=5984F88AFEED
      Key (void (*destructor) (void*) = 0);

      //##ModelId=3DB935A300E6
      ~Key();


      //##ModelId=3B3DE74FFEED
      Key::Data get () const;

      //##ModelId=60738D38FEED
      int set (Key::Data value);

      //##ModelId=AFEDB0DBFEED
      operator Key::Data () const;

      //##ModelId=66708D53FEED
      Thread::Key& operator = (Key::Data value);

    private:
      //##ModelId=3DB935A3012D
      Key(const Key &right);

      //##ModelId=3DB935A301AF
      Key & operator=(const Key &right);

    private:
      // Data Members for Class Attributes

      //##ModelId=3D1060CB03CF
      pthread_key_t key;

    };

    // Class Thread::Key 

    //##ModelId=5984F88AFEED
    //##ModelId=3DB935A3012D
    inline Key::Key (void (*destructor) (void*))
    {
      pthread_key_create(&key,destructor); 
    }


    //##ModelId=3DB935A300E6
    inline Key::~Key()
    {
      pthread_key_delete(key); 
    }



    //##ModelId=3B3DE74FFEED
    inline Key::Data Key::get () const
    {
      return pthread_getspecific(key); 
    }

    //##ModelId=60738D38FEED
    inline int Key::set (Key::Data value)
    {
      return pthread_setspecific(key,value); 
    }

    inline Key::operator Key::Data () const
    {
      return get();
    }

    //##ModelId=66708D53FEED
    inline Thread::Key& Key::operator = (Key::Data value)
    {
      set(value);
      return *this;
    }

    // Class Thread::Key 

#else

    class Key 
    { 
    public:
      typedef void * Data; 
    };

#endif

  } // namespace Thread

} // namespace LOFAR

#endif

//#  Mutex.h: Thread mutex class.
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

#ifndef LOFAR_COMMON_THREAD_MUTEX_H
#define LOFAR_COMMON_THREAD_MUTEX_H

//# Includes
#include <Common/Thread/Thread.h>

namespace LOFAR
{
  namespace Thread {
    // declare a functional Mutex only when USE_THREADS is defined.
    // Otherwise, declare just a skeleton class (to keep, e.g., declarations
    // consistent)
#ifdef USE_THREADS

    //##ModelId=3D1049B40332
    class Mutex 
    {
    public:
      // This is completely non-portable, but pthread.h has me confused
      // In any event, mutex type implementation is OS-dependent (and we can
      // always do recursion and error-checking in the Mutex class itself)
      //##ModelId=3DB935A103A1
      typedef enum { DEFAULT    = PTHREAD_MUTEX_TIMED_NP,
                     FAST       = DEFAULT,
                     RECURSIVE  = PTHREAD_MUTEX_RECURSIVE_NP,
                     ERRORCHECK = PTHREAD_MUTEX_ERRORCHECK_NP } MutexKind;

      //##ModelId=3DB935A103C9
      typedef enum { TRY=1 } MutexOptions;

      //##ModelId=3D1049B40396

      class Lock 
      {
      public:
        //##ModelId=5571A783FEED
        Lock();

        //##ModelId=A15218DBFEED
        Lock(const Lock &right);
            
        Lock & operator = (const Lock &right);

        //##ModelId=3DB935A30335
        Lock (pthread_mutex_t &mutex, int options = 0);

        //##ModelId=3DB935A40034
        Lock (const Thread::Mutex &mutex, int options = 0);

        //##ModelId=3DB935A4012E
        ~Lock();


        //##ModelId=D5165FA7FEED
        bool locked () const;

        //##ModelId=18054E53FEED
        operator bool () const;

        //##ModelId=E5D40595FEED
        bool operator ! () const;

        //##ModelId=E2FBE0C8FEED
        int release ();

        //##ModelId=D8B60901FEED
        void release_without_unlock ();

        //##Documentation
        //## lock() releases current mutex (if any), then obtains 
        //## a lock on the new mutex
        int lock (const Thread::Mutex &mutex, int options = 0);
            
        //##ModelId=3D19CF980270
        //##Documentation
        //## relock() works the othe way around: first obtains a lock 
        //## on the new mutex, then releases the current one
        int relock (const Thread::Mutex &mutex, int options = 0);

        // Additional Public Declarations
        //##ModelId=3DB935A401EC
        const char * debug (int = 1,const string & = "",const char * = 0 ) const
        { return "Mutex::Lock"; }
        //##ModelId=3DB935A4039B
        string sdebug (int = 1,const string & = "",const char * = 0 ) const
        { return debug(); }
      private:

        //##ModelId=5FDF0A36FEED
        void init (const pthread_mutex_t &mtx, int options = 0);

      private:
        // Data Members for Class Attributes

        //##ModelId=3D10514502E9
        pthread_mutex_t *pmutex;

      };

      //##ModelId=70B8C5D3FEED
      Mutex (int kind = RECURSIVE);

      //##ModelId=3D10B976039C
      Mutex (const Mutex &right);

      //##ModelId=3DB935A5020C
      ~Mutex();


      //##ModelId=3D10BC47035F
      Mutex & operator = (const Mutex &right);

      //##ModelId=D4F415F7FEED
      int lock () const;

      //##ModelId=4304D0E8FEED
      int unlock () const;

      //##ModelId=A4649BF5FEED
      int trylock () const;

    public:
      // Additional Public Declarations
      friend class Lock;
    
      //##ModelId=3DB935A5023E
      const char * debug (int = 1,const string & = "",const char * = 0 ) const
      { return "Mutex"; }
      //##ModelId=3DB935A50388
      string sdebug (int = 1,const string & = "",const char * = 0 ) const
      { return debug(); }
    protected:

      //##ModelId=9C882969FEED
      void init (int kind);

      // Data Members for Class Attributes

      //##ModelId=3D10515D008B
      mutable pthread_mutex_t mutex;

    };

    //##ModelId=5571A783FEED
    inline Mutex::Lock::Lock()
      : pmutex(0)
    {
    }

    inline Mutex::Lock::Lock(const Mutex::Lock &right)
    {
      if( right.pmutex )
        init(*right.pmutex,0);
      else
        pmutex = 0;
      
    }
  
    inline Mutex::Lock & Mutex::Lock::operator =(const Mutex::Lock &right)
    {
      if( pmutex ) 
        pthread_mutex_unlock(pmutex); 
      init(*right.pmutex,0);
      return *this;
    }

    //##ModelId=3DB935A30335
    inline Mutex::Lock::Lock (pthread_mutex_t &mutex, int options)
    {
      init(mutex,options);
    }

    //##ModelId=3DB935A40034
    inline Mutex::Lock::Lock (const Thread::Mutex &mutex, int options)
    {
      init(mutex.mutex,options);
    }


    //##ModelId=3DB935A4012E
    inline Mutex::Lock::~Lock()
    {
      if( pmutex ) 
        pthread_mutex_unlock(pmutex); 
    }
  
    inline void Mutex::Lock::init (const pthread_mutex_t &mtx, int options)
    {
      pmutex = const_cast<pthread_mutex_t *>(&mtx);
      if( options == TRY )
      {
        dprintf(3)("init: try-locking mutex @%08X\n",(int)pmutex);
        if( pthread_mutex_trylock(pmutex) < 0 )
          pmutex = 0;
      }
      else
      {
        dprintf(3)("init: locking mutex @%08X\n",(int)pmutex);
        pthread_mutex_lock(pmutex);
      }
      dprintf(3)("init: locked mutex @%08X\n",(int)pmutex);
    }

    //##ModelId=D5165FA7FEED
    inline bool Mutex::Lock::locked () const
    {
      return pmutex != 0;
    }

    //##ModelId=18054E53FEED
    inline Mutex::Lock::operator bool () const
    {
      return locked();
    }

    //##ModelId=E5D40595FEED
    inline bool Mutex::Lock::operator ! () const
    {
      return !locked();
    }

    //##ModelId=E2FBE0C8FEED
    inline int Mutex::Lock::release ()
    {
      dprintf(3)("release: unlocking mutex @%08X\n",(int)pmutex);
      int ret = pmutex ? pthread_mutex_unlock(pmutex) : 0;
      pmutex = 0;
      return ret; 
    }

    //##ModelId=D8B60901FEED
    inline void Mutex::Lock::release_without_unlock ()
    {
      dprintf(3)("release: relasing w/o unlock mutex @%08X\n",(int)pmutex);
      pmutex = 0;
    }

    //##ModelId=3D19CF980270
    inline int Mutex::Lock::relock (const Thread::Mutex &mutex, int options)
    {
      pthread_mutex_t *old = pmutex;
      init(mutex.mutex,options);
      if( old )
      {
        dprintf(3)("relock: unlocking old mutex @%08X\n",(int)old);
        pthread_mutex_unlock(old);
      }
      return 0;
    }

    inline int Mutex::Lock::lock (const Thread::Mutex &mutex, int options)
    {
      release();
      init(mutex.mutex,options);
      return 0;
    }
  
    // Class Thread::Mutex 

    //##ModelId=70B8C5D3FEED
    inline Mutex::Mutex (int kind)
    {
      init(kind);
    }

    //##ModelId=3D10B976039C
    inline Mutex::Mutex (const Mutex &right)
    {
      init(right.mutex.__m_kind);
    }


    //##ModelId=3DB935A5020C
    inline Mutex::~Mutex()
    {
      pthread_mutex_destroy(&mutex);
    }

    //##ModelId=9C882969FEED
    inline void Mutex::init (int kind)
    {
      pthread_mutexattr_t attr = { kind  };
      pthread_mutex_init(&mutex,&attr); 
      dprintf(3)("initialized mutex %08x kind %d\n",(int)&mutex,kind);
    }

    //##ModelId=3D10BC47035F
    inline Mutex & Mutex::operator = (const Mutex &right)
    {
      pthread_mutex_destroy(&mutex);
      init(right.mutex.__m_kind);
      return *this;
    }

    //##ModelId=D4F415F7FEED
    inline int Mutex::lock () const
    {
      dprintf(3)("%d: locking mutex %08x\n",(int)self().id(),(int)&mutex);
      int ret = pthread_mutex_lock(&mutex); 
      dprintf(3)("%d: locked mutex %08x: %d\n",(int)self().id(),(int)&mutex,ret);
      return ret;
    }

    //##ModelId=4304D0E8FEED
    inline int Mutex::unlock () const
    {
      int ret = pthread_mutex_unlock(&mutex); 
      dprintf(3)("%d: unlocked mutex %08x: %d\n",(int)self().id(),(int)&mutex,ret);
      return ret;
    }

    //##ModelId=A4649BF5FEED
    inline int Mutex::trylock () const
    {
      return pthread_mutex_trylock(&mutex);
    }

    // Class Thread::Mutex::Lock 

    // Class Thread::Mutex 

#else // no-threads configuration
    class Mutex
    {
    public:
      class Lock 
      {
      public:
        Lock () {}
        Lock (pthread_mutex_t &, int = 0) {};
        Lock (const Thread::Mutex &, int = 0) {};

        bool locked () const { return false; };
        operator bool () const { return false;};
        bool operator ! () const { return false; };
        int release () { return 0; };
        void release_without_unlock () {};
        int relock (const Thread::Mutex &, int = 0) { return 0; }

        const char * debug (int = 1,const string & = "",const char * = 0 ) const
        { return ""; }
        string sdebug (int = 1,const string & = "",const char * = 0 ) const
        { return debug(); }
      };
    };
#endif

  } // namespace Thread

} // namespace LOFAR

#endif

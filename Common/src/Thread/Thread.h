//#  Thread.h: Thread class that wraps raw pthreads.
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

#ifndef LOFAR_COMMON_THREAD_THREAD_H
#define LOFAR_COMMON_THREAD_THREAD_H

#include <Common/Debug.h>
#ifdef USE_THREADS
#include <pthread.h>
#include <signal.h>
#endif

namespace LOFAR
{
  namespace Thread 
  {
#ifdef USE_THREADS
    extern void * dummy_pvoid;
    extern int dummy_int;
  
    extern ::Debug::Context DebugContext;
    inline ::Debug::Context & getDebugContext() 
    { return DebugContext; }
  
    //##ModelId=3D1049B401F1
    class ThrID 
    {
    private:
      //##ModelId=3D105E60038E
      pthread_t id_;

    public:
      //##ModelId=E3D481F0FEED
      ThrID()                         : id_(0)  {}

      //##ModelId=3DB935AD011A
      ThrID (pthread_t id)            : id_(id) {}

      //##ModelId=3DB935AD0160
      bool operator == (ThrID right) const      
      { return pthread_equal(id_,right.id_); }
      //##ModelId=3DB935AD01BA
      bool operator != (ThrID right) const
      { return !( (*this) == right ); }
      bool operator <  (ThrID right) const
      { return id_ < right.id_; }
      bool operator <= (ThrID right) const
      { return id_ <= right.id_; }
      bool operator >  (ThrID right) const
      { return id_ > right.id_; }
      bool operator >= (ThrID right) const
      { return id_ >= right.id_; }

      //##ModelId=981A70A9FEED
      operator pthread_t () const     { return id_; }
      //##ModelId=3DB935AD0250
      pthread_t id () const           { return id_; }

      //##ModelId=A4925AC3FEED
      ThrID & operator = (pthread_t id)
      { id_ = id; return *this; }
        
      // Joins a thread
      int join (void * &value = dummy_pvoid)
      { return pthread_join(id_,&value);  }
      // Cancels a thread
      int cancel ()
      { return pthread_cancel(id_); }
      // Detaches a thread
      int detach ()
      { return pthread_detach(id_); }
      // Sends a signal to a thread
      inline int kill (int sig)
      { return pthread_kill(id_,sig); }
  
      //##ModelId=98935E61FEED
      static ThrID self ()
      { return ThrID(pthread_self()); }
    };
  

    class Attributes
    {
    private:
      pthread_attr_t attr;
    
    public:
      typedef enum 
        {
          JOINABLE  = PTHREAD_CREATE_JOINABLE,
          DETACHED  = PTHREAD_CREATE_DETACHED
        } AttributeCode;
        
      Attributes  ()           { pthread_attr_init(&attr); }
      Attributes  (int st)     { pthread_attr_init(&attr); 
      pthread_attr_setdetachstate(&attr,st); }
      ~Attributes ()           { pthread_attr_destroy(&attr); }
        
      operator pthread_attr_t & ()              { return attr; }
      operator const pthread_attr_t & () const  { return attr; }
      operator pthread_attr_t * ()              { return &attr; }
      operator const pthread_attr_t * () const  { return &attr; }
        
      // query attributes
      int detachState() const   { int res; pthread_attr_getdetachstate(&attr,&res); return res; }
      bool joinable () const    { return detachState() == JOINABLE; }
      bool detached () const    { return detachState() == DETACHED; }
        
      // set attributes
      Attributes & setDetachState (int st) { pthread_attr_setdetachstate(&attr,st); return *this; }
        
      Attributes & setJoinable ()   { return setDetachState(JOINABLE); }
      Attributes & setDetached ()   { return setDetachState(DETACHED); }
        
      static const Attributes & Null ();
    };

    extern const Attributes _null_attributes;
  
    inline const Attributes & Attributes::Null ()
    { return _null_attributes; }
          
    inline Attributes joinable ()
    { return Attributes(Attributes::JOINABLE); }
  
    inline Attributes detached ()
    { return Attributes(Attributes::DETACHED); }
  
    // -----------------------------------------------------------------------
    // Thread functions
    // -----------------------------------------------------------------------
  
    // returns thread id of self
    inline ThrID self ()
    { 
      return ThrID::self(); 
    }

    // Thread::create() creates a thred
    ThrID create (void * (*start)(void*),void *arg=0,const Attributes &attr = Attributes::Null());
  
    // Exits a thread
    inline void exit (void *value=0)
    { 
      pthread_exit(value); 
    }
  
    // Sets the sigmask for a thread
    inline int signalMask (int how,const sigset_t *newmask,sigset_t *oldmask = 0)
    {
      return pthread_sigmask(how,newmask,oldmask);
    }
  
    // Sets a single signal in a thread's sigmask
    inline int signalMask (int how,int sig,sigset_t *oldmask = 0)
    {
      sigset_t sset;
      sigemptyset(&sset);
      sigaddset(&sset,sig);
      return pthread_sigmask(how,&sset,oldmask);
    }
  
    // sets the thread's cancellation state
    inline int setCancelState (int state,int &oldstate = dummy_int)
    {
      return pthread_setcancelstate(state,&oldstate);
    }
  
    // sets the thread's cancellation type
    inline int setCancelType (int type,int &oldtype = dummy_int)
    {
      return pthread_setcanceltype(type,&oldtype);
    }
  
    inline void testCancel ()
    {
      pthread_testcancel();
    }
  

    // constant: the null thread id
    const ThrID ThrID_null;

#else

  typedef int ThrID;
  class Attributes {};

#endif

  } // namespace Thread
  
} // namespace LOFAR

#ifdef MAKE_LOFAR_SYMBOLS_GLOBAL

namespace Thread
{
  using namespace LOFAR::Thread;
}

#endif

#endif

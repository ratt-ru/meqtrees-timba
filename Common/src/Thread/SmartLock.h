//#  SmartLock.h: Threads SmartLock class.
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

#ifndef LOFAR_COMMON_THREAD_SMARTLOCK_H
#define LOFAR_COMMON_THREAD_SMARTLOCK_H

//# Includes
#include <Common/Thread/Condition.h>

namespace LOFAR 
{
  namespace Thread 
  {

#ifdef USE_THREADS

    //##ModelId=3D1049B500A8
    class SmartLock 
    {
    public:
      //##ModelId=3D1049B50102
      class BaseLock 
      {
      public:
        //##ModelId=27D9633CFEED
        BaseLock (const Thread::SmartLock* pl = 0);


        //##ModelId=7B209A65FEED
        bool locked () const;

        //##ModelId=13FE864CFEED
        operator bool () const;

        //##ModelId=97F0E174FEED
        bool operator ! () const;

      protected:
        // Data Members for Associations

        //##ModelId=3D104B990090
        const SmartLock *plock;

      };

      //##ModelId=3D1049B5012A

      class Read : public BaseLock
      {
      public:
        //##ModelId=2E156332FEED
        Read();

        //##ModelId=3DB935A601E5
        Read(const Read &right);

        //##ModelId=3DB935A60217
        Read (const Thread::SmartLock& lock);

        //##ModelId=3DB935A6025D
        ~Read();

        //##ModelId=3DB935A60271
        Read & operator=(const Read &right);


        //##ModelId=0A10BCC1FEED
        int release ();

        //##ModelId=3D1981B2020C
        int relock (const Thread::SmartLock &lock);

        // Additional Public Declarations
        //##ModelId=3DB935A602CB
        const char * debug (int = 1,const string & = "",const char * = 0 ) const
        { return "SmartLock::Read"; }
        //##ModelId=3DB935A603BC
        string sdebug (int = 1,const string & = "",const char * = 0 ) const
        { return debug(); }
      };

      //##ModelId=3D1049B50171

      class Write : public BaseLock
      {
      public:
        //##ModelId=90340814FEED
        Write();

        //##ModelId=3DB935A7015A
        Write(const Write &right);

        //##ModelId=3DB935A70196
        Write (const Thread::SmartLock& lock);

        //##ModelId=3DB935A701DD
        ~Write();

        //##ModelId=3DB935A701E7
        Write & operator=(const Write &right);


        //##ModelId=86E22961FEED
        int release ();

        //##ModelId=3D1981ED0080
        int relock (const Thread::SmartLock &lock);

        // Additional Public Declarations
        //##ModelId=3DB935A70255
        const char * debug (int = 1,const string & = "",const char * = 0 ) const
        { return "SmartLock::Write"; }
        //##ModelId=3DB935A7039F
        string sdebug (int = 1,const string & = "",const char * = 0 ) const
        { return debug(); }
      };

      //##ModelId=3D1049B501AE

      class Lock : public BaseLock
      {
      public:
        //##ModelId=CCA65344FEED
        Lock();

        //##ModelId=3DB935A801FA
        Lock(const Lock &right);

        //##ModelId=3DB935A8025E
        Lock (const Thread::SmartLock& lock, bool wr);

        //##ModelId=3DB935A80344
        ~Lock();

        //##ModelId=3DB935A8036C
        Lock & operator=(const Lock &right);


        //##ModelId=7D43F6D0FEED
        int release ();

        //##ModelId=3D1981F100D6
        int relock (const Thread::SmartLock &lock, bool wr);

        //##ModelId=3D1981FF03A7
        int relock (bool wr);

        // Additional Public Declarations
        //##ModelId=3DB935A90011
        const char * debug (int = 1,const string & = "",const char * = 0 ) const
        { return write ? "SmartLock::Lock/W" : "SmartLock::Lock/R"; }
        //##ModelId=3DB935AA0252
        string sdebug (int = 1,const string & = "",const char * = 0 ) const
        { return debug(); }
      protected:
        // Data Members for Class Attributes

        //##ModelId=3D1049B600A1
        bool write;

      };

      //##ModelId=3D19866E01D3
      class WriteUpgrade : public Write
      {
      public:
        //##ModelId=3D19A88A02E8
        WriteUpgrade();

        //##ModelId=3DB935AB0018
        WriteUpgrade(const WriteUpgrade &right);

        //##ModelId=3DB935AB005E
        WriteUpgrade (const Thread::SmartLock& lock);

        //##ModelId=3DB935AB009A
        ~WriteUpgrade();

        //##ModelId=3DB935AB00AE
        WriteUpgrade & operator=(const WriteUpgrade &right);


        //##ModelId=3D19869003C6
        int relock (const Thread::SmartLock &lock);

        // Additional Public Declarations
        //##ModelId=3DB935AB0109
        const char * debug (int = 1,const string & = "",const char * = 0 ) const
        { return "SmartLock::WriteUpg"; }
        //##ModelId=3DB935AB020D
        string sdebug (int = 1,const string & = "",const char * = 0 ) const
        { return debug(); }
      };

      //##ModelId=3D1986F90132
      class LockUpgrade : public Lock
      {
      public:
        //##ModelId=3D19A89F00FD
        LockUpgrade();

        //##ModelId=3DB935AC0064
        LockUpgrade(const LockUpgrade &right);

        //##ModelId=3DB935AC00AA
        LockUpgrade (const Thread::SmartLock& lock, bool wr);

        //##ModelId=3DB935AC012C
        ~LockUpgrade();

        //##ModelId=3DB935AC0140
        LockUpgrade & operator=(const LockUpgrade &right);


        //##ModelId=3D1987470243
        int relock (const Thread::SmartLock &lock, bool wr);

        // Additional Public Declarations
        //##ModelId=3DB935AC01A4
        const char * debug (int = 1,const string & = "",const char * = 0 ) const
        { return write ? "SmartLock::LockUpg/W" : "SmartLock::LockUpg/R"; }
        //##ModelId=3DB935AC02B3
        string sdebug (int = 1,const string & = "",const char * = 0 ) const
        { return debug(); }
      };

      //##ModelId=3D10BCC5027A
      SmartLock();

      //##ModelId=3DB935AD003D
      SmartLock (const SmartLock &);

      //##ModelId=3DB935AD00B6
      ~SmartLock();


      //##ModelId=3D10BCCC00A3
      SmartLock& operator = (const SmartLock &);

      //##ModelId=85D1DF88FEED
      int rlock () const;

      //##ModelId=6C3F24E5FEED
      int wlock () const;

      //##ModelId=84F319FCFEED
      int runlock () const;

      //##ModelId=88437021FEED
      int wunlock () const;

      //##ModelId=3D1982B103CB
      int wlock_upgrade () const;

      //##ModelId=3D1982B60364
      int rlock_downgrade () const;

    private:
      // Data Members for Class Attributes

      //##ModelId=3D1049B500F1
      mutable int readers;

      //##ModelId=3D1049B500F2
      mutable int writers;

      //##ModelId=3DB95464039C
      mutable ThrID writer_id;

      // Data Members for Associations

      //##ModelId=3D105A140151
      Condition cond;

    };

    // Class Thread::SmartLock::BaseLock 

    //##ModelId=27D9633CFEED
    inline SmartLock::BaseLock::BaseLock (const Thread::SmartLock* pl)
      : plock(pl)
    {
    }



    //##ModelId=7B209A65FEED
    inline bool SmartLock::BaseLock::locked () const
    {
      return plock != 0;
    }

    //##ModelId=13FE864CFEED
    inline SmartLock::BaseLock::operator bool () const
    {
      return locked();
    }

    //##ModelId=97F0E174FEED
    inline bool SmartLock::BaseLock::operator ! () const
    {
      return !locked();
    }

    // Class Thread::SmartLock::Read 

    //##ModelId=2E156332FEED
    inline SmartLock::Read::Read()
    {
    }

    inline SmartLock::Read::Read(const SmartLock::Read &right)
      : BaseLock(right.plock)
    {
      if( plock )
        plock->rlock();
    }

    //##ModelId=3DB935A60217
    inline SmartLock::Read::Read (const Thread::SmartLock& lock)
      : BaseLock(&lock)
    {
      lock.rlock();
    }


    //##ModelId=3DB935A6025D
    inline SmartLock::Read::~Read()
    {
      if( plock ) 
        plock->runlock();
    }


    //##ModelId=3DB935A60271
    inline SmartLock::Read & SmartLock::Read::operator=(const SmartLock::Read &right)
    {
      if( right.plock )
        right.plock->rlock();
      release();
      plock = right.plock;  
      return *this;
    }



    //##ModelId=0A10BCC1FEED
    inline int SmartLock::Read::release ()
    {
      int ret = plock ? plock->runlock() : 0;
      plock = 0;
      return ret; 
    }

    //##ModelId=3D1981B2020C
    inline int SmartLock::Read::relock (const Thread::SmartLock &lock)
    {
      lock.rlock();
      release();
      plock = &lock;
      return 0;
    }

    // Class Thread::SmartLock::Write 

    //##ModelId=90340814FEED
    inline SmartLock::Write::Write()
    {
    }

    inline SmartLock::Write::Write(const SmartLock::Write &right)
      : BaseLock(right.plock)
    {
      if( plock )
        plock->wlock();
    }

    //##ModelId=3DB935A70196
    inline SmartLock::Write::Write (const Thread::SmartLock& lock)
      : BaseLock(&lock)
    {
      plock->wlock();
    }


    //##ModelId=3DB935A701DD
    inline SmartLock::Write::~Write()
    {
      if( plock )
        plock->wunlock();
    }


    //##ModelId=3DB935A701E7
    inline SmartLock::Write & SmartLock::Write::operator=(const SmartLock::Write &right)
    {
      if( right.plock )
        right.plock->wlock(); 
      release();
      plock = right.plock;  
      return *this;
    }



    //##ModelId=86E22961FEED
    inline int SmartLock::Write::release ()
    {
      int ret = plock ? plock->wunlock() : 0;
      plock = 0;
      return ret; 
    }

    //##ModelId=3D1981ED0080
    inline int SmartLock::Write::relock (const Thread::SmartLock &lock)
    {
      lock.wlock();
      release();
      plock = &lock;
      return 0;
    }

    // Class Thread::SmartLock::Lock 

    //##ModelId=CCA65344FEED
    inline SmartLock::Lock::Lock()
    {
    }

    inline SmartLock::Lock::Lock(const SmartLock::Lock &right)
      : BaseLock(right.plock),write(right.write)
    {
      if( plock )
        write ? plock->wlock() : plock->rlock();
    }

    //##ModelId=3DB935A8025E
    inline SmartLock::Lock::Lock (const Thread::SmartLock& lock, bool wr)
      : BaseLock(&lock),write(wr)
    {
      write ? plock->wlock() : plock->rlock();
    }


    //##ModelId=3DB935A80344
    inline SmartLock::Lock::~Lock()
    {
      if( plock ) 
        write ? plock->wunlock() : plock->runlock(); 
    }


    //##ModelId=3DB935A8036C
    inline SmartLock::Lock & SmartLock::Lock::operator=(const SmartLock::Lock &right)
    {
      right.write ? right.plock->wlock() : right.plock->rlock();
      release();
      plock = right.plock; write = right.write;
      return *this;
    }



    //##ModelId=7D43F6D0FEED
    inline int SmartLock::Lock::release ()
    {
      int ret = plock 
        ? ( write ? plock->wunlock() : plock->runlock() )
        : 0;
      plock = 0;
      return ret; 
    }

    //##ModelId=3D1981F100D6
    inline int SmartLock::Lock::relock (const Thread::SmartLock &lock, bool wr)
    {
      wr ? lock.wlock() : lock.rlock();
      release();
      plock = &lock;
      write = wr;
      return 0;
    }

    //##ModelId=3D1981FF03A7
    inline int SmartLock::Lock::relock (bool wr)
    {
      if( !plock || wr == write )
        return 0;
      write = wr;
      if( write )
        plock->wlock_upgrade();
      else
        plock->rlock_downgrade();
      return 0;
    }

    // Class Thread::SmartLock::WriteUpgrade 

    //##ModelId=3D19A88A02E8
    inline SmartLock::WriteUpgrade::WriteUpgrade()
    {
    }

    inline SmartLock::WriteUpgrade::WriteUpgrade(const SmartLock::WriteUpgrade &right)
      : Write(right)
    {
      // defer to normal write lock since no upgrade is required if we already
      // have a write lock
    }

    //##ModelId=3DB935AB005E
    inline SmartLock::WriteUpgrade::WriteUpgrade (const Thread::SmartLock& lock)
    {
      (plock = &lock)->wlock_upgrade();
    }


    //##ModelId=3DB935AB009A
    inline SmartLock::WriteUpgrade::~WriteUpgrade()
    {
    }


    //##ModelId=3DB935AB00AE
    inline SmartLock::WriteUpgrade & SmartLock::WriteUpgrade::operator=(const SmartLock::WriteUpgrade &right)
    {
      // defer to normal write lock since no upgrade is required
      *static_cast<Write*>(this) = right;
      return *this;
    }



    //##ModelId=3D19869003C6
    inline int SmartLock::WriteUpgrade::relock (const Thread::SmartLock &lock)
    {
      lock.wlock_upgrade();
      release();
      plock = &lock;
      return 0;
    }

    // Class Thread::SmartLock::LockUpgrade 

    //##ModelId=3D19A89F00FD
    inline SmartLock::LockUpgrade::LockUpgrade()
    {
    }

    inline SmartLock::LockUpgrade::LockUpgrade(const SmartLock::LockUpgrade &right)
      : Lock(right)
    {
      // defer to normal lock since no upgrade is required
    }

    //##ModelId=3DB935AC00AA
    inline SmartLock::LockUpgrade::LockUpgrade (const Thread::SmartLock& lock, bool wr)
    {
      plock = &lock;
      (write=wr) ? plock->wlock_upgrade() : plock->rlock();
    }


    //##ModelId=3DB935AC012C
    inline SmartLock::LockUpgrade::~LockUpgrade()
    {
    }


    //##ModelId=3DB935AC0140
    inline SmartLock::LockUpgrade & SmartLock::LockUpgrade::operator=(const SmartLock::LockUpgrade &right)
    {
      // defer to normal lock since no upgrade is required
      *static_cast<Lock*>(this) = right;
      return *this;
    }



    //##ModelId=3D1987470243
    inline int SmartLock::LockUpgrade::relock (const Thread::SmartLock &lock, bool wr)
    {
      wr ? lock.wlock_upgrade() : lock.rlock();
      release();
      plock = &lock;
      write = wr;
      return 0;
    }

    // Class Thread::SmartLock 

    //##ModelId=3D10BCC5027A
    inline SmartLock::SmartLock()
      : readers(0),writers(0)
    {
    }

    //##ModelId=3DB935AD003D
    inline SmartLock::SmartLock (const SmartLock &)
      : readers(0),writers(0)
    {
    }


    //##ModelId=3DB935AD00B6
    inline SmartLock::~SmartLock()
    {
      while( readers )
        runlock();
      while( writers )
        wunlock();
    }



    //##ModelId=3D10BCCC00A3
    inline SmartLock& SmartLock::operator = (const SmartLock &)
    {
      return *this;
    }

#else

    class SmartLock 
    {
    public:
      class Read {};
      class Write {};
      class WriteUpgrade {};
      class Lock {};
      class LockUpgrade {};
    };

#endif

  } // namespace Thread

} // namespace LOFAR


#endif

//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3D1996530052.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3D1996530052.cm

//## begin module%3D1996530052.cp preserve=no
//## end module%3D1996530052.cp

//## Module: SmartLock%3D1996530052; Package body
//## Subsystem: Common::Thread%3D1995E30156
//## Source file: F:\lofar9\oms\LOFAR\src-links\Common\Thread\SmartLock.cc

//## begin module%3D1996530052.additionalIncludes preserve=no
//## end module%3D1996530052.additionalIncludes

//## begin module%3D1996530052.includes preserve=yes
//## end module%3D1996530052.includes

// SmartLock
#include <Common/Thread/SmartLock.h>
//## begin module%3D1996530052.declarations preserve=no
//## end module%3D1996530052.declarations

//## begin module%3D1996530052.additionalDeclarations preserve=yes
//## end module%3D1996530052.additionalDeclarations


//## Modelname: Common::Thread%3D1049DA01E4
namespace LOFAR
{
  namespace Thread 
  {
    //##ModelId=85D1DF88FEED
    //## begin Thread%3D1049DA01E4.initialDeclarations preserve=yes
    //## end Thread%3D1049DA01E4.initialDeclarations

    // Class Thread::SmartLock::BaseLock 

    // Additional Declarations
    //## begin Thread::SmartLock::BaseLock%3D1049B50102.declarations preserve=yes
    //## end Thread::SmartLock::BaseLock%3D1049B50102.declarations

    // Class Thread::SmartLock::Read 

    // Additional Declarations
    //## begin Thread::SmartLock::Read%3D1049B5012A.declarations preserve=yes
    //## end Thread::SmartLock::Read%3D1049B5012A.declarations

    // Class Thread::SmartLock::Write 

    // Additional Declarations
    //## begin Thread::SmartLock::Write%3D1049B50171.declarations preserve=yes
    //## end Thread::SmartLock::Write%3D1049B50171.declarations

    // Class Thread::SmartLock::Lock 

    // Additional Declarations
    //## begin Thread::SmartLock::Lock%3D1049B501AE.declarations preserve=yes
    //## end Thread::SmartLock::Lock%3D1049B501AE.declarations

    // Class Thread::SmartLock::WriteUpgrade 

    // Additional Declarations
    //## begin Thread::SmartLock::WriteUpgrade%3D19866E01D3.declarations preserve=yes
    //## end Thread::SmartLock::WriteUpgrade%3D19866E01D3.declarations

    // Class Thread::SmartLock::LockUpgrade 

    // Additional Declarations
    //## begin Thread::SmartLock::LockUpgrade%3D1986F90132.declarations preserve=yes
#ifdef USE_THREADS
    //## end Thread::SmartLock::LockUpgrade%3D1986F90132.declarations

    // Class Thread::SmartLock 


    //## Other Operations (implementation)
    int SmartLock::rlock () const
    {
      //## begin Thread::SmartLock::rlock%85D1DF88FEED.body preserve=yes
      Mutex::Lock lock(cond);
      if( writer_id != self() )
      {
        while( writers )
          cond.wait();
      }
      readers++;
      return 0;  
      //## end Thread::SmartLock::rlock%85D1DF88FEED.body
    }

    //##ModelId=6C3F24E5FEED
    int SmartLock::wlock () const
    {
      //## begin Thread::SmartLock::wlock%6C3F24E5FEED.body preserve=yes
      Mutex::Lock lock(cond);
      if( writer_id != self() )
      {
        while( readers || writers )
          cond.wait();
        writer_id = self();
      }
      writers++;
      return 0;  
      //## end Thread::SmartLock::wlock%6C3F24E5FEED.body
    }

    //##ModelId=84F319FCFEED
    int SmartLock::runlock () const
    {
      //## begin Thread::SmartLock::runlock%84F319FCFEED.body preserve=yes
      Mutex::Lock lock(cond);
      if( !readers )
        return -1;
      if( !--readers )
        cond.signal();
      return 0;  
      //## end Thread::SmartLock::runlock%84F319FCFEED.body
    }

    //##ModelId=88437021FEED
    int SmartLock::wunlock () const
    {
      //## begin Thread::SmartLock::wunlock%88437021FEED.body preserve=yes
      Mutex::Lock lock(cond);
      if( !writers )
        return -1;
      if( !--writers )
      {
        writer_id = 0;
        cond.signal();
      }
      return 0;  
      //## end Thread::SmartLock::wunlock%88437021FEED.body
    }

    //##ModelId=3D1982B103CB
    int SmartLock::wlock_upgrade () const
    {
      //## begin Thread::SmartLock::wlock_upgrade%3D1982B103CB.body preserve=yes
      Mutex::Lock lock(cond);
      if( writer_id != self() )
      {
        FailWhen(!readers,"must have a read-lock to upgrade to a write-lock");
        while( readers > 1 || writers )
          cond.wait();
        readers--;
        writer_id = self();
      }
      writers++;
      return 0;  
      //## end Thread::SmartLock::wlock_upgrade%3D1982B103CB.body
    }

    //##ModelId=3D1982B60364
    int SmartLock::rlock_downgrade () const
    {
      //## begin Thread::SmartLock::rlock_downgrade%3D1982B60364.body preserve=yes
      Mutex::Lock lock(cond);
      FailWhen(writer_id != self(),"no write lock held");
      {
        readers++;
        writers--;
        writer_id = 0;
        cond.signal();
      }
      return 0;  
      //## end Thread::SmartLock::rlock_downgrade%3D1982B60364.body
    }

    // Additional Declarations
    //## begin Thread::SmartLock%3D1049B500A8.declarations preserve=yes
#endif
    //## end Thread::SmartLock%3D1049B500A8.declarations

  } // namespace Thread

} // namespace LOFAR

//## begin module%3D1996530052.epilog preserve=yes
//## end module%3D1996530052.epilog

#ifdef USE_THREADS
    
#include "DMI/AID-DMI.h"
#include "DMI/TID-DMI.h"
#include "DMI/DataRecord.h"
#include "DMI/DataArray.h"
#include "Common/Thread.h"
        
SmartBlock *sblock;
DataRecord *rec;

#ifndef _GLIBCPP_VERSION
#define _GLIBCPP_VERSION "2 old (\"too old\")"
#endif
    
void * testThread (void*)
{
  Thread::ThrID tid = Thread::self();
  cout<<"Using libstdc++ version "<<_GLIBCPP_VERSION<<endl;
  cout<<"Entering thread "<<tid<<endl;
  try 
  {
    BlockSet set1;
    BlockSet set2;
    BlockRef ref;
    set1.push( BlockRef(sblock) );
    set2.push( BlockRef(sblock) );
    while( 1 )
    {
      switch( rand()%4 )
      {
        case 0:   set1.push( BlockRef(sblock) );
//                  cout<<tid<<": pushing on set1 "<<set1.size()<<"\n";
                  break;
        case 1:   set2.push( BlockRef(sblock) );
//                  cout<<tid<<": pushing on set2 "<<set2.size()<<"\n";
                  break;
        case 2:   if( set1.size() )
                    set1.pop(ref);
//                  cout<<tid<<": popping set1 "<<set1.size()<<"\n";
                  break;
        case 3:   if( set2.size() )
                    set2.pop(ref);
//                  cout<<tid<<": popping set2 "<<set2.size()<<"\n";
                  break;
      }
    }
  }
  catch( LCS::Exception err ) 
  {
    cout<<"Thread "<<tid<<" caught exception:\n"<<err.what()<<endl;
  }
  return 0;
}

void * rec_thread1 (void*)
{
  Thread::ThrID tid = Thread::self();
  cout<<"Using libstdc++ version "<<_GLIBCPP_VERSION<<endl;
  cout<<"Entering thread "<<tid<<endl;
  try 
  {
    while( 1 )
    {
      for( char f1 = 'A'; f1<'G'; f1++ )
      {
        for( char f2 = 'A'; f2<'G'; f2++ )
        {
          (*rec)[string(1,f1)][string(1,f2)] = int(tid);
        }
//        cout<<tid<<": filled "<<f1<<endl;
      }
    }
  }
  catch( LCS::Exception err ) 
  {
    cout<<"Thread "<<tid<<" caught exception:\n"<<err.what()<<endl;
  }
  return 0;
}

void * rec_thread2 (void*)
{
  Thread::ThrID tid = Thread::self();
  cout<<"Using libstdc++ version "<<_GLIBCPP_VERSION<<endl;
  cout<<"Entering thread "<<tid<<endl;
  try 
  {
    while( 1 )
    {
      for( char f1 = 'F'; f1>='A'; f1-- )
      {
        for( char f2 = 'F'; f2>='A'; f2-- )
        {
          (*rec)[string(1,f1)][string(1,f2)] = int(tid);
        }
//        cout<<tid<<": filled "<<f1<<endl;
      }
    }
  }
  catch( std::exception &err ) 
  {
    cout<<"Thread "<<tid<<" caught exception:\n"<<err.what()<<endl;
  }
  return 0;
}

void * rec_thread3 (void*)
{
  Thread::ThrID tid = Thread::self();
  cout<<"Using libstdc++ version "<<_GLIBCPP_VERSION<<endl;
  cout<<"Entering thread "<<tid<<endl;
  try 
  {
    while( 1 )
    {
      for( char f1 = 'A'; f1<'G'; f1++ )
      {
        cout<<f1<<": ";
        for( char f2 = 'F'; f2>='A'; f2-- )
        {
          int val = (*rec)[string(1,f1)][string(1,f2)];
          cout<<f2<<":"<<val<<" ";
        }
        cout<<endl;
      }
    }
  }
  catch( LCS::Exception err ) 
  {
    cout<<"Thread "<<tid<<" caught exception:\n"<<err.what()<<endl;
  }
  return 0;
}


    
int main ( int argc,const char *argv[] )
{
  Debug::getDebugContext().setLevel(10);
  CountedRefBase::getDebugContext().setLevel(0);
  Debug::initLevels(argc,argv);

  rec = new DataRecord;
  for( char f1 = 'A'; f1<'G'; f1++ )
  {
    (*rec)[string(1,f1)] <<= new DataRecord;
    for( char f2 = 'A'; f2<'G'; f2++ )
    {
      (*rec)[string(1,f1)][string(1,f2)] = 0;
    }
  }
  
  sblock = new SmartBlock(0x10000);    
  BlockRef ref0(sblock,DMI::ANONWR);
  
  Thread::ThrID tid[6];
  cout<<"Main thread is "<<Thread::self()<<endl;
  cout<<"Created thread "<<(tid[0]=Thread::create(testThread))<<endl;
  cout<<"Created thread "<<(tid[1]=Thread::create(testThread))<<endl;
  cout<<"Created thread "<<(tid[2]=Thread::create(testThread))<<endl;
  cout<<"Created thread "<<(tid[3]=Thread::create(rec_thread1))<<endl;
  cout<<"Created thread "<<(tid[4]=Thread::create(rec_thread2))<<endl;
  cout<<"Created thread "<<(tid[5]=Thread::create(rec_thread3))<<endl;
  
  for( int i=0; i<6; i++ )
    tid[i].join();
  
  return 0;
}
    
#else
int main ()
{
  return 0;
}
#endif    
    

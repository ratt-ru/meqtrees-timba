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

#ifdef USE_THREADS
    
#include "DMI/AID-DMI.h"
#include "DMI/TID-DMI.h"
#include "DMI/Record.h"
#include "DMI/NumArray.h"
#include "TimBase/Thread.h"
        
DMI::SmartBlock *sblock;
DMI::Record *rec;

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
    DMI::BlockSet set1;
    DMI::BlockSet set2;
    DMI::BlockRef ref;
    set1.push( DMI::BlockRef(sblock) );
    set2.push( DMI::BlockRef(sblock) );
    while( 1 )
    {
      switch( rand()%4 )
      {
        case 0:   set1.push( DMI::BlockRef(sblock) );
//                  cout<<tid<<": pushing on set1 "<<set1.size()<<"\n";
                  break;
        case 1:   set2.push( DMI::BlockRef(sblock) );
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
  catch( std::exception &err ) 
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
  catch( std::exception &err ) 
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
  catch( std::exception &err ) 
  {
    cout<<"Thread "<<tid<<" caught exception:\n"<<err.what()<<endl;
  }
  return 0;
}


    
int main ( int argc,const char *argv[] )
{
  Debug::getDebugContext().setLevel(10);
  DMI::CountedRefBase::getDebugContext().setLevel(0);
  Debug::initLevels(argc,argv);

  rec = new DMI::Record;
  for( char f1 = 'A'; f1<'G'; f1++ )
  {
    (*rec)[string(1,f1)] <<= new DMI::Record;
    for( char f2 = 'A'; f2<'G'; f2++ )
    {
      (*rec)[string(1,f1)][string(1,f2)] = 0;
    }
  }
  
  sblock = new DMI::SmartBlock(0x10000);    
  DMI::BlockRef ref0(sblock,DMI::ANONWR);
  
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
    

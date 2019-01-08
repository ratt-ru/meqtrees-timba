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

#include <DMI/AID-DMI.h>
#include <DMI/TID-DMI.h>
#include <DMI/Record.h>
#include <DMI/NumArray.h>
#include <DMI/ContainerIter.h>
#include <DMI/Global-Registry.h>
#include <TimBase/Stopwatch.h>
//#include <casacore/casa/Arrays/Matrix.h>
//#include <casacore/casa/Arrays/ArrayMath.h>
#include <stdlib.h>
        
using namespace LOFAR;
using namespace DMI;
using namespace DebugDefault;
   
int dum = aidRegistry_Global();
 
int main ( int argc,const char *argv[] )
{
#ifdef __GNUC__
  cout<<"Compiled with gcc "<<__GNUC__<<"."<<__GNUC_MINOR__<<endl;
#endif
  
#ifdef USE_THREADS
  cout<<"Multithreading enabled\n";
#else
  cout<<"Multithreading disabled\n";
#endif

#ifdef __OPTIMIZE__
  cout<<"Compiled with optimizations "<<__OPTIMIZE__<<"\n";
#else
  cout<<"Compiled w/o optimizations \n";
#endif
    
#ifdef _GLIBCPP_VERSION
  cout<<"Using libstdc++ version "<<_GLIBCPP_VERSION<<endl;
#else
  cout<<"Using libstdc++ version 2\n";
#endif
  Debug::getDebugContext().setLevel(0);
  CountedRefBase::getDebugContext().setLevel(0);
  
  Debug::initLevels(argc,argv);
  int test_level = 1;
  string test;
  
  for( int i=1; i<argc; i++ )
  {
    string arg(argv[i]);
    if( arg == "-a" )
      test_level = 2;
    else if( isupper(arg[0]) )
    {
      test = arg;
      test_level = 0;
    }
  }
  
  try 
  {
    double dum=0; int val,nloops;
    long long ndone;
    const char indent[] = "           ";
    
    cout << 
        "Running small NestableContainer benchmarks\n";
    if( test_level<2 )
      cout << 
        "use -a to run all benchmarks\n";
    else
      cout << 
        "running all benchmarks\n";
    if( test_level==0 )  
      cout << "running benchmark " << test << endl;
    else
      cout <<
        "HIID2S: convert HIIDs to strings\n"
        "S2HIID: convert strings to HIIDs\n"
        "RSINIT: init 3-element record\n"
        "RSSCAN: access 3-element record\n"
        "RBINIT: init 10000-element record\n"
        "RBSCAN: access 10000-element record\n"
        "R3INIT: init nested record of 26x26x26 scalar integer fields (fps)\n"
        "R3SCAN: sequential scan of 26x26x26 record (fps)\n"
        "R3AFIX: assigning to fixed field of 3-nested record (fps)\n"
        "R3RFIX: reading fixed field of 3-nested record (fps)\n"
        "R1SCAN: sequential scan of 26-field record (fps)\n"
        "R1AFIX: assigning to fixed field of record (fps)\n"
        "R1RFIX: reading fixed field of record (fps)\n"
        "ADSM1M: sum of 1000x1000 doubles, via Matrix(i,j) (ops)\n"
        "ADSA1M: sum of 1000x1000 doubles, via sum() (ops)\n"
        "ADSI1M: sum of 1000x1000 doubles, via NCIter (ops)\n"
        "ADSH1M: sum of 1000x1000 doubles, via hooks (ops)\n"
        "ADAM1M: addition of 1000x1000 doubles, via Matrix(i,j) (ops)\n"
        "ADAA1M: addition of 1000x1000 doubles, via array math (ops)\n"
        "ADAI1M: addition of 1000x1000 doubles, via NCIters (ops)\n"
        "ADAH1M: addition of 1000x1000 doubles, via hooks (ops)\n"
        
        <<endl<<indent<<Stopwatch::header(1)<<endl;
    
    Stopwatch watch(3.0);
    watch.setNameWidth(10);
    
    ndone = 0;
    string curname;

  #define RUNTEST(LEVEL,NAME)    \
    ndone = 0; curname = #NAME; \
    if( test_level >= LEVEL || test == #NAME ) \
    
    RUNTEST(1,HIID2S)
    {
      for( nloops=0; !watch.fired(); nloops++ )
      {
        HIID hiid = AidA|AidB|AidDMIRecord|AidDMIList;
        int len;
        for( int i=0; i<1000; i++ )
        {
          hiid[0] = i;
          std::string str = hiid.toString();
          len += str.length();
        }
        ndone += 1000;
      }
      cout<<watch.dump("HIID2S",ndone)<<endl;
    }
    
    RUNTEST(1,S2HIID)
    {
      for( nloops=0; !watch.fired(); nloops++ )
      {
        std::string str = "A.B.DMIRecord.DMIList";
        int len;
        for( int i=0; i<1000; i++ )
        {
          str[0] = ('A'+(i%20));
          HIID hiid(str);
          len += hiid.size();
        }
        ndone += 1000;
      }
      cout<<watch.dump("S2HIID",ndone)<<endl;
    }
    
    DMI::Record rec;
    ObjRef ref(new DMI::Record);
    
    RUNTEST(1,RSINIT)
    {
      for( nloops=0; !watch.fired(); nloops++ )
      {
        rec = DMI::Record();
        HIID hiid = AidA|AidB|AidC|0;
        for( int i=0; i<10000; i++ )
        {
          hiid[3] = i%4;
          rec.add(hiid,ref,DMI::REPLACE);
          ndone++;
        }
      }
      cout<<watch.dump("RSINIT",ndone)<<endl;
    }
    
    RUNTEST(1,RSSCAN)
    {
      for( nloops=0; !watch.fired(); nloops++ )
      {
        HIID hiid = AidA|AidB|AidC|0;
        int sum;
        for( int i=0; i<10000; i++ )
        {
          hiid[3] = random()%4;
          sum += rec.hasField(hiid);
          ndone++;
        }
      }
      cout<<watch.dump("RSSCAN",ndone)<<endl;
    }

    RUNTEST(1,RBINIT)
    {
      for( nloops=0; !watch.fired(); nloops++ )
      {
        rec = DMI::Record();
        HIID hiid = AidA|AidB|AidC|0;
        for( int i=0; i<50000; i++ )
        {
          hiid[3] = i;
          rec.add(hiid,ref);
          ndone++;
        }
      }
      cout<<watch.dump("RBINIT",ndone)<<endl;
    }
    
    RUNTEST(1,RBSCAN)
    {
      for( nloops=0; !watch.fired(); nloops++ )
      {
        HIID hiid = AidA|AidB|AidC|0;
        int sum;
        for( int i=0; i<50000; i++ )
        {
          hiid[3] = random()%8192;
          sum += rec.hasField(hiid);
          ndone++;
        }
      }
      cout<<watch.dump("RBSCAN",ndone)<<endl;
    }
    
    RUNTEST(1,R3INIT)
    {
      for( nloops=0; !watch.fired(); nloops++ )
      {
        rec = DMI::Record();
        for( char f1='A'; f1<='Z'; f1++ )
        {
          rec[string(1,f1)] <<= new DMI::Record;
          for( char f2='A'; f2<='Z'; f2++ )
          {
            rec[string(1,f1)][string(1,f2)] <<= new DMI::Record;
            for( char f3='A'; f3<='Z'; f3++ )
            {
  //            rec[string(1,f1)][string(1,f2)][string(1,f3)] <<= new DMI::NumArray(Tpdouble,IPosition(2,30,30));
              rec[string(1,f1)][string(1,f2)][string(1,f3)] = 0;
              ndone++;
            }
          }
        }
      }
      cout<<watch.dump("R3INIT",ndone)<<endl;
    }
    
    RUNTEST(1,R3SCAN)
    {
      watch.reset();    
      ndone=0;
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( char f1='A'; f1<='Z'; f1++ )
        {
          for( char f2='A'; f2<='Z'; f2++ )
          {
            for( char f3='A'; f3<='Z'; f3++ )
            {
    //          double val = rec[string(1,f1)][string(1,f2)][string(1,f3)](10,10);
              val = rec[string(1,f1)][string(1,f2)][string(1,f3)];
              ndone++;
            }
          }
        }
      }
      cout<<watch.dump("R3SCAN",ndone)<<endl;
    }
    
    HIID id("A/B/C");
    RUNTEST(1,R3AFIX)
    {
      watch.reset();    
      for( nloops=0; !watch.fired(); nloops+=1000 )
      {
        for( int count=0; count<1000; count++ )
          rec[id] = 0;
      }
      cout<<watch.dump("R3AFIX",nloops)<<endl;
    }

    RUNTEST(1,R3RFIX)
    {
      for( nloops=0; !watch.fired(); nloops+=1000 )
      {
        for( int count=0; count<1000; count++ )
          val = rec[id];
      }
      cout<<watch.dump("R3RFIX",nloops)<<endl;
    }

    RUNTEST(1,R1SCAN)
    {
      DMI::Record &rec1 = rec["A/B"].as_wr<DMI::Record>();
      watch.reset();
      for( nloops=0; !watch.fired(); nloops+=1000 )
      {
        for( int count=0; count<1000; count++ )
        {
          for( char f1='A'; f1<='Z'; f1++ )
          {
            val = rec1[string(1,f1)] = 0;
            ndone++;
          }
        }
      }
      cout<<watch.dump("R1SCAN",ndone)<<endl;
    }
    
    id = "D";
    RUNTEST(1,R1AFIX)
    {
      DMI::Record &rec1 = rec["A/B"].as_wr<DMI::Record>();
      for( nloops=0; !watch.fired(); nloops+=1000 )
      {
        for( int count=0; count<1000; count++ )
        {
          rec1[id] = 0;
        }
      }
      cout<<watch.dump("R1AFIX",nloops)<<endl;
    }
    
    id = "D";
    RUNTEST(1,R1RFIX)
    {
      DMI::Record &rec1 = rec["A/B"].as_wr<DMI::Record>();
      for( nloops=0; !watch.fired(); nloops+=1000 )
      {
        for( int count=0; count<1000; count++ )
          val = rec1[id];
      }
      cout<<watch.dump("R1RFIX",nloops)<<endl;
    }
          

    int size = 1000;
    DMI::NumArray arr(Tpdouble,makeLoShape(size,size),DMI::ZERO|DMI::WRITE);
    LoMat_double mat = arr[HIID()].as<LoMat_double>();
      
    RUNTEST(1,ADSM1M)
    {
      ndone = 1;
      for( nloops=0; !watch.fired(); nloops+=10 )
      {
        for( int count=0; count<10; count++ )
        {
          mat(10,10) = nloops;
          for( int i=0; i<size; i++ )
            for( int j=0; j<size; j++ )
            {
              dum += mat(i,j);
            }
        }
      }
      cout<<watch.dump("ADSM1M",ndone*nloops)<<endl;
    }
    
    RUNTEST(1,ADSA1M)
    {
      ndone = 1;
      for( nloops=0; !watch.fired(); nloops+=10 )
      {
        for( int count=0; count<10; count++ )
        {
          mat(10,10) = nloops;
          dum += sum(mat);
        }
      }
      cout<<watch.dump("ADSA1M",ndone*nloops)<<endl;
    }
      
    RUNTEST(1,ADSI1M)
    {
      ndone = 1;
      watch.reset();
      double *tmp = arr(10,10).as_wp<double>();
      ConstContainerIter<double> iter(arr[HIID()]);
      for( nloops=0; !watch.fired(); nloops+=10 )
      {
        for( int count=0; count<10; count++ )
        {
          *tmp = nloops;
          iter.reset();
          while( !iter.end() )
            { dum += iter.next(); }
        }
      }
      cout<<watch.dump("ADSI1M",ndone*nloops)<<endl;
    }

        
    DMI::NumArray arr2(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO),
              arr3(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO);
    
    RUNTEST(1,ADAM1M)
    {
      ndone = 1;
      LoMat_double   mat(arr[HIID()].as<LoMat_double>()),
                     mat2(arr2[HIID()].as<LoMat_double>()),
                     mat3(arr3[HIID()].as<LoMat_double>());
      watch.reset();
      for( nloops=0; !watch.fired(); nloops+=10 )
      {
        for( int count=0; count<10; count++ )
        {
          mat(10,10) = nloops;
          for( int i=0; i<size; i++ )
            for( int j=0; j<size; j++ )
            {
              mat3(i,j) = mat2(i,j) + mat(i,j);
            }
        }
      }
      cout<<watch.dump("ADAM1M",ndone*nloops)<<endl;
    }
    
    RUNTEST(1,ADAA1M)
    {
      ndone = 1;
      LoMat_double mat(arr[HIID()].as<LoMat_double>()),
                   mat2(arr2[HIID()].as<LoMat_double>());
      watch.reset();
      for( nloops=0; !watch.fired(); nloops+=10 )
      {
        for( int count=0; count<10; count++ )
        {
          LoMat_double mat3( mat2 + mat );
          mat(10,10) += mat3(10,10);
        }
      }
      cout<<watch.dump("ADAA1M",ndone*nloops)<<endl;
    }
      
    RUNTEST(1,ADAI1M)
    {
      ndone = 1;
      watch.reset();
      double *tmp = arr(10,10).as_wp<double>();
      for( nloops=0; !watch.fired(); nloops+=10 )
      {
        ConstContainerIter<double> iter(arr[HIID()]);
        ConstContainerIter<double> iter2(arr2[HIID()]);
        ContainerIter<double> iter3(arr3[HIID()]);
        for( int count=0; count<10; count++ )
        {
          *tmp = nloops;
          iter.reset(); iter2.reset(); iter3.reset();
          while( !iter.end() )
            { iter3.next( iter2.next()+iter.next() ); }
        }
      }
      cout<<watch.dump("ADAI1M",ndone*nloops)<<endl;
    }
    
    RUNTEST(2,ADAA25M)
    {
      size = 5000;
      DMI::NumArray arr(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO);
      DMI::NumArray arr2(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO);
      
      LoMat_double mat(arr[HIID()].as<LoMat_double>()),
                   mat2(arr2[HIID()].as<LoMat_double>());
      watch.reset();
      double dum=0;
      for( nloops=0; !watch.fired(); nloops++ )
      {
        LoMat_double mat3(mat + mat2);
        dum += mat3(0,0);
      }
      cout<<watch.dump("ADAA25M",nloops)<<endl;
    }
    
    RUNTEST(2,ADAI25M)
    {  
      size = 5000;
      DMI::NumArray arr(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO);
      DMI::NumArray arr2(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO);
      DMI::NumArray arr3(Tpdouble,makeLoShape(size,size),DMI::WRITE);
      
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        ConstContainerIter<double> iter(arr[HIID()]);
        ConstContainerIter<double> iter2(arr2[HIID()]);
        ContainerIter<double> iter3(arr3[HIID()]);
        while( !iter.end() )
        { 
          iter3.next( iter2.next()+iter.next() ); 
        }
      }
      cout<<watch.dump("ADAI25M",nloops)<<endl;
    }
      
        
//     cout<<"=== Randomly assigning to container\n";
//     Timestamp::now(&start);
//     ndone = 100000;
//     for( int count=0; count<ndone; count++ )
//     {
//       char f1 = 'A'+(rand()%26);
//       char f2 = 'A'+(rand()%26);
//       char f3 = 'A'+(rand()%26);
// //      int  i1 = rand()%30, 
// //           i2 = rand()%30;
// //      rec[string(1,f1)][string(1,f2)][string(1,f3)](i1,i2) = rand()%1000;
//       rec[string(1,f1)][string(1,f2)][string(1,f3)] = rand()%1000;
//     }
//     delta = Timestamp::delta(start);
//     cout<<ndone<<" assignments in "<<delta<<"s., "<<ndone/delta<<"/s\n\n";
//     
//     cout<<"=== Randomly reading from container\n";
//     Timestamp::now(&start);
//     ndone = 100000;
//     for( int count=0; count<ndone; count++ )
//     {
//       char f1 = 'A'+(rand()%26);
//       char f2 = 'A'+(rand()%26);
//       char f3 = 'A'+(rand()%26);
// //      int  i1 = rand()%30, 
// //           i2 = rand()%30;
// //      double val = rec[string(1,f1)][string(1,f2)][string(1,f3)](i1,i2);
//       int val = rec[string(1,f1)][string(1,f2)][string(1,f3)];
//     }
//     delta = Timestamp::delta(start);
//     cout<<ndone<<" reads in "<<delta<<"s., "<<ndone/delta<<"/s\n\n";
    
  }
  catch( std::exception &err ) 
  {
    cerr<<"\nCaught exception:\n"<<err.what()<<endl;
    return 1;
  }

  return 0;
}
    
    
    

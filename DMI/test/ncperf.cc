#include "DMI/AID-DMI.h"
#include "DMI/TID-DMI.h"
#include "DMI/DataRecord.h"
#include "DMI/DataArray.h"
#include "DMI/NCIter.h"
#include "Common/Stopwatch.h"
//#include "aips/Arrays/Matrix.h"
//#include "aips/Arrays/ArrayMath.h"
    
#define paddr(x) printf("=== " #x ": %08x\n",(int)&x)
    
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
  
  try 
  {
    double dum=0; int val,nloops;
    long long ndone;
    const char indent[] = "           ";
    cout << 
        "Running NestableContainer benchmarks\n"
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
    
//    cout<<"=== Initializing container\n";
    DataRecord rec;
    ndone = 0;
    for( nloops=0; !watch.fired(); nloops++ )
    {
      rec = DataRecord();
      for( char f1='A'; f1<='Z'; f1++ )
      {
        rec[string(1,f1)] <<= new DataRecord;
        for( char f2='A'; f2<='Z'; f2++ )
        {
          rec[string(1,f1)][string(1,f2)] <<= new DataRecord;
          for( char f3='A'; f3<='Z'; f3++ )
          {
//            rec[string(1,f1)][string(1,f2)][string(1,f3)] <<= new DataArray(Tpdouble,IPosition(2,30,30));
            rec[string(1,f1)][string(1,f2)][string(1,f3)] = 0;
            ndone++;
          }
        }
      }
    }
    cout<<watch.dump("R3INIT",ndone)<<endl;
    
//    cout<<"=== Scanning container sequentially\n";
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
        
//    cout<<"=== Assigning to fixed element\n";
//    HIID id("A/B/C/10.10");
    HIID id("A/B/C");
    watch.reset();    
    for( nloops=0; !watch.fired(); nloops+=1000 )
    {
      for( int count=0; count<1000; count++ )
        rec[id] = 0;
    }
    cout<<watch.dump("R3AFIX",nloops)<<endl;

    watch.reset();    
    for( nloops=0; !watch.fired(); nloops+=1000 )
    {
      for( int count=0; count<1000; count++ )
        val = rec[id];
    }
    cout<<watch.dump("R3RFIX",nloops)<<endl;

    DataRecord &rec1 = rec["A/B"];
    ndone = 0;
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
    
    id = "D";
    watch.reset();
    for( nloops=0; !watch.fired(); nloops+=1000 )
    {
      for( int count=0; count<1000; count++ )
      {
        rec1[id] = 0;
      }
    }
    cout<<watch.dump("R1AFIX",nloops)<<endl;
    
    id = "D";
    watch.reset();
    for( nloops=0; !watch.fired(); nloops+=1000 )
    {
      for( int count=0; count<1000; count++ )
        val = rec1[id];
    }
    cout<<watch.dump("R1RFIX",nloops)<<endl;

    int size = 1000;
    DataArray arr(Tpdouble,makeLoShape(size,size),DMI::ZERO|DMI::WRITE);
    ndone = size*size;
    LoMat_double mat(arr[HIID()].as_LoMat_double());
      
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
    cerr<<dum<<endl;
    
    watch.reset(); 
    for( nloops=0; !watch.fired(); nloops+=10 )
    {
      for( int count=0; count<10; count++ )
      {
        mat(10,10) = nloops;
        dum += sum(mat);
      }
    }
    cout<<watch.dump("ADSA1M",ndone*nloops)<<endl;
    cerr<<dum<<endl;
      
//    cout<<"=== Accessing array with iterators\n";
    ndone = size*size;
    watch.reset();
    double *tmp = &arr(10,10);
    NCConstIter_double iter(arr[HIID()]);
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
    cerr<<dum<<endl;

    int sz1 = min(size,1000);    
    ndone = sz1*sz1;
    watch.reset();
    for( int i=0; i<sz1; i++ )
      for( int j=0; j<sz1; j++ )
      {
        dum += arr(i,j).as_double();
      }
    cout<<watch.dump("ADSH1M",ndone)<<endl;
    cerr<<dum<<endl;
        
    DataArray arr2(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO),
              arr3(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO);
    
    {
      ndone = size*size;
      LoMat_double   mat(arr[HIID()].as_LoMat_double()),
                     mat2(arr2[HIID()].as_LoMat_double()),
                     mat3(arr3[HIID()].as_LoMat_double_w());
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
      cerr<<sum(mat3)<<endl;
    }
    
    {
      LoMat_double mat(arr[HIID()].as_LoMat_double()),
                   mat2(arr2[HIID()].as_LoMat_double());
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
      cerr<<sum(mat)<<endl;
    }
      
    {
      ndone = size*size;
      watch.reset();
      double *tmp = &arr(10,10);
      NCConstIter_double iter(arr[HIID()]);
      NCConstIter_double iter2(arr2[HIID()]);
      NCIter_double iter3(arr3[HIID()]);
      for( nloops=0; !watch.fired(); nloops+=10 )
        for( int count=0; count<10; count++ )
        {
          *tmp = nloops;
          iter.reset(); iter2.reset(); iter3.reset();
          while( !iter.end() )
            { iter3.next( iter2.next()+iter.next() ); }
        }
      cout<<watch.dump("ADAI1M",ndone*nloops)<<endl;
      cerr<<sum(arr3[HIID()].as_LoMat_double())<<endl;
    }
    
    {
      int sz1 = min(size,1000);    
      ndone = sz1*sz1;
      watch.reset();
      for( int i=0; i<sz1; i++ )
        for( int j=0; j<sz1; j++ )
        {
          arr3(i,j) = arr2(i,j).as_double() + arr(i,j).as_double();
        }
      cout<<watch.dump("ADAH1M",ndone)<<endl;
      cerr<<sum(arr3[HIID()].as_LoMat_double())<<endl;
    }
  
    {  
      size = 5000;
      DataArray arr(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO);
      DataArray arr2(Tpdouble,makeLoShape(size,size),DMI::WRITE|DMI::ZERO);
      
      {
      watch.reset();
      DataArray arr3(Tpdouble,makeLoShape(size,size),DMI::WRITE);
      NCConstIter_double iter(arr[HIID()]);
      NCConstIter_double iter2(arr2[HIID()]);
      NCIter_double iter3(arr3[HIID()]);
      while( !iter.end() )
      { 
        iter3.next( iter2.next()+iter.next() ); 
      }
      cout<<watch.dump("ADAI25M",size*size)<<endl;
      cerr<<sum(arr3[HIID()].as_LoMat_double())<<endl;
      }
      
      {
      LoMat_double mat(arr[HIID()].as_LoMat_double()),
                   mat2(arr2[HIID()].as_LoMat_double());
      watch.reset();
      LoMat_double mat3(mat + mat2);
      cout<<watch.dump("ADAA25M",size*size)<<endl;
      cerr<<sum(mat3)<<endl;
      }
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
  catch( Debug::Error err ) 
  {
    cerr<<"\nCaught exception:\n"<<err.what()<<endl;
    return 1;
  }

  return 0;
}
    
    
    

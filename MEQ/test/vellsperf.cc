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

#include <TimBase/Stopwatch.h>
#include <MEQ/Vells.h>
//#include <casacore/casa/Arrays/Matrix.h>
//#include <casacore/casa/Arrays/ArrayMath.h>
#include <stdlib.h>
#include <complex.h>
        
using namespace LOFAR;
using namespace DMI;
using namespace DebugDefault;
using namespace Meq;
   
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
  
  using namespace blitz;
  using namespace VellsMath;
  
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
        "SEXPSC: sum of exp(complex scalar)\n"
        "SEXPSV: sum of exp(complex scalar vells)\n"
        "SEXPVV: sum of exp(vector vells)\n"
        "SEXPV1: sum of exp(1xN vector vells)\n"
        "SEXPVM: sum of exp(matrix vells)\n"
        "SUM_V1: sum of vector vells\n"
        "SUM_1V: sum of 1xN vector vells\n"
        "SUMV1V: sum of vector and 1xN vector vells\n"
        "SUM_MM: sum of matrix vells\n"
        
        <<endl<<indent<<Stopwatch::header(1)<<endl;
    
    Stopwatch watch(3.0);
    watch.setNameWidth(10);
    
    ndone = 0;
    string curname;

  #define RUNTEST(LEVEL,NAME)    \
    ndone = 0; curname = #NAME; \
    if( test_level >= LEVEL || test == #NAME ) 
    
    int size = 1000;
    
    Vells scalar(0.5,false);
    Vells timevec(make_dcomplex(0.5,0.5),makeLoShape(size),true);
    Vells freqvec(make_dcomplex(0.5,0.5),makeLoShape(1,size),true);
    // fill with meaningful numbers
    LoVec_dcomplex tv = timevec.getArray<dcomplex,1>();
    LoMat_dcomplex fv = freqvec.getArray<dcomplex,2>();
    for( int i=0; i<size; i++ )
    {
      tv(i) = make_dcomplex(i*1e-3,i*0.9e-3);
      fv(0,i) = make_dcomplex(i*1.1e-3,i*0.9e-3);
    }
    
    // make a matrix Vells
    Vells matrix = timevec + freqvec;
    
    Vells res(0);
    
    RUNTEST(1,SEXPSC)
    {
      dcomplex sum = make_dcomplex(0,0);
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( int i=0; i<1000; i++ )
        {
          sum += __builtin_cexp(make_dcomplex(i%4,i%8));
        }
        ndone += 1000;
      }
      cout<<watch.dump("SEXPSC",ndone)<<endl;
    }
    
    RUNTEST(1,SEXPSV)
    {
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( int i=0; i<1000; i++ )
        {
          res += exp(scalar);
        }
        ndone += 1000;
      }
      cout<<watch.dump("SEXPSV",ndone)<<endl;
    }
    
    RUNTEST(1,SEXPVV)
    {
      res = timevec;
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( int i=0; i<100; i++ )
        {
          res += exp(timevec);
        }
        ndone += 100;
      }
      cout<<watch.dump("SEXPVV",ndone*size)<<endl;
    }
    
    RUNTEST(1,SEXPV1)
    {
      res = freqvec;
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( int i=0; i<100; i++ )
        {
          res += exp(freqvec);
        }
        ndone += 100;
      }
      cout<<watch.dump("SEXPV1",ndone*size)<<endl;
    }
    
    RUNTEST(1,SEXPVM)
    {
      res = matrix;
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( int i=0; i<10; i++ )
        {
          res += exp(matrix);
        }
        ndone += 10;
      }
      cout<<watch.dump("SEXPVM",ndone*size*size)<<endl;
    }
  
    RUNTEST(1,SUM_V1)
    {
      res = freqvec;
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( int i=0; i<100; i++ )
        {
          res += freqvec;
        }
        ndone += 100;
      }
      cout<<watch.dump("SUM_V1",ndone*size)<<endl;
    }
    
    RUNTEST(1,SUM_1V)
    {
      res = timevec;
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( int i=0; i<100; i++ )
        {
          res += timevec;
        }
        ndone += 100;
      }
      cout<<watch.dump("SUM_1V",ndone*size)<<endl;
    }
    
    RUNTEST(1,SUMV1V)
    {
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( int i=0; i<10; i++ )
        {
          res = timevec + freqvec;
        }
        ndone += 10;
      }
      cout<<watch.dump("SUMV1V",ndone*size*size)<<endl;
    }
  
    RUNTEST(1,SUM_MM)
    {
      watch.reset();
      for( nloops=0; !watch.fired(); nloops++ )
      {
        for( int i=0; i<10; i++ )
        {
          res = matrix + matrix;
        }
        ndone += 10;
      }
      cout<<watch.dump("SUM_MM",ndone*size*size)<<endl;
    }
  }
  catch( std::exception &err ) 
  {
    cerr<<"\nCaught exception:\n"<<err.what()<<endl;
    return 1;
  }

  return 0;
}
    
    
    

#include <DMI/AID-DMI.h>
#include <DMI/TID-DMI.h>
#include <DMI/Record.h>
#include <DMI/NumArray.h>
#include <DMI/Vec.h>
#include <DMI/List.h>
#include <DMI/BOIO.h>
#include <DMI/ContainerIter.h>
    
#define paddr(x) printf("=== " #x ": %08x\n",(int)&x)
    
//using DMI::HIID;
using namespace DebugDefault;
using namespace DMI;

void testBOIO ()    
{
  cout<<"======================= testing BOIO\n";
  cout<<"======================= writing\n";
    BOIO boio("test.boio",BOIO::WRITE);
  
  ObjRef ref;
  ref <<= new DMI::NumArray(Tpdouble,LoShape(1000,1000)); // 8MB array
  
  for( int i=0; i<1000; i++ )
  {
    boio << ref;
    if( !(i%100) )
      cout<<"wrote "<<i<<" arrays\n";
  }
  cout<<"======================= wrote 1000 8Mb arrays\n";
  boio.close();
  
  BOIO rboio("test.boio",BOIO::READ);
  int nread = 0;
  while( rboio>>ref )
  {
    nread++;
    if( !(nread%100) )
      cout<<"read "<<nread<<" arrays\n";
  }
  cout<<"======================= finished reading "<<nread<<" objects\n";
  rboio.close();
}

int main ( int argc,const char *argv[] )
{
#ifdef _GLIBCPP_VERSION
  cout<<"Using libstdc++ version "<<_GLIBCPP_VERSION<<endl;
#else
  cout<<"Using libstdc++ version 2\n";
#endif
  
  Debug::setLevel("CRef",1);
  Debug::initLevels(argc,argv);
  
  try 
  {
    testBOIO();
  }
  catch( std::exception &err )
  {
    cout<<"\nCaught exception:\n"<<err.what()<<endl;
    return 1;
  }

  return 0;
}
    
    
    

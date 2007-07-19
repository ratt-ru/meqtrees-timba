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
    
    
    

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

#include "VisCube/VCubeSet.h"
#include "DMI/BOIO.h"
    
using namespace VisCube;
using namespace DebugDefault;
    
int main (int argc,const char *argv[])
{
  const int NCORR = 4, NFREQ = 10;
  
  Debug::initLevels(argc,argv);
  
  cout<<"=================== new cube ======================\n";
  VCube::Ref vc;
  vc <<= new VCube(NCORR,NFREQ,200,50);
  cout<<vc->sdebug(5)<<endl;
  
  cout<<"=================== filling via iterators =========\n";
  int time = 1,rowflag=1000,weight=5000,dataval=0,flagval=20,uvwval=40;
  LoMat_fcomplex dataplane(NCORR,NFREQ);
  LoMat_int flagplane(NCORR,NFREQ);
  LoVec_double uvwvec(3);
  
  for( VCube::iterator iter = vc().begin(); iter != vc().end(); iter++ )
  {
    iter.set_time(time++);
    iter.set_seqnr(time++);
    iter.set_rowflag(rowflag++);
    iter.set_weight(weight++);
    dataplane = dataval++;
    flagplane = flagval++;
    uvwvec = uvwval++,uvwval++,uvwval++;
    iter.set_data(dataplane);
    iter.set_flags(flagplane);
    iter.set_uvw(uvwvec);
  }
  cout<<"=================== access via iterators =========\n";
  for( VCube::const_iterator iter = vc().begin(); iter != vc().end(); iter++ )
  {
    LoVec_fcomplex f_data = iter.f_data(0);
    Assert( f_data.shape()[0] == NFREQ );
  }
  
  cout<<"=================== cube contents (on the fly) ====\n";
  cout<<"TIME:\n"<<vc->time()<<endl;
//   cout<<"DATA:\n"<<vc->dataCol(true)<<endl;
//   cout<<"FLAGS:\n"<<vc->flagsCol(true)<<endl;
//   cout<<"ROWFLAG:\n"<<vc->rowflagCol(true)<<endl;
//   cout<<"WEIGHT:\n"<<vc->weightCol(true)<<endl;
  cout<<"UVW:\n"<<vc->uvwCol(true)<<endl;
  
  
  cout<<"=================== consolidating =================\n";
  vc->consolidate();
  cout<<vc->sdebug(5)<<endl;
  
  cout<<"=================== cube contents =================\n";
//   cout<<"TIME:\n"<<vc->time()<<endl;
//   cout<<"DATA:\n"<<vc->dataCol()<<endl;
//   cout<<"FLAGS:\n"<<vc->flagsCol()<<endl;
//   cout<<"ROWFLAG:\n"<<vc->rowflagCol()<<endl;
//   cout<<"WEIGHT:\n"<<vc->weightCol()<<endl;
  cout<<"UVW:\n"<<vc->uvwCol(true)<<endl;
  
  cout<<"=================== subset-copy constructor =======\n";
  VCube::Ref vc2;
  vc2 <<= new VCube(*vc,0,0,50,50);
  cout<<vc2->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc2->uvwCol(true)<<endl;
  
  cout<<"=================== append ========================\n";
  vc2().append(*vc,100,50);
  cout<<vc2->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc2->uvwCol(true)<<endl;

  cout<<"=================== append by ref ======================\n";
  VCube::Ref vc3;
  vc3 <<= new VCube(*vc,0,0,0,50);
  vc3().append(*vc2,0,50,VCube::BOTTOM);
  cout<<vc3->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc3->uvwCol(true)<<endl;
  
  cout<<"=================== pop ======================\n";
  vc2().pop(50,VCube::TOP);
  cout<<vc2->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc2->uvwCol(true)<<endl;
  cout<<vc3->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc3->uvwCol(true)<<endl;
  
  cout<<"=================== storing to file ==========\n";
  BOIO outfile("test.vc",BOIO::WRITE);
  outfile<<*vc<<*vc3;
  outfile.close();
  
  cout<<"=================== reading from file ========\n";
  BOIO infile("test.vc");
  ObjRef ref,ref2;
  infile>>ref;
  infile>>ref2;
  infile.close();
  VCube::Ref vc4 = ref.ref_cast<VCube>(),
               vc5 = ref2.ref_cast<VCube>();
  
  cout<<vc4->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc4->uvwCol(true)<<endl;
  cout<<vc5->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc5->uvwCol(true)<<endl;
  
  cout<<"=================== forming set ==============\n";
  VCubeSet::Ref cset(DMI::ANONWR);
  cset() <<= vc;
  cset() <<= vc2;
  cset() <<= vc3;
  cset() <<= vc4;
  cset() <<= vc5;
  cout<<cset->sdebug(4)<<endl;
  
  cout<<"=================== storing to file ==========\n";
  outfile.open("test.vcs",BOIO::WRITE);
  outfile << *cset;
  outfile.close();
  
  cout<<"=================== reading from file ========\n";
  infile.open("test.vcs");
  infile>>ref;
  VCubeSet::Ref cset2 = ref.ref_cast<VCubeSet>();
  cout<<cset2->sdebug(4)<<endl;
  
  cout<<"=================== indexing set ==============\n";
  cout<<cset()[2].sdebug(3)<<endl;
  
  cout<<"=================== popping from set ==============\n";
  cout<<"Ref before pop: "<<vc.sdebug(2)<<endl;
  vc = cset().pop();
  cout<<"Ref after pop: "<<vc.sdebug(2)<<endl;
  cout<<"Set after pop: "<<cset->sdebug(4)<<endl;
  
  
  
  return 0;  
}

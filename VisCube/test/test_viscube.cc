#include "VisCube/VisCubeSet.h"
#include "DMI/BOIO.h"
    
int main (int argc,const char *argv[])
{
  const int NCORR = 4, NFREQ = 10;
  
  Debug::initLevels(argc,argv);
  
  cout<<"=================== new cube ======================\n";
  VisCube::Ref vc;
  vc <<= new VisCube(NCORR,NFREQ,200,50);
  cout<<vc->sdebug(5)<<endl;
  
  cout<<"=================== filling via iterators =========\n";
  int time = 1,rowflag=1000,weight=5000,dataval=0,flagval=20,uvwval=40;
  LoMat_fcomplex dataplane(NCORR,NFREQ);
  LoMat_int flagplane(NCORR,NFREQ);
  LoVec_double uvwvec(3);
  
  for( VisCube::iterator iter = vc().begin(); iter != vc().end(); iter++ )
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
  for( VisCube::const_iterator iter = vc().begin(); iter != vc().end(); iter++ )
  {
    LoVec_fcomplex f_data = iter.f_data(0);
    Assert( f_data.shape()[0] == NFREQ );
  }
  
  cout<<"=================== cube contents (on the fly) ====\n";
  cout<<"TIME:\n"<<vc->time()<<endl;
//   cout<<"DATA:\n"<<vc->dataCol(True)<<endl;
//   cout<<"FLAGS:\n"<<vc->flagsCol(True)<<endl;
//   cout<<"ROWFLAG:\n"<<vc->rowflagCol(True)<<endl;
//   cout<<"WEIGHT:\n"<<vc->weightCol(True)<<endl;
  cout<<"UVW:\n"<<vc->uvwCol(True)<<endl;
  
  
  cout<<"=================== consolidating =================\n";
  vc->consolidate();
  cout<<vc->sdebug(5)<<endl;
  
  cout<<"=================== cube contents =================\n";
//   cout<<"TIME:\n"<<vc->time()<<endl;
//   cout<<"DATA:\n"<<vc->dataCol()<<endl;
//   cout<<"FLAGS:\n"<<vc->flagsCol()<<endl;
//   cout<<"ROWFLAG:\n"<<vc->rowflagCol()<<endl;
//   cout<<"WEIGHT:\n"<<vc->weightCol()<<endl;
  cout<<"UVW:\n"<<vc->uvwCol(True)<<endl;
  
  cout<<"=================== subset-copy constructor =======\n";
  VisCube::Ref vc2;
  vc2 <<= new VisCube(*vc,DMI::WRITE,0,50,50);
  cout<<vc2->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc2->uvwCol(True)<<endl;
  
  cout<<"=================== append ========================\n";
  vc2().append(*vc,100,50);
  cout<<vc2->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc2->uvwCol(True)<<endl;

  cout<<"=================== append by ref ======================\n";
  VisCube::Ref vc3;
  vc3 <<= new VisCube(*vc,DMI::WRITE,0,0,50);
  vc3().append(*vc2,0,50,VisCube::BOTTOM);
  cout<<vc3->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc3->uvwCol(True)<<endl;
  
  cout<<"=================== pop ======================\n";
  vc2().pop(50,VisCube::TOP);
  cout<<vc2->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc2->uvwCol(True)<<endl;
  cout<<vc3->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc3->uvwCol(True)<<endl;
  
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
  VisCube::Ref vc4 = ref.ref_cast<VisCube>(),
               vc5 = ref2.ref_cast<VisCube>();
  
  cout<<vc4->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc4->uvwCol(True)<<endl;
  cout<<vc5->sdebug(5)<<endl;
  cout<<"UVW:\n"<<vc5->uvwCol(True)<<endl;
  
  cout<<"=================== forming set ==============\n";
  VisCubeSet::Ref cset(DMI::ANONWR);
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
  VisCubeSet::Ref cset2 = ref.ref_cast<VisCubeSet>();
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

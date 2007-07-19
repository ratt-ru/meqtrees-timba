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
    
#define paddr(x) printf("=== " #x ": %8p\n",&x)
    
//using DMI::HIID;
using namespace DebugDefault;
using namespace DMI;
    
void TestFunc( const DMI::BlockRef &ref )
{
  cout<<"======================= Copying ref in function\n";
  ref.copy();
}

void TestCountedRefs()
{
  cout<<"=============================================\n";
  cout<<"======================= Testing CountedRefs =\n";
  cout<<"=============================================\n\n";

  cout<<"======================= Allocating two blocks\n";
  DMI::SmartBlock block1(0x2000);
  DMI::SmartBlock block1a(0x2000);
  DMI::SmartBlock * block2 = new DMI::SmartBlock(0x2000);
  DMI::SmartBlock * block2a = new DMI::SmartBlock(0x2000);

  cout<<"======================= attaching ref1/1ro to block1\n";
  DMI::BlockRef ref1( block1,DMI::EXTERNAL|DMI::WRITE );
  Assert(ref1.isDirectlyWritable());
  DMI::BlockRef ref1ro( block1a,DMI::EXTERNAL|DMI::READONLY );
  Assert(!ref1ro.isDirectlyWritable());
  cout<<"======================= attaching ref2/2ro to block2\n";
  DMI::BlockRef ref2( block2 );
  Assert(ref2.isDirectlyWritable());
  DMI::BlockRef ref2ro( block2a, DMI::READONLY );
  // attaching as anon ignores READONLY
  Assert(ref2ro.isDirectlyWritable());
  
  paddr(ref1);
  paddr(ref1ro);
  paddr(ref2);
  paddr(ref2ro);

  cout<<"======================= ref1 -> ref1a (copy constructor)\n";
  Assert(ref1.isOnlyRef());
  DMI::BlockRef ref1a = ref1;
  paddr(ref1a);
  Assert(!ref1.isOnlyRef());
  Assert(block1.targetReferenceCount() == 2 );
  Assert(!ref1.isDirectlyWritable());
  Assert(!ref1a.isDirectlyWritable());
  cout<<"======================= ref1a -> ref1b (copy() method)\n";
  DMI::BlockRef ref1b = ref1a.copy();
  paddr(ref1b);
  Assert( block1.targetReferenceCount() == 3 );
  cout<<"======================= ref1b -> ref1c (xfer constructor)\n";
  DMI::BlockRef ref1c(ref1b,DMI::XFER);
  paddr(ref1c);
  Assert( block1.targetReferenceCount() == 3 );
  Assert( !ref1b.valid() );

  cout<<"======================= writing to ref1c\n";
  Assert(!ref1c.isAnonTarget());
  paddr(ref1c);
  ref1c.dewr();
  paddr(ref1c);
  Assert(ref1c.isAnonTarget());
  Assert(block1.targetReferenceCount() == 2 );
  Assert(ref1c.deref().targetReferenceCount() == 1);
  Assert(ref1c.isDirectlyWritable());
  Assert(!ref1.isDirectlyWritable());
  ref1a.detach();
  Assert(ref1.isDirectlyWritable());
  cout<<"======================= exiting CountedRef Block\n";
}

void TestVec ()
{
  cout<<"=============================================\n";
  cout<<"======================= Testing DMI::Vec   =\n";
  cout<<"=============================================\n\n";

  cout<<"======================= allocating empty field\n";
  DMI::Vec f1;
  cout<<f1.sdebug(2)<<endl;

  cout<<"======================= allocating field of 32 ints\n";
  DMI::Vec f2(Tpint,32);
  f2[0] = 1;
  f2[15] = 2;
  cout<<f2.sdebug(2)<<endl;
  for( int i=0; i<32; i++ )
    cout<<f2[i].as<double>()<<" ";
  cout<<endl;

  cout<<"======================= converting to block: \n";
  DMI::BlockSet set;
  cout<<"toBlock returns "<<f2.toBlock(set)<<endl;
  cout<<"and set: "<<set.sdebug(1)<<endl;

  cout<<"======================= building from block: \n";
  DMI::Vec f2a;
  cout<<"Empty field allocated\n";
  cout<<"fromBlock returns "<<f2a.fromBlock(set)<<endl;
  cout<<"remaining set: "<<set.sdebug(1)<<endl;
  cout<<"resulting field is: "<<f2a.sdebug(2)<<endl;
  for( int i=0; i<32; i++ )
    cout<<f2a[i].as<float>()<<" ";
  cout<<endl;
  cout<<"======================= exiting and destroying:\n";
}
    
void TestList ()
{
  cout<<"=============================================\n";
  cout<<"======================= Testing DMI::List    =\n";
  cout<<"=============================================\n\n";

  cout<<"======================= allocating empty list\n";
  DMI::List f1;
  cout<<f1.sdebug(2)<<endl;
  f1[0] <<= new DMI::Record;
  cout<<f1.sdebug(2)<<endl;

  cout<<"======================= allocating list of 3 items\n";
  DMI::List f2;
  f2[0] = 1;
  f2[1] = "a string";
  f2[2] <<= new DMI::Record;
  DMI::Record &rec = f2.as<DMI::Record>(2);
  f2[2]["a"] = 1;
  f2[2]["b"] = "another string";
  cout<<f2.sdebug(4)<<endl;
  cout<<"f2[2][a]: "<<f2[2]["a"].as<int>()<<endl;
  cout<<"f2[2][b]: "<<f2[2]["b"].as<string>()<<endl;

  cout<<"======================= converting to block: \n";
  DMI::BlockSet set;
  cout<<"toBlock returns "<<f2.toBlock(set)<<endl;
  cout<<"and set: "<<set.sdebug(1)<<endl;

  cout<<"======================= building from block: \n";
  DMI::List f2a;
  cout<<"Empty list allocated\n";
  cout<<"fromBlock returns "<<f2a.fromBlock(set)<<endl;
  cout<<"remaining set: "<<set.sdebug(1)<<endl;
  cout<<"resulting list is: "<<f2a.sdebug(4)<<endl;
  cout<<"f2a[2][a]: "<<f2a[2]["a"].as<int>()<<endl;
  cout<<"f2a[2][b]: "<<f2a[2]["b"].as<string>()<<endl;
  cout<<"======================= exiting and destroying:\n";
}

void TestRecord ()
{
  cout<<"=============================================\n";
  cout<<"======================= Testing DMI::Record   =\n";
  cout<<"=============================================\n\n";

  cout<<"======================= allocating empty record\n";
  DMI::Record rec;

  cout<<"======================= allocating field of 32 ints\n";
  DMI::Vec::Ref f2(new DMI::Vec(Tpint,32)); 
  DMI::Vec &f = f2;
  f[0] = 1;
  f2[15] = 2.5;
  Assert(f[HIID()].as_p<int>() != 0);
  cout<<f2->sdebug(2)<<endl;
  for( int i=0; i<32; i++ )
    cout<<(float)(f[i])<<" ";
  cout<<endl;
  cout<<"======================= adding to record\n";
  HIID id("A.B.C.D");
  cout<<"ID: "<<id.toString()<<endl;
  rec.add(id,f2);
  Assert( f.targetReferenceCount() == 2 );
  Assert( !f2.isDirectlyWritable() );
  rec["A.B.C.D"][20] = 5; // should cause COW
  Assert( f2.isDirectlyWritable() == 1);
  Assert( f.targetReferenceCount() == 1 );
  Assert( rec["A.B.C.D"].exists() );
  Assert( rec["A.B.C.D"].size() == 32 );
  Assert( rec["A.B.C.D"].type() == Tpint );
  Assert( rec["A.B.C.D"][20].type() == Tpint );
  Assert( rec["A.B.C.D"].isContainer() );
  Assert( rec["A.B.C.D"].actualType() == TpDMIObjRef );
  Assert( rec["A.B.C.D"].containerType() == TpDMIVec );
  const Container &cont = rec["A.B.C.D"].as<Container>();
  Assert( cont[20].type() == Tpint );
  cout<<"Values: {{{"<<(int)(rec["A.B.C.D"][20])<<" "<<(int*)&(rec["A.B.C.D"][20])
      <<"  "<<rec["A.B.C.D"].as_p<int>()<<" }}}\n";
  Assert( rec["A.B.C.D/20"].as<int>() == 5 );
  
  int *ptr = &rec["A.B.C.D"];
  Assert(ptr != 0 );
  
  rec["A.B.C.E"] = HIID("A.B.C.D");
  Assert( rec["A.B.C.E"].exists() );
  Assert( rec["A.B.C.E"].size() == 1 );
  Assert( rec["A.B.C.E"].type() == TpDMIHIID );
  Assert( rec["A.B.C.E"].isContainer() );
  Assert( rec["A.B.C.E"].actualType() == TpDMIObjRef );
  Assert( rec["A.B.C.E"].containerType() == TpDMIVec );
  Assert( rec["A.B.C.E/0"].as<HIID>() == HIID("A.B.C.D") );
  HIID id1;
  Assert( rec["A.B.C.E"].get(id1) );
  Assert( !rec["A.B.C.F"].get(id1) );
  Assert( id1 == HIID("A.B.C.D") );
  Assert( rec["A.B.C.E"].as_p<HIID>() != 0 );
  Assert( rec["A.B.C.F"].as_po<HIID>() == 0 );
  
  //  test get-and-init
  Assert( rec["A.B.C.Z"].get(id1,false) == false );
  Assert( rec["A.B.C.Z"].exists() == false );
  Assert( rec["A.B.C.E"].get(id1,false) == true );
  Assert( rec["A.B.C.Z"].get(id1,true) == false );
  Assert( rec["A.B.C.Z"].exists() == true );
  Assert( rec["A.B.C.Z"].as<HIID>() == id1 );
  
  //  test vectors
  HIID id2("A.B.C.D.2");
  rec["A.B.C.Z/1"] = id2;
  std::vector<HIID> hvec,hvec1;
  Assert( rec["A.B.C.Y"].get_vector(hvec) == false );
  Assert( rec["A.B.C.Z"].get_vector(hvec) == true );
  Assert( hvec.size()==2 && hvec[0]==id1 && hvec[1]==id2);
  Assert( rec["A.B.C.Z"].get_vector(hvec,false) == true );
  Assert( rec["A.B.C.Y"].get_vector(hvec,false) == false );
  Assert( rec["A.B.C.Y"].get_vector(hvec,true) == false );
  Assert( rec["A.B.C.Y"].exists());
  Assert( rec["A.B.C.Y"].get_vector(hvec1,true) == true );
  Assert( hvec1.size()==2 && hvec1[0]==id1 && hvec1[1]==id2);
  

  rec["A.B.C.F"] = "test string";
  rec["A.B.C.F"][1] = "another test string";
  Assert( rec["A.B.C.F"].exists() );
  Assert( rec["A.B.C.F"].size() == 2 );
  Assert( rec["A.B.C.F"].type() == Tpstring );
  Assert( rec["A.B.C.F"].isContainer() );
  Assert( rec["A.B.C.F"].actualType() == TpDMIObjRef );
  Assert( rec["A.B.C.F"].containerType() == TpDMIVec );
  Assert( rec["A.B.C.F/1"].as<string>() == "another test string" );
  string str1;
  Assert( rec["A.B.C.F/1"].get(str1) );
  Assert( !rec["A.B.C.G"].get(str1) );
  Assert( str1 == "another test string" );
  
  cout<<"======================= record debug info:\n";
  cout<<rec.sdebug(3)<<endl;
  cout<<"======================= old field debug info:\n";
  cout<<f2->sdebug(3)<<endl;
  cout<<"======================= removing from field:\n";
  rec["A.B.C.D"][31].remove();
  Assert( rec["A.B.C.D"].size() == 31 );
  cout<<"======================= re-inserting into field:\n";
  rec["A.B.C.D/31"] = 5;
  Assert( rec["A.B.C.D"].size() == 32 );
  cout<<"======================= making compound record\n";
  rec["B"] <<= new DMI::Record;
  rec["C"] = f2.copy();
  rec["D"] = f2.copy();
//  Assert( rec["B"].as_DMI::Record_wp() != 0 );
  cout<<"===== added subrecord B\n"<<rec.sdebug(3)<<endl;
  rec["B"]["C"] <<= new DMI::Record;
  cout<<"===== added subrecord B.C\n"<<rec.sdebug(10)<<endl;
  rec["B"]["C"]["A"] <<= new DMI::Vec(Tpint,32);
  rec["B/C/A/10"] = 5;
  rec["B/C/B"] = "a string";
  rec["B/C/C"] = "yet another string";
  Assert( rec["B/C/A"][10].as<int>() == 5 );
  cout<<"Record is "<<rec.sdebug(10)<<endl;

  cout<<"======================= converting record to blockset\n";
  DMI::BlockSet set;
  rec.toBlock(set);
  cout<<"blockset is: "<<set.sdebug(2)<<endl;
  
  cout<<"======================= loading record from blockset\n";
  DMI::Record rec2;
  rec2.fromBlock(set);
  cout<<"New record is "<<rec2.sdebug(10)<<endl;
  cout<<"Blockset now "<<set.sdebug(2)<<endl;
  cout<<"String field is: "<< rec2["B/C/B"].as<string>()<<endl;
  Assert( rec2["B/C/B"].as<string>() == "a string" );

  cout<<"======================= accessing cached field\n";
  cout<<"Value: "<<rec2["B/C/A/10"].as<double>()<<endl;
  Assert( rec2["B/C"]["A"]["10"].as<float>() == 5 );
//  cout<<"Value: "<<rec["A.B.C.E/0"].as<HIID>().toString()<<endl;
  cout<<"Value: "<<rec["A.B.C.F/0"].as<string>()<<endl;
  cout<<"Value: "<<rec["A.B.C.F/1"].as<string>()<<endl;
  Assert( rec["A.B.C.E/0"].as<HIID>() == HIID("A.B.C.D") );
  Assert( rec["A.B.C.F/1"].as<string>() == "another test string" );
  
  cout<<"======================= changing field in original record\n";
  rec["B/C/A/10"] = 10;
  cout<<"Values: "<<rec["B/C/A/10"].as<double>()<<", "<<rec2["B/C/A/10"].as<double>()<<endl;
  Assert( rec["B/C"]["A"]["10"].as<float>() == 10 );
  Assert( rec2["B/C"]["A"]["10"].as<float>() == 5 );
  
  cout<<"======================= getting reference from record\n";
  cout<<rec["B/C/A"].ref().debug(3)<<endl;

  cout<<"======================= checking copy-on-write features\n";
  {
    DMI::Record::Ref rref1(rec,DMI::EXTERNAL|DMI::READONLY);
    DMI::Record::Ref rref2(rref1);
    DMI::Record::Ref rref3(rref1);
    Assert(!rref1.isDirectlyWritable());
    Assert(!rref2.isDirectlyWritable());
    cout<<"rref1 is ref to rec: "<<rref1.sdebug(1)<<endl;
    cout<<"rref2 is ref to rec: "<<rref2.sdebug(1)<<endl;
    DMI::Record &rr = rref1; // this should cause COW of rref1
    Assert(rref1.isOnlyRef());
    Assert(rref1.isAnonTarget());
    const DMI::Record &rr2 = *rref2; // no COW: read-only
    Assert(!rref2.isOnlyRef());
    rref2 = rref1.copy();
    Assert(!rref1.isOnlyRef());
    
    int a1 = rref1["B/C/A/10"];
    string a2 = rref1["B/C/B"].as<string>();
    // no cow yet, should be the same objects
    Assert(rref1["B/C/A/10"].as_p<int>() == rref2["B/C/A/10"].as_p<int>());
    Assert(rref1["B/C/B"].as_p<string>() == rref2["B/C/B"].as_p<string>());
    // now assign, causing cow
    rref1["B/C/A/10"] = 55;
    rref1["B/C/B"] = "another string";
    Assert( rref2["B/C/A"][10].as<int>() == a1 );
    Assert( rref2["B/C/B"].as<string>() == a2 );
    Assert( rref1["B/C/A"][10].as<int>() == 55 );
    Assert( rref1["B/C/B"].as<string>() == "another string" );
    Assert( rref1["C"].as_p<DMI::Vec>() == rref2["C"].as_p<DMI::Vec>() );
    Assert( rref1["B"].as_p<DMI::Record>() != rref2["B"].as_p<DMI::Record>() );
    Assert( rref1["B/C"].as_p<DMI::Record>() != rref2["B/C"].as_p<DMI::Record>() );
    Assert( rref1["B/C/A"].as_p<DMI::Vec>() != rref2["B/C/A"].as_p<DMI::Vec>() );
    Assert( rref1["B/C/B"].as_p<DMI::Vec>() != rref2["B/C/B"].as_p<DMI::Vec>() );
    Assert( rref1["B/C/C"].as_p<DMI::Vec>() == rref2["B/C/C"].as_p<DMI::Vec>() );
    
    cout<<"======================= accessing via read-only ref\n";
    cout<<"ref before write access: "<<rref2.sdebug(10)<<endl;
    Assert(rref2["B/C/A"][10].as<int>() == a1 );
    rref2["B/C/A"][10] = 66;
    cout<<"ref after write access: "<<rref2.sdebug(10)<<endl;
    Assert(rref2["B/C/A"][10].as<int>() == 66 );
  }
  
  cout<<"======================= removing field B/C/A from record\n";
  cout<<"Original record: "<<rec.sdebug(10)<<endl;
  ObjRef fref;
  fref = rec["B/C/A"].remove();
  Assert(fref.valid());
  Assert(!rec["B/C/A"].exists());
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  cout<<"Removed field is: "<<fref.sdebug(10)<<endl;

  cout<<"======================= reattaching instead of B/C\n";
  ObjRef fref2;
  rec["B"]["C"].detach(&fref2) = fref;
  Assert(fref2.valid());
  Assert(fref.valid());
  Assert(fref == rec["B/C"].ref());
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  cout<<"Removed field is: "<<fref2.sdebug(10)<<endl;
  cout<<"======================= copying as B/E\n";
  rec["B/E"] = fref2;
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  cout<<"Source field is: "<<fref2.sdebug(10)<<endl;
  Assert(rec["B/E"].ref() == fref2);
  cout<<"======================= inserting as B/F\n";
  rec["B/F"] <<= fref2;
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  cout<<"Source field is: "<<fref2.sdebug(10)<<endl;
  Assert(rec["B/E"].ref() == rec["B/F"].ref());
  Assert(!fref2.valid());
  cout<<"======================= testing arrays\n";
  cout<<"Creating 10x10 double array\n";
  rec["X"] <<= new DMI::NumArray(Tpdouble,makeLoShape(10,10));
  rec["X.X"] <<= new DMI::NumArray(Tpdouble,makeLoShape(1));
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  
  cout<<"Accessing the array\n";
  LoMat_double arr = rec["X"];
  rec["X.X"] = 2;
  LoVec_double arr2 = rec["X.X"];
  int int3 = rec["X.X"].as<int>();
  Assert(int3 == 2);
  Assert(arr2(0) == 2);
  
  cout<<"Assigning array to another field\n";
  rec["Y"] = arr;
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  
  cout<<"Accessing partial array\n";
  LoVec_double row = rec["X/2.*"];
  cout<<"Row shape is: "<<row.shape()<<endl;
  
  cout<<"Assigning partial array\n";
  rec["Y/*.4"] = row;
  
  cout<<"Assigning a vector to a partial array\n";
  vector<double> vec(10);
  rec["Y/*.4"] = vec;
  
  cout<<"Assigning a vector to a new field\n";
  rec["Z"] = vec;
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  
  cout<<"Assigning a vector to an existing field\n";
  rec["Z"] = vec;
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  
  cout<<"Checking transparent array indexing\n";
  rec["X.Y.Z"] <<= new DMI::NumArray(Tpdouble,makeLoShape(10),DMI::ZERO);
  Assert(rec["X.Y.Z"][0].as<double>() == 0);
  {
    cout<<"Checking ContainerIters\n";
    ContainerIter<double> data(rec["X.Y.Z"]);
    cout<<"filling "<<data.size()<<endl;
    while( !data.end() )
      data.next(0);
  }
  cout<<"======================= testing sparse DMI::Vec\n";
  cout<<"Checking sparse DMI::Vec\n";
  rec["G"] <<= new DMI::Vec(TpDMINumArray,5);
  rec["G"][0] <<= new DMI::NumArray(Tpint,makeLoShape(10,10));
  rec["G"][5] <<= new DMI::NumArray(Tpint,makeLoShape(10,10));
  cout<<"DF[0]: "<<rec["G"][0].exists()<<endl;
  cout<<"DF[1]: "<<rec["G"][1].exists()<<endl;
  cout<<"DF[5]: "<<rec["G"][5].exists()<<endl;
  
  cout<<"======================= testing Array<string>\n";
  DMI::NumArray &strarr = *new DMI::NumArray(Tpstring,makeLoShape(10,10),DMI::WRITE|DMI::ZERO);
  rec["A.Z.G"] <<= strarr;
  for(int i=0; i<10; i++)
    for(int j=0; j<10; j++)
      rec[HIID("A.Z.G")][HIID(i)|j] = Debug::ssprintf("%d-%d",i,j);
//  cout<<"Array contents: "<<rec["A.Z.G"].as_LoMat_string()<<endl;
  cout<<"converting to block\n";
  DMI::BlockSet arrset;
  strarr.toBlock(arrset);
  
  cout<<"converting from block\n";
  DMI::NumArray strarr2;
  strarr2.fromBlock(arrset);
//  cout<<"Array contents: "<<strarr2[HIID()].as_LoMat_string()<<endl;
  for(int i=0; i<10; i++)
    for(int j=0; j<10; j++)
    {
      Assert( strarr2[HIID(i)|j].as<string>() == Debug::ssprintf("%d-%d",i,j));
    }
  
  cout<<"======================= testing BOIO\n";
  cout<<"======================= writing\n";
  BOIO boio("test.boio",BOIO::WRITE);
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  boio << rec << rec["X"].as<DMI::NumArray>();
  boio.close();
  
  cout<<"======================= reading\n";
  boio.open("test.boio",BOIO::READ);
  ObjRef ref;
  while( boio>>ref )
  {
    cout<<"Read object of type "<<ref->objectType().toString()<<endl;
    cout<<ref->sdebug(10)<<endl;
  }
  cout<<"======================= finished reading\n";
  boio.close();
  
  cout<<"======================= testing DMI::Record::merge\n";
  {
    DMI::Record rec1,rec2;
    rec1["A"] = 0;
    rec1["B"] = 1;
    rec1["C"] = 2;
    rec2["C"] = 22;
    rec2["D"] = 3;
    
    DMI::Record rec1a(rec1,DMI::WRITE|DMI::DEEP);
    rec1a.merge(rec2,false); // merge w/o overwrite
    Assert( rec1a["A"].as<int>() == 0 );
    Assert( rec1a["C"].as<int>() == 2 );
    Assert( rec1a["D"].as<int>() == 3 );
    DMI::Record rec1b(rec1,DMI::WRITE|DMI::DEEP);
    rec1b.merge(rec2,true); // merge w/o overwrite
    Assert( rec1b["A"].as<int>() == 0 );
    Assert( rec1b["C"].as<int>() == 22 );
    Assert( rec1b["D"].as<int>() == 3 );
  }
  cout<<"======================= exiting\n";
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
    cout<<"HIID('a_b_c'): "<<HIID("a.b.c",0,".")<<endl;
    HIID test("1.");
    cout<<test.toString()<<endl;
    test = test|5;
    cout<<test.toString()<<endl;
    cout<<HIID("_._.:6").toString()<<endl;
    
    const string lit = "uhfu.efhf.ihusjka.sjkjk";
    const string slit = "$" + lit;
    HIID hlit1(slit),hlit2(lit,true,"_.");
    Assert(hlit1 == hlit2);
    cout<<hlit1<<endl;
    cout<<hlit1.toString('.',false)<<endl;
    TestCountedRefs();
    TestVec();
    TestList();
    TestRecord();
  }
  catch( std::exception &err )
  {
    cout<<"\nCaught exception:\n"<<err.what()<<endl;
    return 1;
  }

  return 0;
}
    
    
    

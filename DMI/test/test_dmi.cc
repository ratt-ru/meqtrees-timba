#include "DMI/AID-DMI.h"
#include "DMI/TID-DMI.h"
#include "DMI/DataRecord.h"
#include "DMI/DataArray.h"
#include "DMI/DataField.h"
#include "DMI/BOIO.h"
#include "DMI/NCIter.h"
    
#define paddr(x) printf("=== " #x ": %08x\n",(int)&x)

        
void TestFunc( const BlockRef &ref )
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
  SmartBlock block1(0x2000);
  SmartBlock * block2 = new SmartBlock(0x2000);

  cout<<"======================= attaching ref1 to block1\n";
  BlockRef ref1( block1,DMI::NON_ANON|DMI::WRITE );
  cout<<"======================= attaching ref2/3 to block2\n";
  BlockRef ref2( block2,DMI::ANON|DMI::WRITE ),
           ref3( block2,DMI::ANON|DMI::READONLY );
  paddr(ref1);
  paddr(ref2);
  paddr(ref3);

  cout<<"======================= ref1 -> ref1a (copy constructor)\n";
  BlockRef ref1a(ref1,DMI::COPYREF|DMI::WRITE);
  paddr(ref1a);
  Assert( block1.refCount() == 2 );
  cout<<"======================= ref1a -> ref1b (copy() method)\n";
  BlockRef ref1b = ref1a.copy();
  paddr(ref1b);
  Assert( block1.refCount() == 3 );
  cout<<"======================= ref1b -> ref1c (xfer constructor)\n";
  BlockRef ref1c(ref1b);
  paddr(ref1c);
  Assert( block1.refCount() == 3 );

  cout<<"======================= privatizing ref3\n";
  ref3.privatize();
  Assert( block2->refCount() == 1 );
  Assert( ref3.deref().refCount() == 1);
  cout<<"======================= passing ref3 to function taking a LockedRef\n";
  TestFunc(ref3);

  cout<<"======================= ref1a -> ref1d (copy(PERSIST))\n";
  BlockRef ref1d = ref1a.copy(DMI::PERSIST);
  cout<<"======================= ref1d -> ref1e (= operator)\n";
  BlockRef ref1e = ref1d;

  cout<<"======================= copying ref2 -> ref2a (copy(PRESERVE_RW))\n";
  BlockRef ref2a = ref2.copy(DMI::PRESERVE_RW);
  Assert( block2->refCount() == 2 );
  Assert( ref2a.isWritable() );
  cout<<"======================= exiting CountedRef Block\n";
}

void TestDataField ()
{
  cout<<"=============================================\n";
  cout<<"======================= Testing DataField   =\n";
  cout<<"=============================================\n\n";

  cout<<"======================= allocating empty field\n";
  DataField f1;
  cout<<f1.sdebug(2)<<endl;

  cout<<"======================= allocating field of 32 ints\n";
  DataField f2(Tpint,32);
  f2[0] = 1;
  f2[15] = 2;
  cout<<f2.sdebug(2)<<endl;
  for( int i=0; i<32; i++ )
    cout<<f2[i].as<double>()<<" ";
  cout<<endl;

  cout<<"======================= converting to block: \n";
  BlockSet set;
  cout<<"toBlock returns "<<f2.toBlock(set)<<endl;
  cout<<"and set: "<<set.sdebug(1)<<endl;

  cout<<"======================= building from block: \n";
  DataField f2a;
  cout<<"Empty field allocated\n";
  cout<<"fromBlock returns "<<f2a.fromBlock(set)<<endl;
  cout<<"remaining set: "<<set.sdebug(1)<<endl;
  cout<<"resulting field is: "<<f2a.sdebug(2)<<endl;
  for( int i=0; i<32; i++ )
    cout<<f2a[i].as<float>()<<" ";
  cout<<endl;
  cout<<"======================= exiting and destroying:\n";
}
    

void TestDataRecord ()
{
  cout<<"=============================================\n";
  cout<<"======================= Testing DataRecord   =\n";
  cout<<"=============================================\n\n";

  cout<<"======================= allocating empty record\n";
  DataRecord rec;

  cout<<"======================= allocating field of 32 ints\n";
  DataFieldRef f2(new DataField(Tpint,32),DMI::ANON|DMI::WRITE); 
  DataField &f = f2.dewr();
  f[0] = 1;
  f[15] = 2.5;
//  Assert(f[HIID()].as_int_p() != 0);
  cout<<f2->sdebug(2)<<endl;
  for( int i=0; i<32; i++ )
    cout<<(float)(f[i])<<" ";
  cout<<endl;
  cout<<"======================= adding to record\n";
  HIID id("A.B.C.D");
  cout<<"ID: "<<id.toString()<<endl;
  rec.add(id,f2.dewr_p(),DMI::COPYREF|DMI::WRITE);
  rec["A.B.C.D"][20] = 5;
  Assert( rec["A.B.C.D"].exists() );
  Assert( rec["A.B.C.D"].size() == 32 );
  Assert( rec["A.B.C.D"].type() == Tpint );
  Assert( rec["A.B.C.D"][20].type() == Tpint );
  Assert( rec["A.B.C.D"].isContainer() );
  Assert( rec["A.B.C.D"].actualType() == TpObjRef );
  Assert( rec["A.B.C.D"].containerType() == TpDataField );
  cout<<"Values: {{{"<<(int)(rec["A.B.C.D"][20])<<" "<<(int*)&(rec["A.B.C.D"][20])
      <<"  "<<rec["A.B.C.D"].as_p<int>()<<" }}}\n";
  Assert( rec["A.B.C.D/20"].as<int>() == 5 );
  
  int *ptr = &rec["A.B.C.D"];
  Assert(ptr != 0 );
  
  rec["A.B.C.E"] = HIID("A.B.C.D");
  Assert( rec["A.B.C.E"].exists() );
  Assert( rec["A.B.C.E"].size() == 1 );
  Assert( rec["A.B.C.E"].type() == TpHIID );
  Assert( rec["A.B.C.E"].isContainer() );
  Assert( rec["A.B.C.E"].actualType() == TpObjRef );
  Assert( rec["A.B.C.E"].containerType() == TpDataField );
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
  Assert( rec["A.B.C.F"].actualType() == TpObjRef );
  Assert( rec["A.B.C.F"].containerType() == TpDataField );
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
  rec["B"] <<= new DataRecord;
  rec["C"] = f2.copy();
  rec["D"] = f2.copy();
//  Assert( rec["B"].as_DataRecord_wp() != 0 );
  cout<<"===== added subrecord B\n"<<rec.sdebug(3)<<endl;
  rec["B"]["C"] <<= new DataRecord;
  cout<<"===== added subrecord B.C\n"<<rec.sdebug(10)<<endl;
  rec["B"]["C"]["A"] <<= new DataField(Tpint,32);
  rec["B/C/A/10"] = 5;
  rec["B/C/B"] = "a string";
  rec["B/C/C"] = "yet another string";
  Assert( rec["B/C/A"][10].as<int>() == 5 );
  cout<<"Record is "<<rec.sdebug(10)<<endl;

  cout<<"======================= converting record to blockset\n";
  BlockSet set;
  rec.toBlock(set);
  cout<<"blockset is: "<<set.sdebug(2)<<endl;
  
  cout<<"======================= loading record from blockset\n";
  DataRecord rec2;
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

  cout<<"======================= deep-cloning record\n";
  DataRecord rec3 = rec2;
  cout<<"Record 3 after cloning: "<<rec3.sdebug(10)<<endl;
//  rec3.setBranch("B",DMI::PRIVATIZE|DMI::WRITE|DMI::DEEP);
//  cout<<"Record 3 after privatize of branch B: "<<rec3.sdebug(10)<<endl;
  rec3.privatize(DMI::WRITE|DMI::DEEP);
  cout<<"Record 3 after full deep-privatize: "<<rec3.sdebug(10)<<endl;
  rec3["B"].privatize(DMI::READONLY|DMI::DEEP);
  cout<<"Record 3 after branch B privatize as read-only: "<<rec3.sdebug(10)<<endl;
  
  cout<<"======================= checking privatize-on-write features\n";
  {
    DataRecord::Ref rref1(new DataRecord(rec,DMI::READONLY|DMI::DEEP),DMI::READONLY|DMI::ANON);
    DataRecord::Ref rref2(rref1,DMI::COPYREF|DMI::READONLY);
    cout<<"rref1 is ref to deep r/o clone of rec: "<<rref1.sdebug(10)<<endl;
    cout<<"rref2 is r/o copy of rref1: "<<rref2.sdebug(1)<<endl;
    rref1.privatize(DMI::WRITE);
    DataRecord &rr = rref1;
    const DataRecord &rr2 = *rref2;
    cout<<"rr after privatize(DMI::WRITE): "<<rr.sdebug(10)<<endl;
    
//    rec["B/C/A/10"] = 5;
//    rec["B/C/B"] = "a string";
//    Assert( rec["B/C/A"][10].as<int>() == 5 );
    
    int a1 = (*rref1)["B/C/A/10"];
    string a2 = (*rref1)["B/C/B"].as<string>();
    rr["B/C/A/10"] = 55;
    cout<<"rr after assignment to B/C/A/10: "<<rr.sdebug(10)<<endl;
    rr["B/C/B"] = "another string";
    cout<<"rr after assignment to B/C/B: "<<rr.sdebug(10)<<endl;
    cout<<"Original record: "<<rref2->sdebug(10)<<endl;
    Assert( rr2["B/C/A"][10].as<int>() == a1 );
    Assert( rr2["B/C/B"].as<string>() == a2 );
    Assert( rr["B/C/A"][10].as<int>() == 55 );
    Assert( rr["B/C/B"].as<string>() == "another string" );
    Assert( rr["C"].as_p<DataField>() == rr2["C"].as_p<DataField>() );
    Assert( rr["B"].as_p<DataRecord>() != rr2["B"].as_p<DataRecord>() );
    Assert( rr["B/C"].as_p<DataRecord>() != rr2["B/C"].as_p<DataRecord>() );
    Assert( rr["B/C/A"].as_p<DataField>() != rr2["B/C/A"].as_p<DataField>() );
    Assert( rr["B/C/B"].as_p<DataField>() != rr2["B/C/B"].as_p<DataField>() );
    Assert( rr["B/C/C"].as_p<DataField>() == rr2["B/C/C"].as_p<DataField>() );
    
    cout<<"======================= accessing via read-only ref\n";
    cout<<"ref before write access: "<<rref2.sdebug(10)<<endl;
    Assert(rref2["B/C/A"][10].as<int>() == a1 );
    rref2["B/C/A"][10] = 66;
    cout<<"ref after write access: "<<rref2.sdebug(10)<<endl;
    Assert(rref2["B/C/A"][10].as<int>() == 66 );
    
  }
  
//  cout<<"======================= autoprivatizing rec3[B/C/A] for write\n";
//  rec3.setBranch("B/C/A",DMI::WRITE)[10] = 2;
//  cout<<"Record 3 is now: "<<rec3.sdebug(10)<<endl;

  cout<<"======================= removing field B/C/A from record\n";
  cout<<"Original record: "<<rec.sdebug(10)<<endl;
  ObjRef fref;  
  fref = rec["B/C/A"].remove();
  Assert(fref.valid());
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  cout<<"Removed field is: "<<fref.sdebug(10)<<endl;

  cout<<"======================= reattaching instead of B/C\n";
  ObjRef fref2;
  rec["B"]["C"].detach(&fref2) = fref;
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  cout<<"Removed field is: "<<fref2.sdebug(10)<<endl;
  cout<<"======================= copying as B/E\n";
  rec["B/E"] = fref2;
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  cout<<"Source field is: "<<fref2.sdebug(10)<<endl;
  cout<<"======================= inserting as B/F\n";
  rec["B/F"] <<= fref2;
  cout<<"Record is now: "<<rec.sdebug(10)<<endl;
  cout<<"Source field is: "<<fref2.sdebug(10)<<endl;
  cout<<"======================= testing arrays\n";
  cout<<"Creating 10x10 double array\n";
  rec["X"] <<= new DataArray(Tpdouble,makeLoShape(10,10));
  rec["X.X"] <<= new DataArray(Tpdouble,makeLoShape(1));
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
  rec["X.Y.Z"] <<= new DataArray(Tpdouble,makeLoShape(10),DMI::ZERO);
  Assert(rec["X.Y.Z"][0].as<double>() == 0);
  
  {
    cout<<"Checking NCIters\n";
    NCIter_double data(rec["X.Y.Z"]);
    cout<<"filling "<<data.size()<<endl;
    while( !data.end() )
      data.next(0);
  }
  cout<<"======================= testing sparse DataField\n";
  cout<<"Checking sparse DataField\n";
  rec["G"] <<= new DataField(TpDataArray,5);
  rec["G"][0] <<= new DataArray(Tpint,makeLoShape(10,10));
  rec["G"][5] <<= new DataArray(Tpint,makeLoShape(10,10));
  cout<<"DF[0]: "<<rec["G"][0].exists()<<endl;
  cout<<"DF[1]: "<<rec["G"][1].exists()<<endl;
  cout<<"DF[5]: "<<rec["G"][5].exists()<<endl;
  
  cout<<"======================= testing Array<string>\n";
  DataArray &strarr = *new DataArray(Tpstring,makeLoShape(10,10),DMI::WRITE|DMI::ZERO);
  rec["A.Z.G"] <<= strarr;
  for(int i=0; i<10; i++)
    for(int j=0; j<10; j++)
      rec[HIID("A.Z.G")][HIID(i)|j] = Debug::ssprintf("%d-%d",i,j);
//  cout<<"Array contents: "<<rec["A.Z.G"].as_LoMat_string()<<endl;
  cout<<"converting to block\n";
  BlockSet arrset;
  strarr.toBlock(arrset);
  
  cout<<"converting from block\n";
  DataArray strarr2;
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
  boio << rec << rec["X"].as<DataArray>();
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
  
  cout<<"======================= testing DataRecord::merge\n";
  {
    DataRecord rec1,rec2;
    rec1["A"] = 0;
    rec1["B"] = 1;
    rec1["C"] = 2;
    rec2["C"] = 22;
    rec2["D"] = 3;
    
    DataRecord rec1a(rec1,DMI::WRITE|DMI::DEEP);
    rec1a.merge(rec2,False); // merge w/o overwrite
    Assert( rec1a["A"].as<int>() == 0 );
    Assert( rec1a["C"].as<int>() == 2 );
    Assert( rec1a["D"].as<int>() == 3 );
    DataRecord rec1b(rec1,DMI::WRITE|DMI::DEEP);
    rec1b.merge(rec2,True); // merge w/o overwrite
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
    TestCountedRefs();
    TestDataField();
    TestDataRecord();
    
    HIID test("1.");
    cout<<test.toString()<<endl;
    test = test|5;
    cout<<test.toString()<<endl;
    cout<<HIID("_._.:6").toString()<<endl;
  }
  catch( std::exception &err )
  {
    cout<<"\nCaught exception:\n"<<err.what()<<endl;
    return 1;
  }

  return 0;
}
    
    
    

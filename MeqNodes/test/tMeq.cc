//# tMeq.cc: test program for the Meq classes
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$


#include <Common/Debug.h>
#include <MEQ/Forest.h>
#include <MEQ/Node.h>
#include <MEQ/Function.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Polc.h>
#include <MEQ/TID-Meq.h>
#include <MeqNodes/TID-MeqNodes.h>
#include <DMI/DataArray.h>
#include <exception>

using namespace Meq;
using namespace std;

int main (int argc,const char* argv[])
{
  Debug::setLevel("MeqNode",5);
  Debug::setLevel("MeqForest",5);
  Debug::initLevels(argc,argv);
  try 
  {
    cout << complex<double>(1. ,2.) << endl;
    LoMat_dcomplex cv1(1,1);
    cv1 = dcomplex (1., 2.);
    cout << cv1 << endl;
    LoMat_double defVal1(1,1);
    defVal1 = 1.;
    LoMat_double defVal2(1,1);
    defVal2 = 2.;
    Forest forest;

    cout << "============ creating parm1 node ==================\n";
    DataRecord::Ref rec_child1(DMI::ANONWR);
    rec_child1["Class"] = "MeqParm";
    rec_child1["Name"] = "p1";
    //    rec_child1["Table.Name"] = "meqadd.MEP";
    rec_child1["Default"] <<= new Polc(defVal1);
    int index_child1;
    Node& child1 = forest.create(index_child1,rec_child1);
    
    cout << "============ creating child2 node ==================\n";
    DataRecord::Ref rec_child2(DMI::ANONWR);
    rec_child2["Class"] = "MeqParm";
    rec_child2["Name"] = "p2";
    //    rec_child2["Table.Name"] = "meqadd.MEP";
    rec_child2["Default"] <<= new Polc(defVal2);
    int index_child2;
    Node& child2 = forest.create(index_child2,rec_child2);
    
    cout << "============ creating child3 node ==================\n";
    DataRecord::Ref rec_child3(DMI::ANONWR);
    rec_child3["Class"] = "MeqConstant";
    rec_child3["Name"] = "c3";
    rec_child3["Value"] = double(3);
    int index_child3;
    Node& child3 = forest.create(index_child3,rec_child3);
    
    cout << "============ creating child4 node ==================\n";
    DataRecord::Ref rec_child4(DMI::ANONWR);
    rec_child4["Class"] = "MeqConstant";
    rec_child4["Name"] = "c4";
    rec_child4["Value"] = dcomplex(2, 1.1);
    int index_child4;
    Node& child4 = forest.create(index_child4,rec_child4);
    
    cout << "============ creating cos node ===\n";
    DataRecord::Ref recc(DMI::ANONWR);
    recc["Class"] = "MeqCos";
    recc["Name"] = "cosp1";
    recc["Children"] <<= new DataRecord;
      recc["Children"]["A"] = "p1";
    int index_cos;
    Node& chcos = forest.create(index_cos,recc);

    cout << "============ creating add node ===\n";
    DataRecord::Ref rec(DMI::ANONWR);
    rec["Class"] = "MeqAdd";
    rec["Name"] = "add1_2";
    rec["Children"] <<= new DataRecord;
      rec["Children"]["A"] = "cosp1";
      rec["Children"]["B"] = index_child2; 
      rec["Children"]["C"] = "c4";
      rec["Children"]["D"] = "c3";
    int index_add;
    Node& chadd = forest.create(index_add,rec);
    
    cout << "============ resolving children on add =========\n";
    chadd.resolveChildren();
    
    // test children type matching
    vector<TypeId> types(1, TpMeqParm);
//    dynamic_cast<Function&>(chcos).testChildren (types);

    cout << "============ getting result =========\n";
    Domain domain(1,4, -2,3);
    Request::Ref reqref;
    reqref <<= new Request(new Cells(domain, 4, 4));
    Result::Ref refres;
    int flag = chadd.execute(refres,*reqref);
    cout << flag << endl;
    cout << refres->vellSet(0).getValue() << endl;
  } 
  catch (std::exception& x) 
  {
    cout << "Caught exception: " << x.what() << endl;
    return 1;
  }
  cout << "OK" << endl;
  return 0;
}

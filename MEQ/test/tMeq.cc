//# tMeq.cc: test program for the MEQ classes
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
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <DMI/DataArray.h>
#include <exception>

using namespace MEQ;

int main (int argc,const char* argv[])
{
  Debug::setLevel("MeqNode",5);
  Debug::setLevel("MeqForest",5);
  Debug::initLevels(argc,argv);
  try 
  {
    LoMat_double defVal1(2,2);
    defVal1 = 1.;
    LoMat_double defVal2(1,1);
    defVal2 = 2.;
    Forest forest;

    cout << "============ creating parm1 node ==================\n";
    DataRecord::Ref rec_child1(DMI::ANONWR);
    rec_child1()["Class"] = "MEQParmPolcStored";
    rec_child1()["Name"] = "p1";
    rec_child1()["Tablename"] = "meqadd.MEP";
    rec_child1()["Default"] = defVal1;
    int index_child1;
    Node& child1 = forest.create(index_child1,rec_child1);
    
    cout << "============ creating child2 node ==================\n";
    DataRecord::Ref rec_child2(DMI::ANONWR);
    rec_child2()["Class"] = "MEQParmPolcStored";
    rec_child2()["Name"] = "p2";
    rec_child2()["Tablename"] = "meqadd.MEP";
    rec_child2()["Default"] = defVal2;
    int index_child2;
    Node& child2 = forest.create(index_child2,rec_child2);
    
    cout << "============ creating cos node ===\n";
    DataRecord::Ref recc(DMI::ANONWR);
    recc()["Class"] = "MEQCos";
    recc()["Name"] = "cosp1";
    recc()["Children"] <<= new DataRecord;
      recc()["Children"]["A"] = "p1";
    int index_cos;
    Node& chcos = forest.create(index_cos,recc);

    cout << "============ creating add node ===\n";
    DataRecord::Ref rec(DMI::ANONWR);
    rec()["Class"] = "MEQAdd";
    rec()["Name"] = "add1_2";
    rec()["Children"] <<= new DataRecord;
      rec()["Children"]["A"] = "cosp1";
      rec()["Children"]["B"] = index_child2; 
    int index_add;
    Node& chadd = forest.create(index_add,rec);
    
    cout << "============ resolving children on add =========\n";
    chadd.resolveChildren();

    cout << "============ getting result =========\n";
    Domain domain(1,4, -2,3);
    Request req(Cells(domain, 4, 4));
    Result res;
    Result::Ref refres(res, DMI::WRITE||DMI::EXTERNAL);;
    int flag = chadd.getResult (refres, req);
    cout << flag << endl;
    cout << res.getValue() << endl;
  } 
  catch (std::exception& x) 
  {
    cout << "Caught exception: " << x.what() << endl;
    return 1;
  }
  cout << "OK" << endl;
  return 0;
}

//# tForest.cc: test program for MEQ::Forest and MEQ::Node class
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
#include <exception>

using namespace MEQ;

int main (int argc,const char *argv[])
{
  Debug::setLevel("MeqNode",5);
  Debug::setLevel("MeqForest",5);
  Debug::initLevels(argc,argv);
  try 
  {
    Forest forest;
    cout << "============ creating child1 node ==================\n";
    DataRecord::Ref rec_child1(DMI::ANONWR);
    rec_child1()["Class"] = "MEQNode";
    rec_child1()["Name"] = "child1";
    int index_child1;
    Node &child1 = forest.create(index_child1,rec_child1);
    cout << "created child1 "<<index_child1<<": "<<child1.sdebug(5)<<endl;
    
    cout << "============ creating child2 node ==================\n";
    DataRecord::Ref rec_child2(DMI::ANONWR);
    rec_child2()["Class"] = "MEQNode";
    rec_child2()["Name"] = "child2";
    int index_child2;
    Node &child2 = forest.create(index_child2,rec_child2);
    cout << "created child2 "<<index_child2<<": "<<child2.sdebug(5)<<endl;
    
    cout << "============ creating parent1 node ===\n";
    DataRecord::Ref rec(DMI::ANONWR);
    rec()["Class"] = "MEQNode";
    rec()["Name"] = "parent1";
    rec()["Children"] <<= new DataRecord;
      rec()["Children"]["A"] = "child1"; 
      rec()["Children"]["B"] = index_child2; 
      rec()["Children"]["C"] <<= new DataRecord;
        rec()["Children/C/Class"] = "MEQNode";
        rec()["Children/C/Name"] = "child3";
      rec()["Children"]["D"] <<= new DataRecord;
        rec()["Children/D/Class"] = "MEQNode";
        rec()["Children/D/Name"] = "child4";
      rec()["Children"]["E"] = "child5";
    int index_parent1;
    Node &parent1 = forest.create(index_parent1,rec);
    cout << "created parent1 "<<index_parent1<<": "<<parent1.sdebug(5)<<endl;
    
    cout << "============ creating child5 node ==================\n";
    DataRecord::Ref rec_child5(DMI::ANONWR);
    rec_child5()["Class"] = "MEQNode";
    rec_child5()["Name"] = "child5";
    int index_child5;
    Node &child5 = forest.create(index_child5,rec_child5);
    cout << "created child5 "<<index_child5<<": "<<child5.sdebug(5)<<endl;
    
    cout << "============ resolving children on parent1 =========\n";
    parent1.resolveChildren();
    cout << "parent1: "<<parent1.sdebug(5)<<endl;
  } 
  catch (std::exception& x) 
  {
    cout << "Caught exception: " << x.what() << endl;
    return 1;
  }
  cout << "OK" << endl;
  return 0;
}

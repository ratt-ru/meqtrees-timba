//# tForest.cc: test program for Meq::Forest and Meq::Node class
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
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


#include <TimBase/Debug.h>
#include <MEQ/Forest.h>
#include <MEQ/Node.h>
#include <exception>
#include <DMI/Vec.h>
#include <MEQ/Polc.h>
#include <MEQ/PolcLog.h>

using namespace Meq;

int main (int argc,const char *argv[])
{
  Debug::setLevel("MeqNode",5);
  Debug::setLevel("MeqForest",5);
  Debug::initLevels(argc,argv);
  try 
  {
    Forest forest;
    cout << "============ creating child1 node ==================\n";
    DMI::Record::Ref rec_child1(DMI::ANON);
    rec_child1()["Class"] = "MeqNode";
    rec_child1()["Name"] = "child1";
    int index_child1;
    Node &child1 = forest.create(index_child1,rec_child1);
    cout << "created child1 "<<index_child1<<": "<<child1.sdebug(5)<<endl;
    
    cout << "============ creating child2 node ==================\n";
    DMI::Record::Ref rec_child2(DMI::ANON);
    rec_child2()["Class"] = "MeqNode";
    rec_child2()["Name"] = "child2";
    int index_child2;
    Node &child2 = forest.create(index_child2,rec_child2);
    cout << "created child2 "<<index_child2<<": "<<child2.sdebug(5)<<endl;
    
    cout << "============ creating parent1 node ===\n";
    DMI::Record::Ref rec(DMI::ANON);
    rec()["Class"] = "MeqNode";
    rec()["Name"] = "parent1";
    rec()["Children"] <<= new DMI::Record;
      rec()["Children"]["1"] = "child1"; 
      rec()["Children"]["2"] = index_child2; 
      rec()["Children"]["3"] <<= new DMI::Record;
        rec()["Children/3/Class"] = "MeqNode";
        rec()["Children/3/Name"] = "child3";
      rec()["Children"]["4"] <<= new DMI::Record;
        rec()["Children/4/Class"] = "MeqNode";
        rec()["Children/4/Name"] = "child4";
      rec()["Children"]["5"] = "child5";
    int index_parent1;
    Node &parent1 = forest.create(index_parent1,rec);
    cout << "created parent1 "<<index_parent1<<": "<<parent1.sdebug(5)<<endl;
    
    cout << "============ creating child5 node ==================\n";
    DMI::Record::Ref rec_child5(DMI::ANON);
    rec_child5()["Class"] = "MeqNode";
    rec_child5()["Name"] = "child5";
    int index_child5;
    Node &child5 = forest.create(index_child5,rec_child5);
    cout << "created child5 "<<index_child5<<": "<<child5.sdebug(5)<<endl;
    
//     cout << "============ creating vec of funklets ==============\n";
//     DMI::Vec::Ref vecref;
//     vecref <<= new DMI::Vec(TpMeqFunklet,2);
//     vecref().put(0,new Polc);
//     vecref().put(1,new PolcLog);
//     const Funklet &funk = vecref->as<Funklet>(0);
//     const Polc &polc = vecref->as<PolcLog>(1);
  } 
  catch (std::exception& x) 
  {
    cout << "Caught exception: " << x.what() << endl;
    return 1;
  }
  cout << "OK" << endl;
  return 0;
}

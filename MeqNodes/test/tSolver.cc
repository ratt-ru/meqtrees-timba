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
//# but WITHOUT ANY WARRANTY; without even the impqlied warranty of
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
#include <MEQ/TID-Meq.h>
#include <MeqNodes/Condeq.h>
#include <MeqNodes/Solver.h>
#include <MeqNodes/Polc.h>
#include <MEQ/MeqVocabulary.h>
#include <DMI/DataArray.h>
#include <exception>

using namespace Meq;

int main (int argc,const char* argv[])
{
  //  Debug::setLevel("MeqNode",5);
  //  Debug::setLevel("MeqForest",5);
  Debug::initLevels(argc,argv);
  try 
  {
    LoMat_double defVal1(2,3);
    defVal1(0,0) = 1.;
    defVal1(1,0) = 2.;
    defVal1(0,1) = 1.5;
    defVal1(1,1) = 0.2;
    defVal1(0,2) = 1.3;
    defVal1(1,2) = 0.5;
    LoMat_double defVal2(2,3);
    defVal2(0,0) = 2.;
    defVal2(1,0) = 10.;
    defVal2(0,1) = 2.;
    defVal2(1,1) = 10.;
    defVal2(0,2) = 2.;
    defVal2(1,2) = 10.;
    Forest forest;

    cout << "============ creating parm1 node ==================\n";
    DataRecord::Ref rec_child1(DMI::ANONWR);
    rec_child1["Class"] = "MeqParm";
    rec_child1["Name"] = "p1";
    rec_child1["Default"] <<= new Polc(defVal1);
    rec_child1["Node.Groups"] = HIID("Solvable.Parm");
    int index_child1;
    Node& child1 = forest.create(index_child1,rec_child1);
    
    cout << "============ creating child2 node ==================\n";
    DataRecord::Ref rec_child2(DMI::ANONWR);
    rec_child2["Class"] = "MeqParm";
    rec_child2["Name"] = "p2";
    rec_child2["Default"] <<= new Polc(defVal2);
    rec_child2["Node.Groups"] = HIID("Solvable.Parm");
    int index_child2;
    Node& child2 = forest.create(index_child2,rec_child2);
    
    cout << "============ creating condeq node ===\n";
    DataRecord::Ref recc(DMI::ANONWR);
    recc["Class"] = "MeqCondeq";
    recc["Name"] = "condeq1";
    recc["Children"] <<= new DataRecord;
      recc["Children"]["A"] = "p1";
      recc["Children"]["B"] = "p2";
    int index_con;
    Node& chcon = forest.create(index_con,recc);

    cout << "============ creating solver node ===\n";
    DataRecord::Ref rec(DMI::ANONWR);
    rec["Class"] = "MeqSolver";
    rec["Name"] = "solve1";
    rec["Num.Steps"] = 5;
    rec["Parm.Group"] = HIID("Solvable.Parm");
    rec["Children"] <<= new DataRecord;
      rec["Children"]["A"] = "condeq1";
    DataRecord& recs = rec["Solvable"] <<= new DataRecord;
    DataField& dfld = recs["Command.By.List"] <<= new DataField(TpDataRecord,2);
      dfld[0]["Name"] = "p2";
      dfld[0]["State"] <<= new DataRecord;
      dfld[0]["State"]["Solvable"] = true;
      // wildcard: not solvable
      dfld[1]["State"] <<= new DataRecord;
      dfld[1]["State"]["Solvable"] = false;
    int index_solv;
    Node& chsolv = forest.create(index_solv,rec);
    
    cout << "============ resolving children on add =========\n";
    chsolv.resolveChildren();
    
    for (int i=0; i<3; i++) {
      cout << "============ getting result " << i << " =========\n";
      Domain domain(1,4, -2,3);
      Request::Ref reqref;
      Request &req = reqref <<= new Request(new Cells(domain, 4, 4));
      ///      if (i == 1) {
	///	req.setNumSteps(0);
	///      } else if (i == 2) {
	///	req.setClearSolver(true);
	///      }
      Result::Ref refres;
      child1.execute(refres, req);
      cout << "p1 before " << refres->vellSet(0) << endl;
      child2.execute(refres, req);
      cout << "p2 before " << refres->vellSet(0) << endl;

      int flag = chsolv.execute(refres, req);
      cout << flag << endl;
      cout << "solver " << refres->vellSet(0) << endl;
      if( refres->hasFails() )
	return 1;
      child1.execute(refres, req);
      cout << "p1 after  " << refres->vellSet(0) << endl;
      child2.execute(refres, req);
      cout << "p2 after  " << refres->vellSet(0) << endl;
    }
  } 
  catch (std::exception& x) 
  {
    cout << "Caught exception: " << x.what() << endl;
    return 1;
  }
  cout << "OK" << endl;
  return 0;
}

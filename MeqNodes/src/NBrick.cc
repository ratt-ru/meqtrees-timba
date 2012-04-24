//# NBrick.cc: computes the n coordinate corresponding to an FFT or image brick
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
//# $Id: NBrick.cc 7532 2010-02-17 00:05:05Z oms $

#include <MeqNodes/NBrick.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
#include <MEQ/Axis.h>
#include <MEQ/VellsSlicer.h>

namespace Meq {

const HIID FAxesIn = AidAxes|AidIn;
  
  
NBrick::NBrick()
  : Node(1)     // exactly 1 child expected
{
  _in_axis_id.resize(2);
  _in_axis_id[0] = "U";
  _in_axis_id[1] = "V";
  Axis::addAxis("U");
  Axis::addAxis("V");
};

NBrick::~NBrick(){};

int NBrick::getResult (Result::Ref &resref,
			 const std::vector<Result::Ref> &child_results,
			 const Request &request,bool newreq)
{
  Assert(child_results.size()==1);
  const Result & childres = child_results.at(0);
  
  int uaxis = Axis::axis(_in_axis_id[0]);
  int vaxis = Axis::axis(_in_axis_id[1]);
  const Cells & cells = childres.cells();
  // get the u/v coordinates from the child result
  const LoVec_double uu = cells.center(uaxis);
  const LoVec_double vv = cells.center(vaxis);
 
  // output result has one N plane, and same cells as input
  Result & result = resref <<= new Result(1);
  result.setCells(cells);
  VellSet & vs = result.setNewVellSet(0);
  
  Vells::Ref nvells;
  // make output Vells of appropriate shape
  LoShape shape = Axis::matrixShape(uaxis,vaxis,uu.size(),vv.size());
  nvells <<= new Vells(0.,shape,false);
  
  // fill output vells
  
  
  
  
  
  // put it in result
  vs.setValue(nvells);
  // this will throw an exception if something was done wrong above
  vs.verifyShape();

  return 0;
};

void NBrick::setStateImpl (DMI::Record::Ref& rec, bool initializing)
{
  Node::setStateImpl(rec,initializing);
  std::vector<HIID> in = _in_axis_id;
  if( rec[FAxesIn].get_vector(in,initializing) || initializing )
  {
    FailWhen(in.size()!=2,FAxesIn.toString()+" field must have 2 elements");
    _in_axis_id = in;
    Axis::addAxis(_in_axis_id[0]);
    Axis::addAxis(_in_axis_id[1]);
  }
};
  
} // namespace Meq

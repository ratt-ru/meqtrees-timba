//# Subtract.cc: TFSmearFactor 2 or more nodes
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
//# $Id: TFSmearFactor.cc 5418 2007-07-19 16:49:13Z oms $

#include <MeqNodes/TFSmearFactor.h>
#include <blitz/array/stencilops.h>

namespace Meq {    


//##ModelId=400E5355029C
TFSmearFactor::TFSmearFactor()
 : Function(2) // two children expected
{}

//##ModelId=400E5355029D
TFSmearFactor::~TFSmearFactor()
{}

using namespace blitz;
using namespace VellsMath;

BZ_DECLARE_STENCIL2(TimeDiff, A,B)
    A = .5*central12(B,blitz::firstDim);
BZ_END_STENCIL
BZ_DECLARE_STENCIL2(TimeDiff1,A,B)
    A = forward11(B,blitz::firstDim);
BZ_END_STENCIL
BZ_DECLARE_STENCIL2(TimeDiff2,A,B)
    A = backward11(B,blitz::firstDim);
BZ_END_STENCIL
BZ_DECLARE_STENCIL2(FreqDiff, A,B)
    A = .5*central12(B,blitz::secondDim);
BZ_END_STENCIL
BZ_DECLARE_STENCIL2(FreqDiff1,A,B)
    A = forward11(B,blitz::secondDim);
BZ_END_STENCIL
BZ_DECLARE_STENCIL2(FreqDiff2,A,B)
    A = backward11(B,blitz::secondDim);
BZ_END_STENCIL


//##ModelId=400E535502A1
Vells TFSmearFactor::evaluate (const Request&,const LoShape &,
			  const vector<const Vells*>& values)
{
  Assert(values.size() == 2 );
  Vells argvells = ((*values[0]) - (*values[1]))/2;
  const blitz::Array<double,2> &arg = argvells.as<double,2>();
  int nt = arg.extent(0);
  int nf = arg.extent(1);
  Vells dfreq(0.,arg.shape()),dtime(0.,arg.shape());
  // apply stencil in time, to get differences over the cells
  blitz::Array<double,2> dtime_2 = dtime.as<double,2>();
  blitz::Array<double,2> dtime_2_row0 = dtime_2(LoRange(0,1),LoRange::all());
  blitz::Array<double,2> arg_row0 = arg(LoRange(0,1),LoRange::all());
  blitz::applyStencil(TimeDiff1(),dtime_2_row0,arg_row0);
  blitz::Array<double,2> dtime_2_row1 = dtime_2(LoRange(nt-2,nt-1),LoRange::all());
  blitz::Array<double,2> arg_row1 = arg(LoRange(nt-2,nt-1),LoRange::all());
  blitz::applyStencil(TimeDiff2(),dtime_2_row1,arg_row1);
  blitz::applyStencil(TimeDiff(),dtime_2,arg);
  // now apply stencil in freq
  blitz::Array<double,2> dfreq_2 = dfreq.as<double,2>();
  blitz::Array<double,2> dfreq_2_col0 = dfreq_2(LoRange::all(),LoRange(0,1));
  blitz::Array<double,2> arg_col0 = arg(LoRange::all(),LoRange(0,1));
  blitz::applyStencil(FreqDiff1(),dfreq_2_col0,arg_col0);
  blitz::Array<double,2> dfreq_2_col1 = dfreq_2(LoRange::all(),LoRange(nf-2,nf-1));
  blitz::Array<double,2> arg_col1 = arg(LoRange::all(),LoRange(nf-2,nf-1));
  blitz::applyStencil(FreqDiff2(),dfreq_2_col1,arg_col1);
  blitz::applyStencil(FreqDiff(),dfreq_2,arg);
  // take sines and compute smearing factors
  return sin(dfreq)*sin(dtime)/(dfreq*dtime);
}


} // namespace Meq

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
#include <cmath>
#include <MeqNodes/TFSmearFactor.h>
#include <casa/BasicSL/Constants.h>

namespace Meq {

const HIID FModulo = AidModulo;
const HIID FPhaseFactor = "Phase.Factor";

//##ModelId=400E5355029C
TFSmearFactor::TFSmearFactor()
 : TensorFunction(2,0,1), narrow_band_limit_(0.05) // one or two children expected
{}

//##ModelId=400E5355029D
TFSmearFactor::~TFSmearFactor()
{}

//##ModelId=400E53550233
void TFSmearFactor::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);
  rec[AidNarrow|AidBand|AidLimit].get(narrow_band_limit_,initializing);
}

const LoShape shape_2vec(2);

LoShape TFSmearFactor::getResultDims (const vector<const LoShape *> &input_dims)
{
  for( uint i=0; i<input_dims.size(); i++ )
  {
    FailWhen((*input_dims[i]) != shape_2vec,
              ssprintf("child %d: 2-vector expected",i));
  }
  // result is a scalar
  return LoShape();
}

void TFSmearFactor::computeResultCells (Cells::Ref &ref,
        const std::vector<Result::Ref> &childres,const Request &request)
{
  TensorFunction::computeResultCells(ref,childres,request);
  const Cells & cells = *ref;
  if( cells.isDefined(Axis::FREQ) )
  {
    int nfreq = cells.ncells(Axis::FREQ);
    // set up frequency vells
    const Domain &dom = cells.domain();
    double freq0 = dom.start(Axis::FREQ);
    double freq1 = dom.end(Axis::FREQ);
    double midfreq = (freq0+freq1)/2;
    // narrow-band: use effectively a single frequency
    if( abs(freq0-freq1)/midfreq < narrow_band_limit_ )
    {
      narrow_band_ = true;
      freq_vells_ = midfreq;
    }
    else
    {
      freq_vells_ = Vells(0,Axis::freqVector(nfreq),false);
      memcpy(freq_vells_.realStorage(),cells.center(Axis::FREQ).data(),nfreq*sizeof(double));
    }
    // set up delta-freq/2 vells
    if( cells.numSegments(Axis::FREQ)<2 )
      dfreq2_vells_ = cells.cellSize(Axis::FREQ)(0)/2;
    else
    {
      dfreq2_vells_ = Vells(0,Axis::freqVector(nfreq),false);
      memcpy(dfreq2_vells_.realStorage(),cells.cellSize(Axis::FREQ).data(),nfreq*sizeof(double));
      dfreq2_vells_ /= 2;
    }
  }
  else
    freq_vells_ = dfreq2_vells_ = 0;
  // set up delta-time/2 vells
  if( cells.isDefined(Axis::TIME) )
  {
    int ntime = cells.ncells(Axis::TIME);
    if( cells.numSegments(Axis::TIME)<2 )
      dtime2_vells_ = cells.cellSize(Axis::TIME)(0)/2;
    else
    {
      dtime2_vells_ = Vells(0,Axis::timeVector(ntime),false);
      memcpy(dtime2_vells_.realStorage(),cells.cellSize(Axis::TIME).data(),ntime*sizeof(double));
      dtime2_vells_ /= 2;
    }
  }
  else
    dtime2_vells_ = 0;
}

using namespace VellsMath;

void TFSmearFactor::evaluateTensors (std::vector<Vells> & out,
                                     const std::vector<std::vector<const Vells *> > &args )
{
  Vells p = (*args[0][0]);
  Vells dp = (*args[0][1]);
  // with two arguments, subtract second
  if( args.size() == 2 )
  {
    p  -= (*args[1][0]);
    dp -= (*args[1][1]);
  }
  const double _2pi_over_c = -casa::C::_2pi / casa::C::c;

  Vells dphi = _2pi_over_c * freq_vells_ * dp * dtime2_vells_;
  Vells dpsi = _2pi_over_c * p * dfreq2_vells_;
  
  Vells prod1 = sin(dphi)/dphi;
  Vells prod2 = sin(dpsi)/dpsi;
  
  prod1.replaceFlaggedValues(dphi.whereEq(0.),1.);
  prod2.replaceFlaggedValues(dpsi.whereEq(0.),1.);
  
  out[0] = prod1*prod2;
}



} // namespace Meq

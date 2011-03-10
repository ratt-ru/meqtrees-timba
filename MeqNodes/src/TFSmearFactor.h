//# TFSmearFactor.h: apply bandwidth/time smearing
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
//# $Id: TFSmearFactor.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQNODES_TFSMEARFACTOR_H
#define MEQNODES_TFSMEARFACTOR_H

#include <MEQ/TensorFunction.h>

#include <MeqNodes/AID-MeqNodes.h>
#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::TFSmearFactor
#pragma aid Narrow Band Limit

namespace Meq {


//##ModelId=400E530400A3
class TFSmearFactor : public TensorFunction
{
public:
    //##ModelId=400E5355029C
  TFSmearFactor();

    //##ModelId=400E5355029D
  virtual ~TFSmearFactor();

  //##ModelId=400E5355029F
  virtual TypeId objectType() const
  { return TpMeqTFSmearFactor; }

protected:
  virtual void computeResultCells (Cells::Ref &ref,
          const std::vector<Result::Ref> &childres,const Request &request);

  // method required by TensorFunction
  // Returns shape of result.
  // Also check child results for consistency
  virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);

  // method required by TensorFunction
  // Evaluates for a given set of children values
  virtual void evaluateTensors (std::vector<Vells> & out,
                                const std::vector<std::vector<const Vells *> > &args);

  void setStateImpl (DMI::Record::Ref &rec,bool initializing);


  // fractional bandwidth over this limit will be considered "wide",
  // and a per-frequency calculation will be done. Below this limit, one value
  // of frequency will be used.
  double narrow_band_limit_;

  // flag: using narrow-band approximation
  bool narrow_band_;

  // cached delta-time/2, delta-freq/2 and freq vells, set up once in computeResultCells.
  Vells dtime2_vells_,freq_vells_,dfreq2_vells_;
};


} // namespace Meq

#endif

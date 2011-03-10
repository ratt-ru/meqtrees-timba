//# UVW.h: Calculate station UVW from station position and phase center
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

#ifndef MEQNODES_UVW_H
#define MEQNODES_UVW_H

#include <MEQ/TensorFunction.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::UVW
#pragma aid RADec XYZ Include Deriv

namespace Meq {

//defrec begin MeqUVW
//  Computes UVWs, given a station position and an observing direction
//field: include_deriv False
//  If False, only computes u,v,w, returns a 3-vector.
//  If True, computes du/dt,dv/dt,dw/dt as well. Returns (2,3) matrix.
//defrec end



class UVW : public TensorFunction
{
public:
  UVW();

  virtual ~UVW();

  virtual TypeId objectType() const
    { return TpMeqUVW; }

protected:
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  // method required by TensorFunction
  // Returns cells of result.
  // This version just uses the time axis.
  virtual void computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request);

  // method required by TensorFunction
  // Returns shape of result.
  // Also check child results for consistency
  virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);

  // method required by TensorFunction
  // Evaluates UVW for a given set of children values
  virtual void evaluateTensors (std::vector<Vells> & out,
       const std::vector<std::vector<const Vells *> > &args );

  bool include_derivatives_;
};

} // namespace Meq

#endif

//# PSVTensor.h: The point source DFT component for a station
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
//# $Id: PSVTensor.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQNODES_PSVTENSOR_H
#define MEQNODES_PSVTENSOR_H

//# Includes
#include <MEQ/TensorFunctionPert.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::PSVTensor

#pragma aid LMN B UVW N Minus Narrow Band Limit

namespace Meq {    

class IntermediateMatrix;
    
class PSVTensor: public TensorFunctionPert
{
public:
  //! The default constructor.
  PSVTensor();

  virtual ~PSVTensor();

  virtual TypeId objectType() const
    { return TpMeqPSVTensor; }

  // this is for the cdebug() mechanism
  LocalDebugContext;
  

protected:
  void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  void computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request);
  
  // method required by TensorFunction
  // Returns shape of result.
  // Also check child results for consistency
  virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);
  
  // method required by TensorFunctionPert
  virtual void evaluateTensors (Result &out,int nchildren,int nperts);
       
  // helper functions to compute the K-Jones exponent and the smeraing term
  Vells computeExponent (const Vells &p,const Cells &cells);
  Vells computeSmearingTerm (const Vells &p,const Vells &dp);
  
  // virtual method to compute the shape function (as a visibility scaling term)
  // Should return true if function was recomputed for this perturbation,
  // or false if the main value (ipert==0) is to be reused. For ipert==0, should return true always.
  virtual bool computeShapeTerm (Vells &shape,int isrc,int ipert,int npert,int nchildren);

  // Helper function. Checks that shape is scalar (N=1) or [N] or Nx1 or Nx1x1 or Nx2x2, throws exception otherwise
  // Also checks that N==nsrc.
  void checkTensorDims (int ichild,const LoShape &shape,int nsrc);

  friend class IntermediateMatrix;                                          
  
  int num_sources_;
  
  // fractional bandwidth over this limit will be considered "wide",
  // and a per-frequency calculation will be done. Below this limit, one value
  // of frequency will be used.
  double narrow_band_limit_;

  // frequency vells
  Vells freq_vells_;
  // cached values used in smearing calculations
  Vells df_over_2_,f_dt_over_2_;  // delta_freq/2, and freq*delta_time/2
  
  // subtracted from n -- set to 1 to use fringe-stopped phases, i.e. w(n-1)
  double n_minus_;

  // number of the first Jones child. Set to 3 in this class, but subclasses may change this
  int first_jones_;

};

} // namespace Meq

#endif

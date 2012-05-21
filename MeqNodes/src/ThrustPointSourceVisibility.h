//# ThrustPointSourceVisibility.h: The point source DFT component for a station
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
//# $Id: ThrustPointSourceVisibility.h 5418 2007-07-19 16:49:13Z oms $

//The following lines are commented out so that this node is excluded when libmeqnodes is linked during a build.
//#ifndef MEQNODES_THRUSTPOINTSOURCEVISIBILITY_H
//#define MEQNODES_THRUSTPOINTSOURCEVISIBILITY_H

//# Includes
#include <MEQ/TensorFunction.h>


#include <MeqNodes/TID-MeqNodes.h>
//The following lines are commented out so that this node is excluded when libmeqnodes is linked during a build.
//#pragma aidgroup MeqNodes
//#pragma types #Meq::ThrustPointSourceVisibility

#ifndef STRIP_CUDA
#include <cuda_runtime.h>

#include <thrust/host_vector.h>
#include <thrust/device_vector.h>
#endif



namespace Meq {    

#ifndef STRIP_CUDA
std::string runCUDAPointSourceVisibilityThrust(int nsrcs,
                                               int nfreq,
                                               int ntime,
                                               thrust::device_vector<double>& d_freq,
                                               thrust::device_vector<double>& d_u,
                                               thrust::device_vector<double>& d_v,
                                               thrust::device_vector<double>& d_w,
                                               //thrust::device_vector<double3>& d_lmn,
                                               thrust::device_vector<double>& d_l,
                                               thrust::device_vector<double>& d_m,
                                               thrust::device_vector<double>& d_n,
                                               thrust::device_vector<double2>& d_b,
                                               thrust::host_vector<double2>& h_output, 
                                               double _2pi_over_c);
#endif

class ThrustPointSourceVisibility: public TensorFunction
{
public:
  //! The default constructor.
  ThrustPointSourceVisibility();

  virtual ~ThrustPointSourceVisibility();

  virtual TypeId objectType() const
    { return TpMeqThrustPointSourceVisibility; }

  // this is for the cdebug() mechanism
  LocalDebugContext;

protected:
  // method required by TensorFunction
  // Returns shape of result.
  // Also check child results for consistency
  virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);
    
  // method required by TensorFunction
  // Evaluates for a given set of children values
  virtual void evaluateTensors (std::vector<Vells> & out,   
       const std::vector<std::vector<const Vells *> > &args);
       


  int num_sources_;
    int uvw_size_; // 1 or 2  (..x3)
       
};

} // namespace Meq

#endif

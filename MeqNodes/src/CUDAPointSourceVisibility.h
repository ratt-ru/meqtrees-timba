//# CUDAPointSourceVisibility.h: The point source DFT component for a station
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
//# $Id: CUDAPointSourceVisibility.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQNODES_CUDAPOINTSOURCEVISIBILITY_H
#define MEQNODES_CUDAPOINTSOURCEVISIBILITY_H

//# Includes
#include <MEQ/TensorFunction.h>




#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::CUDAPointSourceVisibility
#pragma aid LMN UVW B

#include <cuda_runtime.h>

#include <MeqNodes/CUDAPointSourceVisibilityCommon.h>

namespace Meq {    

// CUDA kernel and runner function
void CUDAPointSourceVisibilityKernel();

#ifndef STRIP_CUDA
std::string runCUDAPointSourceVisibilityKernel(lmn_t* d_lmn, 
                                               double2* d_B_complex, 
                                               int nsrcs, 
                                               int nslots,
                                               int nsrcs_per_slot, // nslot == number of threads in x direction (src direction)
                                               int nslots_per_run,
                                               double* d_uvw, 
                                               double* d_duvw, 
                                               double* d_time, 
                                               int ntime, 
                                               double* d_freq, 
                                               int nfreq, 
                                               double* d_df_over_2, 
                                               double* d_f_dt_over_2,
                                               double2* d_intermediate_output_complex,
                                               double2* d_output_copmlex, 
                                               int nOutputElements,
                                               int NUM_MATRIX_ELEMENTS,
                                               double _2pi_over_c, 
                                               std::complex<double>** pout);
#endif

// int getMultiDimIndex(int a, int aT, int b, int bT, int c, int cT, int d, int dT, int e, int eT);
// int getMultiDimIndex(int a, int aT, int b, int bT, int c, int cT, int d, int dT);
// int getMultiDimIndex(int a, int aT, int b, int bT, int c, int cT);


int get_B_index(int s, int nsrcs, 
                int f, int nfreq, 
                int j, int num_matrix_elements);


int get_intermediate_output_index(int s, int nsrcs, 
                                  int t, int ntime, 
                                  int f, int nfreq, 
                                  int j, int num_matrix_elements);

int get_output_index(int t, int ntime, 
                     int f, int nfreq, 
                     int j, int num_matrix_elements);


class CUDAPointSourceVisibility: public TensorFunction
{
public:
    //! The default constructor.
    CUDAPointSourceVisibility();

    virtual ~CUDAPointSourceVisibility();

    virtual TypeId objectType() const
        { return TpMeqCUDAPointSourceVisibility; }

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
       
    double*  d_uvw; // time
    //double*  d_v; // time
    //double*  d_w; // time
    double*  d_duvw; // time
    //double*  d_dv; // time
    //double*  d_dw; // time
    double*  d_df_over_2; // time
    double*  d_f_dt_over_2; // freq
    lmn_t*   d_lmn; // src
    double*  d_freqCellSize; // freq
    double*  d_timeCellSize; // time
    double2* d_B_complex; // src*4*freq
    double*  d_freq; // freq
    double*  d_time; // time
    double2* d_intermediate_output_complex; // src_per_run*time*freq*4
    double2* d_output_complex;

    virtual void doCUDACleanUp();


    int num_sources_;
       
};

} // namespace Meq

#endif

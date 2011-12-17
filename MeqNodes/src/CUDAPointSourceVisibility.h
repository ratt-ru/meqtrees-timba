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
#pragma aid LMN UVW B N Minus Narrow Band Limit Shape Fixed Time Smearing Interval

#ifndef STRIP_CUDA
#include <cuda_runtime.h>
#endif

#include <MeqNodes/CUDAPointSourceVisibilityCommon.h>

namespace Meq {    

#ifndef STRIP_CUDA
struct CUDAMultiDimentionArray {
  
    int srcs_dims;
    int matj_dims;
    int time_dims;
    int freq_dims;

    int srcs_total;
    int matj_total;
    int time_total;
    int freq_total;
    
    std::string name;
    void* device_ptr;
    size_t type_size;


    CUDAMultiDimentionArray(
        const std::string n = "",
        int sd = 0, int md = 0, int td = 0, int fd = 0,
        int st = 0, int mt = 0, int tt = 0, int ft = 0,
        int ts = 0);

    ~CUDAMultiDimentionArray();

    std::string CUDAMemSet();
    std::string CUDAMemAlloc();
    std::string CUDAMemCopy(const void* host_ptr, int element_size = 0, int device_element_offset = 0);

    int getNumElements();

    int getMallocSize();

    void printInfo();
    
};

// CUDA kernel and runner function
void CUDAPointSourceVisibilityKernel();

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
                                               double* d_e_jones,
                                               double* d_e_jones_h,
                                               double2* d_intermediate_output_complex,
                                               double2* d_output_copmlex, 
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


int get_sf_jones_index(int s, int nsrcs, 
                       int f, int nfreq);



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
    
    // method required by TensorFunctionPert
    // virtual void evaluateTensors (Result &out,int nchildren,int nperts);

    // method required by TensorFunction
    // Evaluates for a given set of children values
    virtual void evaluateTensors (std::vector<Vells> & out,   
                                  const std::vector<std::vector<const Vells *> > &args);
       
    // Helper function. Checks that shape is scalar (N=1) or [N] or Nx1 or Nx1x1 or Nx2x2, throws exception otherwise
    // Also checks that N==nsrc.
    void checkTensorDims (int ichild,const LoShape &shape,int nsrc);

    int num_sources_;

    // fractional bandwidth over this limit will be considered "wide",
    // and a per-frequency calculation will be done. Below this limit, one value
    // of frequency will be used.
    double narrow_band_limit_;
  
    double time_smear_interval_;
    double freq_smear_interval_;

    // subtracted from n -- set to 1 to use fringe-stopped phases, i.e. w(n-1)
    double n_minus_;

    // number of the first Jones child. Set to 4 in this class, but subclasses may change this
    int first_jones_;
    
    // flag: we have a valid shape child
    bool have_shape_;
};

} // namespace Meq

#endif

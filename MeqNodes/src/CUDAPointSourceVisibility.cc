//# CUDAPointSourceVisibility.cc: The point source DFT component for a station
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
//# $Id: CUDAPointSourceVisibility.cc 8270 2011-07-06 12:17:23Z oms $


#include <MeqNodes/CUDAPointSourceVisibility.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/BasicSL/Constants.h>

#include <string>


namespace Meq {

InitDebugContext(CUDAPointSourceVisibility,"CUDAPSV");
    
    
using namespace VellsMath;

const HIID child_labels[] = { AidLMN,AidB,AidUVW };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);



CUDAPointSourceVisibility::CUDAPointSourceVisibility()
    : TensorFunction(num_children,child_labels)
{
    // dependence on frequency
    const HIID symdeps[] = { AidDomain,AidResolution };
    setActiveSymDeps(symdeps,2);
}

CUDAPointSourceVisibility::~CUDAPointSourceVisibility()
{}

const LoShape shape_3vec(3),shape_2x3(2,3);

LoShape CUDAPointSourceVisibility::getResultDims (const vector<const LoShape *> &input_dims)
{
    // this gets called to check that the child results have the right shape
    const LoShape &lmn = *input_dims[0], &b = *input_dims[1], &uvw = *input_dims[2];
  
    // the first child (LMN) is expected to be of shape Nx3, the second (B) of Nx2x2, and the third (UVW) is a 3-vector or 2x3-vector (UVW + dUVW) if the smear factor is to be calculated
    FailWhen(lmn.size()!=2 || lmn[1]!=3,"child '"+child_labels[0].toString()+"': an Nx3 result expected");
    FailWhen(b.size()!=3 || b[1]!=2 || b[2]!=2,"child '"+child_labels[1].toString()+"': an Nx2x2 result expected");
    FailWhen(lmn[0] != b[0],"shape mismatch between child '"+
             child_labels[0].toString()+"' and '"+child_labels[1].toString()+"'");
    //cdebug(0) << "uvw size " << uvw.size() << endl;

    FailWhen(uvw != shape_2x3 && uvw == LoShape(3),"child '"+child_labels[2].toString()+"': a 2x3 or 1x3 result expected");


    num_sources_ = lmn[0];
    // result is a 2x2 matrix 
    return LoShape(2,2);
}



#ifdef STRIP_CUDA
void CUDAPointSourceVisibility::evaluateTensors (std::vector<Vells> & out,
                                                 const std::vector<std::vector<const Vells *> > &args )
{
   
    FailWhen(true,"CUDA required in order to use this node"); 
}

void CUDAPointSourceVisibility::doCUDACleanUp(){
}

#else
void CUDAPointSourceVisibility::evaluateTensors (std::vector<Vells> & out,
                                                 const std::vector<std::vector<const Vells *> > &args )
{
    // cells
    const Cells & cells = resultCells();
    const double _2pi_over_c = -casa::C::_2pi / casa::C::c;
    // the frequency and time axis
    int nfreq = cells.ncells(Axis::FREQ);
    int ntime = cells.ncells(Axis::TIME);
    // TODO HACK HELP why does this fail when you request a timeslot size of > 8 !?!?!?!?!?!?1 
    const double * freq_data = cells.center(Axis::FREQ).data();
    const double * freq_cellSize = cells.cellSize(Axis::FREQ).data();
    const double * time_data = cells.center(Axis::TIME).data();
    const double * time_cellSize = cells.cellSize(Axis::TIME).data();
  
    LoShape timeshape = Axis::timeVector(ntime);
    LoShape freqshape = Axis::freqVector(nfreq);
    LoShape timefreqshape = Axis::freqTimeMatrix(nfreq,ntime);
  
    // uvw coordinates are the same for all sources, and each had better be a 'timeshape' vector
    const Vells & vu = *(args[2][0]);
    const Vells & vv = *(args[2][1]);
    const Vells & vw = *(args[2][2]);
    FailWhen(vu.shape() != timeshape || vv.shape() != timeshape || vw.shape() != timeshape,"expecting UVWs that are a vector in time");

    bool computeError = false;
    if( args[2].size() == 6 )
        computeError = true;

    cdebug(0) << "args[2].size() = " << args[2].size() << endl;

    const double *pu = NULL;
    const double *pv = NULL;
    const double *pw = NULL;
    const double *pdu = NULL;
    const double *pdv = NULL;
    const double *pdw = NULL;

    vector<double> vec_df_over_2_(nfreq);
    vector<double> vec_f_dt_over_2_(ntime);


    // these will be vectors of ntime points each
    pu = vu.realStorage();
    pv = vv.realStorage();
    pw = vw.realStorage();

    double narrow_band_limit_ = .05;

    Vells df_over_2_,f_dt_over_2_;  // delta_freq/2, and freq*delta_time/2
    Vells freq_vells_;
    Vells freq_approx;

    if (computeError) {
        const Vells & dvu = *(args[2][3]);
        const Vells & dvv = *(args[2][4]);
        const Vells & dvw = *(args[2][5]);
        FailWhen(dvu.shape() != timeshape || dvv.shape() != timeshape || dvw.shape() != timeshape,"expecting UVWs derivatives that are a vector in time");

        //TODO implement smearing



        //==================================================================================================
        // just copied this from PSVTensor.cc
    
        if( cells.isDefined(Axis::FREQ) )
        {
            // set up frequency vells
            freq_vells_ = Vells(0,Axis::freqVector(nfreq),false);
            memcpy(freq_vells_.realStorage(),cells.center(Axis::FREQ).data(),nfreq*sizeof(double));
            // In the narrow-band case, use a single frequency for smearing calculations
            // (to speed up things)
            const Domain &dom = cells.domain();
            double freq0 = dom.start(Axis::FREQ);
            double freq1 = dom.end(Axis::FREQ);
            double midfreq = (freq0+freq1)/2;
            // narrow-band: use effectively a single frequency
            if( ::abs(freq0-freq1)/midfreq < narrow_band_limit_ )
                freq_approx = midfreq;
            else
                freq_approx = freq_vells_;
            // set up delta-freq/2 vells
            if( cells.numSegments(Axis::FREQ)<2 )
                df_over_2_ = cells.cellSize(Axis::FREQ)(0)/2;
            else
            {
                df_over_2_ = Vells(0,Axis::freqVector(nfreq),false);
                memcpy(df_over_2_.realStorage(),cells.cellSize(Axis::FREQ).data(),nfreq*sizeof(double));
                df_over_2_ /= 2;
            }
        }
        else
            freq_vells_ = freq_approx = df_over_2_ = 0;
        // set up delta-time/2 vells
        if( cells.isDefined(Axis::TIME) )
        {
            if( cells.numSegments(Axis::TIME)<2 )
                f_dt_over_2_ = cells.cellSize(Axis::TIME)(0)/2;
            else
            {
                f_dt_over_2_ = Vells(0,Axis::timeVector(ntime),false);
                memcpy(f_dt_over_2_.realStorage(),cells.cellSize(Axis::TIME).data(),ntime*sizeof(double));
                f_dt_over_2_ /= 2;
            }
            f_dt_over_2_ *= freq_approx;
        }
        else
            f_dt_over_2_ = 0;


        pdu = dvu.realStorage();
        pdv = dvv.realStorage();
        pdw = dvw.realStorage();

        if (df_over_2_.isScalar()) {
            for (int f = 0 ; f < nfreq ; f++) {
                vec_df_over_2_[f] = df_over_2_.as<double>();
            }
        }
        else {
            const double* pdf_over_2_ = df_over_2_.realStorage();
            for (int f = 0 ; f < nfreq ; f++) {
                vec_df_over_2_[f] = pdf_over_2_[f];
            }
        }

        if (f_dt_over_2_.isScalar()) {
            for (int t = 0 ; t < ntime ; t++) {
                vec_f_dt_over_2_[t] = f_dt_over_2_.as<double>();
            }
        }
        else {

            const double* pf_dt_over_2_ = f_dt_over_2_.realStorage();
            for (int t = 0 ; t < ntime ; t++) {
                vec_f_dt_over_2_[t] = f_dt_over_2_[t];
            }
        }
           
    }


    //==================================================================================================

  
    // allocate storage for results, and get pointers to storage
    const int NUM_MATRIX_ELEMENTS = 4;
    dcomplex * pout[NUM_MATRIX_ELEMENTS];


    for( int j=0; j<NUM_MATRIX_ELEMENTS; j++ )
    {
        out[j] = Vells(numeric_zero<dcomplex>(),timefreqshape);
        pout[j] = out[j].complexStorage();
        // pout[j] points to an NTIME x NFREQ array
    }

    int nsrcs = num_sources_; // I just prefer this name to num_sources_


    //==================================================================================================
    // CUDA bit


    d_uvw = NULL;
    d_duvw = NULL;
    d_df_over_2 = NULL;
    d_f_dt_over_2 = NULL;
    d_lmn = NULL;
    d_freqCellSize = NULL;
    d_timeCellSize = NULL;
    d_B_complex = NULL;
    d_freq = NULL;
    d_time = NULL;
    d_intermediate_output_complex = NULL;
    d_output_complex = NULL;

    int nsrcs_per_slot = 1;
#ifdef MULTI_SRC_PER_THREAD
    nsrcs_per_slot = SRC_PER_THREAD;
#endif

    unsigned int nOutputElements = ntime * nfreq * NUM_MATRIX_ELEMENTS;


    std::string errorString = "";

    size_t avail;
    size_t total;
    cudaMemGetInfo( &avail, &total );
    size_t used = total - avail;

    
    int extra_input = 0;
    if (computeError) {
        extra_input = sizeof(double)*((ntime*3) + (nfreq) + (ntime));
    }

    size_t will_use_input = (sizeof(lmn_t)*nsrcs)+(sizeof(double)*((ntime*3) + (nfreq*2) + (ntime*2))) + (sizeof(double2)*nsrcs*NUM_MATRIX_ELEMENTS*nfreq) + extra_input;

    size_t will_use_output = sizeof(double2)*nOutputElements;

    int memory_to_remain_free = 32*1024*1024;

    int nslots_required = ((nsrcs-1)/nsrcs_per_slot)+1;

    size_t remaining_for_intermediate = avail-will_use_input-will_use_output-memory_to_remain_free;
    int nslots_per_run = ((remaining_for_intermediate-1)/will_use_output) + 1;
    if (nslots_per_run > nslots_required)
        nslots_per_run = nslots_required;

    if (nslots_per_run == 0)
        nslots_per_run = 1;

    
    unsigned int nIntermediateElements = nslots_per_run * ntime * nfreq * NUM_MATRIX_ELEMENTS; 
    
    size_t will_use_intermediate = sizeof(double2)*nIntermediateElements;
    size_t will_use_total = will_use_input + will_use_intermediate + will_use_output;


    if (computeError) {
    cdebug(0) << "required for inputs (" << sizeof(lmn_t) << "*" << nsrcs << ") + (" << sizeof(double) << "*((" << ntime << "*" << 6 << ") + (" << nfreq << "*" << 2 << ") + (" << ntime << "*" << 2 << ") + (" << nfreq << ") + (" << ntime << "))) + (" << sizeof(double2) << "*"<< nsrcs << "*" << NUM_MATRIX_ELEMENTS << "*" << nfreq << ") = " <<  will_use_input << " bytes" << endl; 
    }

    if (computeError) {
    cdebug(0) << "required for inputs (" << sizeof(lmn_t) << "*" << nsrcs << ") + (" << sizeof(double) << "*((" << ntime << "*" << 3 << ") + (" << nfreq << "*" << 2 << ") + (" << ntime << "*" << 2 << "))) + (" << sizeof(double2) << "*"<< nsrcs << "*" << NUM_MATRIX_ELEMENTS << "*" << nfreq << ") = " <<  will_use_input << " bytes" << endl; 
    }


    cdebug(0) << "required for output "<< sizeof(double2) <<"*(" <<ntime<<"*"<<nfreq<<"*"<<NUM_MATRIX_ELEMENTS << ") = "<< sizeof(double2) <<"*(" << nOutputElements << ") = " << will_use_output << endl;

    cdebug(0) << "after input and output there is " << remaining_for_intermediate << " bytes, 1 src/slot = " << will_use_output << " bytes, meaning " << nslots_per_run << "/" << nslots_required << " slots can be calculated per run (" << will_use_intermediate << " bytes)" << endl;

    cdebug(0) << "required for intermediate "<< sizeof(double2) <<"*(" << nslots_per_run <<"*"<<ntime<<"*"<<nfreq<<"*"<<NUM_MATRIX_ELEMENTS << ") = " << will_use_intermediate << endl;


    cdebug(0) << "required for total "<< will_use_input << "+" << will_use_intermediate << "+" << will_use_output << " = " << will_use_total << endl;
    
    cdebug(0) << avail << " bytes available (available after = " << (avail-will_use_total)<<" bytes, " << memory_to_remain_free <<" bytes intentionally left free)" << endl;
    char errorChar [256];
    sprintf(errorChar, "Not enough memory on GPU device, requires %u bytes, only %u bytes available", will_use_total, avail);
    FailWhen(avail < will_use_total, errorChar);

    cdebug(0) << "alloc of d_uvw: size = "<< sizeof(double) <<"*" << ntime <<"*" <<3 << endl;
    if (errorString == "" && cudaMalloc((void **) &d_uvw,      sizeof(double)   * ntime*3) != cudaSuccess)
        errorString = "cudaMalloc error for d_uvw : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

    // if (errorString == "" && cudaMalloc((void **) &d_v,      sizeof(double)   * ntime) != cudaSuccess)
    //     errorString = "cudaMalloc error for d_v : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));

    // if (errorString == "" && cudaMalloc((void **) &d_w,      sizeof(double)   * ntime) != cudaSuccess)
    //     errorString =  "cudaMalloc error for d_w : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));
    // TODO, combine into 1 and use texture mem
    if (computeError) {
        cdebug(0) << "alloc of d_duvw: size = "<< sizeof(double) <<"*" << ntime <<"*" <<3 << endl;
        if (errorString == "" && cudaMalloc((void **) &d_duvw,      sizeof(double)   * ntime*3) != cudaSuccess)
            errorString = "cudaMalloc error for d_du : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

        // if (errorString == "" && cudaMalloc((void **) &d_dv,      sizeof(double)   * ntime) != cudaSuccess)
        //     errorString = "cudaMalloc error for d_dv : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));

        // if (errorString == "" && cudaMalloc((void **) &d_dw,      sizeof(double)   * ntime) != cudaSuccess)
        //     errorString =  "cudaMalloc error for d_dw : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));

        cdebug(0) << "alloc of d_df_over_2: size = "<< sizeof(double) <<"*" << nfreq << endl;
        if (errorString == "" && cudaMalloc((void **) &d_df_over_2,      sizeof(double)   * nfreq) != cudaSuccess)
            errorString =  "cudaMalloc error for d_df_over_2 : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));

        cdebug(0) << "alloc of d_f_dt_over_2: size = "<< sizeof(double) <<"*" << ntime << endl;
        if (errorString == "" && cudaMalloc((void **) &d_f_dt_over_2,      sizeof(double)   * ntime) != cudaSuccess)
            errorString =  "cudaMalloc error for d_f_dt_over_2 : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));
    }
    
    cdebug(0) << "alloc of d_lmn: size = "<< sizeof(lmn_t) <<"*" << nsrcs<< endl;
    if (errorString == "" && cudaMalloc((void **) &d_lmn,    sizeof(lmn_t)   * nsrcs) != cudaSuccess) 
        errorString =  "cudaMalloc error for d_lmn : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));

    if (errorString == "" && cudaMalloc((void **) &d_B_complex,      sizeof(double2) * nsrcs*NUM_MATRIX_ELEMENTS*nfreq) != cudaSuccess) 
        errorString =  "cudaMalloc error for d_B : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));


    cdebug(0) << "alloc of d_freq: size = "<< (sizeof(double) * nfreq ) << endl;
    if (errorString == "" && cudaMalloc((void **) &d_freq,     sizeof(double)   * nfreq) != cudaSuccess)
        errorString =  "cudaMalloc error for d_freq : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

    cdebug(0) << "alloc of d_time: size = "<< (sizeof(double) * ntime ) << endl;
    if (errorString == "" && cudaMalloc((void **) &d_time,     sizeof(double)   * ntime) != cudaSuccess) 
        errorString =  "cudaMalloc error for d_time : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

    if (errorString == "" && cudaMalloc((void **) &d_freqCellSize,    sizeof(double) * nfreq) != cudaSuccess) 
        errorString =  "cudaMalloc error for d_freqCellSize : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));

    if (errorString == "" && cudaMalloc((void **) &d_timeCellSize,    sizeof(double) * ntime) != cudaSuccess) 
        errorString =  "cudaMalloc error for d_timeCellSize : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));


    cdebug(0) << "alloc of d_intermediate_output_complex: size = "<< sizeof(double2) <<"*(" << nslots_per_run <<"*"<<ntime<<"*"<<nfreq<<")*"<<NUM_MATRIX_ELEMENTS << " = " << (sizeof(double2) * nIntermediateElements ) << endl;
    if (errorString == "" && cudaMalloc((void **) &d_intermediate_output_complex, sizeof(double2) * nIntermediateElements) != cudaSuccess)
        errorString =  "cudaMalloc error for d_intermediate_output : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

    cdebug(0) << "alloc of d_output_complex: size = "<< sizeof(double2) <<"*(" <<"*"<<ntime<<"*"<<nfreq<<")*"<<NUM_MATRIX_ELEMENTS << " = " << (sizeof(double2) * nOutputElements ) << endl;
    if (errorString == "" && cudaMalloc((void **) &d_output_complex, sizeof(double2) * nOutputElements) != cudaSuccess)
        errorString =  "cudaMalloc error for d_output : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

    if (errorString != ""){
        cdebug(0) << "error encountered: " << errorString << endl;
        doCUDACleanUp();
        cdebug(0) << "cleaned up" << endl;
        cdebug(0) << std::string(cudaGetErrorString (cudaGetLastError  ())) << endl;
        FailWhen(true, errorString);
    }
    cdebug(0) << "error string: " << errorString << endl;

    cudaMemGetInfo( &avail, &total );
    cdebug(0) << "d_uvw    " << d_uvw    << "  \t " << (void*)(sizeof(double) * ntime*3) << " (" << sizeof(double) * ntime *3 << ")" << endl;
    // cdebug(0) << "d_v    " << d_v    << "  \t " << (void*)(sizeof(double) * ntime) << " (" << (sizeof(double) * ntime)<< ")" << endl;
    // cdebug(0) << "d_w    " << d_w    << "  \t " << (void*)(sizeof(double) * ntime) << " (" << (sizeof(double) * ntime)<< ")" << endl;
    cdebug(0) << "d_suvw    " << d_duvw    << "  \t " << (void*)(sizeof(double) * ntime*3) << " (" << sizeof(double) * ntime *3 << ")" << endl;
   cdebug(0) << "d_lmn  " << d_lmn  << "  \t " << (void*)(sizeof(lmn_t) * nsrcs) << " (" << (sizeof(lmn_t) * nsrcs)<< ")" << endl;
   cdebug(0) << "d_B    " << d_B_complex << "  \t " << (void*)(sizeof(double2) * nsrcs*NUM_MATRIX_ELEMENTS*nfreq) << " (" << (sizeof(double2) * nsrcs*NUM_MATRIX_ELEMENTS*nfreq)<< ")" << endl;
   cdebug(0) << "d_freq " << d_freq << "  \t " << (void*)(sizeof(double) * nfreq)  << " (" << (sizeof(double) * nfreq)<< ")" << endl;
    cdebug(0) << "d_time " << d_time << "  \t " << (void*)(sizeof(double) * ntime)  << " (" << (sizeof(double) * ntime)<< ")" << endl;
    cdebug(0) << "d_f_cs " << d_freqCellSize << "  \t " << (void*)(sizeof(double) * nfreq)  << " (" << (sizeof(double) * nfreq)<< ")" << endl;
    cdebug(0) << "d_t_cs " << d_timeCellSize << "  \t " << (void*)(sizeof(double) * ntime)  << " (" << (sizeof(double) * ntime)<< ")" << endl;
    cdebug(0) << "d_i_o  " << d_intermediate_output_complex << "  \t " << (void*)(sizeof(double2) * nIntermediateElements)  << " (" <<(sizeof(double2) * nIntermediateElements) << ")" << endl;
    cdebug(0) << "d_o    " << d_output_complex << "  \t " << (void*)(sizeof(double2) * nOutputElements)  << " (" << (sizeof(double2) * nOutputElements)<< ")" << endl;
    cdebug(0) << "avail  " << avail  << "  \t " << (void*)(avail) << " (" << avail << ")" <<  endl;
    cdebug(0) << "total  " << total  << "  \t " << (void*)(total) << " (" << total << ")" <<  endl;


    //errorString = "force error";

    cdebug(0) << "copying uwv data to gpu device" << endl;

    cdebug(0) << "copying u data to gpu device" << endl;
    if (errorString == "" && cudaMemcpy(d_uvw, pu, sizeof(double)* ntime, cudaMemcpyHostToDevice) != cudaSuccess) 
        errorString = "Memcopy error copying data to d_u : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

    cdebug(0) << "copying v data to gpu device" << endl;
    if (errorString == "" && cudaMemcpy(&(d_uvw[ntime]), pv, sizeof(double)* ntime, cudaMemcpyHostToDevice) != cudaSuccess) 
        errorString = "Memcopy error copying data to d_v : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

    cdebug(0) << "copying w data to gpu device" << endl;
    if (errorString == "" && cudaMemcpy(&(d_uvw[ntime*2]), pw, sizeof(double)* ntime, cudaMemcpyHostToDevice) != cudaSuccess) 
        errorString = "Memcopy error copying data to d_w : " + std::string(cudaGetErrorString (cudaGetLastError  ()));


    if (computeError) {
        cdebug(0) << "copying du data to gpu device" << endl;
        if (errorString == "" && cudaMemcpy(d_duvw, pdu, sizeof(double)* ntime, cudaMemcpyHostToDevice) != cudaSuccess) 
            errorString = "Memcopy error copying data to d_du : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

        cdebug(0) << "copying dv data to gpu device" << endl;
        if (errorString == "" && cudaMemcpy(&(d_duvw[ntime]), pdv, sizeof(double)* ntime, cudaMemcpyHostToDevice) != cudaSuccess) 
            errorString = "Memcopy error copying data to d_dv : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

        cdebug(0) << "copying dw data to gpu device" << endl;
        if (errorString == "" && cudaMemcpy(&(d_duvw[ntime*2]), pdw, sizeof(double)* ntime, cudaMemcpyHostToDevice) != cudaSuccess) 
            errorString = "Memcopy error copying data to d_dw : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
    
        cdebug(0) << "copying d_df_over_2 data to gpu device" << endl;
        if (errorString == "" && cudaMemcpy(d_df_over_2, &(vec_df_over_2_[0]), sizeof(double)* nfreq, cudaMemcpyHostToDevice) != cudaSuccess) 
            errorString = "Memcopy error copying data to d_df_over_2 : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
    
        cdebug(0) << "copying d_f_dt_over_2 data to gpu device" << endl;
        if (errorString == "" && cudaMemcpy(d_f_dt_over_2, &(vec_f_dt_over_2_[0]), sizeof(double)* ntime, cudaMemcpyHostToDevice) != cudaSuccess) 
            errorString = "Memcopy error copying data to d_f_dt_over_2 : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
    }


    if (errorString != ""){
        doCUDACleanUp();
        cdebug(0) << std::string(cudaGetErrorString (cudaGetLastError  ())) << endl;
        FailWhen(true, errorString);
    }


    //cdebug(0) << "copying lmn and B data to arrays" << endl;
    std::vector<lmn_t> lmn_data(nsrcs); 
    std::vector<double2> b_data_complex(nsrcs*nfreq*NUM_MATRIX_ELEMENTS); 
    for( int isrc=0; isrc < nsrcs; isrc++ )
    {
        //cdebug(0) << "src number " << isrc<<"/"<<num_sources_ << endl;

        // get the LMNs for this source
        const Vells & vl = *(args[0][isrc*3]);
        const Vells & vm = *(args[0][isrc*3+1]);
        const Vells & vn = *(args[0][isrc*3+2]);
        if(!vl.isScalar() || !vm.isScalar() || !vn.isScalar()) {
            doCUDACleanUp();
            FailWhen(true, "expecting scalar LMNs");
        }
        double l = vl.as<double>();
        double m = vm.as<double>();
        double n = vn.as<double>();
          

        lmn_data[isrc].x = l;
        lmn_data[isrc].y = m;
        lmn_data[isrc].z = n;


        for( int j=0; j<NUM_MATRIX_ELEMENTS; j++ )
        {
            const Vells &b = *(args[1][isrc*NUM_MATRIX_ELEMENTS + j]);
            if(!b.isScalar() && b.shape() != freqshape) {
                doCUDACleanUp();
                FailWhen(true, "expecting B matrix elements that are either scalar, or a vector in frequency");
            }
            // for each element, either b.isScalar() is true and you can access it as b.as<double>, or
            // b.realStorage() is a vector of nfreq doubles.
    
            if( b.isNull() )
            {
                for (int f = 0 ; f < nfreq ; f++) {
                    
                    int b_i = get_B_index(isrc,  nsrcs,
                                          f,     nfreq,
                                          j,     NUM_MATRIX_ELEMENTS);

                    b_data_complex[b_i].x = 0;
                    b_data_complex[b_i].y = 0;

                }
            }
            else if (b.isScalar()) {

                dcomplex b_complex;
                if (b.isComplex()) {
                    b_complex = b.as<dcomplex>();
                }
                else {
                    b_complex = dcomplex(b.as<double>(), 0);
                }   

                for (int f = 0 ; f < nfreq ; f++) {

                    int b_i = get_B_index(isrc,  nsrcs,
                                          f,     nfreq,
                                          j,     NUM_MATRIX_ELEMENTS);

                    b_data_complex[b_i].x = b_complex.real();
                    b_data_complex[b_i].y = b_complex.imag();

                }
            }
            else { // is a vector of complex values
                const dcomplex* b_complex_vec = b.complexStorage();
                for (int f = 0 ; f < nfreq ; f++) {

                    int b_i = get_B_index(isrc,  nsrcs,
                                          f,     nfreq,
                                          j,     NUM_MATRIX_ELEMENTS);

                    b_data_complex[b_i].x = b_complex_vec[f].real();
                    b_data_complex[b_i].y = b_complex_vec[f].imag();
                }
            }

        }
    }



    cdebug(0) << "zeroing output data on device" << endl; 
    if (errorString == "" && cudaMemset(d_intermediate_output_complex, 0, nIntermediateElements * sizeof(double2)))
        errorString = "Memset error zeroing data in d_intermediate_output_complex : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
    if (errorString == "" && cudaMemset(d_output_complex, 0, nOutputElements * sizeof(double2)))
        errorString = "Memset error zeroing data in d_output_complex : " + std::string(cudaGetErrorString (cudaGetLastError  ()));

    cdebug(0) << "copying lmn data to gpu device" << endl;
    //cudaMemcpy(d_lmn, &(lmn_data[0]), sizeof(double)* nsrc*3, cudaMemcpyHostToDevice);
    if (errorString == "" && cudaMemcpy(d_lmn, &(lmn_data[0]), sizeof(lmn_t)* nsrcs, cudaMemcpyHostToDevice) != cudaSuccess) 
        errorString = "Memcopy error copying data to d_lmn : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
    cdebug(0) << std::string(cudaGetErrorString (cudaGetLastError  ())) << endl;

    cdebug(0) << "copying B data to gpu device" << endl;
    //cudaMemcpy(d_B, &(b_data_complex[0]), sizeof(double)* nsrc*NUM_MATRIX_ELEMENTS*nfreq, cudaMemcpyHostToDevice);
    if (errorString == "" && cudaMemcpy(d_B_complex, &(b_data_complex[0]), sizeof(double2)* nsrcs*NUM_MATRIX_ELEMENTS*nfreq, cudaMemcpyHostToDevice) != cudaSuccess) 
        errorString =  "Memcopy error copying data to d_B : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
    //cdebug(0) << std::string(cudaGetErrorString (cudaGetLastError  ())) << endl;

    cdebug(0) << "copying freq data to gpu device" << endl;
    if (errorString == "" && cudaMemcpy(d_freq, &(freq_data[0]), sizeof(double)* nfreq, cudaMemcpyHostToDevice) != cudaSuccess) 
        errorString =  "Memcopy error copying data to d_freq : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
    //cdebug(0) << std::string(cudaGetErrorString (cudaGetLastError  ())) << endl;

    // converting data to an array
    cdebug(0) << "copying time data to gpu device" << endl;
    if (errorString == "" && cudaMemcpy(d_time, &(time_data[0]), sizeof(double)* ntime, cudaMemcpyHostToDevice) != cudaSuccess) 
        errorString =  "Memcopy error copying data to d_time : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
    //cdebug(0) << std::string(cudaGetErrorString (cudaGetLastError  ())) << endl;
     
    
    
    if (errorString != ""){
        doCUDACleanUp();
        cdebug(0) << std::string(cudaGetErrorString (cudaGetLastError  ())) << endl;
        FailWhen(true, errorString);
    }

    // for (int i = 0 ; i < ntime ; i++) {
    //     cdebug(0) << i << " : " << time_data[i] << endl;
    // } 


    cdebug(0) << "total problem size " << nsrcs << "x" << ntime << "x" << nfreq << ", starting kernel runs" << endl;

    //std::string kernelErrorString;
    errorString = runCUDAPointSourceVisibilityKernel(d_lmn, 
                                                     d_B_complex, 
                                                     nsrcs,
                                                     nslots_required,
                                                     nsrcs_per_slot,
                                                     nslots_per_run,
                                                     d_uvw, 
                                                     d_duvw, 
                                                     d_time, 
                                                     ntime, 
                                                     d_freq, 
                                                     nfreq,
                                                     d_df_over_2, d_f_dt_over_2,
                                                     d_intermediate_output_complex,
                                                     d_output_complex, 
                                                     nOutputElements,
                                                     NUM_MATRIX_ELEMENTS,
                                                     _2pi_over_c,
                                                     pout);


    if (errorString != ""){
        doCUDACleanUp();
        cdebug(0) << std::string(cudaGetErrorString (cudaGetLastError  ())) << endl;
        FailWhen(true, errorString);
    }

    doCUDACleanUp();

    cdebug(0) << "ALL DONE =========================" << endl;

      

    //==================================================================================================

    // // CPU code
    // if (false) {
    //     // need to compute B*exp{ i*_2pi_over_c*freq*(u*l+v*m+w*n) } for every source, and sum over all sources
    //     for( int isrc=0; isrc < num_sources_; isrc++ )
    //     {
    //         cdebug(0) << "src number " << isrc<<"/"<<num_sources_ << endl;
    //         // get the LMNs for this source
    //         const Vells & vl = *(args[0][isrc*3]);
    //         const Vells & vm = *(args[0][isrc*3+1]);
    //         const Vells & vn = *(args[0][isrc*3+2]);
    //         FailWhen(!vl.isScalar() || !vm.isScalar() || !vn.isScalar(),"expecting scalar LMNs");
    //         double l = vl.as<double>();
    //         double m = vm.as<double>();
    //         double n = vn.as<double>();
    //         // get the B matrix elements -- there should be four of them
    //         for( int j=0; j<NUM_MARIX_ELEMENTS; j++ )
    //         {
    //             const Vells &b = *(args[1][isrc*NUM_MATRIX_ELEMENTS + j]);
    //             FailWhen(!b.isScalar() && b.shape() != freqshape,"expecting B matrix elements that are either scalar, or a vector in frequency");
    //             // for each element, either b.isScalar() is true and you can access it as b.as<double>, or
    //             // b.realStorage() is a vector of nfreq doubles.
      
    //             //...do the actual work...

    
    //             if (b.isScalar()) {

    //                 dcomplex b_complex;
    //                 if (b.isComplex()) {
    //                     b_complex = b.as<dcomplex>();
    //                 }
    //                 else {
    //                     b_complex = dcomplex(b.as<double>(), 0);
    //                 }   

    //                 cdebug(0) << "b is a scalar for src number " << isrc << " element " << j << " = (" << real(b_complex) << ", " << imag(b_complex) <<  "j )" << endl;
          
    //                 for (int f = 0 ; f < nfreq ; ++f) {
    //                     for (int t = 0 ; t < ntime ; ++t) {
    //                         out[j] += b*exp(_2pi_over_c*freq_data[f]*(pu[t]*l+pv[t]*m+pw[t]*n));
    //                     }
    //                 }
    //             }
    //             else { // is a vector of complex/double values

    //             }

    //         }
    //     }
    // }
}


void CUDAPointSourceVisibility::doCUDACleanUp(){

    if (d_uvw) cudaFree(d_uvw);
    //if (d_u) cudaFree(d_u);
    //if (d_v) cudaFree(d_v);
    //if (d_w) cudaFree(d_w);
    if (d_duvw) cudaFree(d_duvw);
    //if (d_du) cudaFree(d_du);
    //if (d_dv) cudaFree(d_dv);
    //if (d_dw) cudaFree(d_dw);
    if (d_df_over_2) cudaFree(d_df_over_2);
    if (d_f_dt_over_2) cudaFree(d_f_dt_over_2);
    if (d_lmn) cudaFree(d_lmn);
    if (d_freqCellSize) cudaFree(d_freqCellSize);
    if (d_timeCellSize) cudaFree(d_timeCellSize);
    if (d_B_complex) cudaFree(d_B_complex);
    if (d_time) cudaFree(d_time);
    if (d_freq) cudaFree(d_freq);
    if (d_intermediate_output_complex) cudaFree(d_intermediate_output_complex);
    if (d_output_complex) cudaFree(d_output_complex);

}
#endif

} // namespace Meq

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

// HACKHACKAHCAHCAKHCKAHCKACHKACHKACHAKCHAAAAA get rid of....
#include <cstdio>


namespace Meq {

InitDebugContext(CUDAPointSourceVisibility,"CUDAPSV");
    
    
using namespace VellsMath;

const HIID child_labels[] = { AidLMN,AidB,AidUVW };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

#ifndef STRIP_CUDA
CUDAMultiDimentionArray::CUDAMultiDimentionArray(
    const std::string n,
    int sd, int md, int td, int fd,
    int st, int mt, int tt, int ft,
    int ts) :
    name(n), 
    srcs_dims(sd), matj_dims(md), time_dims(td), freq_dims(fd),
    srcs_total(st), matj_total(mt), time_total(tt), freq_total(ft),
    type_size(ts), device_ptr(0){
}

CUDAMultiDimentionArray::~CUDAMultiDimentionArray(){
    
    printf("CLEANING %s\n", name.c_str());
    if (device_ptr) {
        cudaFree(device_ptr);
        printf("CLEANED\n");
    }
    else {
        printf("no device pointer\n");
    }

}
    
int CUDAMultiDimentionArray::getNumElements(){
    if (srcs_dims==0 && matj_dims==0 && time_dims==0 && freq_dims==0)
        return 0;
    return 
        (srcs_dims==0?1:srcs_dims*srcs_total)*
        (matj_dims==0?1:matj_dims*matj_total)*
        (time_dims==0?1:time_dims*time_total)*
        (freq_dims==0?1:freq_dims*freq_total);
}


int CUDAMultiDimentionArray::getMallocSize(){
    return getNumElements()*type_size; // TODO template for double/double2/double3
}


std::string CUDAMultiDimentionArray::CUDAMemSet(){

    int malloc_size = getMallocSize();
    if (malloc_size > 0 && cudaMemset(device_ptr, 0, malloc_size) != cudaSuccess) 
        return "cudaMemset error for d_"+name+" : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));
    return "";

}

std::string CUDAMultiDimentionArray::CUDAMemAlloc(){

    int malloc_size = getMallocSize();
    printf("MALLOC %i\n", malloc_size);
    if (malloc_size > 0 && cudaMalloc((void **) &device_ptr, malloc_size) != cudaSuccess) 
        return "cudaMalloc error for d_"+name+" : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));
    return "";
}

std::string CUDAMultiDimentionArray::CUDAMemCopy(const void* host_ptr, int element_size, int device_element_offset){

    if (element_size == 0)
        element_size = getNumElements();
    if (element_size > 0 && cudaMemcpy(device_ptr+(device_element_offset*type_size), host_ptr, element_size*type_size, cudaMemcpyHostToDevice) != cudaSuccess) 
        return "cudaMemcpy error for d_"+name+" : "+ std::string(cudaGetErrorString (cudaGetLastError  ()));
    return "";

    // if (errorString == "" && cudaMemcpy(d_uvw, pu, sizeof(double)* ntime, cudaMemcpyHostToDevice) != cudaSuccess) 
    //     errorString = "Memcopy error copying data to d_u : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
}

void CUDAMultiDimentionArray::printInfo(){

    printf("mem required for %-16s:\t%i\t%-2i * (%-6i\t= %i\t* %i\t* %i\t* %i)\n", 
           name.c_str(), getMallocSize(), type_size, getNumElements(),
           (srcs_dims*srcs_total),
           (matj_dims*matj_total),
           (time_dims*time_total),
           (freq_dims*freq_total));
}

#endif

CUDAPointSourceVisibility::CUDAPointSourceVisibility()
: TensorFunction(-4,child_labels,3), // first 3 children mandatory, rest are optional
  narrow_band_limit_(.05),time_smear_interval_(-1),freq_smear_interval_(-1),n_minus_(1),first_jones_(4)
{
    // dependence on frequency
    const HIID symdeps[] = { AidDomain,AidResolution };
    setActiveSymDeps(symdeps,2);
}

CUDAPointSourceVisibility::~CUDAPointSourceVisibility()
{}

const LoShape shape_3vec(3),shape_2x3(2,3);

// Checks tensor dimensions of a child result to see that they are a per-source tensor
// Valid dimensions are [] (i.e. [1]), [N], [Nx1], [Nx1x1], or [Nx2x2].
void CUDAPointSourceVisibility::checkTensorDims (int ichild,const LoShape &shape,int nsrc)
{
  int n = 0;
  FailWhen(shape.size()>3,"child '"+child_labels[ichild].toString()+"': illegal result rank (3 at most expected)");
  if( shape.size() == 0 )
    n = 1;
  else
  {
    n = shape[0];
    printf("child %i is dim %i\n", ichild, shape.size());
    if( shape.size() == 2 )
    {
        printf("                 %i x %i\n", shape[0], shape[1]);
      FailWhen(shape[1]!=1,"child '"+child_labels[ichild].toString()+"': rank-2 result must be of shape Nx1");
    }
    else if( shape.size() == 3 )
    {
        printf("                 %i x %i x %i\n", shape[0], shape[1], shape[2]);
      FailWhen(!(shape[1]==1 && shape[2]==1) && !(shape[1]==2 && shape[2]==2),   // Nx1x1 or Nx2x2 result 
          "child '"+child_labels[ichild].toString()+"': rank-3 result must be of shape Nx2x2 or Nx1x1");
    }
    else {
        printf("                 %i\n", shape[0]);
    }
  }
  FailWhen(n!=nsrc,"child '"+child_labels[1].toString()+"': first dimension does not match number of sources");
}

LoShape CUDAPointSourceVisibility::getResultDims (const vector<const LoShape *> &input_dims)
{

    const LoShape &lmn = *input_dims[0], &b = *input_dims[1], &uvw = *input_dims[2];
    // the first child (LMN) is expected to be of shape Nx3, the second (B) of Nx2x2
    FailWhen(lmn.size()!=2 || lmn[1]!=3,"child '"+child_labels[0].toString()+"': an Nx3 result expected");
    // N is num_sources_
    num_sources_ = lmn[0];
    // UVW must be a 3-vector or a 2x3 matrix (in this case smearing is enabled, and the second row contains du,dv,dw).
    FailWhen(uvw!=shape_3vec && uvw!=shape_2x3,"child '"+child_labels[2].toString()+"': an 2x3 matrix or a 3-vector expected");
    // B must be a per-source tensor
    checkTensorDims(1,b,num_sources_);
    // shape must be either per-source, or else null for no shape
    if( input_dims.size() > 3 )
    {
        const LoShape &shp = *input_dims[3];
        if( shp.size() < 1 || shp.product() == 1 )
            have_shape_ = false;
        else
        {
            FailWhen(shp.size()!=2 || shp[1]!=3,"child '"+child_labels[3].toString()+"': an Nx3 matrix is expected");
            FailWhen(shp[0]!=num_sources_,"child '"+child_labels[3].toString()+"': first dimension does not match number of sources");
            have_shape_ = true;
        }
    }
    else
        have_shape_ = false;
  
    // Additional children after the first_jones should come in pairs (Jones term, plus its conjugate), and be per-source tensors
    FailWhen((input_dims.size()-first_jones_)%2!=0,"a pair of children must be provided per each Jones term");
    for( uint i=first_jones_; i<input_dims.size(); i++ )
        checkTensorDims(i,*input_dims[i],num_sources_);

    // our result is a 2x2 matrix 
    return LoShape(2,2);
}



#ifdef STRIP_CUDA
void CUDAPointSourceVisibility::evaluateTensors (std::vector<Vells> & out,
                                                 const std::vector<std::vector<const Vells *> > &args )
{
   
    FailWhen(true,"CUDA required in order to use this node"); 
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

    bool computeSmear = false;
    if( args[2].size() == 6 )
        computeSmear = true;

    cdebug(0) << "args[2].size() = " << args[2].size() << endl;

    const double *pu = NULL;
    const double *pv = NULL;
    const double *pw = NULL;
    const double *pdu = NULL;
    const double *pdv = NULL;
    const double *pdw = NULL;

    vector<double> vec_df_over_2_(nfreq);
    vector<double> vec_f_dt_over_2_(ntime);

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

    //==================================================================================================

    int nsrcs = num_sources_; // I just prefer this name to num_sources_
    int nmatj = NUM_MATRIX_ELEMENTS; // I just prefer this name too


    // these will be vectors of ntime points each
    pu = vu.realStorage();
    pv = vv.realStorage();
    pw = vw.realStorage();

    double narrow_band_limit_ = .05;

    Vells df_over_2_,f_dt_over_2_;  // delta_freq/2, and freq*delta_time/2
    Vells freq_vells_;
    Vells freq_approx;

    if (computeSmear) {
        const Vells & dvu = *(args[2][3]);
        const Vells & dvv = *(args[2][4]);
        const Vells & dvw = *(args[2][5]);
        FailWhen(dvu.shape() != timeshape || dvv.shape() != timeshape || dvw.shape() != timeshape,"expecting UVWs derivatives that are a vector in time");



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

    int compute_n_jones = -1;
    int compute_z_jones = -1;
    int compute_l_jones = -1;
    int compute_e_jones = -1;

    int num_jones_terms=(args.size()-first_jones_)/2;
    //TODO error check/failwhen

    printf("Number of Joneses %i\n", num_jones_terms);
    for(int i = 0 ; i < num_jones_terms ; ++i) {
        int jones_index   = first_jones_+(i*2);
        int jones_h_index = first_jones_+(i*2)+1;

        
        printf("Jones %i - \ndim 0: %i\n", i, args[jones_index].size());
        const Vells* jones_vell = args[jones_index][0];
        //printf ("dims past s: %i\n", jones_vell->shape().size());

        for(int d = 0 ; d < jones_vell->shape().size(); d++)
            printf ("dim %i: %i\n", d+1, jones_vell->shape()[d]);

        if (args[jones_index].size() == nsrcs) { // then it is a src*freq array (E/Z/N)
            printf("e/z/n-jones\n");

            if (jones_vell->isReal()) {
                printf("Real\n");
                printf("e-jones\n");

                compute_e_jones = jones_index;
                
            }
            else if (jones_vell->isComplex()){ // is a vector of complex values
                printf("Complex\n");
                printf("n/z-jones - NOT IMPLEMENTED\n");
            }

        }
        else { // it is a srcx2x2 = src*matj array (L)
            
            printf("l-jones - NOT IMPLEMENTED\n");
        }


        
        printf("\n");
    }

    //-----------------------------------------------------------------------------------------------

    // Storing into arrays: LMN, brightness, jones terms

    // store source*matrix sized data (B[s*j] / L-jones[s*j]) and source sized data (lmn[s])
    std::vector<lmn_t> lmn_data(nsrcs); 
    std::vector<double2> b_data_complex(nsrcs*nfreq*NUM_MATRIX_ELEMENTS); 
    std::vector<double> e_jones_data[2] = {std::vector<double>(nsrcs*nfreq), std::vector<double>(nsrcs*nfreq)};
    
    for( int isrc=0; isrc < nsrcs; isrc++ )
    {
        //cdebug(0) << "src number " << isrc<<"/"<<num_sources_ << endl;

        //- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        // LMN (3*s)
        // get the LMNs for this source
        const Vells & vl = *(args[0][isrc*3]);
        const Vells & vm = *(args[0][isrc*3+1]);
        const Vells & vn = *(args[0][isrc*3+2]);
        if(!vl.isScalar() || !vm.isScalar() || !vn.isScalar()) {
            FailWhen(true, "expecting scalar LMNs");
        }
        double l = vl.as<double>();
        double m = vm.as<double>();
        double n = vn.as<double>();
          

        lmn_data[isrc].x = l;
        lmn_data[isrc].y = m;
        lmn_data[isrc].z = n;


        //- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        // Brightness (complex s*j*f)
        for( int j=0; j<NUM_MATRIX_ELEMENTS; j++ )
        {
            const Vells &b = *(args[1][isrc*NUM_MATRIX_ELEMENTS + j]);
            if(!b.isScalar() && b.shape() != freqshape) {
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


        //- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        // e-jones (real s*f jones)
        
        if(compute_e_jones){
            int jones_index = compute_e_jones;
            for (int h = 0 ; h < 2 ; h++) {
                const Vells &e = *(args[jones_index+h][isrc]);
        
                if(!e.isScalar() && e.shape() != freqshape) {
                    FailWhen(true, "expecting E-jones elements that are either scalar, or a vector in frequency");
                }
        
                if( e.isNull())
                {
                    for (int f = 0 ; f < nfreq ; f++) {
                    
                        int sf_j_i = get_sf_jones_index(isrc,  nsrcs,
                                                        f,     nfreq);

                        e_jones_data[h][sf_j_i] = 0;

                    }
                }
                else if (e.isScalar()) {

                    double e_real;
                    if (e.isReal()) {
                        e_real = e.as<double>();
                    }
                    else {
                        FailWhen(true, "expecting E-jones elements to be real");
                    }   

                    for (int f = 0 ; f < nfreq ; f++) {

                        int sf_j_i = get_sf_jones_index(isrc,  nsrcs,
                                                        f,     nfreq);

                        e_jones_data[h][sf_j_i] = e_real;

                    }
                }
                else { // is a vector of real values
                    const double* e_real_vec = e.realStorage();
                    for (int f = 0 ; f < nfreq ; f++) {

                        int sf_j_i = get_sf_jones_index(isrc,  nsrcs,
                                                        f,     nfreq);

                        e_jones_data[h][sf_j_i] = e_real_vec[f];
                    }
                }
            }
        }
    }



    //==================================================================================================
    // CUDA bit


    // specifying input and output multi-dimentional arrays/pointers
    CUDAMultiDimentionArray uvw         ("uvw",
                                         0,    0,      3,     0,
                                         nsrcs, nmatj, ntime, nfreq,
                                         sizeof(double));
    CUDAMultiDimentionArray duvw        ("duvw",
                                         0,    0,      computeSmear?3:0, 0,
                                         nsrcs, nmatj, ntime,            nfreq,
                                         sizeof(double));
    CUDAMultiDimentionArray df_over_2   ("df_over_2",
                                         0,    0,      0,     computeSmear?1:0,
                                         nsrcs, nmatj, ntime, nfreq,
                                         sizeof(double));

    CUDAMultiDimentionArray f_dt_over_2 ("f_dt_over_2",
                                         0,    0,      computeSmear?1:0, 0,
                                         nsrcs, nmatj, ntime,            nfreq,
                                         sizeof(double));
    CUDAMultiDimentionArray lmn          ("lmn",
                                          1,    0,      0,     0,
                                          nsrcs, nmatj, ntime, nfreq,
                                          sizeof(lmn_t));
    CUDAMultiDimentionArray brightness   ("B",
                                          1,    1,      0,     1,
                                          nsrcs, nmatj, ntime, nfreq,
                                          sizeof(double2));
    CUDAMultiDimentionArray freq         ("freq",
                                          0,    0,      0,     1,
                                          nsrcs, nmatj, ntime, nfreq,
                                         sizeof(double));
    CUDAMultiDimentionArray time         ("time",
                                          0,    0,      1,     0,
                                          nsrcs, nmatj, ntime, nfreq,
                                         sizeof(double));

    CUDAMultiDimentionArray e_jones      ("e-jones",
                                          compute_e_jones==-1?0:1, 0,     0,     compute_e_jones==-1?0:1,
                                          nsrcs,                   nmatj, ntime, nfreq,
                                          sizeof(double));
    CUDAMultiDimentionArray e_jones_h    ("e-jones H",
                                          compute_e_jones==-1?0:1, 0,     0,     compute_e_jones==-1?0:1,
                                          nsrcs,                   nmatj, ntime, nfreq,
                                          sizeof(double));

    CUDAMultiDimentionArray output       ("output",
                                          0,    1,      1,     1,
                                          nsrcs, nmatj, ntime, nfreq,
                                         sizeof(double2));



    //std::vector<CUDAMultiDimentionArray> tf_joneses();

    std::vector<CUDAMultiDimentionArray*> cmda_input;
    cmda_input.push_back(&uvw);
    cmda_input.push_back(&duvw);
    cmda_input.push_back(&df_over_2);
    cmda_input.push_back(&f_dt_over_2);
    cmda_input.push_back(&lmn);
    cmda_input.push_back(&brightness);
    cmda_input.push_back(&freq);
    cmda_input.push_back(&time);
    cmda_input.push_back(&e_jones);
    cmda_input.push_back(&e_jones_h);


    // Calculating how much intermediate data can be stored
    int total_input_bytes = 0;
    for (int i = 0 ; i < cmda_input.size() ; i++) {
        total_input_bytes += cmda_input[i]->getMallocSize();
        cmda_input[i]->printInfo();
    }
    int total_output_bytes = output.getMallocSize();
    output.printInfo();

    printf("total input bytes                :\t%i\n", total_input_bytes);
    printf("total output bytes               :\t%i\n", total_output_bytes);
    printf("total input/output bytes         :\t%i\n", total_output_bytes+total_input_bytes);
         
    CUDAMultiDimentionArray _1_intermediate ("one_intermediate",
                                             0,    1,      1,     1,
                                             nsrcs, nmatj, ntime, nfreq,
                                             sizeof(double2));

    _1_intermediate.printInfo();

    size_t avail;
    size_t total;
    cudaMemGetInfo( &avail, &total );
    size_t used = total - avail;
    
    int memory_to_remain_free = 32*1024*1024;

    int nsrcs_per_slot = 1;
#ifdef MULTI_SRC_PER_THREAD
    nsrcs_per_slot = 64;
#endif

    int nslots_required = ((nsrcs-1)/nsrcs_per_slot)+1;

    size_t remaining_for_intermediate = avail-total_input_bytes-total_output_bytes-memory_to_remain_free;
    printf("total bytes remaining            :\t%i\n", remaining_for_intermediate);

    int max_slots_per_run = ((remaining_for_intermediate-1)/_1_intermediate.getMallocSize()) + 1;
    printf("nslots_required                  :\t\t\t\t= %i (%i src/slot)\n", nslots_required, nsrcs_per_slot);
    printf("max_slots_per_run                :\t\t\t\t= %i\n", max_slots_per_run);
    int nslots_per_run = nslots_required;
    if (max_slots_per_run > nslots_required)
        nslots_per_run = nslots_required;

    if (nslots_per_run == 0)
        nslots_per_run = 1;


    CUDAMultiDimentionArray intermediate ("intermediate",
                                          1,              1,     1,     1,
                                          nslots_per_run, nmatj, ntime, nfreq,
                                          sizeof(double2));
    intermediate.printInfo();

    // mallocing input, intermediate and output data
    std::vector<CUDAMultiDimentionArray*> cmda = cmda_input;
    cmda.push_back(&intermediate);
    cmda.push_back(&output);
    for (int i = 0 ; i < cmda.size() ; i++) {
        
        printf("CUDA malloc of %-15s - ", cmda[i]->name.c_str());
        std::string errorString = cmda[i]->CUDAMemAlloc() ;
        if (errorString == "")
            printf("Success\n");
        else {
            printf("Failed - %s\n", errorString.c_str());
            FailWhen(true, errorString);
        }
    }




    // Copying data to device
    std::vector<CUDAMultiDimentionArray*> device_cmdas;
    std::vector<const void*> host_ptrs;
    std::vector<int> offsets;
    std::vector<int> sizes;

    device_cmdas.push_back(&uvw);  host_ptrs.push_back(pu);  sizes.push_back(ntime); offsets.push_back(0);
    device_cmdas.push_back(&uvw);  host_ptrs.push_back(pv);  sizes.push_back(ntime); offsets.push_back(ntime);
    device_cmdas.push_back(&uvw);  host_ptrs.push_back(pw);  sizes.push_back(ntime); offsets.push_back(ntime*2);
    if (computeSmear) {
        device_cmdas.push_back(&duvw);        host_ptrs.push_back(pdu); sizes.push_back(ntime); offsets.push_back(0);
        device_cmdas.push_back(&duvw);        host_ptrs.push_back(pdv); sizes.push_back(ntime); offsets.push_back(ntime);
        device_cmdas.push_back(&duvw);        host_ptrs.push_back(pdw); sizes.push_back(ntime); offsets.push_back(ntime*2);
        device_cmdas.push_back(&df_over_2);   host_ptrs.push_back(&(vec_df_over_2_[0])); sizes.push_back(0); offsets.push_back(0);
        device_cmdas.push_back(&f_dt_over_2); host_ptrs.push_back(&(vec_f_dt_over_2_[0])); sizes.push_back(0); offsets.push_back(0);
    }
    device_cmdas.push_back(&lmn);        host_ptrs.push_back(&(lmn_data[0]));       sizes.push_back(0); offsets.push_back(0);
    device_cmdas.push_back(&brightness); host_ptrs.push_back(&(b_data_complex[0])); sizes.push_back(0); offsets.push_back(0);

    device_cmdas.push_back(&freq);      host_ptrs.push_back(&(freq_data[0]));       sizes.push_back(0); offsets.push_back(0);
    device_cmdas.push_back(&time);      host_ptrs.push_back(&(time_data[0]));       sizes.push_back(0); offsets.push_back(0);
    device_cmdas.push_back(&e_jones);   host_ptrs.push_back(&(e_jones_data[0][0])); sizes.push_back(0); offsets.push_back(0);
    device_cmdas.push_back(&e_jones_h); host_ptrs.push_back(&(e_jones_data[1][0])); sizes.push_back(0); offsets.push_back(0);


    for (int i = 0 ; i < device_cmdas.size() ; i++) {
        
        printf("CUDA memcopy of %s (size %i, offset %i) - ", device_cmdas[i]->name.c_str(), sizes[i], offsets[i]);
        std::string errorString = device_cmdas[i]->CUDAMemCopy(host_ptrs[i], sizes[i], offsets[i]) ;
        if (errorString == "")
            printf("Success\n");
        else {
            printf("Failed - %s\n", errorString.c_str());
            FailWhen(true, errorString);
        }
    }


    // Zeroing output data on device - TODO if not doing multiple_srcs_per_thread we can ignore this step
    std::vector<CUDAMultiDimentionArray*> cmda_output;
    cmda_output.push_back(&intermediate);
    cmda_output.push_back(&output);
    for (int i = 0 ; i < cmda_output.size() ; i++) {
        
        printf("CUDA memset of %s - ", cmda_output[i]->name.c_str());
        std::string errorString = cmda_output[i]->CUDAMemSet() ;
        if (errorString == "")
            printf("Success\n");
        else {
            printf("Failed - %s\n", errorString.c_str());
            FailWhen(true, errorString);
        }
    }


    cdebug(0) << "total problem size " << nsrcs << "x" << ntime << "x" << nfreq << ", starting kernel runs" << endl;

    std::string kernelErrorString;
    kernelErrorString = runCUDAPointSourceVisibilityKernel((lmn_t*)lmn.device_ptr, 
                                                           (double2*)brightness.device_ptr, 
                                                           nsrcs,
                                                           nslots_required,
                                                           nsrcs_per_slot,
                                                           nslots_per_run,
                                                           (double*)uvw.device_ptr, 
                                                           (double*)duvw.device_ptr, 
                                                           (double*)time.device_ptr,
                                                           ntime, 
                                                           (double*)freq.device_ptr, 
                                                           nfreq,
                                                           (double*)df_over_2.device_ptr, 
                                                           (double*)f_dt_over_2.device_ptr,
                                                           (double*)e_jones.device_ptr,
                                                           (double*)e_jones_h.device_ptr,
                                                           (double2*)intermediate.device_ptr,
                                                           (double2*)output.device_ptr, 
                                                           NUM_MATRIX_ELEMENTS,
                                                           _2pi_over_c,
                                                           pout);


    if (kernelErrorString != ""){
        cdebug(0) << std::string(cudaGetErrorString (cudaGetLastError  ())) << endl;
        FailWhen(true, kernelErrorString);
    }


    cdebug(0) << "ALL DONE =========================" << endl;

}

#endif

} // namespace Meq


//#include <MeqNodes/CUDAPointSourceVisibility.h>
#include <cuda.h>
#include <cuda_runtime.h>
#include <stdio.h>

#include <vector>
#include <complex>
#include <string>
#include <TimBase/LofarTypedefs.h>

#include <MeqNodes/CUDAPointSourceVisibilityCommon.h>

// HACKHACKAHCAHCAKHCKAHCKACHKACHKACHAKCHAAAAA get rid of....
#include <cstdio>

// this is a test comment to see if my git-svn thing works!

texture<float, 1, cudaReadModeElementType> texRef;

namespace Meq {


    /****************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/

    // inline __device__ int CUDAgetMultiDimIndex(int a, int aT, int b, int bT, int c, int cT, int d, int dT, int e, int eT) {
    //     return a*bT*cT*dT*eT + b*cT*dT*eT + c*dT*eT + d*eT + e;
    // }

    __device__ __host__ __inline__ int getMultiDimIndex(int a, int aT, int b, int bT, int c, int cT, int d, int dT, int e, int eT) {
        return a*bT*cT*dT*eT + b*cT*dT*eT + c*dT*eT + d*eT + e;
    }

    __device__ __host__ __inline__ int getMultiDimIndex(int a, int aT, int b, int bT, int c, int cT, int d, int dT) {
        return a*bT*cT*dT + b*cT*dT + c*dT + d;
    }

    __device__ __host__ __inline__ int getMultiDimIndex(int a, int aT, int b, int bT, int c, int cT) {
        return a*bT*cT + b*cT + c;
    }

    /****************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
    __device__ __host__ int get_B_index(int s, int nsrcs, 
                                        int f, int nfreq, 
                                        int j, int num_matrix_elements){
    
        // return getMultiDimIndex( s,               nsrcs,             
        //                          f,               nfreq,
        //                          j,               num_matrix_elements);

        return getMultiDimIndex( j, num_matrix_elements,
                                 s, nsrcs,             
                                 f, nfreq);
    }

    /****************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
    __device__ __host__ __inline__ int get_intermediate_output_index(int s, int nsrcs, 
                                                                     int t, int ntime, 
                                                                     int f, int nfreq, 
                                                                     int j, int num_matrix_elements){


        // return getMultiDimIndex(s, nsrcs, 
        //                         t, ntime,
        //                         f, nfreq,
        //                         j, num_matrix_elements);

        // return getMultiDimIndex(j, num_matrix_elements,
        //                         t, ntime,
        //                         f, nfreq,
        //                         s, nsrcs );


        // return getMultiDimIndex(j, num_matrix_elements,
        //                         s, nsrcs, 
        //                         t, ntime,
        //                         f, nfreq);

        // return getMultiDimIndex(s, nsrcs,
        //                         j, num_matrix_elements,
        //                         f, nfreq,
        //                         t, ntime);

        return getMultiDimIndex(j, num_matrix_elements,
                                s, nsrcs, 
                                f, nfreq,
                                t, ntime);



    }

    /****************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
    __device__ __host__ __inline__ int get_shared_mem_index(int t, int ntime, 
                                                            int f, int nfreq, 
                                                            int j, int num_matrix_elements){


        // return getMultiDimIndex(t, ntime,
        //                         f, nfreq,
        //                         j, num_matrix_elements);


        // return getMultiDimIndex(j, num_matrix_elements,
        //                         t, ntime,
        //                         f, nfreq);

        return getMultiDimIndex(j, num_matrix_elements,
                                f, nfreq,
                                t, ntime);

    }
    /****************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
    __device__ __host__ __inline__ int get_output_index(int t, int ntime, 
                                                        int f, int nfreq, 
                                                        int j, int num_matrix_elements){


        return getMultiDimIndex(t, ntime,
                                f, nfreq,
                                j, num_matrix_elements);

    }


    /****************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/

    inline __device__ __host__ dim3 fromNormalToAdjustedDim(const dim3& normal) {
        return dim3(normal.x, normal.y*normal.z, 1);
    }

    /****************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/

    inline __device__ __host__ dim3 fromAdjustedToNormalDim(const dim3& adjusted, const dim3& originalGrid) {
        return dim3(adjusted.x, adjusted.y%originalGrid.y, adjusted.y/originalGrid.y);
    }



    //  /***************************************************************************
    //  **
    //  ** Author: Richard Baxter
    //  **
    //  ****************************************************************************/
    // __global__ void CUDAPointSourceVisibilityKernel_K(dim3 desiredGridDim, 
    //                                                   lmn_t* d_lmn, 
    //                                                   double2* d_B_complex,
    //                                                   int nsrcs, 
    //                                                   int srcs_offset, 
    //                                                   int srcs_per_thread,
    //                                                   double* d_uvw, 
    //                                                   double* d_time, 
    //                                                   int ntime, 
    //                                                   double* d_freq, 
    //                                                   int nfreq, 
    //                                                   int num_matrix_elements, 
    //                                                   double2* d_intermediate_output_complex, 
    //                                                   double _2pi_over_c
    //     ) {   


    //     double* d_u = d_uvw;
    //     double* d_v = d_uvw+ntime;
    //     double* d_w = d_uvw+(ntime*2);


    //     dim3 actualBlockIdx = fromAdjustedToNormalDim(blockIdx, desiredGridDim);
    //     #define ADJ_X actualBlockIdx.x
    //     #define ADJ_Y actualBlockIdx.y
    //     #define ADJ_Z actualBlockIdx.z


    //     int s_i = ((ADJ_X*blockDim.x) + threadIdx.x);
    //     int s = s_i+srcs_offset;
    //     int t = ((ADJ_Y*blockDim.y) + threadIdx.y);
    //     int f = ((ADJ_Z*blockDim.z) + threadIdx.z);

    //     if (t < ntime && f < nfreq) 
    //     {
    //         if (s < nsrcs)
    //         {

    //             double argument = _2pi_over_c*(d_u[t]*d_lmn[s].x+d_v[t]*d_lmn[s].y+d_w[t]*d_lmn[s].z);

    //             double realVal;
    //             double imagVal;
    //             sincos(d_freq[f]*argument, &realVal, &imagVal);

    //             for( int j=0; j<num_matrix_elements; ++j ){


    //                 // calcuating B*exp(...) = B*E = (B.r+jB.i)(E.r+jE.i) = (B.r*E.r - B.i*E.i) + j(B.r*E.i + B.i*E.r)
    //                 //                                                    = (B.i*E.r + B.r*E.i) - j(B.i*E.i + B.r*E.r)

    //                 int b_index = get_B_index(s, nsrcs, 
    //                                           f, nfreq,
    //                                           j, num_matrix_elements);

    //                 int the_index = get_intermediate_output_index(s_i, nsrcs, // must address this via the index
    //                                                               t,   ntime,
    //                                                               f,   nfreq,
    //                                                               j,   num_matrix_elements);

    //                 d_intermediate_output_complex[the_index].x = 
    //                     (+ d_B_complex[b_index].y*realVal + d_B_complex[b_index].x*imagVal);
    //                 d_intermediate_output_complex[the_index].y = 
    //                     (+ d_B_complex[b_index].y*imagVal - d_B_complex[b_index].x*realVal);
            


    //             }
    //         }
    //     }

        
    // }



    //  /***************************************************************************
    //  **
    //  ** Author: Richard Baxter
    //  **
    //  ****************************************************************************/
    // __global__ void CUDAPointSourceVisibilityKernel_Smear(dim3 desiredGridDim, 
    //                                                       lmn_t* d_lmn, 
    //                                                       double2* d_B_complex,
    //                                                       int nsrcs, 
    //                                                       int srcs_offset, 
    //                                                       int srcs_per_thread,
    //                                                       double* d_uvw, 
    //                                                       double* d_duvw, 
    //                                                       double* d_time, 
    //                                                       int ntime, 
    //                                                       double* d_freq, 
    //                                                       int nfreq, 
    //                                                       double* d_df_over_2, 
    //                                                       double* d_f_dt_over_2, 
    //                                                       int num_matrix_elements, 
    //                                                       double2* d_intermediate_output_complex, 
    //                                                       double _2pi_over_c
    //     ) {   


    //     double* d_u = d_uvw;
    //     double* d_v = d_uvw+ntime;
    //     double* d_w = d_uvw+(ntime*2);

    //     double* d_du = d_duvw;
    //     double* d_dv = d_duvw+ntime;
    //     double* d_dw = d_duvw+(ntime*2);

    //     dim3 actualBlockIdx = fromAdjustedToNormalDim(blockIdx, desiredGridDim);
    //     #define ADJ_X actualBlockIdx.x
    //     #define ADJ_Y actualBlockIdx.y
    //     #define ADJ_Z actualBlockIdx.z




    //     int s_i = ((ADJ_X*blockDim.x) + threadIdx.x);
    //     int s = s_i+srcs_offset;
    //     int t = ((ADJ_Y*blockDim.y) + threadIdx.y);
    //     int f = ((ADJ_Z*blockDim.z) + threadIdx.z);



    //     if (t < ntime && f < nfreq) 
    //     {


    //         if (s < nsrcs)
    //         {


    //             //double dargument = _2pi_over_c*(d_du[t]*d_lmn[s].x+d_dv[t]*d_lmn[s].y+d_dw[t]*d_lmn[s].z);
    //             //double argument = _2pi_over_c*(d_u[t]*d_lmn[s].x+d_v[t]*d_lmn[s].y+d_w[t]*d_lmn[s].z);
    //             double E_jones = 1.0;


    //             double dphi = d_f_dt_over_2[t] * _2pi_over_c*(d_du[t]*d_lmn[s].x+d_dv[t]*d_lmn[s].y+d_dw[t]*d_lmn[s].z);
    //             if (dphi != 0.0) 
    //                 E_jones = sin(dphi)/dphi;

    //             double dpsi = d_df_over_2[f] * _2pi_over_c*(d_u[t]*d_lmn[s].x+d_v[t]*d_lmn[s].y+d_w[t]*d_lmn[s].z);
    //             if (dpsi != 0.0)
    //                 E_jones *= sin(dpsi)/dpsi;



    //             for( int j=0; j<num_matrix_elements; ++j ){


    //                 int the_index = get_intermediate_output_index(s_i, nsrcs, // must address this via the index
    //                                                               t,   ntime,
    //                                                               f,   nfreq,
    //                                                               j,   num_matrix_elements);

    //                 d_intermediate_output_complex[the_index].x *= E_jones;
    //                 d_intermediate_output_complex[the_index].y *= E_jones;
        



    //             }
    //         }
    //     }

        
    // }

     /***************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
    __global__ void 
    //__launch_bounds__(256, 3)
        CUDAPointSourceVisibilityKernel(dim3 desiredGridDim, 
                                        lmn_t* d_lmn, 
                                        double2* d_B_complex,
                                        int nsrcs, 
                                        int nslots, 
                                        int srcs_offset, 
                                        int srcs_per_thread,
                                        double* d_uvw, 
                                        double* d_duvw, 
                                        double* d_time, 
                                        int ntime, 
                                        double* d_freq, 
                                        int nfreq, 
                                        double* d_df_over_2, 
                                        double* d_f_dt_over_2, 
                                        int num_matrix_elements, 
                                        double2* d_intermediate_output_complex, 
                                        double _2pi_over_c
        ) {   


        double* d_u = d_uvw;
        double* d_v = d_uvw+ntime;
        double* d_w = d_uvw+(ntime*2);
// #define D_U(t) d_u[t]
// #define D_V(t) d_v[t]
// #define D_W(t) d_w[t]
// #define D_U(t) d_uvw[t]
// #define D_V(t) d_uvw[ntime + t]
// #define D_W(t) d_uvw[(ntime*2)+t]

        double* d_du = d_duvw;
        double* d_dv = d_duvw+ntime;
        double* d_dw = d_duvw+(ntime*2);
// #define D_DU(t) d_du[t]
// #define D_DV(t) d_dv[t]
// #define D_DW(t) d_dw[t]
// #define D_DU(t) (d_duvw[t])
// #define D_DV(t) (d_duvw[ntime + t])
// #define D_DW(t) (d_duvw[(ntime*2)+t])


        //double* d_f_dt_over_2 = 0;
    
        // Axes:
        //   x: sources
        //   y: time
        //   z: freq


        //#define ADJ_X (blockIdx.x)
        //#define ADJ_Y (blockIdx.y%desiredGridDim.y)
        //#define ADJ_Z (blockIdx.y/desiredGridDim.y)

        dim3 actualBlockIdx = fromAdjustedToNormalDim(blockIdx, desiredGridDim);
        #define ADJ_X actualBlockIdx.x
        #define ADJ_Y actualBlockIdx.y
        #define ADJ_Z actualBlockIdx.z



        int s_i = ((ADJ_X*blockDim.x) + threadIdx.x); // input index
//#ifdef MULTI_SRC_PER_THREAD
//        int s_start_i = ((ADJ_X*blockDim.x) + threadIdx.x);
//#endif
#ifndef MULTI_SRC_PER_THREAD
        int s = s_i+srcs_offset;
#endif
        int t = ((ADJ_Y*blockDim.y) + threadIdx.y); // t_i since calcs per thread = 1
        int f = ((ADJ_Z*blockDim.z) + threadIdx.z); // f_i since calcs per thread = 1
        //int t_i = t;
        //int f_i = f;
        #define NTIME_SHARED blockDim.y
        #define NFREQ_SHARED blockDim.z

#ifdef SHARED_MEMORY
        int t_si = threadIdx.y; // si = shared (memory) output index
        int f_si = threadIdx.z;
#endif

        //printf("(%i,%i,%i) %i\n", s_i, t, f);
        //for (int s = srcsID_start ; s < srcsID_start+1 && s < nsrcs ; ++s) {
            
        //for (int t = timeID_start ; t < timeID_start+1 && t < ntime; ++t)  {

        //for (int f = freqID_start ; f < freqID_start+1 && f < nfreq ; ++f) {

        // int s = srcsID_start;
        // int t = timeID_start;
        // int f = freqID_start;

        //printf("INFO (%i, %i, %i) \t(t %i/%i, f %i/%i)\n", s_i, t, f, t_si, NTIME_SHARED, f_si, NFREQ_SHARED);

        if (t < ntime && f < nfreq) 
        {

#ifdef SHARED_MEMORY

            //printf("(%i, %i, %i) SHARED!!!!!\n", s_i, t_si, f_si);
            extern __shared__ double2 shared_mem []; // size blockDim.y*blockDim.z*num_matrix_elements
            //printf("(%i, %i, %i) REALLY SHARED!!!!!\n", s_i, t_si, f_si);

//#ifdef MULTI_SRC_PER_THREAD
            for( int j=0; j<num_matrix_elements; ++j ){
                int share_index = get_shared_mem_index(t_si, NTIME_SHARED,
                                                       f_si, NFREQ_SHARED,
                                                       j, num_matrix_elements);

                //printf("(%i, %i, %i) \tshare index: %i \t(t %i/%i, f %i/%i, j %i/%i)\n", s_i, t, f, share_index, t_si, NTIME_SHARED, f_si, NFREQ_SHARED, j, num_matrix_elements);
                shared_mem[share_index].x = 0;
                shared_mem[share_index].y = 0;
            }
//#endif
#endif


#ifdef MULTI_SRC_PER_THREAD
//#pragma unroll 64
                for (int s = s_i*srcs_per_thread; s < (s_i+1)*srcs_per_thread && s < nsrcs ; ++s) 
#endif
#ifndef MULTI_SRC_PER_THREAD
                if (s < nsrcs)
#endif

            {

                double argument = d_freq[f]*_2pi_over_c*(d_u[t]*d_lmn[s].x+d_v[t]*d_lmn[s].y+d_w[t]*(d_lmn[s].z-1));



                double smearFactor = 1.0;

                if (d_duvw) {
//#define DARGUMENT (_2pi_over_c*(D_DU(t)*d_lmn[s].x+D_DV(t)*d_lmn[s].y+D_DW(t)*d_lmn[s].z));

                    double dargument = _2pi_over_c*(d_du[t]*d_lmn[s].x+d_dv[t]*d_lmn[s].y+d_dw[t]*(d_lmn[s].z-1));
                    double dphi = d_f_dt_over_2[t] * dargument;
                    if (dphi != 0.0) 
                        smearFactor = sin(dphi)/dphi;

                    double dpsi = d_df_over_2[f] * argument;
                    if (dpsi != 0.0)
                       smearFactor *= sin(dpsi)/dpsi;

                }

                // double argument = _2pi_over_c*d_freq[f]*(d_u[t]*d_lmn[s].x+d_v[t]*d_lmn[s].y+d_w[t]*d_lmn[s].z);
                // double realVal = sin(argument);
                // double imagVal = cos(argument);

                double realVal;
                double imagVal;
                sincos(argument, &realVal, &imagVal);

                for( int j=0; j<num_matrix_elements; ++j ){

                    // TODO use sincos

                    // calcuating B*exp(...) = B*E = (B.r+jB.i)(E.r+jE.i) = (B.r*E.r - B.i*E.i) + j(B.r*E.i + B.i*E.r)
                    //                                                    = (B.i*E.r + B.r*E.i) - j(B.i*E.i + B.r*E.r)

                    int b_index = get_B_index(s, nsrcs, 
                                              f, nfreq,
                                              j, num_matrix_elements);


#ifndef SHARED_MEMORY
                    int the_index = get_intermediate_output_index(s_i, nslots, // must address this via the index
                                                                  t,   ntime,
                                                                  f,   nfreq,
                                                                  j,   num_matrix_elements);

                    d_intermediate_output_complex[the_index].x += 
                        (+ d_B_complex[b_index].y*realVal + d_B_complex[b_index].x*imagVal)*smearFactor;
                    d_intermediate_output_complex[the_index].y += 
                        (+ d_B_complex[b_index].y*imagVal - d_B_complex[b_index].x*realVal)*smearFactor;
                        
#endif

#ifdef SHARED_MEMORY

                    int share_index = get_shared_mem_index(t_si, NTIME_SHARED,
                                                           f_si, NFREQ_SHARED,
                                                           j,    num_matrix_elements);

                    //printf("(%i, %i, %i) \tshare index: %i \t(t %i, f %i, j %i)\n", s_i, t, f, share_index, t_si, f_si, j);

  #ifdef MULTI_SRC_PER_THREAD
                    shared_mem[share_index].x += 
                        (+ d_B_complex[b_index].y*realVal + d_B_complex[b_index].x*imagVal)*smearFactor;
                    shared_mem[share_index].y += 
                        (+ d_B_complex[b_index].y*imagVal - d_B_complex[b_index].x*realVal)*smearFactor;
  #endif

  #ifndef MULTI_SRC_PER_THREAD
                    shared_mem[share_index].x = 
                          (+ d_B_complex[b_index].y*realVal + d_B_complex[b_index].x*imagVal)*smearFactor;
                    shared_mem[share_index].y = 
                          (+ d_B_complex[b_index].y*imagVal - d_B_complex[b_index].x*realVal)*smearFactor;
  #endif
#endif



                }
            }
#ifdef SHARED_MEMORY
            for( int j=0; j<num_matrix_elements; ++j ){
                int the_index = get_intermediate_output_index(s_i, nslots, 
                                                              t,   ntime,
                                                              f,   nfreq,
                                                              j,   num_matrix_elements);
                int share_index = get_shared_mem_index(t_si, NTIME_SHARED,
                                                   f_si, NFREQ_SHARED,
                                                   j,    num_matrix_elements);
                d_intermediate_output_complex[the_index] = shared_mem[share_index];
            }
#endif
        }

        //}
        //}
        
    }


     /***************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
    __global__ void CUDAPointSourceVisibilityReductionKernel(dim3 desiredGridDim, 
                                                             int nsrcs, 
                                                             int nslots, 
                                                             int srcs_offset, 
                                                             int srcs_per_thread,
                                                             int ntime, 
                                                             int nfreq, 
                                                             int num_matrix_elements, 
                                                             double2* d_intermediate_output_complex,
                                                             int reducers,
                                                             int gap) {   
        
        // Axes:
        //   x: sources (reductor)
        //   y: time
        //   z: freq

        dim3 actualBlockIdx = fromAdjustedToNormalDim(blockIdx, desiredGridDim.x);


        int xThreadIdx = ((actualBlockIdx.x*blockDim.x) + threadIdx.x);
        int yThreadIdx = ((actualBlockIdx.y*blockDim.y) + threadIdx.y);
        int zThreadIdx = ((actualBlockIdx.z*blockDim.z) + threadIdx.z);

        int s_i = xThreadIdx*gap*2;
        int s_i2 = s_i+gap;
        int t = yThreadIdx;
        int f = zThreadIdx;

                                
        //for (int s = srcsID_start ; s < srcsID_start+1 && s < nsrcs ; ++s) {
            
        //for (int t = timeID_start ; t < timeID_start+1 && t < ntime; ++t)  {

        //for (int f = freqID_start ; f < freqID_start+1 && f < nfreq ; ++f) {

        // int s = srcsID_start;
        // int s2 = srcsID2_start;
        // int t = timeID_start;
        // int f = freqID_start;
        if ((s_i*srcs_per_thread)+srcs_offset < nsrcs && (s_i2*srcs_per_thread)+srcs_offset < nsrcs && s_i != s_i2 && t < ntime && f < nfreq) { //TODO - only need n-1 threads if n is odd

            for( int j=0; j<num_matrix_elements; ++j ){

                int the_index = get_intermediate_output_index(s_i, nslots, 
                                                              t,   ntime,
                                                              f,   nfreq,
                                                              j,   num_matrix_elements);

                int the_index2 = get_intermediate_output_index(s_i2, nslots, 
                                                               t,    ntime,
                                                               f,    nfreq,
                                                               j,    num_matrix_elements);

                d_intermediate_output_complex[the_index].x += d_intermediate_output_complex[the_index2].x;
                d_intermediate_output_complex[the_index].y += d_intermediate_output_complex[the_index2].y;


            }
        }
        //}
        //}
        //}



    }

     /***************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
    __global__ void CUDAAddToOutputKernel(dim3 desiredGridDim, 
                                          int nsrcs, 
                                          int nslots, 
                                          int ntime, 
                                          int nfreq, 
                                          int num_matrix_elements, 
                                          double2* d_intermediate_output_complex, 
                                          double2* d_output_complex) {   
        
        // Axes:
        //   x: sources (reductor = 0)
        //   y: time
        //   z: freq

        dim3 actualBlockIdx = fromAdjustedToNormalDim(blockIdx, desiredGridDim.x);


        int xThreadIdx = ((actualBlockIdx.x*blockDim.x) + threadIdx.x);
        int yThreadIdx = ((actualBlockIdx.y*blockDim.y) + threadIdx.y);
        int zThreadIdx = ((actualBlockIdx.z*blockDim.z) + threadIdx.z);

        int s_i = xThreadIdx;
        int t = yThreadIdx;
        int f = zThreadIdx;
                 
        //printf("(%i, %i, %i)\n", s_i,t,f);      

        if (s_i == 0 && t < ntime && f < nfreq) {

            for( int j=0; j<num_matrix_elements; ++j ){

                int the_i_index = get_intermediate_output_index(s_i, nslots, 
                                                                t,   ntime,
                                                                f,   nfreq,
                                                                j,   num_matrix_elements);

                int the_index = get_output_index(t,  ntime,
                                                 f,  nfreq,
                                                 j,  num_matrix_elements);

                //printf("%i \t<-> %i\n");

                //d_intermediate_output_complex[the_i_index].x = 3;
                d_output_complex[the_index].x = d_intermediate_output_complex[the_i_index].x;
                 d_output_complex[the_index].y = d_intermediate_output_complex[the_i_index].y;

                //printf("(%i, %i, %i:%i) \tinput: %i \toutput:%i  \t threadIdx.y: %i  \t blockIdx.y %i \t actualBlockIdx.y %i\n", s_i,t,f,j, the_i_index, the_index, threadIdx.y, blockIdx.y, actualBlockIdx.y);

            }
        }

    }


     /***************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
    std::string runCUDAPointSourceVisibilityKernel(lmn_t* d_lmn, 
                                                   double2* d_B_complex, 
                                                   int nsrcs,
                                                   int nslots,
                                                   int nsrcs_per_slot,
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
                                                   double2* d_output_complex, 
                                                   int nOutputElements,
                                                   int NUM_MATRIX_ELEMENTS,
                                                   double _2pi_over_c,/*make this a constant variable rather than a parameter*/ 
                                                   std::complex<double> ** pout) {


        //cdebug(0) << "Executing Kernel" << endl;

        //double* h_smear_parameters[5] = {d_du, d_dv, d_dw, d_df_over_2, d_f_dt_over_2};
        //cudaMemcpyToSymbol(d_smear_parameters, h_smear_parameters, 5*sizeof(double*), 0, cudaMemcpyHostToDevice);

           
        printf("address of d_duvw: %i\n", d_duvw);

        cudaError_t error;
        error = cudaGetLastError  ();
        if (error != 0) {
            return std::string("CUDA constant memory copy error: ") + std::string(cudaGetErrorString (error));
        }

        int time_threads = 8;
        int freq_threads = 32;//64;
#ifdef SHARED_MEMORY
        freq_threads = 16; // HACK - on 1.x devices 64 threads means there won't be enough shared memory
#endif

        int remaining_slots = nslots;

        int src_offset = 0;

        while(remaining_slots != 0) {

            //=======================================================================================
            int nslots_this_run = nslots_per_run;
            if (remaining_slots < nslots_this_run)
                nslots_this_run = remaining_slots;

            remaining_slots -= nslots_this_run;
            
            printf("running %i slots at %i srcs per slot\n", nslots_this_run, nsrcs_per_slot);

            // Axes are:               srcs,            time,         freq

            int calcsPerProblem [3] = {nslots_this_run,  ntime,        nfreq};
            //int calcsPerGrid    [3] = {128,   1024,  64};

            int calcsPerBlock   [3] = {1,                time_threads, freq_threads}; // product of these will be the number of threads
            int calcsPerThread  [3] = {1,                1,     1}; // MUST = 1. so (1, 1, 1)

            printf("Number of calculation per grid: s) %i, t) %i, f) %i\n", calcsPerProblem[0], calcsPerProblem[1], calcsPerProblem[2]);

#ifdef SHARED_MEMORY
            //cudaFuncSetCacheConfig(CUDAPointSourceVisibilityKernel, cudaFuncCachePreferShared);

            size_t shared_memory = time_threads * freq_threads * NUM_MATRIX_ELEMENTS * sizeof(double2);
            printf("Requesting %i bytes of shared memory\n", shared_memory);
#endif


            for (int i = 0 ; i < 3 ;++i) {
                //if (calcsPerProblem[i] < calcsPerBlock[i]) return "Elements in \'Calculations per Grid\' must be less than or equal to the corresponding element in \'Calculations per Problem\'";
                //FailWhen (calcsPerGrid[i] < calcsPerBlock[i], "Elements in \'Calculations per Block\' must be less than or equal to the corresponding element in \'Calculations per Grid\'");
                if(calcsPerBlock[i] < calcsPerThread[i])
                    return "Elements in \'Calculations per Thread\' must be less than or equal to the corresponding element in \'Calculations per Block\'";
            }

            int gridSize  [3];
            int blockSize [3];
            for (int i = 0 ; i < 3 ;++i) {
                gridSize[i]  = ( (calcsPerProblem[i]-1) / calcsPerBlock[i]  ) + 1;
                blockSize[i] = (  (calcsPerBlock[i]-1)   / calcsPerThread[i] ) + 1;
            }

            //cdebug(0) << "calcsPerProblem: " << calcsPerProblem[0] << ", " << calcsPerProblem[1] << ", " << calcsPerProblem[2] << endl; 
            //cdebug(0) << "calcsPerGrid:    " << calcsPerGrid[0] << ", " << calcsPerGrid[1] << ", " << calcsPerGrid[2] << endl;
            //cdebug(0) << "calcsPerBlock:   " << calcsPerBlock[0] << ", " << calcsPerBlock[1] << ", " << calcsPerBlock[2] << endl;
            //cdebug(0) << "calcsPerThread:  " << calcsPerThread[0] << ", " << calcsPerThread[1] << ", " << calcsPerThread[2] << endl;


            dim3 gridDim (gridSize[0],  gridSize[1],  gridSize[2]);
            dim3 blockDim(blockSize[0], blockSize[1], blockSize[2]);
            dim3 threadDim(gridSize[0]*blockSize[0], gridSize[1]*blockSize[1], gridSize[2]*blockSize[2]);
            dim3 calcsPerThreadDim(calcsPerThread[0], calcsPerThread[1], calcsPerThread[2]);
            //int srcsDim = gridDim.x*blockDim.x*calcsPerThreadDim.x;
            //int timeDim = gridDim.y*blockDim.y*calcsPerThreadDim.y;
            //int freqDim = gridDim.z*blockDim.z*calcsPerThreadDim.z;      

            //cdebug(0) << "Running Kernel gridDim(" << gridDim.x << ", " << gridDim.y << ", " << gridDim.z << ") blockDim(" << blockDim.x << ", " << blockDim.y << ", " << blockDim.z << ")" << ") threadDim(" << threadDim.x << ", " << threadDim.y << ", " << threadDim.z << ")" << endl;

            dim3 adjGridDim = fromNormalToAdjustedDim(gridDim); 
            //nothingKernel<<<gridDim, blockDim>>>();
            //cudaThreadSynchronize();
            printf("adjgrid  %ix%ix%i\n", adjGridDim.x, adjGridDim.y, adjGridDim.z);
            printf("grid     %ix%ix%i\n", gridDim.x, gridDim.y, gridDim.z);
            printf("block    %ix%ix%i = %i threads\n", blockDim.x, blockDim.y, blockDim.z, blockDim.x* blockDim.y* blockDim.z);

            CUDAPointSourceVisibilityKernel<<<adjGridDim, blockDim
#ifdef SHARED_MEMORY
                , shared_memory
#endif
                                           >>> (gridDim, 
                                                d_lmn, 
                                                d_B_complex, 
                                                nsrcs, 
                                                nslots_this_run, 
                                                src_offset, 
                                                nsrcs_per_slot, 
                                                d_uvw,
                                                d_duvw,
                                                d_time, ntime, 
                                                d_freq, nfreq,
                                                d_df_over_2, d_f_dt_over_2,
                                                NUM_MATRIX_ELEMENTS, 
                                                d_intermediate_output_complex, 
                                                _2pi_over_c
                                                );
            cudaThreadSynchronize();

            // CUDAPointSourceVisibilityKernel_K<<<adjGridDim, blockDim
            //                                  >>> (gridDim, 
            //                                       d_lmn, 
            //                                       d_B_complex, 
            //                                       nsrcs, 
            //                                       src_offset, 
            //                                       nsrcs_per_slot, 
            //                                       d_uvw,
            //                                       d_time, ntime, 
            //                                       d_freq, nfreq,
            //                                       NUM_MATRIX_ELEMENTS, 
            //                                       d_intermediate_output_complex, 
            //                                       _2pi_over_c
            //                                      );


            // CUDAPointSourceVisibilityKernel_Smear<<<adjGridDim, blockDim
            //                                      >>> (gridDim, 
            //                                           d_lmn, 
            //                                           d_B_complex, 
            //                                           nsrcs, 
            //                                           nslots_this_run, 
            //                                           src_offset, 
            //                                           nsrcs_per_slot, 
            //                                           d_uvw,
            //                                           d_duvw,
            //                                           d_time, ntime, 
            //                                           d_freq, nfreq,
            //                                           d_df_over_2, d_f_dt_over_2,
            //                                           NUM_MATRIX_ELEMENTS, 
            //                                           d_intermediate_output_complex, 
            //                                           _2pi_over_c
            //                                          );
            error = cudaGetLastError  ();
            if (error != 0) {
                return std::string("CUDA runtime error: ") + std::string(cudaGetErrorString (error));
            }

            //=======================================================================================

            printf("Reduction\n");
            int level = 0;
            int reductors = nslots_this_run;
            while(reductors != 1) {

                if (reductors%2 == 1)
                    reductors ++;
                reductors>>=1;

                int gap = 1<<level;
                level++;

                printf("lvl: %i\n", level);
                printf("red: %i\n", reductors);
                printf("gap: %i\n", gap);
                printf("\n");

                
                gridDim.x = reductors;
                adjGridDim = fromNormalToAdjustedDim(gridDim); 
                
                printf("adjgrid  %ix%ix%i\n", adjGridDim.x, adjGridDim.y, adjGridDim.z);
                printf("grid     %ix%ix%i\n", gridDim.x, gridDim.y, gridDim.z);
                printf("block    %ix%ix%i = %i threads\n", blockDim.x, blockDim.y, blockDim.z, blockDim.x* blockDim.y* blockDim.z);
                CUDAPointSourceVisibilityReductionKernel<<<adjGridDim, blockDim>>> (gridDim, nsrcs, nslots_this_run, src_offset, nsrcs_per_slot,  ntime, nfreq, NUM_MATRIX_ELEMENTS, d_intermediate_output_complex, reductors, gap);
                cudaThreadSynchronize();

                cudaError_t error;
                error = cudaGetLastError  ();
                if (error != 0) 
                    return std::string("CUDA runtime error after reduction step: ") + std::string(cudaGetErrorString (error));


            } //while(reductors != 1) {
            
            //=======================================================================================
            printf("Adding to output array on device\n");
            printf("adjgrid  %ix%ix%i\n", adjGridDim.x, adjGridDim.y, adjGridDim.z);
            printf("grid     %ix%ix%i\n", gridDim.x, gridDim.y, gridDim.z);
            printf("block    %ix%ix%i = %i threads\n", blockDim.x, blockDim.y, blockDim.z, blockDim.x* blockDim.y* blockDim.z);

            gridDim.x = 1;
            adjGridDim = fromNormalToAdjustedDim(gridDim); 

            CUDAAddToOutputKernel<<<adjGridDim, blockDim>>> (gridDim, nsrcs, nslots_this_run, ntime, nfreq, NUM_MATRIX_ELEMENTS, d_intermediate_output_complex, d_output_complex);
            cudaThreadSynchronize();

            error = cudaGetLastError  ();
            if (error != 0) 
                return std::string("CUDA runtime error after output copy: ") + std::string(cudaGetErrorString (error));
            
            //-----------------------------------------------------------------------------------

            src_offset += nslots_this_run*nsrcs_per_slot;
        } // end while(remaining_srcs != 0)

        //printf("Copying from device to host\n");
         std::vector<double2> output_complex(ntime*nfreq*NUM_MATRIX_ELEMENTS);
        if (cudaMemcpy(&(output_complex[0]), d_output_complex, sizeof(double2)*ntime*nfreq*NUM_MATRIX_ELEMENTS , cudaMemcpyDeviceToHost) != cudaSuccess) {
            return "Memcopy error copying data from device (d_output_complex -> output_complex) : " + std::string(cudaGetErrorString (cudaGetLastError  ()));
        }
        printf("Copying to pout\n");
        for (int t = 0 ; t < ntime ; ++t) {
            for (int f = 0 ; f < nfreq ; ++f) {

                for( int j=0; j<NUM_MATRIX_ELEMENTS; ++j ){

                    int the_index = get_output_index(t,  ntime,
                                                     f,  nfreq,
                                                     j,  NUM_MATRIX_ELEMENTS);
                             
                    pout[j][t*nfreq + f] = 
                        std::complex<double>(
                            output_complex[the_index].x, 
                            output_complex[the_index].y
                            );
                    //cdebug(0) << "new total pout[" << j << "]([" << t << "][" << f << "]) " << pout[j][t*freqDim + f] << endl;
                }
            }
        }
        printf("Done\n");
        //========================================================================================


        return "";

    }


}

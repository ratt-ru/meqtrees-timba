
//#include <MeqNodes/ThrustPointSourceVisibility.h>


#include <TimBase/LofarTypedefs.h>


#include <cuda.h>
#include <cuda_runtime.h>

#include <thrust/host_vector.h>
#include <thrust/device_vector.h>

#include <thrust/iterator/zip_iterator.h>
#include <thrust/iterator/constant_iterator.h>
#include <thrust/iterator/permutation_iterator.h>
#include <thrust/iterator/transform_iterator.h>
#include <thrust/sort.h>
#include <thrust/for_each.h>

#include <vector>
#include <complex>
#include <string>

// HACKHACKAHCAHCAKHCKAHCKACHKACHKACHAKCHAAAAA get rid of....
#include <cstdio>

// this is a test comment to see if my git-svn thing works!

namespace Meq {


    /***************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
    struct index_flatten : public thrust::unary_function<int,int>
    {
        int inDim [4];
        int outDim [4];

        int inMults [4];
        int outMults [4];

          
        index_flatten(int aInDim, int bInDim, int cInDim, int dInDim, int aOutDim, int bOutDim, int cOutDim, int dOutDim){
            inDim[0] = aInDim;
            inDim[1] = bInDim;
            inDim[2] = cInDim;
            inDim[3] = dInDim;
            outDim[0] = aOutDim;
            outDim[1] = bOutDim;
            outDim[2] = cOutDim;
            outDim[3] = dOutDim;

            outMults[0] = outDim[0]*outDim[1]*outDim[2]*outDim[3];
            outMults[1] = outDim[1]*outDim[2]*outDim[3];
            outMults[2] = outDim[2]*outDim[3];
            outMults[3] = outDim[3];

            inMults[0] = inDim[0]*inDim[1]*inDim[2]*inDim[3];
            inMults[1] = inDim[1]*inDim[2]*inDim[3];
            inMults[2] = inDim[2]*inDim[3];
            inMults[3] = inDim[3];

        }

          
        __host__ __device__
        int operator()(int x) const
            {
                int total = 0;
                int out [4];
                out[0] = (x);
                out[0] /= outMults[1];

                total += out[0]*outMults[1];

                out[1] = (x - total);
                out[1] /= outMults[2];

                total += out[1]*outMults[2];

                out[2] = (x - total);
                out[2] /= outMults[3];

                total += out[2]*outMults[3];

                out[3] = (x - total);

                for (int i = 0 ; i < 4 ; i++) {
                    if (inDim[i] == 1)
                        out[i] = 0;
                }

                return out[0]*inMults[1] + out[1]*inMults[2] + out[2]*inMults[3] + out[3];

            }
    };


    /***************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/

    typedef thrust::tuple<double, // freq
                          double, // u
                          double, // v
                          double, // w
                          //double3, // lmn
                          double, // l
                          double, // m
                          double, // n
                          double2 // B
                          > PSVTuple;

    struct psv_functor : public thrust::unary_function<PSVTuple,double2>
    {
        double _2pi_over_c;//-casa::C::_2pi / casa::C::c;

        psv_functor(double _2pi_o_c) {
            _2pi_over_c = _2pi_o_c;
        }

        template <typename Tuple>
        __host__ __device__
        double2 operator()(Tuple t)
        {
            //double argument = _2pi_over_c*d_freq[f]*(d_u[t]*d_lmn[s*3+0]+d_v[t]*d_lmn[s*3+1]+d_w[t]*d_lmn[s*3+2]);
            //double realVal = sin(argument);
            //double imagVal = cos(argument);
            //d_output_complex[the_index+0] =  + d_B_complex[b_index*2+1]*realVal + d_B_complex[b_index*2+0]*imagVal;
            //d_output_complex[the_index+1] =  + d_B_complex[b_index*2+1]*imagVal - d_B_complex[b_index*2+0]*realVal;

            // D[i] = A[i] + B[i] * C[i];
            //thrust::get<8>(t) = thrust::get<0>(t);// + thrust::get<1>(t) * thrust::get<2>(t);

            #define FREQ thrust::get<0>(t)
            #define D_U thrust::get<1>(t)
            #define D_V thrust::get<2>(t)
            #define D_W thrust::get<3>(t)
            //#define D_LMN thrust::get<4>(t)
            //#define D_B thrust::get<5>(t)
            #define D_L thrust::get<4>(t)
            #define D_M thrust::get<5>(t)
            #define D_N thrust::get<6>(t)
            #define D_B thrust::get<7>(t)
            
            double argument = _2pi_over_c*FREQ*(D_U*D_L+D_V*D_M+D_W*D_N);
            double realVal = sin(argument);
            double imagVal = cos(argument);

            double2 ret;
            ret.x = D_B.y*realVal + D_B.x*imagVal;
            ret.y = D_B.y*imagVal + D_B.x*realVal;

            return ret;
        }
    };


    struct double2_add {

        __host__ __device__
        double2 operator()(const double2& a, const double2& b) const {

            double2 c;
            c.x = a.x + b.x;
            c.y = a.y + b.y;
            return c;
        }

    };

    /***************************************************************************
     **
     ** Author: Richard Baxter
     **
     ****************************************************************************/
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
                                                   double _2pi_over_c) {

        
      typedef thrust::device_vector<double>::iterator DoubleIterator;
      typedef thrust::device_vector<double2>::iterator DComplexIterator;
      typedef thrust::device_vector<double3>::iterator D3VectorIterator;
        
      typedef thrust::counting_iterator<int> IntCountIterator;

      IntCountIterator counter(0);

      //std::cout << "start of thrusting" << std::endl;

      // j   s   f   t |(B) 
      // 0   0   0   0 | 0
      // 0   0   0   1 | 0
      // 0   0   1   0 | 1
      // 0   0   1   1 | 1
      // 0   0   2   0 | 2
      // 0   0   2   1 | 2
      // 0   1   0   0 | 3
      // 0   1   0   1 | 3
      // 0   1   1   0 | 4
      // 0   1   1   1 | 4
      // 0   1   2   0 | 5
      // 0   1   2   1 | 5
      // 0   2   0   0 | 6
      // ...
      // 1   0   0   0 | 1*nsrc*nfreq*ntime
      // 1   0   0   1 | 1*nsrc*nfreq*ntime
      // 1   0   1   0 | 1*nsrc*nfreq*ntime + 1
      // ...      
      // 2   0   0   0 | 2*nsrc*nfreq*ntime
      // ... 
      // 1   0   1   0 | 1*nsrc*nfreq*ntime + 1
      // ...      
      // 2   0   0   0 | 2*nsrc*nfreq*ntime
      // ...      

      int unreduced_output_size = 4*nfreq*ntime*nsrcs;
      int reduced_output_size   = 4*nfreq*ntime;

      // "[]" means indexing and access like normal, "()" means the index will be flatened
      // output will be indexed on [p]([freq][time])
      // processing will operate on one of each of ([j][nsrc][freq][time])
      // B will be indexed on ([j][nsrc][freq]) - so access muct be expanded to include [time]

      typedef thrust::transform_iterator<index_flatten, IntCountIterator> TransformedIndexIterator;
      TransformedIndexIterator B_index_trans_it   (counter, index_flatten(4,1,nfreq,nsrcs,  4,ntime,nfreq,nsrcs));
      TransformedIndexIterator j_index_trans_it   (counter, index_flatten(4,1,1,1,          4,ntime,nfreq,nsrcs));
      TransformedIndexIterator time_index_trans_it(counter, index_flatten(1,ntime,1,1,      4,ntime,nfreq,nsrcs));
      TransformedIndexIterator freq_index_trans_it(counter, index_flatten(1,1,nfreq,1,      4,ntime,nfreq,nsrcs));
      TransformedIndexIterator src_index_trans_it (counter, index_flatten(1,1,1,nsrcs,      4,ntime,nfreq,nsrcs));

      TransformedIndexIterator jft_index_trans_it (counter, index_flatten(4,ntime,nfreq,1,  4,ntime,nfreq,nsrcs));

      // Need inputs to out[j]([f][t]) from unreduced_out([j][f][t][s]) from freq[f] u[t] v[t] w[t] l[s] m[s] n[s] b([j][s][f]) 

      typedef thrust::permutation_iterator<DoubleIterator, TransformedIndexIterator> PermuteTransformDoubleIterator;
      typedef thrust::permutation_iterator<DComplexIterator, TransformedIndexIterator> PermuteTransformDComplexIterator;
      typedef thrust::permutation_iterator<D3VectorIterator, TransformedIndexIterator> PermuteTransformD3VectorIterator;

      PermuteTransformDoubleIterator perm_freq_it(d_freq.begin(), freq_index_trans_it);
      PermuteTransformDoubleIterator perm_u_it   (d_u.begin(),    time_index_trans_it);
      PermuteTransformDoubleIterator perm_v_it   (d_v.begin(),    time_index_trans_it);
      PermuteTransformDoubleIterator perm_w_it   (d_w.begin(),    time_index_trans_it);
      //PermuteTransformD3VectorIterator perm_lmn_it   (d_lmn.begin(),    src_index_trans_it);
      PermuteTransformDoubleIterator perm_l_it   (d_l.begin(),    src_index_trans_it);
      PermuteTransformDoubleIterator perm_m_it   (d_m.begin(),    src_index_trans_it);
      PermuteTransformDoubleIterator perm_n_it   (d_n.begin(),    src_index_trans_it);
      PermuteTransformDComplexIterator perm_B_it (d_b.begin(),    B_index_trans_it);


      typedef thrust::tuple<PermuteTransformDoubleIterator,   // freq
                            PermuteTransformDoubleIterator,   // u
                            PermuteTransformDoubleIterator,   // v
                            PermuteTransformDoubleIterator,   // w
                            //PermuteTransformD3VectorIterator,   // lmn
                            PermuteTransformDoubleIterator,   // l
                            PermuteTransformDoubleIterator,   // m
                            PermuteTransformDoubleIterator,   // n
                            PermuteTransformDComplexIterator//, // B 
                            //DoubleIterator                    // unreduced_output
                            > // result
          PSVIteratorTuple;


      typedef thrust::zip_iterator<PSVIteratorTuple> PSVZipIterator;

      PSVZipIterator data_zip_it (thrust::make_tuple(
                                      perm_freq_it,
                                      perm_u_it,
                                      perm_v_it,
                                      perm_w_it,
                                      //perm_lmn_it,
                                      perm_l_it,
                                      perm_m_it,
                                      perm_n_it,
                                      perm_B_it//,
                                      //d_unreduced_output.begin()
                                      ));
      
      PSVZipIterator data_zip_it_end (thrust::make_tuple(
                                          perm_freq_it+unreduced_output_size,
                                          perm_u_it+unreduced_output_size,
                                          perm_v_it+unreduced_output_size,
                                          perm_w_it+unreduced_output_size,
                                          //perm_lmn_it+unreduced_output_size,
                                          perm_l_it+unreduced_output_size,
                                          perm_m_it+unreduced_output_size,
                                          perm_n_it+unreduced_output_size,
                                          perm_B_it+unreduced_output_size//,
                                          //d_unreduced_output.end()
                                          ));

      std::cout << "created iterators" << std::endl;

      thrust::device_vector<double2> d_unreduced_output(unreduced_output_size);

      std::cout << "device temp unreduced output alloced ("<< unreduced_output_size << "*" <<sizeof(double2) << ") = "<< (unreduced_output_size*sizeof(double2)) << " bytes" << std::endl;

      thrust::transform (data_zip_it, data_zip_it_end, d_unreduced_output.begin(), psv_functor(_2pi_over_c));

      std::cout << "calc transformed" << std::endl;
      //thrust::transform_iterator<psv_functor ,PSVZipIterator> psv_transform_it(data_zip_it, psv_functor(_2pi_over_c));

      thrust::device_vector<double2> d_output(reduced_output_size);
      thrust::device_vector<int> d_output_keys(reduced_output_size);
      std::cout << "device output + keys alloced" << std::endl;


      size_t avail;
      size_t total;
      cudaMemGetInfo( &avail, &total );
      size_t used = total - avail;

      std::cout << "Device memory total: " << total << std::endl;
      std::cout << "Device memory avail: " << avail << std::endl;
      std::cout << "Device memory used:  " << used << std::endl;

      size_t will_use = (unreduced_output_size*sizeof(double2))+(unreduced_output_size*3*sizeof(unsigned int));

      std::cout << "reduction will temporarily alloc at least ("<< unreduced_output_size << "*" <<sizeof(double2) << " + " << unreduced_output_size << "*3*" << sizeof(unsigned int) << ") = "<< will_use << " bytes" << std::endl;

      if (will_use > avail) {

          char a [256];
          sprintf(a,"Not enough memory for reduce by key (%u bytes available, %u bytes needed)", avail, will_use);
          return std::string(a);

      }

      thrust::equal_to<int> equal_pred;
      thrust::reduce_by_key(jft_index_trans_it,
                            jft_index_trans_it + unreduced_output_size,
                            d_unreduced_output.begin(),
                            //thrust::make_transform_iterator(data_zip_it,  
                            //                                psv_functor(_2pi_over_c)
                            //    ),
                            //psv_transform_it,
                            d_output_keys.begin(),
                            d_output.begin(),
                            equal_pred,
                            double2_add()
                            );
      std::cout << "key reduced with reduce_by_key" << std::endl;

      h_output = d_output;



        //------------start old----------------

      // thrust::host_vector<double2> h_unreduced_output(d_unreduced_output);

      // for (int i = 0 ; i < reduced_output_size ; i++) {
      //     h_output[i].x = 0;
      //     h_output[i].y = 0;
      //     for (int s = 0 ; s < nsrcs ; s++){
      //         h_output[i].x += h_unreduced_output[(i*nsrcs)+s].x;
      //         h_output[i].y += h_unreduced_output[(i*nsrcs)+s].y;
      //     }
      //     }

        //------------end old------------------
      

      // NOTE: using make_transform_iterator(data_zip_it, psv_functor(_2pi_over_c)) should be more efficient since it will transform in place rather than doing a transform run and store, then a read and reduce. Owing to the number of parameters, the formal parameter space overflows, tried to condense l, m & n into a double3 vector instead of 3 double vectors but same problem arrises (I thought the double3 would use one pointer space - instead of 3 - but it seems it passes the double3 directly). Due to the double3 vector not collesing as well as 3 double vectors, it goes slightly slower (0.13 sec/tile vs. 0.12 sec/tile type of difference). So I'm just returning to using 3 double vectors and 2 passes.

      return "";
      
    }

}

//# ThrustPointSourceVisibility.cc: The point source DFT component for a station
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
//# $Id: ThrustPointSourceVisibility.cc 8270 2011-07-06 12:17:23Z oms $


#include <MeqNodes/ThrustPointSourceVisibility.h>
#include <DMI/AID-DMI.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casacore/casa/BasicSL/Constants.h>

// #include <string>               

// #include <thrust/host_vector.h>
// #include <thrust/device_vector.h>

// #include <vector>

namespace Meq {

InitDebugContext(ThrustPointSourceVisibility,"THRUSTPSV");
  
  
using namespace VellsMath;

const HIID child_labels[] = { AidLMN,AidB,AidUVW };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);



ThrustPointSourceVisibility::ThrustPointSourceVisibility()
: TensorFunction(num_children,child_labels)
{
  // dependence on frequency
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

ThrustPointSourceVisibility::~ThrustPointSourceVisibility()
{}

const LoShape shape_3vec(3),shape_2x3(2,3);

LoShape ThrustPointSourceVisibility::getResultDims (const vector<const LoShape *> &input_dims)
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

  uvw_size_ = uvw.size();

  num_sources_ = lmn[0];
  // result is a 2x2 matrix 
  return LoShape(2,2);
}



#ifdef STRIP_CUDA
void ThrustPointSourceVisibility::evaluateTensors (std::vector<Vells> & out,
     const std::vector<std::vector<const Vells *> > &args )
{
   
    FailWhen(true,"CUDA and Thrust required in order to use this node"); 
}

#else
void ThrustPointSourceVisibility::evaluateTensors (std::vector<Vells> & out,
     const std::vector<std::vector<const Vells *> > &args )
{
  // cells
  const Cells & cells = resultCells();
  const double _2pi_over_c = -casacore::C::_2pi / casacore::C::c;
  // the frequency and time axis
  int nfreq = cells.ncells(Axis::FREQ);
  int ntime = cells.ncells(Axis::TIME);
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
  if (uvw_size_ == 2) {
      const Vells & dvu = *(args[2][3]);
      const Vells & dvv = *(args[2][4]);
      const Vells & dvw = *(args[2][5]);
      FailWhen(dvu.shape() != timeshape || dvv.shape() != timeshape || dvw.shape() != timeshape,"expecting UVWs derivatives that are a vector in time");

      //TODO implement smearing
  }
  // these will be vectors of ntime points each
  const double *pu = vu.realStorage();
  const double *pv = vv.realStorage();
  const double *pw = vw.realStorage();

  
  // allocate storage for results, and get pointers to storage
  const int NUM_MATRIX_ELEMENTS = 4;
  dcomplex * pout[NUM_MATRIX_ELEMENTS];


  for( int j=0; j<4; j++ )
  {
    out[j] = Vells(numeric_zero<dcomplex>(),timefreqshape);
    pout[j] = out[j].complexStorage();
    // pout[j] points to an NTIME x NFREQ array
  }

  int nsrcs = num_sources_; // I just prefer this name to num_sources_


  // ==================================================================================================


  int unreduced_output_size = 4*nfreq*ntime*nsrcs;
  int reduced_output_size   = 4*nfreq*ntime;
  
  size_t avail;
  size_t total;
  cudaMemGetInfo( &avail, &total );
  size_t used = total - avail;

  size_t will_use_input = (sizeof(double)*((ntime*3) + nfreq + nsrcs*3)) + (sizeof(double2)*nsrcs*NUM_MATRIX_ELEMENTS*nfreq);
  size_t will_use_intermediate = (sizeof(double2)*unreduced_output_size) + (sizeof(double2)*reduced_output_size) + (sizeof(int)*reduced_output_size);
  size_t will_use_reduce_by_key = (unreduced_output_size*sizeof(double2))+(unreduced_output_size*3*sizeof(unsigned int));
  size_t will_use_total = will_use_input + will_use_intermediate + will_use_reduce_by_key;
  
  cdebug(0) << "required for inputs (" << sizeof(double) << "*(" << ntime << "*3+" << nfreq << " + " << nsrcs << "*3)) + (" << sizeof(double2) << "*" << nsrcs << "*" << NUM_MATRIX_ELEMENTS << "*" << nfreq << ") = " << will_use_input << " bytes" << endl;  
  cdebug(0) << "required for intermediate ((" << sizeof(double2) << "*" << unreduced_output_size  << ") + (" << sizeof(double2) << "*" << reduced_output_size << ") + (" << sizeof(int) << "*" << reduced_output_size << ")) = " << will_use_intermediate << " bytes" << endl;
  cdebug(0) << "required for reduce_by_key (" << unreduced_output_size << "*" << sizeof(double2) << " + " << unreduced_output_size << "*3*" << sizeof(unsigned int) << ") = "<< will_use_reduce_by_key << " bytes" << std::endl;

  cdebug(0) << "required for all (" << will_use_input << " + " << will_use_intermediate << " + " <<  will_use_reduce_by_key << " = " << will_use_total << endl;

  cdebug(0) << avail << " bytes available (available after = " << (avail-will_use_total)<<" bytes)" << endl;

  char errorChar [256];
  sprintf(errorChar, "Not enough memory on GPU device, requires %u bytes, only %u bytes available", will_use_total, avail);

  FailWhen(avail < will_use_total, errorChar);

  thrust::device_vector<double> d_u (pu, pu + ntime);
  thrust::device_vector<double> d_v (pv, pv + ntime);
  thrust::device_vector<double> d_w (pw, pw + ntime);
  thrust::device_vector<double> d_freq (freq_data, freq_data + nfreq);
  //thrust::device_vector<double> d_time (time_data, time_data + ntime);

      
  cdebug(0) << "device uvw + f alloced" << endl;
  //thrust::host_vector<double3> h_lmn (nsrcs);
  thrust::host_vector<double> h_l (nsrcs);
  thrust::host_vector<double> h_m (nsrcs);
  thrust::host_vector<double> h_n (nsrcs);
  thrust::host_vector<double2> h_b(nsrcs*NUM_MATRIX_ELEMENTS*nfreq);

  cdebug(0) << "host lmn + b alloced" << endl;
  for( int isrc=0; isrc < nsrcs; isrc++ )
  {
      //cdebug(0) << "src number " << isrc<<"/"<<num_sources_ << endl;


      // get the LMNs for this source
      const Vells & vl = *(args[0][isrc*3]);
      const Vells & vm = *(args[0][isrc*3+1]);
      const Vells & vn = *(args[0][isrc*3+2]);
      FailWhen(!vl.isScalar() || !vm.isScalar() || !vn.isScalar(),"expecting scalar LMNs");
      double l = vl.as<double>();
      double m = vm.as<double>();
      double n = vn.as<double>();
          
      h_l[isrc] = l;
      h_m[isrc] = m;
      h_n[isrc] = n;
          
      //h_lmn[isrc].x = l;
      //h_lmn[isrc].y = m;
      //h_lmn[isrc].z = n;


      for( int j=0; j<NUM_MATRIX_ELEMENTS; j++ )
      {
          //cdebug(0) << "j number " << j<<"/"<<NUM_MATRIX_ELEMENTS << endl;
          const Vells &b = *(args[1][isrc*NUM_MATRIX_ELEMENTS + j]);
          if( b.isNull() )
          {
              for (int f = 0 ; f < nfreq ; f++) {
                  h_b[(j*nfreq + f)*nsrcs + isrc].x = 0;
                  h_b[(j*nfreq + f)*nsrcs + isrc].y = 0;
                  //cdebug(0) << ((j*nsrcs + isrc)*nfreq + f) << endl;
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
                  h_b[(j*nfreq + f)*nsrcs + isrc].x = b_complex.real();
                  h_b[(j*nfreq + f)*nsrcs + isrc].y = b_complex.imag();
                  //cdebug(0) << ((j*nsrcs + isrc)*nfreq + f) << endl;
              }
          }
          else { // is a vector of complex values
              const dcomplex* b_complex_vec = b.complexStorage();
              for (int f = 0 ; f < nfreq ; f++) {
                  h_b[(j*nfreq + f)*nsrcs + isrc].x = b_complex_vec[f].real();
                  h_b[(j*nfreq + f)*nsrcs + isrc].y = b_complex_vec[f].imag();
                  //cdebug(0) << ((j*nsrcs + isrc)*nfreq + f) << endl;
              }
          }
      }
  }

  thrust::device_vector<double2> d_b (h_b);
  //thrust::device_vector<double3>  d_lmn (h_lmn);
  thrust::device_vector<double>  d_l (h_l);
  thrust::device_vector<double>  d_m (h_m);
  thrust::device_vector<double>  d_n (h_n);

  cdebug(0) << "device lmn + b alloced" << endl;

  //thrust::host_vector<double2>  h_unreduced_output (4*nsrc*nfreq*ntime);
  //thrust::device_vector<double2> d_unreduced_output (4*nsrc*nfreq*ntime);
  thrust::host_vector<double2>  h_output (4*nfreq*ntime);
  cdebug(0) << "host output alloced" << endl;
      
  std::string errorString = runCUDAPointSourceVisibilityThrust(nsrcs,
                                                         nfreq,
                                                         ntime,
                                                         d_freq,
                                                         d_u,
                                                         d_v,
                                                         d_w,
                                                         //d_lmn,
                                                         d_l,
                                                         d_m,
                                                         d_n,
                                                         d_b,
                                                         h_output,
                                                         _2pi_over_c);


  if (errorString != "") {
      

      cdebug(0) << "kernel ran sucessfully" << endl;

      //thrust::host_vector<double2>  h_unreduced_output (d_unreduced_output);
      //h_output = d_output;




      for( int j=0; j<NUM_MATRIX_ELEMENTS; ++j ){
          for( int d=0 ; d <nfreq*ntime ; d++ ){

              pout[j][d] += 
                  std::complex<double>(
                      h_output[d].x, 
                      h_output[d].y
                      );
              // TODO try use memcpy instead, should be faster than the one by one copy
              //cdebug(0) << "new total pout[" << j << "]([" << t << "][" << f << "]) " << pout[j][t*freqDim + f] << endl;
          }
      }
      cdebug(0) << "copied back results" << endl;

  }

  FailWhen(errorString != "", errorString);
  //==================================================================================================

}
#endif


} // namespace Meq

//# FFTBrick.cc: Stored parameter with polynomial coefficients
//#
//# Copyright (C) 2002
//# ASTRON (Netherlands Foundation for Research in Astronomy)
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

#include <MeqNodes/FFTBrick.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
//#include <casa/aips.h>
//#include <casa/Arrays.h>
//#include <casa/Arrays/Vector.h>
//#include <casa/BasicSL/String.h>
//#include <images/Images/ImageInterface.h>
//#include <images/Images/PagedImage.h>
//#include <images/Images/ImageFFT.h>
//#include <images/Images/TempImage.h>
//#include <coordinates/Coordinates/CoordinateUtil.h>
//#include <coordinates/Coordinates/CoordinateSystem.h>
//#include <lattices/Lattices/LatticeIterator.h>
//#include <lattices/Lattices/Lattice.h>
//#include <casa/BasicMath/Math.h>
//#include <casa/BasicSL/Constants.h>
#include <complex.h>
#include <fftw3.h>

namespace Meq {
  

  FFTBrick::FFTBrick()
    :
    _uvppw(2.0)
  {
    // For now these axes are defined in the PatchComposer Node.
    //Axis::addAxis("U");
    //Axis::addAxis("V");
  };
  
  FFTBrick::~FFTBrick()
  {
  };
  
  int FFTBrick::getResult (Result::Ref &resref,
			  const std::vector<Result::Ref> &childres,
			  const Request &request,bool newreq){

    // Get the Cells (Time, Freq, L, M) of the child
    Cells child_cells = childres.at(0)->cells();
    
    if ( child_cells.isDefined(Axis::axis("L")) && child_cells.isDefined(Axis::axis("M")) ){

      // Construct the Result Cells from the Child Cells
      int nf = child_cells.ncells(Axis::FREQ);

      const int nl = child_cells.ncells(Axis::axis("L"));
      const int nu = int(_uvppw*nl)+1;

      const int nm = child_cells.ncells(Axis::axis("M"));
      const int nv = int(_uvppw*nm)+1;

      // Make a new Result: 4 Stokes planes x 4 Interpolation planes
      resref <<= new Result(16);

      VellSet& vs0 = resref().setNewVellSet(0);
      VellSet& vs1 = resref().setNewVellSet(1);
      VellSet& vs2 = resref().setNewVellSet(2);
      VellSet& vs3 = resref().setNewVellSet(3);

      VellSet& vs0u = resref().setNewVellSet(4);
      VellSet& vs1u = resref().setNewVellSet(5);
      VellSet& vs2u = resref().setNewVellSet(6);
      VellSet& vs3u = resref().setNewVellSet(7);

      VellSet& vs0v = resref().setNewVellSet(8);
      VellSet& vs1v = resref().setNewVellSet(9);
      VellSet& vs2v = resref().setNewVellSet(10);
      VellSet& vs3v = resref().setNewVellSet(11);

      VellSet& vs0uv = resref().setNewVellSet(12);
      VellSet& vs1uv = resref().setNewVellSet(13);
      VellSet& vs2uv = resref().setNewVellSet(14);
      VellSet& vs3uv = resref().setNewVellSet(15);

      // For now, use the L & M axes instead of U & V (Visualisation)
      int size = std::max(Axis::axis("L"),Axis::axis("M"))+1;

      Vells::Shape shape;
      Axis::degenerateShape(shape,size);
      shape[Axis::axis("L")] = nu;
      shape[Axis::axis("M")] = nv;
      shape[Axis::FREQ] = nf;

      // change 'false' into 'true' to actually fill the vells
      Vells& vells0 = vs0.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells1 = vs1.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells2 = vs2.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells3 = vs3.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells0u = vs0u.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells1u = vs1u.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells2u = vs2u.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells3u = vs3u.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells0v = vs0v.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells1v = vs1v.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells2v = vs2v.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells3v = vs3v.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells0uv = vs0uv.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells1uv = vs1uv.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells2uv = vs2uv.setValue(new Vells(dcomplex(0.0),shape,true));
      Vells& vells3uv = vs3uv.setValue(new Vells(dcomplex(0.0),shape,true));

      // An absent axis shows up with dimension 1 in the Vells Array
      int nt = child_cells.ncells(Axis::TIME);
      if (nt==0) nt=1;

      // Get the Child Data
      Vells vells11 = childres.at(0) -> vellSet(0).getValue();
      Vells vells12 = childres.at(0) -> vellSet(1).getValue();
      Vells vells21 = childres.at(0) -> vellSet(2).getValue();
      Vells vells22 = childres.at(0) -> vellSet(3).getValue();

      // Make a larger Vells to be used as input for the FFT
      const blitz::Array<dcomplex,3> & arr0_in = vells11.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      const blitz::Array<dcomplex,3> & arr1_in = vells12.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      const blitz::Array<dcomplex,3> & arr2_in = vells21.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      const blitz::Array<dcomplex,3> & arr3_in = vells22.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      Vells pad0 = Vells(dcomplex(0.0),shape,true);
      Vells pad1 = Vells(dcomplex(0.0),shape,true);
      Vells pad2 = Vells(dcomplex(0.0),shape,true);
      Vells pad3 = Vells(dcomplex(0.0),shape,true);     

      blitz::Array<dcomplex,3> arr0 = pad0.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> arr1 = pad1.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> arr2 = pad2.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> arr3 = pad3.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      // Rearrange the data and pad with zeros
      int nl1 = (nl-1)/2;
      int nm1 = (nm-1)/2;

      for (int k=0; k<nf; k++){

	for (int i=0; i<nl1+1; i++){
	  for (int j=0; j<nm1+1;j++){	    
	    arr0(k,i,j) = arr0_in(k,nl1+i,nm1+j);
	    arr1(k,i,j) = arr1_in(k,nl1+i,nm1+j);
	    arr2(k,i,j) = arr2_in(k,nl1+i,nm1+j);
	    arr3(k,i,j) = arr3_in(k,nl1+i,nm1+j);
	  };
	};

	for (int i=0; i<nl1; i++){
	  for (int j=0; j<nm1+1;j++){	    
	    arr0(k,nu-nl1+i,j) = arr0_in(k,i,nm1+j);
	    arr1(k,nu-nl1+i,j) = arr1_in(k,i,nm1+j);
	    arr2(k,nu-nl1+i,j) = arr2_in(k,i,nm1+j);
	    arr3(k,nu-nl1+i,j) = arr3_in(k,i,nm1+j);
	  };
	};

	for (int i=0; i<nl1+1; i++){
	  for (int j=0; j<nm1;j++){	    
	    arr0(k,i,nv-nm1+j) = arr0_in(k,nl1+i,j);
	    arr1(k,i,nv-nm1+j) = arr1_in(k,nl1+i,j);
	    arr2(k,i,nv-nm1+j) = arr2_in(k,nl1+i,j);
	    arr3(k,i,nv-nm1+j) = arr3_in(k,nl1+i,j);
	  };
	};

	for (int i=0; i<nl1; i++){
	  for (int j=0; j<nm1;j++){	    
	    arr0(k,nu-nl1+i,nv-nm1+j) = arr0_in(k,i,j);
	    arr1(k,nu-nl1+i,nv-nm1+j) = arr1_in(k,i,j);
	    arr2(k,nu-nl1+i,nv-nm1+j) = arr2_in(k,i,j);
	    arr3(k,nu-nl1+i,nv-nm1+j) = arr3_in(k,i,j);
	  };
	};


      };

      // Prepare the FFT
      fftw_complex *in1, *out1, *in2, *out2, *in3, *out3, *in4, *out4;
      fftw_plan p;

      Vells oad0 = Vells(dcomplex(0.0),shape,true);
      Vells oad1 = Vells(dcomplex(0.0),shape,true);
      Vells oad2 = Vells(dcomplex(0.0),shape,true);
      Vells oad3 = Vells(dcomplex(0.0),shape,true);    

      // The temporary mapping of the u-v data onto the l-m axes (see above) has no effect here
      // A 2D FFT over the L and M planes (nl=nu, nm=nv) 
      int rank = 2;
      fftw_iodim dims[rank];
      dims[1].n = nv;
      dims[1].is = 1;
      dims[1].os = 1;
      dims[0].n = nu;
      dims[0].is = nv;
      dims[0].os = nv;     

      // Iterate over the Time and Freq planes
      int howmany_rank = 2;
      fftw_iodim howmany_dims[howmany_rank];
      howmany_dims[0].n = nt;
      howmany_dims[0].is = nf*nu*nv;
      howmany_dims[0].os = nf*nu*nv;
      howmany_dims[1].n = nf;
      howmany_dims[1].is = nu*nv;
      howmany_dims[1].os = nu*nv;

      // Cast Vells data pointers into the input and output pointers
      in1 = static_cast<fftw_complex*>(const_cast<void*>(pad0.getConstDataPtr()));
      out1 = static_cast<fftw_complex*>(oad0.getDataPtr());

      // The FFT plan definition
      p = fftw_plan_guru_dft(rank,dims,howmany_rank, howmany_dims,in1,out1,FFTW_FORWARD,FFTW_ESTIMATE);

      // Execution of the FFT
      fftw_execute(p);

      // Cast Vells data pointers into the input and output pointers
      in2 = static_cast<fftw_complex*>(const_cast<void*>(pad1.getConstDataPtr()));
      out2 = static_cast<fftw_complex*>(oad1.getDataPtr());

      // The FFT plan definition
      p = fftw_plan_guru_dft(rank,dims,howmany_rank, howmany_dims,in2,out2,FFTW_FORWARD,FFTW_ESTIMATE);

      // Execution of the FFT
      fftw_execute(p);

      // Cast Vells data pointers into the input and output pointers
      in3 = static_cast<fftw_complex*>(const_cast<void*>(pad2.getConstDataPtr()));
      out3 = static_cast<fftw_complex*>(oad2.getDataPtr());

      // The FFT plan definition
      p = fftw_plan_guru_dft(rank,dims,howmany_rank, howmany_dims,in3,out3,FFTW_FORWARD,FFTW_ESTIMATE);

      // Execution of the FFT
      fftw_execute(p);

      // Cast Vells data pointers into the input and output pointers
      in4 = static_cast<fftw_complex*>(const_cast<void*>(pad3.getConstDataPtr()));
      out4 = static_cast<fftw_complex*>(oad3.getDataPtr());

      // The FFT plan definition
      p = fftw_plan_guru_dft(rank,dims,howmany_rank, howmany_dims,in4,out4,FFTW_FORWARD,FFTW_ESTIMATE);

      // Execution of the FFT
      fftw_execute(p);

      // Destroy the plan 
      if(p) fftw_destroy_plan(p);

      // Rearrange the uv-data

      //blitz::Array<dcomplex,3> brr0 = vells0.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      //blitz::Array<dcomplex,3> brr1 = vells1.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      //blitz::Array<dcomplex,3> brr2 = vells2.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      //blitz::Array<dcomplex,3> brr3 = vells3.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      blitz::Array<dcomplex,3> fft0 = vells0.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft1 = vells1.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft2 = vells2.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft3 = vells3.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      blitz::Array<dcomplex,3> crr0 = oad0.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> crr1 = oad1.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> crr2 = oad2.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> crr3 = oad3.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      int nu1 = nu/2;
      int nv1 = nv/2;

      for (int k=0; k<nf; k++){

	for (int i=0; i<nu1; i++){
	  for (int j=0; j<nv1;j++){	    
	    fft0(k,i,j) = crr0(k,nu-nu1+i,nv-nv1+j);
	    fft1(k,i,j) = crr1(k,nu-nu1+i,nv-nv1+j);
	    fft2(k,i,j) = crr2(k,nu-nu1+i,nv-nv1+j);
	    fft3(k,i,j) = crr3(k,nu-nu1+i,nv-nv1+j);
	  };
	};

	for (int i=0; i<nu1; i++){
	  for (int j=0; j<nv-nv1;j++){	    
	    fft0(k,i,nv1+j) = crr0(k,nu-nu1+i,j);
	    fft1(k,i,nv1+j) = crr1(k,nu-nu1+i,j);
	    fft2(k,i,nv1+j) = crr2(k,nu-nu1+i,j);
	    fft3(k,i,nv1+j) = crr3(k,nu-nu1+i,j);
	  };
	};

	for (int i=0; i<nu-nu1; i++){
	  for (int j=0; j<nv1;j++){	    
	    fft0(k,nu1+i,j) = crr0(k,i,nv-nv1+j);
	    fft1(k,nu1+i,j) = crr1(k,i,nv-nv1+j);
	    fft2(k,nu1+i,j) = crr2(k,i,nv-nv1+j);
	    fft3(k,nu1+i,j) = crr3(k,i,nv-nv1+j);
	  };
	};

	for (int i=0; i<nu-nu1; i++){
	  for (int j=0; j<nv-nv1;j++){	    
	    fft0(k,nu1+i,nv1+j) = crr0(k,i,j);
	    fft1(k,nu1+i,nv1+j) = crr1(k,i,j);
	    fft2(k,nu1+i,nv1+j) = crr2(k,i,j);
	    fft3(k,nu1+i,nv1+j) = crr3(k,i,j);
	  };
	};


      };

     
      // Make the additional Vells planes for higher order Interpolation
      //blitz::Array<dcomplex,3> fft0 = vells0.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      //blitz::Array<dcomplex,3> fft1 = vells1.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      //blitz::Array<dcomplex,3> fft2 = vells2.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      //blitz::Array<dcomplex,3> fft3 = vells3.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft0u = vells0u.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft1u = vells1u.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft2u = vells2u.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft3u = vells3u.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft0v = vells0v.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft1v = vells1v.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft2v = vells2v.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft3v = vells3v.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft0uv = vells0uv.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft1uv = vells1uv.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft2uv = vells2uv.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,3> fft3uv = vells3uv.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      // This could possibly be made optional by a Request parameter

      for (int k=0; k<nf; k++){

      for (int i = 1; i < nu-1; i++){
	for (int j = 1; j < nv-1; j++){
      	  fft0u(k,i,j) = (fft0(k,i+1,j) + fft0(k,i-1,j))/2.;
	  fft0v(k,i,j) = (fft0(k,i,j+1) + fft0(k,i,j-1))/2.;
	  fft0uv(k,i,j) = (fft0(k,i+1,j+1) + fft0(k,i-1,j+1) +
	 		 fft0(k,i+1,j-1) + fft0(k,i-1,j-1))/4.;

	  fft1u(k,i,j) = (fft1(k,i+1,j) + fft1(k,i-1,j))/2.;
	  fft1v(k,i,j) = (fft1(k,i,j+1) + fft1(k,i,j-1))/2.;
	  fft1uv(k,i,j) = (fft1(k,i+1,j+1) + fft1(k,i-1,j+1) +
			 fft1(k,i+1,j-1) + fft1(k,i-1,j-1))/4.;

	  fft2u(k,i,j) = (fft2(k,i+1,j) + fft2(k,i-1,j))/2.;
	  fft2v(k,i,j) = (fft2(k,i,j+1) + fft2(k,i,j-1))/2.;
	  fft2uv(k,i,j) = (fft2(k,i+1,j+1) + fft2(k,i-1,j+1) +
			 fft2(k,i+1,j-1) + fft2(k,i-1,j-1))/4.;

	  fft3u(k,i,j) = (fft3(k,i+1,j) + fft3(k,i-1,j))/2.;
	  fft3v(k,i,j) = (fft3(k,i,j+1) + fft3(k,i,j-1))/2.;
	  fft3uv(k,i,j) = (fft3(k,i+1,j+1) + fft3(k,i-1,j+1) +
			 fft3(k,i+1,j-1) + fft3(k,i-1,j-1))/4.;
	};
      };

      // Assume periodicity: value at '-1' equals 'nu-1' or 'nv-1'
      //                     value at 'nu', 'nv' equals '0'
      // Check this!

      for (int i = 1; i < nu-1; i++){
	  fft0u(k,i,0) = (fft0(k,i+1,0) + fft0(k,i-1,0))/2.;
	  fft0v(k,i,0) = (fft0(k,i,1) + fft0(k,i,nv-1))/2.;
	  fft0uv(k,i,0) = (fft0(k,i+1,1) + fft0(k,i-1,1) +
			 fft0(k,i+1,nv-1) + fft0(k,i-1,nv-1))/4.;

	  fft0u(k,i,nv-1) = (fft0(k,i+1,nv-1) + fft0(k,i-1,nv-1))/2.;
	  fft0v(k,i,nv-1) = (fft0(k,i,0) + fft0(k,i,nv-2))/2.;
	  fft0uv(k,i,nv-1) = (fft0(k,i+1,0) + fft0(k,i-1,0) +
			 fft0(k,i+1,nv-2) + fft0(k,i-1,nv-2))/4.;

	  fft1u(k,i,0) = (fft1(k,i+1,0) + fft1(k,i-1,0))/2.;
	  fft1v(k,i,0) = (fft1(k,i,1) + fft1(k,i,nv-1))/2.;
	  fft1uv(k,i,0) = (fft1(k,i+1,1) + fft1(k,i-1,1) +
			 fft1(k,i+1,nv-1) + fft1(k,i-1,nv-1))/4.;

	  fft1u(k,i,nv-1) = (fft1(k,i+1,nv-1) + fft1(k,i-1,nv-1))/2.;
	  fft1v(k,i,nv-1) = (fft1(k,i,0) + fft1(k,i,nv-2))/2.;
	  fft1uv(k,i,nv-1) = (fft1(k,i+1,0) + fft1(k,i-1,0) +
			 fft1(k,i+1,nv-2) + fft1(k,i-1,nv-2))/4.;

	  fft2u(k,i,0) = (fft2(k,i+1,0) + fft2(k,i-1,0))/2.;
	  fft2v(k,i,0) = (fft2(k,i,1) + fft2(k,i,nv-1))/2.;
	  fft2uv(k,i,0) = (fft2(k,i+1,1) + fft2(k,i-1,1) +
			 fft2(k,i+1,nv-1) + fft2(k,i-1,nv-1))/4.;

	  fft2u(k,i,nv-1) = (fft2(k,i+1,nv-1) + fft2(k,i-1,nv-1))/2.;
	  fft2v(k,i,nv-1) = (fft2(k,i,0) + fft2(k,i,nv-2))/2.;
	  fft2uv(k,i,nv-1) = (fft2(k,i+1,0) + fft2(k,i-1,0) +
			 fft2(k,i+1,nv-2) + fft2(k,i-1,nv-2))/4.;

	  fft3u(k,i,0) = (fft3(k,i+1,0) + fft3(k,i-1,0))/2.;
	  fft3v(k,i,0) = (fft3(k,i,1) + fft3(k,i,nv-1))/2.;
	  fft3uv(k,i,0) = (fft3(k,i+1,1) + fft3(k,i-1,1) +
			 fft3(k,i+1,nv-1) + fft3(k,i-1,nv-1))/4.;

	  fft3u(k,i,nv-1) = (fft3(k,i+1,nv-1) + fft3(k,i-1,nv-1))/2.;
	  fft3v(k,i,nv-1) = (fft3(k,i,0) + fft3(k,i,nv-2))/2.;
	  fft3uv(k,i,nv-1) = (fft3(k,i+1,0) + fft3(k,i-1,0) +
			 fft3(k,i+1,nv-2) + fft3(k,i-1,nv-2))/4.;
      };

      for (int j = 1; j < nv-1; j++){
	fft0u(k,0,j) = (fft0(k,1,j) + fft0(k,nu-1,j))/2.;
	fft0v(k,0,j) = (fft0(k,0,j+1) + fft0(k,0,j-1))/2.;
	fft0uv(k,0,j) = (fft0(k,1,j+1) + fft0(k,nu-1,j+1) +
		       fft0(k,1,j-1) + fft0(k,nu-1,j-1))/4.;

	fft0u(k,nu-1,j) = (fft0(k,0,j) + fft0(k,nu-1,j))/2.;
	fft0v(k,nu-1,j) = (fft0(k,nu-1,j+1) + fft0(k,nu-1,j-1))/2.;
	fft0uv(k,nu-1,j) = (fft0(k,0,j+1) + fft0(k,nu-2,j+1) +
		          fft0(k,0,j-1) + fft0(k,nu-2,j-1))/4.;

	fft1u(k,0,j) = (fft1(k,1,j) + fft1(k,nu-1,j))/2.;
	fft1v(k,0,j) = (fft1(k,0,j+1) + fft1(k,0,j-1))/2.;
	fft1uv(k,0,j) = (fft1(k,1,j+1) + fft1(k,nu-1,j+1) +
		       fft1(k,1,j-1) + fft1(k,nu-1,j-1))/4.;

	fft1u(k,nu-1,j) = (fft1(k,0,j) + fft1(k,nu-1,j))/2.;
	fft1v(k,nu-1,j) = (fft1(k,nu-1,j+1) + fft1(k,nu-1,j-1))/2.;
	fft1uv(k,nu-1,j) = (fft1(k,0,j+1) + fft1(k,nu-2,j+1) +
		          fft1(k,0,j-1) + fft1(k,nu-2,j-1))/4.;

	fft2u(k,0,j) = (fft2(k,1,j) + fft2(k,nu-1,j))/2.;
	fft2v(k,0,j) = (fft2(k,0,j+1) + fft2(k,0,j-1))/2.;
	fft2uv(k,0,j) = (fft2(k,1,j+1) + fft2(k,nu-1,j+1) +
		       fft2(k,1,j-1) + fft2(k,nu-1,j-1))/4.;

	fft2u(k,nu-1,j) = (fft2(k,0,j) + fft2(k,nu-1,j))/2.;
	fft2v(k,nu-1,j) = (fft2(k,nu-1,j+1) + fft2(k,nu-1,j-1))/2.;
	fft2uv(k,nu-1,j) = (fft2(k,0,j+1) + fft2(k,nu-2,j+1) +
		          fft2(k,0,j-1) + fft2(k,nu-2,j-1))/4.;

	fft3u(k,0,j) = (fft3(k,1,j) + fft3(k,nu-1,j))/2.;
	fft3v(k,0,j) = (fft3(k,0,j+1) + fft3(k,0,j-1))/2.;
	fft3uv(k,0,j) = (fft3(k,1,j+1) + fft3(k,nu-1,j+1) +
		       fft3(k,1,j-1) + fft3(k,nu-1,j-1))/4.;

	fft3u(k,nu-1,j) = (fft3(k,0,j) + fft3(k,nu-1,j))/2.;
	fft3v(k,nu-1,j) = (fft3(k,nu-1,j+1) + fft3(k,nu-1,j-1))/2.;
	fft3uv(k,nu-1,j) = (fft3(k,0,j+1) + fft3(k,nu-2,j+1) +
		          fft3(k,0,j-1) + fft3(k,nu-2,j-1))/4.;
      };

      fft0u(k,0,0) = (fft0(k,1,0) + fft0(k,nu-1,0))/2.;
      fft0v(k,0,0) = (fft0(k,0,1) + fft0(k,0,nv-1))/2.;
      fft0uv(k,0,0) = (fft0(k,1,1) + fft0(k,nu-1,1) +
		     fft0(k,1,nv-1) + fft0(k,nu-1,nv-1))/4.;

      fft0u(k,0,nv-1) = (fft0(k,1,nv-1) + fft0(k,nu-1,nv-1))/2.;
      fft0v(k,0,nv-1) = (fft0(k,0,0) + fft0(k,0,nv-2))/2.;
      fft0uv(k,0,nv-1) = (fft0(k,1,0) + fft0(k,nu-1,0) +
			fft0(k,1,nv-2) + fft0(k,nu-1,nv-2))/4.;

      fft0u(k,nu-1,0) = (fft0(k,0,0) + fft0(k,nu-2,0))/2.;
      fft0v(k,nu-1,0) = (fft0(k,nu-1,1) + fft0(k,nu-1,nv-1))/2.;
      fft0uv(k,nu-1,0) = (fft0(k,0,1) + fft0(k,nu-2,1) +
			fft0(k,0,nv-1) + fft0(k,nu-2,nv-1))/4.;

      fft0u(k,nu-1,nv-1) = (fft0(k,0,nv-1) + fft0(k,nu-2,nv-1))/2.;
      fft0v(k,nu-1,nv-1) = (fft0(k,nu-1,0) + fft0(k,nu-1,nv-2))/2.;
      fft0uv(k,nu-1,nv-1) = (fft0(k,0,0) + fft0(k,nu-2,0) +
			   fft0(k,0,nv-2) + fft0(k,nu-2,nv-2))/4.;

      fft1u(k,0,0) = (fft1(k,1,0) + fft1(k,nu-1,0))/2.;
      fft1v(k,0,0) = (fft1(k,0,1) + fft1(k,0,nv-1))/2.;
      fft1uv(k,0,0) = (fft1(k,1,1) + fft1(k,nu-1,1) +
		     fft1(k,1,nv-1) + fft1(k,nu-1,nv-1))/4.;

      fft1u(k,0,nv-1) = (fft1(k,1,nv-1) + fft1(k,nu-1,nv-1))/2.;
      fft1v(k,0,nv-1) = (fft1(k,0,0) + fft1(k,0,nv-2))/2.;
      fft1uv(k,0,nv-1) = (fft1(k,1,0) + fft1(k,nu-1,0) +
			fft1(k,1,nv-2) + fft1(k,nu-1,nv-2))/4.;

      fft1u(k,nu-1,0) = (fft1(k,0,0) + fft1(k,nu-2,0))/2.;
      fft1v(k,nu-1,0) = (fft1(k,nu-1,1) + fft1(k,nu-1,nv-1))/2.;
      fft1uv(k,nu-1,0) = (fft1(k,0,1) + fft1(k,nu-2,1) +
			fft1(k,0,nv-1) + fft1(k,nu-2,nv-1))/4.;

      fft1u(k,nu-1,nv-1) = (fft1(k,0,nv-1) + fft1(k,nu-2,nv-1))/2.;
      fft1v(k,nu-1,nv-1) = (fft1(k,nu-1,0) + fft1(k,nu-1,nv-2))/2.;
      fft1uv(k,nu-1,nv-1) = (fft1(k,0,0) + fft1(k,nu-2,0) +
			   fft1(k,0,nv-2) + fft1(k,nu-2,nv-2))/4.;

      fft2u(k,0,0) = (fft2(k,1,0) + fft2(k,nu-1,0))/2.;
      fft2v(k,0,0) = (fft2(k,0,1) + fft2(k,0,nv-1))/2.;
      fft2uv(k,0,0) = (fft2(k,1,1) + fft2(k,nu-1,1) +
		     fft2(k,1,nv-1) + fft2(k,nu-1,nv-1))/4.;

      fft2u(k,0,nv-1) = (fft2(k,1,nv-1) + fft2(k,nu-1,nv-1))/2.;
      fft2v(k,0,nv-1) = (fft2(k,0,0) + fft2(k,0,nv-2))/2.;
      fft2uv(k,0,nv-1) = (fft2(k,1,0) + fft2(k,nu-1,0) +
			fft2(k,1,nv-2) + fft2(k,nu-1,nv-2))/4.;

      fft2u(k,nu-1,0) = (fft2(k,0,0) + fft2(k,nu-2,0))/2.;
      fft2v(k,nu-1,0) = (fft2(k,nu-1,1) + fft2(k,nu-1,nv-1))/2.;
      fft2uv(k,nu-1,0) = (fft2(k,0,1) + fft2(k,nu-2,1) +
			fft2(k,0,nv-1) + fft2(k,nu-2,nv-1))/4.;

      fft2u(k,nu-1,nv-1) = (fft2(k,0,nv-1) + fft2(k,nu-2,nv-1))/2.;
      fft2v(k,nu-1,nv-1) = (fft2(k,nu-1,0) + fft2(k,nu-1,nv-2))/2.;
      fft2uv(k,nu-1,nv-1) = (fft2(k,0,0) + fft2(k,nu-2,0) +
			   fft2(k,0,nv-2) + fft2(k,nu-2,nv-2))/4.;

      fft3u(k,0,0) = (fft3(k,1,0) + fft3(k,nu-1,0))/2.;
      fft3v(k,0,0) = (fft3(k,0,1) + fft3(k,0,nv-1))/2.;
      fft3uv(k,0,0) = (fft3(k,1,1) + fft3(k,nu-1,1) +
		     fft3(k,1,nv-1) + fft3(k,nu-1,nv-1))/4.;

      fft3u(k,0,nv-1) = (fft3(k,1,nv-1) + fft3(k,nu-1,nv-1))/2.;
      fft3v(k,0,nv-1) = (fft3(k,0,0) + fft3(k,0,nv-2))/2.;
      fft3uv(k,0,nv-1) = (fft3(k,1,0) + fft3(k,nu-1,0) +
			fft3(k,1,nv-2) + fft3(k,nu-1,nv-2))/4.;

      fft3u(k,nu-1,0) = (fft3(k,0,0) + fft3(k,nu-2,0))/2.;
      fft3v(k,nu-1,0) = (fft3(k,nu-1,1) + fft3(k,nu-1,nv-1))/2.;
      fft3uv(k,nu-1,0) = (fft3(k,0,1) + fft3(k,nu-2,1) +
			fft3(k,0,nv-1) + fft3(k,nu-2,nv-1))/4.;

      fft3u(k,nu-1,nv-1) = (fft3(k,0,nv-1) + fft3(k,nu-2,nv-1))/2.;
      fft3v(k,nu-1,nv-1) = (fft3(k,nu-1,0) + fft3(k,nu-1,nv-2))/2.;
      fft3uv(k,nu-1,nv-1) = (fft3(k,0,0) + fft3(k,nu-2,0) +
			   fft3(k,0,nv-2) + fft3(k,nu-2,nv-2))/4.;

      };

      const double fmin = min(child_cells.cellStart(Axis::FREQ));
      const double fmax = max(child_cells.cellEnd(Axis::FREQ));

      const double dl = max(child_cells.cellSize(Axis::axis("L")));
      const double dm = max(child_cells.cellSize(Axis::axis("M")));

      const double lmax = max(child_cells.center(Axis::axis("L")));
      //const double du = 0.5 / lmax / _uvppw;
      const double du = 1.0 / dl / (nu-1);

      const double mmax = max(child_cells.center(Axis::axis("M")));
      //const double dv = 0.5 / mmax / _uvppw;
      const double dv = 1.0 / dm / (nv-1);

      //const double umax = 0.5/max(child_cells.cellSize(Axis::axis("L")));
      //const double umin = -umax;

      //const double vmax = 0.5/max(child_cells.cellSize(Axis::axis("M")));
      //const double vmin = -vmax;

      const double umax = (nu-nu1-1+0.5)*du;
      const double umin = -(nu1+0.5)*du;

      const double vmax = (nv-nv1-1+0.5)*dv;
      const double vmin = -(nv1+0.5)*dv;

      // For now, use the L & M axes instead of U & V (Visualisation)
      Domain::Ref domain(new Domain());
      domain().defineAxis(Axis::FREQ,fmin,fmax);
      domain().defineAxis(Axis::axis("L"),umin,umax);
      domain().defineAxis(Axis::axis("M"),vmin,vmax);

      // For now, use the L & M axes instead of U & V (Visualisation)
      Cells::Ref cells(new Cells(*domain));
      cells().setCells(Axis::FREQ,fmin,fmax,nf);
      cells().setCells(Axis::axis("L"),umin,umax,nu);
      cells().setCells(Axis::axis("M"),vmin,vmax,nv);

      // Set the Cells to the Result
      resref().setCells(*cells);

    };  // end: if axis L and M. 
	 
    return 0;
    
  };
  
  void FFTBrick::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
  };
  
} // namespace Meq

//# UVBrick.cc: Stored parameter with polynomial coefficients
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

#include <MeqNodes/UVBrick.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
#include <casa/aips.h>
#include <casa/Arrays.h>
#include <casa/Arrays/Vector.h>
#include <casa/BasicSL/String.h>
#include <images/Images/ImageInterface.h>
#include <images/Images/PagedImage.h>
#include <images/Images/ImageFFT.h>
#include <images/Images/TempImage.h>
#include <coordinates/Coordinates/CoordinateUtil.h>
#include <coordinates/Coordinates/CoordinateSystem.h>
#include <lattices/Lattices/LatticeIterator.h>
#include <lattices/Lattices/Lattice.h>
#include <casa/BasicMath/Math.h>
#include <casa/BasicSL/Constants.h>

namespace Meq {
  
  UVBrick::UVBrick()
    : 
    // Null-pointers to images
      _uvreal(0),
      _uvimag(0),
      _uvabs(0),
      _patch(0),
      // max baselines for WSRT in [m]
      _umax(2700.0),
      _vmax(2700.0),
      _wmax(0.0),
      // boolean for checking
      _image_exists(false)
  {
    Axis::addAxis("U");
    Axis::addAxis("V");
  };
  
  UVBrick::~UVBrick()
  {
    //
    // Clear memory from the MeqUVbrick image objects
    //     
    delete _uvreal;
    delete _uvimag;
    delete _uvabs;
    delete _patch;
  };
  
  
  int UVBrick::getResult (Result::Ref &resref,
			  const std::vector<Result::Ref> &childres,
			  const Request &request,bool newreq)
  {

    const double c0 = casa::C::c; // Speed of light

    // Get the Request cells.
    const Cells& rcells = request.cells();
    
    if( rcells.isDefined(Axis::TIME) && rcells.isDefined(Axis::FREQ))
      {
	//
	// Make sure we have a valid UV Image
	//
	if (!_image_exists) 
	  {
	    // UV image does not exist, so make one.
	    makeUVImage(rcells);
	  } else {
	  if (!checkValidity(rcells)) {	    
	    // UV image does not satisfy the requirements, so make a new one.
	    makeUVImage(rcells);	    
	  };
	};  //end: if / then / else


	//
	// We now have a valid UV Image and start creating a Result with Vells
	//

	
	//
	// Make the Result
	//

	// Make a Cells corresponding to the Image grid
	casa::IPosition image_shape = _uvreal->shape();
	
	casa::CoordinateSystem cs = _uvreal->coordinates();
	casa::Vector<casa::String> units(4,"lambda");
	units(2) = "";
	units(3) = "Hz";
	cs.setWorldAxisUnits(units);
	
	casa::Vector<double> ref_pixel = cs.referencePixel();
	casa::Vector<double> ref_value = cs.referenceValue();
	casa::Vector<double> increment = cs.increment();

	double umin;
	double umax;

	if (increment(0)>0) {
	  umin = ref_value(0) - (ref_pixel(0)+1-0.5)*increment(0);
	  umax = ref_value(0) + (image_shape(0)-ref_pixel(0)-1+0.5)*increment(0);
	} else {
	  umax = ref_value(0) - (ref_pixel(0)+1-0.5)*increment(0);
	  umin = ref_value(0) + (image_shape(0)-ref_pixel(0)-1+0.5)*increment(0);
	};

	double vmin;
	double vmax; 

	if (increment(1)>0) {
	  vmin = ref_value(1) - (ref_pixel(1)+1-0.5)*increment(1);
	  vmax = ref_value(1) + (image_shape(1)-ref_pixel(1)-1+0.5)*increment(1);
	} else {
	  vmax = ref_value(1) - (ref_pixel(1)+1-0.5)*increment(1);
	  vmin = ref_value(1) + (image_shape(1)-ref_pixel(1)-1+0.5)*increment(1);
	};

	double fmin;
	double fmax;

	if (increment(3)>0) {
	  fmin = ref_value(3) - (ref_pixel(3)+1-0.5)*increment(3);
	  fmax = ref_value(3) + (image_shape(3)-ref_pixel(3)-1+0.5)*increment(3);
	} else {
	  fmax = ref_value(3) - (ref_pixel(3)+1-0.5)*increment(3);
	  fmin = ref_value(3) + (image_shape(3)-ref_pixel(3)-1+0.5)*increment(3);
	};
	
	
	Domain::Ref domain(new Domain());
	domain().defineAxis(2,umin,umax);
	domain().defineAxis(3,vmin,vmax);
	domain().defineAxis(1,fmin,fmax);
	Cells::Ref cells(new Cells(*domain));
	cells().setCells(1,fmin,fmax,image_shape(3));
	cells().setCells(2,umin,umax,image_shape(0));
	cells().setCells(3,vmin,vmax,image_shape(1));

	// Create Result object and attach to the Ref that was passed in.
		
	resref <<= new Result(4);

	// Make the Vells
	// For now, 4 Images are put in separate planes. In the future, 
	//  just 1 plane may combine the real and imaginary images.

	Vells::Shape shape;
	Axis::degenerateShape(shape,cells->rank());
	shape[Axis::axis("u")]    = cells->ncells(Axis::axis("u"));
	shape[Axis::axis("freq")] = cells->ncells(Axis::FREQ);
	shape[Axis::axis("v")]    = cells->ncells(Axis::axis("v"));

	VellSet& vs1  = resref().setNewVellSet(0);  
	Vells& vells1 = vs1.setValue(new Vells(double(0),shape,false));
	VellSet& vs2  = resref().setNewVellSet(1);  
	Vells& vells2 = vs2.setValue(new Vells(double(0),shape,false));
	VellSet& vs3  = resref().setNewVellSet(2);  
	Vells& vells3 = vs3.setValue(new Vells(double(0),shape,false));
	VellSet& vs4  = resref().setNewVellSet(3);  
	Vells& vells4 = vs4.setValue(new Vells(double(0),shape,false));

	fillVells(vells1, vells2, vells3, vells4, cells);

	// Attach Cells to the Result (after the Vells are created!)
	resref().setCells(*cells);          

      };  // end: if axis time and freq. 
    
    return 0;
    
  };
  
  void UVBrick::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
  }


  bool UVBrick::checkValidity(const Cells &fcells)
  {
    // For now assume a equidistant grid in frequency for the Request Cells.
    // In the future, this may be generalized, where we will have two options:
    // 1) Fill the Vells frequency plane by frequency plane.
    // 2) Interpolate in frequency.
    // Right now we assume that the Request cells is equidistant and that the 
    //  frequency planes of the image coincide with the Request Cells.

    bool valid = false;

    // Get the minimal and maximal freq. values from the Image

    casa::IPosition image_shape = _uvreal->shape();
    const int nf = fcells.ncells(Axis::FREQ);

    if (nf==image_shape(3)){
      // The number of frequency planes of the request equals that of the image
      
      casa::CoordinateSystem cs = _uvreal->coordinates();
      casa::Vector<casa::String> units(4,"lambda");
      units(2) = "";
      units(3) = "Hz";
      cs.setWorldAxisUnits(units);
    
      casa::Vector<double> ref_pixel = cs.referencePixel();
      casa::Vector<double> ref_value = cs.referenceValue();
      casa::Vector<double> increment = cs.increment();
    
      double fmin;
      double fmax;
      
      if (increment(3)>0) {
	fmin = ref_value(3) - (ref_pixel(3)+1-0.5)*increment(3);
	fmax = ref_value(3) + (image_shape(3)-ref_pixel(3)-1+0.5)*increment(3);
      } else {
	fmax = ref_value(3) - (ref_pixel(3)+1-0.5)*increment(3);
	fmin = ref_value(3) + (image_shape(3)-ref_pixel(3)-1+0.5)*increment(3);
      };
    
      // Get the freq range from the Request Cells
      const LoVec_double freq = fcells.center(Axis::FREQ); 
      const LoVec_double freqsize = fcells.cellSize(Axis::FREQ);

      // assumes increasing freq. range in cells. Change!
      const double freq_max = max(freq)+0.5*freqsize(nf);
      const double freq_min = min(freq)-0.5*freqsize(0);
      
      if ( (abs(freq_min-fmin)<1e-6) && (abs(freq_max-fmax)<1e-6) ){
	// Request Cells and image have the same domain	
	valid = true;
      } else {
	// Request Cells and image do not have the same domain
	valid = false;
      };;

    } else {

      // Not the same number of frequency planes in Request and Image
      valid = false;

    };
    
    return valid;

  };


  void UVBrick::makeUVImage(const Cells &fcells)
  {
    // Make Patch Image, and its FFT (real & imag UVImages) for the correct 
    // frequency planes (determined by fcells i.e. the Request Cells) 

    // Clear the allocated memory of the MeqUVbrick image objects
    delete _uvreal;
    delete _uvimag;
    delete _uvabs;
    delete _patch;

    _image_exists = false;

    const double c0 = casa::C::c;  // Speed of light

    // nf = number of frequency channels, 
    //      i.e. number of frequency planes of the image
    const int nf = fcells.ncells(Axis::FREQ);

    const LoVec_double freq = fcells.center(Axis::FREQ); 
    const LoVec_double freqsize = fcells.cellSize(Axis::FREQ);
    const double freq_max = max(freq);

    // At the moment there is no LSM and, hence, no Patch Image.
    // Therefore, a Patch Image is constructed. This image does match 
    // the # freq. planes of the Request Cells. When a LSM is available 
    // this is no longer automatically true.
    //
    // Based on the 3C343.1 / 3C343 field we define the following Patch 
    //  Distance from edge to phase center: 0.00175 rad
    //  Times 2 for square image (pos. & neg. axis)
    //  Note: Resolving at 10 points per wavelength and considering a 
    //   factor sqrt(2) (approx. 1.5) for diagonal propagation 
    //   (is it best to have square cells?)
    //   the Patch Image is 15 times larger than the source it contains. 
    //   (since umax = 1 / delta_RA en du = 1 / RA_size) 
    //
    const double RA_size = 0.00175; // rad
    const double Dec_size = 0.00175; //rad

    const double delta_RA = 1.0 / (freq_max * 2 * _umax / c0);
    const double delta_Dec = 1.0 / (freq_max * 2 * _vmax / c0); 
    
    const int nRA = int( 2*RA_size / delta_RA + 0.5);
    const int nDec = int( 2*Dec_size / delta_Dec + 0.5);

    // RA: nRa pixels, Dec: nDec pixels, Stokes: 1 pixels, Freq: nf pixels
    casa::CoordinateSystem cs = casa::CoordinateUtil::defaultCoords4D();
    casa::Vector<double> ref(4,0.0f);
    casa::Vector<casa::String> units(4,"rad");
    // Note: vectors, pixels are zero based in AIPS++, but 1 based in GLISH
    ref(0) = int(nRA / 2.0 + 0.5)-1;
    ref(1) = int(nDec / 2.0 + 0.5)-1;
    ref(2) = 0;
    ref(3) = 0;
    cs.setReferencePixel(ref);
    units(2) = "";
    units(3) = "Hz";
    cs.setWorldAxisUnits(units);
    ref(0) = 4.356647609;
    ref(1) = 1.092209195;
    ref(2) = 4.6113;
    ref(3) = freq(0);
    cs.setReferenceValue(ref);
    ref(0) = -delta_RA;
    ref(1) = delta_Dec;
    ref(2) = 1;
    ref(3) = freqsize(0);
    cs.setIncrement(ref);
    // Note that AIPS++ Images have equidistant grid points.

    _patch = new casa::PagedImage<float>(casa::IPosition(4,nRA,nDec,1,nf), cs, "temp.image");
    
    //
    // No LSM yet, so fill Patch_Image manually
    //
    //_patch = new casa::PagedImage<float>("model3C343.image");
    casa::IPosition image_shape = _patch->shape();
    //cs = _patch->coordinates();
    _patch->set(0.0f);

    // phase center, just for relative positions now
    ref(0) = 4.356647609; // rad
    ref(1) = 1.092209195; // rad
	
    // Fill image per frequency plane
    casa::IPosition position(image_shape.nelements());
    casa::Vector<double> world(4,0.0); 
    casa::Vector<double> pixel(4);
    casa::Vector<bool> absio(4,true);
    casa::Vector<casa::String> unitin(4, "pix");
    unitin(0) = "rad";
    unitin(1) = "rad";
    const casa::Vector<casa::String> unitout(4,"pix");
    casa::MDoppler::Types doppler;
    casa::Double offset = 0.0;

    for (int i = 0; i < nf; i++){
      world(3) = i;

      // 3C343.1    
      
      world(0) = ref(0);
      world(1) = ref(1);
    
      // coordOut=pixel,coordIn=world, absIn=[T, T, T, T], unitsIn="rad rad pix pix", absOut=[T,T,T,T], unitsOut="pix pix pix pix"
      cs.convert(pixel, world, absio, unitin, doppler, absio, unitout, doppler, offset, offset);
      
      // Beware: in this rounding off a pixel may lie just outside the image
      position(0)=int(pixel(0)+0.5);
      position(1)=int(pixel(1)+0.5);
      position(2)=int(pixel(2)+0.5);
      position(3)=int(pixel(3)+0.5);
	
      // _patch->putAt(4.6113, position);
	
      // 3C343

      world(0) = ref(0); //+ 0.00175; // 4.339606069;
      world(1) = ref(1); //+ 0.00175; // 1.095366651;    

      // coordOut=pixel,coordIn=world, absIn=[T, T, T, T], unitsIn="rad rad pix pix", absOut=[T,T,T,T], unitsOut="pix pix pix pix"
      cs.convert(pixel, world, absio, unitin, doppler, absio, unitout, doppler, offset, offset);
	
      // Beware: in this rounding off a pixel may lie just outside the image
      position(0)=int(nRA / 2.0  + 0.5)-1+1; // int(pixel(0)+0.5);
      position(1)=int(nDec / 2.0 + 0.5)-1+1; // int(pixel(1)+0.5);
      position(2)=int(pixel(2)+0.5);
      position(3)=int(pixel(3)+0.5);
    
      _patch->putAt(5.0025, position);

    };
	
    //
    // FFT the Patch Image
    //
    _uvreal = new casa::PagedImage<float>(image_shape, casa::CoordinateUtil::defaultCoords4D(), "fft_real.image");
    _uvimag = new casa::PagedImage<float>(image_shape, casa::CoordinateUtil::defaultCoords4D(), "fft_imag.image");
    _uvabs = new casa::PagedImage<float>(image_shape, casa::CoordinateUtil::defaultCoords4D(), "fft_ampl.image");
    casa::PagedImage<float> test(image_shape, casa::CoordinateUtil::defaultCoords4D(), "test.image");
    
    casa::ImageFFT fft;
    fft.fftsky(*_patch);
    
    fft.getReal(*_uvreal);
    fft.getImaginary(*_uvimag);
    fft.getAmplitude(*_uvabs); 
    fft.getReal(test);  

    _image_exists = true;

  };

  
  void UVBrick::fillVells(Vells &fvells1, Vells &fvells2, Vells &fvells3, Vells &fvells4, const Cells &fcells)
  {
    // nu = shape of U axis
    // nv = shape of V axis
    // nf = shape of FREQ axis
    int nu = fcells.ncells(Axis::axis("u"));
    int nv = fcells.ncells(Axis::axis("v"));
    int nf = fcells.ncells(Axis::axis("freq"));

    // Make an array, connected to the Vells, with which we fill the Vells.
    blitz::Array<double,3> arr1 = fvells1.as<double,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
    blitz::Array<double,3> arr2 = fvells2.as<double,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
    blitz::Array<double,3> arr3 = fvells3.as<double,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
    blitz::Array<double,3> arr4 = fvells4.as<double,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
    // Note that the Vells are 4D (including time), whereas the corresponding 
    //  Cells are 3D (without time).
    // arr(k,i,j)
    arr1 = 0.0;
    arr2 = 0.0;
    arr3 = 0.0;
    arr4 = 0.0;

    // For now fill Vells with image values.    
    casa::IPosition image_shape = _uvreal->shape();
    casa::IPosition position(image_shape.nelements());

    position(2)=0;
    for (int k = 0; k < nf; k++){
      position(0)=0;
      position(3)=k;
      for (int i = 0; i < nu; i++){
	position(1)=0;
	for (int j = 0; j < nv; j++){
	  arr4(k,i,j) = _patch->getAt(position);
	  arr1(k,i,j) = _uvreal->getAt(position);
	  arr2(k,i,j) = _uvimag->getAt(position);
	  arr3(k,i,j) = _uvabs->getAt(position);
	  position(1)+=1;
	};
	position(0)+=1;
      };
    };
  };
  
} // namespace Meq

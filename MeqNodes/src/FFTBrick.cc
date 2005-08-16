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
#include <fftw3.h>

namespace Meq {
  

  FFTBrick::FFTBrick()
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

    Cells child_cells = childres.at(0)->cells();
    
    if ( child_cells.isDefined(Axis::axis("L")) && child_cells.isDefined(Axis::axis("M")) ){

      int nf = child_cells.ncells(Axis::FREQ);
      const double fmin = min(child_cells.cellStart(Axis::FREQ));
      const double fmax = max(child_cells.cellEnd(Axis::FREQ));

      const int nu = child_cells.ncells(Axis::axis("L"));
      const double umax = 0.5/max(child_cells.cellSize(Axis::axis("L")));
      const double umin = -umax;

      const int nv = child_cells.ncells(Axis::axis("M"));
      const double vmax = 0.5/max(child_cells.cellSize(Axis::axis("M")));
      const double vmin = -vmax;
	   
      Domain::Ref domain(new Domain());
      domain().defineAxis(Axis::FREQ,fmin,fmax);
      domain().defineAxis(Axis::axis("U"),umin,umax);
      domain().defineAxis(Axis::axis("V"),vmin,vmax);

      Cells::Ref cells(new Cells(*domain));
      cells().setCells(Axis::FREQ,fmin,fmax,nf);
      cells().setCells(Axis::axis("U"),umin,umax,nu);
      cells().setCells(Axis::axis("V"),vmin,vmax,nv);

      resref <<= new Result(4);

      VellSet& vs0 = resref().setNewVellSet(0);
      VellSet& vs1 = resref().setNewVellSet(1);
      VellSet& vs2 = resref().setNewVellSet(2);
      VellSet& vs3 = resref().setNewVellSet(3);

      Vells::Shape shape;
      Axis::degenerateShape(shape,cells->rank());
      shape[Axis::axis("U")] = cells->ncells(Axis::axis("U"));
      shape[Axis::axis("V")] = cells->ncells(Axis::axis("V"));
      shape[Axis::FREQ] = cells->ncells(Axis::FREQ);

      Vells& vells0 = vs0.setValue(new Vells(dcomplex(0.0),shape,false));
      Vells& vells1 = vs1.setValue(new Vells(dcomplex(0.0),shape,false));
      Vells& vells2 = vs2.setValue(new Vells(dcomplex(0.0),shape,false));
      Vells& vells3 = vs3.setValue(new Vells(dcomplex(0.0),shape,false));

      blitz::Array<dcomplex,4> fft11 = vells0.as<dcomplex,6>()(LoRange::all(),LoRange::all(),0,0,LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,4> fft12 = vells1.as<dcomplex,6>()(LoRange::all(),LoRange::all(),0,0,LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,4> fft21 = vells2.as<dcomplex,6>()(LoRange::all(),LoRange::all(),0,0,LoRange::all(),LoRange::all());
      blitz::Array<dcomplex,4> fft22 = vells3.as<dcomplex,6>()(LoRange::all(),LoRange::all(),0,0,LoRange::all(),LoRange::all());

      fft11 = dcomplex(0.0);
      fft12 = dcomplex(0.0);
      fft21 = dcomplex(0.0);
      fft22 = dcomplex(0.0);

      // Fill the Vells with the FFT values.

      int nt = child_cells.ncells(Axis::TIME);
      if (nt==0) nt=1;

      const Result &tempres = childres.at(0);

      const VellSet &vs11 = tempres.vellSet(0);
      const VellSet &vs12 = tempres.vellSet(1);
      const VellSet &vs21 = tempres.vellSet(2);
      const VellSet &vs22 = tempres.vellSet(3);

      Vells vells11 = vs11.getValue();
      Vells vells12 = vs12.getValue();
      Vells vells21 = vs21.getValue();
      Vells vells22 = vs22.getValue();

      blitz::Array<dcomplex,2> arr11(nu,nv);
      blitz::Array<dcomplex,2> arr12(nu,nv);
      blitz::Array<dcomplex,2> arr21(nu,nv);
      blitz::Array<dcomplex,2> arr22(nu,nv);

      arr11 = dcomplex(0.0);
      arr12 = dcomplex(0.0);
      arr21 = dcomplex(0.0);
      arr22 = dcomplex(0.0);

      nt=1;
      nf=1;

      fftw_complex *in, *out;
      fftw_plan p;

      //      in = fftw_malloc(sizeof(fftw_complex) * nu * nv);
      // out = fftw_malloc(sizeof(fftw_complex) * nu * nv); 

      for (int i=0; i<nt; i++){
      	for (int j=0; j<nf; j++){
      	  
      	  //arr11 = vells11.as<dcomplex,4>()(i,j,LoRange::all(),LoRange::all());
	  //*arr1 = vells11.getDataPtr();
	  arr12 = vells12.as<dcomplex,4>()(i,j,LoRange::all(),LoRange::all());
	  arr21 = vells21.as<dcomplex,4>()(i,j,LoRange::all(),LoRange::all());
	  arr22 = vells22.as<dcomplex,4>()(i,j,LoRange::all(),LoRange::all());
	  
	  in = static_cast<fftw_complex*>(const_cast<void*>(vells11.getConstDataPtr()));
	  out = static_cast<fftw_complex*>(vells0.getDataPtr());

	  p = fftw_plan_dft_2d(nu,nv,in,out,FFTW_FORWARD,FFTW_ESTIMATE);

	  fftw_execute(p);

      	  for (int k=0; k<nu; k++){
      	    for (int l=0; l<nv; l++){

      	      //fft11(i,j,k,l) = arr11(k,l);
	      fft12(i,j,k,l) = arr12(k,l);
	      fft21(i,j,k,l) = arr21(k,l);
	      fft22(i,j,k,l) = arr22(k,l);
      	      
      	    };
      	  };
      	};
      };

      fftw_destroy_plan(p);
      fftw_free(in);
      fftw_free(out);

      resref().setCells(*cells);
	
      

    };  // end: if axis L and M. 
	 
    return 0;
    
  };
  
  void FFTBrick::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
  };
  
} // namespace Meq

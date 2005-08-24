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
      const double fmin = min(child_cells.cellStart(Axis::FREQ));
      const double fmax = max(child_cells.cellEnd(Axis::FREQ));

      const int nu = child_cells.ncells(Axis::axis("L"));
      const double umax = 0.5/max(child_cells.cellSize(Axis::axis("L")));
      const double umin = -umax;

      const int nv = child_cells.ncells(Axis::axis("M"));
      const double vmax = 0.5/max(child_cells.cellSize(Axis::axis("M")));
      const double vmin = -vmax;
	   
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

      // Make a new Result
      resref <<= new Result(4);

      VellSet& vs0 = resref().setNewVellSet(0);
      VellSet& vs1 = resref().setNewVellSet(1);
      VellSet& vs2 = resref().setNewVellSet(2);
      VellSet& vs3 = resref().setNewVellSet(3);

      // For now, use the L & M axes instead of U & V (Visualisation)
      Vells::Shape shape;
      Axis::degenerateShape(shape,cells->rank());
      shape[Axis::axis("L")] = cells->ncells(Axis::axis("L"));
      shape[Axis::axis("M")] = cells->ncells(Axis::axis("M"));
      shape[Axis::FREQ] = cells->ncells(Axis::FREQ);

      Vells& vells0 = vs0.setValue(new Vells(dcomplex(0.0),shape,false));
      Vells& vells1 = vs1.setValue(new Vells(dcomplex(0.0),shape,false));
      Vells& vells2 = vs2.setValue(new Vells(dcomplex(0.0),shape,false));
      Vells& vells3 = vs3.setValue(new Vells(dcomplex(0.0),shape,false));

      // An absent axis, shows up with dimension 1 in the Vells Array
      int nt = child_cells.ncells(Axis::TIME);
      if (nt==0) nt=1;

      // Get the Child Data
      const Result &tempres = childres.at(0);

      const VellSet &vs11 = tempres.vellSet(0);
      const VellSet &vs12 = tempres.vellSet(1);
      const VellSet &vs21 = tempres.vellSet(2);
      const VellSet &vs22 = tempres.vellSet(3);

      Vells vells11 = vs11.getValue();
      Vells vells12 = vs12.getValue();
      Vells vells21 = vs21.getValue();
      Vells vells22 = vs22.getValue();      

      // Prepare the FFT
      fftw_complex *in1, *out1, *in2, *out2, *in3, *out3, *in4, *out4;
      fftw_plan p;

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
      in1 = static_cast<fftw_complex*>(const_cast<void*>(vells11.getConstDataPtr()));
      out1 = static_cast<fftw_complex*>(vells0.getDataPtr());

      // The FFT plan definition
      p = fftw_plan_guru_dft(rank,dims,howmany_rank, howmany_dims,in1,out1,FFTW_FORWARD,FFTW_ESTIMATE);

      // Execution of the FFT
      fftw_execute(p);

      // Cast Vells data pointers into the input and output pointers
      in2 = static_cast<fftw_complex*>(const_cast<void*>(vells12.getConstDataPtr()));
      out2 = static_cast<fftw_complex*>(vells1.getDataPtr());

      // The FFT plan definition
      p = fftw_plan_guru_dft(rank,dims,howmany_rank, howmany_dims,in2,out2,FFTW_FORWARD,FFTW_ESTIMATE);

      // Execution of the FFT
      fftw_execute(p);

      // Cast Vells data pointers into the input and output pointers
      in3 = static_cast<fftw_complex*>(const_cast<void*>(vells21.getConstDataPtr()));
      out3 = static_cast<fftw_complex*>(vells2.getDataPtr());

      // The FFT plan definition
      p = fftw_plan_guru_dft(rank,dims,howmany_rank, howmany_dims,in3,out3,FFTW_FORWARD,FFTW_ESTIMATE);

      // Execution of the FFT
      fftw_execute(p);

      // Cast Vells data pointers into the input and output pointers
      in4 = static_cast<fftw_complex*>(const_cast<void*>(vells22.getConstDataPtr()));
      out4 = static_cast<fftw_complex*>(vells3.getDataPtr());

      // The FFT plan definition
      p = fftw_plan_guru_dft(rank,dims,howmany_rank, howmany_dims,in4,out4,FFTW_FORWARD,FFTW_ESTIMATE);

      // Execution of the FFT
      fftw_execute(p);

      // Destroy the plan 
      if(p) fftw_destroy_plan(p);

      // test to be used later
      //fftw_complex *in, *out;
      //in = (fftw_complex *)fftw_malloc(nu*nv*sizeof(fftw_complex));
     
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

//# FFTBrick.cc: Stored parameter with polynomial coefficients
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
//# $Id$

#include <MeqNodes/FFTBrick.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
#include <MEQ/Axis.h>
#include <MEQ/VellsSlicer.h>

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
#include <fftw3.h>
#include <blitz/array/stencilops.h>

namespace Meq {
  
const HIID FAxesIn = AidAxes|AidIn;
const HIID FAxesOut = AidAxes|AidOut;

FFTBrick::FFTBrick()
  : Node(1),     // exactly 1 child expected
  _uvppw(1.0)
{
  _in_axis_id.resize(2);
  _in_axis_id[0] = "L";
  _in_axis_id[1] = "M";
  _out_axis_id.resize(2);
  _out_axis_id[0] = "U";
  _out_axis_id[1] = "V";
  Axis::addAxis("U");
  Axis::addAxis("V");
};

FFTBrick::~FFTBrick(){};

int FFTBrick::getResult (Result::Ref &resref,
			const std::vector<Result::Ref> &child_results,
			const Request &request,bool newreq)
{
  Assert(child_results.size()==1);
  const Result & childres = child_results[0];
  
  // first, figure out the axes. Exception will be thrown for us if any are
  // invalid
  _inaxis0 = Axis::axis(_in_axis_id[0]);
  _inaxis1 = Axis::axis(_in_axis_id[1]);
  _outaxis0 = Axis::axis(_out_axis_id[0]);
  _outaxis1 = Axis::axis(_out_axis_id[1]);
  
  // Get the Cells of the child and ensure that input axes are present and
  // uniformly gridded
  const Cells & input_cells = childres.cells();
  FailWhen(!input_cells.isDefined(_inaxis0) || !input_cells.isDefined(_inaxis1),
      "one or both input axes are not defined in the child cells");
  //// disable this check for now
  //  FailWhen(input_cells.numSegments(_inaxis0)!=1 || input_cells.numSegments(_inaxis0)!=1,
  //      "one or both input axes not uniformly gridded in the child cells");
  
  // Figure out the shapes 
  // NB: for historical reasons, we'll use l,m to name variables referring to 
  // the input axes, and u,v when referring to the output axes. The real axes
  // in use are of course determined above.
  nl = input_cells.ncells(_inaxis0);
  nu = int(_uvppw*nl);

  nm = input_cells.ncells(_inaxis1);
  nv = int(_uvppw*nm);

  nl1 = int(nl/2)+1; // center point in LM plane
  nm1 = int(nm/2)+1;
  nu1 = int(nu/2)+1;  // center point in UV plane
  nv1 = int(nv/2)+1;
  
  // Now, the Result dimensions. Since we generate 4 output interpolation
  // planes per a single input plane, we add an extra tensor dimension of 
  // size 4
  Result::Dims dims = childres.dims();
  dims.push_back(1);
  
  // make a new Result
  Result & result = resref <<= new Result(dims);
  
  // now loop over input VellSets and FFT them one by one
  int ovs = 0;  // counter of output VellSets
  for( int ivs = 0; ivs<childres.numVellSets(); ivs++ )
  {
    const VellSet &vs_input = childres.vellSet(ivs);
    // create 4 new output VellSets
    VellSet * pvs_output[1];
    for( int i=0; i<1; i++,ovs++ )
      pvs_output[i] = &( result.setNewVellSet(ovs) );
    
    // if the input VellSet is a null, make null outputs and continue
    if( vs_input.isNull() )
    {
      Vells::Ref null_vells(DMI::ANONWR);
      for( int i=0; i<1; i++,ovs++ )
        pvs_output[i]->setValue(null_vells);
      continue;
    }
      
    // ok, we have actual values (main + possibly perturbed). 
    // Setup copies of spid/perturbations.
    for( int i=0; i<1; i++ )
    {
      pvs_output[i]->setNumPertSets(vs_input.numPertSets());
      pvs_output[i]->copySpids(vs_input);
      pvs_output[i]->copyPerturbations(vs_input);
    }
    
    // Now FFT all values
    // this holds the 4 result Vells for each FFT
    Vells::Ref output_vells[1];
    
    // FFT the main value
    doFFT(output_vells,vs_input.getValue());
    for( int i=0; i<1; i++ )
      pvs_output[i]->setValue(output_vells[i]);
    
    // FFT each perturbed value
    for( int ipset=0; ipset<vs_input.numPertSets(); ipset++ )
      for( int ipert=0; ipset<vs_input.numSpids(); ipert++ )
      {
        doFFT(output_vells,vs_input.getPerturbedValue(ipert,ipset));
        for( int i=0; i<1; i++ )
          pvs_output[i]->setPerturbedValue(ipert,output_vells[i],ipset);
      }
      
    // finalize shapes of output vellsets
    for( int i=0; i<1; i++ )
      pvs_output[i]->verifyShape();
  }
  
  // Now figure out the output cells
  
  // NB: cell size is uniform thanks to check at start of getResult()
  const double dl = input_cells.cellSize(_inaxis0)(0); 
  const double dm = input_cells.cellSize(_inaxis1)(0);

  const double du = 1.0 / dl / nu;
  const double dv = 1.0 / dm / nv;
/*
  // previous u domain
  const double umax = (nu-nu1+0.5)*du;
  const double umin = -(nu1-0.5)*du;
*/
  const double umax = (nu-nu1+1.5)*du;
  const double umin = -(nu1-1.5)*du;

  const double vmax = (nv-nv1+0.5)*dv;
  const double vmin = -(nv1-0.5)*dv;

  // Construct the result domain 
  Domain::Ref domain(DMI::ANONWR);
  const Domain &input_domain = input_cells.domain();
  // copy over all axes not involved in the FFT
  for( uint i=0; i<uint(Axis::MaxAxis); i++ )
    if( i != _inaxis0 && i != _inaxis1 && input_domain.isDefined(i) )
      domain().defineAxis(i,input_domain.start(i),input_domain.end(i));
  // define output axes
  domain().defineAxis(_outaxis0,umin,umax);
  domain().defineAxis(_outaxis1,vmin,vmax);
  
  // construct the result cells
  Cells::Ref cells;
  cells <<= new Cells(*domain);
  // copy over all axes not involved in the FFT
  for( uint i=0; i<uint(Axis::MaxAxis); i++ )
    if( i != _inaxis0 && i != _inaxis1 && input_domain.isDefined(i) )
    {
      cells().setCells(i,input_cells.center(i),input_cells.cellSize(i));
      cells().recomputeSegments(i);
    }
  // define output axes
  cells().setCells(_outaxis0,umin,umax,nu);
  cells().setCells(_outaxis1,vmin,vmax,nv);

  // Set the Cells in the Result
  result.setCells(*cells);

  return 0;

};

using namespace blitz;

BZ_DECLARE_STENCIL4(make_interpolation_planes,U,V,UV,X)
  U = (X(-1,0) + X(+1,0))/2;
  V = (X(0,-1) + X(0,+1))/2;
  UV = (X(-1,-1) + X(-1,+1) + X(+1,-1) + X(+1,+1))/4;
BZ_END_STENCIL_WITH_SHAPE(shape(-1,-1),shape(+1,+1))

// Helper function for on-the-fly casting of Blitz arrays from double to dcomplex.
// I cannot get blitz to do this using normal expressions, so here's a version using
// iterators
inline void copyDoubleToComplex ( 
      blitz::Array<dcomplex,2> &out,const LoRange &i1,const LoRange &j1,
      const blitz::Array<double,2> &in,const LoRange &i0,const LoRange &j0)
{
  blitz::Array<dcomplex,2> out1 = out(i1,j1);
  blitz::Array<double,2> in1 = in(i0,j0);
  blitz::Array<dcomplex,2>::iterator iter_out = out1.begin();
  blitz::Array<double,2>::iterator iter_in = in1.begin();
  for( ; iter_out != out1.end(); ++iter_out,++iter_in)
    *iter_out = *iter_in + 0.i;
}

void FFTBrick::doFFT (Vells::Ref output_vells[1],const Vells &input_vells)
{
  Vells::Shape input_shape = input_vells.shape();
  if ( _inaxis0>=input_shape.size() && _inaxis1>=input_shape.size() ) {
    //FailWhen(_inaxis0>=input_shape.size() && _inaxis1>=input_shape.size(),
    //    "one or both input axes are not present in input Vells");
    // No input shape, just a constant input value.
    output_vells[0] <<= new Vells(make_dcomplex(0.0));
  } else {
  
  // check that input axes are present
    //RJN 21-04-2006 
    //FailWhen(_inaxis0>=input_shape.size() && _inaxis1>=input_shape.size(),
    //    "one or both input axes are not present in input Vells");
  // check that output axes of input shape are trivial (unless we're
  // transforming in-place)
  FailWhen((_outaxis0!=_inaxis0 && _outaxis0<input_shape.size() && input_shape[_outaxis0]>1) ||
           (_outaxis1!=_inaxis1 && _outaxis1<input_shape.size() && input_shape[_outaxis1]>1),
      "one or both output axes are present in input Vells");
  // check that input axes have the right nl x nm  shape.
  // NB: ****** BUG
  // This means we fail to deal with collapsed L,M axes. That is, if
  // the input value is constant in L or M (so the Vells shape is 1),
  // we simply fail. The correct behaviour is to expand the input 
  // into the right shape (by populating the missing dimensions
  // with copies of the data). This is a headache I want to avoid for now.
  // Operationally, it's very unlikely that we will want to FFT something
  // that is constant in L or M...
  // NB2: perhaps it would be worthwhile to at least check for a scalar/zero
  // input, and explicitly generate the appropriate FFT.
  FailWhen(input_shape[_inaxis0]!=nl && input_shape[_inaxis1]!=nm,
      "one or both input axes are collapsed in input Vells, this is not yet supported");
  
  // figure out output vells shape and create Vells for the output, and
  // for the intermediate FFT result
  int maxrank = std::max(_outaxis0,_outaxis1);
  Vells::Shape output_shape = input_shape;
  output_shape.resize(maxrank+1,1); // resize to max rank and fill with 1s
  output_shape[_inaxis0] = 1;       // collapse input axes
  output_shape[_inaxis1] = 1;
  output_shape[_outaxis0] = nu;     // fill output axes
  output_shape[_outaxis1] = nv;
  // output vells (and also padded input vells)
  Vells & vells0  = output_vells[0] <<= new Vells(make_dcomplex(0.0),output_shape,true);
  // intermediate FFT result
  Vells fft_vells(make_dcomplex(0.0),output_shape,false); // no need to fill it, fft will do it

  // Rearrange the data and pad with zeros
  // set up VellsSlicers over input vells and over padded vells, so that
  // we go over all other axes.
  // Do separate code for cases of real and complex input
  if( input_vells.isReal() )
  {
    ConstVellsSlicer<double,2> input_slicer(input_vells,_inaxis0,_inaxis1);
    VellsSlicer<dcomplex,2> padded_input_slicer(vells0,_outaxis0,_outaxis1);
    for( ; padded_input_slicer.valid(); padded_input_slicer.incr(),input_slicer.incr())
    {
      Assert(input_slicer.valid()); 
      // must be true since all other axes have the same shape
      const blitz::Array<double,2> in_arr = input_slicer();
      blitz::Array<dcomplex,2> pad_arr = padded_input_slicer();
/* AGW quadrant flip - part 1 */
      uint j = nl1-2;
      for( uint i=0; i<nl-nl1+1; i++ ){
        copyDoubleToComplex(pad_arr,makeLoRange(j,j),makeLoRange(0,nm-nm1),
            in_arr,makeLoRange(i,i),makeLoRange(nm1-1,nm-1));
        copyDoubleToComplex(pad_arr,makeLoRange(j,j),makeLoRange(nv-nm1+1,nv-1),
            in_arr,makeLoRange(i,i),makeLoRange(0,nm1-2));
        j = j - 1;
      }

/*
   // previous FFTBrick quadrant flip
   copyDoubleToComplex(pad_arr,makeLoRange(nu-nl1+1,nu-1),makeLoRange(0,nm-nm1), 
        in_arr,makeLoRange(0,nl1-2),makeLoRange(nm1-1,nm-1));
   copyDoubleToComplex(pad_arr,makeLoRange(nu-nl1+1,nu-1),makeLoRange(nv-nm1+1,nv-1),
        in_arr,makeLoRange(0,nl1-2),makeLoRange(0,nm1-2));
*/

/* AGW quadrant flip - part 2 */
      j = nu-1;
      for( uint i=nl1-1; i<nl; i++ ) {
        copyDoubleToComplex(pad_arr,makeLoRange(j,j),makeLoRange(0,nm-nm1), 
            in_arr,makeLoRange(i,i),makeLoRange(nm1-1,nm-1));
        copyDoubleToComplex(pad_arr,makeLoRange(j,j),makeLoRange(nv-nm1+1,nv-1),
            in_arr,makeLoRange(i,i),makeLoRange(0,nm1-2));
        j = j - 1;
      }

/*
   // previous FFTBrick quadrant flip
   copyDoubleToComplex(pad_arr,makeLoRange(0,nl-nl1),makeLoRange(0,nm-nm1),
        in_arr,makeLoRange(nl1-1,nl-1),makeLoRange(nm1-1,nm-1));
   copyDoubleToComplex(pad_arr,makeLoRange(0,nl-nl1),makeLoRange(nv-nm1+1,nv-1),
        in_arr,makeLoRange(nl1-1,nl-1),makeLoRange(0,nm1-2));
*/
    };
  }

  else // complex input
  {
    ConstVellsSlicer<dcomplex,2> input_slicer(input_vells,_inaxis0,_inaxis1);
    VellsSlicer<dcomplex,2> padded_input_slicer(vells0,_outaxis0,_outaxis1);
    for( ; padded_input_slicer.valid(); padded_input_slicer.incr(),input_slicer.incr())
    {
      Assert(input_slicer.valid()); 
      // must be true since all other axes have the same shape
      const blitz::Array<dcomplex,2> in_arr = input_slicer();
      blitz::Array<dcomplex,2> pad_arr = padded_input_slicer();
      //dcomplex aa,bb,cc;
      //aa=in_arr(257,255);bb=in_arr(257,257);cc=in_arr(255,257);
      //std::cout<<"Array values\t"<<__real__ aa<<"\t"<<__real__ bb
      //     <<"\t"<<__real__ cc<<"\n"<<std::flush;

/* AGW quadrant flip - part 1 */
      uint j = nl1-2;
      for( uint i=0; i<nl-nl1+1; i++ ){
        pad_arr(makeLoRange(j,j),makeLoRange(0,nm-nm1)) =
            in_arr(makeLoRange(i,i),makeLoRange(nm1-1,nm-1));
        pad_arr(makeLoRange(j,j),makeLoRange(nv-nm1+1,nv-1)) =
            in_arr(makeLoRange(i,i),makeLoRange(0,nm1-2));
        j = j - 1;
      }

/*
      // previous version
      pad_arr(makeLoRange(nu-nl1+1,nu-1),makeLoRange(0,nm-nm1)) = 
          in_arr(makeLoRange(0,nl1-2),makeLoRange(nm1-1,nm-1));
      pad_arr(makeLoRange(nu-nl1+1,nu-1),makeLoRange(nv-nm1+1,nv-1)) = 
          in_arr(makeLoRange(0,nl1-2),makeLoRange(0,nm1-2));
*/

/* AGW quadrant flip - part 2 */
      j = nu-1;
      for( uint i=nl1-1; i<nl; i++ ) {
        pad_arr(makeLoRange(j,j),makeLoRange(0,nm-nm1)) = 
            in_arr(makeLoRange(i,i),makeLoRange(nm1-1,nm-1));
        pad_arr(makeLoRange(j,j),makeLoRange(nv-nm1+1,nv-1)) =
            in_arr(makeLoRange(i,i),makeLoRange(0,nm1-2));
        j = j - 1;
      }

/*
      // previous version
      pad_arr(makeLoRange(0,nl-nl1),makeLoRange(0,nm-nm1)) = 
          in_arr(makeLoRange(nl1-1,nl-1),makeLoRange(nm1-1,nm-1));    
      pad_arr(makeLoRange(0,nl-nl1),makeLoRange(nv-nm1+1,nv-1)) = 
          in_arr(makeLoRange(nl1-1,nl-1),makeLoRange(0,nm1-2));
*/
    };
  }
  // Prepare the FFT
  // compute array strides (using the Vells' convenience function)
  // they're the same for input (padded) and output vells
  Vells::Strides strides;
  vells0.computeStrides(strides);
  
  // fill in the FFT'd dimensions
  fftw_iodim fft_dims[2];
  fft_dims[0].n = nu;
  fft_dims[0].is = fft_dims[0].os = strides[_outaxis0];
  fft_dims[1].n = nv;
  fft_dims[1].is = fft_dims[1].os = strides[_outaxis1];
  // fill in the other (non-FFT'd) dimensions
  // first, figure out how many "other" dimensions are present
  int num_other_dims = 0;
  for( uint i=0; i<output_shape.size(); i++ )
    if( i != _outaxis0 && i != _outaxis1 && output_shape[i]>1 )
      num_other_dims++;
  fftw_iodim other_dims[num_other_dims];
  int idim=0;
  // note that the output axes will be skipped in this loop, 
  // since we check for output_shape[i]>1, and the FailWhen() statement
  // above ensures that output axes are either the same as input, or degenerate
  for( uint i=0; i<output_shape.size(); i++ )
    if( i != _outaxis0 && i != _outaxis1 && output_shape[i]>1 )
    {
      other_dims[idim].n  = output_shape[i];
      other_dims[idim].is = other_dims[idim].os = strides[i];
      idim++;
    }
  
  // get pointers to data from padded_vells and fft_result
  fftw_complex *pdata_in = static_cast<fftw_complex*>(vells0.getDataPtr());
  fftw_complex *pdata_out = static_cast<fftw_complex*>(fft_vells.getDataPtr());

  // define & execute FFT
  fftw_plan p;
  p = fftw_plan_guru_dft(2,fft_dims,num_other_dims,other_dims,pdata_in,pdata_out,FFTW_FORWARD,FFTW_ESTIMATE);

// p = fftw_plan_dft_2d(nu, nv, pdata_in,pdata_out,FFTW_FORWARD,FFTW_ESTIMATE);
  fftw_execute(p);
  fftw_destroy_plan(p);
  
  // Reshuffle fft'd data around, and fill in the interpolation planes
  // This is similar to the operation above.
  // We'll use VellsSlicers to repeat this for all other dimensions
  ConstVellsSlicer<dcomplex,2> fft_slicer(fft_vells,_outaxis0,_outaxis1);
  VellsSlicer<dcomplex,2> result_slicer(vells0,_outaxis0,_outaxis1);
  for( ; fft_slicer.valid(); 
       fft_slicer.incr(),result_slicer.incr())
  {
    Assert(result_slicer.valid()); // must be true since all other axes have the same shape
    const blitz::Array<dcomplex,2> fft_arr = fft_slicer();
    blitz::Array<dcomplex,2> out_arr = result_slicer();

    // AGW reshuffle fft data into output array
    uint j = nu1-2;
    for( uint i=0; i<nu-nu1+1; i++ ){
      out_arr(makeLoRange(j,j),makeLoRange(0,nv1-2)) = 
        fft_arr(makeLoRange(i,i),makeLoRange(nv-nv1+1,nv-1));
      out_arr(makeLoRange(j,j),makeLoRange(nv1-1,nv-1)) = 
        fft_arr(makeLoRange(i,i),makeLoRange(0,nv-nv1));
      j = j - 1;
    }

    j = nu-1;
    for( uint i=nu-nu1+1; i<nu; i++ ) {
      out_arr(makeLoRange(j,j),makeLoRange(0,nv1-2)) = 
        fft_arr(makeLoRange(i,i),makeLoRange(nv-nv1+1,nv-1));
      out_arr(makeLoRange(j,j),makeLoRange(nv1-1,nv-1)) = 
        fft_arr(makeLoRange(i,i),makeLoRange(0,nv-nv1));
      j = j - 1;
    }
/*
    // previous FFTBrick reshuffle
    // reshuffle fft data into output array
    out_arr(makeLoRange(nu1-1,nu-1),makeLoRange(0,nv1-2)) =
        fft_arr(makeLoRange(0,nu-nu1),makeLoRange(nv-nv1+1,nv-1));
    out_arr(makeLoRange(nu1-1,nu-1),makeLoRange(nv1-1,nv-1)) =
        fft_arr(makeLoRange(0,nu-nu1),makeLoRange(0,nv-nv1));
    out_arr(makeLoRange(0,nu1-2),makeLoRange(0,nv1-2)) =
        fft_arr(makeLoRange(nu-nu1+1,nu-1),makeLoRange(nv-nv1+1,nv-1));
    out_arr(makeLoRange(0,nu1-2),makeLoRange(nv1-1,nv-1)) =
        fft_arr(makeLoRange(nu-nu1+1,nu-1),makeLoRange(0,nv-nv1));
*/
  }
  }
}

void FFTBrick::setStateImpl (DMI::Record::Ref& rec, bool initializing)
{
  Node::setStateImpl(rec,initializing);
  rec["UVppw"].get(_uvppw,initializing);

  std::vector<HIID> in = _in_axis_id;
  if( rec[FAxesIn].get_vector(in,initializing) || initializing )
  {
    FailWhen(in.size()!=2,FAxesIn.toString()+" field must have 2 elements");
    _in_axis_id = in;
    Axis::addAxis(_in_axis_id[0]);
    Axis::addAxis(_in_axis_id[1]);
  }
  std::vector<HIID> out = _out_axis_id;
  if( rec[FAxesOut].get_vector(out,initializing) || initializing )
  {
    FailWhen(out.size()!=2,FAxesOut.toString()+" field must have 2 elements");
    _out_axis_id = out;
    Axis::addAxis(_out_axis_id[0]);
    Axis::addAxis(_out_axis_id[1]);
  }
  // do not check that axes are valid -- this is done in getResult()
};
  
} // namespace Meq

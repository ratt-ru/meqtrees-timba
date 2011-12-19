//# UVInterpol.cc
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

// This version of the UVInterpol node interpolates a UVBrick in meters.
// The interpolation point is found for the first frequency plane and then
// used for all the other frequency planes.

#include <MeqNodes/UVInterpolWave.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
#include <MEQ/Axis.h>
#include <MEQ/VellsSlicer.h>
#include <MeqNodes/UVDetaper.h>

namespace Meq {
  static const HIID child_labels[] = { AidBrick,AidUVW,AidCoeff };
  static const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);
  const Result * UVInterpolWave::reported_freq_warning_ = 0;
  
  UVInterpolWave::UVInterpolWave():
    // OMS: the "2" below means that only the first two children (Brick and UVW)
    // are mandatory
    Node(num_children,child_labels,2)
  {
    fillWeightsArray();

    _in1_axis_id.resize(3);
    _in1_axis_id[0] = "FREQ";
    _in1_axis_id[1] = "U";
    _in1_axis_id[2] = "V";
    _in2_axis_id.resize(1);
    _in2_axis_id[0] = "TIME";
    _out_axis_id.resize(2);
    _out_axis_id[0] = "U";
    _out_axis_id[1] = "V";
  };

  UVInterpolWave::~UVInterpolWave(){};

  void UVInterpolWave::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
  };

  int UVInterpolWave::getResult (Result::Ref &resref,
				 const std::vector<Result::Ref> &child_results,
				 const Request &request,bool newreq)
  {
    if( child_results.size()==2 )
    {
      // OMS: 2 children, no coeffs
    }
    else
    {
      // OMS: 3 children, so child_results[2] are the coeffs
    }
    // this is from fftbrick and second from uvw antenna track
    const Result & FFTbrickUV = child_results.at(0);
    const Result & BaselineUV = child_results.at(1);
    // OMS: commented this out, has to be optional
    //    const Result & CoeffsUV = child_results.at(2);
    //
    // figure out the axes: for now assume that there are only
    // time for Baselines and nothing for brick.
    // Not sure yet how many there will be...
    _inaxis0 = Axis::axis(_in1_axis_id[0]);
    _inaxis1 = Axis::axis(_in1_axis_id[1]);
    _inaxis2 = Axis::axis(_in1_axis_id[2]);
    _inaxis3 = Axis::axis(_in2_axis_id[0]);
    _outaxis0 = Axis::axis(_out_axis_id[0]);
    _outaxis1 = Axis::axis(_out_axis_id[1]);

    // Get the Cells of the children
    // and ensure that input axes are present and
    // uniformly gridded
    const Cells & BaselineCells = BaselineUV.cells();
    const Cells & FFTbrickCells = FFTbrickUV.cells();
    // OMS: commented this out, has to be optional
    // const Cells & CoeffCells = CoeffsUV.cells();
    FailWhen(//Check that the time is there for the  baseline.
	     !BaselineCells.isDefined(_inaxis3) ,
	     "Time not defined in the antenna cell");

    // Get the request cell reference
    const Cells& rcells = request.cells();
    // Get the number of cells in the uv plane
    nn = rcells.ncells(_inaxis0);
    nt = rcells.ncells(_inaxis3);
    nf = FFTbrickCells.ncells(_inaxis0);
    nu = FFTbrickCells.ncells(_inaxis1);
    nv = FFTbrickCells.ncells(_inaxis2);
    tmin = min(rcells.cellStart(Axis::TIME));
    tmax = max(rcells.cellEnd(Axis::TIME));
    fmin = min(rcells.cellStart(Axis::FREQ));
    fmax = max(rcells.cellEnd(Axis::FREQ));

    //INI: A warning is printed for each MeqUVInterpolWave node created i.e., for each baseline
    //Too many warning messages if too many baselines are present
    //OMS: added a report_freq_warning_ static member.
    // This is set to the address of the brick result. We only print the warning when we get
    // a different brick, i.e. once per every brick.
    if( reported_freq_warning_ != &FFTbrickUV )
    {
      if( rcells.center(_inaxis0)(nn-1) < FFTbrickCells.center(_inaxis0)(0) || rcells.center(_inaxis0)(0) > FFTbrickCells.center(_inaxis0)(nf-1) )
      {
        std::cerr<<"WARNING: The requested MS frequencies are out of range of the input frequencies"<<endl;
        reported_freq_warning_ = &FFTbrickUV;
      }
      else if( rcells.center(_inaxis0)(0) < FFTbrickCells.center(_inaxis0)(0) || rcells.center(_inaxis0)(nf-1) > FFTbrickCells.center(_inaxis0)(nf-1) )
      {
        std::cerr<<"WARNING: Partial frequency mismatch between the input image and the requested MS frequencies"<<endl;
        reported_freq_warning_ = &FFTbrickUV;
      }
    }
    

    // Set Vells shape
    Vells::Shape tfshape;
    Axis::degenerateShape(tfshape,2);
    tfshape[Axis::TIME] = nt;
    tfshape[Axis::FREQ] = nn;

    // What is the dimensions of the result
    // out put is a vector for each nu and time
    Result::Dims dims(FFTbrickUV.dims());

    // OMS: removed this. The purpose of this statement was to remove
    // the last dimension (which was interpolation coeffs) from the result shape.
    // But now that FFTBrickUV no longer includes the coeffs, the result dims
    // must be the same as the FFTBrickUV dims
    // dims.resize(dims.size()-1);

    // Making the results now:
    // First allocate a new results and ref to output
    Result & result = resref <<= new Result(dims);

    int ovs = 0;  // counter of output VellSets
    // In this loop we look at each non-perturbed and each perturbed values
    // in the gridded_ uv VellSet in the input... Not considering perturbed
    // values for the antenna positions at least for now can add later...
    const VellSet &us_input_uv = BaselineUV.vellSet(0);
    const VellSet &vs_input_uv = BaselineUV.vellSet(1);
    for( int ivs = 0; ivs<FFTbrickUV.numVellSets(); ivs+=1 )
      {
	// Get reference to input vells...
	const VellSet &brick_input = FFTbrickUV.vellSet(ivs);
	// OMS: commented this out, should be made optional
//	const VellSet &coeff_inputu = CoeffsUV.vellSet(4*ivs+1);
//	const VellSet &coeff_inputv = CoeffsUV.vellSet(4*ivs+2);
//	const VellSet &coeff_inputuv= CoeffsUV.vellSet(4*ivs+3);
	//std::cout<<dims<<"\t"<<ovs<<"\t"<<ivs<<"\n";
	VellSet &output_vell_set = result.setNewVellSet(ovs);
        ovs++;
	// OMS: if the input VellSet is a null, then output at corresponding
        // position should also be null. Allocating output_vell_set and not filling
        // it produces a null, which is exactly what we want, so we just continue here.
	if( brick_input.isNull() )
          continue;

	// Create the output vells

	// actual values (main + possibly perturbed on the X vell
	// only for now...).
	// Setup copies of spid/perturbations.
	output_vell_set.setNumPertSets(brick_input.numPertSets());
	output_vell_set.copySpids(brick_input);
	output_vell_set.copyPerturbations(brick_input);

	// Now do interpolation
	Vells & output_vells =
	  output_vell_set.setValue(new Vells(make_dcomplex(57.0,54.9),
					     tfshape,true));
	doInterpol(output_vells,
		   us_input_uv.getValue(),vs_input_uv.getValue(),
        // OMS: removed coeff arguments
		   brick_input.getValue(),
		   rcells,FFTbrickCells);

	// Interpolate each perturbed value
	for( int ipset=0; ipset<brick_input.numPertSets(); ipset++ )
	  for( int ipert=0; ipert<brick_input.numSpids(); ipert++ )
	    {
	      Vells & output_vells =
		output_vell_set.setPerturbedValue(ipert,
						  new Vells(make_dcomplex(0),
							    tfshape,true),
						  ipset);
	      doInterpol(output_vells,
			 us_input_uv.getValue(),
			 vs_input_uv.getValue(),
                         // OMS: removed coeff arguments
			 brick_input.getPerturbedValue(ipert,ipset),
			 rcells,FFTbrickCells);
	    }

	// finalize shapes of output vellsets
	output_vell_set.verifyShape();
      }

    // Construct the result domain
    Domain::Ref domain(DMI::ANONWR);
//    const Domain &BaselineUV_domain = BaselineCells.domain();
//    const Domain &FFTbrickUV_domain = FFTbrickCells.domain();
    // Copy the axis TIME and NU
    domain().defineAxis(Axis::TIME,tmin,tmax);
    domain().defineAxis(Axis::FREQ,fmin,fmax);
    // construct the result cells
    Cells::Ref cells;
    cells <<= new Cells(*domain);
    // copy the TIME and NU axis
    cells().setCells(Axis::TIME,tmin,tmax,nt);
    cells().setCells(Axis::FREQ,fmin,fmax,nn);
    result.setCells(*cells);
    return 0;
  };

  void UVInterpolWave::doInterpol(Vells & output_vell,
				  const Vells &input_vells_u,
				  const Vells &input_vells_v,
				  const Vells &input_vells_grid,
                                  // OMS: removed coeff arguments
				  const Cells &rcells,
				  const Cells &brickcells){
    // This does not support yet that there might not be a frequency
    // or a time axis, we have to add that at some point!!!
    ConstVellsSlicer<dcomplex,3> grid_slicer(input_vells_grid,
					     _inaxis0,_inaxis1,_inaxis2);
    // OMS: removed coeff slicers
    ConstVellsSlicer<double,1> u_slicer(input_vells_u,Axis::TIME);
    ConstVellsSlicer<double,1> v_slicer(input_vells_v,Axis::TIME);

    // OMS: made these const-reference (as opposed to copy.)
    // The copying was NOT thread-safe.
    const blitz::Array<dcomplex,3> &garr = grid_slicer();
    const blitz::Array<double,1> &u_arr = u_slicer();
    const blitz::Array<double,1> &v_arr = v_slicer();
    // OMS: removed coeff arrays

    // We are assuming that any other parameters
    // are the same in the UV and that U and V are dependent of time
    // axis only given that u and v are in meters...
    Assert(grid_slicer.valid());
    Assert(u_slicer.valid());
    Assert(v_slicer.valid());

    // Get an array pointer to the
    // OMS: made these const-reference (as opposed to copy.)
    VellsSlicer<dcomplex,2> out_slicer(output_vell,Axis::TIME,Axis::FREQ);
    blitz::Array<dcomplex,2> &arrout = out_slicer();

    const LoVec_double &uu = brickcells.center(Axis::axis("U"));
    const LoVec_double &vv = brickcells.center(Axis::axis("V"));
    const LoVec_double &ff = brickcells.center(Axis::FREQ);
    const LoVec_double &freq = rcells.center(Axis::FREQ);
    const double c0 = 299792458.;

    //const double du = uu(1)-uu(0);
    //const double dv = vv(1)-vv(0);
    const double du = brickcells.cellSize(Axis::axis("U"))(0);
    const double dv = brickcells.cellSize(Axis::axis("V"))(0);

    //INI: If only one frequency plane present in the brick...
    if(nf == 1)
    {
	    extrapolate = true;
	    lfreq = 0;
	    ufreq = 0;
    }
    //INI: boolean value to det. whether the fftbrick freq. are in ascending order.
    else
    {
	if( ff(0) < ff(nf-1) )
		ffbrick_asc = true;
	else
		ffbrick_asc = false;
    }

    for (int i=0;i<nt;i++){
      for (int j=0;j<nn;j++){

	    freq_match = false;
 	    //INI: Determine whether to extrapolate or interpolate	    
	    //for(int k=0; k<nf; k++)
	    if(nf > 1) // Enter for loop only if more than one plane is present in brick
	    {
	    for(int k=1; k<nf; k++)
	    {
		    if(freq(j) == ff(0)){ //special check for brick plane 0, since the index starts from 1.
			    lfreq = 0;
			    ufreq = 0;
			    extrapolate = true; // Not technically extrapolation, but only one freq. plane is used
			    freq_match = true;
			    break;
		    }
		    if(freq(j) == ff(k)){
			    lfreq = k;
			    ufreq = k;
			    extrapolate = true; // Not technically extrapolation, but only one freq. plane is used
			    freq_match = true;
			    break;
		    }
		    else if( (freq(j)>ff(k-1) && (freq(j)<ff(k)) ) || ( freq(j)<ff(k-1) && (freq(j)>ff(k)) ) )
		    {
			    lfreq = k-1;
			    ufreq = k;
			    extrapolate = false;
			    freq_match = true;
			    break;
		    }
	    }
	    //INI: check for extrapolation
	    if(!freq_match){ //if the request frequency freq(j) was not found...
		    extrapolate = true;
		    if( (ffbrick_asc && freq(j) < ff(0)) || (!ffbrick_asc && freq(j) > ff(0)) ){
			    lfreq = 0;
			    ufreq = 0;
		    }
		    else{
			    lfreq = nf-1;
			    ufreq = nf-1;
		    }
	    }
	    } //end of if(nf>1)

        // convert u/v from meters into wavelengths
	double ulambda = -u_arr(i)*freq(j)/c0;
	double vlambda = -v_arr(i)*freq(j)/c0;
        // ...and now into a fractional "cell" coordinate within our uvbrick
	double ucell = (ulambda - uu(0))/du;
	double vcell = (vlambda - vv(0))/dv;
        // now determine the bounding box over which we convolve
	int iu1 = int(floor(ucell-cutoffparam))+1;
	int iu2 = int(floor(ucell+cutoffparam));
	int iv1 = int(floor(vcell-cutoffparam))+1;
	int iv2 = int(floor(vcell+cutoffparam));
        // does our bounding box intersect the domain of our uv-brick at all?
        // if not, insert zero at this point, and go on to the next point
        if( iu1 >= nu || iu2 < 0 || iv1 >= nv || iv2 < 0 )
        {
          arrout(i,j) = make_dcomplex(0);
          continue;
        }
        // work out intersection of the bounding box with our overall uv-plane
        iu1 = std::max(0,iu1);
        iu2 = std::min(iu2,nu-1);
        iv1 = std::max(0,iv1);
        iv2 = std::min(iv2,nv-1);
        // sums of values and sum of weights
	dcomplex arr_value = make_dcomplex(0.0);
	double sum_weight = 0.;
	//std::cout<<nu<<"\t"<<nv<<"\t"<<u_arr(0)*freq(0)/c0
	// <<"\t"<<iv1<<"\t"<<iv2<<"\n"<<std::flush;
	for( int jj=iv1; jj<=iv2; jj++)
        {
	  double weight_v = weights_arr(int(round(fabs(jj-vcell)* griddivisions)));
	  for( int ii=iu1; ii<=iu2; ii++ )
          {
	    double weight_u = weights_arr(int(round(fabs(ii-ucell)* griddivisions)));
            double weight = weight_v*weight_u;
	    if(extrapolate) //INI: only one frequency plane used
	    	arr_value  += weight*garr(lfreq,ii,jj);
	    else //INI: interpolate between two frequency planes
	    	arr_value  += weight*(garr(lfreq,ii,jj)+garr(ufreq,ii,jj));
	    sum_weight += weight;
	  }
	}
        // just in case we didn't sum anything...
	if( sum_weight == 0 )
          arrout(i,j) = make_dcomplex(0);
        else if(extrapolate)
	  arrout(i,j) = arr_value/sum_weight;
	else //INI: two frequency planes used in each iteration - the factor of 2 accounts for that
	  arrout(i,j) = arr_value/(2.0*sum_weight);
      }
    }
  }


//  int UVInterpolWave::cutoffparam = 2;
  int UVInterpolWave::cutoffparam = 4;
  int UVInterpolWave::griddivisions = 10000;
  int UVInterpolWave::weightsparam = 3;
  LoVec_double UVInterpolWave::weights_arr(cutoffparam*griddivisions+1);
  bool UVInterpolWave::weights_arr_filled = false;
  Thread::Mutex UVInterpolWave::weights_arr_mutex;

  void UVInterpolWave::fillWeightsArray ()
  {
    Thread::Mutex::Lock lock(weights_arr_mutex);
    if( weights_arr_filled )
      return;
    for (int i=0;i<=cutoffparam*griddivisions;i++)
    {
      weights_arr(i)=UVDetaper::sphfn(weightsparam,(2*cutoffparam),0,
				      float(i)/(cutoffparam*griddivisions));
      //std::cout<<i<<"\t"<<weights_arr(i)<<"\n"<<std::flush;
    }
    weights_arr_filled = true;
  }

} // namespace Meq

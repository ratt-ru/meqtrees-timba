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

namespace Meq {
  static const HIID child_labels[] = { AidBrick, AidUVW, AidCoeff};
  static const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);
  
  UVInterpolWave::UVInterpolWave():
    Node(num_children,child_labels),
    _method(1)
  {
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
    rec["UVInterpol_method"].get(_method,initializing);
  };
  
  int UVInterpolWave::getResult (Result::Ref &resref,
				 const std::vector<Result::Ref> &child_results,
				 const Request &request,bool newreq)
  {  
    // Check that there are 2 results first, maybe have 3 
    // inputs later for the convolution as well...
    Assert(child_results.size()==3);
    // this is from fftbrick and second from uvw antenna track
    const Result & FFTbrickUV = child_results.at(0);
    const Result & BaselineUV = child_results.at(1);
    const Result & CoeffsUV = child_results.at(2);
  
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
    const Cells & CoeffCells = CoeffsUV.cells();
    FailWhen(//Check that the time is there for the  baseline.
	     !BaselineCells.isDefined(_inaxis3) ,
      "Time not defined in the antenna cell");

    // Get the request cell reference
    const Cells& rcells = request.cells();
    // Get the number of cells in the uv plane
    nu = FFTbrickCells.ncells(_inaxis1);
    nv = FFTbrickCells.ncells(_inaxis2);
    nn = rcells.ncells(_inaxis0);
    nt = rcells.ncells(_inaxis3);
    tmin = min(rcells.cellStart(Axis::TIME));
    tmax = max(rcells.cellEnd(Axis::TIME));
    fmin = min(rcells.cellStart(Axis::FREQ));
    fmax = max(rcells.cellEnd(Axis::FREQ));

    // Set Vells shape
    Vells::Shape tfshape;
    Axis::degenerateShape(tfshape,2);
    tfshape[Axis::TIME] = nt;
    tfshape[Axis::FREQ] = nn;

    // What is the dimensions of the result
    // out put is a vector for each nu and time
    Result::Dims dims(FFTbrickUV.dims());
    dims.resize(dims.size()-1);
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
	const VellSet &coeff_inputu = CoeffsUV.vellSet(4*ivs+1);
	const VellSet &coeff_inputv = CoeffsUV.vellSet(4*ivs+2);
	const VellSet &coeff_inputuv= CoeffsUV.vellSet(4*ivs+3);
	// Create the output vells
	VellSet &output_vell_set =  result.setNewVellSet(ovs) ;ovs++;
	//std::cout<<dims<<"\t"<<ovs<<"\t"<<ivs<<"\n";
	// if the input VellSet is a null, make null outputs and continue
	if( brick_input.isNull() )
	  {
	    // Ignore this for now... might be making a mistake...
	    //Vells::Ref null_vells(DMI::ANONWR);
	    //output_vell_set.setValue(null_vells);ovs++;
	    //continue;
	  }
	
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
		   brick_input.getValue(),coeff_inputu.getValue(),
		   coeff_inputv.getValue(),coeff_inputuv.getValue(),
		   rcells,FFTbrickCells);
	
	// Interpolate each perturbed value
	for( int ipset=0; ipset<brick_input.numPertSets(); ipset++ )
	  for( int ipert=0; ipset<brick_input.numSpids(); ipert++ )
	    {
	      Vells & output_vells = 
		output_vell_set.setPerturbedValue(ipert,
						  new Vells(make_dcomplex(0),
							    tfshape,true),
						  ipset);
	      doInterpol(output_vells,
			 us_input_uv.getValue(),
			 vs_input_uv.getValue(),
			 brick_input.getPerturbedValue(ipert,ipset),
			 coeff_inputu.getPerturbedValue(ipert,ipset),
			 coeff_inputv.getPerturbedValue(ipert,ipset),
			 coeff_inputuv.getPerturbedValue(ipert,ipset),
			 rcells,FFTbrickCells);
	    }
	
	// finalize shapes of output vellsets
	output_vell_set.verifyShape();
      }
    
    // Construct the result domain 
    Domain::Ref domain(DMI::ANONWR);
    const Domain &BaselineUV_domain = BaselineCells.domain();
    const Domain &FFTbrickUV_domain = FFTbrickCells.domain();
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
				  const Vells &CoeffvellsU, 
				  const Vells &CoeffvellsV, 
				  const Vells &CoeffvellsUV, 
				  const Cells &rcells, 
				  const Cells &brickcells){
    // This does not support yet that there might not be a frequency 
    // or a time axis, we have to add that at some point!!!
    ConstVellsSlicer<dcomplex,3> grid_slicer(input_vells_grid,
					     _inaxis0,_inaxis1,_inaxis2);
    ConstVellsSlicer<dcomplex,3> interp_sliceru(CoeffvellsU,
						Axis::FREQ,_inaxis1,_inaxis2);
    ConstVellsSlicer<dcomplex,3> interp_slicerv(CoeffvellsV,
						Axis::FREQ,_inaxis1,_inaxis2);
    ConstVellsSlicer<dcomplex,3> interp_sliceruv(CoeffvellsUV,
						 Axis::FREQ,_inaxis1,_inaxis2);
    ConstVellsSlicer<double,1> u_slicer(input_vells_u,Axis::TIME);
    ConstVellsSlicer<double,1> v_slicer(input_vells_v,Axis::TIME);
 
    blitz::Array<dcomplex,3> farru = interp_sliceru();    
    blitz::Array<dcomplex,3> farrv = interp_slicerv();    
    blitz::Array<dcomplex,3> farruv= interp_sliceruv();
    blitz::Array<dcomplex,3> garr = grid_slicer();
    blitz::Array<double,1> u_arr = u_slicer();
    blitz::Array<double,1> v_arr = v_slicer();

    // We are assuming that any other parameters
    // are the same in the UV and that U and V are dependent of time 
    // axis only given that u and v are in meters...
    Assert(grid_slicer.valid()); 
    Assert(interp_sliceru.valid()); 
    Assert(interp_slicerv.valid()); 
    Assert(interp_sliceruv.valid()); 
    Assert(u_slicer.valid()); 
    Assert(v_slicer.valid()); 

    // Get an array pointer to the  
    VellsSlicer<dcomplex,2> out_slicer(output_vell,Axis::TIME,Axis::FREQ);
    blitz::Array<dcomplex,2> arrout = out_slicer();
   
    // Here we have to do the hard work!!!!!!!!!!!!!!!!!!!!!!!!!
    int ulo=1,uhi=nt,vlo=1,vhi=nt;
    const LoVec_double uu = brickcells.center(Axis::axis("U"));
    const LoVec_double vv = brickcells.center(Axis::axis("V"));
    const LoVec_double freq = rcells.center(Axis::FREQ);
    const double c0 = 299792458.;	
    double uc,vc;
    int    ia,ib,ja,jb;
    double t,s;
    for (int i=0;i<nt;i++){
      for (int j=0;j<nn;j++){
	uc = -u_arr(i)*freq(j)/c0;
	vc = -v_arr(i)*freq(j)/c0;
	ia = 0;
	ib = nu-1;
	ja = 0;
	jb = nv-1;
	for (int i1 = 0; i1 < nu-1; i1++){
	  if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1;ib = i1+1;};
	};
	for (int j1 = 0; j1 < nv-1; j1++){
	  if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1; jb=j1+1;};
	};
	s = (uc-uu(ia))/(uu(ib)-uu(ia));
	t = (vc-vv(ja))/(vv(jb)-vv(ja));
	if (_method == 1) arrout(i,j)= bilinear(s,t,
					       garr(0,ia,ja),garr(0,ia,jb),
					       garr(0,ib,jb),garr(0,ib,ja));
	if (_method == 2) arrout(i,j)=BiCubic(s,t,
					     garr(0,ia,ja),garr(0,ia,jb), 
					     garr(0,ib,jb),garr(0,ib,ja),
					     farru(0,ia,ja),farru(0,ia,jb), 
					     farru(0,ib,jb), farru(0,ib,ja),
					     farrv(0,ia,ja), farrv(0,ia,jb), 
					     farrv(0,ib,jb), farrv(0,ib,ja),
					     farruv(0,ia,ja), farruv(0,ia,jb), 
					     farruv(0,ib,jb), farruv(0,ib,ja));
      }
    }
    
    // Here we have finished doing the hard work!!!!!!!!!!!!!!!!
    
  }

  dcomplex UVInterpolWave::bilinear(double s, double t, 
				    dcomplex fiaja, dcomplex fiajb, 
				    dcomplex fibjb, dcomplex fibja )  {
    return (1-t)*(1-s)*fiaja + s*(1-t)*fibja + t*(1-s)*fiajb + t*s*fibjb;   
  };

  dcomplex UVInterpolWave::BiCubic(double s, double t, 
				   dcomplex fiaja, dcomplex fiajb, 
				   dcomplex fibjb, dcomplex fibja, 
				   dcomplex fuiaja, dcomplex fuiajb, 
				   dcomplex fuibjb, dcomplex fuibja, 
				   dcomplex fviaja, dcomplex fviajb, 
				   dcomplex fvibjb, dcomplex fvibja, 
				   dcomplex fuviaja, dcomplex fuviajb, 
				   dcomplex fuvibjb, dcomplex fuvibja){
    return (1-t)*(1-s)*fiaja + s*(1-t)*fibja 
      + (1-s)*t*fiajb + t*s*fibjb
      + t*s*s*(1-s)*(fibjb-fuibjb) + t*s*(1-s)*(1-s)*(fiajb-fuiajb)
      + (1-t)*s*s*(1-s)*(fibja-fuibja) 
      + (1-t)*s*(1-s)*(1-s)*(fiaja-fuiaja)
      + t*t*s*(1-t)*(fibjb-fvibjb) + t*t*(1-t)*(1-s)*(fiajb-fviajb)
      + (1-t)*s*t*(1-t)*(fibja-fvibja) 
      + t*(1-t)*(1-t)*(1-s)*(fiaja-fviaja)
      + t*t*(1-t)*s*s*(1-s)*(fibjb - fvibjb - fuibjb + fuvibjb)
      + t*t*(1-t)*s*(1-s)*(1-s)*(fiajb - fviajb - fuiajb + fuviajb)
      + t*(1-t)*(1-t)*s*s*(1-s)*(fibja - fvibja - fuibja + fuvibja)
      + t*(1-t)*(1-t)*s*(1-s)*(1-s)*(fiaja - fviaja - fuiaja + fuviaja);
  };
  
  
} // namespace Meq

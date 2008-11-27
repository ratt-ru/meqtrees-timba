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

#include <MeqNodes/UVInterpol.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
#include <MEQ/Axis.h>
#include <MEQ/VellsSlicer.h>

namespace Meq {
  
  UVInterpol::UVInterpol(){
    _in_axis_id.resize(4);
    _in_axis_id[0] = "U";
    _in_axis_id[1] = "V";
    _in_axis_id[2] = "FREQ";
    _in_axis_id[3] = "TIME";
    _out_axis_id.resize(2);
    _out_axis_id[0] = "FREQ";
    _out_axis_id[1] = "TIME";
  };
  
  UVInterpol::~UVInterpol()
  {
  };

  void UVInterpol::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
    rec["UVInterpol_method"].get(_method,initializing);

  };
  
  int UVInterpol::getResult (Result::Ref &resref,
			  const std::vector<Result::Ref> &child_results,
			  const Request &request,bool newreq)
  {  
    // Check that there are 2 results first, maybe have 3 
    // inputs later for the convolution as well...
    Assert(child_results.size()==2);
    const Result & uv_antenna = child_results[0];
    const Result & gridded_uv = child_results[1];
    
    // figure out the axes: for now assume that there are 4 axis
    // input and 2 axis output which are fixed, maybe later check that
    // one of the axis is not used... 
    // Not sure yet how many there will be...
    _inaxis0 = Axis::axis(_in_axis_id[0]);
    _inaxis1 = Axis::axis(_in_axis_id[1]);
    _inaxis2 = Axis::axis(_in_axis_id[2]);
    _inaxis3 = Axis::axis(_in_axis_id[3]);
    _outaxis0 = Axis::axis(_out_axis_id[0]);
    _outaxis1 = Axis::axis(_out_axis_id[1]);

    // Get the Cells of the children 
    // and ensure that input axes are present and
    // uniformly gridded
    const Cells & input_cells_uv = uv_antenna.cells();
    const Cells & input_cells_grid = gridded_uv.cells();
    FailWhen(!input_cells_uv.isDefined(_inaxis3) ||  
	     // Check that T is there 
	     !input_cells_grid.isDefined(_inaxis0) ||
	     !input_cells_grid.isDefined(_inaxis1) ||
	     !input_cells_grid.isDefined(_inaxis2) ||
	     !input_cells_grid.isDefined(_inaxis3),  
	     // Check that the rest is there and later allow
	     // for lack of nu and time
      "one of the axes is not defined in a child cell");

    // Get the number of cells in the uv plane
    nu = input_cells_grid.ncells(_inaxis0);
    nv = input_cells_grid.ncells(_inaxis1);
    nn = input_cells_grid.ncells(_inaxis2);
    nt = input_cells_uv.ncells(_inaxis3);
    // Check that if there is a time on the grid
    // then the time numbers must equal nt on the uv vector
    FailWhen(nt != input_cells_grid.ncells(_inaxis3),
      "different number of time steps each child cell");

    // What is the dimensions of the result
    // out put is a vector for each nu and time
    Result::Dims dims(gridded_uv.dims());
    // Making the results now:
    // First allocate a new results and ref to output
    Result & result = resref <<= new Result(dims);

    int ovs = 0;  // counter of output VellSets
    // In this loop we look at each non-perturbed and each perturbed values
    // in the gridded_ uv VellSet in the input... Not considering perturbed 
    // values for the antenna positions at least for now can add later...
    for (int i_uv = 0; i_uv < 2; i_uv++)
      // we loop over only the u and v but dont check if there is 
      // more components as w might tag along as well
      for( int ivs = 0; ivs<gridded_uv.numVellSets(); ivs++ )
	{
	  // Get reference to input vells...
	  const VellSet &vs_input = gridded_uv.vellSet(ivs);
	  const VellSet &vs_input_uv = uv_antenna.vellSet(i_uv);
	  // Create the output vells
	  VellSet * output_vell_set;
	  output_vell_set = &( result.setNewVellSet(ovs) );ovs++;
	  
	  // if the input VellSet is a null, make null outputs and continue
	  if( vs_input.isNull() )
	    {
	      Vells::Ref null_vells(DMI::ANONWR);
	      output_vell_set->setValue(null_vells);ovs++;
	      continue;
	    }
	  
	  // actual values (main + possibly perturbed on the X vell 
	  // only for now...). 
	  // Setup copies of spid/perturbations.
	  output_vell_set->setNumPertSets(vs_input.numPertSets());
	  output_vell_set->copySpids(vs_input);
	  output_vell_set->copyPerturbations(vs_input);
	  
	  // Now do interpolation
	  Vells::Ref output_vells;
	  doInterpol(output_vells,vs_input_uv.getValue(),vs_input.getValue());
	  output_vell_set->setValue(output_vells);
	  
	  // Interpolate each perturbed value
	  for( int ipset=0; ipset<vs_input.numPertSets(); ipset++ )
	    for( int ipert=0; ipset<vs_input.numSpids(); ipert++ )
	      {
		doInterpol(output_vells,
			   vs_input_uv.getValue(),
			   vs_input.getPerturbedValue(ipert,ipset));
		output_vell_set->setPerturbedValue(ipert,output_vells,ipset);
	      }
	  
	  // finalize shapes of output vellsets
	  output_vell_set->verifyShape();
	}

    // Construct the result domain 
    Domain::Ref domain(DMI::ANONWR);
    const Domain &uv_antenna_domain = input_cells_uv.domain();
    const Domain &gridded_uv_domain = input_cells_grid.domain();
    // OK, I still have to work out if thisd is the correct way 
    // to set these domains...
    // Copy the axis TIME and NU
    domain().defineAxis(_inaxis2,gridded_uv_domain.start(_inaxis2),
			gridded_uv_domain.end(_inaxis2));
    domain().defineAxis(_inaxis3,uv_antenna_domain.start(_inaxis3),
			uv_antenna_domain.end(_inaxis3));
    // copy over all axes which are not TIME and NU and u or v
    for( uint i=0; i<uint(Axis::MaxAxis); i++ )
      if( i != _inaxis0 && i != _inaxis1 && i != _inaxis2 && i != _inaxis3 && 
	  (uv_antenna_domain.isDefined(i) || gridded_uv_domain.isDefined(i)))
	if (gridded_uv_domain.isDefined(i))
	  domain().defineAxis(i,gridded_uv_domain.start(i),
			      gridded_uv_domain.end(i));
	else
	  domain().defineAxis(i,uv_antenna_domain.start(i),
			      uv_antenna_domain.end(i));
    // construct the result cells
    Cells::Ref cells;
    cells <<= new Cells(*domain);
    // copy the TIME and NU axis first
    cells().setCells(_inaxis2,input_cells_grid.center(_inaxis2),
		     input_cells_grid.cellSize(_inaxis2));
    cells().setCells(_inaxis3,input_cells_uv.center(_inaxis3),
		     input_cells_uv.cellSize(_inaxis3));
    // copy over all axes not involved 
    for( uint i=0; i<uint(Axis::MaxAxis); i++ )
      if( i != _inaxis0 && i != _inaxis1 && i != _inaxis2 && i != _inaxis3 && 
	 (uv_antenna_domain.isDefined(i) || gridded_uv_domain.isDefined(i)))
	{
	  if (gridded_uv_domain.isDefined(i))
	    cells().setCells(i,input_cells_grid.center(i),
			     input_cells_grid.cellSize(i));
	  else
	    cells().setCells(i,input_cells_uv.center(i),
			     input_cells_uv.cellSize(i));
	  cells().recomputeSegments(i);
	}
    // Set the Cells in the Result
    result.setCells(*cells);

    return 0;    
  };
  
  void UVInterpol::doInterpol(Vells::Ref &output_vell,
			      const Vells &input_vells_uv,
			      const Vells &input_vells_grid){
    Vells::Shape input_shape_uv = input_vells_uv.shape();
    Vells::Shape input_shape_grid = input_vells_grid.shape();
    if ( _inaxis0>=input_shape_uv.size() && _inaxis1>=input_shape_uv.size() ) {
      //FailWhen(_inaxis0>=input_shape.size() && _inaxis1>=input_shape.size(),
      //    "one or both input axes are not present in input Vells");
      // No input shape, just a constant input value.
      output_vell <<= new Vells(make_dcomplex(0.0));
    } else {
      // This does not support yet that there might not be a frequency 
      // or a time axis, we have to add that at some point!!!
      ConstVellsSlicer<dcomplex,4> grid_slicer(input_vells_grid,_inaxis0,
					       _inaxis1,_inaxis2,_inaxis3);
      ConstVellsSlicer<dcomplex,1> uv_slicer(input_vells_uv,_inaxis3);

      // We are assuming that any other parameters
      // are the same in the UV and that U and V are dependent of time 
      // axis only given that u and v are in meters...
      for( ; grid_slicer.valid(); grid_slicer.incr(),uv_slicer.incr())
	{
	  Assert(grid_slicer.valid()); Assert(uv_slicer.valid()); 
	  // must be true since all other axes have the same shape
	  blitz::Array<dcomplex,1> uv_arr = uv_slicer();
	  blitz::Array<dcomplex,4> grid_arr = grid_slicer();

	  // figure out output vells shape and create Vells for the result
	  Vells::Shape output_shape = input_shape_grid;
	  // Again here we have to change if the input_grid does not depend on
	  // time or frequency... To do later...
	  // resize to max rank and fill with 1s
	  output_shape[_inaxis0] = 1;       // collapse input axes
	  output_shape[_inaxis1] = 1;
	  output_shape[_outaxis0] = nn;     // fill output axes
	  output_shape[_outaxis1] = nt;
	  output_vell <<= new Vells(make_dcomplex(0.0),output_shape,false);

	  // Here we have to do the hard work!!!!!!!!!!!!!!!!!!!!!!!!!

	  // Here we have finished doing the hard work!!!!!!!!!!!!!!!!
	}
    }
  }

} // namespace Meq

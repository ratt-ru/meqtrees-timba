//# PatchComposer.cc: First version of the Node
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

#include <MeqNodes/PatchComposer.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
#include <MEQ/VellsSlicer.h>
#include <casa/BasicMath/Math.h>
#include <casa/BasicSL/Constants.h>

namespace Meq {
  
  PatchComposer::PatchComposer()
    :
    _max_baseline(2700.0),
    _uvppw(1.0)
  {
    _out_axis_id.resize(3);
    _out_axis_id[0] = "FREQ";
    _out_axis_id[1] = "L";
    _out_axis_id[2] = "M";
    Axis::addAxis("L");
    Axis::addAxis("M");
  };
  
  PatchComposer::~PatchComposer()
  {
  };
  
  
  int PatchComposer::getResult (Result::Ref &resref,
			  const std::vector<Result::Ref> &childres,
			  const Request &request,bool newreq)
  {
    // Speed of light
    const double c0 = casa::C::c;

    // Get the Request Cells
    const Cells& rcells = request.cells();

    // Set the output axes
    _outaxis0 = Axis::axis(_out_axis_id[0]);
    _outaxis1 = Axis::axis(_out_axis_id[1]);  
    _outaxis2 = Axis::axis(_out_axis_id[2]);

    
    if (rcells.isDefined(Axis::FREQ)) {

      const int num_children = int(childres.size());

      // When there are no children, nothing is done
      // Is this ok?

      // Check that we do not have to define a new result like: resref <<= new Result(6);
      
      // The first child should always be a two-pack of the Phase Center
      // Does this need any checking? Do we want to generalize this?
      // Attach the RA and Dec of the Phase Center to the first two planes
      if (num_children > 0){
	
	resref = childres.at(0);
	
      };
      
      // When there is more than one child, we assume that those additional children are Point Source sixpacks.
      // Does this need any checking? Generalization?
      // Add the Sources into the Patch
      if (num_children > 1){
	
	// Extend the already created two planes of the Phase Center with 4 more planes for the Stokes values
	VellSet& vs2 = resref().setNewVellSet(2);
	VellSet& vs3 = resref().setNewVellSet(3);
	VellSet& vs4 = resref().setNewVellSet(4);
	VellSet& vs5 = resref().setNewVellSet(5);
	
	// Create the grid (Domain, Cells, Shape) in frequency dependend l' and m' coordinates
	double lmax(0.0),mmax(0.0);
	double lc,mc,ra,dec,ra0,dec0, lf, mf;
	Vells RAvells0, Decvells0;
	Vells RAvells, Decvells;
	Vells Ivells, Qvells, Uvells, Vvells;
	double sI, sQ, sU, sV;

	RAvells0 = childres.at(0)->vellSet(0).getValue();
	Decvells0 = childres.at(0)->vellSet(1).getValue();
	ra0 = RAvells0(0);
	dec0 = Decvells0(0);

	for (int src = 1; src<num_children; src++) {
	  RAvells = childres.at(src)->vellSet(0).getValue();
	  Decvells = childres.at(src)->vellSet(1).getValue();
	  ra = RAvells(0);
	  dec = Decvells(0);

	  lc = casa::cos(dec) * casa::sin(ra-ra0);
       	  mc = casa::cos(dec0) * casa::sin(dec) - 
      	    casa::sin(dec0) * casa::cos(dec) * casa::cos(ra-ra0);

       	  lmax = casa::max(lmax,casa::abs(lc));
       	  mmax = casa::max(mmax,casa::abs(mc));

	};

	// Make a 3D Cells of Frequency, l' (freq dependent l), and m' (frequency dpendent m)
	const double fmax = max(rcells.cellEnd(Axis::FREQ));
	const double fmin = min(rcells.cellStart(Axis::FREQ));
	const LoVec_double freq = rcells.center(Axis::FREQ);
	const int nf = rcells.ncells(Axis::FREQ);

	lmax *= fmax/c0;
	mmax *= fmax/c0;

	const double dl = 1 / (2*_max_baseline +1./_uvppw/lmax);
	const double dm = 1 / (2*_max_baseline +1./_uvppw/mmax);

	// Make sure all sources are actually falling INSIDE the grid
	int nl = 2*int(lmax/dl)+3;
	int nm = 2*int(mmax/dm)+3;

	lmax = nl*dl/2;
	mmax = nm*dm/2;

	Domain::Ref domain(new Domain());
	domain().defineAxis(Axis::axis("L"),-lmax,lmax);
	domain().defineAxis(Axis::axis("M"),-mmax,mmax);
	domain().defineAxis(Axis::FREQ,fmin,fmax);

	Cells::Ref cells(new Cells(*domain));
	cells().setCells(Axis::FREQ,fmin,fmax,nf);
	cells().setCells(Axis::axis("L"),-lmax,lmax,nl);
	cells().setCells(Axis::axis("M"),-mmax,mmax,nm);

	Vells::Shape shape;
	Axis::degenerateShape(shape,cells->rank());
	shape[Axis::axis("L")] = cells->ncells(Axis::axis("L"));
	shape[Axis::axis("M")] = cells->ncells(Axis::axis("M"));
	shape[Axis::FREQ] = cells->ncells(Axis::FREQ);


	// Now start filling the Stokes planes
	// set the result to all 0, hence last argument 'true'
	// SBY: need to reset memeory to 0 before calculations are done
	Vells& vells2 = vs2.setValue(new Vells(double(0.0),shape,true));
	Vells& vells3 = vs3.setValue(new Vells(double(0.0),shape,true));
	Vells& vells4 = vs4.setValue(new Vells(double(0.0),shape,true));
	Vells& vells5 = vs5.setValue(new Vells(double(0.0),shape,true));

	int ni, nj;
	LoVec_double Ivec(nf), Qvec(nf), Uvec(nf), Vvec(nf);
	
//blitz::Array<double,3> arrI = vells2.as<double,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
	//blitz::Array<double,3> arrQ = vells3.as<double,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
	//blitz::Array<double,3> arrU = vells4.as<double,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());	
	//blitz::Array<double,3> arrV = vells5.as<double,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

	VellsSlicer<double,3> I_slicer(vells2,_outaxis0,_outaxis1,_outaxis2);
	VellsSlicer<double,3> Q_slicer(vells3,_outaxis0,_outaxis1,_outaxis2);
	VellsSlicer<double,3> U_slicer(vells4,_outaxis0,_outaxis1,_outaxis2);
	VellsSlicer<double,3> V_slicer(vells5,_outaxis0,_outaxis1,_outaxis2);

	blitz::Array<double,3> arrI = I_slicer();
	blitz::Array<double,3> arrQ = Q_slicer();
	blitz::Array<double,3> arrU = U_slicer();
	blitz::Array<double,3> arrV = V_slicer();

	for (int src = 1; src<num_children; src++) {
	  // For every Point Source sixpack child, put source on nearest pixel position

	  RAvells = childres.at(src)->vellSet(0).getValue();
	  Decvells = childres.at(src)->vellSet(1).getValue();
	  Ivells = childres.at(src)->vellSet(2).getValue();
	  Qvells = childres.at(src)->vellSet(3).getValue();
	  Uvells = childres.at(src)->vellSet(4).getValue();
	  Vvells = childres.at(src)->vellSet(5).getValue();

	  // The following part of code needs further checks
	  // SBY: sometimes we get vectors of dimension [1xnf], instead of vectors [nfx1]. So need to check this
	  if (Ivells.isScalar()){
	    for (int j =0; j<nf; j++) Ivec(j) = Ivells(0);
	  } else {
	    if (Ivells.extent(0) <nf) {
	      //expect an 1xnf array
	      for (int j =0; j<nf; j++) Ivec(j) = Ivells(0,j);
	    } else {
	      //expect an nfx1 array
	      for (int j =0; j<nf; j++) Ivec(j) = Ivells(j);
	    }
	  };
	  if (Qvells.isScalar()){
	    for (int j =0; j<nf; j++) Qvec(j) = Qvells(0);
	  } else {
	    if (Qvells.extent(0) <nf) {
	      for (int j =0; j<nf; j++) Qvec(j) = Qvells(0,j);
	    } else {
	      for (int j =0; j<nf; j++) Qvec(j) = Qvells(j);
	    }
	  };
	  if (Uvells.isScalar()){
	    for (int j =0; j<nf; j++) Uvec(j) = Uvells(0);
	  } else {
	    if (Uvells.extent(0) <nf) {
	      for (int j =0; j<nf; j++) Uvec(j) = Uvells(0,j);
	    } else {
	      for (int j =0; j<nf; j++) Uvec(j) = Uvells(j);
	    }
	  };
	  if (Vvells.isScalar()){
	    for (int j =0; j<nf; j++) Vvec(j) = Vvells(0);
	  } else {
	    if (Vvells.extent(0) <nf) {
	      for (int j =0; j<nf; j++) Vvec(j) = Vvells(0,j);
	    } else {
	      for (int j =0; j<nf; j++) Vvec(j) = Vvells(j);
	    }
	  };

	  ra = RAvells(0);
	  dec = Decvells(0);

	  lc = casa::cos(dec) * casa::sin(ra-ra0);
       	  mc = casa::cos(dec0) * casa::sin(dec) - 
      	    casa::sin(dec0) * casa::cos(dec) * casa::cos(ra-ra0);
    
	  // RJN: For now we neglect this. It has been fixed by making the grid somewhat larger
	  // SBY: remember lower and upper bounds of arrays
	  //blitz::TinyVector<int, 3> lbounds=arrI.lbound();
	  //blitz::TinyVector<int, 3> ubounds=arrI.ubound();
	  //// all other arrays have same dimensions
	  ////std::cout<<"Bounds "<<arrI.lbound()<<arrI.ubound()<<endl;
	  
	  for (int j =0; j<nf; j++){

	    lf = freq(j)*lc/c0;
	    mf = freq(j)*mc/c0;

	    sI = Ivec(j);
	    sQ = Qvec(j);
	    sU = Uvec(j);
	    sV = Vvec(j);

	    // Round off position to nearest pixel position
	    if (lf>0) {
	      ni = (nl-1)/2 + 1 + int(lf/dl+0.5)-1;
	    } else {
	      ni = (nl-1)/2 + 1 + int(lf/dl-0.5)-1;
	    };
	    if (mf>0) {
	      nj = (nm-1)/2 + 1 + int(mf/dm+0.5)-1;
	    } else {
	      nj = (nm-1)/2 + 1 + int(mf/dm-0.5)-1;
	    };

	    // This is also neglected for now (see above)
	    //if ((j<=ubounds[0])&&(j>=lbounds[0])
	    //	&&(ni<=ubounds[1])&&(ni>=lbounds[1])
	    //	&&(nj<=ubounds[2])&&(nj>=lbounds[2])){
	    arrI(j,ni,nj) = sI;
	    arrQ(j,ni,nj) = sQ;
	    arrU(j,ni,nj) = sU;
	    arrV(j,ni,nj) = sV;
	    // }

	  };

	};

	resref().setCells(*cells);
	
      };
      
    };
    
    return 0;
    
  };
  
  void PatchComposer::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
    rec["Max.Baseline"].get(_max_baseline,initializing);
    rec["UVppw"].get(_uvppw,initializing);

    std::vector<HIID> out = _out_axis_id;
    if( rec[PAxesOut].get_vector(out,initializing) || initializing )
      {
	FailWhen(out.size()!=3,PAxesOut.toString()+"field must have 3 elements");
	_out_axis_id = out;
	Axis::addAxis(_out_axis_id[0]);
	Axis::addAxis(_out_axis_id[1]);
	Axis::addAxis(_out_axis_id[2]);
      };
  };
  
} // namespace Meq

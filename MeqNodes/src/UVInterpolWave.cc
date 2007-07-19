//# UVInterpolWave.cc
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

// This version of the UVInterpol node interpolates a UVBrick in wavelengths.
// The interpolation point is found for all frequency planes separately.

#include <MeqNodes/UVInterpolWave.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
#include <MEQ/AID-Meq.h>
#include <MEQ/VellsSlicer.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/aips.h>
#include <casa/BasicSL/Constants.h>
#include <casa/BasicMath/Math.h>

namespace Meq {

  InitDebugContext(UVInterpolWave,"Interpol");

  static const HIID child_labels[] = { AidBrick, AidUVW };
  static const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);
  
#define VERBOSE

  UVInterpolWave::UVInterpolWave():
    Node(num_children,child_labels),
    _additional_info(false),
    _method(1)
  {
    disableAutoResample();
    _in1_axis_id.resize(3);
    _in1_axis_id[0] = "FREQ";
    _in1_axis_id[1] = "U";
    _in1_axis_id[2] = "V";
    _out1_axis_id.resize(2);
    _out1_axis_id[0] = "TIME";
    _out1_axis_id[1] = "FREQ";
    _in2_axis_id.resize(1);
    _in2_axis_id[0] = "TIME";
    _out2_axis_id.resize(2);
    _out2_axis_id[0] = "U";
    _out2_axis_id[1] = "V";

  };
  
  UVInterpolWave::~UVInterpolWave()
  {
  };

  void UVInterpolWave::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
    rec["Additional.Info"].get(_additional_info,initializing);
    rec["Method"].get(_method,initializing);

    std::vector<HIID> in1 = _in1_axis_id;
    if( rec[DAxesIn1].get_vector(in1,initializing) || initializing )
      {
	FailWhen(in1.size() !=3,DAxesIn1.toString()+" field must have 3 elements");
	_in1_axis_id = in1;
	Axis::addAxis(_in1_axis_id[0]);
	Axis::addAxis(_in1_axis_id[1]);
	Axis::addAxis(_in1_axis_id[2]);
      };
    std::vector<HIID> out1 = _out1_axis_id;
    if( rec[DAxesOut1].get_vector(out1,initializing) || initializing )
      {
	FailWhen(out1.size() !=2,DAxesOut1.toString()+" field must have 2 elements");
	_out1_axis_id = out1;
	Axis::addAxis(_out1_axis_id[0]);
	Axis::addAxis(_out1_axis_id[1]);
      };

    std::vector<HIID> in2 = _in2_axis_id;
    if( rec[DAxesIn2].get_vector(in2,initializing) || initializing )
      {
	FailWhen(in2.size() !=1,DAxesIn2.toString()+" field must have 1 elements");
	_in2_axis_id = in2;
	Axis::addAxis(_in2_axis_id[0]);
      };
    std::vector<HIID> out2 = _out2_axis_id;
    if( rec[DAxesOut2].get_vector(out2,initializing) || initializing )
      {
	FailWhen(out2.size() !=2,DAxesOut2.toString()+" field must have 2 elements");
	_out2_axis_id = out2;
	Axis::addAxis(_out2_axis_id[0]);
	Axis::addAxis(_out2_axis_id[1]);
      };

  }
  
  int UVInterpolWave::getResult (Result::Ref &resref,
			  const std::vector<Result::Ref> &childres,
			  const Request &request,bool newreq)
  {
    // Speed of light
    const double c0 = casa::C::c;

    // Get the request cells
    const Cells& rcells = request.cells();
    const Cells brickcells = childres.at(0)->cells();

    if( rcells.isDefined(Axis::TIME) && brickcells.isDefined(Axis::FREQ))
      {
	// Set input and output axes
	_in1axis0 = Axis::axis(_in1_axis_id[0]);
	_in1axis1 = Axis::axis(_in1_axis_id[1]);
	_in1axis2 = Axis::axis(_in1_axis_id[2]);
	_out1axis0 = Axis::axis(_out1_axis_id[0]);
	_out1axis1 = Axis::axis(_out1_axis_id[1]);
	_in2axis0 = Axis::axis(_in2_axis_id[0]);
	_out2axis0 = Axis::axis(_out2_axis_id[0]);
	_out2axis1 = Axis::axis(_out2_axis_id[1]);

	// Create the Interpolated UVdata 
	// (Integration is not implemented. This is ok for small 
	//   time/freq cells. For larger Cells a 2D Integration Routine 
	//   (Romberg?) must be implemented). 
	    
	// Create Result object and attach to the Ref that was passed in.
	resref <<= new Result(4);                 // Create 4 Result planes
	VellSet& vs0 = resref().setNewVellSet(0); 
	VellSet& vs1 = resref().setNewVellSet(1); 
	VellSet& vs2 = resref().setNewVellSet(2); 
	VellSet& vs3 = resref().setNewVellSet(3); 

	//
	// Make the Result
	//

	int nfbrick = brickcells.ncells(Axis::FREQ);

	Vells::Shape tfshape;
	Axis::degenerateShape(tfshape,2);
	int nt, nf;
	LoVec_double freq;
	double tmin, tmax, fmin, fmax;
	
	if (nfbrick == 1) {
	  // UVBrick is constant in frequency.
	  // Result based on frequency domain of the Request
	  nt = tfshape[Axis::TIME] = rcells.ncells(Axis::TIME);
	  nf = tfshape[Axis::FREQ] = rcells.ncells(Axis::FREQ);
	  freq.resize(nf);
	  freq = rcells.center(Axis::FREQ);
	  tmin = min(rcells.cellStart(Axis::TIME));
	  tmax = max(rcells.cellEnd(Axis::TIME));
	  fmin = min(rcells.cellStart(Axis::FREQ));
	  fmax = max(rcells.cellEnd(Axis::FREQ));
	   
	} else {
	  // Result based on frequency domain of the UVBrick
	  
	  nt = tfshape[Axis::TIME] = rcells.ncells(Axis::TIME);
	  nf = tfshape[Axis::FREQ] = brickcells.ncells(Axis::FREQ);
	  freq.resize(nf);
	  freq = brickcells.center(Axis::FREQ);
	  tmin = min(rcells.cellStart(Axis::TIME));
	  tmax = max(rcells.cellEnd(Axis::TIME));
	  fmin = min(brickcells.cellStart(Axis::FREQ));
	  fmax = max(brickcells.cellEnd(Axis::FREQ));
	  
	};

	Domain::Ref tfdomain(new Domain());
	tfdomain().defineAxis(Axis::TIME,tmin,tmax);
	tfdomain().defineAxis(Axis::FREQ,fmin,fmax);
	Cells::Ref tfcells(new Cells(*tfdomain));
	tfcells().setCells(Axis::TIME,tmin,tmax,nt);
	tfcells().setCells(Axis::FREQ,fmin,fmax,nf); 

	// Make a new Vells and fill with zeros
	//Vells & vells0 = vs0.setValue(new Vells(make_dcomplex(0),tfshape,true));
	//Vells & vells1 = vs1.setValue(new Vells(make_dcomplex(0),tfshape,true));
	//Vells & vells2 = vs2.setValue(new Vells(make_dcomplex(0),tfshape,true));
	//Vells & vells3 = vs3.setValue(new Vells(make_dcomplex(0),tfshape,true));
	
	// Fill the Vells (this is were the interpolation takes place)
	//fillVells(childres,vells0,vells1,vells2,vells3,tfcells);	
	
	const Result::Ref uvpoints = childres.at(1);

	Vells  XXvells = childres.at(0)->vellSet(0).getValue();
	if ( XXvells.isScalar() ){
	  cdebug(1) << "XXVells is a scalar" << endl;
	  vs0 = childres.at(0)-> vellSet(0);
	} else {
	  cdebug(1) << "XXVells is no scalar" << endl;
	  Vells & vells0 = vs0.setValue(new Vells(make_dcomplex(0),tfshape,true));
	  Vells XXvells1 = childres.at(0)->vellSet(1).getValue();
	  Vells XXvells2 = childres.at(0)->vellSet(2).getValue();
	  Vells XXvells3 = childres.at(0)->vellSet(3).getValue();
	  fill1Vells(XXvells,XXvells1,XXvells2,XXvells3,vells0,uvpoints,tfcells, brickcells);
	};

	Vells XYvells = childres.at(0)->vellSet(4).getValue();
	if ( XYvells.isScalar() ){
	  cdebug(1) << "XYVells is a scalar" << endl;
	  vs1 = childres.at(0)-> vellSet(4);
	} else {
	  cdebug(1) << "XYVells is no scalar" << endl;
	  Vells & vells1 = vs1.setValue(new Vells(make_dcomplex(0),tfshape,true));
	  Vells XYvells1 = childres.at(0)->vellSet(5).getValue();
	  Vells XYvells2 = childres.at(0)->vellSet(6).getValue();
	  Vells XYvells3 = childres.at(0)->vellSet(7).getValue();
	  fill1Vells(XYvells,XYvells1,XYvells2,XYvells3,vells1,uvpoints,tfcells, brickcells);
	};

	Vells YXvells = childres.at(0)->vellSet(8).getValue();
	if ( YXvells.isScalar() ){
	  cdebug(1) << "YXVells is a scalar" << endl;
	  vs2 = childres.at(0)-> vellSet(8);
	} else {
	  cdebug(1) << "YXVells is no scalar" << endl;
	  Vells & vells2 = vs2.setValue(new Vells(make_dcomplex(0),tfshape,true));
	  Vells YXvells1 = childres.at(0)->vellSet(9).getValue();
	  Vells YXvells2 = childres.at(0)->vellSet(10).getValue();
	  Vells YXvells3 = childres.at(0)->vellSet(11).getValue();
	  fill1Vells(YXvells,YXvells1,YXvells2,YXvells3,vells2,uvpoints,tfcells, brickcells);
	};

	Vells YYvells = childres.at(0)->vellSet(12).getValue();
	if ( YYvells.isScalar() ){
	  cdebug(1) << "YYVells is a scalar" << endl;
	  vs3 = childres.at(0)-> vellSet(12);
	} else {
	  cdebug(1) << "YYVells is no scalar" << endl;
	  Vells & vells3 = vs3.setValue(new Vells(make_dcomplex(0),tfshape,true));
	  Vells YYvells1 = childres.at(0)->vellSet(13).getValue();
	  Vells YYvells2 = childres.at(0)->vellSet(14).getValue();
	  Vells YYvells3 = childres.at(0)->vellSet(15).getValue();
	  fill1Vells(YYvells,YYvells1,YYvells2,YYvells3,vells3,uvpoints,tfcells, brickcells);
	};

	// Attach the request Cells to the result
	resref().setCells(*tfcells);
	resref().setDims(LoShape(2,2));
      
	if (_additional_info){
	  
	  // Make Additional Info on UV-plane coverage.

	  
	  // Make the Additional Vells
	  
	  Result& res2 = resref["UVInterpol.Map"] <<= new Result(1); 
	  VellSet& vs2 = res2.setNewVellSet(0); 
	  
	  //
	  // Make the Result
	  //		
	  
	  // Make a uv-shape
	  Result::Ref uvpoints;
	  uvpoints = childres.at(1);    
	  
	  // uv grid from UVBrick
	  int nu = brickcells.ncells(Axis::axis("U"));
	  int nv = brickcells.ncells(Axis::axis("V"));
	  const LoVec_double uu = brickcells.center(Axis::axis("U"));
	  const LoVec_double vv = brickcells.center(Axis::axis("V"));
	  const double umin = min(brickcells.cellStart(Axis::axis("U")));
	  const double umax = max(brickcells.cellEnd(Axis::axis("U")));
	  const double vmin = min(brickcells.cellStart(Axis::axis("V")));
	  const double vmax = max(brickcells.cellEnd(Axis::axis("V")));
	  
	  // uv image domain
	  Domain::Ref uvdomain(new Domain());
	  uvdomain().defineAxis(Axis::axis("U"),umin,umax);
	  uvdomain().defineAxis(Axis::axis("V"),vmin,vmax);
	  Cells::Ref uvcells(new Cells(*uvdomain));
	  uvcells().setCells(Axis::axis("U"),umin,umax,nu);
	  uvcells().setCells(Axis::axis("V"),vmin,vmax,nv);    
	  
	  Vells::Shape uvshape;
	  Axis::degenerateShape(uvshape,uvcells->rank());
	  uvshape[Axis::axis("U")] = brickcells.ncells(Axis::axis("U"));
	  uvshape[Axis::axis("V")] = brickcells.ncells(Axis::axis("V"));
	  
	  // Make the new Vells

	  Vells& vells2 = vs2.setValue(new Vells(double(0),uvshape,false));
	  
	  // Fill the Vells 

	  // Determine the mapping onto the uv plane of the time-freq. cell

	  VellsSlicer<double,2> uv_slicer(vells2,_out2axis0,_out2axis1);
	  blitz::Array<double,2> arr2 = uv_slicer();
	  arr2 = 0.0;

	  // u,v values from UVW-Node
	  VellSet uvs = uvpoints->vellSet(0);
	  VellSet vvs = uvpoints->vellSet(1);
	  Vells uvells = uvs.getValue();
	  Vells vvells = vvs.getValue();

	  VellsSlicer<double,1> utime_slicer(uvells,_in2axis0);
	  VellsSlicer<double,1> vtime_slicer(vvells,_in2axis0);
	  blitz::Array<double,1> uarr = utime_slicer();
	  blitz::Array<double,1> varr = vtime_slicer();

	  int imin, jmin;

	  for (int j = 0; j < nf; j++){
	    for (int i = 0; i < nt; i++){
        
	      imin = 0;
	      jmin = 0;
	      
	      	      for (int i1 = 0; i1 < nu-1; i1++){
	      		if ((uu(i1)<=uarr(i)*freq(j)/c0) && (uu(i1+1)>uarr(i)*freq(j)/c0)) {imin = i1;};
	      	      };
	      	      for (int j1 = 0; j1 < nv-1; j1++){
	      		if ((vv(j1)<=varr(i)*freq(j)/c0) && (vv(j1+1)>varr(i)*freq(j)/c0)) {jmin = j1;};
	      	      };
	      
	      arr2(imin,jmin) = j + 1.0;
	      
	    }; // i
	  }; // j
	  
	  // Attach a Cells to the result
	  res2.setCells(*uvcells);

	};
	
      }; 
    
    return 0;
    
  };

  void UVInterpolWave::fillVells(const std::vector<Result::Ref> &fchildres, 
			     Vells &fvells0, Vells &fvells1, Vells &fvells2, Vells &fvells3, const Cells &fcells)
  {
    // Definition of constants
    const double c0 = casa::C::c;  // Speed of light

    // If method has incorrect value, use default method
    if ((_method < 1) || (_method > 3)) _method = 1;

    // Time-Freq boundaries of Result to be produced
    int nt = fcells.ncells(Axis::TIME);
    int nf = fcells.ncells(Axis::FREQ);
    const LoVec_double freq = fcells.center(Axis::FREQ); 
    const LoVec_double time = fcells.center(Axis::TIME); 

    // Get the Child Results: brickresult, brickcells for UVBrick-Node
    //                        uvpoints for UVW-Node
    Result::Ref brickresult;
    Cells brickcells; 
    Result::Ref uvpoints;

    brickresult = fchildres.at(0);
    brickcells = brickresult->cells();
    int nfbrick = brickcells.ncells(Axis::FREQ);
    uvpoints = fchildres.at(1);

    // u, v values from UVW-Node
    VellSet uvs = uvpoints->vellSet(0);
    VellSet vvs = uvpoints->vellSet(1);
    Vells uvells = uvs.getValue();
    Vells vvells = vvs.getValue();

    VellsSlicer<double,1> utime_slicer(uvells,_in2axis0);
    VellsSlicer<double,1> vtime_slicer(vvells,_in2axis0);
    blitz::Array<double,1> uarr = utime_slicer();
    blitz::Array<double,1> varr = vtime_slicer();

    // uv grid from UVBrick
    int nu = brickcells.ncells(Axis::axis("U"));
    int nv = brickcells.ncells(Axis::axis("V"));
    const LoVec_double uu = brickcells.center(Axis::axis("U"));
    const LoVec_double vv = brickcells.center(Axis::axis("V"));
    
    
    // uv-data from UVBrick
    // UVImage data
    VellSet vsfXX = brickresult->vellSet(0);
    Vells vellsfXX = vsfXX.getValue(); 
    //VellSet vsfXY = brickresult->vellSet(4);
    //Vells vellsfXY = vsfXY.getValue(); 
    //VellSet vsfYX = brickresult->vellSet(8);
    //Vells vellsfYX = vsfYX.getValue(); 
    // To avoid empty QUV data: copy XX into Xy and YY into YX
    VellSet vsfXY = brickresult->vellSet(0);
    Vells vellsfXY = vsfXY.getValue(); 
    VellSet vsfYX = brickresult->vellSet(12);
    Vells vellsfYX = vsfYX.getValue(); 
    VellSet vsfYY = brickresult->vellSet(12);
    Vells vellsfYY = vsfYY.getValue(); 
    
    VellsSlicer<dcomplex,3> XX_slicer(vellsfXX,_in1axis0,_in1axis1,_in1axis2);
    VellsSlicer<dcomplex,3> XY_slicer(vellsfXY,_in1axis0,_in1axis1,_in1axis2);
    VellsSlicer<dcomplex,3> YX_slicer(vellsfYX,_in1axis0,_in1axis1,_in1axis2);
    VellsSlicer<dcomplex,3> YY_slicer(vellsfYY,_in1axis0,_in1axis1,_in1axis2);

    blitz::Array<dcomplex,3> farrXX = XX_slicer();
    blitz::Array<dcomplex,3> farrXY = XY_slicer();
    blitz::Array<dcomplex,3> farrYX = YX_slicer();
    blitz::Array<dcomplex,3> farrYY = YY_slicer();

    // Output
    // Make an array, connected to the Vells, with which we fill the Vells.
    VellsSlicer<dcomplex,2> XXtf_slicer(fvells0,_out1axis0,_out1axis1);
    blitz::Array<dcomplex,2> arrXX = XXtf_slicer();
    VellsSlicer<dcomplex,2> XYtf_slicer(fvells1,_out1axis0,_out1axis1);
    blitz::Array<dcomplex,2> arrXY = XYtf_slicer();
    VellsSlicer<dcomplex,2> YXtf_slicer(fvells2,_out1axis0,_out1axis1);
    blitz::Array<dcomplex,2> arrYX = YXtf_slicer();
    VellsSlicer<dcomplex,2> YYtf_slicer(fvells3,_out1axis0,_out1axis1);
    blitz::Array<dcomplex,2> arrYY = YYtf_slicer();

    arrXX = make_dcomplex(0.0);
    arrXY = make_dcomplex(0.0);
    arrYX = make_dcomplex(0.0);
    arrYY = make_dcomplex(0.0);

    double uc,vc;
    int    ia,ib,ja,jb;
    double t,s;

    // Method 3
    dcomplex value, dvalue;
    blitz::Array<double,1> x1(4), x2(4);
    blitz::Array<dcomplex,2> yXX(4,4),yXY(4,4),yYX(4,4),yYY(4,4);

    // Think about order of time and frequency.
    // Can the grid search for the next (i,j) tile be optimised 
    //   by using the previous one as starting position?

    // For all methods: the grid search can still be optimised

    if (_method == 1) {

      // Additional input data Vells

      VellSet vsfuXX = brickresult->vellSet(1);
      Vells fuvellsXX = vsfuXX.getValue(); 
      VellsSlicer<dcomplex,3> uXX_slicer(fuvellsXX,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuarrXX = uXX_slicer();
      
      VellSet vsfvXX = brickresult->vellSet(2);
      Vells fvvellsXX = vsfvXX.getValue(); 
      VellsSlicer<dcomplex,3> vXX_slicer(fvvellsXX,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fvarrXX = vXX_slicer();
      
      VellSet vsfuvXX = brickresult->vellSet(3);
      Vells fuvvellsXX = vsfuvXX.getValue(); 
      VellsSlicer<dcomplex,3> uvXX_slicer(fuvvellsXX,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuvarrXX = uvXX_slicer();
      
      //      VellSet vsfuXY = brickresult->vellSet(5);
      VellSet vsfuXY = brickresult->vellSet(1);
      Vells fuvellsXY = vsfuXY.getValue(); 
      VellsSlicer<dcomplex,3> uXY_slicer(fuvellsXY,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuarrXY = uXY_slicer();
      
      //      VellSet vsfvXY = brickresult->vellSet(6);
      VellSet vsfvXY = brickresult->vellSet(2);
      Vells fvvellsXY = vsfvXY.getValue(); 
      VellsSlicer<dcomplex,3> vXY_slicer(fvvellsXY,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fvarrXY = vXY_slicer();
      
      //      VellSet vsfuvXY = brickresult->vellSet(7);
      VellSet vsfuvXY = brickresult->vellSet(3);
      Vells fuvvellsXY = vsfuvXY.getValue(); 
      VellsSlicer<dcomplex,3> uvXY_slicer(fuvvellsXY,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuvarrXY = uvXY_slicer();
      
      //      VellSet vsfuYX = brickresult->vellSet(9);
      VellSet vsfuYX = brickresult->vellSet(13);
      Vells fuvellsYX = vsfuYX.getValue(); 
      VellsSlicer<dcomplex,3> uYX_slicer(fuvellsYX,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuarrYX = uYX_slicer();
      
      //      VellSet vsfvYX = brickresult->vellSet(10);
      VellSet vsfvYX = brickresult->vellSet(14);
      Vells fvvellsYX = vsfvYX.getValue(); 
      VellsSlicer<dcomplex,3> vYX_slicer(fvvellsYX,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fvarrYX = vYX_slicer();
      
      //      VellSet vsfuvYX = brickresult->vellSet(11);
      VellSet vsfuvYX = brickresult->vellSet(15);
      Vells fuvvellsYX = vsfuvYX.getValue(); 
      VellsSlicer<dcomplex,3> uvYX_slicer(fuvvellsYX,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuvarrYX = uvYX_slicer();
      
      VellSet vsfuYY = brickresult->vellSet(13);
      Vells fuvellsYY = vsfuYY.getValue(); 
      VellsSlicer<dcomplex,3> uYY_slicer(fuvellsYY,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuarrYY = uYY_slicer();
      
      VellSet vsfvYY = brickresult->vellSet(14);
      Vells fvvellsYY = vsfvYY.getValue(); 
      VellsSlicer<dcomplex,3> vYY_slicer(fvvellsYY,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fvarrYY = vYY_slicer();
      
      VellSet vsfuvYY = brickresult->vellSet(15);
      Vells fuvvellsYY = vsfuvYY.getValue(); 
      VellsSlicer<dcomplex,3> uvYY_slicer(fuvvellsYY,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuvarrYY = uvYY_slicer();
      
      if (nfbrick==1){
	// return request frequency grid
	for (int j = 0; j < nf; j++){

	  for (int i = 0; i < nt; i++){
	
	    // Determine the uv-coordinates
      
	    uc = uarr(i)*freq(j)/c0;
	    vc = varr(i)*freq(j)/c0;
	    
	    // Bi-Cubic Hermite Interpolation, where the derivatives are
	    //  approximated by central finite differences (already 
	    //  determined in the UVBrick node).
	    
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
	    
	    arrXX(i,j) = scheme1(s,t,
				 farrXX(0,ia,ja), farrXX(0,ia,jb), farrXX(0,ib,jb), farrXX(0,ib,ja),
				 fuarrXX(0,ia,ja), fuarrXX(0,ia,jb), fuarrXX(0,ib,jb), fuarrXX(0,ib,ja),
				 fvarrXX(0,ia,ja), fvarrXX(0,ia,jb), fvarrXX(0,ib,jb), fvarrXX(0,ib,ja),
				 fuvarrXX(0,ia,ja), fuvarrXX(0,ia,jb), fuvarrXX(0,ib,jb), fuvarrXX(0,ib,ja));

	    arrXY(i,j) = scheme1(s,t,
				 farrXY(0,ia,ja), farrXY(0,ia,jb), farrXY(0,ib,jb), farrXY(0,ib,ja),
				 fuarrXY(0,ia,ja), fuarrXY(0,ia,jb), fuarrXY(0,ib,jb), fuarrXY(0,ib,ja),
				 fvarrXY(0,ia,ja), fvarrXY(0,ia,jb), fvarrXY(0,ib,jb), fvarrXY(0,ib,ja),
				 fuvarrXY(0,ia,ja), fuvarrXY(0,ia,jb), fuvarrXY(0,ib,jb), fuvarrXY(0,ib,ja));
	    
	    arrYX(i,j) = scheme1(s,t,
				 farrYX(0,ia,ja), farrYX(0,ia,jb), farrYX(0,ib,jb), farrYX(0,ib,ja),
				 fuarrYX(0,ia,ja), fuarrYX(0,ia,jb), fuarrYX(0,ib,jb), fuarrYX(0,ib,ja),
				 fvarrYX(0,ia,ja), fvarrYX(0,ia,jb), fvarrYX(0,ib,jb), fvarrYX(0,ib,ja),
				 fuvarrYX(0,ia,ja), fuvarrYX(0,ia,jb), fuvarrYX(0,ib,jb), fuvarrYX(0,ib,ja));
	    
	    arrYY(i,j) = scheme1(s,t,
				 farrYY(0,ia,ja), farrYY(0,ia,jb), farrYY(0,ib,jb), farrYY(0,ib,ja),
				 fuarrYY(0,ia,ja), fuarrYY(0,ia,jb), fuarrYY(0,ib,jb), fuarrYY(0,ib,ja),
				 fvarrYY(0,ia,ja), fvarrYY(0,ia,jb), fvarrYY(0,ib,jb), fvarrYY(0,ib,ja),
	   fuvarrYY(0,ia,ja), fuvarrYY(0,ia,jb), fuvarrYY(0,ib,jb), fuvarrYY(0,ib,ja));
	    
	  }; // i
	}; // j


      } else {
	// nfbrick >   1
	// return brick frequency grid
	for (int j = 0; j < nf; j++){

	  for (int i = 0; i < nt; i++){
	
	    // Determine the uv-coordinates
      
	    uc = uarr(i)*freq(j)/c0;
	    vc = varr(i)*freq(j)/c0;
	    
	    // Bi-Cubic Hermite Interpolation, where the derivatives are
	    //  approximated by central finite differences (already 
	    //  determined in the UVBrick node).
	    
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
	    
	    arrXX(i,j) = scheme1(s,t,
				 farrXX(j,ia,ja), farrXX(j,ia,jb), farrXX(j,ib,jb), farrXX(j,ib,ja),
				 fuarrXX(j,ia,ja), fuarrXX(j,ia,jb), fuarrXX(j,ib,jb), fuarrXX(j,ib,ja),
				 fvarrXX(j,ia,ja), fvarrXX(j,ia,jb), fvarrXX(j,ib,jb), fvarrXX(j,ib,ja),
				 fuvarrXX(j,ia,ja), fuvarrXX(j,ia,jb), fuvarrXX(j,ib,jb), fuvarrXX(j,ib,ja));

	    arrXY(i,j) = scheme1(s,t,
				 farrXY(j,ia,ja), farrXY(j,ia,jb), farrXY(j,ib,jb), farrXY(j,ib,ja),
				 fuarrXY(j,ia,ja), fuarrXY(j,ia,jb), fuarrXY(j,ib,jb), fuarrXY(j,ib,ja),
				 fvarrXY(j,ia,ja), fvarrXY(j,ia,jb), fvarrXY(j,ib,jb), fvarrXY(j,ib,ja),
				 fuvarrXY(j,ia,ja), fuvarrXY(j,ia,jb), fuvarrXY(j,ib,jb), fuvarrXY(j,ib,ja));
	    
	    arrYX(i,j) = scheme1(s,t,
				 farrYX(j,ia,ja), farrYX(j,ia,jb), farrYX(j,ib,jb), farrYX(j,ib,ja),
				 fuarrYX(j,ia,ja), fuarrYX(j,ia,jb), fuarrYX(j,ib,jb), fuarrYX(j,ib,ja),
				 fvarrYX(j,ia,ja), fvarrYX(j,ia,jb), fvarrYX(j,ib,jb), fvarrYX(j,ib,ja),
				 fuvarrYX(j,ia,ja), fuvarrYX(j,ia,jb), fuvarrYX(j,ib,jb), fuvarrYX(j,ib,ja));
	    
	    arrYY(i,j) = scheme1(s,t,
				 farrYY(j,ia,ja), farrYY(j,ia,jb), farrYY(j,ib,jb), farrYY(j,ib,ja),
				 fuarrYY(j,ia,ja), fuarrYY(j,ia,jb), fuarrYY(j,ib,jb), fuarrYY(j,ib,ja),
				 fvarrYY(j,ia,ja), fvarrYY(j,ia,jb), fvarrYY(j,ib,jb), fvarrYY(j,ib,ja),
	   fuvarrYY(j,ia,ja), fuvarrYY(j,ia,jb), fuvarrYY(j,ib,jb), fuvarrYY(j,ib,ja));
	    
	  }; // i
	}; // j
	
      }; // nfbrick = 1 vs. >1

    } else {
      if (_method == 2) {

	if (nfbrick == 1) {

	  for (int j = 0; j < nf; j++){ 

	    for (int i = 0; i < nt; i++){
	
	      // Determine the uv-coordinates
      
	      uc = uarr(i)*freq(j)/c0;
	      vc = varr(i)*freq(j)/c0;
	    
	      // 4th order polynomial interpolation
	      // Numerical Recipes, Sec. 3.6
	    
	      ia = 0;
	      ib = nu-1;
	      ja = 0;
	      jb = nv-1;
	    
	      for (int i1 = 0; i1 < nu-1; i1++){
		if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1-1; ib = i1+2;};
	      };
	      for (int j1 = 0; j1 < nv-1; j1++){
		if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1-1; jb = j1+2;};
	      };
	      
	      for (int i1 =0; i1<4; i1++){
		x1(i1) = uu(ia+i1);
		for (int j1=0; j1<4; j1++){
		  x2(j1) = vv(ja+j1);
		  yXX(i1,j1) = farrXX(0,ia+i1, ja+j1);
		  yXY(i1,j1) = farrXY(0,ia+i1, ja+j1);
		  yYX(i1,j1) = farrYX(0,ia+i1, ja+j1);
		  yYY(i1,j1) = farrYY(0,ia+i1, ja+j1);
		};
	      };
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yXX,4,4,uc,vc,value, dvalue);
	      arrXX(i,j) = value;
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yXY,4,4,uc,vc,value, dvalue);
	      arrXY(i,j) = value;
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yYX,4,4,uc,vc,value, dvalue);
	      arrYX(i,j) = value;
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yYY,4,4,uc,vc,value, dvalue);
	      arrYY(i,j) = value;

	    }; // i
	  }; // j

	} else {
	  // nfbrick > 1
	  for (int j = 0; j < nf; j++){ 

	    for (int i = 0; i < nt; i++){
	
	      // Determine the uv-coordinates
      
	      uc = uarr(i)*freq(j)/c0;
	      vc = varr(i)*freq(j)/c0;
	    
	      // 4th order polynomial interpolation
	      // Numerical Recipes, Sec. 3.6
	    
	      ia = 0;
	      ib = nu-1;
	      ja = 0;
	      jb = nv-1;
	    
	      for (int i1 = 0; i1 < nu-1; i1++){
		if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1-1; ib = i1+2;};
	      };
	      for (int j1 = 0; j1 < nv-1; j1++){
		if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1-1; jb = j1+2;};
	      };
	      
	      for (int i1 =0; i1<4; i1++){
		x1(i1) = uu(ia+i1);
		for (int j1=0; j1<4; j1++){
		  x2(j1) = vv(ja+j1);
		  yXX(i1,j1) = farrXX(j,ia+i1, ja+j1);
		  yXY(i1,j1) = farrXY(j,ia+i1, ja+j1);
		  yYX(i1,j1) = farrYX(j,ia+i1, ja+j1);
		  yYY(i1,j1) = farrYY(j,ia+i1, ja+j1);
		};
	      };
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yXX,4,4,uc,vc,value, dvalue);
	      arrXX(i,j) = value;
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yXY,4,4,uc,vc,value, dvalue);
	      arrXY(i,j) = value;
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yYX,4,4,uc,vc,value, dvalue);
	      arrYX(i,j) = value;
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yYY,4,4,uc,vc,value, dvalue);
	      arrYY(i,j) = value;

	    }; // i
	  }; // j

	}; // nfbrick =1 vs. >1

      } else {
	if (_method == 3) {
	    
	  if (nfbrick == 1) {
	    for (int j = 0; j < nf; j++){

	      for (int i = 0; i < nt; i++){
	
		// Determine the uv-coordinates
		
		uc = uarr(i)*freq(j)/c0;
		vc = varr(i)*freq(j)/c0;
		
		// Bi-linear interpolation (Num. Rec. Sec. 3.6)
		
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
		
		arrXX(i,j) = scheme3(s,t,farrXX(0,ia,ja),farrXX(0,ia,jb),farrXX(0,ib,jb),farrXX(0,ib,ja));
		
		arrXY(i,j) = scheme3(s,t,farrXY(0,ia,ja),farrXY(0,ia,jb),farrXY(0,ib,jb),farrXY(0,ib,ja));
		
		arrYX(i,j) = scheme3(s,t,farrYX(0,ia,ja),farrYX(0,ia,jb),farrYX(0,ib,jb),farrYX(0,ib,ja));
		
		arrYY(i,j) = scheme3(s,t,farrYY(0,ia,ja),farrYY(0,ia,jb),farrYY(0,ib,jb),farrYY(0,ib,ja));
		
	      }; // i
	    }; // j


	  } else {
	    // nfbrick > 1
	    for (int j = 0; j < nf; j++){

	      for (int i = 0; i < nt; i++){
	
		// Determine the uv-coordinates
		
		uc = uarr(i)*freq(j)/c0;
		vc = varr(i)*freq(j)/c0;
		
		// Bi-linear interpolation (Num. Rec. Sec. 3.6)
		
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
		
		arrXX(i,j) = scheme3(s,t,farrXX(j,ia,ja),farrXX(j,ia,jb),farrXX(j,ib,jb),farrXX(j,ib,ja));
		
		arrXY(i,j) = scheme3(s,t,farrXY(j,ia,ja),farrXY(j,ia,jb),farrXY(j,ib,jb),farrXY(j,ib,ja));
		
		arrYX(i,j) = scheme3(s,t,farrYX(j,ia,ja),farrYX(j,ia,jb),farrYX(j,ib,jb),farrYX(j,ib,ja));
		
		arrYY(i,j) = scheme3(s,t,farrYY(j,ia,ja),farrYY(j,ia,jb),farrYY(j,ib,jb),farrYY(j,ib,ja));
		
	      }; // i
	    }; // j

	  }; // if nfbrick = 1 vs. >1

	}; // if method = 3
      }; // else
    }; // if method=1  else
      
  }; // fillVells


    

  //--------------------------------------------------------------------------

  void UVInterpolWave::interpolate(int &j, int &ni,int &imin, int &nj, int &jmin, LoMat_dcomplex &coeff, blitz::Array<dcomplex,3> &barr,LoVec_double uu,LoVec_double vv)
  {

    // Find a complex 2D Interpolating polynimial of order ni * nj
    // I(u,v) = sum_{i,j} c(i,j) * u^i * v^j

    blitz::Array<double,2> A(ni*nj,ni*nj);
    blitz::Array<dcomplex,1> B(ni*nj);
    blitz::Array<int,1> indx(ni*nj);

    double uav = (uu(imin+ni-1) - uu(imin))/2.;
    double vav = (vv(jmin+nj-1) - vv(jmin))/2.;
    double ur = uu(imin+ni-1)-uav;
    double vr = vv(jmin+nj-1)-vav;

    for (int k = 0; k < ni; k++){
      for (int l = 0; l < nj; l++){
	for (int i = 0; i < ni; i++){
	  for (int j = 0; j < nj; j++){

	    A(k*nj+l,i*nj+j) = pow((uu(imin+k)-uav)/ur,i) 
	                     * pow((vv(jmin+l)-vav)/vr,j);

	  };
	};
	B(k*nj+l) = barr(j,imin+k,jmin+l);
      };
    };

    myludcmp(A,ni*nj,indx);
    mylubksb(A,ni*nj,indx,B);

    for (int i = 0; i < ni; i++){
      for (int j = 0; j < nj; j++){
	
	coeff(i,j) = B(i*nj+j);
	  
      };
    };

  };


  void UVInterpolWave::myludcmp(blitz::Array<double,2> &A,int n,blitz::Array<int,1> &indx)
  // My version of the Numerical Recipes's ludcmp routine
  {
    const double tiny = 1.0e-20; 

    double big, temp, sum, dum;
    int imax(0);
    blitz::Array<double,1> vv(n);

    // Loop over rows to get the implicit scaling information
    for (int i=0;i<n;i++){
      big = 0.0;
      for (int j=0;j<n;j++){
	if ((temp=fabs(A(i,j))) > big)
	  { 
	    big = temp;
	  };
	FailWhen(big==0.0,"Singular Matrix in UVInterpolWave::myludcmp");
	vv(i) = 1.0/big;
      };
    };

    //This is the loop over columns of Crout's method
    for (int j=0; j<n; j++){

      for (int i=0; i<j; i++){
	sum = A(i,j);
	for (int k=0; k<i; k++) sum -= A(i,k)*A(k,j);
	A(i,j) = sum;
      };

      big = 0.0;
      for (int i=j; i<n; i++){
	sum = A(i,j);
	for (int k=0; k<j; k++) sum -= A(i,k)*A(k,j);
	A(i,j) = sum;
	if ( (dum=vv(i)*fabs(sum)) >= big) {
	  big = dum;
	  imax = i;
	};
      };

      if (j != imax) {
	for (int k=0; k<n; k++){
	  dum = A(imax,k);
	  A(imax,k) = A(j,k);
	  A(j,k) = dum;
	};
	vv(imax) = vv(j);
      };

      indx(j)=imax;
      if (A(j,j) == 0.0) A(j,j) = tiny;
      if (j!=n-1){
	dum=1.0/A(j,j);
	for (int i=j+1;i<n;i++) A(i,j) *= dum;
      };

    };

  };


  void UVInterpolWave::mylubksb(blitz::Array<double,2> &A,int n,blitz::Array<int,1> &indx, blitz::Array<dcomplex,1> &B)
  // My version of the Numerical Recipes's lubksb routine
  {
    int ip, ii=-1;
    dcomplex sum;

    for (int i=0; i<n; i++){
      ip = indx(i);
      sum = B(ip);
      B(ip) = B(i);
      if (ii!=-1)
	for (int j=ii; j<=i-1;j++) sum -= A(i,j)*B(j);
      else if (abs(sum)!=0.0) ii=i;
      B(i) = sum;
    };

    for (int i=n-1; i>-1; i--){
      sum = B(i);
      for (int j = i+1; j<n; j++) sum -= A(i,j)*B(j);
      B(i) = sum / A(i,i);
    };

  };

  //---------------------------------------------------------------------------

  void UVInterpolWave::mysplie2(blitz::Array<double,1> &x1a, blitz::Array<double,1> &x2a, blitz::Array<dcomplex,2> &ya, int &m, int &n, blitz::Array<dcomplex,2> &y2a)
  // My version of splie2 from the Numerical Recipes (Sec. 3.6)
  {
    blitz::Array<dcomplex,1> ytmp(n), yytmp(n);

    for (int j=0; j<m; j++){
      for (int i=0; i<n; i++){
	ytmp(i) = ya(j,i);
      };
      UVInterpolWave::myspline(x2a,ytmp,n,1.0e30,1.0e30,yytmp);
      for (int i=0; i<n; i++){
	y2a(j,i) = yytmp(i);
      };
    };

  };

  void UVInterpolWave::mysplin2(blitz::Array<double,1> &x1a, blitz::Array<double,1> &x2a, blitz::Array<dcomplex,2> &ya, blitz::Array<dcomplex,2> &y2a, int &m, int &n, double &x1, double &x2, dcomplex &y)
  // My version of splin2 from the Numerical Recipes (Sec. 3.6)
  {
    blitz::Array<dcomplex,1> ytmp(n), yytmp(m), y2tmp(n);

    for (int j=0; j<m; j++){
      for (int i=0; i<n; i++){
	ytmp(i) = ya(j,i);
	y2tmp(i) = y2a(j,i);
      };
      UVInterpolWave::mysplint(x2a,ytmp,y2tmp,n,x2,yytmp(j));
    };
    UVInterpolWave::myspline(x1a,yytmp,m,1.0e30,1.0e30,y2tmp);
    UVInterpolWave::mysplint(x1a,yytmp,y2tmp,m,x1,y);

  };

  void UVInterpolWave::myspline(blitz::Array<double,1> &x, blitz::Array<dcomplex,1> &y,int &n, double yp1, double ypn, blitz::Array<dcomplex,1> &y2)
  // My version of spline from the Numerical Recipes (Sec. 3.3)
  // Using natural splines only 
  {
    blitz::Array<dcomplex,1> u(n);
    double sig, qn, un;
    dcomplex p;

    // Natural spline
    y2(0) = u(0) = make_dcomplex(0.0);

    for (int i=1;i<n-1;i++){
      sig = (x(i)-x(i-1))/(x(i+1)-x(i-1));
      p = sig*y2(i-1)+2.0;
      y2(i)=(sig-1.0)/p;
      u(i)=(y(i+1)-y(i))/(x(i+1)-x(i)) - (y(i)-y(i-1))/(x(i)-x(i-1));
      u(i)=(6.0*u(i)/(x(i+1)-x(i-1))-sig*u(i-1))/p;
    };
    
    // Natural spline
    qn = un = 0.0;

    y2(n-1) = (un-qn*u(n-2))/(qn*y2(n-2)+1.0);

    for (int k=n-2; k>-1; k--){
      y2(k) = y2(k)*y2(k+1) + u(k);
    };

  };

  void UVInterpolWave::mysplint(blitz::Array<double,1> &xa, blitz::Array<dcomplex,1> &ya, blitz::Array<dcomplex,1> &y2a, int &n, double &x, dcomplex &y)
  // My version of splint from the Numerical Recipes (Sec. 3.3)
  {
    int klo, khi, k;
    double h, a, b;

    klo = 0;
    khi = n-1;

    while (khi-klo > 1){
      k = (khi+klo)/2;
      if (xa(k) > x) khi = k;
      else klo = k;
    };

    h=xa(khi)-xa(klo);
    FailWhen(h==0.0,"Bad xa input to routine UVInterpol::mysplint");
    a = (xa(khi)-x)/h;
    b = (x-xa(klo))/h;

    y=a*ya(klo) + b*ya(khi) + ((a*a*a-a)*y2a(klo) + (b*b*b-b)*y2a(khi))/(h*h)/6.0;
  };

  //---------------------------------------------------------------------------

  void UVInterpolWave::mypolin2(blitz::Array<double,1> &x1a, blitz::Array<double,1> &x2a, blitz::Array<dcomplex,2> &ya, int m, int n, double &x1, double &x2, dcomplex &y, dcomplex &dy)
  // My version of polin2 from the Numerical Recipes (Sec. 3.6)
  {
    blitz::Array<double,1> ymtmp(m),yatmp(n);
    double ytmp, dytmp;

    for (int j=0; j<m; j++){
      for (int i=0; i<n; i++){
       	yatmp(i) = creal(ya(j,i));
      };
      ytmp=0.0;
      dytmp=0.0;
      UVInterpolWave::mypolint(x2a,yatmp,n,x2,ytmp,dytmp);
      ymtmp(j)=ytmp;
    };
    ytmp=0.0;
    dytmp=0.0;
    UVInterpolWave::mypolint(x1a,ymtmp,m,x1,ytmp,dytmp);

    y = make_dcomplex(ytmp);
    dy = make_dcomplex(dytmp);

    for (int j=0; j<m; j++){
      for (int i=0; i<n; i++){
       	yatmp(i) = cimag(ya(j,i));
      };
      ytmp=0.0;
      dytmp=0.0;
      UVInterpolWave::mypolint(x2a,yatmp,n,x2,ytmp,dytmp);
      ymtmp(j)=ytmp;
    };
    ytmp=0.0;
    dytmp=0.0;
    UVInterpolWave::mypolint(x1a,ymtmp,m,x1,ytmp,dytmp);

    y = y + make_dcomplex(0.0,ytmp);
    dy = dy + make_dcomplex(0.0,dytmp);

  };

  void UVInterpolWave::mypolint(blitz::Array<double,1> &xa, blitz::Array<double,1> &ya, int n, double &x, double &y, double &dy)
  // My version of polint from the Numerical Recipes (Sec. 3.2)
  {
    int ns=1;
    double dif, dift, ho, hp, den;
    blitz::Array<double,1> c(n), d(n);
    double w;

    dif = fabs(x-xa(0));
    for (int i=1; i<=n; i++){
      dift = fabs(x-xa(i-1));
      if (dift < dif){
	ns = i;
	dif = dift;
      };
      c(i-1) = ya(i-1);
      d(i-1) = ya(i-1);
    };
    y=ya(ns-1);
    ns=ns-1;
    for (int m=1; m<=n-1; m++){
      for (int i=1; i<=n-m; i++){
	ho = xa(i-1)-x;
	hp = xa(i+m-1)-x;
	w=c(i)-d(i-1);
	den = ho-hp;
	FailWhen(den==0.0,"Error in routine UVInterpol::mypolint");
	den = w/den;
	d(i-1) = hp*den;
	c(i-1) = ho*den;
      };
      if (2*ns < n-m) {
	dy = c(ns);
      } else {
	dy = d(ns-1);
	ns = ns-1;
      };
      y = y + dy;
    };

  };

  dcomplex UVInterpolWave::scheme1(double s, double t, dcomplex fiaja, dcomplex fiajb, dcomplex fibjb, dcomplex fibja, dcomplex fuiaja, dcomplex fuiajb, dcomplex fuibjb, dcomplex fuibja, dcomplex fviaja, dcomplex fviajb, dcomplex fvibjb, dcomplex fvibja, dcomplex fuviaja, dcomplex fuviajb, dcomplex fuvibjb, dcomplex fuvibja)
  {
    dcomplex value = (1-t)*(1-s)*fiaja + s*(1-t)*fibja 
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

    return value;
  };

  dcomplex UVInterpolWave::scheme3(double s, double t, dcomplex fiaja, dcomplex fiajb, dcomplex fibjb, dcomplex fibja )
  {
    dcomplex value = (1-t)*(1-s)*fiaja 
      + s*(1-t)*fibja 
      + t*(1-s)*fiajb
      + t*s*fibjb;
    
    return value;
  };

  //------------------------------------------------------------------------

  void UVInterpolWave::fill1Vells(Vells &vellsin, Vells &vellsin1, Vells &vellsin2, Vells &vellsin3, Vells &vellsout, const Result::Ref &uvpoints, const Cells &tfcells, const Cells &brickcells) 
  {
    // Definition of constants
    const double c0 = casa::C::c;  // Speed of light

    // If method has incorrect value, use default method
    if ((_method < 1) || (_method > 3)) _method = 1;

    // Time-Freq boundaries of Result to be produced
    int nt = tfcells.ncells(Axis::TIME);
    int nf = tfcells.ncells(Axis::FREQ);
    const LoVec_double freq = tfcells.center(Axis::FREQ); 
    const LoVec_double time = tfcells.center(Axis::TIME);
    
    int nfbrick = brickcells.ncells(Axis::FREQ);

    // u, v values from UVW-Node
    VellSet uvs = uvpoints->vellSet(0);
    VellSet vvs = uvpoints->vellSet(1);
    Vells uvells = uvs.getValue();
    Vells vvells = vvs.getValue();

    VellsSlicer<double,1> utime_slicer(uvells,_in2axis0);
    VellsSlicer<double,1> vtime_slicer(vvells,_in2axis0);
    blitz::Array<double,1> uarr = utime_slicer();
    blitz::Array<double,1> varr = vtime_slicer();

    // uv grid from UVBrick
    int nu = brickcells.ncells(Axis::axis("U"));
    int nv = brickcells.ncells(Axis::axis("V"));
    const LoVec_double uu = brickcells.center(Axis::axis("U"));
    const LoVec_double vv = brickcells.center(Axis::axis("V"));    
    
    // uv-data from UVBrick
    // UVImage data
    
    VellsSlicer<dcomplex,3> in_slicer(vellsin,_in1axis0,_in1axis1,_in1axis2);
    blitz::Array<dcomplex,3> farr = in_slicer();

    // Output
    // Make an array, connected to the Vells, with which we fill the Vells.
    VellsSlicer<dcomplex,2> out_slicer(vellsout,_out1axis0,_out1axis1);
    blitz::Array<dcomplex,2> arrout = out_slicer();
    arrout = make_dcomplex(0.0);

    double uc,vc;
    int    ia,ib,ja,jb;
    double t,s;

    // Method 2
    dcomplex value, dvalue;
    blitz::Array<double,1> x1(4), x2(4);
    blitz::Array<dcomplex,2> yin(4,4);

    // Think about order of time and frequency.
    // Can the grid search for the next (i,j) tile be optimised 
    //   by using the previous one as starting position?

    // For all methods: the grid search can still be optimised

    if (_method == 1) {

      // Additional input data Vells

      VellsSlicer<dcomplex,3> uin_slicer(vellsin1,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuarr = uin_slicer();
      
      VellsSlicer<dcomplex,3> vin_slicer(vellsin2,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fvarr = vin_slicer();
      
      VellsSlicer<dcomplex,3> uvin_slicer(vellsin3,_in1axis0,_in1axis1,_in1axis2);
      blitz::Array<dcomplex,3> fuvarr = uvin_slicer();
      
      if (nfbrick==1){
	// return request frequency grid
	for (int j = 0; j < nf; j++){

	  for (int i = 0; i < nt; i++){
	
	    // Determine the uv-coordinates
      
	    uc = uarr(i)*freq(j)/c0;
	    vc = varr(i)*freq(j)/c0;
	    
	    // Bi-Cubic Hermite Interpolation, where the derivatives are
	    //  approximated by central finite differences (already 
	    //  determined in the UVBrick node).
	    
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
	    
	    arrout(i,j) = scheme1(s,t,
				 farr(0,ia,ja), farr(0,ia,jb), farr(0,ib,jb), farr(0,ib,ja),
				 fuarr(0,ia,ja), fuarr(0,ia,jb), fuarr(0,ib,jb), fuarr(0,ib,ja),
				 fvarr(0,ia,ja), fvarr(0,ia,jb), fvarr(0,ib,jb), fvarr(0,ib,ja),
				 fuvarr(0,ia,ja), fuvarr(0,ia,jb), fuvarr(0,ib,jb), fuvarr(0,ib,ja));
	    
	  }; // i
	}; // j


      } else {
	// nfbrick >   1
	// return brick frequency grid
	for (int j = 0; j < nf; j++){

	  for (int i = 0; i < nt; i++){
	
	    // Determine the uv-coordinates
      
	    uc = uarr(i)*freq(j)/c0;
	    vc = varr(i)*freq(j)/c0;
	    
	    // Bi-Cubic Hermite Interpolation, where the derivatives are
	    //  approximated by central finite differences (already 
	    //  determined in the UVBrick node).
	    
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
	    
	    arrout(i,j) = scheme1(s,t,
				 farr(j,ia,ja), farr(j,ia,jb), farr(j,ib,jb), farr(j,ib,ja),
				 fuarr(j,ia,ja), fuarr(j,ia,jb), fuarr(j,ib,jb), fuarr(j,ib,ja),
				 fvarr(j,ia,ja), fvarr(j,ia,jb), fvarr(j,ib,jb), fvarr(j,ib,ja),
				  fuvarr(j,ia,ja), fuvarr(j,ia,jb), fuvarr(j,ib,jb), fuvarr(j,ib,ja));

	  }; // i
	}; // j
	
      }; // nfbrick = 1 vs. >1

    } else {
      if (_method == 2) {

	if (nfbrick == 1) {

	  for (int j = 0; j < nf; j++){ 

	    for (int i = 0; i < nt; i++){
	
	      // Determine the uv-coordinates
      
	      uc = uarr(i)*freq(j)/c0;
	      vc = varr(i)*freq(j)/c0;
	    
	      // 4th order polynomial interpolation
	      // Numerical Recipes, Sec. 3.6
	    
	      ia = 0;
	      ib = nu-1;
	      ja = 0;
	      jb = nv-1;
	    
	      for (int i1 = 0; i1 < nu-1; i1++){
		if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1-1; ib = i1+2;};
	      };
	      for (int j1 = 0; j1 < nv-1; j1++){
		if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1-1; jb = j1+2;};
	      };
	      
	      for (int i1 =0; i1<4; i1++){
		x1(i1) = uu(ia+i1);
		for (int j1=0; j1<4; j1++){
		  x2(j1) = vv(ja+j1);
		  yin(i1,j1) = farr(0,ia+i1, ja+j1);	  
		};
	      };
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yin,4,4,uc,vc,value, dvalue);
	      arrout(i,j) = value;

	    }; // i
	  }; // j

	} else {
	  // nfbrick > 1
	  for (int j = 0; j < nf; j++){ 

	    for (int i = 0; i < nt; i++){
	
	      // Determine the uv-coordinates
      
	      uc = uarr(i)*freq(j)/c0;
	      vc = varr(i)*freq(j)/c0;
	    
	      // 4th order polynomial interpolation
	      // Numerical Recipes, Sec. 3.6
	    
	      ia = 0;
	      ib = nu-1;
	      ja = 0;
	      jb = nv-1;
	    
	      for (int i1 = 0; i1 < nu-1; i1++){
		if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1-1; ib = i1+2;};
	      };
	      for (int j1 = 0; j1 < nv-1; j1++){
		if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1-1; jb = j1+2;};
	      };
	      
	      for (int i1 =0; i1<4; i1++){
		x1(i1) = uu(ia+i1);
		for (int j1=0; j1<4; j1++){
		  x2(j1) = vv(ja+j1);
		  yin(i1,j1) = farr(j,ia+i1, ja+j1);
		};
	      };
	      
	      value = make_dcomplex(0.0);
	      dvalue = make_dcomplex(0.0);
	      UVInterpolWave::mypolin2(x1,x2,yin,4,4,uc,vc,value, dvalue);
	      arrout(i,j) = value;

	    }; // i
	  }; // j

	}; // nfbrick =1 vs. >1

      } else {
	if (_method == 3) {
	    
	  if (nfbrick == 1) {
	    for (int j = 0; j < nf; j++){

	      for (int i = 0; i < nt; i++){
	
		// Determine the uv-coordinates
		
		uc = uarr(i)*freq(j)/c0;
		vc = varr(i)*freq(j)/c0;
		
		// Bi-linear interpolation (Num. Rec. Sec. 3.6)
		
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
		
		arrout(i,j) = scheme3(s,t,farr(0,ia,ja),farr(0,ia,jb),farr(0,ib,jb),farr(0,ib,ja));
		
	      }; // i
	    }; // j


	  } else {
	    // nfbrick > 1
	    for (int j = 0; j < nf; j++){

	      for (int i = 0; i < nt; i++){
	
		// Determine the uv-coordinates
		
		uc = uarr(i)*freq(j)/c0;
		vc = varr(i)*freq(j)/c0;
		
		// Bi-linear interpolation (Num. Rec. Sec. 3.6)
		
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
		
		arrout(i,j) = scheme3(s,t,farr(j,ia,ja),farr(j,ia,jb),farr(j,ib,jb),farr(j,ib,ja));
		
	      }; // i
	    }; // j

	  }; // if nfbrick = 1 vs. >1

	}; // if method = 3
      }; // else
    }; // if method=1  else
      
  }; // fill1Vells


} // namespace Meq

//# UVInterpol.cc: Stored parameter with polynomial coefficients
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

#include <MeqNodes/UVInterpol.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/aips.h>
#include <casa/BasicSL/Constants.h>
#include <casa/BasicMath/Math.h>


namespace Meq {

  static const HIID child_labels[] = { AidUVBRICK, AidUVW };
  static const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);
  
#define VERBOSE

  UVInterpol::UVInterpol():
    _additional_info(false),
    _uvZ(0.0),
    _uvDelta(casa::C::pi/2.),
    _method(1),
    Node(num_children,child_labels)
  {
    disableAutoResample();
  };
  
  UVInterpol::~UVInterpol()
  {
  };

  void UVInterpol::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
    rec["Additional.Info"].get(_additional_info,initializing);
    rec["UVZ"].get(_uvZ,initializing);
    rec["UVDelta"].get(_uvDelta,initializing);
    rec["Method"].get(_method,initializing);
  }
  
  int UVInterpol::getResult (Result::Ref &resref,
			  const std::vector<Result::Ref> &childres,
			  const Request &request,bool newreq)
  {

    // Get the request cells
    const Cells& rcells = request.cells();
    
    if( rcells.isDefined(Axis::TIME) && rcells.isDefined(Axis::FREQ))
      {
	
	// Create the Interpolated UVdata 
	// (Integration is not implemented. This is ok for small 
	//   time/freq cells. For larger Cells a 2D Integration Routine 
	//   (Romberg?) must be implemented). 
	    
	// Create Result object and attach to the Ref that was passed in.
	resref <<= new Result(1);                 // 1 plane
	VellSet& vs0 = resref().setNewVellSet(0);  // create new object for plane 0
	VellSet& vs1 = resref().setNewVellSet(1);  // create new object for plane 0
	VellSet& vs2 = resref().setNewVellSet(2);  // create new object for plane 0
	VellSet& vs3 = resref().setNewVellSet(3);  // create new object for plane 0

	//
	// Make the Result
	//		
	    
	// Make the Vells (Interpolation)
	Vells::Shape tfshape;
	Axis::degenerateShape(tfshape,rcells.rank());
	int nt = tfshape[Axis::TIME] = rcells.ncells(Axis::TIME);
	int nf = tfshape[Axis::FREQ] = rcells.ncells(Axis::FREQ);
	    
	// Make a new Vells and fill with zeros
	Vells & vells0 = vs0.setValue(new Vells(dcomplex(0),tfshape,true));
	Vells & vells1 = vs1.setValue(new Vells(dcomplex(0),tfshape,true));
	Vells & vells2 = vs2.setValue(new Vells(dcomplex(0),tfshape,true));
	Vells & vells3 = vs3.setValue(new Vells(dcomplex(0),tfshape,true));
	    
	// Fill the Vells (this is were the interpolation takes place)
	fillVells(childres,vells0,vells1,vells2,vells3,rcells);	
	    
	// Attach the request Cells to the result
	resref().setCells(rcells);
      
	if (_additional_info){
	  
	  // Make Additional Info on UV-plane coverage.
	  
	  // Make the Additional Vells
	  
	  Result& res2 = resref["UVInterpol.Map"] <<= new Result(1); 
	  VellSet& vs2 = res2.setNewVellSet(0); 
	  
	  //
	  // Make the Result
	  //		
	  
	  // Make a uv-shape
	  Result::Ref brickresult;
	  Cells brickcells; 
	  Result::Ref uvpoints;
	  
	  //if ( childres.at(0)->cells().isDefined(Axis::axis("U")) &&
	  //     childres.at(0)->cells().isDefined(Axis::axis("V")) )
	  //  //if ( childres.at(0)->cells().isDefined(Axis::axis("L")) &&
	  //  //   childres.at(0)->cells().isDefined(Axis::axis("M")) )
	  //  {
	      brickresult = childres.at(0);
	      brickcells = brickresult->cells();
	      uvpoints = childres.at(1);
	      //  } 
	      //else 
	      //  {
	      //    brickresult = childres.at(1);
	      //    brickcells = brickresult->cells();
	      //     uvpoints = childres.at(0);
	      //  };
	  
	  // uv grid from UVBrick
	  int nu = brickcells.ncells(Axis::axis("U"));
	  int nv = brickcells.ncells(Axis::axis("V"));
	  const LoVec_double uu = brickcells.center(Axis::axis("U"));
	  const LoVec_double vv = brickcells.center(Axis::axis("V"));
	  //int nu = brickcells.ncells(Axis::axis("L"));
	  //int nv = brickcells.ncells(Axis::axis("M"));
	  //const LoVec_double uu = brickcells.center(Axis::axis("L"));
	  //const LoVec_double vv = brickcells.center(Axis::axis("M"));
	  
	  // uv image domain
	  Domain::Ref uvdomain(new Domain());
	  uvdomain().defineAxis(Axis::axis("U"),uu(0),uu(nu-1));
	  uvdomain().defineAxis(Axis::axis("V"),vv(0),vv(nv-1));
	  Cells::Ref uvcells(new Cells(*uvdomain));
	  uvcells().setCells(Axis::axis("U"),uu(0),uu(nu-1),nu);
	  uvcells().setCells(Axis::axis("V"),vv(0),vv(nv-1),nv);    
	  
	  Vells::Shape uvshape;
	  Axis::degenerateShape(uvshape,uvcells->rank());
	  uvshape[Axis::axis("U")] = brickcells.ncells(Axis::axis("U"));
	  uvshape[Axis::axis("V")] = brickcells.ncells(Axis::axis("V"));
	  //uvshape[Axis::axis("TIME")] = brickcells.ncells(Axis::axis("L"));
	  //uvshape[Axis::axis("FREQ")] = brickcells.ncells(Axis::axis("M"));
	  
	  // Make the new Vells

	  Vells& vells2 = vs2.setValue(new Vells(double(0),uvshape,false));
	  
	  // Fill the Vells 

	  // Determine the mapping onto the uv plane of the time-freq. cell

	  LoMat_double arr2 = vells2.as<double,2>();
	  arr2 = 0.0;

	  // u,v values from UVW-Node
	  VellSet uvs = uvpoints->vellSet(0);
	  VellSet vvs = uvpoints->vellSet(1);
	  Vells uvells = uvs.getValue();
	  Vells vvells = vvs.getValue();
	  int vellsrank = uvs.shape().size();

#ifdef VERBOSE
	  cout << uvs.shape() << uvs.shape().size() << endl;
#endif

	  if (vellsrank==2) {

	    blitz::Array<double,2> uarr = uvells.as<double,2>()(LoRange::all(),LoRange::all());
	    blitz::Array<double,2> varr = vvells.as<double,2>()(LoRange::all(),LoRange::all());

	    int imin, jmin;

	    for (int i = 0; i < nt; i++){
        
	      imin = 0;
	      jmin = 0;
	   
	      
	      for (int i1 = 0; i1 < nu-1; i1++){
		if ((uu(i1)<=uarr(0,i)) && (uu(i1+1)>uarr(0,i))) {imin = i1;};
	      };
	      for (int j1 = 0; j1 < nv-1; j1++){
		if ((vv(j1)<=varr(0,i)) && (vv(j1+1)>varr(0,i))) {jmin = j1;};
	      };
	      
	      arr2(imin,jmin) = 1.0;
	      
	    }; // i
	  
	  }

	  if (vellsrank==1) {

	    blitz::Array<double,1> uarr = uvells.as<double,1>()(LoRange::all());
	    blitz::Array<double,1> varr = vvells.as<double,1>()(LoRange::all());

	    int imin, jmin;

	    for (int i = 0; i < nt; i++){
        
	      imin = 0;
	      jmin = 0;
	   
	      
	      for (int i1 = 0; i1 < nu-1; i1++){
	    	if ((uu(i1)<=uarr(i)) && (uu(i1+1)>uarr(i))) {imin = i1;};
	      };
	      for (int j1 = 0; j1 < nv-1; j1++){
	    	if ((vv(j1)<=varr(i)) && (vv(j1+1)>varr(i))) {jmin = j1;};
	      };
	      
	     arr2(imin,jmin) = 1.0;
	      
	    }; // i
	  
	  }
	  
	  // Attach a Cells to the result
	  res2.setCells(*uvcells);
	  

	};
	
      }; 
    
    return 0;
    
  };

  void UVInterpol::fillVells(const std::vector<Result::Ref> &fchildres, 
			     Vells &fvells0, Vells &fvells1, Vells &fvells2, Vells &fvells3, const Cells &fcells)
  {
    // Definition of constants
    const double c0 = casa::C::c;  // Speed of light

    // If method has incorrect value, use default method
    if ((_method < 1) || (_method > 4)) _method = 1;

    // Time-Freq boundaries of Request
    int nt = fcells.ncells(Axis::TIME);
    int nf = fcells.ncells(Axis::FREQ);
    const LoVec_double freq = fcells.center(Axis::FREQ); 
    const LoVec_double time = fcells.center(Axis::TIME); 

    // Get the Child Results: brickresult, brickcells for UVBrick-Node
    //                        uvpoints for UVW-Node
    Result::Ref brickresult;
    Cells brickcells; 
    Result::Ref uvpoints;

    //if ( fchildres.at(0)->cells().isDefined(Axis::axis("U")) &&
    //	 fchildres.at(0)->cells().isDefined(Axis::axis("V")) )
    //	  //if ( fchildres.at(0)->cells().isDefined(Axis::axis("L")) &&
    //	  //fchildres.at(0)->cells().isDefined(Axis::axis("M")) )
    //  {
	brickresult = fchildres.at(0);
	brickcells = brickresult->cells();
	uvpoints = fchildres.at(1);
	//  } 
	//else 
	//  {
	//	brickresult = fchildres.at(1);
	//	brickcells = brickresult->cells();
	//	uvpoints = fchildres.at(0);
	// };

    // u, v values from UVW-Node
    VellSet uvs = uvpoints->vellSet(0);
    VellSet vvs = uvpoints->vellSet(1);
    Vells uvells = uvs.getValue();
    Vells vvells = vvs.getValue();

    int vellsrank = uvs.shape().size();
    blitz::Array<double,1> uarr1(nt);
    blitz::Array<double,1> varr1(nt);

    if (vellsrank==2){
      blitz::Array<double,2> uarr = uvells.as<double,2>()(LoRange::all(),LoRange::all());
      blitz::Array<double,2> varr = vvells.as<double,2>()(LoRange::all(),LoRange::all());
      for (int i = 0; i < nt; i++){      
	uarr1(i) = uarr(i,0);
	varr1(i) = varr(i,0);
      }
    }
    if (vellsrank==1){
      blitz::Array<double,1> uarr = uvells.as<double,1>()(LoRange::all());
      blitz::Array<double,1> varr = vvells.as<double,1>()(LoRange::all());
      for (int i = 0; i < nt; i++){
      	uarr1(i) = uarr(i);
      	varr1(i) = varr(i);
      }
    }


    // uv grid from UVBrick
    int nu = brickcells.ncells(Axis::axis("U"));
    int nv = brickcells.ncells(Axis::axis("V"));
    const LoVec_double uu = brickcells.center(Axis::axis("U"));
    const LoVec_double vv = brickcells.center(Axis::axis("V"));
    //int nu = brickcells.ncells(Axis::axis("L"));
    //int nv = brickcells.ncells(Axis::axis("M"));
    //const LoVec_double uu = brickcells.center(Axis::axis("L"));
    //const LoVec_double vv = brickcells.center(Axis::axis("M"));
    
    // uv-data from UVBrick
    // UVImage data
    VellSet vsf = brickresult->vellSet(0);
    Vells vellsfI = vsf.getValue(); 
    VellSet vsfQ = brickresult->vellSet(4);
    Vells vellsfQ = vsfQ.getValue(); 
    VellSet vsfU = brickresult->vellSet(8);
    Vells vellsfU = vsfU.getValue(); 
    VellSet vsfV = brickresult->vellSet(12);
    Vells vellsfV = vsfV.getValue(); 
    //Vells vellsfQ = brickresult->vellSet(4).getValue();
    //Vells vellsfU = brickresult->vellSet(8).getValue();
    //Vells vellsfV = brickresult->vellSet(12).getValue();
    blitz::Array<dcomplex,3> farrI = vellsfI.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
    blitz::Array<dcomplex,3> farrQ = vellsfQ.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
    blitz::Array<dcomplex,3> farrU = vellsfU.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());
    blitz::Array<dcomplex,3> farrV = vellsfV.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

    // Method 1
    blitz::Array<dcomplex,3> fuarrI(nf,nu,nv);
    blitz::Array<dcomplex,3> fvarrI(nf,nu,nv);
    blitz::Array<dcomplex,3> fuvarrI(nf,nu,nv);
    blitz::Array<dcomplex,3> fuarrQ(nf,nu,nv);
    blitz::Array<dcomplex,3> fvarrQ(nf,nu,nv);
    blitz::Array<dcomplex,3> fuvarrQ(nf,nu,nv);
    blitz::Array<dcomplex,3> fuarrU(nf,nu,nv);
    blitz::Array<dcomplex,3> fvarrU(nf,nu,nv);
    blitz::Array<dcomplex,3> fuvarrU(nf,nu,nv);
    blitz::Array<dcomplex,3> fuarrV(nf,nu,nv);
    blitz::Array<dcomplex,3> fvarrV(nf,nu,nv);
    blitz::Array<dcomplex,3> fuvarrV(nf,nu,nv);

    if (_method == 1){
      // Additional data Vells

      VellSet vsfuI = brickresult->vellSet(1);
      Vells fuvellsI = vsfuI.getValue(); 
      fuarrI = fuvellsI.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfvI = brickresult->vellSet(2);
      Vells fvvellsI = vsfvI.getValue(); 
      fvarrI = fvvellsI.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfuvI = brickresult->vellSet(3);
      Vells fuvvellsI = vsfuvI.getValue(); 
      fuvarrI = fuvvellsI.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfuQ = brickresult->vellSet(5);
      Vells fuvellsQ = vsfuQ.getValue(); 
      fuarrQ = fuvellsQ.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfvQ = brickresult->vellSet(6);
      Vells fvvellsQ = vsfvQ.getValue(); 
      fvarrQ = fvvellsQ.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfuvQ = brickresult->vellSet(7);
      Vells fuvvellsQ = vsfuvQ.getValue(); 
      fuvarrQ = fuvvellsQ.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfuU = brickresult->vellSet(9);
      Vells fuvellsU = vsfuU.getValue(); 
      fuarrU = fuvellsU.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfvU = brickresult->vellSet(10);
      Vells fvvellsU = vsfvU.getValue(); 
      fvarrU = fvvellsU.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfuvU = brickresult->vellSet(11);
      Vells fuvvellsU = vsfuvU.getValue(); 
      fuvarrU = fuvvellsU.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfuV = brickresult->vellSet(13);
      Vells fuvellsV = vsfuV.getValue(); 
      fuarrV = fuvellsV.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfvV = brickresult->vellSet(14);
      Vells fvvellsV = vsfvV.getValue(); 
      fvarrV = fvvellsV.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

      VellSet vsfuvV = brickresult->vellSet(15);
      Vells fuvvellsV = vsfuvV.getValue(); 
      fuvarrV = fuvvellsV.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

    };

    // Make an array, connected to the Vells, with which we fill the Vells.
    LoMat_dcomplex arrI = fvells0.as<dcomplex,2>();
    LoMat_dcomplex arrQ = fvells1.as<dcomplex,2>();
    LoMat_dcomplex arrU = fvells2.as<dcomplex,2>();
    LoMat_dcomplex arrV = fvells3.as<dcomplex,2>();
    arrI = dcomplex(0.0);
    arrQ = dcomplex(0.0);
    arrU = dcomplex(0.0);
    arrV = dcomplex(0.0);

    double uc,vc;
    int    ia,ib,ja,jb;
    double t,s;

    // Method 3
    dcomplex value, dvalue;
    blitz::Array<double,1> x1(4), x2(4);
    blitz::Array<dcomplex,2> yI(4,4),yQ(4,4),yU(4,4),yV(4,4);

    // Think about order of time and frequency.
    // Can the grid search for the next (i,j) tile be optimised 
    //   by using the previous one as starting position?

    for (int i = 0; i < nt; i++){
	
      // Determine the uv-coordinates
      
      uc = uarr1(i);
      vc = varr1(i);


      // For all methods: the grid search can still be optimised

      if (_method == 1) {
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
	
	for (int j = 0; j < nf; j++){

	  arrI(i,j) = (1-t)*(1-s)*farrI(j,ia,ja) 
	    + s*(1-t)*farrI(j,ib,ja) 
	    + (1-s)*t*farrI(j,ia,jb)
	    + t*s*farrI(j,ib,jb)
	    + t*s*s*(1-s)*(farrI(j,ib,jb)-fuarrI(j,ib,jb))
	    + t*s*(1-s)*(1-s)*(farrI(j,ia,jb)-fuarrI(j,ia,jb))
	    + (1-t)*s*s*(1-s)*(farrI(j,ib,ja)-fuarrI(j,ib,ja))
	    + (1-t)*s*(1-s)*(1-s)*(farrI(j,ia,ja)-fuarrI(j,ia,ja))
	    + t*t*s*(1-t)*(farrI(j,ib,jb)-fvarrI(j,ib,jb))
	    + t*t*(1-t)*(1-s)*(farrI(j,ia,jb)-fvarrI(j,ia,jb))
	    + (1-t)*s*t*(1-t)*(farrI(j,ib,ja)-fvarrI(j,ib,ja))
	    + t*(1-t)*(1-t)*(1-s)*(farrI(j,ia,ja)-fvarrI(j,ia,ja))
	    + t*t*(1-t)*s*s*(1-s)*(farrI(j,ib,jb) - fvarrI(j,ib,jb) - fuarrI(j,ib,jb) + fuvarrI(j,ib,jb))
	    + t*t*(1-t)*s*(1-s)*(1-s)*(farrI(j,ia,jb) - fvarrI(j,ia,jb) - fuarrI(j,ia,jb) + fuvarrI(j,ia,jb))
	    + t*(1-t)*(1-t)*s*s*(1-s)*(farrI(j,ib,ja) - fvarrI(j,ib,ja) - fuarrI(j,ib,ja) + fuvarrI(j,ib,ja))
	    + t*(1-t)*(1-t)*s*(1-s)*(1-s)*(farrI(j,ia,ja) - fvarrI(j,ia,ja) - fuarrI(j,ia,ja) + fuvarrI(j,ia,ja));

	  arrQ(i,j) = (1-t)*(1-s)*farrQ(j,ia,ja) 
	    + s*(1-t)*farrQ(j,ib,ja) 
	    + (1-s)*t*farrQ(j,ia,jb)
	    + t*s*farrQ(j,ib,jb)
	    + t*s*s*(1-s)*(farrQ(j,ib,jb)-fuarrQ(j,ib,jb))
	    + t*s*(1-s)*(1-s)*(farrQ(j,ia,jb)-fuarrQ(j,ia,jb))
	    + (1-t)*s*s*(1-s)*(farrQ(j,ib,ja)-fuarrQ(j,ib,ja))
	    + (1-t)*s*(1-s)*(1-s)*(farrQ(j,ia,ja)-fuarrQ(j,ia,ja))
	    + t*t*s*(1-t)*(farrQ(j,ib,jb)-fvarrQ(j,ib,jb))
	    + t*t*(1-t)*(1-s)*(farrQ(j,ia,jb)-fvarrQ(j,ia,jb))
	    + (1-t)*s*t*(1-t)*(farrQ(j,ib,ja)-fvarrQ(j,ib,ja))
	    + t*(1-t)*(1-t)*(1-s)*(farrQ(j,ia,ja)-fvarrQ(j,ia,ja))
	    + t*t*(1-t)*s*s*(1-s)*(farrQ(j,ib,jb) - fvarrQ(j,ib,jb) - fuarrQ(j,ib,jb) + fuvarrQ(j,ib,jb))
	    + t*t*(1-t)*s*(1-s)*(1-s)*(farrQ(j,ia,jb) - fvarrQ(j,ia,jb) - fuarrQ(j,ia,jb) + fuvarrQ(j,ia,jb))
	    + t*(1-t)*(1-t)*s*s*(1-s)*(farrQ(j,ib,ja) - fvarrQ(j,ib,ja) - fuarrQ(j,ib,ja) + fuvarrQ(j,ib,ja))
	    + t*(1-t)*(1-t)*s*(1-s)*(1-s)*(farrQ(j,ia,ja) - fvarrQ(j,ia,ja) - fuarrQ(j,ia,ja) + fuvarrQ(j,ia,ja));

	  arrU(i,j) = (1-t)*(1-s)*farrU(j,ia,ja) 
	    + s*(1-t)*farrU(j,ib,ja) 
	    + (1-s)*t*farrU(j,ia,jb)
	    + t*s*farrU(j,ib,jb)
	    + t*s*s*(1-s)*(farrU(j,ib,jb)-fuarrU(j,ib,jb))
	    + t*s*(1-s)*(1-s)*(farrU(j,ia,jb)-fuarrU(j,ia,jb))
	    + (1-t)*s*s*(1-s)*(farrU(j,ib,ja)-fuarrU(j,ib,ja))
	    + (1-t)*s*(1-s)*(1-s)*(farrU(j,ia,ja)-fuarrU(j,ia,ja))
	    + t*t*s*(1-t)*(farrU(j,ib,jb)-fvarrU(j,ib,jb))
	    + t*t*(1-t)*(1-s)*(farrU(j,ia,jb)-fvarrU(j,ia,jb))
	    + (1-t)*s*t*(1-t)*(farrU(j,ib,ja)-fvarrU(j,ib,ja))
	    + t*(1-t)*(1-t)*(1-s)*(farrU(j,ia,ja)-fvarrU(j,ia,ja))
	    + t*t*(1-t)*s*s*(1-s)*(farrU(j,ib,jb) - fvarrU(j,ib,jb) - fuarrU(j,ib,jb) + fuvarrU(j,ib,jb))
	    + t*t*(1-t)*s*(1-s)*(1-s)*(farrU(j,ia,jb) - fvarrU(j,ia,jb) - fuarrU(j,ia,jb) + fuvarrU(j,ia,jb))
	    + t*(1-t)*(1-t)*s*s*(1-s)*(farrU(j,ib,ja) - fvarrU(j,ib,ja) - fuarrU(j,ib,ja) + fuvarrU(j,ib,ja))
	    + t*(1-t)*(1-t)*s*(1-s)*(1-s)*(farrU(j,ia,ja) - fvarrU(j,ia,ja) - fuarrU(j,ia,ja) + fuvarrU(j,ia,ja));

	  arrV(i,j) = (1-t)*(1-s)*farrV(j,ia,ja) 
	    + s*(1-t)*farrV(j,ib,ja) 
	    + (1-s)*t*farrV(j,ia,jb)
	    + t*s*farrV(j,ib,jb)
	    + t*s*s*(1-s)*(farrV(j,ib,jb)-fuarrV(j,ib,jb))
	    + t*s*(1-s)*(1-s)*(farrV(j,ia,jb)-fuarrV(j,ia,jb))
	    + (1-t)*s*s*(1-s)*(farrV(j,ib,ja)-fuarrV(j,ib,ja))
	    + (1-t)*s*(1-s)*(1-s)*(farrV(j,ia,ja)-fuarrV(j,ia,ja))
	    + t*t*s*(1-t)*(farrV(j,ib,jb)-fvarrV(j,ib,jb))
	    + t*t*(1-t)*(1-s)*(farrV(j,ia,jb)-fvarrV(j,ia,jb))
	    + (1-t)*s*t*(1-t)*(farrV(j,ib,ja)-fvarrV(j,ib,ja))
	    + t*(1-t)*(1-t)*(1-s)*(farrV(j,ia,ja)-fvarrV(j,ia,ja))
	    + t*t*(1-t)*s*s*(1-s)*(farrV(j,ib,jb) - fvarrV(j,ib,jb) - fuarrV(j,ib,jb) + fuvarrV(j,ib,jb))
	    + t*t*(1-t)*s*(1-s)*(1-s)*(farrV(j,ia,jb) - fvarrV(j,ia,jb) - fuarrV(j,ia,jb) + fuvarrV(j,ia,jb))
	    + t*(1-t)*(1-t)*s*s*(1-s)*(farrV(j,ib,ja) - fvarrV(j,ib,ja) - fuarrV(j,ib,ja) + fuvarrV(j,ib,ja))
	    + t*(1-t)*(1-t)*s*(1-s)*(1-s)*(farrV(j,ia,ja) - fvarrV(j,ia,ja) - fuarrV(j,ia,ja) + fuvarrV(j,ia,ja));

	};

      } else {
	if (_method == 2) {

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

	  for (int j = 0; j < nf; j++){ 

	    for (int i1 =0; i1<4; i1++){
	      x1(i1) = uu(ia+i1);
	      for (int j1=0; j1<4; j1++){
		x2(j1) = vv(ja+j1);
		yI(i1,j1) = farrI(j,ia+i1, ja+j1);
		yQ(i1,j1) = farrQ(j,ia+i1, ja+j1);
		yU(i1,j1) = farrU(j,ia+i1, ja+j1);
		yV(i1,j1) = farrV(j,ia+i1, ja+j1);
	      };
	    };
	    
	    value = dcomplex(0.0);
	    dvalue = dcomplex(0.0);
	    UVInterpol::mypolin2(x1,x2,yI,4,4,uc,vc,value, dvalue);
	    arrI(i,j) = value;

	    value = dcomplex(0.0);
	    dvalue = dcomplex(0.0);
	    UVInterpol::mypolin2(x1,x2,yQ,4,4,uc,vc,value, dvalue);
	    arrQ(i,j) = value;

	    value = dcomplex(0.0);
	    dvalue = dcomplex(0.0);
	    UVInterpol::mypolin2(x1,x2,yU,4,4,uc,vc,value, dvalue);
	    arrU(i,j) = value;

	    value = dcomplex(0.0);
	    dvalue = dcomplex(0.0);
	    UVInterpol::mypolin2(x1,x2,yV,4,4,uc,vc,value, dvalue);
	    arrV(i,j) = value;

	  };

	} else {
	  if (_method == 3) {
	    
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
	    
	    for (int j = 0; j < nf; j++){

	      arrI(i,j) = (1-t)*(1-s)*farrI(j,ia,ja) 
		+ s*(1-t)*farrI(j,ib,ja) 
		+ t*(1-s)*farrI(j,ia,jb)
		+ t*s*farrI(j,ib,jb);

	      arrQ(i,j) = (1-t)*(1-s)*farrQ(j,ia,ja) 
		+ s*(1-t)*farrQ(j,ib,ja) 
		+ t*(1-s)*farrQ(j,ia,jb)
		+ t*s*farrQ(j,ib,jb);

	      arrU(i,j) = (1-t)*(1-s)*farrU(j,ia,ja) 
		+ s*(1-t)*farrU(j,ib,ja) 
		+ t*(1-s)*farrU(j,ia,jb)
		+ t*s*farrU(j,ib,jb);

	      arrV(i,j) = (1-t)*(1-s)*farrV(j,ia,ja) 
		+ s*(1-t)*farrV(j,ib,ja) 
		+ t*(1-s)*farrV(j,ia,jb)
		+ t*s*farrV(j,ib,jb);	  
	      
	    };
	  };
	};
      }; // End filling arr(i,j) by one of the 3 Methods
	
    }; // End of time loop
      
      
  };


    

  //--------------------------------------------------------------------------

  void UVInterpol::interpolate(int &j, int &ni,int &imin, int &nj, int &jmin, LoMat_dcomplex &coeff, blitz::Array<dcomplex,3> &barr,LoVec_double uu,LoVec_double vv)
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


  void UVInterpol::myludcmp(blitz::Array<double,2> &A,int n,blitz::Array<int,1> &indx)
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
	FailWhen(big==0.0,"Singular Matrix in UVInterpol::myludcmp");
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


  void UVInterpol::mylubksb(blitz::Array<double,2> &A,int n,blitz::Array<int,1> &indx, blitz::Array<dcomplex,1> &B)
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

  void UVInterpol::mysplie2(blitz::Array<double,1> &x1a, blitz::Array<double,1> &x2a, blitz::Array<dcomplex,2> &ya, int &m, int &n, blitz::Array<dcomplex,2> &y2a)
  // My version of splie2 from the Numerical Recipes (Sec. 3.6)
  {
    blitz::Array<dcomplex,1> ytmp(n), yytmp(n);

    for (int j=0; j<m; j++){
      for (int i=0; i<n; i++){
	ytmp(i) = ya(j,i);
      };
      UVInterpol::myspline(x2a,ytmp,n,1.0e30,1.0e30,yytmp);
      for (int i=0; i<n; i++){
	y2a(j,i) = yytmp(i);
      };
    };

  };

  void UVInterpol::mysplin2(blitz::Array<double,1> &x1a, blitz::Array<double,1> &x2a, blitz::Array<dcomplex,2> &ya, blitz::Array<dcomplex,2> &y2a, int &m, int &n, double &x1, double &x2, dcomplex &y)
  // My version of splin2 from the Numerical Recipes (Sec. 3.6)
  {
    blitz::Array<dcomplex,1> ytmp(n), yytmp(m), y2tmp(n);

    for (int j=0; j<m; j++){
      for (int i=0; i<n; i++){
	ytmp(i) = ya(j,i);
	y2tmp(i) = y2a(j,i);
      };
      UVInterpol::mysplint(x2a,ytmp,y2tmp,n,x2,yytmp(j));
    };
    UVInterpol::myspline(x1a,yytmp,m,1.0e30,1.0e30,y2tmp);
    UVInterpol::mysplint(x1a,yytmp,y2tmp,m,x1,y);

  };

  void UVInterpol::myspline(blitz::Array<double,1> &x, blitz::Array<dcomplex,1> &y,int &n, double yp1, double ypn, blitz::Array<dcomplex,1> &y2)
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

  void UVInterpol::mysplint(blitz::Array<double,1> &xa, blitz::Array<dcomplex,1> &ya, blitz::Array<dcomplex,1> &y2a, int &n, double &x, dcomplex &y)
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

  void UVInterpol::mypolin2(blitz::Array<double,1> &x1a, blitz::Array<double,1> &x2a, blitz::Array<dcomplex,2> &ya, int m, int n, double &x1, double &x2, dcomplex &y, dcomplex &dy)
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
      UVInterpol::mypolint(x2a,yatmp,n,x2,ytmp,dytmp);
      ymtmp(j)=ytmp;
    };
    ytmp=0.0;
    dytmp=0.0;
    UVInterpol::mypolint(x1a,ymtmp,m,x1,ytmp,dytmp);

    y = dcomplex(ytmp);
    dy = dcomplex(dytmp);

    for (int j=0; j<m; j++){
      for (int i=0; i<n; i++){
       	yatmp(i) = cimag(ya(j,i));
      };
      ytmp=0.0;
      dytmp=0.0;
      UVInterpol::mypolint(x2a,yatmp,n,x2,ytmp,dytmp);
      ymtmp(j)=ytmp;
    };
    ytmp=0.0;
    dytmp=0.0;
    UVInterpol::mypolint(x1a,ymtmp,m,x1,ytmp,dytmp);

    y = y + make_dcomplex(0.0,ytmp);
    dy = dy + make_dcomplex(0.0,dytmp);

  };

  void UVInterpol::mypolint(blitz::Array<double,1> &xa, blitz::Array<double,1> &ya, int n, double &x, double &y, double &dy)
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


} // namespace Meq

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
#include <casa/aips.h>
#include <casa/BasicSL/Constants.h>
#include <casa/BasicMath/Math.h>


namespace Meq {
  
  UVInterpol::UVInterpol()
  {
    Axis::addAxis("U");
    Axis::addAxis("V");
  };
  
  UVInterpol::~UVInterpol()
  {
  };
  
  int UVInterpol::getResult (Result::Ref &resref,
			  const std::vector<Result::Ref> &childres,
			  const Request &request,bool newreq)
  {

    // Get the request cells
    const Cells& rcells = request.cells();
    
    if( rcells.isDefined(Axis::TIME) && rcells.isDefined(Axis::FREQ))
      {
    
	// Create Result object and attach to the Ref that was passed in.
	resref <<= new Result(1);                 // 1 plane
	VellSet& vs = resref().setNewVellSet(0);  // create new object for plane 0

	//
	// Make the Result
	//		

	// Make the Vells (Interpolation)
	Vells::Shape shape;
	Axis::degenerateShape(shape,rcells.rank());
	shape[Axis::TIME] = rcells.ncells(Axis::TIME);
	shape[Axis::FREQ] = rcells.ncells(Axis::FREQ);

	// Make a new Vells
	Vells & vells = vs.setValue(new Vells(dcomplex(0),shape,false));
	
	// Fill the Vells (this is were the interpolation takes place)
	 fillVells(childres,vells,rcells);	
	
	// Attach the request Cells to the result
	 resref().setCells(rcells);

	

	// Make the Vells (Show Cell mapping)

	 Result& res2 = resref["UVInterpol.Map"] <<= new Result(1);                 // 1 plane
	 VellSet& vs2 = res2.setNewVellSet(0);  // create new object for plane 0

	// Get the Child Results: brickresult, brickcells for UVBrick-Node
	//                        uvpoints for UVW-Node
	Result::Ref brickresult;
	Cells brickcells; 

	if ( childres.at(0)->cells().isDefined(Axis::axis("U")) &&
	     childres.at(0)->cells().isDefined(Axis::axis("V")) )
	  {
	    brickresult = childres.at(0);
	    brickcells = brickresult->cells();
	  } 
	else 
	  {
	    brickresult = childres.at(1);
	    brickcells = brickresult->cells();
	  };

	// uv grid from UVBrick
	int nu = brickcells.ncells(Axis::axis("U"));
	int nv = brickcells.ncells(Axis::axis("V"));
	const LoVec_double uu = brickcells.center(Axis::axis("U"));
	const LoVec_double vv = brickcells.center(Axis::axis("V"));

	Domain::Ref newdomain(new Domain());
	newdomain().defineAxis(2,uu(0),uu(nu-1));
	newdomain().defineAxis(3,vv(0),vv(nv-1));
	Cells::Ref newcells(new Cells(*newdomain));
	newcells().setCells(2,uu(0),uu(nu-1),nu);
	newcells().setCells(3,vv(0),vv(nv-1),nv);

	Vells::Shape shape2;
	Axis::degenerateShape(shape2,newcells->rank());
	shape2[Axis::axis("U")] = brickcells.ncells(Axis::axis("U"));
	shape2[Axis::axis("V")] = brickcells.ncells(Axis::axis("V"));

	// Make a new Vells
	Vells & vells2 = vs2.setValue(new Vells(double(0),shape2,false));
	
	// Fill the Vells (this is were the interpolation takes place)
	fillVells2(childres,vells2,rcells);	
	
	// Attach the request Cells to the result
	res2.setCells(*newcells);
	
      }; 
    
    return 0;
    
  };
  
  void UVInterpol::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
  }

  void UVInterpol::fillVells(const std::vector<Result::Ref> &fchildres, 
			     Vells &fvells, const Cells &fcells)
  {
    // Definition of constants
    const double c0 = casa::C::c;  // Speed of light
    const double pi = casa::C::pi; // Pi = 3.1415....

    // Time-Freq boundaries of Request
    int nt = fcells.ncells(Axis::TIME);
    int nf = fcells.ncells(Axis::FREQ);
    const LoVec_double freq = fcells.center(Axis::FREQ); 
    const LoVec_double lofr = fcells.cellStart(Axis::FREQ); 
    const LoVec_double hifr = fcells.cellEnd(Axis::FREQ);
 
    const LoVec_double time = fcells.center(Axis::TIME); 
    const LoVec_double loti = fcells.cellStart(Axis::TIME); 
    const LoVec_double hiti = fcells.cellEnd(Axis::TIME); 

    // Get the Child Results: brickresult, brickcells for UVBrick-Node
    //                        uvpoints for UVW-Node
    Result::Ref brickresult;
    Cells brickcells; 
    Result::Ref uvpoints;

    if ( fchildres.at(0)->cells().isDefined(Axis::axis("U")) &&
	 fchildres.at(0)->cells().isDefined(Axis::axis("V")) )
      {
	brickresult = fchildres.at(0);
	brickcells = brickresult->cells();
	uvpoints = fchildres.at(1);
      } 
    else 
      {
	brickresult = fchildres.at(1);
	brickcells = brickresult->cells();
	uvpoints = fchildres.at(0);
      };

    // u, v values from UVW-Node
    VellSet uvs = uvpoints->vellSet(0);
    VellSet vvs = uvpoints->vellSet(1);
    Vells uvells = uvs.getValue();
    Vells vvells = vvs.getValue();

    blitz::Array<double,2> uarr = uvells.as<double,2>()(LoRange::all(),LoRange::all());
    blitz::Array<double,2> varr = vvells.as<double,2>()(LoRange::all(),LoRange::all());

    // uv-data from UVBrick
    VellSet bvsr = brickresult->vellSet(0);
    Vells bvellsr = bvsr.getValue();         // Real part
    VellSet bvsi = brickresult->vellSet(1);
    Vells bvellsi = bvsi.getValue();         // Imaginary part
    Vells bvells = VellsMath::tocomplex(bvellsr,bvellsi);
    blitz::Array<dcomplex,3> barr = bvells.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

    // uv grid from UVBrick
    int nu = brickcells.ncells(Axis::axis("U"));
    int nv = brickcells.ncells(Axis::axis("V"));
    const LoVec_double uu = brickcells.center(Axis::axis("U"));
    const LoVec_double vv = brickcells.center(Axis::axis("V"));

    // Map Time-Freq Cell boundaries on UV-data boundaries
    // Lower and higher bound for u and v based on circular (not elliptical) 
    //   trajectory
    // Assume u, v of UVW-Node are not frequency dependent.
    blitz::Array<double,1> lu(nt);
    blitz::Array<double,1> hu(nt);
    blitz::Array<double,1> lv(nt);
    blitz::Array<double,1> hv(nt);
    
    double dt1,dt2;
    for (int i = 0; i < nt; i++){

      dt1 = loti(i)-time(i);
      lu(i) = uarr(i,0)*casa::cos(2*pi*dt1/24/3600)+varr(i,0)*casa::sin(2*pi*dt1/24/3600);
      lv(i) = -uarr(i,0)*casa::sin(2*pi*dt1/24/3600)+varr(i,0)*casa::cos(2*pi*dt1/24/3600);
      
      dt2 = hiti(i)-time(i);
      hu(i) = uarr(i,0)*casa::cos(2*pi*dt2/24/3600)+varr(i,0)*casa::sin(2*pi*dt2/24/3600);
      hv(i) = -uarr(i,0)*casa::sin(2*pi*dt2/24/3600)+varr(i,0)*casa::cos(2*pi*dt2/24/3600);

    };

    // Make an array, connected to the Vells, with which we fill the Vells.
    LoMat_dcomplex arr = fvells.as<dcomplex,2>();
    arr = 0.0;

    double uc,vc,u1,u2,u3,u4,v1,v2,v3,v4;
    double umax,umin,vmax,vmin;
    int    imin,imax,jmin,jmax;
    bool   t1,t2,t3,t4;
    int    np;
    int    ia,ib,ja,jb;
    double t,s;

    for (int i = 0; i < nt; i++){
      for (int j = 0; j < nf; j++){
	
	// Determine center value & boundary values of a Cell
	uc = freq(j)*uarr(i,0)/c0;
	vc = freq(j)*varr(i,0)/c0;

	u1 = lofr(j)*lu(i)/c0;
	u2 = hifr(j)*lu(i)/c0;
	u3 = hifr(j)*hu(i)/c0;
	u4 = lofr(j)*hu(i)/c0;

	v1 = lofr(j)*lv(i)/c0;
	v2 = hifr(j)*lv(i)/c0;
	v3 = hifr(j)*hv(i)/c0;
	v4 = lofr(j)*hv(i)/c0;

	// Determine range of UVBrick gridpoints where the Cell maps onto
	umin = casa::min(casa::min(u1,u2),casa::min(u3,u4));
	umax = casa::max(casa::max(u1,u2),casa::max(u3,u4));
	vmin = casa::min(casa::min(v1,v2),casa::min(v3,v4));
	vmax = casa::max(casa::max(v1,v2),casa::max(v3,v4));

	for (int i1 = 0; i1 < nu-1; i1++){
	  if ((uu(i1)<=umin) && (uu(i1+1)>umin)) {imin = i1;};
	  if ((uu(i1)<=umax) && (uu(i1+1)>umax)) {imax = i1;};
	};
	for (int j1 = 0; j1 < nv-1; j1++){
	  if ((vv(j1)<=vmin) && (vv(j1+1)>vmin)) {jmin = j1;};
	  if ((vv(j1)<=vmax) && (vv(j1+1)>vmax)) {jmax = j1;};
	};

	// Add uv-data for UVBrick gridpoints within the Cell
	np=0;
	for (int i1 = imin; i1 < imax+1; i1++){
	  for (int j1 = jmin; j1 < jmax+1; j1++){

	    t1 = line(u1,v1,u2,v2,uc,vc,uu(i1),vv(j1));
	    t2 = line(u3,v3,u4,v4,uc,vc,uu(i1),vv(j1));
	    t3 = arc(u2,v2,u3,v3,uc,vc,uu(i1),vv(j1));
	    t4 = arc(u4,v4,u1,v1,uc,vc,uu(i1),vv(j1));

	    if (t1 && t2 && t3 && t4){
	      arr(i,j) = arr(i,j) + barr(j,i1,j1);
	      np++;
	    };
	    
	  };
	};
	
	if (np==0){
	  // No points found in the Cell, so find a value by bilinear interpolation

	  for (int i1 = imin; i1 < imax+1; i1++){
	    if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1;ib = i1+1;};
	  };
	  for (int j1 = jmin; j1 < jmax+1; j1++){
	    if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1; jb=j1+1;};
	  };

	  t = (uc-uu(ia))/(uu(ib)-uu(ia));
	  s = (vc-vv(ja))/(vv(jb)-vv(ja));
	  
	  arr(i,j) = (1-t)*(1-s)*barr(j,ia,jb) + t*(1-s)*barr(j,ib,ja) +
	    t*s*barr(j,ib,jb) + (1-t)*s*barr(j,ia,jb);

	} else {
	  // Np points found in the Cell, take average value

	  arr(i,j) = arr(i,j)/double(np);	  

	};

	// Mutiply with the area of the Cell to get integrated value
	arr(i,j) = arr(i,j)*double(2)*pi*(hiti(i)-loti(i))/double(24)/double(3600) * ( u2*u2 + v2*v2 - u1*u1 - v1*v1 ) / double(2);

      };
    };
    
    
  };


  bool UVInterpol::line(double u1, double v1, double u2, double v2, double u3, double v3, double u4, double v4)
  {
    // True: (u3,v3) and (u4,v4) lie on the same side of the line through (u1,v1) and (u2,v2).
    // False: not.

    double r1,r2;
    bool t(false);

    r1 = (u1-u2)*v3 - (v1-v2)*u3 + u2*v1 - u1*v2;
    r2 = (u1-u2)*v4 - (v1-v2)*u4 + u2*v1 - u1*v2;

    if (r1*r2 > 0) {
      t = true;
    }

    return t;
  };
    
  bool UVInterpol::arc(double u1, double v1, double u2, double v2, double u3, double v3, double u4, double v4)
  {
  
    // True: (u3,v3) and (u4,v4) lie on the same side of the (circular) arc through (u1,v1) and (u2,v2).
    // False: not.
  
    double r1,r2;
    bool t(false);

    r1 = u1*u1 + v1*v1 - u3*u3 - v3*v3;
    r2 = u1*u1 + v1*v1 - u4*u4 - v4*v4;

    if (r1*r2 > 0) {
      t = true;
    }

    return t;

  };

 void UVInterpol::fillVells2(const std::vector<Result::Ref> &fchildres, 
			     Vells &fvells, const Cells &fcells)
  {
    // Definition of constants
    const double c0 = casa::C::c;  // Speed of light
    const double pi = casa::C::pi; // Pi = 3.1415....

    // Time-Freq boundaries of Request
    int nt = fcells.ncells(Axis::TIME);
    int nf = fcells.ncells(Axis::FREQ);
    const LoVec_double freq = fcells.center(Axis::FREQ); 
    const LoVec_double lofr = fcells.cellStart(Axis::FREQ); 
    const LoVec_double hifr = fcells.cellEnd(Axis::FREQ);
 
    const LoVec_double time = fcells.center(Axis::TIME); 
    const LoVec_double loti = fcells.cellStart(Axis::TIME); 
    const LoVec_double hiti = fcells.cellEnd(Axis::TIME); 

    // Get the Child Results: brickresult, brickcells for UVBrick-Node
    //                        uvpoints for UVW-Node
    Result::Ref brickresult;
    Cells brickcells; 
    Result::Ref uvpoints;

    if ( fchildres.at(0)->cells().isDefined(Axis::axis("U")) &&
	 fchildres.at(0)->cells().isDefined(Axis::axis("V")) )
      {
	brickresult = fchildres.at(0);
	brickcells = brickresult->cells();
	uvpoints = fchildres.at(1);
      } 
    else 
      {
	brickresult = fchildres.at(1);
	brickcells = brickresult->cells();
	uvpoints = fchildres.at(0);
      };

    // u, v values from UVW-Node
    VellSet uvs = uvpoints->vellSet(0);
    VellSet vvs = uvpoints->vellSet(1);
    Vells uvells = uvs.getValue();
    Vells vvells = vvs.getValue();

    blitz::Array<double,2> uarr = uvells.as<double,2>()(LoRange::all(),LoRange::all());
    blitz::Array<double,2> varr = vvells.as<double,2>()(LoRange::all(),LoRange::all());

    // uv-data from UVBrick
    //VellSet bvsr = brickresult->vellSet(0);
    //Vells bvellsr = bvsr.getValue();         // Real part
    //VellSet bvsi = brickresult->vellSet(1);
    //Vells bvellsi = bvsi.getValue();         // Imaginary part
    //Vells bvells = VellsMath::tocomplex(bvellsr,bvellsi);
    //blitz::Array<dcomplex,3> barr = bvells.as<dcomplex,4>()(0,LoRange::all(),LoRange::all(),LoRange::all());

    // uv grid from UVBrick
    int nu = brickcells.ncells(Axis::axis("U"));
    int nv = brickcells.ncells(Axis::axis("V"));
    const LoVec_double uu = brickcells.center(Axis::axis("U"));
    const LoVec_double vv = brickcells.center(Axis::axis("V"));

    // Map Time-Freq Cell boundaries on UV-data boundaries
    // Lower and higher bound for u and v based on circular (not elliptical) 
    //   trajectory
    // Assume u, v of UVW-Node are not frequency dependent.
    blitz::Array<double,1> lu(nt);
    blitz::Array<double,1> hu(nt);
    blitz::Array<double,1> lv(nt);
    blitz::Array<double,1> hv(nt);
    
    double dt1,dt2;
    for (int i = 0; i < nt; i++){

      dt1 = loti(i)-time(i);
      lu(i) = uarr(i,0)*casa::cos(2*pi*dt1/24/3600)+varr(i,0)*casa::sin(2*pi*dt1/24/3600);
      lv(i) = -uarr(i,0)*casa::sin(2*pi*dt1/24/3600)+varr(i,0)*casa::cos(2*pi*dt1/24/3600);
      
      dt2 = hiti(i)-time(i);
      hu(i) = uarr(i,0)*casa::cos(2*pi*dt2/24/3600)+varr(i,0)*casa::sin(2*pi*dt2/24/3600);
      hv(i) = -uarr(i,0)*casa::sin(2*pi*dt2/24/3600)+varr(i,0)*casa::cos(2*pi*dt2/24/3600);

    };

    // Make an array, connected to the Vells, with which we fill the Vells.
    LoMat_double arr = fvells.as<double,4>()(0,0,LoRange::all(),LoRange::all());;
    arr = 0.0;

    double uc,vc,u1,u2,u3,u4,v1,v2,v3,v4;
    double umax,umin,vmax,vmin;
    int    imin,imax,jmin,jmax;
    bool   t1,t2,t3,t4;
    int    np;
    int    ia,ib,ja,jb;
    double t,s;

    for (int i = 0; i < nt; i++){
      for (int j = 0; j < nf; j++){
	
	// Determine center value & boundary values of a Cell
	uc = freq(j)*uarr(i,0)/c0;
	vc = freq(j)*varr(i,0)/c0;

	u1 = lofr(j)*lu(i)/c0;
	u2 = hifr(j)*lu(i)/c0;
	u3 = hifr(j)*hu(i)/c0;
	u4 = lofr(j)*hu(i)/c0;

	v1 = lofr(j)*lv(i)/c0;
	v2 = hifr(j)*lv(i)/c0;
	v3 = hifr(j)*hv(i)/c0;
	v4 = lofr(j)*hv(i)/c0;

	// Determine range of UVBrick gridpoints where the Cell maps onto
	umin = casa::min(casa::min(u1,u2),casa::min(u3,u4));
	umax = casa::max(casa::max(u1,u2),casa::max(u3,u4));
	vmin = casa::min(casa::min(v1,v2),casa::min(v3,v4));
	vmax = casa::max(casa::max(v1,v2),casa::max(v3,v4));

	for (int i1 = 0; i1 < nu-1; i1++){
	  if ((uu(i1)<=umin) && (uu(i1+1)>umin)) {imin = i1;};
	  if ((uu(i1)<=umax) && (uu(i1+1)>umax)) {imax = i1;};
	};
	for (int j1 = 0; j1 < nv-1; j1++){
	  if ((vv(j1)<=vmin) && (vv(j1+1)>vmin)) {jmin = j1;};
	  if ((vv(j1)<=vmax) && (vv(j1+1)>vmax)) {jmax = j1;};
	};

	// Add uv-data for UVBrick gridpoints within the Cell
	np=0;
	for (int i1 = imin; i1 < imax+1; i1++){
	  for (int j1 = jmin; j1 < jmax+1; j1++){

	    t1 = line(u1,v1,u2,v2,uc,vc,uu(i1),vv(j1));
	    t2 = line(u3,v3,u4,v4,uc,vc,uu(i1),vv(j1));
	    t3 = arc(u2,v2,u3,v3,uc,vc,uu(i1),vv(j1));
	    t4 = arc(u4,v4,u1,v1,uc,vc,uu(i1),vv(j1));

	    if (t1 && t2 && t3 && t4){
	      arr(i1,j1) = double(j + nf*i+1);
	      np++;
	    };
	    
	  };
	};

      };
    };
    
    
  };
  
} // namespace Meq

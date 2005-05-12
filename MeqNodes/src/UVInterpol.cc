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
  
  UVInterpol::UVInterpol():
    _additional_info(false),
    _uvZ(0.0),
    _uvDelta(casa::C::pi/2.)
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
	if (!_additional_info)
	  {
	    // Create only the Integrated / Interpolated UVdata
	    
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
	  }
	else
	  {
	    // Make both the Integrated / Interpolated UVdata
	    // and Additional Info on Number of gridpoints per Cell 
	    //                    and UV-plane coverage
	    
	    // Create Result object and attach to the Ref that was passed in.
	    resref <<= new Result(1);                  // 1 plane
	    VellSet& vs1 = resref().setNewVellSet(0);  // create new object for plane 0
	    // Make the Additional Vells
	    
	    Result& res2 = resref["UVInterpol.Map"] <<= new Result(1); 
	    VellSet& vs2 = res2.setNewVellSet(0);
	    
	    Result& res3 = resref["UVInterpol.Count"] <<= new Result(1);
	    VellSet& vs3 = res3.setNewVellSet(0);  

	    Result& res4 = resref["UVInterpol.UVImage"] <<= new Result(1);
	    VellSet& vs4 = res4.setNewVellSet(0);  

	    Result& res5 = resref["UVInterpol.UVCurvature"] <<= new Result(1);
	    VellSet& vs5 = res5.setNewVellSet(0);  
	    
	    //
	    // Make the Result
	    //		
	    
	    // Make a shape (Interpolation and Grid Point Count)
	    Vells::Shape shape1;
	    Axis::degenerateShape(shape1,rcells.rank());
	    shape1[Axis::TIME] = rcells.ncells(Axis::TIME);
	    shape1[Axis::FREQ] = rcells.ncells(Axis::FREQ);
	    
	    // Make a second shape for the UV Coverage
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
	    
	    // uv image domain
	    Domain::Ref newdomain(new Domain());
	    newdomain().defineAxis(1,uu(0),uu(nu-1));
	    newdomain().defineAxis(0,vv(0),vv(nv-1));
	    Cells::Ref newcells(new Cells(*newdomain));
	    newcells().setCells(1,uu(0),uu(nu-1),nu);
	    newcells().setCells(0,vv(0),vv(nv-1),nv);    
	    
	    Vells::Shape shape2;
	    Axis::degenerateShape(shape2,newcells->rank());
	    shape2[Axis::axis("freq")] = brickcells.ncells(Axis::axis("U"));
	    shape2[Axis::axis("time")] = brickcells.ncells(Axis::axis("V"));
	    
	    // curvature map domain
	    Domain::Ref newdomain2(new Domain());
	    newdomain2().defineAxis(1,uu(1),uu(nu-2));
	    newdomain2().defineAxis(0,vv(1),vv(nv-2));
	    Cells::Ref newcells2(new Cells(*newdomain2));
	    newcells2().setCells(1,uu(1),uu(nu-2),nu-2);
	    newcells2().setCells(0,vv(1),vv(nv-2),nv-2);

	    Vells::Shape shape3;
	    Axis::degenerateShape(shape3,newcells->rank());
	    shape3[Axis::axis("freq")] = nu-2;
	    shape3[Axis::axis("time")] = nv-2;

	    // Make a new Vells
	    Vells & vells1 = vs1.setValue(new Vells(dcomplex(0),shape1,false));
	    Vells & vells2 = vs2.setValue(new Vells(double(0),shape2,false));
	    Vells & vells3 = vs3.setValue(new Vells(double(0),shape1,false));
	    Vells & vells4 = vs4.setValue(new Vells(dcomplex(0),shape2,false));
	    Vells & vells5 = vs5.setValue(new Vells(dcomplex(0),shape3,false));

	    
	    // Fill the Vells (this is were the interpolation takes place)
	    //fillVells(childres,vells1,rcells);	
	   	     
	    // Fill the Vells (this is were the interpolation takes place)
	    //fillVells2(childres,vells1,vells2,vells3,vells4,vells5,rcells);	
	    // Fill the Vells (this is were the interpolation takes place)
	    fillVells3(childres,vells1,vells2,vells3,vells4,vells5,rcells);	
	    
	    // Attach the request Cells to the result
	    resref().setCells(rcells);
	    res2.setCells(*newcells);
	    res3.setCells(rcells);
	    res4.setCells(*newcells);
	    res5.setCells(*newcells2);

	  };

      }; 
    
    return 0;
    
  };
  
  void UVInterpol::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
    rec["Additional.Info"].get(_additional_info,initializing);
    rec["UVZ"].get(_uvZ,initializing);
    rec["UVDelta"].get(_uvDelta,initializing);
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
      lu(i) = uarr(i,0)*casa::cos(2*pi*dt1/24/3600)
	     -(varr(i,0)-casa::cos(_uvDelta)*_uvZ)/casa::sin(_uvDelta)
	     *casa::sin(2*pi*dt1/24/3600);
      lv(i) = casa::sin(_uvDelta)*uarr(i,0)*casa::sin(2*pi*dt1/24/3600)
	     +(varr(i,0)-casa::cos(_uvDelta)*_uvZ)
	     *casa::cos(2*pi*dt1/24/3600)
	     +casa::cos(_uvDelta)*_uvZ;
      
      dt2 = hiti(i)-time(i);
      hu(i) = uarr(i,0)*casa::cos(2*pi*dt2/24/3600)
	     -(varr(i,0)-casa::cos(_uvDelta)*_uvZ)/casa::sin(_uvDelta)
	     *casa::sin(2*pi*dt2/24/3600);
      hv(i) = casa::sin(_uvDelta)*uarr(i,0)*casa::sin(2*pi*dt2/24/3600)
	     +(varr(i,0)-casa::cos(_uvDelta)*_uvZ)
	     *casa::cos(2*pi*dt2/24/3600)
	     +casa::cos(_uvDelta)*_uvZ;

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

	imin = 0;
	imax = nu-1;
	jmin = 0;
	jmax = nv-1;

	for (int i1 = 0; i1 < nu-1; i1++){
	  if ((uu(i1)<=umin) && (uu(i1+1)>umin)) {imin = i1;};
	  if ((uu(i1)<=umax) && (uu(i1+1)>umax)) {imax = i1+1;};
	};
	for (int j1 = 0; j1 < nv-1; j1++){
	  if ((vv(j1)<=vmin) && (vv(j1+1)>vmin)) {jmin = j1;};
	  if ((vv(j1)<=vmax) && (vv(j1+1)>vmax)) {jmax = j1+1;};
	};

	// Add uv-data for UVBrick gridpoints within the Cell
	np=0;
	for (int i1 = imin; i1 < imax+1; i1++){
	  for (int j1 = jmin; j1 < jmax+1; j1++){

	    t1 = line(u1,v1,u2,v2,uc,vc,uu(i1),vv(j1));
	    t2 = line(u3,v3,u4,v4,uc,vc,uu(i1),vv(j1));
	    t3 = arc(u2,v2,u3,v3,uc,vc,uu(i1),vv(j1),hifr(j));
	    t4 = arc(u4,v4,u1,v1,uc,vc,uu(i1),vv(j1),lofr(j));

	    if (t1 && t2 && t3 && t4){
	      arr(i,j) = arr(i,j) + barr(j,i1,j1);
	      np++;
	    };
	    
	  };
	};
	
	//	if (np==0){
	  // No points found in the Cell, so find a value by bilinear interpolation

	//	  for (int i1 = imin; i1 < imax+1; i1++){
	//	    if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1;ib = i1+1;};
	//	  };
	//	  for (int j1 = jmin; j1 < jmax+1; j1++){
	//	    if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1; jb=j1+1;};
	//	  };

	//	  t = (uc-uu(ia))/(uu(ib)-uu(ia));
	//	  s = (vc-vv(ja))/(vv(jb)-vv(ja));
	  
	//	  arr(i,j) = (1-t)*(1-s)*barr(j,ia,jb) + t*(1-s)*barr(j,ib,ja) +
	//	    t*s*barr(j,ib,jb) + (1-t)*s*barr(j,ia,jb);

	//	} else {
	  // Np points found in the Cell, take average value

	//	  arr(i,j) = arr(i,j)/double(np);	  

	//	};

	// Bi-linear interpolation (Num. Rec. Sec. 3.6)

	for (int i1 = imin; i1 < imax+1; i1++){
	  if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1;ib = i1+1;};
	};
	for (int j1 = jmin; j1 < jmax+1; j1++){
	  if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1; jb=j1+1;};
	};
	
	t = (uc-uu(ia))/(uu(ib)-uu(ia));
	s = (vc-vv(ja))/(vv(jb)-vv(ja));
	
	arr(i,j) = (1-t)*(1-s)*barr(j,ia,ja) 
	  + t*(1-s)*barr(j,ib,ja) +
	  t*s*barr(j,ib,jb) + (1-t)*s*barr(j,ia,jb);
	
	//	arr(i,j) = arr(i,j)/double(np+1);	  

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
    
  bool UVInterpol::arc(double u1, double v1, double u2, double v2, double u3, double v3, double u4, double v4, double freq)
  {
  
    // True: (u3,v3) and (u4,v4) lie on the same side of the (circular) arc through (u1,v1) and (u2,v2).
    // False: not.
    const double c0 = casa::C::c;  // Speed of light

    double r1,r2;
    bool t(false);

    r1 = u1*u1 + (v1-freq*_uvZ*casa::cos(_uvDelta)/c0)
                *(v1-freq*_uvZ*casa::cos(_uvDelta)/c0)
                /casa::sin(_uvDelta)/casa::sin(_uvDelta) 
       - u3*u3 - (v3-freq*_uvZ*casa::cos(_uvDelta)/c0)
                *(v3-freq*_uvZ*casa::cos(_uvDelta)/c0)
                /casa::sin(_uvDelta)/casa::sin(_uvDelta);
    r2 = u1*u1 + (v1-freq*_uvZ*casa::cos(_uvDelta)/c0)
                *(v1-freq*_uvZ*casa::cos(_uvDelta)/c0)
                /casa::sin(_uvDelta)/casa::sin(_uvDelta) 
       - u4*u4 - (v4-freq*_uvZ*casa::cos(_uvDelta)/c0)
                *(v4-freq*_uvZ*casa::cos(_uvDelta)/c0)
                /casa::sin(_uvDelta)/casa::sin(_uvDelta);

    if (r1*r2 > 0) {
      t = true;
    }

    return t;

  };

 void UVInterpol::fillVells2(const std::vector<Result::Ref> &fchildres, 
			     Vells &fvells1, Vells &fvells2, Vells &fvells3, 
			     Vells &fvells4, Vells &fvells5, const Cells &fcells)
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
      lu(i) = uarr(i,0)*casa::cos(2*pi*dt1/24/3600)
	     -(varr(i,0)-casa::cos(_uvDelta)*_uvZ)/casa::sin(_uvDelta)
	     *casa::sin(2*pi*dt1/24/3600);
      lv(i) = casa::sin(_uvDelta)*uarr(i,0)*casa::sin(2*pi*dt1/24/3600)
	     +(varr(i,0)-casa::cos(_uvDelta)*_uvZ)
	     *casa::cos(2*pi*dt1/24/3600)
	     +casa::cos(_uvDelta)*_uvZ;
      
      dt2 = hiti(i)-time(i);
      hu(i) = uarr(i,0)*casa::cos(2*pi*dt2/24/3600)
	     -(varr(i,0)-casa::cos(_uvDelta)*_uvZ)/casa::sin(_uvDelta)
	     *casa::sin(2*pi*dt2/24/3600);
      hv(i) = casa::sin(_uvDelta)*uarr(i,0)*casa::sin(2*pi*dt2/24/3600)
	     +(varr(i,0)-casa::cos(_uvDelta)*_uvZ)
	     *casa::cos(2*pi*dt2/24/3600)
	     +casa::cos(_uvDelta)*_uvZ;
    };

    // Make an array, connected to the Vells, with which we fill the Vells.
    LoMat_dcomplex arr1 = fvells1.as<dcomplex,2>();
    arr1 = 0.0;
    LoMat_double arr2 = fvells2.as<double,2>();
    arr2 = 0.0;
    LoMat_double arr3 = fvells3.as<double,2>();
    arr3 = 0.0;
    LoMat_dcomplex arr4 = fvells4.as<dcomplex,2>();
    arr4 = 0.0;
    LoMat_dcomplex arr5 = fvells5.as<dcomplex,2>();
    arr5 = 0.0;

	//blitz::Array<dcomplex,2> arr1 = fvells1.as<dcomplex,2>();
	//arr1 = 0.0;
	//blitz::Array<double,2>   arr2 = fvells2.as<double,2>();
	//arr2 = 0.0;
	//blitz::Array<double,2>   arr3 = fvells3.as<double,2>();
	//arr3 = 0.0;
	//blitz::Array<dcomplex,2> arr4 = fvells4.as<dcomplex,2>();
	//arr4 = 0.0;
	//blitz::Array<dcomplex,2> arr5 = fvells5.as<dcomplex,2>();
	//arr5 = 0.0;

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

	imin = 0;
	imax = nu-1;
	jmin = 0;
	jmax = nv-1;

	for (int i1 = 0; i1 < nu-1; i1++){
	  if ((uu(i1)<=umin) && (uu(i1+1)>umin)) {imin = i1;};
	  if ((uu(i1)<=umax) && (uu(i1+1)>umax)) {imax = i1+1;};
	};
	for (int j1 = 0; j1 < nv-1; j1++){
	  if ((vv(j1)<=vmin) && (vv(j1+1)>vmin)) {jmin = j1;};
	  if ((vv(j1)<=vmax) && (vv(j1+1)>vmax)) {jmax = j1+1;};
	};

	// Add uv-data for UVBrick gridpoints within the Cell
	np=0;
	for (int i1 = imin; i1 < imax+1; i1++){
	  for (int j1 = jmin; j1 < jmax+1; j1++){

	    t1 = line(u1,v1,u2,v2,uc,vc,uu(i1),vv(j1));
	    t2 = line(u3,v3,u4,v4,uc,vc,uu(i1),vv(j1));
	    t3 = arc(u2,v2,u3,v3,uc,vc,uu(i1),vv(j1),hifr(j));
	    t4 = arc(u4,v4,u1,v1,uc,vc,uu(i1),vv(j1),lofr(j));

	    if (t1 && t2 && t3 && t4){
	      arr1(i,j) = arr1(i,j) + barr(j,i1,j1);
	      arr2(j1,i1) = double(j + nf*i+1);
	      np++;
	    };
	    
	  };
	};
	arr3(i,j) = np;

	//	if (np==0){
	  // No points found in the Cell, so find a value by bilinear interpolation
	  
	//	  for (int i1 = imin; i1 < imax+1; i1++){
	//	    if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1;ib = i1+1;};
	//	  };
	//	  for (int j1 = jmin; j1 < jmax+1; j1++){
	//	    if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1; jb=j1+1;};
	//	  };
	  
	//	  t = (uc-uu(ia))/(uu(ib)-uu(ia));
	//	  s = (vc-vv(ja))/(vv(jb)-vv(ja));
	  
	//	  arr1(i,j) = (1-t)*(1-s)*barr(j,ia,jb) + t*(1-s)*barr(j,ib,ja) +
	//	    t*s*barr(j,ib,jb) + (1-t)*s*barr(j,ia,jb);

	//	} else {
	  // Np points found in the Cell, take average value

	//	  arr1(i,j) = arr1(i,j)/double(np);	  

	//	};
	  

	arr1(i,j) = 0.0;

	ia = imin;
	ib = imax+1;
	ja = jmin;
	jb = jmax+1;

	for (int i1 = imin; i1 < imax+1; i1++){
	  if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1;ib = i1+1;};
	};
	for (int j1 = jmin; j1 < jmax+1; j1++){
	  if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1; jb=j1+1;};
	};
	
	t = (uc-uu(ia))/(uu(ib)-uu(ia));
	s = (vc-vv(ja))/(vv(jb)-vv(ja));
	
	//	arr1(i,j) = arr1(i,j) + (1-t)*(1-s)*barr(j,ia,jb) 
	 arr1(i,j) = (1-t)*(1-s)*barr(j,ia,ja) 
	  + t*(1-s)*barr(j,ib,ja) +
	  t*s*barr(j,ib,jb) + (1-t)*s*barr(j,ia,jb);
	 //arr1(i,j) = (1-t)*(1-s)*barr(j,ja,ia) 
	 // + t*(1-s)*barr(j,ja,ib) +
	 // t*s*barr(j,jb,ib) + (1-t)*s*barr(j,jb,ia);
	
	//	arr1(i,j) = arr1(i,j)/double(np+1);	  
	
      };
    };
    
    for (int i = 0; i < nu; i++){
      for (int j = 0; j < nv; j++){
    	arr4(j,i) = barr(0,i,j);
      };
    };

    for (int i = 1; i < nu-1; i++){
      for (int j = 1; j < nv-1; j++){
    	arr5(j,i) = (barr(0,i+1,j+1) + barr(0,i+1,j-1) + barr(0,i-1,j+1) + barr(0,i-1,j-1)) / 4.0 - barr(0,i,j);
      };
    };

    
  };


 void UVInterpol::fillVells3(const std::vector<Result::Ref> &fchildres, 
			     Vells &fvells1, Vells &fvells2, Vells &fvells3, 
			     Vells &fvells4, Vells &fvells5, const Cells &fcells)
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
    LoVec_double uu = brickcells.center(Axis::axis("U"));
    LoVec_double vv = brickcells.center(Axis::axis("V"));

    // u, v values from UVW-Node
    VellSet uvs = uvpoints->vellSet(0);
    VellSet vvs = uvpoints->vellSet(1);
    Vells uvells = uvs.getValue();
    Vells vvells = vvs.getValue();

    blitz::Array<double,2> uarr = uvells.as<double,2>()(LoRange::all(),LoRange::all());
    blitz::Array<double,2> varr = vvells.as<double,2>()(LoRange::all(),LoRange::all());

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
      lu(i) = uarr(i,0)*casa::cos(2*pi*dt1/24/3600)
	     -(varr(i,0)-casa::cos(_uvDelta)*_uvZ)/casa::sin(_uvDelta)
	     *casa::sin(2*pi*dt1/24/3600);
      lv(i) = casa::sin(_uvDelta)*uarr(i,0)*casa::sin(2*pi*dt1/24/3600)
	     +(varr(i,0)-casa::cos(_uvDelta)*_uvZ)
	     *casa::cos(2*pi*dt1/24/3600)
	     +casa::cos(_uvDelta)*_uvZ;
      
      dt2 = hiti(i)-time(i);
      hu(i) = uarr(i,0)*casa::cos(2*pi*dt2/24/3600)
	     -(varr(i,0)-casa::cos(_uvDelta)*_uvZ)/casa::sin(_uvDelta)
	     *casa::sin(2*pi*dt2/24/3600);
      hv(i) = casa::sin(_uvDelta)*uarr(i,0)*casa::sin(2*pi*dt2/24/3600)
	     +(varr(i,0)-casa::cos(_uvDelta)*_uvZ)
	     *casa::cos(2*pi*dt2/24/3600)
	     +casa::cos(_uvDelta)*_uvZ;
    };

    // Make an array, connected to the Vells, with which we fill the Vells.
    LoMat_dcomplex arr1 = fvells1.as<dcomplex,2>();
    arr1 = dcomplex(0.0);
    LoMat_double arr2 = fvells2.as<double,2>();
    arr2 = 0.0;
    LoMat_double arr3 = fvells3.as<double,2>();
    arr3 = 0.0;
    LoMat_dcomplex arr4 = fvells4.as<dcomplex,2>();
    arr4 = dcomplex(0.0);
    LoMat_dcomplex arr5 = fvells5.as<dcomplex,2>();
    arr5 = dcomplex(0.0);

    double uc,vc,u1,u2,u3,u4,v1,v2,v3,v4;
    double umax,umin,vmax,vmin;
    int    imin,imax,jmin,jmax;
    bool   t1,t2,t3,t4;
    int    np;
    int    ia,ib,ja,jb;
    double t,s;

    int ni, nj;
    LoMat_dcomplex coeff(nu,nv);

    // Bicubic Spline Interpolation using Natural Splines
    // Precompute 2nd derivative table (Can be done in UVBrick later)
    blitz::Array<dcomplex,2> btarr(nu,nv);
    blitz::Array<dcomplex,2> b2arr(nu,nv);
    dcomplex value, dvalue;
    blitz::Array<double,1> x1(4), x2(4);
    blitz::Array<dcomplex,2> y(4,4);

    blitz::Array<dcomplex,2> fx(nu,nv), fy(nu,nv), fxy(nu,nv);
    fx = dcomplex(0.0);
    fy = dcomplex(0.0);
    fxy = dcomplex(0.0);

    for (int i = 0; i < nt; i++){
      for (int j = 0; j < nf; j++){
	
	for (int i1= 1; i1< nu-1; i1++){
	  for (int j1 = 1; j1< nv-1; j1++){
	    fx(i1,j1) = (barr(j,i1+1,j1) + barr(j,i1-1,j1))/2.;
	    fy(i1,j1) = (barr(j,i1,j1+1) + barr(j,i1,j1-1))/2.;
	    fxy(i1,j1) = (barr(j,i1+1,j1+1) + barr(j,i1-1,j1+1) +
			  barr(j,i1+1,j1-1) + barr(j,i1-1,j1-1))/4.;
	  };
	};

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

	arr1(i,j) = dcomplex(0.0);

	ia = 0;
	ib = nu-1;
	ja = 0;
	jb = nv-1;

	for (int i1 = 0; i1 < nu; i1++){
	  if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {ia = i1;ib = i1+1;};
	};
	for (int j1 = 0; j1 < nv; j1++){
	  if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {ja = j1; jb=j1+1;};
	};

	s = (uc-uu(ia))/(uu(ib)-uu(ia));
	t = (vc-vv(ja))/(vv(jb)-vv(ja));
	
	arr1(i,j) = (1-t)*(1-s)*barr(j,ia,ja) 
	  + s*(1-t)*barr(j,ib,ja) 
	  + (1-s)*t*barr(j,ia,jb)
	  + t*s*barr(j,ib,jb)
	  + t*s*s*(1-s)*(barr(j,ib,jb)-fx(ib,jb))
	  + t*s*(1-s)*(1-s)*(barr(j,ia,jb)-fx(ia,jb))
	  + (1-t)*s*s*(1-s)*(barr(j,ib,ja)-fx(ib,ja))
	  + (1-t)*s*(1-s)*(1-s)*(barr(j,ia,ja)-fx(ia,ja))
	  + t*t*s*(1-t)*(barr(j,ib,jb)-fy(ib,jb))
	  + t*t*(1-t)*(1-s)*(barr(j,ia,jb)-fy(ia,jb))
	  + (1-t)*s*t*(1-t)*(barr(j,ib,ja)-fy(ib,ja))
	  + t*(1-t)*(1-t)*(1-s)*(barr(j,ia,ja)-fy(ia,ja))
	  + t*t*(1-t)*s*s*(1-s)*(barr(j,ib,jb) - fy(ib,jb) - fx(ib,jb) + fxy(ib,jb))
	  + t*t*(1-t)*s*(1-s)*(1-s)*(barr(j,ia,jb) - fy(ia,jb) - fx(ia,jb) + fxy(ia,jb))
	  + t*(1-t)*(1-t)*s*s*(1-s)*(barr(j,ib,ja) - fy(ib,ja) - fx(ib,ja) + fxy(ib,ja))
	  + t*(1-t)*(1-t)*s*(1-s)*(1-s)*(barr(j,ia,ja) - fy(ia,ja) - fx(ia,ja) + fxy(ia,ja));

	// 4th order polynomial interpolation

	//btarr = barr(j,LoRange::all(),LoRange::all());

	 //	for (int i1 = 0; i1 < nu-1; i1++){
	 //	  if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {
	 //	    imin = i1-1;
	 //	    imax = i1+2;
	 //	  };
	 //	};

	 //	for (int j1 = 0; j1 < nv-1; j1++){
	 //	  if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {
	 //	    jmin = j1-1;
	 //	    jmax = j1+2;
	 //	  };
	 //	};

	 //	for (int i1 =0; i1<4; i1++){
	 //	  x1(i1) = uu(imin+i1);
	 //	  for (int j1=0; j1<4; j1++){
	 //	    x2(j1) = vv(jmin+j1);
	 //	    y(i1,j1) = barr(j,imin+i1, jmin+j1);
	 //	  };
	 //	};

	//
	// High order polynomial interpolation
	 //	value = dcomplex(0.0);
	 //	dvalue = dcomplex(0.0);
	//UVInterpol::mypolin2(uu,vv,btarr,nu,nv,uc,vc,value, dvalue);
	 //	UVInterpol::mypolin2(x1,x2,y,4,4,uc,vc,value, dvalue);

	 //	arr1(i,j) = value;
	 //	arr3(i,j) = abs(dvalue);

	//
	// Bicubic (natural) Splines	

	//UVInterpol::mysplie2(uu,vv,btarr,nu,nv,b2arr);

	// Bicubic Spline Interpolation
	//UVInterpol::mysplin2(uu,vv,btarr,b2arr,nu,nv,uc,vc,value);
	//arr1(i,j) = value;

	//
	// Method by determining polynomial coefficients
	// (Not robust) 

	//	// Determine range of UVBrick gridpoints where the Cell maps onto
	//	umin = casa::min(casa::min(u1,u2),casa::min(u3,u4));
	//	umax = casa::max(casa::max(u1,u2),casa::max(u3,u4));
	//	vmin = casa::min(casa::min(v1,v2),casa::min(v3,v4));
	//	vmax = casa::max(casa::max(v1,v2),casa::max(v3,v4));

	//	imin = 0;
	//	imax = nu-1;
	//	jmin = 0;
	//	jmax = nv-1;

	// Searching can be optimised (Num. Rec. Sec. 3.4)
	//	for (int i1 = 0; i1 < nu-1; i1++){
	//	  if ((uu(i1)<=umin) && (uu(i1+1)>umin)) {imin = i1;};
	//	  if ((uu(i1)<=umax) && (uu(i1+1)>umax)) {imax = i1+1;};
	//	};
	//	for (int j1 = 0; j1 < nv-1; j1++){
	//	  if ((vv(j1)<=vmin) && (vv(j1+1)>vmin)) {jmin = j1;};
	//	  if ((vv(j1)<=vmax) && (vv(j1+1)>vmax)) {jmax = j1+1;};
	//	};

	// Construct 2D interpolating polynomial on 
	//  [imin,imax] x [jmin,jmax] grid

	//	ni = imax - imin + 1;
	//	nj = jmax - jmin + 1;

	//	if (ni>4) {
	//	  ni=4;
	//	  for (int i1 = 0; i1 < nu-1; i1++){
	//	    if ((uu(i1)<=uc) && (uu(i1+1)>uc)) {
	//	      imin = i1-1;
	//	      imax = i1+2;
	//	    };
	//	  };
	//	};

	//	if (nj>4) {
	//	  nj=4;
	//	  for (int j1 = 0; j1 < nv-1; j1++){
	//	    if ((vv(j1)<=vc) && (vv(j1+1)>vc)) {
	//	      jmin = j1-1;
	//	      jmax = j1+2;
	//	    };
	//	  };
	//	};

	//	interpolate(j,ni,imin,nj,jmin,coeff,barr,uu,vv);	

	// Integrate the Interpolating polynomial    

	//	double uav = (uu(imin+ni-1) - uu(imin))/2.;
	//	double vav = (vv(jmin+nj-1) - vv(jmin))/2.;
	//	double ur = uu(imin+ni-1)-uav;
	//	double vr = vv(jmin+nj-1)-vav;

	//	for (int k=0; k<ni; k++){
	//	  for (int l=0; l<nj; l++){
	//	    arr1(i,j) = arr1(i,j) + coeff(k,l)*pow((uc-uav)/ur,k) 
	//	                                      *pow((vc-vav)/vr,l);
	//	  };
	//	};

	//	arr3(i,j) = double(ni*nj);

      };
    };

    // First frequency plane of the UVImage
    for (int i = 0; i < nu; i++){
      for (int j = 0; j < nv; j++){
    	arr4(j,i) = barr(0,i,j);
      };
    };

    // Curvature map of the first frequency plane of the UVImage
    for (int i = 1; i < nu-1; i++){
      for (int j = 1; j < nv-1; j++){
    	arr5(j,i) = (barr(0,i+1,j+1) + barr(0,i+1,j-1) + barr(0,i-1,j+1) + barr(0,i-1,j-1)) / 4.0 - barr(0,i,j);
      };
    };


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
    int imax;
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
    y2(0) = u(0) = 0.0;

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
       	yatmp(i) = real(ya(j,i));
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
       	yatmp(i) = imag(ya(j,i));
      };
      ytmp=0.0;
      dytmp=0.0;
      UVInterpol::mypolint(x2a,yatmp,n,x2,ytmp,dytmp);
      ymtmp(j)=ytmp;
    };
    ytmp=0.0;
    dytmp=0.0;
    UVInterpol::mypolint(x1a,ymtmp,m,x1,ytmp,dytmp);

    y = y + dcomplex(0.0,ytmp);
    dy = dy + dcomplex(0.0,dytmp);

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

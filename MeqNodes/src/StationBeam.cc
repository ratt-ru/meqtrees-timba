//# StationBeam.cc: Calculates beam gasin of a StationBeam tracking a source at Ra, Dec
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
//# $Id: StationBeam.cc 5021 2007-03-29 12:47:34Z sarod $

#include <MeqNodes/StationBeam.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casacore/measures/Measures/MCDirection.h>
#include <casacore/measures/Measures/MBaseline.h>
#include <casacore/measures/Measures/MPosition.h>
#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/MeasConvert.h>
#include <casacore/measures/Measures/MeasTable.h>
#include <casacore/casa/Quanta/MVuvw.h>


//#define DEBUG
/*ra_,dec_; //tracking centre 
x_,y_,z_;//coords of phase centre in ITRF
phi0_; //rotation around zenith
f0_; //reference freq in Hz */

using namespace casacore;

namespace Meq {
  

const HIID FFilename= AidFilename;
const HIID FCoupling= AidCoupling;

const HIID child_labels[] = { AidAzEl|0,AidAzEl,AidRef|AidFreq };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);



//The node should have no children
StationBeam::StationBeam()
: TensorFunction(num_children,child_labels)
{
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
  coupling_defined_=0;
  phi0_ = 0;
}

StationBeam::~StationBeam()
{}

// Obtain an observatory - if a name is supplied
// use a 'global observatory position' to calculate StationBeam.
// Otherwise StationBeam will be calculated for individual
// station positions.
void StationBeam::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  TensorFunction::setStateImpl(rec,initializing);

  rec[AidPhi|0].get(phi0_,initializing);

  rec[FFilename].get(coordfile_name_,initializing);
#ifdef DEBUG
  cout<<"File Name ="<<coordfile_name_<<endl;
#endif

  //read file
  ifstream infd;
  string line;
  int nx,ci;
  infd.open(coordfile_name_.c_str());
  if (infd.is_open()) {
    getline(infd,line);
    sscanf(line.c_str(),"%d",&nx); 
    //allocate memory
    p_.resize(nx,6);
    ci=0;
    while (!infd.eof() && ci<nx){
      getline(infd,line);
      sscanf(line.c_str(),"%lf %lf %lf %lf %lf %lf",&p_(ci,0), &p_(ci,1), &p_(ci,2), &p_(ci,3), &p_(ci,4), &p_(ci,5)); 
      ci++;
    }
    infd.close();
  }

#ifdef DEBUG
   cout<<"P="<<p_<<endl;
#endif
  
  if (rec[FCoupling].get(couplingfile_name_,initializing) ) 
  {
#ifdef DEBUG
    cout<<"Coupling File Name ="<<couplingfile_name_<<endl;
#endif
    infd.open(couplingfile_name_.c_str());
    if (infd.is_open()) {
      coupling_defined_=1;
      c_.resize(nx,nx);//mutual coupling matrix
      ci=0;
      int cj;
      double dummy1,dummy2;
      while (!infd.eof() && ci<nx) {
        c_(ci,ci)=make_dcomplex(1.0,0.0); // diagonal is 1
        cj=0;
        while (!infd.eof() && cj<ci) {
          getline(infd,line);
          sscanf(line.c_str(),"%lf %lf",&dummy1, &dummy2); 
          c_(ci,cj)=make_dcomplex(dummy1,dummy2);
          c_(cj,ci)=make_dcomplex(dummy1,-dummy2);
          cj++;
        }
        ci++;
      }
      infd.close();
    }
#ifdef DEBUG
   cout<<"C="<<c_<<endl;
#endif
  }
}


void StationBeam::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &result,const Request &request)
{
  TensorFunction::computeResultCells(ref,result,request);
  const Cells & cells = *ref;
  FailWhen(!cells.isDefined(Axis::FREQ),"Meq::StationBeam: no freq axis in cells, can't compute StationBeams");
  // generate frequency vells for use in evaluateTensors() below
  Vells::Shape shape;
  Axis::degenerateShape(shape,cells.rank());
  int nc = shape[Axis::FREQ] = cells.ncells(Axis::FREQ);
  vfreq_ = Vells(0,shape,false);
  memcpy(vfreq_.realStorage(),cells.center(Axis::FREQ).data(),nc*sizeof(double));
}


LoShape StationBeam::getResultDims (const vector<const LoShape *> &input_dims)
{
  //Assert(input_dims.size()>=1);
  // result is a single vellset
  return LoShape(1);
}



void StationBeam::evaluateTensors (std::vector<Vells> & out,   
                            const std::vector<std::vector<const Vells *> > &args)
{
  const Vells& vaz0  = *(args[0][0]);
  const Vells& vel0 = *(args[0][1]);
  const Vells& vaz = *(args[1][0]);
  const Vells& vel = *(args[1][1]);
  const Vells& vf0 = *(args[2][0]);
  // we only support scalar for reference freq
  Assert(vf0.isScalar());
  double f0_   = vf0.getScalar<double>();
 
  // we iterate over az0, el0, az,el, and frequency, so compute output shape and strides accordingly
  Vells::Shape outshape;
  Vells::Strides strides[5];
  const Vells::Shape * inshapes[5] = { 
      &(vaz0.shape()),&(vel0.shape()),&(vaz.shape()),&(vel.shape()),&(vfreq_.shape()) };  
  Vells::computeStrides(outshape,strides,5,inshapes,"StationBeam");

  // allocate output Vells
  out[0] = Vells(make_dcomplex(0.0),outshape,false);
  dcomplex * pout = out[0].complexStorage();

  // some more constants
  double c=2.99792458e8;
  blitz::Array<dcomplex,1> wk;
  wk.resize(p_.extent(0));

  // setup input iterators
  Vells::ConstStridedIterator<double> paz0(vaz0,strides[0]);
  Vells::ConstStridedIterator<double> pel0(vel0,strides[1]);
  Vells::ConstStridedIterator<double> paz(vaz,strides[2]);
  Vells::ConstStridedIterator<double> pel(vel,strides[3]);
  Vells::ConstStridedIterator<double> pfreq(vfreq_,strides[4]);

  // az0,el0 are the current tracking center.
  // az,el is the current direction for which we're computing the beam.
  // Init them to be != to their initial itertor values, so that comparisons below
  // fail and various quentities dependent on them are recomputed.
  double az0 = *paz0-1,
         el0 = *pel0-1,
         az  = *paz -1,
         el  = *pel -1;
  double cphi,sphi,ctheta,stheta;

  Vells::DimCounter counter(outshape);
  while( true )
  {
    // If tracking center has changed w.r.t. previous iteration, recompute delays & weights.
    // Typically, this will only change with time, which iterates slowest, so this
    // computation will not happen too often.
    if( *paz0 != az0 || *pel0 != el0 )
    {
      az0 = *paz0;
      el0 = *pel0;
      double phi0 = az0 - phi0_; // azimuth rotated by station orientation
      double theta0 = M_PI_2 - el0; // declination from zenith
      //find k_0
      double k0[3];
      double omega0=2*M_PI*f0_; //reference freq
      k0[0]=-sin(theta0)*cos(phi0)/c*omega0;
      k0[1]=-sin(theta0)*sin(phi0)/c*omega0;
      k0[2]=-cos(theta0)/c*omega0;
      //calculate delays and weights
      double tau;
      for( int nt=0; nt<wk.extent(0); nt++ ) 
      {
        tau    = k0[0]*p_(nt,0)+k0[1]*p_(nt,1)+k0[2]*p_(nt,2);
        wk(nt) = make_dcomplex(cos(tau),sin(tau))/(double)p_.extent(0); //conjugate, and normalize
      }
     // mutual copling makes w^H x v_k to w^H x C x v_k, so postmultiply w by C
     // to reduce cost
     if (coupling_defined_) 
     {
        blitz::Array<dcomplex,1> wk1;
        int np=p_.extent(0);
        wk1.resize(np);
        wk1=wk;
        for (int nrr=0; nrr<np; nrr++) {
         wk(nrr)=make_dcomplex(0); 
         for (int ncc=0; ncc<np; ncc++) {
           wk(nrr)+=wk1(ncc)*c_(ncc,nrr);
         }
        }
      }
    }
    // omega_c is the only thing dependent on frequency. Cheap enough to recompute it each 
    // iteration, even if frequency hasn't changed
    double omega=2*M_PI*(*pfreq);
    double omega_c=omega/c;

    // if azimuth or elevation change, recompute sines/cosines
    if( az != *paz )
    {
      double phi = (az=*paz) - phi0_; // azimuth rotated by station orientation
      cphi = -cos(phi);
      sphi = -sin(phi);
    }
    if( el != *pel )
    {
      double theta  = M_PI_2 - (el=*pel);
      stheta = sin(theta);
      ctheta = cos(theta);
    }
    // init output beam to 0
    *pout = make_dcomplex(0);
    // now loop over weights and accumulate beam
    double kt[3];
//**        kt[0]=-sin(theta)*cos(phi)/c*omega;
//**        kt[1]=-sin(theta)*sin(phi)/c*omega;
//**        kt[2]=-cos(theta)/c*omega;
    kt[0] = stheta*cphi*omega_c;
    kt[1] = stheta*sphi*omega_c;
    kt[2] = -ctheta*omega_c;
    double tau;
    for( int nt=0; nt<wk.extent(0); nt++ ) 
    {
      tau = kt[0]*p_(nt,0)+kt[1]*p_(nt,1)+kt[2]*p_(nt,2);
      *pout += make_dcomplex(cos(tau),-sin(tau))*wk(nt);
    }
    // increment iterators
    pout++;
    // increment counter, break out when finished
    int ndim = counter.incr();
    if( !ndim )    
      break;
    paz0.incr(ndim);
    pel0.incr(ndim);
    paz.incr(ndim);
    pel.incr(ndim);
    pfreq.incr(ndim);
  }
}



} // namespace Meq

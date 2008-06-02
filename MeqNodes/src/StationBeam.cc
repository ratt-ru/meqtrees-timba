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
#include <measures/Measures/MCDirection.h>
#include <measures/Measures/MBaseline.h>
#include <measures/Measures/MPosition.h>
#include <measures/Measures/MEpoch.h>
#include <measures/Measures/MeasConvert.h>
#include <measures/Measures/MeasTable.h>
#include <casa/Quanta/MVuvw.h>


//#define DEBUG
/*ra_,dec_; //tracking centre 
x_,y_,z_;//coords of phase centre in ITRF
phi0_; //rotation around zenith
f0_; //reference freq in Hz */

using namespace casa;

namespace Meq {
  

const HIID FFilename= AidFilename;
const HIID FCoupling= AidCoupling;

const HIID child_labels[] = { AidRADec,AidXYZ,AidPhi0,AidRef|AidFreq };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);



//The node should have no children
StationBeam::StationBeam()
: TensorFunction(num_children,child_labels)
{
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
  coupling_defined_=0;
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

	if (rec[FCoupling].get(couplingfile_name_,initializing) ) {
#ifdef DEBUG
   cout<<"Coupling File Name ="<<couplingfile_name_<<endl;
#endif
   infd.open(couplingfile_name_.c_str());
   if (infd.is_open()) {
    coupling_defined_=1;
    c_.resize(nx,nx);//mutual coupling matrix
    ci=0;
    int cj;
    double dummy;
    while (!infd.eof() && ci<nx) {
      c_(ci,ci)=1; // diagonal is 1
      cj=0;
      while (!infd.eof() && cj<ci) {
        getline(infd,line);
        sscanf(line.c_str(),"%lf %lf",&c_(ci,cj), &dummy); 
        c_(cj,ci)=c_(ci,cj);
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


void StationBeam::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &,const Request &request)
{
  // NB: for the time being we only support scalar child results, 
  // and so we ignore the child cells, and only use the request cells
  // (while checking that they have a time axis)
  const Cells &cells = request.cells();
  FailWhen(!cells.isDefined(Axis::TIME),"Meq::StationBeam: no time axis in request, can't compute StationBeams");
  ref.attach(cells);
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
  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
  // create a frame for an Observatory, or a telescope station
  MeasFrame Frame; // create default frame 

  const Vells& vra  = *(args[0][0]);
  const Vells& vdec = *(args[0][1]);
  const Vells& vx   = *(args[1][0]);
  const Vells& vy   = *(args[1][1]);
  const Vells& vz   = *(args[1][2]);
  const Vells& vphi0   = *(args[2][0]);
  const Vells& vf0 = *(args[3][0]);
  // we only support scalars
  Assert( vra.isScalar() && vdec.isScalar() &&
    vx.isScalar() && vy.isScalar() && vz.isScalar() && 
    vphi0.isScalar() && vf0.isScalar() );

  double ra_ = vra.getScalar<double>();
  double dec_ = vdec.getScalar<double>();
  double x_ = vx.getScalar<double>();
  double y_ = vy.getScalar<double>();
  double z_ = vz.getScalar<double>();
  double phi0_ =vphi0.getScalar<double>();
  double f0_ =vf0.getScalar<double>();
 

  // thanks to checks in getResultDims(), we can expect all 
  // vectors to have the right sizes
  // Get RA and DEC, and station positions
  MPosition stnpos(MVPosition(x_,y_,z_),MPosition::ITRF);
  Frame.set(stnpos); // tie this frame to station position

  const Cells& cells = resultCells();
  // Get RA and DEC of location to be transformed to StationBeam (default is J2000).
  // assume input ra and dec are in radians
  MVDirection sourceCoord(ra_,dec_);

  int ntime = cells.ncells(Axis::TIME);
  int nfreq = cells.ncells(Axis::FREQ);
  int naz= cells.ncells(2);
  int nel= cells.ncells(3);

  const blitz::Array<double,1>& time = cells.center(Axis::TIME);
  const blitz::Array<double,1>& freq= cells.center(Axis::FREQ);
  const blitz::Array<double,1>& azval= cells.center(2);
  const blitz::Array<double,1>& elval= cells.center(3);
  out[0] = Vells(make_dcomplex(0.0),cells.shape(),false);
  dcomplex* data = out[0].complexStorage();
  blitz::Array<dcomplex,4> B(data,blitz::shape(ntime,nfreq,naz,nel));
  Quantum<double> qepoch(0, "s");
  qepoch.setValue(time(0));
  MEpoch mepoch(qepoch, MEpoch::UTC);
  Frame.set (mepoch);
  MDirection::Convert azel_converter = MDirection::Convert(sourceCoord,MDirection::Ref(MDirection::AZEL,Frame));
  double theta0,phi0;
  double c=2.99792e8;
  blitz::Array<dcomplex,1> wk;
  wk.resize(p_.extent(0));
  for( int ci=0; ci<ntime; ci++)  {
   qepoch.setValue (time(ci));
   mepoch.set (qepoch);
   Frame.set (mepoch);
   MDirection az_el_out(azel_converter());
   // convert ra, dec to Az El at given time
   Vector<Double> az_el = az_el_out.getValue().getAngle("rad").getValue();
   theta0 = M_PI/2-az_el(1); // declination from zenith
   phi0 = az_el(0)+phi0_; // azimuth rotated by 45
   //find k_0
	 double k0[3];
   double omega0=2*M_PI*f0_; //reference freq
   k0[0]=-sin(theta0)*cos(phi0)/c*omega0;
   k0[1]=-sin(theta0)*sin(phi0)/c*omega0;
   k0[2]=-cos(theta0)/c*omega0;
   for(int cj=0; cj<nfreq; cj++)  {
     double omega=2*M_PI*freq(cj);
     double tau;
     //calculate delays and weights
     for (int nt=0; nt<wk.extent(0); nt++) {
        tau=k0[0]*p_(nt,0)+k0[1]*p_(nt,1)+k0[2]*p_(nt,2);
        wk(nt)=make_dcomplex(cos(tau),sin(tau))/p_.extent(0); //conjugate, and normalize
     }
     // mutual copling makes w^H x v_k to w^H x C x v_k, so postmultiply w by C
     // to reduce cost
     if (coupling_defined_) {
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

     for( int ck=0; ck<naz; ck++)  {
       double phi=azval(ck); //no rotation here, because already rotated
       for( int cl=0; cl<nel; cl++)  {
          double theta=M_PI/2-elval(cl);
//std::cout<<"phi0="<<phi0<<" phi="<<phi<<" theta0="<<theta0<<" theta="<<theta<<std::endl;
          B(ci,cj,ck,cl)=make_dcomplex(0);
          //make array manifold vector
          double kt[3];
          kt[0]=-sin(theta)*cos(phi)/c*omega;
          kt[1]=-sin(theta)*sin(phi)/c*omega;
          kt[2]=-cos(theta)/c*omega;
//std::cout<<"k0 ="<<k0[0]<<" "<<k0[1]<<" "<<k0[2]<<std::endl;
//std::cout<<"k ="<<kt[0]<<" "<<kt[1]<<" "<<kt[2]<<std::endl;
          dcomplex vk;
          for (int nt=0; nt<wk.extent(0); nt++) {
           tau=kt[0]*p_(nt,0)+kt[1]*p_(nt,1)+kt[2]*p_(nt,2);
           vk=make_dcomplex(cos(tau),-sin(tau));
           B(ci,cj,ck,cl)+=vk*wk(nt);
          }
       }
     }
   }
  }
}

} // namespace Meq

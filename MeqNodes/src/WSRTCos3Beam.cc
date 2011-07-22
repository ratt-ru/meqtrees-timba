//# WSRTCos3Beam.cc: computes a WSRT cos(BF*freq*r)**3 voltage beam factor from BF and r children.
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
//# $Id: WSRTCos3Beam.cc 5418 2007-07-19 16:49:13Z oms $

#include <MeqNodes/WSRTCos3Beam.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <DMI/List.h>
#include <casa/BasicSL/Constants.h>
#include <cmath>

namespace Meq {

using namespace VellsMath;

const HIID child_labels[] = { AidBF,AidR,AidZ };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);


// Constants defining Zernike polynomials
// highest n (in Z^m_n) supported
const int MAX_N = 5;

// This determines the standard Noll numbering from a single integer j
// to n,m,k giving the Zernike polynomial Z^m_n (see http://oeis.org/A176988)
// with the radial polynomial R_k (see table below)
// (The R_k numbering simply uses the R^m_n polynomials in order of increasing n,m)
const int nmk_from_j[][3] =
{
     {0,0,0}, {1,1,1}, {1,-1,1}, {2,0,2}, {2,-2,3}, {2,2,3}, {3,-1,4}, {3,1,4}, {3,-3,5}, {3,3,5},
     {4,0,6}, {4,2,7}, {4,-2,7}, {4,4,8}, {4,-4,8}, {5,1,9}, {5,-1,9}, {5,3,10}, {5,-3,10}, {5,5,11}
};
// this gives the coefficients of the first few radial polynomials per each k
const int rk_coeff[][MAX_N+1] =
{
  {  1,  0,  0,  0,  0,  0},
  {  0,  1,  0,  0,  0,  0},
  { -1,  0,  2,  0,  0,  0},
  {  0,  0,  1,  0,  0,  0},
  {  0, -2,  0,  3,  0,  0},
  {  0,  0,  0,  1,  0,  0},
  {  1,  0, -6,  0,  6,  0},
  {  0,  0, -3,  0,  4,  0},
  {  0,  0,  0,  0,  1,  0},
  {  0,  3,  0,-12,  0, 10},
  {  0,  0,  0, -4,  0,  5},
  {  0,  0,  0,  0,  0,  1},
};
// max number of Zernike polynomials supported
const int MAX_NZ = sizeof(nmk_from_j)/(sizeof(int)*3);
// highest K (in R_k) supported
const int NUM_RK = sizeof(rk_coeff)/(sizeof(int)*(MAX_N+1));


WSRTCos3Beam::WSRTCos3Beam()
: TensorFunction(num_children,child_labels,num_children-1),
  clip_(100*(casa::C::pi/180)),deriv_(false)
{
  // dependence on frequency
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

WSRTCos3Beam::~WSRTCos3Beam()
{}

void WSRTCos3Beam::setStateImpl (DMI::Record::Ref& rec, bool initializing)
{
  Node::setStateImpl(rec,initializing);
  rec[AidDeriv].get(deriv_,initializing);
  rec[AidClip].get(clip_,initializing);
  // in first-model mode, compute argument clip
  if( clip_ > 0 )
    argclip_ = std::acos(std::pow(std::min(clip_,1.),1/3.));
  else if( clip_ == 0 )
    argclip_ = 0;
}

void WSRTCos3Beam::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request)
{
  // copy cells of first child
  if( childres[0]->hasCells() )
    ref.attach(childres[0]->cells());
  else
    ref.attach(request.cells());
  // check that we now have a time axis
  FailWhen(!ref->isDefined(Axis::FREQ),"Meq::WSRTCos3Beam: no freq axis in child result or in request, can't compute RA/Dec");
  // create frequency vells
  int nfreq = request.cells().ncells(Axis::FREQ);
  freq_vells_ = Vells(0,Axis::vectorShape(Axis::FREQ,nfreq),false);
  memcpy(freq_vells_.realStorage(),request.cells().center(Axis::FREQ).data(),nfreq*sizeof(double));
}


LoShape WSRTCos3Beam::getResultDims (const vector<const LoShape *> &input_dims)
{
  if( input_dims[0]->product() != 1)
    Throw("child 0: single value (bf) expected");
  if( deriv_ )
  {
    if( input_dims[1]->product() != 2)
      Throw("child 1: 2-vector (l,m) expected");
    return LoShape(2);
  }
  else
  {
    if( input_dims[1]->product() > 2 )
      Throw("child 1: single value (r) or 2-vector (l,m) expected");
    return LoShape(1);
  }
  // check Z child
  if( input_dims.size()>2 )
  {
    if( input_dims[2]->size() != 1 )
      Throw("child 2: single vector of Zernike coefficients expected");
    if( input_dims[2][0] > MAX_NZ )
      Throw(Debug::ssprintf("child 2: too many values, at most %d allowed",MAX_NZ));
    if( input_dims[1]->product() != 2 )
      Throw(Debug::ssprintf("child 1: 2-vector (l,m) expected, if child 3 (Zernike coefficients) is given"));
  }
}

void WSRTCos3Beam::evaluateTensors (std::vector<Vells> & out,
                                   const std::vector<std::vector<const Vells *> > &args )
{
  const Vells &bf = *(args[0][0]);
  Vells bf_by_freq = bf*freq_vells_;
  Vells r,l,m;
  if( args[1].size() == 1 )
    r = *args[1][0];
  else if( args[1].size() == 2 )
  {
    l = *args[1][0];
    m = *args[1][1];
    r = sqrt(l*l+m*m);
  }
  Vells bfr = r*bf_by_freq;
  // derivative mode
  if( deriv_ )
  {
    const Vells &l = *args[1][0];
    const Vells &m = *args[1][1];
    Vells t = -3 * bf * pow2(cos(bfr)) * sin(bfr) / r;
    out[0] = t * l * freq_vells_;
    out[1] = t * m * freq_vells_;
  }
  // normal mode
  else
  {
    // broken NEWSTAR-style clipping
    if( clip_ < 0 )
      out[0] = max(abs(pow3(cos(bfr))),-clip_,-1,2);
    // proper argument clipping
    else if( argclip_ > 0 )
      out[0] = pow3(cos(min(bfr,argclip_,-1,2)));
    else
      out[0] = pow3(cos(bfr));
  }
  // compute Zernike polynomial, if a third child is given
  if( args.size() > 2 )
  {
    const std::vector<const Vells *> &zcoeff = args[2];
    // figure out radius of first null
    Vells rmax = M_PI/(2*bf_by_freq);
    // normalize l,m to rmax
    Vells l1 = l/rmax;
    Vells m1 = m/rmax;
    Vells phi = atan2(m1,l1);
    // r1 is normalized radius, r1clip is flag vells indicating where r1>=1
    Vells r1 = r/rmax;
    r1 = min(r1,1.0,VellsFullFlagMask,VellsFullFlagMask);
    Vells r1clip = r1.whereEq(1.0);
    // precompute powers of r1
    int max_n = nmk_from_j[zcoeff.size()-1][0];
    std::vector<Vells> r1_pow(max_n+1);
    r1_pow[0] = 1;
    for( int i=1; i<=max_n; i++ )
      r1_pow[i] = r1_pow[i-1]*r1;
    // Each radial polynomial R_k will be cached here
    std::vector<Vells> Rk_cache(NUM_RK);
    std::vector<bool> has_Rk(NUM_RK,false);
    // now compute every Zernike polynomial, and add them into the sum 'zsum'
    const std::vector<const Vells *> &zz = args[2];
    Vells zsum(0.);
    DMI::List::Ref zzrec(new DMI::List);
    for( uint j=0; j<zz.size(); j++ )
    {
      // lookup Zernike polynomial numbers
      int n = nmk_from_j[j][0];
      int m = nmk_from_j[j][1];
      int k = nmk_from_j[j][2];
      Vells &Rk = Rk_cache[k];
      // compute radial polynomial R_k, if not already computed
      if( !has_Rk[k] )
      {
        Rk = 0.;
        for( int i=0; i<=MAX_N; i++ )
        {
          int cc = rk_coeff[k][i];
          if( cc )
            Rk += r1_pow[i]*cc;
        }
        has_Rk[k] = true;
      }
      // compute Zernike polynomial itself, and add to sum
      Vells zpol = Rk*( m>=0 ? cos(m*phi) : sin(-m*phi) );
      zzrec().addBack(new Vells(zpol));
      zsum += (*zcoeff[j])*zpol;
    }
    // clip on r1>=1
    zsum.replaceFlaggedValues(r1clip,1.0);
    wstate()["$ZZ"] = zzrec;
    wstate()["$ZZsum"] = zsum;
    wstate()["$Zr1"] = r1;
    wstate()["$Zrmax"] = rmax;
    wstate()["$Zfq"] = freq_vells_;
    wstate()["$Zr1clip"] = r1clip;
    wstate()["$Zphi"] = phi;
    // done, multiply result
    out[0] *= zsum;
  }
}

} // namespace Meq

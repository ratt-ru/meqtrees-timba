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
#include <DMI/AID-DMI.h>
#include <DMI/List.h>
#include <casa/BasicSL/Constants.h>
#include <cmath>

namespace Meq {

using namespace VellsMath;

const HIID child_labels[] = { AidBF,AidR,AidE };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);


// commenting this out for now
// // Constants defining Zernike polynomials
// // highest n (in Z^m_n) supported
// const int MAX_N = 5;
// 
// // This determines the standard Noll numbering from a single integer j
// // to n,m,k giving the Zernike polynomial Z^m_n (see http://oeis.org/A176988)
// // with the radial polynomial R_k (see table below)
// // (The R_k numbering simply uses the R^m_n polynomials in order of increasing n,m)
// const int nmk_from_j[][3] =
// {
//      {0,0,0}, {1,1,1}, {1,-1,1}, {2,0,2}, {2,-2,3}, {2,2,3}, {3,-1,4}, {3,1,4}, {3,-3,5}, {3,3,5},
//      {4,0,6}, {4,2,7}, {4,-2,7}, {4,4,8}, {4,-4,8}, {5,1,9}, {5,-1,9}, {5,3,10}, {5,-3,10}, {5,5,11}
// };
// // this gives the coefficients of the first few radial polynomials per each k
// const int rk_coeff[][MAX_N+1] =
// {
//   {  1,  0,  0,  0,  0,  0},
//   {  0,  1,  0,  0,  0,  0},
//   { -1,  0,  2,  0,  0,  0},
//   {  0,  0,  1,  0,  0,  0},
//   {  0, -2,  0,  3,  0,  0},
//   {  0,  0,  0,  1,  0,  0},
//   {  1,  0, -6,  0,  6,  0},
//   {  0,  0, -3,  0,  4,  0},
//   {  0,  0,  0,  0,  1,  0},
//   {  0,  3,  0,-12,  0, 10},
//   {  0,  0,  0, -4,  0,  5},
//   {  0,  0,  0,  0,  0,  1},
// };
// // max number of Zernike polynomials supported
// const int MAX_NZ = sizeof(nmk_from_j)/(sizeof(int)*3);
// // highest K (in R_k) supported
// const int NUM_RK = sizeof(rk_coeff)/(sizeof(int)*(MAX_N+1));


WSRTCos3Beam::WSRTCos3Beam()
: TensorFunction(num_children,child_labels,num_children-1),
  clip_(100*(casa::C::pi/180))
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
  FailWhen( input_dims[0]->product()>1,"child '"+child_labels[0].toString()+"': single value expected");
  is_elliptical_ = ( input_dims.size()>2 );
  FailWhen( is_elliptical_ && input_dims[2]->product()!=2,"child '"+child_labels[2].toString()+"': 2-vector expected");
// commenting this out for now
  /*  // check Z child
  if( input_dims.size()>2 )
  {
    if( input_dims[2]->size() != 1 )
      Throw("child 2: single vector of Zernike coefficients expected");
    if( input_dims[2][0] > MAX_NZ )
      Throw(Debug::ssprintf("child 2: too many values, at most %d allowed",MAX_NZ));
//    if( input_dims[1]->product() != 2 )
//      Throw(Debug::ssprintf("child 1: 2-vector (l,m) expected, if child 3 (Zernike coefficients) is given"));
  }*/
  // check r child 
  const LoShape &rlm = *input_dims[1];
  FailWhen( rlm.size()>0 && ( rlm.size() > 2 || rlm[rlm.size()-1]>2 ),
           "child '"+child_labels[1].toString()+"': Nx2 or Nx1 or 2-vector (l,m) or single-value (r) expected");
  if( rlm.size() < 2 )
  {
    num_sources_ = 0;
    if( is_elliptical_ )
    {
      FailWhen( rlm.size() != 1 || rlm[0]!=2,
              "child '"+child_labels[1].toString()+"': Nx2 or 2-vector (l,m) expected, since ellipticity (child '"
              +child_labels[2].toString()+"') is supplied" );
      return LoShape(2,2);
    }
    else
      return LoShape(1);
  }
  else 
  {
    num_sources_ = rlm[0];
    if( is_elliptical_ )
    {
      FailWhen( rlm[rlm.size()-1]!=2,
              "child '"+child_labels[1].toString()+"': Nx2 or 2-vector (l,m) expected, since ellipticity (child '"
              +child_labels[1].toString()+"') is supplied" );
      return LoShape(num_sources_,2,2);
    }
    else
      return LoShape(num_sources_);
  }
}

// helper function, computes beam for a given cosine argument, applying clipping options
inline Vells WSRTCos3Beam::computeBeam (const Vells &bfr)
{
  // broken NEWSTAR-style clipping
  if( clip_ < 0 )
    return max(abs(pow3(cos(bfr))),-clip_,-1,2);
  // proper argument clipping
  else if( argclip_ > 0 )
    return pow3(cos(min(bfr,argclip_,-1,2)));
  else
    return pow3(cos(bfr));
}

void WSRTCos3Beam::evaluateTensors (std::vector<Vells> & out,
                                    const std::vector<std::vector<const Vells *> > &args )
{
  const Vells &bf = *(args[0][0]);
  Vells bf_by_freq = bf*freq_vells_;
  Vells exl,exm,eyl,eym;
  if( is_elliptical_ )
  {
    exl = 1/pow2(1+*args[2][0]);
    exm = 1/pow2(1-*args[2][0]);
    eyl = 1/pow2(1+*args[2][1]);
    eym = 1/pow2(1-*args[2][1]);
  }
  // old scalar version
  if( !num_sources_ )
  {
    if( is_elliptical_ )
    {
      Vells l2 = pow2(*args[1][0]);
      Vells m2 = pow2(*args[1][1]);
      wstate()["$exl"] = exl;
      wstate()["$eyl"] = eyl;
      wstate()["$l2"] = l2;
      wstate()["$m2"] = m2;
      wstate()["$l2a"] = l2*exl;
      wstate()["$l2b"] = l2*eyl;
      out[0]   = computeBeam(sqrt(l2*exl+m2*exm)*bf_by_freq);
      out[3]   = computeBeam(sqrt(l2*eyl+m2*eym)*bf_by_freq);
    }
    else
    {
      if( args[1].size() == 1 )
        out[0] = computeBeam(*args[1][0]*bf_by_freq);
      else if( args[1].size() == 2 )
        out[0] = computeBeam(sqrt(pow2(*args[1][0])+pow2(*args[1][1]))*bf_by_freq);
    }
  }
  // else tensor version
  else
  {
    for( int isrc=0; isrc<num_sources_; isrc++ )
    {
      // polarized elliptical beam
      if( is_elliptical_ )
      {
        Vells l2 = pow2(*args[1][isrc*2]);
        Vells m2 = pow2(*args[1][isrc*2+1]);
        out[isrc*4]   = computeBeam(sqrt(l2*exl+m2*exm)*bf_by_freq);
        out[isrc*4+3] = computeBeam(sqrt(l2*eyl+m2*eym)*bf_by_freq);
      }
      // unpolarized, circular beam
      else
      {
        Vells r;
        if( args[1].size() == num_sources_ )
          r = *args[1][isrc];
        else 
        {
          Vells l = *args[1][isrc*2];
          Vells m = *args[1][isrc*2+1];
          r = sqrt(l*l+m*m);
        }
        out[isrc] = computeBeam(r*bf_by_freq);
      }
    }
  }
}

} // namespace Meq

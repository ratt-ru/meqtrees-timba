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
#include <casa/BasicSL/Constants.h>
#include <cmath>

namespace Meq {

using namespace VellsMath;

const HIID child_labels[] = { AidBF,AidR };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

const HIID FDomain = AidDomain;

WSRTCos3Beam::WSRTCos3Beam()
: TensorFunction(num_children,child_labels),
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
}

void WSRTCos3Beam::evaluateTensors (std::vector<Vells> & out,
                                   const std::vector<std::vector<const Vells *> > &args )
{
  const Vells &bf = *(args[0][0]);
  Vells r;
  if( args[1].size() == 1 )
    r = *args[1][0];
  else if( args[1].size() == 2 )
  {
    const Vells &l = *args[1][0];
    const Vells &m = *args[1][1];
    r = sqrt(l*l+m*m);
  }
  Vells bfr = bf*r*freq_vells_;
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
    r = r*bf*freq_vells_;
    // broken NEWSTAR-style clipping
    if( clip_ < 0 )
      out[0] = max(abs(pow3(cos(bfr))),-clip_,-1,-1);
    // proper argument clipping
    else if( argclip_ > 0 )
      out[0] = pow3(cos(min(bfr,argclip_,-1,-1)));
    else
      out[0] = pow3(cos(bfr));
  }
}

} // namespace Meq

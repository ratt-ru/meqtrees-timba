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
: Function(num_children,child_labels),
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
}


//##ModelId=400E535502C4
Vells WSRTCos3Beam::evaluate (const Request &request,const LoShape &,
		   	      const vector<const Vells*>& values)
{
  // create frequency vells
  int nfreq = request.cells().ncells(Axis::FREQ);
  Vells freq(0,Axis::vectorShape(Axis::FREQ,nfreq),false);
  memcpy(freq.realStorage(),request.cells().center(Axis::FREQ).data(),nfreq*sizeof(double));
  
  const Vells & bf = *(values[0]);
  const Vells & r = *(values[1]);
  
  // broken NEWSTAR-style clipping
  if( clip_ < 0 )
    return max(abs(pow3(cos((bf*r)*freq))),-clip_,-1,-1);
  // proper argument clipping
  else
    return pow3(cos(min((bf*r)*freq,argclip_,-1,-1)));
}

} // namespace Meq

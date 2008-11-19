//# WSRTCos3Beam.h: computes a WSRT cos(BF*freq*r)**3 voltage beam factor from BF and r children.
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
//# $Id: WSRTCos3Beam.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQNODES_WSRTCOS3BEAM_H
#define MEQNODES_WSRTCOS3BEAM_H

//# Includes
#include <MEQ/Function.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::WSRTCos3Beam
#pragma aid BF R Clip

namespace Meq {    


//! This node implements two possible beam models:
//!   - a cos^3 model: cos(min(BF*r*freq,argclip))^3
//!   - a NEWSTAR-compatible model: max(abs(cos(BF*r*freq)^3),clip)
//! Note that the first model clips (i.e. makes flat) the beam outside a certain circle 
//! (determined by argclip), while the second model does not clip further-away regions where
//! the cos^3 argument goes above the clipping level again. The second model makes no
//! physical sense, but is currently implemented by NEWSTAR, and so is needed for compatibility.
//! 
//! BF and r are children:
//!   r=sqrt(l^2+m^2) usually (which is precise enough for WSRT fields)
//!   BF is the beam factor, in units of 1/Ghz. A good value for BF is 65*1e-9 (around 1.4 GHz at least)
//!
//! 'clip' is supplied in the state record. 
//! If state.clip>0, then the first model is used, with argclip=arccos(clip^(1/3))
//! If state.clip<0, then the second (NEWSTAR-compatible) model is used (with clip=-state.clip)
    
class WSRTCos3Beam: public Function
{
public:
  //! The default constructor.
  WSRTCos3Beam();

  virtual ~WSRTCos3Beam();

  virtual TypeId objectType() const
    { return TpMeqWSRTCos3Beam; }


protected:
  void setStateImpl (DMI::Record::Ref& rec, bool initializing);
  
  Vells evaluate (const Request &req,const LoShape &,
                  const vector<const Vells*>& values);


  double clip_;
  double argclip_;
};

} // namespace Meq

#endif

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
#include <MEQ/TensorFunction.h>

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
//! First child is BF, second child is either r, or a 2-vector of l,m, in which case r
//! is computed as sqrt(l^2+m^2) (which is precise enough for WSRT fields)
//! A third, optional, child 'Z' gives a vector of coefficients for Zernike polynomials
//! which are used to distort the beam.
//! For a Z of length N, the first N Zernike polynomials ZP_1...ZP_N are taken (following the Noll
//! numbering scheme), and the beam pattern within the main lobe is multipled by
//!             \sum_j{ ZP_j(l',m')*Z[j] }
//! where l',m' is normalized to unity at the first null (= pi/(2*BF*freq))
//!
//! BF is the beam factor, in units of 1/Ghz. A good value for BF is 65*1e-9 (around 1.4 GHz at least)
//!
//! 'clip' is supplied in the state record.
//! If state.clip>0, then the first model is used, with argclip=arccos(clip^(1/3))
//! If state.clip<0, then the second (NEWSTAR-compatible) model is used (with clip=-state.clip)
//! 'deriv'
//!   If true, then result is a 2-vector of dE/dl,dE/dm. If False, result is just the beam gain E.

class WSRTCos3Beam: public TensorFunction
{
public:
  //! The default constructor.
  WSRTCos3Beam();

  virtual ~WSRTCos3Beam();

  virtual TypeId objectType() const
    { return TpMeqWSRTCos3Beam; }


protected:
  void setStateImpl (DMI::Record::Ref& rec, bool initializing);

  // method required by TensorFunction
  // Returns cells of result.
  // This also computes the freq axis
  virtual void computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request);

  // method required by TensorFunction
  // Returns shape of result.
  // Also check child results for consistency
  virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);

  // method required by TensorFunction
  // Evaluates RADec for a given set of children values
  virtual void evaluateTensors (std::vector<Vells> & out,
                                const std::vector<std::vector<const Vells *> > &args );
        
  // helper functyion to compute cos^3 and apply clipping
  Vells computeBeam (const Vells &bfr);

  double clip_;
  double argclip_;

  Vells freq_vells_;

  // 0 if returning result for a single source
  // 1+ if returning tensor for multiple sources
  int num_sources_;
  // flag: beam has ellipticty (so is 2x2 matrix)
  bool is_elliptical_;
};

} // namespace Meq

#endif

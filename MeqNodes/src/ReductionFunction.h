//# ReductionFunction.h: abstract base for reduction funcs (min/max/mean/etc.)
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

#ifndef MEQNODES_REDUCTIONFUNCTION_H
#define MEQNODES_REDUCTIONFUNCTION_H
    
#include <MEQ/Function.h>
#include <MEQ/VellsSlicer.h>

#include <MeqNodes/TID-MeqNodes.h>

#pragma aid Reduction Axes

namespace Meq {    


class ReductionFunction : public Function
{
public:
  ReductionFunction (int nchildren=-1);

  bool hasReductionAxes () const
  { return !reduction_axes_.empty(); }

protected:
  // flags can be collapsed along the reduction axes
  virtual void evaluateFlags (Vells::Ref &,const Request &,const LoShape &,const vector<const VellSet*>&);
  
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  
  // does axis mapping before calling Function::getResult
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  // helper method: checks if a flag vells is fully flagged with a given mask,
  // returns mask itself if so, or 0 if at least one point is not flagged
  VellsFlagType isAllFlagged (const Vells &flagvells,VellsFlagType mask);

  // helper method: given an input Vells and the reduction_axes_ specified
  // below, creates an output Vells containing the non-reduction axes,
  // and a const VellsSlicer for the reduction axes.
  void makeVellsSlicer (Vells::Ref &out,ConstVellsSlicer0 &slicer,const Vells &invells);

  // helper method: given an input Vells and the reduction_axes_ specified
  // below, creates an output Vells containing the non-reduction axes,
  // and applies the given reduction function to every slice
  Vells apply (VellsMath::UnaryRdFunc func,const Vells &invells,VellsFlagType flagmask);
  
  // similar method for reduction functions that have an explicit result shape
  Vells apply (VellsMath::UnaryRdFuncWS func,const Vells &invells,const LoShape &shape,VellsFlagType flagmask);
      
  // if true, axes were specified as HIIDs, and will be mapped
  // to indices every getResult(). If false, indices are used.
  bool has_axes_ids_;
  
  // IDs of the reduction axes
  std::vector<HIID> reduction_axes_ids_;
  
  // indices of the reduction axes -- guaranteed to be filled in by the time
  // evaluate() is called
  std::vector<int> reduction_axes_;
};


} // namespace Meq

#endif

//# ReqMux.h: resamples result resolutions
//#
//# Copyright (C) 2003
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

#ifndef MEQ_REQMUX_H
#define MEQ_REQMUX_H
    
#include <MEQ/Node.h>
#include <MEQ/AID-Meq.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::ReqMux 
#pragma aid Integrate Oper Upsample Integrate Freq Time Pass Wait

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqReqMux
//  Resamples the Vells in its child's Result to the Cells of the parent's
//  Request. Current version ignores cell centers, sizes, domains, etc.,
//  and goes for a simple integrate/expand by an integer factor.
//field: integrate F
//  If True, then Vells are treated as integral values over a cell (i.e.,
//  when downsampling, values are integrated; when upsampling, values are 
//  divided). If False, then Vells are treated as samples at cell center 
//  (i.e., when downsampling, values are averaged; when upsampling, values 
//  are duplicated).
//field: flag_mask -1
//  Flag mask applied to child's result. -1 for all flags, 0 to ignore 
//  flags. Flagged values are ignored during integration.
//field: flag_bit 0
//  Flag bit(s) used to indicate flagged integrated results. If 0, then 
//  flag_mask&input_flags is used.
//field: flag_density 0.5
//  Critical ration of flagged/total pixels for integration. If this ratio
//  is exceeded, the integrated pixel is flagged.
//defrec end

namespace Meq {    

//##ModelId=400E530400A3
class ReqMux : public Node
{
public:
    //##ModelId=400E5355029C
  ReqMux();

    //##ModelId=400E5355029D
  virtual ~ReqMux();

  //##ModelId=400E5355029F
  virtual TypeId objectType() const
  { return TpMeqReqMux; }
  

protected:
  virtual void setStateImpl (DataRecord &rec,bool initializing);
    
  virtual int pollChildren (std::vector<Result::Ref> &child_results,
                            Result::Ref &resref,
                            const Request &req);

  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
private:
  // the OpSpec class specifies an operation that is applied to
  // every request
  class OpSpec
  {
    public:
      int   integrate[2];
      int   upsample[2];
      bool  resample;
      bool  wait;

      OpSpec()
      { 
        upsample[0]=upsample[1]=integrate[0]=integrate[1]=0; 
        resample=wait=false; 
      }
  };
  
  std::vector<OpSpec> ops_;
  int pass_child_;
  
  int res_depend_mask_;
  
};


} // namespace Meq

#endif

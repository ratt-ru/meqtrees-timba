//# ReqSeq.h: request sequencer
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

#ifndef MEQ_REQSEQ_H
#define MEQ_REQSEQ_H
    
#include <MEQ/Node.h>
#include <MEQ/AID-Meq.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::ReqSeq 
#pragma aid Cells Only

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqReqSeq
//  Forwards its request to all children in sequence (i.e. each child is  
//  activated only after the previous child has returned). Returns the result
//  of one designated child.
//field: result_index 1
//  Which child's result to return.
//defrec end

namespace Meq {    

//##ModelId=400E530400A3
class ReqSeq : public Node
{
public:
    //##ModelId=400E5355029C
  ReqSeq();

    //##ModelId=400E5355029D
  virtual ~ReqSeq();

  //##ModelId=400E5355029F
  virtual TypeId objectType() const
  { return TpMeqReqSeq; }
  

protected:
  virtual void setStateImpl (DataRecord &rec,bool initializing);
    
  virtual int pollChildren (std::vector<Result::Ref> &child_results,
                            Result::Ref &resref,
                            const Request &req);

  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
private:
  int which_result_;
  bool cells_only_;
  
  Result::Ref result_;
  int result_code_;
};


} // namespace Meq

#endif

//# ReqMux.h: resamples result resolutions
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
//# $Id$

#ifndef MEQNODES_REQMUX_H
#define MEQNODES_REQMUX_H
    
#include <MEQ/Node.h>
#include <MEQ/AID-Meq.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::ReqMux 

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqReqMux
//  Forwards its request to all children. Returns the result
//  of one designated child.
//field: result_index 1
//  Which child's result to return.
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
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  virtual int pollChildren (Result::Ref &resref,
                            std::vector<Result::Ref> &childres,
                            const Request &req);
    
  virtual int  getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
  virtual int  discoverSpids (Result::Ref &resref, 
                             const std::vector<Result::Ref> &childres,
                             const Request &req);
  
private:
  int which_result_;

};


} // namespace Meq

#endif

//# ZeroFlagger.h: a trivial flagger: flags ==0 or !=0
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

#ifndef MEQ_ZEROFLAGGER_H
#define MEQ_ZEROFLAGGER_H
    
#include <MEQ/Node.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MeqNodes/TID-MeqNodes.h>

#pragma aidgroup MeqNodes
#pragma types #Meq::ZeroFlagger 
#pragma aid Oper Flag Bit EQ NE LT GT LE GE

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqZeroFlagger
//  Sets flags in a VellSet based on a comparison of the main value with 0.
//field: oper hiid('ne')
//  logical operator to use (HIID or string). One of: EQ NE GE LE GT LT,
//  for == != >= <= < >. 
//field: flag_bit 1
//  this value is ORed with the flags at all points where the 
//  main value OPER 0 is true.
//defrec end

namespace Meq {    

const HIID FOper    = AidOper;
const HIID FFlagBit = AidFlag|AidBit;

//##ModelId=400E530400A3
class ZeroFlagger : public Node
{
public:
    //##ModelId=400E5355029C
  ZeroFlagger();

    //##ModelId=400E5355029D
  virtual ~ZeroFlagger();

  //##ModelId=400E5355029F
  virtual TypeId objectType() const
  { return TpMeqZeroFlagger; }

protected:
  //##ModelId=400E531402D1
  virtual void setStateImpl (DataRecord &rec,bool initializing);
    
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
private:
    
  int flagbit_;
  AtomicID oper_;
};


} // namespace Meq

#endif

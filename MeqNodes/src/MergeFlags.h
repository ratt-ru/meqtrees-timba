//# MergeFlags.h: a trivial flagger: flags ==0 or !=0
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

#ifndef MEQ_MERGEFLAGS_H
#define MEQ_MERGEFLAGS_H
    
#include <MEQ/Function.h>
#include <MEQ/AID-Meq.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::MergeFlags 
#pragma aid Flag Mask

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqMergeFlags
//  Merges (bitwise-ORs) the flags supplied by all its children.
//  The output result is a copy of the first child's input result, 
//  but all the flags are merged.
//field: flag_mask -1
//  Flag mask to apply during merge. -1 means full mask. This can
//  be a single mask, or a vector of one mask per child.
//defrec end

namespace Meq {    

//##ModelId=400E530400A3
class MergeFlags : public Function
{
public:
    //##ModelId=400E5355029C
  MergeFlags();

    //##ModelId=400E5355029D
  virtual ~MergeFlags();

  //##ModelId=400E5355029F
  virtual TypeId objectType() const
  { return TpMeqMergeFlags; }

protected:
    
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
};


} // namespace Meq

#endif

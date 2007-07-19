//# Paster.h: pastes child 2 into specified position of child 1 result
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

#ifndef MEQNODES_PASTER_H
#define MEQNODES_PASTER_H
    
#include <MEQ/Node.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes

#pragma types #Meq::Paster

#pragma aid Multi

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqPaster
//  A MeqPaster "pastes" the result of its second child (Result2) at the 
//  selected position in the result of the first child (Result1).
//field: index []
//  Index (1-based) of position(s) to paste at. If more than one index is
//  supplied, it is interpreted according to the 'multi' field below. Note
//  that the semantics of the selection match those of the MeqSelector node.
//field: multi F
//  If false (default): a multiple-element index is treated as a tensor index 
//    that selects a single element or a slice. Result1 must  be a tensor 
//    of the same rank as there are elements in 'index'. A '-1' at
//    any position in 'index' indicates a slice along the corresponding axis.
//    Result2 must have the same dimensions/rank as the selected slice.
//  If true: a multiple-element index is treated as a set of  scalar indices.
//    Result2 must have the same number of vellsets as there are elements in
//    'index', and they are pasted at the indicated positions.
//defrec end

namespace Meq {    


//##ModelId=400E53040077
class Paster : public Node
{
  public:
    //##ModelId=400E5355022C
    Paster ();
    //##ModelId=400E5355022D
    virtual ~Paster ();
    
    //##ModelId=400E5355022F
    virtual TypeId objectType() const
    { return TpMeqPaster; }
    
  protected:
    //##ModelId=400E53550233
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    //##ModelId=400E53550237
    virtual int getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &req,bool newreq);
  
  private:
    //##ModelId=400E5355022A
    vector<int> selection_;
  
    bool multi_;
};


} // namespace Meq

#endif

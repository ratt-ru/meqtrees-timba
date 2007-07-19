//# Selector.h: Selects result planes from a result set
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

#ifndef MEQNODES_SELECTOR_H
#define MEQNODES_SELECTOR_H
    
#include <MEQ/Node.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes

#pragma types #Meq::Selector

#pragma aid Multi

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqSelector
//  A MeqSelector selects one or more results from the result set of its child.
//  Must have exactly one child.
//field: index []
//  Index (1-based) of results to be selected. If more than one index is
//  supplied, it is interpreted according to the 'multi' field below.
//field: multi F
//  If false (default): a multiple-element index is treated as a tensor index 
//    that selects a single element or a slice. Child result must be a tensor 
//    of the same rank as there are elements in 'index'. A '-1' at
//    any position in 'index' indicates a slice along the corresponding axis.
//  If true: a multiple-element index is treated as a set of scalar indices, 
//    and the corresponding number of output vellsets is produced.
//defrec end

namespace Meq {    


//##ModelId=400E53040077
class Selector : public Node
{
  public:
    //##ModelId=400E5355022C
    Selector ();
    //##ModelId=400E5355022D
    virtual ~Selector ();
    
    //##ModelId=400E5355022F
    virtual TypeId objectType() const
    { return TpMeqSelector; }
    
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

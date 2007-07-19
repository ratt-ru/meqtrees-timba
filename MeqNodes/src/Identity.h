//# Identity.h: Selects result planes from a result set
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

#ifndef MEQNODES_IDENTITY_H
#define MEQNODES_IDENTITY_H
    
#include <MEQ/Node.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes

#pragma types #Meq::Identity

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqIdentity
//  A MeqIdentity node simply returns its child result.
//  Must have exactly one child.
//defrec end

namespace Meq {    


//##ModelId=400E53040077
class Identity : public Node
{
  public:
    //##ModelId=400E5355022C
    Identity ();
    //##ModelId=400E5355022D
    virtual ~Identity ();
    
    //##ModelId=400E5355022F
    virtual TypeId objectType() const
    { return TpMeqIdentity; }
    
  protected:
    //##ModelId=400E53550237
    virtual int getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &req,bool newreq);
};


} // namespace Meq

#endif

//# Composer.h: Selects result planes from a result set
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

#ifndef MEQ_COMPOSER_H
#define MEQ_COMPOSER_H
    
#include <MEQ/Node.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Composer

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqComposer
//  A MeqComposer concatenates the results of all its children 
//  into a single result.
//field: contagious_fail F
//  If true, then a fail in any child result causes the composer to generate
//  a complete fail -- i.e., a result composed entirely of fails.
//  If false (default), then fail vellsets from children are collected and 
//  passed along with valid vellsets.
//defrec end

namespace Meq {    


//##ModelId=400E53030268
class Composer : public Node
{
  public:
    //##ModelId=400E53050042
    Composer ();
    //##ModelId=400E53050043
    virtual ~Composer ();

    //##ModelId=400E53050045
    virtual TypeId objectType() const
    { return TpMeqComposer; }
    
  protected:
//    //##ModelId=400E53050047
//    virtual void checkInitState (DataRecord &rec);
      
    //##ModelId=400E5305004A
    virtual void setStateImpl (DataRecord &rec,bool initializing);
    // Get the result for the given request.
    //##ModelId=400E5305004F
    virtual int getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &req,bool newreq);
  
  private:
    //##ModelId=400E53050040
    bool contagious_fail;
};


} // namespace Meq

#endif

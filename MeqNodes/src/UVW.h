//# UVW.h: Calculate station UVW from station position and phase center
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

#ifndef MEQ_UVW_H
#define MEQ_UVW_H
    
#include <MEQ/Function.h>
#include <measures/Measures/MPosition.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::UVW
#pragma aid RA Dec X Y Z

namespace Meq {    


//##ModelId=400E530400BD
class UVW : public Function
{
public:
    //##ModelId=400E535502D1
  UVW();

    //##ModelId=400E535502D2
  virtual ~UVW();

    //##ModelId=400E535502D4
  virtual TypeId objectType() const
    { return TpMeqUVW; }

  // Get the result for the given request.
    //##ModelId=400E535502D6
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

private:
//    //##ModelId=400E535502D0
//  MPosition itsEarthPos;
//    get this from children instead!
};

} // namespace Meq

#endif

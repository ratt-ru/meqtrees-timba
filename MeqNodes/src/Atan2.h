//# Atan2.h: return arctan of y/x
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
//# $Id: Atan2.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQNODES_ATAN2_H
#define MEQNODES_ATAN2_H
    
#include <MEQ/Function.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Atan2

namespace Meq {    


//##ModelId=400E53030294
class Atan2 : public Function2
{
public:
    //##ModelId=400E530500D3
  Atan2();

    //##ModelId=400E530500D4
  virtual ~Atan2();

    //##ModelId=400E530500D6
    virtual TypeId objectType() const
    { return TpMeqAtan2; }

  // Evaluate the value for the given request.
    //##ModelId=400E530500D8
  virtual Vells evaluate (const Request&,const LoShape &,
			  const vector<const Vells*>& values);
};


} // namespace Meq

#endif

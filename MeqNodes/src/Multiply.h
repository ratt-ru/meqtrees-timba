//# Multiply.h: Multiply 2 or more nodes
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

#ifndef MEQ_MULTIPLY_H
#define MEQ_MULTIPLY_H
    
#include <MEQ/Function.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Multiply

namespace Meq {    


//##ModelId=400E530302E4
class Multiply : public Function
{
public:
    //##ModelId=400E530A0105
  Multiply();

    //##ModelId=400E530A0106
  virtual ~Multiply();

    //##ModelId=400E530A0108
  virtual TypeId objectType() const
    { return TpMeqMultiply; }

  // Evaluate the value for the given request.
    //##ModelId=400E530A010A
  virtual Vells evaluate (const Request&, const LoShape&,
			  const vector<const Vells*>& values);
};


} // namespace Meq

#endif

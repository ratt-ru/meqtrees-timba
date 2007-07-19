//# MatrixInvert22.cc: quick invert of 2x2 matrix
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

#ifndef MEQNODES_MATRIXINVERT22_H
#define MEQNODES_MATRIXINVERT22_H 1
    
#include <MEQ/Function.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::MatrixInvert22

namespace Meq {    


//##ModelId=400E530302E4
class MatrixInvert22 : public Function
{
public:
    //##ModelId=400E530A0105
  MatrixInvert22();

    //##ModelId=400E530A0106
  virtual ~MatrixInvert22();

    //##ModelId=400E530A0108
  virtual TypeId objectType() const
    { return TpMeqMatrixInvert22; }
  
protected:
  int getResult (Result::Ref &resref,
                 const std::vector<Result::Ref> &childres,
                 const Request &request,bool);

  // helper function computes invert
  // changed is true whenever the input value has changed from the last call
  void computeInvert (Vells::Ref out[],const std::vector<const Vells*> &in,
                      const std::vector<bool> &changed);
  
  // cached intermediate values
  Vells ad_;
  Vells bc_;
};


} // namespace Meq

#endif

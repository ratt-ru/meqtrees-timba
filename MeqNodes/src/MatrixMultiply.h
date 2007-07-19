//# MatrixMultiply.cc: Multiply 2 or more matrix results
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

#ifndef MEQNODES_MATRIXMULTIPLY_H
#define MEQNODES_MATRIXMULTIPLY_H
    
#include <MEQ/Function.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::MatrixMultiply

namespace Meq {    


//##ModelId=400E530302E4
class MatrixMultiply : public Function
{
public:
    //##ModelId=400E530A0105
  MatrixMultiply();

    //##ModelId=400E530A0106
  virtual ~MatrixMultiply();

    //##ModelId=400E530A0108
  virtual TypeId objectType() const
    { return TpMeqMatrixMultiply; }
  
protected:
  int getResult (Result::Ref &resref,
                 const std::vector<Result::Ref> &childres,
                 const Request &request,bool);

  // helper functions

  // multiplies a scalar child by a tensor child
  void scalarMultiply (Result::Ref &res,const Result &scalar,const Result &tensor,
                       VellsFlagType fms,VellsFlagType fmt,
                       bool integrated,int tensor_ich);

  
};

} // namespace Meq

#endif

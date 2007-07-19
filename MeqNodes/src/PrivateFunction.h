//# PrivateFunction.h: Private function on vells
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
//# $Id: PrivateFunction.h,v 1.4 2005/02/06 16:21:41 smirnov Exp $

#ifndef MEQ_PRIVATEFUNCTION_H
#define MEQ_PRIVATEFUNCTION_H

#include <MEQ/Function.h>
#include <MeqNodes/TID-MeqNodes.h>
#include <MEQ/Vells.h>
#include <MEQ/Cells.h>
#include <MEQ/Axis.h>
#include <MEQ/Request.h>
#include <dlfcn.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::PrivateFunction

namespace Meq {    

  const HIID
    // PrivateFunction staterec fields
    FLibName        = AidLib|AidName,
    FFunctionName   = AidFunction|AidName;
  
//##ModelId=3F86886E0162
class PrivateFunction : public Function
{
public:
    //##ModelId=3F86886E028F
  PrivateFunction();

    //##ModelId=3F86886E0293
  virtual ~PrivateFunction();

    //##ModelId=400E5304032A
  virtual TypeId objectType() const
    { return TpMeqPrivateFunction; }

  // Evaluate the value for the given request.
    //##ModelId=400E53040332
  virtual Vells evaluate (const Request&, const LoShape&,
			  const vector<const Vells*>& values);

protected:
  // sets up state from state record
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

 private:
  Vells (*pt2Func)(const vector<const Vells *> &par,const Vells* x) ;//function pointer
  double (*pt2doubleFunc)(const double *par,const double* x) ;//function pointer
  dcomplex (*pt2complexFunc)(const dcomplex *par,const dcomplex* x) ;//function pointer
  int Npar;
  int Nx;
  void init_functions(const string &lib_name, const string &function_name);
  void *handle ; //handle to shared library;
  Vells evaluateDouble(const std::vector<Vells::Ref>  &grid,const std::vector<Vells::Ref>  &values,const Vells::Shape &outshape,const Vells::Strides * strides);
  Vells evaluateComplex(const std::vector<Vells::Ref>  &grid,const std::vector<Vells::Ref>  &values,const Vells::Shape &outshape,const Vells::Strides * strides);

};


} // namespace Meq

#endif

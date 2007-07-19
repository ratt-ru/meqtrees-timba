//# Functional.h: Calculates result from string (see Aips++ CompiledFunction) 
//# describing function. Paramters in the string are given by the children.
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
//# $Id:

#ifndef MEQNODES_FUNCTIONAL_H
#define MEQNODES_FUNCTIONAL_H
    
#include <MEQ/TensorFunction.h>
#include <MEQ/Vells.h>
#include <scimath/Functionals/CompiledFunction.h>
#include <scimath/Functionals.h>
#include <MEQ/MeqVocabulary.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Functional

namespace Meq {    
  const HIID
    // Functional staterec fields
    FChildMap        = AidChild|AidMap;
  const int MaxNrDims=100;
class Functional : public TensorFunction
{
public:
  Functional();

  virtual ~Functional();

  virtual TypeId objectType() const
    { return TpMeqFunctional; }
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  

protected:
  // method required by TensorFunction
  // Returns shape of result.
  // Also check child results for consistency
  virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);
    
  // method required by TensorFunction
  // Evaluates Functional for a given set of children values
  virtual void evaluateTensors (std::vector<Vells> & out,   
       const std::vector<std::vector<const Vells *> > &args );

  void setFunction(const string &funcstring);
  void fill_complex_xval(std::vector<Vells> & out,const std::vector<Vells::Ref>  &args,const Vells::Shape &outshape,const Vells::Strides * strides_);
  void fill_double_xval(std::vector<Vells> & out,const std::vector<Vells::Ref>  &args,const Vells::Shape &outshape,const Vells::Strides * strides_);
  void map_parameters(int, int, const std::vector<int> & );

  casa::CompiledFunction<casa::DComplex> * itsComplexFunction;
  casa::CompiledFunction<double> * itsRealFunction;
  int Ndim_,Ninput_;
  string function_string_;
  std::vector<LoShape> shapes_;
  int MaxN_[MaxNrDims][MaxNrDims],Ndims_[MaxNrDims];
  std::vector<int> childnr_;
  std::vector<std::vector<int> > vellsnr_;
};

} // namespace Meq

#endif

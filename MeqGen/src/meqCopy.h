//# meqCopy.h: 
//# MeqExpr node class, automatically generated from Glish
//#
//# Copyright  (C)  2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2,  7990 AA Dwingeloo, The Netherlands,  seg@astron.nl
//# 
//# $Id$: 

#ifndef MEQ_meqCopy_H
#define MEQ_meqCopy_H
    
#include <MEQ/Function.h>
#include <MeqGen/TID-MeqGen.h>

#pragma aidgroup MeqGen
#pragma types #meq::Copy


namespace meq {

  using namespace Meq;

  class Copy : public Function
  {

    public:

      Copy();

      virtual ~Copy();
      
      virtual TypeId objectType () const { return TpmeqCopy; }

      virtual void evaluateVells (Vells& result, const Request&, const vector<const Vells*>& values);


    private:

  };

} // namespace meq

#endif

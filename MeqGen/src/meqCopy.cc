//# meqCopy.cc: 
//# MeqExpr node class, automatically generated from Glish
//#
//# Copyright  (C)  2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2,  7990 AA Dwingeloo, The Netherlands,  seg@astron.nl
//# 
//# $Id$: 

#include "meqCopy.h"
#include <MEQ/Vells.h>
#include <Common/Debug.h>

#define   meqFlagger        *(values[0])



using namespace Meq::VellsMath;


namespace meq {

  Copy::Copy()
  {}

  Copy::~Copy()
  {}

  void Copy::evaluateVells (Vells& result, const Request&, const vector<const Vells*>& values)
  {
    result = ( meqFlagger );
  }


} // namespace meq


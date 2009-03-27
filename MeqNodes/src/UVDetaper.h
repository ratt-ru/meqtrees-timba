//# UVDetaper.h:  Detaper an image 
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
//# $Id: UVDetaper.h 5418 2009-02-20  fba $

#ifndef MEQNODES_UVDETAPER_H
#define MEQNODES_UVDETAPER_H
    
#include <MEQ/Function.h>

#include <casa/BasicSL/Constants.h>
#include <scimath/Mathematics/MathFunc.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::UVDetaper

//#pragma aids UVDetaper_method


namespace Meq {    

class UVDetaper : public Function1 {
 private:
  //int _method;
  Vells::Ref CorrVells;
  int weightsparam;
  int cutoffparam;

  //protected:
  //virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  
 public:
  UVDetaper();
  virtual ~UVDetaper();
  virtual TypeId objectType() const
    { return TpMeqUVDetaper; }
  
  // Evaluate the value for the given request.
  virtual Vells evaluate (const Request&,const LoShape &,
			  const vector<const Vells*>& values);
  int getResult (Result::Ref &resref,
		 const std::vector<Result::Ref> &child_results,
		 const Request &request, bool newreq);
  static int sphfn(int *ialf, int *im, int *iflag, float *eta, 
		   float *psi, int *ierr);
  static float sphfn(int ialf, int im, int flag, float eta);
};
 
 
} // namespace Meq

#endif

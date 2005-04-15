//# UVInterpol.h: Parameter with polynomial coefficients
//#
//# Copyright (C) 2002
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

#ifndef MEQNODES_UVINTERPOL_H
#define MEQNODES_UVINTERPOL_H

//# Includes
#include <MEQ/Node.h>
//#include <MeqNodes/ReductionFunction.h>


#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::UVInterpol
#pragma aids UVInterpol Map Count Additional Info

namespace Meq {


class UVInterpol: public Node
	       //class UVInterpol: public ReductionFunction
{
public:
  // The default constructor.
  // The object should be filled by the init method.
  UVInterpol();

  virtual ~UVInterpol();

  virtual TypeId objectType() const
  { return TpMeqUVInterpol; }

  /*
// Evaluate the value for the given request.
  virtual Vells evaluate (const Request&,const LoShape &,
			  const vector<const Vells*>& values);
  */

  // Get the requested result of the Node.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  
 protected:

  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

 private:

  bool _additional_info;  

  void UVInterpol::fillVells(const std::vector<Result::Ref> &fchildres, 
			     Vells &fvells, const Cells &fcells);

  bool UVInterpol::line(double u1, double v1, double u2, double v2, double u3, double v3, double u4, double v4);

  bool UVInterpol::arc(double u1, double v1, double u2, double v2, double u3, double v3, double u4, double v4);

  void UVInterpol::fillVells2(const std::vector<Result::Ref> &fchildres, 
			      Vells &fvells1, Vells &fvells2, const Cells &fcells);
   
};


} // namespace Meq

#endif

//# TFSmearFactor.h: apply bandwidth/time smearing
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
//# $Id: TFSmearFactor.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQNODES_TFSMEAR_H
#define MEQNODES_TFSMEAR_H
    
#include <MEQ/Function.h>

#include <MeqNodes/AID-MeqNodes.h>
#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::TFSmearFactor

namespace Meq {    


//##ModelId=400E530400A3
class TFSmearFactor : public Function
{
public:
    //##ModelId=400E5355029C
  TFSmearFactor();

    //##ModelId=400E5355029D
  virtual ~TFSmearFactor();

    //##ModelId=400E5355029F
    virtual TypeId objectType() const
    { return TpMeqTFSmearFactor; }

  // Evaluate the value for the given request.
    //##ModelId=400E535502A1
  virtual Vells evaluate (const Request&,const LoShape &,
			  const vector<const Vells*>& values);

protected:
  void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  bool is_modulo_;
  double modulo_;
  double phase_factor_;
};


} // namespace Meq

#endif

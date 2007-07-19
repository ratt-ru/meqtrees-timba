//# WMean.h: Weighted sum of 2 or more nodes, weights normalized
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

#ifndef MEQNODES_WAVG_H
#define MEQNODES_WAVG_H
    
#include <MeqNodes/WSum.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::WMean

namespace Meq {    


//##ModelId=3F86886E0162
class WMean : public WSum
{
public:
    //##ModelId=3F86886E028F ??
  WMean();

    //##ModelId=3F86886E0293??
  virtual ~WMean();

    //##ModelId=400E5304032A??
  virtual TypeId objectType() const
    { return TpMeqWMean; }

 protected:


  virtual Vells evaluate (const Request&, const LoShape&,
                          const vector<const Vells*>& values);
 private:
  //normalize weightsvector
  void NormWeights();

};


} // namespace Meq

#endif

//# StatPointSourceDFT.h: The point source DFT component for a station
//#
//# Copyright (C) 2004
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

#ifndef MEQ_STATPOINTSOURCEDFT_H
#define MEQ_STATPOINTSOURCEDFT_H

//# Includes
#include <MEQ/CompoundFunction.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::StatPointSourceDFT
#pragma aid LMN UVW

namespace Meq {    

class StatPointSourceDFT: public CompoundFunction
{
public:
  // The default constructor.
  StatPointSourceDFT();

  virtual ~StatPointSourceDFT();

  virtual TypeId objectType() const
    { return TpMeqStatPointSourceDFT; }

  // Get the result for the given request.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

protected:
  virtual void evalResult (std::vector<Vells> &res,
          const std::vector<const Vells*> &values,
          const Cells &);
};

} // namespace Meq

#endif

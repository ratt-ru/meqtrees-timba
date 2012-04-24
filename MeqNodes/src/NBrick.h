//# NBrick.h: computes the n coordinate corresponding to an FFT or image brick
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
//# $Id: NBrick.h 6895 2009-04-02 15:56:26Z oms $

#ifndef MEQNODES_NBRICK_H
#define MEQNODES_NBRICK_H

//# Includes
#include <MEQ/Node.h>

#include <MeqNodes/TID-MeqNodes.h>
#include <MeqNodes/AID-MeqNodes.h>

#pragma aidgroup MeqNodes
#pragma types #Meq::NBrick

namespace Meq {
  
class NBrick: public Node
  // An NBrick computes the per-pixel N coordinate associated with every 
  {
  public:
    // The default constructor.
    // The object should be filled by the init method.
    NBrick();
    virtual ~NBrick();
    virtual TypeId objectType() const
    { return TpMeqNBrick; }
    
    // Get the requested result of the Node.
    virtual int getResult (Result::Ref &resref, 
			   const std::vector<Result::Ref> &childres,
			   const Request &req,bool newreq);
  
  protected:
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  
  private:
    // which 2 axes are treated as an input plane?
    std::vector<HIID> _in_axis_id;
    
  };
} // namespace Meq

#endif

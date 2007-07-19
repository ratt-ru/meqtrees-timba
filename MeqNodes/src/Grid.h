//# Grid.h: Give the values along specified grid axis
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

#ifndef MEQNODES_GRID_H
#define MEQNODES_GRID_H
    
#include <MEQ/Node.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Grid

namespace Meq {    


//##ModelId=400E530400AB
class Grid : public Node
{
public:
    //##ModelId=400E535502AC
  Grid();
    //##ModelId=400E535502AD
  virtual ~Grid();
  
    //##ModelId=400E535502B3
  virtual TypeId objectType() const
  { return TpMeqGrid; }

protected:
  // Evaluate the value for the given request.
    //##ModelId=400E535502B5
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  
  // if not empty, axis was specified as HIID, and will be mapped
  // to index at every getResult(). If false, idirect index is used.
  HIID axis_id_;
  
  int axis_index_;
};

} // namespace Meq

#endif

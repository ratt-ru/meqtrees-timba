//# CoordTransform.h: modifies request resolutions
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
//# $Id: CoordTransform.h 4624 2007-01-24 10:54:27Z sarod $

#ifndef MEQNODES_COORDTRANSFORM_H
#define MEQNODES_COORDTRANSFORM_H
    
#include <MEQ/Node.h>
#include <MEQ/Cells.h>
#include <MEQ/VellSet.h>
#include <MEQ/AID-Meq.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::CoordTransform 

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqCoordTransform
//  Child 0: defines the grid for interpolation
//  Child 1: defines the function for interpolation
//  This nodes interpolates the result returned by child 1 according
//  to the gride defined by child 0.
//
//field: mode
//  mode 1 (sequential): passes the original requser to child 0, recreates a requset for child 1 according to the result returned by child 0.
//  mode 2 (parallel): passes the same requset to both children (not yet implemented)
//  mode 3 (simple): only handle 2D results in Time,Freq
//field: common_axes []
//  a vector which gives the axes returned by the grid child that is given to the function. Axes names can be characters like 'L','M' etc
//field:  default_cell_size: when the first child returns just a scalar, it is impossible to create a grid wirh proper cell sizes to send to the second child. So use this value to create the grid.
//defrec end

namespace Meq {   
  const HIID
    // CoordTransform staterec fields
    FAxis        = AidAxis;

class CoordTransform : public Node
{
public:
  CoordTransform();

  virtual ~CoordTransform();

  virtual TypeId objectType() const
  { return TpMeqCoordTransform; }


protected:
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  virtual int pollChildren (Result::Ref &resref,
                            std::vector<Result::Ref> &childres,
                            const Request &req);
    
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
private:

  
  const bool checkResult(blitz::Array<double,1> & , blitz::Array<double,1> &);
 //for caching result in pollChildren()
  Result::Ref result_;
  int result_code_;
  vector<HIID>    res_symdeps_;
  int             res_depmask_;
  vector<HIID>    seq_symdeps_;
  int             seq_depmask_;
  vector<HIID>    dom_symdeps_;
  int             dom_depmask_;
  int n_axis_;

};


} // namespace Meq


#endif

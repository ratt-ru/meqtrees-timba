//# DataCollect.h: Class to visualize data
//#
//# Copyright (C) 2003
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

#ifndef MEQ_DATACOLLECT_H
#define MEQ_DATACOLLECT_H
    
#include <MEQ/Node.h>
#include <MEQ/VellSet.h>
#include <MeqNodes/TID-MeqNodes.h>

#pragma types #Meq::DataCollect
#pragma aid Top Label Attrib Plot Data Color Style Size Profile Visu XX XY YX YY

namespace Meq {

class Request;


class DataCollect : public Node
{
public:

  DataCollect();
    
  virtual ~DataCollect();

  virtual TypeId objectType () const { return TpMeqDataCollect; }

protected:
  //## override this, since we poll children ourselves
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  virtual void setStateImpl (DataRecord &rec,bool initializing);
  
  //##Documentation

  HIID top_label_;
  
  ObjRef attrib_;
  DataField::Ref labels_;
};


} // namespace Meq

#endif

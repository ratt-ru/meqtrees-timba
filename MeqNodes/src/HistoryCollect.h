//# HistoryCollect.h: Class to visualize data
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

#ifndef MEQNODES_HISTORYCOLLECT_H
#define MEQNODES_HISTORYCOLLECT_H
    
#include <MEQ/Node.h>
#include <MEQ/VellSet.h>
#include <MeqNodes/TID-MeqNodes.h>

#pragma types #Meq::HistoryCollect
#pragma aid History Input Index List Max Size Verbose Get Error Clear

namespace Meq {

class Request;


class HistoryCollect : public Node
{
public:

  HistoryCollect();
    
  virtual ~HistoryCollect();

  virtual TypeId objectType () const { return TpMeqHistoryCollect; }

protected:
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  
  virtual int  processCommands (Result::Ref &resref,const DMI::Record &rec,const Request &req);
  
  void fillResult (Result::Ref &resref,const DMI::List &list);
  
  //##Documentation
  // top-level label in output 
  HIID top_label_;
  // index of input result
  HIID input_index_;
  // maximum list size
  int max_size_;
  // verbosity: if False, then history list is only returned
  // when requested. If True, it is attached to every result.
  bool verbose_;
  
  // temporary verbosity flag used when a Get.History command is issued 
  bool temp_verbose_;
  // temporary clear-history flag used when a Clear.History command is issued 
  bool temp_clear_;
  
};


} // namespace Meq

#endif

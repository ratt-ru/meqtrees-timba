//# Request.h: The request for an evaluation of an expression
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

#ifndef MEQ_REQUEST_H
#define MEQ_REQUEST_H

//# Includes
#include <MEQ/Cells.h>
#include <DMI/Record.h>

#pragma aidgroup Meq
#pragma types #Meq::Request
#pragma aid Reexecute

// This class represents a request for which an expression has to be
// evaluated. It contains the domain and cells to evaluate for.
// A flag tells if derivatives (perturbed values) have to be calculated.

namespace Meq { using namespace DMI;

class Node;

//##ModelId=3F86886E01FF
class Request : public DMI::Record
{
public:
  typedef enum 
  {
    DISCOVER_SPIDS = -1,
    GET_RESULT     = 0,
    DERIV_SINGLE   = 1,
    DERIV_DOUBLE   = 2
  } EvaluationMode;
    
    //##ModelId=400E53040057
  typedef CountedRef<Request> Ref;
    
    //##ModelId=3F8688700056
  Request ();
    
    //##ModelId=3F8688700061
  //##Documentation
  //## Construct from DMI::Record 
  Request (const DMI::Record &other,int flags=0,int depth=0);
  
    //##ModelId=400E535403DD
  //##Documentation
  //## Create the request from the cells for which the expression has
  //## to be evaluated. 
  explicit Request (const Cells &, int evmode = DERIV_SINGLE, const HIID &id=HIID(),int cellflags=DMI::AUTOCLONE);
  
    //##ModelId=400E53550016
  explicit Request (const Cells *, int evmode = DERIV_SINGLE, const HIID &id=HIID(),int cellflags=0);

    //##ModelId=400E53550034
  virtual TypeId objectType () const
  { return TpMeqRequest; }
  
    //##ModelId=400E53550038
   //##Documentation
   //## implement standard clone method via copy constructor
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Request(*this,flags,depth); }
  
    //##ModelId=400E53550049
  //##Documentation
  //## validate record contents and setup shortcuts to them. This is called 
  //## automatically whenever a Request is made from a DMI::Record
  //## (or when the underlying DMI::Record is privatized, etc.)
  virtual void validateContent (bool recursive);
  
    //##ModelId=3F868870006C
  //##Documentation
  //## Evaluation mode (only makes sense if Cells are attached).
  //## See enum EvluationMode above for details
  int evalMode () const
  { return eval_mode_; }
  
  void setEvalMode (int em);
  
  //## Service flag. Requests with a service flag bypass the normal cache.
  //## Used for requests that manage tree state, etc.
  bool serviceFlag () const
  { return service_flag_; }

  void setServiceFlag (bool flag=true);
  
    //##ModelId=3F868870006E
  //##Documentation
  // Attaches cells object (default as anon). 
  void setCells (const Cells *,int flags=0);
    //##ModelId=400E53550065
  //##Documentation
  //## Attaches cells object 
  void setCells (const Cells &cells,int flags=DMI::AUTOCLONE)
  { setCells(&cells,flags); }
  
    //##ModelId=400E53550076
  //##Documentation
  //## true if a cells object is attached
  bool hasCells () const
  { return pcells_; }
    //##ModelId=3F8688700073
  //##Documentation
  //## Returns cells
  const Cells& cells() const
  { DbgFailWhen(!pcells_,"no cells in Meq::Request");
    return pcells_->deref(); }
  
    //##ModelId=3F8688700075
  //##Documentation
  //## Set the request id.
  void setId (const HIID &id);

  //##ModelId=400E5355007E
  //##Documentation
  //## Get the request id.
  const HIID & id() const
  { return id_; }
  
  //## Set the next-request hint
  void setNextId (const HIID &id);

  //##ModelId=400E5355007E
  //##Documentation
  //## Get the request id.
  const HIID & nextId() const
  { return next_id_; }
  
  //##Documentation
  //## does this request have a rider field?
  bool hasRider () const
  { return has_rider_; }
  
  //## copies over rider from another request
  void copyRider (const Request &other);
  
  //## clears rider
  void clearRider ();

  //##Documentation
  //## re-checks elf_ for a rider record, sets the has_rider_ flag.
  //## should be called after an app has changed the rider
  void validateRider ();
  
private: 
  Record::protectField;  
  Record::unprotectField;  
  Record::begin;  
  Record::end;  
  Record::as;
  Record::clear;
  
    //##ModelId=400E535403B3
  HIID   id_;
  HIID   next_id_;
    //##ModelId=3F86BFF80269
  Cells::Ref * pcells_;
    //##ModelId=3F868870003C
  int    eval_mode_;
  
  bool   has_rider_;
  
  bool   service_flag_;
};


} // namespace Meq

#endif

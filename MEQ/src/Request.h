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
#include <DMI/DataRecord.h>

#pragma aidgroup Meq
#pragma types #Meq::Request

// This class represents a request for which an expression has to be
// evaluated. It contains the domain and cells to evaluate for.
// A flag tells if derivatives (perturbed values) have to be calculated.

namespace Meq {

class Node;

//##ModelId=3F86886E01FF
class Request : public DataRecord
{
public:
    //##ModelId=400E53040057
  typedef CountedRef<Request> Ref;
    
    //##ModelId=3F8688700056
  Request ();
    
    //##ModelId=3F8688700061
  //##Documentation
  //## Construct from DataRecord 
  Request (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  
    //##ModelId=400E535403DD
  //##Documentation
  //## Create the request from the cells for which the expression has
  //## to be calculated. Optionally no derivatives are calculated.
  explicit Request (const Cells&, int calcDeriv=1, const HIID &id=HIID(),int cellflags=DMI::EXTERNAL|DMI::NONSTRICT);
  
    //##ModelId=400E53550016
  explicit Request (const Cells *, int calcDeriv=1, const HIID &id=HIID(),int cellflags=DMI::ANON|DMI::NONSTRICT);

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
  //## automatically whenever a Request is made from a DataRecord
  //## (or when the underlying DataRecord is privatized, etc.)
  virtual void validateContent ();
  
    //##ModelId=400E5355004C
  virtual int remove (const HIID &);
  
    //##ModelId=3F868870006C
  //##Documentation
  //## Calculate derivatives? 0 for none, 1 for standard, 2 for double-deriv
  int calcDeriv() const
  { return calcDeriv_; }
  
  void setCalcDeriv (int calc);

    //##ModelId=3F868870006E
  //##Documentation
  // Attaches cells object (default as anon). Can also specify DMI::CLONE
  // to copy
  void setCells (const Cells *,int flags = DMI::ANON|DMI::NONSTRICT);
    //##ModelId=400E53550065
  //##Documentation
  //## Attaches cells object (default is external). 
  void setCells (const Cells &cells,int flags = DMI::EXTERNAL|DMI::NONSTRICT)
  { setCells(&cells,flags); }
    //##ModelId=400E53550076
  //##Documentation
  //## True if a cells object is attached
  bool hasCells () const
  { return cells_; }
    //##ModelId=3F8688700073
  //##Documentation
  //## Returns cells
  const Cells& cells() const
  { DbgFailWhen(!cells_,"no cells in Meq::Request");
    return *cells_; }
  
    //##ModelId=3F8688700075
  //##Documentation
  //## Set the request id.
  void setId (const HIID &id);

  //##ModelId=400E5355007E
  //##Documentation
  //## Get the request id.
  const HIID & id() const
  { return id_; }
  
  //##Documentation
  //## does this request have a rider field?
  bool hasRider () const
  { return hasRider_; }

  //##Documentation
  //## re-checks elf_ for a rider record, sets the hasRider flag.
  //## should be called after an app has changed the rider
  void validateRider ();
    
protected: 
    //##ModelId=400E5354039C
  //##Documentation
  //## disable public access to some DataRecord methods that would violate the
  //## structure of the container
  DataRecord::remove;
    //##ModelId=400E535403A4
  DataRecord::replace;
    //##ModelId=400E535403AB
  DataRecord::removeField;
  
private:
    //##ModelId=400E535403B3
  HIID   id_;
    //##ModelId=3F868870003C
  int    calcDeriv_;
    //##ModelId=3F86BFF80269
  const  Cells* cells_;
  
  bool   hasRider_;
};


} // namespace Meq

#endif

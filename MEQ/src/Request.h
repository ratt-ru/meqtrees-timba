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

class Request : public DataRecord
{
public:
  typedef CountedRef<VellSet> Ref;
    
  Request ();
    
  // Construct from DataRecord 
  Request (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  
  // Create the request from the cells for which the expression has
  // to be calculated. Optionally no derivatives are calculated.
  explicit Request (const Cells&, bool calcDeriv=true, const HIID &id=HIID(),int cellflags=DMI::EXTERNAL|DMI::NONSTRICT);
  
  explicit Request (const Cells *, bool calcDeriv=true, const HIID &id=HIID(),int cellflags=DMI::ANON|DMI::NONSTRICT);

  virtual TypeId objectType () const
  { return TpMeqRequest; }
  
//   // implement standard clone method via copy constructor
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Request(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Request is made from a DataRecord
  // (or when the underlying DataRecord is privatized, etc.)
  virtual void validateContent ();
  
  // this disables removal of fields via hooks
  virtual bool remove (const HIID &)
  { Throw("remove() from a Meq::VellSet not allowed"); }
  
  // Calculate derivatives if parameters are solvable?
  bool calcDeriv() const
  { return itsCalcDeriv; }

  // Attaches cells object (default as anon). Can also specify DMI::CLONE
  // to copy
  void setCells (const Cells *,int flags = DMI::ANON|DMI::NONSTRICT);
  // Attaches cells object (default is external). 
  void setCells (const Cells &cells,int flags = DMI::EXTERNAL|DMI::NONSTRICT)
  { setCells(&cells,flags); }
  // True if a cells object is attached
  bool hasCells () const
  { return itsCells; }
  // Returns cells
  const Cells& cells() const
  { DbgFailWhen(!itsCells,"no cells in Meq::Request");
    return *itsCells; }
  
  // Set the request id.
  void setId (const HIID &id);

  // Get the request id.
  const HIID & id() const
  { return itsId; }

protected: 
  // disable public access to some DataRecord methods that would violate the
  // structure of the container
  DataRecord::remove;
  DataRecord::replace;
  DataRecord::removeField;
  
private:
  HIID   itsId;
  bool   itsCalcDeriv;
  const  Cells* itsCells;
};


} // namespace Meq

#endif

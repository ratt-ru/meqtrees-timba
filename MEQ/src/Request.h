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

//##ModelId=3F86886E01FF
class Request : public DataRecord
{
public:
    //##ModelId=400E53040057
  typedef CountedRef<VellSet> Ref;
    
    //##ModelId=3F8688700056
  Request ();
    
  // Construct from DataRecord 
    //##ModelId=3F8688700061
  Request (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  
  // Create the request from the cells for which the expression has
  // to be calculated. Optionally no derivatives are calculated.
    //##ModelId=400E535403DD
  explicit Request (const Cells&, bool calcDeriv=true, const HIID &id=HIID(),int cellflags=DMI::EXTERNAL|DMI::NONSTRICT);
  
    //##ModelId=400E53550016
  explicit Request (const Cells *, bool calcDeriv=true, const HIID &id=HIID(),int cellflags=DMI::ANON|DMI::NONSTRICT);

    //##ModelId=400E53550034
  virtual TypeId objectType () const
  { return TpMeqRequest; }
  
//   // implement standard clone method via copy constructor
    //##ModelId=400E53550038
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Request(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Request is made from a DataRecord
  // (or when the underlying DataRecord is privatized, etc.)
    //##ModelId=400E53550049
  virtual void validateContent ();
  
  // this disables removal of fields via hooks
    //##ModelId=400E5355004C
  virtual bool remove (const HIID &)
  { Throw("remove() from a Meq::VellSet not allowed"); }
  
  // Calculate derivatives if parameters are solvable?
    //##ModelId=3F868870006C
  bool calcDeriv() const
  { return itsCalcDeriv; }

  // Attaches cells object (default as anon). Can also specify DMI::CLONE
  // to copy
    //##ModelId=3F868870006E
  void setCells (const Cells *,int flags = DMI::ANON|DMI::NONSTRICT);
  // Attaches cells object (default is external). 
    //##ModelId=400E53550065
  void setCells (const Cells &cells,int flags = DMI::EXTERNAL|DMI::NONSTRICT)
  { setCells(&cells,flags); }
  // True if a cells object is attached
    //##ModelId=400E53550076
  bool hasCells () const
  { return itsCells; }
  // Returns cells
    //##ModelId=3F8688700073
  const Cells& cells() const
  { DbgFailWhen(!itsCells,"no cells in Meq::Request");
    return *itsCells; }
  
  // Set the request id.
    //##ModelId=3F8688700075
  void setId (const HIID &id);

  // Get the request id.
    //##ModelId=400E5355007E
  const HIID & id() const
  { return itsId; }

protected: 
  // disable public access to some DataRecord methods that would violate the
  // structure of the container
    //##ModelId=400E5354039C
  DataRecord::remove;
    //##ModelId=400E535403A4
  DataRecord::replace;
    //##ModelId=400E535403AB
  DataRecord::removeField;
  
private:
    //##ModelId=400E535403B3
  HIID   itsId;
    //##ModelId=3F868870003C
  bool   itsCalcDeriv;
    //##ModelId=3F86BFF80269
  const  Cells* itsCells;
};


} // namespace Meq

#endif

//# Result.h: A set of VellSet results
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

#ifndef MEQ_RESULT_H
#define MEQ_RESULT_H

//# Includes
#include <iostream>
#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <MEQ/VellSet.h>

#pragma aidgroup Meq
#pragma type #Meq::Result

// This class represents a result of a domain for which an expression
// has been evaluated.

namespace Meq {

class Cells;

class Result : public DataRecord
{
public:
  typedef CountedRef<Result> Ref;

  // ------------------------ CONSTRUCTORS
  // Create a Result with the given number of vellsets.
  // If <0, then the set is marked as a fail
  explicit Result (int nresults=1);
  
  explicit Result (const Request &req);
  
  Result (int nresults,const Request &req);
  Result (const Request &req,int nresults);
  
  // Construct from DataRecord. 
  Result (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);

  ~Result();

  virtual TypeId objectType () const
  { return TpMeqResult; }
  
  // implement standard clone method via copy constructor
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Result(*this,flags,depth); }
  
  virtual void privatize (int flags = 0, int depth = 0);
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Result is made from a DataRecord
  // (or when the underlying DataRecord is privatized, etc.)
  virtual void validateContent ();
  

  // ------------------------ CELLS
  // Set or get the cells.
  // Attaches cells object (default as anon). Can also specify DMI::CLONE
  // to copy
  void setCells (const Cells *,int flags = DMI::ANON|DMI::NONSTRICT);
  // Attaches cells object (default is external). 
  void setCells (const Cells &cells,int flags = DMI::EXTERNAL|DMI::NONSTRICT)
  { setCells(&cells,flags); }

  bool hasCells () const
  { return itsCells; }
    
  const Cells& cells() const
  { DbgFailWhen(!itsCells,"no cells in Meq::VellSet");
    return *itsCells; }

  // ------------------------ VELLSETS
  void allocateVellSets (int nvellsets);
    
  int numVellSets () const
    { return itsVellSets.valid() ? itsVellSets->size() : 0; }
  
  const VellSet & vellSetConst (int i) const
    { return itsVellSets.deref()[i].as<VellSet>(); }
  
  VellSet & vellSet (int i)
    { return itsVellSets.dewr()[i].as_wr<VellSet>(); }
  
  VellSet & setVellSet (int i,VellSet *vellset);
  
  VellSet & setVellSet (int i,VellSet::Ref::Xfer &vellset);
  
  // creates new vellset at plane i with the given # of spids
  VellSet & setNewVellSet (int i,int nspids=0)
  { 
    VellSet::Ref resref(new VellSet(nspids),DMI::ANONWR); 
    return setVellSet(i,resref); 
  }

  // ------------------------ FAIL RESULTS
  // checks if this Result has any fails in it
  bool hasFails () const;
  // returns the number of fails in the set
  int numFails () const;
  

  // dumps result to stream
  void show (std::ostream&) const;

  static int nctor;
  static int ndtor;
  
protected: 
  // disable public access to some DataRecord methods that would violate the
  // structure of the container
  DataRecord::remove;
  DataRecord::replace;
  DataRecord::removeField;
  
private:

  DataField::Ref  itsVellSets;
  const Cells    *itsCells;
};


} // namespace Meq

#endif

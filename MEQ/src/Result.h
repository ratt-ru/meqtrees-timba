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
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>

#pragma aidgroup Meq
#pragma type #Meq::Result

// This class represents a result of a domain for which an expression
// has been evaluated.

namespace Meq { using namespace DMI;

//##ModelId=3F86886E020D
class Result : public DMI::Record
{
public:
    //##ModelId=3F86886E0210
  typedef CountedRef<Result> Ref;

  // ------------------------ CONSTRUCTORS
  // Create a Result with the given number of vellsets.
  // If <0, then the set is marked as a fail
  // The integrated flag specifies whether the result is an integration
  // over the specified cells, or a sampling at the cell center.  
    //##ModelId=3F86887000CE
  explicit Result (int nresults=0,bool integrated=false);
  
    //##ModelId=3F8688700151
  explicit Result (const Request &req,bool integrated=false);
  
    //##ModelId=400E535500F5
  Result (int nresults,const Request &req,bool integrated=false);
    //##ModelId=400E53550105
  Result (const Request &req,int nresults,bool integrated=false);
  
  // Construct from DMI::Record. 
    //##ModelId=400E53550116
  Result (const DMI::Record &other,int flags=0,int depth=0);

    //##ModelId=3F86887000D3
  ~Result();

    //##ModelId=400E5355012D
  virtual TypeId objectType () const
  { return TpMeqResult; }
  
  // implement standard clone method via copy constructor
    //##ModelId=400E53550131
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Result(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Result is made from a DMI::Record
  // (or when the underlying DMI::Record is privatized, etc.)
    //##ModelId=400E53550156
  virtual void validateContent (bool recursive);
  

  // ------------------------ CELLS
  // Set or get the cells.
  // Attaches cells object 
    //##ModelId=3F86887000D4
  void setCells (const Cells *,int flags = 0);
  // Attaches cells object (default is external). 
    //##ModelId=400E53550163
  void setCells (const Cells &cells,int flags = DMI::AUTOCLONE)
  { setCells(&cells,flags); }

    //##ModelId=400E53550174
  bool hasCells () const
  { return pcells_ != 0; }
    
    //##ModelId=400E53550178
  const Cells& cells() const
  { DbgFailWhen(!pcells_,"no cells in Meq::Result");
    return pcells_->deref(); }
    
  // ------------------------ INTEGRATED property
  // this is set at construction time
  bool isIntegrated () const
  { return is_integrated_; }
  
  // integrates all VellSets (multiplies values by cell size)
  // if integrate=true, does nothing
  void integrate (bool reverse=false);
  
  // differentiates all VellSets (divides values by cell size)
  // if integrate=false, does nothing
  void differentiate ()
  { integrate(true); }

  // ------------------------ VELLSETS
    //##ModelId=400E5355017B
  void allocateVellSets (int nvellsets);
    
    //##ModelId=400E53550185
  int numVellSets () const
    { return pvellsets_ ? pvellsets_->deref().size() : 0; }
  
    //##ModelId=400E53550189
  const VellSet & vellSet (int i) const
    { return pvellsets_->deref()[i].as<VellSet>(); }
  
  VellSet::Ref vellSetRef (int i) const
    { return pvellsets_->deref()[i].ref(); }
  
    //##ModelId=400E53550193
  VellSet & vellSetWr (int i)
    { return wrVellSets()[i].as_wr<VellSet>(); }
  
    //##ModelId=400E5355019D
  const VellSet & setVellSet (int i,const VellSet *pvs,int flags=0)
    { wrVellSets().put(i,pvs,flags); return *pvs; }
  
  VellSet & setVellSet (int i,VellSet *pvs,int flags=0)
    { wrVellSets().put(i,pvs,flags); return *pvs; }
  
    //##ModelId=400E535501AD
  const VellSet & setVellSet (int i,const VellSet::Ref &vellset,int flags=0)
    { wrVellSets().put(i,vellset,flags); return *vellset; }
  
  // creates new vellset at plane i with the given # of spids and perturbation sets
    //##ModelId=400E535501BF
  VellSet & setNewVellSet (int i,int nspids=0,int npertsets=1);

  // ------------------------ FAIL RESULTS
  // checks if this Result has any fails in it
    //##ModelId=400E535501D1
  bool hasFails () const;
  // returns the number of fails in the set
    //##ModelId=400E535501D4
  int numFails () const;

  // dumps result to stream
    //##ModelId=3F868870014C
  void show (std::ostream&) const;

protected: 
  Record::protectField;  
  Record::unprotectField;  
  Record::begin;  
  Record::end;  
  Record::as;
  Record::clear;
  
private:
  // sets the integrated property, including underlying record
  void setIsIntegrated (bool integrated);
    
  // helper function: write-access to vellsets (enforces COW)
  DMI::Vec &       wrVellSets ()
  {
    return pvellsets_->dewr();
  }
    
    //##ModelId=400E535500B8
  DMI::Vec::Ref  * pvellsets_;
    //##ModelId=3F86BFF802B0
  Cells::Ref     * pcells_;
  
  bool            is_integrated_;
};


} // namespace Meq

#endif

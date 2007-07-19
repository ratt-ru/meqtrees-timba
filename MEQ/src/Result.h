//# Result.h: A set of VellSet results
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
  // tensor dimensions, for tensor results
  typedef LoShape Dims;
  typedef LoShape TIndex;
  
    //##ModelId=3F86886E0210
  typedef CountedRef<Result> Ref;

  // ------------------------ CONSTRUCTORS
  // Create a Result with the given number of vellsets.
  // If <0, then the set is marked as a fail.
  // The integrated flag specifies whether the result is an integration
  // over the specified cells, or a sampling at the cell center.  
    //##ModelId=3F86887000CE
  explicit Result (int nvs=0, bool integrated=false);
  
  // Create a tensor Result with the number of vellsets specified by dims
  // if dims is empty (rank 0), creates one vellset
  explicit Result (const Dims &dims, bool integrated=false);
  
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
  
  // ------------------------ DIMENSIONS
  // A Result with a single VellSet will always have empty dimensions and 
  // a tensor rank of 0. 
  const Dims & dims () const
  { return dims_; }
  
  int tensorRank () const 
  { return dims_.size(); }
  
  // Sets dimensions, returns their product (i.e. # of vellsets)
  // If result is non-empty, then dims may only change if the # of vellsets
  // doesn't (this is the equivalent of a reshape operation).
  // If result is empty, this implictly allocates vellsets.
  int setDims (const Dims &dims);
  
  // returns scalar offset corresponding to given tensor index
  // versions ending with Chk check indices for range
  int getOffsetChk (const TIndex &ind) const
  {
    FailWhen(ind.size() != dims_.size(),"tensor rank mismatch");  
    int offset=0, stride=1;
    for( int i = ind.size()-1; i>=0; i-- )
    {
      FailWhen(ind[i]<0 || ind[i]>=dims_[i],ssprintf("tensor index #%d out of range",i));
      offset += ind[i]*stride;
      stride *= dims_[i];
    }
    return offset;
  }
  int getOffset (const TIndex &ind) const
  {
    int offset=0, stride=1;
    for( int i = ind.size()-1; i>=0; i-- )
    {
      offset += ind[i]*stride;
      stride *= dims_[i];
    }
    return offset;
  }
  
  // shortcut for matrices
  int getOffsetChk (int i,int j) const
  {
    FailWhen(dims_.size()!=2,"tensor rank mismatch");  
    FailWhen(i<0 || i>=dims_[0],"tensor index 0 out of range");
    FailWhen(j<0 || j>=dims_[1],"tensor index 1 out of range");
    return i*dims_[1] + j;
  }
  
  int getOffset (int i,int j) const
  {
    return i*dims_[1] + j;
  }

  // ------------------------ CELLS
  // Set or get the cells.
  // This attaches a cells object to the result. If force=false, then cells
  // are only attached if any vellsets in the result have a shape.
  // In any case the vellset shapes are checked against the Cells shape.
  // Note that if all vellsets are shapeless (i.e. do not depend on any axis),
  // it is normal for the result object to have no cells, since this
  // allows it to be cached and reused without regard to request cells.
    //##ModelId=3F86887000D4
  void setCells (const Cells *,int flags = 0,bool force=false);
  // Attaches cells object (default is external). 
    //##ModelId=400E53550163
  void setCells (const Cells &cells,int flags = DMI::AUTOCLONE,bool force=false)
  { setCells(&cells,flags,force); }
  
  // This attaches a cells object to the result with force=true
  void forceCells (const Cells *cells,int flags = 0)
  { setCells(cells,flags,true); }
  // Attaches cells object (default is external). 
    //##ModelId=400E53550163
  void forceCells (const Cells &cells,int flags = DMI::AUTOCLONE)
  { setCells(&cells,flags,true); }
  
  // removes cells from result -- exception thrown if any vellsets have shapes
  void clearCells ();

    //##ModelId=400E53550174
  bool hasCells () const
  { return pcells_ != 0; }
  
  // returns true if result has a shape and needs to have cells attached
  bool needsCells (const Cells &cells) const;
    
    //##ModelId=400E53550178
  const Cells& cells() const
  { DbgFailWhen(!pcells_,"no cells in Meq::Result");
    return pcells_->deref(); }
    
  // Rechecks the shapes of vells objects against the result cells.
  // If vells have shapes, then a result cells must have been set (throws
  // error otherwise), and the shapes must be compatible (the
  // cells is allowed to have extra axes of variability). If none of
  // the vells have shapes, result cells will be deleted if reset=true.
  void verifyShape (bool reset=true);
  
  // returns the overall shape of the vellsets (i.e. merges shapes of
  // all vellsets)
  LoShape getVellSetShape () const;
  
  // ------------------------ INTEGRATED property
// NB: OMS 04/01/2007 this is being phased out; the first step is to make
// it always False
 
  // this is set at construction time
  bool isIntegrated () const
  { return false; }
//   { return is_integrated_; }
//   
//   // integrates all VellSets (multiplies values by cell size)
//   // attaches supplied cells if none already attached
//   // if isIntegrated()=true, does nothing
   void integrate (const Cells *pcells=0,bool reverse=false)
   {}
//   
//   // differentiates all VellSets (divides values by cell size)
//   // uses supplied cells if none attached
//   // if isIntegrated()=false, does nothing
//   void differentiate (const Cells *pcells=0)
//   { integrate(pcells,true); }

  // ------------------------ VELLSETS
    //##ModelId=400E5355017B
  // allocates vellsets and sets dimensions (result must be empty). Returns nvs.
  int allocateVellSets (int nvs);
  // allocates vellsets and sets dimensions (result must be empty)
  // Returns product of dims.
  int allocateVellSets (const Dims &dims);
    
    //##ModelId=400E53550185
  int numVellSets () const
    { return pvellsets_ ? pvellsets_->deref().size() : 0; }
  
    //##ModelId=400E53550189
  const VellSet & vellSet (int i) const
    { return pvellsets_->deref().as<VellSet>(i); }
  
  VellSet::Ref vellSetRef (int i) const
    { return pvellsets_->deref().getObj(i); }
  
    //##ModelId=400E53550193
  VellSet & vellSetWr (int i)
    { return wrVellSets().as<VellSet>(i); }
  
    //##ModelId=400E5355019D
  const VellSet & setVellSet (int i,const VellSet *pvs,int flags=0)
    { wrVellSets().put(i,pvs,flags); return *pvs; }
  
  VellSet & setVellSet (int i,VellSet *pvs,int flags=0)
    { wrVellSets().put(i,pvs,flags); return *pvs; }
  
  const VellSet & setVellSet (int i,const VellSet &vs,int flags=0)
    { wrVellSets().put(i,&vs,flags); return vs; }
  
  VellSet & setVellSet (int i,VellSet &vs,int flags=0)
    { wrVellSets().put(i,&vs,flags); return vs; }
  
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
  
  // adds fails to ExceptionList
  DMI::ExceptionList & addToExceptionList (DMI::ExceptionList &) const;
  
  DMI::ExceptionList makeExceptionList () const
  { DMI::ExceptionList list; return addToExceptionList(list); }

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
  void setIsIntegrated (bool)
// 04/01/2007 phased out, so inlined to NOP
  {}

  // verifies vellsets against a cell shape, throws exception on mismatch.
  //  Returns true if any vellsets are variable.
  bool verifyShape (const LoShape &cellshape) const;
    
  // helper function: write-access to vellsets (enforces COW)
  DMI::Vec &       wrVellSets ()
  {
    return pvellsets_->dewr();
  }
    
    //##ModelId=400E535500B8
  DMI::Vec::Ref  * pvellsets_;
    //##ModelId=3F86BFF802B0
  Cells::Ref     * pcells_;

// 04/01/2007 phased out  
//  bool            is_integrated_;
  
  Dims            dims_;
};


} // namespace Meq

#endif

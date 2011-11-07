//# VellSet.h: The result of an expression for a domain.
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

#ifndef MEQ_VELLSET_H
#define MEQ_VELLSET_H

//# Includes
#include <iostream>
#include <TimBase/lofar_vector.h>
#include <MEQ/Vells.h>
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <MEQ/TID-Meq.h>

#pragma aidgroup Meq
#pragma types #Meq::VellSet

// This class represents a result of a domain for which an expression
// has been evaluated.

namespace Meq { using namespace DMI;

//##ModelId=400E530400D3
class VellSet : public DMI::Record // , public OptionalColumns
{
public:
  //##ModelId=400E530400D6
  typedef CountedRef<VellSet> Ref;

  typedef int SpidType;

  // Create a time,frequency result for the given shape, number of spids,
  // number of pert sets
    //##ModelId=400E5355031E
  VellSet (const LoShape &shp,int nspid=0,int npertsets=1);

  // Create a time,frequency result for the given number of spids, number
  // of pert sets. Shape has to be supplied later.
  explicit VellSet (int nspid=0,int nset=1);

  // Construct from DMI::Record.
    //##ModelId=400E53550322
  VellSet (const DMI::Record &other,int flags=0,int depth=0);

  // destructor
    //##ModelId=400E53550329
  ~VellSet();

  // returns the object tid
    //##ModelId=400E5355032B
  virtual TypeId objectType () const
  { return TpMeqVellSet; }

  // implement standard clone method via copy constructor
    //##ModelId=400E5355032D
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new VellSet(*this,flags,depth); }

  // validate record contents and setup shortcuts to them. This is called
  // automatically whenever a VellSet is made from a DMI::Record
  // (or when the underlying DMI::Record is privatized, etc.)
    //##ModelId=400E5355033A
  virtual void validateContent (bool recursive);

  // ------------------------ SHAPE
  // The "shape" attribute indicates the variability of the vellset
  // along specific axes. If shape[iaxis]>1, the vellset is variable along
  // that axis. All Vells in the vellset must conform to the shape
  // (i.e. be of size ==1 or ==shape[iaxis] along each axis of variability).
  // Normally the shape attribute is initialized/checked automatically
  // as Vells are assigned. E.g., if all vells are non-variable, shape
  // remains nil (hasShape()==false). However, should you subsequently change
  // the shape of a Vells directly inside the vellset (avoid doing this if
  // you can), you must call verifyShape() to reset the shape attribute.
  const bool hasShape () const
  { return !shape_.empty(); }

  const LoShape & shape () const
  { return shape_; }

  // Sets an explicit shape. Will throw exception if a non-conformant
  // shape is already set, although the new shape may have _more_ axes of
  // variability.
  void setShape (const Vells::Shape &shp);

  void setShape (int nx,int ny)
  { setShape(Vells::Shape(nx,ny)); }

  // Recomputes shape (if reset=True or shape is not set) based on all
  // Vells in the set.
  // If reset=False and shape is already set, verifies that all Vells
  // conform, and throws an exception if not.
  void verifyShape (bool reset=true);

  // ------------------------ SPIDS AND ASSOCIATED ATTRIBUTES
  // Get the spids.
    //##ModelId=400E5355033C
  int numSpids() const
  { return numspids_; }

    //##ModelId=400E5355033E
  SpidType getSpid (int i) const
  { return spids_[i]; }

  // number of perturbation sets (1 or 2)
  int numPertSets () const
  { return pset_.size(); }

  void setNumPertSets (int nsets);

  // nperturbed() is an alias for getNumSpids
    //##ModelId=400E53550342
  int nperturbed() const
  { return numSpids(); }

  // Set the spids. If VellSet was created with a >0 nspids,
  // then the size of the vector must match. If VellSet was created
  // with 0 spids, this can be used to initialize spids & perturbations.
    //##ModelId=400E53550344
  void setSpids (const vector<SpidType>& spids);

  // Copies spids from other VellSet. If VellSet was created with >0 nspids,
  // then the number in other must match. If VellSet was created with 0
  // spids, this can be used to initialize spids & perturbations.
  void copySpids (const VellSet &other);

  // is spid defined at this position? increments index if true
  // It returns the index (-1 if not found).
    //##ModelId=400E53550348
  int isDefined (SpidType spid, int& index) const
  { return (index>=numspids_  ?  -1 :
	    spid==spids_[index]  ?  index++ : -1); }

  // Get the i-th perturbed parameter.
    //##ModelId=400E5355034E
  double getPerturbation (int i,int iset=0) const
  { return pset_[iset].pert[i]; }

  // Set the i-th perturbed parameter of set iset
    //##ModelId=400E53550353
  void setPerturbation (int i, double value, int iset=0);
  // set all perturbations of set iset
    //##ModelId=400E53550359
  void setPerturbations (const vector<double>& perts,int iset=0);

  void copyPerturbations (const VellSet &other);

  // ------------------------ MAIN RESULT VALUE
  // a vellset is empty when it has no main value or perturbed values
  bool isEmpty () const
  { return !hasValue() && !numSpids(); }

  // a vellset is a "null" when it has no main value, or main value
  // is a null and there are no perturbed values
  bool isNull () const
  { return !hasValue() || ( !numSpids() && pvalue_->deref().isNull() ); }

  // returns true if vellset has a value
  bool hasValue () const
  { return pvalue_ != 0; }

  // Get the value.
    //##ModelId=400E5355035C
  const Vells & getValue() const
  {
    Thread::Mutex::Lock lock(mutex());
    FailWhen( !pvalue_,"no main value in this VellSet" );
    return pvalue_->deref();
  }
    //##ModelId=400E5355035E

  Vells & getValueWr ()
  {
    Thread::Mutex::Lock lock(mutex());
    FailWhen( !pvalue_,"no main value in this VellSet" );
    return pvalue_->dewr();
  }

  // Attaches the given Vells to value. Vells ref may be COWed if flags need
  // to be attached
  void setValue (Vells::Ref &ref,int flags=0);

  void setValue (const Vells::Ref &ref)
  { Vells::Ref ref2(ref); setValue(ref2); }

    //##ModelId=400E53550360
  Vells & setValue (Vells *val,int flags=0)
  { Vells::Ref ref(val,flags); setValue(ref); return *val; }

  // set the value to a copy of the given Vells object (Vells copy uses ref semantics!)
    //##ModelId=400E53550363
  Vells & setValue   (const Vells & value) { return setValue(new Vells(value)); }
  Vells & setReal    (const Vells::Shape &shp) { return setValue(new Vells(0.,shp,false)); }
  Vells & setComplex (const Vells::Shape &shp) { return setValue(new Vells(numeric_zero<dcomplex>(),shp,false)); }
  Vells & setReal    () { return setReal(shape()); }
  Vells & setComplex () { return setComplex(shape()); }

  // ------------------------ PERTURBED VALUES
  // Get the i-th perturbed value from set iset
    //##ModelId=400E5355037E
  const Vells& getPerturbedValue (int i,int iset=0) const
    { DbgAssert(i>=0 && i<numspids_ && iset>=0 && iset<int(pset_.size()));
      DbgAssert(pset_[iset].pertval_vec);
      return pset_[iset].pertval_vec->deref().as<Vells>(i); }
    //##ModelId=400E53550383
  Vells& getPerturbedValueWr (int i,int iset=0)
    { DbgAssert(i>=0 && i<numspids_ && iset>=0 && iset<int(pset_.size()));
      DbgAssert(pset_[iset].pertval_vec);
      return pset_[iset].pertval_vec->dewr().as<Vells>(i); }

  // Set the i-th perturbed value (ref semantics)
  void setPerturbedValue (int i,Vells::Ref &ref,int iset=0,int flags=0);

  void setPerturbedValue (int i,const Vells::Ref &ref,int iset=0)
  {
    Vells::Ref ref2(ref);
    setPerturbedValue(i,ref2,iset);
  }

    //##ModelId=400E53550387
  Vells & setPerturbedValue (int i,Vells *val,int iset=0)
  {
    Vells::Ref ref(val);
    setPerturbedValue(i,ref,iset);
    return *val;
  }

  // Set the i-th perturbed value (copy semantics, but internally
  // Vells copy uses ref semantics, this is handy for setting the value
  // with a result of an expression, which is a const temp object
  const Vells & setPerturbedValue (int i,const Vells &vells,int iset=0)
  {
    Vells::Ref ref(new Vells(vells));
    setPerturbedValue(i,ref,iset);
    return vells;
  }

  // provides access to the mutex associated with the perturbation set (if any)
  const Thread::Mutex & pertSetMutex (int iset) const
  {
    return pset_[iset].pertval_vec->deref_p()->mutex();
  }

  // ------------------------ DATA FLAGS
  // does this VellSet have flags attached?
  bool hasDataFlags () const
  { return pflags_; }

  // returns flags of this VellSet
  const Vells & dataFlags () const
  { return pflags_->deref(); }

  // returns true if dataflags are the same object as given
  bool sameDataFlags (const Vells &flags) const
  { return hasDataFlags() && pflags_->deref_p() == &flags; }

  // sets the dataflags of a VellSet
  void setDataFlags (const Vells::Ref &flags);

  // aliases for passing flags by value or pointer
  void setDataFlags (const Vells &flags)
  {
    Vells::Ref ref(flags);
    setDataFlags(ref);
  }

  void setDataFlags (const Vells *flags)
  {
    Vells::Ref ref(flags);
    setDataFlags(ref);
  }

  // removes flags from VellSet (and constituent Vells)
  void clearDataFlags ();

  // ------------------------ DATA WEIGHTS
  // does this VellSet have weights attached?
  bool hasDataWeights () const
  { return pweights_; }

  // returns weights of this VellSet
  const Vells & dataWeights () const
  { return pweights_->deref(); }

  // sets the weights of a VellSet
  void setDataWeights (const Vells::Ref &weights);

  // aliases for passing weights by value or pointer
  void setDataWeights (const Vells &weights)
  { setDataWeights(Vells::Ref(weights)); }

  void setDataWeights (const Vells *weights)
  { setDataWeights(Vells::Ref(weights)); }

  // removes weights from VellSet
  void clearDataWeights ();

protected:
  // called after flags have been attached, to verify flag shapes
  // and to propagate the flags to all child Vells
  void setupFlags (const Vells::Ref flagref);

  // called to adjust/verify shape after a new Vells has been added
  void adjustShape (const Vells &vells);

  // helper function for above
  bool adjustShape (LoShape &shp,const Vells &vells);


  // ------------------------ FAIL RECORDS
  // A VellSet may be a Fail. A Fail will not contain any values or
  // perturbations, but rather a field of 1+ fail records.

  // This marks the Result as a FAIL, and adds a fail-record.
  // All values and perturbations are cleared, and a Fail field is
  // created if necessary.
public:
  void addFail (const ObjRef &ref);

    //##ModelId=400E53550393
  void addFail (const std::exception &exc)
  { addFail(exceptionToObj(exc)); }

#define MakeFailVellSet(res,msg) \
  (res).addFail(MakeNodeException(msg))

#define MakeFailVellSetMore(res,exc,msg) { \
  DMI::ExceptionList *pelist = dynamic_cast<DMI::ExceptionList *>(&(exc)); \
  if( pelist ) \
    (res).addFail(pelist->add(MakeNodeException(msg))); \
  else \
    (res).addFail(exc); \
}

  // checks if this VellSet is a fail
    //##ModelId=400E535503A5
  bool isFail () const
  { return is_fail_; }
  // returns the number of fail records
    //##ModelId=400E535503A7
  int numFails () const;
  // returns the i-th fail record
    //##ModelId=400E535503A9
  ObjRef getFail (int i=0) const;

  const std::string & getFailMessage (int i=0) const;

  // adds fails to ExceptionList
  DMI::ExceptionList & addToExceptionList (DMI::ExceptionList &) const;

  DMI::ExceptionList makeExceptionList () const
  { DMI::ExceptionList list; return addToExceptionList(list); }

  // print VellSet to stream
    //##ModelId=400E535503AE
  void show (std::ostream&) const;

  // this disables removal of DMI::Record fields via hooks
    //##ModelId=400E535503B1
  virtual int remove (const HIID &)
  { Throw("remove() from a Meq::VellSet not allowed"); }

protected:
  Record::protectField;
  Record::unprotectField;
  Record::begin;
  Record::end;
  Record::as;
  Record::clear;

private:
  void init ();
  // Remove all shortcuts, pertubed values, etc. (Does not do anything
  // to the underlying DMI::Record though)
    //##ModelId=400E535503B5
  void clear();

  void setupPertData (int iset);

//   // Allocate the main value with given type and shape.
//     //##ModelId=400E535503B7
//   Vells & allocateReal (int nfreq, int  ntime)
//     { setShape(nfreq,ntime);
//       return setValue(new Vells(double(0),nfreq,ntime,false)); }
//     //##ModelId=400E535503BD
//   Vells & allocateComplex (int nfreq, int ntime)
//     { setShape(nfreq,ntime);
//       return setValue(new Vells(dcomplex(0),nfreq,ntime,false)); }
//
    //##ModelId=400E535502FC
  Vells::Ref * pvalue_;

  Vells::Ref * pflags_;

  Vells::Ref * pweights_;

    //##ModelId=400E53550302
  double default_pert_;

  typedef struct
  {
    double * pert;
    DMI::Vec::Ref *   pertval_vec;
  } PerturbationSet;

  vector<PerturbationSet> pset_;

// OMS 28/01/05: phasing this out, replace with explicit data flags
//   typedef struct
//   {
//     DMI::NumArray::Ref ref;
//     void          *ptr;
//   } OptionalColumnData;
//
//   OptionalColumnData optcol_[NUM_OPTIONAL_COL];

  LoShape        shape_;

    //##ModelId=400E53550314
  const int *    spids_;
    //##ModelId=400E53550317
  int            numspids_;

    //##ModelId=400E5355031B
  bool           is_fail_;
};


} // namespace Meq

inline std::ostream& operator << (std::ostream& os, const Meq::VellSet& res)
{
  res.show(os);
  return os;
}

#endif

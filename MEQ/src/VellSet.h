//# VellSet.h: The result of an expression for a domain.
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

#ifndef MEQ_VELLSET_H
#define MEQ_VELLSET_H

//# Includes
#include <iostream>
#include <Common/lofar_vector.h>
#include <MEQ/Vells.h>
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <MEQ/TID-Meq.h>

#pragma aidgroup Meq
#pragma types #Meq::VellSet

// This class represents a result of a domain for which an expression
// has been evaluated.

namespace Meq { using namespace DMI;

class OptionalColumns
{
  public:
    typedef enum
    {
        FLAGS   = 0,
        WEIGHT  = 1,

        NUM_OPTIONAL_COL = 2
    }
    OptionalColumnEnums;

    template<int N> class Traits
    {
      public:
          typedef void ElementType;
          typedef void ArrayType;
    };

    static TypeId optColElementType (uint icol);

    static TypeId optColArrayType (uint icol);

    static const HIID & optColFieldId (uint icol);
};

template<> class OptionalColumns::Traits<OptionalColumns::FLAGS> 
{
  public:
      typedef int ElementType;
      typedef blitz::Array<ElementType,2> ArrayType;
};

template<> class OptionalColumns::Traits<OptionalColumns::WEIGHT> 
{
  public:
      typedef float ElementType;
      typedef blitz::Array<ElementType,2> ArrayType;
};


inline TypeId OptionalColumns::optColElementType (uint icol)
{
  const TypeId type[] = { typeIdOf(Traits<FLAGS>::ElementType),
                          typeIdOf(Traits<WEIGHT>::ElementType) };
  DbgAssert1(icol<NUM_OPTIONAL_COL);
  return type[icol];  
}

inline TypeId OptionalColumns::optColArrayType (uint icol)
{
  const TypeId type[] = { typeIdOf(Traits<FLAGS>::ArrayType),
                          typeIdOf(Traits<WEIGHT>::ArrayType) };
  DbgAssert1(icol<NUM_OPTIONAL_COL);
  return type[icol];  
}


//##ModelId=400E530400D3
class VellSet : public DMI::Record , public OptionalColumns
{
public:
  //##ModelId=400E530400D6
  typedef CountedRef<VellSet> Ref;

  typedef Traits<FLAGS>::ElementType FlagType; 
  typedef Traits<FLAGS>::ArrayType FlagArrayType; 

  // Create a time,frequency result for the given shape, number of spids,
  // number of pert sets
    //##ModelId=400E5355031E
  VellSet (const LoShape &shp,int nspid=0,int nset=1);
  
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
  const bool hasShape () const
  { return shape_.size()>0; }

  const LoShape & shape () const
  { return shape_; }
  
  void setShape (const Vells::Shape &shp);
  
  void setShape (int nx,int ny)
  { setShape(Vells::Shape(nx,ny)); }
  
  // ------------------------ SPIDS AND ASSOCIATED ATTRIBUTES
  // Get the spids.
    //##ModelId=400E5355033C
  int numSpids() const
  { return numspids_; }
  
    //##ModelId=400E5355033E
  int getSpid (int i) const
  { return spids_[i]; }
  
  // number of perturbation sets (0
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
  void setSpids (const vector<int>& spids);

  // Copies spids from other VellSet. If VellSet was created with >0 nspids,
  // then the number in other must match. If VellSet was created with 0 
  // spids, this can be used to initialize spids & perturbations.
  void copySpids (const VellSet &other);

  // is spid defined at this position? increments index if true
  // It returns the index (-1 if not found).
    //##ModelId=400E53550348
  int isDefined (int spid, int& index) const
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

  // Attaches the given Vells to value
  void setValue (const Vells::Ref &ref,int flags=0);
  
    //##ModelId=400E53550360
  Vells & setValue (Vells *val,int flags=0)
  { Vells::Ref ref(val,flags); setValue(ref); return *val; }
  
  // set the value to a copy of the given Vells object (Vells copy uses ref semantics!)
    //##ModelId=400E53550363
  Vells & setValue   (const Vells & value) { return setValue(new Vells(value)); }
  Vells & setReal    (const Vells::Shape &shp) { return setValue(new Vells(0.,shp,false)); }
  Vells & setComplex (const Vells::Shape &shp) { return setValue(new Vells(dcomplex(0),shp,false)); }
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
  void setPerturbedValue (int i,const Vells::Ref &vref,int iset=0);
  
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
      
      
  // ------------------------ OPTIONAL COLUMNS
protected:
  // ensures writability of optional column by privatizing for writing as needed;
  // returns pointer to blitz array
  void * writeOptCol (uint icol);
      
  void * initOptCol (uint icol,bool array);

  void   doSetOptCol (uint icol,DMI::NumArray *parr,int dmiflags);
  
public:
          
  bool hasOptCol (uint icol) const
  { 
    DbgAssert1(icol<NUM_OPTIONAL_COL); 
    return optcol_[icol].ptr != 0;
  }
  
  template<int N>
  bool hasOptCol () const
    { return hasOptCol(N); }
  
  template<int N>
  const typename Traits<N>::ArrayType & getOptCol () const
    { Assert(hasOptCol(N)); return *static_cast<const typename Traits<N>::ArrayType *>(optcol_[N].ptr); }
  
  template<int N>
  typename Traits<N>::ArrayType & getOptColWr (bool init=true,bool array=true)
    { return *static_cast<typename Traits<N>::ArrayType *>
          ( (!init || hasOptCol(N)) ? writeOptCol(N) : initOptCol(N,array) ); }
  
  const DMI::NumArray::Ref & getOptColRef (int icol) const
    { Assert(hasOptCol(icol)); return optcol_[icol].ref; }

  template<int N>
  typename Traits<N>::ArrayType & initOptCol (bool array=true)
    { return *static_cast<typename Traits<N>::ArrayType *>
        ( initOptCol(N,array) ); }

  void setOptCol (uint icol,const DMI::NumArray *parr,int dmiflags=0)
    { doSetOptCol(icol,const_cast<DMI::NumArray*>(parr),dmiflags|DMI::READONLY); }
    
  void setOptCol (uint icol,DMI::NumArray *parr,int dmiflags=0)
    { doSetOptCol(icol,parr,dmiflags); }
  
  void setOptCol (uint icol,const DMI::NumArray::Ref::Xfer & ref);
  
  void clearOptCol (int icol);
  
  template<int N>
  void clearOptCol () { clearOptCol(N); }
  
  // ------------------------ FAIL RECORDS
  // A VellSet may be a Fail. A Fail will not contain any values or 
  // perturbations, but rather a field of 1+ fail records.
    
  // This marks the Result as a FAIL, and adds a fail-record.
  // All values and perturbations are cleared, and a Fail field is 
  // created if necessary.
    //##ModelId=400E53550393
  void addFail (const DMI::Record *rec,int flags=0);
    //##ModelId=400E53550399
  void addFail (const string &nodename,const string &classname,
                const string &origin,int origin_line,const string &msg);
//#if defined(HAVE_PRETTY_FUNCTION)
//# define MeqResult_FailLocation __PRETTY_FUNCTION__ "() " __FILE__ 
//#elif defined(HAVE_FUNCTION)
//# define MeqResult_FailLocation __FUNCTION__ "() " __FILE__ 
//#else
# define MeqResult_FailLocation __FILE__ 
//#endif
  
  // macro for automatically generating the correct fail location and adding
  // a fail to the resultset
#define MakeFailVellSet(res,msg) \
    (res).addFail(name(),objectType().toString(),MeqResult_FailLocation,__LINE__,msg);
    
  // checks if this VellSet is a fail
    //##ModelId=400E535503A5
  bool isFail () const
  { return is_fail_; }
  // returns the number of fail records 
    //##ModelId=400E535503A7
  int numFails () const;
  // returns the i-th fail record
    //##ModelId=400E535503A9
  const DMI::Record & getFail (int i=0) const;
  
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
    //##ModelId=400E53550302
  double default_pert_;
  
  typedef struct 
  {
    double * pert;
    DMI::Vec::Ref *   pertval_vec;
  } PerturbationSet;
  
  vector<PerturbationSet> pset_;
  
  typedef struct 
  {
    DMI::NumArray::Ref ref;
    void          *ptr;
  } OptionalColumnData;
  
  OptionalColumnData optcol_[NUM_OPTIONAL_COL];
  
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

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
#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <MEQ/TID-Meq.h>

#pragma aidgroup Meq
#pragma types #Meq::VellSet

// This class represents a result of a domain for which an expression
// has been evaluated.

namespace Meq {

class Cells;


//##ModelId=400E530400D3
class VellSet : public DataRecord
{
public:
    //##ModelId=400E530400D6
  typedef CountedRef<VellSet> Ref;

  // Create a time,frequency result for the given number of spids.
    //##ModelId=400E5355031E
  explicit VellSet (int nspid=0,int nset=1);

  // Construct from DataRecord.
    //##ModelId=400E53550322
  VellSet (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  
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

  // override privatize so that shortcut refs are detached/reattacghed 
  // automatically
    //##ModelId=400E53550333
  virtual void privatize (int flags = 0, int depth = 0);
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a VellSet is made from a DataRecord
  // (or when the underlying DataRecord is privatized, etc.)
    //##ModelId=400E5355033A
  virtual void validateContent ();
    
  // ------------------------ SPIDS AND ASSOCIATED ATTRIBUTES
  // Get the spids.
    //##ModelId=400E5355033C
  int getNumSpids() const
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
  { return getNumSpids(); }

  // Set the spids. If VellSet was created with a >0 nspids,
  // then the size of the vector must match. If VellSet was created
  // with 0 spids, this can be used to initialize the number
    //##ModelId=400E53550344
  void setSpids (const vector<int>& spids);

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

  // ------------------------ MAIN RESULT VALUE
  // Get the value.
    //##ModelId=400E5355035C
  const Vells& getValue() const
    { return value_.deref(); }
    //##ModelId=400E5355035E
  Vells& getValueRW()
    { return value_.dewr(); }

  // Attaches the given Vells to value (as an anon object)
    //##ModelId=400E53550360
  Vells & setValue (Vells *);
  // set the value to a copy of the given Vells object (Vells copy uses ref semantics!)
    //##ModelId=400E53550363
  Vells & setValue (const Vells & value) { return setValue(new Vells(value)); }

  // Allocate the value with a given type and shape.
  // It won't change if the current value type and shape match.
    //##ModelId=400E53550367
  LoMat_double& setReal (int nfreq, int ntime)
    { if( value_.valid() && value_->isCongruent(true,nfreq,ntime) )
        return value_().getRealArray();
      else
        return allocateReal(nfreq, ntime).getRealArray();
    } 
    //##ModelId=400E5355036D
  LoMat_dcomplex& setComplex (int nfreq, int ntime)
    { if( value_.valid() && value_->isCongruent(false,nfreq,ntime) )
        return value_().getComplexArray();
      else
        return allocateComplex(nfreq, ntime).getComplexArray();
    } 
    //##ModelId=400E53550375
  Vells& setValue (bool isReal, int nfreq, int ntime)
    { if( value_.valid() && value_->isCongruent(isReal,nfreq,ntime) )
        return value_();
      else if( isReal )
        return allocateReal(nfreq, ntime);
      else 
        return allocateComplex(nfreq, ntime);
    }

  // ------------------------ PERTURBED VALUES
  // Get the i-th perturbed value from set iset
    //##ModelId=400E5355037E
  const Vells& getPerturbedValue (int i,int iset=0) const
    { DbgAssert(i>=0 && i<numspids_ && iset>=0 && iset<int(pset_.size())); 
      return pset_[iset].pertval[i].deref(); }
    //##ModelId=400E53550383
  Vells& getPerturbedValueRW (int i,int iset=0)
    { DbgAssert(i>=0 && i<numspids_ && iset>=0 && iset<int(pset_.size())); 
      return pset_[iset].pertval[i].dewr(); }

  // Attaches the given Vells to i-th perturbed value of set nset (as an anon object)
    //##ModelId=400E53550387
  Vells & setPerturbedValue (int i,Vells *,int iset=0);
  // Set the i-th perturbed value (Vells copy uses ref semantics!)
    //##ModelId=400E5355038C
  Vells & setPerturbedValue (int i,const Vells & value,int iset=0)
    { return setPerturbedValue(i,new Vells(value),iset); }

  // ------------------------ FAIL RECORDS
  // A VellSet may be a Fail. A Fail will not contain any values or 
  // perturbations, but rather a field of 1+ fail records.
    
  // This marks the Result as a FAIL, and adds a fail-record.
  // All values and perturbations are cleared, and a Fail field is 
  // created if necessary.
    //##ModelId=400E53550393
  void addFail (const DataRecord *rec,int flags=DMI::ANON|DMI::NONSTRICT);
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
  const DataRecord & getFail (int i=0) const;
  
  // print VellSet to stream
    //##ModelId=400E535503AE
  void show (std::ostream&) const;

  // this disables removal of DataRecord fields via hooks
    //##ModelId=400E535503B1
  virtual int remove (const HIID &)
  { Throw("remove() from a Meq::VellSet not allowed"); }
  
protected: 
  // disable public access to some DataRecord methods that would violate the
  // structure of the container
    //##ModelId=400E535502F0
  DataRecord::remove;
    //##ModelId=400E535502F2
  DataRecord::replace;
    //##ModelId=400E535502F4
  DataRecord::removeField;
  
private:
  // Remove all shortcuts, pertubed values, etc. (Does not do anything
  // to the underlying DataRecord though)
    //##ModelId=400E535503B5
  void clear();

  void setupPertData (int iset);

  // Allocate the main value with given type and shape.
    //##ModelId=400E535503B7
  Vells & allocateReal (int nfreq, int  ntime)
    { return setValue(new Vells(double(0),nfreq,ntime,false)); }
    //##ModelId=400E535503BD
  Vells & allocateComplex (int nfreq, int ntime)
    { return setValue(new Vells(dcomplex(0),nfreq,ntime,false)); }

    //##ModelId=400E535502FC
  Vells::Ref value_;
    //##ModelId=400E53550302
  double default_pert_;
  
  typedef struct 
  {
    const double *     pert;
    vector<Vells::Ref> pertval;
    DataField::Ref     pertval_field;
  } PerturbationSet;
  
  vector<PerturbationSet> pset_;
  
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

//# Result.h: The result of an expression for a domain.
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
#include <MEQ/Vells.h>
#include <Common/lofar_vector.h>
#include <DMI/DataRecord.h>
#include <MEQ/TID-Meq.h>

#pragma aidgroup Meq
#pragma types #Meq::Result

// This class represents a result of a domain for which an expression
// has been evaluated.

namespace Meq {

class Cells;


class Result : public DataRecord
{
public:
  typedef CountedRef<Result> Ref;

  // Create a time,frequency result for the given number of spids.
  explicit Result (int nspid=0);

  // Construct from DataRecord.
  Result (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  
  // destructor
  ~Result();

  // returns the object tid  
  virtual TypeId objectType () const
  { return TpMeqResult; }
  
  // implement standard clone method via copy constructor
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Result(*this,flags,depth); }

  // override privatize so that shortcut refs are detached/reattacghed 
  // automatically
  virtual void privatize (int flags = 0, int depth = 0);
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Result is made from a DataRecord
  // (or when the underlying DataRecord is privatized, etc.)
  virtual void validateContent ();
    
  // ------------------------ SPIDS AND ASSOCIATED ATTRIBUTES
  // Get the spids.
  int getNumSpids() const
  { return itsNumSpids; }
  int getSpid (int i) const
  { return itsSpids[i]; }
  
  // nperurbed() is the same as getNumSpids
  int nperturbed() const
  { return itsNumSpids; }

  // Set the spids.
  void setSpids (const vector<int>& spids);

  // is spid defined at this position? increments index if true
  bool isDefined (int spid, int& index) const
  { return (index>=itsNumSpids  ?  false :
	    spid==itsSpids[index]  ?  index++,true : false); }

  // Get the i-th perturbed parameter.
  double getPerturbation (int i) const
  { return itsPerturbations[i]; }
  // Set the i-th perturbed parameter.
  void setPerturbation (int i, double value);
  // set all perturbations at once
  void setPerturbations (const vector<double>& spids);

  // ------------------------ MAIN RESULT VALUE
  // Get the value.
  const Vells& getValue() const
    { return itsValue.deref(); }
  Vells& getValueRW()
    { return itsValue.dewr(); }

  // Attaches the given Vells to value (as an anon object)
  Vells & setValue (Vells *);
  // set the value to a copy of the given Vells object (Vells copy uses ref semantics!)
  Vells & setValue (const Vells & value) { return setValue(new Vells(value)); }

  // Allocate the value with a given type and shape.
  // It won't change if the current value type and shape match.
  LoMat_double& setReal (int nfreq, int ntime)
    { if( itsValue.valid() && itsValue->isCongruent(true,nfreq,ntime) )
        return itsValue().getRealArray();
      else
        return allocateReal(nfreq, ntime).getRealArray();
    } 
  LoMat_dcomplex& setComplex (int nfreq, int ntime)
    { if( itsValue.valid() && itsValue->isCongruent(false,nfreq,ntime) )
        return itsValue().getComplexArray();
      else
        return allocateComplex(nfreq, ntime).getComplexArray();
    } 
  Vells& setValue (bool isReal, int nfreq, int ntime)
    { if( itsValue.valid() && itsValue->isCongruent(isReal,nfreq,ntime) )
        return itsValue();
      else if( isReal )
        return allocateReal(nfreq, ntime);
      else 
        return allocateComplex(nfreq, ntime);
    }

  // ------------------------ PERTURBED VALUES
  // Get the i-th perturbed value.
  const Vells& getPerturbedValue (int i) const
  { return itsPerturbedValues[i].deref(); }
  Vells& getPerturbedValueRW (int i)
  { return itsPerturbedValues[i].dewr(); }

  // Attaches the given Vells to i-th perturbed value (as an anon object)
  Vells & setPerturbedValue (int i,Vells *);
  // Set the i-th perturbed value (Vells copy uses ref semantics!)
  Vells & setPerturbedValue (int i, const Vells & value)
    { return setPerturbedValue(i,new Vells(value)); }

  // Set the i-th perturbed value with a given type and shape.
  // It won't change if the current value type and shape matches.
  LoMat_double& setPerturbedReal (int i, int nfreq, int ntime)
    { if( itsPerturbedValues[i].valid() && 
          itsPerturbedValues[i]->isCongruent(true,nfreq,ntime) ) 
        return itsPerturbedValues[i]().getRealArray();
      else
        return allocatePertReal(i, nfreq, ntime).getRealArray();
    }
  LoMat_dcomplex& setPerturbedComplex (int i, int nfreq, int ntime)
    { if( itsPerturbedValues[i].valid() && 
          itsPerturbedValues[i]->isCongruent(false,nfreq,ntime) ) 
        return itsPerturbedValues[i]().getComplexArray();
      else
        return allocatePertComplex(i, nfreq, ntime).getComplexArray();
    }
  Vells& setPerturbedValue (int i, bool isReal, int nfreq, int ntime)
    { if( itsPerturbedValues[i].valid() && 
          itsPerturbedValues[i]->isCongruent(isReal,nfreq,ntime) )
        return itsPerturbedValues[i]();
      else if( isReal )
        return allocatePertReal(i,nfreq, ntime);
      else 
        return allocatePertComplex(i,nfreq, ntime);
    }
    
  // ------------------------ FAIL RECORDS
  // A Result may be a Fail. A Fail will not contain any values or 
  // perturbations, but rather a field of 1+ fail records.
    
  // This marks the ResultSet as a FAIL, and adds a fail-record.
  // All values and perturbations are cleared, and a Fail field is 
  // created if necessary.
  void addFail (const DataRecord *rec,int flags=DMI::ANON|DMI::NONSTRICT);
  void addFail (const string &nodename,const string &classname,
                const string &origin,int origin_line,const string &msg);
#if defined(HAVE_PRETTY_FUNCTION)
# define MeqResult_FailLocation __PRETTY_FUNCTION__ "() " __FILE__ 
#elif defined(HAVE_FUNCTION)
# define MeqResult_FailLocation __FUNCTION__ "() " __FILE__ 
#else
# define MeqResult_FailLocation __FILE__ 
#endif
  
  // macro for automatically generating the correct fail location and adding
  // a fail to the resultset
#define MakeFailResult(res,msg) \
    (res).addFail(name(),objectType().toString(),MeqResult_FailLocation,__LINE__,msg);
    
  // checks if this Result is a fail
  bool isFail () const
  { return itsIsFail; }
  // returns the number of fail records 
  int numFails () const;
  // returns the i-th fail record
  const DataRecord & getFail (int i=0) const;
  
  // print Result to stream
  void show (std::ostream&) const;

  // this disables removal of DataRecord fields via hooks
  virtual bool remove (const HIID &)
  { Throw("remove() from a Meq::Result not allowed"); }
  
  static int nctor;
  static int ndtor;
  

protected: 
  // disable public access to some DataRecord methods that would violate the
  // structure of the container
  DataRecord::remove;
  DataRecord::replace;
  DataRecord::removeField;
  
private:
  // Remove all shortcuts, pertubed values, etc. (Does not do anything
  // to the underlying DataRecord though)
  void clear();

  // Allocate the main value with given type and shape.
  Vells & allocateReal (int nfreq, int  ntime)
    { return setValue(new Vells(double(0),nfreq,ntime,false)); }
  Vells & allocateComplex (int nfreq, int ntime)
    { return setValue(new Vells(dcomplex(0),nfreq,ntime,false)); }
  // Allocate the i-th perturbed value with given type and shape.
  Vells & allocatePertReal (int i, int nfreq, int ntime)
    { return setPerturbedValue(i,new Vells(double(0),nfreq,ntime,false)); }
  Vells & allocatePertComplex (int i, int nfreq, int ntime)
    { return setPerturbedValue(i,new Vells(dcomplex(0),nfreq,ntime,false)); }

  int    itsCount;
  Vells::Ref itsValue;
  double itsDefPert;
  
  vector<Vells::Ref> itsPerturbedValues;
  NestableContainer::Ref perturbed_ref;
  
  const double * itsPerturbations;
  const int *    itsSpids;
  int            itsNumSpids;
  
  bool itsIsFail;
};


} // namespace Meq

inline std::ostream& operator << (std::ostream& os, const Meq::Result& res)
{
  res.show(os);
  return os;
}

#endif

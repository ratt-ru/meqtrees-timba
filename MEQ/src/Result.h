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
#include <MEQ/Vells.h>
#include <Common/lofar_vector.h>
#include <iostream>
#include <DMI/DataRecord.h>
#include <MEQ/AID-Meq.h>
#include <MEQ/TID-Meq.h>

#pragma aidgroup Meq
#pragma aid Cells Value Parm Spid Index Perturbed Perturbations
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
  
  ~Result();
  
  virtual TypeId objectType () const
  { return TpMeqResult; }
  
//   // implement standard clone method via copy constructor
//   virtual CountedRefTarget* clone (int flags, int depth) const
//   { return new Result(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Result is made from a DataRecord
  // (or when the underlying DataRecord is privatized, etc.)
  virtual void validateContent ();
  
  // this disables removal of fields via hooks
  virtual bool remove (const HIID &)
  { Throw("remove() from a Meq::Result not allowed"); }

  // Get the value.
  const Vells& getValue() const
    { return itsValue.deref(); }
  Vells& getValueRW()
    { return itsValue.dewr(); }

  // Get the spids.
  int getNumSpids() const
  { return itsNumSpids; }
  int getSpid (int i) const
  { return itsSpids[i]; }
  
//  // get all spids as a vector
//  vector<int> getSpids() const;
  // Set the spids.
  void setSpids (const vector<int>& spids);

  //
  bool isDefined (int spid, int& index) const
  { return (index>=itsNumSpids  ?  false :
	    spid==itsSpids[index]  ?  index++,true : false); }

  // Get the i-th perturbed value.
  const Vells& getPerturbedValue (int i) const
  { return itsPerturbedValues[i].deref(); }

  Vells& getPerturbedValueRW (int i)
  { return itsPerturbedValues[i].dewr(); }

  // Get the i-th perturbed parameter.
  double getPerturbation (int i) const
  { return itsPerturbations[i]; }

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

  // Attaches the given Vells to value.
  Vells & setValue (Vells *);
  // Attaches the given Vells to i-th perturbed value.
  Vells & setPerturbedValue (int i,Vells *);
  
  // set the value (Vells uses ref semantics)
  Vells & setValue (const Vells & value)
    { return setValue(new Vells(value)); }
  // set the i-th perturbed value (Vells uses ref semantics)
  Vells & setPerturbedValue (int i, const Vells & value)
    { return setPerturbedValue(i,new Vells(value)); }

  // Remove all perturbed values.
  void clear();

  int nperturbed() const
  { return itsNumSpids; }

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
        return allocateReal(nfreq, ntime);
      else 
        return allocateComplex(nfreq, ntime);
    }

  // Set the i-th perturbed parameter.
  void setPerturbation (int i, double value)
    { itsPerturbations[i] = value; }

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

   // Allocate a sub-container for perturbations (if not already present),
  // return ref to it
  DataField & nc_perturbed ();

  int    itsCount;
  Vells::Ref itsValue;
//  Cells* itsCells;
  double itsDefPert;
  
  vector<Vells::Ref> itsPerturbedValues;
  double * itsPerturbations;
//  vector<double> itsParmValues;
  int * itsSpids;
  int   itsNumSpids;
  
  DataField *pnc_perturbed;
};


} // namespace Meq

#endif

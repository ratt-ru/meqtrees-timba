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
#include <MEQ/AID-MEQ.h>


#pragma aidgroup MEQ
#pragma aid Cells Values ParmValues Spids Perturbations


// This class represents a result of a domain for which an expression
// has been evaluated.

namespace MEQ {

class Cells;


class Result : public DataRecord
{
public:
  typedef CountedRef<Result> Ref;

  // Create a time,frequency result for the given number of spids.
  explicit Result (int nspid=0);

  ~Result();

  // Set or get the cells.
  void setCells (const Cells&);
  const Cells& getCells() const
    { return *itsCells; }

  // Get the value.
  const Vells& getValue() const
    { return itsValue; }
  Vells& getValueRW()
    { return itsValue; }

  // Get the spids.
  const vector<int>& getSpids() const
    { return itsSpids; }

  bool isDefined (int spid, int& index) const
  { return (index>=int(itsSpids.size())  ?  false :
	    spid==itsSpids[index]  ?  index++,true : false); }

  // Get the i-th perturbed value.
  const Vells& getPerturbedValue (int i) const
    { return *(itsPerturbedValues[i]); }

  Vells& getPerturbedValueRW (int i)
    { return *(itsPerturbedValues[i]); }

  // Get the i-th perturbed parameter.
  double getPerturbation (int i) const
    { return (itsPerturbations[i]); }

  // Allocate the value with a given type and shape.
  // It won't change if the current value type and shape match.
  LoMat_double& setReal (int nfreq, int ntime)
    { if (!itsValue.isReal()
      ||  itsValue.nx() != nfreq
      ||  itsValue.ny() != ntime) {
        allocateReal (nfreq, ntime);
      }
      return itsValue.getRealArray();
    } 
  LoMat_dcomplex& setComplex (int nfreq, int ntime)
    { if (itsValue.isReal()
      ||  itsValue.nx() != nfreq
      ||  itsValue.ny() != ntime) {
        allocateComplex (nfreq, ntime);
      }
      return itsValue.getComplexArray();
    } 
  Vells& setValue (bool isReal, int nfreq, int ntime)
    { if (isReal) {
        setReal (nfreq, ntime);
      } else {
        setComplex (nfreq, ntime);
      }
      return itsValue;
    }

  // Set the value to the given value.
  void setValue (const Vells& value);

  // Remove all perturbed values.
  void clear();

  int nperturbed() const
    { return itsPerturbations.size(); }

  // Set the i-th parm value.
  void setParmValue (int i, const Vells&);

  // Set the i-th perturbed value with a given type and shape.
  // It won't change if the current value type and shape matches.
  LoMat_double& setPerturbedReal (int i, int nfreq, int ntime)
    { if (!itsPerturbedValues[i]  ||  !itsPerturbedValues[i]->isReal()
      ||  itsPerturbedValues[i]->nx() != nfreq
      ||  itsPerturbedValues[i]->ny() != ntime) {
        allocatePertReal (i, nfreq, ntime);
      }
      return itsPerturbedValues[i]->getRealArray();
    } 
  LoMat_dcomplex& setPerturbedComplex (int i, int nfreq, int ntime)
    { if (!itsPerturbedValues[i]  ||  itsPerturbedValues[i]->isReal()
      ||  itsPerturbedValues[i]->nx() != nfreq
      ||  itsPerturbedValues[i]->ny() != ntime) {
        allocatePertComplex (i, nfreq, ntime);
      }
      return itsPerturbedValues[i]->getComplexArray();
    } 
  Vells& setPerturbedValue (int i, bool isReal, int nfreq, int ntime)
    { if (isReal) {
        setPerturbedReal (i, nfreq, ntime);
      } else {
        setPerturbedComplex (i, nfreq, ntime);
      }
      return *(itsPerturbedValues[i]);
    }

  // Set the i-th perturbed value.
  void setPerturbedValue (int i, const Vells&);

  // Set the i-th perturbed parameter.
  void setPerturbation (int i, double value)
    { itsPerturbations[i] = value; }

  void show (std::ostream&) const;

  static int nctor;
  static int ndtor;

private:
  // Forbid copy and assignment.
  Result (const Result&);
  Result& operator= (const Result&);

  // Allocate the main value with given type and shape.
  void allocateReal (int nfreq, int  ntime);
  void allocateComplex (int nfreq, int ntime);
  // Allocate the i-th perturbed value with given type and shape.
  void allocatePertReal (int i, int nfreq, int ntime);
  void allocatePertComplex (int i, int nfreq, int ntime);

  int    itsCount;
  Vells  itsValue;
  Cells* itsCells;
  double itsDefPert;
  vector<Vells*> itsPerturbedValues;
  vector<double> itsPerturbations;
  vector<double> itsParmValues;
  vector<int>    itsSpids;
};


} // namespace MEQ

#endif

//# Polc.h: Ordinary polynomial with coefficients valid for a given domain.
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

#ifndef MEQ_POLC_H
#define MEQ_POLC_H

//# Includes
#include <MEQ/Funklet.h>

#include <MEQ/TID-Meq.h>
#pragma aidgroup Meq
#pragma type #Meq::Polc

// This class implements a Polc funklet --
// an ordinary 1/2-dim polynomial with real coefficients.

namespace Meq {

const int    MaxPolcRank = 2;
const double defaultPolcPerturbation = defaultFunkletPerturbation;
const double defaultPolcWeight = defaultFunkletWeight;
extern const int    defaultPolcAxes[MaxPolcRank];
extern const double defaultPolcOffset[MaxPolcRank];
extern const double defaultPolcScale[MaxPolcRank];


//##ModelId=3F86886E01F6
class Polc : public Funklet
{
public:
  typedef CountedRef<Polc> Ref;

  //------------------ constructors -------------------------------------------------------
  explicit Polc (double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,DbId id=-1);
    
    //##ModelId=3F86886F0366
  explicit Polc(double c00,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(const LoVec_double &coeff,
                int iaxis=0,double x0=0,double xsc=1,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(const LoMat_double &coeff,
                const int    iaxis[]  = defaultPolcAxes,
                const double offset[] = defaultPolcOffset,
                const double scale[]  = defaultPolcScale,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(DataArray *pcoeff,
                const int    iaxis[]  = defaultPolcAxes,
                const double offset[] = defaultPolcOffset,
                const double scale[]  = defaultPolcScale,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  //##ModelId=400E5354033A
  Polc (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  
  //------------------ various member access methods --------------------------------------
    //##ModelId=3F86886F0373
  void setCoeff (double c00);
  void setCoeff (const LoVec_double & coeff);
  void setCoeff (const LoMat_double & coeff);
  
  // Get number of coefficients.
    //##ModelId=3F86886F036F
  int ncoeff() const
  { return coeff_->size(); }
  // Get rank of polynomial
  // Get shape of coefficients
  const LoShape & getCoeffShape () const
  { return coeff_->shape(); };
  
  // Get c00 coefficient
  double getCoeff0 () const
  { return *static_cast<const double*>(coeff_->getConstDataPtr()); }
  
  // Get vector or matrix of coeffs (exception if this does not match shape)
  const LoVec_double & getCoeff1 () const
  { return coeff_->getConstArray<double,1>(); }
  
  const LoMat_double & getCoeff2 () const
  { return coeff_->getConstArray<double,2>(); }

  //------------------ implement public Funklet interface ---------------------------------
  // returns the number of parameters describing this funklet
  virtual int getNumParms () const
  { return coeff_->size(); }
  
  // returns max rank for funklets of this type
  virtual int maxFunkletRank () const
  { return MaxPolcRank; }
  
  // returns true if funklet has no dependence on domain (e.g.: a single {c00} polc)
  virtual bool isConstant () const 
  { return ncoeff()<=1; }
  
  //------------------ standard DMI-related methods ---------------------------------------
  virtual TypeId objectType () const
  { return TpMeqPolc; }
  
  // implement standard clone method via copy constructor
    //##ModelId=400E53550131
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Polc(*this,flags,depth); }
  
  virtual void privatize (int flags=0,int depth=0);
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Polc is made from a DataRecord
  // (or when the underlying DataRecord is privatized, etc.)
    //##ModelId=400E53550156
  virtual void validateContent ();
  virtual void revalidateContent ();

protected:
  //------------------ implement protected Funklet interface ---------------------------------
  virtual void do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const;

  virtual void do_update (const double values[],const std::vector<int> &spidIndex);

  //------------------ end of protected Funklet interface ------------------------------------
    
  // disable public access to some DataRecord methods that would violate the
  // structure of the container
    //##ModelId=400E535500A0
  DataRecord::remove;
    //##ModelId=400E535500A8
  DataRecord::replace;
    //##ModelId=400E535500AF
  DataRecord::removeField;
  
private:
  static const int MaxNumPerts = 2;

    //##ModelId=3F86BFF80221
  DataArray::Ref      coeff_;
  
};
  
} // namespace Meq

#endif

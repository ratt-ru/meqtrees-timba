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
#include <MEQ/Domain.h>
#include <MEQ/Vells.h>
#include <MEQ/VellSet.h>

#include <MEQ/TID-Meq.h>
#pragma aidgroup Meq
#pragma type #Meq::Polc

//# Forward declarations
template<class T> class Matrix;

// This class contains an ordinary 2-dim with real coefficients.
// It is valid for the given domain only.
// The domain is scaled between -1 and 1 to avoid large values for
// the high order terms. The coefficients are valid for the scaled
// domain.
// The coefficients are numbered 0..N with the time as the most rapidly
// varying axis.

namespace Meq {
class Request;


const int    maxPolcRank = 2;
const double defaultPolcPerturbation = 1e-6;
const double defaultPolcWeight = 1;
extern const int    defaultPolcAxes[maxPolcRank];
extern const double defaultPolcOffset[maxPolcRank];
extern const double defaultPolcScale[maxPolcRank];


//##ModelId=3F86886E01F6
class Polc : public DataRecord
{
public:
  typedef CountedRef<Polc> Ref;
  typedef int DbId;

  Polc ();
    
    //##ModelId=3F86886F0366
  explicit Polc(double c00,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(const LoVec_double &coeff,
                int iaxis=0,double x0=0,double xsc=1,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(const LoMat_double &coeff,
                const int    iaxis[]     = defaultPolcAxes,
                const double offset[] = defaultPolcOffset,
                const double scale[]     = defaultPolcScale,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(DataArray *pcoeff,
                const int    iaxis[]     = defaultPolcAxes,
                const double offset[] = defaultPolcOffset,
                const double scale[]     = defaultPolcScale,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
    //##ModelId=400E5354033A
  Polc (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  
//   explicit Polc(const Vells &coeff,double freq0=0,double freqsc=1,
//                 double time0=0,double timesc=1,
//                 double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
//                 DbId id=-1);
  
  // sets all of a polc's axes and attributes in one go
  void init (int rank,
             const int iaxis[] = defaultPolcAxes,
             const double offset[] = defaultPolcOffset,
             const double scale[] = defaultPolcScale,
             double pert = defaultPolcPerturbation,
             double weight = defaultPolcWeight,
             DbId id=-1);
  
  
  // Set the domain to which this polc applies.
  void setDomain (const Domain* domain,int flags);
    //##ModelId=3F86886F038C
  void setDomain (const Domain& domain)
  { setDomain(&domain,0); }
  // Get the domain.
    //##ModelId=3F86886F038A
  const Domain & domain() const
  { return domain_.valid() ? *domain_ : default_domain; }

  // sets up an axis of variability
  void setAxis (int i,int iaxis,double offset=0,double scale=1);

  // returns axis of variability
  int    getAxis (int i) const {
    FailWhen(i<0 || i>=rank(),"illegal Meq::Polc axis");
    return axes_[i]; 
  }
  
  double getOffset (int i) const {
    FailWhen(i<0 || i>=rank(),"illegal Meq::Polc axis");
    return offsets_[i]; 
  }
  
  double getScale (int i) const {
    FailWhen(i<0 || i>=rank(),"illegal Meq::Polc axis");
    return scales_[i]; 
  }

  // Set the coefficients. The mask is set to all true.
    //##ModelId=3F86886F0373
  void setCoeff (double c00);
  void setCoeff (const LoVec_double & coeff);
  void setCoeff (const LoMat_double & coeff);
  
  // Get number of coefficients.
    //##ModelId=3F86886F036F
  int ncoeff() const
  { return coeff_->size(); }
  // Get rank of polynomical
  int rank () const
  { return rank_; }
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
  
  // shortcut for using the grid in the request
    //##ModelId=400E53540350
  void evaluate (VellSet &,const Request &) const;
  void evaluate (VellSet &,const Cells &,int deriv=0) const;

  // Get the perturbation.
    //##ModelId=3F86886F0396
  double getPerturbation(int ipert=0) const
  { DbgAssert(ipert==0 || ipert==1); return ipert ? -pertValue_ : pertValue_ ; }
    //##ModelId=3F86886F039A
  void setPerturbation (double perturbation = defaultPolcPerturbation);
  
  Polc::DbId getDbId () const
  { return id_; }
  void setDbId (DbId id);
  
  double getWeight() const
  { return weight_; }
  void setWeight (double weight);

  // Make the polynomial non-solvable.
    //##ModelId=3F86886F03A4
  void clearSolvable();

  // Make the parameters solvable, thus perturbed values have to be calculated.
  // spidIndex is the index of the first spid of this polc.
  // It returns the number of spids in this polc.
    //##ModelId=3F86886F03A6
  int makeSolvable (int spidIndex);

//   // Get the current values of the solvable parameter and store them
//   // in the argument.
//     //##ModelId=3F86886F03AC
//   void getInitial (Vells& values) const;
// 
//   // Get the current value of the solvable parameter and store it
//   // in the argument.
//     //##ModelId=3F86886F03B3
//   void getCurrentValue (Vells& value, bool denormalize) const;

  // Update the solvable parameters with the new values.
  // It returns the number of values used.
    //##ModelId=3F86886F03BE
  uint update (const double* values, uint nrval);

  // Get the spids.
  //##ModelId=400E53540373
  const vector<int> getSpids() const
    { return spids_; }
  
  
  


  // standard methods follow  
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


protected:
  // disable public access to some DataRecord methods that would violate the
  // structure of the container
    //##ModelId=400E535500A0
  DataRecord::remove;
    //##ModelId=400E535500A8
  DataRecord::replace;
    //##ModelId=400E535500AF
  DataRecord::removeField;
  
private:
  // Calculate the value and possible perturbations (deriv>0)
  // for the given grid. The grid is already normalized.
  void evaluate (VellSet &,const Vells::Shape &vshape,
                 const LoVec_double grid[],int deriv=0) const;
  
//  // Fill Pascal's triangle.
//    //##ModelId=3F868870002F
//  static void fillPascal();

  static const int MaxNumPerts = 2;

    //##ModelId=3F86BFF80221
  int                 rank_;
  DataArray::Ref      coeff_;
  LoShape             shape_;
  // axes of variability
  std::vector<int>    axes_;
  // offsets
  std::vector<double> offsets_;
  std::vector<double> scales_;
  
    //##ModelId=3F86BFF8023F
  // perturbation values
  std::vector<double> perturbation_;
    //##ModelId=3F86BFF8024A
  // domain over which this polc is valid
  // Any missing axes in the domain imply that polc is valid for that entire dimension
  CountedRef<Domain>  domain_;
  
  
//  std::vector<bool> mask_;
    //##ModelId=3F86886F0324
  std::vector<int>  spidInx_;     //# -1 is not solvable
    //##ModelId=400E53540331
  std::vector<int>  spids_;
    //##ModelId=3F86886F032B
  int          nrSpid_;
    //##ModelId=3F86886F0333
  double       pertValue_;
    //##ModelId=3F86886F0341
  
  double       weight_;
  
  int          id_;
  
  static Domain default_domain;

//   //# Pascal's triangle for the binomial coefficients needed when normalizing.
//     //##ModelId=3F86886F0357
//   static double theirPascal[10][10];
//     //##ModelId=3F86886F035E
//   static bool   theirPascalFilled;
};

} // namespace Meq

#endif

//# Funklet.h: Base class for parm funklets
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

#ifndef MEQ_FUNKLET_H
#define MEQ_FUNKLET_H

//# Includes
#include <MEQ/Domain.h>
#include <MEQ/Result.h>
#include <DMI/NumArray.h>
#include <DMI/List.h>
#include <MEQ/MeqVocabulary.h>

#include <MEQ/TID-Meq.h>

#pragma aidgroup Meq
#pragma type #Meq::Funklet

namespace Meq { 
  
class Request;
class VellSet;

const double defaultFunkletPerturbation = 1e-6;
const double defaultFunkletWeight = 1;
const int defaultFunkletRank = 2;

extern const int    defaultFunkletAxes[defaultFunkletRank];
extern const double defaultFunkletOffset[defaultFunkletRank];
extern const double defaultFunkletScale[defaultFunkletRank];


static double logfac(int n)
{
  // calculates log of n factorial
  double fac=0.;
  for(int i=n;i>0;i--)
    fac += log(i);
  
  return fac;
}

static double noverm(int n, int m)
{
  //calculates  n over m
  double result;
  result=logfac(n)-logfac(m)-logfac(n-m);
  return exp(result);

}

class Funklet : public DMI::Record
{
public:
  typedef DMI::CountedRef<Funklet> Ref;
  typedef int DbId;
  
  // maximum # of perturbation sets passed to evaluate() below
  static const int MaxNumPerts = 2;

  //------------------ constructors -------------------------------------------------------
    //##ModelId=3F86886F0366
  explicit Funklet (double pert=defaultFunkletPerturbation,
                    double weight=defaultFunkletWeight,
                    DbId id=-1);
  
  Funklet (int naxis,const int iaxis[]=defaultFunkletAxes,const double offset[]=defaultFunkletOffset,const double scale[]=defaultFunkletScale,
           double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
           DbId id=-1);
  
  Funklet (const Funklet &other,int flags=0,int depth=0);
  // sets all of a funklet's attributes in one go
  void init (int naxis,const int iaxis[],const double offset[],const double scale[],
             double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
             DbId id=-1);


  //------------------ standard member access ---------------------------------------------
  // Set the domain to which this funklet applies.
  void setDomain (const Domain* domain,int flags=0);
  
  void setDomain (const Domain& domain,int flags=DMI::AUTOCLONE)
  { setDomain(&domain,flags); }
  
  // true if domain is set
  bool hasDomain () const
  { return domain_.valid(); }
  
  // Gets the domain.
  const Domain & domain() const
  { return domain_.valid() ? *domain_ : default_domain; }

  void setRank(int rank);

  // returns "rank" of funklet (normally, the number of variability axes)
  int rank () const
  { return axes_.size(); }
  
  // sets up an axis of variability
  void setAxis (int i,int iaxis,double offset=0.,double scale=1.);

  // returns axis of variability
  int getAxis (int i) const {
    return axes_[i]; 
  }

  const std::vector<int> getAxes() {
    return axes_;
  }


  // sets offset along axis of variability
  int setOffset (int i, double offset) {
    if( offsets_.size()<=uint(i)){
      cdebug(2)<<" cannot set offset, no default defined ..."<<endl;
      return 0;
    }

    offsets_[i]= offset; 
    (*this)[FOffset]    = offsets_;
    return 1;
  }

  // sets scale along axis of variability
  int setScale (int i, double scale) {
    if( scales_.size()<=uint(i)){
      cdebug(2)<<" cannot set scale, no default defined ..."<<endl;
      return 0;
    }

    scales_[i]= scale; 
    (*this)[FScale]     = scales_;
    return 1;
  }
  // returns offset along axis of variability
  double getOffset (int i) const {
    return offsets_[i]; 
  }
  // returns scale along axis of variability
  double getScale (int i) const {
    return scales_[i]; 
  }

  // get/set the base perturbation.
  double getPerturbation(int ipert=0) const
  { DbgAssert(ipert==0 || ipert==1); return ipert ? -pertValue_ : pertValue_ ; }
  void setPerturbation (double perturbation = defaultFunkletPerturbation);
  
  // get/set database id
  Funklet::DbId getDbId () const
  { return id_; }
  void setDbId (DbId id);
  
  // get/set weight
  double getWeight() const
  { return weight_; }
  void setWeight (double weight);

  //------------------ public Funklet interface (to be implemented by subclasses) ---------
  // returns the number of parameters describing this funklet
  virtual int getNumParms () const
  { return ncoeff();}//spids_.empty()?ncoeff():spids_.size(); }
  
  // returns max rank for funklets of this type
  virtual int maxFunkletRank () const
  { return Axis::MaxAxis; }
  
  // returns true if funklet has no dependence on domain (e.g.: a single {c00} polc)
  virtual bool isConstant () const 
  { return false; }
  
  //------------------ other Funklet methods ----------------------------------------------
  // evaluate method: evaluates funklet over a given cells. Sets up vellset and calls
  // the private virtual do_evaluate() below.
  void evaluate (VellSet &,const Cells &,int makePerturb=0) const;
   // shortcut to above taking a Request
  void evaluate (VellSet &,const Request &) const;
  // evaluate funket on given cells, in case parm has children that (partially) define the grid 
  void evaluate (VellSet &,const Cells &, const std::vector<Result::Ref> & childres,int makePerturb=0) const;
  // shortcut to evaluate funket on given cells, in case parm has children that (partially) define the grid 
  void evaluate (VellSet &,const Request &, const std::vector<Result::Ref> & childres) const;
  
  // Make the funklet non-solvable.
  void clearSolvable();
  
  // Is this funklet currently solvable?
  bool isSolvable () const
  { return !spids_.empty(); }

  // Make the entire funklet solvable, thus perturbed values have to be calculated.
  // spidIndex0 is the index of the first spid of this funklet, the rest are assigned
  // contiguously. 
  // Returns the number of spids in this funklet (==getNumParms())
    //##ModelId=3F86886F03A6
  virtual int makeSolvable (int spidIndex);
  // Make the funklet solvable, but only w.r.t. a specific subset of its parameters.
  // The mask vector (must be same size as returned by getNumParms()) tells which 
  // parameters are solvable. 
  // Returns the number of spids in this funklet (==number of true values in mask)
  int makeSolvable (int spidIndex,const std::vector<bool> &mask);

  // Updates solvable parms of funklet. Size of values must be equal to the number 
  // of solvable parms.
  void update (const double values[],bool force_positive=false);
  // Updates solvable parms of funklet. Size of values must be equal to the number 
  // of solvable parms. constraints, only valid for constant funklets, should be vector of min,max
  void update (const double values[],const std::vector<double> &contraints,bool force_positive=false);

  void update (const double values[],const std::vector<double> &contraints_min,const std::vector<double> &contraints_max,bool force_positive=false);


  // Get vector of parm perturbations (set up by the makeSolvable() methods above)
  // There is one for each parameter; thus its size is getNumParms().
  const std::vector<double> & getParmPerts() const
  { return parm_perts_; }
  
  // Get the spids -- solvable parameter IDs (set up by the makeSolvable() methods above)
  // If makeSolvable() was called w/o a mask, then there's one spid per each parm
  // (as returned by getNumParms())
  // If makeSolvable() was called with a mask, then there may be fewer spids
  const std::vector<int> & getSpids() const
  { return spids_; }

  //get number of solvable coeff
  const int getNrSpids() const
  { return spids_.size(); }
  
  // Get vector of spid perturbations (set up by the makeSolvable() methods above)
  // There is one for each spid; thus its size is same as that of getSpids()
  const std::vector<double> & getSpidPerts() const
  { return spid_perts_; }
  // get vector (size = rank )giving the index of the coefficient belong to a spididx. 
  DMI::Vec * getCoeffIndex(int spidid) const;

  //------------------ standard DMI-related methods ---------------------------------------
  virtual DMI::TypeId objectType () const
  { return TpMeqFunklet; }
  
  // implement standard clone method via copy constructor
  virtual DMI::CountedRefTarget* clone (int flags, int depth) const
  { return new Funklet(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Funklet is made from a DMI::Record
  virtual void validateContent (bool recursive);

  // this function applies to one of the axes of the funklet and is called in do_evaluate
  //  in specific subclasses of Polc
  virtual void axis_function(int axis, LoVec_double & grid) const {   }



  // Get c00 coefficient
  const double getCoeff0 () const
  { return *static_cast<const double*>(coeff().getConstDataPtr()); }
  
  // Get vector of coeffs 
  const LoVec_double & getCoeff1 () const
  { return coeff().getConstArray<double,1>(); }
  
  // Get matrix of coeffs 
  const LoMat_double & getCoeff2 () const
  { return coeff().getConstArray<double,2>(); }

  //various virtual access functions for coeefs
  virtual void setCoeff (double c00);
  virtual void setCoeff (const LoVec_double & coeff);
  virtual void setCoeff (const LoMat_double & coeff);
  virtual void setCoeff (const DMI::NumArray & coeff);
  // Get number of coefficients.
    //##ModelId=3F86886F036F
  int ncoeff() const
  { return pcoeff_ ? pcoeff_->deref().size() : 0; }
  
  // Get shape of coefficients
  const LoShape & getCoeffShape () const
  { return coeff().shape(); }
  

  virtual void setCoeffShape(const LoShape & shape)
  { 
    // to be reimplemented by polctype funklets
    cdebug(2)<<"set coeff shape only implemented for polctype funklets"<<endl;
  }

  virtual const DMI::NumArray & coeff () const
  { DbgAssert(pcoeff_); return pcoeff_->deref(); }
  
  virtual DMI::NumArray & coeffWr () const
  {DbgAssert(pcoeff_); return pcoeff_->dewr(); }
  




  //changeSolveDomain: this function determines new offsets and scales and projects the Funklet 
  // to the solveDomain (to avoid large numbers that the solvver has difficulties to deal with.
  // Typically the solvedomain = [0,1][0,1] or [-1,1][-1,1]...
  virtual void changeSolveDomain(const Domain & solveDomain){};
  virtual void changeSolveDomain(const std::vector<double> & solveDomain){};


  //reimplement in  (CompiledFunklet) since browser doesnt know about aips++ contaminated classes
  virtual Record::Ref getState(){
    Record::Ref funkref;
    funkref<<=new Record(*this);
    return funkref;
  }

  virtual string getFunction() const{
    //reset in CompiledFunklet, default is just the string of the type
    return objectType().toString();
  }

  virtual void setFunction(string funcstring){
    (*this)[FFunction] = funcstring;
   }

  virtual vector<double> getConstants () const {
        return vector<double>();
  }
  virtual void setConstants () const {
  }

protected:
  Record::protectField;  
  Record::unprotectField;  
  Record::begin;  
  Record::end;  
  Record::as;
  Record::clear;
  
  //------------------ protected Funklet interface (to be implemented by subclasses) ---------
  // do_evaluate(): this is the real workhorse.
  // Evaluates funklet over a given cells. This is called by public evaluate() above 
  // after setting up the vellset properly (i.e. assigning spids and perturbations to it, 
  // etc., so the implementation here need not worry).
  // The perts argument is a vector of perturbations: _one per parameter_ (i.e. 
  // getNumParms() in length). 
  // The spidIndex argument is a vector of spid positions: _one per parameter_.
  // For each parm marked as solvable, it contains the index at which the corresponding
  // perturbed value is to be placed into the VellSet. Non-solvable parms (which may 
  // exist if makeSolvable() with a mask was used) have an index of -1.
  // makePerturbed argument is 0 for no perturbations, 1 for single, 2 for double. 
  // For double-perts, a perturbation value of -perts should be used.
  //Two versions are available, if childres is specified, the grid is already defined by he parms children


  virtual void do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const;

 

  //This one not implemented yet
  void do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
			    const std::vector<Result::Ref> & childres,
                            int makePerturbed) const;
                            
  // Update the solvable parameters with the new values. Called by public update(). 
  // spidIndex has the same meaning as for do_evaluate(): for each solvable parm,
  // it gives the index of its updated in values[]; for each non-solvable parm,
  // a -1
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,bool force_positive=false);
  // Update the solvable parameters with the new values. Called by public update(). 
  // spidIndex has the same meaning as for do_evaluate(): for each solvable parm,
  // it gives the index of its updated in values[]; for each non-solvable parm,
  // a -1. Constrained (only for constant funklets)
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints,bool force_positive=false);
  //
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints_min,const std::vector<double> &constraints_max,bool force_positive=false);
  
  // This method is called when a Funklet is marked as solvable (by makeSolvable() above).
  // This should fill the perts vector (which has been pre-sized to getNumParms()) with
  // perturbation values based on the "basis" perturbation pert0.
  // Default version uses the same perturbation for all parameters, but specialized
  // funklets may want to redefine this, to use, e.g., smaller perts for higher-order
  // coefficients
  virtual void calcPerturbations (std::vector<double> &perts,double pert0) const
  { perts.assign(perts.size(),pert0); }

  //------------------ other protected methods -----------------------------------------------
  Funklet (const DMI::Record &other,int flags=0,int depth=0);
  DMI::NumArray::Ref * pcoeff_;
  virtual void transformCoeff(const std::vector<double> & newoffsets,const std::vector<double> & newscales)
  {}


private:
  //------------------ data members ----------------------------------------------------------
  // axes of variability
  std::vector<int>    axes_;
  // offsets and scales
  std::vector<double> offsets_;
  std::vector<double> scales_;
  
  // domain over which this funklet is valid
  // Any missing axes in the domain imply that the funklet is valid for that 
  // entire dimension
  DMI::CountedRef<Domain>  domain_;
  
  //##ModelId=400E53540331
  std::vector<int>  spids_;
  std::vector<int>  spidInx_;
  
  std::vector<double> parm_perts_;
  std::vector<double> spid_perts_;

  // default perturbation value
  double       pertValue_;
  //##ModelId=3F86886F0341
  
  // default weight
  double       weight_;
  
  // default database ID
  int          id_;
  
  // default domain (common to all funklet objects)
  static Domain default_domain;
};

} // namespace Meq
#endif

//# Funklet.h: Base class for parm funklets
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

#ifndef MEQ_FUNKLET_H
#define MEQ_FUNKLET_H

//# Includes
#include <MEQ/Domain.h>
#include <MEQ/Vells.h>
#include <MEQ/VellSet.h>

#include <MEQ/TID-Meq.h>
#pragma aidgroup Meq
#pragma type #Meq::Funklet

namespace Meq {
class Request;

const double defaultFunkletPerturbation = 1e-6;
const double defaultFunkletWeight = 1;

//##ModelId=3F86886E01F6
class Funklet : public DataRecord
{
public:
  typedef CountedRef<Funklet> Ref;
  typedef int DbId;
  
  // maximum # of perturbation sets passed to evaluate() below
  static const int MaxNumPerts = 2;

  //------------------ constructors -------------------------------------------------------
    //##ModelId=3F86886F0366
  explicit Funklet (double pert=defaultFunkletPerturbation,
                    double weight=defaultFunkletWeight,
                    DbId id=-1);
  
  Funklet (int naxis,const int iaxis[],const double offset[],const double scale[],
           double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
           DbId id=-1);
  
  // sets all of a funklet's attributes in one go
  void init (int naxis,const int iaxis[],const double offset[],const double scale[],
             double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
             DbId id=-1);

  //------------------ standard member access ---------------------------------------------
  // Set the domain to which this funklet applies.
  void setDomain (const Domain* domain,int flags);
  void setDomain (const Domain& domain)
  { setDomain(&domain,0); }
  
  // true if domain is set
  bool hasDomain () const
  { return domain_.valid(); }
  
  // Gets the domain.
  const Domain & domain() const
  { return domain_.valid() ? *domain_ : default_domain; }

  // returns "rank" of funklet (normally, the number of variability axes)
  int rank () const
  { return axes_.size(); }
  
  // sets up an axis of variability
  void setAxis (int i,int iaxis,double offset=0,double scale=1);

  // returns axis of variability
  int getAxis (int i) const {
    return axes_[i]; 
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
  { return 0; }
  
  // returns max rank for funklets of this type
  virtual int maxFunkletRank () const
  { return Axis::MaxAxis; }
  
  // returns true if funklet has no dependence on domain (e.g.: a single {c00} polc)
  virtual bool isConstant () const 
  { return False; }
  
  //------------------ other Funklet methods ----------------------------------------------
  // evaluate method: evaluates funklet over a given cells. Sets up vellset and calls
  // the private virtual do_evaluate() below.
  void evaluate (VellSet &,const Cells &,int makePerturb=0) const;
   // shortcut to above taking a Request
  void evaluate (VellSet &,const Request &) const;
  
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
  int makeSolvable (int spidIndex);
  // Make the funklet solvable, but only w.r.t. a specific subset of its parameters.
  // The mask vector (must be same size as returned by getNumParms()) tells which 
  // parameters are solvable. 
  // Returns the number of spids in this funklet (==number of true values in mask)
  int makeSolvable (int spidIndex,const std::vector<bool> &mask);

  // Updates solvable parms of funklet. Size of values must be equal to the number 
  // of solvable parms.
  void update (const double values[]);

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
  
  // Get vector of spid perturbations (set up by the makeSolvable() methods above)
  // There is one for each spid; thus its size is same as that of getSpids()
  const std::vector<double> & getSpidPerts() const
  { return spid_perts_; }
  
  //------------------ standard DMI-related methods ---------------------------------------
  virtual TypeId objectType () const
  { return TpMeqFunklet; }
  
  // implement standard clone method via copy constructor
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Funklet(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Funklet is made from a DataRecord
  virtual void validateContent ();
  // ...and when the underlying DataRecord is privatized
  virtual void revalidateContent ();


protected:
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
  virtual void do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const;
                            
  // Update the solvable parameters with the new values. Called by public update(). 
  // spidIndex has the same meaning as for do_evaluate(): for each solvable parm,
  // it gives the index of its updated in values[]; for each non-solvable parm,
  // a -1
  virtual void do_update (const double values[],const std::vector<int> &spidIndex);
  
  // This method is called when a Funklet is marked as solvable (by makeSolvable() above).
  // This should fill the perts vector (which has been pre-sized to getNumParms()) with
  // perturbation values based on the "basis" perturbation pert0.
  // Default version uses the same perturbation for all parameters, but specialized
  // funklets may want to redefine this, to use, e.g., smaller perts for higher-order
  // coefficients
  virtual void calcPerturbations (std::vector<double> &perts,double pert0) const
  { perts.assign(perts.size(),pert0); }

  //------------------ other protected methods -----------------------------------------------
  Funklet (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);

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
  CountedRef<Domain>  domain_;
  
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

  // disable public access to some DataRecord methods that would violate the
  // structure of the container
    //##ModelId=400E535500A0
  DataRecord::remove;
    //##ModelId=400E535500A8
  DataRecord::replace;
    //##ModelId=400E535500AF
  DataRecord::removeField;
};

} // namespace Meq

#endif

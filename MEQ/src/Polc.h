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

const double defaultPolcPerturbation = 1e-6;
const double defaultPolcWeight = 1;


//##ModelId=3F86886E01F6
class Polc : public DataRecord
{
public:
  typedef CountedRef<Polc> Ref;
  typedef int DbId;

  Polc ();
    
    //##ModelId=3F86886F0366
  explicit Polc(double c00,double freq0=0,double freqsc=1,
                double time0=0,double timesc=1,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(LoMat_double coeff,double freq0=0,double freqsc=1,
                double time0=0,double timesc=1,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(DataArray *parr,double freq0=0,double freqsc=1,
                double time0=0,double timesc=1,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(const Vells &coeff,double freq0=0,double freqsc=1,
                double time0=0,double timesc=1,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  // sets all of a polc's attributes in one go
  void setEverything (double freq0,double freqsc,double time0,double timesc,
                      double pert,double weight,DbId id);
  
    //##ModelId=400E5354033A
  Polc (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  
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


  // Calculate the value and possible perturbations (deriv>0)
  // for the given grid
  void evaluate (VellSet &,const LoVec_double &xgrid,
                 const LoVec_double &ygrid,int deriv=0) const;
  
  // shortcut for using the grid in the request
    //##ModelId=400E53540350
  void evaluate (VellSet &,const Request&) const;

  // Get number of coefficients.
    //##ModelId=3F86886F036F
  int ncoeff() const
    { return itsCoeff.nelements(); }

  // Get the coefficients.
    //##ModelId=3F86886F0371
  const Vells& getCoeff() const
    { return itsCoeff; }

  // Set the coefficients. The mask is set to all true.
    //##ModelId=3F86886F0373
  void setCoeff (const Vells& coeff);

  // Get the domain.
    //##ModelId=3F86886F038A
  const Domain & domain() const
    { return *itsDomain; }

  // Set the domain.
    //##ModelId=3F86886F038C
  void setDomain (const Domain& domain);

  // Get the perturbation.
    //##ModelId=3F86886F0396
  double getPerturbation(int ipert=0) const
    { DbgAssert(ipert==0 || ipert==1); return ipert ? -itsPertValue : itsPertValue ; }
  
    //##ModelId=3F86886F039A
  void setPerturbation (double perturbation = defaultPolcPerturbation);
  
  Polc::DbId getDbId () const
  { return itsId; }
  
  void setDbId (DbId id);
  
  double getWeight() const
    { return itsWeight; }
  
  void setWeight (double weight);

  // Make the polynomial non-solvable.
    //##ModelId=3F86886F03A4
  void clearSolvable();

  // Make the parameters solvable, thus perturbed values have to be calculated.
  // spidIndex is the index of the first spid of this polc.
  // It returns the number of spids in this polc.
    //##ModelId=3F86886F03A6
  int makeSolvable (int spidIndex);

  // Get the current values of the solvable parameter and store them
  // in the argument.
    //##ModelId=3F86886F03AC
  void getInitial (Vells& values) const;

  // Get the current value of the solvable parameter and store it
  // in the argument.
    //##ModelId=3F86886F03B3
  void getCurrentValue (Vells& value, bool denormalize) const;

  // Update the solvable parameters with the new values.
  // It returns the number of values used.
    //##ModelId=3F86886F03BE
  uint update (const double* values, uint nrval);

  // Set the zero-points and scales of the function.
  // <group>
    //##ModelId=3F86886F03D6
  void setFreq0 (double freq0);
    //##ModelId=3F86886F03DD
  void setTime0 (double time0);
  void setFreqScale (double freqScale);
  void setTimeScale (double timeScale);
  // </group>

  // Get the zero-points and scales of the function.
  // <group>
    //##ModelId=3F86886F03E3
  double getFreq0() const
    { return itsFreq0; }
    //##ModelId=3F86886F03E5
  double getTime0() const
    { return itsTime0; }
  double getFreqScale() const
    { return itsFreqScale; }
  double getTimeScale() const
    { return itsTimeScale; }
  // </group>

  // Change scale and renormalize the coefficients 
    //##ModelId=3F8688700008
  void renormalize (double freq0,double freqscale,double time0,double timescale);

//   // Denormalize the coefficients.
//     //##ModelId=3F8688700011
//   Vells denormalize (const Vells& coeff) const;
// 
  // (De)normalize real coefficients.
    //##ModelId=3F8688700019
  static Vells normDouble (const Vells& coeff, double sx,
			   double sy, double ox, double oy);

  // Get the spids.
    //##ModelId=400E53540373
  const vector<int> getSpids() const
    { return itsSpids; }

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
  // Fill Pascal's triangle.
    //##ModelId=3F868870002F
  static void fillPascal();

  static const int MaxNumPerts = 2;

    //##ModelId=3F86BFF80221
  Vells        itsCoeff;
    //##ModelId=3F86BFF8023F
  // perturbation values
  std::vector<double> itsPerturbation;
    //##ModelId=3F86BFF8024A
  const Domain * itsDomain;
  
//  std::vector<bool> itsMask;
    //##ModelId=3F86886F0324
  std::vector<int>  itsSpidInx;     //# -1 is not solvable
    //##ModelId=400E53540331
  std::vector<int>  itsSpids;
    //##ModelId=3F86886F032B
  int          itsNrSpid;
    //##ModelId=3F86886F0333
  double       itsPertValue;
    //##ModelId=3F86886F0341
  double       itsFreq0;
    //##ModelId=3F86886F0348
  double       itsTime0;
  double       itsFreqScale;
  double       itsTimeScale;
  
  double       itsWeight;
  
  int          itsId;

  //# Pascal's triangle for the binomial coefficients needed when normalizing.
    //##ModelId=3F86886F0357
  static double theirPascal[10][10];
    //##ModelId=3F86886F035E
  static bool   theirPascalFilled;
};

} // namespace Meq

#endif

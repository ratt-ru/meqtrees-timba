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


//##ModelId=3F86886E01F6
class Polc
{
public:
  // Create an empty 2-dim polynomial.
  // By default a relative perturbation of 10^-6 is used.
    //##ModelId=3F86886F0366
  Polc();

  //  Create from a DataRecord
    //##ModelId=400E5354033A
  Polc (DataRecord &rec);
  
  //  Export to a DataRecord
    //##ModelId=400E53540345
  void fillRecord (DataRecord &rec);

  // Calculate the value and possible perturbations.
    //##ModelId=400E53540350
  void evaluate (VellSet &, const Request&);

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

  // Set the coefficients and mask.
    //##ModelId=3F86886F037A
  void setCoeff (const Vells& coeff, const Matrix<bool>& mask);

  // Set the coefficients only. The mask is left alone.
    //##ModelId=3F86886F0384
  void setCoeffOnly (const Vells& coeff);

  // Get the domain.
    //##ModelId=3F86886F038A
  const Domain& domain() const
    { return itsDomain; }

  // Set the domain.
    //##ModelId=3F86886F038C
  void setDomain (const Domain& domain)
    { itsDomain = domain; }

  // Get the perturbation.
    //##ModelId=3F86886F0396
  double getPerturbation() const
    { return itsPertValue; }
    //##ModelId=3F86886F0398
  bool isRelativePerturbation() const
    { return itsIsRelPert; }

    //##ModelId=3F86886F039A
  void setPerturbation (double perturbation = 1e-6,
			bool isRelativePerturbation = true)
    { itsPertValue = perturbation; itsIsRelPert = isRelativePerturbation; }

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

  // Set the original simulation coefficients.
    //##ModelId=3F86886F03C4
  void setSimCoeff (const Vells& coeff)
    { itsSimCoeff = coeff; }

  // Set the perturbation of the simulation coefficients.
    //##ModelId=3F86886F03CB
  void setPertSimCoeff (const Vells& coeff)
    { itsPertSimCoeff = coeff; }

  // Get the original simulation coefficients.
    //##ModelId=3F86886F03D2
  const Vells& getSimCoeff() const
    { return itsSimCoeff; }

  // Get the perturbation of the simulation coefficients.
    //##ModelId=3F86886F03D4
  const Vells& getPertSimCoeff() const
    { return itsPertSimCoeff; }

  // Set the zero-points of the function.
    //##ModelId=3F86886F03D6
  void setFreq0 (double freq0)
    { itsFreq0 = freq0; }
    //##ModelId=3F86886F03DD
  void setTime0 (double time0)
    { itsTime0 = time0; }

  // Get the zero-point of the function.
    //##ModelId=3F86886F03E3
  double getFreq0() const
    { return itsFreq0; }
    //##ModelId=3F86886F03E5
  double getTime0() const
    { return itsTime0; }

  // Tell if the coefficients have to be normalized.
    //##ModelId=3F86886F03E7
  void setNormalize (bool normalize)
    { itsNormalized = normalize; }

  // Tell if the coefficients are normalized.
    //##ModelId=3F8688700006
  bool isNormalized() const
    { return itsNormalized; }

  // Normalize the coefficients for the given domain.
    //##ModelId=3F8688700008
  Vells normalize (const Vells& coeff, const Domain&);

  // Denormalize the coefficients.
    //##ModelId=3F8688700011
  Vells denormalize (const Vells& coeff) const;

  // (De)normalize real coefficients.
    //##ModelId=3F8688700019
  static Vells normDouble (const Vells& coeff, double sx,
			   double sy, double ox, double oy);

  // Get the spids.
    //##ModelId=400E53540373
  const vector<int> getSpids() const
    { return itsSpids; }

private:
  // Fill Pascal's triangle.
    //##ModelId=3F868870002F
  static void fillPascal();

    //##ModelId=3F86BFF80221
  Vells        itsCoeff;
    //##ModelId=3F86BFF8022A
  Vells        itsSimCoeff;
    //##ModelId=3F86BFF80235
  Vells        itsPertSimCoeff;
    //##ModelId=3F86BFF8023F
  Vells        itsPerturbation;
    //##ModelId=3F86BFF8024A
  Domain       itsDomain;
    //##ModelId=3F86886F031C
  std::vector<bool> itsMask;
    //##ModelId=3F86886F0324
  std::vector<int>  itsSpidInx;     //# -1 is not solvable
    //##ModelId=400E53540331
  std::vector<int>  itsSpids;
    //##ModelId=3F86886F032B
  int          itsNrSpid;
    //##ModelId=3F86886F0333
  double       itsPertValue;
    //##ModelId=3F86886F033A
  bool         itsIsRelPert;   //# true = perturbation is relative
    //##ModelId=3F86886F0341
  double       itsFreq0;
    //##ModelId=3F86886F0348
  double       itsTime0;
    //##ModelId=3F86886F0350
  bool         itsNormalized;  //# true = coefficients normalized to domain

  //# Pascal's triangle for the binomial coefficients needed when normalizing.
    //##ModelId=3F86886F0357
  static double theirPascal[10][10];
    //##ModelId=3F86886F035E
  static bool   theirPascalFilled;
};

} // namespace Meq

#endif

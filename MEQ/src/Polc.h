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
#include <MEQ/Result.h>

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


class Polc
{
public:
  // Create an empty 2-dim polynomial.
  // By default a relative perturbation of 10^-6 is used.
  Polc();

  // Calculate the value and possible perturbations.
  void getResult (Result &, const Request&);

  // Get number of coefficients.
  int ncoeff() const
    { return itsCoeff.nelements(); }

  // Get the coefficients.
  const Vells& getCoeff() const
    { return itsCoeff; }

  // Set the coefficients. The mask is set to all true.
  void setCoeff (const Vells& coeff);

  // Set the coefficients and mask.
  void setCoeff (const Vells& coeff, const Matrix<bool>& mask);

  // Set the coefficients only. The mask is left alone.
  void setCoeffOnly (const Vells& coeff);

  // Get the domain.
  const Domain& domain() const
    { return itsDomain; }

  // Set the domain.
  void setDomain (const Domain& domain)
    { itsDomain = domain; }

  // Get the perturbation.
  double getPerturbation() const
    { return itsPertValue; }
  bool isRelativePerturbation() const
    { return itsIsRelPert; }

  void setPerturbation (double perturbation = 1e-6,
			bool isRelativePerturbation = true)
    { itsPertValue = perturbation; itsIsRelPert = isRelativePerturbation; }

  // Make the polynomial non-solvable.
  void clearSolvable();

  // Make the parameters solvable, thus perturbed values have to be calculated.
  // spidIndex is the index of the first spid of this polc.
  // It returns the number of spids in this polc.
  int makeSolvable (int spidIndex);

  // Get the current values of the solvable parameter and store them
  // in the argument.
  void getInitial (Vells& values) const;

  // Get the current value of the solvable parameter and store it
  // in the argument.
  void getCurrentValue (Vells& value, bool denormalize) const;

  // Update the solvable parameters with the new values.
  void update (const Vells& value);

  // Set the original simulation coefficients.
  void setSimCoeff (const Vells& coeff)
    { itsSimCoeff = coeff; }

  // Set the perturbation of the simulation coefficients.
  void setPertSimCoeff (const Vells& coeff)
    { itsPertSimCoeff = coeff; }

  // Get the original simulation coefficients.
  const Vells& getSimCoeff() const
    { return itsSimCoeff; }

  // Get the perturbation of the simulation coefficients.
  const Vells& getPertSimCoeff() const
    { return itsPertSimCoeff; }

  // Set the zero-points of the function.
  void setFreq0 (double freq0)
    { itsFreq0 = freq0; }
  void setTime0 (double time0)
    { itsTime0 = time0; }

  // Get the zero-point of the function.
  double getFreq0() const
    { return itsFreq0; }
  double getTime0() const
    { return itsTime0; }

  // Tell if the coefficients have to be normalized.
  void setNormalize (bool normalize)
    { itsNormalized = normalize; }

  // Tell if the coefficients are normalized.
  bool isNormalized() const
    { return itsNormalized; }

  // Normalize the coefficients for the given domain.
  Vells normalize (const Vells& coeff, const Domain&);

  // Denormalize the coefficients.
  Vells denormalize (const Vells& coeff) const;

  // (De)normalize real coefficients.
  static Vells normDouble (const Vells& coeff, double sx,
			   double sy, double ox, double oy);

private:
  // Fill Pascal's triangle.
  static void fillPascal();

  Vells        itsCoeff;
  Vells        itsSimCoeff;
  Vells        itsPertSimCoeff;
  Vells        itsPerturbation;
  Domain       itsDomain;
  std::vector<bool> itsMask;
  std::vector<int>  itsSpidInx;     //# -1 is not solvable
  int          itsNrSpid;
  double       itsPertValue;
  bool         itsIsRelPert;   //# true = perturbation is relative
  double       itsFreq0;
  double       itsTime0;
  bool         itsNormalized;  //# true = coefficients normalized to domain

  //# Pascal's triangle for the binomial coefficients needed when normalizing.
  static double theirPascal[10][10];
  static bool   theirPascalFilled;
};

} // namespace Meq

#endif

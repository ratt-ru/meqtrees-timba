//# Vells.h: Values for Meq expressions
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

#ifndef MEQ_VELLS_H
#define MEQ_VELLS_H


//# Includes
#include <MEQ/VellsRep.h>
#include <Common/Lorrays.h>

namespace MEQ {

//# Forward Declarations
class VellsTmp;


class Vells
{
public:
  // A null vector (i.e. no vector assigned yet).
  // This can be used to clear the 'cache'.
  Vells();

  // Create a scalar Vells.
  // <group>
  explicit Vells (double value);
  explicit Vells (const dcomplex& value);
  // <group>

  // Create a Vells of given size.
  // If the init flag is true, the matrix is initialized to the given value.
  // Otherwise the value only indicates the type of matrix to be created.
  // <group>
  Vells (double, int nx, int ny, bool init=true);
  Vells (const dcomplex&, int nx, int ny, bool init=true);
  // <group>

  // Create a Vells from a blitz array.
  // <group>
  explicit Vells (LoMat_double&);
  explicit Vells (LoMat_dcomplex&);
  // </group>

  // Create a Vells from a blitz array pointer.
  // It does not take over the pointer.
  // <group>
  explicit Vells (LoMat_double*);
  explicit Vells (LoMat_dcomplex*);
  // </group>

  // Create a Vells from a VellsRep.
  // It takes over the pointer and deletes it in the destructor.
  explicit Vells (VellsRep* rep);

  // Create a Vells from a temporary one (reference semantics).
  Vells (const VellsTmp& that);

  // Copy constructor (reference semantics).
  Vells (const Vells& that);

  ~Vells();

  // Assignment (reference semantics).
  Vells& operator= (const Vells& other);
  Vells& operator= (const VellsTmp& other);

  // Clone the matrix (copy semantics).
  Vells clone() const
    { return Vells (itsRep->clone()); }

  // Change the type/or shape if different.
  LoMat_double& setSizeReal (int nrx, int nry)
    { if (itsRep == 0  ||  !isReal()  ||  nrx != nx()  ||  nry != ny()) {
        setRealArray (nrx, nry);
      }
      return getRealArray();
    }
  LoMat_dcomplex& setSizeComplex (int nrx, int nry)
    { if (itsRep == 0  ||  isReal()  ||  nrx != nx()  ||  nry != ny()) {
        setComplexArray (nrx, nry);
      }
      return getComplexArray();
    }
  void setRealArray (int nx, int ny);
  void setComplexArray (int nx, int ny);

  int nx() const
    { return itsNx; }

  int ny() const
    { return itsNy; }

  int nelements() const
    { return itsNx*itsNy; }

  bool isNull() const
    { return (itsRep == 0); }

  bool isScalar() const
    { return itsIsScalar; }

  void show (std::ostream& os) const
    { itsRep->show (os); }

  bool isReal() const
    { return itsRealArray != 0; }

  const LoMat_double& getRealArray() const
    { return *itsRealArray; }
  const LoMat_dcomplex& getComplexArray() const
    { return *itsComplexArray; }
  LoMat_double& getRealArray()
    { return *itsRealArray; }
  LoMat_dcomplex& getComplexArray()
    { return *itsComplexArray; }

  double getRealScalar() const
    { return itsRealArray->data()[0]; }
  const dcomplex& getComplexScalar() const
    { return itsComplexArray->data()[0]; }

  void init (double val)
    { if (isReal()) getRealArray()=val; else getComplexArray()=dcomplex(val); }

  const double* realStorage() const
    { return getRealArray().data(); }
  double* realStorage()
    { return getRealArray().data(); }
  const dcomplex* complexStorage() const
    { return getComplexArray().data(); }
  dcomplex* complexStorage()
    { return getComplexArray().data(); }

  VellsRep* rep() const
    { return itsRep; }

  void operator+= (const Vells& right);
  void operator+= (const VellsTmp& right);

  void operator-= (const Vells& right);
  void operator-= (const VellsTmp& right);

  void operator*= (const Vells& right);
  void operator*= (const VellsTmp& right);

  void operator/= (const Vells& right);
  void operator/= (const VellsTmp& right);

  VellsTmp operator+ (const Vells& right) const;
  VellsTmp operator+ (const VellsTmp& right) const;

  VellsTmp operator- (const Vells& right) const;
  VellsTmp operator- (const VellsTmp& right) const;

  VellsTmp operator* (const Vells& right) const;
  VellsTmp operator* (const VellsTmp& right) const;

  VellsTmp operator/ (const Vells& right) const;
  VellsTmp operator/ (const VellsTmp& right) const;

  VellsTmp operator-() const;

  friend VellsTmp posdiff (const Vells&, const Vells&);
  friend VellsTmp posdiff (const Vells&, const VellsTmp&);
  friend VellsTmp tocomplex (const Vells&, const Vells&);
  friend VellsTmp tocomplex (const Vells&, const VellsTmp&);
  friend VellsTmp pow (const Vells&, const Vells& exponent);
  friend VellsTmp pow (const Vells&, const VellsTmp& exponent);
  friend VellsTmp sin (const Vells&);
  friend VellsTmp cos (const Vells&);
  friend VellsTmp exp (const Vells&);
  friend VellsTmp sqr (const Vells&);
  friend VellsTmp sqrt(const Vells&);
  friend VellsTmp conj(const Vells&);
  friend VellsTmp min (const Vells&);
  friend VellsTmp max (const Vells&);
  friend VellsTmp mean(const Vells&);
  friend VellsTmp sum (const Vells&);


private:
  VellsRep*       itsRep;
  LoMat_double*   itsRealArray;
  LoMat_dcomplex* itsComplexArray;
  int             itsNx;
  int             itsNy;
  bool            itsIsScalar;
  bool            itsIsOwner;
};


inline std::ostream& operator<< (std::ostream& os, const Vells& vec)
  { vec.show (os); return os; }


} // namespace MEQ

#endif

//# Vells.cc: Values for Meq expressions
//#
//# Copyright (C) 2003
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


#include <MEQ/Vells.h>
#include <MEQ/VellsTmp.h>
#include <MEQ/VellsRealSca.h>
#include <MEQ/VellsComplexSca.h>
#include <MEQ/VellsRealArr.h>
#include <MEQ/VellsComplexArr.h>
#include <Common/Debug.h>

namespace MEQ {

Vells::Vells()
: itsRep         (0),
  itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (0),
  itsNy          (0),
  itsIsScalar    (True),
  itsIsOwner     (False)
{}

Vells::Vells (double value)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (1),
  itsNy          (1),
  itsIsScalar    (True),
  itsIsOwner     (True)
{
  VellsRealSca* v = new VellsRealSca (value);
  itsRep = v->link();
  itsRealArray = new LoMat_double (v->realStorage(),
				   LoMatShape(1,1),
				   blitz::neverDeleteData);
}

Vells::Vells (const dcomplex& value)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (1),
  itsNy          (1),
  itsIsScalar    (True),
  itsIsOwner     (True)
{
  VellsComplexSca* v = new VellsComplexSca (value);
  itsRep = v->link();
  itsComplexArray = new LoMat_dcomplex (v->complexStorage(),
					LoMatShape(1,1),
					blitz::neverDeleteData);
}

Vells::Vells (double value, int nx, int ny, bool init)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (nx),
  itsNy          (ny),
  itsIsScalar    (nx==1 && ny==1),
  itsIsOwner     (True)
{
  if (itsIsScalar) {
    VellsRealSca* v = new VellsRealSca (value);
    itsRep = v->link();
  } else {
    VellsRealArr* v = new VellsRealArr (nx, ny);
    itsRep = v->link();
    if (init) {
      v->set (value);
    }
  }
  itsRealArray = new LoMat_double (itsRep->realStorage(),
				   LoMatShape(nx,ny),
				   blitz::neverDeleteData);
}

Vells::Vells (const dcomplex& value, int nx, int ny, bool init)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (nx),
  itsNy          (ny),
  itsIsScalar    (nx==1 && ny==1),
  itsIsOwner     (True)
{
  if (itsIsScalar) {
    VellsComplexSca* v = new VellsComplexSca (value);
    itsRep = v->link();
  } else {
    VellsComplexArr* v = new VellsComplexArr (nx, ny);
    itsRep = v->link();
    if (init) {
      v->set (value);
    }
  }
  itsComplexArray = new LoMat_dcomplex (itsRep->complexStorage(),
					LoMatShape(nx,ny),
					blitz::neverDeleteData);
}

Vells::Vells (LoMat_double& array)
: itsRealArray   (new LoMat_double(array)),
  itsComplexArray(0),
  itsNx          (array.extent(blitz::firstDim)),
  itsNy          (array.extent(blitz::secondDim)),
  itsIsScalar    (itsNx==1 && itsNy==1),
  itsIsOwner     (True)
{
  Assert (array.isStorageContiguous());
  if (itsIsScalar) {
    VellsRealSca* v = new VellsRealSca (array.data());
    itsRep = v->link();
  } else {
    VellsRealArr* v = new VellsRealArr (array.data(), itsNx, itsNy);
    itsRep = v->link();
  }
}

Vells::Vells (LoMat_dcomplex& array)
: itsRealArray   (0),
  itsComplexArray(new LoMat_dcomplex(array)),
  itsNx          (array.extent(blitz::firstDim)),
  itsNy          (array.extent(blitz::secondDim)),
  itsIsScalar    (itsNx==1 && itsNy==1),
  itsIsOwner     (True)
{
  Assert (array.isStorageContiguous());
  if (itsIsScalar) {
    VellsComplexSca* v = new VellsComplexSca (array.data());
    itsRep = v->link();
  } else {
    VellsComplexArr* v = new VellsComplexArr (array.data(), itsNx, itsNy);
    itsRep = v->link();
  }
}

Vells::Vells (LoMat_double* array)
: itsRealArray   (array),
  itsComplexArray(0),
  itsNx          (array->extent(blitz::firstDim)),
  itsNy          (array->extent(blitz::secondDim)),
  itsIsScalar    (itsNx==1 && itsNy==1),
  itsIsOwner     (False)
{
  Assert (array->isStorageContiguous());
  if (itsIsScalar) {
    VellsRealSca* v = new VellsRealSca (array->data());
    itsRep = v->link();
  } else {
    VellsRealArr* v = new VellsRealArr (array->data(), itsNx, itsNy);
    itsRep = v->link();
  }
}

Vells::Vells (LoMat_dcomplex* array)
: itsRealArray   (0),
  itsComplexArray(array),
  itsNx          (array->extent(blitz::firstDim)),
  itsNy          (array->extent(blitz::secondDim)),
  itsIsScalar    (itsNx==1 && itsNy==1),
  itsIsOwner     (False)
{
  Assert (array->isStorageContiguous());
  if (itsIsScalar) {
    VellsComplexSca* v = new VellsComplexSca (array->data());
    itsRep = v->link();
  } else {
    VellsComplexArr* v = new VellsComplexArr (array->data(), itsNx, itsNy);
    itsRep = v->link();
  }
}

Vells::Vells (VellsRep* rep)
: itsRep          (rep->link()),
  itsRealArray    (0),
  itsComplexArray (0),
  itsNx           (rep->nx()),
  itsNy           (rep->ny()),
  itsIsScalar     (itsNx==1 && itsNy==1),
  itsIsOwner      (true)
{
  if (itsRep->isReal()) {
    itsRealArray = new LoMat_double (itsRep->realStorage(),
				     LoMatShape(itsNx,itsNy),
				     blitz::neverDeleteData);
  } else {
    itsComplexArray = new LoMat_dcomplex (itsRep->complexStorage(),
					  LoMatShape(itsNx,itsNy),
					  blitz::neverDeleteData);
  }
}

Vells::Vells (const Vells& that)
: itsRep          (that.itsRep),
  itsRealArray    (that.itsRealArray),
  itsComplexArray (that.itsComplexArray),
  itsNx           (that.itsNx),
  itsNy           (that.itsNy),
  itsIsScalar     (that.itsIsScalar),
  itsIsOwner      (that.itsIsOwner)
{
  if (itsRep != 0) {
    itsRep->link();
  }
  if (itsIsOwner) {
    if (itsRealArray) {
      itsRealArray = new LoMat_double (*itsRealArray);
    } else {
      itsComplexArray = new LoMat_dcomplex (*itsComplexArray);
    }
  }   
}

Vells::Vells (const VellsTmp& that)
: itsRep          (that.rep()->link()),
  itsRealArray    (0),
  itsComplexArray (0),
  itsNx           (that.nx()),
  itsNy           (that.ny()),
  itsIsScalar     (that.nelements()==1),
  itsIsOwner      (True)
{
  if (that.isReal()) {
    itsRealArray = new LoMat_double (itsRep->realStorage(),
				     LoMatShape(itsNx,itsNy),
				     blitz::neverDeleteData);
  } else {
    itsComplexArray = new LoMat_dcomplex (itsRep->complexStorage(),
					  LoMatShape(itsNx,itsNy),
					  blitz::neverDeleteData);
  }
}

Vells& Vells::operator= (const Vells& that)
{
  if (this != &that) {
    VellsRep::unlink (itsRep);
    if (itsIsOwner) {
      delete itsRealArray;
      delete itsComplexArray;
    }
    itsRep = that.itsRep;
    if (itsRep != 0) {
      itsRep->link();
    }
    itsRealArray    = that.itsRealArray;
    itsComplexArray = that.itsComplexArray;
    itsNx           = that.itsNx;
    itsNy           = that.itsNy;
    itsIsScalar     = that.itsIsScalar;
    itsIsOwner      = that.itsIsOwner;
    if (itsIsOwner) {
      if (itsRealArray) {
	itsRealArray = new LoMat_double (*itsRealArray);
      } else {
	itsComplexArray = new LoMat_dcomplex (*itsComplexArray);
      }
    }
  }   
  return *this;
}
Vells& Vells::operator= (const VellsTmp& that)
{
  VellsRep::unlink (itsRep);
  if (itsIsOwner) {
    delete itsRealArray;
    delete itsComplexArray;
  }
  itsRep          = that.rep()->link();
  itsRealArray    = 0;
  itsComplexArray = 0;
  itsNx           = that.nx();
  itsNy           = that.ny();
  itsIsScalar     = that.nelements()==1;
  itsIsOwner      = True;
  if (that.isReal()) {
    itsRealArray = new LoMat_double (itsRep->realStorage(),
				     LoMatShape(itsNx,itsNy),
				     blitz::neverDeleteData);
  } else {
    itsComplexArray = new LoMat_dcomplex (itsRep->complexStorage(),
					  LoMatShape(itsNx,itsNy),
					  blitz::neverDeleteData);
  }
  return *this;
}

Vells::~Vells()
{
  VellsRep::unlink (itsRep);
  if (itsIsOwner) {
    delete itsRealArray;
    delete itsComplexArray;
  }
}

void Vells::setRealArray (int nx, int ny)
{
  Assert (itsIsOwner);
  VellsRep::unlink (itsRep);
  itsRep = 0;
  if (nx == 1  &&  ny == 1) {
    itsRep = new VellsRealSca (0.);
  } else {
    itsRep = new VellsRealArr (nx, ny);
  }
  itsRep->link();
}
void Vells::setComplexArray (int nx, int ny)
{
  Assert (itsIsOwner);
  VellsRep::unlink (itsRep);
  itsRep = 0;
  if (nx == 1  &&  ny == 1) {
    itsRep = new VellsComplexSca (dcomplex());
  } else {
    itsRep = new VellsComplexArr (nx, ny);
  }
  itsRep->link();
}



void Vells::operator+= (const Vells& right)
{
  VellsRep* res = itsRep->add (*right.itsRep, False);
  AssertStr (res == itsRep, "Mismatching types");
}   
void Vells::operator+= (const VellsTmp& right)
{
  VellsRep* res = itsRep->add (*right.rep(), False);
  AssertStr (res == itsRep, "Mismatching types");
}   
void Vells::operator-= (const Vells& right)
{
  VellsRep* res = itsRep->subtract (*right.rep(), False);
  AssertStr (res == itsRep, "Mismatching types");
}   
void Vells::operator-= (const VellsTmp& right)
{
  VellsRep* res = itsRep->subtract (*right.rep(), False);
  AssertStr (res == itsRep, "Mismatching types");
}   
void Vells::operator*= (const Vells& right)
{
  VellsRep* res = itsRep->multiply (*right.rep(), False);
  AssertStr (res == itsRep, "Mismatching types");
}   
void Vells::operator*= (const VellsTmp& right)
{
  VellsRep* res = itsRep->multiply (*right.rep(), False);
  AssertStr (res == itsRep, "Mismatching types");
}   
void Vells::operator/= (const Vells& right)
{
  VellsRep* res = itsRep->divide (*right.rep(), False);
  AssertStr (res == itsRep, "Mismatching types");
}   
void Vells::operator/= (const VellsTmp& right)
{
  VellsRep* res = itsRep->divide (*right.rep(), False);
  AssertStr (res == itsRep, "Mismatching types");
}   

VellsTmp Vells::operator+ (const Vells& right) const
{
    return VellsTmp(*this) + right;
}   
VellsTmp Vells::operator+ (const VellsTmp& right) const
{
    return (VellsTmp&)right + *this;
}

VellsTmp Vells::operator- (const Vells& right) const
{
    return VellsTmp(*this) - right;
}   
VellsTmp Vells::operator- (const VellsTmp& right) const
{
    return VellsTmp(*this) - right;
}

VellsTmp Vells::operator* (const Vells& right) const
{
    return VellsTmp(*this) * right;
}   
VellsTmp Vells::operator* (const VellsTmp& right) const
{
    return (VellsTmp&)right * *this;
}

VellsTmp Vells::operator/ (const Vells& right) const
{
    return VellsTmp(*this) / right;
}
//# This could possibly be speeded up by using right as the result.
//# It requires a special divide function in VellsRep and derived classes.
//# The same is true for operator-.
//# (Alternatively one could do  "(-right) + this".)
VellsTmp Vells::operator/ (const VellsTmp& right) const
{
    return VellsTmp(*this) / right;
}

VellsTmp Vells::operator-() const
{
    return VellsTmp(*this).operator-();
}

VellsTmp posdiff (const Vells& left, const Vells& right)
{
    return left.itsRep->posdiff(*right.itsRep);
}
VellsTmp posdiff (const Vells& left, const VellsTmp& right)
{
    return left.itsRep->posdiff(*right.rep());
}
VellsTmp tocomplex (const Vells& left, const Vells& right)
{
    return left.itsRep->tocomplex(*right.itsRep);
}
VellsTmp tocomplex (const Vells& left, const VellsTmp& right)
{
    return left.itsRep->tocomplex(*right.rep());
}
VellsTmp sin (const Vells& arg)
{
    return sin(VellsTmp(arg));
}
VellsTmp cos(const Vells& arg)
{
    return cos(VellsTmp(arg));
}
VellsTmp exp(const Vells& arg)
{
    return exp(VellsTmp(arg));
}
VellsTmp sqr(const Vells& arg)
{
    return sqr(VellsTmp(arg));
}
VellsTmp sqrt(const Vells& arg)
{
    return sqrt(VellsTmp(arg));
}
VellsTmp conj(const Vells& arg)
{
    return conj(VellsTmp(arg));
}
VellsTmp min(const Vells& arg)
{
    return arg.itsRep->min();
}
VellsTmp max(const Vells& arg)
{
    return arg.itsRep->max();
}
VellsTmp mean(const Vells& arg)
{
    return arg.itsRep->mean();
}
VellsTmp sum(const Vells& arg)
{
    return arg.itsRep->sum();
}

} // namespace MEQ

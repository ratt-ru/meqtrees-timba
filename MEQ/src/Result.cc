//# Result.cc: The result of an expression for a domain.
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


#include <MEQ/Result.h>
#include <MEQ/Cells.h>
#include <MEQ/VellsTmp.h>
#include <DMI/DataArray.h>

namespace MEQ {

int Result::nctor = 0;
int Result::ndtor = 0;


Result::Result (int nspid)
: itsCount           (0),
  itsCells           (0),
  itsDefPert         (0.),
  itsPerturbedValues (nspid),
  itsPerturbations   (nspid)
{
  nctor++;
}

Result::~Result()
{
  clear();
  ndtor--;
}

void Result::setCells (const Cells& cells)
{
  itsCells = new Cells(cells);
  this->operator[](AidCells) <<= static_cast<DataRecord*>(itsCells);
}

void Result::clear()
{
  for (unsigned int i=0; i<itsPerturbedValues.size(); i++) {
    delete itsPerturbedValues[i];
    itsPerturbedValues[i] = 0;
  }
}

void Result::setPerturbedValue (int i, const Vells& value)
{
  if (itsPerturbedValues[i] == 0) {
    itsPerturbedValues[i] = new Vells();
  }
  *(itsPerturbedValues[i]) = value;
}

void Result::show (std::ostream& os) const
{
  os << "Value: " << itsValue << endl;
  for (unsigned int i=0; i<itsPerturbedValues.size(); i++) {
    os << "deriv parm " << itsSpids[i]
       << " with " << itsPerturbations[i] << endl;
    os << "   " << (*(itsPerturbedValues[i]) - itsValue) << endl;
    os << "   " << (*(itsPerturbedValues[i]) - itsValue) /
      itsPerturbations[i] << endl;
  }
}

void Result::allocateReal (int nfreq, int ntime)
{
  DataArray* ptr = new DataArray (Tpdouble, LoMatShape(nfreq,ntime));
  (*this)[AidValues] <<= ptr;
  LoMat_double arr = (*ptr)[HIID()];
  itsValue = Vells(arr);
}

void Result::allocateComplex (int nfreq, int ntime)
{
  DataArray* ptr = new DataArray (Tpdcomplex, LoMatShape(nfreq,ntime));
  (*this)[AidValues] <<= ptr;
  LoMat_dcomplex arr = (*ptr)[HIID()];
  itsValue = Vells(arr);
}

void Result::allocatePertReal (int i, int nfreq, int ntime)
{
  DataArray* ptr = new DataArray (Tpdouble, LoMatShape(nfreq,ntime));
  (*this)[i] <<= ptr;
  LoMat_double arr = (*ptr)[HIID()];
  itsPerturbedValues[i] = new Vells(arr);
}

void Result::allocatePertComplex (int i, int nfreq, int ntime)
{
  DataArray* ptr = new DataArray (Tpdcomplex, LoMatShape(nfreq,ntime));
  (*this)[i] <<= ptr;
  LoMat_dcomplex arr = (*ptr)[HIID()];
  itsPerturbedValues[i] = new Vells(arr);
}

} // namespace MEQ

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
#include <DMI/HIID.h>
#include <DMI/DataArray.h>

namespace Meq {

static NestableContainer::Register reg(TpMeqResult,True);

const HIID FValue           = AidValue,
           FSpids           = AidSpid|AidIndex,
           FPerturbedValues = AidPerturbed|AidValue,
           FPerturbations   = AidPerturbations;
//           FParmValue       = AidParm|AidValue;

int Result::nctor = 0;
int Result::ndtor = 0;


Result::Result (int nspid)
: itsCount           (0),
  itsDefPert         (0.),
  itsPerturbedValues (nspid),
  itsPerturbations   (0),
  itsSpids           (0),
  itsNumSpids        (nspid),
  pnc_perturbed      (0)
{
  nctor++;
  // create appropriate fields in the record:
  //    spids vector
  if( itsNumSpids )
  {
    DataField *pdf = new DataField(Tpint,nspid);
    DataRecord::add(FSpids,pdf,DMI::ANONWR);
    itsSpids = (*pdf)[HIID()].as_wp<int>();
    //    perturbations vector
    pdf = new DataField(Tpdouble,nspid);
    DataRecord::add(FPerturbations,pdf,DMI::ANONWR);
    itsPerturbations = (*pdf)[HIID()].as_wp<double>();
  }
}

Result::Result (const DataRecord &other,int flags,int depth)
: DataRecord(other,flags,depth),
  itsCount           (0),
  itsDefPert         (0.),
  itsPerturbedValues (0),
  itsPerturbations   (0),
  pnc_perturbed      (0)
{
  nctor++;
  validateContent();
}


Result::~Result()
{
  clear();
  ndtor--;
}

void Result::makeVells (Vells &vells,NestableContainer &nc,const HIID &field)
{
  if( !nc[field].exists() )
  {
    vells = Vells();
    return;
  }
  DataArray & darr = nc[field].as_wr<DataArray>();
  TypeId type = darr.elementType();
  if( type == Tpdouble )
  {
    LoMat_double arr = darr[HIID()];
    vells = Vells(arr);
  }
  else if( type == Tpdcomplex )
  {
    LoMat_dcomplex arr = darr[HIID()];
    vells = Vells(arr);
  }
  else
    Throw("illegal "+field.toString()+" type "+type.toString());
}

void Result::validateContent ()
{
  // clear out pointers to perturbed values
  clear();
  // ensure that our record contains all the right fields, and that they're
  // indeed writable. Setup shortcuts to their contents
  try
  {
    // get pointer to spids vector and its size
    if( (*this)[FSpids].exists() )
    {
      itsSpids = (*this)[FSpids].as_wp<int>(itsNumSpids);
      int size;
      // get pointer to perturbations vector, verify size
      itsPerturbations = (*this)[FPerturbations].as_wp<double>(size);
      FailWhen(size!=itsNumSpids,"size mismatch between spids and perturbations");
      // get value, if it exists in the data record
      makeVells(itsValue,*this,FValue);
      // get perturbations, if they exist
      itsPerturbedValues.resize(itsNumSpids);
      if( (*this)[FPerturbedValues].exists() )
      {
        pnc_perturbed = (*this)[FPerturbedValues].as_wp<DataField>();
        FailWhen( pnc_perturbed->size(TpDataArray) != itsNumSpids,
              "size mismatch between spids and perturbed values");
        // setup shortcuts to perturbation vells
        for( int i=0; i<itsNumSpids; i++ )
        {
          itsPerturbedValues[i] = new Vells();
          makeVells(*itsPerturbedValues[i],*pnc_perturbed,AtomicID(i));
        }
      }
    }
    else
    {
      itsNumSpids = 0;
      itsSpids = 0;
      itsPerturbations = 0;
      itsPerturbedValues.resize(0);
      pnc_perturbed = 0;
    }
  }
  catch( std::exception &err )
  {
    clear();
    Throw(string("Validate of Result record failed: ") + err.what());
  }
  catch( ... )
  {
    clear();
    Throw("Validate of Result record failed with unknown exception");
  }  
}

void Result::setSpids (const vector<int>& spids)
{
  FailWhen( spids.size() != uint(itsNumSpids),"setSpids: vector size mismatch" );
  if( itsNumSpids )
    (*this)[FSpids] = spids;
}

//void Result::setCells (const Cells& cells)
//{
//  itsCells = new Cells(cells);
//  this->operator[](AidCells) <<= static_cast<DataRecord*>(itsCells);
//}

void Result::clear()
{
  for (unsigned int i=0; i<itsPerturbedValues.size(); i++) {
    delete itsPerturbedValues[i];
    itsPerturbedValues[i] = 0;
  }
}

void Result::setValue (const Vells& value)
{
  if (value.isReal()) {
    LoMat_double& mat = setReal (value.nx(), value.ny());
    mat = value.getRealArray();
  } else {
    LoMat_dcomplex& mat = setComplex (value.nx(), value.ny());
    mat = value.getComplexArray();
  }
}

void Result::setPerturbedValue (int i, const Vells& value)
{
  if( value.isReal() )
    setPerturbedReal(i,value.nx(),value.ny()) = value.getRealArray();
  else
    setPerturbedComplex(i,value.nx(),value.ny()) = value.getComplexArray();
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
  DataRecord::replace(FValue,ptr,DMI::ANONWR);
  LoMat_double arr = (*ptr)[HIID()];
  itsValue = Vells(arr);
}

void Result::allocateComplex (int nfreq, int ntime)
{
  DataArray* ptr = new DataArray (Tpdcomplex, LoMatShape(nfreq,ntime));
  DataRecord::replace(FValue,ptr,DMI::ANONWR);
  LoMat_dcomplex arr = (*ptr)[HIID()];
  itsValue = Vells(arr);
}

void Result::allocatePertReal (int i, int nfreq, int ntime)
{
  DataArray* ptr = new DataArray (Tpdouble, LoMatShape(nfreq,ntime));
  nc_perturbed()[i].replace() <<= ptr;
  LoMat_double arr = (*ptr)[HIID()];
  itsPerturbedValues[i] = new Vells(arr);
}

void Result::allocatePertComplex (int i, int nfreq, int ntime)
{
  DataArray* ptr = new DataArray (Tpdcomplex, LoMatShape(nfreq,ntime));
  nc_perturbed()[i].replace() <<= ptr;
  LoMat_dcomplex arr = (*ptr)[HIID()];
  itsPerturbedValues[i] = new Vells(arr);
}

DataField & Result::nc_perturbed ()
{
  // allocate one if not already done so
  if( !pnc_perturbed )
  {
    pnc_perturbed = new DataField(itsNumSpids,TpDataArray);
    DataRecord::replace(FPerturbedValues,pnc_perturbed,DMI::ANONWR);
  }
  return *pnc_perturbed;
}

} // namespace Meq

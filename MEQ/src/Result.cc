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
#include <DMI/HIID.h>
#include <DMI/DataArray.h>
#include <DMI/DataField.h>

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

static Vells * makeVells (NestableContainer &nc,const HIID &field)
{
  if( !nc[field].exists() )
    return new Vells();
  else
    return new Vells(nc[field].privatize(DMI::WRITE).as_wp<DataArray>());
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
      itsSpids = (*this)[FSpids].privatize(DMI::WRITE).as_wp<int>(itsNumSpids);
      int size;
      // get pointer to perturbations vector, verify size
      itsPerturbations = (*this)[FPerturbations].privatize(DMI::WRITE).as_wp<double>(size);
      FailWhen(size!=itsNumSpids,"size mismatch between spids and perturbations");
      // get value, if it exists in the data record
      itsValue <<= makeVells(*this,FValue);
      // get perturbations, if they exist
      itsPerturbedValues.resize(itsNumSpids);
      if( (*this)[FPerturbedValues].exists() )
      {
        pnc_perturbed = (*this)[FPerturbedValues].privatize(DMI::WRITE).as_wp<DataField>();
        FailWhen( pnc_perturbed->size(TpDataArray) != itsNumSpids,
              "size mismatch between spids and perturbed values");
        // setup shortcuts to perturbation vells
        for( int i=0; i<itsNumSpids; i++ )
          itsPerturbedValues[i] <<=
              makeVells(*pnc_perturbed,AtomicID(i));
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
    Throw(string("Validate of Meq::Result record failed: ") + err.what());
  }
  catch( ... )
  {
    clear();
    Throw("Validate of Meq::Result record failed with unknown exception");
  }  
}

void Result::setSpids (const vector<int>& spids)
{
  FailWhen( spids.size() != uint(itsNumSpids),"setSpids: vector size mismatch" );
  if( itsNumSpids )
    (*this)[FSpids] = spids;
}

void Result::clear()
{
  for (unsigned int i=0; i<itsPerturbedValues.size(); i++) 
    itsPerturbedValues[i].detach();
}

Vells & Result::setValue (Vells *pvells)
{
  itsValue <<= pvells;
  DataRecord::replace(FValue,&(pvells->getDataArray()),DMI::ANONWR);
  return *pvells;
}

Vells & Result::setPerturbedValue (int i,Vells *pvells)
{
  itsPerturbedValues[i] <<= pvells;
  nc_perturbed()[i].replace() <<= &(pvells->getDataArray());
  return *pvells;
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

void Result::show (std::ostream& os) const
{
  os << "Value: " << *itsValue << endl;
  for( uint i=0; i<itsPerturbedValues.size(); i++) 
  {
    os << "deriv parm " << itsSpids[i]
       << " with " << itsPerturbations[i] << endl;
    os << "   " << (*(itsPerturbedValues[i]) - *itsValue) << endl;
    os << "   " << (*(itsPerturbedValues[i]) - *itsValue) /
      Vells(itsPerturbations[i]) << endl;
  }
}


} // namespace Meq

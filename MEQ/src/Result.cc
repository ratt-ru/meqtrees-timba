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


#include "Result.h"
#include "MeqVocabulary.h"
#include <DMI/HIID.h>
#include <DMI/DataArray.h>
#include <DMI/DataField.h>

namespace Meq {

static NestableContainer::Register reg(TpMeqResult,True);

int Result::nctor = 0;
int Result::ndtor = 0;


Result::Result (int nspid)
: itsCount           (0),
  itsDefPert         (0.),
  itsPerturbedValues (nspid),
  itsPerturbations   (0),
  itsSpids           (0),
  itsNumSpids        (nspid),
  itsIsFail          (false)
{
  nctor++;
  // create appropriate fields in the record: spids vector and perturbations vector
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
  itsSpids           (0),
  itsIsFail          (false)
{
  nctor++;
  validateContent();
}


Result::~Result()
{
  clear();
  ndtor--;
}

// helper function makes a Vells from a container field; 
// or empty Vells if field does not exist
static Vells * makeVells (NestableContainer &nc,const HIID &field)
{
  // writability of Vells dertermined by writability of array in container
  if( nc[field].exists() )
    return new Vells(nc[field].ref(DMI::PRESERVE_RW));
  else
    return new Vells();
}

static Vells * makeVells (const NestableContainer &nc,const HIID &field)
{
  // writability of Vells dertermined by writability of array in container
  if( nc[field].exists() )
    return new Vells(nc[field].ref());
  else
    return new Vells();
}

void Result::privatize (int flags, int depth)
{
  // if deep-privatizing, clear all shortcuts. We can rely on
  // DataRecord's privatize to call validateContent() afterwards 
  // to reset them.
  if( flags&DMI::DEEP || depth>0 )
    clear();
  DataRecord::privatize(flags,depth);
}

void Result::validateContent ()
{
#ifdef USE_THREADS
  Thread::Mutex::Lock lock(mutex());
#endif
  // ensure that our record contains all the right fields, and that they're
  // indeed writable. Setup shortcuts to their contents
  try
  {
    if( DataRecord::hasField(FFail) ) // a fail result
    {
      itsIsFail = true;
    }
    else
    {
      itsIsFail = false;
      // get value, if it exists in the data record
      itsValue <<= makeVells(*this,FValue);
      // get pointer to spids vector and its size
      if( DataRecord::hasField(FSpids) )
      {
        itsSpids = (*this)[FSpids].as_p<int>(itsNumSpids);
        int size;
        // get pointer to perturbations vector, verify size
        itsPerturbations = (*this)[FPerturbations].as_p<double>(size);
        FailWhen(size!=itsNumSpids,"size mismatch between spids and perturbations");
        // get perturbations, if they exist
        itsPerturbedValues.resize(itsNumSpids);
        if( DataRecord::hasField(FPerturbedValues) )
        {
          perturbed_ref = (*this)[FPerturbedValues].ref(DMI::PRESERVE_RW);
          FailWhen(perturbed_ref->size(TpDataArray) != itsNumSpids,
                "size mismatch between spids and perturbed values");
          // setup shortcuts to perturbation vells
          // use different versions for writable/non-writable
          if( perturbed_ref.isWritable() )
          {
            for( int i=0; i<itsNumSpids; i++ )
              itsPerturbedValues[i] <<=
                  makeVells(perturbed_ref(),AtomicID(i));
          }
          else
          {
            for( int i=0; i<itsNumSpids; i++ )
              itsPerturbedValues[i] <<=
                  makeVells(*perturbed_ref,AtomicID(i));
          }
        }
      }
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

void Result::clear()
{
  itsNumSpids = 0;
  itsSpids = 0;
  itsPerturbations = 0;
  itsPerturbedValues.resize(0);
  perturbed_ref.detach();
  itsValue.detach();
  itsIsFail = false;
}

void Result::setSpids (const vector<int>& spids)
{
  FailWhen(itsNumSpids && spids.size() != uint(itsNumSpids),"setSpids: vector size mismatch" );
  FailWhen(!isWritable(),"r/w access violation");
  if( itsNumSpids ) // assigning to existing vector
    (*this)[FSpids] = spids;
  else // setting new vector
  {
    DataField *pdf = new DataField(Tpint,spids.size(),DMI::WRITE,&spids[0]);
    DataRecord::add(FSpids,pdf,DMI::ANONWR);
    itsSpids = (*pdf)[HIID()].as_wp<int>();
    //    perturbations vector
    pdf = new DataField(Tpdouble,spids.size());
    DataRecord::add(FPerturbations,pdf,DMI::ANONWR);
    itsPerturbations = (*pdf)[HIID()].as_wp<double>();
  }
}

void Result::setPerturbation (int i, double value)
{ 
  (*this)[FPerturbations][i] = value;
}

// set all perturbations at once
void Result::setPerturbations (const vector<double>& perts)
{
  FailWhen(perts.size() != uint(itsNumSpids),"setPerturbations: vector size mismatch" );
  FailWhen(!isWritable(),"r/w access violation");
  if( itsNumSpids )
  {
    (*this)[FPerturbations] = perts;
    itsPerturbations = (*this)[FPerturbations].as_p<double>();
  }
}

Vells & Result::setValue (Vells *pvells)
{
  FailWhen(!isWritable(),"r/w access violation");
  itsValue <<= pvells;
  DataRecord::replace(FValue,&(pvells->getDataArray()),DMI::ANONWR);
  return *pvells;
}

Vells & Result::setPerturbedValue (int i,Vells *pvells)
{
  // allocate container for perturbed values
  if( !perturbed_ref.valid() )
  {
    FailWhen(!isWritable(),"r/w access violation");
    perturbed_ref <<= new DataField(TpDataArray,itsNumSpids);
  }
  perturbed_ref()[i].replace() <<= &(pvells->getDataArray());
  itsPerturbedValues[i] <<= pvells;
  return *pvells;
}

void Result::addFail (const DataRecord *rec,int flags)
{
  FailWhen(!isWritable(),"r/w access violation");
  clear();
  itsIsFail = true;
  // clear out the DR
  DataRecord::removeField(FValue,true);
  DataRecord::removeField(FSpids,true);
  DataRecord::removeField(FPerturbations,true);
  DataRecord::removeField(FPerturbedValues,true);
  // get address of fail field (create it as necessary)
  DataField *fails;
  if( DataRecord::hasField(FFail) )
  {
    fails = &(*this)[FFail];
    // add record to fail field
    fails->put(fails->size(),rec,(flags&~DMI::WRITE)|DMI::READONLY);
  }
  else
  {
    DataRecord::add(FFail,fails = new DataField(TpDataRecord,1),DMI::ANONWR);
    // add record to fail field
    fails->put(0,rec,(flags&~DMI::WRITE)|DMI::READONLY);
  }
}

void Result::addFail (const string &nodename,const string &classname,
                      const string &origin,int origin_line,const string &msg)
{
  DataRecord::Ref ref;
  DataRecord & rec = ref <<= new DataRecord;
  // populate the fail record
  rec[FNodeName] = nodename;
  rec[FClassName] = classname;
  rec[FOrigin] = origin;
  rec[FOriginLine] = origin_line;
  rec[FMessage] = msg;
  addFail(&rec);
}

int Result::numFails () const
{
  return (*this)[FFail].size();
}
  
const DataRecord & Result::getFail (int i) const
{
  return (*this)[FFail][i].as<DataRecord>();
}



void Result::show (std::ostream& os) const
{
  if( isFail() )
    os << "FAIL" << endl;
  else
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
}


} // namespace Meq

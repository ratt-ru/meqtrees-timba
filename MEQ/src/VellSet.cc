//# VellSet.cc: The result of an expression for a domain.
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


#include "VellSet.h"
#include "MeqVocabulary.h"
#include <DMI/HIID.h>
#include <DMI/DataArray.h>
#include <DMI/DataField.h>

namespace Meq {

static NestableContainer::Register reg(TpMeqVellSet,True);

//##ModelId=400E535502F6
int VellSet::nctor = 0;
//##ModelId=400E535502F8
int VellSet::ndtor = 0;


//##ModelId=400E5355031E
VellSet::VellSet (int nspid)
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

//##ModelId=400E53550322
VellSet::VellSet (const DataRecord &other,int flags,int depth)
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


//##ModelId=400E53550329
VellSet::~VellSet()
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

//##ModelId=400E53550333
void VellSet::privatize (int flags, int depth)
{
  // if deep-privatizing, clear all shortcuts. We can rely on
  // DataRecord's privatize to call validateContent() afterwards 
  // to reset them.
  if( flags&DMI::DEEP || depth>0 )
    clear();
  DataRecord::privatize(flags,depth);
}

//##ModelId=400E5355033A
void VellSet::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
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
          for( int i=0; i<itsNumSpids; i++ )
            itsPerturbedValues[i] <<= new Vells(perturbed_ref[i].ref(DMI::PRESERVE_RW));
        }
      }
    }
  }
  catch( std::exception &err )
  {
    clear();
    Throw(string("Validate of Meq::VellSet record failed: ") + err.what());
  }
  catch( ... )
  {
    clear();
    Throw("Validate of Meq::VellSet record failed with unknown exception");
  }  
}

//##ModelId=400E535503B5
void VellSet::clear()
{
  itsNumSpids = 0;
  itsSpids = 0;
  itsPerturbations = 0;
  itsPerturbedValues.resize(0);
  perturbed_ref.detach();
  itsValue.detach();
  itsIsFail = false;
}

//##ModelId=400E53550344
void VellSet::setSpids (const vector<int>& spids)
{
  FailWhen(itsNumSpids && spids.size() != uint(itsNumSpids),"setSpids: vector size mismatch" );
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
    itsNumSpids = spids.size();
    itsPerturbedValues.resize(itsNumSpids);
  }
}

//##ModelId=400E53550353
void VellSet::setPerturbation (int i, double value)
{ 
  DbgAssert(i>=0 && i<itsNumSpids);
  (*this)[FPerturbations][i] = value;
}

// set all perturbations at once
//##ModelId=400E53550359
void VellSet::setPerturbations (const vector<double>& perts)
{
  FailWhen(perts.size() != uint(itsNumSpids),"setPerturbations: vector size mismatch" );
  if( itsNumSpids )
  {
    (*this)[FPerturbations] = perts;
    itsPerturbations = (*this)[FPerturbations].as_p<double>();
  }
}

//##ModelId=400E53550360
Vells & VellSet::setValue (Vells *pvells)
{
  itsValue <<= pvells;
  DataRecord::replace(FValue,&(pvells->getDataArray()),DMI::ANONWR);
  return *pvells;
}

//##ModelId=400E53550387
Vells & VellSet::setPerturbedValue (int i,Vells *pvells)
{
  DbgAssert(i>=0 && i<itsNumSpids);
  // allocate container for perturbed values
  if( !perturbed_ref.valid() )
  {
    DataField *df = new DataField(TpDataArray,itsNumSpids);
    perturbed_ref <<= df;
    DataRecord::add(FPerturbedValues,df,DMI::ANONWR);
  }
  perturbed_ref().put(i,&(pvells->getDataArray()),DMI::ANONWR);
  itsPerturbedValues[i] <<= pvells;
  return *pvells;
}

//##ModelId=400E53550393
void VellSet::addFail (const DataRecord *rec,int flags)
{
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

//##ModelId=400E53550399
void VellSet::addFail (const string &nodename,const string &classname,
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

//##ModelId=400E535503A7
int VellSet::numFails () const
{
  return (*this)[FFail].size();
}
  
//##ModelId=400E535503A9
const DataRecord & VellSet::getFail (int i) const
{
  return (*this)[FFail][i].as<DataRecord>();
}



//##ModelId=400E535503AE
void VellSet::show (std::ostream& os) const
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
      if( itsPerturbedValues[i].valid() )
      {
        os << "   " << (*(itsPerturbedValues[i]) - *itsValue) << endl;
//        os << "   " << (*(itsPerturbedValues[i]) - *itsValue) /
//          Vells(itsPerturbations[i]) << endl;
      }
      else
      {
        os << "oops, perturbed vells "<<i<<" missing???"<<endl;
      }
    }
  }
}


} // namespace Meq

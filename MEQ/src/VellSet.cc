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

// inline helper functions to generate field names: 
// default (first) set has no suffix, then _1, _2, etc.
static inline HIID FieldWithSuffix (const HIID &fname,int iset)
{
  return iset ? fname|AtomicID(iset) : fname;
}

static inline HIID FiPerturbations (int iset)
{
  return FieldWithSuffix(FPerturbations,iset);
}

static inline HIID FiPerturbedValues (int iset)
{
  return FieldWithSuffix(FPerturbedValues,iset);
}

//##ModelId=400E5355031E
VellSet::VellSet (int nspid,int nset)
: default_pert_ (0.),
  pset_         (nset),
  spids_        (0),
  numspids_     (nspid),
  is_fail_      (false)
{
  // create appropriate fields in the record: spids vector and perturbations vector
  if( nspid )
  {
    DataField *pdf = new DataField(Tpint,nspid);
    DataRecord::add(FSpids,pdf,DMI::ANONWR);
    spids_ = (*pdf)[HIID()].as_wp<int>();
    // setups perturbations structures
    setupPertData();
  }
}

//##ModelId=400E53550322
VellSet::VellSet (const DataRecord &other,int flags,int depth)
: DataRecord(other,flags,depth),
  default_pert_ (0.)
{
  validateContent();
}


//##ModelId=400E53550329
VellSet::~VellSet()
{
  clear();
}

// helper function to initialize perturbations structures
void VellSet::setupPertData ()
{
  for( uint iset=0; iset<pset_.size(); iset++ )
  {
    // add perturbations field
    DataField *pdf = new DataField(Tpdouble,numspids_);
    DataRecord::add(FiPerturbations(iset),pdf,DMI::ANONWR);
    pset_[iset].pert = (*pdf)[HIID()].as_p<double>();
    // add perturbed values field
    pset_[iset].pertval.resize(numspids_); 
    pset_[iset].pertval_field <<= pdf = new DataField(TpDataArray,numspids_);
    DataRecord::add(FiPerturbedValues(iset),pdf,DMI::ANONWR);
  }
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
      is_fail_ = true;
    }
    else
    {
      is_fail_ = false;
      // get value, if it exists in the data record
      if( DataRecord::hasField(FValue) )
        value_ <<= new Vells((*this)[FValue].ref(DMI::PRESERVE_RW));
      else
        value_ <<= new Vells;
      // get pointer to spids vector and its size
      if( DataRecord::hasField(FSpids) )
      {
        spids_ = (*this)[FSpids].as_p<int>(numspids_);
        int size;
        // figure out number of perturbation sets in the record
        int nsets = 0;
        while( (*this)[FiPerturbations(nsets)].exists() )
          nsets++;
        // if non-zero, setup shortcuts
        if( nsets )
        {
          pset_.resize(nsets);
          for( int iset=0; iset<nsets; iset++ )
          {
            // get pointer to perturbations vector, verify size
            pset_[iset].pert = (*this)[FiPerturbations(iset)].as_p<double>(size);
            FailWhen(size!=numspids_,"size mismatch between spids and "+FiPerturbations(iset).toString());
            // get perturbations, if they exist
            pset_[iset].pertval.resize(numspids_);
            HIID fid = FiPerturbedValues(iset);
            if( DataRecord::hasField(fid) )
            {
              pset_[iset].pertval_field = (*this)[fid].ref(DMI::PRESERVE_RW);
              FailWhen(pset_[iset].pertval_field->size(TpDataArray) != numspids_,
                       "size mismatch between spids and "+fid.toString());
              // setup shortcuts to perturbation vells
              // use different versions for writable/non-writable
              for( int i=0; i<numspids_; i++ )
              {
                if( pset_[iset].pertval_field[i].exists() )
                  pset_[iset].pertval[i] <<= new Vells(pset_[iset].pertval_field[i].ref(DMI::PRESERVE_RW));
                else
                  pset_[iset].pertval[i] <<= new Vells;
              }
            }
          }
        }
      }
    }
  }
  catch( std::exception &err )
  {
//    cerr<<"Failed VellSet: "<<sdebug(10)<<endl;
    clear();
    Throw(string("Validate of Meq::VellSet record failed: ") + err.what());
  }
  catch( ... )
  {
//    cerr<<"Failed VellSet: "<<sdebug(10)<<endl;
    clear();
    Throw("Validate of Meq::VellSet record failed with unknown exception");
  }  
}

//##ModelId=400E535503B5
void VellSet::clear()
{
  numspids_ = 0;
  spids_ = 0;
  pset_.resize(0);
  value_.detach();
  is_fail_ = false;
}

//##ModelId=400E53550344
void VellSet::setSpids (const vector<int>& spids)
{
  if( numspids_ ) // assigning to existing vector
  {
    FailWhen(spids.size() != uint(numspids_),"setSpids: vector size mismatch" );
    (*this)[FSpids] = spids;
  }
  else // setting new vector
  {
    numspids_ = spids.size();
    DataField *pdf = new DataField(Tpint,spids.size(),DMI::WRITE,&spids[0]);
    DataRecord::add(FSpids,pdf,DMI::ANONWR);
    spids_ = (*pdf)[HIID()].as_wp<int>();
    setupPertData();
  }
}

//##ModelId=400E53550353
void VellSet::setPerturbation (int i, double value,int iset)
{ 
  DbgAssert(i>=0 && i<numspids_);
  (*this)[FiPerturbations(iset)][i] = value;
//  pset_[iset].pert[i] = value;
}

// set all perturbations at once
//##ModelId=400E53550359
void VellSet::setPerturbations (const vector<double>& perts,int iset)
{
  FailWhen(perts.size() != uint(numspids_),"setPerturbations: vector size mismatch" );
  if( numspids_ )
  {
    (*this)[FiPerturbations(iset)] = perts;
    pset_[iset].pert = (*this)[FPerturbations].as_p<double>();
  }
}

//##ModelId=400E53550360
Vells & VellSet::setValue (Vells *pvells)
{
  value_ <<= pvells;
  DataRecord::replace(FValue,&(pvells->getDataArray()),DMI::ANONWR);
  return *pvells;
}

//##ModelId=400E53550387
Vells & VellSet::setPerturbedValue (int i,Vells *pvells,int iset)
{
  DbgAssert(i>=0 && i<numspids_);
  PerturbationSet &ps = pset_[iset];
  // allocate container for perturbed values
  if( !ps.pertval_field.valid() )
  {
    DataField *df = new DataField(TpDataArray,numspids_);
    ps.pertval_field <<= df;
    DataRecord::add(FiPerturbedValues(iset),df,DMI::ANONWR);
  }
  ps.pertval_field().put(i,&(pvells->getDataArray()),DMI::ANONWR);
  ps.pertval[i] <<= pvells;
  return *pvells;
}

//##ModelId=400E53550393
void VellSet::addFail (const DataRecord *rec,int flags)
{
  clear();
  is_fail_ = true;
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
    os << "Value: " << *value_ << endl;
    os << "  " << numspids_ << " spids; " << pset_.size() << " diff set(s)\n";
    for( int i=0; i<numspids_; i++) 
    {
      os << "Spid " << spids_[i] << " ";
      for( uint iset=0; iset<pset_.size(); iset++ )
      {
        if( iset )
          os << "          ";
        os << " pert=" << pset_[iset].pert[i] << ":" << endl;
        if( pset_[iset].pertval[i].valid() )
        {
          os << "            " << (*(pset_[iset].pertval[i]) - *value_) << endl;
        }
        else
        {
          os << "            perturbed vells "<<i<<" is missing"<<endl;
        }
      }
    }
  }
}


} // namespace Meq

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
#include <DMI/DataList.h>

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

static const HIID optColFieldId_array[] = { FFlags, FWeight };


const HIID & OptionalColumns::optColFieldId (uint icol)
{
  DbgAssert1(icol<NUM_OPTIONAL_COL);
  return optColFieldId_array[icol];
}


//##ModelId=400E5355031E
VellSet::VellSet (const LoShape &shp,int nspid,int nset)
: default_pert_ (0.),
  pset_         (nset),
  spids_        (0),
  numspids_     (nspid),
  is_fail_      (false)
{
  init();
  setShape(shp);
}

VellSet::VellSet (int nspid,int nset)
: default_pert_ (0.),
  pset_         (nset),
  spids_        (0),
  numspids_     (nspid),
  is_fail_      (false)
{
  init();
}

void VellSet::init ()
{
  // clear optional columns
  for( uint i=0; i<NUM_OPTIONAL_COL; i++ )
    optcol_[i].ptr = 0;
  // create appropriate fields in the record: spids vector and perturbations vector
  if( numspids_ )
  {
    DataField *pdf = new DataField(Tpint,numspids_);
    DataRecord::add(FSpids,pdf,DMI::ANONWR);
    spids_ = (*pdf)[HIID()].as_wp<int>();
    // setups perturbations structures
    for( uint iset=0; iset<pset_.size(); iset++ )
      setupPertData(iset);
  }
}

//##ModelId=400E53550322
VellSet::VellSet (const DataRecord &other,int flags,int depth)
: DataRecord(other,flags,depth),
  default_pert_ (0.),
  pset_         (0),
  spids_        (0),
  numspids_     (0),
  is_fail_      (false)
{
  // clear optional columns
  for( uint i=0; i<NUM_OPTIONAL_COL; i++ )
    optcol_[i].ptr = 0;
  validateContent();
}


//##ModelId=400E53550329
VellSet::~VellSet()
{
  clear();
}

// helper function to initialize perturbations structures
void VellSet::setupPertData (int iset)
{
  Thread::Mutex::Lock lock(mutex());
  // add perturbations field
  DataField *pdf = new DataField(Tpdouble,numspids_);
  DataRecord::add(FiPerturbations(iset),pdf,DMI::ANONWR);
  pset_[iset].pert = (*pdf)[HIID()].as_p<double>();
  // add perturbed values field
  pset_[iset].pertval.resize(numspids_); 
  pset_[iset].pertval_field <<= pdf = new DataField(TpDataArray,numspids_);
  DataRecord::add(FiPerturbedValues(iset),pdf,DMI::ANONWR);
}

void VellSet::setShape (const Vells::Shape &shp)
{
  Thread::Mutex::Lock lock(mutex());
  if( hasShape() )
  {
    if( shape_ != shp)
    {
      Throw("different VellSet shape already set");
    }
  }
  else
  {
    shape_ = shp;
    DataRecord::replace(FShape,new DataField(Tpint,shp.size(),&(shp[0])),DMI::ANONWR);
  }
}
    
//##ModelId=400E53550333
void VellSet::privatize (int flags, int depth)
{
  // if deep-privatizing, then detach shortcuts -- they will be reattached 
  // by validateContent()
//  if( flags&DMI::DEEP || depth>0 )
//  {
//    Thread::Mutex::Lock lock(mutex());
    DataRecord::privatize(flags,depth);
//  }
}

void VellSet::revalidateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  protectAllFields();
  if( DataRecord::hasField(FSpids) )
  {
    spids_ = (*this)[FSpids].as_p<int>(numspids_);
    for( uint i=0; i<pset_.size(); i++ )
      pset_[i].pert = (*this)[FiPerturbations(i)].as_p<double>();
  }
  else
  {
    spids_ = 0;
    numspids_ = 0;
  }
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
      // get shape from data record
      Hook hshp(*this,FShape);
      if( hshp.exists() )
      {
        vector<int> shp = (*this)[FShape].as_vector<int>();
        FailWhen(int(shp.size())>Axis::MaxAxis,"illegal "+FShape.toString()+" field");
        shape_ = shp;
      }
      // get value, if it exists in the data record
      Hook hval(*this,FValue);
      bool has_value = hval.exists();
      if( has_value )
      {
        value_ <<= new Vells(hval.ref());
        // check for matching shape
        FailWhen(!value_->isCompatible(shape_),"main value: incompatible shape");
      }
      else
        value_ <<= new Vells;
      // get optional columns, if they exist in the data record
      for( int i=0; i<NUM_OPTIONAL_COL; i++ )
      {
        Hook hcol(*this,optColFieldId(i));
        if( hcol.exists() )
        {
          FailWhen(!has_value,"missing main value");
          const DataArray &darr = *(optcol_[i].ref = hcol.ref());
          FailWhen(darr.size() != 1 && darr.shape() != shape_,
                   "column "+optColFieldId(i).toString()+": bad shape");
          // cast away const here: writability is checked separately
          optcol_[i].ptr = const_cast<void*>(darr.getConstArrayPtr(optColArrayType(i)));
        }
        else
          optcol_[i].ptr = 0;
      }
      // get pointer to spids vector and its size
      if( DataRecord::hasField(FSpids) )
      {
        spids_ = (*this)[FSpids].as_p<int>(numspids_);
        FailWhen(!has_value,"missing main value");
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
              pset_[iset].pertval_field = (*this)[fid].ref();
              FailWhen(pset_[iset].pertval_field->size(TpDataArray) != numspids_,
                       "size mismatch between spids and "+fid.toString());
              // setup shortcuts to perturbation vells
              // use different versions for writable/non-writable
              for( int i=0; i<numspids_; i++ )
              {
                if( pset_[iset].pertval_field[i].exists() )
                {
                  Vells *pvells = new Vells(pset_[iset].pertval_field[i].ref());
                  pset_[iset].pertval[i] <<= pvells;
                  FailWhen(!pvells->isCompatible(shape_),
                      Debug::ssprintf("perturbed value %d/%d: incompatible shape",i,iset));
                }
// removed this: rather than attach a null Vells, keep the ref unattached
//                else
//                  pset_[iset].pertval[i] <<= new Vells;
              }
            }
          }
        }
      }
      else
      {
        spids_ = 0;
        numspids_ = 0;
      }
    }
    protectAllFields();
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
  Thread::Mutex::Lock lock(mutex());
  shape_.clear();
  numspids_ = 0;
  spids_ = 0;
  pset_.resize(0);
  value_.detach();
  is_fail_ = false;
  // clear optional columns
  for( int i=0; i<NUM_OPTIONAL_COL; i++ )
  {
    optcol_[i].ptr = 0;
    optcol_[i].ref.detach();
  }
}

// void VellSet::makeReadOnly (int flags)
// {
//   Thread::Mutex::Lock lock(mutex());
//   // call DataRecord method to make fields read-only
//   // (this will take care of DMI::DEEP flag if passed, making contents r/o)
//   DataRecord::makeReadOnly(flags);
//   // make all cached refs r/o
//   value_.change(DMI::READONLY);
//   for( uint i=0; i<pset_.size(); i++ )
//   {
//     for( uint j=0; j<pset_[i].pertval.size(); j++ )
//       pset_[i].pertval[j].change(DMI::READONLY);
//     pset_[i].pertval_field.change(DMI::READONLY);
//   }
//   for( int i=0; i<NUM_OPTIONAL_COL; i++ )
//     optcol_[i].ref.change(DMI::READONLY);
// }
// 

Vells & VellSet::getValueWr ()
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen( !value_.valid(),"no main value in this VellSet" );
  // if not writable, privatize for writing
  if( !value_.isWritable() || !value_->isWritable() )
  {
    value_.privatize(DMI::WRITE|DMI::DEEP);
    DataRecord::replace(FValue,&(value_().getDataArray()),DMI::WRITE);
  }
  return value_.dewr();
}

void * VellSet::writeOptCol (uint icol)
{
  Thread::Mutex::Lock lock(mutex());
  Assert(hasOptCol(icol));
  if( !optcol_[icol].ref.isWritable() )
  {
    // if not writable, privatize for writing
    DataArray *parr = optcol_[icol].ref.privatize(DMI::WRITE).dewr_p();
    DataRecord::replace(optColFieldId(icol),parr,DMI::WRITE);
    optcol_[icol].ptr = parr->getArrayPtr(optColArrayType(icol));
  }
  return optcol_[icol].ptr;
}

void * VellSet::initOptCol (uint icol,bool array)
{
  Thread::Mutex::Lock lock(mutex());
  // attach & return
  DataArray *parr = array ? new DataArray(optColArrayType(icol),shape(),DMI::ZERO)
                          : new DataArray(optColArrayType(icol),LoShape(1),DMI::ZERO);
  optcol_[icol].ref <<= parr;
  (*this)[optColFieldId(icol)].replace() <<= parr;
  return optcol_[icol].ptr = parr->getArrayPtr(optColArrayType(icol));
}

void VellSet::doSetOptCol (uint icol,DataArray *parr,int dmiflags)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(!hasShape(),"VellSet shape not set");
  FailWhen(parr->size() != 1 && parr->shape() != shape(),
           "column "+optColFieldId(icol).toString()+": bad shape");
  // get pointer to blitz array (this also verifies type)
  optcol_[icol].ptr = parr->getArrayPtr(optColArrayType(icol));
  // attach & return
  optcol_[icol].ref.attach(parr,dmiflags);
  (*this)[optColFieldId(icol)].replace().put(*parr,dmiflags);
}

void VellSet::setOptCol (uint icol,const DataArray::Ref::Xfer &ref)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(!hasShape(),"VellSet shape not set");
  FailWhen(ref->size() != 1 && ref->shape() != shape(),
           "column "+optColFieldId(icol).toString()+": bad shape");
  // get pointer to blitz array (this also verifies type)
  optcol_[icol].ptr = const_cast<void*>(ref->getConstArrayPtr(optColArrayType(icol)));
  // attach & return
  optcol_[icol].ref <<= ref;
  (*this)[optColFieldId(icol)].replace() <<= optcol_[icol].ref.copy();
}

void VellSet::clearOptCol (int icol)
{
  Thread::Mutex::Lock lock(mutex());
  DataRecord::removeField(optColFieldId(icol),true);
  optcol_[icol].ref.detach();
  optcol_[icol].ptr = 0;
}


void VellSet::setNumPertSets (int nsets)
{
  Thread::Mutex::Lock lock(mutex());
  // can only change from 0 to smth
  FailWhen(pset_.size() && nsets != int(pset_.size()),
      "can't change the number of perturbation sets in a VellSet");
  pset_.resize(nsets);
  if( numspids_ )
  {
    // setups perturbations structures
    for( int iset=0; iset<nsets; iset++ )
      setupPertData(iset);
  }
}

//##ModelId=400E53550344
void VellSet::setSpids (const vector<int>& spids)
{
  Thread::Mutex::Lock lock(mutex());
  if( numspids_ ) // assigning to existing vector
  {
    FailWhen(spids.size() != uint(numspids_),"setSpids: vector size mismatch" );
    (*this)[FSpids] = spids;
  }
  else // setting new vector
  {
    numspids_ = spids.size();
    if( numspids_ )
    {
      DataField *pdf = new DataField(Tpint,spids.size(),&spids[0]);
      DataRecord::add(FSpids,pdf,DMI::ANONWR);
      spids_ = (*pdf)[HIID()].as_wp<int>();
      for( uint iset=0; iset<pset_.size(); iset++ )
        setupPertData(iset);
    }
  }
}

void VellSet::copySpids (const VellSet &other)
{
  Thread::Mutex::Lock lock(mutex());
  if( numspids_ ) // assigning to existing vector -- check sizes
  {
    FailWhen(other.numSpids() != numspids_,"copySpids: size mismatch" );
  }
  if( !other.numSpids() )
    return;
  DataRecord::replace(FSpids,other[FSpids].ref());
  spids_ = (*this)[FSpids].as_p<int>();
  // if newly allocated spids, setup other data
  if( !numspids_ )
  {
    numspids_ = other.numSpids(); 
    for( uint iset=0; iset<pset_.size(); iset++ )
      setupPertData(iset);
  }
}

//##ModelId=400E53550353
void VellSet::setPerturbation (int i, double value,int iset)
{ 
  Thread::Mutex::Lock lock(mutex());
  DbgAssert(i>=0 && i<numspids_ && iset>=0 && iset<int(pset_.size())); 
  (*this)[FiPerturbations(iset)][i] = value;
//  pset_[iset].pert[i] = value;
}

// set all perturbations at once
//##ModelId=400E53550359
void VellSet::setPerturbations (const vector<double>& perts,int iset)
{
  Thread::Mutex::Lock lock(mutex());
  DbgAssert(iset>=0 && iset<int(pset_.size())); 
  FailWhen(perts.size() != uint(numspids_),"setPerturbations: vector size mismatch" );
  if( numspids_ )
  {
    (*this)[FiPerturbations(iset)] = perts;
    pset_[iset].pert = (*this)[FiPerturbations(iset)].as_p<double>();
  }
}

void VellSet::copyPerturbations (const VellSet &other)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(numSpids() != other.numSpids(),"setPerturbations: number of spids does not match" );
  FailWhen(numPertSets() != other.numPertSets(),"setPerturbations: number of pert sets does not match" );
  if( !other.numSpids() )
    return;
  for( int iset=0; iset<numPertSets(); iset++ )
  {
    (*this)[FiPerturbations(iset)] = other[FiPerturbations(iset)].as_vector<double>();
    pset_[iset].pert = (*this)[FiPerturbations(iset)].as_p<double>();
  }
}

//##ModelId=400E53550360
Vells & VellSet::setValue (Vells *pvells)
{
  Thread::Mutex::Lock lock(mutex());
  if( !hasShape() )
    setShape(pvells->shape());
  else {
    FailWhen(!pvells->isCompatible(shape()),"main value: incompatible shape");
  }
  value_ <<= pvells;
  DataRecord::replace(FValue,&(pvells->getDataArray()),DMI::ANONWR);
  return *pvells;
}

void VellSet::setValue (const Vells::Ref::Xfer &vref)
{
  Thread::Mutex::Lock lock(mutex());
  if( !hasShape() )
    setShape(vref->shape());
  else {
    FailWhen(!vref->isCompatible(shape()),"main value: incompatible shape");
  }
  value_ = vref;
  if( value_.isWritable() )
    DataRecord::replace(FValue,&( value_().getDataArrayWr() ),DMI::WRITE);
  else
    DataRecord::replace(FValue,&( value_->getDataArray() ),DMI::READONLY);
}

//##ModelId=400E53550387
Vells & VellSet::setPerturbedValue (int i,Vells *pvells,int iset)
{
  Thread::Mutex::Lock lock(mutex());
  DbgAssert(i>=0 && i<numspids_ && iset>=0 && iset<int(pset_.size())); 
  FailWhen(!hasShape(),"VellSet shape not set");
  FailWhen(!pvells->isCompatible(shape()),
        Debug::ssprintf("perturbed value %d/%d: incompatible shape",i,iset));
  PerturbationSet &ps = pset_[iset];
  // allocate container for perturbed values
  if( !ps.pertval_field.valid() )
  {
    DataField *df = new DataField(TpDataArray,numspids_);
    ps.pertval_field <<= df;
    DataRecord::add(FiPerturbedValues(iset),df,DMI::ANONWR);
  }
  ps.pertval_field().put(i,&( pvells->getDataArray() ),DMI::ANONWR);
  ps.pertval[i] <<= pvells;
  return *pvells;
}

void VellSet::setPerturbedValue (int i,const Vells::Ref::Xfer &vref,int iset)
{
  Thread::Mutex::Lock lock(mutex());
  DbgAssert(i>=0 && i<numspids_ && iset>=0 && iset<int(pset_.size())); 
  FailWhen(!hasShape(),"VellSet shape not set");
  FailWhen(!vref->isCompatible(shape()),
        Debug::ssprintf("perturbed value %d/%d: incompatible shape",i,iset));
  PerturbationSet &ps = pset_[iset];
  // allocate container for perturbed values
  if( !ps.pertval_field.valid() )
  {
    DataField *df = new DataField(TpDataArray,numspids_);
    ps.pertval_field <<= df;
    DataRecord::add(FiPerturbedValues(iset),df,DMI::ANONWR);
  }
  Vells::Ref &ref = ps.pertval[i];
  ref = vref;
  if( ref.isWritable() )
    ps.pertval_field().put(i,&( ref().getDataArrayWr() ),DMI::WRITE);
  else
    ps.pertval_field().put(i,&( ref->getDataArray() ),DMI::READONLY);
}


//##ModelId=400E53550393
void VellSet::addFail (const DataRecord *rec,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  clear();
  is_fail_ = true;
  // clear out the DR
  DataRecord::removeField(FValue,true);
  DataRecord::removeField(FSpids,true);
  DataRecord::removeField(FPerturbations,true);
  DataRecord::removeField(FPerturbedValues,true);
  // get address of fail field (create it as necessary)
  DataList *fails = (*this)[FFail].as_wpo<DataList>();
  if( !fails  )
  {
    DataRecord::add(FFail,fails = new DataList,DMI::ANONWR);
  }
  // add record to fail field
  fails->addBack(rec,(flags&~DMI::WRITE)|DMI::READONLY);
}

//##ModelId=400E53550399
void VellSet::addFail (const string &nodename,const string &classname,
                      const string &origin,int origin_line,const string &msg)
{
  Thread::Mutex::Lock lock(mutex());
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
  Thread::Mutex::Lock lock(mutex());
  if( isFail() )
  {
    const DataList & fails = (*this)[FFail].as<DataList>();
    for( int i=0; i<fails.size(); i++ )
      os << "FAIL: " << fails[i][FMessage].as<string>() <<endl;
  }
  else
  {
    os << "Value" << *value_;
    os << "  " << numspids_ << " spids; " << pset_.size() << " pert set(s)\n";
    for( int i=0; i<numspids_; i++) 
    {
      os << "  spid " << spids_[i] << " ";
      for( uint iset=0; iset<pset_.size(); iset++ )
      {
        if( iset )
          os << "          ";
        os << " pert " <<iset<<": "<<pset_[iset].pert[i];
        if( pset_[iset].pertval[i].valid() && !pset_[iset].pertval[i]->isNull() )
        {
          os << (*(pset_[iset].pertval[i]) - *value_);
        }
        else
        {
          os << ": perturbed vells "<<i<<" null or missing"<<endl;
        }
      }
    }
  }
}


} // namespace Meq

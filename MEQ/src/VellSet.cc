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
#include <DMI/NumArray.h>
#include <DMI/List.h>

namespace Meq {

static DMI::Container::Register reg(TpMeqVellSet,true);

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

// OMS 28/01/05: phasing this out, replace with explicit data flags
// static const HIID optColFieldId_array[] = { FFlags, FWeight };
// 
// const HIID & OptionalColumns::optColFieldId (uint icol)
// {
//   DbgAssert1(icol<NUM_OPTIONAL_COL);
//   return optColFieldId_array[icol];
// }

//##ModelId=400E5355031E
VellSet::VellSet (const LoShape &shp,int nspid,int nset)
: pvalue_       (0),
  pflags_       (0),
  default_pert_ (0.),
  pset_         (nset),
  spids_        (0),
  numspids_     (nspid),
  is_fail_      (false)
{
  init();
  setShape(shp);
}

VellSet::VellSet (int nspid,int nset)
: pvalue_       (0),
  pflags_       (0),
  default_pert_ (0.),
  pset_         (nset),
  spids_        (0),
  numspids_     (nspid),
  is_fail_      (false)
{
  init();
}

void VellSet::init ()
{
//  // clear optional columns
//  for( uint i=0; i<NUM_OPTIONAL_COL; i++ )
//    optcol_[i].ptr = 0;
  // create appropriate fields in the record: spids vector and perturbations vector
  if( numspids_ )
  {
    DMI::Vec *pdf = new DMI::Vec(Tpint,numspids_);
    ObjRef ref(pdf);
    Record::addField(FSpids,ref,DMI::REPLACE|Record::PROTECT);
    spids_ = (*pdf)[HIID()].as_wp<int>();
    // setups perturbations structures
    for( uint iset=0; iset<pset_.size(); iset++ )
      setupPertData(iset);
  }
}

//##ModelId=400E53550322
VellSet::VellSet (const DMI::Record &other,int flags,int depth)
: Record(),
  default_pert_ (0.),
  pset_         (0),
  spids_        (0),
  numspids_     (0),
  is_fail_      (false)
{
//  // clear optional columns
//  for( uint i=0; i<NUM_OPTIONAL_COL; i++ )
//    optcol_[i].ptr = 0;
  Record::cloneOther(other,flags,depth,true);
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
  DMI::Vec *pdf = new DMI::Vec(Tpdouble,numspids_);
  ObjRef ref(pdf);
  Record::addField(FiPerturbations(iset),ref,DMI::REPLACE|Record::PROTECT);
  pset_[iset].pert = (*pdf)[HIID()].as_wp<double>();
  // add perturbed values field
  pdf = new DMI::Vec(TpMeqVells,numspids_);
  ref <<= pdf;
  Field & field = Record::addField(FiPerturbedValues(iset),ref,DMI::REPLACE|Record::PROTECT);
  pset_[iset].pertval_vec = &( field.ref.ref_cast<DMI::Vec>() );
}

void VellSet::setShape (const Vells::Shape &shp)
{
  Thread::Mutex::Lock lock(mutex());
  if( hasShape() )
  {
    FailWhen(shape_ != shp,"different VellSet shape already set");
  }
  else
  {
    shape_ = shp;
    ObjRef ref(new DMI::Vec(Tpint,shp.size(),&(shp[0])));
    Record::addField(FShape,ref,DMI::REPLACE|Record::PROTECT);
  }
}

    
//##ModelId=400E5355033A
void VellSet::validateContent (bool)
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields, and that they're
  // indeed writable. Setup shortcuts to their contents
  try
  {
    if( Record::hasField(FFail) ) // a fail result
    {
      is_fail_ = true;
    }
    else
    {
      is_fail_ = false;
      // get shape from data record
      Field * fld = Record::findField(FShape);
      if( fld )
      {
        const Container & cc = fld->ref.as<Container>();
        std::vector<int> shp = cc[HIID()].as_vector<int>();
        FailWhen(int(shp.size())>Axis::MaxAxis,"illegal "+FShape.toString()+" field");
        shape_ = shp;
        fld->protect = true;
      }
      else
        shape_.clear();
      // get flags, if they exist in the data record
      fld = Record::findField(FFlags);
      const Vells * flagvells = 0;
      if( fld )
      {
        pflags_ = &( fld->ref.ref_cast<Vells>() );
        flagvells = pflags_->deref_p();
        // check for matching shape
        FailWhen(!flagvells->isFlags(),"dataflags: invalid type "+flagvells->elementType().toString());
        FailWhen(!flagvells->isCompatible(shape_),"dataflags: incompatible shape");
        fld->protect = true;
      }
      else
        pflags_ = 0;
      // get value, if it exists in the data record
      fld = Record::findField(FValue);
      if( fld )
      {
        pvalue_ = &( fld->ref.ref_cast<Vells>() );
        // check for matching shape
        const Vells &val = pvalue_->deref();
        FailWhen(!val.isCompatible(shape_),"main value: incompatible shape");
        fld->protect = true;
        // init flags in this Vells
        Vells::Ref &vr = *pvalue_;
        if( flagvells )
        {
          if( !vr->hasDataFlags() || &(vr->dataFlags()) != flagvells )
            vr().setDataFlags(flagvells);
        }
        else if( vr->hasDataFlags() ) // get rid of flags if we have none
          vr().clearDataFlags();
      }
      else
        pvalue_ = 0;
//       // get optional columns, if they exist in the data record
//       for( int i=0; i<NUM_OPTIONAL_COL; i++ )
//       {
//         Hook hcol(*this,optColFieldId(i));
//         if( hcol.exists() )
//         {
//           FailWhen(!pvalue_,"missing main value");
//           const DMI::NumArray &darr = *(optcol_[i].ref = hcol.ref());
//           FailWhen(darr.size() != 1 && darr.shape() != shape_,
//                    "column "+optColFieldId(i).toString()+": bad shape");
//           // cast away const here: writability is checked separately
//           optcol_[i].ptr = const_cast<void*>(darr.getConstArrayPtr(optColArrayType(i)));
//         }
//         else
//           optcol_[i].ptr = 0;
//       }
      // get spids and perturbations, if they exist
      fld = Record::findField(FSpids);
      if( fld )
      {
        const Container & cc = fld->ref.as<Container>();
        spids_ = cc[HIID()].as_p<int>(numspids_);
        FailWhen(!pvalue_,"missing main value");
        fld->protect = true;
        int size;
        // figure out number of perturbation sets in the record and setup shortcuts
        pset_.reserve(2);
        int iset = 0;
        while( (fld = Record::findField(FiPerturbations(iset))) != 0 )
        {
          fld->protect = true;
          pset_.resize(iset+1);
          Container &cc = fld->ref.as<Container>();
          pset_[iset].pert = cc[HIID()].as_wp<double>(size);
          FailWhen(size!=numspids_,"size mismatch between spids and "+FiPerturbations(iset).toString());
          // get perturbations, if they exist
          HIID fld_id = FiPerturbedValues(iset);
          fld = Record::findField(fld_id);
          if( fld )
          {
            DMI::Vec::Ref *pvr = &( fld->ref.ref_cast<DMI::Vec>() );
            const DMI::Vec * pvec = pvr->deref_p();
            FailWhen(pvec->type() != TpMeqVells,fld_id.toString()+": not MeqVells");
            FailWhen(pvec->size() != numspids_,"size mismatch between spids and "+fld_id.toString());
            pset_[iset].pertval_vec = pvr;
            fld->protect = true;
            // init flags in perturbed Vells
            for( int i=0; i<numspids_; i++ )
            {
              const Vells &val = pvec->as<Vells>(i);
              if( flagvells )
              {
                if( !val.hasDataFlags() || &(val.dataFlags()) != flagvells )
                {
                  DMI::Vec & wvec = pvr->dewr(); // COW as needed
                  wvec.as<Vells>(i).setDataFlags(flagvells);
                  pvec = &wvec;
                }
              }
              else if( val.hasDataFlags() ) // get rid of flags if we have none
              {
                DMI::Vec & wvec = pvr->dewr(); // COW as needed
                wvec.as<Vells>(i).clearDataFlags();
                pvec = &wvec;
              }
            }
          }
          else
          {            // add new perturbed values field
            ObjRef ref(new DMI::Vec(TpMeqVells,numspids_));
            Field & field = Record::addField(fld_id,ref,Record::PROTECT);
            pset_[iset].pertval_vec = &( field.ref.ref_cast<DMI::Vec>() );
          }
          iset++;
        }
      }
      else
      {
        spids_ = 0;
        numspids_ = 0;
        pset_.resize(0);
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
  Thread::Mutex::Lock lock(mutex());
  Record::clear();
  shape_.clear();
  numspids_ = 0;
  spids_ = 0;
  pset_.resize(0);
  pvalue_ = 0;
  pflags_ = 0;
  is_fail_ = false;
//   // clear optional columns
//   for( int i=0; i<NUM_OPTIONAL_COL; i++ )
//   {
//     optcol_[i].ptr = 0;
//     optcol_[i].ref.detach();
//   }
}

// OMS 28/01/05: phasing this out, replace with explicit data flags
// void * VellSet::writeOptCol (uint icol)
// {
//   Thread::Mutex::Lock lock(mutex());
//   Assert(hasOptCol(icol));
// //   // ensure COW
// //   DMI::NumArray *parr = optcol_[icol].ref.privatize(DMI::WRITE).dewr_p();
// //   if( !optcol_[icol].ref.isWritable() )
// //   {
// //     // if not writable, privatize for writing
// //     DMI::NumArray *parr = optcol_[icol].ref.privatize(DMI::WRITE).dewr_p();
// //     DMI::Record::replace(optColFieldId(icol),parr,DMI::WRITE);
// //     optcol_[icol].ptr = parr->getArrayPtr(optColArrayType(icol));
// //   }
//   return optcol_[icol].ptr;
// }
// 
// void * VellSet::initOptCol (uint icol,bool array)
// {
//   Thread::Mutex::Lock lock(mutex());
//   // attach & return
//   DMI::NumArray *parr = array ? new DMI::NumArray(optColArrayType(icol),shape())
//                           : new DMI::NumArray(optColArrayType(icol),LoShape(1));
//   optcol_[icol].ref <<= parr;
//   (*this)[optColFieldId(icol)].replace() <<= parr;
//   return optcol_[icol].ptr = parr->getArrayPtr(optColArrayType(icol));
// }
// 
// void VellSet::doSetOptCol (uint icol,DMI::NumArray *parr,int dmiflags)
// {
//   Thread::Mutex::Lock lock(mutex());
//   FailWhen(!hasShape(),"VellSet shape not set");
//   FailWhen(parr->size() != 1 && parr->shape() != shape(),
//            "column "+optColFieldId(icol).toString()+": bad shape");
//   // get pointer to blitz array (this also verifies type)
//   optcol_[icol].ptr = parr->getArrayPtr(optColArrayType(icol));
//   // attach & return
//   optcol_[icol].ref.attach(parr,dmiflags);
//   (*this)[optColFieldId(icol)].replace().put(*parr,dmiflags);
// }
// 
// void VellSet::setOptCol (uint icol,const DMI::NumArray::Ref &ref)
// {
//   Thread::Mutex::Lock lock(mutex());
//   FailWhen(!hasShape(),"VellSet shape not set");
//   FailWhen(ref->size() != 1 && ref->shape() != shape(),
//            "column "+optColFieldId(icol).toString()+": bad shape");
//   // get pointer to blitz array (this also verifies type)
//   optcol_[icol].ptr = const_cast<void*>(ref->getConstArrayPtr(optColArrayType(icol)));
//   // attach & return
//   optcol_[icol].ref <<= ref;
//   (*this)[optColFieldId(icol)].replace() <<= optcol_[icol].ref.copy();
// }
// 
// void VellSet::clearOptCol (int icol)
// {
//   Thread::Mutex::Lock lock(mutex());
//   Record::removeField(optColFieldId(icol),true,0);
//   optcol_[icol].ref.detach();
//   optcol_[icol].ptr = 0;
// }
// 

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
  }
  else
  { // setup pert data if assigning new vector
    numspids_ = spids.size();
    for( uint iset=0; iset<pset_.size(); iset++ )
      setupPertData(iset);
  }
  if( numspids_ )
  {
    DMI::Vec *pdf = new DMI::Vec(Tpint,spids.size(),&spids[0]);
    ObjRef ref(pdf);
    Record::addField(FSpids,ref,DMI::REPLACE|Record::PROTECT);
    spids_ = (*pdf)[HIID()].as_p<int>();
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
  ObjRef ref = other.get(FSpids);
  Field & field = Record::addField(FSpids,ref,DMI::REPLACE|Record::PROTECT);
  const Container &cc = field.ref.as<Container>();
  spids_ = cc[HIID()].as_p<int>();
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
  pset_[iset].pert[i] = value;
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
    DMI::Vec *pdf = new DMI::Vec(Tpdouble,numspids_,&perts[0]);
    ObjRef ref(pdf);
    Field & field = Record::addField(FiPerturbations(iset),ref,DMI::REPLACE|Record::PROTECT);
    pset_[iset].pert = (*pdf)[HIID()].as_wp<double>();
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
    ObjRef ref = other.get(FiPerturbations(iset));
    Field & field = Record::addField(FiPerturbations(iset),ref,DMI::REPLACE|Record::PROTECT);
    Container &cc = field.ref.as<Container>();
    pset_[iset].pert = cc[HIID()].as_wp<double>();
  }
}

void VellSet::setDataFlags (const Vells::Ref &flags)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(!flags->isFlags(),"dataflags: invalid type "+flags->elementType().toString());
  FailWhen(!hasShape(),"can't attach flags to VellSet until shape has been specified");
  FailWhen(!flags->isCompatible(shape()),"shape of flags Vells not compatible with VellSet");
  Field & field = Record::addField(FFlags,flags.ref_cast<BObj>(),DMI::REPLACE|Record::PROTECT);
  pflags_ = &( field.ref.ref_cast<Vells>() );
  // set flags in all values
  if( pvalue_ )
    pvalue_->dewr().setDataFlags(flags);
  if( numSpids() )
  {
    for( int iset=0; iset<numPertSets(); iset++ )
      if( pset_[iset].pertval_vec )
      {
        DMI::Vec & pvec = pset_[iset].pertval_vec->dewr();
        for( int i=0; i<numSpids(); i++ )
          pvec.as<Vells>(i).setDataFlags(flags);
      }
  }
}

void VellSet::clearDataFlags ()
{
  Thread::Mutex::Lock lock(mutex());
  if( !pflags_ )
    return;
  pflags_ = 0;
  // clear flags in all values
  if( pvalue_ && pvalue_->deref().hasDataFlags() )
    pvalue_->dewr().clearDataFlags();
  for( int iset=0; iset<numPertSets(); iset++ )
  {
    const DMI::Vec * pvec = pset_[iset].pertval_vec->deref_p();
    for( int i=0; i<numSpids(); i++ )
      if( pvec->as<Vells>(i).hasDataFlags() )
      {
        DMI::Vec *wvec = pset_[iset].pertval_vec->dewr_p();
        pvec = wvec;
        wvec->as<Vells>(i).clearDataFlags();
      }
  }
}


void VellSet::setValue (Vells::Ref &ref,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  if( !hasShape() )
    setShape(ref->shape());
  else {
    FailWhen(!ref->isCompatible(shape()),"main value: incompatible shape");
  }
  // attach flags if we have them
  if( hasDataFlags() )
    ref().setDataFlags(dataFlags());
  Field & field = Record::addField(FValue,ref.ref_cast<BObj>(),flags|DMI::REPLACE|Record::PROTECT);
  pvalue_ = &( field.ref.ref_cast<Vells>() );
}

void VellSet::setPerturbedValue (int i,Vells::Ref &ref,int iset,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  DbgAssert(i>=0 && i<numspids_ && iset>=0 && iset<int(pset_.size())); 
  FailWhen(!hasShape(),"VellSet shape not set");
  FailWhen(!ref->isCompatible(shape()),
        Debug::ssprintf("perturbed value %d/%d: incompatible shape",i,iset));
  PerturbationSet &ps = pset_[iset];
  // allocate container for perturbed values
  FailWhen(!ps.pertval_vec,"perturbed values not initialized in this VellSet");
  // attach flags if we have them
  if( hasDataFlags() )
    ref().setDataFlags(dataFlags());
  ps.pertval_vec->dewr().put(i,ref,flags);
}

//##ModelId=400E53550393
void VellSet::addFail (const DMI::Record *rec,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  clear();
  is_fail_ = true;
  // clear out the DR
  Record::removeField(FValue,true,0);
  Record::removeField(FSpids,true,0);
  for( int i=0; i<2; i++ )
  {
    Record::removeField(FiPerturbations(i),true,0);
    Record::removeField(FiPerturbations(i),true,0);
  }
  // get address of fail field (hook will create it as necessary)
  DMI::List *fails = (*this)[FFail].as_wpo<DMI::List>();
  if( !fails  )
  {
    Record::add(FFail,fails = new DMI::List);
  }
  // add record to fail field
  fails->addBack(rec,0);
}

//##ModelId=400E53550399
void VellSet::addFail (const string &nodename,const string &classname,
                      const string &origin,int origin_line,const string &msg)
{
  Thread::Mutex::Lock lock(mutex());
  DMI::Record::Ref ref;
  DMI::Record & rec = ref <<= new DMI::Record;
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
const DMI::Record & VellSet::getFail (int i) const
{
  return (*this)[FFail][i].as<DMI::Record>();
}

//##ModelId=400E535503AE
void VellSet::show (std::ostream& os) const
{
  Thread::Mutex::Lock lock(mutex());
  if( isFail() )
  {
    const DMI::List & fails = (*this)[FFail].as<DMI::List>();
    for( int i=0; i<fails.size(); i++ )
      os << "FAIL: " << fails[i][FMessage].as<string>() <<endl;
  }
  else
  {
    os << "Value " << pvalue_->deref();
    os << "  " << numspids_ << " spids; " << pset_.size() << " pert set(s)\n";
    for( int i=0; i<numspids_; i++) 
    {
      os << "  spid " << spids_[i] << " ";
      for( uint iset=0; iset<pset_.size(); iset++ )
      {
        if( iset )
          os << "          ";
        os << " pert " <<iset<<": "<<pset_[iset].pert[i];
        ObjRef ref = pset_[iset].pertval_vec->deref().getObj(i);
        if( ref.valid() )
        {
          const Vells &pval = ref.as<Vells>();
          if( !pval.isNull() )
            os << pval - pvalue_->deref();
          else
            os << ": perturbed vells "<<i<<" is null"<<endl;
        }
        else
        {
          os << ": perturbed vells "<<i<<" is missing"<<endl;
        }
      }
      os<<"\n";
    }
  }
}


} // namespace Meq

//# VellSet.cc: The result of an expression for a domain.
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
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
  pweights_     (0),
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
  pweights_     (0),
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
  pset_[iset].pertval_vec = &( field.ref().ref_cast<DMI::Vec>() );
}

void VellSet::setShape (const Vells::Shape &shp)
{
  Thread::Mutex::Lock lock(mutex());
  if( hasShape() )
  {
    FailWhen(!Vells::isCompatible(shape_,shp),
              "non-conforming VellSet shape already set");
  }
  shape_ = shp;
  ObjRef ref(new DMI::Vec(Tpint,shp.size(),&(shp[0])));
  Record::addField(FShape,ref,DMI::REPLACE|Record::PROTECT);
}

void VellSet::verifyShape (bool reset)
{
  Thread::Mutex::Lock lock(mutex());
  LoShape shp;
  if( !reset )
    shp = shape_;
  bool adjusted = false;
  if( pvalue_ )
    adjusted |= adjustShape(shp,pvalue_->deref());
  if( hasDataFlags() )
    adjusted |= adjustShape(shp,dataFlags());
  if( hasDataWeights() )
    adjusted |= adjustShape(shp,dataWeights());
  for( uint iset=0; iset<pset_.size(); iset++ )
    for( int i=0; i<numspids_; i++ )
      adjusted |= adjustShape(shp,getPerturbedValue(i,iset));
  // set new shape if needed
  if( adjusted )
    setShape(shp);
}

bool VellSet::adjustShape (LoShape &shp,const Vells &vells)
{
  // ignore null or scalar vells
  if( !vells.valid() || vells.isScalar() )
    return false;
  const Vells::Shape &vs = vells.shape();
  // no shape? simply set from vells
  if( shp.empty() )
  {
    shp = vs;
    return true;
  }
  // resize to Vells rank (tail filled with 0s)
  if( vs.size() > shp.size() )
    shp.resize(vs.size());
  int changed = 0;
  for( uint i=0; i<vs.size(); i++ )
  {
    if( vs[i]>1 )
    {
      if( shp[i]<=1 )
        changed = shp[i] = vs[i];
      else
      {
        FailWhen(shp[i]!=vs[i],"Vells does not conform to shape of VellSet");
      }
    }
    else if( shp[i] == 0 )
      changed = shp[i] = 1;
  }
  return changed;
}

void VellSet::adjustShape (const Vells &vells)
{
  // ignore null or scalar vells
  if( !vells.valid() || vells.isScalar() )
    return;
  LoShape shp = shape_;
  if( adjustShape(shp,vells) )
    setShape(shp);
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
        fld->ref().as<Container>()[HIID()].get_vector(shape_);
        FailWhen(int(shape_.size())>Axis::MaxAxis,"illegal "+FShape.toString()+" field");
        fld->protect(true);
      }
      else
        shape_.clear();
      // get flags, if they exist in the data record
      fld = Record::findField(FFlags);
      const Vells * flagvells = 0;
      if( fld )
      {
        pflags_ = &( fld->ref().ref_cast<Vells>() );
        flagvells = pflags_->deref_p();
        FailWhen(!flagvells->isFlags(),"flags: invalid type "+flagvells->elementType().toString());
        fld->protect(true);
      }
      else
        pflags_ = 0;
      // get weights, if they exist in the data record
      fld = Record::findField(FWeights);
      if( fld )
      {
        pweights_ = &( fld->ref().ref_cast<Vells>() );
        FailWhen(!(*pweights_)->isReal(),"weights: invalid type "+(*pweights_)->elementType().toString());
        fld->protect(true);
      }
      else
        pweights_ = 0;
      // get value, if it exists in the data record
      fld = Record::findField(FValue);
      if( fld )
      {
        pvalue_ = &( fld->ref().ref_cast<Vells>() );
        // check for matching shape
        const Vells &val = pvalue_->deref();
        fld->protect(true);
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
      // get spids and perturbations, if they exist
      fld = Record::findField(FSpids);
      if( fld )
      {
        const Container & cc = fld->ref().as<Container>();
        spids_ = cc[HIID()].as_p<int>(numspids_);
        FailWhen(!pvalue_,"missing main value");
        fld->protect(true);
        int size;
        // figure out number of perturbation sets in the record and setup shortcuts
        pset_.reserve(2);
        int iset = 0;
        while( (fld = Record::findField(FiPerturbations(iset))) != 0 )
        {
          fld->protect(true);
          pset_.resize(iset+1);
          Container &cc = fld->ref().as<Container>();
          pset_[iset].pert = cc[HIID()].as_wp<double>(size);
          FailWhen(size!=numspids_,"size mismatch between spids and "+FiPerturbations(iset).toString());
          // get perturbations, if they exist
          HIID fld_id = FiPerturbedValues(iset);
          fld = Record::findField(fld_id);
          if( fld )
          {
            DMI::Vec::Ref *pvr = &( fld->ref().ref_cast<DMI::Vec>() );
            const DMI::Vec * pvec = pvr->deref_p();
            FailWhen(pvec->type() != TpMeqVells,fld_id.toString()+": not MeqVells");
            FailWhen(pvec->size() != numspids_,"size mismatch between spids and "+fld_id.toString());
            pset_[iset].pertval_vec = pvr;
            fld->protect(true);
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
            pset_[iset].pertval_vec = &( field.ref().ref_cast<DMI::Vec>() );
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
      verifyShape();
    }
  }
  catch( std::exception &err )
  {
//    cerr<<"Failed VellSet: "<<sdebug(10)<<endl;
    clear();
    ThrowMore(err,"Validate of Meq::VellSet record failed");
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
  pset_.clear();
  pvalue_ = 0;
  pflags_ = 0;
  is_fail_ = false;
}


void VellSet::setNumPertSets (int nsets)
{
  Thread::Mutex::Lock lock(mutex());
  // setting to 0 clears the pertsets
  if( !nsets )
  {
    Record::removeField(FSpids,true,0);
    for( uint i=0; i<pset_.size(); i++ )
    {
      Record::removeField(FiPerturbations(i),true,0);
      Record::removeField(FiPerturbedValues(i),true,0);
    }
    numspids_ = 0;
    spids_ = 0;
    pset_.clear();
    return;
  }
  // else can only change from 0 to smth
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
  const Container &cc = field.ref().as<Container>();
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
    Container &cc = field.ref().as<Container>();
    pset_[iset].pert = cc[HIID()].as_wp<double>();
  }
}

void VellSet::setDataFlags (const Vells::Ref &flags)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(!flags->isFlags(),"flags: invalid type "+flags->elementType().toString());
  adjustShape(*flags);
  Field & field = Record::addField(FFlags,flags.ref_cast<BObj>(),DMI::REPLACE|Record::PROTECT);
  pflags_ = &( field.ref().ref_cast<Vells>() );
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
  Record::removeField(FFlags,true,0);
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

void VellSet::setDataWeights (const Vells::Ref &weights)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(!weights->isReal(),"weights: invalid type "+weights->elementType().toString());
  adjustShape(*weights);
  Field & field = Record::addField(FWeights,weights.ref_cast<BObj>(),DMI::REPLACE|Record::PROTECT);
  pweights_ = &( field.ref().ref_cast<Vells>() );
}

void VellSet::clearDataWeights ()
{
  Thread::Mutex::Lock lock(mutex());
  if( !pweights_ )
    return;
  Record::removeField(FWeights,true,0);
  pweights_ = 0;
}

void VellSet::setValue (Vells::Ref &ref,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  adjustShape(*ref);
  // attach flags if we have them
  if( hasDataFlags() )
    ref().setDataFlags(dataFlags());
  Field & field = Record::addField(FValue,ref.ref_cast<BObj>(),flags|DMI::REPLACE|Record::PROTECT);
  pvalue_ = &( field.ref().ref_cast<Vells>() );
}

void VellSet::setPerturbedValue (int i,Vells::Ref &ref,int iset,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  DbgAssert(i>=0 && i<numspids_ && iset>=0 && iset<int(pset_.size())); 
  adjustShape(*ref);
  PerturbationSet &ps = pset_[iset];
  // allocate container for perturbed values
  FailWhen(!ps.pertval_vec,"perturbed values not initialized in this VellSet");
  // attach flags if we have them
  if( hasDataFlags() )
    ref().setDataFlags(dataFlags());
  ps.pertval_vec->dewr().put(i,ref,flags);
}

//##ModelId=400E53550393
void VellSet::addFail (const ObjRef &ref)
{
  Thread::Mutex::Lock lock(mutex());
  clear();
  is_fail_ = true;
  // clear out the DR
  Record::removeField(FValue,true,0);
  Record::removeField(FSpids,true,0);
  Record::removeField(FShape,true,0);
  for( int i=0; i<2; i++ )
  {
    Record::removeField(FiPerturbations(i),true,0);
    Record::removeField(FiPerturbations(i),true,0);
  }
  // plist!=0 if fail is a list (otherwise treat it as a single fail-record)
  const DMI::List *plist = dynamic_cast<const DMI::List *>(ref.deref_p());
  // do we have a fail field already?
  DMI::List *fails = (*this)[FFail].as_wpo<DMI::List>();
  if( !fails  )
  {
    if( plist ) // directly put list in if we have one
    {
      Record::add(FFail,plist);
      return;
    }
    Record::add(FFail,fails = new DMI::List);
  }
  // we have an existing fail field -- append or merge
  if( plist )
    fails->append(*plist);
  else  
    fails->addBack(ref);
}

//##ModelId=400E535503A7
int VellSet::numFails () const
{
  return (*this)[FFail].size();
}
  
//##ModelId=400E535503A9
ObjRef VellSet::getFail (int i) const
{
  return (*this)[FFail][i].ref();
}

const std::string & VellSet::getFailMessage (int i) const
{
  return (*this)[FFail][i][AidMessage];
}

DMI::ExceptionList & VellSet::addToExceptionList (DMI::ExceptionList &list) const
{
  // get address of fail field (hook will create it as necessary)
  const DMI::List *fails = (*this)[FFail].as_po<DMI::List>();
  if( fails )
    list.add(*fails);
  return list;
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
          if( pval.valid() )
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

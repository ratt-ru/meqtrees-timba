//# Funklet.cc: Polynomial coefficients
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

#include <TimBase/Profiling/PerfProfile.h>

#include "Funklet.h"
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/MeqVocabulary.h>
#include <TimBase/Debug.h>
#include <TimBase/lofar_vector.h>
#include <cstdlib>
#include <cmath>

namespace Meq {
using namespace DMI;

static DMI::Container::Register reg(TpMeqFunklet,true);


//   const int    defaultFunkletAxes[defaultFunkletRank]   = {0,1,2,3,4,5,6,7};
//   const double defaultFunkletOffset[defaultFunkletRank] = {0,0,0,0,0,0,0,0};
//   const double defaultFunkletScale[defaultFunkletRank]  = {1,1,1,1,1,1,1,1};
  const int    defaultFunkletAxes[defaultFunkletRank]   = {0,1};
  const double defaultFunkletOffset[defaultFunkletRank] = {0,0};
  const double defaultFunkletScale[defaultFunkletRank]  = {1,1};

static std::vector<int> default_axes(defaultFunkletAxes,defaultFunkletAxes+defaultFunkletRank);
static std::vector<double> default_offset(defaultFunkletOffset,defaultFunkletOffset+defaultFunkletRank);
static std::vector<double> default_scale(defaultFunkletScale,defaultFunkletScale+defaultFunkletRank);

Domain Funklet::default_domain;

//##ModelId=3F86886F0366
Funklet::Funklet(double pert,double weight,DbId id)
  :pcoeff_(0)
{
  init(0,0,0,0,pert,weight,id);
}

Funklet::Funklet(int naxis,const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
  :pcoeff_(0)
{
  init(naxis,iaxis,offset,scale,pert,weight,id);
}

//##ModelId=400E5354033A
Funklet::Funklet (const DMI::Record &other,int flags,int depth)
  : DMI::Record(other,flags,depth),pcoeff_(0)
{
  validateContent(false); // not recursive
}

Funklet::Funklet (const Funklet &other,int flags,int depth)
: DMI::Record(other,flags,depth),
  axes_(other.axes_),
  offsets_(other.offsets_),
  scales_(other.scales_),
  spids_(other.spids_),
  spidInx_(other.spidInx_),
  parm_perts_(other.parm_perts_),
  spid_perts_(other.spid_perts_),
  pertValue_(other.pertValue_),
  weight_(other.weight_),
  id_(other.id_)
{
  //  cdebug(0)<<"creating funklet from other "<<other.objectType()<<endl;
  //  cdebug(0)<<"rank = "<<rank()<<endl;
// no need to validate content outside the domain and coeff, because other funklet will be 
// valid anyway
  Field * fld = Record::findField(FDomain);
  if( fld )
    domain_ = fld->ref();
  else
    domain_ <<= new Domain;
  Field *cfld = Record::findField(FCoeff);

  pcoeff_ = cfld ? &( cfld->ref().ref_cast<DMI::NumArray>() ) : 0;
}

void Funklet::validateContent (bool)    
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields; setup shortcuts
  // to their contents
  try
  {
    Field * fld = Record::findField(FDomain);
    if( fld )
      domain_ = fld->ref();
    else
      domain_ <<= new Domain;
    // get various others
// OMS 10/01/05: assigning vectors has been consistently crashing in mt_alloc
// with g++-3.4.5. Rewriting this to try to get around it (will be more efficient 
// this way in any case)
    if( !(*this)[FAxisIndex].get_vector(axes_) )
      (*this)[FAxisIndex].replace() = axes_ = default_axes;
    if( !(*this)[FOffset].get_vector(offsets_) )
      (*this)[FOffset].replace() = offsets_ = default_offset;
    if( !(*this)[FScale].get_vector(scales_) )
      (*this)[FScale].replace() = scales_ = default_scale;
//     axes_       = (*this)[FAxisIndex].as_vector(default_axes);
//     if(!Record::hasField(FAxisIndex))
//       (*this)[FAxisIndex].replace()=axes_;
//     offsets_    = (*this)[FOffset].as_vector(default_offset);
//     if(!Record::hasField(FOffset))
//       (*this)[FOffset].replace()=offsets_;
//     scales_     = (*this)[FScale].as_vector(default_scale);
//     if(!Record::hasField(FScale))
//       (*this)[FScale].replace()=scales_;
//    Assert(axes_.size() >= uint(rank()) && offsets_.size() >= uint(rank()) && scales_.size() >= uint(rank()) );
    //?? rank() is  defined as axes_.size(), no need to check really....

    uint rnk = uint(rank());
    if(offsets_.size() < rnk)
      {
	for(uint i=offsets_.size();i<rnk;i++)
	  offsets_.push_back(0.);
        (*this)[FOffset].replace()=offsets_;
      }
    if(scales_.size() < rnk)
      {
	for(uint i=scales_.size();i<rnk;i++)
	  scales_.push_back(1.);
        (*this)[FScale].replace()=scales_;
      }

    pertValue_  = (*this)[FPerturbation].as<double>(defaultFunkletPerturbation);
    weight_     = (*this)[FWeight].as<double>(defaultFunkletWeight);
    id_         = (*this)[FDbId].as<int>(-1);
    

    fld = Record::findField(FCoeff);
    if( fld ){
      pcoeff_ = &( fld->ref().ref_cast<DMI::NumArray>() );
      //coeff should be doubles:
      if ((*pcoeff_)->elementType()==Tpint ||(*pcoeff_)->elementType()==Tpfloat||(*pcoeff_)->elementType()==Tplong )
	{
	  //convert to double

	}
      FailWhen((*pcoeff_)->elementType()!=Tpdouble,"Meq::Funklet: coeff array must be of type double");
     

    }
    else
      pcoeff_ = 0;
    // check for sanity
    Assert( coeff().rank()<=rank());
  }
  catch( std::exception &err )
  {
    ThrowMore(err,"validate of Funklet record failed");
  }
  catch( ... )
  {
    Throw("validate of Funklet record failed with unknown exception");
  }
}

// sets all of a funklet's axes and attributes in one go
void Funklet::init (int rnk,const int iaxis[],
                    const double offset[],
                    const double scale[],
                    double pert,double weight,DbId id)
{
  Thread::Mutex::Lock lock(mutex());

  FailWhen(rnk<0 || rnk>maxFunkletRank(),"illegal Meq::Funklet rank");
  axes_.resize(rnk);
  offsets_.resize(rnk);
  scales_.resize(rnk);
  // init fields
  if( rnk )
  {
    // assign defaults
    axes_.assign(iaxis,iaxis+rnk);
    offsets_.assign(offset,offset+rnk);
    scales_.assign(scale,scale+rnk);
    (*this)[FAxisIndex] = axes_;
    (*this)[FOffset]    = offsets_;
    (*this)[FScale]     = scales_;
  }
  (*this)[FPerturbation] = pertValue_ = pert;
  (*this)[FWeight] = weight_ = weight;
  (*this)[FDbId] = id_ = id;
}


void Funklet::setDomain (const Domain * domain,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  domain_.attach(domain,flags);
  Record::addField(FDomain,domain_.ref_cast<BObj>(),DMI::REPLACE|Record::PROTECT);
}

// sets up an axis of variability
void Funklet::setAxis (int i,int iaxis,double offset,double scale)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(i<0 || i>rank(),"illegal Meq::Funklet axis");
  // up rank by one
  if( i == rank() )
  {
    axes_.push_back(iaxis);

    if(offsets_.size()==uint(i))
      offsets_.push_back(offset);
    if(scales_.size()==uint(i))
      scales_.push_back(scale);
    (*this)[FAxisIndex].replace() = axes_;
    (*this)[FOffset].replace()    = offsets_;
    (*this)[FScale].replace()     = scales_;
  }
  else
  {
    (*this)[FAxisIndex][i] = axes_[i] = iaxis;
    (*this)[FOffset][i] = offsets_[i] = offset;
    (*this)[FScale][i] = scales_[i] = scale;
  }
}

void Funklet::setPerturbation (double perturbation)
{ 
  Thread::Mutex::Lock lock(mutex());
  (*this)[FPerturbation] = pertValue_ = perturbation; 
}

void Funklet::setWeight (double weight)
{ 
  Thread::Mutex::Lock lock(mutex());
  (*this)[FWeight] = weight_ = weight; 
}

void Funklet::setDbId (Funklet::DbId id)
{ 
  Thread::Mutex::Lock lock(mutex());
  (*this)[FDbId] = id_ = id; 
}

//##ModelId=3F86886F03A6
int Funklet::makeSolvable (int spidIndex0)
{
  if((*this).hasField(FCoeffMask))
    {
      std::vector<bool> mask;
      if((*this)[FCoeffMask].get_vector(mask))
	return makeSolvable(spidIndex0,mask);
      
    }
  int nspids = getNumParms();
  parm_perts_.resize(nspids);
  calcPerturbations(parm_perts_,pertValue_);
  spid_perts_.resize(nspids);
  spid_perts_ = parm_perts_;
  spidInx_.resize(nspids);
  spids_.resize(nspids);
  for( int i=0; i<nspids; i++) 
  {
    spidInx_[i] = i;
    spids_[i]   = spidIndex0++;
  }
  return nspids;
}

int Funklet::makeSolvable (int spidIndex0,const std::vector<bool> &mask)
{
  uint np = getNumParms();
  Assert(mask.size() == np);
  parm_perts_.resize(np);
  calcPerturbations(parm_perts_,pertValue_);
  // count solvable parms
  int nspids = 0;
  for( uint i=0; i<np; i++ )
    if( mask[i] )
      nspids++;
  // assign
  spidInx_.resize(np);
  spids_.resize(nspids);
  spid_perts_.resize(nspids);
  int isp = 0;
  for( uint i=0; i<np; i++) 
    if( mask[i] )
    {
      spids_[isp] = spidIndex0++;
      spid_perts_[isp] = parm_perts_[i];
      spidInx_[i] = isp++;
    }
    else
    {
      spidInx_[i] = -1;
    }


  return nspids;
}

//##ModelId=3F86886F03A4
void Funklet::clearSolvable()
{
  spids_.clear();
  spidInx_.clear();
  spid_perts_.clear();
  parm_perts_.clear();
}

DMI::Vec * Funklet::getCoeffIndex(int spidid) const
{
    int coeffidx[2];
    coeffidx[0]=0;
    coeffidx[1]=0;

    int shape1(1),shape2(1);
    const LoShape shape = getCoeffShape ();
    if(shape.size()>1){
      shape2=shape[1];
    }
    shape1=shape[0];
    uint idx=0;
    uint np = getNumParms();
    for( uint i=spidid; i<np; i++){
      if(spidInx_[i]==spidid){
	idx = i;
	break;
      }
      
    }
    
    coeffidx[0] = idx/shape2;
    coeffidx[1] = idx%shape2;
    
    return  new DMI::Vec(Tpint,2,coeffidx);
}


  void Funklet::setRank(int rnk){
    //increases rank of funklet, to make sure vectors have at least the right size
    int rnk_old =rank();
    for(int i=rnk_old;i<rnk;i++)
      //add axis i
      setAxis(i,i);
  }

void Funklet::setCoeff (const DMI::NumArray &arr)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(arr.elementType()!=Tpdouble,"Meq::Funklet: coeff array must be of type double");

  //  FailWhen(rank()!=arr.rank(),"Meq::Funklet: coeff rank mismatch");
  //if there is a rank mismatch add axes ? 
  

  ObjRef ref(new DMI::NumArray(arr));
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref().ref_cast<DMI::NumArray>() );
}

void Funklet::setCoeff (double c00)
{
  Thread::Mutex::Lock lock(mutex());
  //  FailWhen(rank()!=0,"Meq::Funklet: coeff rank mismatch");
  //if there is a rank mismatch reinit ? 
  LoVec_double coeff(1);
  coeff = c00;
  ObjRef ref(new DMI::NumArray(coeff));
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref().ref_cast<DMI::NumArray>() );
}

void Funklet::setCoeff (const LoVec_double & coeff)
{
  Thread::Mutex::Lock lock(mutex());
  if(! rank())
    //  init(1,defaultFunkletAxes,defaultFunkletOffset,defaultFunkletScale);
    setAxis(1,1);
  //  else {
  //    FailWhen(rank()!=1,"Meq::Funklet: coeff rank mismatch");
  //  }
  ObjRef ref(new DMI::NumArray(coeff));
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref().ref_cast<DMI::NumArray>() );
}

void Funklet::setCoeff (const LoMat_double & coeff)
{
  Thread::Mutex::Lock lock(mutex());
  //  if( !rank() || rank() !=2 )
  //  init(2,defaultFunkletAxes,defaultFunkletOffset,defaultFunkletScale);


  if(rank()<2){
    int rnk=rank();
    for(int i=rnk;i<2;i++)
      setAxis(i,i);
    

  }
  


  //  else {
  //    FailWhen(rank()!=2,"Meq::Funklet: coeff rank mismatch");
  //  }
  ObjRef ref(new DMI::NumArray(coeff));
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref().ref_cast<DMI::NumArray>() );
}





void Funklet::evaluate (VellSet &vs,const Cells &cells,int makePerturbed) const
{
  Thread::Mutex::Lock lock(mutex());
  PERFPROFILE(__PRETTY_FUNCTION__);
  // sets spids and perturbations in output vellset


  if( spids_.empty() ) // no active solvable spids? Force no perturbations then
    makePerturbed = 0;
  else if( makePerturbed )
  {
    Assert(makePerturbed==1 || makePerturbed==2);
    vs.setNumPertSets(makePerturbed);
    vs.setSpids(spids_);

    cdebug(4)<<"nr spids in Funklet "<<spids_.size()<<endl;
    
    vs.setPerturbations(spid_perts_);
    // since we can't just do unary-minus on an std::vector, do ugly loop:
    if( makePerturbed==2 )
      for( uint i=0; i<spid_perts_.size(); i++ )
        vs.setPerturbation(i,-spid_perts_[i],1);
  }
  // call do_evaluate() to do the real work
  do_evaluate(vs,cells,parm_perts_,spidInx_,makePerturbed);
}

// shortcut to standard evaluate()
void Funklet::evaluate (VellSet &vs,const Request &request) const
{
  evaluate(vs,request.cells(),request.evalMode());
}


  void Funklet::evaluate (VellSet &vs,const Cells &cells,const std::vector<Result::Ref> & childres,int makePerturbed) const
{
  Thread::Mutex::Lock lock(mutex());
  PERFPROFILE(__PRETTY_FUNCTION__);
  // sets spids and perturbations in output vellset


  if( spids_.empty() ) // no active solvable spids? Force no perturbations then
    makePerturbed = 0;
  else if( makePerturbed )
  {
    Assert(makePerturbed==1 || makePerturbed==2);
    vs.setNumPertSets(makePerturbed);
    vs.setSpids(spids_);

    cdebug(4)<<"nr spids in Funklet "<<spids_.size()<<endl;
    
    vs.setPerturbations(spid_perts_);
    // since we can't just do unary-minus on an std::vector, do ugly loop:
    if( makePerturbed==2 )
      for( uint i=0; i<spid_perts_.size(); i++ )
        vs.setPerturbation(i,-spid_perts_[i],1);
  }
  // call do_evaluate() to do the real work
  do_evaluate(vs,cells,parm_perts_,spidInx_,childres,makePerturbed);
}

// shortcut to standard evaluate()
  void Funklet::evaluate (VellSet &vs,const Request &request,const std::vector<Result::Ref> & childres) const
{
  evaluate(vs,request.cells(),childres,request.evalMode());
}
void Funklet::update (const double values[],bool force_positive)
{
  do_update(values,spidInx_,force_positive);
}

void Funklet::update (const double values[],const std::vector<double>& constraints,bool force_positive)
{
  do_update(values,spidInx_,constraints,force_positive);
}


void Funklet::update (const double values[],const std::vector<double>& constraints_min,const std::vector<double>& constraints_max,bool force_positive)
{
  do_update(values,spidInx_,constraints_min,constraints_max,force_positive);
}

void Funklet::do_evaluate (VellSet &,const Cells &,
                           const std::vector<double> &,
                           const std::vector<int>    &,
                           int) const
{ 
  Throw("do_evaluate() not implemented by Funklet subclass"); 
}

void Funklet::do_evaluate (VellSet &,const Cells &,
                           const std::vector<double> &,
                           const std::vector<int>    &,
			   const std::vector<Result::Ref> &,
                           int) const
{ 
  Throw("do_evaluate() not implemented by Funklet subclass"); 
}

void Funklet::do_update (const double [],const std::vector<int> &,bool force_positive)
{ 
  Throw("do_update() not implemented by Funklet subclass"); 
}

void Funklet::do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &cnstrnts,bool force_positive)
{ 
  //ignore constraints if not implemented;
  do_update(values,spidIndex,force_positive);
}

void Funklet::do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &cnstrnts1,const std::vector<double> &cnstrnts2,bool force_positive)
{ 
  //ignore constraints if not implemented;
  do_update(values,spidIndex,force_positive);
}

} // namespace Meq

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

#include <Common/Profiling/PerfProfile.h>

#include "Funklet.h"
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/MeqVocabulary.h>
#include <Common/Debug.h>
#include <Common/lofar_vector.h>
#include <cstdlib>
#include <cmath>

namespace Meq {

static NestableContainer::Register reg(TpMeqFunklet,True);

const int defaultFunkletRank = 2;

const int    defaultFunkletAxes[defaultFunkletRank]   = {0,1};
const double defaultFunkletOffset[defaultFunkletRank] = {0,0};
const double defaultFunkletScale[defaultFunkletRank]  = {1,1};

static std::vector<int> default_axes(defaultFunkletAxes,defaultFunkletAxes+defaultFunkletRank);
static std::vector<double> default_offset(defaultFunkletOffset,defaultFunkletOffset+defaultFunkletRank);
static std::vector<double> default_scale(defaultFunkletScale,defaultFunkletScale+defaultFunkletRank);

Domain Funklet::default_domain;

//##ModelId=3F86886F0366
Funklet::Funklet(double pert,double weight,DbId id)
{
  init(0,0,0,0,pert,weight,id);
}

Funklet::Funklet(int naxis,const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
{
  init(naxis,iaxis,offset,scale,pert,weight,id);
}


//##ModelId=400E5354033A
Funklet::Funklet (const DataRecord &other,int flags,int depth)
  : DataRecord(other,flags,depth)
{
}

// sets all of a funklet's axes and attributes in one go
void Funklet::init (int rnk,const int iaxis[],
                    const double offset[],
                    const double scale[],
                    double pert,double weight,DbId id)
{
  Thread::Mutex::Lock lock(mutex());
  // this ensures a rank match: first time 'round, set the rank
  if( axes_.empty() )
  {
    FailWhen(rnk<0 || rnk>maxFunkletRank(),"illegal Meq::Funklet rank");
    axes_.resize(rnk);
    offsets_.resize(rnk);
    scales_.resize(rnk);
  }
  else // otherwise ensure rank did not change
  {
    FailWhen(rank() != rnk,"Meq::Funklet already initialized with a different rank");
  }
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
  if( !(flags&(DMI::ANON|DMI::EXTERNAL)) )
  {
    if( domain->refCount() )
      domain_.attach(domain,DMI::READONLY);
    else
      domain_.attach(new Domain(*domain),DMI::ANON|DMI::READONLY);
  }
  else
    domain_.attach(domain,(flags&~DMI::WRITE)|DMI::READONLY);
  (*this)[FDomain] <<= domain_.copy();
}

// sets up an axis of variability
void Funklet::setAxis (int i,int iaxis,double offset,double scale)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(i<0 || i>=rank(),"illegal Meq::Funklet axis");
  (*this)[FAxisIndex][i] = axes_[i] = iaxis;
  (*this)[FOffset][i] = offsets_[i] = offset;
  (*this)[FScale][i] = scales_[i] = scale;
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

void Funklet::revalidateContent ()    
{
  protectAllFields();
}
  
void Funklet::validateContent ()    
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields; setup shortcuts
  // to their contents
  try
  {
    protectAllFields();
    if( DataRecord::hasField(FDomain) ) // verify cells field
      domain_ <<= (*this)[FDomain].as_p<Domain>();
    else
      domain_ <<= new Domain;
    // get various others
    axes_       = (*this)[FAxisIndex].as_vector(default_axes);
    offsets_    = (*this)[FOffset].as_vector(default_offset);
    scales_     = (*this)[FScale].as_vector(default_scale);
    Assert(axes_.size() == uint(rank()) && offsets_.size() == uint(rank()) && scales_.size() == uint(rank()) );
    pertValue_  = (*this)[FPerturbation].as<double>(defaultFunkletPerturbation);
    weight_     = (*this)[FWeight].as<double>(defaultFunkletWeight);
    id_         = (*this)[FDbId].as<int>(-1);
  }
  catch( std::exception &err )
  {
    Throw(string("validate of Funklet record failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Funklet record failed with unknown exception");
  }
}

//##ModelId=3F86886F03A6
int Funklet::makeSolvable (int spidIndex0)
{
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
    vs.setPerturbations(spid_perts_);
    // since we can't just do unary-minus on an std::vector, do ugly loop:
    if( makePerturbed==2 )
      for( uint i=0; i<spid_perts_.size(); i++ )
        vs.setPerturbation(i,-spid_perts_[i],1);
  }
  // call do_evaluate() to do the real work
  do_evaluate(vs,cells,parm_perts_,spidInx_,makePerturbed);
}

void Funklet::update (const double values[])
{
  do_update(values,spidInx_);
}

// shortcut to standard evaluate()
void Funklet::evaluate (VellSet &vs,const Request &request) const
{
  evaluate(vs,request.cells(),request.calcDeriv());
}

void Funklet::do_evaluate (VellSet &,const Cells &,
                           const std::vector<double> &,
                           const std::vector<int>    &,
                           int) const
{ 
  Throw("do_evaluate() not implemented by Funklet subclass"); 
}

void Funklet::do_update (const double [],const std::vector<int> &)
{ 
  Throw("do_update() not implemented by Funklet subclass"); 
}

} // namespace Meq

//# Parm.cc: Stored parameter with polynomial coefficients
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

#include <MeqNodes/Parm.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/MeqVocabulary.h>
#include <Common/Debug.h>
#include <Common/Lorrays.h>
#include <casa/BasicMath/Math.h>

namespace Meq {

InitDebugContext(Parm,"MeqParm");

const HIID symdeps_all[]    = { FDomain,FResolution,FParmValue };
const HIID symdeps_domain[] = { FDomain,FResolution };
const HIID symdeps_solve[]  = { FParmValue };

const HIID
    // Parm staterec fields
    FTableName       = AidTable|AidName,
    FParmName        = AidParm|AidName,
    FAutoSave        = AidAuto|AidSave,
    FDomainId        = AidDomain|AidId,
    // FDomain      defined previously
    FFunklet         = AidFunklet,
    FDefaultFunklet  = AidDefault|AidFunklet;

//##ModelId=3F86886F021B
Parm::Parm()
: Node  (0), // no children allowed
  solvable_ (false),
  auto_save_(false),
  parmtable_(0),
  domain_depend_mask_(0),
  solve_depend_mask_(0),
  domain_symdeps_(symdeps_domain,symdeps_domain+2),
  solve_symdeps_(symdeps_solve,symdeps_solve+1),
  integrated_(false)
{
// note that we leave the default dependency mask at 0: instead, we
// maintain two of our own masks. domain_depend_mask is returned
// if the funklet has >1 coefficient; solve_depend_mask is added if
// the parm is solvable
  setKnownSymDeps(symdeps_all,3);
}

//##ModelId=3F86886F0242
Parm::Parm (const string& name, ParmTable* table,
	          const Funklet::Ref::Xfer & defaultValue)
: Node  (0), // no children allowed
  solvable_  (false),
  auto_save_ (false),
  name_      (name),
  parmtable_ (table),
  default_funklet_(defaultValue),
  domain_depend_mask_(0),
  solve_depend_mask_(0),
  domain_symdeps_(symdeps_domain,symdeps_domain+2),
  solve_symdeps_(symdeps_solve,symdeps_solve+1),
  integrated_(false)
{
  setKnownSymDeps(symdeps_all,3);
}

//##ModelId=3F86886F021E
Parm::~Parm()
{}

Funklet * Parm::findRelevantFunklet (Funklet::Ref &funkletref,const Domain &domain)
{
  cdebug(2)<<"looking for suitable funklets"<<endl;
  funkletref.detach();
  if( parmtable_ )
  {
    vector<Funklet::Ref> funklets;
    int n = parmtable_->getFunklets(funklets,name_,domain);
    cdebug(3)<<n<<" funklets found in MEP table"<<endl;
    if( n>1 )
    {
      cdebug(3)<<"discarding mutliple funklets as only one is currently suported"<<endl;
    }
    if( n )
    {
      funkletref <<= funklets.front();
      return funkletref.dewr_p();
    }
  }
  else
  {
    cdebug(3)<<"no MEP table assigned"<<endl;
  }
  // If we get here, there's no table or no funklet has been found -- try to get default
  if( !funkletref.valid() )
  {
    if( parmtable_ )
    {
      int n = parmtable_->getInitCoeff(funkletref,name_);
      cdebug(3)<<"looking for funklets in defaults subtable: "<<n<<endl;
    }
    if( !funkletref.valid() )
    {
      const Funklet *deffunklet = state()[FDefaultFunklet].as_po<Funklet>();
      FailWhen(!deffunklet,"no funklets found and no default_funklet specified");
      cdebug(3)<<"no funklets found, using default value from state record"<<endl;
      funkletref <<= deffunklet;
      funkletref.privatize(DMI::WRITE|DMI::DEEP);
    }
    funkletref().clearSolvable();
    funkletref().setDomain(domain);
    return funkletref.dewr_p();
  }
  return 0;
}

//##ModelId=400E5353019E
int Parm::initSolvable (Funklet &funklet,const Request &request)
{
  // copy current domain into solvable funklet
  // (once we start solving, it is only valid for the solve domain, even if it may
  // have been valid for a bigger/different domain before)
  funklet.setDomain(request.cells().domain());
  int nr = 0;
  funklet.clearSolvable();
  if( isSolvable() )
  {
    int spidIndex = 256*nodeIndex();
    nr += funklet.makeSolvable(spidIndex);
    if( funklet.getPerturbation() == 0 )
    {
      cdebug(3)<<"warning: null funklet perturbation, using default 1e-6"<<endl;
      funklet.setPerturbation(1e-6);
    }
  } 
  return nr;
}

Funklet * Parm::initFunklet (const Request &request,bool solve)
{
  const Domain &domain = request.cells().domain();
  HIID rq_dom_id = maskSubId(request.id(),domain_depend_mask_); 
  // do we have a current funklet set up?
  Funklet * pfunklet = wstate()[FFunklet].as_wpo<Funklet>();
  // see if this can be reused
  if( pfunklet )
  {
    // (a) domain ID of request matches that of funklet: can reuse
    //     (a null domain ID in the request precludes this)
    if( !rq_dom_id.empty() && rq_dom_id == domain_id_ )
    {
      cdebug(3)<<"current funklet domain ID matches, re-using"<<endl;
      return pfunklet;
    }
    // (b) no domain in funklet (i.e. effectively infinite domain of applicability)
    if( !pfunklet->hasDomain() )
    { 
      cdebug(3)<<"current funklet has infinite domain, re-using"<<endl;
      wstate()[FDomainId] = domain_id_ = rq_dom_id;
      wstate()[FDomain].replace() <<= &domain;
      return pfunklet;
    }
    // (c) funklet domain is a superset of the requested domain
    if( pfunklet->domain().supersetOfProj(domain) )
    {
      cdebug(3)<<"current funklet defined for superset of requested domain, re-using"<<endl;
      wstate()[FDomainId] = domain_id_ = rq_dom_id;
      wstate()[FDomain].replace() <<= &domain;
      return pfunklet;
    }
  }
  // no funklet, or funklet not suitable -- get a new one
  Funklet::Ref funkref;
  pfunklet = findRelevantFunklet(funkref,domain);
  FailWhen(!pfunklet,"no funklets found for specified domain");
  // update state record
  wstate()[FFunklet].replace() <<= pfunklet;
  wstate()[FDomainId] = domain_id_ = rq_dom_id;
  wstate()[FDomain].replace() <<= &domain;
  return pfunklet;
}

//##ModelId=3F86886F022E
int Parm::getResult (Result::Ref &resref,
                     const std::vector<Result::Ref> &,
                     const Request &request,bool newreq)
{
  cdebug(2)<<"evaluating parm for domain "<<request.cells().domain()<<endl;
  // is request for solvable parm values?
  bool solve = isSolvable() && request.calcDeriv();
  // find a funklet to use
  Funklet * pfunklet = initFunklet(request,solve);
  // if funklet not set to solvable, do some extra init
  if( solve && !pfunklet->isSolvable() )
  {
    cdebug(2)<<"new solve domain, initializing"<<endl;
    initSolvable(*pfunklet,request);
  }
  else if( !solve && pfunklet->isSolvable() )
  {
    pfunklet->clearSolvable();
  }
  // init depend mask
  int depend = solve ? solve_depend_mask_ : 0;
  
  // Create result object and attach to the ref that was passed in
  Result &result = resref <<= new Result(1,request); // result has one vellset
  VellSet & vs = result.setNewVellSet(0,0,request.calcDeriv());
  
  // If we have a single constant funklet, and are not integrated, then there's no 
  // dependency on domain. Otherwise, add domain mask
  if( !pfunklet->isConstant() || integrated_ )
    depend |= domain_depend_mask_;
  
  cdebug(3)<<"evaluating funklet"<<endl;
  pfunklet->evaluate(vs,request);
  
  // integrate over cell if so specified
  if( integrated_ )
    result.integrate();
  
  return depend;
}

//##ModelId=3F86886F023C
void Parm::save()
{
  if( !parmtable_ )
    return;
  Funklet * pfunklet = wstate()[FFunklet].as_wpo<Funklet>();
  if( !pfunklet ) 
    return;
  cdebug(2)<<"saving funklet"<<endl;
  parmtable_->putCoeff1(name_,*pfunklet);
}

void Parm::resetDependMasks ()
{
  domain_depend_mask_ = computeDependMask(domain_symdeps_);
  solve_depend_mask_ = computeDependMask(solve_symdeps_);
  if( hasState() )
  {
    wstate()[FDomainDependMask] = domain_depend_mask_;
    wstate()[FSolveDependMask] = solve_depend_mask_;
  }
}

//##ModelId=400E5353033A
void Parm::setStateImpl (DataRecord& rec, bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get parm name, or use node name by default
  if( initializing && name_.empty() )
    name_ = name();
  rec[FParmName].get(name_,initializing);
  rec[FAutoSave].get(auto_save_,initializing);
  rec[FSolvable].get(solvable_,initializing);
  rec[FIntegrated].get(integrated_,initializing);
  // recompute depmasks if active sysdeps change
  if( rec[FDomainSymDeps].get_vector(domain_symdeps_,initializing) )
  {
    cdebug(2)<<"domain_symdeps set via state\n";
    resetDependMasks();
  }
  if( rec[FSolveSymDeps].get_vector(solve_symdeps_,initializing) )
  {
    cdebug(2)<<"solve_symdeps set via state\n";
    resetDependMasks();
  }
  // now set the dependency mask if specified; this will override
  // possible modifications made above
  rec[FDomainDependMask].get(domain_depend_mask_,initializing);
  rec[FSolveDependMask].get(solve_depend_mask_,initializing);
 
  // Is a funklet specified? 
  const Funklet * pfunklet = rec[FFunklet].as_po<Funklet>();
  if( pfunklet )
  {
    cdebug(2)<<"new funklet set via state\n";
    // if a new funklet is set on the fly (i.e. not in node initialization),
    // then reset cached domain & domain ID. This will force an reinit
    // on the next getResult() call, thus either re-using or discarding the
    // funklet as appropriate.
    if( !initializing )
    {
      wstate()[FDomain].remove(); 
      wstate()[FDomainId] = domain_id_ = HIID();
    }
  }
  // get domain IDs, if specified
  rec[FDomainId].get(domain_id_);
  // Get default funklet (to be used if no table exists)
  // We don't really do anything with the pointer (save for some debug output),
  // but this effectively verifies that the Default field is in fact a Funklet
  // object if it is present.
  const Funklet *deffunklet = rec[FDefaultFunklet].as_po<Funklet>();
  if( deffunklet )
  {
    cdebug(2)<<"default funklet set via state\n";
  }
  // Get ParmTable name 
  string tableName;
  if( rec[FTableName].get(tableName) )
  {
    if( tableName.empty() )  // no table
      parmtable_ = 0;
    else    // else open a table
      parmtable_ = ParmTable::openTable(tableName);
  }
}

int Parm::processCommands (const DataRecord &rec,Request::Ref &reqref)
{
  // process parent class's commands
  int retcode = Node::processCommands(rec,reqref);
  bool saved  = False;
  
  // Is an Update.Values command specified? use it to update solve funklets
  DataRecord::Hook hset(rec,FUpdateValues);
  if( hset.exists() )
  {
    if( isSolvable() )
    {
      HIID req_domain_id = maskSubId(reqref->id(),domain_depend_mask_);
      if( req_domain_id == domain_id_ )
      {
        cdebug(4)<<"got "<<FUpdateValues<<" command"<<endl;
        // Update the funklet coefficients with the new values.
        LoVec_double values = hset.as<LoVec_double>();
        Funklet &funklet = wstate()[FFunklet].as_wr<Funklet>();
        FailWhen(values.size() != int(funklet.getSpids().size()),
                 "size of "+FUpdateValues.toString()+" does not match size of funklets");
        funklet.update(values.data());
        if( auto_save_ )
        {
          save();
          saved = True;
        }
        // result depends on everything
        retcode |= domain_depend_mask_|solve_depend_mask_;
      }
      else
      {
        cdebug(2)<<"got "<<FUpdateValues<<", but request domain ID "<<req_domain_id<<
                  " does not match current funklet domain ID "<<domain_id_<<endl;
        cdebug(2)<<"ignoring "<<FUpdateValues<<" command"<<endl;
      }
    }
    else
    {
      cdebug(2)<<"got "<<FUpdateValues<<", but parm is not solvable"<<endl;
      cdebug(2)<<"ignoring "<<FUpdateValues<<" command"<<endl;
    }
  }
  // if not already saved, then check for a Save.Funklets command
  if( !saved && rec[FSaveFunklets].as<bool>(false) )
    save();
  // lastly, check for a Clear.Funklets command
  if( rec[FClearFunklets].as<bool>(false) )
  {
    // clear out relevant fields
    wstate()[FFunklet].remove();
    wstate()[FDomain].remove();
    wstate()[FDomainId].remove();
    domain_id_ = HIID();
//    retcode |= RES_NO_CACHE;
  }
  return retcode;
}

//##ModelId=400E53520391
string Parm::sdebug (int detail, const string &prefix,const char* nm) const
{
  string out = Node::sdebug(detail,prefix,nm);
  if( detail>=2 || detail == -2) {
    Debug::appendf(out,"  parmtable=%s", parmtable_->name().c_str());
  }
  return out;
}

} // namespace Meq

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
// if the polc has >1 coefficient; solve_depend_mask is added if
// the parm is solvable
  setKnownSymDeps(symdeps_all,3);
}

//##ModelId=3F86886F0242
Parm::Parm (const string& name, ParmTable* table,
	          const Polc::Ref::Xfer & defaultValue)
: Node  (0), // no children allowed
  solvable_  (false),
  auto_save_ (false),
  name_      (name),
  parmtable_ (table),
  default_polc_(defaultValue),
  domain_depend_mask_(0),
  solve_depend_mask_(0),
  domain_symdeps_(symdeps_domain,symdeps_domain+2),
  solve_symdeps_(symdeps_solve,symdeps_solve+1),
  integrated_(false)
{
}

//##ModelId=3F86886F021E
Parm::~Parm()
{}

//##ModelId=400E5352023D
void Parm::init (DataRecord::Ref::Xfer& initrec, Forest* frst)
{
  // do parent init (this will call our setStateImpl())
  Node::init (initrec, frst);
  // use default parm name ( = node name) if not set 
  if( name_.empty() )
    wstate()[FParmName] = name_ = name(); 
}


void Parm::findRelevantPolcs (vector<Polc::Ref> &polcs,const Domain &domain)
{
  cdebug(2)<<"looking for suitable polcs"<<endl;
  if( parmtable_ )
  {
    int n = parmtable_->getPolcs(polcs,name_,domain);
    cdebug(3)<<n<<" polcs found in MEP table"<<endl;
  }
  else
  {
    cdebug(3)<<"no MEP table assigned"<<endl;
  }
  // If none found, try to get a default value.
  if( polcs.size() == 0 )
  {
    Polc::Ref defpolc;
    if( parmtable_ )
    {
      int n = parmtable_->getInitCoeff(defpolc,name_);
      cdebug(3)<<"looking for polcs in defaults subtable: "<<n<<endl;
    }
    if( !defpolc.valid() )
    {
      FailWhen(!default_polc_.valid(),"no polcs found and no default specified");
      cdebug(3)<<"no polcs found, using default value from state record"<<endl;
      defpolc.copy(default_polc_).privatize(DMI::WRITE|DMI::DEEP);
    }
    FailWhen(defpolc->getCoeff().isNull(),"no polcs found");
    defpolc().setDomain(domain);
    polcs.push_back(defpolc);
  }
}

//##ModelId=400E5353019E
int Parm::initSpids ()
{
  int nr = 0;
  for( uint i=0; i<solve_polcs_.size(); i++) 
    solve_polcs_[i]().clearSolvable();
  if( isSolvable() )
  {
    Polc & polc = solve_polcs_.front();
    int spidIndex = 256*nodeIndex();
    nr += polc.makeSolvable(spidIndex);
    if( polc.getPerturbation() == 0 )
    {
      cdebug(3)<<"warning: null polc perturbation, using default 1e-6"<<endl;
      polc.setPerturbation(1e-6);
    }
  } 
  return nr;
}

// define binary predicate for comparing polcs
// compare by weight first, and dbid afterwards (higher dbids have priority)
class ComparePolcs {
  public: 
    int operator () (const Polc &a,const Polc &b) const {
      return a.getWeight() < b.getWeight() ||
           ( a.getWeight() == b.getWeight() && a.getDbId() < b.getDbId() );
    }
};
    
int Parm::initSolvable (const Domain &domain)
{
  // check to see if the current solve_polc_ can be re-used
  if( solve_polcs_.size() == 1 )
  {
    Polc & polc = solve_polcs_.front();
    if( polc[FGrowDomain].as<bool>(false) )
    {
      cdebug(2)<<"growing domain for current solve-polc"<<endl;
      polc.setDomain(domain.envelope(polc.domain())); // extend the domain
      return initSpids();
    }
    else if( polc.domain().supersetOf(domain) )
    {
      cdebug(2)<<"solve-polc defined over superset of requested domain, re-using"<<endl;
      return initSpids();
    }
  }
  // since we got here, no re-use is possible. Try to find new polcs:
  // First, init the predict domain. All relevant polcs will be loaded 
  // into the polcs_ member.
  solve_polcs_.clear();
  initDomain(domain);
  FailWhen(polcs_.size()<1,"no polcs found for domain");
  // if solvable but polcs_ has more than one element, reduce it to
  // the single "most relevant" polc
  solve_polcs_.resize(1);
  if( polcs_.size()==1 ) // copy single polc
  {
    solve_polcs_.front() = polcs_.front().copy();
  }
  else // multiple polcs found, select most suitable 
  {
    cdebug(3)<<"multiple polcs found for solvable parm, looking for best match"<<endl;
    // look for polc with max weight, and also an exact-domain polc with max weight
    int iexact=-1,imax=-1;
    for( uint i=0; i<polcs_.size(); i++ )
    {
      const Polc &np = *polcs_[i];
      if( imax<0 || ComparePolcs()(*polcs_[imax],np) )
        imax = i;
      if( np.domain() == domain && ( iexact<0 || ComparePolcs()(*polcs_[iexact],np) ) )
        iexact = i;
    }
    if( iexact>=0 )
    {
      cdebug(3)<<"using polc "<<iexact<<": exact domain match"<<endl;
      solve_polcs_.front() = polcs_[iexact].copy();
    }
    else
    {
      cdebug(3)<<"using polc "<<imax<<": no domain match"<<endl;
      solve_polcs_.front() = polcs_[imax].copy();
    }
  }
  // make sure the current domain overrides the solvable polc's domain 
  // (they may be different in case of growing domains, etc.)
  cdebug(3)<<"original domain: "<<solve_polcs_.front()->domain()<<endl;
  solve_polcs_.front()().setDomain(domain);
  
  // copy polc refs to state record
  DataField & polcrec = wstate()[FSolvePolcs].replace() <<= new DataField(TpMeqPolc,solve_polcs_.size());
  for (uint i=0; i<solve_polcs_.size(); i++) 
    polcrec[i] <<= solve_polcs_[i].copy();
  
  // assign spids
  return initSpids();
}

//##ModelId=3F86886F0226
int Parm::initDomain (const Domain& domain)
{
  cdebug(2)<<"initializing for domain "<<domain<<endl;
  // do we have a source for new polcs (i.e. table or default polc?)
  if( parmtable_ || default_polc_.valid() )
  {
    // Check if polcs_ already contain a suitable polc. Only do this
    // for cases of single polc (multiple polcs should always be reloaded)
    if( polcs_.size() == 1 )
    {
      Polc & polc = polcs_.front();
      // check for cases where the current polc may be reused
      // (a) marked as infinite-domain
      if( polc[FInfDomain].as<bool>(false) )
      { 
        cdebug(2)<<"current polc has infinite domain, re-using"<<endl;
        return 1;
      }
      // (b) is a superset of the requested domain
      else if( polc.domain().supersetOf(domain) )
      {
        cdebug(2)<<"current polc defined for superset of requested domain, re-using"<<endl;
        return 1;
      }
    }
    // no suitable polcs -- go looking
    vector<Polc::Ref> newpolcs;
    findRelevantPolcs(newpolcs,domain);
    polcs_ = newpolcs;
  }
  else
  {
    FailWhen(!polcs_.size(),"no polcs found for domain");
    cdebug(2)<<"no MEP table and no default specified, will use current polcs"<<endl;
    // some additional checking may be required here
  }
  // copy polc refs to state record
  DataField & polcrec = wstate()[FPolcs].replace() <<= new DataField(TpMeqPolc,polcs_.size());
  for (uint i=0; i<polcs_.size(); i++) 
    polcrec[i] <<= polcs_[i].copy();
  return polcs_.size();
}

//##ModelId=3F86886F022E
int Parm::getResult (Result::Ref &resref,
                     const std::vector<Result::Ref> &,
                     const Request &request,bool newreq)
{
  const Domain &domain = request.cells().domain();
  HIID domain_id = maskSubId(request.id(),domain_depend_mask_); 
  cdebug(2)<<"evaluating parm for domain "<<domain<<endl;
  int depend = 0;
  
  // Figure out which set of polcs to use for this request.
  // ppolcs will point to either polcs_ or solve_polcs_, depending on
  // which domain is matched
  vector<Polc::Ref> *ppolcs = 0;
  bool match_solve_domain = !domain_id.empty() && domain_id == solve_domain_id_;
  // Solvable and request wants derivatives? Must use solve_polcs_ 
  if( isSolvable() && request.calcDeriv() )
  {
    // if new solve domain, then find a new set of solve_polcs_
    // Note that this reinitializes both the solve and the predict domains.
    if( !match_solve_domain )
    {
      cdebug(2)<<"new solve domain, initializing"<<domain<<endl;
      initSolvable(domain);
      wstate()[FSolveDomain].replace() <<= new Domain(domain);
      wstate()[FSolveDomainId] = solve_domain_id_ = domain_id;
    }
    ppolcs = &solve_polcs_;
    depend |= solve_depend_mask_;
  }
  // Predict only, matches the solve domain? Just use solve_polcs_
  else if( match_solve_domain )
  {
    ppolcs = &solve_polcs_;
    depend |= solve_depend_mask_;
  }
  // predict only, matches the predict domain? Use polcs_
  else if( !domain_id.empty() && domain_id == domain_id_ )
    ppolcs = &polcs_;
  // predict of a new domain -- recompute polcs_
  else 
  {
    // Note that this reinitializes the predict domain only
    cdebug(2)<<"new predict domain, initializing"<<domain<<endl;
    initDomain(domain);
    wstate()[FDomain].replace() <<= new Domain(domain);
    wstate()[FDomainId] = domain_id_ = domain_id;
    ppolcs = &polcs_;
  }
  
  // Create result object and attach to the ref that was passed in
  Result &result = resref <<= new Result(1,request); // result has one vellset
  VellSet & vs = result.setNewVellSet(0,0,request.calcDeriv());
  vs.setShape(request.cells().shape());
  
  // add dependency on domain, unless we're not integrated and have a 
  // single c00 polc
  if( ppolcs->size()>1 || integrated_ || ppolcs->front()->ncoeff() )
    depend |= domain_depend_mask_;
  
  // A single polc can be evaluated immediately.
  if( ppolcs->size() == 1 )
  {
    cdebug(3)<<"evaluating and returning single polc"<<endl;
    ppolcs->front()->evaluate(vs,request);
    if( integrated_ )
      result.integrate();
    return depend;
  }
  
  // Get the domain, etc.
  const Cells &cells = request.cells();
  double* datar = 0;
  const LoVec_double & midFreq = cells.center(FREQ),
                       midTime = cells.center(TIME);
  int ndFreq = midFreq.extent(0);
  int ndTime = midTime.extent(0);
                       
  double firstMidFreq = midFreq(0);
  double lastMidFreq  = midFreq(ndFreq-1);
  double firstMidTime = midTime(0);
  double lastMidTime  = midTime(ndTime-1);
  vs.setReal(ndFreq,ndTime);
  // Iterate over all polynomials.
  // Evaluate one if its domain overlaps the request domain.
  cdebug(3)<<"midfreqs: "<<firstMidFreq<<":"<<lastMidFreq<<endl;
  cdebug(3)<<"midtimes: "<<firstMidTime<<":"<<lastMidTime<<endl;
  cdebug(3)<<"evaluating for "<<ppolcs->size()<<" polcs"<<endl;
  for( uint i=0; i<ppolcs->size(); i++ )
  {
    const Polc& polc = *((*ppolcs)[i]);
    cdebug(3)<<"polc "<<i<<" domain is "<<polc.domain()<<endl;
    double pfreq0 = polc.domain().start(FREQ), 
           pfreq1 = polc.domain().end(FREQ),
           ptime0 = polc.domain().start(TIME), 
           ptime1 = polc.domain().end(TIME);
    if( firstMidFreq < pfreq1 && lastMidFreq > pfreq0 &&
        firstMidTime < ptime1 && lastMidTime > ptime0 )
    {
      // Determine which subset of the request Cells is covered by the poly
      int ifreq0 = 0, ifreq1 = ndFreq-1;
      while( midFreq(ifreq0) < pfreq0 ) 
        ifreq0++;
      while( midFreq(ifreq1) > pfreq1 )
        ifreq1--;
      int itime0 = 0, itime1 = ndTime-1;
      while( midTime(itime0) < ptime0 ) 
        itime0++;
      while( midTime(itime1) > ptime1 )
        itime1--;
      int nrFreq = ifreq1 - ifreq0 + 1;
      int nrTime = itime1 - itime0 + 1;
      cdebug(3)<<"polc "<<i<<" overlap: "<<ifreq0<<":"<<ifreq1
                <<","<<itime0<<":"<<itime1<<endl;
      // If the overlap is full, only this polynomial needs to be evaluated.
      if( ifreq0 == 0 && ifreq1 == ndFreq-1 &&
          itime0 == 0 && itime1 == ndTime-1 )
      {
        polc.evaluate(vs,request);
        if( integrated_ )
          result.integrate();
        return depend;
      }
      // Evaluate polc over overlapping part of grid
      VellSet partRes;
      partRes.setShape(nrFreq,nrTime);
      polc.evaluate(partRes,
                    midFreq(blitz::Range(ifreq0,ifreq1)),
                    midTime(blitz::Range(itime0,itime1)),
                    request.calcDeriv());
      // Create the result matrix if it is the first Time.
      // Now it is initialized with zeroes (to see possible errors).
      // In the future the outcommnented statement can be used
      // which saves the initialization Time. It requires that the
      // request domain is entirely covered by the polcs.
      if (datar == 0) {
        LoMat_double& mat = vs.setReal (ndFreq, ndTime);
        datar = mat.data();
      }
      // Move the values to the correct place in the output result.
      // Note that in principle a polynomial could be a single coefficient
      // in which case it returns a single value.
      const double* from = partRes.getValue().realStorage();
      double* to = datar + ifreq0 + itime0*ndFreq;
      if (partRes.getValue().nelements() == 1) {
        for (int iTime=0; iTime<nrTime; iTime++) {
          for (int iFreq=0; iFreq<nrFreq; iFreq++) {
            to[iFreq] = *from;
          }
          to += ndFreq;
        }
      } else {
        for (int iTime=0; iTime<nrTime; iTime++) {
          for (int iFreq=0; iFreq<nrFreq; iFreq++) {
            to[iFreq] = *from++;
          }
          to += ndFreq;
        }
      }
    }
  }
  if( integrated_ )
    result.integrate();
  return depend;
}

//##ModelId=3F86886F023C
void Parm::save()
{
  if( parmtable_ ) 
  {
    cdebug(2)<<"saving "<<solve_polcs_.size()<<" polcs"<<endl;
    for( uint i=0; i<solve_polcs_.size(); i++) 
      parmtable_->putCoeff1(name_,solve_polcs_[i]());
  }
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
// 31/03/04: we do allow changing the Polcs now, see below
//  // inhibit changing of FPolcs field
//  if( !initializing )
//  {
//    protectStateField(rec,FPolcs);
//    protectStateField(rec,FSolvePolcs);
//  }
  Node::setStateImpl(rec,initializing);
  
  rec[FAutoSave].get(auto_save_,initializing);
  rec[FParmName].get(name_,initializing);
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
 
  // Are polcs specified? 
  int npolcs = rec[FPolcs].size(TpMeqPolc);
  FailWhen(npolcs<0,"illegal "+FPolcs.toString()+" state field");
  if( npolcs )
  {
    polcs_.resize(npolcs);
    if( npolcs == 1 )
      polcs_[0] <<= rec[FPolcs].as_wp<Polc>();
    else
      for( int i=0; i<npolcs; i++ )
        polcs_[i] <<= rec[FPolcs][i].as_wp<Polc>();
    // if new polcs are set on the fly (i.e. not in node initialization),
    // then reset cached domain & domain ID. This will force an initDomain()
    // on the next getResult() call, thus either re-using or discarding the
    // polcs.
    if( !initializing )
    {
      wstate()[FDomain].remove(); 
      wstate()[FDomainId] = domain_id_ = HIID();
    }
  }
  // Are solve polcs specified? 
  int nspolcs = rec[FSolvePolcs].size(TpMeqPolc);
  FailWhen(nspolcs<0,"illegal "+FSolvePolcs.toString()+" state field");
  if( nspolcs )
  {
    FailWhen(nspolcs>1,"MeqParm currently supports only one solvable polc");
    solve_polcs_.resize(1);
    solve_polcs_.front() <<= rec[FSolvePolcs].as_wp<Polc>();
    // if new polcs are set on the fly (i.e. not in node initialization), then
    // reset cached solve domain & domain ID. This will force an initSolvable()
    // on the next getResult() call, thus either re-using or discarding the
    // solve_polcs
    if( !initializing )
    {
      wstate()[FSolveDomain].remove(); 
      wstate()[FSolveDomainId] = solve_domain_id_ = HIID();
    }
  }
  // get domain IDs, if specified
  rec[FDomainId].get(domain_id_);
  rec[FSolveDomainId].get(solve_domain_id_);
  // Get default polc (to be used if no table exists)
  const Polc *defpolc = rec[FDefault].as_po<Polc>();
  if( defpolc )
    default_polc_ <<= defpolc;
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
  
  // Is an Update.Values command specified? use it to update solve polcs
  DataRecord::Hook hset(rec,FUpdateValues);
  if( hset.exists() )
  {
    HIID req_domain_id = maskSubId(reqref->id(),domain_depend_mask_);
    if( req_domain_id == solve_domain_id_ )
    {
      cdebug(4)<<"got "<<FUpdateValues<<" command"<<endl;
      // Update the polc coefficients with the new values.
      LoVec_double values = hset.as<LoVec_double>();
      uint inx = 0;
      for (uint i=0; i<solve_polcs_.size(); i++) 
        inx += solve_polcs_[i]().update(&values(inx), values.size()-inx);
      FailWhen(inx != uint(values.size()),
                "size of "+FUpdateValues.toString()+" does not match size of polcs");
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
                " does not match current solve domain ID "<<solve_domain_id_<<endl;
      cdebug(2)<<"ignoring "<<FUpdateValues<<" command"<<endl;
    }
  }
  // if not already saved, then check for a Save.Polcs command
  if( !saved && rec[FSavePolcs].as<bool>(false) )
    save();
  // lastly, check for a Clear.Polcs command
  if( rec[FClearPolcs].as<bool>(false) )
  {
    polcs_.clear();
    solve_polcs_.clear();
    // clear out relevant fields
    static const HIID * flds[] = {  &FPolcs,    &FSolvePolcs,
                                    &FDomain,   &FSolveDomain,
                                    &FDomainId, &FSolveDomainId  };
    for( uint i=0; i<sizeof(flds)/sizeof(flds[0]); i++ )
      wstate()[*(flds[i])].remove();
    domain_id_ = solve_domain_id_ = HIID();
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

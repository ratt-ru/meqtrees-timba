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
#include <MEQ/ComposedPolc.h>
#include <MEQ/Polc.h>
#include <MEQ/PolcLog.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/MeqVocabulary.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <Common/Debug.h>
#include <Common/Lorrays.h>
#include <casa/BasicMath/Math.h>
#include <casa/Arrays/Matrix.h>
#include <casa/Arrays/Vector.h>
#include <DMI/List.h>
#include <DMI/Record.h>
#include <MEQ/Forest.h>

using namespace casa;

namespace Meq {

  InitDebugContext(Parm,"MeqParm");

  const HIID symdeps_all[]     = { FDomain,FResolution,FIteration };
  const HIID symdeps_domain[]  = { FDomain,FResolution };
  const HIID symdeps_solve[]   = { FIteration };
  const HIID symdeps_default[] = { };

  const HIID
  // Parm staterec fields
  FTableName       = AidTable|AidName,
    FParmName        = AidParm|AidName,
    FAutoSave        = AidAuto|AidSave,
    FDomainId        = AidDomain|AidId,
  // FDomain      defined previously
    FFunklet         = AidFunklet,
    FDefaultFunklet  = AidDefault|AidFunklet,
    FSolveDomain = AidSolve|AidDomain,
    FUsePrevious = AidUse|AidPrevious,
    FTileSize = AidTile|AidSize,
    FTiling = AidTiling,
    FConverged  = AidConverged;

    


  Parm::Parm()
    : Node  (0), // no children allowed
      solvable_ (false),
      auto_save_(false),
      tiled_ (false),
      _use_previous(true),
      converged_(false),
      parmtable_(0),
      domain_depend_mask_(0),
      solve_depend_mask_(0),
      domain_symdeps_(symdeps_domain,symdeps_domain+2),
      solve_symdeps_(symdeps_solve,symdeps_solve+1),
      solve_domain_(2),
      integrated_(false)
  {
    // The default depmask only includes Solution. Solution is meant to be updated
    // whenever the parm solvable state is changed, or when fiddling.
    // Domain mask will be added if the funklet has >1 coefficient; solve_depend_mask 
    // is added if the parm is solvable
    setKnownSymDeps(symdeps_all,3);
    setActiveSymDeps(symdeps_default,0);
  }

  Parm::Parm (const string& name, ParmTable* table,
	      const Funklet::Ref::Xfer & defaultValue)
    : Node  (0), // no children allowed
      solvable_  (false),
      auto_save_ (false),
      tiled_ (false),
      _use_previous(true),
      converged_(false),
      name_      (name),
      parmtable_ (table),
      default_funklet_(defaultValue),
      domain_depend_mask_(0),
      solve_depend_mask_(0),
      domain_symdeps_(symdeps_domain,symdeps_domain+2),
      solve_symdeps_(symdeps_solve,symdeps_solve+1),
      solve_domain_(2),
      integrated_(false)
  {
    setKnownSymDeps(symdeps_all,3);
    setActiveSymDeps(symdeps_default,0);
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
	    cdebug(3)<<"discarding multiple funklets as only one is currently suported, unless ? "<<(!isSolvable()||tiled_)<< "= true "<<endl;
	    if(tiled_ || !isSolvable() ){
	      funkletref <<=new ComposedPolc(funklets);
	      cdebug(3)<<"composed funklet found? "<<funkletref-> objectType()<<endl;
	      funkletref().setDomain(domain);
	      return funkletref.dewr_p();
	    }
	  }
	if( n )
	  {
	    //get the one with best fitting domain....
	    funkletref <<= funklets.front();
	    
	    //reset dbid if funklet domain not matching 
	    if(funkletref().domain().start(0)<domain.start(0) || funkletref().domain().start(1)<domain.start(1) ||
	       funkletref().domain().end(0)>domain.end(0) || funkletref().domain().end(1)>domain.end(1))
	      funkletref(). setDbId (-1);
	    funkletref().setDomain(domain);
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

	    //use previous funklet, unless user really wants default??
	    if( _use_previous && converged_ && its_funklet_.valid()&& (its_funklet_->objectType()!=TpMeqComposedPolc))
	      {

		funkletref <<= its_funklet_;
		//reset dbid
		funkletref(). setDbId (-1);

	      }
	    else{
	      const Funklet *deffunklet = state()[FDefaultFunklet].as_po<Funklet>();
	      //	    FailWhen(!deffunklet,"no funklets found and no default_funklet specified");
	      if(!deffunklet) {
		cdebug(3)<<"no funklets found, try reusing old one "<<endl;
		FailWhen(!its_funklet_.valid()|| (its_funklet_->objectType()==TpMeqComposedPolc),"no funklets found,no default_funklet and no funklet specified");
		funkletref <<= its_funklet_;
		//reset dbid
		funkletref(). setDbId (-1);
	      }
	      else{
		funkletref <<= deffunklet;
		cdebug(3)<<"no funklets found, using default value from state record, type "<<funkletref().objectType()<<endl;
	      }
	    }
	  }
	funkletref().clearSolvable();
	funkletref().setDomain(domain);
	
	return funkletref.dewr_p();
      }
    return 0;
  }


  int Parm::initSolvable (Funklet &funklet,const Request &request)
  {
    // copy current domain into solvable funklet
    // (once we start solving, it is only valid for the solve domain, even if it may
    // have been valid for a bigger/different domain before)
  
    cdebug(4)<<"init solvable "<<endl;
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
    cdebug(4)<<"init solvable, nr:"<<nr<<endl;

    return nr;
  }

  void Parm::GetTiledDomains(Domain::Ref & domain, const Cells & cells,vector<Domain::Ref> & domainV){
    //   vector<Domain> domainV; //create vector of domains..1 per funklettile
    domainV.push_back(domain);
    //calculate domains..
    for(int axis=0;axis<Axis::MaxAxis;axis++){
      cdebug(4)<<"tiling axis "<<axis<<", nr_tiles:"<<tiling_[axis]<<endl;

      if(tiling_[axis]<=0) continue; //not tiled in this direction
      int nr_cells=cells.ncells(axis);
      const LoVec_double & cellStart = cells.cellStart (axis);
      const LoVec_double & cellEnd = cells.cellEnd (axis);
      if(nr_cells<=0) continue;

      int nr_tiles=(nr_cells+tiling_[axis]-1)/tiling_[axis]; //round to higher value
      vector<Domain::Ref> helpV;
 
      for(vector<Domain::Ref>::iterator domIt=domainV.begin();domIt<domainV.end();domIt++)
	  {
	    
	    for(int i=0;i<nr_tiles;i++)
	      {
		(*domIt)().defineAxis(axis,cellStart(i*tiling_[axis]),cellEnd(std::min(nr_cells-1,(i+1)*tiling_[axis]-1)));
		helpV.push_back(*domIt);
	      }
	    
	    
	  }
      domainV.clear();

      for(vector<Domain::Ref>::iterator domIt2=helpV.begin();domIt2<helpV.end();domIt2++)
	{
	  domainV.push_back(*domIt2);
	  
	}
      helpV.clear();
      cdebug(2)<<" total nr domains : "<<domainV.size()<<endl;
      
    }
  }


  Funklet * Parm::initTiledFunklet(Funklet::Ref &funkletref,const Domain & domain, const Cells & cells){

    //now if tiling change to ComposedPolc, all initialized with the same funklet....(should we check on solvability here?) 
    vector<Domain::Ref> domainV; //create vector of domains..1 per funklettile
    Domain::Ref domref;
    domref <<=new Domain(domain);


    GetTiledDomains(domref,cells,domainV);
    //now create funklet for every domain.
    if (funkletref->objectType()==TpMeqComposedPolc)
	{
	  bool match =true;
	  const DMI::List *funklist = funkletref[FFunkletList].as_po<DMI::List>();
	  FailWhen(!funklist,"Composed Polc does not contain funklist");
	  const Funklet::Ref & firstfunk = funklist->get(0);
	  int ncoeff = firstfunk->ncoeff();
	  
	  if(!funklist  || (domainV.size()!=funklist->size())) match=false;
	  else
	    for(int axis=0;axis<Axis::MaxAxis;axis++){
	      if(!tiling_[axis]) continue;
	      int funknr=0;
	      for(vector<Domain::Ref>::iterator domIt=domainV.begin();domIt<domainV.end();domIt++){
		const Funklet::Ref & partfunk = funklist->get(funknr++); 

		if(((*domIt)->start(axis)!= partfunk->domain().start(axis)) ||
		   ((*domIt)->end(axis)!= partfunk->domain().end(axis))||
		   (partfunk->ncoeff()!=ncoeff))
		  {
		    //maybe even better; only keep those funklets that do match in case nr_funklets>nr_domains
		    match=false;
		    break;
		  }

	      }
	      if(!match) break;

	    }
	  if(match){
	    return funkletref.dewr_p();
	  }
	  else
	    funkletref = firstfunk;
	}
    

    if(domainV.size()<=1)
      return funkletref.dewr_p();
      
 
    vector<Funklet::Ref> funklets;
    funklets.resize(domainV.size());
    int n=0;
    for(vector<Domain::Ref>::iterator domIt=domainV.begin();domIt<domainV.end();domIt++){
      funkletref().setDomain(**domIt);
      funkletref().setDbId(-1);
      funklets[n++]=funkletref;
    }
    cdebug(2)<<"creating composed polc  "<<funklets.size()<<endl;
    //   funkletref.detach();
    ComposedPolc * cpolc =new ComposedPolc(funklets);
    funkletref<<=cpolc;
    return funkletref.dewr_p();
      
  }


  Funklet * Parm::initFunklet (const Request &request,bool solve)
  {
    const Domain &domain = request.cells().domain();
    const Cells &cells = request.cells();
    
    HIID rq_dom_id = RqId::maskSubId(request.id(),domain_depend_mask_); 
    HIID newrid = RqId::maskSubId(request.id(),forest().getDependMask(FDomain)|forest().getDependMask(FDataset));
    // do we have a current funklet set up?
    
    //parm should keep a reference to the funklet object, snce it doesnt have to be equal to the wstate...
    //    Funklet * pfunklet = wstate()[FFunklet].as_wpo<Funklet>();
    Funklet * pfunklet(0);
    cdebug(3)<<" getting old funklet"<<endl;
   if(its_funklet_.valid())

      pfunklet= its_funklet_.dewr_p();
    // see if this can be reused
 
    if( pfunklet )
      {
	// (a) domain ID of request matches that of funklet: can reuse
	//     (a null domain ID in the request precludes this)

	//MM: changed.. reuse the funklet if domain or dataset changes 
	//	if( !rq_dom_id.empty() && rq_dom_id == domain_id_ )
	if( !newrid.empty() && newrid == rqid_ )
	  {
	    cdebug(3)<<"current funklet domain ID matches, re-using"<<endl;
	    return pfunklet;
	  }
	
	// (b) no domain in funklet (i.e. effectively infinite domain of applicability)
	if( ! tiled_ && (pfunklet->objectType()!=TpMeqComposedPolc) && !pfunklet->hasDomain() )
	  { 
	    cdebug(3)<<"current funklet has infinite domain, re-using"<<endl;
	    wstate()[FDomainId] = domain_id_ = rq_dom_id;
	    wstate()[FDomain].replace() <<= &domain;
	    rqid_=newrid;
	    return pfunklet;
	  }
	// (c) funklet domain is a superset of the requested domain
	if(!tiled_ && (pfunklet->objectType()!=TpMeqComposedPolc) &&  pfunklet->domain().supersetOfProj(domain) )
	  {
	    cdebug(3)<<"current funklet defined for superset of requested domain, re-using"<<pfunklet->getDbId()<<endl;
	    pfunklet->setDbId(-1);
	    wstate()[FDomainId] = domain_id_ = rq_dom_id;
	    wstate()[FDomain].replace() <<= &domain;
	    rqid_=newrid;
	    return pfunklet;
	  }
      }
    // no funklet, or funklet not suitable -- get a new one
    Funklet::Ref funkref;
    pfunklet = findRelevantFunklet(funkref,domain);
    FailWhen(!pfunklet,"no funklets found for specified domain");
    cdebug(2)<<"found relevant funklet, type "<<pfunklet->objectType()<<endl;
    if(tiled_ && isSolvable()){
     
	cdebug(4)<<"tiling funklet, "<<endl;
	Funklet *newfunklet = initTiledFunklet(funkref,domain,cells);
	newfunklet->setDomain(domain);
	its_funklet_<<=newfunklet;
	wstate()[FFunklet].replace() = newfunklet->getState();
	wstate()[FDomainId] = domain_id_ = rq_dom_id;
	wstate()[FDomain].replace() <<= &domain;
	rqid_=newrid;
	cdebug(2)<<"found relevant funklet,after tiling type "<<newfunklet->objectType()<<endl;
	return newfunklet;
      }

    
    if(pfunklet->objectType()!=TpMeqCompiledFunklet && pfunklet->hasField(FFunction))
      {
	cdebug(4)<<"function found in state, creating new compiled funklet"<<endl;
	its_funklet_<<=new CompiledFunklet(*pfunklet);
	pfunklet = its_funklet_.dewr_p();
      }
    else
      its_funklet_<<=funkref;
    // update state record
    wstate()[FFunklet].replace() = pfunklet->getState();
    wstate()[FDomainId] = domain_id_ = rq_dom_id;
    wstate()[FDomain].replace() <<= &domain;
    rqid_=newrid;
    return pfunklet;
  }



  // creates spid map in output result
  int Parm::discoverSpids (Result::Ref &ref,
                           const std::vector<Result::Ref> &,
                           const Request &request)
  {
    // init solvable funklet for this request
    Funklet * pfunklet = initFunklet(request,True);
    cdebug(3)<<"init funklet "<<pfunklet->objectType()<<" "<<pfunklet->isSolvable()<<endl;
    if( !pfunklet->isSolvable() )
      {	
	initSolvable(*pfunklet,request);
	if(  isSolvable()){
	  //set solve domain, default [0,1]
	  pfunklet->changeSolveDomain(solve_domain_);
	}
      }
    wstate()[FFunklet].replace() = pfunklet->getState();

    // get spids from funklet
    const std::vector<int> & spids = pfunklet->getSpids();
    ref <<= new Result(0);
    // populate spid map with default spid description record containing
    // just our node name
    DMI::Record::Ref defrec(DMI::ANONWR);
    defrec[AidName] = name();
    defrec[FNodeIndex] = nodeIndex();
    //get tilesizes, 0 for no tiling

    if(tiled_ && isSolvable())
      {
	DMI::Vec & tiles  = defrec[FTileSize] <<=new DMI::Vec(Tpint,Axis::MaxAxis,tiling_);
      }
    DMI::Record &map = ref()[FSpidMap] <<= new DMI::Record; 
    for( uint i=0; i<spids.size(); i++ ){
      map[spids[i]] = defrec; 
      cdebug(2)<<"spid "<<i<<" = "<<spids[i]<<endl;
    }
    return domain_depend_mask_|solve_depend_mask_;
  }


  //##ModelId=3F86886F022E
  int Parm::getResult (Result::Ref &resref,
		       const std::vector<Result::Ref> & childres,
		       const Request &request,bool newreq)
  {
    cdebug(3)<<"evaluating parm for domain "<<request.cells().domain()<<endl;
    // is request for solvable parm values?
    bool solve = isSolvable() && request.evalMode() > Request::GET_RESULT;
    // find a funklet to use
    Funklet * pfunklet = initFunklet(request,solve);
    // if funklet not set to solvable, do some extra init
    if( solve && !pfunklet->isSolvable() )
      {
	cdebug(3)<<"new solve domain, initializing"<<endl;
	initSolvable(*pfunklet,request);
	pfunklet->changeSolveDomain(solve_domain_);
      }
    else if( !solve && pfunklet->isSolvable() )
      {
	pfunklet->clearSolvable();
      }
    wstate()[FFunklet].replace() = pfunklet->getState();

    // init depend mask
    // if we are solvable, then we always depend on solution progress
    int depend = isSolvable() ? solve_depend_mask_ : 0;
    // Create result object and attach to the ref that was passed in
    //    Result &result = resref <<= new Result(1,request); // result has one vellset
    Result &result = resref <<= new Result(1); // result has one vellset
    VellSet & vs = result.setNewVellSet(0,0,request.evalMode());
    if(childres.empty())
      {
	//let funklet define the grid
	cdebug(3)<<"evaluating funklet"<<endl;
	pfunklet->evaluate(vs,request);
      }
    else
      {
	//grid was (partially) defined by children
	pfunklet->evaluate(vs,request,childres);

      }


    // If we have a single constant funklet, and are not integrated, then there's no 
    // dependency on domain. Otherwise, add domain mask
    //MM: Changed since even a constant MeqParm can depend on domain (eg. if its coeff in the meptable depend onthe domain)  
    
    //   if( !pfunklet->isConstant() || integrated_ )
    if( !pfunklet->isConstant() || integrated_ || parmtable_)
      depend |= domain_depend_mask_;

    // set cells in result as needed
    result.setCells(request.cells());
  
    // integrate over cell if so specified
    if( integrated_ )
      result.integrate();
  
    return depend;
  }


  void Parm::save()
  {
    if( !parmtable_ )
      return;
    if( !its_funklet_.valid() ) 
      return;
    if(its_funklet_->objectType()==TpMeqComposedPolc){
      DMI::List *funklist = its_funklet_()[FFunkletList].as_wpo<DMI::List>();
      if(!funklist) return;
      int nr_funk=funklist->size();
      cdebug(2)<<"saving "<<nr_funk<<" funklets"<<endl;
      for (int ifunk=0;ifunk<nr_funk;ifunk++)
	{
	  Funklet::Ref partfunk = funklist->get(ifunk);
	  parmtable_->putCoeff1(name_,partfunk(),false);
	  cdebug(4)<<" put in database "<<partfunk->getDbId()<<endl;
	  funklist->replace(ifunk,partfunk);
	}
    }
    else
      parmtable_->putCoeff1(name_,its_funklet_,false);
  }

  void Parm::resetDependMasks ()
  {
    Node::resetDependMasks();
    domain_depend_mask_ = computeDependMask(domain_symdeps_);
    solve_depend_mask_ = computeDependMask(solve_symdeps_);
    if( hasState() )
      {
	wstate()[FDomainDependMask] = domain_depend_mask_;
	wstate()[FSolveDependMask] = solve_depend_mask_;
      }
  }

  void Parm::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
    // get parm name, or use node name by default
    if( initializing && name_.empty() )
      name_ = name();
    rec[FParmName].get(name_,initializing);
    rec[FAutoSave].get(auto_save_,initializing);
    rec[FUsePrevious].get(_use_previous,initializing);
    rec[FConverged].get(converged_,initializing);
    rec[FSolvable].get(solvable_,initializing);
    rec[FIntegrated].get(integrated_,initializing);
    
    //default
    solve_domain_[0]=0.;
    solve_domain_[1]=1.;
    

    rec[FSolveDomain].get_vector(solve_domain_,initializing);

    const DMI::Record *tiling = rec[FTiling].as_po<DMI::Record>();
    if(tiling){
      for(int i=0;i<Axis::MaxAxis;i++){
	tiling_[i]=0;
	(*tiling)[Axis::axisId(i)].get(tiling_[i],0);
      
	if(tiling_[i]) tiled_=true;
      }
    }

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
	
	if(pfunklet->objectType()!=TpMeqCompiledFunklet  && pfunklet->hasField(FFunction))
	  {
	    cdebug(4)<<"function found in state, creating new compiled funklet"<<endl;
	    its_funklet_<<= new CompiledFunklet(*pfunklet);
	    
	  }
	else
	  if(pfunklet->hasField(FClass) && (*pfunklet)[FClass].as<string>()=="MeqPolcLog")
	    its_funklet_<<= new PolcLog(*pfunklet);
	  else
	    its_funklet_<<= new Polc(*pfunklet);
	

	cdebug(2)<<"new funklet set via state\n";
	// if a new funklet is set on the fly (i.e. not in node initialization),
	// then reset cached domain & domain ID. This will force an reinit
	// on the next getResult() call, thus either re-using or discarding the
	// funklet as appropriate.
	if( !initializing )
	  {
	    wstate()[FDomain].remove(); 
	    wstate()[FDomainId] = domain_id_ = HIID();
	    rqid_=HIID();
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
	cdebug(2)<<"default funklet set via state\n type = "<<deffunklet->objectType()<< endl;;
      }


    // Get ParmTable name 
    string tableName;
    HIID tableId;
    TypeId  TableType;
    if( rec->hasField(FTableName))
      {  TableType= rec[FTableName].type();   
	//check wether tablename is a string or a hiid in which case one should look in the forest state for the name
	if(TableType==Tpstring)
	  rec[FTableName].get(tableName);
	else if(TableType==TpDMIHIID)
	  {
	    //try to get the name from forest
	    rec[FTableName].get(tableId);
	    cdebug(3)<<"looking for tablename in forest state, field: "<<tableId<<endl;
	    const DMI::Record &Fstate=forest().state();
	    if(Fstate.hasField(tableId) && Fstate[tableId].type()==Tpstring) 
	      {
		Fstate[tableId].get(tableName);
	      }
	  }
	if (tableName.empty())
	  cdebug(2)<<"TableName doesnot have  correct type, or not found in forest state"<<endl; 
      
	if( tableName.empty() ) { // no table
	  parmtable_ = 0;
	}
	else    // else open a table
	  {
	    cdebug(2)<<"opening table: "<<tableName<<endl;
	    //check if table exists, otherwise create.
	    
	    parmtable_ = ParmTable::openTable(tableName);
	  }
      }//if rec[TableName]
    
  }

  int Parm::processCommands (Result::Ref &resref,const DMI::Record &rec,Request::Ref &reqref)
  {
    // process parent class's commands
    int retcode = Node::processCommands(resref,rec,reqref);
    bool saved  = false;
    
    if(rec[FConverged].as<bool>(false))
      {
	converged_=true;
	wstate()[FConverged]=converged_;
      }
    // Is an Update.Values command specified? use it to update solve funklets
    DMI::Record::Hook hset(rec,FUpdateValues);
    if( hset.exists() )
      {
	if( isSolvable() )
	  {
	    HIID req_domain_id = RqId::maskSubId(reqref->id(),domain_depend_mask_);
	    if( req_domain_id == domain_id_ )
	      {
		cdebug(2)<<"got "<<FUpdateValues<<" command"<<endl;
		// Update the funklet coefficients with the new values.
		LoVec_double values = hset.as<LoVec_double>();
		FailWhen(!tiled_ && (values.size() != int(its_funklet_().getSpids().size())),
			 "size of "+FUpdateValues.toString()+" does not match size of funklets");
		its_funklet_().update(values.data());
		wstate()[FFunklet].replace()=its_funklet_().getState();
		if( auto_save_ )
		  {
		    save();
		    saved = true;
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

    cdebug(2)<<"saving funklets ? "<<rec[FSaveFunklets].as<bool>(false)<<endl;

    if( !saved && rec[FSaveFunklets].as<bool>(false) ){
      save();

    }
    // lastly, check for a Clear.Funklets command
    if( rec[FClearFunklets].as<bool>(false) )
      {
	// clear out relevant fields
	its_funklet_.detach();
	wstate()[FFunklet].remove();
	wstate()[FDomain].remove();
	wstate()[FDomainId].remove();
	domain_id_ = HIID();
	rqid_ = HIID();
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

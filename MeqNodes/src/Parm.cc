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
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/MeqVocabulary.h>
#include <Common/Debug.h>
#include <Common/Lorrays.h>
#include <casa/BasicMath/Math.h>
#include <casa/Arrays/Matrix.h>
#include <casa/Arrays/Vector.h>
#include <DMI/List.h>
#include <MEQ/Forest.h>


static int checknr=0;

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
    FAutoSolve = AidAuto|AidSolve,
    FSolveAxis = AidSolve|AidAxis,
    FSolveRank = AidSolve|AidRank,
    FFunklet         = AidFunklet,
    FDefaultFunklet  = AidDefault|AidFunklet,
    FLongPolc = AidSolve|AidPolc,
    FParmValues = AidParm|AidValues,
    FSolveOffset = AidSolve|AidOffset;
 
  static const int minimal_points=1;
  //hardcoded scale factor to keep axis in reasonable range, 60 is chosen to convert seconds to minutes
  static const double scalefactor=1.;

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
      integrated_(false),
      LPnr_equations(0),
      auto_solve_(false),
      solve_axis_(-1),
      solve_rank_(3),
      solve_offset_(0),
      LPDbId(-1)
  {
    LPDomain=Domain();
// The default depmask only includes Solution. Solution is meant to be updated
// whenever the parm solvable state is changed, or when fiddling.
// Domain mask will be added if the funklet has >1 coefficient; solve_depend_mask 
// is added if the parm is solvable
    setKnownSymDeps(symdeps_all,3);
    setActiveSymDeps(symdeps_default,1);
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
      integrated_(false),
      LPnr_equations(0),
      auto_solve_(false),
      solve_axis_(-1),
      solve_rank_(3),
      solve_offset_(0),
      LPDbId(-1)
  {
    LPDomain=Domain();
// The default depmask only includes Solution. Solution is meant to be updated
// whenever the parm solvable state is changed, or when fiddling.
// Domain mask will be added if the funklet has >1 coefficient; solve_depend_mask 
// is added if the parm is solvable
    setKnownSymDeps(symdeps_all,3);
    setActiveSymDeps(symdeps_default,1);
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
	int n = parmtable_->getFunklets(funklets,name_,domain,auto_solve_);
	cdebug(3)<<n<<" funklets found in MEP table"<<endl;
	if( n>1 )
	  {
	    cdebug(2)<<"discarding mutliple funklets as only one is currently suported, unless ? "<<isSolvable()<< "= false "<<endl;
	    // ok think of something to make somthing big out of multiple funklets...
	    //What about creating a "mutliplePolc" class that does the job for you
	    //only if non-solvable..otherwise, at least select best fitting!
	    if(!isSolvable()){
	      funkletref <<=new ComposedPolc(funklets);
	      cdebug(2)<<"composed funklet found? "<<funkletref-> objectType()<<endl;
	      return funkletref.dewr_p();
	    }
	    
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
	    //	    FailWhen(!deffunklet,"no funklets found and no default_funklet specified");
	    if(!deffunklet) {
	      cdebug(3)<<"no funklets found, try reusing old one "<<endl;
	      Funklet *oldfunklet = wstate()[FFunklet].as_wpo<Funklet>();
	      FailWhen(!oldfunklet,"no funklets found,no default_funklet and no funklet specified");
	      //reset dbid
	      oldfunklet-> setDbId (-1);
	      funkletref <<= oldfunklet;
	    }
	    else{
	      cdebug(3)<<"no funklets found, using default value from state record, type "<<deffunklet -> objectType()<<endl;
	      funkletref <<= deffunklet;
	    }
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
    HIID rq_dom_id = RqId::maskSubId(request.id(),domain_depend_mask_); 
    // do we have a current funklet set up?
    Funklet * pfunklet = wstate()[FFunklet].as_wpo<Funklet>();
    // see if this can be reused
 
    if(auto_solve_ && !LPDomain.isDefined(0)) {//first domain
      LPnr_equations=0;
      LPDomain=Domain(domain);
    }   
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
    if(auto_solve_ && solve)//try snippet prediction 
      pfunklet = PredictFromLongPolc(funkref,request.cells().domain());
    else
      pfunklet = findRelevantFunklet(funkref,domain);
    FailWhen(!pfunklet,"no funklets found for specified domain");
    cdebug(2)<<"found relevant funklet, type "<<pfunklet->objectType()<<endl;
    // update state record
    wstate()[FFunklet].replace() <<= pfunklet;
    wstate()[FDomainId] = domain_id_ = rq_dom_id;
    wstate()[FDomain].replace() <<= &domain;
    return pfunklet;
  }

  // creates spid map in output result
  int Parm::discoverSpids (Result::Ref &ref,
                           const std::vector<Result::Ref> &,
                           const Request &request)
  {
    // init solvable funklet for this request
    Funklet * pfunklet = initFunklet(request,True);
    if( !pfunklet->isSolvable() )
    	initSolvable(*pfunklet,request);
    // get spids from funklet
    const std::vector<int> & spids = pfunklet->getSpids();
    ref <<= new Result(0);
    // populate spid map with default spid description record containing
    // just our node name
    DMI::Record::Ref defrec(DMI::ANONWR);
    defrec[AidName] = name();
    DMI::Record &map = ref()[FSpidMap] <<= new DMI::Record; 
    for( uint i=0; i<spids.size(); i++ )
      map[spids[i]] = defrec; 
    return domain_depend_mask_|solve_depend_mask_;
  }

  //##ModelId=3F86886F022E
  int Parm::getResult (Result::Ref &resref,
		       const std::vector<Result::Ref> &,
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
      }
    else if( !solve && pfunklet->isSolvable() )
      {
	pfunklet->clearSolvable();
      }
    // init depend mask
    // if we are solvable, then we always depend on solution progress
    int depend = isSolvable() ? solve_depend_mask_ : 0;
  
    // Create result object and attach to the ref that was passed in
    //    Result &result = resref <<= new Result(1,request); // result has one vellset
    Result &result = resref <<= new Result(1); // result has one vellset
    VellSet & vs = result.setNewVellSet(0,0,request.evalMode());
    cdebug(3)<<"evaluating funklet"<<endl;
    pfunklet->evaluate(vs,request);
  
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

  //##ModelId=3F86886F023C
  void Parm::save()
  {
    if( !parmtable_ )
      return;
    Funklet * pfunklet = wstate()[FFunklet].as_wpo<Funklet>();
    if( !pfunklet ) 
      return;
    cdebug(3)<<"saving funklet "<<LPDbId<<endl;
    parmtable_->putCoeff1(name_,*pfunklet,LPDbId,false);
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

  //##ModelId=400E5353033A
  void Parm::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
    // get parm name, or use node name by default
    if( initializing && name_.empty() )
      name_ = name();
    rec[FParmName].get(name_,initializing);
    rec[FAutoSave].get(auto_save_,initializing);
    rec[FSolvable].get(solvable_,initializing);
    rec[FIntegrated].get(integrated_,initializing);
    rec[FAutoSolve].get(auto_solve_,initializing);
    rec[FSolveAxis].get(solve_axis_,initializing);
    rec[FSolveRank].get(solve_rank_,initializing);
    rec[FSolveOffset].get(solve_offset_,initializing);
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
	// not in case the funklet is constant, therefore also remove cache 
	if( !initializing )
	  {
	    //	    cdebug(2)<<"new funklet, clearing cache"<<endl;
	    //	    clearCache();	    
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
	cdebug(2)<<"default funklet set via state\n type = "<<deffunklet->objectType()<< endl;;
      }


    // Get ParmTable name 
    string tableName;
    HIID tableId;
    TypeId  TableType;
    if( (*rec).hasField(FTableName))
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
	  if(auto_solve_ && initializing)
	    {
	      //open default table
	      cdebug(2)<<"no table name given, creating default with name: default_table"<<endl;
	      
	      if(!Table::isOpened("default_table"))
		ParmTable::createTable("default_table");
	      parmtable_ = ParmTable::openTable("default_table");
	      wstate()[FTableName] = "default_table";
	    }
	}
	else    // else open a table
	  {
	    cdebug(2)<<"opening table: "<<tableName<<endl;
	    //check if table exists, otherwise create.
	    
	    parmtable_ = ParmTable::openTable(tableName);
	  }
      }//if rec[TableName]
    
    else if(auto_solve_ && initializing)
      {
	//open default table
	cdebug(2)<<"no table name given, creating default with name: default_table"<<endl;
	
	if(!Table::isOpened("default_table"))
	  ParmTable::createTable("default_table");
	parmtable_ = ParmTable::openTable("default_table");
	wstate()[FTableName] = "default_table";
      }
  
    
    if(auto_solve_ && initializing)
      {
	DMI::List &LongPolc = wstate()[FLongPolc] <<=new DMI::List();
	DMI::List &ParmValues = wstate()[FParmValues] <<=new DMI::List();
      }
  }

  int Parm::processCommands (const DMI::Record &rec,Request::Ref &reqref)
  {
    // process parent class's commands
    int retcode = Node::processCommands(rec,reqref);
    bool saved  = false;
  
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
		Funklet &funklet = wstate()[FFunklet].as_wr<Funklet>();
		FailWhen(values.size() != int(funklet.getSpids().size()),
			 "size of "+FUpdateValues.toString()+" does not match size of funklets");
		funklet.update(values.data());
		//now update longpolc_solution
		//called here, because we want to sace LP, b4 saving "short polc", to have DBId
		if(auto_solve_ && auto_save_ ){
		  cdebug(2)<<"updating LP for the "<<++checknr<<"th time"<<endl;
		  UpdateLongPolc(1,&funklet);
		}


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
    if( !saved && rec[FSaveFunklets].as<bool>(false) ){
      if(auto_solve_){
	Funklet &funklet = wstate()[FFunklet].as_wr<Funklet>();
	cdebug(2)<<"updating LP for the "<<++checknr<<"th time"<<endl;
	UpdateLongPolc(1,&funklet);
      }
      save();

    }
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






  Funklet * Parm::PredictFromLongPolc(Funklet::Ref &funkletref,const Domain & rdom){
    cdebug(2)<<"predicting from long polc "<<endl;
    Funklet *pfunklet =  wstate()[FFunklet].as_wpo<Funklet>();
    DMI::List &LongPolc = wstate()[FLongPolc].as_wr<List>();
    if(pfunklet){
      //a funklet was available with different domain, update LongPolc
      UpdateLongPolc(0,pfunklet);
      int nd=UpdateLPDomain(rdom);
      if(nd){
	//domain is not fitting previous longpolc solution, restart from the beginning
	
	cdebug(3)<<"new domain restart long polc "<<endl;

	pfunklet = findRelevantFunklet(funkletref,rdom);
	
 	if(pfunklet)
	  {
	    
	    //update  long polc
	    UpdateLongPolc(0,pfunklet); 

	  }
	return pfunklet;
      }
      int last= LPAxis.size()-1;
      if(last<0) {
	cdebug(3)<<"failed updating coeff "<<" "<<last<<endl;

	pfunklet-> setDomain(rdom);
	//reset dbid
	pfunklet->setDbId(-1);
	return pfunklet;


      }
      const int nr_spids = pfunklet->getNumParms();
      //now  get funklet parameters
      double coeff[nr_spids];

      for(int spid=0;spid<nr_spids;spid++){
	
	
	Polc::Ref polcref = LongPolc.get(spid);
	DMI::NumArray Fcoeff = polcref->coeff();
	// Evaluate the expression (as double).
	const double* coeffData = static_cast<const double *>(Fcoeff.getConstDataPtr());
	double val=0.;
	for(int i=0;i<=solve_rank_;i++){
	  val += coeffData[i]*pow(1./scalefactor*(LPAxis[last]-solve_offset_),i);

	}
	
	coeff[spid]=val;

      }
            
      pfunklet->update(&coeff[0]);
      pfunklet-> setDomain(rdom);
      //reset dbid
      pfunklet->setDbId(-1);
      return pfunklet;

    }
    else //no funklet defined yet; 	
      {
	cdebug(3)<<"PredictFRomLongPolc, no funklet defined yet, looking for default"<<endl;
        pfunklet = findRelevantFunklet(funkletref,rdom);
	if(pfunklet)
	  {
	    
	    //update  long polc
	    UpdateLongPolc(0,pfunklet); 

	  }
	return pfunklet;
      }

   


    return pfunklet;
    
  }

  int Parm::UpdateLPDomain(const Domain &rdom){
 
    if(!LPDomain.isDefined(0)) {//first domain
      LPnr_equations=0;
      LPDomain=Domain(rdom);
      return 1;
    }


    double start[2];
    double end[2];
    int reset=0;
    for(int i=0;i<2;i++){
      start[i]=rdom.start(i);
      end[i]=rdom.end(i);
      if(i==solve_axis_) continue;
      if(!LPDomain.isDefined(i) || (start[i]!=LPDomain.start(i) || end[i]!=LPDomain.end(i))) 
	{
	  if(solve_axis_>=0) reset=1;
	  else {
	    solve_axis_=i;
	    wstate()[FSolveAxis]=  solve_axis_; 
	    solve_offset_=LPDomain.start(solve_axis_);
	    wstate()[FSolveOffset]=  solve_offset_; 
	  }
	}
      
    }
    if(!reset) {
      if(LPAxis.empty()) //initialize 
	LPAxis.push_back(LPDomain.start(solve_axis_)+0.5*(LPDomain.end(solve_axis_) - LPDomain.start(solve_axis_)));

      LPAxis.push_back(start[solve_axis_]+0.5*(end[solve_axis_]-start[solve_axis_]));
      LPDomain=LPDomain.envelope(rdom);   
      return reset;
    }
    

    SaveLongPolc(); //SAve All this work we did in internal(?) table, and restart..

    //reset
    wstate()[FLongPolc].remove();
    wstate()[FParmValues].remove();
    wstate()[FLongPolc] <<=new DMI::List();
    wstate()[FParmValues] <<=new DMI::List();
    
    
    

    LPDbId=-1; //reset rownr in meptable

    //clear LongPolc;
    //LPpar_valuesV.clear();
    LPAxis.clear();
    itsSolver.clear();

    LPnr_equations=0;
    LPDomain=rdom;
    solve_axis_=-1;
    return reset;
    
    
  }


  int Parm::UpdateLongPolc(int old_domain, Funklet * rpolc){  //called from processcommands ...update with latest values of funklet for old domain, or create new values if new_daomain

    if(!auto_solve_) return 0;

    //    Funklet * rfunklet = wstate()[FFunklet].as_wpo<Funklet>();

 
    if(! rpolc) return  0;
    if (rpolc->objectType() != TpMeqPolc) return 0;
    Polc::Ref polcref;
    polcref<<= new Polc(*rpolc);
    //initialize LongPolcs
    int nr_spids=rpolc->getNumParms();
    DMI::List &LongPolc = wstate()[FLongPolc].as_wr<List>();
    int size =LongPolc.size();
    if(size && size !=nr_spids)
      {//nr. spids changed, reset

	wstate()[FLongPolc].remove();
	wstate()[FParmValues].remove();
	wstate()[FLongPolc] <<=new DMI::List();
	wstate()[FParmValues] <<=new DMI::List();
	

	
	//clear LongPolc;
	//LPpar_valuesV.clear();
	LPAxis.clear();
	itsSolver.clear();
	
	LPnr_equations=0;
	LPDomain=Domain();
	solve_axis_=-1;
	return 0;

      }
    LongPolc = wstate()[FLongPolc].as_wr<List>();
    if(!LongPolc.size())
      InitLongPolc(polcref);
    DMI::List &ParmValues = wstate()[FParmValues].as_wr<List>();
    
    int last = ParmValues.size()-1;
    if(last<0 && old_domain) {cdebug(3)<<"no Parmvalues although domain has been updated"<<endl;return 0;}
    if(!old_domain)
      { 
	ParmValues.addBack(polcref); 
	LPnr_equations++;
	return 0;
      }
    else
      {
	ParmValues.replace(last,polcref);

      }

       

    if(LPnr_equations>=min(solve_rank_+1,2)){//only solve if we have enough equations

      vector<double> derv(min(solve_rank_+1 , LPnr_equations));

      // To be used as an index array for quickly feeding the equations
      // to the solver.
      vector<int> dervIndex(min(solve_rank_+1 , LPnr_equations));
      Vector<double> solutions(min(solve_rank_+1 , LPnr_equations),0.);


      cdebug(3)<<"filling the equations nr:"<<LPnr_equations<<" Axis "<<LPAxis.size()<<endl;
    
      for(int spid=0;spid<nr_spids;spid++) //we have to solve for every spid.
	{

	  //initialize the solver
	  uint startnewdata=0;
	  if(LPnr_equations<=solve_rank_+minimal_points)
	    itsSolver[spid].set((uint) min(solve_rank_+1 , LPnr_equations));
	  else {
	    //don't initialize if nr_equations large enough
	    startnewdata = LPnr_equations-2;
	  }
	  //fill matrix
	  //ony add the last equation to a temporay copy, such that we do not overload itSolver

	  

	  double val=0;
	  for(int eqnr=startnewdata;eqnr<LPnr_equations-1;eqnr++){
	    Polc::Ref PVref = ParmValues.get(eqnr);
	    DMI::NumArray PVcoeff= PVref->coeff();
	    const double* PVcoeffData = static_cast<const double *>(PVcoeff.getConstDataPtr());
	    val=PVcoeffData[spid];
	    int nr_derv=0;
	    for(int k=0;k<=solve_rank_ && k<LPnr_equations;k++){//only solve up to order <= nr_equations
	      derv[k]=(pow(1./scalefactor*(LPAxis[eqnr]-solve_offset_),k));
	      dervIndex[nr_derv++] = k;
	    }
	    itsSolver[spid].makeNorm(nr_derv,&dervIndex[0],&derv[0],1.,val);
	  }
	  //now solve
	
	  uint rank;
	  //make copy of solver for the real work
	  casa::LSQaips tmpsolver(itsSolver[spid]);
	  

	  uint lasteq = LPnr_equations-1;
	  Polc::Ref PVref = ParmValues.get(lasteq);
	  DMI::NumArray PVcoeff= PVref->coeff();
	  const double* PVcoeffData = static_cast<const double *>(PVcoeff.getConstDataPtr());
	  val=PVcoeffData[spid];
	  int nr_derv=0;
	  for(int k=0;k<=solve_rank_ && k<LPnr_equations;k++){//only solve up to order <= nr_equations
	    derv[k]=(pow(1./scalefactor*(LPAxis[lasteq]-solve_offset_),k));
	    dervIndex[nr_derv++] = k;
	  }
	  tmpsolver.makeNorm(nr_derv,&dervIndex[0],&derv[0],1.,val);
	  
	  Bool ok = tmpsolver.invert(rank);
	  tmpsolver.solve( solutions);
	 
	  //update Longpolc:
	  LoVec_double coeff(solve_rank_+1);
	  for(int rnk=0; rnk <=solve_rank_;rnk++) coeff(rnk)=0.;
	  for(uint sol=0;sol<solutions.nelements();sol++)
	    coeff(sol)=solutions[sol];
	  
	  Polc::Ref LPref = LongPolc.get(spid);
	  Polc::Ref newpolc;
	  LPref().setCoeff(coeff);
	  newpolc<<= new Polc(LPref);
	  LongPolc.replace(spid,newpolc);
	  

	  //get errors
	  Matrix<double> covar;
	  Vector<double> errors;
	  tmpsolver.getErrors(errors);
	  tmpsolver.getCovariance(covar);
	  cdebug(4)<<"cov. matrix :"<<endl;
	  for(int i=0;i<=min(solve_rank_,LPnr_equations-1);i++){
	    for(int j=0;j<=min(solve_rank_,LPnr_equations-1);j++)
	      cdebug(4)<<covar(i,j)<<"  ";
	    cdebug(4)<<" error "<<errors(i)<<endl;
	  }
	  double chi2 = tmpsolver.getChi2();
	  cdebug(4)<<" rank "<<rank<<" chi2 "<<chi2<<endl;

	}//loop over spids
    }//check on nr of equations
    SaveLongPolc();
    return LPnr_equations;
  }







  void Parm::SaveLongPolc()
  {
    if( !parmtable_ )
      return;
    //make funklet from Longpolc
    DMI::List &LongPolc = wstate()[FLongPolc].as_wr<List>();
    Polc * rpolc = wstate()[FFunklet].as_wpo<Polc>();
    int nr_spids = rpolc->getNumParms();
    LoShape shape;
    if(solve_axis_==0) shape = LoShape(solve_rank_+1,nr_spids);
    else shape = LoShape(nr_spids,solve_rank_+1);
    cdebug(3)<<"saving LP "<<solve_axis_<<"  nr_spids "<<nr_spids<<"  "<<LongPolc.size()<<endl;

    LoMat_double Coeff(shape);
    // LoMat_double Coeff(nr_spids,solve_rank_);

    for(int spid=0;spid<nr_spids;spid++) //we have to solve for every spid.
      {
        Polc::Ref LPref = LongPolc.get(spid);
        DMI::NumArray LPcoeff= LPref->coeff();
        const double* LPcoeffData = static_cast<const double *>(LPcoeff.getConstDataPtr());
        for(int i=0; i<=solve_rank_;i++){
	  if(solve_axis_==0)
	    Coeff(i,spid)=LPcoeffData[i];
	  else 
	    Coeff(spid,i)=LPcoeffData[i];
	}

      }


    Polc pfunklet(Coeff);
    pfunklet.setDomain(LPDomain);
    pfunklet.setDbId(LPDbId);
    pfunklet.setOffset(solve_axis_,solve_offset_);
    parmtable_->putCoeff1(name_,pfunklet,-1,0);
    LPDbId=pfunklet.getDbId();

  }

  

  void Parm::InitLongPolc(const Polc &rpolc){
    //  itscoeff.clear();
    itsSolver.clear();
    DMI::List &LongPolc = wstate()[FLongPolc].as_wr<List>();
    int LPSize=LongPolc.size();
    int nr_spids=rpolc.getNumParms();
    LoVec_double coeff(solve_rank_+1);
    DMI::NumArray Fcoeff = rpolc.coeff();
    // Evaluate the expression (as double).
    const double* coeffData = static_cast<const double *>(Fcoeff.getConstDataPtr());
    if(LPSize<nr_spids){
      for(int i=LPSize;i<nr_spids;i++)
	{
	  casa::LSQaips tmpSolver(1);
	  itsSolver.push_back(tmpSolver);
	  coeff(0) = coeffData[i];
	  //itscoeff.push_back(coeff(0));
	  for(int cf=1;cf<=solve_rank_;cf++){
	    coeff(cf)=0.;
	    //itscoeff.push_back(0.);
	  }
	  Polc::Ref polcref;
	  polcref <<= new Polc(coeff);
	  
	  LongPolc.addBack(polcref);
	  cdebug(3)<<"initializing  LP, size "<<LongPolc.size()<<endl;;

	}
      


    }

    
  }



} // namespace Meq

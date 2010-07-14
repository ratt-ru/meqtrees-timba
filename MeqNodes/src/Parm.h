//# Parm.h: (solvable) Parameter
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

#ifndef MEQNODES_PARM_H
#define MEQNODES_PARM_H

//# Includes
#include <MEQ/Node.h>
#include <MEQ/Vells.h>
#include <MEQ/Funklet.h>
#include <MEQ/ComposedPolc.h>
#include <MEQ/Spline.h>
#include <MEQ/Polc.h>
#include <MEQ/PolcLog.h>



#ifdef HAVE_PARMDB
#include <ParmDB/ParmDB.h>
#else
#include <MEQ/ParmTable.h>
#endif
#include <TimBase/lofar_vector.h>
#include <MEQ/MeqVocabulary.h>
#include <MeqNodes/TID-MeqNodes.h>
#include <MeqNodes/AID-MeqNodes.h>

#pragma aidgroup MeqNodes
#pragma types #Meq::Parm

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqParm
//  Represents a parameter, either created on-the-fly (a default
//  value must then be supplied), or read from a MEP database.
//  A MeqParm cannot have any children.
//field: funklet [=]
//  active funklet. A funklet object (e.g. meq.polc()) may be provided. 
//  This will be reused for subsequent requests if the domains match, or
//  if no domain is specified.
//field: default_value [=]
//  default value. The c00 coefficient of a polc.
//  This is used when an applicable funklet is not found in the table, or 
//  a table is not provided.
//field: integrated F  
//  if true, the parm represents an integration -- result value will be 
//  multiplied by cell size
//field: table_name '' 
//  MEP table name. If empty, then the default parameter value is used
//field: parm_name '' 
//  MEP parm name used to look inside the table. If empty, then the node 
//  name is used instead.
//field: auto_save F 
//  if T, then any updates to a funklet are saved into the MEP table 
//  automatically (for example, after each solve iteration). Default 
//  behaviour is to only save when specified via a request rider (e.g.,
//  at the end of a solve).
//defrec end

namespace Meq {
  const HIID
    // Parm staterec fields
    FSolvable        = AidSolvable,
    FTableName       = AidTable|AidName,
    FParmName        = AidParm|AidName,
    FAutoSave        = AidAuto|AidSave,
    FDomainId        = AidDomain|AidId,
    // FDomain      defined previously
    FFunklet         = AidFunklet,
    FDefaultFunklet  = AidDefault|AidFunklet,
    FDefaultValue  = AidDefault|AidValue,
    FSolveDomain = AidSolve|AidDomain,
    FUsePrevious = AidUse|AidPrevious,
    FSolveGroup = AidSolve|AidGroup,
    FTileSize = AidTile|AidSize,
    FTiling = AidTiling,
    FSpline = AidSpline,
    FInitFunklet  = AidInit|AidFunklet,
    FConverged  = AidConverged,
    FSaveAll  = AidSave|AidAll,
    FResetFunklet = AidReset|AidFunklet,
    FIgnoreTime = AidIgnore|AidTime,
    FForcePositive = AidForce|AidPositive,
    FCyclic = AidCyclic,
    FCacheFunklet = AidCache|AidFunklet,
    FConstrain = AidConstrain,
    FConstrainMin = AidConstrain|AidMin,
    FConstrainMax = AidConstrain|AidMax,
    FCoeffIndex = AidCoeff|AidIndex;
  
  
  const double PI=3.14159265; 

  // This class contains the coeff of any funklet, either solvable or unsolvable.
  class Parm: public Node
  {
  public:
    // The default constructor.
    // The object should be filled by the init method.
    Parm();
    
    virtual ~Parm();
    
    virtual TypeId objectType() const
    { return TpMeqParm; }
    
    bool isSolvable() const
    { return solvable_; }

    // Get the requested result of the parameter.
    virtual int getResult (Result::Ref &resref, 
			   const std::vector<Result::Ref> &childres,
			   const Request &req,bool newreq);

    // process Parm-specific rider commands
    // the following commands are recognized:
    // Update.Parm , args:
    //    { incr_update=<vector of doubles>, # incremental updates to spid values (default: no update)
    //      converged=bool,                  # set the converged flag (default false)
    //      save_funklets=bool,              # save funklets (default false)
    //      clear_funklets=bool              # clear funklets (default false)
    //    }
    // Save.Funklets      args: none          
    //    Save funklets (can also be specified via an option to Update.Parm)
    // Clear.Funklets     args: none          # clear funklets
    //    Clear funklets (can also be specified via an option to Update.Parm)
    virtual int processCommand (Result::Ref &resref,
                                const HIID &command,
                                DMI::Record::Ref &args,
                                const RequestId &rqid = RequestId(),
                                int verbosity=0);
    
    // clears out any current funklets
    void clearFunklets ();

    
    // Make the new value persistent (for the given domain).
    virtual void save();

    //## Standard debug info method
    virtual string sdebug (int detail = 1, const string& prefix = "",
			   const char* name = 0) const;

  

    LocalDebugContext;

  protected:
    Funklet * initSplineFunklet(Funklet::Ref &funkletref,const Domain & domain, const Cells & cells);
    Funklet * initTiledFunklet(Funklet::Ref &funkletref,const Domain & domain, const Cells & cells);
    bool checkTiledFunklet(Funklet::Ref &funkletref,std::vector<Domain::Ref> domainV);
    // checks if current funklet can be reused
    Funklet * initFunklet (const Request &request,bool solve);
    //##ModelId=400E5353019E
    // finds new funklets in table or uses the default
    Funklet * findRelevantFunklet (Funklet::Ref &funkletref,const Domain &domain);
  
    // Initialize the funklet for the given solve domain. First
    int initSolvable (Funklet &funklet,const Request &request);

    void openTable(); 
    void closeTable(); 
    Funklet *getFunkletFromDB(Funklet::Ref &funkletref,const Domain &domain);
    void getDefaultFromDB(Funklet::Ref &funkletref);
    //##ModelId=400E5353033A
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  
  
    virtual int discoverSpids (Result::Ref &resref, 
			       const std::vector<Result::Ref> &childres,
			       const Request &req);
  
  private:
    bool solvable_;
    bool auto_save_;
    std::string solve_group_;  // solve subgroup, empty by default
    bool tiled_;//true for tiled solvables
    int tiling_[Axis::MaxAxis]; //vector containing tilesizes per axis (<= 0 means no tiling)
    bool splined_;//true for spline funklet
    int splining_[Axis::MaxAxis]; //vector containing spline_sizes per axis (<= 0 means no splining)
    int _use_previous;// if available use previous funklet,  instead of default_funklet

    bool converged_; // only use previous if previous solution converged..
    bool ignore_convergence_; // also use previous if previous solution did not converge..

    bool reset_funklet_;//reset funklet instead of using values from database
    bool ignore_time_;// if true time stamp is ignored when retrieving from ParmDB
    //##ModelId=3F86886F0213
    std::string name_;
    //##ModelId=400E535000A3
#ifdef HAVE_PARMDB
    LOFAR::ParmDB::ParmDB * parmtable_;
#else
    ParmTable *parmtable_;
#endif
    std::string parmtable_name_;
    double  default_;
    bool force_shape_;
    bool constrained_;
    bool force_positive_;
    bool cyclic_;  //for cyclic parameters (like phases) force coefficients to stay within one period per grid ... only valid for polcs and even there..
    bool cache_funklet_;  // keep funklet of non-solvable parameters in cahce
    double period_;
    LoShape shape_;//shape of  polctype funklets
    Funklet::Ref init_funklet_;//funklet for initialisation 
    Funklet::Ref its_funklet_; //keep a ref to the funklet 


    HIID        domain_id_,res_id_,rq_all_id_;
    int         domain_depend_mask_;
    int         solve_depend_mask_;
    int         res_depend_mask_;
    std::vector<HIID> domain_symdeps_;
    std::vector<HIID> solve_symdeps_;
    std::vector<HIID> resolution_symdeps_;

    std::vector<double> solve_domain_; //solve domain, default = [0,1]
    std::vector<double> its_constraints_; //constraints, default = [-inf,inf], only filled if constrained_ =true;only working for constant polcs
    std::vector<double> its_constraints_min_; //constraints, default = [-inf,inf], only filled if constrained_ =true;
    std::vector<double> its_constraints_max_; //constraints, default = [-inf,inf], only filled if constrained_ =true;
    bool        integrated_;

    //some functions
    void GetTiledDomains(Domain::Ref & domain, const Cells& cells,vector<Domain::Ref> & domainV);
  


  };
}// namespace Meq

#endif

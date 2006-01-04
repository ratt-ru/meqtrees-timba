//# Parm.h: (solvable) Parameter
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

#ifndef MEQNODES_PARM_H
#define MEQNODES_PARM_H

//# Includes
#include <MEQ/Node.h>
#include <MEQ/Vells.h>
#include <MEQ/Funklet.h>
#include <MeqNodes/CompiledFunklet.h>
#include <MeqNodes/ParmTable.h>
#include <Common/lofar_vector.h>

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
//field: default [=]
//  default funklet. A funklet object (e.g. meq.polc()) may be provided. 
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
  // This class contains the coeff of any funklet, either solvable or unsolvable.
  class Parm: public Node
  {
  public:
    // The default constructor.
    // The object should be filled by the init method.
    //##ModelId=3F86886F021B
    Parm();
    
    // Create a parameter with the given name and default value.
    // The default value is used if no suitable value can be found.
    // The ParmTable can be null meaning that the parameter is temporary.
  
    Parm (const string& name, ParmTable* table,
	  const Funklet::Ref::Xfer & defaultValue = Funklet::Ref() );
    
    virtual ~Parm();
    
    virtual TypeId objectType() const
    { return TpMeqParm; }
    
    bool isSolvable() const
    { return solvable_; }

    // Get the requested result of the parameter.
    virtual int getResult (Result::Ref &resref, 
			   const std::vector<Result::Ref> &childres,
			   const Request &req,bool newreq);

    // process parm-specific rider commands
    virtual int processCommands (Result::Ref &resref,const DMI::Record &rec,const Request &req);
    
    // Make the new value persistent (for the given domain).
    virtual void save();

    //## Standard debug info method
    virtual string sdebug (int detail = 1, const string& prefix = "",
			   const char* name = 0) const;

  

    LocalDebugContext;

  protected:
    virtual void resetDependMasks ();
    Funklet * initTiledFunklet(Funklet::Ref &funkletref,const Domain & domain, const Cells & cells);

    // checks if current funklet can be reused
    Funklet * initFunklet (const Request &request,bool solve);
    //##ModelId=400E5353019E
    // finds new funklets in table or uses the default
    Funklet * findRelevantFunklet (Funklet::Ref &funkletref,const Domain &domain);
  
    // Initialize the funklet for the given solve domain. First
    int Parm::initSolvable (Funklet &funklet,const Request &request);

    //##ModelId=400E5353033A
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  
  
    virtual int discoverSpids (Result::Ref &resref, 
			       const std::vector<Result::Ref> &childres,
			       const Request &req);
  
  private:
    
    //##ModelId=3F86886F0216
    bool solvable_;
    bool auto_save_;
    bool tiled_;//true for tiled solvables
    int tiling_[Axis::MaxAxis]; //vector containing tilesizes per axis (<= 0 means no tiling)
    bool _use_previous;// if available use previous funklet,  instead of default_funklet

    bool converged_; // only use previous if previous solution converged..
    //##ModelId=3F86886F0213
    string name_;
  
    //##ModelId=400E535000A3
    ParmTable * parmtable_;
  
    //##ModelId=400E535000B2
    //##Documentation
    //## default funklet (used if no table or no matching funklets in the table)
    Funklet::Ref   default_funklet_;
    Funklet::Ref its_funklet_; //keep a ref to the funklet 
  
    HIID        domain_id_,rqid_;
  
    int         domain_depend_mask_;
    int         solve_depend_mask_;
    std::vector<HIID> domain_symdeps_;
    std::vector<HIID> solve_symdeps_;
    std::vector<double> solve_domain_; //solve domain, default = [0,1]

  
    bool        integrated_;

    //some functions
    void GetTiledDomains(Domain::Ref & domain, const Cells& cells,vector<Domain::Ref> & domainV);
  


  };
}// namespace Meq

#endif

//# Parm.h: Parameter with polynomial coefficients
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

#ifndef MEQ_PARM_H
#define MEQ_PARM_H

//# Includes
#include <MEQ/Node.h>
#include <MEQ/Vells.h>
#include <MEQ/Funklet.h>
#include <MeqNodes/ParmTable.h>
#include <Common/lofar_vector.h>

#include <MeqNodes/TID-MeqNodes.h>
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


// This class contains the coefficients of a 2-dim polynomial.
// The order in time and frequency must be given.
// The nr of coefficients is (1+order(time)) * (1+order(freq)).
// The coefficients are numbered 0..N with the time as the most rapidly
// varying axis.

//##ModelId=3F86886E01BD
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
    //##ModelId=3F86886F0242
  Parm (const string& name, ParmTable* table,
	      const Funklet::Ref::Xfer & defaultValue = Funklet::Ref() );

    //##ModelId=3F86886F021E
  virtual ~Parm();

  //##ModelId=400E53510330
  virtual TypeId objectType() const
  { return TpMeqParm; }

    //##ModelId=3F86886F022C
  bool isSolvable() const
  { return solvable_; }

  // Get the requested result of the parameter.
    //##ModelId=3F86886F022E
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  // process parm-specific rider commands
  virtual int processCommands (const DataRecord &rec,Request::Ref &reqref);

  // Make the new value persistent (for the given domain).
    //##ModelId=3F86886F023C
  virtual void save();

    //##ModelId=400E53520391
  //## Standard debug info method
  virtual string sdebug (int detail = 1, const string& prefix = "",
			 const char* name = 0) const;
  
  LocalDebugContext;

protected:
  virtual void resetDependMasks ();

  // checks if current funklet can be reused
  Funklet * initFunklet (const Request &request,bool solve);
    //##ModelId=400E5353019E
  // finds new funklets in table or uses the default
  Funklet * findRelevantFunklet (Funklet::Ref &funkletref,const Domain &domain);
  
  // Initialize the funklet for the given solve domain. First
  int Parm::initSolvable (Funklet &funklet,const Request &request);

    //##ModelId=400E5353033A
  virtual void setStateImpl (DataRecord &rec,bool initializing);
  
private:
    
    //##ModelId=3F86886F0216
  bool solvable_;
  bool auto_save_;
  
    //##ModelId=3F86886F0213
  string name_;
  
    //##ModelId=400E535000A3
  ParmTable * parmtable_;
  
  //##ModelId=400E535000B2
  //##Documentation
  //## default funklet (used if no table or no matching funklets in the table)
  Funklet::Ref   default_funklet_;
  
  //##Documentation
  //## ID of current domain
  HIID        domain_id_;
  
  int         domain_depend_mask_;
  int         solve_depend_mask_;
  std::vector<HIID> domain_symdeps_;
  std::vector<HIID> solve_symdeps_;
  
  bool        integrated_;
  
};


} // namespace Meq

#endif

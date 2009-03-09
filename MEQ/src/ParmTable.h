//# ParmTable.h: Abstract class for holding parameters in a table.
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
//# $Id: ParmTable.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQNODES_PARMTABLE_H
#define MEQNODES_PARMTABLE_H

#include <MEQ/Funklet.h>
#include <MEQ/Domain.h>
#include <map>

//# Includes
namespace Meq {

//##ModelId=3F86886E01E4
class ParmTable
{
public:
  virtual ~ParmTable ()
  {}
  
  // Get the parameter values for the given funklet and domain.
  // The matchDomain argument is set telling if the found parameter
  // matches the domain exactly.
  // Note that the requested domain may contain multiple funklets.
  // Returns # of funklets in vector
    //##ModelId=3F86886F02BD
  virtual int getFunklets (vector<Funklet::Ref> &funklets,const string& parmName, const Domain& domain) =0;

  // Put the coefficients for the given funklet and domain.
  // Returns the DbId of the funklet.
  // If domain_is_key, checks that domain is unique
    //##ModelId=3F86886F02C8
  virtual Funklet::DbId putCoeff (const string& parmName, const Funklet& funklet,bool domain_is_key=false) =0;
  
  // Alternative: put the coefficients for the given funklet and domain.
  // If a new DbId is allocated, stores it in the funklet.
  // If domain_is_key, checks that domain is unique.
  void putCoeff1 (const string& parmName,Funklet& funklet, bool domain_is_key=false)
  { funklet.setDbId(putCoeff(parmName,funklet,domain_is_key)); }
  
  
  // Get the initial coefficients for the given funklet.
  // Returns the # of coefficients (0 for none)
  // This really ought to be phased out...
    //##ModelId=3F86886F02C3
  virtual int getInitCoeff (Funklet::Ref &,const string&)
  { return 0; }

    //##ModelId=3F95060D0388
  virtual const string& name() const  =0;

  // Lock the parm table (for write).
  virtual void lock()
  {}

  // Unlock the parm table.
  virtual void unlock()
  {}

  // flushes data from the ParmTable to disk
  virtual void flush ()
  {}

  
  // define a debug context
  LocalDebugContext;
  
  virtual std::string sdebug(int=0)
  { return name(); }


};


} // namespace Meq

#endif

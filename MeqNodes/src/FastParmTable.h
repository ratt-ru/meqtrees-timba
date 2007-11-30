//# FastParmTable.h: Object to hold parameters in a casa table.
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
//# $Id: CasaParmTable.h 5418 2007-07-19 16:49:13Z oms $

#ifndef HAVE_PARMDB

#ifndef MEQNODES_FASTPARMTABLE_H
#define MEQNODES_FASTPARMTABLE_H

#include "config.h"
#ifdef HAVE_GDBM
#define HAVE_FASTPARMTABLE 1

#include <gdbm.h>
#include <MeqNodes/ParmTable.h>

namespace Meq {

//##ModelId=3F86886E01E4
class FastParmTable : public ParmTable
{
public:
    //##ModelId=3F86886F02B7
  explicit FastParmTable (const string& tableName,bool create_new=false);

    //##ModelId=3F86886F02BC
  virtual ~FastParmTable();

  // Get the parameter values for the given funklet and domain.
  // The matchDomain argument is set telling if the found parameter
  // matches the domain exactly.
  // Note that the requested domain may contain multiple funklets.
  // Returns # of funklets in vector
    //##ModelId=3F86886F02BD
  int getFunklets (vector<Funklet::Ref> &funklets,const string& parmName, const Domain& domain);

  // Put the coefficients for the given funklet and domain.
  // Returns the DbId of the funklet.
  // If domain_is_key, checks that domain is unique
    //##ModelId=3F86886F02C8
  Funklet::DbId putCoeff (const string& parmName, const Funklet& funklet,bool domain_is_key=false);
  
  
  // Get the name of the CasaParmTable.
    //##ModelId=3F95060D0388
  const string& name() const
  { return table_name_; }

//  // Lock the parm table (for write).
//  void lock();
//
//  // Unlock the parm table.
//  void unlock();

  void flush ();
  
private:
  std::string table_name_;
  Thread::Mutex mutex_;
  
  FILE *fdomains_;
  GDBM_FILE fdb_;
  
  // this is a binary structure used to represent a domain in the list
  class DomainEntry
  {
    public:
      DomainEntry ();
      DomainEntry (const Domain &dom);
      
      // returns True if domains match
      bool match (const Domain &dom);
      
      // returns True if dom overlaps self
      bool overlaps (const Domain &dom);
      
    private:
      bool   defined[Axis::MaxAxis];
      double start[Axis::MaxAxis];
      double end[Axis::MaxAxis];
  };
  
  // list of known domains
  std::vector<DomainEntry> domain_list_;
  std::vector<bool>        domain_match_;

  // helper functions to throw an error (from errno or gdbm)
  void throwErrno (const string &message);
  void throwGdbm  (const string &message);
  

};


} // namespace Meq

#endif // HAVE_GDBM

#endif
#endif

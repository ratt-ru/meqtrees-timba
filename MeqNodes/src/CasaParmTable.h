//# CasaCasaParmTable.h: Object to hold parameters in a casa table.
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
//# $Id$

#ifndef HAVE_PARMDB

#ifndef MEQNODES_CASAPARMTABLE_H
#define MEQNODES_CASAPARMTABLE_H

//# Includes
#include <tables/Tables/Table.h>
#include <tables/Tables/ColumnsIndex.h>
#include <casa/Containers/RecordField.h>
#include <MeqNodes/ParmTable.h>
#include <TimBase/lofar_vector.h>
#include <TimBase/Thread/Mutex.h>
#include <map>


namespace Meq {

//##ModelId=3F86886E01E4
class CasaParmTable : public ParmTable
{
public:
    //##ModelId=3F86886F02B7
  explicit CasaParmTable (const string& tableName,bool create_new=false);

    //##ModelId=3F86886F02BC
  virtual ~CasaParmTable();

  // Get the parameter values for the given funklet and domain.
  // The matchDomain argument is set telling if the found parameter
  // matches the domain exactly.
  // Note that the requested domain may contain multiple funklets.
  // Returns # of funklets in vector
    //##ModelId=3F86886F02BD
  int getFunklets (vector<Funklet::Ref> &funklets,const string& parmName, const Domain& domain);

  // Get the initial coefficients for the given funklet.
  // Returns the # of coefficients (0 for none)
    //##ModelId=3F86886F02C3
  int getInitCoeff (Funklet::Ref &funklet,const string& parmName);

  // Put the coefficients for the given funklet and domain.
  // Returns the DbId of the funklet.
  // If domain_is_key, checks that domain is unique
    //##ModelId=3F86886F02C8
  Funklet::DbId putCoeff (const string& parmName, const Funklet& funklet,bool domain_is_key=false);
  
  
  // Get the name of the CasaParmTable.
    //##ModelId=3F95060D0388
  const string& name() const
    { return itsTable.tableName(); }

  // Lock the parm table (for write).
  void lock();

  // Unlock the parm table.
  void unlock();
  
  // Flush the parm table.
  void flush ();

private:
  Thread::Mutex::Lock constructor_lock;
    
  // Find the table subset containing the parameter values for the
  // requested domain.
    //##ModelId=3F86886F02CE
  casa::Table find (const string& parmName, const Domain& domain);

    //##ModelId=3F86886F0297
  casa::Table                        itsTable;
    //##ModelId=3F86886F029C
  casa::ColumnsIndex                 itsIndex;
    //##ModelId=3F86886F02A1
  casa::RecordFieldPtr<casa::String> itsIndexName;
    //##ModelId=3F86886F02A6
  casa::Table                        itsInitTable;
    //##ModelId=3F86886F02AB
  casa::ColumnsIndex*                itsInitIndex;
    //##ModelId=3F86886F02B0
  casa::RecordFieldPtr<casa::String> itsInitIndexName;


  static Thread::Mutex their_mutex_;
  
  static Thread::Mutex & theirMutex ()
  { return their_mutex_; }
  
  const string & createIfNeeded (const string& tableName,bool create);
};


} // namespace Meq

#endif
#endif

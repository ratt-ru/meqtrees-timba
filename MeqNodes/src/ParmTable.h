//# ParmTable.h: Object to hold parameters in a table.
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

#ifndef MEQ_PARMTABLE_H
#define MEQ_PARMTABLE_H

//# Includes
#include <tables/Tables/Table.h>
#include <tables/Tables/ColumnsIndex.h>
#include <casa/Containers/RecordField.h>
#include <MEQ/Funklet.h>
#include <Common/lofar_vector.h>
#include <Common/Thread/Mutex.h>
#include <map>


namespace Meq {

//# Forward Declarations
class Domain;


//##ModelId=3F86886E01E4
class ParmTable
{
public:
    //##ModelId=3F86886F02B7
  explicit ParmTable (const string& tableName);

    //##ModelId=3F86886F02BC
  ~ParmTable();

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
  Funklet::DbId putCoeff (const string& parmName, const Funklet& funklet,bool domain_is_key=true);
  
  // Put the coefficients for the given funklet and domain.
  // If a new DbId is allocated, stores it in the funklet.
  // If domain_is_key, checks that domain is unique.
  void putCoeff1 (const string& parmName,Funklet& funklet,bool domain_is_key=true);

  // Return point sources for the given source numbers.
  // An empty sourceNr vector means all sources.
  // In the 2nd version the pointers to the created Parm objects
  // are added to the vector of objects to be deleted.
  //  MeqSourceList getPointSources (const Vector<int>& sourceNrs);
  //  MeqSourceList getPointSources (const Vector<int>& sourceNrs,
  //				 vector<MeqExpr*>& exprDel);

  // Get the name of the ParmTable.
    //##ModelId=3F95060D0388
  const string& name() const
    { return itsTable.tableName(); }

  // Lock the parm table (for write).
  void lock();

  // Unlock the parm table.
  void unlock();

  // Open the table if not opened yet. If opened, it is added to the map.
    //##ModelId=3F95060D033E
  static ParmTable* openTable (const String& tableName);

  // Create a new table.
    //##ModelId=400E535402E7
  static void createTable (const String& tableName);

  // Close all tables in the map. All ParmTable objects are deleted.
    //##ModelId=3F95060D0372
  static void closeTables();

  // Lock all tables for write.
  static void lockTables();

  // Unlock all tables.
  static void unlockTables();

private:
  Thread::Mutex::Lock constructor_lock;
    
  // Find the table subset containing the parameter values for the
  // requested domain.
    //##ModelId=3F86886F02CE
  Table find (const string& parmName, const Domain& domain);

    //##ModelId=3F86886F0297
  Table                  itsTable;
    //##ModelId=3F86886F029C
  ColumnsIndex           itsIndex;
    //##ModelId=3F86886F02A1
  RecordFieldPtr<String> itsIndexName;
    //##ModelId=3F86886F02A6
  Table                  itsInitTable;
    //##ModelId=3F86886F02AB
  ColumnsIndex*          itsInitIndex;
    //##ModelId=3F86886F02B0
  RecordFieldPtr<String> itsInitIndexName;

    //##ModelId=3F95060D031A
  static std::map<string, ParmTable*> theirTables;
  
  static Thread::Mutex   theirMutex;
};


} // namespace Meq

#endif

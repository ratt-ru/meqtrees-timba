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

#ifndef MEQNODES_PARMTABLEUTILS_H
#define MEQNODES_PARMTABLEUTILS_H

#include <MEQ/ParmTable.h>
#include <map>

//# Includes
namespace Meq {

//##ModelId=3F86886E01E4
class ParmTableUtils
{
public:
  // Open the table if not opened yet. If opened, it is added to the map.
  // The type of the table to open is determined by the name/type argument
    //##ModelId=3F95060D033E
  static ParmTable* openTable (const string & tableName,int type=0);

  // Close all tables in the map. All ParmTable objects are deleted.
    //##ModelId=3F95060D0372
  static void closeTables();

  // Lock all tables for write.
  static void lockTables();

  // Unlock all tables.
  static void unlockTables();
  
  // Flush all tables.
  static void flushTables();

private:
  static std::map<string, ParmTable*> open_tables_;
  
  static Thread::Mutex static_table_mutex_;
};


} // namespace Meq

#endif

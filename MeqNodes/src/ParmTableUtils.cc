///# ParmTable.cc: static parts of asbtract ParmTable class
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
//# $Id: ParmTable.cc 5418 2007-07-19 16:49:13Z oms $

#ifndef HAVE_PARMDB

#include <MeqNodes/ParmTableUtils.h>
#include <MeqNodes/CasaParmTable.h>
#include <MEQ/FastParmTable.h>

namespace Meq {

Thread::Mutex ParmTableUtils::static_table_mutex_;
std::map<string, ParmTable*> ParmTableUtils::open_tables_;

//##ModelId=3F95060D033E
ParmTable* ParmTableUtils::openTable (const string& tablename,int type)
{
  Thread::Mutex::Lock lock(static_table_mutex_);
  std::map<string,ParmTable*>::const_iterator p = open_tables_.find(tablename);
  if (p != open_tables_.end()) {
    return p->second;
  }
  // determine type of table to open
  int len = tablename.length();
#ifdef HAVE_FASTPARMTABLE
  ParmTable *tab;
  if( len>5 && !tablename.compare(len-4,4,".mep") || 
      !tablename.compare(len-5,5,".mep/") )
    tab = new CasaParmTable(tablename);
  else
    tab = new FastParmTable(tablename);
#else
  ParmTable *tab = new CasaParmTable(tablename);
#endif
  open_tables_[tablename] = tab;
  return tab;
}

//##ModelId=3F95060D0372
void ParmTableUtils::closeTables()
{
  Thread::Mutex::Lock lock(static_table_mutex_);
  for (std::map<string,ParmTable*>::const_iterator iter = open_tables_.begin();
       iter != open_tables_.end();
       ++iter) {
    delete iter->second;
  }
  open_tables_.clear();
}

void ParmTableUtils::lockTables()
{
  Thread::Mutex::Lock lock(static_table_mutex_);
  for (std::map<string,ParmTable*>::const_iterator iter = open_tables_.begin();
       iter != open_tables_.end();
       ++iter) {
    iter->second->lock();
  }
}

void ParmTableUtils::unlockTables()
{
  Thread::Mutex::Lock lock(static_table_mutex_);
  for (std::map<string,ParmTable*>::const_iterator iter = open_tables_.begin();
       iter != open_tables_.end();
       ++iter) {
    iter->second->unlock();
  }
}

void ParmTableUtils::flushTables()
{
  Thread::Mutex::Lock lock(static_table_mutex_);
  for (std::map<string,ParmTable*>::const_iterator iter = open_tables_.begin();
       iter != open_tables_.end();
       ++iter) {
    iter->second->flush();
  }
}

} // namespace Meq

#endif

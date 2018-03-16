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

#ifndef MEQNODES_FASTPARMTABLE_H
#define MEQNODES_FASTPARMTABLE_H

#include <config.h>

#ifdef HAVE_QDBM
  #define HAVE_FASTPARMTABLE 1
  #include <qdbm/depot.h>
#endif

#ifdef HAVE_FASTPARMTABLE 

#include <MEQ/ParmTable.h>

namespace Meq {

//##ModelId=3F86886E01E4
class FastParmTable : public ParmTable
{
public:
  // this is a binary structure used to represent a domain in the domain index
  class DomainEntry
  {
    public:
      DomainEntry ();
      DomainEntry (const Domain &dom);
      
      // returns True if domains match
      bool match (const Domain &dom) const;
      
      // returns True if dom overlaps self
      bool overlaps (const Domain &dom) const;
      
      // makes a Meq::Domain object from the domain entry, attaches to ref
      const Domain & makeDomain (Domain::Ref &domref) const;
      
    private:
      bool   defined[Axis::MaxAxis];
      double start[Axis::MaxAxis];
      double end[Axis::MaxAxis];
  };
  typedef std::vector<DomainEntry> DomainList;
  typedef std::vector<Domain::Ref> DomainObjectList;
  typedef struct { char *dptr; int dsize; } datum;
  
    //##ModelId=3F86886F02B7
  explicit FastParmTable (const string& tableName,bool write=false,bool create_new=false);

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

  void flush ();

// helper methods
  int getFunklet (Funklet::Ref &ref,const string& parmName,int domain_id);
  
  void deleteFunklet (const string &parmName,int domain_id);
  void deleteAllFunklets (const string &parmName);
  
  const DomainList & domainList () const
  { return domain_list_; }
  
// this iterates over funklets in the database
// call this first to initiazize the iterator.
  bool firstFunklet (string &name,int &domain_index);
// and call this to get the net funklet name and domain index.
// Return values is false once the list of funklets has been exhausted.
// Note that iteration is not thread-safe, so get a lock on the mutex first.
  bool nextFunklet (string &name,int &domain_index);
  
  // exposes mutex
  Thread::Mutex & mutex ()
  { return mutex_; }
  
private:

  std::string table_name_;
  Thread::Mutex mutex_;
  
  bool writing_;
  
  std::string domains_file_;
  std::string funklets_file_;
  
  FILE *fdomains_;
  DEPOT *fdb_;
  
  // list of known domains
  DomainList domain_list_;
  DomainObjectList domain_ref_list_;
  std::vector<bool>        domain_match_;
  

  // this is used by first/nextFunklet
  datum prev_key;
  bool dpiter_initialized_;
  
  // reopens table for writing, if it's not open for writing yet
  void openForWriting ();
  
  // internal function, gets funklet with given DB key
  int getFunklet (Funklet::Ref &ref,const char *kbuf,int ksiz,int domain_index);
  
  // helper function, returns DB key size, given a parmname
  int keySize (const string &name)
  { return sizeof(int)+name.length()+1; }
  // forms up key from name and domain index. Key must point to a buffer
  // of at least keySize() length
  void makeKey (char *key,const string &name,int domain_index);
  
  // helper functions to throw an error (from errno or Depot)
  void throwErrno (const string &message);
  void throwDepot (const string &message);
  

};


} // namespace Meq

#endif // HAVE_FASTPARMTABLE

#endif

///# FastParmTable.cc: Object to hold parameters in a table.
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
//# $Id: CasaParmTable.cc 5418 2007-07-19 16:49:13Z oms $

#include <MEQ/FastParmTable.h>
#include <MEQ/Polc.h>

#ifdef HAVE_FASTPARMTABLE

#include <TimBase/Debug.h>
#include <DMI/BlockSet.h>
#include <DMI/DynamicTypeManager.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <errno.h>

namespace Meq 
{

FastParmTable::FastParmTable (const string& tablename,bool)
 : table_name_ (tablename),fdomains_(0),fdb_(0)
{
  prev_key.dptr = 0;
  struct stat stat_buf;
  // check if directory exists, if it doesn't, then try to create it
  if( stat(tablename.c_str(),&stat_buf) < 0)
  {
    // only try to create if error is "no such entry", else report error
    if( errno != ENOENT )
      throwErrno("can't open '%s'");
    if( mkdir(tablename.c_str(),0777) < 0 )
      throwErrno("can't create '%s'");
  }
  // create/open domain list file
  fdomains_ = fopen((tablename+"/domains").c_str(),"a+b");
  if( !fdomains_ )
    throwErrno("can't open '%s/domains'");
  // see how many domains we've got based on filesize
  if( fstat(fileno(fdomains_),&stat_buf)<0 )
    throwErrno("can't stat '%s/domains'");
  int ndom = stat_buf.st_size/sizeof(DomainEntry);
  domain_list_.reserve((ndom/1024+1)*1024);
  domain_ref_list_.reserve((ndom/1024+1)*1024);
  domain_list_.resize(ndom);
  domain_ref_list_.resize(ndom);
  // read them in
  if( ndom )
  {
    if( fread(&(domain_list_[0]),sizeof(DomainEntry),ndom,fdomains_) != uint(ndom) )
      Throw("error reading '%s/domains'");
  }
  dprintf(1)("read %d domains\n",ndom);
  // just in case, seek to new domain position
  fseek(fdomains_,ndom*sizeof(DomainEntry),SEEK_SET);
  // create/open funklet database
  fdb_ = gdbm_open(const_cast<char*>((tablename+"/funklets").c_str()),
                    1024,GDBM_WRCREAT,0666,0);
  // "bad magic number" indicates corruption from previous run, so flush it
  if( !fdb_ && gdbm_errno == GDBM_BAD_MAGIC_NUMBER )
  {
    cerr<<"Warning: "<<tablename<<" appears to be corrupt. This may be due to the system crashing or being killed during a previous run. Creating a new, empty table.\n";
    fdb_ = gdbm_open(const_cast<char*>((tablename+"/funklets").c_str()),
                     1024,GDBM_NEWDB,0666,0);
  }
  // still an error? report as exception
  if( !fdb_ )
  {
    fclose(fdomains_);
    throwGdbm("can't open '%s/funklets'");
  }
}

FastParmTable::~FastParmTable()
{
  if( fdomains_ )
    fclose(fdomains_);
  if( fdb_ )
    gdbm_close(fdb_);
  if( prev_key.dptr )
    free(prev_key.dptr);
}

void FastParmTable::flush ()
{
  Thread::Mutex::Lock lock(mutex_);
  if( fdomains_ )
    fflush(fdomains_);
  if( fdb_ )
    gdbm_sync(fdb_);
}

void FastParmTable::throwErrno (const string &message)
{
  int errno0 = errno;
  char errbuf[256];
  char *err = strerror_r(errno0,errbuf,sizeof(errbuf));
  Throw(Debug::ssprintf("%s: %s (errno=%d)",
        Debug::ssprintf(message.c_str(),table_name_.c_str()).c_str(),err,errno0));
}

void FastParmTable::throwGdbm (const string &message)
{
  Throw(Debug::ssprintf("%s: %s (gdbm_errno=%d)",
        Debug::ssprintf(message.c_str(),table_name_.c_str()).c_str(),gdbm_strerror(gdbm_errno),gdbm_errno));
}


void FastParmTable::makeKey (char *key,const string& name,int domain_index)
{
  int *key_dom = reinterpret_cast<int*>(key);
  *key_dom = domain_index;
  name.copy(key+sizeof(int),name.length());
  key[keySize(name)-1] = 0;
}

int FastParmTable::getFunklet (Funklet::Ref &ref,datum db_key,int domain_index)
{
  datum db_data = gdbm_fetch(fdb_,db_key);
  if( !db_data.dptr )
  {
    // check for real errors
    if( gdbm_errno != GDBM_ITEM_NOT_FOUND )
      throwGdbm("error reading '%s/funklets'");
    // else just return 0 indicating no such funklet
    return 0;
  }
  // use a try-block to deallocate db_data.dptr on any exception
  try
  {
    // shortcut for 0-deg polcs -- only c00 is stored
    if( db_data.dsize == sizeof(double) )
    {
      double c00 = *reinterpret_cast<double*>(db_data.dptr);
      Polc *polc = new Polc(c00,defaultPolcPerturbation,defaultPolcWeight,-1);
      ref <<= polc;
      const Domain *pdom;
      if( domain_ref_list_[domain_index].valid() )
        pdom = domain_ref_list_[domain_index].deref_p();
      else
        pdom = &( domain_list_[domain_index].makeDomain(domain_ref_list_[domain_index]) );
      polc->setDomain(*pdom);
      polc->setDbId(domain_index);
      free(db_data.dptr);
      db_data.dptr = 0;
      return 1;
    }
    // generic funklet stored as blockset
    else
    {
      // make funklet from the data block
      size_t *dptr = reinterpret_cast<size_t*>(db_data.dptr);
      int nblocks = dptr[0];
      size_t *block_sizes = dptr+1;
      // check for data size sanity
      size_t totsize = sizeof(size_t)*(nblocks+1);
      if( db_data.dsize < int(totsize) )
        Throw("malformed funklet block in database");
      // check for exact size
      for( int i=0; i<nblocks; i++ )
        totsize += block_sizes[i];
      if( db_data.dsize != int(totsize) )
        Throw("malformed funklet block in database");
      // now allocate blocks and copy data to them
      char *dataptr = reinterpret_cast<char*>(block_sizes+nblocks);
      BlockSet bset;
      for( int i=0; i<nblocks; i++ )
      {
        SmartBlock *block = new SmartBlock(block_sizes[i]);
        bset.pushNew().attach(block);
        memcpy(block->data(),dataptr,block_sizes[i]);
        dataptr += block_sizes[i];
      }
      // free data buffer
      free(db_data.dptr);
      db_data.dptr = 0;
      // create funklet from blockset
      ref.copy(DynamicTypeManager::construct(0,bset));
    }
    return 1;
  }
  catch(...)
  {
    if( db_data.dptr )
      free(db_data.dptr);
    throw;
  }
  return 1;
}

int FastParmTable::getFunklet (Funklet::Ref &ref,const string& parmName,int domain_index)
{
  Thread::Mutex::Lock lock(mutex_);
  size_t keysize = keySize(parmName);
  char key[keysize];
  makeKey(key,parmName,domain_index);
  datum db_key = { key,keysize }; 
  return getFunklet(ref,db_key,domain_index);
}

int FastParmTable::getFunklets (vector<Funklet::Ref> &funklets,const string& parmName,const Domain& domain)
{
  Thread::Mutex::Lock lock(mutex_);
  dprintf(2)("getFunklets() for '%s' domain %lf,%lf %lf,%lf\n",parmName.c_str(),
                domain.start(0),domain.end(0),domain.start(1),domain.end(1));
  if( domain_list_.empty() )
    return 0;
  // build up funklet database key
  size_t keysize = keySize(parmName);
  char key[keysize];
  makeKey(key,parmName,0);
  int *key_dom = reinterpret_cast<int*>(key);
  datum db_key = { key,keysize }; 
  // find all overlapping domains in domain list, and set a flag
  // if a funklet exists for them
  domain_match_.resize(domain_list_.size());
  int nfunk = 0;
  for( uint i=0; i<domain_list_.size(); i++ )
    if( domain_list_[i].overlaps(domain) )
    {
      *key_dom = i;
      domain_match_[i] = gdbm_exists(fdb_,db_key);
      if( domain_match_[i] )
        nfunk++;
    }
    else
      domain_match_[i] = false;
  dprintf(2)("%d matching funklets found\n",nfunk);
  // ok, now load list of corresponding funklets
  if( !nfunk )
    return 0;
  funklets.resize(nfunk);
  int ifunk = 0;
  for( uint i=0; i<domain_list_.size(); i++ )
    if( domain_match_[i] )
    {
      *key_dom = i;
      getFunklet(funklets[ifunk],db_key,i);
      if( Debug(3) )
      {
        const Funklet &funk = *funklets[ifunk];
        dprintf(3)("funklet %d, c00 is %lf, domain %lf,%lf %lf,%lf\n",ifunk,
              funk.getCoeff0(),
              funk.domain().start(0),funk.domain().end(0),
              funk.domain().start(1),funk.domain().end(1));
      }
      ifunk++;
    }
  funklets.resize(ifunk);
  return ifunk;
}

Funklet::DbId FastParmTable::putCoeff (const string& parmName, const Funklet& funklet,
                                       bool)
{
  Thread::Mutex::Lock lock(mutex_);
  // search for domain in domain list
  dprintf(2)("putCoeff() for %s, c00 is %lf, domain %lf,%lf %lf,%lf\n",
        parmName.c_str(),funklet.getCoeff0(),
        funklet.domain().start(0),funklet.domain().end(0),
        funklet.domain().start(1),funklet.domain().end(1));
  const Domain &domain = funklet.domain(); 
  int dom_id = -1;
  if( !domain_list_.empty() )
  {
    // first check domain indicated by funklet's dbid
    int dbid = funklet.getDbId();
    if( dbid >= 0 && dbid < int(domain_list_.size()) && 
        domain_list_[dbid].match(domain) )
      dom_id = dbid;
    // else just look through whole list, but backwards
    // (since newer domains are likely to be towards the end)
    else
      for( int i=int(domain_list_.size())-1; i>=0; i-- )
        if( domain_list_[i].match(domain) )
        {
          dom_id = i;
          break;
        }
  }
  dprintf(2)("matched domain #%d\n",dom_id);
  // if no such domain, we have to store a new one
  if( dom_id < 0 )
  {
    dom_id = domain_list_.size();
    // make new domain entry and write it out first. If that succeeds,
    // add it to list 
    DomainEntry de(domain);
    if( fwrite(&de,sizeof(DomainEntry),1,fdomains_) != 1 )
      throwErrno("error writing to '%s/domains'");
    domain_list_.reserve((dom_id/1024+1)*1024); // keep sizing up in large chunks
    domain_list_.resize(dom_id+1);
    domain_list_[dom_id] = de;
    domain_ref_list_.reserve((dom_id/1024+1)*1024); // keep sizing up in large chunks
    domain_ref_list_.resize(dom_id+1);
    domain_ref_list_[dom_id].attach(domain);
    dprintf(2)("created new domain %d\n",dom_id);
  }
  // build up funklet database key
  size_t keysize = keySize(parmName);
  char key[keysize];
  makeKey(key,parmName,dom_id);
  datum db_key = { key,keysize }; 
  // now store the funklet
  const Polc *polc = dynamic_cast<const Polc*>(&funklet);
  // 0-degree polcs just have their c00 stored
  if( polc && polc->isConstant() )
  {
    double c00 = polc->getCoeff0();
    datum db_data = { reinterpret_cast<char*>(&c00),sizeof(c00) };
    if( gdbm_store(fdb_,db_key,db_data,GDBM_REPLACE)<0 )
      throwGdbm("error writing to '%s/funklets'");
  }
  else
  {
    BlockSet bset;
    funklet.toBlock(bset);
    // work out required size of data block
    size_t totsize = (bset.size()+1)*sizeof(size_t);
    for( BlockSet::const_iterator iter = bset.begin(); iter != bset.end(); iter++ )
      totsize += (*iter)->size();
    // allocate block
    BlockRef bref(new SmartBlock(totsize));
    // store header info (# blocks and block sizes)
    size_t *pdata = bref().pdata<size_t>();
    *pdata = bset.size();
    pdata++;
    // pdata points to start of block size array, cdata points to start of data area
    char *cdata = reinterpret_cast<char*>(pdata+bset.size());
    // fill both from the blockset
    for( BlockSet::const_iterator iter = bset.begin(); iter != bset.end(); iter++,pdata++ )
    {
      size_t sz = *pdata = (*iter)->size();
      memcpy(cdata,(*iter)->data(),sz);
      cdata += sz;
    }
    // store block in database
    // NB: this is the place to check for domain_is_key, but I won't bother just now
    datum db_data = { bref().cdata(),bref().size() };
    if( gdbm_store(fdb_,db_key,db_data,GDBM_REPLACE)<0 )
      throwGdbm("error writing to '%s/funklets'");
  }
  return dom_id; 
}

void FastParmTable::deleteFunklet (const string &parmName,int domain_index)
{
  Thread::Mutex::Lock lock(mutex_);
  size_t keysize = keySize(parmName);
  char key[keysize];
  makeKey(key,parmName,domain_index);
  datum db_key = { key,keysize };
  if( gdbm_delete(fdb_,db_key) < 0 )
    throwGdbm("error deleting funklet '"+parmName+"'");
}

void FastParmTable::deleteAllFunklets (const string &parmName)
{
  Thread::Mutex::Lock lock(mutex_);
  size_t keysize = keySize(parmName);
  char key[keysize];
  makeKey(key,parmName,0);
  datum db_key = { key,keysize };
  int *pdom = reinterpret_cast<int*>(key);
  for( int idom=0; idom<int(domain_list_.size()); idom++ )
  {
    *pdom = idom;
    if( gdbm_delete(fdb_,db_key) < 0 )
    {
      if( gdbm_errno != GDBM_ITEM_NOT_FOUND )
        throwGdbm("error deleting funklet '"+parmName+"'");
    }
  }
}

static void decomposeKey (const datum &key,string &name,int &domain_index)
{
  // decomposes a key into a funklet name and a domain index
  int *pdom = reinterpret_cast<int*>(key.dptr);
  domain_index = *pdom;
  name.assign(reinterpret_cast<char*>(pdom+1));
}

bool FastParmTable::firstFunklet (string &name,int &domain_index)
{
  Thread::Mutex::Lock lock(mutex_);
  if( prev_key.dptr )
    free(prev_key.dptr);
  // get first DB key, return false if None
  prev_key = gdbm_firstkey(fdb_);
  if( !prev_key.dptr )
    return false;
  // decompose key
  decomposeKey(prev_key,name,domain_index);
  return true;
}

// and call this to get the net funklet name and domain index.
// Return values is false once the list of funklets has been exhausted.
// Note that iteration is not thread-safe, so get a lock on the mutex first.
bool FastParmTable::nextFunklet (string &name,int &domain_index)
{
  Thread::Mutex::Lock lock(mutex_);
  FailWhen(!prev_key.dptr,"must initiate iteration with firstFunklet() before calling nextFunklet()");
  // get next key and deallocate previous
  datum key = gdbm_nextkey(fdb_,prev_key);
  if( prev_key.dptr ) 
  {
    free(prev_key.dptr);
    prev_key.dptr = 0;
  }
  if( !key.dptr )
    return false;
  prev_key = key;
  // decompose key and return true
  decomposeKey(prev_key,name,domain_index);
  return true;
}

FastParmTable::DomainEntry::DomainEntry ()
{ memset(defined,sizeof(defined),0); }

FastParmTable::DomainEntry::DomainEntry (const Domain &dom)
{
  for( int i=0; i<Axis::MaxAxis; i++ )
  {
    defined[i] = dom.isDefined(i);
    if( defined[i] )
    {
      start[i] = dom.start(i);
      end[i]   = dom.end(i);
    }
    else
      start[i] = end[i] = 0;
  }
}

// returns True if domains match
bool FastParmTable::DomainEntry::match (const Domain &dom) const
{
  for( int i=0; i<Axis::MaxAxis; i++ )
  {
    if( defined[i] != dom.isDefined(i) )
      return false;
    if( defined[i] &&
        ( fabs(start[i]-dom.start(i)) > 1e-16 ||
          fabs(end[i]-dom.end(i)) > 1e-16 ) )
      return false;
  }
  return true;
}

// returns True if self is a superset of the domain
bool FastParmTable::DomainEntry::overlaps (const Domain &dom) const
{
  for( int i=0; i<Axis::MaxAxis; i++ )
  {
    if( defined[i] && dom.isDefined(i) )
    {
      if( start[i] >= dom.end(i) ||
          end[i] <= dom.start(i)  )
        return false;
    }
  }
  return true;
}

const Domain & FastParmTable::DomainEntry::makeDomain (Domain::Ref &domref) const
{
  Domain &dom = domref <<= new Domain;
  for( int i=0; i<Axis::MaxAxis; i++ )
    if( defined[i] )
      dom.defineAxis(i,start[i],end[i]);
  return dom;
}


} // namespace Meq

#endif

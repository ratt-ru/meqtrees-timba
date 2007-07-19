//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include "VCube.h"
#include "VTile.h"

namespace VisCube 
{

//##ModelId=3DB964F4035E
VCube::ConstIterator::ConstIterator()
  : pcube(0)
{
}

VCube::ConstIterator::ConstIterator(const VCube::ConstIterator &right)
    : VTile::ConstIterator()
{
  operator =(right);
}

//##ModelId=3DB964F403C3
VCube::ConstIterator::ConstIterator (const VCube& cube,int flags)
{
  attach(cube,flags);
}

//##ModelId=3DB964F50068
VCube::ConstIterator::~ConstIterator()
{
  cubelock.release();
}


//##ModelId=3DB964F5007B
VCube::ConstIterator & VCube::ConstIterator::operator = (const VCube::ConstIterator &right)
{
  if( this != &right )
  {
    cubelock.release();
    VTile::ConstIterator::operator =(right);
    pcube = right.pcube;
#ifdef USE_THREADS
    if( pcube )
      cubelock.lock(pcube->mutex());
#endif
    cuberef = right.cuberef;
    itile = right.itile;
    icubetime = right.icubetime;
  }
  return *this;
}



//##ModelId=3DB964F500C2
void VCube::ConstIterator::attach (const VCube& cube,int flags)
{
  cubelock.release();
  cuberef.detach();
  attachCube(const_cast<VCube*>(&cube),flags|DMI::READONLY);
}

//##ModelId=3DB964F50186
void VCube::ConstIterator::reset ()
{
  attachTile(0);
}

// Additional Declarations
// helper method -- attaches base tile iter to given tile,
// or detaches it if out of tiles
//##ModelId=3DB964F5020B
bool VCube::ConstIterator::attachTile (int it)
{
  if( (itile=it) < pcube->ntiles() )
  {
    VTile::ConstIterator::attach(pcube->tiles[itile]);
    icubetime = pcube->ts_offset[itile];
    return true;
  }
  else
  {
    VTile::ConstIterator::detach();
    return false;
  }
}

//##ModelId=3DB964F5025C
void VCube::ConstIterator::attachCube (VCube *cube,int flags)
{
#ifdef USE_THREADS
  cubelock.lock(cube->mutex());
#endif
  pcube = cube;
  cuberef.attach(cube,flags);
  itile = 0;
  // attach base tile iterator to first tile 
  attachTile(0);
}

//##ModelId=3DB964F501F7
void VCube::ConstIterator::detach ()
{
  cubelock.release();
  cuberef.detach();
  pcube = 0;
}

// Class VCube::Iterator 

//##ModelId=3DB964F50306
VCube::Iterator::Iterator()
    : ConstIterator()
{
}

VCube::Iterator::Iterator(const VCube::Iterator &right)
    : VTile::ConstIterator(),ConstIterator(),VTile::Iterator()
{
  operator =(right);
}

//##ModelId=3DB964F5035C
VCube::Iterator::Iterator (VCube& cube,int flags)
    : ConstIterator()
{
  attach(cube,flags);
}

//##ModelId=3DB964F503E4
VCube::Iterator::~Iterator()
{
}


//##ModelId=3DB964F60011
VCube::Iterator & VCube::Iterator::operator=(const VCube::Iterator &right)
{
  ConstIterator::operator =(right);
  return *this;
}

//##ModelId=3DB964F60053
void VCube::Iterator::attach (VCube& cube,int flags)
{
  ConstIterator::attach(cube,flags);
}

//##ModelId=3DB964F60138
VCube::VCube()
  : regular_tiling(0)
{
}

//##ModelId=3DB964F603D0
VCube::VCube (const VCube &right, int flags, int depth, int it0, int nt)
{
  Thread::Mutex::Lock lock2(right.mutex_);
  int append_flags = flags;
  // force privatization of tiles, if appropriate flags are specified
  if( flags&DMI::DEEP || depth > 0 )
    append_flags |= DMI::DEEP;
  // call append
  append(right,it0,nt,BOTTOM,append_flags);
  // privatize header, if available and/or required
  header_ = right.header_;
  if( ( depth > 1 || flags&DMI::DEEP ) && header_.valid() )
    header_.privatize(flags,depth-2);
}

//##ModelId=3DD374F4021E
VCube::VCube (const VCube &right, int flags, int depth)
    : DMI::BObj()
{
  assign(right,flags,depth);
}


//##ModelId=3DB964F603A9
VCube::VCube (const Format::Ref &form, int nt, int tilesize)
{
  init(form,nt,tilesize);
}

//##ModelId=3DB964F60139
VCube::VCube (int nc, int nf, int nt, int tilesize)
{
  init(nc,nf,nt,tilesize);
}

//##ModelId=3DB964F60194
VCube::~VCube()
{
  Thread::Mutex::Lock lock(mutex_);
  header_.unlock();
  format_.unlock();
}


//##ModelId=3DB964F60195
VCube & VCube::operator=(const VCube &right)
{
  if( this != &right )
  {
    Thread::Mutex::Lock lock(mutex_);
    Thread::Mutex::Lock lock2(right.mutex_);
    // flush any existing data
    format_.unlock().detach();
    header_.unlock().detach();
    tiles.clear();
    assign(right,0,0);
  }
  return *this;
}

// this instantiate a copyRefContainer template (from DMI/CountedRef.h)
// used by assign()
} 
namespace DMI 
{
template
void copyRefContainer (std::deque<VisCube::VTile::Ref> &dest,
                       const std::deque<VisCube::VTile::Ref> &src,
                       int flags=0,int depth=0);
} 
namespace VisCube 
{

//##ModelId=3DD10109026A
void VCube::assign (const VCube &right,int flags,int depth)
{
  Thread::Mutex::Lock lock(mutex_);
  Thread::Mutex::Lock lock2(right.mutex_);
  // copy format and header
  format_.copy(right.format_);
  header_.copy(right.header_,flags,depth-2).lock();
  // copy tile refs at depth-1
  DMI::copyRefContainer(tiles,right.tiles,flags,depth-1);
  // copy other data
  ncorr_ = right.ncorr_;
  nfreq_ = right.nfreq_;
  // recompute indexing
  setupIndexing();
}

//##ModelId=3DB964F7002B
void VCube::init (const Format::Ref &form, int nt, int tilesize)
{
  Thread::Mutex::Lock lock(mutex_);
  format_.unlock().detach();
  header_.unlock().detach();
  tiles.resize(0);
  // copy over format
  format_.unlock().copy(form).lock();
  LoShape shape = format().shape(VTile::DATA);
  ncorr_ = shape[0];
  nfreq_ = shape[1];
  // setup initial tiles, if nt > 0
  if( nt )
  {
    // number of timeslots specified in advance, so setup the empty tiles
    int numtiles;
    if( tilesize )
    {
      FailWhen( nt%tilesize,"# of time slots must be a multiple of tile size");
      numtiles = nt/tilesize;
    }
    else // use just one tile
    {
      tilesize = nt;
      numtiles = 1;
    }
    // initialize array of empty tiles and timeslot->tile index
    ts_index.resize(nt);
    tiles.resize(numtiles);
    ts_offset.resize(numtiles);
    int islot = 0;
    for( int itile = 0; itile < numtiles; itile++ )
    {
      tiles[itile] <<= new VTile(format_,tilesize);
      ts_offset[itile] = islot;
      for( int j = 0; j < tilesize; j++ )
        ts_index[islot++] = itile;
    }
    // initialize timeslots cache
    timeslots.resize(nt);
    regular_tiling = tilesize;
  }
}

//##ModelId=3DB964F601A3
void VCube::init (int nc,int nf, int nt, int tilesize)
{
  Thread::Mutex::Lock lock(mutex_);
  // init with default format for NCxNF visibilties
  Format::Ref form(new Format);
  VTile::makeDefaultFormat(form,nc,nf);
  init(form,nt,tilesize);
}

//##ModelId=3DD1010402BE
void VCube::setTime (const LoVec_double &tm)
{
  Thread::Mutex::Lock lock(mutex_);
  // does this need to be thread-safe?
  FailWhen( tm.size() != ntime(),"vector sizes do not match");
  timeslots = tm;
  for( uint i=0; i<tiles.size(); i++ )
    tiles[i]().wtime() = timeslots( makeLoRangeWithLen(ts_offset[i],tiles[i]->ntime()) );
}

//##ModelId=3DD101050085
void VCube::setTime (int it, double tm)
{
  Thread::Mutex::Lock lock(mutex_);
  timeslots[it] = tm;
  setTileElement(&VTile::wtime,it,tm);
}

// const LoMat_fcomplex VCube::tfData (int icorr = 0,bool on_the_fly = false) const
// {
//   LoMat_fcomplex ret; 
//   return getTiledArray(on_the_fly,ret,&VTile::data); 
// }
// 
// const LoMat_int VCube::tfFlags (int icorr = 0,bool on_the_fly = false) const
// {
//   LoMat_fcomplex ret; 
//   return getTiledArray(ret,&VTile::data); 
// }
// 

//##ModelId=3DD10105036C
LoMat_fcomplex VCube::tfData (int icorr)
{
  Thread::Mutex::Lock lock(mutex_);
  if( !tiles.size() )
    return LoMat_fcomplex();
  else if( tiles.size() > 1 )
    consolidate();
  return tiles[0]().tf_data(icorr);
}
    
//##ModelId=3DD101070096
LoMat_int VCube::tfFlags (int icorr)
{
  Thread::Mutex::Lock lock(mutex_);
  if( !tiles.size() )
    return LoMat_int();
  else if( tiles.size() > 1 )
    consolidate();
  return tiles[0]().tf_flags(icorr);
}

//##ModelId=3DB964F602F0
void VCube::consolidate () const
{
  Thread::Mutex::Lock lock(mutex_);
  // consolidates all tiles into a single tile
  if( tiles.size()<1 )
    return;
  dprintf(2)("consolidating");
  // allocate new tile to hold whole cube
  VTile *newtile = new VTile(format_,ntime());
  VTile::Ref ref(newtile);
  // copy existing tiles into it
  for( int i=0; i<ntiles(); i++ )
    newtile->copy(ts_offset[i],*tiles[i]);
  // readjust all internal  indices
  tiles.resize(1);
  tiles[0] = ref;
  ts_offset.resize(1);
  ts_offset[0] = 0;
  ts_index.assign(ntime(),0);
}

//##ModelId=3DB964F602F2
void VCube::pop (int nt, int where)
{
  Thread::Mutex::Lock lock(mutex_);
  FailWhen(!initialized(),"uninitialized cube");
  if( !nt )
    return;
  FailWhen(nt<0 || nt>ntime(),"illegal number of timeslots");
  // removes slice of NT timeslots from the top or bottom of the cube
  while( nt && tiles.size() )
  {
    VTile::Ref &ref = (where == TOP ? tiles.front() : tiles.back());
    int tilesize = ref->ntime();
    if( tilesize <= nt ) // tile smaller than remaining slice -- just pop it
    {
      where == TOP ? tiles.pop_front() : tiles.pop_back();
      nt -= tilesize;
    }
    else // tile larger -- form new tile with remaining slots
    {
      VTile::Ref newtile(new VTile);
      if( where == TOP )
        newtile().copy(*ref,tilesize-nt);
      else
        newtile().copy(*ref,0,nt);
      ref = newtile;
      nt = 0;
    }
  }
  setupIndexing();
}

//##ModelId=3DB964F6030C
void VCube::append (const VCube &other, int it0, int nt, int where,int flags)
{
  Thread::Mutex::Lock lock(mutex_);
  Thread::Mutex::Lock lock2(other.mutex_);
  // nt<0 (default) means copy whole other cube
  if( nt<0 )
    nt = other.ntime();
  FailWhen(it0<0 || it0+nt>other.ntime(),"illegal number of timeslots");
  // check for mutually consistent formats
  bool init_from_other = false;
  if( initialized() )
  {
    FailWhen( format() != other.format(),"cube formats do not match" );
  }
  else // or if we weren't initialized, just use the other's format
  {
    init(other.formatRef(),0);
    init_from_other = true;
  }
  // grab a ref to the other's header record if we don't have one of our own
  // <commented out for now as I'm not sure it's the right thing to do>
  //  if( !hasHeader() && other.hasHeader() )
  //    setHeader(other.headerRef());
  // return if nothing to append
  if( !nt )
    return;
  // copy NT timeslots into temporary list
  std::deque<VTile::Ref> tmptiles;
  int last = it0 + nt;
  while( it0 < last )
  {
    int nleft = last - it0;
    int itile = other.ts_index[it0];
    const VTile::Ref &ref(other.tiles[itile]);
    int tilesize = ref->ntime();
    // do we need to copy a full tile?
    if( other.ts_offset[itile] == it0 && tilesize <= nleft )
    {
      tmptiles.push_back(ref.copy(flags));
    }
    else // copy partial tile
    {
      VTile::Ref newtile(new VTile);
      int start = it0 - other.ts_offset[itile];
      int num = std::min(nleft,tilesize-start);
      newtile().copy(*ref,start,num);
      tmptiles.push_back(newtile);
    }
    it0 += tilesize;
  }
  // insert temp list at appropriate position
  tiles.insert( where == TOP ? tiles.begin() : tiles.end(),tmptiles.begin(),tmptiles.end());
  // recompute indexing
  setupIndexing();
}

//##ModelId=3DB964F60367
void VCube::push (const VTile::Ref &tileref, int where)
{
  Thread::Mutex::Lock lock(mutex_);
  // adds tile to bottom/top of cube. Tile ref is xferred.
  FailWhen( !initialized(),"cube not initialized");
  FailWhen( format() != tileref->format(),"tile format does not match" );
  if( where == TOP )
    tiles.push_front(tileref);
  else
    tiles.push_back(tileref);
  setupIndexing();
  
// other version of push(cube) commented out:
//
//   // concatenates other cube to bottom/top of this cube
//   if( initialized() )
//     append(other,0,-1,where);
//   else // if not initialized, then equivalent to assignment
//     operator = (other);
}



//##ModelId=3DB964F60382
void VCube::grow (int nt, int tilesize, int where)
{
  // adds NT timeslots at bottom/top of cube
  // If tilesize>0 is specified, uses NT/tilesize tiles.
  // If tilesize=0 and cube is homogenously tiled, uses the cube tilesize,
  // if not, then uses just one tile.
  // If NT is not a multiple of the tilesize, a shorter end tile will be added
  Thread::Mutex::Lock lock(mutex_);
  FailWhen(!initialized(),"cube not initialized");
  // figure out the right tilesize
  if( !tilesize )
  {
    if( tiles.size() && regular_tiling )
      tilesize = regular_tiling;
    else
      tilesize = nt; // 
  }
  // add tiles one by one
  while( nt )
  {
    int sz = std::min(nt,tilesize);
    VTile::Ref ref(new VTile(format_,tilesize));
    if( where == TOP )
      tiles.push_front(ref);
    else
      tiles.push_back(ref);
    nt -= sz;
  }
  // recompute indexing
  setupIndexing();
}

// Additional Declarations
//##ModelId=3DB964F70078
int VCube::toBlock (BlockSet& set) const
{
  Thread::Mutex::Lock lock(mutex_);
  int bc = 1;
  // push out header block (filled below)
  SmartBlock *pb = new SmartBlock(sizeof(Header));
  set.push(BlockRef(pb));
  // convert format first
  if( format_.valid() )
    bc += format_->toBlock(set);
  // convert tiles
  for( CTI iter = tiles.begin(); iter != tiles.end(); iter++ )
    bc += (*iter).deref().toBlock(set);
  // convert header record, if any
  if( header_.valid() )
    bc += header_->toBlock(set);
  // fill header block
  HeaderBlock *hdr = pb->pdata<HeaderBlock>();
  BObj::fillHeader(hdr,bc);
  hdr->ntiles = tiles.size();
  hdr->hasformat = format_.valid();
  hdr->hasheader = header_.valid();
  return bc;
}

//##ModelId=3DB964F70086
int VCube::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock lock(mutex_);
  int bc = 1;
  format_.unlock().detach();
  header_.unlock().detach();
  tiles.resize(0);
  // get header block
  FailWhen( set.empty(),"invalid set" );
  BlockRef hdrblock = set.pop();
  FailWhen( hdrblock->size() != sizeof(HeaderBlock),"invalid header block" );
  const HeaderBlock * phdr = hdrblock->pdata<HeaderBlock>();
  int expect_bc = BObj::checkHeader(phdr);
  // get format [if available] 
  if( phdr->hasformat )
  {
    format_ <<= new Format;
    bc += format_().fromBlock(set);
    format_.lock();
    // get the shape out
    LoShape shape = format().shape(VTile::DATA);
    ncorr_ = shape[0];
    nfreq_ = shape[1];
  }
  // now, convert the tiles
  tiles.resize(phdr->ntiles);
  for( TI iter = tiles.begin(); iter != tiles.end(); iter++ )
  {
    VTile *ptile = new VTile;
    (*iter) <<= ptile;
    bc += ptile->fromBlock(set);
    if( phdr->hasformat )
      ptile->applyFormat(format_);
  }
  // get header [if available]
  if( phdr->hasheader )
  {
    header_ <<= new DMI::Record;
    bc += header_().fromBlock(set);
  }
  // recompute indexing
  setupIndexing();
  FailWhen(bc!=expect_bc,"block count mismatch in header");
  return bc;
}

//##ModelId=3DB964F700AF
CountedRefTarget * VCube::clone (int flags,int depth) const
{
  return new VCube(*this,flags,depth);
}

//##ModelId=3DD1010A0340
void VCube::setupIndexing ()
{
  int nslots=0;
  // count total # of timeslots
  for( CTI iter = tiles.begin(); iter != tiles.end(); iter++ )
    nslots += (*iter)->ntime();
  timeslots.resize(nslots);
  ts_index.resize(nslots);
  ts_offset.resize(tiles.size());
  // setup index vectors
  int islot = 0;
  regular_tiling = -1;
  for( uint itile=0; itile<tiles.size(); itile++ )
  {
    ts_offset[itile] = islot;
    LoVec_double tms = tiles[itile]().time();
    int sz = tms.size();
    timeslots( makeLoRangeWithLen(islot,sz) ) = tms;
    for( int j=0; j<sz; j++,islot++ )
      ts_index[islot] = itile;
    // check for regular tiling
    if( regular_tiling < 0 )
      regular_tiling = sz;
    else if( sz != regular_tiling )
      regular_tiling = 0;
  }
}

#ifdef LORRAYS_USE_BLITZ

// Templated helper method for on-the-fly concatenation of columns
// This uses blitz-specific features
template<class T,int N>
blitz::Array<T,N> & VCube::getTiledArray( blitz::Array<T,N> &cache,
    blitz::Array<T,N> & (VTile::*accessor)() ) 
{
  Thread::Mutex::Lock lock(mutex_);
  if( !tiles.size() ) // no tiles? init & return empty cache
  {
    cache.free();
    return cache;
  }
  else if( tiles.size() > 1 )
  {
    consolidate();
  }
  return (tiles[0].dewr().*accessor)();
}

// Templated helper method for const column accessors
// Does consolidation or on-the-fly concatenation of columns
// This uses blitz-specific features
template<class T,int N>
const blitz::Array<T,N> & VCube::getTiledArray( bool on_the_fly,
    blitz::Array<T,N> &cache,
    const blitz::Array<T,N> & (VTile::*accessor)() const ) const
{
  Thread::Mutex::Lock lock(mutex_);
  
  using blitz::Array;
  using blitz::TinyVector;
  using blitz::RectDomain;
  
  if( !tiles.size() ) // no tiles? init & return empty cache
  {
    cache.free();
    return cache;
  }
  else if( tiles.size() > 1 )
  {
    // create consolidated array on-the-fly, using cache object
    if( on_the_fly )
    {
      // get basic shape, plus upper and lower bounds, from first tile
      const Array<T,N> &atile0 = (tiles.front().deref().*accessor)();
      TinyVector<int,N> 
          lbound = atile0.lbound(), // lower bound of destination
          ubound = atile0.ubound(), // upper bound of destination
          shape  = atile0.shape();
      // extend time axis and resize the cached array
      shape[N-1] = ntime();
      cache.free();         // just in case,, clear out any old data
      cache.resize(shape);
      // copy over tiles one by one
      for( CTI iter = tiles.begin(); iter != tiles.end(); iter++ )
      {
        const Array<T,N> &atile = ((*iter).deref().*accessor)();
        int nt = atile.extent(N-1);
        cache(RectDomain<N>(lbound,ubound)) = atile;
        lbound[N-1] += nt;
        ubound[N-1] += nt; 
      }
      return cache;
    }
    // else consolidate the cube
    consolidate();
  }
  // we now have exactly one tile
  return (tiles[0].deref().*accessor)();
}

// instantiate the helper methods for all required combinations of
// column type and dimensionality

#define instantiate(T,N) \
  template \
blitz::Array<T,N> & VCube::getTiledArray (blitz::Array<T,N> &cache, \
    blitz::Array<T,N> & (VTile::*accessor)() ); \
template \
const blitz::Array<T,N> & VCube::getTiledArray (bool on_the_fly, \
    blitz::Array<T,N> &cache, \
    const blitz::Array<T,N> & (VTile::*accessor)() const ) const; 

instantiate(int,1);
instantiate(float,1);
instantiate(double,1);
instantiate(double,2);
instantiate(fcomplex,3);
instantiate(int,3);
#undef instantiate

#else
#error VCube no longer supports AIPS++ arrays
#endif

//##ModelId=3DF9FDD001AB
string VCube::sdebug ( int detail,const string &prefix,const char *name ) const
{
  Thread::Mutex::Lock lock(mutex_);
  
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"VCube",this);
  }
  if( detail >= 1 || detail == -1 )
  {
    if( initialized() )
    {
      appendf(out,"%dx%dx%d, %d tiles",ncorr(),nfreq(),ntime(),ntiles()); 
      if( abs(detail) == 1 )
      {
        append(out,"format: "+format().sdebug(-1));
        append(out,hasHeader()?"w/hdr":"no hdr");
      }
    }
    else
      append(out,"uninit");
  }
  if( detail >= 2 || detail <= -2 )
  {
    if( initialized() )
    {
      append(out,"format: "+format().sdebug(-2));
      out += "\n    " + prefix + header_.sdebug(abs(detail)-1,prefix,"DMI::Record::Ref");
      for( uint i=0; i<tiles.size(); i++ )
        out += "\n    " + prefix + tiles[i].sdebug(abs(detail)-1,prefix,"VTile::Ref");
    }
  }
  return out;
}


//##ModelId=3DF9FDCD02BB
string VCube::ConstIterator::sdebug ( int detail,const string &prefix,const char *name ) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"CI:VCube",this);
  }
  if( detail >= 1 || detail <= -1 )
  {
    if( pcube )
    {
      appendf(out,"@tile %d/%d",itile,pcube->ntiles());
      append(out,VTile::ConstIterator::sdebug(-1,prefix));
      appendf(out,"of %s",pcube->sdebug(abs(detail)).c_str());
    }
    else
      append(out,"no cube");
    if( ptile && abs(detail) == 1 )
      append(out,cuberef.valid() ? "(ref)" : "(no ref)" );
  }
  if( detail >= 2 || detail <= -2 )
  {
    if( tileref.valid() )
      append(out,"("+cuberef.sdebug(1,"","VCube::Ref")+")");
    else
      append(out,"(no ref)");
  }
  return out;
}

};

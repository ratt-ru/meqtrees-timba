#include "VisCube/VisCube.h"

//##ModelId=3DB964F4035E
VisCube::ConstIterator::ConstIterator()
  : pcube(0)
{
}

VisCube::ConstIterator::ConstIterator(const VisCube::ConstIterator &right)
    : VisTile::ConstIterator()
{
  operator =(right);
}

//##ModelId=3DB964F403C3
VisCube::ConstIterator::ConstIterator (const VisCube& cube)
{
  attach(cube);
}

//##ModelId=3DB964F50021
VisCube::ConstIterator::ConstIterator (const VisCubeRef &ref)
{
  attach(ref);
}


//##ModelId=3DB964F50068
VisCube::ConstIterator::~ConstIterator()
{
  cubelock.release();
}


//##ModelId=3DB964F5007B
VisCube::ConstIterator & VisCube::ConstIterator::operator = (const VisCube::ConstIterator &right)
{
  if( this != &right )
  {
    cubelock.release();
    VisTile::ConstIterator::operator =(right);
    pcube = right.pcube;
#ifdef USE_THREADS
    if( pcube )
      cubelock.lock(pcube->mutex());
#endif
    if( right.cuberef.valid() )
      cuberef.copy(right.cuberef,DMI::READONLY);
    itile = right.itile;
    icubetime = right.icubetime;
  }
  return *this;
}



//##ModelId=3DB964F500C2
void VisCube::ConstIterator::attach (const VisCube& cube)
{
  cubelock.release();
  cuberef.detach();
  attachCube(const_cast<VisCube*>(&cube));
}

//##ModelId=3DB964F50115
void VisCube::ConstIterator::attach (const VisCubeRef &ref)
{
  cubelock.release();
  cuberef.copy(ref,DMI::READONLY);
  attachCube(const_cast<VisCube*>(ref.deref_p()));
}

//##ModelId=3DB964F50186
void VisCube::ConstIterator::reset ()
{
  attachTile(0);
}

// Additional Declarations
// helper method -- attaches base tile iter to given tile,
// or detaches it if out of tiles
//##ModelId=3DB964F5020B
bool VisCube::ConstIterator::attachTile (int it)
{
  if( (itile=it) < pcube->ntiles() )
  {
    VisTile::ConstIterator::attach(pcube->tiles[itile]);
    icubetime = pcube->ts_offset[itile];
    return True;
  }
  else
  {
    VisTile::ConstIterator::detach();
    return False;
  }
}

//##ModelId=3DB964F5025C
void VisCube::ConstIterator::attachCube (VisCube *cube)
{
#ifdef USE_THREADS
  cubelock.lock(cube->mutex());
#endif
  pcube = cube;
  itile = 0;
  // attach base tile iterator to first tile 
  attachTile(0);
}

//##ModelId=3DB964F501F7
void VisCube::ConstIterator::detach ()
{
  cubelock.release();
  cuberef.detach();
  pcube = 0;
}

// Class VisCube::Iterator 

//##ModelId=3DB964F50306
VisCube::Iterator::Iterator()
    : ConstIterator()
{
}

VisCube::Iterator::Iterator(const VisCube::Iterator &right)
    : VisTile::ConstIterator(),ConstIterator(),VisTile::Iterator()
{
  operator =(right);
}

//##ModelId=3DB964F5035C
VisCube::Iterator::Iterator (VisCube& cube)
    : ConstIterator()
{
  attach(cube);
}

//##ModelId=3DB964F503A1
VisCube::Iterator::Iterator (const VisCubeRef &ref)
    : ConstIterator()
{
  attach(ref);
}


//##ModelId=3DB964F503E4
VisCube::Iterator::~Iterator()
{
}


//##ModelId=3DB964F60011
VisCube::Iterator & VisCube::Iterator::operator=(const VisCube::Iterator &right)
{
  ConstIterator::operator =(right);
  return *this;
}

//##ModelId=3DB964F60053
void VisCube::Iterator::attach (VisCube& cube)
{
  FailWhen( !cube.isWritable(),"cube not writable" );
  ConstIterator::attach(cube);
}

//##ModelId=3DB964F60099
void VisCube::Iterator::attach (const VisCubeRef &ref)
{
  FailWhen( !ref.isWritable() || !ref->isWritable(),"cube not writable" );
  ConstIterator::attach(ref);
}


//##ModelId=3DB964F60138
VisCube::VisCube()
  : writable_(True),regular_tiling(0)
{
}

//##ModelId=3DB964F603D0
VisCube::VisCube (const VisCube &right, int flags, int depth, int it0, int nt)
{
  Thread::Mutex::Lock lock2(right.mutex_);
  
  writable_ = True; // to make sure append works
  if( !right.isWritable() )
    flags = (flags&~DMI::WRITE) | DMI::READONLY;
  int append_flags = flags;
  // force privatization of tiles, if appropriate flags are specified
  if( flags&DMI::DEEP || flags&DMI::FORCE_CLONE || depth > 0 )
    append_flags |= DMI::PRIVATIZE;
  // call append
  append(right,it0,nt,BOTTOM,append_flags);
  // privatize header, if available and/or required
  if( ( depth > 1 || flags&DMI::DEEP ) && header_.valid() )
    header_.privatize(flags,depth-2);
  writable_ = right.writable_;
}

//##ModelId=3DD374F4021E
VisCube::VisCube (const VisCube &right, int flags, int depth)
    : BlockableObject()
{
  assign(right,flags,depth);
}


//##ModelId=3DB964F603A9
VisCube::VisCube (const Format::Ref &form, int nt, int tilesize)
{
  init(form,nt,tilesize);
}

//##ModelId=3DB964F60139
VisCube::VisCube (int nc, int nf, int nt, int tilesize)
{
  init(nc,nf,nt,tilesize);
}

//##ModelId=3DB964F60194
VisCube::~VisCube()
{
  Thread::Mutex::Lock lock(mutex_);
  header_.unlock();
  format_.unlock();
}


//##ModelId=3DB964F60195
VisCube & VisCube::operator=(const VisCube &right)
{
  if( this != &right )
  {
    Thread::Mutex::Lock lock(mutex_);
    // flush any existing data
    format_.unlock().detach();
    header_.unlock().detach();
    tiles.clear();
    // assign other by reference
    Thread::Mutex::Lock lock2(right.mutex_);
    writable_ = right.writable_;
    assign(right,DMI::PRESERVE_RW,0);
  }
  return *this;
}

// this instantiate a copyRefContainer template (from DMI/CountedRef.h)
// used by assign()
template
void copyRefContainer (deque<VisTile::Ref> &dest,
                       const deque<VisTile::Ref> &src,
                       int flags=DMI::PRESERVE_RW,int depth=-1);

//##ModelId=3DD10109026A
void VisCube::assign (const VisCube &right,int flags,int depth)
{
  Thread::Mutex::Lock lock(mutex_);
  Thread::Mutex::Lock lock2(right.mutex_);
  
  // read-only rhs cube implies readonly copy
  if( !right.isWritable() )
    flags = (flags&~(DMI::WRITE|DMI::PRESERVE_RW)) | DMI::READONLY;
  // format always copied as readonly
  format_.copy(right.format_,DMI::READONLY).lock();
  // copy header (force PRESERVE_RW privileges, and depth-2)
  if( right.header_.valid() )
     header_.copy(right.header_,
              (flags&~(DMI::WRITE|DMI::READONLY))|DMI::PRESERVE_RW,depth-2).lock();
  // copy tile refs at depth-1
  copyRefContainer(tiles,right.tiles,flags,depth-1);
  // copy other data
  ncorr_ = right.ncorr_;
  nfreq_ = right.nfreq_;
  // recompute indexing
  setupIndexing();
  writable_ = right.isWritable();
}

//##ModelId=3DB964F7002B
void VisCube::init (const Format::Ref &form, int nt, int tilesize)
{
  Thread::Mutex::Lock lock(mutex_);
  
  format_.unlock().detach();
  header_.unlock().detach();
  tiles.resize(0);
  writable_ = True;
  // copy over format
  format_.unlock().copy(form,DMI::READONLY).lock();
  LoShape shape = format().shape(VisTile::DATA);
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
      tiles[itile] <<= new VisTile(format_,tilesize);
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
void VisCube::init (int nc,int nf, int nt, int tilesize)
{
  // init with default format for NCxNF visibilties
  Format::Ref form(new Format,DMI::ANONWR);
  VisTile::makeDefaultFormat(form,nc,nf);
  init(form,nt,tilesize);
}

//##ModelId=3DD1010402BE
void VisCube::setTime (const LoVec_double &tm)
{
  // does this need to be thread-safe?
  FailWhen( !isWritable(),"r/w access violation" );
  FailWhen( tm.size() != ntime(),"vector sizes do not match");
  timeslots = tm;
  for( uint i=0; i<tiles.size(); i++ )
    tiles[i]().wtime() = timeslots( makeLoRangeWithLen(ts_offset[i],tiles[i]->ntime()) );
}

//##ModelId=3DD101050085
void VisCube::setTime (int it, double tm)
{
  FailWhen( !isWritable(),"r/w access violation" );
  timeslots[it] = tm;
  setTileElement(&VisTile::wtime,it,tm);
}

// const LoMat_fcomplex VisCube::tfData (int icorr = 0,bool on_the_fly = False) const
// {
//   LoMat_fcomplex ret; 
//   return getTiledArray(on_the_fly,ret,&VisTile::data); 
// }
// 
// const LoMat_int VisCube::tfFlags (int icorr = 0,bool on_the_fly = False) const
// {
//   LoMat_fcomplex ret; 
//   return getTiledArray(ret,&VisTile::data); 
// }
// 

//##ModelId=3DD10105036C
LoMat_fcomplex VisCube::tfData (int icorr)
{
  if( !tiles.size() )
    return LoMat_fcomplex();
  else if( tiles.size() > 1 )
    consolidate();
  return tiles[0].dewr().tf_data(icorr);
}
    
//##ModelId=3DD101070096
LoMat_int VisCube::tfFlags (int icorr)
{
  if( !tiles.size() )
    return LoMat_int();
  else if( tiles.size() > 1 )
    consolidate();
  return tiles[0].dewr().tf_flags(icorr);
}

//##ModelId=3DB964F602F0
void VisCube::consolidate () const
{
  Thread::Mutex::Lock lock(mutex_);
  // consolidates all tiles into a single tile
  if( tiles.size()<1 )
    return;
//  FailWhen( !isWritable(),"r/w access violation" );
  dprintf(2)("consolidating");
  // allocate new tile to hold whole cube
  VisTile *newtile = new VisTile(format_,ntime());
  VisTileRef ref(newtile,DMI::ANONWR);
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
void VisCube::pop (int nt, int where)
{
  Thread::Mutex::Lock lock(mutex_);
  FailWhen(!initialized(),"uninitialized cube");
  FailWhen(!isWritable(),"r/w access violation");
  if( !nt )
    return;
  FailWhen(nt<0 || nt>ntime(),"illegal number of timeslots");
  // removes slice of NT timeslots from the top or bottom of the cube
  while( nt && tiles.size() )
  {
    VisTileRef &ref = (where == TOP ? tiles.front() : tiles.back());
    int tilesize = ref->ntime();
    if( tilesize <= nt ) // tile smaller than remaining slice -- just pop it
    {
      where == TOP ? tiles.pop_front() : tiles.pop_back();
      nt -= tilesize;
    }
    else // tile larger -- form new tile with remaining slots
    {
      VisTileRef newtile(new VisTile,DMI::ANONWR);
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
void VisCube::append (const VisCube &other, int it0, int nt, int where,int flags)
{
  Thread::Mutex::Lock lock(mutex_);
  Thread::Mutex::Lock lock2(other.mutex_);
  FailWhen( !isWritable(),"r/w access violation" );
  // nt<0 (default) means copy whole other cube
  if( nt<0 )
    nt = other.ntime();
  FailWhen(it0<0 || it0+nt>other.ntime(),"illegal number of timeslots");
  // check for mutually consistent formats
  bool init_from_other = False;
  if( initialized() )
  {
    FailWhen( format() != other.format(),"cube formats do not match" );
  }
  else // or if we weren't initialized, just use the other's format
  {
    init(other.formatRef(),0);
    init_from_other = True;
  }
  // grab a ref to the other's header record if we don't have one of our own
  // <commented out for now as I'm not sure it's the right thing to do>
  //  if( !hasHeader() && other.hasHeader() )
  //    setHeader(other.headerRef());
  // return if nothing to append
  if( !nt )
    return;
  // copy NT timeslots into temporary list
  deque<VisTileRef> tmptiles;
  int last = it0 + nt;
  while( it0 < last )
  {
    int nleft = last - it0;
    int itile = other.ts_index[it0];
    const VisTileRef &ref(other.tiles[itile]);
    int tilesize = ref->ntime();
    // do we need to copy a full tile?
    if( other.ts_offset[itile] == it0 && tilesize <= nleft )
    {
      tmptiles.push_back(ref.copy(flags));
    }
    else // copy partial tile
    {
      VisTileRef newtile(new VisTile,DMI::ANONWR);
      int start = it0 - other.ts_offset[itile];
      int num = min(nleft,tilesize-start);
      newtile().copy(*ref,start,num);
      tmptiles.push_back(newtile);
    }
    it0 += tilesize;
  }
  // insert temp list at appropriate position
  tiles.insert( where == TOP ? tiles.begin() : tiles.end(),tmptiles.begin(),tmptiles.end());
  // recompute indexing
  setupIndexing();
  if( init_from_other )
    writable_ = other.isWritable();
}

//##ModelId=3DB964F60367
void VisCube::push (VisTileRef &tileref, int where)
{
  Thread::Mutex::Lock lock(mutex_);
  // adds tile to bottom/top of cube. Tile ref is xferred.
  FailWhen( !initialized(),"cube not initialized");
  FailWhen( !isWritable(),"r/w access violation" );
  const VisTile &tile = *tileref;
  FailWhen( format() != tile.format(),"tile format does not match" );
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
void VisCube::grow (int nt, int tilesize, int where)
{
  // adds NT timeslots at bottom/top of cube
  // If tilesize>0 is specified, uses NT/tilesize tiles.
  // If tilesize=0 and cube is homogenously tiled, uses the cube tilesize,
  // if not, then uses just one tile.
  // If NT is not a multiple of the tilesize, a shorter end tile will be added
  Thread::Mutex::Lock lock(mutex_);
  FailWhen(!initialized(),"cube not initialized");
  FailWhen( !isWritable(),"r/w access violation" );
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
    int sz = min(nt,tilesize);
    VisTileRef ref(new VisTile(format_,tilesize),DMI::ANONWR);
    if( where == TOP )
      tiles.push_front(ref);
    else
      tiles.push_back(ref);
    nt -= sz;
  }
  // recompute indexing
  setupIndexing();
}

///##ModelId=3DC271C20007
//##ModelId=3DC271C20007
void VisCube::setWritable(bool write)
{
  Thread::Mutex::Lock lock(mutex_);
  if( write == writable_ )
    return;
  // downgrades everything to read-only
  if( !write )
  {
    writable_ = False;
    if( header_.valid() )
      header_.change(DMI::READONLY);
    for( TI iter = tiles.begin(); iter != tiles.end(); iter++ )
      iter->change(DMI::READONLY);
  }
  // upgrades to read-write
  else
  {
    writable_ = True;
    // privatize header
    if( header_.valid() && !header_.isWritable() )
      header_.privatize(DMI::WRITE,0);
    // privatize tiles for writing as needed
    for( TI iter = tiles.begin(); iter != tiles.end(); iter++ )
      if( iter->isWritable() )
        iter->dewr().makeWritable();  // writable tile ref? ensure tile itself is writable
      else
        iter->privatize(DMI::WRITE|DMI::DEEP,0); // else privatize the ref
  }
}


// Additional Declarations
//##ModelId=3DB964F70078
int VisCube::toBlock (BlockSet& set) const
{
  Thread::Mutex::Lock lock(mutex_);
  int ret = 1;
  // allocate header block if none is cached
  if( !hdrblock.valid() )
    hdrblock <<= new SmartBlock(sizeof(HeaderBlock));
  else // else privatize the existing header block
    hdrblock.privatize(DMI::WRITE,0);
  HeaderBlock * phdr = hdrblock().ptr_cast<HeaderBlock>();
  // fill in header
  phdr->ntiles = tiles.size();
  phdr->hasformat = format_.valid();
  phdr->hasheader = header_.valid();
  hdrblock.change(DMI::READONLY);
  set.pushCopy(hdrblock);
  // convert format first
  if( format_.valid() )
    ret += format_->toBlock(set);
  // convert tiles
  for( CTI iter = tiles.begin(); iter != tiles.end(); iter++ )
    ret += (*iter).deref().toBlock(set);
  // convert header record, if any
  if( header_.valid() )
    ret += header_->toBlock(set);
  return ret;
}

//##ModelId=3DB964F70086
int VisCube::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock lock(mutex_);
  FailWhen( !isWritable(),"r/w access violation" );
  int ret = 1;
  format_.unlock().detach();
  header_.unlock().detach();
  tiles.resize(0);
  // get header block
  FailWhen( set.empty(),"invalid set" );
  set.pop(hdrblock);
  FailWhen( hdrblock->size() != sizeof(HeaderBlock),"invalid block" );
  const HeaderBlock * phdr = hdrblock->const_ptr_cast<HeaderBlock>();
  // get format [if available] and downgrade to readonly
  if( phdr->hasformat )
  {
    format_ <<= new Format;
    ret += format_().fromBlock(set);
    format_.lock().change(DMI::READONLY);
    // get the shape out
    LoShape shape = format().shape(VisTile::DATA);
    ncorr_ = shape[0];
    nfreq_ = shape[1];
  }
  // now, convert the tiles
  writable_ = True;
  tiles.resize(phdr->ntiles);
  for( TI iter = tiles.begin(); iter != tiles.end(); iter++ )
  {
    VisTile *ptile = new VisTile;
    (*iter) <<= ptile;
    ret += ptile->fromBlock(set);
    if( phdr->hasformat )
      ptile->applyFormat(format_);
  }
  // get header [if available]
  if( phdr->hasheader )
  {
    header_ <<= new DataRecord;
    ret += header_().fromBlock(set);
  }
  // recompute indexing
  setupIndexing();
  
  return ret;
}

//##ModelId=3DB964F70094
void VisCube::privatize (int flags,int depth)
{
  // privatizing with depth = 0 simply changes the writable property.
  // privatizing with depth = 1 privatizes tiles, but not the header.
  // privatizing with depth > 1 privatizes tiles + header (with depth-2)
  // DMI::DEEP flag is equivalent to depth > 1.
  // Note that format is never privatized since it's essentially read-only
  // (i.e., if and when the format is changed, the whole object is replaced)
  Thread::Mutex::Lock lock(mutex_);
  
  writable_ = flags&DMI::WRITE;
  
  if( depth > 0 || flags&DMI::DEEP )
  {
    for( uint itile=0; itile<tiles.size(); itile++ )
      tiles[itile].privatize(flags,depth-1);
  }
  if( (depth > 1 || flags&DMI::DEEP) && header_.valid() )
    header_.privatize(flags,depth-2);
}

//##ModelId=3DB964F700AF
CountedRefTarget * VisCube::clone (int flags,int depth) const
{
  return new VisCube(*this,flags,depth);
}

//##ModelId=3DD1010A0340
void VisCube::setupIndexing ()
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
blitz::Array<T,N> & VisCube::getTiledArray( blitz::Array<T,N> &cache,
    blitz::Array<T,N> & (VisTile::*accessor)() ) 
{
  Thread::Mutex::Lock lock(mutex_);
  FailWhen(!isWritable(),"r/w access violation");
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
const blitz::Array<T,N> & VisCube::getTiledArray( bool on_the_fly,
    blitz::Array<T,N> &cache,
    const blitz::Array<T,N> & (VisTile::*accessor)() const ) const
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
blitz::Array<T,N> & VisCube::getTiledArray (blitz::Array<T,N> &cache, \
    blitz::Array<T,N> & (VisTile::*accessor)() ); \
template \
const blitz::Array<T,N> & VisCube::getTiledArray (bool on_the_fly, \
    blitz::Array<T,N> &cache, \
    const blitz::Array<T,N> & (VisTile::*accessor)() const ) const; 

instantiate(int,1);
instantiate(float,1);
instantiate(double,1);
instantiate(double,2);
instantiate(fcomplex,3);
instantiate(int,3);
#undef instantiate

#else
#error VisCube no longer supports AIPS++ arrays
#endif

//##ModelId=3DF9FDD001AB
string VisCube::sdebug ( int detail,const string &prefix,const char *name ) const
{
  Thread::Mutex::Lock lock(mutex_);
  
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"VisCube",(int)this);
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
      out += "\n    " + prefix + header_.sdebug(abs(detail)-1,prefix,"DataRecord::Ref");
      for( uint i=0; i<tiles.size(); i++ )
        out += "\n    " + prefix + tiles[i].sdebug(abs(detail)-1,prefix,"VisTile::Ref");
    }
  }
  return out;
}


//##ModelId=3DF9FDCD02BB
string VisCube::ConstIterator::sdebug ( int detail,const string &prefix,const char *name ) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"CI:VisCube",(int)this);
  }
  if( detail >= 1 || detail <= -1 )
  {
    if( pcube )
    {
      appendf(out,"@tile %d/%d",itile,pcube->ntiles());
      append(out,VisTile::ConstIterator::sdebug(-1,prefix));
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
      append(out,"("+cuberef.sdebug(1,"","VisCube::Ref")+")");
    else
      append(out,"(no ref)");
  }
  return out;
}

// VisTile
#include "VisTile.h"
#include "AID-VisCube.h"
    
// pull in registry
static int dum = aidRegistry_VisCube ();

//##ModelId=3DB964F40176
VDSID::VDSID (int segid,int beamid,int obsid)
{
  resize(3);
  (*this)[2] = segid;
  (*this)[1] = beamid;
  (*this)[0] = obsid;
}
  
//##ModelId=3DB964F40177
VDSID::VDSID (const HIID &id)
{
  resize(3);
  (*this)[0] = id[0];
  (*this)[1] = id[1];
  (*this)[2] = id[2];
}
    
    
// Class VisTile::ConstIterator 

//##ModelId=3DB964F701E6
VisTile::ConstIterator::ConstIterator()
  : ptile(0)
{
}

VisTile::ConstIterator::ConstIterator(const VisTile::ConstIterator &right)
{
  operator =(right);
}

//##ModelId=3DB964F70241
VisTile::ConstIterator::ConstIterator (const VisTile &tile)
{
  attach(tile);
}

//##ModelId=3DB964F70288
VisTile::ConstIterator::ConstIterator (const VisTileRef &ref)
{
  attach(ref);
}

//##ModelId=3DB964F702D0
VisTile::ConstIterator & VisTile::ConstIterator::operator=(const VisTile::ConstIterator &right)
{
  if( this != &right )
  {
    tilelock.release();
    ptile = right.ptile;
#ifdef USE_THREADS
    if( ptile )
      tilelock.lock(ptile->mutex());
#endif
    if( right.tileref.valid() )
      tileref.copy(right.tileref,DMI::COPYREF|DMI::READONLY);
    ntime = right.ntime;
    itime = right.itime;
  }
  return *this;
}

//##ModelId=3DF9FDD2025D
VisTile::ConstIterator::~ConstIterator()
{
  // make sure lock is released before possibly releasing tile
  tilelock.release();
}

//##ModelId=3DB964F70322
void VisTile::ConstIterator::attach (const VisTile &tile)
{
  tileref.detach();
  ptile = const_cast<VisTile*>(&tile);
#ifdef USE_THREADS
  tilelock.lock(ptile->mutex());
#endif
  ntime = ptile->ntime();
  itime = 0;
}

//##ModelId=3DB964F70368
void VisTile::ConstIterator::attach (const VisTileRef &ref)
{
  tileref.copy(ref,DMI::READONLY);
  ptile = const_cast<VisTile*>(tileref.deref_p()); 
#ifdef USE_THREADS
  tilelock.lock(ptile->mutex());
#endif
  ntime = ptile->ntime();
  itime = 0;
}

// Additional Declarations
//##ModelId=3DB964F80132
void VisTile::ConstIterator::detach ()
{
  tilelock.release();
  ptile = 0;
  tileref.detach();
}


//##ModelId=3DB964F8019C
VisTile::Iterator::Iterator()
  : ConstIterator()
{
}

// Class VisTile::Iterator 

VisTile::Iterator::Iterator(const VisTile::Iterator &right)
  : ConstIterator()
{
  operator = (right);
}

//##ModelId=3DB964F80204
VisTile::Iterator::Iterator (VisTile &tile)
{
  attach(tile);
}

//##ModelId=3DB964F8025C
VisTile::Iterator::Iterator (const VisTileRef &ref)
{
  attach(ref);
}

//##ModelId=3DB964F8029F
VisTile::Iterator & VisTile::Iterator::operator=(const VisTile::Iterator &right)
{
  ConstIterator::operator=(right);
  return *this;
}

//##ModelId=3DB964F802EF
void VisTile::Iterator::attach (VisTile &tile)
{
  tile.makeWritable();
  ConstIterator::attach(tile);
}

//##ModelId=3DB964F80334
void VisTile::Iterator::attach (const VisTileRef &ref)
{
  FailWhen(!ref.isWritable(),"tile ref not writable" );
  ref().makeWritable();
  ConstIterator::attach(ref);
}

// Additional Declarations
//##ModelId=3DB964F900AF

// Class VisTile 

VisTile::VisTile()
  : ncorr_(0),nfreq_(0)
{
}

//##ModelId=3DB964F900B0
VisTile::VisTile (const VisTile &right, int flags,int depth)
    : ColumnarTableTile(right,flags,depth),
      ncorr_(right.ncorr_),nfreq_(right.nfreq_)
{
  // temporarily make 
  if( hasFormat() )
    initArrays();
}

//##ModelId=3DB964F900BF
VisTile::VisTile (int nc, int nf, int nt)
{
  init(nc,nf,nt);
}

//##ModelId=3DB964F900D5
VisTile::VisTile (const FormatRef &form, int nt)
{
  init(form,nt);
}

//##ModelId=3DB964F900E4
VisTile::VisTile (const VisTile &a, const VisTile &b)
  : ColumnarTableTile(a,b),
    ncorr_(a.ncorr_),nfreq_(a.nfreq_)
{
  FailWhen( ncorr() != b.ncorr() || nfreq() != b.nfreq(),
      "cannot concatenate incompatible tiles");
  if( hasFormat() )
    initArrays();
}


//##ModelId=3DB964F900F6
VisTile::~VisTile()
{
}


//##ModelId=3DB964F900F7
VisTile & VisTile::operator=(const VisTile &right)
{
  if( this != &right )
  {
    Thread::Mutex::Lock lock(mutex());  
    ColumnarTableTile::operator=(right);
    nfreq_ = right.nfreq_;
    ncorr_ = right.ncorr_;
    if( hasFormat() )
      initArrays();
  }
  return *this;
}



//##ModelId=3DB964F90100
void VisTile::makeDefaultFormat (Format &form, int nc, int nf)
{
  LoShape shape(nc,nf);
  form.init(MAXCOL);
  form.add(DATA,Tpfcomplex,shape)
      .add(TIME,Tpdouble)
      .add(INTERVAL,Tpdouble)
      .add(WEIGHT,Tpfloat)
      .add(UVW,Tpdouble,LoShape(3))
      .add(FLAGS,Tpint,shape)
      .add(ROWFLAG,Tpint)
      .add(SEQNR,Tpint);
}

// returns a static vector mapping column index to name
//##ModelId=3F98DA6F0142
const VisTile::IndexToNameMap & VisTile::getIndexToNameMap ()
{
  // singleton: initializes static mapping from number to name
  static IndexToNameMap colmap;
  static Thread::Mutex initmutex;
  static volatile bool initmap = False;
  if( !initmap )
  {
    Thread::Mutex::Lock lock(initmutex);
    if( !initmap )
    {
      colmap.resize(VisTile::MAXCOL);
      #define addToMap(type,ndim,name,id) colmap[id] = #id;
      DoForAllVisTileColumns(addToMap);
      #undef addToMap
      initmap = True;
    }
  }
  return colmap;
}

// returns a static map for column name to index
//##ModelId=3F98DA6F01B8
const VisTile::NameToIndexMap & VisTile::getNameToIndexMap ()
{
  // singleton: initializes static mapping from number to name
  static NameToIndexMap colmap;
  static Thread::Mutex initmutex;
  static volatile bool initmap = False;
  if( !initmap )
  {
    Thread::Mutex::Lock lock(initmutex);
    if( !initmap )
    {
      #define addToMap(type,ndim,name,id) colmap[#id] = id;
      DoForAllVisTileColumns(addToMap);
      #undef addToMap
      initmap = True;
    }
  }
  return colmap;
}

//##ModelId=3DB964F90117
void VisTile::init (int nc, int nf, int nt)
{
  Thread::Mutex::Lock lock(mutex());  
  FormatRef ref(new Format,DMI::ANONWR);
  makeDefaultFormat(ref.dewr(),nc,nf);
  init(ref,nt);
}

//##ModelId=3DB964F9012E
void VisTile::init (const FormatRef &form, int nt)
{
  Thread::Mutex::Lock lock(mutex());  
  LoShape shape = form->shape(DATA);
  FailWhen( shape.size() != 2 ,"Missing or misshapen DATA column in tile format");
  ColumnarTableTile::init(form,nt);
  ncorr_ = shape[0];
  nfreq_ = shape[1];
  dprintf(2)("initialized tile: %s\n",sdebug(5).c_str());
  initArrays();
}

//##ModelId=3DB964F9013E
void VisTile::reset ()
{
  Thread::Mutex::Lock lock(mutex());  
  ColumnarTableTile::reset();
  ncorr_ = nfreq_ = 0;
}

//##ModelId=3DB964F9013F
void VisTile::applyFormat (const FormatRef &form)
{
  Thread::Mutex::Lock lock(mutex());  
  ColumnarTableTile::applyFormat(form);
  initArrays();
}

//##ModelId=3DB964F90147
void VisTile::changeFormat (const FormatRef &form)
{
  Thread::Mutex::Lock lock(mutex());  
  ColumnarTableTile::changeFormat(form);
  initArrays();
}

//##ModelId=3DB964F9014F
void VisTile::copy (int it0, const VisTile &other, int other_it0, int nt)
{
  Thread::Mutex::Lock lock(mutex());  
  // did we already have a format
  bool had_format = hasFormat();
  ColumnarTableTile::copy(it0,other,other_it0,nt);
  // if a format got set up for us, reinitialize the arrays
  if( !had_format )
  {
    // since the copy succeeded, we're now guaranteed to have a format
    LoShape shape = format().shape(DATA);
    // this shouldn't happen, but just in case
    FailWhen( shape.size() != 2 ,"Missing or misshapen DATA column in tile format");
    ncorr_ = shape[0];
    nfreq_ = shape[1];
    initArrays();
  }
}

//##ModelId=3DB964F90184
void VisTile::addRows (int nr)
{
  Thread::Mutex::Lock lock(mutex());  
  ColumnarTableTile::addRows(nr);
  // if this succeeded, then we have a format
  initArrays();
}

//##ModelId=3DB964F901CD
int VisTile::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock lock(mutex());  
  int ret = ColumnarTableTile::fromBlock(set);
  if( hasFormat() )
    initArrays();
  return ret;
}

//##ModelId=3DB964F901D6
CountedRefTarget* VisTile::clone (int flags, int depth) const
{
  return new VisTile(*this,flags,depth);
}

// Additional Declarations
//##ModelId=3DB964F901F6
void VisTile::initArrays ()
{
  FailWhen(!hasFormat(),"tile format not defined");
  const Format &form = format();

// use a macro to initialize all arrays in a consistent manner
// Note that we cast away const, because the tile may be read-only.
  #define initRefArray(type,ndim,name,columnId) \
    if( form.defined(columnId) ) \
    { \
      LoShape shape = form.shape(columnId); \
      shape.push_back(ntime()); \
      name##_array_.reference(blitz::Array<type,ndim+1> \
        (static_cast<type*>(const_cast<void*>(column(columnId))),shape,blitz::neverDeleteData)); \
    } \
    else \
      name##_array_.free();

  DoForAllVisTileColumns(initRefArray);      
}

//##ModelId=3DD3C6CB02E9
string VisTile::sdebug ( int detail,const string &prefix,const char *name ) const
{
  return ColumnarTableTile::sdebug(detail,prefix,name?name:"VisTile");
}
    

//##ModelId=3DD3CB0003D0
string VisTile::ConstIterator::sdebug ( int detail,const string &prefix,const char *name ) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"CI:VisTile",(int)this);
  }
  if( detail >= 1 || detail == -1 )
  {
    if( ptile )
      appendf(out,"@ts %d/%d of %s",itime,ntime,
          ptile->sdebug(abs(detail),prefix).c_str());
    else
      append(out,"no tile");
    if( ptile && abs(detail) == 1 )
      append(out,tileref.valid() ? "(ref)" : "(no ref)" );
  }
  if( detail >= 2 || detail <= -2 )
  {
    if( tileref.valid() )
      append(out,"("+tileref.sdebug(1,"","VisTile::Ref")+")");
    else
      append(out,"(no ref)");
  }
  return out;
}


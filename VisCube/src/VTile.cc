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

#include "VTile.h"
#include "AID-VisCube.h"
    
namespace VisCube 
{

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
    
    
// Class VTile::ConstIterator 

//##ModelId=3DB964F701E6
VTile::ConstIterator::ConstIterator()
  : ptile(0)
{
}

VTile::ConstIterator::ConstIterator(const VTile::ConstIterator &right)
{
  operator =(right);
}

//##ModelId=3DB964F70241
VTile::ConstIterator::ConstIterator (const VTile &tile,int flags)
{
  attach(tile,flags);
}

//##ModelId=3DB964F702D0
VTile::ConstIterator & VTile::ConstIterator::operator=(const VTile::ConstIterator &right)
{
  if( this != &right )
  {
    tilelock.release();
    ptile = right.ptile;
#ifdef USE_THREADS
    if( ptile )
      tilelock.lock(ptile->mutex());
#endif
    tileref.copy(right.tileref);
    ntime = right.ntime;
    itime = right.itime;
  }
  return *this;
}

//##ModelId=3DF9FDD2025D
VTile::ConstIterator::~ConstIterator()
{
  // make sure lock is released before possibly releasing tile
  tilelock.release();
}

//##ModelId=3DB964F70322
void VTile::ConstIterator::attach (const VTile &tile,int flags)
{
  tileref.attach(tile,flags);
  ptile = const_cast<VTile*>(&tile);
#ifdef USE_THREADS
  tilelock.lock(ptile->mutex());
#endif
  ntime = ptile->ntime();
  itime = 0;
}

// Additional Declarations
//##ModelId=3DB964F80132
void VTile::ConstIterator::detach ()
{
  tilelock.release();
  ptile = 0;
  tileref.detach();
}


//##ModelId=3DB964F8019C
VTile::Iterator::Iterator()
  : ConstIterator()
{
}

// Class VTile::Iterator 

VTile::Iterator::Iterator(const VTile::Iterator &right)
  : ConstIterator()
{
  operator = (right);
}

//##ModelId=3DB964F80204
VTile::Iterator::Iterator (VTile &tile,int flags)
{
  attach(tile,flags);
}

//##ModelId=3DB964F8029F
VTile::Iterator & VTile::Iterator::operator=(const VTile::Iterator &right)
{
  ConstIterator::operator=(right);
  return *this;
}

//##ModelId=3DB964F802EF
void VTile::Iterator::attach (VTile &tile,int flags)
{
  tile.makeWritable();
  ConstIterator::attach(tile,flags);
}

// Additional Declarations
//##ModelId=3DB964F900AF

// Class VTile 

VTile::VTile()
  : ncorr_(0),nfreq_(0)
{
}

//##ModelId=3DB964F900B0
VTile::VTile (const VTile &right, int flags,int depth)
    : ColumnarTableTile(right,flags,depth),
      ncorr_(right.ncorr_),nfreq_(right.nfreq_)
{
  // init arrays 
  if( hasFormat() )
    initArrays();
}

//##ModelId=3DB964F900BF
VTile::VTile (int nc, int nf, int nt)
{
  init(nc,nf,nt);
}

//##ModelId=3DB964F900D5
VTile::VTile (const Format::Ref &form, int nt)
{
  init(form,nt);
}

//##ModelId=3DB964F900E4
VTile::VTile (const VTile &a, const VTile &b)
  : ColumnarTableTile(a,b),
    ncorr_(a.ncorr_),nfreq_(a.nfreq_)
{
  FailWhen( ncorr() != b.ncorr() || nfreq() != b.nfreq(),
      "cannot concatenate incompatible tiles");
  if( hasFormat() )
    initArrays();
}


//##ModelId=3DB964F900F6
VTile::~VTile()
{
}


//##ModelId=3DB964F900F7
VTile & VTile::operator=(const VTile &right)
{
  if( this != &right )
  {
    Thread::Mutex::Lock lock(mutex());  
    Thread::Mutex::Lock lock2(right.mutex());  
    ColumnarTableTile::operator=(right);
    nfreq_ = right.nfreq_;
    ncorr_ = right.ncorr_;
    if( hasFormat() )
      initArrays();
  }
  return *this;
}


//##ModelId=3DB964F90100
void VTile::makeDefaultFormat (Format &form, int nc, int nf)
{
  LoShape shape(nc,nf);
  form.init(MAXCOL);
  form.add(DATA,Tpfcomplex,shape)
      .add(TIME,Tpdouble)
      .add(INTERVAL,Tpdouble)
      .add(WEIGHT,Tpfloat,shape)
      .add(UVW,Tpdouble,LoShape(3))
      .add(FLAGS,Tpint,shape)
      .add(ROWFLAG,Tpint)
      .add(SEQNR,Tpint);
}

// returns a static vector mapping column index to name
//##ModelId=3F98DA6F0142
const VTile::IndexToNameMap & VTile::getIndexToNameMap ()
{
  // singleton: initializes static mapping from number to name
  static IndexToNameMap colmap;
  static Thread::Mutex initmutex;
  static volatile bool initmap = false;
  if( !initmap )
  {
    Thread::Mutex::Lock lock(initmutex);
    if( !initmap )
    {
      colmap.resize(VTile::MAXCOL);
      #define addToMap(type,ndim,name,id) colmap[id] = #id;
      DoForAllVTileColumns(addToMap);
      #undef addToMap
      initmap = true;
    }
  }
  return colmap;
}

// returns a static map for column name to index
//##ModelId=3F98DA6F01B8
const VTile::NameToIndexMap & VTile::getNameToIndexMap ()
{
  // singleton: initializes static mapping from number to name
  static NameToIndexMap colmap;
  static Thread::Mutex initmutex;
  static volatile bool initmap = false;
  if( !initmap )
  {
    Thread::Mutex::Lock lock(initmutex);
    if( !initmap )
    {
      #define addToMap(type,ndim,name,id) colmap[#id] = id;
      DoForAllVTileColumns(addToMap);
      #undef addToMap
      initmap = true;
    }
  }
  return colmap;
}

//##ModelId=3DB964F90117
void VTile::init (int nc, int nf, int nt)
{
  Thread::Mutex::Lock lock(mutex());  
  Format::Ref ref(new Format,DMI::ANONWR);
  makeDefaultFormat(ref.dewr(),nc,nf);
  init(ref,nt);
}

//##ModelId=3DB964F9012E
void VTile::init (const Format::Ref &form, int nt)
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
void VTile::reset ()
{
  Thread::Mutex::Lock lock(mutex());  
  ColumnarTableTile::reset();
  ncorr_ = nfreq_ = 0;
}

//##ModelId=3DB964F9013F
void VTile::applyFormat (const Format::Ref &form)
{
  Thread::Mutex::Lock lock(mutex());  
  ColumnarTableTile::applyFormat(form);
  initArrays();
}

//##ModelId=3DB964F90147
void VTile::changeFormat (const Format::Ref &form)
{
  Thread::Mutex::Lock lock(mutex());  
  ColumnarTableTile::changeFormat(form);
  initArrays();
}

//##ModelId=3DB964F9014F
void VTile::copy (int it0, const VTile &other, int other_it0, int nt)
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
void VTile::addRows (int nr)
{
  Thread::Mutex::Lock lock(mutex());  
  ColumnarTableTile::addRows(nr);
  // if this succeeded, then we have a format
  initArrays();
}

//##ModelId=3DB964F901CD
int VTile::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock lock(mutex());  
  int ret = ColumnarTableTile::fromBlock(set);
  if( hasFormat() )
  {
    LoShape shape = format().shape(DATA);
    FailWhen( shape.size() != 2 ,"Missing or misshapen DATA column in tile format");
    ncorr_ = shape[0];
    nfreq_ = shape[1];
    initArrays();
  }
  return ret;
}

//##ModelId=3DB964F901D6
CountedRefTarget* VTile::clone (int flags, int depth) const
{
  return new VTile(*this,flags,depth);
}

// Additional Declarations
//##ModelId=3DB964F901F6
void VTile::initArrays ()
{
  FailWhen(!hasFormat(),"tile format not defined");
  const Format &form = format();

// use a macro to initialize all arrays in a consistent manner
// Note that we cast away const, because the tile may be read-only; makeWritable()
// will already have ensured an only copy as needed
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

  DoForAllVTileColumns(initRefArray);      
}

//##ModelId=3DD3C6CB02E9
string VTile::sdebug ( int detail,const string &prefix,const char *name ) const
{
  return ColumnarTableTile::sdebug(detail,prefix,name?name:"VTile");
}
    

//##ModelId=3DD3CB0003D0
string VTile::ConstIterator::sdebug ( int detail,const string &prefix,const char *name ) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"CI:VTile",this);
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
      append(out,"("+tileref.sdebug(1,"","VTile::Ref")+")");
    else
      append(out,"(no ref)");
  }
  return out;
}


};

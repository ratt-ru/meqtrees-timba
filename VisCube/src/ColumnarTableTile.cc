//##ModelId=3DB964F20141
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

#include "ColumnarTableTile.h"

namespace VisCube 
{
    
// the null block represents an empty tile
BlockRef ColumnarTableTile::nullBlock
    (new SmartBlock(sizeof(BlockHeader),DMI::ZERO),DMI::LOCK);

//##ModelId=3DB964F20171
ColumnarTableTile::ColumnarTableTile()
  : ncol_(0),nrow_(0)
{
}

//##ModelId=3DB964F20172
ColumnarTableTile::ColumnarTableTile (const ColumnarTableTile &other,int flags,int depth)
  : DMI::BObj(),ncol_(0)
{
  cloneOther(other,flags,depth);
}

//##ModelId=3DB964F2018C
ColumnarTableTile::ColumnarTableTile (const Format::Ref &form, int nr,
                                      const HIID &id)
{
  init(form,nr,id);
}

//##ModelId=3DB964F201A6
ColumnarTableTile::ColumnarTableTile (const ColumnarTableTile &a, const ColumnarTableTile &b)
{
  Thread::Mutex::Lock lock2(a.mutex_);  
  Thread::Mutex::Lock lock3(b.mutex_);  
  // init with the first tile's format & ID
  init(a.formatRef(),a.nrow()+b.nrow(),a.tileId());
  copy(a);
  copy(a.nrow(),b);
}


//##ModelId=3DB964F201C0
ColumnarTableTile::~ColumnarTableTile()
{
  format_.unlock();
  datablock.unlock();
}


//##ModelId=3DB964F201C2
ColumnarTableTile & ColumnarTableTile::operator=(const ColumnarTableTile &right)
{
  if( this != &right )
    cloneOther(right,0,0);
  return *this;
}

void ColumnarTableTile::cloneOther (const ColumnarTableTile &right,int flags,int depth)
{
  Thread::Mutex::Lock lock(mutex_);
  Thread::Mutex::Lock lock2(right.mutex_);
  reset();
  id_ = right.id_;
  // copy format
  if( right.format_.valid() )
  {
    format_.copy(right.format_).lock();
    ncol_ = format_->maxcol();
  }
  nrow_ = right.nrow_;
  datablock.unlock().copy(right.datablock,flags,depth).lock();
  if( datablock == right.datablock )
    pdata = right.pdata;
  else
    setupDataPointers();
}

void ColumnarTableTile::setupDataPointers ()
{
  // recompute offsets into data block since it may have changed
  std::vector<int> offset;
  computeOffsets(offset,format(),nrow());
  applyOffsets(pdata,offset,datablock->cdata());
}


//##ModelId=3DB964F201D0
void ColumnarTableTile::init (const Format::Ref &form, int nr,
                              const HIID &id)
{
  Thread::Mutex::Lock lock(mutex_);
  reset();
  FailWhen(nr<0,"illegal numer of rows");
  format_.copy(form,DMI::READONLY).lock();
  id_ = id;
  nrow_ = nr;
  ncol_ = format_->maxcol();
  if( nrow() )
  {
    // compute offsets within block and total data size
    vector<int> offset;
    int totsize = computeOffsets(offset,format(),nrow());
    if( !nrow() ) // point to null block
      datablock.copy(nullBlock).lock();
    else // else allocate block
    {
      datablock.attach(new SmartBlock(totsize,DMI::ZERO),DMI::LOCK);
      initBlock(datablock().data(),totsize);
    }
    // setup pointers to column data
    applyOffsets(pdata,offset,datablock->cdata());
  }
}

//##ModelId=3DF9FDCC00FB
void ColumnarTableTile::initBlock (void *data,size_t sz) const
{
  BlockHeader *hdr = static_cast<BlockHeader*>(data);
  // block count is 2 if we have a format, 1 otherwise
  BObj::fillHeader(hdr,format_.valid()?2:1);
  hdr->nrow = nrow();
  // pack ID following the header
  sz -= sizeof(BlockHeader);
  hdr->idsize = id_.pack(static_cast<char*>(data) + sizeof(BlockHeader),sz);
}

//##ModelId=3DB964F201EA
void ColumnarTableTile::reset ()
{
  Thread::Mutex::Lock lock(mutex_);
  format_.unlock().detach();
  datablock.unlock().detach();
  nrow_ = ncol_ = 0;
  id_ = HIID();
  pdata.resize(0);
}

//##ModelId=3DB964F201EC
void ColumnarTableTile::applyFormat (const Format::Ref &form)
{
  Thread::Mutex::Lock lock(mutex_);
  if( format_.valid() )
  {
    // if we already have a valid format, check for compatibility
    FailWhen( format_ != form && format_.deref() != form.deref(),
        "cannot apply incompatible format");
  }
  else
  {
    // attaching format to existing tile (possible if tile was
    // fromBlocked but no format has been attached);
    // check that format is consistent with existing data layout 
    if( nrow() )
    {
      FailWhen( !datablock.valid(),"missing data block" );
      // compute offsets within block and total data size
      vector<int> offset;
      uint totsize = computeOffsets(offset,form.deref(),nrow());
      // check block size
      FailWhen(datablock->size() != totsize,"format not compatible with contents");
      // setup pointers to column data
      applyOffsets(pdata,offset,datablock->cdata());
    }
    format_.copy(form).lock();
    ncol_ = format().maxcol();
    if( datablock.isDirectlyWritable() )
      BObj::fillHeader(datablock().pdata<BlockHeader>(),2); // sets flag in block
  }
}

//##ModelId=3DB964F201F9
void ColumnarTableTile::changeFormat (const Format::Ref &form)
{
  Thread::Mutex::Lock lock(mutex_);
  // change only applies when we already have a format
  FailWhen(!hasFormat(),"tile format not yet defined");
  // when changing formats, data block needs to be re-done
  if( nrow() )
  {
    const Format &oldform = format(), &newform = form.deref();
    FailWhen( !datablock.valid(),"missing data block" );
    // allocate new datablock and compute offsets within
    vector<int> offset;
    int totsize = computeOffsets(offset,newform,nrow());
    BlockRef newblock(new SmartBlock(totsize,DMI::ZERO));
    // setup pointers to new column data
    vector<const void *> newptr;
    applyOffsets(newptr,offset,newblock->cdata());
    // copy across all matching columns
    int ncol = std::min(oldform.maxcol(),newform.maxcol());
    for( int icol=0; icol < ncol; icol++ )
    {
      // skip column if absent in either format
      if( !oldform.type(icol) || !newform.type(icol) )
        continue;
      Assert(pdata[icol]);
      // only copy if shapes are the same
      if( oldform.shape(icol) == newform.shape(icol) )
        memcpy(const_cast<void*>(newptr[icol]),pdata[icol],columnSize(icol));
    }
    // take over new block
    pdata = newptr;
    datablock.unlock().xfer(newblock).lock();
    initBlock(datablock().data(),totsize);
  }
  // remember new format
  format_.unlock().copy(form).lock();
  ncol_ = format().maxcol();
}

//##ModelId=3DB964F2020C
bool ColumnarTableTile::defined (int icol) const
{
  Thread::Mutex::Lock lock(mutex_);
  if( !pdata.size() )
    return 0;
  DbgFailWhen(icol<0 || icol>=(int)pdata.size(),"illegal column index");
  return pdata[icol] != 0;
}

//##ModelId=3DB964F2021A
const void * ColumnarTableTile::column (int icol) const
{
  DbgFailWhen(icol<0 || icol>=(int)pdata.size(),"illegal column index");
  FailWhen(!pdata[icol],"column empty or undefined");
  return pdata[icol];
}

//##ModelId=3DB964F20228
const void * ColumnarTableTile::column (int icol, int irow) const
{
  DbgFailWhen(icol<0 || icol>=(int)pdata.size(),"illegal column index");
  FailWhen(!pdata[icol],"column empty or undefined");
  return cdata(icol,irow);
}

//##ModelId=3DB964F20288
void ColumnarTableTile::addRows (int nr)
{
  Thread::Mutex::Lock lock(mutex_);
  FailWhen(!hasFormat(),"tile format not yet set");
  if( !nr )
    return;
  FailWhen(nr<0,"illegal number of rows");
  makeWritable();
  vector<int> offset;
  int totsize = computeOffsets(offset,format(),nrow()+nr);
  // allocate new block
  BlockRef newblock(new SmartBlock(totsize,DMI::ZERO));
  // setup pointers to new column data
  vector<const void *> newptr;
  applyOffsets(newptr,offset,newblock->cdata());
  // copy columns
  if( nrow() )
  {
    for( int i=0; i<format_->maxcol(); i++ )
      if( defined(i) )
        memcpy(const_cast<void*>(newptr[i]),pdata[i],columnSize(i));
  }
  nrow_ += nr;
  pdata = newptr;
  datablock.unlock().xfer(newblock).lock();
  initBlock(datablock().data(),totsize);
}

//##ModelId=3DB964F20295
void ColumnarTableTile::copy (int startrow, const ColumnarTableTile &other, int other_start, int numrows)
{
  Thread::Mutex::Lock lock(mutex_);
  Thread::Mutex::Lock lock2(other.mutex_);
  
  if( numrows<0 )
    numrows = other.nrow() - other_start;
  FailWhen(startrow<0 || other_start<0,"illegal row index");
  FailWhen(other_start + numrows > other.nrow(),"too many rows specified");
  FailWhen(!other.hasFormat(),"tile format not yet defined");
  
  // if we have no format, this sets it from other, else checks for consistency
  applyFormat(other.format_);
        
  // return if 0 rows are to be copied
  if( !numrows )
    return;
  // check for writability
  makeWritable();
  // uninitialized tile? Init with required size
  if( !nrow() )
    addRows(numrows);
  else // else check that we have enough space
  {
    FailWhen(startrow + numrows > nrow(),"insufficient space for copy");
  }
  // if no ID, get it from other
  if( !id_.size() )
    setTileId(other.id_);
  // copy data from other tile
  for( int i=0; i<format().maxcol(); i++ )
    if( defined(i) )
      memcpy( cwdata(i,startrow),other.cdata(i,other_start),columnSize(i,numrows) );
}

//##ModelId=3DB964F202F0
int ColumnarTableTile::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock lock(mutex_);
  int count = 1;
  datablock.unlock();
  set.pop(datablock);
  datablock.lock();
  const BlockHeader* hdr = datablock->pdata<BlockHeader>();
  int blockcount = BObj::checkHeader(hdr);
  FailWhen(blockcount<1 || blockcount>2,"invalid block count in header");
  nrow_ = hdr->nrow;
  const int maxsz = HIID::HIIDSize(MaxIdSize);
  FailWhen(datablock->size() < sizeof(BlockHeader) + maxsz,"corrupt block");
  // unpack the ID from the block
  id_.unpack(datablock->cdata()+sizeof(BlockHeader),hdr->idsize);
  // do we have a format? from-block it then.
  if( blockcount == 2 )
  {
    format_.unlock().attach(new TableFormat).lock();
    int nb = format_().fromBlock(set);
    FailWhen(nb!=1,"illegal block count in tile format");
    count++;
  }
  // no data -- get ID out of the block and set the nil representation
  if( !nrow_ )
  {
    id_.unpack(datablock->cdata()+sizeof(BlockHeader),hdr->idsize);
    pdata.resize(0);
    datablock.unlock().detach();
  }
  else // else we have some data
  {
    // if we already have a format, check that it is compatible with data
    if( hasFormat() )
    {
      ncol_ = format().maxcol();
      vector<int> offset;
      size_t totsize = computeOffsets(offset,format(),nrow());
      FailWhen(totsize != datablock->size(),"block not compatible with tile format");
      // setup pointers to column data
      applyOffsets(pdata,offset,datablock->cdata());
    }
    else // no format, will be attached later
    {
      ncol_ = -1;
      pdata.resize(0);
    }
  }
  return count;
}

//##ModelId=3DB964F202FE
int ColumnarTableTile::toBlock (BlockSet &set) const
{
  // note that for empty tiles (with no data or rows in them)
  // IDs will not be preserved
  Thread::Mutex::Lock lock(mutex_);
  FailWhen(nrow() && !datablock.valid(),"tile data missing??");
  int count = 1;
  // if we have data, push it out
  if( nrow() )
  {
    BlockRef ref = datablock;
    // make sure the block count is set correctly (COW block if not)
    int nb = format_.valid() ? 2 : 1;
    if( ref->pdata<BlockHeader>()->blockcount != nb )
      ref().pdata<BlockHeader>()->blockcount = nb;
    set.push(ref);
  }
  // else push out the nil representation
  else
  {
    BlockRef ref(new SmartBlock(sizeof(BlockHeader) + HIID::HIIDSize(MaxIdSize)));
    initBlock(ref().data(),ref->size());
    set.push(ref);
  }
  // push out format
  if( format_.valid() )
    count += format_->toBlock(set);
  return count;
}

//##ModelId=3DB964F2030D
CountedRefTarget* ColumnarTableTile::clone (int flags, int depth) const
{
  return new ColumnarTableTile(*this,flags,depth);
}

//##ModelId=3DF9FDCB008B
void ColumnarTableTile::setTileId (const HIID &id)
{
  makeWritable();
  FailWhen(id.size() > MaxIdSize,"Length of tile ID > maximum" );
  id_ = id;
  if( datablock.valid() )
  {
    // re-init block to copy new ID into it
    initBlock(datablock().data(),datablock->size());
  }
}

//##ModelId=3DB964F30005
int ColumnarTableTile::computeOffsets (vector<int> &offset,const Format &format,int nrow)
{
  int totsize = sizeof(BlockHeader) + HIID::HIIDSize(MaxIdSize);
  offset.resize(format.maxcol());
  offset.assign(format.maxcol(),-1);
  // -1 marks undefined column. With 0 rows, all columns are undefined.
  for( int i=0; i<format.maxcol(); i++ )
  {
    int elsize = format.elsize(i);
    if( elsize )
    {
      int align = totsize%elsize; // align at element size
      if( align )
        totsize += elsize - align;
      offset[i] = totsize;
      totsize += format.cellsize(i)*nrow;
    }
  }
  return totsize;
}

//##ModelId=3DB964F3002D
void ColumnarTableTile::applyOffsets (vector<const void *> &ptrs,const vector<int> &offset,const char *ptr0)
{
  ptrs.resize(offset.size());
  for( uint i=0; i<offset.size(); i++ )
    if( offset[i]>=0 )
      ptrs[i] = ptr0 + offset[i];
    else
      ptrs[i] = 0;
}


//##ModelId=3DD3C52001FE
string ColumnarTableTile::sdebug ( int detail,const string &,const char *name ) const
{
  Thread::Mutex::Lock lock(mutex_);
  
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"ColTableTile",this);
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"id=%s",id_.toString().c_str());
    appendf(out,"%d rows",nrow());
    if( datablock.valid() )
      appendf(out,"%ld bytes @%x",datablock->size(),datablock->data());
  }
  if( detail >= 2 || detail <= -2 )
  {
    out += ", ";
    if( hasFormat() )
      out += format().sdebug(-abs(detail)+1,"","");
    else
      out += "no format";
  }
  return out;
}
    
};

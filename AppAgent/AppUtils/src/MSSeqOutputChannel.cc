//  MSVisOutputAgent.h: agent for writing an AIPS++ MS
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#include "MSSeqOutputChannel.h"

#include <TimBase/BlitzToAips.h>
#include <DMI/Exception.h>
#include <AppAgent/VisDataVocabulary.h>
#include <TimBase/AipsppMutex.h>

#include <tables/Tables/ArrColDesc.h>
#include <tables/Tables/ArrayColumn.h>
#include <tables/Tables/ScalarColumn.h>
#include <casa/Arrays/Matrix.h>

using namespace casa;

namespace AppAgent
{

using namespace LOFAR;
using namespace LOFAR::Thread;
using AipsppMutex::aipspp_mutex;

using namespace AppEvent;
using namespace VisData;
using namespace MSChannel;

MSSeqOutputChannel::MSSeqOutputChannel ()
{
}


void MSSeqOutputChannel::close (const string &msg)
{
  row_to_tile_.clear();
  tiles_.clear();
  MSOutputChannel::close(msg);
  cdebug(1)<<"closed\n";
}

//##ModelId=3E28316403E4
void MSSeqOutputChannel::doPutHeader (const DMI::Record &header)
{
  MSOutputChannel::doPutHeader(header);
  int nant = header[FNumAntenna].as<int>(27);
  tiles_.reserve(nant*(nant-1)/2);
  // init row map
  ms_num_rows_ = ms_.nrow();
  row_to_tile_.resize(ms_num_rows_);
  memset(&(row_to_tile_[0]),0xFF,ms_num_rows_*sizeof(row_to_tile_[0]));
  
  current_seqnr_ = -1;
  min_ms_row_ = ms_num_rows_;
  max_ms_row_ = 0;
}

void MSSeqOutputChannel::doPutFooter (const DMI::Record &footer)
{
  flushOutputTiles();
  row_to_tile_.clear();
  tiles_.clear();
  MSOutputChannel::doPutFooter(footer);
}

void MSSeqOutputChannel::flushOutputTiles ()
{
  if( tiles_.empty() )
    return;
  try
  {
    Assert(min_ms_row_<=max_ms_row_);
    // This function is called whenever we have a whole time chunk's worth 
    // of tiles sitting in the output cache. The assumption is that the tiles
    // are sorted by time, and that the MS is sorted by time, so the MS rows
    // associated with this chunk are all > the MS rows of the previous chunk.
    // min_ms_row_ and max_ms_row_ are the min/max MS rows associated with 
    // this chunk
    for( int msrow = min_ms_row_; msrow<=max_ms_row_; msrow++ )
    {
      // get tile associated with this MS row
      const TileMapping & tm = row_to_tile_[msrow];
      if( tm.tile_num < 0 )
        continue;
      const VTile & tile = *(tiles_[tm.tile_num]);
      // ok, this is the right row
      if( tile.defined(VTile::DATA) && datacol_.valid )
        putColumn(datacol_,msrow,tile.data()(LoRange::all(),LoRange::all(),tm.tile_row));
      if( tile.defined(VTile::PREDICT) && predictcol_.valid )
        putColumn(predictcol_,msrow,tile.predict()(LoRange::all(),LoRange::all(),tm.tile_row));
      if( tile.defined(VTile::RESIDUALS) && rescol_.valid )
        putColumn(rescol_,msrow,tile.residuals()(LoRange::all(),LoRange::all(),tm.tile_row));
      if( write_bitflag_ || write_legacy_flags_ )
      {
        if( use_bitflag_col_ )
        {
          // read in the bitflag columns
          int rowflag = rowBitflagCol_(msrow);
          Matrix<Int> abitflags;
          bitflagCol_.getSlice(msrow,column_slicer_,abitflags);
          // if writing bitflags, apply masks and write back
          if( write_bitflag_ )
          {
            rowflag = (rowflag&ms_flagmask_)|(tile.rowflag(tm.tile_row)&tile_flagmask_?tile_bitflag_:0);
            rowBitflagCol_.put(msrow,rowflag);
            for( Matrix<Int>::iterator iter = abitflags.begin(); iter != abitflags.end(); iter++ )
              (*iter) &= ms_flagmask_;
            if( tile.defined(VTile::FLAGS) && tile_flagmask_ )
            {
              LoMat_int int_flags = tile.flags()(LoRange::all(),LoRange::all(),tm.tile_row);
              int_flags = where(int_flags&tile_flagmask_,tile_bitflag_,0);
              if( flip_freq_ )
                int_flags.reverseSelf(blitz::secondDim);
              Matrix<Int> abitflags_add;
              B2A::copyArray(abitflags_add,int_flags);
              Matrix<Int>::const_iterator iter2 = abitflags_add.begin();
              for( Matrix<Int>::iterator iter = abitflags.begin(); iter != abitflags.end(); iter++,iter2++ )
                (*iter) |= (*iter2);
            }
            bitflagCol_.putSlice(msrow,column_slicer_,abitflags);
          }
          // if writing legacy flags, apply legacy flagmasks and write
          if( write_legacy_flags_ )
          {
            rowFlagCol_.put(msrow,(rowflag&legacy_flagmask_) != 0);
            Matrix<Bool> aflags(abitflags.shape());
            Matrix<Int>::const_iterator iter2 = abitflags.begin();
            for( Matrix<Bool>::iterator iter = aflags.begin(); iter != aflags.end(); iter++,iter2++ )
              (*iter) = ((*iter2)&legacy_flagmask_) != 0;
            flagCol_.putSlice(msrow,column_slicer_,aflags);
          }
        }
        else if( write_legacy_flags_ ) // write legacy FLAG column based on the tile_flagmask_
        {
          rowFlagCol_.put(msrow,(tile.rowflag(tm.tile_row)&tile_flagmask_) != 0);
          if( tile.defined(VTile::FLAGS) )
          {
            LoMat_int int_flags = tile.flags()(LoRange::all(),LoRange::all(),tm.tile_row);
            LoMat_bool flags( int_flags.shape() );
            flags = blitz::cast<bool>(int_flags & tile_flagmask_ );
            if( flip_freq_ )
              flags.reverseSelf(blitz::secondDim);
            Matrix<Bool> aips_flags;
            B2A::copyArray(aips_flags,flags);
  //          cdebug(6)<<"writing to FLAG column: "<<aips_flags<<endl;
            flagCol_.putSlice(msrow,column_slicer_,aips_flags);
          }
        }
      }
    }
  }
  catch( std::exception &exc )
  {
    min_ms_row_ = ms_num_rows_;
    max_ms_row_ = 0;
    tiles_.resize(0);
    throw;
  }
  min_ms_row_ = ms_num_rows_;
  max_ms_row_ = 0;
  tiles_.resize(0);
}

//##ModelId=3E28316B012D
void MSSeqOutputChannel::doPutTile (const VTile &tile)
{
  cdebug(3)<<"putting tile "<<tile.tileId()<<", "<<tile.nrow()<<" rows"<<endl;
  cdebug(4)<<"  into table rows: "<<tile.seqnr()<<endl;
  cdebug(4)<<"  rowflags are: "<<tile.rowflag()<<endl;
  int seqnr = tile.seqNumber();
  // first tile ever -- set starting sequence number
  if( current_seqnr_ < 0 )
  {
    current_seqnr_ = seqnr;
    min_ms_row_ = ms_num_rows_;
    max_ms_row_ = 0;
  }
  // else sequence number has changed, so flush any accumulated tiles
  else if( seqnr != current_seqnr_ )
  {
    flushOutputTiles();
    current_seqnr_ = seqnr;
  }
  // now, attach to the tile 
  tiles_.push_back(VTile::Ref(tile));
  // work out row numbers
  for( int irow=0; irow<tile.nrow(); irow++ )
  {
    if( tile.rowflag(irow) != int(VTile::MissingData) )
    {
      int msrow = tile.seqnr(irow);
      row_to_tile_[msrow].tile_num = tiles_.size()-1;
      row_to_tile_[msrow].tile_row = irow;
      if( msrow < min_ms_row_ )
        min_ms_row_ = msrow;
      if( msrow > max_ms_row_ )
        max_ms_row_ = msrow;
    }
  }
}

string MSSeqOutputChannel::sdebug (int detail,const string &prefix,const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"MSSeqOutputChannel",this);
  }
  return out;
}

} // namespace AppAgent


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

#include "MSOutputChannel.h"

#include <TimBase/BlitzToAips.h>
#include <DMI/Exception.h>
#include <AppAgent/VisDataVocabulary.h>
#include <TimBase/AipsppMutex.h>

#include <tables/Tables/ArrColDesc.h>
#include <tables/Tables/ScaColDesc.h>
#include <tables/Tables/ArrayColumn.h>
#include <tables/Tables/ScalarColumn.h>
#include <tables/Tables/TiledStManAccessor.h>
#include <tables/Tables/TiledColumnStMan.h>
#include <tables/Tables/IncrementalStMan.h>
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

//##ModelId=3E2831C7010D
MSOutputChannel::MSOutputChannel ()
    : FileChannel(),msname_("(none)")
{
  setState(CLOSED);
}


//##ModelId=3E28315F0001
int MSOutputChannel::init (const DMI::Record &params)
{
  if( FileChannel::init(params) < 0 )
    return state();

  Mutex::Lock lock(aipspp_mutex);
  params_ = params;
  ms_ = MeasurementSet();
  msname_ = "(none)";

  cdebug(1)<<"initialized with "<<params_.sdebug(3)<<endl;

  return state();
}

void MSOutputChannel::close (const string &msg)
{
  FileChannel::close(msg);
  close_ms();
  cdebug(1)<<"closed\n";
}

void MSOutputChannel::close_ms ()
{
  Mutex::Lock lock(aipspp_mutex);
  rowFlagCol_.reference(casa::ScalarColumn<casa::Bool>());
  flagCol_.reference(casa::ArrayColumn<casa::Bool>());
  datacol_.col.reference(casa::ArrayColumn<casa::Complex>());
  predictcol_.col.reference(casa::ArrayColumn<casa::Complex>());
  rescol_.col.reference(casa::ArrayColumn<casa::Complex>());
  ms_ = MeasurementSet();
  msname_ = "(none)";
}

//##ModelId=3EC25BF002D4
void MSOutputChannel::postEvent (const HIID &id, const ObjRef &data,AtomicID cat,const HIID &src)
{
  recordOutputEvent(id,data,cat,src);
  Mutex::Lock lock(aipspp_mutex);
  try
  {
    int code = VisEventType(id);
    if( code == HEADER )
    {
      DMI::Record::Ref ref = data;
      doPutHeader(*ref);
      setState(DATA);
    }
    else if( code == DATA )
    {
      if( state() != DATA )
      {
        cdebug(3)<<"got tile but state is not DATA, ignoring\n";
      }
      else
      {
        VTile::Ref ref = data;
        doPutTile(*ref);
      }
    }
    else if( code == FOOTER )
    {
      if( state() == DATA || state() == HEADER )
      {
        DMI::Record::Ref ref = data;
        doPutFooter(*ref);
        setState(CLOSED);
      }
      else
      {
        cdebug(2)<<"got footer but state is not DATA, ignoring\n";
      }
    }
  }
  catch( std::exception &exc )
  {
    cdebug(1)<<"error handling event ["<<id<<"]: "<<exceptionToString(exc);
    throw;
  }
  catch( ... )
  {
    cdebug(1)<<"unknown exception handling event ["<<id<<"]\n";
    throw;
  }
}

//##ModelId=3EC25BF002E4
bool MSOutputChannel::isEventBound (const HIID &id,AtomicID)
{
  return id.matches(VisEventMask());
}

bool MSOutputChannel::setupDataColumn (Column &col)
{
  // if name is not set, then column is ignored
  if( !col.name.length() )
    return col.valid = false;
  const TableDesc &td = ms_.tableDesc();
  // add column to MS, if it doesn't exist
  if( !td.isColumn(col.name) )
  {
    ArrayColumnDesc<Complex> coldesc(col.name,
                          "added by MSOutputAgent",
                           null_cell_.shape(),
                           ColumnDesc::Direct|ColumnDesc::FixedShape);
    // check what storage manager the standard DATA column uses
    string dmtype;
    if( td.isColumn("DATA") )
      dmtype = td.columnDesc("DATA").dataManagerType();
    if( dmtype.length() > 5 && !dmtype.compare(0,5,"Tiled") )
    {
      // get tile shape from storage manager of DATA column
      ROTiledStManAccessor acc(ms_,td.columnDesc("DATA").dataManagerGroup());
      IPosition tileShape(acc.tileShape(0));
      // create a tiled storage manager with the same shape
      TiledColumnStMan stman("Tiled_"+col.name,acc.tileShape(0));
      cdebug(1)<<"creating new column "+col.name+", shape "<<null_cell_.shape()
                <<", TiledColumnStMan data manager with shape "<<acc.tileShape(0)<<endl;
      ms_.addColumn(coldesc,stman);
    }
    // else add using a standard data manager
    else
    {
      cdebug(1)<<"creating new column "+col.name+", shape "<<null_cell_.shape()
                <<" using the default data manager"<<endl;
      ms_.addColumn(coldesc);
    }
  }
  // init the column
  cdebug(2)<<"attaching to column "<<col.name<<endl;
  col.col.attach(ms_,col.name);
  return col.valid = true;
}

//##ModelId=3EC25F74033F
int MSOutputChannel::refillStream()
{
  return AppEvent::WAIT; // no input events
}

//##ModelId=3E28316403E4
void MSOutputChannel::doPutHeader (const DMI::Record &header)
{
  // open the MS named in the header (incidentally, this will also
  // flush & close any previously named MS)
  msname_ = header[FMSName].as<string>();
  ms_ = MeasurementSet(msname_,TableLock(TableLock::AutoNoReadLocking),Table::Update);
  // get range of channels from header and setup slicer
  time_incr_ = header[FTimeIncrement].as<int>(1);
  channels_[0] = header[FChannelStartIndex].as<int>();
  channels_[1] = header[FChannelEndIndex].as<int>();
  chan_incr_ = header[FChannelIncrement].as<int>(1);
  int ncorr = header[FCorr].size(Tpstring);
  flip_freq_ = header[FFlipFreq].as<bool>(false);
  column_slicer_ = Slicer(IPosition(2,0,channels_[0]),
                          IPosition(2,ncorr-1,channels_[1]),
                          IPosition(2,1,chan_incr_),
                          Slicer::endIsLast);
  IPosition origshape = LoShape(header[FOriginalDataShape].as_vector<int>());
  null_cell_.resize(origshape);
  null_cell_.set(0);
  null_bitflag_cell_.resize(origshape);
  null_bitflag_cell_.set(0);
  // setup parameters from default record
  write_bitflag_      = params_[FWriteBitflag].as<bool>(true);
  write_legacy_flags_ = params_[FWriteLegacyFlags].as<bool>(true);
  legacy_flagmask_    = params_[FLegacyFlagMask].as<int>(0xFFFFFFFF);
  ms_flagmask_        = params_[FMSFlagMask].as<int>(0xFFFFFFFF);
  tile_flagmask_      = params_[FTileFlagMask].as<int>(0xFFFFFFFF);
  tile_bitflag_       = params_[FTileBitflag].as<int>(1);
  use_bitflag_col_    = params_[FUseBitflagColumn].as<bool>(true);
  datacol_.name       = params_[FDataColumn].as<string>("");
  predictcol_.name    = params_[FPredictColumn].as<string>("");
  rescol_.name        = params_[FResidualsColumn].as<string>("");
  // and override them from the header
  if( header[FOutputParams].exists() )
  {
    const DMI::Record &hparm = header[FOutputParams].as<DMI::Record>();
    write_bitflag_      = hparm[FWriteBitflag].as<bool>(write_bitflag_);
    write_legacy_flags_ = hparm[FWriteLegacyFlags].as<bool>(write_legacy_flags_);
    legacy_flagmask_    = hparm[FLegacyFlagMask].as<int>(legacy_flagmask_);
    ms_flagmask_        = hparm[FMSFlagMask].as<int>(ms_flagmask_);
    tile_flagmask_      = hparm[FTileFlagMask].as<int>(tile_flagmask_);
    tile_bitflag_       = hparm[FTileBitflag].as<int>(tile_bitflag_);
    use_bitflag_col_    = hparm[FUseBitflagColumn].as<bool>(use_bitflag_col_);
    datacol_.name       = hparm[FDataColumn].as<string>(datacol_.name);
    predictcol_.name    = hparm[FPredictColumn].as<string>(predictcol_.name);
    rescol_.name        = hparm[FResidualsColumn].as<string>(rescol_.name);
  }
  // setup columns
  setupDataColumn(datacol_);
  setupDataColumn(predictcol_);
  setupDataColumn(rescol_);
  // attach to FLAG columns if writing to them
  if( write_legacy_flags_ )
  {
    rowFlagCol_.attach(ms_,"FLAG_ROW");
    flagCol_.attach(ms_,"FLAG");
  }
  // setup the BITFLAG columns if needed
  if( use_bitflag_col_ && ( write_bitflag_ || write_legacy_flags_ ) )
  {
    const TableDesc &td = ms_.tableDesc();
    if( td.isColumn("BITFLAG") && td.isColumn("BITFLAG_ROW") )
    {
      cdebug(2)<<"attaching to columns BITFLAG and BITFLAG_ROW\n";
      bitflagCol_.attach(ms_,"BITFLAG");
      rowBitflagCol_.attach(ms_,"BITFLAG_ROW");
    }
    else
      use_bitflag_col_ = false;
  }
  cdebug(2)<<"got header for MS "<<msname_<<endl;
  cdebug(2)<<"  orig shape: "<<origshape<<endl;
  cdebug(2)<<"  channels: "<<channels_[0]<<"-"<<channels_[1]<<endl;
  cdebug(2)<<"  correlations: "<<ncorr<<endl;
  cdebug(2)<<"  colname_data: "<<datacol_.name<<endl;
  cdebug(2)<<"  colname_predict: "<<predictcol_.name<<endl;
  cdebug(2)<<"  colname_residuals: "<<rescol_.name<<endl;
  // set state to indicate success
  tilecount_ = rowcount_ = 0;
}

void MSOutputChannel::doPutFooter (const DMI::Record &)
{
  cdebug(2)<<"got footer event, flushing & closing ms\n";
  ms_.unlock();
  ms_.flush();
  ms_ = MeasurementSet();
}


//##ModelId=3F5F436303AB
void MSOutputChannel::putColumn (Column &col,int irow,const LoMat_fcomplex &data)
{
  Matrix<Complex> aips_data;
  if( flip_freq_ )
  {
    LoMat_fcomplex revdata(data);
    revdata.reverseSelf(blitz::secondDim);
    B2A::copyArray(aips_data,revdata);
  }
  else
    B2A::copyArray(aips_data,data);
  // cdebug(6)<<"writing "<<col.name<<": "<<aips_data<<endl;
  if( !col.col.isDefined(irow) )
    col.col.put(irow,null_cell_);
  col.col.putSlice(irow,column_slicer_,aips_data);
}

//##ModelId=3E28316B012D
void MSOutputChannel::doPutTile (const VTile &tile)
{
  tilecount_++;
  cdebug(3)<<"putting tile "<<tile.tileId()<<", "<<tile.nrow()<<" rows"<<endl;
  cdebug(4)<<"  into table rows: "<<tile.seqnr()<<endl;
  cdebug(4)<<"  rowflags are: "<<tile.rowflag()<<endl;
  // iterate over rows of the tile
  int count=0;
  for( VTile::const_iterator iter = tile.begin(); iter != tile.end(); iter++ )
  {
    int rowflag = iter.rowflag();
    if( rowflag == int(VTile::MissingData) )
    {
      cdebug(5)<<"  tile row flagged as missing, skipping\n";
      continue;
    }
    count++;
    rowcount_++;
    int irow = iter.seqnr();
    cdebug(5)<<"  writing to table row "<<irow<<endl;
    // write flags if required
    if( write_bitflag_ || write_legacy_flags_ )
    {
      if( use_bitflag_col_ )
      {
        // read in current bitflag column
        int rflag = (rowBitflagCol_(irow)&ms_flagmask_)|(rowflag&tile_flagmask_?tile_bitflag_:0);
        Matrix<Int> abitflags;
        bool has_abitflags = false;
        try
        {
          bitflagCol_.getSlice(irow,column_slicer_,abitflags);
          has_abitflags = true;
        }
        // error probably means uninitialized column, we'll fill it below
        catch( std::exception &exc )
        {
          cdebug(1)<<"Failed to read BITFLAG/BITFLAG_ROW, assuming null bitflags\n";
          cdebug(1)<<"Error was: "<<exc.what()<<endl;
        }
        // if writing bitflags, apply masks and write out
        if( write_bitflag_ )
        {
          rflag = (rflag&ms_flagmask_)|(rowflag&tile_flagmask_?tile_bitflag_:0);
          rowBitflagCol_.put(irow,rflag);
          if( has_abitflags )
          {
            for( Matrix<Int>::iterator miter = abitflags.begin(); miter != abitflags.end(); miter++ )
              (*miter) &= ms_flagmask_;
          }
          if( tile_flagmask_ )
          {
            LoMat_int tileflags(iter.flags().shape());
            tileflags = where(iter.flags()&tile_flagmask_,tile_bitflag_,0);
            if( flip_freq_ )
              tileflags.reverseSelf(blitz::secondDim);
            if( has_abitflags )
            {
              Matrix<Int> abitflags_add;
              B2A::copyArray(abitflags_add,tileflags);
              Matrix<Int>::const_iterator iter2 = abitflags_add.begin();
              for( Matrix<Int>::iterator iter = abitflags.begin(); iter != abitflags.end(); iter++,iter2++ )
                (*iter) |= (*iter2);
            }
            else
            {
              B2A::copyArray(abitflags,tileflags);
              has_abitflags = true;
            }
          }
          bitflagCol_.putSlice(irow,column_slicer_,abitflags);
        }
        // if writing legacy flags, apply masks and write out
        if( write_legacy_flags_ && has_abitflags )
        {
          rowFlagCol_.put(irow,(rflag&legacy_flagmask_) != 0);
          Matrix<Bool> aflags(abitflags.shape());
          Matrix<Int>::const_iterator iter2 = abitflags.begin();
          for( Matrix<Bool>::iterator iter = aflags.begin(); iter != aflags.end(); iter++,iter2++ )
            (*iter) = ((*iter2)&legacy_flagmask_) != 0;
          flagCol_.putSlice(irow,column_slicer_,aflags);
        }
      }
      else if ( write_legacy_flags_ )
      // write legacy FLAG/FLAG_ROW columns based on the tile_flagmask
      {
        rowFlagCol_.put(irow,(rowflag&tile_flagmask_) != 0);
        LoMat_bool flags( iter.flags().shape() );
        flags = blitz::cast<bool>(iter.flags() & tile_flagmask_ );
        if( flip_freq_ )
          flags.reverseSelf(blitz::secondDim);
        Matrix<Bool> aflags;
        B2A::copyArray(aflags,flags);
        flagCol_.putSlice(irow,column_slicer_,aflags);
      }
    }
    if( tile.defined(VTile::DATA) && datacol_.valid )
      putColumn(datacol_,irow,iter.data());
    if( tile.defined(VTile::PREDICT) && predictcol_.valid )
      putColumn(predictcol_,irow,iter.predict());
    if( tile.defined(VTile::RESIDUALS) && rescol_.valid )
      putColumn(rescol_,irow,iter.residuals());
  }
  cdebug(4)<<"  wrote "<<count<<"/"<<tile.nrow()<<" rows\n";
}

string MSOutputChannel::sdebug (int detail,const string &prefix,const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;

  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"MSOutputChannel",this);
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"MS %s, state %s",msname_.c_str(),stateString().c_str());
  }
  if( detail >= 2 || detail <= -2 )
  {
    appendf(out,"wrote %d tiles/%d rows",tilecount_,rowcount_);
  }
  return out;
}

} // namespace AppAgent


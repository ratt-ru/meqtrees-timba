//  MSVisInputAgent.cc: VisInputAgent for reading an AIPS++ MS
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

#define AIPSPP_HOOKS
#include <TimBase/AipsppMutex.h>
#include "MSInputChannel.h"
#include <AppAgent/VisDataVocabulary.h>
#include <TimBase/BlitzToAips.h>
#include <DMI/AIPSPP-Hooks.h>

#include <ms/MeasurementSets/MSAntenna.h>
#include <ms/MeasurementSets/MSAntennaColumns.h>
#include <ms/MeasurementSets/MSDataDescription.h>
#include <ms/MeasurementSets/MSDataDescColumns.h>
#include <ms/MeasurementSets/MSField.h>
#include <ms/MeasurementSets/MSFieldColumns.h>
#include <ms/MeasurementSets/MSPolarization.h>
#include <ms/MeasurementSets/MSPolColumns.h>
#include <ms/MeasurementSets/MSSpectralWindow.h>
#include <ms/MeasurementSets/MSSpWindowColumns.h>
#include <ms/MeasurementSets/MSRange.h>
#include <measures/Measures/MDirection.h>
#include <measures/Measures/MeasConvert.h>
#include <measures/Measures/Stokes.h>
#include <casa/Quanta/MVPosition.h>
#include <casa/Containers/Record.h>
#include <tables/Tables/ArrColDesc.h>
#include <tables/Tables/ArrayColumn.h>
#include <tables/Tables/ColumnDesc.h>
#include <tables/Tables/ExprNode.h>
#include <tables/Tables/ExprNodeSet.h>
#include <tables/Tables/SetupNewTab.h>
#include <tables/Tables/TableParse.h>
#include <unistd.h>

using namespace casa;

// temp kludge for gcc 4.1, as TableParse.h does not have these declarations,
// only friend statements
namespace casa
{
  TaQLResult tableCommand (const String& command);

  TaQLResult tableCommand (const String& command,
                                 const Table& tempTable);
  TaQLResult tableCommand (const String& command,
                                 const std::vector<const Table*>& tempTables);
  TaQLResult tableCommand (const String& command,
                                 Vector<String>& columnNames);
  TaQLResult tableCommand (const String& command,
                                 Vector<String>& columnNames,
                                 String& commandType);
  TaQLResult tableCommand (const String& command,
                                 const std::vector<const Table*>& tempTables,
                                 Vector<String>& columnNames);
  TaQLResult tableCommand (const String& command,
                                 const std::vector<const Table*>& tempTables,
                                 Vector<String>& columnNames,
                                 String& commandType);
};

namespace AppAgent
{
using namespace LOFAR;
using AipsppMutex::aipspp_mutex;
using namespace LOFAR::Thread;

using namespace AppEvent;
using namespace VisData;
using namespace MSChannel;

//##ModelId=3DF9FECD0219
MSInputChannel::MSInputChannel ()
    : FileChannel(),obsid_(0)
{
}

    
//##ModelId=3DF9FECD0285
void MSInputChannel::fillHeader (DMI::Record &hdr,const DMI::Record &select)
{
  // get relevant selection parameters
  int ddid = select[FDDID].as<int>(0);        
  int fieldid = select[FFieldIndex].as<int>(0);        
  
  // place current selection into header
  // clone a readonly snapshot, since selection will not change
  hdr[FSelection] <<= new DMI::Record(select,DMI::DEEP|DMI::READONLY);
  
  // get phase reference from FIELD subtable
  {
    MSField mssub(ms_.field());
    ROMSFieldColumns mssubc(mssub);
      // Get the phase reference of the first field.
    MDirection dir = mssubc.phaseDirMeasCol()(fieldid)(IPosition(1,0));
    Vector<Double> dirvec = MDirection::Convert(dir, MDirection::J2000)().getValue().get();
    // assign to header
    hdr[FPhaseRef] = dirvec;
  }
  // get frequencies from DATA_DESC and SPW subtables
  // ddid determines which segment to read
  {
    // Get the frequency domain of the given data descriptor id
    // which gives as the spwid.
    MSDataDescription mssub1(ms_.dataDescription());
    ROMSDataDescColumns mssub1c(mssub1);
    int spw = mssub1c.spectralWindowId()(ddid);
    MSSpectralWindow mssub(ms_.spectralWindow());
    ROMSSpWindowColumns mssubc(mssub);
    // get freqs
    Array<Double> ch_freq  = mssubc.chanFreq()(spw);
    Array<Double> ch_width = mssubc.chanWidth()(spw);
    num_channels_ = ch_freq.nelements();
    if( channels_[0]<0 )
      channels_[0] = 0; 
    if( channels_[1]<0 )
      channels_[1] = num_channels_+channels_[1]; 
    if( channels_[0] > num_channels_ )
      channels_[0] = num_channels_-1;
    if( channels_[1] > num_channels_ )
      channels_[1] = num_channels_-1;
    if( channels_[1] < channels_[0] )
    {
      int dum = channels_[1]; channels_[1] = channels_[0]; channels_[0] = dum; 
    }
    IPosition ip0(1,channels_[0]),ip1(1,channels_[1]),iinc(1,channel_incr_);
    Array<Double> ch_freq1 = ch_freq(ip0,ip1,iinc);
    Array<Double> ch_width1 = abs(ch_width(ip0,ip1,iinc));
    // recompute # channels since an increment may have been applied
    num_channels_ = ch_freq1.nelements();
    // if frequencies are in decreasing order, freq axis needs to be flipped
    if( ch_freq1(IPosition(1,0)) > ch_freq1(IPosition(1,num_channels_-1)) )
    {
      dprintf(2)("reversing frequency channel\n");
      hdr[FFlipFreq] = flip_freq_ = true;
      hdr[FChannelFreq] = B2A::refAipsToBlitz<double,1>(ch_freq1).reverse(blitz::firstDim);
      hdr[FChannelWidth] = B2A::refAipsToBlitz<double,1>(ch_width1).reverse(blitz::firstDim);
    }
    else
    {
      dprintf(2)("frequency channel is in normal order\n");
      hdr[FFlipFreq] = flip_freq_ = false;
      hdr[FChannelFreq]  = ch_freq1;
      hdr[FChannelWidth] = ch_width1;
    }
    // now get the correlations & their types
    int polzn = mssub1c.polarizationId()(ddid);
    MSPolarization mssub2(ms_.polarization());
    ROMSPolarizationColumns mssub2c(mssub2);
    num_corrs_ = mssub2c.numCorr()(polzn);
    Vector<int> corrtypes = mssub2c.corrType()(polzn);
    vector<string> corrnames(corrtypes.nelements());
    for( uint i=0; i<corrtypes.nelements(); i++ )
      corrnames[i] = Stokes::name(Stokes::type(corrtypes(i)));
    hdr[FCorr] = corrnames;
  }
  // get antenna positions from ANTENNA subtable
  {
    MSAntenna          mssub(ms_.antenna());
    ROMSAntennaColumns mssubc(mssub);
    hdr[FNumAntenna] = num_antennas_ = mssub.nrow();
    // Just get all positions as a single array
    hdr[FAntennaPos] = mssubc.position().getColumn();
  }
}
 
//##ModelId=3DF9FECD025E
void MSInputChannel::openMS (DMI::Record &header,const DMI::Record &select)
{
  Mutex::Lock lock(aipspp_mutex);
  // open MS
  ms_ = MeasurementSet(msname_,TableLock(TableLock::AutoNoReadLocking),Table::Old);
  dprintf(1)("opened MS %s, %d rows\n",msname_.c_str(),ms_.nrow());
  
  dprintf(3)("selection record is %s\n",select.sdebug(4).c_str());
  
  // get DDID and Field ID (default is 0)
  int ddid = select[FDDID].as<int>(0);        
  int fieldid = select[FFieldIndex].as<int>(0);        
  // Get range of channels (default values: all channles)
  channels_[0] = select[FChannelStartIndex].as<int>(0);
  channels_[1] = select[FChannelEndIndex].as<int>(-1);
  channel_incr_ = select[FChannelIncrement].as<int>(1);
  
  // fill header from MS
  fillHeader(header,select);
  // put MS name into header
  header[FMSName] = msname_;
  // get CWD
  const size_t cwdsize = 16384;
  char *cwd_temp = new char[cwdsize];
  getcwd(cwd_temp,cwdsize);
  header[FCwd] = cwd_temp;
  delete [] cwd_temp;
  
  // figure out max ifr index
  num_ifrs_ = ifrNumber(num_antennas_-1,num_antennas_-1) + 1;
  
  // We only handle the given field & data desc id
  TableExprNode expr = ( ms_.col("FIELD_ID") == fieldid && ms_.col("DATA_DESC_ID") == ddid );
  selms_ = ms_(expr);
  // sort by time
  selms_.sort("TIME");
  
  vdsid_ = VDSID(obsid_++,0,0);
  header[FVDSID] = static_cast<HIID&>(vdsid_);
  header[FDDID] = ddid;
  header[FFieldIndex] = fieldid;
  header[FDataType] = HIID("MS.Non.Calibrated");
  header[FDataColumnName] = dataColName_;
  header[FDomainIndex] = -1; // negative domain index indicates full data
  
  header[FChannelStartIndex] = channels_[0];
  header[FChannelEndIndex]   = channels_[1];
  header[FChannelIncrement]  = channel_incr_;
  
  // get and apply selection string
  String where = select[FSelectionString].as<string>("");
  dprintf(1)("select ddid=%d, field=%d, where=\"%s\", channels=[%d:%d]\n",
      ddid,fieldid,where.c_str(),channels_[0],channels_[1]);
  if( where.empty() ) 
  {
    tableiter_  = TableIterator(selms_, "TIME");
  }
  else
  {
    selms_ = tableCommand ("select from $1 where " + where, selms_).table();
    FailWhen( !selms_.nrow(),"selection yields empty table" );
    tableiter_  = TableIterator(selms_, "TIME");
  }
  int nrows = selms_.nrow();
  FailWhen(!nrows,"MS selection yield no rows");
  dprintf(1)("MS selection yields %d rows\n",selms_.nrow());
  
  // do we have a WEIGHT_SPECTRUM column at all?
  const TableDesc & tabledesc = selms_.tableDesc();
  has_weights_ = tabledesc.isColumn("WEIGHT_SPECTRUM");
  
  // do we have a BITFLAG column?
  has_bitflags_ = tabledesc.isColumn("BITFLAG") && tabledesc.isColumn("BITFLAG_ROW"); 
  dprintf(1)(has_bitflags_?"Found BITFLAG extension in this MS, will look for flags there":"No BITFLAG extension found, using standard FLAG column");
  if( !has_bitflags_ )
    flagmask_ = 0;

  // process the TIME column to figure out the tiling
  ROScalarColumn<Double> timeCol(selms_,"TIME");
  Vector<Double> times = timeCol.getColumn();
  // store time extent in table
  time_range_.resize(2);
  time_range_[0] = times(0);
  time_range_[1] = times(nrows-1);
  header[FTimeExtent] = time_range_;

  // times are sorted. We go over them to discover timeslots, i.e. "chunks" 
  // with the same timestamp. Every time we find a new timeslot, we check if
  //  (a) it's in a new tile (i.e. we've gone past the tilesize)
  //  (b) it's in a different segment (i.e. delta-t has changed)
  // The following variables are used:
  // current tile number
  int current_tile = 0;     // # of current tile
  // current segment within this tile (when using multiple segments per tile)
  int num_subsegment = 0;
  // size of current segment
  int segment_size = 0; 
  // delta-t of current segment
  Double seg_delta = -1;         
  // timestamp of current timeslot
  Double curtime = 0; 
  // number of timeslots per each tile
  tile_sizes_.resize(nrows);     // make big enough, will resize back later
  tile_sizes_[0] = 0;            // first timeslot in first tile
  std::vector<double> start_times(nrows);
  // now loop over all times
  for( int i=0; i<nrows; i++ )
  {
    Double tm = times(i);
    if( i && tm == curtime ) // skip if in same timeslot
      continue;
    // at this point we have a new timeslot
    // this is its delta-t w.r.t. previous timeslot
    Double delta = tm - curtime;
    curtime = tm;
    // add timeslot to the current tile
    if( !tile_sizes_[current_tile] )
      start_times[current_tile] = tm;
    // add timeslot to current subsegment
    segment_size++;
    // if this is the second timeslot in a segment, set the segment's 
    // delta-t value. 
    if( segment_size == 2 )
      seg_delta = delta;
    // else if third+ timeslot, check if delta-t has changed and start
    // a new segment if it has. 
    else if( segment_size>2 && fabs(delta - seg_delta) > .1 )
    {
      num_subsegment++;
      segment_size = 1;  // new subsegment already has this timeslot
      // if tilesegs_>0, then check if we need to start a new tile at
      // this segment
      if( tilesegs_ && num_subsegment >= tilesegs_ )
      {
        // go to the next tile
        tile_sizes_[++current_tile] = 0;
        start_times[current_tile] = tm;
        // start new subsegment with this timeslot
        num_subsegment = 0;
      }
    }
    // add timeslot to current tile
    tile_sizes_[current_tile]++;
    // have we reached the tilesize limit? If so, then we start a new tile
    // (note that if tilesize_=0, this condition is always false)
    if( tile_sizes_[current_tile] == tilesize_ )
    {
      tile_sizes_[++current_tile] = 0;
      num_subsegment = 0;
      segment_size = 0;
    }
  }
  // ok, at this point we've found current_tile+1 tiles, although the last 
  // one may be empty. Resize the size vector as appropriate
  if( tile_sizes_[current_tile] )
    current_tile++;
  tile_sizes_.resize(current_tile);
  start_times.resize(current_tile);
  if( Debug(2) )
  {
    cdebug(2)<<"Found the following tiling: "<<endl;
    for( int i=0; i<current_tile; i++ )
    {
      dprintf(2)("  %d: size %d time %.2f\n",i,tile_sizes_[i],start_times[i]);
    }
  }
  
  // init global tile and timeslot counter
  current_tile_ = current_timeslot_ = 0;
  
  // get the original shape of the data array
  LoShape datashape = ROArrayColumn<Complex>(selms_,dataColName_).shape(0);
  header[FOriginalDataShape] = datashape;
  
  tableiter_.reset();
}

//##ModelId=3DF9FECD0235
int MSInputChannel::init (const DMI::Record &params)
{
  if( FileChannel::init(params) < 0 )
    return state();

  DMI::Record &header = *new DMI::Record;
  ObjRef href(header,DMI::ANONWR); 

  // get MS and selection
  msname_ = params[FMSName].as<string>();
  DMI::Record::Ref empty;
  const DMI::Record *pselection = params[FSelection].as_po<DMI::Record>();
  if( !pselection )
    empty <<= pselection = new DMI::Record;
  // get name of data column (default is DATA)
  dataColName_ = params[FDataColumnName].as<string>("DATA");
  // get # of timeslots or # of segments per tile 
  tilesize_ = params[FTileSize].as<int>(0);
  tilesegs_ = params[FTileSegments].as<int>(0);
//// 15/01/2007: I no longer see the logic of this restriction, so I'm removing it
//  FailWhen( tilesegs_>1 && tilesize_,"Can't specify a "+FTileSize.toString()+
//        " with "+FTileSegments.toString()+">1");
  if( !tilesize_ && !tilesegs_ )
    tilesize_ = 1;
  // bitflag mask
  flagmask_ = params[FFlagMask].as<int>(-1);
  legacy_bitflag_ = params[FLegacyBitflag].as<int>(1);
  tile_bitflag_ = params[FTileBitflag].as<int>(2);
  // hanning tapering?
  apply_hanning_ = params[FApplyHanning].as<bool>(false);

  openMS(header,*pselection);  

  // init common tile format and place it into header
  tileformat_ <<= new VTile::Format;
  VTile::makeDefaultFormat(tileformat_,num_corrs_,num_channels_);
  header[FTileFormat] <<= tileformat_.copy(); 

  tiles_.clear();
  
  setState(HEADER);

  // put header on output stream
  putOnStream(VisEventHIID(HEADER,vdsid_),href);

  return state();
}

//##ModelId=3DF9FECD0244
void MSInputChannel::close (const string &str)
{
  FileChannel::close(str);
  // close & detach from everything
  Mutex::Lock lock(aipspp_mutex);
  selms_ = MeasurementSet();
  ms_ = MeasurementSet();
  tileformat_.detach();
}

// declare blitz stencil for Hanning tapering
BZ_DECLARE_STENCIL2(hanning_stencil,A,B)
  A = (.5*B(0,0,0) + .25*B(0,1,0) + .25*B(0,-1,0));
BZ_END_STENCIL_WITH_SHAPE(blitz::shape(0,-1,0),blitz::shape(0,1,0))

//##ModelId=3DF9FECD021B
int MSInputChannel::refillStream ()
{
  Mutex::Lock lock(aipspp_mutex);
  try
  {
    if( state() == HEADER )
      setState(DATA);
    else if( state() != DATA ) // return CLOSED when no more data
    {
      return AppEvent::CLOSED;
    }
  // loop until some tiles are generated
    int nout = 0;
    while( !nout )
    {
    // End of table iterator? Generate footer and close MS
      if( tableiter_.pastEnd() )
      {
        setState(FOOTER);
        DMI::Record::Ref footer(DMI::ANONWR);
        footer()[FVDSID] = vdsid_; 
        putOnStream(VisEventHIID(FOOTER,vdsid_),footer);
        selms_ = MeasurementSet();
        ms_ = MeasurementSet();
        tileformat_.detach();
        return AppEvent::SUCCESS;
      }
      const LoRange ALL = LoRange::all();
      const LoRange CHANS = LoRange(channels_[0],channels_[1],channel_incr_);
    // fill cache with next time interval
      if( tiles_.empty() )
        tiles_.resize(num_ifrs_);
      // loop until we've got the requisite number of timeslots
      FailWhen(uint(current_tile_)>=tile_sizes_.size(),
          "inconsistency in MS: TableIterator yields more timeslots than expected");
      int current_tilesize = tile_sizes_[current_tile_];
      // the tile_times vector will be assigned to the TIME column of each
      // tile. 0 times are used to indicate rows that are missing in EVERY
      // tile.
      LoVec_double tile_times(current_tilesize);
      tile_times(LoRange::all()) = 0;
      for( int ntimes = 0; ntimes < current_tilesize && !tableiter_.pastEnd(); ntimes++,tableiter_++ )
      {
        const Table &table = tableiter_.table();
        int nrows = table.nrow();
        FailWhen( !nrows,"unexpected empty table iteration");
        dprintf(4)("Table iterator yields %d rows\n",table.nrow());
        // get relevant table columns
        ROScalarColumn<Double> timeCol(table,"TIME");
        double timeslot = timeCol(0); // same for all rows since we iterate over it
        ROScalarColumn<Double> intCol(table,"EXPOSURE");
        ROScalarColumn<Int> ant1col(table,"ANTENNA1");
        ROScalarColumn<Int> ant2col(table,"ANTENNA2");
        ROScalarColumn<Bool> rowflagCol(table,"FLAG_ROW");
        LoCube_float weightcube;
        tile_times(ntimes) = timeslot;
        if( !ntimes )
        {
          dprintf(2)("Tile %d: time is %.2f\n",current_tile_,timeslot);
        }
        else if( ntimes == current_tilesize-1 )
        {
          dprintf(2)("Tile %d: ending time is %.2f\n",current_tile_,timeslot);
        }
        // WEIGHT is optional
        Cube<Float> weightcube1;
        if( has_weights_ )
        {
          try
          { 
            weightcube1 = ROArrayColumn<Float>(table,"WEIGHT_SPECTRUM").getColumn();
            weightcube.reference(B2A::refAipsToBlitz<float,3>(weightcube1));
            weightcube.reference(weightcube(ALL,CHANS,ALL));
            cdebug(5)<<"WEIGHT_SPECTRUM: "<<weightcube;
          }
          catch( ... )
          {}
        }
        cdebug(5)<<"WEIGHT_SPECTRUM: "<<weightcube(ALL,ALL,0);
        // get array columns as Lorrays
        Matrix<Double> uvwmat1 = ROArrayColumn<Double>(table, "UVW").getColumn();
        LoMat_double uvwmat = B2A::refAipsToBlitz<double,2>(uvwmat1);
        Cube<Complex> datacube1 = ROArrayColumn<Complex>(table, dataColName_).getColumn();
        LoCube_fcomplex datacube = B2A::refAipsToBlitzComplex<3>(datacube1);
        // apply taper
//        if( apply_hanning_ )
//        {
//          cdebug(0)<<"before: "<<abs(datacube(0,10,0));
//          LoCube_fcomplex tapered_data(datacube.shape());
//          blitz::applyStencil(hanning_stencil(),tapered_data,datacube);
//          datacube.reference(tapered_data);
//          cdebug(0)<<"after: "<<abs(datacube(0,10,0));
//        }
        if( apply_hanning_ )
        {
          LoShape shape = datacube.shape();
          LoCube_fcomplex tapered_data(shape);
          for( int i=0; i<shape[0]; i++ )
            for( int j=0; j<shape[2]; j++ )
            {
              tapered_data(i,0,j) = datacube(i,0,j);
              tapered_data(i,shape[1]-1,j) = datacube(i,shape[1]-1,j);
              for( int k=1; k<shape[1]-1; k++ )
                tapered_data(i,k,j) = .50*datacube(i,k,j)+
                                      .25*datacube(i,k-1,j)+
                                      .25*datacube(i,k+1,j);
            }
          datacube.reference(tapered_data);
        }
        LoCube_int bitflagcube;
        LoVec_int bitflagvec;
        bool hasflags = false;
        // read bitflag columns, if available
        if( has_bitflags_ & flagmask_ )
        {
          Cube<Int> bitflagcube1 = ROArrayColumn<Int>(table,"BITFLAG").getColumn();
          B2A::copyArray(bitflagcube,bitflagcube1);
          bitflagcube &= flagmask_;
          Vector<Int> bitflagvec1 = ROScalarColumn<Int>(table,"BITFLAG_ROW").getColumn();
          B2A::copyArray(bitflagvec,bitflagvec1);
          bitflagvec &= flagmask_;
          if( tile_bitflag_ )
          {
            bitflagcube = where(bitflagcube,tile_bitflag_,0);
            bitflagvec = where(bitflagvec,tile_bitflag_,0);
          }
          hasflags = true;
        }
        // read legacy flag columns, if available
        if( legacy_bitflag_ )
        {
          Cube<Bool> flagcube1 = ROArrayColumn<Bool>(table,"FLAG").getColumn();
          LoCube_bool flagcube = B2A::refAipsToBlitz<bool,3>(flagcube1);
          if( !hasflags ) // array not initialized above
          {
            bitflagcube.resize(flagcube.shape());
            bitflagcube = where(flagcube,legacy_bitflag_,0);
          }
          else
            bitflagcube |= where(flagcube,legacy_bitflag_,0);
          Vector<Bool> bitflagrow1 = ROScalarColumn<Bool>(table,"FLAG_ROW").getColumn();
          LoVec_bool bitflagrow = B2A::refAipsToBlitz<bool,1>(bitflagrow1);
          if( !hasflags )
          {
            bitflagvec.resize(bitflagrow.shape());
            bitflagvec = where(bitflagrow,legacy_bitflag_,0);
          }
          else
            bitflagvec |= where(bitflagrow,legacy_bitflag_,0);
          hasflags = true;
        }
        // apply channel selection
        datacube.reference(datacube(ALL,CHANS,ALL));
        if( hasflags )
          bitflagcube.reference(bitflagcube(ALL,CHANS,ALL));
        // check weightcube shape (WSRT gets it wrong), disable weights on first error
        if( has_weights_ && weightcube.shape() != datacube.shape() )
        {
          cdebug(0)<<"WEIGHT_SPECTRUM column malformed, weights will be ignored\n";
          has_weights_ = false;
        }
        // flip along frequency axis, if asked to
        cdebug(5)<<"WEIGHT_SPECTRUM: "<<weightcube(ALL,ALL,0);
        if( flip_freq_ )
        {
          datacube.reverseSelf(blitz::secondDim);
          if( hasflags )
            bitflagcube.reverseSelf(blitz::secondDim);
          if( has_weights_ )
            weightcube.reverseSelf(blitz::secondDim);
        }
        // get vector of row numbers 
        Vector<uInt> rownums = table.rowNumbers(ms_);
    // now process rows one by one
        for( int i=0; i<nrows; i++ )
        {
          int ant1 = ant1col(i), ant2 = ant2col(i);
          int ifr = ifrNumber(ant1,ant2);
    // init tile if one is not ready 
          VTile *ptile;
          if( tiles_[ifr].valid() )
            ptile = tiles_[ifr].dewr_p();
          else
          {
            tiles_[ifr] <<= ptile = new VTile(tileformat_,current_tilesize);
            // set tile ID
            ptile->setTileId(ant1col(i),ant2col(i),current_tile_,vdsid_);
            // init all row flags to missing
            ptile->wrowflag() = FlagMissing;
          }
          ptile->winterval()(ntimes) = intCol(i);
          ptile->wuvw()(ALL,ntimes)  = uvwmat(ALL,i);
          ptile->wdata()(ALL,ALL,ntimes) = datacube(ALL,ALL,i);
          if( has_weights_ )
          {
            cdebug(6)<<"weights for timeslot "<<ntimes<<" ifr "<<ant1<<"-"<<ant2<<":"<<weightcube(ALL,ALL,i)<<endl;
            ptile->wweight()(ALL,ALL,ntimes) = weightcube(ALL,ALL,i);
            cdebug(6)<<"weights for timeslot after assignment "<<ptile->wweight()(ALL,ALL,ntimes)<<endl;
          }
          if( hasflags )
          {
            ptile->wrowflag()(ntimes) = bitflagvec(i);
            ptile->wflags()(ALL,ALL,ntimes) = bitflagcube(ALL,ALL,i);
          }
          else
          {
            ptile->wrowflag()(ntimes) = 0;
            ptile->wflags()(ALL,ALL,ntimes) = 0;
          }
          ptile->wseqnr()(ntimes) = rownums(i);
        }
        current_timeslot_++;
      }
      current_tile_++;
      // output all valid collected tiles onto stream, but do fill in
      // their TIME column so that it's the same for all tiles regardless
      // of what rows are actually found
      for( uint i=0; i<tiles_.size(); i++ )
      {
        if( tiles_[i].valid() )
        {
          VTile &tile = tiles_[i];
          tile.wtime() = tile_times;
          HIID id = VisEventHIID(DATA,tiles_[i]->tileId());
          putOnStream(id,tiles_[i]);
          tiles_[i].detach();
          nout++;  // increment pointer so that we break out of loop
        }
      }
      dprintf(2)("tile yielded %d baselines\n",nout);
      cdebug(3)<<"tile times are "<<LoVec_double(tile_times-4646800000.)<<endl;
    }
    return AppEvent::SUCCESS;
  }
  // catch AIPS++ errors, but not our own exceptions -- these can only be
  // caused by real bugs
  catch( AipsError &err )
  {
    tiles_.clear();
    close("AIPS++ error: "+err.getMesg());
    return AppEvent::CLOSED;
  }
  return AppEvent::CLOSED;
}

//##ModelId=3DFDFC060373
string MSInputChannel::sdebug ( int detail,const string &prefix,const char *name ) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"MSInputChannel",this);
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"MS %s (%d rows)",msname_.c_str(),selms_.nrow());
  }
  if( detail >= 2 || detail <= -2 )
  {
    appendf(out,"timeslot %d, state %s",current_timeslot_,stateString().c_str());
  }
  return out;
}


} // namespace AppAgent


//  MSVisInputAgent.h: agent for reading an AIPS++ MS
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

#ifndef _MSVISAGENT_MSVISINPUTAGENT_H
#define _MSVISAGENT_MSVISINPUTAGENT_H 1

#include <AppUtils/MSChannelDebugContext.h>
#include <AppUtils/MSChannelVocabulary.h>
#include <VisCube/VisVocabulary.h>
#include <VisCube/VTile.h>

#include <casacore/ms/MeasurementSets/MeasurementSet.h>
#include <casacore/tables/Tables/TableIter.h>
#include <AppAgent/FileChannel.h>

namespace AppAgent
{
using namespace DMI;

using namespace VisCube;
using namespace VisVocabulary;

//##ModelId=3DF9FECD013C
//##Documentation
//## MSVisInputAgent is an input agent for reading data from an AIPS++
//## Measurement Set. It is initialized from a DMI::Record laid out as follows:
//##
//## rec[MSVisInputAgentParams]  (record)    contains all parameters below
//##    +--[FMSName]             (string)    MS filename (must be present)
//##    +--[FDataColumnName]     (string)    column to read tile DATA visibilities from
//##                                         (default is "DATA", but can use, any column)
//##    +--[FPredictColumnName]  (string)    column to read tile PREDICT visibilities from
//##                                         (default is none)
//##    +--[FTileSize]           (int)       tile size (default: 1 timeslot)
//##    +--[FTimeIncrement]      (int)       time stepping (in timeslots), default is 1
//##    +--[FFlagMask]           (int)       apply flag mask to input bitflags (if available). 0 for no flags.
//##                                         Default is -1 (all flags).
//##    +--[FLegacyBitflag]      (int)       bitflag(s) corresponding to legacy FLAG column (default 1).
//##                                         0 to ignore legacy flags.
//##    +--[FTileBitflag]        (int)       tile bitflag to set corresponding to input bitflags (default 2).
//##                                         If 0, then tile bitflag is
//##                                           ms_bitflags&flag_mask | (ms_legacy_flag?legacy_bitflag:0)
//##                                         If !=0, then tile bitflag is
//##                                           (ms_bitflags&flag_mask?tile_bitflag:0).| (ms_legacy_flag?legacy_bitflag:0)
//##    +--[FApplyHanning]       (bool)      apply Hanning taper to input data
//##    +--[FSelection]          (record)    determines MS selection:
//##       +--[FDDID]              (int)     selects data description ID
//##       +--[FFieldIndex]        (int)     selects field
//##       +--[FChannelStartIndex] (int)     starting channel (default: 0)
//##       +--[FChannelEndIndex]   (int)     ending channel (default: last chan.)
//##       +--[FChannelIncrement]  (int)     channel increment step (default: 1)
//##       +--[FAutoCorr]          (bool)    selects auto-correlations if True (default is False)
//##       +--[FSelectionString] (string)    additional TaQL selection applied
//##                                           to MS
class MSInputChannel : public FileChannel
{
  public:
    //##ModelId=3DF9FECD0219
      MSInputChannel ();

    //##ModelId=3DF9FECD0235
      virtual int init (const DMI::Record &data);

    //##ModelId=3DF9FECD0244
      virtual void close (const string &str="");

    //##ModelId=3DFDFC060373
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;

    //##ModelId=400E5B6C0098
      ImportDebugContext(MSChannelDebugContext);

  protected:
    //##ModelId=3EC252C1000E
    //##Documentation
    //## called to put more objects on the stream. Returns SUCCESS if something
    //## was put on, or <0 code (ERROR/CLOSED/whatever)
    virtual int refillStream();

  private:
      //##ModelId=3DF9FECD0142
      typedef vector<VTile::Ref> TileCache;

    //##ModelId=3DF9FECD0248
      MSInputChannel(const MSInputChannel &right);
    //##ModelId=3DF9FECD0253
      MSInputChannel& operator = (const MSInputChannel &right);

      // prepares MS for reading
    //##ModelId=3DF9FECD025E
      void openMS     (DMI::Record &hdr,const DMI::Record &selection);
      // fills headers from subtables
    //##ModelId=3DF9FECD0285
      void fillHeader (DMI::Record &hdr,const DMI::Record &selection);


    //##ModelId=3DFDFC06033A
      string msname_;
    //##ModelId=3DF9FECD0199
      casacore::MeasurementSet ms_;
    //##ModelId=3DF9FECD019A
      casacore::MeasurementSet selms_;

      // VDS id
    //##ModelId=3E00AA5101A0
      VDSID vdsid_;
      // observation ID -- this is incremented by 1 for each MS
    //##ModelId=3DF9FECD01A9
      int obsid_;

      // name of data column used
    //##ModelId=3DF9FECD01B0
      string dataColName_;
      string predictColName_;

      // MS tiling specification
      //  * if tilesegs_>1, then each tile will be composed of the specified
      //    number of segments; tilesize_ must be 0.
      //  * if tilesegs_=1 and tilesize_=0, there will be one tile per
      //    segment
      //  * if tilesegs_=1 and tilesize_>0, each segment will be broken up
      //    into tiles of the requested size
      //  * if tilesegs_=0 and tilesize_>0, no segmentation is done, and each
      //    tile will simply have the requsite number of timeslots
      //  * if both are 0, tilesize_=1 will be used.
    //##ModelId=3DF9FECD01C0
      int tilesize_;
      int tilesegs_;
      // * the time increment. 1 means read every time slot. 2 means read every second timeslot.
      int time_incr_;

      // channel subset
    //##ModelId=3DF9FECD01C8
      int channels_[2];         // integer channel indices
      // channel increment
      int channel_incr_;
      // various counts
    //##ModelId=3DF9FECD01D0
      int num_channels_;
    //##ModelId=3DF9FECD01D7
      int num_corrs_;
    //##ModelId=3DF9FECD01DF
      int num_antennas_;
    //##ModelId=3DF9FECD01E6
      int num_ifrs_;

      //## flag: flip frequency axis. Output frequencies will always be
      //## in increasing order; if MS freqs are decreasing, then the freq axis
      //## must be flipped. This flag is set in fillHeader()
      bool flip_freq_;

      bool has_bitflags_;
      int flagmask_;
      int legacy_bitflag_;
      int tile_bitflag_;

      // apply preprocessing to data column
      bool apply_hanning_;
      double channel_width_factor_;
      bool invert_phases_;

      //## true is MS has a valid WEIGHT_SPECTRUM column
      bool has_weights_;

      // count of timeslots already returned
    //##ModelId=3DFDFC060354
      int current_timeslot_;

      // this gives the default exposure time associated with each timeslot
      std::vector<double> exposure_times_;

      // current MS chunk number. A chunk contains N timeslots (i.e. all
      // the per-ifr tiles for a particular time tile)
      int chunk_num_;

      // this gives the size of each successive MS tile
      std::vector<int>  tile_sizes_;
      // this gives the current tile number
      int current_tile_;

      // range of times in current selection
      std::vector<double> time_range_;
      
      typedef std::map<std::pair<int,int>,LoVec_double> PrevUVWMap;
      PrevUVWMap prev_uvw_;

      // iterator
    //##ModelId=3DF9FECD01EE
      casacore::TableIterator tableiter_;

      // tile format
    //##ModelId=3DF9FECD01F6
      VTile::Format::Ref tileformat_;

      //##ModelId=3DF9FECD020D
      TileCache::iterator tileiter_;

      //##ModelId=3DF9FECD01FF
      TileCache tiles_;

};

};
#endif

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

#ifndef MSVISAGENT_SRC_MSSEQOUTPUTCHANNEL_H_HEADER_INCLUDED_F5146265
#define MSVISAGENT_SRC_MSSEQOUTPUTCHANNEL_H_HEADER_INCLUDED_F5146265
    
#include <AppUtils/MSOutputChannel.h>

namespace AppAgent
{
using namespace DMI;
  
using namespace VisCube;
using namespace VisVocabulary;

//##ModelId=3E02FF340070
class MSSeqOutputChannel : public MSOutputChannel
{
  public:
    //##ModelId=3E2831C7010D
    MSSeqOutputChannel ();

    //## Applications call close() when they're done speaking to an agent.
    virtual void close(const string &str="");

    //##ModelId=3E283172001B
    string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    
  protected:
      
    virtual void doPutHeader(const DMI::Record &header);

    virtual void doPutTile (const VTile &tile);
    
    virtual void doPutFooter(const DMI::Record &footer);

    void flushOutputTiles ();
    
    // map from table row numbers -> (tile,row) pair
    typedef struct { int tile_num,tile_row; } TileMapping;
    std::vector<TileMapping> row_to_tile_;
    
    // vector of tiles for current chunk in time
    std::vector<VTile::Ref> tiles_;
    
    // number of rows in  MS
    int ms_num_rows_;
    // range of active rows for current time chunk
    int min_ms_row_;
    int max_ms_row_;
    // current time chunk sequence number
    int current_seqnr_;
    
    
    
  private:
    //##ModelId=3E2831C7011D
    MSSeqOutputChannel(const MSSeqOutputChannel& right);

    //##ModelId=3E2831C70155
    MSSeqOutputChannel& operator=(const MSSeqOutputChannel& right);
    

};


} // namespace AppAgent
#endif /* MSVISAGENT_SRC_MSVISOUTPUTAGENT_H_HEADER_INCLUDED_F5146265 */

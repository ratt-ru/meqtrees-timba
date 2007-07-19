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

#ifndef MEQSERVER_SRC_VISDATAMUX_H_HEADER_INCLUDED_82375EEB
#define MEQSERVER_SRC_VISDATAMUX_H_HEADER_INCLUDED_82375EEB

#include <AppAgent/EventChannel.h>
#include <MeqServer/VisHandlerNode.h>
#include <MeqServer/TID-MeqServer.h>
#include <VisCube/VisVocabulary.h>
#include <vector>
    
#pragma types #Meq::VisDataMux
#pragma aid Station Index Tile Format Start Pre Post Sync Chunks 
#pragma aid Open Closed Current Timeslots

namespace Meq 
{

class Spigot;
class Sink;
  
//##ModelId=3F98DAE503DA
class VisDataMux : public Node
{
  public:
    //##ModelId=3F9FF71B006A
    VisDataMux ();
  
    virtual TypeId objectType() const
    { return TpMeqVisDataMux; }

    //##ModelId=3F98DAE6024A
    //##Documentation
    //## delivers visdata header to data mux
    int deliverHeader (const DMI::Record &header);
      
    //##ModelId=3F98DAE60251
    //##Documentation
    //## delivers tile to data mux
    //## rowrange specifies range of valid rows in tile
    int deliverTile (VisCube::VTile::Ref &tileref);

    //##Documentation
    //## delivers visdata footer to data mux
    int deliverFooter (const DMI::Record &footer);
    
    // helper func:
    // returns Meq::Cells object corresponding to a VisCube::VTile, plus range
    // of valid rows
    //##ModelId=3F9FF6970269
    void fillCells (Cells &cells,LoRange &range,const VisCube::VTile &tile);

    //##ModelId=3F98DAE60246
    LocalDebugContext;
    
  protected:
    void setStateImpl (DMI::Record::Ref &rec,bool initializing);
  
    // redefined to check that children are Sinks and stepchildren are Spigots
    virtual void checkChildren ();
    
    int  pollChildren (Result::Ref &resref,
                      std::vector<Result::Ref> &childres,
                      const Request &request);
    
  private:
    //##ModelId=3F9FF71B00C7
    VisDataMux (const VisDataMux &);

    void initInput (const DMI::Record &rec);
    void initOutput (const DMI::Record &rec);
    
    void clearOutput ();
    
    void postStatus ();
    
    int startSnippet (const VisCube::VTile &tile);
    int endSnippet   ();
    
    //##ModelId=3F992F280174
    static int formDataId (int sta1,int sta2)
    { return VisVocabulary::ifrNumber(sta1,sta2); }

    //##ModelId=3F99305003E3
    typedef std::set<VisHandlerNode *> HandlerSet;
    typedef std::set<int> IndexSet;
    
    //##ModelId=3F98DAE60247
    // set of all handlers for each data ID (==IFR)
    std::vector<HandlerSet> handlers_;
    // set of children numbers for each data ID (==IFR)
    std::vector<IndexSet> child_indices_;
    // set of flags: do we have a tile for this data ID (==IFR)
    std::vector<bool> have_tile_;
    
    //  list of columns to be added to output tiles
    //##ModelId=3FAA52A6008E
    typedef std::set<int> ColumnSet;
    ColumnSet output_columns_;
    
    // header is cached; it is dumped to output only if some tiles are being
    // written
    DMI::Record::Ref cached_header_;
    // flag: tiles are being written
    bool writing_data_;

    LoVec_double channel_freqs;
    LoVec_double channel_widths;  
    // flag: require a fully regular cells (single-segment)
    bool force_regular_grid;
    
    RequestId rqid_;
    // id of next request
    RequestId next_rqid_;
    
    Request::Ref current_req_;
    int current_seqnr_;
    LoRange current_range_;
    
    int max_tiles_;  // max number of input tiles -- rest are ignored

    int num_chunks_;
    int num_tiles_;
    int num_ts_;                    // number of timeslots seen
    std::vector<int> tile_ts_;      // range of timeslot indices for current tile
    std::vector<double> tile_time_; // range of times for current tile
    std::vector<double> time_extent_; // range of times for full stream (from header)
    AppAgent::EventChannel::Ref  input_channel_;    
    AppAgent::EventChannel::Ref  output_channel_;    
};

} // namespace Meq

#endif /* MEQSERVER_SRC_SPIGOTMUX_H_HEADER_INCLUDED_82375EEB */

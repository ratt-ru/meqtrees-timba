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

#ifndef MEQSERVER_SRC_SINK_H_HEADER_INCLUDED_9B1ECA78
#define MEQSERVER_SRC_SINK_H_HEADER_INCLUDED_9B1ECA78
    
#include <MeqServer/VisHandlerNode.h>
#include <MeqServer/TID-MeqServer.h>

#pragma aid Sink 
#pragma aid Output Col Corr Index
#pragma types #Meq::Sink

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqSink
//  A MeqSink is attached to a VisAgent data source. A MeqSink represents
//  one interferometer. For every matching VisCube::VTile at the input of the 
//  source, it generates a MeqRequest corresponding to the domain/cells 
//  of the tile, and optionally stores the result back in the tile.
//  A MeqSink must have exactly one child. The child may return a 
//  multi-plane result.
//field: station_1_index 0
//  Index (1-based) of first station comprising the interferometer
//field: station_2_index 0
//  Index (1-based) of second station comprising the interferometer
//field: output_col ''
//  tile column to write results to: DATA, PREDICT or RESIDUALS for 
//  correlation data, but other columns may be used too,
//  If empty, then no output is generated.
//field: corr_index []
//  Defines mappings from result vellsets to correlations. If empty, then
//  a default one-to-one mapping is used, and an error will be thrown if
//  sizes mismatch. Otherwise, should contain one correlation index (1-based) 
//  per each vellset (0 to ignore that vellset). Note that tensor 
//  results are decomposed in row-major order, [[1,2],[3,4]].
//field: flag_mask 0
//  If non-0, then any data flags in the result are ANDed with this mask
//  and written to the FLAGS column of the output tile. If 0, then no
//  tile flags are generated. Use -1 for a full flag mask.
//field: flag_bit 
//  Output flag bit. If non-0, overrides flag behaviour as follows:
//  the dataflags are AND-ed with flag_mask, and the output is flagged with
//  flag_bit wherever the result of this operation is not 0.
//defrec end
    
namespace Meq {

//##ModelId=3F98DAE503B5
class Sink : public VisHandlerNode
{
  public:
    Sink ();  

    virtual int deliverHeader (const DMI::Record &,
                               const VisCube::VTile::Format &);
    
    virtual int deliverTile   (const Request &,VisCube::VTile::Ref &,const LoRange &);
    
    virtual int deliverFooter (const DMI::Record &);
    
    int getOutputColumn () const
    { return output_col; }
    
    //##ModelId=3F98DAE60222
    virtual TypeId objectType() const
    { return TpMeqSink; }
    
    LocalDebugContext;
    
  protected:
    //##ModelId=3F98DAE60217
    virtual int getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &req,bool newreq);
  
    //##ModelId=3F9918390169
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  private:
    // current tile stored here
    VisCube::VTile::Ref cur_tile;
    LoRange cur_range;
    RequestId cur_rqid;
    
    VisCube::VTile::Format::Ref output_format;
      
    // processes pending tile, if any
    int procPendingTile (VisCube::VTile::Ref &tileref);
  
    // maps plane to output correlation
    //##ModelId=400E5B6D0048
    int mapOutputCorr (int iplane);
    
    template<class T,class U>
    void fillTileColumn (T *coldata,const LoShape &colshape,
                         const LoRange &rowrange,
                         const blitz::Array<U,2> &arr,int icorr);
    template<class T>
    void zeroTileColumn (T *coldata,const LoShape &colshape,
                         const LoRange &rowrange,int icorr);
      
    //##ModelId=3F98DAE60211
    string output_colname;
    int output_col;
    //##ModelId=3F9918390123
    vector<int> output_icorrs;
    
    int flag_mask;
    int flag_bit;
//    int row_flag_mask;
    
//    HIID uvw_node_group;
//    string uvw_node_name;
    
};

}

#endif /* MEQSERVER_SRC_SPIGOT_H_HEADER_INCLUDED_9B1ECA78 */

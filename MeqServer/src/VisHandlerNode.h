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

#ifndef MEQSERVER_SRC_VISHANDLERNODE_H_HEADER_INCLUDED_9B1ECA78
#define MEQSERVER_SRC_VISHANDLERNODE_H_HEADER_INCLUDED_9B1ECA78
    
#include <MEQ/Node.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <VisCube/VTile.h>
#include <MeqServer/AID-MeqServer.h>

#pragma aid VisHandlerNode 
#pragma aid Station Index Data Id Num Antenna Tile Format Input 
#pragma aid Output Col Corr Next Read Flag Flags Mask Row Mandate Regular Grid
#pragma aid UVW Node Name Group
    
namespace Meq 
{
  
const HIID  FStation1Index = AidStation|1|AidIndex,
            FStation2Index = AidStation|2|AidIndex,
            FNumStations   = AidNum|AidAntenna,
            FTileFormat    = AidTile|AidFormat,
            FDataId        = AidData|AidId,

            FOutputColumn = AidOutput|AidCol,
            FInputColumn  = AidInput|AidCol,
//            FFlagMask     already defined in MeqVocabulary
            FRowFlagMask  = AidRow|AidFlag|AidMask,
            FCorrIndex    = AidCorr|AidIndex,
            FNext         = AidNext,
            FUVWNodeName  = AidUVW|AidNode|AidName,
            FUVWNodeGroup = AidUVW|AidNode|AidGroup,
            
// this is a MeqServer config flag, default true
            FMandateRegularGrid = AidMandate|AidRegular|AidGrid;
    

class Cells;

//##ModelId=3F98DAE60009
class VisHandlerNode : public Node
{
  public:
    //##ModelId=3F98DAE60319
    VisHandlerNode (int nchildren=-1,const HIID *labels=0);
      
    //##ModelId=3F98DAE60327
    int dataId () const;
    
    const HIID & ifrId () const;
    
    //##Documentation
    //## Alerts node that a vistile stream is starting.
    //## The desired output format (with any extra columns added in) is
    //## is passed in here.
    virtual int deliverHeader (const DMI::Record &,
                               const VisCube::VTile::Format &)
    { return 0; }

    //##ModelId=3F98DAE60344
    //##Documentation
    //## Delivers a VisCube::VTile to the node.
    //## req is the request generated using this VisCube::VTile
    //## tileref is a ref to the tile (will be detached)
    //## range is the range of valid rows to use
    //## Returns result state (see Node::RES_xxx constants), which can be
    //## Node::RES_FAIL for failure, or a combination of the following
    //## bit flags:
    //##    RES_WAIT    result not yet available, must wait
    //##    RES_UPDATED result available and tile was updated, output tile is
    //##                attached to tileref
    virtual int deliverTile   (const Request &,VisCube::VTile::Ref &,const LoRange &) { return 0; }
                         
    //##Documentation
    //## Alerts node that a visdata stream is finished.
    //## Returns result state (see Node::RES_xxx constants), which can be
    //## Node::RES_FAIL for failure, or a combination of the following
    //## bit flags:
    //##    RES_WAIT    must wait (please call again)
    //##    RES_UPDATED last tile was updated, output tile is attached to tileref
    virtual int deliverFooter (const DMI::Record &) { return 0; };
    
    //##ModelId=3F98DAE602DA
    LocalDebugContext;
    
  protected:
    //##ModelId=400E5B6E01FA
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

        
  private:
    //##ModelId=3F98DAE602F6
    int data_id;
  
    HIID ifr_id;
};

//##ModelId=3F98DAE60327
inline int VisHandlerNode::dataId () const   
{ return data_id; }


}

#endif /* MEQSERVER_SRC_SPIGOT_H_HEADER_INCLUDED_9B1ECA78 */

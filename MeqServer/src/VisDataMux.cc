//#  VisDataMux.cc
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#include "VisDataMux.h"
#include "AID-MeqServer.h"
#include <VisCube/VisVocabulary.h>
#include <MEQ/Forest.h>
#include <MEQ/Cells.h>
#include <MEQ/Request.h>
#include <AppAgent/AppControlAgent.h>

using namespace AppControlAgentVocabulary;
using namespace VisVocabulary;
using namespace VisAgent;

const HIID Meq::VisDataMux::EventCreate = AidCreate;
const HIID Meq::VisDataMux::EventDelete = AidDelete; 
    
//##ModelId=3F9FF71B006A
Meq::VisDataMux::VisDataMux (Meq::Forest &frst)
    : forest_(frst)
{
  // use reasonable default
  handlers_.resize(VisVocabulary::ifrNumber(30,30)+1);
}

//##ModelId=3FA1016000B0
void Meq::VisDataMux::init (const DataRecord &rec,
                VisAgent::InputAgent  & inp,
                VisAgent::OutputAgent & outp,
                AppControlAgent       & ctrl)
{
  input_ = &inp;
  output_ = &outp;
  control_ = &ctrl;
  
  out_columns_.clear();
  out_colnames_.clear();
  // setup output column indices
  if( rec[FOutputColumn].exists() )
  {
    out_colnames_ = rec[FOutputColumn];
    out_columns_.resize(out_colnames_.size());
    const VisTile::NameToIndexMap &colmap = VisTile::getNameToIndexMap();
    for( uint i=0; i<out_colnames_.size(); i++ )
    {
      VisTile::NameToIndexMap::const_iterator iter = 
          colmap.find(out_colnames_[i] = struppercase(out_colnames_[i]));
      FailWhen(iter==colmap.end(),"unknown output column "+out_colnames_[i]);
      out_columns_[i] = iter->second;
      cdebug(2)<<"indicated output column: "<<out_colnames_[i]<<endl;
    }
  }
  force_regular_grid = rec[FMandateRegularGrid].as<bool>(false);
}

int Meq::VisDataMux::receiveEvent (const EventIdentifier &evid,const ObjRef::Xfer &,void *ptr)
{
  if( evid.id() == EventCreate )
    addNode( *static_cast<Node*>(ptr) );
  else if( evid.id() == EventDelete )
  {
    if( ptr )
      removeNode( *static_cast<Node*>(ptr) );
    else // null ptr means all nodes
      handlers_.clear();
  }
  // ignore all other events
  return 0;
}

//##ModelId=3F716E98002E
void Meq::VisDataMux::addNode (Node &check_node)
{
  // return if the node is not a VisHandlerNode
  VisHandlerNode *node = dynamic_cast<VisHandlerNode*>(&check_node);
  if( !node )
    return;
  cdebug(2)<<"node is a visdata handler, adding to data mux\n";
  // form data ID from state record
  const DataRecord &state = node->state();
  int did;
  try
  {
    did = formDataId(state[FStation1Index].as<int>(),
                     state[FStation2Index].as<int>());
  }
  catch(...)
  {
    Throw(node->objectType().toString()+
          " state record is missing station and/or correlation identifiers");
  }
  // let the node know about its data id
  node->setDataId(did);
  // add list of handlers for this data id (if necessary)
  if( did >= int(handlers_.size()) )
    handlers_.resize(did+100);
  // add node to list of handlers
  VisHandlerList &hlist = handlers_[did];
  VisHandlerList::const_iterator iter = hlist.begin();
  // ... though not if it's already there on the list
  for( ; iter != hlist.end(); iter++ )
    if( *iter == node )
      return;
  hlist.push_back(node); 
}

//##ModelId=3F716EAA0106
void Meq::VisDataMux::removeNode (Node &check_node)
{
  // return if the node is not a VisHandlerNode
  VisHandlerNode *node = dynamic_cast<VisHandlerNode*>(&check_node);
  if( !node )
    return;
  cdebug(2)<<"node is a visdata handler, removing from spigot mux\n";
  int did = node->dataId();
  if( did < 0 )
  {
    cdebug(2)<<"no data ID in node: not attached to this spigot mux?\n";
    return;
  }
  // erase from handler list
  VisHandlerList &hlist = handlers_[did];
  VisHandlerList::iterator iter = hlist.begin();
  for( ; iter != hlist.end(); iter++ )
    if( *iter == node )
    {
      hlist.erase(iter);
      break;
    }
}

//##ModelId=3F992F280174
int Meq::VisDataMux::formDataId (int sta1,int sta2)
{
  return VisVocabulary::ifrNumber(sta1,sta2);
}

void Meq::VisDataMux::fillCells (Cells &cells,LoRange &range,const VisTile &tile)
{    
  // figure out range of valid rows
  LoVec_bool valid( tile.rowflag() != int(VisTile::MissingData) );
  cdebug1(6)<<"valid rows: "<<valid<<endl;
  // find first valid row, error if none
  int i0,i1;
  for( i0=0; !valid(i0); i0++ )
    if( i0 >= tile.nrow() )
    { Throw("tile does not contain any valid rows"); }
  cdebug1(5)<<"valid row range: "<<i0<<":"<<i1<<endl;
  // find last valid row (error condition above enures that at least one exists)
  for( i1=tile.nrow()-1; !valid(i1); i1-- );
  // form a LoRange describing valid rows, extract time/interval for them
  range = makeLoRange(i0,i1);
  LoVec_double time1     = tile.time()(range).copy();
  LoVec_double interval1 = tile.interval()(range).copy();
  // now, for any rows missing _within_ the valid range, fill in interpolated
  // times (just to keep Cells & co. happy)
  int j=1;
  for( int i=i0+1; i<i1; i++,j++ ) // no need to look at start/end rows -- always valid
    if( !valid(i) )
      time1(j) = time1(j-1) + ( interval1(j) = interval1(j-1) );
  cdebug1(5)<<"time:     "<<time1<<endl;
  cdebug1(5)<<"interval: "<<interval1<<endl;
  cells.setCells(FREQ,channel_freqs,channel_widths);
  cells.setCells(TIME,time1,interval1);
  cells.recomputeDomain();
  cells.recomputeSegments(FREQ);
  cells.recomputeSegments(TIME);
  cells.recomputeDomain();
  cdebug1(5)<<"cells: "<<cells;
  if( force_regular_grid )
  {
    FailWhen(cells.numSegments(TIME)>1 || cells.numSegments(FREQ)>1,
        "tile has irregular grid, we're configured for regular grids only" );
  }
}

//##ModelId=3F98DAE6024A
int Meq::VisDataMux::deliverHeader (const DataRecord &header)
{
  // check header for number of stations, use a reasonable default
  cdebug(3)<<"got header: "<<header.sdebug(DebugLevel)<<endl;
  int nstations = header[FNumStations].as<int>(-1);
  if( nstations>0 )
  {
    cdebug(2)<<"header indicates "<<nstations<<" stations\n";
  }
  else
  {
    nstations = 30;
    cdebug(2)<<"no NumStations parameter in header, assuming 30\n";
  }
  handlers_.resize(VisVocabulary::ifrNumber(nstations,nstations)+1);
  // get frequencies 
  if( !header[VisVocabulary::FChannelFreq].get(channel_freqs) ||
      !header[VisVocabulary::FChannelWidth].get(channel_widths) )
  {
    Throw("dataset header is missing frequency information");
  }
//  // BUG BUG BUG! This assumes a regualr frequency spacing
//  minfreq = min(channel_freqs) - channels_widths(0)/2;
//  maxfreq = max(channel_freqs) + channels_widths(0)/2;
  // init output tile format
  out_format_.attach(header[FTileFormat].as_p<VisTile::Format>(),DMI::READONLY);
  for( uint i=0; i<out_columns_.size(); i++ )
  {
    if( out_format_->defined(out_columns_[i]) )
    {
      cdebug(3)<<"output column "<<out_colnames_[i]<<" already present in tile format"<<endl;
    }
    else
    {
      cdebug(2)<<"adding output column "<<out_colnames_[i]<<" to tile format\n";
      out_format_.privatize(DMI::WRITE);
      out_format_().add(out_columns_[i],out_format_->type(VisTile::DATA),
                        out_format_->shape(VisTile::DATA));
    }
  }
  // notify all handlers of header
  int result_flag = 0;
  for( uint i=0; i<handlers_.size(); i++ )
  {
    VisHandlerList & hlist = handlers_[i];
    VisHandlerList::iterator iter = hlist.begin();
    for( ; iter != hlist.end(); iter++ )
      result_flag |= (*iter)->deliverHeader(*out_format_);
  }
  // cache the header
  cached_header_.attach(header,DMI::READONLY);
  writing_data_ = false;
  return result_flag;
}

//##ModelId=3F950ACA0160
int Meq::VisDataMux::deliverTile (VisTile::Ref::Copy &tileref)
{
  int result_flag = 0;
  int did = formDataId(tileref->antenna1(),tileref->antenna2());
  if( did > int(handlers_.size()) )
  {
    cdebug(4)<<"no handlers for did "<<did<<", skipping tile "<<tileref->sdebug(DebugLevel-2)<<endl;
    return 0;
  }
  VisHandlerList &hlist = handlers_[did];
  if( hlist.empty() )
  {
    cdebug(4)<<"no handlers for did "<<did<<", skipping tile "<<tileref->sdebug(DebugLevel-2)<<endl;
    return 0;
  }
  else
  {
    cdebug(3)<<"have handlers for did "<<did<<", got tile "<<tileref->sdebug(DebugLevel-1)<<endl;
    // For now, generate the request right here.
    Cells::Ref cellref(DMI::ANONWR);
    LoRange range;
    fillCells(cellref(),range,*tileref);
    Request::Ref reqref;
    Request &req = reqref <<= new Request(cellref.deref_p(),0);
    forest_.assignRequestId(req);
    cdebug(3)<<"have handler, generated request id="<<req.id()<<endl;
    // deliver to all known handlers
    VisHandlerList::iterator iter = hlist.begin();
    for( ; iter != hlist.end(); iter++ )
    {
      VisTile::Ref ref(tileref,DMI::COPYREF);
      int code = (*iter)->deliverTile(req,ref,range);
      result_flag |= code;
      // if an output tile is returned, dump it out
      if( code&Node::RES_UPDATED )
      {
        cdebug(3)<<"handler returns updated tile "<<tileref->tileId()<<", posting to output\n";
        writing_data_ = true;
        if( cached_header_.valid() )
        {
          output().put(HEADER,cached_header_);
          cached_header_.detach();
        }
        output().put(DATA,ref);
      }
    }
  }
  return result_flag;
}

int Meq::VisDataMux::deliverFooter (const DataRecord &footer)
{
  cdebug(2)<<"delivering footer to all handlers"<<endl;
  int result_flag = 0;
  for( uint i=0; i<handlers_.size(); i++ )
  {
    VisHandlerList & hlist = handlers_[i];
    VisHandlerList::iterator iter = hlist.begin();
    for( ; iter != hlist.end(); iter++ )
    {
      VisTile::Ref tileref;
      int code = (*iter)->deliverFooter(tileref);
      if( code&Node::RES_UPDATED )
      {
        cdebug(2)<<"handler returns updated tile "<<tileref->tileId()<<", posting to output\n";
        writing_data_ = true;
        if( cached_header_.valid() )
        {
          output().put(HEADER,cached_header_);
          cached_header_.detach();
        }
        output().put(DATA,tileref);
      }
      result_flag |= code;
    }
  }
  if( writing_data_ )
    output().put(FOOTER,ObjRef(footer,DMI::READONLY));
  return result_flag;
}

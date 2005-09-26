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
#include <MeqServer/Spigot.h>
#include <MeqServer/Sink.h>

using namespace AppAgent;
using namespace AppControlAgentVocabulary;
using namespace VisVocabulary;
using namespace VisAgent;

const HIID child_labels[] = { AidStart,AidPre,AidPost };

InitDebugContext(Meq::VisDataMux,"VisDataMux");
    
//##ModelId=3F9FF71B006A
Meq::VisDataMux::VisDataMux ()
  : Node(-4,child_labels,0)  // 3 labeled children, more possible, 0 mandatory
{
  force_regular_grid = false;
  // use reasonable default
  handlers_.resize(VisVocabulary::ifrNumber(30,30)+1);
  sinks_.resize(VisVocabulary::ifrNumber(30,30)+1);
  // init request id for dataset=1
  // frst.incrRequestId(rqid_,FDataset);
}

void Meq::VisDataMux::clear ()
{
  for( uint i=0; i<handlers_.size(); i++ )
    handlers_[i].clear();  
  for( uint i=0; i<sinks_.size(); i++ )
    sinks_[i].clear();  
}

//##ModelId=3FA1016000B0
void Meq::VisDataMux::attachAgents (
                VisAgent::InputAgent  & inp,
                VisAgent::OutputAgent & outp,
                AppControlAgent & ctrl)
{
  input_ = &inp;
  output_ = &outp;
  control_ = &ctrl;
//   force_regular_grid = rec[FMandateRegularGrid].as<bool>(false);
}

void Meq::VisDataMux::attachSpigot (Meq::Spigot &spigot)
{
  // get data ID from spigot
  int did = spigot.dataId();
  if( did >= int(handlers_.size()) )
    handlers_.resize(did+100);
  cdebug(2)<<"attaching spigot for did "<<did<<endl;
  // add spigot to list of handlers for this data id
  handlers_[did].insert(&spigot);
}

void Meq::VisDataMux::attachSink (Meq::Sink &sink)
{
  // get data ID from sink
  int did = sink.dataId();
  if( did >= int(handlers_.size()) )
    handlers_.resize(did+100);
  if( did >= int(sinks_.size()) )
    sinks_.resize(did+100);
  cdebug(2)<<"attaching sink for did "<<did<<endl;
  // get sink output column
  output_columns_.insert(sink.getOutputColumn());
  // add sink to list of handlers for this data id
  handlers_[did].insert(&sink);
  sinks_[did].insert(&sink);
  // add sink to children
  Node::Ref sinkref(sink,DMI::SHARED);
  addChild(sinkref);
}

//##ModelId=3F716EAA0106
void Meq::VisDataMux::detachSpigot (Meq::Spigot &spigot)
{
  handlers_[spigot.dataId()].erase(&spigot);
}

void Meq::VisDataMux::detachSink (Meq::Sink &sink)
{
  handlers_[sink.dataId()].erase(&sink);
  sinks_[sink.dataId()].erase(&sink);
}

// define standard catch clauses to be re-used below on multiple occasions
// first form simply adds exception to error list
#define CatchExceptions(doing_what) \
      catch( std::exception &exc ) \
      { \
        errors.add(exc); \
        result_flag |= Node::RES_FAIL; \
      } \
      catch( ... ) \
      { \
        errors.add(MakeNodeException(string("error ")+(doing_what))); \
        result_flag |= Node::RES_FAIL; \
      } \
      
// second form does the same, plus tags on another error message
#define CatchExceptionsMore(doing_what) \
      catch( std::exception &exc ) \
      { \
        errors.add(exc); \
        errors.add(MakeNodeException(string("error ")+(doing_what))); \
        result_flag |= Node::RES_FAIL; \
      } \
      catch( ... ) \
      { \
        errors.add(MakeNodeException(string("uknown error ")+(doing_what))); \
        result_flag |= Node::RES_FAIL; \
      } \

//##ModelId=3F98DAE6024A
int Meq::VisDataMux::deliverHeader (const DMI::Record &header)
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
  // reset request ID
  forest().incrRequestId(rqid_,FDataset);
  RqId::setSubId(rqid_,forest().getDependMask(FDomain),0);
  current_seqnr_ = -1;
  int maxdid = formDataId(nstations-1,nstations-1) + 1;
  have_tile_.assign(maxdid,false);
  // forest().resetForNewDataSet();
  handlers_.resize(maxdid);
  sinks_.resize(maxdid);
  
  // get frequencies 
  if( !header[VisVocabulary::FChannelFreq].get(channel_freqs) ||
      !header[VisVocabulary::FChannelWidth].get(channel_widths) )
  {
    Throw("header is missing frequency information");
  }
//  // BUG BUG BUG! This assumes a regualr frequency spacing
//  minfreq = min(channel_freqs) - channels_widths(0)/2;
//  maxfreq = max(channel_freqs) + channels_widths(0)/2;
  
  //make sure all output columns are present in output tile format
  VisCube::VTile::Format::Ref out_format_;
  out_format_ <<= header[FTileFormat].as_p<VisCube::VTile::Format>();
  for( ColumnSet::const_iterator iter = output_columns_.begin();
      iter != output_columns_.end(); iter++ )
  {
    std::string colname = VisCube::VTile::getIndexToNameMap()[*iter];
    if( out_format_->defined(*iter) )
    {
      cdebug(3)<<"output column "<<colname<<" already present in tile format"<<endl;
    }
    else
    {
      cdebug(2)<<"adding output column "<<colname<<" to tile format\n";
      out_format_().add(*iter,out_format_->type(VisCube::VTile::DATA),
                        out_format_->shape(VisCube::VTile::DATA));
    }
  }
  DMI::ExceptionList errors;
  // notify all handlers of header
  int result_flag = 0;
  for( uint i=0; i<handlers_.size(); i++ )
  {
    HandlerSet & hlist = handlers_[i];
    HandlerSet::iterator iter = hlist.begin();
    for( ; iter != hlist.end(); iter++ )
    {
      try
      {
        result_flag |= (*iter)->deliverHeader(header,*out_format_);
      }
      CatchExceptionsMore("delivering header to '"+(*iter)->name()+"'");
    }
  }
  // cache the header
  cached_header_.attach(header);
  writing_data_ = false;
  // throw errors if any
  if( !errors.empty() )
    throw errors;
  return result_flag;
}

//##ModelId=3F950ACA0160
int Meq::VisDataMux::deliverTile (VisCube::VTile::Ref &tileref)
{
  int result_flag = 0;
  DMI::ExceptionList errors;
  // get handler for this tile
  int did = formDataId(tileref->antenna1(),tileref->antenna2());
  if( did > int(handlers_.size()) )
  {
    cdebug(4)<<"no handlers for did "<<did<<", skipping tile "<<tileref->sdebug(DebugLevel-2)<<endl;
    return 0;
  }
  // see if tile represents a new snippet (i.e. new sequence number)
  int seqnr = tileref->seqNumber();
  cdebug(4)<<"got tile did "<<did<<" seq "<<seqnr<<", "<<tileref->sdebug(DebugLevel-2)<<endl;
  if( seqnr != current_seqnr_ )
  {
    // previous snippet complete, so poll all handlers
    if( current_seqnr_ >= 0 )
    {
      try { result_flag |= endSnippet(); }
      CatchExceptions("ending snippet "+rqid_.toString('.'));
    }
    current_seqnr_ = seqnr;
    // notify start of new snippet
    try { result_flag |= startSnippet(*tileref); }
    CatchExceptions("starting snippet "+rqid_.toString('.'));
  }
  have_tile_[did] = true;
  // deliver tile to all handlers
  HandlerSet & hlist = handlers_[did];
  HandlerSet::iterator iter = hlist.begin();
  for( ; iter != hlist.end(); iter++ )
  {
    cdebug(4)<<"delivering to "<<(*iter)->name()<<endl;
    try { result_flag |= (*iter)->deliverTile(*current_req_,tileref,current_range_); }
    CatchExceptionsMore("delivering tile "+tileref->tileId().toString('.')+" to '"+(*iter)->name()+"'");
  }
  // throw errors if any
  if( !errors.empty() )
    throw errors;
  return result_flag;
}

int Meq::VisDataMux::deliverFooter (const DMI::Record &footer)
{
  DMI::ExceptionList errors;
  int result_flag = 0;
  if( current_seqnr_ >= 0 )
  {
    try { result_flag |= endSnippet(); }
    CatchExceptions("ending snippet "+rqid_.toString('.'));
  }
  cdebug(2)<<"delivering footer to all handlers"<<endl;
  for( uint i=0; i<handlers_.size(); i++ )
  {
    HandlerSet & hlist = handlers_[i];
    HandlerSet::iterator iter = hlist.begin();
    for( ; iter != hlist.end(); iter++ )
    {
      try { result_flag |= (*iter)->deliverFooter(footer); }
      CatchExceptionsMore("delivering footer to '"+(*iter)->name()+"'");
    }
  }
  if( !errors.empty() )
    throw errors;
  return result_flag;
}

int Meq::VisDataMux::startSnippet (const VisCube::VTile &tile)
{
  int result_flag = 0;
  DMI::ExceptionList errors;
  try
  {
    // Generate new Request id
    RqId::incrSubId(rqid_,forest().getDependMask(FDomain));
    // Generate Cells object from tile
    Cells::Ref cellref;
    Cells &cells = cellref <<= new Cells;
    fillCells(cells,current_range_,tile);
    // Generate new Request with these Cells
    Request &req = current_req_ <<= new Request(cells,0,rqid_);
    cdebug(3)<<"start of snippet, generated request id="<<rqid_<<endl;
    // reset have-tile flags
    have_tile_.assign(handlers_.size(),false);
    // if we have a pre-processing child, poll it now
    if( isChildValid(0) )
    {
      Result::Ref res;
      result_flag = getChild(0).execute(res,req);
      if( result_flag&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException(
            "error starting snippet "+rqid_.toString('.')+": "+
            "child '"+getChild(0).name()+"' returns a FAIL"));
      }
    }
  }
  CatchExceptionsMore("starting snippet "+rqid_.toString('.'));
  if( !errors.empty() )
    throw errors;
  return result_flag;
}

int Meq::VisDataMux::endSnippet ()
{
  DMI::ExceptionList errors;
  int result_flag = 0;
  cdebug(3)<<"end of snippet"<<endl;
  // poll pre-processing child
  if( isChildValid(1) )
  {
    Result::Ref res;
    try 
    { 
      int retcode = getChild(1).execute(res,*current_req_); 
      result_flag |= retcode;
      if( retcode&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException(
            "error pre-processing snippet "+rqid_.toString('.')+": "+
            "child '"+getChild(1).name()+"' returns a FAIL"));
      }
    }
    CatchExceptionsMore("pre-processing snippet "+rqid_.toString('.'));
  }
  int nerr0 = errors.size();
  // poll all sinks for which a tile was assigned
  for( uint i=0; i<sinks_.size(); i++ )
    if( have_tile_[i] )
    {
      SinkSet & hlist = sinks_[i];
      SinkSet::iterator iter = hlist.begin();
      for( ; iter != hlist.end(); iter++ )
      {
        Result::Ref res;
        try 
        { 
          int retcode = (*iter)->execute(res,*current_req_);
          result_flag |= retcode;
          if( retcode&RES_FAIL )
          {
            res->addToExceptionList(errors);
            errors.add(MakeNodeException("sink '"+(*iter)->name()+"' returns a FAIL"));
          }
          else // if sink returns a Tile field in the result, dump tile to output
          {
            const VisCube::VTile *ptile = res[AidTile].as_po<VisCube::VTile>();
            if( ptile )
            {
              cdebug(2)<<"handler returns updated tile "<<ptile->tileId()<<", posting to output\n";
              writing_data_ = true;
              if( cached_header_.valid() )
              {
                output().put(HEADER,cached_header_);
                cached_header_.detach();
              }
              output().put(DATA,ObjRef(ptile));
            }
          }
        }
        CatchExceptions("error processing snippet "+rqid_.toString('.'));
      }
    }
  if( errors.size() > nerr0 )
    errors.add(MakeNodeException("error processing snippet "+rqid_.toString('.')));
  // poll post-processing child
  if( isChildValid(2) )
  {
    Result::Ref res;
    try 
    {
      int retcode = getChild(2).execute(res,*current_req_); 
      result_flag |= retcode; 
      if( retcode&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException(
            "error post-processing snippet "+rqid_.toString('.')+": "+
            "child '"+getChild(2).name()+"' returns a FAIL"));
      }
    }
    CatchExceptionsMore("post-processing snippet "+rqid_.toString('.'));
  }
  // throw errors if any
  if( !errors.empty() )
    throw errors;
  return result_flag;
}
  
void Meq::VisDataMux::fillCells (Cells &cells,LoRange &range,const VisCube::VTile &tile)
{    
  // figure out range of valid rows
  LoVec_bool valid( tile.rowflag() != int(VisCube::VTile::MissingData) );
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
  cells.setCells(Axis::FREQ,channel_freqs,channel_widths);
  cells.setCells(Axis::TIME,time1,interval1);
  cells.recomputeSegments(Axis::FREQ);
  cells.recomputeSegments(Axis::TIME);
  cells.recomputeDomain();
  if( force_regular_grid )
  {
    FailWhen(cells.numSegments(Axis::TIME)>1 || cells.numSegments(Axis::FREQ)>1,
        "tile has irregular grid, we're configured for regular grids only" );
  }
}


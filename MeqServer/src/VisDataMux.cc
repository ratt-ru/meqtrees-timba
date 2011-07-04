//#  VisDataMux.cc
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
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
#include <AppAgent/BOIOChannel.h>
#include <AppAgent/VisDataVocabulary.h>
#include <AppAgent/MTQueueChannel.h>
#include <AppUtils/MSInputChannel.h>
#include <AppUtils/MSSeqOutputChannel.h>
#include <MeqServer/MeqPython.h>
#include <MeqServer/Spigot.h>
#include <MeqServer/Sink.h>

using namespace AppAgent;
using namespace VisVocabulary;
using namespace AppAgent;

const HIID child_labels[] = { AidStart,AidPre,AidPost };

InitDebugContext(Meq::VisDataMux,"VisDataMux");

const HIID FInput    = AidInput;
const HIID FOutput   = AidOutput;
const HIID FMS       = AidMS;
const HIID FMS0      = AidMS|0;
const HIID FBOIO     = AidBOIO;
const HIID FDefault  = AidDefault;
const HIID FMaxTiles = AidMax|AidTiles;


const HIID FNumTiles     = AidNum|AidTiles;
const HIID FNumChunks    = AidNum|AidChunks;
// const HIID FNumTimeslots = AidNum|AidTimeslots;  // declared elsewhere
const HIID FTimeslots    = AidTimeslots;
const HIID FTime         = AidTime;

// events posted by VisDataMux
const HIID FVisChannelOpen   = AidVis|AidChannel|AidOpen;
const HIID FVisHeader        = AidVis|AidHeader;
const HIID FVisNumTiles      = AidVis|AidNum|AidTiles;
const HIID FVisFooter        = AidVis|AidFooter;
const HIID FVisChannelClosed = AidVis|AidChannel|AidClosed;

const HIID FCurrentRequest = AidCurrent|AidRequest;


//##ModelId=3F9FF71B006A
Meq::VisDataMux::VisDataMux ()
  : Node(-4,child_labels,0)  // 3 labeled children, more possible, 0 mandatory
{
  time_extent_.resize(2,0);
  tile_time_.resize(2,0);
  tile_ts_.resize(2,0);

  force_regular_grid = false;
  // use reasonable default
  handlers_.resize(VisVocabulary::ifrNumber(30,30)+1);
  child_indices_.resize(VisVocabulary::ifrNumber(30,30)+1);

  setActiveSymDeps(FDataset);

  enableMultiThreadedPolling();
}

void Meq::VisDataMux::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // do nothing else for now
}

// inits input channel from record
void Meq::VisDataMux::initInput (const DMI::Record &rec)
{
  wstate()[FInput].remove();
  EventChannel::Ref newchannel;
  // instantiate one of a number of channel types depending on record
  const DMI::Record * prec = 0;
  if( (prec = rec[FMS].as_po<DMI::Record>()) != 0 )
    newchannel <<= new MSInputChannel;
  else if( (prec = rec[FBOIO].as_po<DMI::Record>()) != 0 )
    newchannel <<= new BOIOChannel;
  else if( (prec = rec[FDefault].as_po<DMI::Record>()) != 0 )
    newchannel <<= new EventChannel;
  else if( !rec.size() ) // empty record means no channel
    Throw("invalid specification for input channel");
  // max tiles specification
  max_tiles_ = rec[FMaxTiles].as<int>(-1);
  // detach old channel
  if( input_channel_.valid() )
  {
    input_channel_().close();
    input_channel_.detach();
  }
  // init new channel
  if( prec )
  {
    MeqPython::processInitRecord(rec);
    input_channel_ <<= new MTQueueChannel(newchannel);
    input_channel_().init(*prec);
    wstate()[FInput] = rec;
  }
}

// inits input channel from record
void Meq::VisDataMux::initOutput (const DMI::Record &rec)
{
  wstate()[FOutput].remove();
  EventChannel::Ref newchannel;
  // instantiate one of a number of channel types depending on record
  const DMI::Record * prec = 0;
  if( (prec = rec[FMS].as_po<DMI::Record>()) != 0 )
    newchannel <<= new MSSeqOutputChannel;
  else if( (prec = rec[FMS0].as_po<DMI::Record>()) != 0 )
    newchannel <<= new MSOutputChannel;
  else if( (prec = rec[FBOIO].as_po<DMI::Record>()) != 0 )
    newchannel <<= new BOIOChannel;
  else if( (prec = rec[FDefault].as_po<DMI::Record>()) != 0 )
    newchannel <<= new EventChannel;
  else if( !rec.size() ) // empty record means no channel
    Throw("invalid specification for output channel");
  // detach old channel
  if( output_channel_.valid() )
  {
    output_channel_().close();
    output_channel_.detach();
  }
  // init new channel
  if( prec )
  {
    output_channel_ <<= new MTQueueChannel(newchannel);
    // output_channel_.xfer(newchannel);
    output_channel_().init(*prec);
    wstate()[FOutput] = rec;
  }
}

void Meq::VisDataMux::clearOutput ()
{
  output_channel_.detach();
  wstate()[FOutput].replace() = false;
}

void Meq::VisDataMux::postStatus ()
{
  DMI::Record::Ref ref(DMI::ANONWR);
  ref[FNode] = name();
  ref[FNumTiles]  = num_tiles_;
  ref[FNumChunks] = num_chunks_;
  ref[FNumTimeslots] = num_ts_;
  ref[FTimeslots] = tile_ts_;
  ref[FTime] = tile_time_;
  ref[FTimeExtent] = time_extent_;
  postEvent(FVisNumTiles,ref);
}

void Meq::VisDataMux::checkChildren ()
{
  Node::checkChildren();
  // disable first three children (pre/post/start) since we execute them manually
  children().disableChild(0);
  children().disableChild(1);
  children().disableChild(2);
  // regular children from #3 on are expected to be sinks
  for( int ichild=3; ichild<numChildren(); ichild++ )
  {
    Sink * psink = dynamic_cast<Sink*>(&(children().getChild(ichild)));
    FailWhen(!psink,Debug::ssprintf("child %d not of class MeqSink",ichild));
    int did = psink->dataId();
    FailWhen(did<0 || did>0xFFFF,ssprintf("illegal data id %x from sink %s",did,psink->name().c_str()));
    if( did >= int(handlers_.size()) )
      handlers_.resize(did+100);
    if( did >= int(child_indices_.size()) )
      child_indices_.resize(did+100);
    cdebug(2)<<"attaching sink for did "<<did<<endl;
    // get sink output column
    int outcol = psink->getOutputColumn();
    if( outcol >= 0 )
      output_columns_.insert(outcol);
    // add sink to list of handlers for this data id
    handlers_[did].insert(psink);
    // add index of child to list of children for this data id
    child_indices_[did].insert(ichild);
  }
  // all stepchildren are expected to be spigots
  for( int ichild=0; ichild<stepchildren().numChildren(); ichild++ )
  {
    Spigot * pspigot = dynamic_cast<Spigot*>(&(stepchildren().getChild(ichild)));
    FailWhen(!pspigot,Debug::ssprintf("stepchild %d not of class MeqSpigot",ichild));
    int did = pspigot->dataId();
    FailWhen(did<0 || did>0xFFFF,ssprintf("illegal data id %x from spigot %s",did,pspigot->name().c_str()));
    if( did >= int(handlers_.size()) )
      handlers_.resize(did+100);
    cdebug(2)<<"attaching spigot for did "<<did<<endl;
    // add spigot to list of handlers for this data id
    handlers_[did].insert(pspigot);
  }
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
  forest().incrRequestId(next_rqid_,FDataset);
  RequestType::setType(next_rqid_,RequestType::EVAL);
  RqId::setSubId(next_rqid_,symdeps().getMask(FDomain),0);
  current_seqnr_ = -1;
  int maxdid = formDataId(nstations-1,nstations-1) + 1;
  have_tile_.assign(maxdid,false);
  // forest().resetForNewDataSet();
  handlers_.resize(maxdid);
  child_indices_.resize(maxdid);

  // get time extent
  if( !header[VisVocabulary::FTimeExtent].get_vector(time_extent_) )
    time_extent_.assign(2,0);
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
  // if max_tiles_ is set and has been exceeded, ignore
  if( max_tiles_ >= 0 && num_tiles_ > max_tiles_ )
    return 0;
  int result_flag = 0;
  DMI::ExceptionList errors;
  num_chunks_++;
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
      CatchExceptions("ending tile "+rqid_.toString('.'));
    }
    num_tiles_++;
    if( max_tiles_ >= 0 && num_tiles_ > max_tiles_ )
      return 0;
    current_seqnr_ = seqnr;
    // notify start of new snippet
    try { result_flag |= startSnippet(*tileref); }
    CatchExceptions("starting tile "+rqid_.toString('.'));
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
  int result_flag = 0;
  DMI::ExceptionList errors;
  if( max_tiles_ < 0 || num_tiles_ <= max_tiles_ )
  {
    if( current_seqnr_ >= 0 )
    {
      try { result_flag |= endSnippet(); }
      CatchExceptions("ending tile "+rqid_.toString('.'));
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
  }
  // post footer to output
  if( output_channel_.valid() )
    output_channel_().postEvent(VisData::VisEventHIID(VisData::FOOTER,HIID()),ObjRef(footer));

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
    rqid_ = next_rqid_;
    RqId::incrSubId(next_rqid_,symdeps().getMask(FDomain));
    // Generate Cells object from tile
    Cells::Ref cellref;
    Cells &cells = cellref <<= new Cells;
    fillCells(cells,current_range_,tile);
    // Generate new Request with these Cells
    Request &req = current_req_ <<= new Request(cells,rqid_);
    req.setNextId(next_rqid_);
    wstate()[FCurrentRequest] = current_req_;
    req.setRequestType(RequestType::EVAL);
    cdebug(3)<<"start of tile, "<<tile.nrow()<<" rows, generated request id="<<rqid_<<endl;
    // reset have-tile flags
    have_tile_.assign(handlers_.size(),false);
    // if we have a pre-processing child, poll it now
    if( children().isChildValid(0) )
    {
      Result::Ref res;
      timers().getresult.stop();
      timers().children.start();
      result_flag = children().getChild(0).execute(res,req,0);
      timers().children.stop();
      timers().getresult.start();
      if( result_flag&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException(
            "error starting tile "+rqid_.toString('.')+": "+
            "child '"+children().getChild(0).name()+"' returns a FAIL"));
      }
    }
  }
  CatchExceptionsMore("starting tile "+rqid_.toString('.'));
  if( !errors.empty() )
    throw errors;
  return result_flag;
}

int Meq::VisDataMux::endSnippet ()
{
  DMI::ExceptionList errors;
  int result_flag = 0;
  cdebug(3)<<"end of tile"<<endl;
  // post tile count
  postStatus();
  // poll pre-processing child
  if( children().isChildValid(1) )
  {
    Result::Ref res;
    try
    {
      timers().getresult.stop();
      timers().children.start();
      int retcode = children().getChild(1).execute(res,*current_req_,0);
      timers().children.stop();
      timers().getresult.start();
      result_flag |= retcode;
      if( retcode&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException(
            "error pre-processing tile "+rqid_.toString('.')+": "+
            "child '"+children().getChild(1).name()+"' returns a FAIL"));
      }
    }
    CatchExceptionsMore("pre-processing tile "+rqid_.toString('.'));
  }
  int nerr0 = errors.size();
  // ok, now we want to asyncronously poll all sinks that have a tile
  // assigned. First, disable all children
  for( int i=0; i<numChildren(); i++ )
    children().disableChild(i);
  // now, enable sinks with associated tiles
  for( uint i=0; i<child_indices_.size(); i++ )
    if( have_tile_[i] )
    {
      const IndexSet & ilist = child_indices_[i];
      for( IndexSet::const_iterator iter = ilist.begin(); iter != ilist.end(); iter++ )
        children().enableChild(*iter);
    }
  // now do the poll
  children().startAsyncPoll(*current_req_,0);
  while( !forest().abortFlag() )
  {
    try
    {
      int retcode;
      Result::Ref res;
      timers().getresult.stop();
      timers().children.start();
      int ichild = children().awaitChildResult(retcode,res,*current_req_);
      timers().children.stop();
      timers().getresult.start();
      if( ichild < 0 )  // break out if finished
        break;
      result_flag |= retcode;
      if( retcode&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException("child '"+children().getChild(ichild).name()+"' returns a FAIL"));
      }
      else if( !(retcode&(RES_WAIT|RES_ABORT)) ) // if child returns a Tile field in the result, dump tile to output
      {
        const VisCube::VTile *ptile = res[AidTile].as_po<VisCube::VTile>();
        if( ptile )
        {
          cdebug(2)<<"handler returns updated tile "<<ptile->tileId()<<", posting to output\n";
          writing_data_ = true;
          if( output_channel_.valid() )
          {
            if( cached_header_.valid() )
            {
              output_channel_().postEvent(VisData::VisEventHIID(VisData::HEADER,HIID()),cached_header_);
              cached_header_.detach();
            }
            output_channel_().postEvent(VisData::VisEventHIID(VisData::DATA,ptile->tileId()),ObjRef(ptile));
          }
        }
      }
    }
    CatchExceptions("error processing tile "+rqid_.toString('.'));
  }
  if( errors.size() > nerr0 )
    errors.add(MakeNodeException("error processing tile "+rqid_.toString('.')));
  // poll post-processing child
  if( !forest().abortFlag() && children().isChildValid(2) )
  {
    Result::Ref res;
    try
    {
      timers().getresult.stop();
      timers().children.start();
      int retcode = children().getChild(2).execute(res,*current_req_,0);
      timers().children.stop();
      timers().getresult.start();
      result_flag |= retcode;
      if( retcode&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException(
            "error post-processing tile "+rqid_.toString('.')+": "+
            "child '"+children().getChild(2).name()+"' returns a FAIL"));
      }
    }
    CatchExceptionsMore("post-processing tile "+rqid_.toString('.'));
  }
  // throw errors if any
  if( !errors.empty() )
    throw errors;
  return result_flag;
}

void Meq::VisDataMux::fillCells (Cells &cells,LoRange &range,const VisCube::VTile &tile)
{
  // find first valid row, error if none
  int i0,i1;
  for( i0=0; tile.time(i0) == 0; i0++ )
    if( i0 >= tile.nrow() )
    { Throw("tile does not contain any valid rows"); }
  cdebug1(5)<<"valid row range: "<<i0<<":"<<i1<<endl;
  // find last valid row (error condition above ensures that at least one exists)
  for( i1=tile.nrow()-1; tile.time(i1)==0 ; i1-- );
  // form a LoRange describing valid rows, extract time/interval for them
  range = makeLoRange(i0,i1);
  LoVec_double time1     = tile.time()(range).copy();
  LoVec_double interval1 = tile.interval()(range).copy();
  // setup time limits
  tile_ts_[0] = num_ts_;
  tile_ts_[1] = num_ts_ + i1-i0;
  num_ts_ += tile.nrow();
  tile_time_[0] = time1(0);
  tile_time_[1] = time1(i1-i0);
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

//##ModelId=400E5355026B
int Meq::VisDataMux::pollChildren (Result::Ref &resref,
          std::vector<Result::Ref> &childres,
          const Request &request)
{
  const DMI::Record * inrec = request[FInput].as_po<DMI::Record>();
  // no "Input" field in request, pass request on normally
  if( !inrec )
    return Node::pollChildren(resref,childres,request);
  timers().children.stop();
  timers().getresult.start();
  // init input channel
  initInput(*inrec);
  // init output channel, if any
  const DMI::Record * outrec = request[FOutput].as_po<DMI::Record>();
  if( outrec )
    initOutput(*outrec);
  else
    clearOutput();
  // any non-fatal fails during processing are accumulated here
  // (fatal errors are thrown immediately)
  VellSet::Ref fail_list(DMI::ANONWR);
  int stream_state = VisData::FOOTER; // no stream event yet
  time_extent_.assign(2,0);
  bool had_data = false;
  // prepare event record describing start
  DMI::Record::Ref ref(DMI::ANONWR);
  ref[FNode] = name();
  ref[FOutput] = output_channel_.valid();
  // prepare event record describing end
  DMI::Record::Ref endref(DMI::ANONWR);
  endref[FNode] = name();
  // now post the start event
  postEvent(FVisChannelOpen,ref);
  // a start event MUST be matched by an end event
  // (otherwise progress meters, etc. in the browser get confused).
  // Therefore, we now catch any exceptions and post the end event
  // as part of cleanup.
  try
  {
    input_channel_().solicitEvent(VisData::VisEventMask());
    // now run the I/O loop
    cached_header_.detach();
    DMI::Record::Ref header;
    while( !forest().abortFlag() )
    {
      HIID evid;
      ObjRef evdata;
      // wait for a valid input event
      int state = input_channel_().getEvent(evid,evdata);
      // break out once stream is closed
      if( state == AppEvent::CLOSED )
        break;
      else if( state != AppEvent::SUCCESS )
        Throw(ssprintf("input channel fails with state %d",state));
      // parse the event
      if( !VisData::VisEventMask().matches(evid) )
      {
        postError("unknown input event "+evid.toString()+", ignoring");
        continue;
      }
      // figure out the event type
      int event_type = VisData::VisEventType(evid);
      HIID ev_inst = VisData::VisEventInstance(evid);
      string doing_what;
      DMI::ExceptionList errors;
      // process data event
      if( event_type == VisData::DATA )
      {
        doing_what = "processing data event "+ev_inst.toString('.');
        VisCube::VTile::Ref tileref = evdata.ref_cast<VisCube::VTile>();
        cdebug(4)<<"received tile "<<tileref->tileId()<<endl;
        doing_what = "processing tile "+tileref->tileId().toString('.');
        // check for correct sequence
        FailWhen(stream_state!=VisData::DATA,"data event "+ev_inst.toString('.')+" out of sequence");
        // deliver tile to Python
        try  { MeqPython::processVisTile(*tileref); }
        catch( std::exception &exc ) { errors.add(exc); }
        // deliver the tile
        try { deliverTile(tileref); }
        catch( std::exception &exc ) { errors.add(exc); }
      }
      else if( event_type == VisData::FOOTER )
      {
        doing_what = "processing footer "+ev_inst.toString('.');
        cdebug(2)<<"received footer"<<endl;
        FailWhen(stream_state!=VisData::DATA,"footer out of sequence");
        stream_state = VisData::FOOTER;
        const DMI::Record &footer = *(evdata.ref_cast<DMI::Record>());
        // deliver footer to Python
        try  { MeqPython::processVisFooter(footer); }
        catch( std::exception &exc ) { errors.add(exc); }
        // deliver footer to ourselves
        try { deliverFooter(footer); }
        catch( std::exception &exc ) { errors.add(exc); }
        // generate footer report
        DMI::Record::Ref evrec(DMI::ANONWR);
        if( header.valid() )
          evrec[AidHeader] <<= header.copy();
        evrec[AidFooter] <<= evdata.copy();
        evrec[FNode] = name();
        evrec[FNumTiles]  = num_tiles_;
        evrec[FNumChunks] = num_chunks_;
        evrec[FNumTimeslots] = num_ts_;
        evrec[FMessage] = ssprintf("received footer %s. Processed %d timeslots, %d tiles, %d chunks",
            ev_inst.toString('.').c_str(),tile_ts_[1]+1,num_tiles_,num_chunks_);
        postEvent(FVisFooter,evrec);
      }
      else if( event_type == VisData::HEADER )
      {
        had_data = true;
        doing_what = "processing header "+ev_inst.toString('.');
        cdebug(2)<<"received header"<<endl;
        FailWhen(stream_state!=VisData::FOOTER,"header out of sequence");
        header = evdata;
        stream_state = VisData::DATA;
        // deliver header to Python
        try  { MeqPython::processVisHeader(*header); }
        catch( std::exception &exc ) { errors.add(exc); }
        // deliver header to mux
        try  { deliverHeader(*header); }
        catch( std::exception &exc ) { errors.add(exc); }
        // generate header report
        DMI::Record::Ref evrec(DMI::ANONWR);
        evrec[AidHeader] <<= header.copy();
        evrec[FNode] = name();
        evrec[FMessage] = "received header "+ev_inst.toString('.');
        num_tiles_ = num_chunks_ = num_ts_ = 0;
        tile_ts_.assign(2,0);
        tile_time_.assign(2,0);
        postEvent(FVisHeader,evrec);
      }
      else // unknown event
      {
        postError("unknown input event "+evid.toString()+", ignoring");
        continue;
      }
      // have we accumulated any exceptions?
      if( !errors.empty() )
      {
        fail_list().addFail(errors); // add to overall list
        postError("error "+doing_what,errors.makeList());
      }
    }
    // check for correct stream state -- last thing should have been a footer
    if( !forest().abortFlag() )
    {
      if( stream_state != VisData::FOOTER )
        fail_list().addFail(MakeNodeException("input dataset missing a footer"));
      if( !had_data )
        fail_list().addFail(MakeNodeException("input stream was empty"));
    }
    // have we accumulated any errors? abort channels
    if( fail_list->isFail() )
    {
      input_channel_().abort();
      if( output_channel_.valid() )
        output_channel_().abort();
    }
    else // close & flush channels normally
    {
      input_channel_().close();
      // flush output if needed
      if( output_channel_.valid() )
      {
        postMessage("flushing output, this may take a few seconds");
        output_channel_().flush();
        output_channel_().close();
      }
    }
  }
  catch( std::exception &exc )  // catch-all for errors 
  {
    // abort channels
    input_channel_().abort();
    if( output_channel_.valid() )
      output_channel_().abort();
    // add to error list
    fail_list().addFail(exc);
  }
  catch( ... )  // catch-all and cleanup for any errors not caught above
  {
    // post end event
    postEvent(FVisChannelClosed,endref);
    // abort channels
    input_channel_().abort();
    if( output_channel_.valid() )
      output_channel_().abort();
    timers().getresult.stop();
    forest().closeLog();
    throw; // rethrow
  }
  // post end event
  postEvent(FVisChannelClosed,endref);
  timers().getresult.stop();
  forest().closeLog();
  // if we have accumulated any fails, return them here
  if( fail_list->isFail() )
  {
    resref <<= new Result(1);
    resref().setVellSet(0,fail_list);
    return RES_FAIL|getDependMask();
  }
  // normal exit -- return empty result
  return getDependMask();
}

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
#include <AppAgent/BOIOChannel.h>
#include <AppAgent/VisDataVocabulary.h>
#include <AppAgent/MTQueueChannel.h>
#include <AppUtils/MSInputChannel.h>
#include <AppUtils/MSOutputChannel.h>
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
const HIID FBOIO     = AidBOIO;
const HIID FDefault  = AidDefault;
const HIID FNumTiles = AidNum|AidTiles;
const HIID FNumChunks = AidNum|AidChunks;
const HIID FTime0      = AidTime|0;
const HIID FTime1      = AidTime|1;
const HIID FVisNumTiles = AidVis|AidNum|AidTiles;
const HIID FSync     = AidSync;

    
//##ModelId=3F9FF71B006A
Meq::VisDataMux::VisDataMux ()
  : Node(-4,child_labels,0)  // 3 labeled children, more possible, 0 mandatory
{
  force_regular_grid = false;
  // use reasonable default
  handlers_.resize(VisVocabulary::ifrNumber(30,30)+1);
  child_indices_.resize(VisVocabulary::ifrNumber(30,30)+1);
  // init request id for dataset=1
  // frst.incrRequestId(rqid_,FDataset);
  enableMultiThreadedPolling();
  // default cache policy is to cache nothing
  cache_policy_ = CACHE_MINIMAL;
}

void Meq::VisDataMux::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // disable first three children since we execute them manually
  child_disabled_[0] = child_disabled_[1] = child_disabled_[2] = true;
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
    input_channel_().solicitEvent(VisData::VisEventMask());
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
  ref[FTime0] = tile_time_[0];
  ref[FTime1] = tile_time_[1];
  postEvent(FVisNumTiles,ref);
}

void Meq::VisDataMux::resolveChildren ()
{
  Node::resolveChildren();
  // all regular children are sinks, but skip the first three (start, post and pre)
  for( int i=3; i<numChildren(); i++ )
  {
    Sink * psink = dynamic_cast<Sink*>(&(getChild(i)));
    FailWhen(!psink,Debug::ssprintf("child %d not of class MeqSink",i));
    int did = psink->dataId();
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
    child_indices_[did].insert(i); 
  }
  // all stepchildren are spigots
  for( int i=0; i<numStepChildren(); i++ )
  {
    Spigot * pspigot = dynamic_cast<Spigot*>(&(getStepChild(i)));
    FailWhen(!pspigot,Debug::ssprintf("stepchild %d not of class MeqSpigot",i));
    int did = pspigot->dataId();
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
  forest().incrRequestId(rqid_,FDataset);
  RqId::setSubId(rqid_,forest().getDependMask(FDomain),0);
  current_seqnr_ = -1;
  int maxdid = formDataId(nstations-1,nstations-1) + 1;
  have_tile_.assign(maxdid,false);
  // forest().resetForNewDataSet();
  handlers_.resize(maxdid);
  child_indices_.resize(maxdid);
  
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
  DMI::ExceptionList errors;
  int result_flag = 0;
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
  num_tiles_++;
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
    Request &req = current_req_ <<= new Request(cells,rqid_);
    req.setRequestType(RequestType::EVAL);
    cdebug(3)<<"start of tile, generated request id="<<rqid_<<endl;
    // reset have-tile flags
    have_tile_.assign(handlers_.size(),false);
    // if we have a pre-processing child, poll it now
    if( isChildValid(0) )
    {
      Result::Ref res;
      timers_.getresult.stop();
      timers_.children.start();
      result_flag = getChild(0).execute(res,req);
      timers_.children.stop();
      timers_.getresult.start();
      if( result_flag&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException(
            "error starting tile "+rqid_.toString('.')+": "+
            "child '"+getChild(0).name()+"' returns a FAIL"));
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
  if( isChildValid(1) )
  {
    Result::Ref res;
    try 
    { 
      timers_.getresult.stop();
      timers_.children.start();
      int retcode = getChild(1).execute(res,*current_req_); 
      timers_.children.stop();
      timers_.getresult.start();
      result_flag |= retcode;
      if( retcode&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException(
            "error pre-processing tile "+rqid_.toString('.')+": "+
            "child '"+getChild(1).name()+"' returns a FAIL"));
      }
    }
    CatchExceptionsMore("pre-processing tile "+rqid_.toString('.'));
  }
  int nerr0 = errors.size();
  // ok, now we want to asyncronously poll all sinks that have a tile 
  // assigned. First, disable all children
  for( int i=0; i<numChildren(); i++ )
    child_disabled_[i] = true;
  // now, enable sinks with tiles
  for( uint i=0; i<child_indices_.size(); i++ )
    if( have_tile_[i] )
    {
      const IndexSet & ilist = child_indices_[i];
      for( IndexSet::const_iterator iter = ilist.begin(); iter != ilist.end(); iter++ )
        child_disabled_[*iter] = false;
    }
  // now do the poll
  startAsyncPoll(*current_req_);
  while( true )
  {
    try
    {
      int retcode;
      Result::Ref res;
      timers_.getresult.stop();
      timers_.children.start();
      int ichild = awaitChildResult(retcode,res,*current_req_);
      timers_.children.stop();
      timers_.getresult.start();
      if( ichild < 0 )  // break out if finished
        break;
      result_flag |= retcode;
      if( retcode&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException("child '"+getChild(ichild).name()+"' returns a FAIL"));
      }
      else // if child returns a Tile field in the result, dump tile to output
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
  if( isChildValid(2) )
  {
    Result::Ref res;
    try 
    {
      timers_.getresult.stop();
      timers_.children.start();
      int retcode = getChild(2).execute(res,*current_req_); 
      timers_.children.stop();
      timers_.getresult.start();
      result_flag |= retcode; 
      if( retcode&RES_FAIL )
      {
        res->addToExceptionList(errors);
        errors.add(MakeNodeException(
            "error post-processing tile "+rqid_.toString('.')+": "+
            "child '"+getChild(2).name()+"' returns a FAIL"));
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
  // setup time limits
  if( num_tiles_ == 1 )
    time0_ = time1(0); // reference time
  tile_time_[0] = time1(0) - time0_;
  tile_time_[1] = time1(i1-i0) - time0_;
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

//##ModelId=400E5355026B
int Meq::VisDataMux::pollChildren (Result::Ref &resref,const Request &request)
{
  const DMI::Record * inrec = request[FInput].as_po<DMI::Record>();
  // no "Input" field in request, pass request on normally
  if( !inrec )
    return Node::pollChildren(resref,request);
  timers_.children.stop();
  timers_.getresult.start();
  // init input channel
  initInput(*inrec);
  // init output channel, if any
  const DMI::Record * outrec = request[FOutput].as_po<DMI::Record>();
  bool sync_output = false;
  if( outrec )
  {
    initOutput(*outrec);
    sync_output= (*outrec)[FSync].as<bool>(true);
  }
  else
    clearOutput();
  // now run the I/O loop
  cached_header_.detach();
  DMI::Record::Ref header;
  int stream_state = VisData::FOOTER; // no event
  // any non-fatal fails during processing are accumulatede here
  // (fatal errors are thrown immediately)
  VellSet::Ref fail_list(DMI::ANONWR); 
  while( true )
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
      postMessage(ssprintf("received footer %s, %d tiles (%d chunks) processed",
          ev_inst.toString('.').c_str(),num_tiles_,num_chunks_),evrec);
    }
    else if( event_type == VisData::HEADER )
    {
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
      postMessage("received header "+ev_inst.toString('.'),evrec);
      num_tiles_ = num_chunks_ = 0;
      postStatus();
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
  input_channel_().close();
  // flush output if needed
  if( output_channel_.valid() )
  {
    if( sync_output )
    {
      postMessage("flushing output");
      output_channel_().flush();
    }
    output_channel_().close();
  }
  FailWhen(stream_state!=VisData::FOOTER,"data stream missing a footer");
  // if we have accumulated any fails, return them here
  if( fail_list->isFail() )
  {
    resref <<= new Result(1);
    resref().setVellSet(0,fail_list);
    return RES_FAIL;
  }
  postMessage("visibility stream processed successfully");
  // normal exit
  return 0;
}

#include "Spigot.h"
#include "AID-MeqServer.h"
#include <VisCube/VisVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Forest.h>

namespace Meq {
  
using namespace blitz;

const HIID FQueue          = AidQueue;
const HIID FQueueRequestId = AidQueue|AidRequest|AidId;

InitDebugContext(Spigot,"MeqSpigot");

Spigot::Spigot ()
    : VisHandlerNode(0),        // no children allowed
      icolumn(VisCube::VTile::DATA),
      colname("DATA"),
      flag_mask(-1),
      row_flag_mask(-1),
      flag_bit(1)
{
  setActiveSymDeps(FDomain);
}
  
//##ModelId=3F9FF6AA03D2
void Spigot::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  VisHandlerNode::setStateImpl(rec,initializing);
  // ensure column name is processed first time through
  if( rec[FInputColumn].get(colname,initializing) )
  {
    colname = struppercase(colname);
    const VisCube::VTile::NameToIndexMap &colmap = VisCube::VTile::getNameToIndexMap();
    VisCube::VTile::NameToIndexMap::const_iterator iter = colmap.find(colname);
    if( iter == colmap.end() ) {
      NodeThrow(FailWithoutCleanup,"unknown input column "+colname);
    }
    icolumn = iter->second;
  }
  rec[FFlagBit].get(flag_bit,initializing);
  rec[FFlagMask].get(flag_mask,initializing);
  rec[FRowFlagMask].get(row_flag_mask,initializing);
}

//##ModelId=3F98DAE6023B
int Spigot::deliverTile (const Request &req,VisCube::VTile::Ref &tileref,const LoRange &rowrange)
{
  const VisCube::VTile &tile = *tileref;
  const HIID &rqid = req.id();
  cdebug(3)<<"deliver: tile "<<tile.tileId()<<", rqid "<<rqid<<",row rowrange "<<rowrange<<endl;
  // already waiting for such a request? Do nothing for now
  if( currentRequestId() == rqid )
  {
    cdebug(2)<<"deliver: already at rqid but notify not implemented, doing nothing"<<endl;
    Throw("Spigot: deliver() called after getResult() for the same request ID. "
          "This is not something we can handle w/o a parent notify mechanism, "
          "which is not yet implemented. Either something is wrong with your tree, "
          "or you're not generating unique request IDs.");
  }
  else
  {
    const VisCube::VTile::Format &tileformat = tile.format();
    TypeId coltype = tileformat.type(icolumn);
    LoShape colshape = tileformat.shape(icolumn);
    // # output rows -- tile.nrow() if rowrange is all, or rowrange length otherwise
    int nrows = rowrange.last(tile.nrow()-1) - rowrange.first(0)+1; 
    colshape.push_back(tile.nrow());
    cdebug(3)<<"deliver: using "<<nrows<<" of "<<tile.nrow()<<" tile rows\n";
    // casting away const because blitz constructors below only take non-const
    // pointers
    void *coldata = const_cast<void*>(tile.column(icolumn));
    int nplanes = colshape.size() == 3 ? colshape[0] : 1;
    Result::Ref next_res;
    Result & result = next_res <<= new Result(nplanes,true);
    // get array 
    if( coltype == Tpdouble )
    {
      if( colshape.size() == 3 )
      {
        LoCube_double cube(static_cast<double*>(coldata),colshape,blitz::neverDeleteData);
        LoShape shape = Axis::freqTimeMatrix(colshape[1],nrows);
        for( int i=0; i<nplanes; i++ )
          result.setNewVellSet(i).setReal(shape).getArray<double,2>() = 
              cube(i,LoRange::all(),rowrange);
      }
      else if( colshape.size() == 2 )
      {
        LoMat_double mat(static_cast<double*>(coldata),colshape,blitz::neverDeleteData);
        LoShape shape = Axis::freqTimeMatrix(colshape[0],nrows);
        result.setNewVellSet(0).setReal(shape).getArray<double,2>() = 
              mat(LoRange::all(),rowrange);
      }
      else
        Throw("bad input column shape");
    }
    else if( coltype == Tpfcomplex )
    {
      if( colshape.size() == 3 )
      {
        LoCube_fcomplex cube(static_cast<fcomplex*>(coldata),colshape,blitz::neverDeleteData);
        LoShape shape = Axis::freqTimeMatrix(colshape[1],nrows);
        for( int i=0; i<nplanes; i++ )
          result.setNewVellSet(i).setComplex(shape).getArray<dcomplex,2>() = 
              blitz::cast<dcomplex>(cube(i,LoRange::all(),rowrange));
      }
      else if( colshape.size() == 2 )
      {
        LoMat_fcomplex mat(static_cast<fcomplex*>(coldata),colshape,blitz::neverDeleteData);
        LoShape shape = Axis::freqTimeMatrix(colshape[0],nrows);
        result.setNewVellSet(0).setComplex(shape).getArray<dcomplex,2>() = 
            blitz::cast<dcomplex>(mat(LoRange::all(),rowrange));
      }
      else
        Throw("bad input column shape");
    }
    else
    {
      Throw("invalid column type: "+coltype.toString());
    }
    // get flags
    if( flag_mask || row_flag_mask )
    {
      // only applies to 3D columns (such as visibilty)
      if( colshape.size() == 3 )
      {
        // get flag columns
        const LoCube_int & flags   = tile.flags();
//        cout<<"Tile flags: "<<flags<<endl;
        const LoVec_int  rowflag = tile.rowflag()(rowrange);
        typedef Vells::Traits<VellsFlagType,2>::Array FlagMatrix; 
        for( int i=0; i<nplanes; i++ )
        {
          Vells::Ref flagref;
          FlagMatrix * pfl = 0;
          // get flags
          if( flag_mask )
          {
            flagref <<= new Vells(LoShape(colshape[1],nrows),VellsFlagType(),false);
            pfl = &( flagref().getArray<VellsFlagType,2>() );
            *pfl = flags(i,LoRange::all(),rowrange) & flag_mask;
            if( row_flag_mask )
              for( int j=0; j<nrows; j++ )
                (*pfl)(LoRange::all(),j) |= rowflag(j) & row_flag_mask;
          }
          else if( row_flag_mask ) // apply only row flags with a mask
          {
          // shape of flag array is 1D (time only)
            flagref <<= new Vells(LoShape(1,nrows),VellsFlagType(),true);
            pfl = &( flagref().getArray<VellsFlagType,2>() );
            (*pfl)(0,LoRange::all()) |= rowflag & row_flag_mask;
          }
          // only attach data flags if they're non-0
          if( pfl && blitz::any(*pfl) )
          {
            if( flag_bit ) // override with flag bit if requested
              *pfl = blitz::where(*pfl,flag_bit,0);
            result.vellSetWr(i).setDataFlags(flagref);
          }
        }
      }
      else
      {
        cdebug(2)<<"column "<<colname<<" is not 3D, ignoring flags"<<endl;
      }
    }
      
    result.setCells(req.cells());
    
    // add to queue
    res_queue_.push_back(ResQueueItem());
    res_queue_.back().rqid = rqid;
    res_queue_.back().res = next_res;
    cdebug(3)<<res_queue_.size()<<" results in queue"<<endl;
    
    if( forest().verbosity() > 1 )
      fillDebugState();
    
// 02/04/04: commented out, since it screws up (somewhat) the RES_UPDATED flag
// going back to old scheme
//    // cache the result for this request. This will be picked up and 
//    // returned by Node::execute() later
//    setCurrentRequest(req);
//    cacheResult(resref,dependRES_UPDATED);
  }
  return 0;
}

void Spigot::fillDebugState ()
{
  if( res_queue_.empty() )
  {
    wstate()[FQueue].replace() = false;
    wstate()[FQueueRequestId].replace() = false;
  }
  else
  {
    DMI::Vec &qvec = wstate()[FQueue].replace() <<= new DMI::Vec(TpMeqResult,res_queue_.size());
    DMI::Vec &idvec = wstate()[FQueueRequestId].replace() <<= new DMI::Vec(TpDMIHIID,res_queue_.size());
    int n=0;
    for( ResQueue::const_iterator qiter = res_queue_.begin(); qiter != res_queue_.end(); qiter++,n++ )
    {
      idvec[n] = qiter->rqid;
      qvec[n] = qiter->res.copy();
    }
  }
}


//##ModelId=3F9FF6AA0300
int Spigot::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &,
                       const Request &req,bool)
{
  // have we got a cached result?
  if( !res_queue_.empty() )
  {
    ResQueue::iterator pnext = res_queue_.begin();
    // doesn't match? see if next one does
    if( !maskedCompare(req.id(),pnext->rqid,getDependMask()) )
    {
      // try second item in queue
      pnext++;
      if( pnext == res_queue_.end() || 
          !maskedCompare(req.id(),pnext->rqid,getDependMask()) ) // still no match? fail
      {
        ResQueueItem &next = res_queue_.front();
        resref <<= new Result(1,req);
        VellSet &vs = resref().setNewVellSet(0);
        MakeFailVellSet(vs,
            Debug::ssprintf("spigot: request out of sequence: got rqid %s, expecting %s (depmask is %X)",
                          req.id().toString().c_str(),
                          next.rqid.toString().c_str(),
                          getDependMask()));
        return RES_FAIL;
      }
      else // dequeue front item
        res_queue_.pop_front();
    }
    // return result and dequeue
    resref.copy(pnext->res);
    // update state record
    if( forest().verbosity() > 1 )
      fillDebugState();
    return 0;
  }
  else // no result at all, return WAIT
  {
    return RES_WAIT;
  }
}

}

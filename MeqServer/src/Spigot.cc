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
      icolumn_(VisCube::VTile::DATA),
      colname_("DATA"),
      flag_mask_(-1),
      row_flag_mask_(-1),
      flag_bit_(1),
      dims_(2,2)
{
  // since we effectively hold our own cache, disable node's result caching
  // by default
  setCachePolicy(CACHE_NEVER);

  corr_index_.resize(4);
  for( int i=0; i<4; i++ )
    corr_index_[i] = i;
  const HIID deps[2] = {FDataset,FDomain};
  setActiveSymDeps(deps,2);
}

//##ModelId=3F9FF6AA03D2
void Spigot::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  VisHandlerNode::setStateImpl(rec,initializing);
  // ensure column name is processed first time through
  if( rec[FInputColumn].get(colname_,initializing) )
  {
    colname_ = struppercase(colname_);
    const VisCube::VTile::NameToIndexMap &colmap = VisCube::VTile::getNameToIndexMap();
    VisCube::VTile::NameToIndexMap::const_iterator iter = colmap.find(colname_);
    if( iter == colmap.end() ) {
      NodeThrow(FailWithoutCleanup,"unknown input column "+colname_);
    }
    icolumn_ = iter->second;
  }
  if( colname_ == "UVW" )
  {
    dims_.resize(1);
    dims_[0] = 3;
  }
  else
  {
    // check output shapes and maps for consistency
    bool reshaped = rec[FDims].get_vector(dims_,initializing);
    reshaped |= rec[FCorrIndex].get_vector(corr_index_,initializing);
    FailWhen(reshaped && dims_.product() != int(corr_index_.size()),
            "length of "+FCorrIndex.toString()+" vector does not match dimensions given by "+FDims.toString());
    rec[FFlagBit].get(flag_bit_,initializing);
    rec[FFlagMask].get(flag_mask_,initializing);
    rec[FRowFlagMask].get(row_flag_mask_,initializing);
  }
}

// template<typename TT,typename VT>
// void Spigot::readColumn<3,TT,VT> (Result &result,void *coldata,const LoShape &colshape,const LoRange &rowrange,int nrows)
// {
//   blitz::Array<TT,3> cube(static_cast<TT*>(coldata),colshape,blitz::neverDeleteData);
//   cube.transposeSelf(blitz::thirdDim,blitz::secondDim,blitz::firstDim);
//   LoShape shape = Axis::freqTimeMatrix(colshape[1],nrows);
//   for( uint i=0; i<corr_index_.size(); i++ )
//   {
//     VellSet &vs = result.setNewVellSet(i);
//     int icorr = corr_index_[i];
//     if( icorr >=0 )
//       vs.setValue(new Vells(VT(),shape,false)).getArray<typename VT,2>()
//           = cube(rowrange,LoRange::all(),icorr);
//     // else leave vellset empty to indicate missing data
//   }
// }
//
// template<typename TT,typename VT>
// void Spigot::readColumn<2,TT,VT> (Result &result,void *coldata,const LoShape &colshape,const LoRange &rowrange,int nrows)
// {
//   blitz::Array<TT,2> mat(static_cast<TT*>(coldata),colshape,blitz::neverDeleteData);
//   // transpose into time-freq order
//   mat.transposeSelf(blitz::secondDim,blitz::firstDim);
//   LoShape shape = Axis::freqTimeMatrix(colshape[0],nrows);
//   result.setNewVellSet(0).setValue(new Vells(VT(),shape,false)).getArray<VT,2>() =
//         mat(rowrange,LoRange::all());
// }
//
// template<typename TT,typename VT>
// void Spigot::readColumn<1,TT,VT> (Result &result,void *coldata,const LoShape &colshape,const LoRange &rowrange,int nrows)
// {
//   blitz::Array<TT,1> vec(static_cast<TT*>(coldata),colshape,blitz::neverDeleteData);
//   blitz::Array<TT,1> vec1 = vec(rowrange);
//   LoShape shape = Axis::timeVector(nrows);
//   result.setNewVellSet(0).setValue(new Vells(VT(),shape,false)).getArray<VT,1>() =
//   result.setNewVellSet(0).setReal(shape).getArray<VT,1>() = blitz::cast<VT>(vec1);
// }
//
//##ModelId=3F98DAE6023B
int Spigot::deliverTile (const Request &req,VisCube::VTile::Ref &tileref,const LoRange &rowrange)
{
  Assert(Axis::TIME==0 && Axis::FREQ==1);
  const VisCube::VTile &tile = *tileref;
  cdebug(3)<<"deliver: tile "<<tile.tileId()<<", rqid "<<req.id()<<",row rowrange "<<rowrange<<endl;
  // already waiting for such a request? Do nothing for now
  if( currentRequestId() == req.id() )
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
    TypeId coltype = tileformat.type(icolumn_);
    LoShape colshape = tileformat.shape(icolumn_);
    // # output rows -- tile.nrow() if rowrange is all, or rowrange length otherwise
    int nrows = rowrange.last(tile.nrow()-1) - rowrange.first(0)+1;
    colshape.push_back(tile.nrow());
    cdebug(3)<<"deliver: using "<<nrows<<" of "<<tile.nrow()<<" tile rows\n";
    int nfreq = 0;
    bool cubic_column = colshape.size() == 3;
    // casting away const because blitz constructors below only take non-const
    // pointers
    void *coldata = const_cast<void*>(tile.column(icolumn_));
    int nplanes = cubic_column ? colshape[0] : 1;
    //FailWhen(cubic_column && nplanes!=int(corr_index_.size()),
    //            "tile dimensions do not match spigot settings");
    Result::Ref next_res;
    Result & result = next_res <<= new Result(dims_);
    // get array
    if( coltype == Tpdouble )
    {
      // UVW column is a special case
      if( colname_ == "UVW" )
      {
        LoMat_double mat(static_cast<double*>(coldata),colshape,blitz::neverDeleteData);
        LoShape shape = Axis::timeVector(nrows);
        for( int i=0; i<3; i++ )
        {
          VellSet &vs = result.setNewVellSet(i);
          vs.setReal(shape).getArray<double,1>() = mat(i,rowrange);
        }
      }
      // else treat it as a standard corr/freq/time column
      else if( colshape.size() == 3 )
      {
        LoCube_double cube(static_cast<double*>(coldata),colshape,blitz::neverDeleteData);
        // transpose into time-freq-corr order
        cube.transposeSelf(blitz::thirdDim,blitz::secondDim,blitz::firstDim);
        LoShape shape = Axis::freqTimeMatrix(nfreq = colshape[1],nrows);
        for( uint i=0; i<corr_index_.size(); i++ )
        {
          VellSet &vs = result.setNewVellSet(i);
          int icorr = corr_index_[i];
          if( icorr >=0 )
          {
            FailWhen(icorr >= nplanes,ssprintf("corr index %d out of range for this tile",icorr));
            vs.setReal(shape).getArray<double,2>() = cube(rowrange,LoRange::all(),icorr);
          }
          // else leave vellset empty to indicate missing data
        }
      }
      else if( colshape.size() == 2 )
      {
        LoMat_double mat(static_cast<double*>(coldata),colshape,blitz::neverDeleteData);
        // transpose into time-freq order
        mat.transposeSelf(blitz::secondDim,blitz::firstDim);
        LoShape shape = Axis::freqTimeMatrix(nfreq = colshape[0],nrows);
        result.setNewVellSet(0).setReal(shape).getArray<double,2>() =
              mat(rowrange,LoRange::all());
      }
      else if( colshape.size() == 1 )
      {
        LoVec_double vec(static_cast<double*>(coldata),colshape,blitz::neverDeleteData);
        LoVec_double vec1 = vec(rowrange);
        LoShape shape = Axis::timeVector(nrows);
        result.setNewVellSet(0).setReal(shape).getArray<double,1>() = vec1;
      }
      else
        Throw("bad input column shape");
    }
    else if( coltype == Tpfloat )
    {
      if( colshape.size() == 3 )
      {
        LoCube_float cube(static_cast<float*>(coldata),colshape,blitz::neverDeleteData);
        // transpose into time-freq-corr order
        cube.transposeSelf(blitz::thirdDim,blitz::secondDim,blitz::firstDim);
        LoShape shape = Axis::freqTimeMatrix(nfreq = colshape[1],nrows);
        cdebug(5)<<"column data t/s 0: "<<cube(0,LoRange::all(),LoRange::all())<<endl;
        cdebug(5)<<"column data t/s 1: "<<cube(0,LoRange::all(),LoRange::all())<<endl;
        for( uint i=0; i<corr_index_.size(); i++ )
        {
          VellSet &vs = result.setNewVellSet(i);
          int icorr = corr_index_[i];
          if( icorr >=0 )
          {
            FailWhen(icorr >= nplanes,ssprintf("corr index %d out of range for this tile",icorr));
            cdebug(5)<<"column data corr "<<icorr<<": "<<cube(rowrange,LoRange::all(),icorr)<<endl;
            vs.setReal(shape).getArray<double,2>() = blitz::cast<double>(cube(rowrange,LoRange::all(),icorr));
          }
          // else leave vellset empty to indicate missing data
        }
      }
      else if( colshape.size() == 2 )
      {
        LoMat_float mat(static_cast<float*>(coldata),colshape,blitz::neverDeleteData);
        // transpose into time-freq order
        mat.transposeSelf(blitz::secondDim,blitz::firstDim);
        LoShape shape = Axis::freqTimeMatrix(nfreq = colshape[0],nrows);
        result.setNewVellSet(0).setReal(shape).getArray<double,2>() =
              blitz::cast<double>(mat(rowrange,LoRange::all()));
      }
      else if( colshape.size() == 1 )
      {
        LoVec_float vec(static_cast<float*>(coldata),colshape,blitz::neverDeleteData);
        cdebug(5)<<"column data "<<vec<<endl;
        LoVec_float vec1 = vec(rowrange);
        LoShape shape = Axis::timeVector(nrows);
        result.setNewVellSet(0).setReal(shape).getArray<double,1>() = blitz::cast<double>(vec1);
      }
      else
        Throw("bad input column shape");
    }
    else if( coltype == Tpfcomplex )
    {
      if( colshape.size() == 3 )
      {
        LoCube_fcomplex cube(static_cast<fcomplex*>(coldata),colshape,blitz::neverDeleteData);
        // transpose into time-freq-corr order
        cube.transposeSelf(blitz::thirdDim,blitz::secondDim,blitz::firstDim);
        LoShape shape = Axis::freqTimeMatrix(nfreq = colshape[1],nrows);
        for( uint i=0; i<corr_index_.size(); i++ )
        {
          VellSet &vs = result.setNewVellSet(i);
          int icorr = corr_index_[i];
          if( icorr >=0 )
          {
            FailWhen(icorr >= nplanes,ssprintf("corr index %d out of range for this tile",icorr));
            vs.setComplex(shape).getArray<dcomplex,2>() =
              blitz::cast<dcomplex>(cube(rowrange,LoRange::all(),icorr));
          }
          // else leave vellset empty to indicate missing data
        }
      }
      else if( colshape.size() == 2 )
      {
        LoMat_fcomplex mat(static_cast<fcomplex*>(coldata),colshape,blitz::neverDeleteData);
        // transpose into time-freq order
        mat.transposeSelf(blitz::secondDim,blitz::firstDim);
        LoShape shape = Axis::freqTimeMatrix(nfreq = colshape[0],nrows);
        result.setNewVellSet(0).setComplex(shape).getArray<dcomplex,2>() =
            blitz::cast<dcomplex>(mat(rowrange,LoRange::all()));
      }
      else if( colshape.size() == 1 )
      {
        LoVec_fcomplex vec(static_cast<fcomplex*>(coldata),colshape,blitz::neverDeleteData);
        LoVec_fcomplex vec1 = vec(rowrange);
        LoShape shape = Axis::timeVector(nrows);
        result.setNewVellSet(0).setComplex(shape).getArray<dcomplex,1>() = blitz::cast<dcomplex>(vec1);
      }
      else
        Throw("bad input column shape");
    }
    else
    {
      Throw("invalid column type: "+coltype.toString());
    }
    // get flags
    if( flag_mask_ || row_flag_mask_ )
    {
      // only applies to 3D columns (such as visibilty)
      if( colshape.size() == 3 )
      {
        // get flag columns
        LoCube_int flags   = tile.flags();
        // transpose into time-freq-corr order
        flags.transposeSelf(blitz::thirdDim,blitz::secondDim,blitz::firstDim);
//        cout<<"Tile flags: "<<flags<<endl;
        const LoVec_int  rowflag = tile.rowflag()(rowrange);
        typedef Vells::Traits<VellsFlagType,2>::Array FlagMatrix;
        for( uint i=0; i<corr_index_.size(); i++ )
        {
          VellSet &vs = result.vellSetWr(i);
          int icorr = corr_index_[i];
          if( icorr >=0 )
          {
            Vells::Ref flagref;
            FlagMatrix * pfl = 0;
            // get flags
            if( flag_mask_ )
            {
              flagref <<= new Vells(Axis::freqTimeMatrix(nfreq,nrows),VellsFlagType(),false);
              pfl = &( flagref().getArray<VellsFlagType,2>() );
              *pfl = flags(rowrange,LoRange::all(),icorr) & flag_mask_;
              if( row_flag_mask_ )
                for( int j=0; j<nrows; j++ )
                  (*pfl)(j,LoRange::all()) |= rowflag(j) & row_flag_mask_;
            }
            else if( row_flag_mask_ ) // apply only row flags with a mask
            {
            // shape of flag array is 1D (time only)
              flagref <<= new Vells(Axis::freqTimeMatrix(1,nrows),VellsFlagType(),true);
              pfl = &( flagref().getArray<VellsFlagType,2>() );
              (*pfl)(0,LoRange::all()) |= rowflag & row_flag_mask_;
            }
            // only attach data flags if they're non-0
            if( pfl && blitz::any(*pfl) )
            {
              if( flag_bit_ ) // override with flag bit if requested
                *pfl = blitz::where(*pfl,flag_bit_,0);
              result.vellSetWr(icorr).setDataFlags(flagref);
            }
          }
        }
      }
      else
      {
        cdebug(2)<<"column "<<colname_<<" is not a cube, ignoring flags"<<endl;
      }
    }
    // copy cells to result
    result.setCells(req.cells());

    // add to queue
    res_queue_.push_back(ResQueueItem());
    res_queue_.back().rqid = req.id();
    res_queue_.back().res = next_res;
    cdebug(3)<<res_queue_.size()<<" results in queue"<<endl;

    if( forest().debugLevel() > 1 )
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
  // if we have cached results in the queue, go through them until we find
  // a match. Discard non-matching results at head of queue
  while( !res_queue_.empty() &&
         !RqId::maskedCompare(req.id(),res_queue_.begin()->rqid,getDependMask()) )
    res_queue_.pop_front();
  // queue empty, no match -- return missing data
  if( res_queue_.empty() )
  {
    (resref <<= new Result(1)).setNewVellSet(0);
    return RES_MISSING;
  }
  // else return head of queue
  resref.copy(res_queue_.front().res);
  // update state record
  if( forest().debugLevel() > 1 )
    fillDebugState();
  return 0;
//// this code no longer invoked
//       if( pnext == res_queue_.end() ||
//           !RqId::maskedCompare(req.id(),pnext->rqid,getDependMask()) ) // still no match? fail
//       {
//         ResQueueItem &next = res_queue_.front();
//         resref <<= new Result(1);
//         VellSet &vs = resref().setNewVellSet(0);
//         MakeFailVellSet(vs,
//             Debug::ssprintf("spigot: request out of sequence: request id %s, expecting %s (depmask is %X)",
//                           req.id().toString('.').c_str(),
//                           next.rqid.toString('.').c_str(),
//                           getDependMask()));
//         return RES_FAIL;
//       }
}


}

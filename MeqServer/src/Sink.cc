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

#include "Sink.h"
#include <DMI/Vec.h>
#include <VisCube/VisVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Forest.h>

namespace Meq {

InitDebugContext(Sink,"MeqSink");

Sink::Sink()
  : VisHandlerNode(1),        // 1 child node expected
    output_col(-1),
    flag_mask(-1),
    flag_bit(0)
{
//  const HIID gendeps[] = { FDomain,FResolution };
//  const int  masks[]   = { RQIDM_DOMAIN,RQIDM_RESOLUTION }; 
//  setGenSymDeps(gendeps,masks,2);
}
   
//##ModelId=400E5B6D0048
int Sink::mapOutputCorr (int iplane)
{
  if( output_icorrs.empty() )
    return iplane;
  if( iplane<0 || iplane >= int(output_icorrs.size()) )
    return -1;
  return output_icorrs[iplane]; 
}

//##ModelId=3F9918390169
void Sink::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  VisHandlerNode::setStateImpl(rec,initializing);
  // check if output column is specified
  if( rec[FOutputColumn].get(output_colname,initializing) )
  {
    if( output_colname.length() )
    {
      output_colname = struppercase(output_colname);
      const VisCube::VTile::NameToIndexMap &colmap = VisCube::VTile::getNameToIndexMap();
      VisCube::VTile::NameToIndexMap::const_iterator iter = colmap.find(output_colname);
      if( iter == colmap.end() ) {
        NodeThrow(FailWithoutCleanup,"unknown output column "+output_colname);
      }
      output_col = iter->second;
    }
    else
      output_col = -1;
  }
  // check if output correlation map is specified
  rec[FCorrIndex].get_vector(output_icorrs,initializing);
  // get flag masks
  rec[FFlagMask].get(flag_mask,initializing);
  rec[FFlagBit].get(flag_bit,initializing);
//  rec[FRowFlagMask].get(row_flag_mask,initializing);
//  // get UVW nodes
//  rec[FUVWNodeGroup].get(uvw_node_group,initializing);
//  rec[FUVWNodeName].get(uvw_node_name,initializing);
}

//##ModelId=3F9509770277
int Sink::getResult (Result::Ref &resref, 
                     const std::vector<Result::Ref> &childres,
                     const Request &req,bool)
{
  FailWhen(req.id() != cur_rqid,"expected rqid "+cur_rqid.toString()+", got "+req.id().toString());
  FailWhen(!cur_tile.valid(),"this sink did not receive a tile");
  VisCube::VTile::Ref tileref;
  // this will invalidate the pending refs
  tileref.xfer(cur_tile);
  const HIID &tile_id = tileref->tileId();
  cdebug(3)<<"procPendingTile: processing tile "<<tile_id<<" of "
            <<tileref->ntime()<<" timeslots"<<endl;
  resref = childres[0];
  // if no output column, then return immediately
  if( output_col < 0 )
    return 0;
  // get results from child node (1 expected)
  const Result &result = *resref;
  int nvs = result.numVellSets();
  cdebug(3)<<"child returns "<<nvs<<" vellsets"<<endl;
  // any fails in result automatically passed up
  if( result.numFails() )
    return RES_FAIL;
  // store resulting Vells into the tile
  // loop over vellsets and get a tf-plane from each
  VisCube::VTile *ptile = 0; 
  const VisCube::VTile::Format *pformat = 0;
  void *coldata = 0; 
  TypeId coltype;
  LoShape colshape;   // current output column shape, may be NCORRxNFREQxTIME or NFREQxNTIME
  LoShape colshape2;  // 2D column shape: always NFREQxNTIME
  int ncorr = tileref->ncorr();
  // Check if we have a special case of 1 input VellSet (i.e. a scalar) 
  // This usually needs to be treated as a 2x2 matrix. (In the strange case
  // where only a single output correlation needs to be generated, this can
  // be effected by setting output_icorrs to [N,-1,-1,-1].)
  // res_vs[i] will contain a pointer to vellset #i, or 0 if the vellset is 0. 
  // If only one vellset came in, we'll duplicate pointers to it for the diagonal elements,
  // and set off-diagonals to 0.
  const VellSet *res_vs[std::max(nvs,4)];
  if( nvs == 1 )
  {
    res_vs[0] = res_vs[3] = &( resref->vellSet(0) );
    res_vs[1] = res_vs[2] = 0;
    nvs = 4;
  }
  else
  {
    // fill res_vs[i] with pointer to vellset #i. If fewer than four vellsets,
    // fill remainder with 0 
    for( int ivs = 0; ivs < nvs; ivs++ )
      res_vs[ivs] = &( resref->vellSet(ivs) );
    for( int ivs = nvs; ivs < 4; ivs++ )
      res_vs[ivs] = 0;
  }
  for( int ivs = 0; ivs < nvs; ivs++ )
  {
    int icorr = mapOutputCorr(ivs);
    if( icorr<0 )
    {
      cdebug(3)<<"vellset "<<ivs<<" output disabled, skipping"<<endl;
    }
    else if( icorr >= ncorr )
    {
      cdebug(3)<<"child "<<ivs<<" correlation not available, skipping"<<endl;
    }
    else // OK, write it
    {
      if( !ptile )
      {
        ptile = tileref.dewr_p(); // COW here
        pformat = &(ptile->format());
        // add output column to tile as needed
        if( !pformat->defined(output_col) )
        {
          pformat = output_format.deref_p();
          FailWhen(!pformat->defined(output_col),"sink output column not defined "
                  "in common tile output format");
          cdebug(3)<<"adding output column to tile"<<endl;
          ptile->changeFormat(output_format);
        }
        coldata  = ptile->wcolumn(output_col);
        coltype  = pformat->type(output_col);
        colshape = pformat->shape(output_col);
        colshape.push_back(ptile->nrow()); // add third dimension to column shape
        FailWhen(colshape.size()!=3 && colshape.size()!=2,"output column must have 2 or 3 dimensions");
        // set the basic 2D shape 
        colshape2.resize(2);
        colshape2[0] = colshape[colshape.size()-2];
        colshape2[1] = colshape[colshape.size()-1];
      }
      const VellSet * pvs = res_vs[ivs];
      // process null vellset -- store zeroes to output column
      if( !pvs || pvs->isNull() )
      {
        if( coltype == Tpdouble )
          fillTileColumnWithConstant(static_cast<double*>(coldata),numeric_zero<double>(),colshape,cur_range,icorr);
        else  // complex values
          fillTileColumnWithConstant(static_cast<fcomplex*>(coldata),numeric_zero<fcomplex>(),colshape,cur_range,icorr);
      }
      else
      {
        const Vells &vells = pvs->getValue();
        if( vells.isScalar() ) // constant vells
        {
          if( vells.isReal() ) // real values can go to real or complex column
          {
            if( coltype == Tpdouble )
              fillTileColumnWithConstant(static_cast<double*>(coldata),vells.as<double>(),colshape,cur_range,icorr);
            else if( coltype == Tpfcomplex )
              fillTileColumnWithConstant(static_cast<fcomplex*>(coldata),make_fcomplex(vells.as<double>(),0),colshape,cur_range,icorr);
            else
            {
              Throw("type mismatch: double child result, "+coltype.toString()+" column");
            }
          }
          else  // complex values
          {
            FailWhen(coltype!=Tpfcomplex,"type mismatch: complex child result, "+coltype.toString()+" column");
            fillTileColumnWithConstant(static_cast<fcomplex*>(coldata),static_cast<fcomplex>(vells.as<dcomplex>()),colshape,cur_range,icorr);
          }
        }
        else // non-scalar vells
        {
          // get the values out, and copy them to tile column
          const Vells &vells = pvs->getValue();
          FailWhen(vells.rank() != 2,"child result must be scalar, or a rank-2 (time-freq) array");
          if( vells.isReal() ) // real values can go to real or complex column
          {
            if( coltype == Tpdouble )
              fillTileColumn(static_cast<double*>(coldata),colshape,cur_range,
                              vells.getConstArray<double,2>(),icorr);
            else if( coltype == Tpfcomplex )
              fillTileColumn(static_cast<fcomplex*>(coldata),colshape,cur_range,
                              vells.getConstArray<double,2>(),icorr);
            else
            {
              Throw("type mismatch: double child result, "+coltype.toString()+" column");
            }
          }
          else  // complex values
          {
            FailWhen(coltype!=Tpfcomplex,"type mismatch: complex child result, "+coltype.toString()+" column");
            fillTileColumn(static_cast<fcomplex*>(coldata),colshape,cur_range,
                          vells.getConstArray<dcomplex,2>(),icorr);
          }
        }
        // write flags, if specified by flag mask
        if( flag_mask )
        {
          LoMat_int tileflags = ptile->wflags()(icorr,LoRange::all(),cur_range);
          // if vells has flags, work out how to copy them
          if( vells.hasDataFlags() )
          {
            Vells realflags;
            const Vells & dataflags = vells.dataFlags();
            // if same shape, then write directly
            if( dataflags.shape() == colshape2 )
              realflags = dataflags & flag_mask;
            // else flags may have a "collapsed" shape, then:
            // create a flag vells of the same shape as the data, and fill it
            // with the flag mask, then AND with flags and let Vells math do
            // the expansion
            else if( dataflags.isCompatible(colshape2) )
              realflags = Vells(colshape2,flag_mask,true) & dataflags;
            else
            {
              cdebug(2)<<"shape of dataflags not compatible with output flag column, omitting flags"<<endl;
            }
            Vells::Traits<VellsFlagType,2>::Array fl = 
                realflags.getConstArray<VellsFlagType,2>();
            // flip into freq-time order
            fl.transposeSelf(blitz::secondDim,blitz::firstDim);
            // if flag bit is set, use a where-expression, else simply copy
            if( flag_bit )
              tileflags = where(fl,flag_bit,0);
            else
              tileflags = fl;
          }
          // no flags on Vells -- simply clear the tile's flags
          else
            tileflags(LoRange::all(),LoRange::all()) = 0;
        }
      }
    }
  }
  // have we written to the tile? Attach to result
  if( ptile )
  {
    resref[AidTile] <<= ptile;
    return RES_UPDATED;
  }
  // else no change
  return 0;
}

template<class T,class U>
void Sink::fillTileColumn (T *coldata,const LoShape &colshape,
                           const LoRange &rowrange,
                           const blitz::Array<U,2> &arr,int icorr)
{
  const LoShape arrshape = arr.shape();
  blitz::Array<T,2> colarr;
  // option 1 is writing to a 2D column with same shape
  if( colshape.size() == 2 )
  {
    blitz::Array<T,2> colarr0(coldata,colshape,blitz::neverDeleteData);
    colarr.reference(colarr0(LoRange::all(),rowrange));
  }
  // option 2 is writing to a cube column using the current correlation
  else if( colshape.size() == 3 )
  {
    blitz::Array<T,3> colarr0(coldata,colshape,blitz::neverDeleteData);
    colarr.reference(colarr0(icorr,LoRange::all(),rowrange));
  }
  // flip into freq-time order for assignment
  colarr.transposeSelf(blitz::secondDim,blitz::firstDim);
  FailWhen(colarr.shape()!=arr.shape(),"shape of child result does not match output column");
  colarr = blitz::cast<T>(arr);
}


template<class T>
void Sink::fillTileColumnWithConstant (T *coldata,T value,const LoShape &colshape,
                                       const LoRange &rowrange,int icorr)
{
  blitz::Array<T,2> colarr;
  // option 1 is writing to a 2D column with same shape
  if( colshape.size() == 2 )
  {
    blitz::Array<T,2> colarr0(coldata,colshape,blitz::neverDeleteData);
    colarr.reference(colarr0(LoRange::all(),rowrange));
  }
  // option 2 is writing to a cube column using the current correlation
  else if( colshape.size() == 3 )
  {
    blitz::Array<T,3> colarr0(coldata,colshape,blitz::neverDeleteData);
    colarr.reference(colarr0(icorr,LoRange::all(),rowrange));
  }
  // assign zeroes
  colarr = value;
}

int Sink::deliverHeader (const DMI::Record&,const VisCube::VTile::Format &outformat)
{
  output_format.attach(outformat);
  cdebug(3)<<"deliverHeader: got format "<<outformat.sdebug(2)<<endl;
  cur_tile.detach();
  return 0;
}

//##ModelId=3F98DAE6021E
int Sink::deliverTile (const Request &req,VisCube::VTile::Ref &tileref,const LoRange &range)
{
  cur_rqid = req.id();
  cur_tile.copy(tileref);
  cur_range = range;
  return 0;
}

int Sink::deliverFooter (const DMI::Record &)
{
  cur_tile.detach();
  return 0;
}


}

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
  const HIID gendeps[] = { FDomain,FResolution };
  const int  masks[]   = { RQIDM_DOMAIN,RQIDM_RESOLUTION }; 
  setGenSymDeps(gendeps,masks,2);
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
int Sink::getResult (Result::Ref &ref, 
                     const std::vector<Result::Ref> &childres,
                     const Request &,bool)
{
  ref = childres[0];
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
  else
  {
    Throw("output tile column must have 2 or 3 dimensions")
  }
  FailWhen(colarr.shape()!=arr.shape(),"shape of child result does not match output column");
  colarr = blitz::cast<T>(arr);
}

int Sink::deliverHeader (const VisCube::VTile::Format &outformat)
{
  output_format.attach(outformat);
  cdebug(3)<<"deliverHeader: got format "<<outformat.sdebug(2)<<endl;
  pending.tile.detach();
  setExecState(CS_ES_IDLE,
    (control_status_&~(CS_CACHED|CS_RETCACHE|CS_RES_MASK))|CS_RES_WAIT);
  return 0;
}


int Sink::procPendingTile (VisCube::VTile::Ref &tileref)
{
  if( !pending.tile.valid() ) // no tile pending?
    return 0;
  // this will invalidate the pending refs
  tileref = pending.tile;
  Request::Ref reqref  = pending.request;
  if( forest().verbosity()>1 )
    wstate()[FNewRequest].replace() = reqref.copy();
  setExecState(CS_ES_REQUEST);
  cdebug(3)<<"procPendingTile: processing tile "<<tileref->tileId()<<" of "
            <<tileref->ntime()<<" timeslots"<<endl;
  // get results from all child nodes 
  Result::Ref resref;
  setExecState(CS_ES_POLLING);
  cdebug(5)<<"calling execute() on child "<<endl;
  int resflag = getChild(0).execute(resref,*reqref);
  FailWhen(resflag&RES_WAIT,"Meq::Sink received a WAIT result code. This "
      "is usually the result of an incorrectly constructed tree and/or missing "
      "data");
  if( resflag == RES_FAIL )
  {
    cdebug(3)<<"child result is FAIL, ignoring"<<endl;
    setExecState(CS_ES_IDLE,
            (control_status_&~(CS_CACHED|CS_RETCACHE|CS_RES_MASK))|CS_RES_FAIL);
    return RES_FAIL;
  }
  if( output_col<0 )
  {
    cdebug(3)<<"output disabled, skipping"<<endl;
    setExecState(CS_ES_IDLE,
            (control_status_&~(CS_CACHED|CS_RETCACHE|CS_RES_MASK))|CS_RES_EMPTY);
    return resflag;
  }
  setExecState(CS_ES_EVALUATING);
  Thread::Mutex::Lock lock(resref->mutex());
  int nvs = resref->numVellSets();
  cdebug(3)<<"child returns "<<nvs<<" vellsets, resflag "<<resflag<<endl;
  // store resulting Vells into the tile
  // loop over vellsets and get a tf-plane from each
  VisCube::VTile *ptile = 0; 
  const VisCube::VTile::Format *pformat = 0;
  void *coldata; 
  TypeId coltype;
  LoShape colshape; 
  int ncorr = tileref->ncorr();
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
                  "in common tile output format.");
          cdebug(3)<<"adding output column to tile"<<endl;
          ptile->changeFormat(output_format);
        }
        coldata  = ptile->wcolumn(output_col);
        coltype  = pformat->type(output_col);
        colshape = pformat->shape(output_col);
        colshape.push_back(ptile->nrow()); // add third dimension to column shape
      }
      // get the values out, and copy them to tile column
      const Vells &vells = resref->vellSet(ivs).getValue();
      FailWhen(vells.rank()>2,"illegal Vells rank");
      if( vells.isReal() ) // real values
      {
        FailWhen(coltype!=Tpdouble,"type mismatch: double Vells, "+coltype.toString()+" column");
        fillTileColumn(static_cast<double*>(coldata),colshape,pending.range,
                        vells.getConstArray<double,2>(),icorr);
      }
      else  // complex values
      {
        FailWhen(coltype!=Tpfcomplex,"type mismatch: complex Vells, "+coltype.toString()+" column");
        fillTileColumn(static_cast<fcomplex*>(coldata),colshape,pending.range,
                      vells.getConstArray<dcomplex,2>(),icorr);
      }
      // write flags, if specified by flag mask and present in vells
      if( flag_mask && vells.hasDataFlags() )
      {
        Vells realflags;
        const Vells & dataflags = vells.dataFlags();
        // if same shape, then write directly
        if( vells.shape() == dataflags.shape() )
          realflags = dataflags & flag_mask;
        // else flags may have a "collapsed" shape, then:
        // create a flag vells of the same shape as the data, and fill it
        // with the flag mask, then AND with flags and let Vells math do
        // the expansion
        else if( dataflags.isCompatible(vells.shape()) )
          realflags = Vells(vells.shape(),flag_mask,true) & dataflags;
        else
        {
          cdebug(2)<<"shape of dataflags not compatible with data, omitting flags"<<endl;
        }
        const Vells::Traits<VellsFlagType,2>::Array & fl = 
            realflags.getConstArray<VellsFlagType,2>();
        // if flag bit is set, use a where-expression, else simply copy
        if( flag_bit )
          ptile->wtf_flags(icorr) = where(fl,flag_bit,0);
        else
          ptile->wtf_flags(icorr) = fl;
      }
      resflag |= RES_UPDATED;
    }
  }
  lock.release();
  setExecState(CS_ES_IDLE,
            (control_status_&~(CS_CACHED|CS_RETCACHE|CS_RES_MASK))|CS_RES_OK);
  return resflag;
}

//##ModelId=3F98DAE6021E
int Sink::deliverTile (const Request &req,VisCube::VTile::Ref &tileref,const LoRange &range)
{
  // grab a copy of the ref (since procPendingTile may overwrite tileref)
  VisCube::VTile::Ref ref(tileref,DMI::COPYREF);
  // process any pending tiles from previous deliver() call
  std::string errstr;
  int resflag = 0;
  RequestId rqid;
  if( pending.request.valid() )
    rqid = pending.request->id();
  try
  {
    resflag = procPendingTile(tileref);
  }
  catch( std::exception &exc )
  {
    errstr = rqid.toString()  + ": " + exc.what();
    resflag |= RES_FAIL;
  }
  catch( ... )
  {
    errstr = rqid.toString()  + ": unknown exception";
    resflag |= RES_FAIL;
  }
  // if no asked to wait, make this tile pending
  if( !(resflag&RES_WAIT) )
  {
    // make this tile & request pending
    pending.request.attach(req);
    pending.tile  = ref;
    pending.range = range;
  }
  // set execution state
  int st = CS_RES_NONE;
  if( resflag&RES_FAIL )
  {
    st = CS_RES_FAIL;
    wstate()[AidFail].replace() = errstr;
  }
  else
  {
    if( getControlStatus()&CS_RES_MASK == CS_RES_FAIL )
      wstate()[AidFail].remove();
  }
  setExecState(CS_ES_IDLE,
    (control_status_&~(CS_CACHED|CS_RETCACHE|CS_RES_MASK))|st);
  return resflag;
}

int Sink::deliverFooter (VisCube::VTile::Ref &tileref)
{
  // process any pending tiles from previous deliver() call
  return procPendingTile(tileref);  
}


}

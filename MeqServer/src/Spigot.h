#ifndef MEQSERVER_SRC_SPIGOT_H_HEADER_INCLUDED_9B1ECA78
#define MEQSERVER_SRC_SPIGOT_H_HEADER_INCLUDED_9B1ECA78
    
#include <MeqServer/VisHandlerNode.h>
#include <MeqServer/TID-MeqServer.h>

#pragma aid Spigot 
#pragma aid Input Col Next Request Id Queue
#pragma types #Meq::Spigot
    
// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqSpigot
//  A MeqSpigot is attached to a VisAgent data source, and represents
//  one interferometer. For every matching VisCube::VTile at the input of the 
//  source, it caches the visibility data. If a matching request is then
//  received, it returns that data as the result (with one plane per
//  correlation.) A MeqSpigot usually works in concert with a MeqSink,
//  in that a sink is placed at the base of the tree, and generates 
//  results matching the input data. 
//  A MeqSpigot can have no children.
//field input_column "DATA"
//  Gives the tile column from which data is to be read. Note that any double
//  or fcomplex tile column can be used (i.e. WEIGHT and SIGMA and such, not
//  just DATA, PREDICT and RESIDUALS, which contain correlations). 
//  1D columns produce a time-variable vells in the result, matrix columns 
//  produce a time-freq variable vells in the result, and cubic columns can 
//  produce a tensor result with multiple vells. 
//  In the latter case, the dims and corr_index fields come into play,
//  telling the spigot how to decompose the "correlation" axis into a tensor,
//  as well as the flag_mask and row_flag_mask fields, to set flags. In the
//  case of 1D or 2D columns, flags are ignored (NB: in the future, we may
//  support row flags for these columns).
//field: dims [2,2]
//  For 3D tile columns only.
//  Tensor dimensions of result. Set to [1] for a scalar result, 
//  [n] for a vector result, etc. Default is [2,2] (a canonical coherency
//  matrix).
//field: corr_index [1,2,3,4]
//  For 3D tile columns only.
//  A vector of four indices telling how to map output vellsets to
//  the correlation axis in the tile column. A tensor result is
//  composed in row-major order, e.g. a 2x2 matrix is composed as 
//  [[C1,C2],[C3,C4]], where Ci is the correlation column given by corr_index[i].
//  For example, the canonical form of a coherency matrix is [[xx,xy],[yx,yy]]. 
//  Therefore, if the correlation axis of the tile is ordered as XX XY YX YY, 
//  then corr_index should be set to [1,2,3,4]. If the correlation axis
//  contains XX YY only, corr_index should be set to [1,0,0,2].
//field: station_1_index 0
//  Index (1-based) of first station comprising the interferometer
//field: station_2_index 0
//  Index (1-based) of second station comprising the interferometer
//field: flag_mask_ -1
//  For 3D tile columns only.
//  Flags bitmask. This is AND-ed with the FLAGS column of the tile to 
//  generate output VellSet flags. Use -1 for a full mask. If both 
//  flag_mask_ and row_flag_mask_ are 0, no output flags will be generated.
//field: row_flag_mask_ -1
//  For 3D tile columns only.
//  Row flags bitmask. This is AND-ed with the ROWFLAG column of the tile 
//  and added to the output VellSet flags. Use -1 for a full mask. If both
//  flag_mask_ and row_flag_mask_ are 0, no output flags will be generated.
//field: flag_bit_ 1
//  For 3D tile columns only.
//  Vells flag bit. If non-0, overrides flag behaviour as follows:
//  the FLAGS and ROWFLAG columns tile of the tile are AND-ed with flag_mask_
//  and row_flag_mask_, respecitively, and the output is flagged with
//  flag_bit_ wherever the result of this operation is not 0.
//defrec end

namespace Meq {

//##ModelId=3F98DAE503C9
class Spigot : public VisHandlerNode
{
  public:
    Spigot ();
  
    //##ModelId=3F98DAE6023B
    virtual int deliverTile (const Request &req,VisCube::VTile::Ref &tileref,const LoRange &);
    
    //##ModelId=3F98DAE6023E
    virtual TypeId objectType() const
    { return TpMeqSpigot; }
    
    //##ModelId=3F9FF6AA016C
    LocalDebugContext;

  protected:
    //##ModelId=3F9FF6AA0300
    virtual int getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &req,bool newreq);
  
    //##ModelId=3F9FF6AA03D2
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  private:
    void fillDebugState ();

//    template<int N,typename TT,typename VT>
//    void readColumn (Result &result,void *coldata,const LoShape &colshape,const LoRange &rowrange,int nrows);
      
    //##ModelId=3F9FF6AA01A3
    int icolumn_;
    string colname_;
    int flag_mask_;
    int row_flag_mask_;
    int flag_bit_;
    
    //##ModelId=3F9FF6AA0221
    typedef struct
    {
      HIID rqid;
      Result::Ref res;
    } ResQueueItem;
    
    typedef std::list<ResQueueItem> ResQueue;
        
    ResQueue res_queue_;
    
    Result::Dims     dims_;
    std::vector<int> corr_index_;
    bool             integrated_;
    
};

}

#endif /* MEQSERVER_SRC_SPIGOT_H_HEADER_INCLUDED_9B1ECA78 */

#ifndef MEQSERVER_SRC_VISDATAMUX_H_HEADER_INCLUDED_82375EEB
#define MEQSERVER_SRC_VISDATAMUX_H_HEADER_INCLUDED_82375EEB

#include <AppAgent/AppControlAgent.h>
#include <VisAgent/InputAgent.h>
#include <VisAgent/OutputAgent.h>
#include <MeqServer/VisHandlerNode.h>
#include <DMI/Events.h>
#include <vector>
    
#pragma aid Station Index Tile Format Create Delete

class AppControlAgent;
        
namespace Meq {
  
const HIID VisDataMux_EventCreate = AidCreate;
const HIID VisDataMux_EventDelete = AidDelete;
   
//##ModelId=3F98DAE503DA
class VisDataMux : public EventRecepient
{
  public:
    static const HIID EventCreate;
    static const HIID EventDelete; 
  
    //##ModelId=3F9FF71B006A
    VisDataMux (Meq::Forest &frst);
    
    virtual ~VisDataMux () 
    {}
      
    //##ModelId=3FA1016000B0
    void init (const DataRecord &rec,
                VisAgent::InputAgent  & inp,
                VisAgent::OutputAgent & outp,
                AppControlAgent       & ctrl);
    
    // this receives node create/delete events
    virtual int receiveEvent (const EventIdentifier &evid,const ObjRef::Xfer &evdata,void *);
    
    //##ModelId=3F98DAE6024C
    void addNode (Node &node);
  
    //##ModelId=3F98DAE6024F
    void removeNode (Node &node);
    
    //##ModelId=3F98DAE6024A
    //##Documentation
    //## delivers visdata header to data mux
    int deliverHeader (const DataRecord &header);
      
    //##ModelId=3F98DAE60251
    //##Documentation
    //## delivers tile to data mux
    //## rowrange specifies range of valid rows in tile
    int deliverTile (VisTile::Ref::Copy &tileref);

    //##Documentation
    //## delivers visdata footer to data mux
    int deliverFooter (const DataRecord &footer);
    
    // helper func:
    // returns Meq::Cells object corresponding to a VisTile, plus range
    // of valid rows
    //##ModelId=3F9FF6970269
    void fillCells (Cells &cells,LoRange &range,const VisTile &tile);

    AppControlAgent &       control()   { return *control_; }
    VisAgent::InputAgent &  input()     { return *input_;   }
    VisAgent::OutputAgent & output()    { return *output_; }
        
    //##ModelId=3F98DAE60246
    ImportDebugContext(VisHandlerNode);
    
  private:
    //##ModelId=3F9FF71B00AE
    VisDataMux ();
    //##ModelId=3F9FF71B00C7
    VisDataMux (const VisDataMux &);
    
    //##ModelId=3F992F280174
    static int formDataId (int sta1,int sta2);
  
    //##ModelId=3F99305003E3
    typedef std::list<VisHandlerNode *> VisHandlerList;
    //##ModelId=3F98DAE60247
    std::vector<VisHandlerList> handlers_;
    
    //##ModelId=3F9FF71B004E
    Meq::Forest & forest_;
 
    //  list of columns to be added to output tiles
    //##ModelId=3FAA52A6008E
    std::vector<int>     out_columns_;
    //##ModelId=3FAA52A6014F
    std::vector<string>  out_colnames_;
    //##ModelId=3FAA52A6018C
    VisTile::Format::Ref out_format_;
    
    // header is cached; it is dumped to output only if some tiles are being
    // written
    DataRecord::Ref cached_header_;
    // flag: tiles are being written
    bool writing_data_;

    LoVec_double channel_freqs;
    LoVec_double channel_widths;  
    // flag: require a fully regular cells (single-segment)
    bool force_regular_grid;
    //##ModelId=400E5B6D0151
//    double minfreq;
    //##ModelId=400E5B6D0177
//    double maxfreq;
    
    AppControlAgent       * control_;
    VisAgent::InputAgent  * input_;
    VisAgent::OutputAgent * output_;
};

} // namespace Meq

#endif /* MEQSERVER_SRC_SPIGOTMUX_H_HEADER_INCLUDED_82375EEB */

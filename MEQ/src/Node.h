#ifndef MEQSERVER_SRC_NODE_H_HEADER_INCLUDED_E5514413
#define MEQSERVER_SRC_NODE_H_HEADER_INCLUDED_E5514413
    
#include <DMI/DataRecord.h>
#include <MEQ/AID-MEQ.h>
#include <MEQ/TID-MEQ.h>
#include <MEQ/Result.h>
    
#pragma aidgroup MEQ
#pragma aid Node Class Name State Child Children
#pragma types #MEQ::Node

namespace MEQ {

class Forest;
class Request;


//##ModelId=3F5F436202FE
class Node : public BlockableObject
{
  public:
    //##ModelId=3F5F43620304
    typedef CountedRef<Node> Ref;
  
  
    // these are flags returned by getResult(), indicating result properties
    //##ModelId=3F698825005B
    typedef enum {
      RES_WAIT    = 1,    // result not yet available, must wait
      RES_MUTABLE = 2,    // result may change for this request
      RES_UPDATED = 4,    // result updated since last request
    } ResultAttributes;

  
    //##ModelId=3F5F43E000A0
    Node();
    //##ModelId=3F5F44A401BC
    virtual ~Node();

    //##ModelId=3F5F45D202D5
    virtual void init (DataRecord::Ref::Xfer &initrec, Forest* frst);
        
    //##ModelId=3F5F44820166
    const string & name() const;
    
    //##ModelId=3F5F441602D2
    const DataRecord & state() const;
    
    //##ModelId=3F5F445A00AC
    virtual void setState (const DataRecord &rec);
    
    //##ModelId=3F6726C4039D
    virtual int getResult (Result::Ref &resref, const Request&);

    // implement abstract methods inherited from BlockableObject 
    //##ModelId=3F5F4363030F
    //##Documentation
    //## Clones a node. 
    //## Currently not implemented (throws exception)
    virtual CountedRefTarget* clone(int flags = 0, int depth = 0) const;
    //##ModelId=3F5F43630313
    //##Documentation
    //## Returns the class TypeId
    virtual TypeId objectType() const
    { return TpMEQNode; }
    //##ModelId=3F5F43630315
    //##Documentation
    //## Un-serialize.
    //## Currently not implemented (throws exception)
    virtual int fromBlock(BlockSet& set);
    //##ModelId=3F5F43630318
    //##Documentation
    //## Serialize.
    //## Currently not implemented (throws exception)
    virtual int toBlock(BlockSet &set) const;
    
    //##ModelId=3F5F48180303
    //##Documentation
    //## Standard debug info method
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    
  private:
    DataRecord & state();

    //##ModelId=3F5F4363030D
    DataRecord::Ref staterec;
    //##ModelId=3F5F48040177
    string myname;
    //##ModelId=3F5F43930004
    Forest *forest;
};

//##ModelId=3F5F441602D2
inline const DataRecord & Node::state() const
{
  return *staterec;
}

inline DataRecord & Node::state() 
{
  return staterec();
}

//##ModelId=3F5F44820166
inline const string & Node::name() const
{
  return myname;
}

} // namespace MEQ

#endif /* MEQSERVER_SRC_NODE_H_HEADER_INCLUDED_E5514413 */

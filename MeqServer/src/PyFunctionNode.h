#ifndef MEQSERVER_SRC_PYFUNCTIONNODE_H
#define MEQSERVER_SRC_PYFUNCTIONNODE_H
    
#include <MeqServer/PyNode.h>

#pragma types #Meq::PyFunctionNode

namespace Meq {
  
//##ModelId=3F98DAE503C9
class PyFunctionNode : public PyNode
{
  public:
    PyFunctionNode ();
  
    virtual ~PyFunctionNode ();
    
    //##ModelId=3F98DAE60222
    virtual TypeId objectType() const
    { return TpMeqPyFunctionNode; }
    
    //##ModelId=3F9FF6AA016C
    LocalDebugContext;

  protected:
    //##ModelId=3F9FF6AA0300
    virtual Vells evaluate (const Request &req,const LoShape &shape,const vector<const Vells*>&);
  
    //##ModelId=3F9FF6AA03D2
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
    // "evaluate" method
    OctoPython::PyObjectRef pynode_evaluate_;
    
    // previous request object and its corresponding Python form
    ObjRef prev_request_;
    OctoPython::PyObjectRef py_prev_request_;
};

}

#endif

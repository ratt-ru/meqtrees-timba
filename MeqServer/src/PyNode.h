#ifndef MEQSERVER_SRC_PYNODE_H
#define MEQSERVER_SRC_PYNODE_H
    
#include <MEQ/Node.h>
#include <MeqServer/MeqPython.h>
#include <MeqServer/AID-MeqServer.h>
#include <MeqServer/TID-MeqServer.h>
#include <OCTOPython/OctoPython.h>

#pragma types #Meq::PyNode
#pragma aid Class Module Name

namespace Meq {
  

//##ModelId=3F98DAE503C9
class PyNode : public Node
{
  public:
    PyNode ();
  
    virtual ~PyNode ();
    
    //##ModelId=3F98DAE60222
    virtual TypeId objectType() const
    { return TpMeqPyNode; }
    
    // changes a state field without 
    
    //##ModelId=3F9FF6AA016C
    LocalDebugContext;

  protected:
    //##ModelId=3F9FF6AA0300
    virtual int getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &req,bool newreq);
  
    //##ModelId=3F9FF6AA03D2
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
    OctoPython::PyObjectRef pynode_obj_;
    OctoPython::PyObjectRef pynode_setstate_;
    OctoPython::PyObjectRef pynode_getresult_;

};

}

#endif

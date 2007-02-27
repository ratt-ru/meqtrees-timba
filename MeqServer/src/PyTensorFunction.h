#ifndef MEQSERVER_SRC_PYTENSORFUNCTIONNODE_H
#define MEQSERVER_SRC_PYTENSORFUNCTIONNODE_H
    
#include <MeqServer/PyNode.h>
#include <MEQ/TensorFunction.h>

#pragma types #Meq::PyTensorFunction

namespace Meq {
  
class PyTensorFuncImpl : public PyNodeImpl
{
  public:
    PyTensorFuncImpl (Node *node);
      
    //##ModelId=3F9FF6AA0300
    int getResult (Result::Ref &resref, 
                   const std::vector<Result::Ref> &childres,
                   const Request &req,bool newreq);
  
    //##ModelId=3F9FF6AA03D2
    void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
  protected:
    OctoPython::PyObjectRef pynode_compute_result_cells_;
    OctoPython::PyObjectRef pynode_setstate_;
    OctoPython::PyObjectRef pynode_evaluate_tensors_;
    
};

  
//##ModelId=3F98DAE503C9
class PyTensorFunction : public TensorFunction
{
  public:
    PyTensorFunction ();
  
    virtual ~PyTensorFunction ();
    
    virtual TypeId objectType() const
    { return TpMeqPyTensorFunction; }
    
    ImportDebugContext(PyNodeImpl);

  protected:
    virtual void computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request);

    // Virtual method to be redefined by subclasses.
    // Returns the tensor dimensions of the result, given a set of child 
    // dimensions. Should return an empty shape for a scalar result.
    // If child dimensions are not valid, may throw an exception.
    // Default version returns empty shape (i.e. scalar result)
    virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);

    // Virtual method to be redefined by subclasses.
    // Evaluates one result tensor based on N child tensors
    virtual void evaluateTensors (
         // output should be assigned here. The vector is pre-sized 
         // according to what is returned by getResultDims()
         std::vector<Vells> & out,   
         // this is the input. For child #i, args[i][j] gives the input
         // tensor; j can be interpreted using the input_dims (as usual,
         // row-major ordering).
         const std::vector<std::vector<const Vells *> > &args );
  
    //##ModelId=3F9FF6AA03D2
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
    PyTensorFuncImpl impl_;
    
};

}

#endif

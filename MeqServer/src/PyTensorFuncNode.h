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

#ifndef MEQSERVER_SRC_PYTENSORFUNCNODE_H
#define MEQSERVER_SRC_PYTENSORFUNCNODE_H
    
#include <MeqServer/PyNode.h>
#include <MEQ/TensorFunction.h>

#pragma types #Meq::PyTensorFuncNode

namespace Meq {
  
class PyTensorFuncImpl : public PyNodeImpl
{
  public:
    PyTensorFuncImpl (Node *node);
      
    // these functions implement the python-side calls
    void computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request);
    
    LoShape getResultDims (const vector<const LoShape *> &input_dims);

    void evaluateTensors (std::vector<Vells> & out,   
         const std::vector<std::vector<const Vells *> > &args );
    
    void setStateImpl (DMI::Record::Ref &rec,bool initializing);

    
  // these data members are public because below (in PyTensorFuncNode)
  // we want to check  whether they're set or not, and call the Python
  // implementation or the parent class's implementation as appropriate
    OctoPython::PyObjectRef pynode_compute_result_cells_;
    OctoPython::PyObjectRef pynode_get_result_dims_;
    OctoPython::PyObjectRef pynode_evaluate_tensors_;

};

  
//##ModelId=3F98DAE503C9
class PyTensorFuncNode : public TensorFunction
{
  public:
    PyTensorFuncNode ();
  
    virtual ~PyTensorFuncNode ();
    
    virtual TypeId objectType() const
    { return TpMeqPyTensorFuncNode; }
    
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

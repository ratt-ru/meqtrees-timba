//# TensorFunction.h: Base class for an compound expression node (i.e. with multiple-planed result)
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$

#ifndef MEQ_TENSORFUNCTION_H
#define MEQ_TENSORFUNCTION_H
    
#include <MEQ/Function.h>

namespace Meq 
{ 

using namespace DMI;

//##ModelId=3F86886E01A8
class TensorFunction : public Function
{
public:
    //##ModelId=3F86886E03C5
  TensorFunction (int nchildren=-1,const HIID *labels = 0,int nmandatory=-1);

    //##ModelId=3F86886E03D1
  virtual ~TensorFunction();

protected:
  // A TensorFunction is similar to a regular function, but whereas Function
  // evaluates itself element-by-element on each element of a tensor,
  // TensorFunction treats all the VellSets of a tensor as a unit.
  // Since each VellSet may contain its own set of spids, TensorFunction
  // provides the outer loop over all spids, and calls evaluate() for
  // every required combination of perturbed values.

  // virtual method to figure out the cells of the result object, based
  // on child cells.
  // Default version simply uses the first child cells it can find,
  // or the Request cells if no child cells are found, else none.
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
       const std::vector<std::vector<const Vells *> > &args )
  = 0;
    
  // Virtual method to be optionally redefined by subclasses.
  // Evaluate the flags for the given request, and return them in 'out_flags'.
  // out_flags is presized according to getResultDims().
  // If out_flags[i] is not a valid ref, a new Vells should be assigned. 
  // (If it is, assume some initial flags are passed in, and do not reinitialize).
  // If no flags were generated (e.g. due to all children being flagless),
  // 'out_flags[i]' may be left uninitialized.
  // Default version works as follows:
  //  * merges the flags within each child tensor
  //  * bitwise-ANDs these with each child's flagmask
  //  * merges this across all children
  //  * assigns this value to all output flags
  virtual void evaluateTensorFlags (
        std::vector<Vells::Ref> & out_flags,
        const std::vector<std::vector<const VellSet *> > &pvs );
        
        
  // This method does most of the spid looping work
  //  * calls getResultDims() to establish result dimensions
  //  * creates Result object
  //  * calls evaluateTensors() to compute main values and puts them into
  //    the result
  //  * calls evaluateTensorFlags() to compute flags, puts them into result
  //  * collects spids from child results, then loops over all spids,
  //    calls evaluateTensors() to compute the perturbed value, and puts them 
  //    into result.
  // Note that this function makes no assumptions about children 
  // or node state or whatever; so it may in fact be used with a 
  // compleely different childres vector than that passed to getResult()
  void computeTensorResult (Result::Ref &resref, 
                            const std::vector<Result::Ref> &childres);
                            
  
  // TensorFunction overrides the standard getResult() method to
  // calls computeTensorResult() to do all the work, then return the
  // result.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  
  // True if result cells have been set by the computeResultCells method
  // above
  bool hasResultCells () const
  { return result_cells_.valid(); }
  
  // Returns the result cells, or throws exception if hasResultCells()==false
  const Cells & resultCells () const
  { 
    FailWhen(!result_cells_.valid(),"can't compute the result cells for this set of child results");
    return *result_cells_; 
  }
  
  // (Note also that Node::currentRequest() may be called to obtain the current
  // request object.)
  
  // This returns the tensor dimensions of a given child result.
  // Also meant to be ued by subclasses if needed.
  // Initialized in computeTensorResult(), and only valid during
  // an evaluate() or evaluateFlags() call.
  const LoShape & childDims (int ichild) const
  { 
    return *dims_vector_[ichild]; 
  }
  
private:
  // hide these methods since they don't apply to tensor functions
  Function::evaluate;
  Function::evaluateFlags;
  
    
  // data members for informational stuff above
  Cells::Ref result_cells_;
  std::vector<const LoShape *> dims_vector_;
    
  // These are setup and used in computeTensorResult().
  // We keep most of them as data members (as opposed to local vars)
  // to minimize reallocations.
  typedef std::vector<const Vells *> CVPVector;
  typedef std::vector<const VellSet *> CVSPVector;

  std::vector<CVSPVector> pvs_vector_;
  std::vector<CVPVector> mainval_vector_;
  std::vector<std::vector<int> > index_vector_;
  
  std::vector<Vells> resval_vector_;
  std::vector<Vells::Ref> flag_vector_;
  CVSPVector pvs_all_;
  
  std::vector<std::vector<CVPVector> > pert_vectors_;
};

} // namespace Meq

#endif

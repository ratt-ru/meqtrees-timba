//# TensorFunctionPert.h: Base class for a tensor-aware function with explicit handling of perturbed values
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
//# $Id: TensorFunctionPert.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQ_TENSORFUNCTIONPERT_H
#define MEQ_TENSORFUNCTIONPERT_H
    
#include <MEQ/TensorFunction.h>

namespace Meq 
{ 

using namespace DMI;

//##ModelId=3F86886E01A8
class TensorFunctionPert : public TensorFunction
{
public:
    //##ModelId=3F86886E03C5
  TensorFunctionPert (int nchildren=-1,const HIID *labels = 0,int nmandatory=-1);

    //##ModelId=3F86886E03D1
  virtual ~TensorFunctionPert();

protected:
  // vector: number of vellsets per child
  std::vector<int> nvs_child_;
  // number of total spids
  int num_spids_;
  // max number of vellsets in child results
  int maxplanes_; 
  // pointer to matrrix of Vells filled in computeTensorResult(), and used by getChildValue()
  // this is of size NCHILD x MAX_PLANES x (NUM_SPIDS+1)
  const Vells **vp_;
  // currently allocated matrix size
  int nvp_;
  
  // interface used by evaluateTensors() to query child results.
  // this returns the number of tensor elements in child ichild
  int numChildElements (int ichild)
  { return nvs_child_[ichild]; }
  
  int IPTR (int ichild,int ispid,int ielem) 
  { return (ichild*(num_spids_+1)+ispid)*maxplanes_ + ielem; }

  // This returns the ielem-th element's main (ipert=0) or ipert-th perturbed value from the ichild-th child.
  const Vells * getChildValue (int ichild,int ipert,int ielem)
  { return vp_[IPTR(ichild,ipert,ielem)]; }
  
  // Like the above, but if ipert>0 and the value is missing, returns value for ipert=0;
  // If value is already there (or if ipert==0), sets newval=True.
  const Vells * getChildValue (bool &newval,int ichild,int ipert,int ielem)
  { 
    const Vells *vp = getChildValue(ichild,ipert,ielem); 
    if( vp )
      newval = true;
    else if( ipert )
      vp = getChildValue(ichild,0,ielem); 
    return vp;
  }
  
  // This inits the main (ipert=0) or ipert-th perturbed value for the ielem-th output element.
  // Return a reference to the value itself.
  Vells & initResultValue (Result &out,int ipert,int ielem)
  { 
    if( !ipert )
      return out.vellSetWr(ielem).setValue(new Vells);
    else
      return out.vellSetWr(ielem).setPerturbedValue(ipert-1,new Vells);
  }
  
  // A TensorFunctionPert is a variation on TensorFunction that explicitly handles perturbed values.
  // Whereas a normal TensorFunction evaluates perturbed values by calling evaluateTensors() once
  // per each perturbation, this class calls evaluateTensors() once, en masse.
  // For each child for 0 to nchild-1, for each pert from 0 to nperts, for each child tensor element
  // from 0 to numChildElements(ichild)-1, the value of the element can be obtained by calling
  // getChildValue(ichild,ipert,ielem). For ipert=0 this is the main value and is guaranteed to be there.
  // For ipert>0, this is the perturbed value, and a null pointer may be returned to indicate that
  // there is no perturbed value and that the main value should be used.
  virtual void evaluateTensors (
       // output should be assigned here. 
       // This is the output Result. This is already pre-initialized with the right number of VellSets,
       // and the expected number of perturbation values and perturbation sets. Subclass is meant to
       // fuill in the individual vellsets
       Result &out,
       // number of children
       int nchildren,
       // this is actually equal to NUM_SPIDS
       int nperts
       )
  =0;
  
    
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
  // completely different childres vector than that passed to getResult()
  void computeTensorResult (Result::Ref &resref, 
                            const std::vector<Result::Ref> &childres);
                            
  
  // TensorFunctionPert overrides the standard getResult() method to
  // calls computeTensorResult() to do all the work, then return the
  // result.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);


private:
  // Define virtrual method required by TensorFunction to null, since we don't use it
  virtual void evaluateTensors (
       std::vector<Vells> &,   
       const std::vector<std::vector<const Vells *> > & )
  {}
};

} // namespace Meq

#endif

//# CoordTransform.cc: modifies request resolutions
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
//# $Id: CoordTransform.cc 4622 2007-01-24 10:44:39Z sarod $

#include <MeqNodes/CoordTransform.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Node.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/Forest.h>
#include <MEQ/AID-Meq.h>
#include <MEQ/VellsSlicer.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MEQ/Vells.h>

using namespace Meq::VellsMath;


//#define DEBUG
namespace Meq {

  const HIID symdeps[] = { FDomain,FResolution };



  CoordTransform::CoordTransform()
    : Node(2),    // 2 children expected
      n_axis_(0)
  {
    // our own result depends on domain & resolution
    res_symdeps_.resize(1);
    res_symdeps_.assign(1,AidResolution);
    // our own result depends on domain & resolution
    dom_symdeps_.resize(1);
    dom_symdeps_.assign(1,AidDomain);
    //default seq symdeps
    seq_symdeps_.resize(1);
    seq_symdeps_.assign(1,AidState);

  }

  CoordTransform::~CoordTransform()
  {}

  void CoordTransform::setStateImpl (DMI::Record::Ref &rec,bool initializing)
  {
    Node::setStateImpl(rec,initializing);
    // get axis of transformation
    HIID axis_id = AidTime;
    rec[FAxis].get(axis_id,initializing);
    for(int i=0;i<Axis::MaxAxis;i++){
      if(Axis::axisId(i)== axis_id)
	{
	  n_axis_=i;
	  break;
	}
      }
    if(axis_id != AidTime && n_axis_ == 0)
      {
	cdebug(2)<<"Axis Id not known, using time instead!!!"<<endl;
      }
  }


  int CoordTransform::pollChildren (Result::Ref &resref,
				std::vector<Result::Ref> &childres,
				const Request &request)
  {
    res_depmask_ = symdeps().getMask(res_symdeps_);
    seq_depmask_ = symdeps().getMask(seq_symdeps_);
    dom_depmask_ = symdeps().getMask(dom_symdeps_);

    //handle parm update the default way
    if( request.requestType() ==RequestType::PARM_UPDATE || request.requestType() ==RequestType::DISCOVER_SPIDS )
      return Node::pollChildren(resref,childres,request);

    /******************* poll child 0 ********/
    setExecState(CS_ES_POLLING);
    timers().children.start();


    Result::Ref child_res;
    childres.resize(2);
    unlockStateMutex();
    int code=result_code_=children().getChild(0).execute(child_res,request,currentRequestDepth()+1);
    lockStateMutex();
    childres[0]= child_res;
    //handle standard error states
    if(forest().abortFlag())
      return RES_ABORT;
    if(code&RES_WAIT) {
      //this node will need to run again
      timers().children.stop();
      return 0;
    }
    if (code&RES_FAIL) {
      resref.xfer(childres[0]);
      timers().children.stop();
      return code;
    }
    //check if result is double outherwise fail!!
    //check order of result, if x[max] < x[min] reverse, if afterwards for any x, x[n]<x[n-1] Fail

    Result &res1=result_<<= new Result(childres[0]->numVellSets());

    /**** begin poll child 1 ******************/
    // extract values from the result of child 0 to define our axes
    // get input cells
    const Cells &incells=request.cells();
    const int nvells=childres[0]->numVellSets();
    const int nr_axis = incells.rank();
    LoVec_double start_cells[nr_axis];
    LoVec_double end_cells[nr_axis];
    int idx[nr_axis];
    for (int axis =0;axis<nr_axis;axis++){
      incells.getCellStartEnd (start_cells[axis],end_cells[axis],axis);
    }

    Cells::Ref outcells_ref;
    Cells &trans_cells=outcells_ref<<= new Cells(incells);
    RequestId rqid=request.id();
    Request::Ref newreq(request);
    int res_nr=nodeIndex();


    //get slices of childres in the transform axis
    Axis::Shape shape;
    for(int vellsi=0;vellsi<nvells;vellsi++){//loop over vellsets
      shape = childres[0]->vellSet(vellsi).shape();
      FailWhen(shape.size() <= n_axis_,"child 0 result has two few axes");
      for (int axis =0;axis<shape.size();axis++){
	idx[axis]=0;
      }
      // get vells
      Vells input_vells = childres[0]->vellSet(vellsi).getValue();
      FailWhen(input_vells.elementType() != Tpdouble,"First child of CoordTransform must return real values!");

      VellSet & vs = res1.setNewVellSet(vellsi,0,request.evalMode());
      Vells::Ref vref;
      Vells &new_vells= vref <<= new Vells(0.,input_vells.shape());
      new_vells.copyData(input_vells);
      vs.setValue(new_vells);
      //get perturbations
      int npert =  childres[0]->vellSet(vellsi).nperturbed();
      if(npert)
	{
	  vs.copySpids(childres[0]->vellSet(vellsi));
	  vs.copyPerturbations(childres[0]->vellSet(vellsi));
	}
      VellsSlicer0 slice(new_vells, n_axis_);

      while(slice.valid()){//loop over slices
	Result::Ref  child2_res;

	blitz::Array<double,1> slice_array =   slice.getArray<double,1>();
	blitz::Array<double,1> sizes;
	bool reversed = checkResult(slice_array,sizes); //reverse array if needed, fail when for any x-> x[n]<x[n-1], fill sizes


	// set request cells to this slice + fill other dimensions
	for (int axis =0;axis<shape.size();axis++){
	  if(axis!=n_axis_ )
	    {
	      trans_cells.setCells(axis,start_cells[axis](idx[axis]),end_cells[axis](idx[axis]),1);
	      //also set domain
	    }
	  else
	    {
	      trans_cells.setCells(axis,slice_array,sizes);
	    }
	}
	//set domain

	trans_cells.recomputeDomain ();
	// increase res_dep rqid
	RqId::incrSubId(rqid,seq_depmask_);
	RqId::setSubId(rqid,res_depmask_,res_nr);
	//also increase dom_id
	RqId::setSubId(rqid,dom_depmask_,res_nr++);
	newreq().setCells(trans_cells);
	newreq().setId(rqid);

	//get _result for these Cells
	unlockStateMutex();
        int code=result_code_=children().getChild(1).execute(child2_res,newreq,currentRequestDepth()+1);
	lockStateMutex();

	//add child_res to final result
	//get the slice from the childresult
	//if child returns complex values we have a problem
	Vells resvells = child2_res->vellSet(0).getValue();
	if(resvells.elementType()==Tpdcomplex){
	  cdebug(2)<<" Complex not yet implemented, using real part instead"<<endl;
	  resvells= real(resvells);
	}
	ConstVellsSlicer0 v100(resvells, n_axis_);
	blitz::Array<double,1>  temp_slice = v100.getArray<double,1>();
	if (reversed) temp_slice.reverseSelf(0); //turn back
	slice_array = temp_slice;

	//check if childres(1) has perturbed values, NOT implemented at the moment
	//increment counter
	slice.incr();
	//calculate grid position of the non sliced axes
 	bool ready =false;

	for (int axisi=nr_axis-1;axisi>=0;axisi--)
	  {
	    if(axisi!=n_axis_ && !ready){
	      idx[axisi]++;
	      if(idx[axisi] >= shape[axisi]){
		idx[axisi]=0;
	      }
	      else
		ready = true;
	    }
	  }
      }//end slice loop
      //loop over perturbations (if exists)
      for(int ipert = 0;ipert <npert;ipert++){
	for (int axis =0;axis<shape.size();axis++){
	  idx[axis]=0;
	}
	// get vells
	Vells input_pert_vells = childres[0]->vellSet(vellsi).getPerturbedValue(ipert);
	FailWhen(input_vells.elementType() != Tpdouble,"First child of CoordTransform must return real values!");
	Vells &new_pert_vells= vref <<= new Vells(0.,input_pert_vells.shape());
	new_pert_vells.copyData(input_pert_vells);
	VellsSlicer0 pslice(new_pert_vells, n_axis_);

	while(pslice.valid()){//loop over pslices
	  Result::Ref  child2_res;

	  blitz::Array<double,1> pslice_array =   pslice.getArray<double,1>();
	  blitz::Array<double,1> sizes;
	  bool reversed;
	  reversed = checkResult(pslice_array,sizes); //reverse array if needed, fail when for any x-> x[n]<x[n-1], fill sizes


	  // set request cells to this pslice + fill other dimensions
	  for (int axis =0;axis<shape.size();axis++){
	    if(axis!=n_axis_ && shape[axis]>1)
	      {
		trans_cells.setCells(axis,start_cells[axis](idx[axis]),end_cells[axis](idx[axis]),1);
		//also set domain
	      }
	    else
	      {
		trans_cells.setCells(axis,pslice_array,sizes);
	      }
	  }
	  //set domain

	  trans_cells.recomputeDomain ();

	  //check if order of vells is still ok, is this necessary?
	  RqId::incrSubId(rqid,seq_depmask_);
	  RqId::setSubId(rqid,res_depmask_,res_nr++);
	  //also increase dom_id
	  RqId::setSubId(rqid,dom_depmask_,res_nr++);
	  newreq().setCells(trans_cells);
	  newreq().setId(rqid);

	  //get _result for these Cells
	  unlockStateMutex();
          int code=result_code_=children().getChild(1).execute(child2_res,newreq,currentRequestDepth()+1);
	  lockStateMutex();
	  // not needed since in principle psliced_vells refers to the right vells.
	  LoShape ranges;
	  ranges.resize(shape.size());
	  //add child_res to final result
	  //get the pslice from the childresult
	  //if child returns complex values we have a problem
	  Vells respvells = child2_res->vellSet(0).getValue();
	  if(respvells.elementType()==Tpdcomplex){
	    cdebug(2)<<" Complex not yet implemented, using real part instead"<<endl;
	    respvells= real(respvells);
	  }
	  ConstVellsSlicer0 vp100(respvells, n_axis_);
	  blitz::Array<double,1>  temp_pslice = vp100.getArray<double,1>();
	  if (reversed) temp_pslice.reverseSelf(0); //turn back
	  pslice_array = temp_pslice;

	  //check if childres(1) has perturbed values
	  //increment counter
	  pslice.incr();
	  bool ready =false;

	  for (int axisi=nr_axis-1;axisi>=0;axisi--)
	    {
	      ranges[axisi] = idx[axisi];
	      if(axisi!=n_axis_ && !ready){
		idx[axisi]++;
		if(idx[axisi] >= shape[axisi]){
		  idx[axisi]=0;
		}
		else
		  ready = true;
	      }
	    }
	}// loop over pslice

	vs.setPerturbedValue(ipert,new_pert_vells);
      }//loop over perturbed values

    }


    res1.setCells(request.cells());

    unlockStateMutex();
    stepchildren().backgroundPoll(request,currentRequestDepth()+1);
    timers().children.stop();
    lockStateMutex();
    return code;
  }


  const bool CoordTransform::checkResult (blitz::Array<double,1> & result_array, blitz::Array<double,1> & sizes){
    //checks if the array needs to be reversed to be ordered min->max
    // Fails if for any n: result_array[n]<result_array[n-1]
					    //returns if_reversed + array  of grid sizes
   bool reversed =  false;
   int size = result_array.size();
   if (size==1) //just return 1;
     {sizes.resize(size);
       sizes(0)=1.;
       return reversed;
     }
   if(result_array(size-1)<result_array(0)){
     result_array.reverseSelf(0);
     reversed = true;
   }
   sizes.resize(size);
   sizes(blitz::Range(0,size-2)) = result_array(blitz::Range(1,size-1));
   sizes(blitz::Range(0,size-2)) -= result_array(blitz::Range(0,size-2));
   // now what should be the last size? take equal  to last-1 size for the moment
   sizes(size-1)=sizes(size-2);
   FailWhen(min(sizes) <=0,"Result array of first child must be sorted (can be reversed)");
  return reversed;


  }


int CoordTransform::getResult (Result::Ref &resref,
			     const std::vector<Result::Ref> &childres,
			     const Request &request,bool)
{
    //pass on the cached result
    resref=result_;
    return result_code_;
}




} // namespace Meq

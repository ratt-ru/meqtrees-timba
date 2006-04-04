//# Compounder.cc: modifies request resolutions
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
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

#include <MeqNodes/Compounder.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Node.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/Forest.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <algorithm>


//#define DEBUG
namespace Meq {

const HIID FMode = AidMode;
const HIID FCommAxes= AidCommon|AidAxes;

const HIID FResolutionSymdeps    = AidResolution|AidSymdeps;
const HIID FResolutionId         = AidResolution|AidId;

const HIID symdeps[] = { FDomain,FResolution };
const HIID FSequenceSymdeps = AidSequence|AidSymdeps;





/****** small class for sorting with indices */
class IdVal;
//declare this as a friend to have similar behaviour as the builtin 
bool operator <(const IdVal& a, const IdVal& b);

class IdVal {
				public:
				blitz::Array<int,1> id; //sequence of axes t,f,perturbed values...
				// if no f or perturbed values are defined
				// they are set to -1
				double val;
        friend bool operator <(const IdVal& a, const IdVal& b);

};
bool operator <(const IdVal& a, const IdVal& b)
{
  return a.val< b.val;
}
/********************************************/



//##ModelId=400E5355029C
Compounder::Compounder()
: Node(2), // 2 children expected
	mode_(1),res_index_(0)
{
  // our own result depends on domain & resolution
	res_symdeps_.resize(1);
  res_symdeps_.assign(1,AidResolution);

	comm_axes_.resize(2);
	//default axes
	comm_axes_[0]="L";
	comm_axes_[1]="M";

	//default seq symdeps
	seq_symdeps_.resize(1);
	seq_symdeps_.assign(1,AidState);

}

//##ModelId=400E5355029D
Compounder::~Compounder()
{}

void Compounder::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);

  // get symdeps
  rec[FResolutionSymdeps].get_vector(res_symdeps_,initializing);
  // get resolution index
  rec[FResolutionId].get(res_index_,initializing);

	//temporary backup
	std::vector<HIID> tmp=comm_axes_;
	if (rec[FCommAxes].get_vector(tmp,initializing) ) {
			FailWhen(tmp.size()!=2,FCommAxes.toString()+" field must have 2 elements");
			comm_axes_=tmp;
	}
	rec[FMode].get(mode_,initializing);
	FailWhen((mode_!=1)&&(mode_!=2),FMode.toString()+" field must be 1 or 2");

	//Add these axes to Axis object
	Axis::addAxis(comm_axes_[0]);
	Axis::addAxis(comm_axes_[1]);

	rec[FSequenceSymdeps].get_vector(seq_symdeps_,initializing);

	//do not resample
	disableAutoResample();

}

int Compounder::pollChildren (Result::Ref &resref,
                          std::vector<Result::Ref> &childres,
                          const Request &request)
{
  res_depmask_ = symdeps().getMask(res_symdeps_);
  seq_depmask_ = symdeps().getMask(seq_symdeps_);

	//handle parm update the default way 
	if( request.requestType() ==RequestType::PARM_UPDATE )
					    return Node::pollChildren(resref,childres,request);

	/******************* poll child 0 ********/
  setExecState(CS_ES_POLLING);
	timers().children.start();
	

	Result::Ref child_res;
	unlockStateMutex();
	int code=result_code_=children().getChild(0).execute(child_res,request);
	lockStateMutex();
	//handle standard error states
	if(forest().abortFlag())
			return RES_ABORT;
	if(code&RES_WAIT) {
		//this node will need to run again 
		timers().children.stop();
		return 0;
	}
	if (code&RES_FAIL) {
			resref.xfer(child_res);
			timers().children.stop();
			return code;
	}

	/*** end poll child 0 **********************/

	/**** begin poll child 1 ******************/
	// extract values from the result of child 0 to define our axes
	Request::Ref newreq(request);

	childres.resize(2);
	childres[0]=child_res;
	/* if we discover spids */
	if ( request.requestType() ==RequestType::DISCOVER_SPIDS ) {  

	const Cells &incells=request.cells();
	const Domain &old_dom=incells.domain();
	Domain::Ref domain(new Domain());
	if (old_dom.isDefined(Axis::TIME))
	 domain().defineAxis(Axis::TIME, old_dom.start(Axis::TIME), old_dom.end(Axis::TIME));
	if (old_dom.isDefined(Axis::FREQ))
	 domain().defineAxis(Axis::FREQ, old_dom.start(Axis::FREQ), old_dom.end(Axis::FREQ));
	//add two more defined in the initrec()
	domain().defineAxis(Axis::axis(comm_axes_[0]),-10000,10000);
	domain().defineAxis(Axis::axis(comm_axes_[1]),-10000,10000);
	Cells::Ref outcells_ref0;
	Cells &outcells=outcells_ref0<<=new Cells(*domain);
	outcells.setCells(Axis::TIME,incells.center(Axis::TIME),incells.cellSize(Axis::TIME));
	outcells.setCells(Axis::FREQ,incells.center(Axis::FREQ),incells.cellSize(Axis::FREQ));

	  outcells.setCells(Axis::axis(comm_axes_[0]),-10000,10000,1);
	  outcells.setCells(Axis::axis(comm_axes_[1]),-10000,10000,1);




	 newreq().setCells(outcells);
	//increment request sequence sub id
	RequestId rqid=request.id();
	RqId::incrSubId(rqid,seq_depmask_);
	//set resolution sub id to node index of this node
	RqId::setSubId(rqid,res_depmask_,nodeIndex());
	newreq().setId(rqid);


	Result::Ref child_res1;
	 unlockStateMutex();
	 code=children().getChild(1).execute(child_res1,*newreq);
	 lockStateMutex();
	 cout<<"Request Id="<<newreq().id()<<endl;
	 //cout<<"Result has cells="<<child_res1().hasCells()<<endl;
	 //cout<<"Result ="<<*child_res1<<endl;
	 //FailWhen(child_res1().hasFails(),"Got Fails in spid discovery");
	 //if (!child_res1().hasCells())
	//	child_res1().setCells(outcells);

	 childres[0]=child_res;
	 childres[1]=child_res1;
	 // resref.xfer(child_res1);
	 resref.detach();
	 //result_=child_res1;
	 unlockStateMutex();
	// stepchildren().backgroundPoll(*newreq);
	 timers().children.stop();
	 lockStateMutex();



	 return code; 
	}

  int nvs=child_res().numVellSets();
#ifdef DEBUG
	cout<<"Got "<<nvs<<" Vellsets"<<endl;
#endif

	FailWhen(nvs!=2,"We need 2 vellsets, but got "+nvs);
	// get input cells
	const Cells &incells=request.cells();
	Cells::Ref outcells_ref;
	const Domain &old_dom=incells.domain();
	Domain::Ref domain(new Domain());

	double start0,end0,start1,end1;
  blitz::Array<double,1> cen0;
	blitz::Array<double,1> cen1;
  // get first vellset
  if (nvs>0) { 		
		Vells vl0=child_res().vellSet(0).getValue();
		int nx=vl0.extent(0);
		int ny=vl0.extent(1);
#ifdef DEBUG
		cout<<"Dimension "<<nx<<","<<ny<<endl;
#endif
	  FailWhen(ny!=1,"We need a 1D array here, but got a 2D array");
		//create axis vector
		const double *data=vl0.realStorage();
		cen0.resize(nx);
		//cen0=vl0.as<double,1>();
		cen0=blitz::Array<double,1>(const_cast<double*>(data),blitz::shape(nx),blitz::neverDeleteData);
#ifdef DEBUG
		cout<<"Axis 1="<<cen0<<endl;
#endif
	} 
	if (nvs>1) { 		
		Vells vl0=child_res().vellSet(1).getValue();
		int nx=vl0.extent(0);
		int ny=vl0.extent(1);
#ifdef DEBUG
		cout<<"Dimension "<<nx<<","<<ny<<endl;
#endif
	  FailWhen(ny!=1,"We need a 1D array here, but got a 2D array");
		//create axis vector
		cen1.resize(nx);
		//cen1=vl0.as<double,1>();
		const double *data=vl0.realStorage();
		cen1=blitz::Array<double,1>(const_cast<double*>(data),blitz::shape(nx),blitz::neverDeleteData);
#ifdef DEBUG
		cout<<"Axis 2="<<cen1<<endl;
#endif
  }
	//if the grid function is not monotonically increasing, we get
	//unsorted arrays for axes.
  //if cen0 or cen1 is not sorted, we recreate that
	//axis to cover the whole range and interpolate the result
	//use STL
	blitz::Array<IdVal,1> sarray0(cen0.extent(0));
	//copy data
	for (int i=0; i<cen0.extent(0);i++) {
		sarray0(i).id.resize(1);
		sarray0(i).id(0)=i;
		sarray0(i).val=cen0(i);
	}
#ifdef DEBUG
	cout<<"Before sort"<<endl;
	for (int i=0; i<sarray0.extent(0);i++) {
		cout<<i<<"="<<sarray0(i).id<<","<<sarray0(i).val<<endl;
	}
#endif
	std::sort(sarray0.data(), sarray0.data()+sarray0.extent(0));
#ifdef DEBUG
	cout<<"After sort"<<endl;
	for (int i=0; i<sarray0.extent(0);i++) {
		cout<<i<<"="<<sarray0(i).id<<","<<sarray0(i).val<<endl;
	}
#endif
	//overwrite the old array
	for (int i=0; i<sarray0.extent(0);i++) {
		cen0(i)=sarray0(i).val;
	}
	blitz::Array<IdVal,1> sarray1(cen1.extent(0));
	//copy data
	for (int i=0; i<cen1.extent(0);i++) {
		sarray1(i).id.resize(1);
		sarray1(i).id(0)=i;
		sarray1(i).val=cen1(i);
	}
#ifdef DEBUG
	cout<<"Before sort"<<endl;
	for (int i=0; i<sarray1.extent(0);i++) {
		cout<<i<<"="<<sarray1(i).id<<","<<sarray1(i).val<<endl;
	}
#endif
	std::sort(sarray1.data(), sarray1.data()+sarray1.extent(0));
#ifdef DEBUG
	cout<<"After sort"<<endl;
	for (int i=0; i<sarray1.extent(0);i++) {
		cout<<i<<"="<<sarray1(i).id<<","<<sarray1(i).val<<endl;
	}
#endif
	//overwrite the old array
	for (int i=0; i<sarray1.extent(0);i++) {
		cen1(i)=sarray1(i).val;
	}

	//calculate grid spacing and bounds
	blitz::Array<double,1> space0(cen0.extent(0));
		//create a space grid
		if (cen0.extent(0)==1) {
			//scalar case
			space0(0)=0.1;
		} else {
			//vector case
			for (int i=1;i<cen0.extent(0);i++) 
				space0(i)=cen0(i)-cen0(i-1);
			space0(0)=space0(1);
		}
	  start0=cen0(0)-space0(0)/2;
		end0=cen0(cen0.extent(0)-1)+space0(cen0.extent(0)-1)/2;


		blitz::Array<double,1> space1(cen1.extent(0));
		//create a space grid
		if (cen1.extent(0)==1) {
			//scalar case
			space1(0)=0.1;
		} else {
			//vector case
			for (int i=1;i<cen1.extent(0);i++) 
				space1(i)=cen1(i)-cen1(i-1);
			space1(0)=space1(1);
		}
	  start1=cen1(0)-space1(0)/2;
		end1=cen1(cen1.extent(0)-1)+space1(cen1.extent(0)-1)/2;
	
	//define axis of the new domain
	if (old_dom.isDefined(Axis::TIME))
	 domain().defineAxis(Axis::TIME, old_dom.start(Axis::TIME), old_dom.end(Axis::TIME));
	if (old_dom.isDefined(Axis::FREQ))
	 domain().defineAxis(Axis::FREQ, old_dom.start(Axis::FREQ), old_dom.end(Axis::FREQ));
	//add two more defined in the initrec()
	domain().defineAxis(Axis::axis(comm_axes_[0]),start0,end0);
	domain().defineAxis(Axis::axis(comm_axes_[1]),start1,end1);
	Cells &outcells=outcells_ref<<=new Cells(*domain);

	outcells.setCells(Axis::TIME,incells.center(Axis::TIME),incells.cellSize(Axis::TIME));
	outcells.setCells(Axis::FREQ,incells.center(Axis::FREQ),incells.cellSize(Axis::FREQ));

	  outcells.setCells(Axis::axis(comm_axes_[0]),cen0,space0);
	  outcells.setCells(Axis::axis(comm_axes_[1]),cen1,space1);

	newreq().setCells(outcells);
	//increment request sub id
	RequestId rqid=request.id();
	RqId::incrSubId(rqid,seq_depmask_);
	newreq().setId(rqid);
	unlockStateMutex();
	code=children().getChild(1).execute(child_res,*newreq);
	lockStateMutex();

	//remember this result
	Result::Ref res0=child_res;
	result_code_|=code;

	/*** end poll child 1 **********************/

	/**** begin processing of the result to correct for grid sorting */
  /** also create a new result with one vellset */
  Result &res1=result_<<= new Result(1,child_res().isIntegrated());
	const Vells vl=res0().vellSet(0).getValue();
	Vells &in=const_cast<Vells &>(vl);
	//create new vellset
  int npsets=res0().vellSet(0).numPertSets();
	int nspids=res0().vellSet(0).numSpids();
	VellSet::Ref ref;
	VellSet &vs=ref <<=new VellSet(incells.shape(),nspids,npsets);
	vs.copySpids(res0().vellSet(0));
	vs.copyPerturbations(res0().vellSet(0));

	Vells &out=vs.setValue(new Vells(0.0,incells.shape()));
	//now fill in the values only defined at the original grid points
	//imagine the axes are (t,f,a,b): then for each (t,f) grid point
	//find points a0,b0 in a and b axes respectively. this value will
	//go to the new grid point (t,f)
	blitz::Array<double,2> A=out.as<double,2>()(blitz::Range::all(),blitz::Range::all());
	blitz::Array<double,4> B=in.getArray<double,4>();
	//reindexing arrays
	for (int i=0;i<A.extent(0);i++)
	  for (int j=0;j<A.extent(1);j++) {
    //find the correct location for this (t,f) point in B
		//need to look up axes a,b for this	
		//Note: we only search for time (or i in this case)
		int k=0;
		while( (k< sarray0.extent(0)) && (sarray0(k).id(0)!=i) ) {k++;}
		int l=0;
		while( (l< sarray1.extent(0)) && (sarray1(l).id(0)!=i)) {l++;}

		//special case, if we overstep our k,l limits
		//that means that particular axis is a scalar so use the value at 0
		if(k==sarray0.extent(0)) {k=0;}
		if(l==sarray0.extent(1)) {l=0;}
#ifdef DEBUG
		//cout<<"for tf ("<<i<<","<<j<<") : ab ["<<k<<","<<l<<"]"<<endl;
#endif
		A(i,j)=B(i,j,k,l);
  }
	// handle perturbed sets if any
  if (npsets >0) {
#ifdef DEBUG
   cout<<"Found "<<npsets<<" perturbed sets"<<endl;
#endif
   for (int ipset=0; ipset<npsets; ipset++) 
    for (int ipert=0; ipert<nspids; ipert++)  {
	   const Vells pvl=res0().vellSet(0).getPerturbedValue(ipert,ipset);
	   Vells &pin=const_cast<Vells &>(pvl);
	   Vells &pout=vs.setPerturbedValue(ipert,new Vells(0.0,incells.shape()),ipset);

    	blitz::Array<double,2> pA=pout.as<double,2>()(blitz::Range::all(),blitz::Range::all());
	blitz::Array<double,4> pB=pin.getArray<double,4>();
	for (int i=0;i<pA.extent(0);i++)
	  for (int j=0;j<pA.extent(1);j++) {
    //find the correct location for this (t,f) point in B
		//need to look up axes a,b for this	
		//Note: we only search for time (or i in this case)
		int k=0;
		while( (k< sarray0.extent(0)) && (sarray0(k).id(0)!=i)) {k++;}
		int l=0;
		while( (l< sarray1.extent(0)) && (sarray1(l).id(0)!=i)) {l++;}

		//special case, if we overstep our k,l limits
		//that means that particular axis is a scalar so use the value at 0
		if(k==sarray0.extent(0)) {k=0;}
		if(l==sarray0.extent(1)) {l=0;}
#ifdef DEBUG
		//cout<<"for tf ("<<i<<","<<j<<") : ab ["<<k<<","<<l<<"]"<<endl;
#endif
		pA(i,j)=pB(i,j,k,l);
  }

	 }
	}
	res1.setVellSet(0,ref);
	res1.setCells(incells);

	childres[1]=child_res;
  //return Node::pollChildren(resref,childres,newreq);
	unlockStateMutex();
	stepchildren().backgroundPoll(request);
	timers().children.stop();
	lockStateMutex();

	return code;
} 

int Compounder::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &childres,
                       const Request &request,bool)
{
	//pass on the cached result
  resref=result_;
  return result_code_;
}


} // namespace Meq

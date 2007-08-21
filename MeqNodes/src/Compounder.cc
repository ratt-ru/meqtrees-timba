//# Compounder.cc: modifies request resolutions
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

#include <MeqNodes/Compounder.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Node.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/Forest.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <algorithm>
#include <map>
#include <list>


//#define DEBUG
namespace Meq {

  const HIID FMode = AidMode;
  const HIID FCommAxes= AidCommon|AidAxes;
  const HIID FDefCellSize= AidDefault|AidCell|AidSize;

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
    int *id; //sequence of axes = [time,freq,spid id,perturbed value]
    // if no f or perturbed values are defined
    // they are set to -1
    double val;
    friend bool operator <(const IdVal& a, const IdVal& b);

  };
  bool operator <(const IdVal& a, const IdVal& b)
  {
    return a.val< b.val;
  }

  // helper func to convert anything to string
  template<class T> std::string 
  __to_string(T x) {
    std::stringstream ss;
    std::string str;
    ss << x;
    ss >> str;
    return str;
  }
  /********************************************/



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

    def_cell_size_=0.1;
  }

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
    FailWhen((mode_>3),FMode.toString()+" field must be 1 or 3, 2 not implementd");

    //Add these axes to Axis object
    Axis::addAxis(comm_axes_[0]);
    Axis::addAxis(comm_axes_[1]);

    rec[FSequenceSymdeps].get_vector(seq_symdeps_,initializing);

    //do not resample
    disableAutoResample();
    //get default cell size
    rec[FDefCellSize].get(def_cell_size_,initializing);

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
    childres.resize(2);
    unlockStateMutex();
    int code=result_code_=children().getChild(0).execute(child_res,request);
    lockStateMutex();
    childres[0]=child_res;
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

    /*** end poll child 0 **********************/

    /**** begin poll child 1 ******************/
    // extract values from the result of child 0 to define our axes
    Request::Ref newreq(request);

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
      if (mode_!=3) {
       domain().defineAxis(Axis::axis(comm_axes_[0]),-INFINITY,INFINITY);
       domain().defineAxis(Axis::axis(comm_axes_[1]),-INFINITY,INFINITY);
      }
      Cells::Ref outcells_ref0;
      Cells &outcells=outcells_ref0<<=new Cells(*domain);
      outcells.setCells(Axis::TIME,incells.center(Axis::TIME),incells.cellSize(Axis::TIME));
      outcells.setCells(Axis::FREQ,incells.center(Axis::FREQ),incells.cellSize(Axis::FREQ));

      if (mode_!=3) {
       outcells.setCells(Axis::axis(comm_axes_[0]),-INFINITY,INFINITY,1);
       outcells.setCells(Axis::axis(comm_axes_[1]),-INFINITY,INFINITY,1);
      }




      newreq().setCells(outcells);
      //increment request sequence sub id
      RequestId rqid=request.id();
      RqId::incrSubId(rqid,seq_depmask_);
      //set resolution sub id to node index of this node
      RqId::setSubId(rqid,res_depmask_,nodeIndex());
      newreq().setId(rqid);


      unlockStateMutex();
      code=children().getChild(1).execute(child_res,*newreq);
      lockStateMutex();
#ifdef DEBUG
      cout<<"Discover SPIDS Request Id="<<newreq->id()<<endl;
#endif

      childres[1]=child_res;
      resref.detach();
      unlockStateMutex();
      //we might have some step children ??
      stepchildren().backgroundPoll(*newreq);
      timers().children.stop();
      lockStateMutex();



      return code; 
    }
    // get input cells
    const Cells &incells=request.cells();
    int intime=incells.ncells(Axis::TIME);
    int infreq=incells.ncells(Axis::FREQ);
    //if we have a 4D request, recreate a 2D cells from it
    blitz::TinyVector<int,2> inshape(incells.ncells(0),incells.ncells(1));



    int naxis=childres[0]->numVellSets();
#ifdef DEBUG
    cout<<"Got "<<naxis<<" Vellsets"<<endl;
#endif

    FailWhen(naxis!=2,"We need 2 vellsets, but got "+__to_string(naxis));
		build_axes_(childres[0],intime,infreq);
    Cells::Ref outcells_ref;
    const Domain &old_dom=incells.domain();
    Domain::Ref domain(new Domain());


    int ntime,nfreq,nplanes;

    // get first vellset
    Vells vl0=childres[0]->vellSet(0).getValue();
    int nx=ntime=vl0.extent(0);
    int ny=nfreq=vl0.extent(1);
    //check for perturbed values
    int ipert0=childres[0]->vellSet(0).numPertSets();
    int ispid0=childres[0]->vellSet(0).numSpids();
#ifdef DEBUG
    cout<<"0: Pert "<<ipert0<<" Spids "<<ispid0<<endl;
#endif
    nplanes=ipert0*ispid0;

#ifdef DEBUG
    cout<<"Dimension "<<nx<<","<<ny<<","<<nplanes<<endl;
#endif


    //if there are any perturbed sets fill them.
    //Note that we start counting them from 1 onwards
    //Note also that there are 3 cases for perturbed sets.
    // 1) both axes (vellsets) have same number of perturbations
    // 2) axis 1 have perturbations but not axis 2
    // 3) axis 2 have perturbations but not axis 1
    // case 1) is standard. both axes share same plane number in id[2]
    // in case 2) or 3) the axis missing a perturbed value will use plane 0
    // as its perturbation. this should be done when building the map



    vl0=childres[0]->vellSet(1).getValue();
    nx=vl0.extent(0);
    ny=vl0.extent(1);
    //check for perturbed values
    int ipert1=childres[0]->vellSet(1).numPertSets();
    int ispid1=childres[0]->vellSet(1).numSpids();
#ifdef DEBUG
    cout<<"1: Pert "<<ipert1<<" Spids "<<ispid1<<endl;
#endif
    //check for consistency of perturbed values
    FailWhen(!((ipert0==ipert1 && ispid0==ispid1)
	       || ipert0*ispid0==0
	       || ipert1*ispid1==0),"Axis 1 returns "+__to_string(ipert0)+","+__to_string(ispid0)+" perturbations but axis 2 returns "+ __to_string(ipert1)+","+__to_string(ispid1));


    // the array for reverse mapping of sorted values
    // length =ntime*nfreq*(nplanes+1)
    // columns are= time, freq, plane, axis1, axis2
    // where axis1, axis2 are the location of the value on
    // sorted axis arrays
    // key=(time,freq,spid,perturbation), value=(axis1,axis2)
    // note in case where only one axis has perturbations, the value for the 
    // other axis will be taken from the value in plane 0
    //map<const std::vector<int>, int *, compare_vec> revmap_;

    map<const std::vector<int>, int *, compare_vec>::iterator mapiter=revmap_.begin();

    //define axis of the new domain
    if (mode_!=3) {
    if (old_dom.isDefined(Axis::TIME))
      domain().defineAxis(Axis::TIME, old_dom.start(Axis::TIME), old_dom.end(Axis::TIME));
    if (old_dom.isDefined(Axis::FREQ))
      domain().defineAxis(Axis::FREQ, old_dom.start(Axis::FREQ), old_dom.end(Axis::FREQ));
    }
		std::vector<blitz::Array<double,1> > space;
    //calculate grid spacing and bounds
		space.resize(grid_.size());
		for (unsigned int ch=0; ch<grid_.size(); ch++) {
      space[ch].resize(grid_[ch].extent(0));
      //create a space grid
      if (grid_[ch].extent(0)==1) {
        //scalar case
        space[ch](0)=def_cell_size_;
      } else {
       //vector case
       for (int i=1;i<grid_[ch].extent(0);i++) 
        	space[ch](i)=grid_[ch](i)-grid_[ch](i-1);
       space[ch](0)=space[ch](1);
      }
      //calculate extents for domain 
      double llimit=grid_[ch](0)-space[ch](0);
      double ulimit=grid_[ch](grid_[ch].extent(0)-1)+space[ch](grid_[ch].extent(0)-1);
      if (llimit==ulimit) ulimit=llimit+1; //catch scalar case
      domain().defineAxis(Axis::axis(comm_axes_[ch]),llimit,ulimit);
		}

    Cells &outcells=outcells_ref<<=new Cells(*domain);

    if (mode_!=3) {
    outcells.setCells(Axis::TIME,incells.center(Axis::TIME),incells.cellSize(Axis::TIME));
    outcells.setCells(Axis::FREQ,incells.center(Axis::FREQ),incells.cellSize(Axis::FREQ));
    }

#ifdef DEBUG
    cout<<"Request "<<grid_[0]<<" space "<<space[0]<<endl;
    cout<<"Request "<<grid_[1]<<" space "<<space[1]<<endl;
#endif

		 for (unsigned int ch=0; ch<grid_.size(); ch++) {
      outcells.setCells(Axis::axis(comm_axes_[ch]),grid_[ch],space[ch]);
		 }
#ifdef DEBUG
    cout<<"Request "<<outcells.center(Axis::axis(comm_axes_[0]))<<" space "<< outcells.cellSize(Axis::axis(comm_axes_[0]))<<endl;
    cout<<"Request "<<outcells.center(Axis::axis(comm_axes_[1]))<<" space "<< outcells.cellSize(Axis::axis(comm_axes_[1]))<<endl;
#endif

    newreq().setCells(outcells);
    //increment request sub id
    RequestId rqid=request.id();
    RqId::incrSubId(rqid,seq_depmask_);
    RqId::setSubId(rqid,res_depmask_,nodeIndex());
    newreq().setId(rqid);
#ifdef DEBUG
    cout<<"********************* Req Id "<<rqid<<endl;
#endif

    unlockStateMutex();
    code=children().getChild(1).execute(child_res,*newreq);
    lockStateMutex();

    //remember this result
    childres[1]=child_res;
    result_code_|=code;

    /*** end poll child 1 **********************/

    /**** begin processing of the result to correct for grid sorting */
    /** also create a new result with one vellset */
    Result &res1=result_<<= new Result(childres[1]->numVellSets(),childres[1]->isIntegrated());


   map<const VellSet::SpidType, int *, compare_spid>::iterator spmapiter=spidmap_.begin();
//// begin looping over child vellsets
    for (int ivs=0; ivs<childres[1]->numVellSets(); ivs++) {
    const Vells vl=childres[1]->vellSet(ivs).getValue();
    Vells &in=const_cast<Vells &>(vl);
    int npsetsf=childres[1]->vellSet(ivs).numPertSets();
    int nspidsf=childres[1]->vellSet(ivs).numSpids();

		//merge spids, if any
	  for (int ipert=0; ipert<nspidsf; ipert++)  {
				VellSet::SpidType spid=childres[1]->vellSet(ivs).getSpid(ipert);
        if (spidmap_.find(spid)==spidmap_.end()) {
					//insert
					int *dd=new int[naxis+1]; //last one for the funklet
          dd[0]=dd[1]=dd[2]=-1; //not found yet
					dd[naxis]=ipert;
          spidmap_[spid]=dd;
				} else {
					//this already exists
					int *dd=spidmap_[spid];
					dd[naxis]=ipert;
				}
	  }

#ifdef DEBUG
	 cout<<"Spids"<<endl;
    while(spmapiter!=spidmap_.end()) {
			VellSet::SpidType key=spmapiter->first;
      int *value=spmapiter->second;
      cout<<"["<<key<<"] = ["<<value[0]<<","<<value[1]<<","<<value[2]<<"]"<<endl;
      spmapiter++;
    }

#endif


    VellSet::Ref ref;
		//determine the correct spids and perturbations before creating 
		//the vellset. the priority is given to the axis child
		//so if either grid vellset 0 or 1 has them, the vellset
		//will be created to match those values. Else, the vellset
		//will be created to math the spid/perturbations of the funklet
		int npsets, nspids;
		npsets=0;
		//find the max value of perturbed sets from all vellsets
		for (int ch=0; ch<naxis; ch++ ) {
			if (childres[0]->vellSet(ch).numPertSets()>npsets) {
       npsets=childres[0]->vellSet(ch).numPertSets();
			}
		}
#ifdef  DEBUG
    cout<<"NPset "<<npsets<<endl;
#endif
		//check out the funklet too
		if (childres[1]->vellSet(ivs).numPertSets()>npsets) {
       npsets=childres[1]->vellSet(ivs).numPertSets();
		}
#ifdef DEBUG
    cout<<"NPset "<<npsets<<endl;
#endif
		//create a spids vector
    std::vector<VellSet::SpidType> newspids(spidmap_.size());
    spmapiter=spidmap_.begin();
		int sp_id=0;
		while(spmapiter!=spidmap_.end()) {
      newspids[sp_id++]=spmapiter->first;
			spmapiter++;
		}
		nspids=spidmap_.size();
    //create new vellset
    //FIXME: if nspids==0, no need to have npsets>0, so adjust it
    if (!nspids) npsets=0;
    VellSet &vs=ref <<=new VellSet(inshape,nspids,npsets);
    vs.setSpids(newspids);
#ifdef DEBUG
		cout<<"creating vellset with spids, pertsets"<<nspids<<","<<npsets<<endl;
#endif
    spmapiter=spidmap_.begin();
		sp_id=0;
		while(spmapiter!=spidmap_.end()) {
						int *dd=spmapiter->second;
						//find a sutitable result to get the perturbed values
						//for this spid, give priority to funklet
						//Note this does not check that number of perturbations are same in all results
						if (dd[2] !=-1) {
							//copy from funklet
							for (int ii=0; ii<npsets; ii++) 
							  vs.setPerturbation(sp_id,childres[1]->vellSet(ivs).getPerturbation(dd[2],ii),ii);
						} else if (dd[0] != -1) {
						 //copy from grid child 1
							for (int ii=0; ii<npsets; ii++) 
							  vs.setPerturbation(sp_id,childres[0]->vellSet(0).getPerturbation(dd[0],ii),ii);

						} else if (dd[1] != -1) {
						 //copy from grid child 2
						 for (int ii=0; ii<npsets; ii++) 
							  vs.setPerturbation(sp_id,childres[0]->vellSet(1).getPerturbation(dd[1],ii),ii);
						} else {
							//fali
#ifdef DEBUG
            cout<<"Fail. this cannot happen"<<endl;
#endif
						}
			      spmapiter++;
						sp_id++;
		}

	  if (in.isScalar()) {
		 ///handle scalar case
		 //FIXME : collapse axes first
		  if (in.isReal()) {
        double a=in.as<double>();
        Vells *out=new Vells(a);
        vs.setValue(out);
      } else {
        dcomplex a=in.as<dcomplex>();
        Vells *out=new Vells(a);
        vs.setValue(out);
      }
		} else {
		/////////////////////////////////////// real data
		if (in.isReal()) {
    Vells &out=vs.setValue(new Vells(0.0,inshape));
    //now fill in the values only defined at the original grid points
    //imagine the axes are (t,f,a,b): then for each (t,f) grid point
    //find points a0,b0 in a and b axes respectively. this value will
    //go to the new grid point (t,f)
    blitz::Array<double,2> A=out.as<double,2>()(blitz::Range::all(),blitz::Range::all());

    if (mode_!=3)  {
    blitz::Array<double,4> B=in.getArray<double,4>();
	
		
#ifdef DEBUG
    cout<<"In "<<intime<<","<<infreq<<endl;
    cout<<"InCells from funklet"<<endl;
		int fktime=vl.extent(Axis::TIME);
		int fkfreq=vl.extent(Axis::FREQ);
    cout<<"t,f="<<fktime<<","<<fkfreq<<endl;
    cout<<childres[1]->cells().center(Axis::axis(comm_axes_[0]))<<endl;
    cout<<childres[1]->cells().center(Axis::axis(comm_axes_[1]))<<endl;
#endif

    //apply the grid to main value
    apply_grid_map_2d4d(A, B, 0);

    // handle perturbed sets if any
		//
    spmapiter=spidmap_.begin();
		sp_id=0;
		while(spmapiter!=spidmap_.end()) {
       int *value=spmapiter->second;
       if (value[2]!=-1) {
					//spid in funklet, use the perturbed value from funklet
#ifdef DEBUG
          cout<<"(Real) Pert sets ="<< childres[1]->vellSet(ivs).numPertSets()<<endl;
#endif
          for (int ipset=0; ipset< childres[1]->vellSet(ivs).numPertSets(); ipset++) {
	          const Vells pvl=childres[1]->vellSet(ivs).getPerturbedValue(value[2],ipset);
	          Vells &pin=const_cast<Vells &>(pvl);
	          Vells &pout=vs.setPerturbedValue(sp_id,new Vells(0.0,inshape),ipset);
	          blitz::Array<double,2> pA=pout.as<double,2>()(blitz::Range::all(),blitz::Range::all());
	          blitz::Array<double,4> pB=pin.getArray<double,4>();
						if (value[0]==-1 && value[1]==-1) {
						  //not present in any of the axes
							//use the same grid as the main value
             apply_grid_map_2d4d(pA, pB, 0);
						} else {
						  //present in at least one of the axes
							//use the grid for this spid
             apply_grid_map_2d4d(pA, pB, spmapiter->first);
						}
					}
			 } else {
				  //no spid in funklet, use the main value of the funklet
					//use the main value from funklet, but use the grid
					//of the spid
					int npsets0=0;
					int spid=0;
					if (value[0]!=-1) {
							npsets0=childres[0]->vellSet(0).numPertSets();
					} else {
							npsets0=childres[0]->vellSet(1).numPertSets();
					}
#ifdef DEBUG
          cout<<"(Real) Pert sets ="<<npsets0<<endl;
#endif
					for (int ipset=0; ipset<npsets0; ipset++) {
	          Vells &pout=vs.setPerturbedValue(sp_id,new Vells(0.0,inshape),ipset);
	          blitz::Array<double,2> pA=pout.as<double,2>()(blitz::Range::all(),blitz::Range::all());
	
            apply_grid_map_2d4d(pA, B, spmapiter->first);
					}
			 }	 
       spmapiter++;
			 sp_id++;
		}
    } else {
     //simple 2D case 
     blitz::Array<double,2> B=in.getArray<double,2>();
     A=B;
    }
	
		} else {
		/////////////////////////////////////// complex data
	  Vells &out=vs.setValue(new Vells(make_dcomplex(0.0),inshape));
    //now fill in the values only defined at the original grid points
    //imagine the axes are (t,f,a,b): then for each (t,f) grid point
    //find points a0,b0 in a and b axes respectively. this value will
    //go to the new grid point (t,f)
    blitz::Array<dcomplex,2> A=out.as<dcomplex,2>()(blitz::Range::all(),blitz::Range::all());

    if (mode_!=3)  {
    blitz::Array<dcomplex,4> B=in.getArray<dcomplex,4>();

    //apply the grid to main value
    apply_grid_map_2d4d(A, B, 0);

    // handle perturbed sets if any
		//
    spmapiter=spidmap_.begin();
		sp_id=0;
		while(spmapiter!=spidmap_.end()) {
       int *value=spmapiter->second;
       if (value[2]!=-1) {
					//spid in funklet, use the perturbed value from funklet
#ifdef DEBUG
          cout<<"(Complex ) Pert sets ="<< childres[1]->vellSet(ivs).numPertSets()<<endl;
#endif
          for (int ipset=0; ipset< childres[1]->vellSet(ivs).numPertSets(); ipset++) {
	          const Vells pvl=childres[1]->vellSet(ivs).getPerturbedValue(value[2],ipset);
	          Vells &pin=const_cast<Vells &>(pvl);
	          Vells &pout=vs.setPerturbedValue(sp_id,new Vells(make_dcomplex(0.0),inshape),ipset);
	          blitz::Array<dcomplex,2> pA=pout.as<dcomplex,2>()(blitz::Range::all(),blitz::Range::all());
	          blitz::Array<dcomplex,4> pB=pin.getArray<dcomplex,4>();
						if (value[0]==-1 && value[1]==-1) {
						  //not present in any of the axes
							//use the same grid as the main value
             apply_grid_map_2d4d(pA, pB, 0);
						} else {
						  //present in at least one of the axes
							//use the grid for this spid
             apply_grid_map_2d4d(pA, pB, spmapiter->first);
						}
					}
			 } else {
				  //no spid in funklet, use the main value of the funklet
					//use the main value from funklet, but use the grid
					//of the spid
					int npsets0=0;
					int spid=0;
					if (value[0]!=-1) {
							npsets0=childres[0]->vellSet(0).numPertSets();
					} else {
							npsets0=childres[0]->vellSet(1).numPertSets();
					}
#ifdef DEBUG
          cout<<"(Complex ) Pert sets ="<<npsets0<<endl;
#endif
					for (int ipset=0; ipset<npsets0; ipset++) {
	          Vells &pout=vs.setPerturbedValue(sp_id,new Vells(make_dcomplex(0.0),inshape),ipset);
	          blitz::Array<dcomplex,2> pA=pout.as<dcomplex,2>()(blitz::Range::all(),blitz::Range::all());
	
            apply_grid_map_2d4d(pA, B, spmapiter->first);
					}
			 }	 
       spmapiter++;
			 sp_id++;
		}
		
    } else {
     //simple 2D case 
     blitz::Array<dcomplex,2> B=in.getArray<dcomplex,2>();
     A=B;
    }
	  }
 
		}
		res1.setVellSet(ivs,ref);



    }
//////// end loop over vellsets
    //delete map
		std::list<int*>::iterator liter=maplist_.begin();
    while(liter!=maplist_.end()) {
      delete [] *liter;
      liter++;
    }
		maplist_.clear();
		revmap_.clear();

    spmapiter=spidmap_.begin();
    while(spmapiter!=spidmap_.end()) {
      delete [] spmapiter->second;
      spmapiter++;
    }
		spidmap_.clear();

    res1.setCells(incells);
  /// if funklet child has more than 1 vellset and it also has dims, copy them
    if (childres[1]->numVellSets()> 1) {
	    res1.setDims(childres[1]->dims());
    }

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

//IN: grid child result, request time,freq
//OUT: vector of funklet request grids, map for mapping back grid values 
//to time,freq,spid, perturbation
int Compounder::build_axes_(Result::Ref &childres, int intime, int infreq) {


	 //sorting array
   blitz::Array<IdVal,1> sarray;

   int naxes=childres->numVellSets();
	 //resize grid
	 grid_.resize(naxes);

   std::vector<int> aa(4);
   for (int ch=0; ch<naxes; ch++) {
    Vells vl0=childres->vellSet(ch).getValue();
    int nx=vl0.extent(0);
    int ny=vl0.extent(1);
    //check for perturbed values
    int ipert0=childres->vellSet(ch).numPertSets();
    int ispid0=childres->vellSet(ch).numSpids();
#ifdef DEBUG
    cout<<ch<<": Pert "<<ipert0<<" Spids "<<ispid0<<endl;
#endif

    int nplanes=ipert0*ispid0;
#ifdef DEBUG
    cout<<"Dimension "<<nx<<","<<ny<<","<<nplanes<<endl;
#endif

    grid_[ch].resize(nx*ny*(nplanes+1));
    //create axis vector
    if (ny==1) {
			//note: even when ny==1, we might get a 2D array here
      //blitz::Array<double,1> data=vl0.as<double,1>()(blitz::Range::all());
      double *data_=vl0.getStorage<double>();
      blitz::Array<double,1> data(data_, blitz::shape(nx), blitz::neverDeleteData); 
#ifdef DEBUG
      cout<<"Axis "<<ch<<" 1 (in)="<<data<<endl;
#endif
      //cen0=vl0.as<double,1>();
      grid_[ch]=data(blitz::Range::all(),0);
    } else  {
      blitz::Array<double,2> data=vl0.as<double,2>()(blitz::Range::all(),blitz::Range::all());
#ifdef DEBUG
      cout<<"Axis "<<ch<<" 1 (in)="<<data<<endl;
#endif
      //copy each columns from column 0 to ny-1
      for (int i=0; i<ny;i++)  {
	     grid_[ch](blitz::Range(i*nx,(i+1)*nx-1))=data(blitz::Range::all(),i);
      }
    }

    //if there are any perturbed sets fill them.
    //Note that we start counting them from 1 onwards
    //Note also that there are 3 cases for perturbed sets.
    // 1) both axes (vellsets) have same number of perturbations
    // 2) axis 1 have perturbations but not axis 2
    // 3) axis 2 have perturbations but not axis 1
    // case 1) is standard. both axes share same plane number in id[2]
    // in case 2) or 3) the axis missing a perturbed value will use plane 0
    // as its perturbation. this should be done when building the map
    if (nplanes>0) {
	    for (int ipert=0; ipert<ispid0; ipert++)  {
				//remember this spid
				VellSet::SpidType spid=childres->vellSet(ch).getSpid(ipert);
        if (spidmap_.find(spid)==spidmap_.end()) {
					//insert
					int *dd=new int[naxes+1]; //last one for the funklet
          dd[0]=dd[1]=dd[2]=-1; //not found yet
					dd[ch]=ipert;
          spidmap_[spid]=dd;
				} else {
					//this already exists
					int *dd=spidmap_[spid];
					dd[ch]=ipert;
				}
        for (int ipset=0; ipset<ipert0; ipset++)  {
	          Vells pvl=childres->vellSet(ch).getPerturbedValue(ipert,ipset);
	          blitz::Array<double,1> pB(nx*ny);
	          if (ny==1) {
               double *data_=pvl.getStorage<double>();
               blitz::Array<double,1> data(data_, blitz::shape(nx), blitz::neverDeleteData); 
	             pB=data(blitz::Range::all(),0);
	          } else  {
	            blitz::Array<double,2> data=pvl.as<double,2>()(blitz::Range::all(),blitz::Range::all());
	           //copy each columns from column 0 to ny-1
	           for (int i=0; i<ny;i++)  {
	             pB(blitz::Range(i*nx,(i+1)*nx-1))=data(blitz::Range::all(),i);
	           }
	         }

	         //finally copy to original array
	         grid_[ch](blitz::Range(nx*ny*(ispid0*ipset+ipert+1),nx*ny*(ispid0*ipset+ipert+2)-1))=pB;
	}
      }
    }
#ifdef DEBUG
    cout<<"Axis "<<ch<<" 1="<<grid_[ch]<<endl;
#endif


		//sorting...sorting..
    sarray.resize(grid_[ch].extent(0));


    //copy data
    int k=0;
    for (int i=0; i<ny;i++) {
      for (int j=0; j<nx;j++) {
      	sarray(k).id=new int[4];
	      sarray(k).id[0]=j;
	      sarray(k).id[1]=i;
	      sarray(k).id[2]=0;
	      sarray(k).id[3]=0;
	      sarray(k).val=grid_[ch](k);
	      k++;
      }
    }
    if (nplanes>0) {
      //we have perturbed values, so copy them
      for (int ipset=0; ipset<ipert0; ipset++)  {
           for (int ipert=0; ipert<ispid0; ipert++)  {
	             for (int i=0; i<ny;i++) {
	                for (int j=0; j<nx;j++) {
	                  sarray(k).id=new int[4];
	                  sarray(k).id[0]=j;
	                  sarray(k).id[1]=i;
	                  sarray(k).id[2]=childres->vellSet(ch).getSpid(ipert);
	                  sarray(k).id[3]=ipset;
	                  sarray(k).val=grid_[ch](k);
	                  k++;
	               }
	            }
	        }
      }
    }

#ifdef DEBUG
    cout<<"Before sort"<<endl;
    for (int i=0; i<sarray.extent(0);i++) {
      cout<<i<<"="<<sarray(i).id[0]<<","<<sarray(i).id[1]<<","<<sarray(i).id[2]<<","<<sarray(i).id[3]<<","<<sarray(i).val<<endl;
    }
#endif
    std::sort(sarray.data(), sarray.data()+sarray.extent(0));
#ifdef DEBUG
    cout<<"After sort"<<endl;
    for (int i=0; i<sarray.extent(0);i++) {
      cout<<i<<"="<<sarray(i).id[0]<<","<<sarray(i).id[1]<<","<<sarray(i).id[2]<<","<<sarray(i).id[3]<<","<<sarray(i).val<<endl;
    }
#endif
    //overwrite the old array
    //also build rev map
    for (int i=0; i<sarray.extent(0);i++) {
      grid_[ch](i)=sarray(i).val;
      aa[0]=sarray(i).id[0];
      aa[1]=sarray(i).id[1];
      aa[2]=sarray(i).id[2];
      aa[3]=sarray(i).id[3];
      if(revmap_.find(aa)==revmap_.end()) {
        //cannot find it, use the 0-th plane value
        int *bb=new int[naxes]; //leak!!
				for (int jj=0; jj<naxes; jj++) bb[jj]=0;
        //rest not yet defined
        bb[ch]=i;
        revmap_[aa]=bb;
				maplist_.push_front(bb);
			} else {
        int *bb=revmap_[aa];
				bb[ch]=i;
			} 

    }
#ifdef DEBUG
   map<const std::vector<int>, int *, compare_vec>::iterator mapiter=revmap_.begin();
    while(mapiter!=revmap_.end()) {
      std::vector<int> key=mapiter->first;
      int *value=mapiter->second;
      cout<<"["<<key[0]<<","<<key[1]<<","<<key[2]<<","<<key[3]<<"] = ["<<value[0]<<","<<value[1]<<"]"<<endl;
      mapiter++;
    }
#endif

    for (int i=0; i<sarray.extent(0);i++) {
      delete [] sarray(i).id;
    }

   }

  std::vector<int> atf(4);
  //handle degenerate axes
  for (int ch=0; ch<naxes; ch++) {
    int ipert0=childres->vellSet(ch).numPertSets();
    int ispid0=childres->vellSet(ch).numSpids();

    int nx=childres->vellSet(ch).getValue().extent(0);
    int ny=childres->vellSet(ch).getValue().extent(1);

	  if (intime*infreq*(ipert0*ispid0+1)>grid_[ch].extent(0)) {
				//we have degeneray in time or frequency or in both so copy the
				//appropriate t,f value to this location
#ifdef DEBUG
				cout<<"LM degeneracy 0: in t,f because "<<intime<<","<<infreq<<","<<ipert0<<","<<ispid0<<","<<grid_[ch].extent(0)<<",["<<nx<<","<<ny<<"]"<<endl;
#endif
				for (int i=1; i<intime; i++) {
					for (int j=0; j<infreq; j++) {
            aa[0]=i;
            aa[1]=j;
            aa[2]=aa[3]=0; //main value
            if(revmap_.find(aa)==revmap_.end()) {
							//check for time only degeneracy
							atf[0]=atf[2]=atf[3]=0;
							atf[1]=j;
              if(revmap_.find(atf)!=revmap_.end()) {
               revmap_[aa]=revmap_[atf];
							} else {
							  //check for freq only degeneracy
							  atf[1]=0;
							  atf[0]=i;
                if(revmap_.find(atf)!=revmap_.end()) {
                  revmap_[aa]=revmap_[atf];
								} else {
                  int *bb=new int[naxes];
		     		     for (int jj=0; jj<naxes; jj++) bb[jj]=0;
                 revmap_[aa]=bb;
				         maplist_.push_front(bb);
								}
							}
					  }
            for (int ipset=0; ipset<ipert0; ipset++)  {
                for (int ipert=0; ipert<ispid0; ipert++)  {
	                aa[2]=childres->vellSet(ch).getSpid(ipert);
                  aa[3]=ipset;
                  if(revmap_.find(aa)==revmap_.end()) {
       							//check for time only degeneracy
			      				atf[0]=0;
					      		atf[1]=j;
			      				atf[2]=aa[2];
			      				atf[3]=aa[3];
                    if(revmap_.find(atf)!=revmap_.end()) {
                      revmap_[aa]=revmap_[atf];
							      } else {
							        //check for freq only degeneracy
							        atf[1]=0;
							        atf[0]=i;
                      if(revmap_.find(atf)!=revmap_.end()) {
                        revmap_[aa]=revmap_[atf];
								      } else {
                        int *bb=new int[naxes];
		     		            for (int jj=0; jj<naxes; jj++) bb[jj]=0;
                        revmap_[aa]=bb;
				                maplist_.push_front(bb);
							      	}
							     }

									}
					     }
			      }
					}
				}
				for (int j=1; j<infreq; j++) {
            aa[0]=0;
            aa[1]=j;
            aa[2]=aa[3]=0; //main value
            if(revmap_.find(aa)==revmap_.end()) {
							//check for time only degeneracy
							atf[0]=atf[2]=atf[3]=0;
							atf[1]=j;
              if(revmap_.find(atf)!=revmap_.end()) {
               revmap_[aa]=revmap_[atf];
							} else {
							  //check for freq only degeneracy
							  atf[1]=0;
							  atf[0]=0;
                if(revmap_.find(atf)!=revmap_.end()) {
                  revmap_[aa]=revmap_[atf];
								} else {
                  int *bb=new int[naxes];
		     		     for (int jj=0; jj<naxes; jj++) bb[jj]=0;
                 revmap_[aa]=bb;
				         maplist_.push_front(bb);
								}
							}
					  }

            for (int ipset=0; ipset<ipert0; ipset++)  {
               for (int ipert=0; ipert<ispid0; ipert++)  {
	                aa[2]=childres->vellSet(ch).getSpid(ipert);
                  aa[3]=ipset;
                  if(revmap_.find(aa)==revmap_.end()) {
       							//check for time only degeneracy
			      				atf[0]=0;
					      		atf[1]=j;
			      				atf[2]=aa[2];
			      				atf[3]=aa[3];
                    if(revmap_.find(atf)!=revmap_.end()) {
                      revmap_[aa]=revmap_[atf];
							      } else {
							        //check for freq only degeneracy
							        atf[1]=0;
							        atf[0]=0;
                      if(revmap_.find(atf)!=revmap_.end()) {
                        revmap_[aa]=revmap_[atf];
								      } else {
                        int *bb=new int[naxes];
		     		            for (int jj=0; jj<naxes; jj++) bb[jj]=0;
                        revmap_[aa]=bb;
				                maplist_.push_front(bb);
							      	}
							     }
									}

					     }
			      }

				}

		 }

		}
#ifdef DEBUG
   map<const std::vector<int>, int *, compare_vec>::iterator mapiter=revmap_.begin();
    while(mapiter!=revmap_.end()) {
      std::vector<int> key=mapiter->first;
      int *value=mapiter->second;
      cout<<"["<<key[0]<<","<<key[1]<<","<<key[2]<<","<<key[3]<<"] = ["<<value[0]<<","<<value[1]<<"]"<<endl;
      mapiter++;
    }
   map<const VellSet::SpidType, int *, compare_spid>::iterator spmapiter=spidmap_.begin();
    while(spmapiter!=spidmap_.end()) {
			VellSet::SpidType key=spmapiter->first;
      int *value=spmapiter->second;
      cout<<"["<<key<<"] = ["<<value[0]<<","<<value[1]<<","<<value[2]<<"]"<<endl;
      spmapiter++;
    }

#endif



	 return 0;

}

template<class T>
int Compounder::apply_grid_map_2d4d( blitz::Array<T,2> A, blitz::Array<T,4> B, int spid ) {
    int itime, ifreq, il, im;
    map<const std::vector<int>, int *, compare_vec>::iterator mapiter=revmap_.begin();
		int fktime=B.extent(0);
		int fkfreq=B.extent(1);
		int fl=B.extent(2);
		int fm=B.extent(3);
		int sp_id;
    while(mapiter!=revmap_.end()) {
      std::vector<int> key=mapiter->first;
      int *value=mapiter->second;
      itime=key[0];
      ifreq=key[1];
      sp_id=key[2];
#ifdef DEBUG
			cout<<"look for "<<itime<<","<<ifreq<<endl;
#endif
      if (sp_id==spid) { // if 0, it is the main value
			 //check for degeneracy in funklet value too
			 if (itime>=fktime) itime=0;
			 if (ifreq>=fkfreq) ifreq=0;
			 il=value[0];
			 im=value[1];
			 if (value[0]>=fl) il=0;
			 if (value[1]>=fm) im=0;
       A(key[0],key[1])=B(itime,ifreq,il,im);
#ifdef DEBUG
			cout<<"copy "<<itime<<","<<ifreq<<" "<<A(key[0],key[1])<<endl;
#endif
			}
      mapiter++;
    }


			return 0;
}

} // namespace Meq

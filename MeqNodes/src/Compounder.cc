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
#include <map>


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
    int *id; //sequence of axes t,f,perturbed values...
    // if no f or perturbed values are defined
    // they are set to -1
    double val;
    friend bool operator <(const IdVal& a, const IdVal& b);

  };
  bool operator <(const IdVal& a, const IdVal& b)
  {
    return a.val< b.val;
  }
  // for the map less than comparison
  struct compare_vec{
    bool operator()(const std::vector<int> v1, const std::vector<int> v2) const
    {
      return ((v1[0] < v2[0]) 
	      ||( (v1[0] == v2[0]) && (v1[1] < v2[1]))
	      ||( (v1[0] == v2[0]) && (v1[1] == v2[1]) && (v1[2] < v2[2])));
    }
  };

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
      resref.xfer(child_res);
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
      domain().defineAxis(Axis::axis(comm_axes_[0]),-INFINITY,INFINITY);
      domain().defineAxis(Axis::axis(comm_axes_[1]),-INFINITY,INFINITY);
      Cells::Ref outcells_ref0;
      Cells &outcells=outcells_ref0<<=new Cells(*domain);
      outcells.setCells(Axis::TIME,incells.center(Axis::TIME),incells.cellSize(Axis::TIME));
      outcells.setCells(Axis::FREQ,incells.center(Axis::FREQ),incells.cellSize(Axis::FREQ));

      outcells.setCells(Axis::axis(comm_axes_[0]),-INFINITY,INFINITY,1);
      outcells.setCells(Axis::axis(comm_axes_[1]),-INFINITY,INFINITY,1);




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
#ifdef DEBUG
      cout<<"Request Id="<<newreq().id()<<endl;
#endif

      childres[1]=child_res1;
      resref.detach();
      unlockStateMutex();
      //we do not have any step children ??
      // stepchildren().backgroundPoll(*newreq);
      timers().children.stop();
      lockStateMutex();



      return code; 
    }

    int nvs=child_res().numVellSets();
#ifdef DEBUG
    cout<<"Got "<<nvs<<" Vellsets"<<endl;
#endif

    FailWhen(nvs!=2,"We need 2 vellsets, but got "+__to_string(nvs));
    // get input cells
    const Cells &incells=request.cells();
    Cells::Ref outcells_ref;
    const Domain &old_dom=incells.domain();
    Domain::Ref domain(new Domain());

    double start0,end0,start1,end1;
    blitz::Array<double,1> cen0;
    blitz::Array<double,1> cen1;
		VellSet::Ref vsax0;
		VellSet::Ref vsax1;

    int ntime,nfreq,nplanes;

    // get first vellset
		vsax0=child_res->vellSetRef(0);
    Vells vl0=child_res().vellSet(0).getValue();
    int nx=ntime=vl0.extent(0);
    int ny=nfreq=vl0.extent(1);
    //check for perturbed values
    int ipert0=child_res().vellSet(0).numPertSets();
    int ispid0=child_res().vellSet(0).numSpids();
#ifdef DEBUG
    cout<<"0: Pert "<<ipert0<<" Spids "<<ispid0<<endl;
#endif
    nplanes=ipert0*ispid0;

#ifdef DEBUG
    cout<<"Dimension "<<nx<<","<<ny<<","<<nplanes<<endl;
#endif

    cen0.resize(nx*ny*(nplanes+1));
    //create axis vector
    if (ny==1) {
			//note: even when ny==1, we might get a 2D array here
      //blitz::Array<double,1> data=vl0.as<double,1>()(blitz::Range::all());
      double *data_=vl0.getStorage<double>();
      blitz::Array<double,1> data(data_, blitz::shape(nx), blitz::neverDeleteData); 
#ifdef DEBUG
      cout<<"Axis 1 (in)="<<data<<endl;
#endif
      //cen0=vl0.as<double,1>();
      cen0=data(blitz::Range::all(),0);
    } else  {
      blitz::Array<double,2> data=vl0.as<double,2>()(blitz::Range::all(),blitz::Range::all());
#ifdef DEBUG
      cout<<"Axis 1 (in)="<<data<<endl;
#endif
      //copy each columns from column 0 to ny-1
      for (int i=0; i<ny;i++)  {
	cen0(blitz::Range(i*nx,(i+1)*nx-1))=data(blitz::Range::all(),i);
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
    if (ipert0*ispid0>0) {
      for (int ipset=0; ipset<ipert0; ipset++)  {
	for (int ipert=0; ipert<ispid0; ipert++)  {
	  Vells pvl=child_res->vellSet(0).getPerturbedValue(ipert,ipset);

	  blitz::Array<double,1> pB(nx*ny);
	  if (ny==1) {
      //note: even when ny==1, we might get a 2D array here
	    //blitz::Array<double,1> data=pvl.as<double,1>()(blitz::Range::all());
      double *data_=pvl.getStorage<double>();
      blitz::Array<double,1> data(data_, blitz::shape(nx), blitz::neverDeleteData); 
#ifdef DEBUG
	    cout<<"Axis 1 (in)="<<data<<endl;
#endif
	    //cen0=vl0.as<double,1>();
	    pB=data(blitz::Range::all(),0);
	  } else  {
	    blitz::Array<double,2> data=pvl.as<double,2>()(blitz::Range::all(),blitz::Range::all());
#ifdef DEBUG
	    cout<<"Axis 1 (in)="<<data<<endl;
#endif
	    //copy each columns from column 0 to ny-1
	    for (int i=0; i<ny;i++)  {
	      pB(blitz::Range(i*nx,(i+1)*nx-1))=data(blitz::Range::all(),i);
	    }
	  }

	  //finally copy to original array
	  cen0(blitz::Range(nx*ny*(ispid0*ipset+ipert+1),nx*ny*(ispid0*ipset+ipert+2)-1))=pB;
	}
      }
    }
#ifdef DEBUG
    cout<<"Axis 1="<<cen0<<endl;
#endif



    //if the grid function is not monotonically increasing, we get
    //unsorted arrays for axes.
    //if cen0 or cen1 is not sorted, we recreate that
    //axis to cover the whole range and interpolate the result
    //use STL
    blitz::Array<IdVal,1> sarray0(cen0.extent(0));
    //copy data
    int k=0;
    for (int i=0; i<ny;i++) {
      for (int j=0; j<nx;j++) {
      	sarray0(k).id=new int[3];
	      sarray0(k).id[0]=j;
	      sarray0(k).id[1]=i;
	      sarray0(k).id[2]=0;
	      sarray0(k).val=cen0(k);
	      k++;
      }
    }
    if (nplanes>0) {
      //we have perturbed values, so copy them
      for (int ipset=0; ipset<ipert0; ipset++)  {
           for (int ipert=0; ipert<ispid0; ipert++)  {
	             for (int i=0; i<ny;i++) {
	                for (int j=0; j<nx;j++) {
	                  sarray0(k).id=new int[3];
	                  sarray0(k).id[0]=j;
	                  sarray0(k).id[1]=i;
	                  sarray0(k).id[2]=ipset*ispid0+ipert+1;
	                  sarray0(k).val=cen0(k);
	                  k++;
	               }
	            }
	        }
      }
    }

    // do all of the above for second vellset
		vsax1=child_res->vellSetRef(1);
    vl0=child_res->vellSet(1).getValue();
    nx=vl0.extent(0);
    ny=vl0.extent(1);
    //check for perturbed values
    int ipert1=child_res->vellSet(1).numPertSets();
    int ispid1=child_res->vellSet(1).numSpids();
#ifdef DEBUG
    cout<<"1: Pert "<<ipert1<<" Spids "<<ispid1<<endl;
#endif
    //check for consistency of perturbed values
    FailWhen(!((ipert0==ipert1 && ispid0==ispid1)
	       || ipert0*ispid0==0
	       || ipert1*ispid1==0),"Axis 1 returns "+__to_string(ipert0)+","+__to_string(ispid0)+" perturbations but axis 2 returns "+ __to_string(ipert1)+","+__to_string(ispid1));

    int have_perturbed_sets=-1; //flag
    if ((ipert0==ipert1 && ispid0==ispid1 && ipert0*ispid0>0 && ipert1*ispid1>0)) {
      have_perturbed_sets=0; //common case, both axes have same perturbations
    } else if (ipert0*ispid0==0 && ipert1*ispid1!=0 ) { //only axis 2 have perturbations
      have_perturbed_sets=2; 
    } else if (ipert1*ispid1==0 && ipert0*ispid0!=0) { //only axis 1 have perturbations
      have_perturbed_sets=1; 
    }
    if (ntime<nx) {ntime=nx;}
    if (nfreq<ny) {nfreq=ny;}
    if (nplanes<ipert1*ispid1) { nplanes=ipert1*ispid1;}
#ifdef DEBUG
    cout<<"Dimension "<<nx<<","<<ny<<","<<nplanes<<endl;
#endif
    //create axis vector
    cen1.resize(nx*ny*(ipert1*ispid1+1));
    if (ny==1) {
    	//note: even when ny==1, we might get a 2D array here
      //blitz::Array<double,1> data=vl0.as<double,1>()(blitz::Range::all());
      double *data_=vl0.getStorage<double>();
      blitz::Array<double,1> data(data_, blitz::shape(nx), blitz::neverDeleteData); 
#ifdef DEBUG
      cout<<"Axis 2 (in)="<<data<<endl;
#endif
      cen1=data(blitz::Range::all(),0);
    } else {
      blitz::Array<double,2> data=vl0.as<double,2>()(blitz::Range::all(),blitz::Range::all());
#ifdef DEBUG
      cout<<"Axis 2 (in)="<<data<<endl;
#endif
      //copy each columns from column 0 to ny-1
      for (int i=0; i<ny;i++)  {
	cen1(blitz::Range(i*nx,(i+1)*nx-1))=data(blitz::Range::all(),i);
      }
    }

    if (ipert1*ispid1>0) {
      for (int ipset=0; ipset<ipert1; ipset++)  {
	     for (int ipert=0; ipert<ispid1; ipert++)  {
	      Vells pvl=child_res->vellSet(1).getPerturbedValue(ipert,ipset);

	    blitz::Array<double,1> pB(nx*ny);
	  if (ny==1) {
    	//note: even when ny==1, we might get a 2D array here
	    //blitz::Array<double,1> data=pvl.as<double,1>()(blitz::Range::all());
      double *data_=pvl.getStorage<double>();
      blitz::Array<double,1> data(data_, blitz::shape(nx), blitz::neverDeleteData); 
#ifdef DEBUG
	    cout<<"Axis 2 (in)="<<data<<endl;
#endif
	    //cen0=vl0.as<double,1>();
	    pB=data(blitz::Range::all(),0);
	  } else  {
	    blitz::Array<double,2> data=pvl.as<double,2>()(blitz::Range::all(),blitz::Range::all());
#ifdef DEBUG
	    cout<<"Axis 2 (in)="<<data<<endl;
#endif
	    //copy each columns from column 0 to ny-1
	    for (int i=0; i<ny;i++)  {
	      pB(blitz::Range(i*nx,(i+1)*nx-1))=data(blitz::Range::all(),i);
	    }
	  }

	  //finally copy to original array
	  cen1(blitz::Range(nx*ny*(ispid1*ipset+ipert+1),nx*ny*(ispid1*ipset+ipert+2)-1))=pB;
	}
      }
    }
#ifdef DEBUG
    cout<<"Axis 2="<<cen1<<endl;
#endif



    blitz::Array<IdVal,1> sarray1(cen1.extent(0));
    //copy data
    k=0;
    for (int i=0; i<ny;i++) {
      for (int j=0; j<nx; j++) {
	sarray1(k).id=new int[3];
	sarray1(k).id[0]=j;
	sarray1(k).id[1]=i;
	sarray1(k).id[2]=0;
	sarray1(k).val=cen1(k);
	k++;
      }
    }
    if ( ipert1*ispid1>0) {
      //we have perturbed values, so copy them
      for (int ipset=0; ipset<ipert1; ipset++)  {
	for (int ipert=0; ipert<ispid1; ipert++)  {
	  for (int i=0; i<ny;i++) {
	    for (int j=0; j<nx;j++) {
	      sarray1(k).id=new int[3];
	      sarray1(k).id[0]=j;
	      sarray1(k).id[1]=i;
	      sarray1(k).id[2]=ipset*ispid1+ipert+1;
	      sarray1(k).val=cen1(k);
	      k++;
	    }
	  }
	}
      }

    }
    //we consider the value[] vells as the 0-th plane
#ifdef DEBUG
    cout<<"Time ="<<ntime<<" Freq="<<nfreq<<" Perturbed Planes="<<nplanes<<endl;
#endif

    // the array for reverse mapping of sorted values
    // length =ntime*nfreq*(nplanes+1)
    // columns are= time, freq, plane, axis1, axis2
    // where axis1, axis2 are the location of the value on
    // sorted axis arrays
    // key=(time,freq,plane), value=(axis1,axis2)
    // note in case where only one axis has perturbations, the value for the 
    // other axis will be taken from the value in plane 0
    map<const std::vector<int>, int *, compare_vec> revmap;

#ifdef DEBUG
    cout<<"Before sort"<<endl;
    for (int i=0; i<sarray0.extent(0);i++) {
      cout<<i<<"="<<sarray0(i).id[0]<<","<<sarray0(i).id[1]<<","<<sarray0(i).id[2]<<","<<sarray0(i).val<<endl;
    }
#endif
    std::sort(sarray0.data(), sarray0.data()+sarray0.extent(0));
#ifdef DEBUG
    cout<<"After sort"<<endl;
    for (int i=0; i<sarray0.extent(0);i++) {
      cout<<i<<"="<<sarray0(i).id[0]<<","<<sarray0(i).id[1]<<","<<sarray0(i).id[2]<<","<<sarray0(i).val<<endl;
    }
#endif
    //overwrite the old array
    //also build rev map
    std::vector<int> aa(3);
    for (int i=0; i<sarray0.extent(0);i++) {
      cen0(i)=sarray0(i).val;
      aa[0]=sarray0(i).id[0];
      aa[1]=sarray0(i).id[1];
      aa[2]=sarray0(i).id[2];
      int *bb=new int[2];
      bb[0]=i;
      bb[1]=0; //not yet defined
      revmap[aa]=bb;
    }

#ifdef DEBUG
    cout<<"Before sort"<<endl;
    for (int i=0; i<sarray1.extent(0);i++) {
      cout<<i<<"="<<sarray1(i).id[0]<<","<<sarray1(i).id[1]<<","<<sarray1(i).id[2]<<","<<sarray1(i).val<<endl;
    }
#endif
    std::sort(sarray1.data(), sarray1.data()+sarray1.extent(0));
#ifdef DEBUG
    cout<<"After sort"<<endl;
    for (int i=0; i<sarray1.extent(0);i++) {
      cout<<i<<"="<<sarray1(i).id[0]<<","<<sarray1(i).id[1]<<","<<sarray1(i).id[2]<<","<<sarray1(i).val<<endl;
    }
#endif
    //overwrite the old array
    //also update rev map
    for (int i=0; i<sarray1.extent(0);i++) {
      cen1(i)=sarray1(i).val;
      aa[0]=sarray1(i).id[0];
      aa[1]=sarray1(i).id[1];
      aa[2]=sarray1(i).id[2];
      //try to get value
      //
      if(revmap.find(aa)==revmap.end()) {
	//not found
	int *bb=new int[2];
	bb[0]=0;//not yet defined
	bb[1]=i; 
	revmap[aa]=bb;
      } else {
	int *bb=revmap[aa];
	bb[1]=i; 
      }

    }
    map<const std::vector<int>, int *, compare_vec>::iterator mapiter=revmap.begin();
    //first: key, second: value
#ifdef DEBUG
    while(mapiter!=revmap.end()) {
      std::vector<int> key=mapiter->first;
      int *value=mapiter->second;
      cout<<"["<<key[0]<<","<<key[1]<<","<<key[2]<<"] = ["<<value[0]<<","<<value[1]<<"]"<<endl;
      mapiter++;
    }
#endif
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
    //domain().defineAxis(Axis::axis(comm_axes_[0]),-10000,10000);
    domain().defineAxis(Axis::axis(comm_axes_[1]),start1,end1);
    //domain().defineAxis(Axis::axis(comm_axes_[1]),-10000,10000);
    Cells &outcells=outcells_ref<<=new Cells(*domain);

    outcells.setCells(Axis::TIME,incells.center(Axis::TIME),incells.cellSize(Axis::TIME));
    outcells.setCells(Axis::FREQ,incells.center(Axis::FREQ),incells.cellSize(Axis::FREQ));

#ifdef DEBUG
    cout<<"Request "<<cen0<<" space "<<space0<<endl;
    cout<<"Request "<<cen1<<" space "<<space1<<endl;
#endif

    outcells.setCells(Axis::axis(comm_axes_[0]),cen0,space0);
    outcells.setCells(Axis::axis(comm_axes_[1]),cen1,space1);
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
    Result::Ref res0=child_res;
    result_code_|=code;

    /*** end poll child 1 **********************/

    /**** begin processing of the result to correct for grid sorting */
    /** also create a new result with one vellset */
    Result &res1=result_<<= new Result(1,child_res->isIntegrated());
    const Vells vl=res0->vellSet(0).getValue();
    Vells &in=const_cast<Vells &>(vl);
    //create new vellset
    int npsetsf=res0->vellSet(0).numPertSets();
    int nspidsf=res0->vellSet(0).numSpids();
    VellSet::Ref ref;
		//determine the correct spids and perturbations before creating 
		//the vellset. the priority is given to the axis child
		//so if either vsax0 or vsax1 has them, the vellset
		//will be created to match those values. Else, the vellset
		//will be created to math the spid/perturbations of the funklet
		int npsets, nspids;
		npsets=nspids=0;
		if ( have_perturbed_sets!=-1) {
			if (have_perturbed_sets==0 || have_perturbed_sets==1) {
				//copy from axis 1
			  npsets=ipert0;
			  nspids=ispid0;
			} else if (have_perturbed_sets==2) {
				//copy from axis 2
			  npsets=ipert1;
			  nspids=ispid1;
			}
		} else {
			//copy from funklet
			npsets=npsetsf;
			nspids=nspidsf;
		}
    VellSet &vs=ref <<=new VellSet(incells.shape(),nspids,npsets);
		if (npsetsf*nspidsf>0) {
     vs.copySpids(res0->vellSet(0));
     vs.copyPerturbations(res0->vellSet(0));
		} else if ( have_perturbed_sets!=-1) {
			if (have_perturbed_sets==0 || have_perturbed_sets==1) {
				//copy from axis 1
       vs.copySpids(vsax0);
       vs.copyPerturbations(vsax0);
			} else if (have_perturbed_sets==2) {
				//copy from axis 2
        vs.copySpids(vsax1);
        vs.copyPerturbations(vsax1);
			}
		}

    Vells &out=vs.setValue(new Vells(0.0,incells.shape()));
    //now fill in the values only defined at the original grid points
    //imagine the axes are (t,f,a,b): then for each (t,f) grid point
    //find points a0,b0 in a and b axes respectively. this value will
    //go to the new grid point (t,f)
    blitz::Array<double,2> A=out.as<double,2>()(blitz::Range::all(),blitz::Range::all());
    blitz::Array<double,4> B=in.getArray<double,4>();
    //reindexing arrays
	
    int intime=incells.ncells(Axis::TIME);
    int infreq=incells.ncells(Axis::FREQ);
#ifdef DEBUG
    cout<<"In "<<intime<<","<<infreq<<endl;
#endif
#ifdef DEBUG
    cout<<"InCells from funklet"<<endl;
    cout<<res0().cells().center(Axis::axis(comm_axes_[0]))<<endl;
    cout<<res0().cells().center(Axis::axis(comm_axes_[1]))<<endl;
#endif
    int itime, ifreq,iplane;
    mapiter=revmap.begin();
    while(mapiter!=revmap.end()) {
      std::vector<int> key=mapiter->first;
      int *value=mapiter->second;
      itime=key[0];
      ifreq=key[1];
      iplane=key[2];
      if (!iplane) { //copy only the 0-th plane that has the value, the others are perturbed values
      A(itime,ifreq)=B(itime,ifreq,value[0],value[1]);
			}

      mapiter++;
    }

    //handle degenerate axes here, if ntime or nfreq is less that the request shape copy the same value
    //three cases: | |    ------------------      _
    //             | |    ------------------     | |
    //             | |                            -
    if ((ntime<intime) || (nfreq<infreq)) {
      //we have degeneracy here
      if ((ntime==intime) && (infreq>nfreq)) {
	//degeneracy in frequency, copy values from freq 0
	for (int i=1; i<infreq; i++)
	  A(blitz::Range::all(),i)=A(blitz::Range::all(),0);
      } else if ((intime>ntime) && (infreq==nfreq)) {
	// degeneracy in time, copy values from time 0
	for (int i=1; i<intime; i++)
	  A(i,blitz::Range::all())=A(0,blitz::Range::all());
      } else {
	//degeneracy in both, copy values from t,f 0,0
	for (int i=1; i<intime; i++)
	  A(i,0)=A(0,0);
	for (int i=1; i<infreq; i++)
	  A(blitz::Range::all(),i)=A(blitz::Range::all(),0);
      }
    }

    // handle perturbed sets if any
    if (npsetsf*nspidsf >0) {
#ifdef DEBUG
      cout<<"Found "<<npsetsf*nspidsf<<" perturbed sets from the funklet child"<<endl;
#endif
      for (int ipset=0; ipset<npsetsf; ipset++) 
	for (int ipert=0; ipert<nspidsf; ipert++)  {
	  const Vells pvl=res0->vellSet(0).getPerturbedValue(ipert,ipset);
	  Vells &pin=const_cast<Vells &>(pvl);
	  Vells &pout=vs.setPerturbedValue(ipert,new Vells(0.0,incells.shape()),ipset);

	  blitz::Array<double,2> pA=pout.as<double,2>()(blitz::Range::all(),blitz::Range::all());
	  blitz::Array<double,4> pB=pin.getArray<double,4>();

	  mapiter=revmap.begin();
	  while(mapiter!=revmap.end()) {
	    std::vector<int> key=mapiter->first;
	    int *value=mapiter->second;
	    itime=key[0];
	    ifreq=key[1];
	    iplane=key[2];
    
	    pA(itime,ifreq)=pB(itime,ifreq,value[0],value[1]);
	    mapiter++;
	  }

	  //handle degenerate axes here, if ntime or nfreq is less that the request shape copy the same value
	  if ((ntime<intime) || (nfreq<infreq)) {
	    //we have degeneracy here
	    if ((ntime==intime) && (infreq>nfreq)) {
	      //degeneracy in frequency, copy values from freq 0
	      for (int i=1; i<infreq; i++)
		pA(blitz::Range::all(),i)=pA(blitz::Range::all(),0);
	    } else if ((intime>ntime) && (infreq==nfreq)) {
	      // degeneracy in time, copy values from time 0
	      for (int i=1; i<intime; i++)
		pA(i,blitz::Range::all())=pA(0,blitz::Range::all());
	    } else {
	      //degeneracy in both, copy values from t,f 0,0
	      for (int i=1; i<intime; i++)
		pA(i,0)=pA(0,0);
	      for (int i=1; i<infreq; i++)
		pA(blitz::Range::all(),i)=pA(blitz::Range::all(),0);
	    }
	  }



	}
    } else if ( have_perturbed_sets!=-1) { //we have perturbed sets in the grid
#ifdef DEBUG
      cout<<"Found "<<nplanes<<" perturbed sets from the grid child case:"<<have_perturbed_sets<<endl;
#endif
			int nnpert,nnspid;
			nnpert=nnspid=0;
				if (have_perturbed_sets==0 || have_perturbed_sets==1) {
				//copy from axis 1
				//
				nnpert=ipert0;
				nnspid=ispid0;
			} else if (have_perturbed_sets==2) {
				//copy from axis 2
				nnpert=ipert1;
				nnspid=ispid1;
			}
      for (int ipset=0; ipset<nnpert; ipset++) 
	         for (int ipert=0; ipert<nnspid; ipert++)  {
	          Vells &pout=vs.setPerturbedValue(ipert,new Vells(0.0,incells.shape()),ipset);
        	  blitz::Array<double,2> pA=pout.as<double,2>()(blitz::Range::all(),blitz::Range::all());
            blitz::Array<double,4> pB=in.getArray<double,4>();


	          int plane=ipset*nnspid+ipert+1;
			   for (int itime=0; itime<ntime; itime++) 
						for (int ifreq=0; ifreq<nfreq; ifreq++) {
              aa[0]=itime;
              aa[1]=ifreq;
              aa[2]=plane;
#ifdef DEBUG
							cout<<"looking for: ["<<aa[0]<<","<<aa[1]<<","<<aa[2]<<"]"<<endl;
#endif
              //try to get value
              if(revmap.find(aa)==revmap.end()) {
							//cannot find it, use the 0-th plane value
              aa[2]=0;
			        } 
	            int *bb=revmap[aa];
              if (bb)
	              pA(itime,ifreq)=pB(itime,ifreq,bb[0],bb[1]);
							}


	  //handle degenerate axes here, if ntime or nfreq is less that the request shape copy the same value
	  if ((ntime<intime) || (nfreq<infreq)) {
	    //we have degeneracy here
	    if ((ntime==intime) && (infreq>nfreq)) {
	      //degeneracy in frequency, copy values from freq 0
	      for (int i=1; i<infreq; i++)
		pA(blitz::Range::all(),i)=pA(blitz::Range::all(),0);
	    } else if ((intime>ntime) && (infreq==nfreq)) {
	      // degeneracy in time, copy values from time 0
	      for (int i=1; i<intime; i++)
		pA(i,blitz::Range::all())=pA(0,blitz::Range::all());
	    } else {
	      //degeneracy in both, copy values from t,f 0,0
	      for (int i=1; i<intime; i++)
		pA(i,0)=pA(0,0);
	      for (int i=1; i<infreq; i++)
		pA(blitz::Range::all(),i)=pA(blitz::Range::all(),0);
	    }
	  }
						}


		}
    res1.setVellSet(0,ref);
    res1.setCells(incells);


		/*cout<<"Spids=";
    for (int i=0; i<res1.vellSet(0).numSpids(); i++) {
				cout<<res1.vellSet(0).getSpid(i)<<",";
		}*/
		cout<<endl;

    //delete map
    mapiter=revmap.begin();
    while(mapiter!=revmap.end()) {
      delete [] mapiter->second;
      mapiter++;
    }

    for (int i=0; i<sarray0.extent(0);i++) {
      delete [] sarray0(i).id;
    }
    for (int i=0; i<sarray1.extent(0);i++) {
      delete [] sarray1(i).id;
    }

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

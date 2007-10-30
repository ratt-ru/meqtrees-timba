//# ParmDBInterface.cc: The methods for storing and retrieving parms from the DB
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

#include <MeqNodes/ParmDBInterface.h>
#include <MEQ/Axis.h>

#ifdef HAVE_PARMDB
using namespace LOFAR::ParmDB;

ParmDomain toParmDomain(const Meq::Domain &domain){
  Thread::Mutex::Lock lock(parmdbMutex());

  vector<double> start,end;
  for(int axisi = 0; axisi< Meq::Axis::MaxAxis;axisi++)
    {
      if(domain.isDefined(axisi))
	{
	  start.push_back(domain.start(axisi));
	  end.push_back(domain.end(axisi));

	 
	}
      else
	break;
    }
  return ParmDomain(start,end);





}

Meq::Domain fromParmDomain(const ParmDomain &domain){
  Thread::Mutex::Lock lock(parmdbMutex());
  vector<double> start,end;
  start= domain.getStart();
  end = domain.getEnd();
  Meq::Domain Mdomain(start[0],end[0],start[1],end[1]);
  for (int i =2 ; i < start.size();i++)
    {
      Mdomain.defineAxis (i,start[i],end[i]);
	
    }
  return Mdomain;
}

Meq::Funklet::Ref  ParmValue2Funklet(const ParmValue &pv){
  Thread::Mutex::Lock lock(parmdbMutex());

  Meq::Funklet::Ref funkletref;
  string type=pv.rep().itsType;
  const int axis[] = { Meq::Axis::TIME,Meq::Axis::FREQ };
  vector<double> cf=pv.rep().itsCoeff;
  const vector<int> shape=pv.rep().itsShape;
  const int nx=(shape.size() && shape[0]>0?shape[0]:1);
  const int ny=(shape.size()>1 && shape[1]>0?shape[1]:1);
  double data[nx*ny];
  for(int i=0;i<nx*ny;i++){
  //convert
    int j=ny*(i%nx);//rownr
    j+=i/nx;//collumn nr;
    data[j]=cf[i];
  }
  const LoMat_double theCoeff(data,LoShape(nx,ny)); 

  vector<double> offsets,scales,constants;
  offsets = pv.rep().itsOffset;
  scales = pv.rep().itsScale;
  constants = pv.rep().itsConstants;
  const int ndim = offsets.size();
  double offset[ndim];
  double scale[ndim];



  for(int i=0;i<ndim;i++)
    {
      offset[i]=offsets[i];
      scale[i]=scales[i];
    }

  // what about more dmensions?? working on it...



  if (type== "PolcLog" || type =="polclog"||type=="MeqPolcLog")
    funkletref<<=new Meq::PolcLog(theCoeff,axis,offset,scale,
				  pv.rep().itsPerturbation,pv.rep().itsWeight,
				  pv.rep().itsDBRowRef,constants);
  else if(type=="Polc"||type =="polc"||type=="MeqPolc")
    funkletref<<=new Meq::Polc(theCoeff,axis,offset,scale,
			       pv.rep().itsPerturbation,pv.rep().itsWeight,pv.rep().itsDBRowRef);
  else
    funkletref<<=new Meq::CompiledFunklet(theCoeff,Meq::defaultFunkletAxes,Meq::defaultFunkletOffset,Meq::defaultFunkletScale,
					  pv.rep().itsPerturbation,pv.rep().itsWeight,
					  pv.rep().itsDBRowRef,type);
  

  
  Meq::Domain domain = fromParmDomain(pv.rep().itsDomain);
  funkletref().setDomain(domain);
  return funkletref;
}

ParmValue Funklet2ParmValue(Meq::Funklet::Ref  funklet){
  Thread::Mutex::Lock lock(parmdbMutex());
  ParmValue pv;
  ParmValueRep &pval= pv.rep();
  string type;
  type=funklet->getFunction();
  pval.setType(type);
  double *data;


  const int N=funklet->getCoeffShape().size();
  if(N==2)//convert data, assuming at most 2 dimensions for the moment
    {
      data=new double[funklet->getNumParms()];
      blitz::Array<double,2> tmp(data,funklet->getCoeffShape(),blitz::neverDeleteData,blitz::ColumnMajorArray<2>());
      tmp=funklet->getCoeff2();
      }
  else
    data = static_cast<double*>(funklet->coeffWr().getDataPtr());
 


  pval.setCoeff (data, funklet->getCoeffShape());

  pval.setPerturbation (funklet->getPerturbation());
  // Set domain and default offset/scale.
  pval.setDomain (toParmDomain(funklet->domain()));

  const int ndim =  pval.itsDomain.getStart().size();

  vector<double> offset(ndim);
  vector<double> scale(ndim);

  for(int i=0;i<ndim;i++)
    {
      offset[i]=funklet->getOffset(i);
      scale[i]=funklet->getScale(i);
    }
  
  pval.itsOffset = offset;
  pval.itsScale = scale;

  vector<double> Constants = funklet->getConstants ();

  pval.itsConstants=Constants;

  //no errors defined yet, use constants for consistency
  pval.itsErrors=Constants;
  pval.itsWeight = funklet->getWeight();
  pval.itsDBRowRef = funklet->getDbId();
  if(funklet->getDbId()<0)//this funklet should get a new entry
    pv.setNewParm(); //if TabRef==-1 a new entry is stored
  else
    pval.itsDBTabRef =ParmDBRep::UseNormal ; //use normal table
  return pv;
}


#else
using namespace casa;
#endif

namespace Meq {

#ifdef HAVE_PARMDB
  void Parm::save()
  {
    Thread::Mutex::Lock lock(parmdbMutex());
    if( !parmtable_ )
      return;
    
    if( !its_funklet_.valid() ) 
      return;
    ParmValue pv;

    if(its_funklet_->objectType()==TpMeqComposedPolc){
      DMI::List *funklist = its_funklet_()[FFunkletList].as_wpo<DMI::List>();
      if(!funklist) return;
      int nr_funk=funklist->size();
      cdebug(2)<<"saving "<<nr_funk<<" funklets"<<endl;
      for (int ifunk=0;ifunk<nr_funk;ifunk++)
	{
	  Funklet::Ref partfunk = funklist->get(ifunk);
	  
	  pv = Funklet2ParmValue(partfunk);
	  parmtable_->putValue(name_,pv,ParmDBRep::UseNormal);
	  partfunk().setDbId(pv.rep().itsDBRowRef);
	  cdebug(4)<<" put in database "<<partfunk->getDbId()<<endl;
 	  funklist->replace(ifunk,partfunk);
	}
    }
    else
      {
	pv = Funklet2ParmValue(its_funklet_);
	parmtable_->putValue(name_,pv,ParmDBRep::UseNormal);
	its_funklet_().setDbId(pv.rep().itsDBRowRef);
      }

    //its_funklet might have changed, reset state
    wstate()[FFunklet].replace() = its_funklet_().getState();

  }
  

  void Parm::openTable(){
    Thread::Mutex::Lock lock(parmdbMutex());
    cdebug(2)<<"opening table: "<<parmtable_name_<<endl;
    //check if table exists, otherwise create.
    if(parmtable_)
      closeTable();
    parmtable_ =  new ParmDB(ParmDBMeta("aips",parmtable_name_));
  }
  
  void Parm::closeTable(){
    Thread::Mutex::Lock lock(parmdbMutex());
    if (parmtable_)
      delete parmtable_;
  }
  

  
  Funklet * Parm::getFunkletFromDB(Funklet::Ref &funkletref,const Domain &domain){
    Thread::Mutex::Lock lock(parmdbMutex());
    if( !parmtable_ )
      return 0;

    //reimplement different function for (non)solvable
    vector<Funklet::Ref> funklets;


    const ParmValueSet pvs = parmtable_->getValues(name_,toParmDomain(domain));
    std::vector<ParmValue> pvV=pvs.getValues();
    funklets.resize(pvV.size());
    int i=0;
    for(std::vector<ParmValue>::iterator pvIt=pvV.begin();pvIt!=pvV.end();pvIt++)
      funklets[i++]=ParmValue2Funklet(*pvIt);
    int n=funklets.size();
	
    cdebug(3)<<n<<" funklets found in MEP table"<<endl;
    if( n>1 )
      {
	cdebug(3)<<"discarding multiple funklets as only one is currently suported, unless ? "<<(!isSolvable()||tiled_)<< "= true "<<endl;
	if(!reset_funklet_ && (tiled_ || !isSolvable()) ){
	  funkletref <<=new ComposedPolc(funklets);
	  cdebug(3)<<"composed funklet found? "<<funkletref-> objectType()<<endl;
	  funkletref().setDomain(domain);
	  if(force_shape_)
	    funkletref().setCoeffShape(shape_);

	  return funkletref.dewr_p();
	}
	//	getBestFitting(funklets);//reorder list, such that best fitting is first,especially important if perfect fitis in the list, since we do not w
	//ant another entry in DB then.
	
      }
    if( n )
      {
	//get the one with best fitting domain....
	funkletref <<= funklets.front();
	    
	//reset dbid if funklet domain not matching 
	if(funkletref->domain().start(0)!=domain.start(0) || funkletref->domain().start(1)!=domain.start(1) ||
	   funkletref->domain().end(0)!=domain.end(0) || funkletref->domain().end(1)!=domain.end(1))
	  {
	    cdebug(3)<<" resetting dbid" <<funkletref->domain().start(0)<<" == "<<domain.start(0)<<endl;
	    cdebug(3)<<funkletref->domain().start(1)<<" == "<<domain.start(1)<<endl;
	    cdebug(3)<<funkletref->domain().end(1)<<" == "<<domain.end(1)<<endl;
	    cdebug(3)<<funkletref->domain().end(1)<<" == "<<domain.end(1)<<endl;
	    funkletref(). setDbId (-2);
	    funkletref().setDomain(domain);
	  }
	if(force_shape_)
	  funkletref().setCoeffShape(shape_);
	return funkletref.dewr_p();
      }
    cdebug(2)<<"no funklets found in parmtable"<<endl;
    return 0;
  }



  void Parm::getDefaultFromDB(Funklet::Ref &funkletref){
    Thread::Mutex::Lock lock(parmdbMutex());
  
    int n=0;
    cdebug(3)<<"looking for funklets in defaults subtable: "<<n<<endl;
  }






#else
  //the interface to the old parmtable

  void Parm::save()
  {

    parmtable_ = ParmTable::openTable(parmtable_name_);
    if( !parmtable_ )
      return;

    if( !its_funklet_.valid() ) 
      return;
    //parmtable_ = ParmTable::openTable(parmtable_name_);

    if(its_funklet_->objectType()==TpMeqComposedPolc){
      DMI::List *funklist = its_funklet_()[FFunkletList].as_wpo<DMI::List>();
      if(!funklist) return;
      int nr_funk=funklist->size();
      cdebug(2)<<"saving "<<nr_funk<<" funklets"<<endl;
      for (int ifunk=0;ifunk<nr_funk;ifunk++)
	{
	  Funklet::Ref partfunk = funklist->get(ifunk);
	  parmtable_->putCoeff1(name_,partfunk,false);
	  cdebug(4)<<" put in database "<<partfunk->getDbId()<<endl;
 	  funklist->replace(ifunk,partfunk);
	}
    }
    else
      parmtable_->putCoeff1(name_,its_funklet_,false);
  }

  void Parm::openTable(){
    cdebug(2)<<"opening table: "<<parmtable_name_<<endl;
    //check if table exists, otherwise create.
    //MMMM: change to new tableinterface??
    parmtable_ = ParmTable::openTable(parmtable_name_);
  }

  void Parm::closeTable(){
  }


  Funklet * Parm::getFunkletFromDB(Funklet::Ref &funkletref,const Domain &domain){
    parmtable_ = ParmTable::openTable(parmtable_name_);
    if( !parmtable_ )
      return 0;

    //reimplement different function for (non)solvable
    vector<Funklet::Ref> funklets;
    parmtable_ = ParmTable::openTable(parmtable_name_);
    int n = parmtable_->getFunklets(funklets,name_,domain);
	
    cdebug(3)<<n<<" funklets found in MEP table"<<endl;
    if( n>1 )
      {
	cdebug(3)<<"discarding multiple funklets as only one is currently suported, unless ? "<<(!isSolvable()||tiled_)<< "= true "<<endl;
	if(!reset_funklet_ && (tiled_ || !isSolvable()) )
	  {
	    funkletref <<=new ComposedPolc(funklets);
	    cdebug(3)<<"composed funklet found? "<<funkletref-> objectType()<<endl;
	    funkletref().setDomain(domain);
	    if(force_shape_)
	      funkletref().setCoeffShape(shape_);
	    
	    return funkletref.dewr_p();
	  }
	else
	  //Sort on domain time0,f0,time1,f1...
	  {
	    

	  }
      }
    if( n )
      {
	//get the one with best fitting domain....
	funkletref <<= funklets.front();
	    
	//reset dbid if funklet domain not matching 
	if(funkletref->domain().start(0)!=domain.start(0) || funkletref->domain().start(1)!=domain.start(1) ||
	   funkletref->domain().end(0)!=domain.end(0) || funkletref->domain().end(1)!=domain.end(1))
	  {
	    cdebug(3)<<" resetting dbid" <<funkletref->domain().start(0)<<" == "<<domain.start(0)<<endl;
	    cdebug(3)<<funkletref->domain().start(1)<<" == "<<domain.start(1)<<endl;
	    cdebug(3)<<funkletref->domain().end(1)<<" == "<<domain.end(1)<<endl;
	    cdebug(3)<<funkletref->domain().end(1)<<" == "<<domain.end(1)<<endl;
	    funkletref(). setDbId (-1);
	    funkletref().setDomain(domain);
	  }
	if(force_shape_)
	  funkletref().setCoeffShape(shape_);
	return funkletref.dewr_p();
      }
    cdebug(2)<<"no funklets found in parmtable"<<endl;
    return 0;
  }



  void Parm::getDefaultFromDB(Funklet::Ref &funkletref){
  
    parmtable_ = ParmTable::openTable(parmtable_name_);
    int n = parmtable_->getInitCoeff(funkletref,name_);
    cdebug(3)<<"looking for funklets in defaults subtable: "<<n<<endl;
  }

#endif






}//namespace Meq

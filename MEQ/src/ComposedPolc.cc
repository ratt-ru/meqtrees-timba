//# Includes
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

#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/Cells.h>
#include <MEQ/ComposedPolc.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {
  static DMI::Container::Register reg(TpMeqComposedPolc,true);


  ComposedPolc::ComposedPolc(vector<Funklet::Ref> & funklets,double pert,double weight,DbId id):Polc(*funklets.begin()),nr_funklets_(funklets.size())
  {
    //   cdebug(3)<<"creating composed polc"<<endl;
    (*this)[FClass]=objectType().toString();

    initFunklets(funklets);
  }


  ComposedPolc::ComposedPolc (const ComposedPolc &other,int flags,int depth) :
    Polc(other,flags,depth),nr_funklets_(other.nr_funklets_)
  {
    (*this)[FClass]=objectType().toString();
    for(int i=0;i<Axis::MaxAxis;i++)
      axisHasShape_[i]=other.axisHasShape_[i];
  }

  ComposedPolc::ComposedPolc (const DMI::Record &other,int flags,int depth) :
    Polc(other,flags,depth),nr_funklets_(0)
  {
    (*this)[FClass]=objectType().toString();

  }

  ComposedPolc::ComposedPolc (double pert,double weight,DbId id):
    Polc(pert,weight,id),nr_funklets_(0)
   {
    (*this)[FClass]=objectType().toString();

   }

void ComposedPolc::validateContent (bool recursive)
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields; setup shortcuts
  // to their contents
  try
  {
    // init polc fields
    if( recursive )
      Funklet::validateContent(true);
    // get polc coefficients
    else{
      Field * fld = Record::findField(FCoeff);
      if( fld ){
	pcoeff_ = &( fld->ref().ref_cast<DMI::NumArray>() );
	//coeff should be doubles:
	if ((*pcoeff_)->elementType()==Tpint ||(*pcoeff_)->elementType()==Tpfloat||(*pcoeff_)->elementType()==Tplong )
	{
	  //convert to double

	}
	FailWhen((*pcoeff_)->elementType()!=Tpdouble,"Meq::Polc: coeff array must be of type double");

	// check for sanity
	FailWhen((*pcoeff_)->rank()>MaxPolcRank,"Meq::Polc: coeff can have max. rank of 2");

      }
      else
	pcoeff_ = 0;
    }
    //init_funklets
    Field * fld = Record::findField(FFunkletList);
    FailWhen(!fld,"no funklet list in record of composedpolc");

    DMI::List * funklistp =   fld->ref().ref_cast<DMI::List>() ;
    int nr_funklets = nr_funklets_ = funklistp->size();
    vector<Funklet::Ref>  funklets;
    for(int funknr=0;funknr<nr_funklets;funknr++){
      //for( DMI::List::iterator funkIt = funklistp->begin();funkIt!=funklistp->end();funkIt++){
      ObjRef partfunk = funklistp->get(funknr);
      FailWhen(!partfunk.valid(),"this is not a valid ref");

      Funklet::Ref funkref;funkref <<= partfunk;
      FailWhen(!funkref.valid(),"this is not a valid funkref");
      funklets.push_back(funkref);
     }
    initFunklets(funklets);


  }
  catch( std::exception &err )
  {
    ThrowMore(err,"validate of Polc record failed");
  }
  catch( ... )
  {
    Throw("validate of Polc record failed with unknown exception");
  }
}


  void ComposedPolc::initFunklets(vector<Funklet::Ref> & funklets)
  {
    Thread::Mutex::Lock lock(mutex());

    cdebug(2)<<"init funklets "<<funklets.size()<<endl;
    for ( int axisi= 0; axisi<Axis::MaxAxis;axisi++   )
      axisHasShape_[axisi]=0;

    DMI::List::Ref funklist;
    funklist <<= new  DMI::List();

    std::sort(funklets.begin(),funklets.end(),compareDomain);
    Domain newdom;
    for(vector<Funklet::Ref>::iterator funkIt=funklets.begin();funkIt!=funklets.end();funkIt++)
      {
	FailWhen(!(*funkIt).valid(),"this is not a valid funkIt");
        const Funklet &funklet = *funkIt;
        cdebug(2)<<"adding funklet with c00 "<<funklet.getCoeff0();
	//check on shape
	const LoShape fshape= funklet.getCoeffShape ();
        for(int axisi= 0; axisi<Axis::MaxAxis;axisi++)
        {
	    if(axisHasShape_[axisi]) continue;

	    if(fshape.size()>axisi && fshape[axisi]>1 )
	      axisHasShape_[axisi] |= 1; 
              
	    //cehck if domain changes around this axis
	    if( newdom.isDefined(axisi) &&
                ( newdom.start(axisi) != funklet.domain().start(axisi) ||
	          newdom.end(axisi)   != funklet.domain().end(axisi)) )
	      axisHasShape_[axisi] |= 2;
	}
	newdom=newdom.envelope(funklet.domain());

	//add to DMI List to show up in tree

	funklist().addBack(*funkIt);


      }
    setDomain(newdom);
    (*this)[FFunkletList].replace() = funklist;
  }


  void ComposedPolc::do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const
  {


    //get funklets from list


    const Field * fld = Record::findField(FFunkletList);
    if(!fld ){
      cdebug(2)<<"no funklet list found in record"<<endl;
      return;
    }
    const DMI::List * funklistp =   fld->ref().ref_cast<DMI::List>() ;


    int nr_funklets = funklistp->size();
    int nr_parms = getNumParms();
    int nr_spids = getNrSpids();

    const int nr_axis=cells.rank();
    const Domain cell_dom = cells.domain();

    LoVec_double startgrid[nr_axis],endgrid[nr_axis],sizegrid[nr_axis],centergrid[nr_axis];
    for(int i=0;i<nr_axis;i++){
      startgrid[i].resize(cells.ncells(i));
      endgrid[i].resize(cells.ncells(i));
      centergrid[i].resize(cells.ncells(i));

      centergrid[i] = ( cells.center(i));

      startgrid[i]=cells.cellStart(i);
      endgrid[i]=cells.cellEnd(i);

    }


    //init vells with 0
    Vells::Shape res_shape;
    Axis::degenerateShape(res_shape,nr_axis);


    for(int iaxis=0;iaxis<nr_axis;iaxis++)
      if(axisHasShape_[iaxis])
	res_shape[iaxis]=cells.ncells(iaxis);
      else
    	res_shape[iaxis]=1;

    cdebug(3)<<"evalauating cells with res_Shape : "<<res_shape<<endl;
    double *value = vs.setValue(new Vells(double(0),res_shape,true)).realStorage();

    double *pertValPtr[makePerturbed][nr_spids];
   // Create a vells for each perturbed value.
    // Keep a pointer to its storage
    if(makePerturbed)
      {
	for(int ipert=0;ipert<makePerturbed;ipert++)
	  for(int ispid=0;ispid<nr_spids;ispid++)
	      {
		pertValPtr[ipert][ispid] =
		vs.setPerturbedValue(ispid,new Vells(double(0),res_shape,true),ipert)
		.realStorage();

	      }
      }


    //loop over funklets
    int starti[8]={-1,-1,-1,-1,-1,-1,-1,-1};
    int endi[8]={-1,-1,-1,-1,-1,-1,-1,-1};

    for(int funknr=0;funknr<nr_funklets;funknr++){
      cdebug(3)<<"evalauating funklet : "<<funknr<<endl;

      const Funklet & partfunk = funklistp->as<Funklet>(funknr);

      //get cells for this domain
      int isConstant=1;

      //if funklet is constant, we dont have to do all the work, just fill the fitting vells
      double constpart=0;
      double constpert[2];
      if(partfunk.isConstant())
	{
	  constpart= partfunk.getCoeff0();
	  if(makePerturbed)
	    {
	      double d = partfunk.getPerturbation(0);
	      for(int ipert=0;ipert<makePerturbed;ipert++,d=-d )
		constpert[ipert]=constpart+d;
	    }
	}
      else isConstant=0;

      const Domain & polcdom(partfunk.domain());
      for(int axisi=0;axisi<nr_axis;axisi++){
	if (!cell_dom.isDefined(axisi)){
	  starti[axisi]=0;endi[axisi]=0;continue;
	}
	if (!polcdom.isDefined(axisi)){
	  starti[axisi]=0;endi[axisi]=std::min(res_shape[axisi]-1,startgrid[axisi].size()-1);continue;
	}
	int maxk=std::min(res_shape[axisi],startgrid[axisi].size());
	int k=0;
	while(k<maxk  && centergrid[axisi](k)<polcdom.start(axisi)) k++;
	starti[axisi] = k;
	k=std::min(res_shape[axisi]-1,startgrid[axisi].size()-1);
	while(k>0 && (centergrid[axisi](k)>polcdom.end(axisi))) k--;
	endi[axisi] = k;
	cdebug(3)<<"axis : "<<axisi<<" begin : "<<starti[axisi]<<" end : "<<endi[axisi]<<endl;
	if(endi[axisi]<starti[axisi]) break;
      }
      //      if(endi[0]<starti[0]) continue;/
      //     if(nr_axis>1 && (endi[1]<starti[1])) continue;



      VellSet partvs;
      if(!isConstant)
	{
	  partfunk.evaluate(partvs,cells,makePerturbed);
	  if(partvs.isNull ()) continue;
	}
      int maxnx=1;
      int maxny=1;
      if(!isConstant && partvs.hasShape()){
	maxnx =  partvs.shape()[0];
	maxny =  partvs.shape()[1];
	cdebug(3)<<"got partvs with shape "<< partvs.shape()<<endl;
      }


      //blitz::Array<double,2>  parts;
      const double *parts;
      //blitz::Array<double,2> perts[2][nr_spids] ;
      const double *perts[2][nr_spids];
      if(!isConstant)	// constant;
	{
	  const Vells & partvells = partvs.getValue();
	  if(partvells.isScalar())
	    {
	      constpart = partvells.getScalar<double>();
	      isConstant=1;//constant after all
	    }
	  else
	    {
// 	      parts.resize(partvells.shape());
// 	      parts= partvells.getConstArray<double,2>();
	      parts =partvells.getStorage<double>();
	    }

	  if(makePerturbed){
	    for(int ipert=0;ipert<makePerturbed;ipert++){
	      if(partvells.isScalar())
		{
		  constpert[ipert] = (partvs.getPerturbedValue(0,ipert)).getScalar<double>();
		}
	      else
		{

		  for(int ispid=0;ispid<nr_spids;ispid++){
// 		    perts[ipert][ispid].resize(partvs.getPerturbedValue(ispid,ipert).shape());
// 		    perts[ipert][ispid]=partvs.getPerturbedValue(ispid,ipert).getConstArray<double,2>();
		    perts[ipert][ispid] = partvs.getPerturbedValue(ispid,ipert).getStorage<double>();
		  }
		}

	    }//ipert loop

	  }//makeperturbed


	}//not constant


      //now fill result in array..
      //here we make assumptions about the rank of the array, generalize!!
      if(isConstant)
	{
	  int val[8];
	  fill_const_value(nr_axis,starti,endi,res_shape,val,0,value,constpart);
	  if( makePerturbed )
	    for( int ipert=0; ipert<makePerturbed; ipert++ )
	      fill_const_value(nr_axis,starti,endi,res_shape,val,0, pertValPtr[ipert][0],constpert[ipert]);
	}
      else
	{// not constant assume freq,time polc for now
	
      int nx(0),ny(0);


      for(int valx = starti[0];valx<=endi[0];valx++){
	ny=0;
	for(int valy = starti[1];valy<=endi[1];valy++){
	  int idx = valy + valx*res_shape[1];
	    {
	      cdebug(3)<<"nx "<<nx<<" ny "<<ny<<" val "<<ny+nx*maxny<<" "<<valx*res_shape[1]+valy<<endl;
	      cdebug(3)<<parts[ny+nx*maxny]<<endl;

	      value[idx] = parts[ny+nx*maxny] ;
	    }
	  ny=std::min(ny+1,maxny-1);//put check on y shape b4
	}
	nx=std::min(nx+1,maxnx-1);//put check on x shape b4
      }


      //fill perturbed values

      if( makePerturbed )
	{
	  for( int ipert=0; ipert<makePerturbed; ipert++ )
	    {
	      nx=ny=0;
	      for(int valx = starti[0];valx<=endi[0];valx++){
		ny=0;
		for(int valy = starti[1];valy<=endi[1];valy++){
		  int idx = valx*res_shape[1]+valy;
		  
		  for(int ispid=0;ispid<nr_spids;ispid++)
		    {
		      pertValPtr[ipert][ispid][idx] = (perts[ipert][ispid])[ny+nx*maxny] ;
		    }
		  
		  ny=std::min(ny+1,maxny-1);//put check on y shape b4
		}
		nx=std::min(nx+1,maxnx-1);//put check on x shape b4
	      }
	      


	    }//loop over perturbations
	}//if makeperturbed
	}//if not constant



    }//end loop over funklets
 
  }


 const  void ComposedPolc::fill_const_value(const int nr_axis,const int starti[],const int endi[],const Vells::Shape res_shape,int val[],int axisi,double *value,const double constpart) const {
       //recursive filling to allow for more than 2 axis, only for constant value for now
       if (axisi>=nr_axis){
	 //fill value
	 int idx = val[0];
	 int maxidx=res_shape[0];
	 for(int ai = 1;ai<nr_axis;ai++){
	   maxidx*=res_shape[ai];
	   idx*=res_shape[ai];
	   idx+=val[ai];
	 }
	 Assert(idx<maxidx);
	 value[idx] = constpart ;
       }
       else
	 {//loop over this axis
	   for (val[axisi]= starti[axisi];val[axisi]<=endi[axisi];val[axisi]++){
	     //recursive call
	     fill_const_value(nr_axis,starti,endi,res_shape,val,axisi+1,value,constpart);
	     
	     
	   }
	   



	 }
	
  }







  void ComposedPolc::do_update(const double values[],const std::vector<int> &spidIndex,bool force_positive)
  {
    Thread::Mutex::Lock lock(mutex());
    const Field * fld = Record::findField(FFunkletList);
    if(!fld ){
      cdebug(2)<<"no funklet list found in record"<<endl;
      return;
    }
    DMI::List & funklist =  (*this)[FFunkletList].as_wr<DMI::List>();

    int nrfunk=funklist.size();
    int nr_spids = spidIndex.size();
    int ifunk=0;
     for(int funknr=0 ; funknr<nrfunk ; funknr++)
      {


	Funklet::Ref partfunk = funklist.get(funknr);
	double* coeff = static_cast<double*>((partfunk)().coeffWr().getDataPtr());


	for( int i=0; i<nr_spids; i++ )
	  {
	    if( spidIndex[i] >= 0 )
	      {
		cdebug(3)<<"updateing polc "<< coeff[i]<<" adding "<< values[spidIndex[i]]<<spidIndex[i]<<endl;
		coeff[i] += values[spidIndex[i]*nrfunk+ifunk];
		if(force_positive && partfunk->isConstant())
		  coeff[i]=std::fabs(coeff[i]);
	      }
	  }

	funklist.replace(funknr,partfunk);
	ifunk++;


      }//loop over funklets


  }



  void ComposedPolc::do_update(const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints,bool force_positive)
  {
    Thread::Mutex::Lock lock(mutex());
    const Field * fld = Record::findField(FFunkletList);
    if(!fld ){
      cdebug(2)<<"no funklet list found in record"<<endl;
      return;
    }
    DMI::List & funklist =  (*this)[FFunkletList].as_wr<DMI::List>();

    int nrfunk=funklist.size();
    int nr_spids = spidIndex.size();
    int ifunk=0;
     for(int funknr=0 ; funknr<nrfunk ; funknr++)
      {


	Funklet::Ref partfunk = funklist.get(funknr);
	double* coeff = static_cast<double*>((partfunk)().coeffWr().getDataPtr());


	for( int i=0; i<nr_spids; i++ )
	  {
	    if( spidIndex[i] >= 0 )
	      {
		cdebug(3)<<"updateing polc "<< coeff[i]<<" adding "<< values[spidIndex[i]]<<spidIndex[i]<<endl;
		coeff[i] += values[spidIndex[i]*nrfunk+ifunk];

		//constrain constant funklets
		if(partfunk->isConstant()){
		  coeff[i] = std::min(coeff[i],constraints[1]);
		  coeff[i] = std::max(coeff[i],constraints[0]);

		}
		if(force_positive && partfunk->isConstant())
		  coeff[i]=std::fabs(coeff[i]);

	      }
	  }

	funklist.replace(funknr,partfunk);
	ifunk++;


      }//loop over funklets


  }

  void ComposedPolc::do_update(const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints_min,const std::vector<double> &constraints_max,bool force_positive)
  {
    Thread::Mutex::Lock lock(mutex());
    const Field * fld = Record::findField(FFunkletList);
    if(!fld ){
      cdebug(2)<<"no funklet list found in record"<<endl;
      return;
    }
    DMI::List & funklist =  (*this)[FFunkletList].as_wr<DMI::List>();

    int nrfunk=funklist.size();
    int nr_spids = spidIndex.size();
    int ifunk=0;
     for(int funknr=0 ; funknr<nrfunk ; funknr++)
      {


	Funklet::Ref partfunk = funklist.get(funknr);
	double* coeff = static_cast<double*>((partfunk)().coeffWr().getDataPtr());


	for( int i=0; i<nr_spids; i++ )
	  {
	    if( spidIndex[i] >= 0 )
	      {
		cdebug(3)<<"updateing polc "<< coeff[i]<<" adding "<< values[spidIndex[i]]<<spidIndex[i]<<endl;
		coeff[i] += values[spidIndex[i]*nrfunk+ifunk];


		if(i<int(constraints_max.size()))
		  coeff[i] = std::min(coeff[i],constraints_max[i]);
		if(i<int(constraints_min.size()))
		  coeff[i] = std::max(coeff[i],constraints_min[i]);
		if(force_positive && partfunk->isConstant())
		  coeff[i]=std::fabs(coeff[i]);

	      }
	  }

	funklist.replace(funknr,partfunk);
	ifunk++;


      }//loop over funklets


  }


  void ComposedPolc::changeSolveDomain(const Domain & solveDomain){
    Thread::Mutex::Lock lock(mutex());
    //transform cooeff of every Polc
    const Field * fld = Record::findField(FFunkletList);
    if(!fld ){
      cdebug(2)<<"no funklet list found in record"<<endl;
      return;
    }
    DMI::List & funklist =  (*this)[FFunkletList].as_wr<DMI::List>();

    int nrfunk=funklist.size();
    for(int funknr=0 ; funknr<nrfunk ; funknr++)
      {


	Funklet::Ref partfunk = funklist.get(funknr);

	partfunk().changeSolveDomain(solveDomain);

	funklist.replace(funknr,partfunk);

      }//loop over funklets
  };




  void ComposedPolc::changeSolveDomain(const std::vector<double> & solveDomain){
    Thread::Mutex::Lock lock(mutex());
    //transform cooeff of every Polc
    if(solveDomain.size()<2) return; //incorrect format
    const Field * fld = Record::findField(FFunkletList);
    if(!fld ){
      cdebug(2)<<"no funklet list found in record"<<endl;
      return;
    }
    DMI::List & funklist =  (*this)[FFunkletList].as_wr<DMI::List>();

    int nrfunk=funklist.size();
    for(int funknr=0 ; funknr<nrfunk ; funknr++)
      {


	Funklet::Ref partfunk = funklist.get(funknr);

	partfunk().changeSolveDomain(solveDomain);

	funklist.replace(funknr,partfunk);

      }//loop over funklets
  };



  void ComposedPolc::setCoeffShape(const LoShape & shape){
    Thread::Mutex::Lock lock(mutex());
    //transform cooeff of every Polc
    const Field * fld = Record::findField(FFunkletList);
    if(!fld ){
      cdebug(2)<<"no funklet list found in record"<<endl;
      return;
    }
    DMI::List & funklist =  (*this)[FFunkletList].as_wr<DMI::List>();

    int nrfunk=funklist.size();
    for(int funknr=0 ; funknr<nrfunk ; funknr++)
      {


	Funklet::Ref partfunk = funklist.get(funknr);

	partfunk().setCoeffShape(shape);

	funklist.replace(funknr,partfunk);

      }//loop over funklets
    //also set shape of own coeff, for spid recovery
    Funklet::Ref partfunk = funklist.get(0);
    setCoeff(partfunk->coeff());
    // and set axisHasShape_ flag
    for( uint i=0; i<shape.size(); i++ )
      if( shape[i] > 1 )
        axisHasShape_[i] |= 1;
      else
        axisHasShape_[i] &= ~1;
  };

}//namespace Meq





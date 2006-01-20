
//# Includes
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
    
    (*this)[AidClass].replace() = "MeqComposedPolc";
    initFunklets(funklets);
  }


  ComposedPolc::ComposedPolc (const ComposedPolc &other,int flags,int depth) : 
    Polc(other,flags,depth),nr_funklets_(other.nr_funklets_)
  {
    for(int i=0;i<Axis::MaxAxis;i++)
      axisHasShape_[i]=other.axisHasShape_[i];
    (*this)[AidClass].replace() = "MeqComposedPolc";
  }

  ComposedPolc::ComposedPolc (const DMI::Record &other,int flags,int depth) : 
    Polc(other,flags,depth),nr_funklets_(0)
  {

    (*this)[AidClass].replace() = "MeqComposedPolc";
  }
  
  ComposedPolc::ComposedPolc (double pert,double weight,DbId id):
    Polc(pert,weight,id),nr_funklets_(0)
   {
   
    (*this)[AidClass].replace() = "MeqComposedPolc";
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
    Domain::Ref domref;
    Domain & newdom = domref<<= new Domain();
    for(vector<Funklet::Ref>::iterator funkIt=funklets.begin();funkIt!=funklets.end();funkIt++)
      {
	//check on shape 
	const LoShape fshape= (*funkIt)->getCoeffShape ();
	  const int rank=(*funkIt)->rank();
	  for(uint axisi= 0; axisi<rank;axisi++){
	    if(axisHasShape_[axisi]) continue;

	    if(fshape[axisi]>1 ) { axisHasShape_[axisi]=1; continue;}
	    //cehck if domain changes around this axis
	    if(!newdom.isDefined (axisi)) continue;
	    if(newdom.start(axisi)!= (*funkIt)->domain().start(axisi) ||
	       newdom.end(axisi)!= (*funkIt)->domain().end(axisi))
	      { axisHasShape_[axisi]=1; continue;}
	}
	newdom=newdom.envelope((*funkIt)->domain());
	
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
    const DMI::List * funklistp =   fld->ref.ref_cast<DMI::List>() ;


    int nr_funklets = funklistp->size();
    int nr_parms = getNumParms(); 
    int nr_spids = getNrSpids(); 

    int nr_axis=cells.rank();//assume 2 for simplicity
    
    LoVec_double startgrid[2],endgrid[2],sizegrid[2],centergrid[2];
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
    Axis::degenerateShape(res_shape,cells.rank());


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
    int starti[2]={-1,-1};
    int endi[2]={-1,-1};

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

      blitz::Array<double,2>  parts;
      blitz::Array<double,2> perts[2][nr_spids] ;
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
	      parts.resize(partvells.shape());
	      parts= partvells.getConstArray<double,2>();
	  
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
		    perts[ipert][ispid].resize(partvs.getPerturbedValue(ispid,ipert).shape());
		    perts[ipert][ispid]=partvs.getPerturbedValue(ispid,ipert).getConstArray<double,2>();

		  }		  
		}
	      
	    }//ipert loop

	  }//makeperturbed


	}//not constant

  
      //now fill result in array..
      int nx(0),ny(0);
      for(int valx = starti[0];valx<=endi[0];valx++){
	ny=0;
	for(int valy = starti[1];valy<=endi[1];valy++){
	  if(isConstant)
	    value[valy + valx*res_shape[1]] = constpart ;
	  else
	    {
	      cdebug(3)<<"nx "<<nx<<" ny "<<ny<<" val "<<valx*res_shape[1]+valy<<endl;
	      cdebug(3)<<parts(nx,ny)<<endl;

	      value[valy + valx*res_shape[1]] = parts(nx,ny) ;
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
		  if(isConstant)
		    pertValPtr[ipert][0][valx*res_shape[1]+valy]= constpert[ipert] ;
		  else
		    {

		      for(int ispid=0;ispid<nr_spids;ispid++)
			{
			  pertValPtr[ipert][ispid][valx*res_shape[1]+valy] = perts[ipert][ispid](nx,ny) ;
			}
		    }
		  ny=std::min(ny+1,maxny-1);//put check on y shape b4 
		}
		nx=std::min(nx+1,maxnx-1);//put check on x shape b4 
	      }
	      


	    }//loop over perturbations
	}//if makeperturbed



    }//end loop over funklets

  }










  void ComposedPolc::do_update(const double values[],const std::vector<int> &spidIndex)
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

}//namespace Meq

      
   
     

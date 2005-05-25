
//# Includes
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/Cells.h>
#include <MEQ/ComposedPolc.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {    
  static DMI::Container::Register reg(TpMeqComposedPolc,true);


  ComposedPolc::ComposedPolc(vector<Funklet::Ref> funklets):Polc(),itsFunklets( funklets)
  {
    std::sort(itsFunklets.begin(),itsFunklets.end(),compareDomain);
    setDomain(0,0);
    Domain newdom;
    for(vector<Funklet::Ref>::iterator funkIt=itsFunklets.begin();funkIt!=itsFunklets.end();funkIt++)
      newdom=newdom.envelope((*funkIt)->domain());
    setDomain(newdom);
    setCoeff(0);
  }


  ComposedPolc::ComposedPolc (const ComposedPolc &other,int flags,int depth) : 
    Polc(other,flags,depth)
  {
      itsFunklets=vector<Funklet::Ref> ( other.itsFunklets);
    setCoeff(0);
  }
  
  ComposedPolc::ComposedPolc (double pert,double weight,DbId id):
    Polc(pert,weight,id),itsFunklets(0)
   {    setCoeff(0);
   }

  
  void ComposedPolc::setFunklets(vector<Funklet::Ref> funklets)
  {
    setDomain(0,0);
    itsFunklets=vector<Funklet::Ref> ( funklets);
    std::sort(itsFunklets.begin(),itsFunklets.end(),compareDomain);
    Domain newdom;
    for(vector<Funklet::Ref>::iterator funkIt=itsFunklets.begin();funkIt!=itsFunklets.end();funkIt++)
      newdom=newdom.envelope((*funkIt)->domain());
    setDomain(newdom);

  }


  void ComposedPolc::do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const
  {
    cdebug(4)<<"evaluating ComposedPolc"<<endl;
    if(itsFunklets.empty()) return;
    // init shape of result
    Vells::Shape res_shape;
    Vells::Shape part_shape;
    Axis::degenerateShape(res_shape,cells.rank());
    Axis::degenerateShape(part_shape,cells.rank());
    int varying_axis=-1;//only aloow one varying axis for the moment
    int partidx=0;
    int nr_notvarying=0;
    for(int iaxis=0;iaxis<cells.rank();iaxis++)
      part_shape[iaxis]=res_shape[iaxis]=cells.ncells(iaxis);
    
    // Create matrix for the main value and keep a pointer to its storage
    double* value ;
    vs.setValue(new Vells(double(0),res_shape,true));
   
    cout<<"value " << value<<endl;
    //DMI::NumArray &value;
    double lastend[2];
 
    Domain fulldomain(cells.domain());
    //create vector with endpoint of each cell 
    LoVec_double endgrid[2];
    for( int i=0; i<2; i++ )
      {
	int iaxis = i;
	if(cells.isDefined(iaxis)){
	  endgrid[i].resize(cells.ncells(iaxis));
	  endgrid[i] = cells.center(iaxis) + 0.5*cells.cellSize(iaxis);
	}
      }



    vector<Funklet::Ref> funklets(itsFunklets);
    for(vector<Funklet::Ref>::iterator funkIt=funklets.begin();funkIt!=funklets.end();funkIt++){
      
      int stopit=0;
            
      Domain partdom((*funkIt)->domain());
      if(funkIt!=funklets.begin()){
	for(int i=0;i<2;i++)
	  {
	    if(varying_axis<0) {if(partdom.end(i)>lastend[i]) {varying_axis=i; part_shape[i]=1;nr_notvarying=part_shape[abs(i-1)];}}
	    else
	      if(i!=varying_axis)
		{
		  if(partdom.end(i)<fulldomain.end(i) ||partdom.start(i)>fulldomain.start(i) )
		    {
		      cdebug(0)<<"couldnot fill complete domain from composed Polc, Polcs are changing in more than 1 axis"<<endl;
		      stopit=1;
		      break;
		    }
		}
	  }
	if(varying_axis>=0)
	  {

	    while(partdom.start(varying_axis)>=endgrid[varying_axis](partidx)) 
	      {
		partidx++;
		if(partidx >=res_shape[varying_axis]) return;
 		
		//break;
	      }
	 

	    if(partdom.end(varying_axis)<endgrid[varying_axis](partidx)) 
	      {
		cdebug(0)<<"some funklet from composed Polc does not fit, skipping"<<endl;
		continue;
	      }
	  }
      }
      
      if(stopit) break;
      lastend[0]=partdom.end(0);
      lastend[1]=partdom.end(1);
     
      //evaluate this funklet on its domain
      VellSet partvs;
      
      (*funkIt)->evaluate(partvs,cells,0);
      //make sure shape is correct
      //for the moment just check and define j and jpartidx accordingly
      

      //partvs.setShape(res_shape);
     
      int VellsisConstant=0;
      int partshape[2]={1,1};
      if(partvs.hasShape()){
	partshape[0] =  partvs.shape()[0];
	partshape[1] =  partvs.shape()[1];
      }
      
      if(partshape[0]<=1 && partshape[1]<=1)
	VellsisConstant=1;
      int j=0;
      int jpartidx=0;
      Vells partvells(partvs.getValue());
      blitz::Array<double,2> parts ;
      double constpart=0;
      if(VellsisConstant)	// constant;
	{
	  if(partvells.isScalar())
	    constpart = partvells.getScalar<double>();
	  else
	    constpart= partvells.getArray<double,2>()(0);
	}
      else 
	{
	  parts.resize(partvells.shape());
	  parts= partvells.getArray<double,2>();

	}
      if(varying_axis<0){
	//value = (partvs.getValue());
	Vells fullvells = vs.getValue();
	fullvells+= partvs.getValue();
	value = vs.setValue(fullvells).realStorage();
	


	//	  break;
	}
      else
	while(lastend[varying_axis]>=endgrid[varying_axis](partidx))
	  {
	    
	    if(! VellsisConstant){
	      if(partshape[varying_axis]==res_shape[varying_axis]) jpartidx=partidx;
	      else jpartidx=0;
	      for(int i= 0;i<nr_notvarying;i++)
		{
		  
		  if(partshape[abs(varying_axis-1)]== nr_notvarying) j=i;
		  else j=0;
		  if(varying_axis==0){
		    //		  value[partidx*nr_notvarying + i] =  partvs.getValue()[jpartidx][j];
		    value[partidx*nr_notvarying + i] = parts(jpartidx,j);
		  }
		  else
		    {
		      //		  value[i*res_shape[varying_axis]+partidx] =  partvs.getValue()[j][jpartidx];
		      value[i*res_shape[varying_axis]+partidx] =  parts(j,jpartidx);
		      
		    }
	      }
	    }
	    else //constant
	      for(int i= 0;i<nr_notvarying;i++) {
		if(varying_axis==0) value[partidx*nr_notvarying + i] = constpart;
		else value[i*res_shape[varying_axis]+partidx] = constpart;
	      }

	      
	    
	    partidx++;
	    if(partidx >=res_shape[varying_axis]) return;
	  }
      

      
    }//endloop over funklets
    
  }

}//namespace Meq

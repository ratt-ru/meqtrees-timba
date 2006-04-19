
//# Includes
#include <MEQ/PolcLog.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {    

  const HIID  FAxisList      = AidAxis|AidList;
  
  static DMI::Container::Register reg(TpMeqPolcLog,true);

  PolcLog::PolcLog()
  {
    (*this)[FClass]=objectType().toString();

    axis_vector_.resize(Axis::MaxAxis);
    axis_vector_[0]=axis_vector_[1]=1;

    for(int i=2;i<Axis::MaxAxis;i++)
      axis_vector_[i]=0;

  }

  PolcLog::PolcLog (const DMI::Record  &other,int flags,int depth): Polc(other,flags,depth){
    //    scale0=1.;
   (*this)[FClass]=objectType().toString();
    axis_vector_.resize(Axis::MaxAxis);
    axis_vector_[0]=axis_vector_[1]=1;

    for(int i=2;i<Axis::MaxAxis;i++)
      axis_vector_[i]=0;

    Field * fld = Record::findField(FAxisList);
    DMI::Record::Ref *axisArray = (fld) ? &(fld->ref.ref_cast<DMI::Record>()) : 0;
    if(axisArray){
      for(int i=0;i<Axis::MaxAxis;i++){
	axis_vector_[i]=0;
	(*axisArray)[Axis::axisId(i)].get(axis_vector_[i],0);

      }
    }
    else
      {
	DMI::Record axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
	axisArrayL[Axis::axisId(0)]=1;
	axisArrayL[Axis::axisId(1)]=1;
	(*this)[FAxisList]= axisArrayL;
      }
   }

  PolcLog::PolcLog (const PolcLog &other,int flags,int depth): Polc(other,flags,depth){
     (*this)[FClass]=objectType().toString();
    axis_vector_.resize(Axis::MaxAxis);
    axis_vector_[0]=axis_vector_[1]=1;

    for(int i=2;i<Axis::MaxAxis;i++)
      axis_vector_[i]=0;

    Field * fld = Record::findField(FAxisList);
    DMI::Record::Ref *axisArray = (fld) ? &(fld->ref.ref_cast<DMI::Record>()) : 0;
    if(axisArray){
      for(int i=0;i<Axis::MaxAxis;i++){
	axis_vector_[i]=0;
	(*axisArray)[Axis::axisId(i)].get(axis_vector_[i],0);
	
      }
    }
    else
      {
	DMI::Record axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
	axisArrayL[Axis::axisId(0)]=1;
	axisArrayL[Axis::axisId(1)]=1;
	(*this)[FAxisList]= axisArrayL;
      }
   }

  
  PolcLog::PolcLog(const LoVec_double &coeff,
	     int iaxis,double x0,double xsc,
		   double pert,double weight,DbId id,std::vector<double> scale_vector)
    : Polc(coeff,iaxis,x0,xsc,pert,weight,id),axis_vector_(scale_vector)
  {
    (*this)[FClass]=objectType().toString();
    int size = scale_vector.size()-1;
    if(size<0) return;
    DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
    for(int i=0;i<2;i++)
      axisArrayL[Axis::axisId(i)]=scale_vector[std::min(size,i)];
  }
  
  PolcLog::PolcLog(const LoMat_double &coeff,
           const int iaxis[],const double offset[],const double scale[],
	     double pert,double weight,DbId id,std::vector<double> scale_vector)
    : Polc(coeff,iaxis,offset,scale,pert,weight,id),axis_vector_(scale_vector)
  {
    (*this)[FClass]=objectType().toString();
    int size = scale_vector.size()-1;
    if(size<0) return;
    DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
    for(int i=0;i<2;i++)
      axisArrayL[Axis::axisId(i)]=scale_vector[std::min(size,i)];
  }
  
  PolcLog::PolcLog(DMI::NumArray *pcoeff,
	     const int iaxis[],const double offset[],const double scale[],
		   double pert,double weight,DbId id,std::vector<double> scale_vector)
    : Polc(pcoeff,iaxis,offset,scale,pert,weight,id),axis_vector_(scale_vector)
  {

    (*this)[FClass]=objectType().toString();
    int size = scale_vector.size()-1;
    if(size<0) return;
    DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
    for(int i=0;i<2;i++)
      axisArrayL[Axis::axisId(i)]=scale_vector[std::min(size,i)];
  }
    
  void PolcLog::validateContent (bool recursive){

    Field * fld = Record::findField(FAxisList);
    DMI::Record::Ref *axisArray = (fld) ? &(fld->ref.ref_cast<DMI::Record>()) : 0;
    if(axisArray){
       for(int i=0;i<Axis::MaxAxis;i++){
	axis_vector_[i]=0;
	(*axisArray)[Axis::axisId(i)].get(axis_vector_[i],0);
	
      }
    }
    else
      {
	DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
	axisArrayL[Axis::axisId(0)]=1;
	axisArrayL[Axis::axisId(1)]=1;
	(*this)[FAxisList]= axisArrayL;
      }
    if(recursive)
      Funklet::validateContent(recursive);
  }

  void PolcLog::axis_function(int axis, LoVec_double &grid) const
  {
    if(!fabs(axis_vector_[axis])) return;

    if(axis_vector_[axis]*grid(0) <=0 || axis_vector_[axis]*grid(grid.size()-1)<=0){
      cdebug(4)<<"trying to take log of 0 or negative value, axis not changed"<<endl;

      return;
    }
    grid=1./log(10.)*log(grid/axis_vector_[axis]);
    cdebug(4)<<grid<<endl;
   
  }

  void PolcLog::changeSolveDomain(const Domain & solveDomain){
    Thread::Mutex::Lock lock(mutex());
    if(!hasDomain()) return; //nothing to change
  
  
    const Domain &valDomain =  domain(); //validity domain
    
    if(fabs(axis_vector_[0])&&(axis_vector_[0]*valDomain.start(0)<=0||axis_vector_[0]*valDomain.end(0)<=0))//stop trying to take log of 0 or negative value!!, nothing
      {
	cdebug(2)<<"trying to take log of <=0 !! for axis "<<Axis::axisId(0)<<endl;
	Polc::changeSolveDomain(solveDomain);
	return;
      }
    if(fabs(axis_vector_[1])&&(axis_vector_[1]*valDomain.start(1)<=0||axis_vector_[1]*valDomain.end(1)<=0))//stop trying to take log of 0 or negative value!!, nothing
      {
	cdebug(2)<<"trying to take log of <=0 !! for axis "<<Axis::axisId(1)<<endl;
	Polc::changeSolveDomain(solveDomain);
	return;
      }
    
    
    std::vector<double> newoffsets(2);
    std::vector<double> newscales(2);
    for(int axisi=0;axisi<2;axisi++){
      if(fabs(axis_vector_[axisi])) {
	newoffsets[axisi] = solveDomain.start(axisi)*log(valDomain.end(axisi)/axis_vector_[axisi])-
	  solveDomain.end(axisi)*log(valDomain.start(axisi)/axis_vector_[axisi]);
	newoffsets[axisi] /= log(10.)*(solveDomain.start(axisi)-solveDomain.end(axisi));
	newscales[axisi] = log(valDomain.end(axisi)/axis_vector_[axisi]) - log(valDomain.start(axisi)/axis_vector_[axisi]);
	newscales[axisi] /= log(10.)*(solveDomain.end(axisi) - solveDomain.start(axisi));
      }
      else{
	newoffsets[axisi] = solveDomain.start(axisi)*valDomain.end(axisi)-
	  solveDomain.end(axisi)*valDomain.start(axisi);
	newoffsets[axisi] /= solveDomain.start(axisi)-solveDomain.end(axisi);
	newscales[axisi] = valDomain.end(axisi) - valDomain.start(axisi);
	newscales[axisi] /= solveDomain.end(axisi) - solveDomain.start(axisi);
	
      }
    
    }
    transformCoeff(newoffsets,newscales);      
    
   
  }


  void PolcLog::changeSolveDomain(const std::vector<double> & solveDomain){
    Thread::Mutex::Lock lock(mutex());
    if(!hasDomain()) return; //nothing to change
  
  
    const Domain &valDomain =  domain(); //validity domain
    
    if(fabs(axis_vector_[0])&&(axis_vector_[0]*valDomain.start(0)<=0||axis_vector_[0]*valDomain.end(0)<=0))//stop trying to take log of 0 or negative value!!, nothing
      {
	cdebug(2)<<"trying to take log of <=0 !! for axis "<<Axis::axisId(0)<<endl;
	Polc::changeSolveDomain(solveDomain);
	return;
      }
    if(fabs(axis_vector_[1])&&(axis_vector_[1]*valDomain.start(1)<=0||axis_vector_[1]*valDomain.end(1)<=0))//stop trying to take log of 0 or negative value!!, nothing
      {
	cdebug(2)<<"trying to take log of <=0 !! for axis "<<Axis::axisId(1)<<endl;
	Polc::changeSolveDomain(solveDomain);
	return;
      }
    
    
    std::vector<double> newoffsets(2);
    std::vector<double> newscales(2);
    for(int axisi=0;axisi<2;axisi++){
      if(fabs(axis_vector_[axisi])) {
	newoffsets[axisi] = solveDomain[0]*log(valDomain.end(axisi)/axis_vector_[axisi])-
	  solveDomain[1]*log(valDomain.start(axisi)/axis_vector_[axisi]);
	newoffsets[axisi] /= log(10.)*(solveDomain[0]-solveDomain[1]);
	newscales[axisi] = log(valDomain.end(axisi)/axis_vector_[axisi]) - log(valDomain.start(axisi)/axis_vector_[axisi]);
	newscales[axisi] /= log(10.)*(solveDomain[1] - solveDomain[0]);
      }
      else{
	newoffsets[axisi] = solveDomain[0]*valDomain.end(axisi)-
	  solveDomain[1]*valDomain.start(axisi);
	newoffsets[axisi] /= solveDomain[0]-solveDomain[1];
	newscales[axisi] = valDomain.end(axisi) - valDomain.start(axisi);
	newscales[axisi] /= solveDomain[1] - solveDomain[0];
      }
    
    }
    transformCoeff(newoffsets,newscales);      
  }

}//namespace MEQ


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

#include <MEQ/PolcLog.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {    

  
  static DMI::Container::Register reg(TpMeqPolcLog,true);

  PolcLog::PolcLog(double pert,double weight,DbId id):
   Polc(pert,weight,id)
  {
    (*this)[FClass].replace()=objectType().toString();

  }

PolcLog::PolcLog(double c00,double pert,double weight,DbId id,std::vector<double> scale_vector)
  : Polc(pert,weight,id)
{
  (*this)[FClass].replace()=objectType().toString();
     int size = scale_vector.size();
     if(size<0) return;
     DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
     for(int i=0;i<size;i++)
       axisArrayL[Axis::axisId(i)]=scale_vector[i];
     (*this)[FAxisList].replace() = axisArrayL;
}

  PolcLog::PolcLog (const DMI::Record  &other,int flags,int depth): Polc(other,flags,depth){
    (*this)[FClass].replace()=objectType().toString();
     validateContent(false); // not recursive
   }

  PolcLog::PolcLog (const PolcLog &other,int flags,int depth): Polc(other,flags,depth){
    (*this)[FClass].replace()=objectType().toString();
   }

  
  PolcLog::PolcLog(const LoVec_double &coeff,
	     int iaxis,double x0,double xsc,
		   double pert,double weight,DbId id,std::vector<double> scale_vector)
    : Polc(coeff,iaxis,x0,xsc,pert,weight,id)
  {
    (*this)[FClass].replace()=objectType().toString();
     int size = scale_vector.size();
     if(size<0) return;
     DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
     for(int i=0;i<size;i++)
       axisArrayL[Axis::axisId(i)]=scale_vector[i];
     (*this)[FAxisList].replace() = axisArrayL;
  }
  
  PolcLog::PolcLog(const LoMat_double &coeff,
           const int iaxis[],const double offset[],const double scale[],
	     double pert,double weight,DbId id,std::vector<double> scale_vector)
    : Polc(coeff,iaxis,offset,scale,pert,weight,id)
  {
    (*this)[FClass].replace()=objectType().toString();
     int size = scale_vector.size();
     if(size<0) return;
     DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
     for(int i=0;i<size;i++)
       axisArrayL[Axis::axisId(i)]=scale_vector[i];
     (*this)[FAxisList].replace() = axisArrayL;
//     int size = scale_vector.size()-1;
//     if(size<0) return;
//     DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
//     for(int i=0;i<2;i++)
//       axisArrayL[Axis::axisId(i)]=scale_vector[std::min(size,i)];
  }
  
  PolcLog::PolcLog(DMI::NumArray *pcoeff,
	     const int iaxis[],const double offset[],const double scale[],
		   double pert,double weight,DbId id,std::vector<double> scale_vector)
    : Polc(pcoeff,iaxis,offset,scale,pert,weight,id)
  {

     (*this)[FClass].replace()=objectType().toString();
     int size = scale_vector.size();
     if(size<0) return;
     DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
     for(int i=0;i<size;i++)
       axisArrayL[Axis::axisId(i)]=scale_vector[i];
     (*this)[FAxisList].replace() = axisArrayL;
  }
    
  void PolcLog::validateContent (bool recursive){

    (*this)[FClass].replace()=objectType().toString();
    Field * fld = Record::findField(FAxisList);
    DMI::Record::Ref *axisArray = (fld) ? &(fld->ref().ref_cast<DMI::Record>()) : 0;
    if(!axisArray){
      DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
      axisArrayL[Axis::axisId(0)]=1.;
      axisArrayL[Axis::axisId(1)]=1.;
      (*this)[FAxisList].replace()= axisArrayL;
    }
    if(recursive)
      Funklet::validateContent(recursive);
  }

  void PolcLog::axis_function(int axis, LoVec_double &grid) const
  {
    double  axis_scale;
    const Field * fld = Record::findField(FAxisList);
    const DMI::Record::Ref *axisArray = (fld) ? &(fld->ref().ref_cast<DMI::Record>()) : 0;
    if(axisArray){
      (*axisArray)[Axis::axisId(axis)].get(axis_scale,0.);
	
      
    }
    else
      {//set to default
	DMI::Record & axisArrayL =(*this)[FAxisList]<<= new DMI::Record();
	axisArrayL[Axis::axisId(0)]=1.;
	axisArrayL[Axis::axisId(1)]=1.;
	(*this)[FAxisList].replace()= axisArrayL;
      }
 
   if(!fabs(axis_scale)) return;

    if(axis_scale*grid(0) <=0 || axis_scale*grid(grid.size()-1)<=0){
      cdebug(4)<<"trying to take log of 0 or negative value, axis not changed"<<endl;

      return;
    }
    grid=1./log(10.)*log(grid/axis_scale);
    cdebug(4)<<grid<<endl;
   
  }

  void PolcLog::changeSolveDomain(const Domain & solveDomain){
    Thread::Mutex::Lock lock(mutex());
    if(!hasDomain()) return; //nothing to change
  
  
    const Domain &valDomain =  domain(); //validity domain
    std::vector<double> axis_vector_(2,1.); //contains scale L_0 for every axis, if 0 or not defined, no transformationis applied
    const Field * fld = Record::findField(FAxisList);
    const DMI::Record::Ref *axisArray = (fld) ? &(fld->ref().ref_cast<DMI::Record>()) : 0;
    if(axisArray){
        for(int i=0;i<2;i++){
	  axis_vector_[i]=0;
	  (*axisArray)[Axis::axisId(i)].get(axis_vector_[i],0.);
	  
	}
    }
    
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
    std::vector<double> axis_vector_(2,1.); //contains scale L_0 for every axis, if 0 or not defined, no transformationis applied
    const Field * fld = Record::findField(FAxisList);
    const DMI::Record::Ref *axisArray = (fld) ? &(fld->ref().ref_cast<DMI::Record>()) : 0;
    if(axisArray){
        for(int i=0;i<2;i++){
	  axis_vector_[i]=0;
	  (*axisArray)[Axis::axisId(i)].get(axis_vector_[i],0.);
	  
	}
    }
    
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
	//only transform linear axes
	/*
	newoffsets[axisi] = solveDomain[0]*log(valDomain.end(axisi)/axis_vector_[axisi])-
	  solveDomain[1]*log(valDomain.start(axisi)/axis_vector_[axisi]);
	newoffsets[axisi] /= log(10.)*(solveDomain[0]-solveDomain[1]);
	newscales[axisi] = log(valDomain.end(axisi)/axis_vector_[axisi]) - log(valDomain.start(axisi)/axis_vector_[axisi]);
	newscales[axisi] /= log(10.)*(solveDomain[1] - solveDomain[0]);
	*/
	newoffsets[axisi]  = 0.;
	newscales[axisi] = 1.;
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

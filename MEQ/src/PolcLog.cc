
//# Includes
#include <MEQ/PolcLog.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {    

  const HIID  FLScale      = AidL|AidScale;
  
  static DMI::Container::Register reg(TpMeqPolcLog,true);

  PolcLog::PolcLog()
  {
    scale0=1.;
    Field * fld = Record::findField(FLScale);
    DMI::NumArray::Ref *scaleArray = (fld) ? &(fld->ref.ref_cast<DMI::NumArray>()) : 0;
    if(scaleArray){
      if((*scaleArray)->elementType()==Tpdouble) scale0 = *((double *)(*scaleArray).deref().getConstDataPtr());
      if((*scaleArray)->elementType()==Tpint)scale0 = *((int *)(*scaleArray).deref().getConstDataPtr());
      if((*scaleArray)->elementType()==Tplong)scale0 = *((long *)(*scaleArray).deref().getConstDataPtr());
    }
    else
      (*this)[FLScale]=scale0;
  
  }


  PolcLog::PolcLog (const Polc &other,int flags=0,int depth=0): Polc(other,flags,depth){
    scale0=1.;
    Field * fld = Record::findField(FLScale);
    DMI::NumArray::Ref *scaleArray = (fld) ? &(fld->ref.ref_cast<DMI::NumArray>()) : 0;
    if(scaleArray){
      if((*scaleArray)->elementType()==Tpdouble) scale0 = *((double *)(*scaleArray).deref().getConstDataPtr());
      if((*scaleArray)->elementType()==Tpint)scale0 = *((int *)(*scaleArray).deref().getConstDataPtr());
      if((*scaleArray)->elementType()==Tplong)scale0 = *((long *)(*scaleArray).deref().getConstDataPtr());
    }
    else
      (*this)[FLScale]=scale0;
   }
  
  PolcLog::PolcLog(const LoVec_double &coeff,
	     int iaxis,double x0,double xsc,
	     double pert,double weight,DbId id,double lscale)
    : Polc(coeff,iaxis,x0,xsc,pert,weight,id)
  {
    scale0=lscale;
    //set state record
    LoVec_double sc(1);
    sc = scale0;
    ObjRef ref(new DMI::NumArray(sc));
    Record::addField(FLScale,ref,Record::PROTECT|DMI::REPLACE);
       
  }
  
  PolcLog::PolcLog(const LoMat_double &coeff,
           const int iaxis[],const double offset[],const double scale[],
	     double pert,double weight,DbId id,double lscale)
    : Polc(coeff,iaxis,offset,scale,pert,weight,id)
  {
    scale0=lscale;
    LoVec_double sc(1);
    sc = scale0;
    ObjRef ref(new DMI::NumArray(sc));
    Record::addField(FLScale,ref,Record::PROTECT|DMI::REPLACE);
         
  }
  
  PolcLog::PolcLog(DMI::NumArray *pcoeff,
	     const int iaxis[],const double offset[],const double scale[],
	     double pert,double weight,DbId id,double lscale)
    : Polc(pcoeff,iaxis,offset,scale,pert,weight,id)
  {
    scale0=lscale;
    LoVec_double sc(1);
    sc = scale0;
    ObjRef ref(new DMI::NumArray(sc));
    Record::addField(FLScale,ref,Record::PROTECT|DMI::REPLACE);
  }
    


  void PolcLog::axis_function(int axis, LoVec_double &grid) const
  {
    if(scale0*grid(0) <=0 || scale0*grid(grid.size()-1)<=0){
      cdebug(0)<<"trying to take log of 0 or negative value, axis not changed"<<endl;

      return;
    }
    grid=1./log(10.)*log(grid/scale0);
    cdebug(0)<<grid<<endl;
   
  }
}

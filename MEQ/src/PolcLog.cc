
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
  }
  
  void PolcLog::axis_function(int axis, LoVec_double &grid) const
  {
    cdebug(0)<<"changing grid "<<endl;
    if(scale0*grid(0) <=0 || scale0*grid(grid.size()-1)<=0){
      cdebug(0)<<"trying to take log of 0 or negative value, axis not changed"<<endl;

      return;
    }
    grid=1./log(10.)*log(grid/scale0);
 
   
  }
}


//# Includes
#include <MEQ/PolcLog.h>

namespace Meq {    
  static DMI::Container::Register reg(TpMeqPolcLog,true);


  void PolcLog::axis_function(int axis, LoVec_double &grid) const
  {
    cdebug(0)<<"changing grid "<<endl;
    if(grid(0) <=0 || grid(grid.size()-1)<=0){
      cdebug(0)<<"trying to take log of 0 or negative value, axis not changed"<<endl;

      return;
    }
    grid=1./log(10.)*log(grid);
 
   
  }
}


//# Includes
#include <MEQ/LogPolc.h>

namespace Meq {    
  static DMI::Container::Register reg(TpMeqLogPolc,true);


  void LogPolc::axis_function(int axis, LoVec_double &grid) const
  {
    cdebug(0)<<"changing grid "<<endl;
    grid=1./log(10.)*log(grid);
 
   
  }
}

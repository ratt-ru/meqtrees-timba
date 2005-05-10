
#ifndef MEQ_POLCLOG_H
#define MEQ_POLCLOG_H

//# Includes
#include <MEQ/Polc.h>

#pragma aidgroup Meq
#pragma type #Meq::PolcLog

// This class implements a PolcLog funklet --
// It takes the log of all axes 

namespace Meq 
{ 


  class PolcLog : public Polc
  {
    //reimplement axis function 
  public:
  typedef DMI::CountedRef<PolcLog> Ref;

  virtual DMI::TypeId objectType () const
  { return TpMeqPolcLog; }
  
  // implement standard clone method via copy constructor
    //##ModelId=400E53550131
  virtual DMI::CountedRefTarget* clone (int flags, int depth) const
  { return new PolcLog(*this,flags,depth); }
  

  //constructors
  PolcLog (){}
  PolcLog (const Polc &other,int flags=0,int depth=0): Polc(other,flags,depth){}
  ~PolcLog(){}
    
    virtual void axis_function(int axis, LoVec_double & grid) const ;  
  };
}
 // namespace Meq

#endif

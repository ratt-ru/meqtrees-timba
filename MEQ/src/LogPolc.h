
#ifndef MEQ_LOGPOLC_H
#define MEQ_LOGPOLC_H

//# Includes
#include <MEQ/Polc.h>

#pragma aidgroup Meq
#pragma type #Meq::LogPolc

// This class implements a LogPolc funklet --
// It takes the log of all axes 

namespace Meq 
{ 


  class LogPolc : public Polc
  {
    //reimplement axis function 
  public:
  typedef DMI::CountedRef<LogPolc> Ref;

  virtual DMI::TypeId objectType () const
  { return TpMeqLogPolc; }
  
  // implement standard clone method via copy constructor
    //##ModelId=400E53550131
  virtual DMI::CountedRefTarget* clone (int flags, int depth) const
  { return new LogPolc(*this,flags,depth); }
  

  //constructors
  LogPolc (){}
  LogPolc (const Polc &other,int flags=0,int depth=0): Polc(other,flags,depth){}
  ~LogPolc(){}
    
    virtual void axis_function(int axis, LoVec_double & grid) const ;  
  };
}
 // namespace Meq

#endif

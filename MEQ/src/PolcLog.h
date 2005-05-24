
#ifndef MEQ_POLCLOG_H
#define MEQ_POLCLOG_H
//# Includes
#include <MEQ/Polc.h>
#include <Common/lofar_vector.h>



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
  PolcLog ();
  PolcLog (const Polc &other,int flags,int depth);

  explicit PolcLog(const LoVec_double &coeff,
		   int iaxis=0,double x0=0,double xsc=1,
		   double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
		   DbId id=-1, double lscale=1.);

  explicit PolcLog(const LoMat_double &coeff,
		   const int    iaxis[]  = defaultPolcAxes,
		   const double offset[] = defaultPolcOffset,
		   const double scale[]  = defaultPolcScale,
		   double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
		   DbId id=-1, double lscale=1.);
  

  explicit  PolcLog(DMI::NumArray *pcoeff,
		    const int    iaxis[]  = defaultPolcAxes,
		    const double offset[] = defaultPolcOffset,
		    const double scale[]  = defaultPolcScale,
		    double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
		    DbId id=-1, double lscale=1.);
  ~PolcLog(){}
  
  virtual void axis_function(int axis, LoVec_double & grid) const ;  
  private:
    double scale0;//scale 
  };
}
 // namespace Meq

#endif


#ifndef MEQNODES_SPLINE_H
#define MEQNODES_SPLINE_H

//# Includes
#include <MEQ/Funklet.h>
#include <DMI/NumArray.h>

#pragma aidgroup Meq
#pragma type #Meq::Spline





namespace Meq { 

  const int    MaxSplineRank = Axis::MaxAxis;

  class Spline: public Funklet{ 

  public:
  typedef DMI::CountedRef<Spline> Ref;

  virtual DMI::TypeId objectType () const
  { return TpMeqSpline; }

  
  // implement standard clone method via copy constructor
    //##ModelId=400E53550131
  virtual DMI::CountedRefTarget* clone (int flags, int depth) const
  { return new Spline(*this,flags,depth); }
  

  //constructors
  explicit Spline (double pert=1e-06,double weight=1,DbId id=-1);
  explicit Spline(double c00,const  Domain &dom,int Npoints,
		  double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
		  DbId id=-1);
  
  explicit Spline(const LoVec_double &coeff,const Domain &dom,
                int iaxis=0,double x0=0,double xsc=1,
                double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
                DbId id=-1);
  
  explicit Spline(const LoMat_double &coeff,const Domain &dom,
                const int    iaxis[]  = defaultFunkletAxes,
                const double offset[] = defaultFunkletOffset,
                const double scale[]  = defaultFunkletScale,
                double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
                DbId id=-1);
  
  explicit Spline(DMI::NumArray *pcoeff,const Domain &dom,
                const int    iaxis[]  = defaultFunkletAxes,
                const double offset[] = defaultFunkletOffset,
                const double scale[]  = defaultFunkletScale,
                double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
                DbId id=-1);
  Spline (const Spline &other,int flags=0,int depth=0);
  Spline (const DMI::Record &other,int flags=0,int depth=0);
  virtual void validateContent (bool recursive);


  ~Spline(){
  }


  virtual void setCoeffShape(const LoShape & shape);
  protected:
  //------------------ implement protected Funklet interface ---------------------------------
  virtual void do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const;

  virtual void do_update (const double values[],const std::vector<int> &spidIndex,bool force_positive=false);
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double>& constraints,bool force_positive=false);
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints_min,const std::vector<double> &constraints_max,bool force_positive=false);

  
  private:
  int N[MaxSplineRank];//number of coeffs
  double dx[MaxSplineRank];//distance between 2 knots
  double x0[MaxSplineRank];//starting point
  void init();
  void create_spline(const Axis::Shape& res_shape,
		     const std::vector<double> &perts,
		     const std::vector<int>    &spidIndex,
		     int makePerturbed ,double A[],double B[],double C[],
		     double Ap[2][100][100],double Bp[2][100][100],double Cp[2][100][100]) const;
  double get_value(const double * x,const int ipert, const int perturb,const double pert, double A[],double B[],double C[],
		   double Ap[2][100][100],double Bp[2][100][100],double Cp[2][100][100]) const;
  

  };


}
 // namespace Meq

#endif

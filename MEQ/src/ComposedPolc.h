#ifndef MEQ_COMPOSEDPOLC_H
#define MEQ_COMPOSEDPOLC_H
//# Includes
#include <MEQ/Polc.h>
#include <Common/lofar_vector.h>

#pragma aidgroup Meq
#pragma type #Meq::ComposedPolc


//A Composed polc contains a list of polcs valid for subdomains of the domain of the composed polcs

namespace Meq 
{ 

  class ComposedPolc : public Polc
  {
    //reimplement axis function 
  public:
  typedef DMI::CountedRef<ComposedPolc> Ref;

  virtual DMI::TypeId objectType () const
  { return TpMeqComposedPolc; }
  // implement standard clone method via copy constructor
    //##ModelId=400E53550131
  virtual DMI::CountedRefTarget* clone (int flags, int depth) const
  { return new ComposedPolc(*this,flags,depth); }
  

  //constructors
  ComposedPolc (const ComposedPolc &other,int flags,int depth) ;
  
  ComposedPolc (double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,DbId id=-1);
      
  ComposedPolc (vector<Funklet::Ref>);
  ~ComposedPolc(){}

  void setFunklets(vector<Funklet::Ref> funklets);

  protected:
  //------------------ implement protected Funklet interface ---------------------------------
  virtual void do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const;
    
  private:
  vector<Funklet::Ref> itsFunklets;

  };

  
  //define  compare functions, for sorting

  static bool compareDomain(const Funklet::Ref f1, const Funklet::Ref f2)
  {
    //first sort on time
    if(f1->domain().start(0) != f2->domain().start(0)) return (f1->domain().start(0) < f2->domain().start(0));
    if(f1->domain().end(0) != f2->domain().end(0))  return (f1->domain().end(0) < f2->domain().end(0)) ;
    //then freq
    if(f1->domain().start(1) != f2->domain().start(1)) return (f1->domain().start(1) < f2->domain().start(1));
    if(f1->domain().end(1) != f2->domain().end(1))  return (f1->domain().end(1) < f2->domain().end(1)) ;
  
    //all the same...hmmm, let's return somtehing for the moment
    cdebug(0)<<"Composed Polc consists of funklets with equal domain!!"<<endl;
    return true;
  
  }


}
 // namespace Meq

#endif

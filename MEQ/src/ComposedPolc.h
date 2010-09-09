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

#ifndef MEQ_COMPOSEDPOLC_H
#define MEQ_COMPOSEDPOLC_H
//# Includes
#include <MEQ/Polc.h>
#include <DMI/List.h>
#include <TimBase/lofar_vector.h>

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
  ComposedPolc (const DMI::Record &other,int flags=0,int depth=0);

  ComposedPolc (double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,DbId id=-1);

  ComposedPolc (vector<Funklet::Ref> & funklets,double default_value=0,double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,DbId id=-1);
  ~ComposedPolc(){}
  virtual void validateContent (bool recursive);

  void initFunklets(vector<Funklet::Ref> & funklets);

  const DMI::List & funkletList () const
  { return Record::as<DMI::List>(FFunkletList); }

  DMI::List & funkletList ()
  { return Record::as<DMI::List>(FFunkletList); }

  int makeSolvable(int spidIndex)
  {
    Thread::Mutex::Lock lock(mutex());
    Polc::makeSolvable(spidIndex);
    DMI::List & funklist = funkletList();
    for( DMI::List::iterator iter = funklist.begin(); iter != funklist.end(); iter ++)
      iter->as<Funklet>().makeSolvable(spidIndex);
    return getNrSpids();
  }

  int makeSolvable(int spidIndex,const std::vector<bool> &mask)
  {
    Thread::Mutex::Lock lock(mutex());
    Funklet::makeSolvable(spidIndex,mask);
    DMI::List & funklist = funkletList();
    for( DMI::List::iterator iter = funklist.begin(); iter != funklist.end(); iter ++)
      iter->as<Funklet>().makeSolvable(spidIndex);
    //    (*this)[FFunkletList].replace()=funklist;
    return getNrSpids();
  }

  int nrFunklets()
  {
    return nr_funklets_;
  }

  virtual void changeSolveDomain(const Domain & solveDomain);
  virtual void changeSolveDomain(const std::vector<double> & solveDomain);
  virtual void setCoeffShape(const LoShape & shape);

  protected:
  //------------------ implement protected Funklet interface ---------------------------------


  virtual void do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const;

  virtual void do_update (const double values[],const std::vector<int> &spidIndex,bool force_positive=false);
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints,bool force_positive=false);
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints_min,const std::vector<double> &constraints_max,bool force_positive=false);

  private:
  double default_value_;
  int nr_funklets_;
  int axisHasShape_[Axis::MaxAxis];
  const void fill_const_value(const int nr_axis,const int starti[],const int endi[],const Vells::Shape res_shape,int val[],int axisi,double *value,const double constpart) const ;
  };



  //define  compare functions, for sorting

  static bool compareDomain(const Funklet::Ref & f1, const Funklet::Ref & f2)
  {
    if(f1 == f2) return 0;
    for (int ai=0;ai<Axis::MaxAxis;ai++){
      if (f1->domain().isDefined(ai) && f2->domain().isDefined(ai))
	{
	  if(fabs(f1->domain().start(ai)- f2->domain().start(ai))>1e-16) return (f1->domain().start(ai) < f2->domain().start(ai));



	}
    }
    //domains fully overlap now for sure
    for (int ai=0;ai<Axis::MaxAxis;ai++){
      if (f1->domain().isDefined(ai) && f2->domain().isDefined(ai)){
	//use the one with largest domain
	if(fabs(f1->domain().end(ai) - f2->domain().end(ai))>1e-16)  return (f1->domain().end(ai) < f2->domain().end(ai)) ;
      }
    }
    //all the same...hmmm, let's return somtehing for the moment
    return f1->ncoeff()<f2->ncoeff();

  }


}
 // namespace Meq

#endif

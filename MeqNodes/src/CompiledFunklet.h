
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

#ifndef MEQNODES_COMPILEDFUNKLET_H
#define MEQNODES_COMPILEDFUNKLET_H

//# Includes
//#include <MEQ/Funklet.h>
#include <MEQ/Polc.h>
#include <DMI/NumArray.h>

#include <scimath/Functionals/CompiledFunction.h>
#include <scimath/Mathematics/AutoDiff.h>
#include <casa/BasicSL/String.h>
#include <MEQ/Vells.h>

#include <MeqNodes/TID-MeqNodes.h>

#pragma aidgroup MeqNodes
#pragma type #Meq::CompiledFunklet





namespace Meq { 

class CompiledFunklet: public Funklet{

  public:
  typedef DMI::CountedRef<CompiledFunklet> Ref;

  virtual DMI::TypeId objectType () const
  { return TpMeqCompiledFunklet; }

  
  // implement standard clone method via copy constructor
    //##ModelId=400E53550131
  virtual DMI::CountedRefTarget* clone (int flags, int depth) const
  { return new CompiledFunklet(*this,flags,depth); }
  

  //constructors
  explicit CompiledFunklet (double pert=1e-06,double weight=1,DbId id=-1);
  CompiledFunklet (const CompiledFunklet &other,int flags=0,int depth=0);
  CompiledFunklet (const DMI::Record &other,int flags=0,int depth=0);

  explicit CompiledFunklet(const LoVec_double &coeff,
		    const int    iaxis[]  = defaultFunkletAxes,
		    const double offset[] = defaultFunkletOffset,
		    const double scale[]  = defaultFunkletScale,
		    double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
			   DbId id=-1,string fstr  = "p0") 
  {
    //   setCoeff(coeff);
    //set by hand since setcoeff calls init too early
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    itsFunction = new casa::CompiledFunction<casa::Double>();
    itsDerFunction = new casa::CompiledFunction<casa::AutoDiff<casa::Double> >();
    ObjRef ref(new DMI::NumArray(coeff));
    Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
    pcoeff_ = &( field.ref().ref_cast<DMI::NumArray>() );
    if(hasField(FFunction)){
      (*this)[FFunction].get(fstr,0);
    }
    setFunction(fstr);
    
    init(Ndim,iaxis,offset,scale,pert,weight,id);
    itsState<<=new Funklet(*this);
  }

  explicit CompiledFunklet(const LoMat_double &coeff,
		    const int    iaxis[]  = defaultFunkletAxes,
		    const double offset[] = defaultFunkletOffset,
		    const double scale[]  = defaultFunkletScale,
		    double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
		    DbId id=-1,string fstr  = "p0") 
  {
    //    setCoeff(coeff);
    //set by hand since setcoeff calls init before we know about Ndim
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    itsFunction = new casa::CompiledFunction<casa::Double>();
    itsDerFunction = new casa::CompiledFunction<casa::AutoDiff<casa::Double> >();
    ObjRef ref(new DMI::NumArray(coeff));
    Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
    pcoeff_ = &( field.ref().ref_cast<DMI::NumArray>() );
    if(hasField(FFunction)){
      (*this)[FFunction].get(fstr,0);
    }

    setFunction(fstr);
  
    init(Ndim,iaxis,offset,scale,pert,weight,id);
   
    itsState<<=new Funklet(*this);
  }
 

  explicit  CompiledFunklet(DMI::NumArray *pcoeff,
		     const int    iaxis[]  = defaultFunkletAxes,
		     const double offset[] = defaultFunkletOffset,
		     const double scale[]  = defaultFunkletScale,
		     double pert=defaultFunkletPerturbation,double weight=defaultFunkletWeight,
		     DbId id=-1,string fstr  = "p0") 
  {
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    itsFunction = new casa::CompiledFunction<casa::Double>();
    itsDerFunction = new casa::CompiledFunction<casa::AutoDiff<casa::Double> >();
    ObjRef ref(pcoeff);
    FailWhen(pcoeff->elementType() != Tpdouble,"can't create Meq::CompiledFunklet from this array: not double");
    FailWhen(pcoeff->rank()>maxFunkletRank(),"can't create Meq::CompiledFunklet from this array: rank too high");

    Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
    pcoeff_ = &( field.ref().ref_cast<DMI::NumArray>() );
    if(hasField(FFunction)){
      (*this)[FFunction].get(fstr,0);
    }

    setFunction(fstr);
    
    

    init(Ndim,iaxis,offset,scale,pert,weight,id);
    itsState<<=new Funklet(*this);
  }

  ~CompiledFunklet(){
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    delete itsFunction;
    delete itsDerFunction;
  }

  void setFunction(string funcstring){
    //check if this is a valid string
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    (*this)[FFunction] = funcstring;

    FailWhen(!itsFunction->setFunction(funcstring),std::string(itsFunction->errorMessage()));
    Npar = itsFunction->nparameters();
    Ndim = itsFunction->ndim();
    itsDerFunction->setFunction(funcstring);
    int dim=0;
    for(uint i=0;i<Ndim;i++) {
      depend_[i]=0;
      if(dependsOn(i))
	{
	  depend_[i]=1;
	  setAxis(i,dim++);
	}
    }
    realDim=dim;
    setParam();
  }

  //check if 'xi' occurs in function string
    int dependsOn(int i);

  void setParam(){
    //set paramters...if coeff doesnt match, take matching part and set rest to unsolvable/0  ?
    FailWhen(int(Npar) != getNumParms (),"nr. coeff not matching nr. of parameters in Compiled Function!!");
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
   
    const double* coeffData = static_cast<const double *>(coeff().getConstDataPtr());
    
    for(uint i=0;i< Npar;i++){
      //	  cdebug(0)<<"setting par "<<i<<" :"<<coeffData[i]<<endl;
      (*itsDerFunction)[i]=casa::AutoDiff<casa::Double>(coeffData[i],  Npar,i);
      (*itsFunction)[i]=coeffData[i];
    }
	
  }


  virtual string getFunction() const{
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    return string(itsFunction->getText());
  }




  protected:
  //------------------ implement protected Funklet interface ---------------------------------
  virtual void do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const;

  virtual void do_update (const double values[],const std::vector<int> &spidIndex,bool force_positive=false);
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints,bool force_positive=false){
    Funklet::do_update (values,spidIndex,constraints,force_positive);
  }
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints_min,const std::vector<double> &constraints_max,bool force_positive=false);
  
  private:

  //autodiff is only calculated if the parm is solvable
  casa::CompiledFunction<casa::AutoDiff<casa::Double> >  * itsDerFunction;
  //otherwise use this one, initialize both
  casa::CompiledFunction<casa::Double> * itsFunction;
  // casa::CompiledFunction<casa::Double> itsFunction;
  uint Npar,Ndim,realDim;
  uint depend_[Axis::MaxAxis];
  //recursive filling of the VellSet
  void fill_values(double *value, double * pertValPtr[],double *xval,const Vells::Shape & res_shape,const int dimN , const LoVec_double *grid,const std::vector<double> &perts, const std::vector<int> &spidIndex, const int makePerturbed,int & pos) const;


  Funklet::Ref itsState;

  };


}
 // namespace Meq

#endif

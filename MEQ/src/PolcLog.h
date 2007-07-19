
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

#ifndef MEQ_POLCLOG_H
#define MEQ_POLCLOG_H
//# Includes
#include <MEQ/Polc.h>
#include <MEQ/Axis.h>
#include <TimBase/lofar_vector.h>



#pragma aidgroup Meq
#pragma type #Meq::PolcLog

// This class implements a PolcLog funklet --
// It takes the log of all axes 

namespace Meq 
{ 
  const std::vector<double> defaultLogScale(1,1.);
  const HIID  FAxisList      = AidAxis|AidList;

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
  PolcLog (const PolcLog &other,int flags=0,int depth=0);
  PolcLog (const DMI::Record &other,int flags=0,int depth=0);

  explicit PolcLog (double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,DbId id=-1);

  explicit PolcLog(double c00,
		   double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
		   DbId id=-1,std::vector<double> scale_vector=defaultLogScale);
  explicit PolcLog(const LoVec_double &coeff,
		   int iaxis=0,double x0=0,double xsc=1,
		   double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
		   DbId id=-1,std::vector<double> scale_vector=defaultLogScale);

  explicit PolcLog(const LoMat_double &coeff,
		   const int    iaxis[]  = defaultPolcAxes,
		   const double offset[] = defaultPolcOffset,
		   const double scale[]  = defaultPolcScale,
		   double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
		   DbId id=-1,std::vector<double> scale_vector=defaultLogScale);
  

  explicit  PolcLog(DMI::NumArray *pcoeff,
		    const int    iaxis[]  = defaultPolcAxes,
		    const double offset[] = defaultPolcOffset,
		    const double scale[]  = defaultPolcScale,
		    double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
		    DbId id=-1,std::vector<double> scale_vector=defaultLogScale);
  ~PolcLog(){}
  
  virtual void axis_function(int axis, LoVec_double & grid) const ;  
  virtual void changeSolveDomain(const Domain & solveDomain);
  virtual void changeSolveDomain(const std::vector<double> & solveDomain);
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Funklet is made from a DMI::Record
  //i.e if an empty funklet is created from python and the fields are filled afterwards, initialization should be done inthis function
  virtual void validateContent (bool recursive);

  // returns scales of axis_function (overwritten by PolcLog)
  virtual vector<double> getConstants () const {
/*     double temp_scales[]={axis_vector_[0],axis_vector_[1]} ; */
/*     LoVec_double axis_scales(temp_scales, LoVecShape(2), */
/* 			     blitz::duplicateData); */
/*     return axis_scales; */
    
    std::vector<double> axis_vector_(2); //contains scale L_0 for every axis, if 0 or not defined, no transformationis applied
    const Field * fld = Record::findField(FAxisList);
    const DMI::Record::Ref *axisArray = (fld) ? &(fld->ref().ref_cast<DMI::Record>()) : 0;
    if(axisArray){
        for(int i=0;i<2;i++){
	  axis_vector_[i]=0;
	  (*axisArray)[Axis::axisId(i)].get(axis_vector_[i],0.);
	  
	}
    }
    return axis_vector_;
  }

  };
}
 // namespace Meq

#endif

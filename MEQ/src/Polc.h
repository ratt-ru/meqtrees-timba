//# Polc.h: Ordinary polynomial with coefficients valid for a given domain.
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$

#ifndef MEQ_POLC_H
#define MEQ_POLC_H

//# Includes
#include <MEQ/Funklet.h>
#include <DMI/NumArray.h>

#include <MEQ/TID-Meq.h>
#pragma aidgroup Meq
#pragma type #Meq::Polc

// This class implements a Polc funklet --
// an ordinary 1/2-dim polynomial with real coefficients.

namespace Meq 
{ 

const int    MaxPolcRank = 2;
const double defaultPolcPerturbation = defaultFunkletPerturbation;
const double defaultPolcWeight = defaultFunkletWeight;
extern const int    defaultPolcAxes[MaxPolcRank];
extern const double defaultPolcOffset[MaxPolcRank];
extern const double defaultPolcScale[MaxPolcRank];


//##ModelId=3F86886E01F6
class Polc : public Funklet
{
public:
  typedef DMI::CountedRef<Polc> Ref;

  //------------------ constructors -------------------------------------------------------
  explicit Polc (double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,DbId id=-1);
    
    //##ModelId=3F86886F0366
  explicit Polc(double c00,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(const LoVec_double &coeff,
                int iaxis=0,double x0=0,double xsc=1,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(const LoMat_double &coeff,
                const int    iaxis[]  = defaultPolcAxes,
                const double offset[] = defaultPolcOffset,
                const double scale[]  = defaultPolcScale,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  explicit Polc(DMI::NumArray *pcoeff,
                const int    iaxis[]  = defaultPolcAxes,
                const double offset[] = defaultPolcOffset,
                const double scale[]  = defaultPolcScale,
                double pert=defaultPolcPerturbation,double weight=defaultPolcWeight,
                DbId id=-1);
  
  //##ModelId=400E5354033A
  //## copy-constructor works for generic records and for funklets, see the Funklet 
  //## class for differences
  Polc (const DMI::Record &other,int flags=0,int depth=0);
  Polc (const Polc &other,int flags=0,int depth=0);
  
  
  //------------------ implement public Funklet interface ---------------------------------
  // returns the number of parameters describing this funklet
  /*  virtual int getNumParms () const
  { return ncoeff(); }
  */
  // returns max rank for funklets of this type
  virtual int maxFunkletRank () const
  { return MaxPolcRank; }
  
  // returns true if funklet has no dependence on domain (e.g.: a single {c00} polc)
  virtual bool isConstant () const 
  { return ncoeff()<=1; }
  
  //------------------ standard DMI-related methods ---------------------------------------
  virtual DMI::TypeId objectType () const
  { return TpMeqPolc; }
  
  // implement standard clone method via copy constructor
    //##ModelId=400E53550131
  virtual DMI::CountedRefTarget* clone (int flags, int depth) const
  { return new Polc(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Polc is made from a DMI::Record
  // (or when the underlying DMI::Record is privatized, etc.)
    //##ModelId=400E53550156
  virtual void validateContent (bool recursive);
  virtual void axis_function(int axis, LoVec_double & grid) const{}
  virtual void changeSolveDomain(const Domain & solveDomain);
  virtual void changeSolveDomain(const std::vector<double> & solveDomain);


  virtual int makeSolvable (int spidIndex);

  virtual void setCoeffShape(const LoShape & shape);


  virtual void setCoeff (double c00){
    Funklet::setCoeff(c00);
  }
  virtual void setCoeff (const LoVec_double & coeff);
  virtual void setCoeff (const LoMat_double & coeff);
  virtual void setCoeff (const DMI::NumArray & coeff);

protected:
  //------------------ implement protected Funklet interface ---------------------------------
  virtual void do_evaluate (VellSet &vs,const Cells &cells,
                            const std::vector<double> &perts,
                            const std::vector<int>    &spidIndex,
                            int makePerturbed) const;

  virtual void do_update (const double values[],const std::vector<int> &spidIndex,bool force_positive=false);
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double>& constraints,bool force_positive=false);
  virtual void do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints_min,const std::vector<double> &constraints_max,bool force_positive=false);

  //------------------ end of protected Funklet interface ------------------------------------
  virtual void transformCoeff(const std::vector<double> & newoffsets,const std::vector<double> & newscales);
    
private:
  static const int MaxNumPerts = 2;

  
};
  
} // namespace Meq

#endif

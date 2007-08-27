//# ShapeletVisTf.h: Calculates beam gasin of a ShapeletVisTf tracking a source at Ra, Dec
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
//# $Id: ShapeletVisTf.h 5175 2007-05-15 21:21:00Z twillis $


#ifndef MEQNODES_SHAPELETVISTF_H
#define MEQNODES_SHAPELETVISTF_H
    
#include <MEQ/TensorFunction.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::ShapeletVisTf
#pragma aid Filename Cutoff Modes


//defrec begin MeqShapeletVisTf
////  Changes the resolution of a parent's Request before passing it on to the
////  child. Returns child result as is. Expects exactly one child.
////field: children []
////  UV children, modes
////
////defrec end
//
namespace Meq {    

class ShapeletVisTf : public TensorFunction
{
public:
  ShapeletVisTf();

  virtual ~ShapeletVisTf();

  virtual TypeId objectType() const
    { return TpMeqShapeletVisTf; }

protected:
  // method required by TensorFunction
  // Returns cells of result.
  // This version just uses the time axis.
  virtual void computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request);

  // method required by TensorFunction
  // Returns shape of result.
  // Also check child results for consistency
  virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);
    
  // method required by TensorFunction
  // Evaluates ShapeletVisTf for a given set of children values
  virtual void evaluateTensors (std::vector<Vells> & out,   
       const std::vector<std::vector<const Vells *> > &args );

  // Used to test if we are initializing with an observatory name
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

private:
  string filename_;
  //
  //cutoff weak modes
  double cutoff_;

  // shapelet stuff: to be included separately in the future
  /* evaluate Hermite polynomial value using recursion
  */
  //double H_e(double x, int n);

  /* calculate the UV mode vectors (block version, needs at least 2 grid points)
  * in: u,v: arrays of the grid points in UV domain
  *      M: number of modes
  *      beta: scale factor
  *      n0: number of modes in each dimension
  * out:
  *      Av: array of mode vectors size Nu.Nv times n0.n0, in column major order
  *      cplx: array of integers, size n0*n0, if 1 this mode is imaginary, else real
 *
 */
 int calculate_uv_mode_vectors(double *u, int Nu, double *v, int Nv, double beta, int n0, double **Av, int **cplx);


/** calculate the UV mode vectors (scalar version, only 1 point)
 * in: u,v: arrays of the grid points in UV domain
 *      M: number of modes
 *      beta: scale factor
 *      n0: number of modes in each dimension
 * out:
 *      Av: array of mode vectors size Nu.Nv times n0.n0, in column major order
 *      cplx: array of integers, size n0*n0, if 1 this mode is imaginary, else real
 *
 */
 int calculate_uv_mode_vectors_scalar(double *u, int Nu, double *v, int Nv, double beta, int n0, double **Av, int **cplx);

};

} // namespace Meq

#endif

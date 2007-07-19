//# FFTBrick.h: Parameter with polynomial coefficients
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

#ifndef MEQNODES_FFTBRICK_H
#define MEQNODES_FFTBRICK_H

//# Includes
#include <MEQ/Node.h>
#include <images/Images/PagedImage.h>
//#include <MeqNodes/ReductionFunction.h>


#include <MeqNodes/TID-MeqNodes.h>
#include <MeqNodes/AID-MeqNodes.h>

#pragma aidgroup MeqNodes
#pragma types #Meq::FFTBrick

#pragma aid Axes In Out
#pragma aids UVppw

namespace Meq {

const HIID FAxesIn = AidAxes|AidIn;
const HIID FAxesOut = AidAxes|AidOut;


class FFTBrick: public Node
	       //class FFTBrick: public ReductionFunction
{
public:
  // The default constructor.
  // The object should be filled by the init method.
  FFTBrick();

  virtual ~FFTBrick();

  virtual TypeId objectType() const
  { return TpMeqFFTBrick; }

  // Get the requested result of the Node.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  
 protected:

  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

 private:
  
  // helper function to perform a single FFT.
  // returns four outputs: the FFT, plus higher-order interpolation planes
  void doFFT (Vells::Ref output_vells[4],const Vells &input_vells);
     
  // which 2 axes are treated as an input plane?
  std::vector<HIID> _in_axis_id;
  // which 2 axes are treated as the output plane?
  std::vector<HIID> _out_axis_id;

  double _uvppw;
  
  // axis numbers -- filled in by getResult()
  uint _inaxis0; 
  uint _inaxis1; 
  uint _outaxis0;
  uint _outaxis1;
  
  // thse are shared between getResult() and doFFT(), so declare them
  // without _ prefix to make code more readable
  // NB: for historical reasons, we'll use l,m to name variables referring to 
  // the input axes, and u,v when referring to the output axes. The real axes
  // in use are of course determined above.
  int nl,nm,nl1,nm1;
  int nu,nv,nu1,nv1;
   
};


} // namespace Meq

#endif

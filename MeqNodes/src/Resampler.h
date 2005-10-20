//# Resampler.h: resamples result resolutions
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
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

#ifndef MEQNODES_RESAMPLER_H
#define MEQNODES_RESAMPLER_H
    
#include <MEQ/Node.h>
#include <MEQ/AID-Meq.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Resampler 
#pragma aid Integrate Flag Density Factor Num Cells

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqResampler
//  Resamples the Vells in its child's Result to the Cells of the parent's
//  Request. Current version ignores cell centers, sizes, domains, etc.,
//  and goes for a simple integrate/expand by an integer factor.
//field: flag_mask -1
//  Flag mask applied to child's result. -1 for all flags, 0 to ignore 
//  flags. Flagged values are ignored during integration.
//field: flag_bit 0
//  Flag bit(s) used to indicate flagged integrated results. If 0, then 
//  flag_mask&input_flags is used.
//field: flag_density 0.5
//  Critical ratio of flagged/total pixels for integration. If this ratio
//  is exceeded, the integrated pixel is flagged.
//field: num_cells []
//  If this is given, changes the number of cells along each axis. Must be 
//  a vector of 2 values (time,freq) or a single value.
//defrec end

namespace Meq {    

//##ModelId=400E530400A3
class Resampler : public Node
{
public:
    //##ModelId=400E5355029C
  Resampler();

    //##ModelId=400E5355029D
  virtual ~Resampler();

  //##ModelId=400E5355029F
  virtual TypeId objectType() const
  { return TpMeqResampler; }
  
  

protected:
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
	
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

	virtual int pollChildren (std::vector<Result::Ref> &child_results,
	   Result::Ref &resref,const Request &req);


  
private:
  int flag_mask;
  
  int flag_bit; //which way to resample, (0): result, (1):request
  
  float flag_density;

  //number of cells of the resampling
  int nx_; //no. of cells in the first axis
	int ny_; //no. of cells in the second axis

  int do_resample_;//flag to remember if to actually resample

int 
bin_search(blitz::Array<double,1> xarr,double x,int i_start,int i_end);
template<typename T> T
bicubic_interpolate(int p,int q,blitz::Array<double,1> xax,blitz::Array<double,1> yax,double x,double y,blitz::Array<T,2> A);
template<typename T> T
bilinear_interpolate(int p,int q,blitz::Array<double,1> xax,blitz::Array<double,1> yax,double x,double y,blitz::Array<T,2> A);
template<typename T> int 
resample(blitz::Array<T,2> A,blitz::Array<double,1> xax,blitz::Array<double,1> yax,
			blitz::Array<T,2> B,blitz::Array<double,1> xaxs,blitz::Array<double,1> yaxs, 
			double xstart, double xend, double ystart, double yend);
template<typename T> void
bcubic_coeff(T *yy, T *dyy1, T *dyy2, T *dyy12, double d1, double d2, blitz::Array<T,2> c);
//1 D cubic spline interpolation
//ripped from numerical recipes
template<class T> void
spline(blitz::Array<double,1> x, blitz::Array<T,1> y, int n, blitz::Array<T,1> y2);
template<class T> void
splint(blitz::Array<double,1> xax,double xstart, double xend, blitz::Array<T,1> yax, int n, blitz::Array<double,1> xaxs, int ns, blitz::Array<T,1> y);


};


} // namespace Meq

#endif

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
#pragma aid Integrate Flag Density

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
  
private:
  int flag_mask;
  
  int flag_bit;
  
  float flag_density;

};


// put the code here
class ResampleMachine 
{
public:
   ResampleMachine(const Cells &in, const Cells &out);

   ~ResampleMachine();

	 bool isIdentical() const
	 { return identical_; }

	 void setFlagPolicy(int flag_mask, int flag_bit, float flag_density)
	 { flag_mask_= flag_mask; flag_bit_=flag_bit; flag_density_=flag_density; }

	 int apply(VellSet &out, const VellSet &in);

private:
	 int flag_mask_;
	 int flag_bit_;
	 float flag_density_;
	 bool identical_;

	 blitz::Array<int,1> xindex_,yindex_; //indices of the old cells
	 int nx_,ny_; // size of the resampled (new) cells
	 blitz::Array<blitz::TinyVector<double,2>,1> xweights_,yweights_;
	 blitz::Array<double,2> cell_weight_;

	 int  ResampleMachine::bin_search(blitz::Array<double,1> xarr,double x,int i_start,int i_end); 
  template<class T> int  
   ResampleMachine::do_resample(int xlow, int xhigh, int nxs, 
	      int ylow, int yhigh, int nys, 
				blitz::Array<T,2> A,  blitz::Array<T,2> B ); 
  template<class T> int  
   ResampleMachine::do_resample(int xlow, int xhigh, int nxs, 
	      int ylow, int yhigh, int nys, 
				blitz::Array<T,2> A,  blitz::Array<T,2> B,  
			  VellsFlagType *Fp, bool has_flags, blitz::Array<VellsFlagType,2> Aflag);

};

} // namespace Meq

#endif

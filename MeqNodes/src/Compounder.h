//# Compounder.h: modifies request resolutions
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

#ifndef MEQNODES_COMPOUNDER_H
#define MEQNODES_COMPOUNDER_H
    
#include <MEQ/Node.h>
#include <MEQ/Cells.h>
#include <MEQ/VellSet.h>
#include <MEQ/AID-Meq.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Compounder 
#pragma aid Mode Common Axes

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqCompounder
//  Child 0: defines the grid for interpolation
//  Child 1: defines the function for interpolation
//  This nodes interpolates the result returned by child 1 according
//  to the gride defined by child 0.
//
//field: mode
//  mode 1 (sequential): passes the original requser to child 0, recreates a requset for child 1 according to the result returned by child 0.
//  mode 2 (parallel): passes the same requset to both children
//field: common_axes []
//  a vector which gives the axes returned by the grid child that is given to the function. Axes names can be characters like 'L','M' etc
//defrec end

namespace Meq {   

// for the map less than comparison
struct compare_vec{
 bool operator()(const std::vector<int> v1, const std::vector<int> v2) const
 {
  return ((v1[0] < v2[0])
    ||( (v1[0] == v2[0]) && (v1[1] < v2[1]))
	  ||( (v1[0] == v2[0]) && (v1[1] == v2[1]) && (v1[2] < v2[2]))
	  ||( (v1[0] == v2[0]) && (v1[1] == v2[1]) && (v1[2] == v2[2]) && (v1[3] < v2[3])));
 }
};

// for the spid map less than comparison
struct compare_spid{
 bool operator()(const VellSet::SpidType v1, const VellSet::SpidType v2) const
 {
  return (v1 < v2);
 }
};

class Compounder : public Node
{
public:
  Compounder();

  virtual ~Compounder();

	virtual TypeId objectType() const
	{ return TpMeqCompounder; }


protected:
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  virtual int pollChildren (Result::Ref &resref,
                            std::vector<Result::Ref> &childres,
                            const Request &req);
    
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
private:

  
  std::vector<HIID> comm_axes_;
	int mode_;

  // symdeps generated by Compounder
  vector<HIID>    res_symdeps_;
  int             res_depmask_;
  vector<HIID>    seq_symdeps_;
  int             seq_depmask_;
  
  // if =0, res depmask is incremented
  // if !=0, res depmask is assigned with this index directly
  int   res_index_;

	//for caching result in pollChildren()
	Result::Ref result_;
	int result_code_;

	//array of arrays for storing axes returned from the grid
  std::vector<blitz::Array<double,1> > grid_;	

	//map to store grid values and perturbed values and their mapping
	//key=(time,freq,spid,perturbation), value=(axis1,axis2,...,axisn)
	//
	map<const std::vector<int>, int *, compare_vec> revmap_;
	//list to keep track of all allocated memory
	std::list<int *> maplist_;

	//map for merging spids
	//key: spid
	//value: array of integers, for ax1, ax2, ... funklet
	//if no spid : -1, else the number of that spid in each axis
	map<const VellSet::SpidType, int *, compare_spid> spidmap_;

	//build axes from the grid child result
	int build_axes_(Result::Ref &childres, int ntime, int nfreq);

	//apply the grid to the funklet, for the main value, put spid=0
	template<class T> int apply_grid_map_2d4d( blitz::Array<T,2> A, blitz::Array<T,4> B, int spid);
};


} // namespace Meq


#endif

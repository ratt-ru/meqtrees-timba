//# Axis.h: Defines axes information
//#
//# Copyright (C) 2002
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

#ifndef MEQ_AXIS_H
#define MEQ_AXIS_H


#include <Common/Lorrays.h>
#include <DMI/HIID.h>
#include <map>

// aids used as some standard Axis identifiers
#pragma aid Freq Time L M N X Y Z Lag

namespace Meq {

namespace Axis 
{
  // max number of supported axes
  const int MaxAxis = 8; 
  
  // shape type used to represent a hypercube
  typedef LoShape Shape;
  
// variables for standard axis definitions
  extern int FREQ;
  extern int TIME;
  
// mappings between names and numbers
  extern AtomicID _name_map[MaxAxis];
  extern std::map<AtomicID,int> _num_map;
  
// standard functions to access the mappings
  
  // get name of axis #n
  inline AtomicID name (int n)
  { return _name_map[n]; }

  // get ordinal number of named axis (-1 if no such axis)
  inline int number (AtomicID name)
  { std::map<AtomicID,int>::const_iterator f = _num_map.find(name);
    return f == _num_map.end() ? -1 : f->second; }
    
// functions to set up the mappings    
  void setAxisMap (const HIID &map);
  void setAxisMap (const AtomicID names[],int num);
  
// helper function: creates a degenrate shape of rank N
  inline void degenerateShape (Shape &shape,int rank)
  {
    shape.resize(rank);
    shape.assign(rank,1);
  }
  inline Shape degenerateShape (int rank)
  {
    Shape out;
    degenerateShape(out,rank);
    return out;
  }
  inline Shape vectorShape (int iaxis,int np)
  {
    Shape out;
    degenerateShape(out,iaxis+1);
    out[iaxis] = np;
    return out;
  }
  inline Shape matrixShape (int ix,int iy,int nx,int ny)
  {
    Shape out;
    degenerateShape(out,std::max(ix,iy)+1);
    out[ix] = nx;
    out[iy] = ny;
    return out;
  }
  inline Shape freqVector (int np)
  { return vectorShape(Axis::FREQ,np); }
  
  inline Shape timeVector (int np)
  { return vectorShape(Axis::TIME,np); }
  
  inline Shape freqTimeMatrix (int nf,int nt)
  { return matrixShape(Axis::FREQ,Axis::TIME,nf,nt); }
};

}


#endif

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

#include <TimBase/Lorrays.h>
#include <DMI/HIID.h>
#include <DMI/Vec.h>
#include <MEQ/Meq.h>

#include <map>

// aids used as some standard Axis identifiers
#pragma aid Freq Time L M N X Y Z U V W RA Dec Lag

namespace Meq 
{
using DMI::HIID;

namespace Axis 
{
  using namespace DebugMeq;
  
// max number of supported axes
  const int MaxAxis = 8; 
  
// internal mappings between names and numbers
  extern HIID _name_map[MaxAxis];
  extern std::map<HIID,int> _num_map;
  extern bool _default_mapping;
// mutex used to protect the axis map 
  extern Thread::Mutex _mutex;  
  
// shape type used to represent a hypercube
  typedef LoShape Shape;
  
// initialized default mapping. Should be called automatically from _init()
  extern void initDefaultMaps ();
  
// resets to default axis mapping
  extern void resetDefaultMap ();
  
// internal initialization functions (called only once)
  inline void _init ()
  {
    static bool done = false;
    Thread::Mutex::Lock lock(_mutex);
    if( !done )
    {
      done = true;
      resetDefaultMap();
    }
  }
  
  
//=========== standard functions to access the axis mappings

  // returns id of axis #n
  inline const HIID & axisId (int n)
  { _init(); return _name_map[n]; }

  // returns ordinal number of named axis. If no such axis, either throws an
  // exception, or returns -1 (nothrow=true)
  inline int axis (const HIID &id,bool nothrow=false)
  { 
    _init();
    // if name is "n", return that n directly
    if( id.size() == 1 )
    {
      int index = id[0].index();
      if( index >= 0 )
        return index;
    }
    // else look in map
    std::map<HIID,int>::const_iterator f = _num_map.find(id);
    if( f == _num_map.end() )
    {
      if( nothrow )
        return -1;
      else
        Throw("unknown axis: "+id.toString());
    }
    else
      return f->second; 
  }
  
  // ordinal numbers of standard axes. All others must be accessed
  // as Axis::axis("X"), etc.
  extern int FREQ;
  extern int TIME;
  
  // returns a Vec containing MaxAxis axis ids (HIIDs). For undefined
  // axes, this is simply their ordinal number, e.g. "3", "4", etc.
  DMI::Vec::Ref getAxisIds ();
  // alternate version to attach it to a ref
  void getAxisIds (ObjRef &ref);
  
  // returns a Vec containing MaxAxis axis Records. For each defined axis the
  // record contains, as a minimum, the field "Id" giving the axis id.  
  // Undefined axes are represented by empty records.
  DMI::Vec::Ref getAxisRecords ();
  // alternate version to attach it to a ref
  void getAxisRecords (ObjRef &ref);
  
    
//=========== functions to set up the axis mappings
  // Note that since the axis map is global state that affects different
  // data objects (domains, cells, vells, results, etc.), it may only be 
  // specified once. Subsequent attempts to change the map will result in
  // an exception. It's ok to re-specify the same mapping though, and it's
  // also ok to change the axis records, provided the axis ids remain
  // the same.
    
  // are we using a default mapping?
  inline bool isDefaultMap ()
  { _init(); return _default_mapping; }
  
  // allocate a new axis in the mapping, if not present. Nodes that use non-default 
  // axes should call this method in the constructor, this will allow them
  // to be used without setting an explicit axis map. 
  void addAxis (const HIID &name);
  
  // specifies non-default axis mapping as a vector of HIIDs 
  void setAxisMap (const std::vector<HIID> &map);
  
  // specifies non-default axis mapping as an array of HIIDs 
  void setAxisMap (const HIID names[],int num);
  
  // specifies non-default axis mapping as a DMI::Vec of HIIDs
  void setAxisMap (const DMI::Vec &map);
  
  // specifies non-default axis mapping as a Vec of axis records
  // Each record only needs to contain the field "Id".
  // Further info may be added in the future though.
  void setAxisRecords (const DMI::Vec &recvec);
  
  
//=========== helper functions to manipulate shapes

  // creates a degenerate shape of rank N
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
  
  // creates a "vector" shape of np points along axis iaxis
  inline Shape vectorShape (int iaxis,int np)
  {
    Shape out;
    degenerateShape(out,iaxis+1);
    out[iaxis] = np;
    return out;
  }
  
  inline Shape & addAxisToShape (LoShape &shape,int iaxis,int np)
  {
    if( shape.size() <= uint(iaxis) )
      shape.resize(iaxis+1,1);
    shape[iaxis] = np;
    return shape;
  }
  
  // "merges" one axis shape into the other. Returns true on success,
  // or false on failure (i.e. incompatible shapes)
  inline bool mergeShape (Shape &shp,const Shape &other)
  {
    if( shp.size() < other.size() )
      shp.resize(other.size(),1);
    for( uint i=0; i<other.size(); i++ )
      if( other[i] != 1 )
      {
        if( shp[i] == 1 )
          shp[i] = other[i];
        else if( shp[i] != other[i] ) 
          return false;
      }
    return true;
  }
  
  // creates a "matrix" shape of nx x ny points along axes ix,iy
  inline Shape matrixShape (int ix,int iy,int nx,int ny)
  {
    Shape out;
    degenerateShape(out,std::max(ix,iy)+1);
    out[ix] = nx;
    out[iy] = ny;
    return out;
  }
  
  // creates a "vector" shape along the frequency axis
  inline Shape freqVector (int np)
  { return vectorShape(Axis::FREQ,np); }
  
  // creates a "vector" shape along the time axis
  inline Shape timeVector (int np)
  { return vectorShape(Axis::TIME,np); }
  
  // creates a "matrix" shape along the time/freq axes
  inline Shape freqTimeMatrix (int nf,int nt)
  { return matrixShape(Axis::FREQ,Axis::TIME,nf,nt); }
};

}


#endif

//#  SymdepMap.h: map of symbolic dependencies
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$
#ifndef MEQ_SRC_SYMDEPMAP_H_HEADER_INCLUDED_C53FA569
#define MEQ_SRC_SYMDEPMAP_H_HEADER_INCLUDED_C53FA569


#include <DMI/Record.h>
#include <DMI/HIID.h>
#include <vector>
#include <map>

namespace Meq
{
using namespace DMI;  

 
class SymdepMap
{
  public:
    typedef std::vector<HIID> DepSet;  
    typedef std::map<HIID,int> DepMap;  
  
    SymdepMap ()
      : active_mask_(0)
    {}
    
    //## inits map from a record
    SymdepMap (const DMI::Record &rec)
      : active_mask_(0)
    { load(rec); }
    
    //## creates record from map
    DMI::Record::Ref toRecord () const;
    
    //## sets symdep, returns current active mask
    int set (const HIID &symdep,int mask);
    
    //## load map from a record, returns current active mask
    int load (const DMI::Record &rec);
    
    //## loads map from a DepMap, returns current active mask
    int load (const DepMap &map);
    
    //## copies map from another SymdepMap, returns current active mask
    int copyMap (const SymdepMap &other)
    { return load(other.map_); }
    
    //## returns current active mask
    int getActiveMask () const
    { return active_mask_; }
    
    //## returns mask for a given set of dependencies
    int getMask (const HIID deps[],int ndeps) const;
    
    int getMask (const HIID &dep) const
    { return getMask(&dep,1); }
    
    int getMask (const std::vector<HIID> &deps) const
    { return deps.empty() ? 0 : getMask(&deps.front(),deps.size()); }
    
    //## sets the set of active dependencies, and recomputes mask
    int setActive (const HIID deps[],int ndeps);
    
    int setActive (const HIID &dep)
    { return setActive(&dep,1); }
    
    int setActive (const std::vector<HIID> &deps)
    { return setActive(&deps.front(),deps.size()); }
    
    int setActive ()
    { active_set_.clear(); return active_mask_ = 0; }
    
    //## returns the active set
    const DepSet & getActive () const
    { return active_set_; }
    
      
  private:
    DepMap map_;
    
    DepSet active_set_;
    
    int active_mask_;
  
};  
  
  
  
  
};


#endif

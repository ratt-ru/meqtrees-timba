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

#include <DMI/Record.h>
#include <MEQ/AID-Meq.h>
#include <MEQ/Axis.h>
#include <MEQ/Meq.h>

namespace Meq {
  
using namespace DebugMeq;

namespace Axis {
  
int TIME = 0;
int FREQ = 1;

// mappings between names and numbers
HIID _name_map[MaxAxis];
std::map<HIID,int> _num_map;
bool _default_mapping = true;

Thread::Mutex _mutex;

// vector containing description records
static DMI::Vec::Ref axis_recs,axis_ids;

// Defines name of axis i 
// * if the name is just "i", does nothing 
// * if a name for the axis is already defined, it must be the same,
//   throws exception otherwise
// * else adds name for the axis
static void defineAxis (int i,const HIID &name0,bool addrec=true)
{
  Thread::Mutex::Lock lock(_mutex);
  _init();
  HIID name = name0;
  int name_index;
  // an empty name is equivalent to using the axis number
  if( name.empty() )
  {
    name = AtomicID(i);
    name_index = i;
  }
  // a name of "n" is also just the axis number
  else if( name.size() == 1 )
    name_index = name[0].index();
  // else a true name
  else
    name_index = -1;
  // if name is a number, check that it matches i, if so, do nothing,
  // else throw error (i.e. we can't name axis 1 to be "2")
  if( name_index >= 0 )
  {
    FailWhen(name_index != i,
             Debug::ssprintf("can't define axis %d as '%d'",i,name_index));
    return;
  }
// NB: allow axes to be overridden for now
//   // if axis is already has a name, check for match
//   if( _name_map[i] != AtomicID(i) )
//   { 
//     // unspecified axes have the name "i", so this name we can always override 
//     FailWhen(_name_map[i] != name,
//              Debug::ssprintf("can't define axis %d as '%s': already defined as '%s'",
//                 i,_name_map[i].toString().c_str(),name.toString().c_str()));
//     return;
//   }
  // now define the axis
  _name_map[i] = axis_ids[i] = name;
  _num_map[name] = i;
  if( name == HIID(AidFreq) )
    FREQ = i;
  else if( name == HIID(AidTime) )
    TIME = i;
  // init record for axis
  if( addrec )
  {
    DMI::Record & axrec = axis_recs[i].replace() <<= new DMI::Record;
    axrec[AidId] = name;
  }
  axis_ids[i] = name;
}

template<class Iter>
static void setAxisMap (Iter begin,Iter end)
{
  Thread::Mutex::Lock lock(_mutex);
  _init();
  int i=0;
  for( ; begin<end; i++,begin++ )
  {
    FailWhen(i >= MaxAxis,"too many axes in mapping");
    defineAxis(i,*begin);
  }
  // fill the rest with numbers
  for( ; i<MaxAxis; i++ )
  {
    defineAxis(i,AtomicID(i));
  }
  // mapping no longer default
  _default_mapping = false;
}

void setAxisMap (const DMI::Vec &map)
{
  Thread::Mutex::Lock lock(_mutex);
  _init();
  FailWhen(map.type() != TpDMIHIID,"axis map: expected HIIDs, got "+map.type().toString());
  FailWhen(map.size() > MaxAxis,"too many axes in mapping");
  for( int i=0; i<map.size(); i++ )
    defineAxis(i,map[i].as<HIID>());
  _default_mapping = false;
}

void setAxisMap (const std::vector<HIID> &map)
{
  setAxisMap(map.begin(),map.end());
}

void setAxisMap (const HIID names[],int num)
{
  setAxisMap(names,names+num);
}

DMI::Vec::Ref getAxisRecords ()
{
  Thread::Mutex::Lock lock(_mutex);
  _init();
  return axis_recs.copy();
}

DMI::Vec::Ref getAxisIds ()
{
  Thread::Mutex::Lock lock(_mutex);
  _init();
  return axis_ids.copy();
}

void getAxisRecords (ObjRef &ref)
{
  Thread::Mutex::Lock lock(_mutex);
  _init();
  ref = axis_recs;
}

void getAxisIds (ObjRef &ref)
{
  Thread::Mutex::Lock lock(_mutex);
  _init();
  ref = axis_ids;
}

void setAxisRecords (const DMI::Vec & vec)
{
  Thread::Mutex::Lock lock(_mutex);
  _init();
  FailWhen(vec.type() != TpDMIRecord,"expected vector of axis records");
  FailWhen(vec.size() > MaxAxis,"too many axis records specified");
  int i=0;
  for( ; i<vec.size(); i++ )
  {
    DMI::Record::Ref rec = vec[i].ref();
    HIID name = AtomicID(i);
    bool addrec = false;
    // get name
    rec()[AidId].get(name,true);
    // add to map
    defineAxis(i,name);
    // replace axis record 
    axis_recs[i].replace() <<= rec;
  }
  _default_mapping = false;
}

void addAxis (const HIID &name)
{
  Thread::Mutex::Lock lock(_mutex);
  _init();
  // return axis if found
  int n = axis(name,true);
  if( n >= 0 )
    return;
  // allocate new
  for( int i=0; i<MaxAxis; i++ )
    if( _name_map[i] == AtomicID(i) )
    {
      defineAxis(i,name);
      // mapping no longer default
      _default_mapping = false;
      return;
    }
  // out of axes
  Throw("too many axes defined");
}

// init default map of TIME/FREQ
void resetDefaultMap ()
{
  Thread::Mutex::Lock lock(_mutex);
  axis_recs <<= new DMI::Vec(TpDMIRecord,MaxAxis);
  axis_ids  <<= new DMI::Vec(TpDMIHIID,MaxAxis);
  
  // clear existing definitions
  _num_map.clear();
  for( int i=0; i<MaxAxis; i++ )
  {
    HIID axis = AtomicID(i);
    _name_map[i] = axis;
    axis_ids[i] = axis;
  }
  const HIID defmap[] = { AidTime,AidFreq };
  setAxisMap(defmap,sizeof(defmap)/sizeof(defmap[0]));
  // reset default_mapping flag again since it was cleared by setAxisMap()
  _default_mapping = true;
}

}}; // close both namespaces
  

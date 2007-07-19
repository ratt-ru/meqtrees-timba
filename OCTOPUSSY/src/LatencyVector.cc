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

#include "DMI/Packer.h"    
#include "LatencyVector.h"
#include "OctopussyDebugContext.h"
#include <unistd.h>
#include <math.h>
   
using namespace DebugOctopussy;
using namespace DMI;
    
// returns sum of all values
//##ModelId=3DB958F300F8
Timestamp Octopussy::LatencyVector::total () const
{ 
  Timestamp tot(0,0);
  for( CVEI iter = tms.begin(); iter != tms.end(); iter++ )
    tot += iter->first;
  return tot;
}

// adds two latency vectors together
//##ModelId=3DB958F300FA
Octopussy::LatencyVector & Octopussy::LatencyVector::operator += ( const LatencyVector & other )
{
  if( tms.size() )
  {
    FailWhen(other.tms.size() != tms.size(),
        "incompatible latency vectors [" +
        toString() + "] and [" + other.toString() + "]" );
    VEI iter = tms.begin();
    CVEI iter2 = other.tms.begin();
    for( ; iter2 != other.tms.end(); iter++,iter2++ )
    {
      FailWhen(iter->second != iter2->second,
        "incompatible latency vectors [" +
        toString() + "] and [" + other.toString() + "]" );
      iter->first += iter2->first;
    }
  }
  else // null vector -- simply copy other over
  {
    tms = other.tms;
  }
  return *this;
}
    
// divides latency vector by some value
//##ModelId=3DB958F3010D
Octopussy::LatencyVector & Octopussy::LatencyVector::operator /= ( double x )
{
  for( VEI iter = tms.begin(); iter != tms.end(); iter++ )
    iter->first /= x;
  return *this;
}

// converts latency vector to strings
//##ModelId=3DB958F30120
string Octopussy::LatencyVector::toString() const
{
  string out;
  for( CVEI iter = tms.begin(); iter != tms.end(); iter++ )
    out += iter->second + ":" + iter->first.toString(Timestamp::USEC) + " ";
  out += "(us)";
  return out;
}

namespace DMI
{
using Octopussy::LatencyVector;

// implement the Packer template for a LatencyVector::Entry
template <>
inline size_t Packer<LatencyVector::Entry>::pack (const LatencyVector::Entry& obj, void* block,size_t &nleft)
{
  FailWhen(nleft < sizeof(obj.first) + obj.second.length(),"block too small");
  nleft -= obj.second.length() + sizeof(obj.first);
  *static_cast<Timestamp*>(block) = obj.first;
  return sizeof(obj.first) + 
      obj.second.copy(static_cast<char*>(block)+sizeof(obj.first),string::npos);
}

template <>
inline void Packer<LatencyVector::Entry>::unpack (LatencyVector::Entry& obj, const void* block, size_t sz)
{
  FailWhen(sz < sizeof(obj.first),"block too small");
  obj.first = *static_cast<const Timestamp *>(block);
  sz -= sizeof(obj.first);
  obj.second.assign(static_cast<const char*>(block) + sizeof(obj.first),sz);
}

template <>
inline size_t Packer<LatencyVector::Entry>::packSize (const LatencyVector::Entry& obj)
{
  return sizeof(obj.first) + obj.second.length();
}
}

//##ModelId=3DB958F30122
size_t Octopussy::LatencyVector::pack (void *block,size_t &nleft) const
{
  Timestamp *bl = static_cast<Timestamp*>(block);
  *bl++ = tms0;
  nleft -= sizeof(tms0);
  return SeqPacker<vector<Entry> >::pack(tms,bl,nleft);
}

//##ModelId=3DB958F30148
void Octopussy::LatencyVector::unpack (const void *block,size_t sz)
{
  FailWhen(sz < sizeof(tms0),"block too small");
  const Timestamp *bl = static_cast<const Timestamp*>(block);
  tms0 = *bl++;
  SeqPacker<vector<Entry> >::unpack(tms,bl,sz-sizeof(tms0));
}

//##ModelId=3DB958F3016C
size_t Octopussy::LatencyVector::packSize () const
{
  return sizeof(tms0) + SeqPacker<vector<Entry> >::packSize(tms);
}


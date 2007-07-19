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

#include "EventFlag.h"

namespace AppAgent
{    

    
//##ModelId=3E43E49702A5
EventFlag::EventFlag ()
    : flagword(0),nsources(0),have_async(false)
{
}

//##ModelId=3E43E49702AE
EventFlag::EventFlag (const EventFlag& right)
    : SingularRefTarget()
{
  operator = (right);
}

//##ModelId=3E43E49702D4
EventFlag& EventFlag::operator= (const EventFlag& right)
{
  if( this != &right )
  {
    Thread::Mutex::Lock lock(cond);
    flagword = 0;
    nsources = right.nsources;
    have_async = right.have_async;
  }
  return *this;
}


//##ModelId=3E43EDCD037F
int EventFlag::addSource (bool is_async)
{
  FailWhen( nsources >= MAXSOURCES,"too many sinks registered");
  if( is_async )
    have_async = true;
  return nsources++;
}


//##ModelId=3E43E440007D
void EventFlag::raise (int snum)
{
  FailWhen(snum<0 || snum>=nsources,"illegal event source number");
  Thread::Mutex::Lock lock(cond);
  flagword |= (1<<snum);
  cond.broadcast();
}

//##ModelId=3E43EA3D0366
void EventFlag::clear (int snum)
{
  FailWhen(snum<0 || snum>=nsources,"illegal event source number");
  Thread::Mutex::Lock lock(cond);
  flagword &= ~(1<<snum);
}

bool EventFlag::wait (ulong mask,bool lock) const
{
  if( flagword&mask )
    return true;
  // if we don't have any async event sources, then return false
  // since then we would wait forever
  if( !have_async )
    return false;
  Thread::Mutex::Lock mlock;
  if( lock )
    mlock.lock(cond);
  while( !(flagword&mask) )
    cond.wait();
  return true;
}

};

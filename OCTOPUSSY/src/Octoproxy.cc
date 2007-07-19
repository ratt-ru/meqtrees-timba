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

#include "Octoproxy.h"
#include "OctoproxyWP.h"
#include "Dispatcher.h"
#include "OctopussyDebugContext.h"

using namespace DebugOctopussy;
    
namespace Octopussy
{

namespace Octoproxy 
{
  
Identity::Identity (AtomicID wpid)
{
  FailWhen(!Dispatcher::dispatcher,"OCTOPUSSY dispatcher not initialized");
  // instantiate proxy and attach to Dispatcher
  proxy <<= new ProxyWP(wpid);
  Dispatcher::dispatcher->attach(proxy);
}


//##ModelId=3E08ECB30275
Identity::Identity (const Identity& right)
    : proxy(right.proxy)
{
}

//##ModelId=3E08ECB302D7
Identity::~Identity ()
{
// detach proxy WP from Dispatcher
  FailWhen(!Dispatcher::dispatcher,"OCTOPUSSY dispatcher not initialized");
  Dispatcher::dispatcher->detach(proxy.dewr_p());
}

//##ModelId=3E08ECB30303
Identity & Identity::operator= (const Identity& right)
{
  if( this != & right )
  {
    proxy = right.proxy;
  }
  return *this;
}

void Identity::wait ()
{
  FailWhen( !wp().isRunning(),"OCTOPUSSY not started" );
#ifdef USE_THREADS
  Thread::Mutex::Lock lock(wp().queueCondition());
  wp().queueCondition().wait();
#endif
}

//##ModelId=3E09032400F1
bool Identity::receive(Message::Ref &mref,bool wait)
{
  FailWhen( !wp().isRunning(),"OCTOPUSSY not started" );
  mref.detach();
#ifdef USE_THREADS
  Thread::Mutex::Lock lock(wp().queueCondition());
  wp().queueCondition().wait();
#endif
  // bug, finish this
  return false;
}

} // namespace Octoproxy

};

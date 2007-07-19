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

#include <TimBase/Debug.h>
#include "Octopussy.h"
#include "Dispatcher.h"
#include "Gateways.h"
#include "LoggerWP.h"
#include "OctopussyDebugContext.h"

using namespace DebugOctopussy;
    
namespace Octopussy
{
  
Dispatcher *pdsp = 0;

Thread::ThrID thread = 0;
  
DMI::Record gatewayPeerList;

// attach external ref so that other refs are attached automatically as EXTERNAL
DMI::Record::Ref gatewayPeerListRef(gatewayPeerList,DMI::EXTERNAL);
        
bool isRunning ()
{
  return pdsp != 0;
}

Dispatcher &  init     (bool start_gateways,bool start_logger)
{
  FailWhen( pdsp,"OCTOPUSSY already initialized" );
  pdsp = new Dispatcher;
  if( start_logger )
    pdsp->attach(new LoggerWP(10,Message::LOCAL),DMI::ANON);
  if( start_gateways )
    initGateways(*pdsp);
  return *pdsp;
}

void          start    ()
{
  FailWhen( !pdsp,"OCTOPUSSY not initialized" );
  pdsp->start();
  
}

void          stop     ()
{
  FailWhen( !pdsp,"OCTOPUSSY not initialized" );
  pdsp->stop();
}

void          pollLoop ()
{
  FailWhen( !pdsp,"OCTOPUSSY not initialized" );
  pdsp->pollLoop();
}

void          destroy  ()
{
  FailWhen( !pdsp,"OCTOPUSSY not initialized" );
  delete pdsp;
  pdsp = 0;
}


Thread::ThrID  initThread (bool wait_for_start)
{
#ifndef USE_THREADS
  Throw("OCTOPUSSY was built w/o thread support");
#else
  if( !pdsp )
    init();
  return thread = pdsp->startThread(wait_for_start);
#endif
}

void           stopThread  ()
{
#ifndef USE_THREADS
  Throw("OCTOPUSSY was built w/o thread support");
#else
  stop();
#endif
}

Thread::ThrID  threadId    ()
{
  return thread;
}

Dispatcher &   dispatcher  ()
{
  return *pdsp;
}

};

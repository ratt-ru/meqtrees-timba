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

#include "ReflectorWP.h"

namespace Octopussy
{

ReflectorWP::ReflectorWP (AtomicID wpid)
 : WorkProcess(wpid)
{
}

ReflectorWP::~ReflectorWP()
{
}

void ReflectorWP::init ()
{
  WorkProcess::init();
  subscribe("Reflect.*");
}

//##ModelId=3C7E4AC70261
bool ReflectorWP::start ()
{
  WorkProcess::start();
  return false;
}

//##ModelId=3C7E49AC014C
int ReflectorWP::receive (Message::Ref& mref)
{
  // ignore messages from ourselves
  if( mref->from() == address() )
    return Message::ACCEPT;
  // print the message starting at debug level 2
  if( Debug(2) )
  {
    int level = getDebugContext().level() - 1;
    dprintf(2)("received: %s\n",mref->sdebug(level).c_str());
  }
  // prepend "Reflect" to the message ID
  mref().setId( AidReflect | mref->id() );
  // return to sender
  MsgAddress from = mref->from();
  send(mref,from);
  
  return Message::ACCEPT;
}

};

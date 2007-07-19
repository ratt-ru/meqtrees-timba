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

#ifndef OCTOPUSSY_OCTOPUSSY_H 
#define OCTOPUSSY_OCTOPUSSY_H 1

#define MAKE_LOFAR_SYMBOLS_GLOBAL 1

#include <TimBase/Thread.h>
    
namespace Octopussy
{
  class Dispatcher;    

//  using namespace LOFAR;
  
  Dispatcher &  init     (bool start_gateways=true,bool start_logger=false);
  void          start    ();
  void          pollLoop ();
  void          stop     ();
  void          destroy  ();
  
  
  Thread::ThrID  initThread  (bool wait_for_start=false);
  void           stopThread  ();
  
  Thread::ThrID  threadId    ();
  
  Dispatcher &   dispatcher  ();
  
  bool           isRunning ();

};
#endif

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

#ifndef OCTOPUSSY_Octoproxy_h
#define OCTOPUSSY_Octoproxy_h 1

#include <OCTOPUSSY/WPInterface.h>
#include <OCTOPUSSY/Message.h>
#include <OCTOPUSSY/WPInterface.h>

namespace Octopussy
{
using namespace DMI;

namespace Octoproxy 
{
// Initializes run-time environment: creates Dispatcher, creates & 
// attaches standard set of WPs (Gateways, etc.)
// Some applications may initialize their own environment, in which
// case this step may be skipped.
  void init ();
  
// starts the Octopussy poll loop in a separate thread
  void start ();
  
// stops Octopussy thread
  void stop ();
  
//##ModelId=3E08EBFD03B8
  class Identity
  {
    public:
      //##ModelId=3E08ECB30259
      //##Documentation
      //## creates a new identity in the OCTOPUSSY net, using myid as the WPid.
      //## Octoproxy::init() must be called first (or a Dispatcher instantiated
      //## som e other way) 
      //## Until Octoproxy::start() is called, the only two legal operations
      //## on an Identity are subscribe() and unsubscribe().
      Identity (AtomicID wpid);

      //##ModelId=3E08ECB30275
      Identity (const Identity& right);

      //##ModelId=3E08ECB302D7
      ~Identity ();

      //##ModelId=3E08ECB30303
      Identity & operator= (const Identity& right);
      
      //##ModelId=3E08FF11036A
      //##Documentation
      //## Returns a reference to the proxy WP
      WPInterface & wp ();
      
      //##Documentation
      //## Returns a reference to the proxy WP
      const WPInterface & wp () const;
      
      //##ModelId=3E08FF7C030D
      //##Documentation
      //## Waits for an event on the identity proxy (message received, etc.)
      void wait ();
      
      //##ModelId=3E09032400F1
      bool receive (Message::Ref &mref,bool wait=true);

      bool isRunning ();
      
    private:
    //##ModelId=3E08FF110299
      WPRef proxy;

  };
    
  //##ModelId=3E08FF11036A
  inline WPInterface & Identity::wp ()
  {
    return proxy.dewr();
  }
  
  inline const WPInterface & Identity::wp () const
  {
    return proxy.deref();
  }
  
  inline bool Identity::isRunning ()
  {
    return wp().isRunning();
  }
  
} // namespace Octoproxy

};

#endif

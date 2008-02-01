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

#ifndef OCTOPUSSY_GWServerWP_h
#define OCTOPUSSY_GWServerWP_h 1

#include <TimBase/Net/Socket.h>
#include <DMI/DMI.h>
#include <OCTOPUSSY/MTGatewayWP.h>
#include <OCTOPUSSY/GatewayWP.h>
#include <OCTOPUSSY/WorkProcess.h>

#pragma aid Gateway GWServerWP GWClientWP GatewayWP

namespace Octopussy
{

//##ModelId=3C8F942502BA

class GWServerWP : public WorkProcess
{
  public:
      //##ModelId=3C8F95710177
      GWServerWP (int port1 = -1);

      //##ModelId=3CC95151026E
      GWServerWP (const string &path = "", int port1 = -1);

    //##ModelId=3DB9367E019C
      ~GWServerWP();


      //##ModelId=3CC951680113
      virtual void init ();

      //##ModelId=3C90BE4A029B
      virtual bool start ();

      //##ModelId=3C90BE880037
      virtual void stop ();

      //##ModelId=3C90BE8E000E
      virtual int timeout (const HIID &);

      //##ModelId=3C95B4DC031C
      virtual int input (int , int );

      //##ModelId=3CC951890246
      virtual int receive (Message::Ref &mref);

    // Additional Public Declarations
    //##ModelId=3DB9367E033E
      void advertiseServer();
      
      // a process will typically have at most two GWServers up:
      // one on a tcp port, one on a unix socket. Their addresses are available here.
      
      // Returns the TCP port bound to a GWServerWP. 0 if no server listening.
      static int getGlobalPort ()
      { return gwserver_tcp_port; }
      
      // Returns the unix socket bound to a GWServerWP. "" if no server listening.
      static std::string getGlobalSocket ()
      { 
        Thread::Mutex::Lock lock(gwserver_unix_socket_mutex);
        return std::string(gwserver_unix_socket); 
      }
      
  protected:
    // Additional Protected Declarations
      // tries to open server socket
    //##ModelId=3DB9367E037A
      void tryOpen ();
  private:
    //##ModelId=3DB9367F000A
      GWServerWP(const GWServerWP &right);

    //##ModelId=3DB9367F0104
      GWServerWP & operator=(const GWServerWP &right);

  private:
      
    // Data Members for Class Attributes

      //##ModelId=3C90BE3503C7
      int port;

      //##ModelId=3CC951EA0214
      string hostname;

    // Data Members for Associations

      //##ModelId=3C92257101CE
      Socket *sock;

    // Additional Implementation Declarations
    //##ModelId=3DB9367E0051
      int type;  // Socket::TCP or Socket::UNIX
    //##ModelId=3DB9367E00D5
      Message::Ref advertisement;
    //##ModelId=3DB9367E0110
      int open_retries;

      // global tcp port/unix socket
      
      static int gwserver_tcp_port;
      static Thread::Mutex gwserver_unix_socket_mutex;
      static std::string gwserver_unix_socket;
      
      static void setGlobalSocket (const std::string &socket)
      { 
        Thread::Mutex::Lock lock(gwserver_unix_socket_mutex);
        gwserver_unix_socket = socket;
      }
      
      static void setGlobalPort   (int port)
      { gwserver_tcp_port = port; }

};

// Class GWServerWP 


};
#endif

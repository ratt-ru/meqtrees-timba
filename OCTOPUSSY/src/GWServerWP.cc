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

#include "Gateways.h"
#include "GWServerWP.h"

namespace Octopussy
{

// timeout value for a retry of bind, in seconds
const Timeval Timeout_Retry(10.0),
// re-advertise timeout, in seconds
      Timeout_Advertise(10.0);
// max retries
const int MaxOpenRetries = 10;

// using LOFAR::num2str;  // defined in <TimBase/Debug.h>
using Debug::ssprintf;

int GWServerWP::gwserver_tcp_port = 0;
Thread::Mutex GWServerWP::gwserver_unix_socket_mutex;
std::string GWServerWP::gwserver_unix_socket;

// Class GWServerWP 

GWServerWP::GWServerWP (int port1)
  : WorkProcess(AidGWServerWP),port(port1),sock(0),type(Socket::TCP)
{
  // get port from config if not specified explicitly
  if( port<=0 )
    config.get("gwport",port,4808);
  // get the local hostname
  char hname[1024];
  FailWhen(gethostname(hname,sizeof(hname))<0,"gethostname(): "+string(strerror(errno)));
  hostname = hname;
}

GWServerWP::GWServerWP (const string &path, int port1)
  : WorkProcess(AidGWServerWP),port(port1),sock(0),type(Socket::UNIX)
{
  // get path from config, if not specified explicitly
  hostname = path;
  if( !hostname.length() )
    config.get("gwpath",hostname,"=octopussy-%U");
  // check if port number is part of pathname --
  //    find last segment after ":", and check that it is all digits
  size_t pos0 = hostname.find_last_of(':');
  if( pos0 != string::npos )
  {
    size_t pos = pos0+1;
    for( ; pos < hostname.length(); pos++ )
      if( !isdigit(hostname[pos]) )
        break;
    if( pos >= hostname.length() )
    {
      port = atoi(hostname.substr(pos0+1).c_str());
      hostname = hostname.substr(0,pos0);
    }
  }
  // if hostname contains a "@U" string, replace with uid
  string uid = Debug::ssprintf("%d",(int)getuid());
  while( (pos0 = hostname.find_first_of("%U")) != string::npos )
    hostname = hostname.substr(0,pos0) + uid + hostname.substr(pos0+2);
  // get port from config if not specified
  if( port<=0 )
    config.get("gwport",port,4808);
}


GWServerWP::~GWServerWP()
{
  if( sock )
    delete sock;
}



void GWServerWP::init ()
{
  subscribe(MsgGWRemoteUp|AidWildcard,Message::GLOBAL);
  // add local server port as -1 to indicate no active server
  if( type == Socket::TCP )
  {
    int dum = -1;
    dsp()->localData(GWNetworkServer).get(dum,true);
  }
  else
  {
    string dum;    
    dsp()->localData(GWLocalServer).get(dum,true);
  }
}

bool GWServerWP::start ()
{
  WorkProcess::start();
  open_retries = 0;
  tryOpen();
  return false;
}

void GWServerWP::stop ()
{
  WorkProcess::stop();
  if( sock )
    delete sock;
  sock = 0;
}

int GWServerWP::timeout (const HIID &)
{
  if( !sock || !sock->ok() )
    tryOpen();
#if ADVERTISE_SERVERS
  else
    advertiseServer();
#endif
  return Message::ACCEPT;
}

int GWServerWP::input (int , int )
{
  // This is called when an incoming connection is requested
  // (since we only have one active input, we don't need no arguments)
  if( !sock ) // sanity check
    return Message::CANCEL;
  // do an accept on the socket
  Socket *newsock = sock->accept(0);
  if( newsock ) // success? Launch a Gateway WP to manage it
  {
    lprintf(1,"accepted new connection, launching gateway\n");
  	newsock->setBlocking(false);
#ifdef USE_THREADS
    attachWP(new MTGatewayWP(newsock),DMI::ANON);
#else
    attachWP(new GatewayWP(newsock),DMI::ANON);
#endif
    return Message::ACCEPT;
  }
  else if( sock->errcode() == Socket::INPROGRESS )
  {
    lprintf(2,"connection in progress, will retry later\n");
    return Message::ACCEPT;
  }
  else
  { 
    lprintf(1,"error: accept(): %s.\nClosing and retrying\n",sock->errstr().c_str());
    // just to be anal, close the socket and retry binding it
    if( type == Socket::TCP )
      dsp()->localData(GWNetworkServer)[0] = -1;
    else
      dsp()->localData(GWLocalServer)[0] = "";
    open_retries = 0;
    tryOpen();
    return Message::CANCEL;
  }
}

int GWServerWP::receive (Message::Ref &mref)
{
  if( mref->id().matches(MsgGWRemoteUp|AidWildcard) && sock && sock->ok() )
    advertiseServer();
  return Message::ACCEPT;
}

// Additional Declarations

void GWServerWP::advertiseServer ()
{
  if( !advertisement.valid() )
  {
    Message *msg = new Message( type == Socket::UNIX 
                                ? MsgGWServerOpenLocal
                                : MsgGWServerOpenNetwork );
    advertisement <<= msg;
    (*msg)[AidHost] = hostname;
    (*msg)[AidPort] = port;
    (*msg)[AidType] = type;
  }
  lprintf(4,"advertising server on %s:%d",hostname.c_str(),port);
  publish(advertisement,
      type == Socket::UNIX ? Message::HOST : Message::GLOBAL );
}

void GWServerWP::tryOpen ()
{
  // Try to start a server socket
  for( ;; )
  {
    if( sock )
      delete sock;
    string sockport = num2str(port);
    if( type == Socket::UNIX )
      sockport = hostname + ":" + sockport;
    sock = new Socket("sock/"+wpname(),sockport,type,10);
    if( !sock->ok() )
    {
      if( sock->errcode() == Socket::BIND )
      {
        // if bind error, assume another process already has it open,
        // so launch a GWClientWP to attach to it, and commit harakiri
        lprintf(1,"server socket %s:%d already bound\n",
                   hostname.c_str(),port);
        Message::Ref mref(new Message(MsgGWServerBindError),DMI::ANON|DMI::WRITE);
        Message &msg = mref;
        msg[AidHost] = hostname;
        msg[AidPort] = port;
        msg[AidType] = type;
        publish(mref,0,Message::LOCAL);
        // try the next port
        port++;
        continue;
      }
      else // some other error
      {
        string err = sock->errstr();
        lprintf(1,AidLogError,"fatal error (%s) on server socket %s:%d\n",
                   err.c_str(),hostname.c_str(),port);
        delete sock; sock=0;
        if( open_retries++ > MaxOpenRetries )
        {
          lprintf(1,AidLogError,"fatal error (%s) on server socket %s:%d, giving up\n",
                     err.c_str(),hostname.c_str(),port);
          Message::Ref mref(new Message(MsgGWServerFatalError),DMI::ANON|DMI::WRITE);
          Message &msg = mref;
          msg[AidHost] = hostname;
          msg[AidPort] = port;
          msg[AidType] = type;
          msg[AidError] = sock->errstr();
          publish(mref,0,Message::LOCAL);
          detachMyself();
        }
        else // retry later - schedule a timeout
        {
          lprintf(1,AidLogError,"fatal error (%s) on server socket %s:%d, will retry later\n",
                     err.c_str(),hostname.c_str(),port);
          addTimeout(Timeout_Retry,0,EV_ONESHOT);
        }
        return;
      }
    }
    // since we got here, the socket is OK
    // shout about it
    lprintf(1,"opened server socket %s:%d\n",hostname.c_str(),port);
	sock->setBlocking(false);
    advertiseServer();
    if( type == Socket::TCP )
    {
      dsp()->localData(GWNetworkServer)[0] = port;
      setGlobalPort(port);
    }
    else
    {
      std::string sock = ssprintf("%s:%d",hostname.c_str(),port);
      setGlobalSocket(sock);
      dsp()->localData(GWLocalServer)[0] = sock;
    }
    // add an input on the socket
    addInput(sock->getSid(),EV_FDREAD);
#if ADVERTISE_SERVERS
    // add a continuous re-advertise timeout so that open servers
    // are re-broadcast across the system (in case someone loses a connection)
    addTimeout(Timeout_Advertise,0,EV_CONT);
#endif
    return;
  }
}
};

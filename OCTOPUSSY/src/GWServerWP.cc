//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C95AADB010A.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C95AADB010A.cm

//## begin module%3C95AADB010A.cp preserve=no
//## end module%3C95AADB010A.cp

//## Module: GWServerWP%3C95AADB010A; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\GWServerWP.cc

//## begin module%3C95AADB010A.additionalIncludes preserve=no
//## end module%3C95AADB010A.additionalIncludes

//## begin module%3C95AADB010A.includes preserve=yes
#include "Gateways.h"
//## end module%3C95AADB010A.includes

// GWServerWP
#include "OCTOPUSSY/GWServerWP.h"
//## begin module%3C95AADB010A.declarations preserve=no
//## end module%3C95AADB010A.declarations

//## begin module%3C95AADB010A.additionalDeclarations preserve=yes
// timeout value for a retry of bind, in seconds
const Timeval Timeout_Retry(10.0),
// re-advertise timeout, in seconds
      Timeout_Advertise(10.0);
// max retries
const int MaxOpenRetries = 10;

// using LOFAR::num2str;  // defined in <Common/Debug.h>
using Debug::ssprintf;

//##ModelId=3C8F95710177
//## end module%3C95AADB010A.additionalDeclarations


// Class GWServerWP 

GWServerWP::GWServerWP (int port1)
  //## begin GWServerWP::GWServerWP%3C8F95710177.hasinit preserve=no
  //## end GWServerWP::GWServerWP%3C8F95710177.hasinit
  //## begin GWServerWP::GWServerWP%3C8F95710177.initialization preserve=yes
  : WorkProcess(AidGWServerWP),port(port1),sock(0),type(Socket::TCP)
  //## end GWServerWP::GWServerWP%3C8F95710177.initialization
{
  //## begin GWServerWP::GWServerWP%3C8F95710177.body preserve=yes
  // get port from config if not specified explicitly
  if( port<0 )
    config.get("gwport",port,4808);
  // get the local hostname
  char hname[1024];
  FailWhen(gethostname(hname,sizeof(hname))<0,"gethostname(): "+string(strerror(errno)));
  hostname = hname;
  //## end GWServerWP::GWServerWP%3C8F95710177.body
}

//##ModelId=3CC95151026E
GWServerWP::GWServerWP (const string &path, int port1)
  //## begin GWServerWP::GWServerWP%3CC95151026E.hasinit preserve=no
  //## end GWServerWP::GWServerWP%3CC95151026E.hasinit
  //## begin GWServerWP::GWServerWP%3CC95151026E.initialization preserve=yes
  : WorkProcess(AidGWServerWP),port(port1),sock(0),type(Socket::UNIX)
  //## end GWServerWP::GWServerWP%3CC95151026E.initialization
{
  //## begin GWServerWP::GWServerWP%3CC95151026E.body preserve=yes
  // get path from config, if not specified explicitly
  hostname = path;
  if( !hostname.length() )
  {
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
  }
  //## end GWServerWP::GWServerWP%3CC95151026E.body
}


//##ModelId=3DB9367E019C
GWServerWP::~GWServerWP()
{
  //## begin GWServerWP::~GWServerWP%3C8F942502BA_dest.body preserve=yes
  if( sock )
    delete sock;
  //## end GWServerWP::~GWServerWP%3C8F942502BA_dest.body
}



//##ModelId=3CC951680113
//## Other Operations (implementation)
void GWServerWP::init ()
{
  //## begin GWServerWP::init%3CC951680113.body preserve=yes
  subscribe(MsgGWRemoteUp|AidWildcard,Message::GLOBAL);
  // add local server port as -1 to indicate no active server
  if( type == Socket::TCP )
  {
    if( !dsp()->hasLocalData(GWNetworkServer) )
      dsp()->localData(GWNetworkServer) = -1;
  }
  else
  {
    if( !dsp()->hasLocalData(GWLocalServer) )
      dsp()->localData(GWLocalServer) = "";
  }
  //## end GWServerWP::init%3CC951680113.body
}

//##ModelId=3C90BE4A029B
bool GWServerWP::start ()
{
  //## begin GWServerWP::start%3C90BE4A029B.body preserve=yes
  WorkProcess::start();
  open_retries = 0;
  tryOpen();
  return False;
  //## end GWServerWP::start%3C90BE4A029B.body
}

//##ModelId=3C90BE880037
void GWServerWP::stop ()
{
  //## begin GWServerWP::stop%3C90BE880037.body preserve=yes
  WorkProcess::stop();
  if( sock )
    delete sock;
  sock = 0;
  //## end GWServerWP::stop%3C90BE880037.body
}

//##ModelId=3C90BE8E000E
int GWServerWP::timeout (const HIID &)
{
  //## begin GWServerWP::timeout%3C90BE8E000E.body preserve=yes
  if( !sock || !sock->ok() )
    tryOpen();
#if ADVERTISE_SERVERS
  else
    advertiseServer();
#endif
  return Message::ACCEPT;
  //## end GWServerWP::timeout%3C90BE8E000E.body
}

//##ModelId=3C95B4DC031C
int GWServerWP::input (int , int )
{
  //## begin GWServerWP::input%3C95B4DC031C.body preserve=yes
  // This is called when an incoming connection is requested
  // (since we only have one active input, we don't need no arguments)
  if( !sock ) // sanity check
    return Message::CANCEL;
  // do an accept on the socket
  Socket *newsock = sock->accept();
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
  //## end GWServerWP::input%3C95B4DC031C.body
}

//##ModelId=3CC951890246
int GWServerWP::receive (MessageRef &mref)
{
  //## begin GWServerWP::receive%3CC951890246.body preserve=yes
  if( mref->id().matches(MsgGWRemoteUp|AidWildcard) && sock && sock->ok() )
    advertiseServer();
  return Message::ACCEPT;
  //## end GWServerWP::receive%3CC951890246.body
}

// Additional Declarations
//##ModelId=3DB9367E033E
  //## begin GWServerWP%3C8F942502BA.declarations preserve=yes

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
  publish(advertisement.copy(),
      type == Socket::UNIX ? Message::HOST : Message::GLOBAL );
}

//##ModelId=3DB9367E037A
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
        MessageRef mref(new Message(MsgGWServerBindError),DMI::ANON|DMI::WRITE);
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
          MessageRef mref(new Message(MsgGWServerFatalError),DMI::ANON|DMI::WRITE);
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
      dsp()->localData(GWNetworkServer)[0] = port;
    else
      dsp()->localData(GWLocalServer)[0] = ssprintf("%s:%d",hostname.c_str(),port);
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
  //## end GWServerWP%3C8F942502BA.declarations
//## begin module%3C95AADB010A.epilog preserve=yes
//## end module%3C95AADB010A.epilog

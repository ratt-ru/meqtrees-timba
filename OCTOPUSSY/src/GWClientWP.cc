//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C95AADB0170.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C95AADB0170.cm

//## begin module%3C95AADB0170.cp preserve=no
//## end module%3C95AADB0170.cp

//## Module: GWClientWP%3C95AADB0170; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\GWClientWP.cc

//## begin module%3C95AADB0170.additionalIncludes preserve=no
//## end module%3C95AADB0170.additionalIncludes

//## begin module%3C95AADB0170.includes preserve=yes
#include "Gateways.h"
#include "GWServerWP.h"
//## end module%3C95AADB0170.includes

// GWClientWP
#include "OCTOPUSSY/GWClientWP.h"
//## begin module%3C95AADB0170.declarations preserve=no
//## end module%3C95AADB0170.declarations

//## begin module%3C95AADB0170.additionalDeclarations preserve=yes
const Timeval ReconnectTimeout(.2),
              ReopenTimeout(2.0),
// how long to try connect() (if operation in progress is returned)
              FailConnectTimeout(10.0),
// how long to try connects() before giving up on a transient connection
              GiveUpTimeout(30.0);
              
//## end module%3C95AADB0170.additionalDeclarations


// Class GWClientWP 

GWClientWP::GWClientWP (const string &host, int port, int type)
  //## begin GWClientWP::GWClientWP%3CD0167B021B.hasinit preserve=no
  //## end GWClientWP::GWClientWP%3CD0167B021B.hasinit
  //## begin GWClientWP::GWClientWP%3CD0167B021B.initialization preserve=yes
  : WorkProcess(AidGWClientWP),
    peerref(new DataRecord,DMI::ANONWR),
    peerlist(dynamic_cast<DataRecord&>(peerref.dewr()))
  //## end GWClientWP::GWClientWP%3CD0167B021B.initialization
{
  //## begin GWClientWP::GWClientWP%3CD0167B021B.body preserve=yes
  // add default connection, if specified
  if( host.length() )
  {
    FailWhen(!port,"both host and port must be specified");
    addConnection(host,port,type);
  }
  // add connections from config
  string peers;
  if( config.get("gwpeer",peers) )
  {
    while( peers.length() )
    {
      // split into "host1:port1,host2:port2,", etc.
      string peer;
      size_t pos = peers.find_first_of(',');
      if( pos != string::npos )
      {
        peer = peers.substr(0,pos);
        peers = peers.substr(pos+1);
      }
      else
      {
        peer = peers;
        peers = "";
      }
      pos = peer.find_first_of(':');
      FailWhen(pos == string::npos || !pos,"malformed 'gwpeer' specification");
      string host = peer.substr(0,pos);
      int port = atoi(peer.substr(pos+1).c_str());
      int type = ( host[0] == '=' || host.find_first_of('/') != string::npos )
                 ? Socket::UNIX : Socket::TCP;
      addConnection(host,port,type);
    }
  }
  
  // get the local hostname
  char hname[1024];
  FailWhen(gethostname(hname,sizeof(hname))<0,"gethostname(): "+string(strerror(errno)));
  hostname = hname;
  setState(STOPPED);
  //## end GWClientWP::GWClientWP%3CD0167B021B.body
}


GWClientWP::~GWClientWP()
{
  //## begin GWClientWP::~GWClientWP%3C95A941002E_dest.body preserve=yes
  for( CCLI iter = conns.begin(); iter != conns.end(); iter++ )
    if( iter->sock )
      delete iter->sock;
  //## end GWClientWP::~GWClientWP%3C95A941002E_dest.body
}



//## Other Operations (implementation)
void GWClientWP::init ()
{
  //## begin GWClientWP::init%3CA1C0C300FA.body preserve=yes
  // add our peerlist to local data
  dsp()->addLocalData(GWPeerList,peerref.copy(DMI::WRITE));
  if( !dsp()->hasLocalData(GWNetworkServer) )
    dsp()->localData(GWNetworkServer) = -1;
  if( !dsp()->hasLocalData(GWLocalServer) )
    dsp()->localData(GWLocalServer) = "";
  // messages from server gateway tell us when it fails to bind
  // to a port/when it binds/when it gives up
  subscribe(MsgGWServer|AidWildcard,Message::LOCAL);
  // subscribe to server advertisements
  subscribe(MsgGWServerOpenNetwork,Message::GLOBAL);
  subscribe(MsgGWServerOpenLocal,Message::HOST);
  // Bye messages from child gateways tell us when they have closed
  // (and thus need to be reopened)
  subscribe(MsgBye|AidGatewayWP|AidWildcard,Message::LOCAL);
  // Remote messages for remote node management
  subscribe(MsgGWRemote|AidWildcard,Message::LOCAL);
  subscribe(MsgGWRemoteUp|AidWildcard,Message::GLOBAL);
  //## end GWClientWP::init%3CA1C0C300FA.body
}

bool GWClientWP::start ()
{
  //## begin GWClientWP::start%3C95A941008B.body preserve=yes
  activate();
  return WorkProcess::start();
  //## end GWClientWP::start%3C95A941008B.body
}

void GWClientWP::stop ()
{
  //## begin GWClientWP::stop%3C95A9410092.body preserve=yes
  setState(STOPPED);
  for( CLI iter = conns.begin(); iter != conns.end(); iter++ )
  {
    if( iter->sock )
      delete iter->sock;
    iter->sock = 0;
    iter->state = STOPPED;
  }
  //## end GWClientWP::stop%3C95A9410092.body
}

int GWClientWP::timeout (const HIID &id)
{
  //## begin GWClientWP::timeout%3C95A9410093.body preserve=yes
  bool connecting = False;
  Timestamp::now(&now);
  // go thru connection list and figure out what to do
  for( CLI iter = conns.begin(); iter != conns.end(); iter++ )
  {
    switch( iter->state )
    {
      case CONNECTED:   // do nothing
        break;
      
      case CONNECTING:  // connecting?
        if( now >= iter->fail ) // check for timeout
        {
          lprintf(1,"connect(%s:%d) timeout; will retry later",iter->host.c_str(),iter->port);
          delete iter->sock; iter->sock = 0;
          iter->state = WAITING;
          iter->retry = now + ReopenTimeout;
          break;
        }
        
      case STOPPED:
      case WAITING:    // not connecting - is it time for a retry?
        if( now >= iter->retry )
          tryConnect(*iter);
        break;
      
      default:
        lprintf(1,"error: unexpected state %d for %s:%d\n",iter->state,
            iter->host.c_str(),iter->port);
    }
    if( iter->state == CONNECTING )
      connecting = True;
  }
  // if reconnecting timeout (i.e. short one) is set, and no-one
  // seems to be connecting, then cancel it
  if( id == AidReconnect && !connecting )
  {
    reconnect_timeout_set = False;
    return Message::CANCEL;
  }
  if( connecting && !reconnect_timeout_set )
  {
    addTimeout(ReconnectTimeout,AidReconnect);
    reconnect_timeout_set = True;
  }
  
  return Message::ACCEPT;
  //## end GWClientWP::timeout%3C95A9410093.body
}

int GWClientWP::receive (MessageRef& mref)
{
  //## begin GWClientWP::receive%3C95A9410095.body preserve=yes
  const Message &msg = mref.deref();
  const HIID &id = msg.id();
  if( id == MsgGWServerBindError )
  {
    // server has failed to bind to a port -- assume a local peer has already
    // bound to it, so add it to our connection list
    int type = msg[AidType];
    if( type == Socket::UNIX )
    {
      string host = msg[AidHost];
      int port = msg[AidPort];
      Connection &cx = addConnection(host,port,type);
      lprintf(2,LogNormal,"adding %s:%d to connection list",host.c_str(),port);
      if( state() != STOPPED )
        tryConnect(cx);
    }
  }
  // a non-local server advertisement: see if we need to establish
  // a connection to it
  else if( id.matches(MsgGWServerOpen|AidWildcard) && !isLocal(msg) )
  {
    // ignore local server advertisements from non-local hosts
    if( id == MsgGWServerOpenLocal && msg.from().host() != address().host() )
      return Message::ACCEPT;
    // ignore network server advertisements from local host
    if( id == MsgGWServerOpenNetwork && msg.from().host() == address().host() )
      return Message::ACCEPT;
    HIID peerid = msg.from().peerid();
    if( peerlist[peerid].exists() )
    {
      lprintf(3,"peer-adv %s: already connected (%s:%d %s), ignoring",
          peerid.toString().c_str(),
          peerlist[peerid][AidHost].as_string().c_str(),
          peerlist[peerid][AidPort].as_int(),
          peerlist[peerid][AidTimestamp].as_Timestamp().toString("%T").c_str());
    }
    else
    {
      // initiate a connection only if (a) we don't have a server ourselves, 
      // or (b) our peerid is < remote
      // This ensures that only one peer of any given pair actually makes the 
      // connection.
      string host = msg[AidHost];
      int port = msg[AidPort];
      int type = msg[AidType];
      // advertisement for a local connection?
      if( type == Socket::UNIX )
      {
        if( !dsp()->localData(GWLocalServer).as_string().length() )
          lprintf(2,"peer-adv %s@%s:%d: no unix server here, initiating connection",peerid.toString().c_str(),host.c_str(),port); 
        else if( address().peerid() < peerid )
          lprintf(2,"peer-adv %s@%s:%d: higher rank, initiating connection",peerid.toString().c_str(),host.c_str(),port);
        else
        {
          lprintf(2,"peer-adv %s@%s:%d: lower rank, ignoring and waiting for connection",peerid.toString().c_str(),host.c_str(),port);   
          return Message::ACCEPT;
        }
      }
      else // network connection
      {
        if( !dsp()->localData(GWNetworkServer).as_int() < 0 )
          lprintf(2,"peer-adv %s@%s:%d: no network server here, initiating connection",peerid.toString().c_str(),host.c_str(),port); 
        else if( address().peerid() < peerid )
          lprintf(2,"peer-adv %s@%s:%d: higher rank, initiating connection",peerid.toString().c_str(),host.c_str(),port);
        else
        {
          lprintf(2,"peer-adv %s@%s:%d: lower rank, ignoring and waiting for connection",peerid.toString().c_str(),host.c_str(),port);   
          return Message::ACCEPT;
        }
        if( host == hostname )
          host = "localhost";
      }
      // create the connection
      Connection &cx = addConnection(host,port,type);
      cx.give_up = Timestamp::now() + GiveUpTimeout;
      if( state() != STOPPED )
        tryConnect(cx);
    }
  }
  else if( id.prefixedBy(MsgGWRemoteDuplicate) )
  {
    // message from child gateway advises us of a duplicate connection -- better
    // remove this from the connection list
    if( msg[AidHost].exists() )
    {
      const string &host = msg[AidHost];
      int port = msg[AidPort];
      if( removeConnection(host,port) )
        lprintf(2,LogNormal,"removed duplicate connection %s:%d",host.c_str(),port);
//      else
//        lprintf(2,LogWarning,"%s:%d not known, ignoring [%s]",
//            host.c_str(),port,msg.sdebug(1).c_str());
    }
  }
  // bye message from child? Reopen its gateway then
  // (unless the connection has been removed by MsgGWRemoteDuplicate, above)
  else if( id.prefixedBy(MsgBye|AidGatewayWP) )
  {
    Connection *cx = find(msg.from());
    if( cx )
    {
      lprintf(2,"caught Bye from child gateway for %s:%d, waking up\n",
          cx->host.c_str(),cx->port);
      if( cx->state == CONNECTED ) // just to make sure it's not a stray message
      {
        if( cx->give_up )
          cx->give_up = Timestamp::now() + GiveUpTimeout;
        cx->state = WAITING;
        tryConnect(*cx);
      }
    }
  }
  return Message::ACCEPT;
  //## end GWClientWP::receive%3C95A9410095.body
}

// Additional Declarations
  //## begin GWClientWP%3C95A941002E.declarations preserve=yes
GWClientWP::Connection & GWClientWP::addConnection (const string &host,int port,int type)
{
  for( CLI iter = conns.begin(); iter != conns.end(); iter++ )
    if( iter->host == host && iter->port == port )
      return *iter;
  Connection cx;
  cx.host = host;
  cx.port = port;
  cx.type = type;
  cx.sock = 0;
  cx.state = STOPPED;
  cx.give_up = Timestamp(0,0);
  cx.reported_failure = False;
  conns.push_back(cx);
  return conns.back();
}
    
bool GWClientWP::removeConnection (const string &host,int port)
{
  bool localhost = (host == "localhost");
  bool res = False;
  for( CLI iter = conns.begin(); iter != conns.end(); )
    if( iter->port == port &&
        ( iter->host == host || ( localhost && iter->host == "localhost" ) ) )
    {
      conns.erase(iter++);
      res = True;
    }
    else
      iter++;
  return res;
}

GWClientWP::Connection * GWClientWP::find (const string &host, const string &port)
{
  for( CLI iter = conns.begin(); iter != conns.end(); iter++ )
    if( iter->host == host && iter->port == port )
      return &(*iter);
  return 0;
}

GWClientWP::Connection * GWClientWP::find (const MsgAddress &gw)
{
  for( CLI iter = conns.begin(); iter != conns.end(); iter++ )
    if( iter->gw == gw )
      return &(*iter);
  return 0;
}


    
void GWClientWP::activate ()
{
  Timestamp::now(&now);
  setState(CONNECTING);
  // initiate connection on every socket
  for( CLI iter = conns.begin(); iter != conns.end(); iter++ )
    tryConnect(*iter);
  // add a re-open timeout
  addTimeout(ReopenTimeout,AidReopen);
}

void GWClientWP::tryConnect (Connection &cx)
{
  if( cx.state == CONNECTED ) // ignore if connected
    return;
  if( cx.state != CONNECTING ) // try to reconnect completely
  {
    if( cx.sock )
      delete cx.sock;
    lprintf(4,"creating client socket for %s:%d\n",
              cx.host.c_str(),cx.port);
    cx.sock = new Socket("cx.sock/"+wpname(),cx.host,num2str(cx.port),cx.type,-1);
    cx.state = CONNECTING;
    cx.fail = now  + FailConnectTimeout; 
    // fall thru to connection attempt, below
  }
  if( !cx.sock )  // sanity check
    return;
  // [re]try connection attempt
  int res = cx.sock->connect(0);
  dprintf(3)("connect(%s:%d): %d (%s)\n",cx.host.c_str(),cx.port,
                  res,cx.sock->errstr().c_str());
  if( res > 0 ) // connection established
  {
    lprintf(1,"connected to %s:%d, spawning child gateway\n",
                      cx.host.c_str(),cx.port);
    cx.state = CONNECTED;
    // spawn a new child gateway, subscribe to its Bye message
    cx.gw   = attachWP( new GatewayWP(cx.sock),DMI::ANON );
    cx.sock = 0; // socket is taken over by child
    cx.reported_failure = False;
  }
  else if( !res )  // in progress
  {
    dprintf(3)("connect still in progress\n");
    if( !reconnect_timeout_set )
    {
      addTimeout(ReconnectTimeout,AidReconnect);
      reconnect_timeout_set = True;
    }
  }
  else // else it is a fatal error, close and retry
  {
    if( cx.give_up && now > cx.give_up )
    {
      lprintf(2,"connect(%s:%d) error: %s; giving up",
          cx.host.c_str(),cx.port,cx.sock->errstr().c_str());
      delete cx.sock;
      removeConnection(cx.host,cx.port);
    }
    else
    {
      lprintf(cx.reported_failure?4:2,"connect(%s:%d) error: %s; will keep trying",
          cx.host.c_str(),cx.port,cx.sock->errstr().c_str());
      cx.reported_failure = True;
      delete cx.sock; cx.sock = 0;
      cx.state = WAITING;
      cx.retry = now + ReopenTimeout;
    }
  }
}
  //## end GWClientWP%3C95A941002E.declarations
//## begin module%3C95AADB0170.epilog preserve=yes
void initGateways (Dispatcher &dsp)
{
  dsp.attach(new GWServerWP(-1),DMI::ANON);
  dsp.attach(new GWServerWP("",0),DMI::ANON);
  dsp.attach(new GWClientWP,DMI::ANON);
}

//## end module%3C95AADB0170.epilog


// Detached code regions:
#if 0
//## begin GWClientWP::GWClientWP%3C95A9410081.initialization preserve=yes
  : WorkProcess(AidGWClientWP),
    peerref(new DataRecord,DMI::ANONWR),
    peerlist(dynamic_cast<DataRecord&>(peerref.dewr()))
//## end GWClientWP::GWClientWP%3C95A9410081.initialization

//## begin GWClientWP::GWClientWP%3C95A9410081.body preserve=yes
  // add default connection, if specified
  if( host.length() )
  {
    FailWhen(!port,"both host and port must be specified");
    addConnection(host,port,type);
  }
  // add connections from config
  string peers;
  if( config.get("gwpeer",peers) )
  {
    while( peers.length() )
    {
      // split into "host1:port1,host2:port2,", etc.
      string peer;
      size_t pos = peers.find_first_of(',');
      if( pos != string::npos )
      {
        peer = peers.substr(0,pos);
        peers = peers.substr(pos+1);
      }
      else
      {
        peer = peers;
        peers = "";
      }
      pos = peer.find_first_of(':');
      FailWhen(pos == string::npos || !pos,"malformed 'gwpeer' specification");
      string host = peer.substr(0,pos);
      int port = atoi(peer.substr(pos+1).c_str());
      int type = ( host[0] == '=' || host.find_first_of('/') != string::npos )
                 ? Socket::UNIX : Socket::TCP;
      addConnection(host,port,type);
    }
  }
  
  // get the local hostname
  char hname[1024];
  FailWhen(gethostname(hname,sizeof(hname))<0,"gethostname(): "+string(strerror(errno)));
  hostname = hname;
  setState(STOPPED);
//## end GWClientWP::GWClientWP%3C95A9410081.body

#endif

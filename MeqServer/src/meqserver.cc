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

#include <OCTOPUSSY/Octopussy.h>
#include <OCTOPUSSY/StatusMonitorWP.h>
#include <OCTOPUSSY/GWServerWP.h>
#include <OCTOPUSSY/GWClientWP.h>
#include <AppAgent/OctoEventMux.h>
#include <MeqServer/MeqServer.h>
#include <MeqServer/AID-MeqServer.h>
#include <MEQ/MTPool.h>
#include <unistd.h>

typedef std::vector<string> StrVec;
typedef StrVec::iterator SVI;
typedef StrVec::const_iterator SVCI;

using namespace DebugMeq;
using namespace DMI;
using namespace AppAgent;
using LOFAR::Socket;

// define a local debug context
namespace main_debug_context
{
  static ::Debug::Context main_debug_context("meqserver_main");
  static inline ::Debug::Context & getDebugContext() { return main_debug_context; };
}
    
int main (int argc,const char *argv[])
{
  // begin by closing all open FDs -- this is necessary so that we don't inherit any
  // GW sockets from a launching browser
  for( int i=2; i<1024; i++ )
    close(i);

  using main_debug_context::getDebugContext;
  try 
  {
    // collect command-line arguments into vector
    StrVec args(argc-1);
    for( int i=1; i<argc; i++ )
      args[i-1] = argv[i];
    
    // parse various options
    bool start_gateways = 
        std::find(args.begin(),args.end(),string("-nogw")) == args.end();
    // "-ssr" option
    if( std::find(args.begin(),args.end(),string("-ssr")) != args.end() )
      Meq::NodeNursery::forceSequentialServiceRequests(true);
    // "-mt" option
    StrVec::const_iterator iter = 
        std::find(args.begin(),args.end(),string("-mt"));
    if( iter != args.end() )
    {
      ++iter;
      if( iter == args.end() || !isdigit((*iter)[0]) )
      {
        cerr<<"-mt option must be followed by number of threads to use\n";
        return 1;
      }
      int nt = atoi(iter->c_str());
      if( nt>0 )
      {
        Meq::MTPool::Brigade::setBrigadeSize(nt);
        Meq::MTPool::Brigade::startNewBrigade();
        Meq::MTPool::Brigade::startNewBrigade();
      }
    }
    // "-gw" option
    string local_gw;
    iter = std::find(args.begin(),args.end(),string("-gw"));
    if( iter != args.end() )
    {
      ++iter;
      if( iter == args.end() )
      {
        cerr<<"-gw option must be followed by socket name\n";
        return 1;
      }
      local_gw = *iter;
    }
    Debug::initLevels(argc,argv);
    
    cdebug(0)<<"=================== initializing OCTOPUSSY =====================\n";
    Octopussy::OctopussyConfig::initGlobal(argc,argv);
    Octopussy::init(false);  // start_gateways=False, we start our own
    // We open a local server called =meqserver-%U:1 (and increment port number as
    // appropriate)
    std::string sock = ssprintf("=meqserver-%d",(int)getuid());
    Octopussy::dispatcher().attach(new Octopussy::GWServerWP(sock,1));
    // We also open a client to connect to any local browsers, and to
    // anything specified via gwpeer=.
    sock = ssprintf("=meqbrowser-%d",(int)getuid());
    Octopussy::dispatcher().attach(new
              Octopussy::GWClientWP(sock,1,Octopussy::Socket::UNIX));
    if( !local_gw.empty() )
      Octopussy::dispatcher().attach(new
                Octopussy::GWClientWP(local_gw,1,Octopussy::Socket::UNIX));
    // Note that meqserver does not open a local TCP server. The connection
    // is always initiated from server to browser!
    
    cdebug(0)<<"=================== starting StatusMonitor ====================\n";
    Octopussy::dispatcher().attach(new Octopussy::StatusMonitorWP());
    
    cdebug(0)<<"=================== creating MeqServer ========================\n";
    Meq::MeqServer meqserver;
    
    // create control channel 
    DMI::Record::Ref recref;
    DMI::Record &rec = recref <<= new DMI::Record;
    rec[FEventMapIn] <<= new DMI::Record;
    rec[FEventMapIn][FDefaultPrefix] = AidMeqServer|AidIn;
    rec[FEventMapOut] <<= new DMI::Record;
    rec[FEventMapOut][FDefaultPrefix] = AidMeqServer|AidOut;

    // create octopussy message multiplexer and event channel
    AppAgent::OctoEventMux::Ref mux(new AppAgent::OctoEventMux(AidMeqServer));
    EventChannel::Ref control_channel(mux().newChannel());
    
    // attach channel to app and mux to OCTOPUSSY
    meqserver.attachControl(control_channel);
    Octopussy::dispatcher().attach(mux);
    // preinitialize control channel
    control_channel().init(recref);
    
    cdebug(0)<<"=================== starting OCTOPUSSY thread =================\n";
    Octopussy::initThread(true);
    
    cdebug(0)<<"=================== running MeqServer =========================\n";
    meqserver.run();
    
//     cdebug(0)<<"=================== starting app threads ======================\n";
//     std::vector<Thread::ThrID> appthreads(apps.size());
//     for( uint i=0; i<apps.size(); i++)
//     {
//       appthreads[i] = apps[i]().runThread(true);
//       cdebug(0)<<"  thread: "<<appthreads[i]<<endl;
//     }
//     
//     cdebug(0)<<"=================== rejoining app threads =====================\n";
//     for( uint i=0; i<appthreads.size(); i++ )
//       appthreads[i].join();

    if( Meq::MTPool::Brigade::numBrigades() )
    {
      cdebug(0)<<"=================== stopping worker threads ===================\n";
      Meq::MTPool::Brigade::stopAll();
    }

//    pthread_kill_other_threads_np();
//    exit(1);
    
    cdebug(0)<<"=================== stopping OCTOPUSSY ========================\n";
    Octopussy::stopThread();
    
    cdebug(0)<<"=================== exiting ===================================\n";
  }
  catch ( std::exception &exc ) 
  {
    cdebug(0)<<"Exiting with exception: "<<exc.what()<<endl;  
    return 1;
  }
//  catch ( AipsError &err ) 
//  {
//    cdebug(0)<<"Exiting with AIPS++ exception: "<<err.getMesg()<<endl;  
//    return 1;
//  }
  catch( ... )
  {
    cdebug(0)<<"Exiting with unknown exception\n";  
    return 1;
  }
  
  return 0;  
}

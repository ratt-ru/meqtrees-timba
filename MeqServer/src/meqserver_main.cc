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

#include "config.h"
#ifdef HAVE_MPI
#include <MeqMPI/MeqMPI.h>
#endif

typedef std::vector<string> StrVec;
typedef StrVec::iterator SVI;
typedef StrVec::const_iterator SVCI;

using namespace DebugMeq;
using namespace DMI;
using namespace AppAgent;
using LOFAR::Socket;
using namespace Meq;

// define a local debug context
namespace main_debug_context
{
  static ::Debug::Context main_debug_context("meqserver_main");
  static inline ::Debug::Context & getDebugContext() { return main_debug_context; };
}
    
int main (int argc,const char *argv[])
{
  int retcode = 0;
  Debug::initLevels(argc,argv);
  // begin by closing all open FDs -- this is necessary so that we don't inherit any
  // GW sockets from a launching browser
  for( int i=3; i<1024; i++ )
    close(i);
  
  int max_threads = 1;

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
      max_threads = nt;
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
  
#ifdef HAVE_MPI
  // init MPI 
  MPI_Init(&argc,const_cast<char***>(&argv));
  
  MeqMPI meqmpi(argc,argv);
  // If we're on processor 0, proceed below for regular meqserver startup.
  // On all other processors, start abbreviated version 
  if( meqmpi.comm_rank() !=0 )
  {
    Meq::Forest forest;
    meqmpi.attachForest(forest);
    meqmpi.initialize();
    meqmpi.rejoinCommThread();
    // stop worker threads
    Meq::MTPool::stop();
  }
  else
  {
    // rank 0: main server.
    // don't bother to initialize MPI unless there's someone to talk to
    if( meqmpi.comm_size() > 1 )
    {
      meqmpi.initialize();
      // start worker threads, since we always need them in MPI mode
      Meq::MTPool::start(max_threads*2-1,max_threads);
    }
#else
  // no MPI support -- start worker threads only as needed
  // Start one less since the main execution thread will join the brigade.
  if( max_threads > 1 )
    Meq::MTPool::start(max_threads*2-1,max_threads);
#endif

  using main_debug_context::getDebugContext;
  try 
  {
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
    #ifdef HAVE_MPI
    meqmpi.attachForest(meqserver.getForest());
    #endif
    
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
    
//    pthread_kill_other_threads_np();
//    exit(1);
    
    cdebug(0)<<"=================== stopping OCTOPUSSY ========================\n";
    Octopussy::stopThread();
    
    cdebug(0)<<"=================== exiting ===================================\n";
  }
  catch ( std::exception &exc ) 
  {
    cdebug(0)<<"Exiting with exception: "<<exc.what()<<endl;  
    retcode = 1;
  }
//  catch ( AipsError &err ) 
//  {
//    cdebug(0)<<"Exiting with AIPS++ exception: "<<err.getMesg()<<endl;  
//    return 1;
//  }
  catch( ... )
  {
    cdebug(0)<<"Exiting with unknown exception\n";  
    retcode = 1;
  }
  // stop worker threads, if we were running them
  if( MTPool::enabled() )
  {
    cdebug(0)<<"=================== stopping worker threads ===================\n";
    MTPool::stop();
  }
#ifdef HAVE_MPI
  // tell remote subservers to stop
  for( int i=1; i<meqmpi.comm_size(); i++ )
    meqmpi.postCommand(MeqMPI::TAG_HALT,i);
  }
  meqmpi.stopCommThread();
  MPI_Finalize();
#endif
  return retcode;  
}

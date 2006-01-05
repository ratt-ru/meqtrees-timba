#include <OCTOPUSSY/Octopussy.h>
#include <OCTOPUSSY/StatusMonitorWP.h>
#include <AppAgent/OctoEventMux.h>
#include <MeqServer/MeqServer.h>
#include <MeqServer/AID-MeqServer.h>
#include <MEQ/MTPool.h>

typedef std::vector<string> StrVec;
typedef StrVec::iterator SVI;
typedef StrVec::const_iterator SVCI;

using namespace DebugMeq;
using namespace DMI;
using namespace AppAgent;
    
int main (int argc,const char *argv[])
{
  try 
  {
    // collect command-line arguments into vector
    StrVec args(argc-1);
    for( int i=1; i<argc; i++ )
      args[i-1] = argv[i];
    
    // parse various options
    bool start_gateways = 
        std::find(args.begin(),args.end(),string("-nogw")) == args.end();
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
    
//     Debug::setLevel("VisRepeater",2);
//     Debug::setLevel("MSVisAgent",2);
//     Debug::setLevel("VisAgent",2);
//     Debug::setLevel("OctoEventMux",2);
//     Debug::setLevel("OctoEventSink",2);
//     Debug::setLevel("BOIOSink",2);
//     Debug::setLevel("AppControl",2);
//     Debug::setLevel("Dsp",1);
//     Debug::setLevel("Solver",3);
    Debug::initLevels(argc,argv);
    
    cout<<"=================== initializing OCTOPUSSY =====================\n";
    Octopussy::OctopussyConfig::initGlobal(argc,argv);
    Octopussy::init(start_gateways);
    
    cout<<"=================== starting StatusMonitor ====================\n";
    Octopussy::dispatcher().attach(new Octopussy::StatusMonitorWP());
    
    cout<<"=================== starting OCTOPUSSY thread =================\n";
    Octopussy::initThread(true);
    
    cout<<"=================== creating MeqServer ========================\n";
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
    
    cout<<"=================== running MeqServer =========================\n";
    meqserver.run();
    
//     cout<<"=================== starting app threads ======================\n";
//     std::vector<Thread::ThrID> appthreads(apps.size());
//     for( uint i=0; i<apps.size(); i++)
//     {
//       appthreads[i] = apps[i]().runThread(true);
//       cout<<"  thread: "<<appthreads[i]<<endl;
//     }
//     
//     cout<<"=================== rejoining app threads =====================\n";
//     for( uint i=0; i<appthreads.size(); i++ )
//       appthreads[i].join();

    if( Meq::MTPool::Brigade::numBrigades() )
    {
      cout<<"=================== stopping worker threads ===================\n";
      Meq::MTPool::Brigade::stopAll();
    }

//    pthread_kill_other_threads_np();
//    exit(1);
    
    cout<<"=================== stopping OCTOPUSSY ========================\n";
    Octopussy::stopThread();
    
    cout<<"=================== exiting ===================================\n";
  }
  catch ( std::exception &exc ) 
  {
    cout<<"Exiting with exception: "<<exc.what()<<endl;  
    return 1;
  }
//  catch ( AipsError &err ) 
//  {
//    cout<<"Exiting with AIPS++ exception: "<<err.getMesg()<<endl;  
//    return 1;
//  }
  catch( ... )
  {
    cout<<"Exiting with unknown exception\n";  
    return 1;
  }
  
  return 0;  
}

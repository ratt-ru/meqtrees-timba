#include <AppAgent/BOIOSink.h>
#include <MSVisAgent/MSInputSink.h>
#include <MSVisAgent/MSOutputSink.h>
#include <OCTOPUSSY/Octopussy.h>
#include <OCTOGlish/GlishConnServerWP.h>
#include <OctoAgent/EventMultiplexer.h>
// #include <casa/Exceptions/Error.h>

#include <AppUtils/VisRepeater.h>
#include <MeqServer/MeqServer.h>
#include <MeqServer/AID-MeqServer.h>

typedef std::vector<string> StrVec;
typedef StrVec::iterator SVI;
typedef StrVec::const_iterator SVCI;

using namespace MSVisAgent;
using namespace OctoAgent;
using namespace AppControlAgentVocabulary;

bool setupApp (ApplicationBase::Ref &app,const string &str)
{
  if( str.length() < 6 )
    return False;
  string name = str.substr(0,5);
  string spec = str.substr(5);
  // select application based on spec string
  AtomicID wpclass;
  if( name == "-meq:" )
  {
    cout<<"=================== creating MeqServer =-==================\n";
    app <<= new Meq::MeqServer;
    wpclass = AidMeqServer;
  }
  else if( name == "-rpt:" )
  {
    cout<<"=================== creating repeater =====================\n";
    app <<= new VisRepeater;
    wpclass = AidRepeater;
  }
  else 
    return False;
  
  // split spec string at ":" character
  StrVec specs;
  uint ipos = 0, len = spec.length();
  while( ipos < len )
  {
    uint ipos1 = spec.find(':',ipos);
    if( ipos1 == string::npos )
      ipos1 = len;
    specs.push_back(spec.substr(ipos,ipos1-ipos));
    ipos = ipos1 + 1;
  }
  // print it out
  cout<<"=== app spec: ";
  for( uint i=0; i<specs.size(); i++ )
      cout<<"\""<<specs[i]<<"\" ";
  cout<<endl;
  FailWhen(specs.size() != 3,"invalid app spec: "+spec);
  
  // initialize parameter record
  DataRecord::Ref recref;
  DataRecord &rec = recref <<= new DataRecord;
  // init errors will be thrown as exceptions
  rec[FThrowError] = True;
  // setup control agent for delayed initialization
  rec[AidControl] <<= new DataRecord;
  rec[AidControl][FDelayInit] = True;
  rec[AidControl][FEventMapIn] <<= new DataRecord;
  rec[AidControl][FEventMapIn][FDefaultPrefix] = HIID(specs[2])|AidIn;
  rec[AidControl][FEventMapOut] <<= new DataRecord;
  rec[AidControl][FEventMapOut][FDefaultPrefix] = HIID(specs[2])|AidOut;

  // create agents
  OctoAgent::EventMultiplexer::Ref mux;
    mux <<= new OctoAgent::EventMultiplexer(wpclass);
  // input agent
  VisAgent::InputAgent::Ref in;
  if( specs[0] == "M" )
    in <<= new VisAgent::InputAgent(new MSVisAgent::MSInputSink,DMI::ANONWR);
  else if( specs[0] == "B" )
    in <<= new VisAgent::InputAgent(new BOIOSink,DMI::ANONWR);
  else if( specs[0] == "O" )
    in <<= new VisAgent::InputAgent(mux().newSink());
  else
    Throw("invalid input type: "+spec[0]);
  // output agent
  VisAgent::OutputAgent::Ref out;
  if( specs[1] == "M" )
    out <<= new VisAgent::OutputAgent(new MSVisAgent::MSOutputSink,DMI::ANONWR);
  else if( specs[1] == "B" )
    out <<= new VisAgent::OutputAgent(new BOIOSink,DMI::ANONWR);
  else if( specs[1] == "O" )
    out <<= new VisAgent::OutputAgent(mux().newSink());
  else
    Throw("invalid output type: "+spec[1]);
  // control agent
  AppControlAgent::Ref control;
  control <<= new AppControlAgent(mux().newSink());
  // attach flags to non-octopussy agents
  if( specs[0] != "O" )
    in().attach(mux().eventFlag());
  if( specs[1] != "O" )
    out().attach(mux().eventFlag());
  // attach agents to app and mux to OCTOPUSSY
  app()<<in<<out<<control;
  Octopussy::dispatcher().attach(mux,DMI::WRITE);
  // preinitialize control
  control().preinit(recref);
  
  return True;
}
    
int main (int argc,const char *argv[])
{
  
  try 
  {
    // collect command-line arguments into vector
    StrVec args(argc-1);
    // use defaults if none
    if( args.empty() )
    {
      args.push_back(string("-meq:M:M:MeqServer"));
    }
    else // else fill from command line
    {
      for( int i=1; i<argc; i++ )
        args[i-1] = argv[i];
    }
    // parse various options
    bool glish = 
        std::find(args.begin(),args.end(),string("-noglish")) == args.end();
    bool start_gateways = 
        std::find(args.begin(),args.end(),string("-nogw")) == args.end();
    
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
    OctopussyConfig::initGlobal(argc,argv);
    Octopussy::init(start_gateways);
    
    if( glish )
    {
      cout<<"=================== initializing Glish gateway =================\n";
      Octopussy::dispatcher().attach(
          new GlishConnServerWP,DMI::ANON);
    }
    
    cout<<"=================== starting OCTOPUSSY thread =================\n";
    Octopussy::initThread(True);
    
    cout<<"=================== creating apps =============================\n";
    std::vector<ApplicationBase::Ref> apps;
    for( uint i=0; i<args.size(); i++ )
    {
      ApplicationBase::Ref ref;
      if( setupApp(ref,args[i]) )
        apps.push_back(ref);
    }
    // init a default solver, if no apps were set up
    if( apps.empty() )
    {
      ApplicationBase::Ref ref;
      if( setupApp(ref,"-meq:M:M:Solver") )
        apps.push_back(ref);
    }
    
    cout<<"=================== starting app threads ======================\n";
    std::vector<Thread::ThrID> appthreads(apps.size());
    for( uint i=0; i<apps.size(); i++)
    {
      appthreads[i] = apps[i]().runThread(True);
      cout<<"  thread: "<<appthreads[i]<<endl;
    }
    
    cout<<"=================== rejoining app threads =====================\n";
    for( uint i=0; i<appthreads.size(); i++ )
      appthreads[i].join();
    
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

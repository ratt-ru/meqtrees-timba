#include <OCTOPUSSY/Dispatcher.h>
#include <OCTOPUSSY/Gateways.h>
#include <OCTOPUSSY/GWClientWP.h>
#include <OCTOPUSSY/ListenerWP.h>
#include <DMI/Global-Registry.h>
#include <sys/types.h>
#include <unistd.h>    

using namespace Octopussy;

int aidRegistry_Meq();
int aidRegistry_MeqNodes();
int aidRegistry_MeqServer();

static int dum = aidRegistry_Global() +
                 aidRegistry_Meq() +
                 aidRegistry_MeqNodes() +
                 aidRegistry_MeqServer();
    

int main (int argc,const char *argv[])
{
  Debug::initLevels(argc,argv);
  OctopussyConfig::initGlobal(argc,argv);
  
  try 
  {
    Dispatcher dsp;
    dsp.attach(new ListenerWP);
    initGateways(dsp);
    dsp.start();
    dsp.pollLoop();
    dsp.stop();
  }
  catch( std::exception &err ) 
  {
    cerr<<"\nCaught exception:\n"<<err.what()<<endl;
    return 1;
  }
  cerr<<"Exiting normally\n";
  return 0;
}


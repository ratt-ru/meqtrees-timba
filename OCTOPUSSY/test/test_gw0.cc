#include "OCTOPUSSY/Dispatcher.h"
#include "OCTOPUSSY/Gateways.h"
#include "OCTOPUSSY/LoggerWP.h"
#include <sys/types.h>
#include <unistd.h>    

int aidRegistry_Testing();
static int dum = aidRegistry_Testing();
    
int main (int argc,const char *argv[])
{
  Debug::initLevels(argc,argv);
  OctopussyConfig::initGlobal(argc,argv);

  try 
  {
    Dispatcher dsp;
    dsp.attach(new LoggerWP(10,Message::LOCAL),DMI::ANON);
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


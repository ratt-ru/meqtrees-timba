#include "OCTOPUSSY/Dispatcher.h"
#include "OCTOPUSSY/LoggerWP.h"
#include "OCTOPUSSY/Gateways.h"
#include "OCTOGlish/GlishConnServerWP.h"
#include "OCTOGlish/AID-OCTOGlish.h"
#include "DMI/Exception.h"
#include <sys/types.h>
#include <unistd.h>    

static int dum = 
    aidRegistry_OCTOPUSSY() && 
    aidRegistry_OCTOGlish();    

using namespace OctoGlish;

// octoserver -- glish proxy for octopussy
// This is started as a server from glish (from octopussy.g) in order
// to establish a connection to octopussy.
    
int main (int argc,const char *argv[])
{
  Debug::initLevels(argc,argv);
  OctopussyConfig::initGlobal(argc,argv);
  
  try 
  {
    Dispatcher dsp;
    initGateways(dsp);
    dsp.attach(new GlishConnServerWP);
    dsp.attach(new LoggerWP(10,Message::HOST));
    dsp.start();
    dsp.pollLoop();
    dsp.stop();
  }
  catch( std::exception &exc ) 
  {
    cerr<<"\nCaught exception:\n"<<exceptionToString(exc)<<endl;
    return 1;
  }
  cerr<<"Exiting normally\n";
  return 0;
}


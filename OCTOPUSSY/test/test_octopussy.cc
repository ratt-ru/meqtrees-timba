#include "OCTOPUSSY/Dispatcher.h"
#include "OCTOPUSSY/GWServerWP.h"
#include "OCTOPUSSY/LoggerWP.h"
#include "EchoWP.h"
#include <sys/types.h>
#include <unistd.h>    

static int dum = aidRegistry_Testing();
    
int main (int argc,const char *argv[])
{
  Debug::initLevels(argc,argv);
  Debug::initLevels(argc,argv);
  
  try 
  {
    Dispatcher dsp;
    dsp.attach(new LoggerWP,DMI::ANON);
    dsp.attach(new EchoWP,DMI::ANON);
    dsp.attach(new EchoWP(5),DMI::ANON);
    dsp.start();
    dsp.pollLoop();
    dsp.stop();
  }
  catch( Debug::Error err ) 
  {
    cerr<<"\nCaught exception:\n"<<err.what()<<endl;
    return 1;
  }
  cerr<<"Exiting normally\n";
  return 0;
}


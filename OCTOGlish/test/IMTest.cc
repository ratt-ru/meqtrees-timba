#include "OCTOPUSSY/Dispatcher.h"
#include "OCTOPUSSY/Gateways.h"
#include "OCTOPUSSY/LoggerWP.h"
#include "IMTestWP.h"
#include <sys/types.h>
#include <unistd.h>    
    
// make sure registery gets pulled in
int aidRegistry_OCTOGlish ();
static int dum = aidRegistry_OCTOGlish();


int main (int argc,const char *argv[])
{
  Debug::initLevels(argc,argv);
  OctopussyConfig::initGlobal(argc,argv);
  
  try 
  {
    Dispatcher dsp;
    initGateways(dsp);
    dsp.attach(new LoggerWP,DMI::ANON);
    if (argc >= 2)
    {
      for (int i=1; i < argc; i++)
      {
	if (!strncmp(argv[i], "-m", 2))
	{
	  cout << "Master: sending messages." << endl;
	  dsp.attach(new IMTestWP(true), DMI::ANON);
	}
      }
      for (int i=1; i < argc; i++)
      {
	if (!strncmp(argv[i], "-s", 2))
	{
	  cout << "Slave: echoing messages." << endl;
	  dsp.attach(new IMTestWP(false), DMI::ANON);
	}
      }
    }
    else
    {
      dsp.attach(new IMTestWP(true),DMI::ANON);
      dsp.attach(new IMTestWP(false),DMI::ANON);
    }
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


#include "OCTOPUSSY/Dispatcher.h"
#include "OCTOPUSSY/Gateways.h"
#include "OCTOPUSSY/LoggerWP.h"
#include "IMTestWP.h"
#include <sys/types.h>
#include <unistd.h>    
    
// make sure registery gets pulled in
int aidRegistry_OCTOGlish ();
static int dum = aidRegistry_OCTOGlish();

using namespace OctoGlish;

int main (int argc,const char *argv[])
{
  Debug::initLevels(argc,argv);
  OctopussyConfig::initGlobal(argc,argv);
  
  try 
  {
    Dispatcher dsp;
    initGateways(dsp);
    dsp.attach(new LoggerWP);
    if (argc >= 2)
    {
      for (int i=1; i < argc; i++)
      {
	if (!strncmp(argv[i], "-m", 2))
	{
	  cout << "Master: sending messages." << endl;
	  dsp.attach(new IMTestWP(true));
	}
      }
      for (int i=1; i < argc; i++)
      {
	if (!strncmp(argv[i], "-s", 2))
	{
	  cout << "Slave: echoing messages." << endl;
	  dsp.attach(new IMTestWP(false));
	}
      }
    }
    else
    {
      dsp.attach(new IMTestWP(true));
      dsp.attach(new IMTestWP(false));
    }
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


#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

#include "ListenerWP.h"
#include "AID-OCTOPUSSY.h"

namespace Octopussy
{
  
using namespace DMI;
    
ListenerWP::ListenerWP ()
  : WorkProcess(AidListenerWP)
{
}


//##ModelId=3DB9369A0073
ListenerWP::~ListenerWP()
{
}



//##ModelId=3CA045020054
void ListenerWP::init ()
{
  // subscribe to all messages
  subscribe(AidWildcard,Message::GLOBAL);
}


//##ModelId=3CA0450C0103
int ListenerWP::receive (Message::Ref &mref)
{
  std::cout<<"ListenerWP: received "<<mref->sdebug(getDebugContext().level()+1,"  ")<<endl;
  return Message::ACCEPT;
}

    
};

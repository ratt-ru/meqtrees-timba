#include "ReflectorWP.h"

namespace Octopussy
{

ReflectorWP::ReflectorWP (AtomicID wpid)
 : WorkProcess(wpid)
{
}

ReflectorWP::~ReflectorWP()
{
}

void ReflectorWP::init ()
{
  WorkProcess::init();
  subscribe("Reflect.*");
}

//##ModelId=3C7E4AC70261
bool ReflectorWP::start ()
{
  WorkProcess::start();
  return false;
}

//##ModelId=3C7E49AC014C
int ReflectorWP::receive (Message::Ref& mref)
{
  // ignore messages from ourselves
  if( mref->from() == address() )
    return Message::ACCEPT;
  // print the message starting at debug level 2
  if( Debug(2) )
  {
    int level = getDebugContext().level() - 1;
    dprintf(2)("received: %s\n",mref->sdebug(level).c_str());
  }
  // prepend "Reflect" to the message ID
  mref().setId( AidReflect | mref->id() );
  // return to sender
  MsgAddress from = mref->from();
  send(mref,from);
  
  return Message::ACCEPT;
}

};

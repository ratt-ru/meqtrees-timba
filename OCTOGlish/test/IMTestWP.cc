#include <DMI/Record.h>

#include "IMTestWP.h"

namespace OctoGlish
{
    
const HIID MsgHelloWorld("IMTestWP.HelloWorld");
const HIID MsgStart("start");

IMTestWP::IMTestWP (bool isWriter)
  : WorkProcess(AidIMTestWP),
    itsIsWriter(isWriter)
{
}

IMTestWP::~IMTestWP()
{
}

void IMTestWP::init ()
{
  WorkProcess::init();

  subscribe("WP.Hello.*");
  subscribe("IMTestWP.*");
  subscribe("start.*");
}

bool IMTestWP::start ()
{
  WorkProcess::start();

#ifdef USE_THREADS
  //  for( int i=0; i<threads; i++ )
    createWorker();
#endif

  return false;
}

int IMTestWP::receive (Message::Ref& mref)
{
  lprintf(2,"received %s\n",mref.debug(10));

  if (mref->from() == address()) return Message::ACCEPT;

  // wait for start message
  if (mref->id().matches("start.*"))
  {
    cout << "mref->from() = " << mref->from().toString() << endl;
    cout << "I am " << address().toString() << endl;

    if (itsIsWriter)
    {
      cout << "Sending HelloWorld msg." << endl;
      sendMsg();
    }
  }
  else if( mref->id() == MsgHelloWorld)
  {
    // COW message
    Message & msg = mref();
    
    string content = msg["Content"].as<string>();
    cout << "Received msg: " << content << endl;
    
    if (itsIsWriter) msg["Content"] = "from master";
    else             msg["Content"] = "from slave";
    
    // send reply
    send(mref,msg.from());
  }

  return Message::ACCEPT;
}

int IMTestWP::timeout (const HIID &)
{
  return Message::ACCEPT;
}

void IMTestWP::sendMsg()
{
  Message::Ref mref;
  Message &msg = mref <<= new Message(MsgHelloWorld,new DMI::Record);

  msg["Content"] = "Hello, world!";

  publish(mref);
}


};


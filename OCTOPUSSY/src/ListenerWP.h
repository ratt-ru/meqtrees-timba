#ifndef OCTOPUSSY_ListenerWP_h
#define OCTOPUSSY_ListenerWP_h 1

#include <OCTOPUSSY/WorkProcess.h>
    
namespace Octopussy
{

#pragma aid ListenerWP 

//##ModelId=3CA044DE02AB
class ListenerWP : public WorkProcess
{
  public:
      //##ModelId=3CA0451401B9
      ListenerWP ();

    //##ModelId=3DB9369A0073
      ~ListenerWP();


      //##ModelId=3CA045020054
      virtual void init ();


      //##ModelId=3CA0450C0103
      virtual int receive (Message::Ref &mref);


  private:
    //##ModelId=3DB9369B0043
      ListenerWP(const ListenerWP &right);

    //##ModelId=3DB9369B016F
      ListenerWP & operator=(const ListenerWP &right);

};

};
#endif

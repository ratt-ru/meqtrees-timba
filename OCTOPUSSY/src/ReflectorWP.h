#ifndef _OCTOPUSSY_ReflectorWP_h
#define _OCTOPUSSY_ReflectorWP_h 1

#include <OCTOPUSSY/WorkProcess.h>
#include <OCTOPUSSY/AID-OCTOPUSSY.h>
    
#pragma aid ReflectorWP Reflect

namespace Octopussy
{
using namespace DMI;


class ReflectorWP : public WorkProcess
{
  public:
      ReflectorWP (AtomicID wpid = AidReflectorWP);

      ~ReflectorWP();

      virtual void init ();

      virtual bool start ();

      virtual int receive (Message::Ref& mref);

  private:
      ReflectorWP(const ReflectorWP &right);

      ReflectorWP & operator=(const ReflectorWP &right);
};

// Class ReflectorWP 


};
#endif

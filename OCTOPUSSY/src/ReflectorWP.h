#ifndef _OCTOPUSSY_ReflectorWP_h
#define _OCTOPUSSY_ReflectorWP_h 1

#include "OCTOPUSSY/WorkProcess.h"
#include "AID-OCTOPUSSY.h"
    
#pragma aid ReflectorWP Reflect

class ReflectorWP : public WorkProcess
{
  public:
      ReflectorWP (AtomicID wpid = AidReflectorWP);

      ~ReflectorWP();

      virtual void init ();

      virtual bool start ();

      virtual int receive (MessageRef& mref);

  private:
      ReflectorWP(const ReflectorWP &right);

      ReflectorWP & operator=(const ReflectorWP &right);
};

// Class ReflectorWP 


#endif

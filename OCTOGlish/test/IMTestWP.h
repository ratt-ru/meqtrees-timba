#ifndef OctoGlish_IMTestWP_h
#define OctoGlish_IMTestWP_h 1

#include "DMI/DMI.h"

#include "OCTOPUSSY/WorkProcess.h"
#include "OCTOGlish/AID-OCTOGlish.h"

namespace OctoGlish
{
using namespace Octopussy;
    
class IMTestWP : public WorkProcess
{
  public:
      IMTestWP (bool isWriter);

      ~IMTestWP();

      virtual void init ();

      virtual bool start ();

      virtual int receive (Message::Ref& mref);

      virtual int timeout (const HIID &);

      void sendMsg ();

  private:
      IMTestWP(const IMTestWP &right);
      IMTestWP & operator=(const IMTestWP &right);

      bool itsIsWriter;
};

};

#endif

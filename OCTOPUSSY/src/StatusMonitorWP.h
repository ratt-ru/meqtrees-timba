#ifndef _OCTOPUSSY_StatusMonitorWP_h
#define _OCTOPUSSY_StatusMonitorWP_h 1

#include <OCTOPUSSY/WorkProcess.h>
#include <OCTOPUSSY/AID-OCTOPUSSY.h>
#include <stdio.h>
        
#pragma aid StatusMonitorWP Period Process Status Broadcast Request Set

namespace Octopussy
{
using namespace DMI;


class StatusMonitorWP : public WorkProcess
{
  public:
      StatusMonitorWP (int period_ms=2000,AtomicID wpid = AidStatusMonitorWP);

      ~StatusMonitorWP();

      virtual bool start ();
      
      virtual int timeout (const HIID &);

      virtual int receive (Message::Ref& mref);
      
      void setPeriod (int ms);
      
      void setPrefix (const HIID &prefix)
      { prefix_ = prefix; }

  private:
      void makeStatusMessage (Message::Ref &msg);
      
      int period_ms_;
      
      HIID prefix_;
      
      int pagesize_;
      
      StatusMonitorWP(const StatusMonitorWP &right);

      StatusMonitorWP & operator=(const StatusMonitorWP &right);
};

// Class StatusMonitorWP 


};
#endif

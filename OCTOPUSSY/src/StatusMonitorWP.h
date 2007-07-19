//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

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

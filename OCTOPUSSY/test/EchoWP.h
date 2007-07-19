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

#ifndef OCTOPUSSY_EchoWP_h
#define OCTOPUSSY_EchoWP_h 1

#include <DMI/DMI.h>
#include <OCTOPUSSY/LatencyVector.h>
#include <OCTOPUSSY/WorkProcess.h>
#include "AID-Testing.h"

#pragma aidgroup Testing
#pragma aid EchoWP Ping Pong
#pragma aid Reply Timestamp Invert Data Count Process

namespace Octopussy
{
using namespace DMI;

//##ModelId=3C7E498E00D1
class EchoWP : public WorkProcess
{
  public:
      //##ModelId=3C7E49B60327
      EchoWP (int pingcount = 0);

    //##ModelId=3DB936790173
      ~EchoWP();


      //##ModelId=3C7F884A007D
      virtual void init ();

      //##ModelId=3C7E4AC70261
      virtual bool start ();

      //##ModelId=3C7E49AC014C
      virtual int receive (Message::Ref& mref);

      //##ModelId=3C98CB600343
      virtual int timeout (const HIID &);

  protected:
    // Additional Protected Declarations
    //##ModelId=3DB93677029C
      int pcount,blocksize,pipeline,fill;
    //##ModelId=3DB9367703C9
      int process,threads;
  
    //##ModelId=3DB936780095
      long   bytecount,msgcount;
    //##ModelId=3DB936780167
      double ts,timecount;
#ifdef ENABLE_LATENCY_STATS
    //##ModelId=3DB958F202CA
      LatencyVector pinglat,ponglat;
    //##ModelId=3DB93678033E
      int nping,npong;
    //##ModelId=3DB93679005A
      double ping_ts,pong_ts;
#endif
      
    //##ModelId=3DB93679023B
      void stepCounters ( size_t nb,const Timestamp &stamp );
  
    //##ModelId=3DB9367903B8
      void sendPing (int pc);
  private:
    //##ModelId=3DB9367A00E8
      EchoWP(const EchoWP &right);

    //##ModelId=3DB9367A01F6
      EchoWP & operator=(const EchoWP &right);

};

// Class EchoWP 

};
#endif

//#  WorkProcess.h: a work process prototype
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef OCTOPUSSY_WorkProcess_h
#define OCTOPUSSY_WorkProcess_h 1

#include <DMI/Common.h>
#include <DMI/DMI.h>

#include <OCTOPUSSY/WPInterface.h>
#include <OCTOPUSSY/Dispatcher.h>
    
#pragma aid MsgLog LogNormal LogWarning LogError LogFatal LogDebug


//##ModelId=3C8F25430087

class WorkProcess : public WPInterface
{
  public:
      //##ModelId=3C8F25DB014E
      WorkProcess (AtomicID wpc);


      //##ModelId=3C7D285803B0
      void addTimeout (const Timestamp &period, const HIID &id = HIID(), int flags = 0, int priority = Message::PRI_EVENT);

      //##ModelId=3C7D2874023E
      void addInput (int fd, int flags, int priority = Message::PRI_EVENT);

      //##ModelId=3C7DFE520239
      void addSignal (int signum, int flags = 0, int priority = Message::PRI_EVENT);

      //##ModelId=3C7D287F02C6
      bool removeTimeout (const HIID &id);

      //##ModelId=3C7D28A30141
      bool removeInput (int fd, int flags = EV_FDALL);

      //##ModelId=3C7DFE480253
      bool removeSignal (int signum);

      //##ModelId=3C95A89D015E
      void detachMyself ();

      //##ModelId=3C95BA1602D9
      const MsgAddress & attachWP (WPRef &wpref);

      //##ModelId=3C95BA1A02D5
      const MsgAddress & attachWP (WPInterface* wp, int flags);
      
      bool isDetaching () const
      { return detaching_; }

  private:
      bool detaching_;
      
      
    //##ModelId=3DB937290303
      WorkProcess();

    //##ModelId=3DB9372903AD
      WorkProcess(const WorkProcess &right);

    //##ModelId=3DB9372A0123
      WorkProcess & operator=(const WorkProcess &right);

};

// Class WorkProcess 


#endif

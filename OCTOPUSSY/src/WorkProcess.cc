//  WorkProcess.cc: implementation of WorkProcess
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#include <OCTOPUSSY/Dispatcher.h>
#include <OCTOPUSSY/AID-OCTOPUSSY.h>
#include <OCTOPUSSY/WorkProcess.h>

WorkProcess::WorkProcess (AtomicID wpc)
  : WPInterface(wpc),detaching_(false)
{
}

//##ModelId=3C7D285803B0
void WorkProcess::addTimeout (const Timestamp &period, const HIID &id, int flags, int priority)
{
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->addTimeout(this,period,id,flags,priority);
}

//##ModelId=3C7D2874023E
void WorkProcess::addInput (int fd, int flags, int priority)
{
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->addInput(this,fd,flags,priority);
}

//##ModelId=3C7DFE520239
void WorkProcess::addSignal (int signum, int flags, int priority)
{
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->addSignal(this,signum,flags,priority);
}

//##ModelId=3C7D287F02C6
bool WorkProcess::removeTimeout (const HIID &id)
{
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->removeTimeout(this,id);
}

//##ModelId=3C7D28A30141
bool WorkProcess::removeInput (int fd, int flags)
{
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->removeInput(this,fd,flags);
}

//##ModelId=3C7DFE480253
bool WorkProcess::removeSignal (int signum)
{
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->removeSignal(this,signum);
}

//##ModelId=3C95A89D015E
void WorkProcess::detachMyself ()
{
  if( !detaching_ )
    dsp()->detach(this,True);
  detaching_ = true;
}

//##ModelId=3C95BA1602D9
const MsgAddress & WorkProcess::attachWP (WPRef &wpref)
{
  return dsp()->attach(wpref);
}

//##ModelId=3C95BA1A02D5
const MsgAddress & WorkProcess::attachWP (WPInterface* wp, int flags)
{
  return dsp()->attach(wp,flags);
}

// Additional Declarations




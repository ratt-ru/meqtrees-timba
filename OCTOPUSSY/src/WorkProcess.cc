//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7B7F3000C5.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7B7F3000C5.cm

//## begin module%3C7B7F3000C5.cp preserve=no
//## end module%3C7B7F3000C5.cp

//## Module: WorkProcess%3C7B7F3000C5; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\WorkProcess.cc

//## begin module%3C7B7F3000C5.additionalIncludes preserve=no
//## end module%3C7B7F3000C5.additionalIncludes

//## begin module%3C7B7F3000C5.includes preserve=yes
#include "OCTOPUSSY/Dispatcher.h"
#include "OCTOPUSSY/AID-OCTOPUSSY.h"
//## end module%3C7B7F3000C5.includes

// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
//## begin module%3C7B7F3000C5.declarations preserve=no
//## end module%3C7B7F3000C5.declarations

//## begin module%3C7B7F3000C5.additionalDeclarations preserve=yes
//## end module%3C7B7F3000C5.additionalDeclarations


// Class WorkProcess 

WorkProcess::WorkProcess (AtomicID wpc)
  //## begin WorkProcess::WorkProcess%3C8F25DB014E.hasinit preserve=no
  //## end WorkProcess::WorkProcess%3C8F25DB014E.hasinit
  //## begin WorkProcess::WorkProcess%3C8F25DB014E.initialization preserve=yes
  : WPInterface(wpc)
  //## end WorkProcess::WorkProcess%3C8F25DB014E.initialization
{
  //## begin WorkProcess::WorkProcess%3C8F25DB014E.body preserve=yes
  //## end WorkProcess::WorkProcess%3C8F25DB014E.body
}



//## Other Operations (implementation)
void WorkProcess::addTimeout (const Timestamp &period, const HIID &id, int flags, int priority)
{
  //## begin WorkProcess::addTimeout%3C7D285803B0.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->addTimeout(this,period,id,flags,priority);
  //## end WorkProcess::addTimeout%3C7D285803B0.body
}

void WorkProcess::addInput (int fd, int flags, int priority)
{
  //## begin WorkProcess::addInput%3C7D2874023E.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->addInput(this,fd,flags,priority);
  //## end WorkProcess::addInput%3C7D2874023E.body
}

void WorkProcess::addSignal (int signum, int flags, volatile int* counter, int priority)
{
  //## begin WorkProcess::addSignal%3C7DFE520239.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->addSignal(this,signum,flags,counter,priority);
  //## end WorkProcess::addSignal%3C7DFE520239.body
}

bool WorkProcess::removeTimeout (const HIID &id)
{
  //## begin WorkProcess::removeTimeout%3C7D287F02C6.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->removeTimeout(this,id);
  //## end WorkProcess::removeTimeout%3C7D287F02C6.body
}

bool WorkProcess::removeInput (int fd, int flags)
{
  //## begin WorkProcess::removeInput%3C7D28A30141.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->removeInput(this,fd,flags);
  //## end WorkProcess::removeInput%3C7D28A30141.body
}

bool WorkProcess::removeSignal (int signum)
{
  //## begin WorkProcess::removeSignal%3C7DFE480253.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  return dsp()->removeSignal(this,signum);
  //## end WorkProcess::removeSignal%3C7DFE480253.body
}

void WorkProcess::detachMyself ()
{
  //## begin WorkProcess::detachMyself%3C95A89D015E.body preserve=yes
  dsp()->detach(this,True);
  //## end WorkProcess::detachMyself%3C95A89D015E.body
}

const MsgAddress & WorkProcess::attachWP (WPRef &wpref)
{
  //## begin WorkProcess::attachWP%3C95BA1602D9.body preserve=yes
  return dsp()->attach(wpref);
  //## end WorkProcess::attachWP%3C95BA1602D9.body
}

const MsgAddress & WorkProcess::attachWP (WPInterface* wp, int flags)
{
  //## begin WorkProcess::attachWP%3C95BA1A02D5.body preserve=yes
  return dsp()->attach(wp,flags);
  //## end WorkProcess::attachWP%3C95BA1A02D5.body
}

// Additional Declarations
  //## begin WorkProcess%3C8F25430087.declarations preserve=yes
  //## end WorkProcess%3C8F25430087.declarations

//## begin module%3C7B7F3000C5.epilog preserve=yes
//## end module%3C7B7F3000C5.epilog


// Detached code regions:
#if 0
//## begin WorkProcess::lprintf%3CA0738D007F.body preserve=yes
  if( level > logLevel() )
    return;
  // create the string
  char str[1024];
  va_list(ap);
  va_start(ap,format);
  vsnprintf(str,sizeof(str),format,ap);
  va_end(ap);
  log(str,level,type);
//## end WorkProcess::lprintf%3CA0738D007F.body

//## begin WorkProcess::lprintf%3CA0739F0247.body preserve=yes
  if( level > logLevel() )
    return;
  char str[1024];
  va_list(ap);
  va_start(ap,format);
  vsnprintf(str,sizeof(str),format,ap);
  va_end(ap);
  log(str,level,LogNormal);
//## end WorkProcess::lprintf%3CA0739F0247.body

//## begin WorkProcess::start%3C9216B701CA.body preserve=yes
  WPInterface::start();
//## end WorkProcess::start%3C9216B701CA.body

//## begin WorkProcess::stop%3C9216C10015.body preserve=yes
  WPInterface::stop();
//## end WorkProcess::stop%3C9216C10015.body

//## begin WorkProcess::send%3C7CB9E802CF.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  // if not writable, privatize for writing (but not deeply)
  if( !msg.isWritable() )
    msg.privatize(DMI::WRITE);
  msg().setFrom(address());
  msg().setState(state());
  dprintf(2)("send [%s] to %s\n",msg->sdebug(1).c_str(),to.toString().c_str());
  // substitute 'Local' for actual addresses
  if( to.host() == AidLocal )
    to.host() = address().host();
  if( to.process() == AidLocal )
    to.process() = address().process();
  return dsp()->send(msg,to); 
//## end WorkProcess::send%3C7CB9E802CF.body

//## begin WorkProcess::publish%3C7CB9EB01CF.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  // if not writable, privatize for writing (but not deeply)
  if( !msg.isWritable() )
    msg.privatize(DMI::WRITE);
  msg().setFrom(address());
  msg().setState(state());
  dprintf(2)("publish [%s] scope %d\n",msg->sdebug(1).c_str(),scope);
  AtomicID host = (scope < Message::GLOBAL) ? dsp()->hostId() : AidAny;
  AtomicID process = (scope < Message::HOST) ? dsp()->processId() : AidAny;
  return dsp()->send(msg,MsgAddress(AidPublish,AidPublish,process,host));
//## end WorkProcess::publish%3C7CB9EB01CF.body

//## begin WorkProcess::subscribe%3C7CB9B70120.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
   dprintf(2)("subscribing to %s\n",id.toString().c_str());
  subscriptions().add(id);
  return True;
//## end WorkProcess::subscribe%3C7CB9B70120.body

//## begin WorkProcess::unsubscribe%3C7CB9C50365.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  dprintf(2)("unsubscribing from %s\n",id.toString().c_str());
  subscriptions().remove(id);
  return True;
//## end WorkProcess::unsubscribe%3C7CB9C50365.body

#endif

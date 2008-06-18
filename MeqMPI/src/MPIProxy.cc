#include <MeqMPI/MeqMPI.h>
#include <MeqMPI/MPIProxy.h>
#include <MeqMPI/AID-MeqMPI.h>


namespace Meq

{

void MPIProxy::init (NodeFace *parent,bool stepparent,int init_index)
{ 
  Node::init(parent,stepparent,init_index);
  // get remote processor number
  remote_proc_ = wstate()[AidRemote|AidProc].as<int>(0);
  // send init message and wait for reply
  MeqMPI::ReplyEndpoint reply;
  MeqMPI::HdrNodeInit header = { nodeIndex(),parent->nodeIndex(),stepparent,init_index,&reply };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_INIT,remote_proc_,header);
  reply.await();
}


void MPIProxy::getSyncState (DMI::Record::Ref &ref) 
{
  // send message and wait for reply
  MeqMPI::ReplyEndpoint reply;
  MeqMPI::HdrNodeOperation header = { nodeIndex(),0,&reply };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_GET_STATE,remote_proc_,header);
  ObjRef objref;
  reply.await(objref);
  ref = objref;
}
    
int MPIProxy::execute (CountedRef<Result> &resref, const Request &req) throw()
{
  // send message and wait for reply
  MeqMPI::ReplyEndpoint reply;
  MeqMPI::HdrNodeOperation header = { nodeIndex(),0,&reply };
  ObjRef objref(req);
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_EXECUTE,remote_proc_,header,objref);
  int retcode = reply.await(objref);
  if( !objref.valid() )
  {
    Result &res = resref <<= new Result(1);
    VellSet &vs = res.setNewVellSet(0);
    MakeFailVellSet(vs,"remote MPI node did not return a Result object");
    retcode |= RES_FAIL;
  }
  else
    resref = objref;
  return retcode;
}

void MPIProxy::setState (DMI::Record::Ref &rec)
{
  MeqMPI::HdrNodeOperation header = { nodeIndex(),0,0 };
  ObjRef objref(rec);
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_SET_STATE,remote_proc_,header,objref);
}

int MPIProxy::processCommand (CountedRef<Result> &resref,
                                      const HIID &command,
                                      DMI::Record::Ref &args,
                                      const RequestId &rqid,
                                      int verbosity)
{
  // send message and wait for reply
  MeqMPI::ReplyEndpoint reply;
  MeqMPI::HdrNodeOperation header = { nodeIndex(),0,&reply };
  DMI::Record *prec = new DMI::Record;
  ObjRef objref(prec);
  (*prec)[AidCommand] = command;
  (*prec)[AidArgs] = args;
  (*prec)[AidRequest|AidId] = rqid;
  (*prec)[AidVerbose] = verbosity;
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_PROCESS_COMMAND,remote_proc_,header,objref);
  int retcode = reply.await(objref);
  resref = objref;
  return retcode;
}

void MPIProxy::clearCache (bool recursive) throw()
{
  MeqMPI::HdrNodeOperation header = { nodeIndex(),recursive,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_CLEAR_CACHE,remote_proc_,header);
}

void MPIProxy::holdCache (bool hold) throw()
{
  MeqMPI::HdrNodeOperation header = { nodeIndex(),hold,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_HOLD_CACHE,remote_proc_,header);
}
    
void MPIProxy::propagateStateDependency ()
{
  MeqMPI::HdrNodeOperation header = { nodeIndex(),0,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_PROPAGATE_STATE_DEP,remote_proc_,header);
}

void MPIProxy::publishParentalStatus ()
{
  MeqMPI::HdrNodeOperation header = { nodeIndex(),0,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_PUBLISH_PARENTAL_STAT,remote_proc_,header);
}

void MPIProxy::setBreakpoint (int bpmask,bool single_shot)
{
  MeqMPI::HdrNodeBreakpoint header = { nodeIndex(),bpmask,single_shot,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_SET_BREAKPOINT,remote_proc_,header);
}

void MPIProxy::clearBreakpoint (int bpmask,bool single_shot)
{
  MeqMPI::HdrNodeBreakpoint header = { nodeIndex(),bpmask,single_shot,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_CLEAR_BREAKPOINT,remote_proc_,header);
}

void MPIProxy::setPublishingLevel (int level)
{
  MeqMPI::HdrNodeOperation header = { nodeIndex(),level,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_SET_PUBLISHING_LEVEL,remote_proc_,header);
}


}

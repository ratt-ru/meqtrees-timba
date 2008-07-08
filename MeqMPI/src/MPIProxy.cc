#include <MeqMPI/MeqMPI.h>
#include <MeqMPI/MPIProxy.h>
#include <MeqMPI/AID-MeqMPI.h>
#include <MEQ/Forest.h>


namespace Meq

{

InitDebugContext(MPIProxy,"MPIProxy");

MPIProxy::MPIProxy ()
: Node()
{
  num_local_parents_ = 0;
}

MPIProxy::~MPIProxy ()
{
}

void MPIProxy::init ()
{ 
  // init the node
  Node::init();
  dprintf(2)("init");
  // get remote processor number
  remote_proc_ = wstate()[AidRemote|AidProc].as<int>(0);
  // count the number of local (i.e. non-MPIProxy) parents. 
  // We need to know since we only hold cache for local parents
  num_local_parents_ = 0;
  for( int i=0; i<numParents(); i++ )
    if( getParent(i).objectType() != TpMeqMPIProxy )
      num_local_parents_++;
  dprintf(2)("we have %d local parents\n",num_local_parents_);
  // rather clumsy way to propagate this into the Node mechanism, but there you go...
  DMI::Record::Ref rec(new DMI::Record);
  rec()[FCacheNumActiveParents] = num_local_parents_;
  Node::setStateImpl(rec,false);
//  // send init message and wait for reply
//  MeqMPI::ReplyEndpoint reply;
//  MeqMPI::HdrNodeInit header = { nodeIndex(),parent?parent->nodeIndex():0,stepparent,init_index,&reply };
//  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_INIT,remote_proc_,header);
//  reply.await();
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
  Thread::Mutex::Lock lock(execCond());
  // if node is already executing, then wait for it to finish, and meanwhile
  // mark our thread as blocked
  if( executing_ )
  {
    MTPool::Brigade::markThreadAsBlocked(name());
    while( executing_ )
      execCond().wait();
    MTPool::Brigade::markThreadAsUnblocked(name());
  }
  executing_ = true;
  
  if( forest().abortFlag() )
    return exitAbort(RES_ABORT);
  
  // check the cache, return on match (cache will be cleared on mismatch)
  int retcode;
  if( getCachedResult(retcode,resref,req) )
  {
    cdebug(3)<<"  cache hit, returning cached code "<<ssprintf("0x%x",retcode)<<" and result:"<<endl<<
                "    "<<resref->sdebug(DebugLevel-1,"    ")<<endl;
    return exitExecute(retcode);
  }
  
  lock.release();
  
  // send message and wait for reply
  MeqMPI::ReplyEndpoint reply;
  MeqMPI::HdrNodeOperation header = { nodeIndex(),0,&reply };
  ObjRef objref(req);
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_EXECUTE,remote_proc_,header,objref);
  
  // wait for reply, while marking ourselves blocked
  MTPool::Brigade::markThreadAsBlocked(name());
  retcode = reply.await(objref);
  MTPool::Brigade::markThreadAsUnblocked(name());
  
  // dispence with reply
  if( !objref.valid() )
  {
    Result &res = resref <<= new Result(1);
    VellSet &vs = res.setNewVellSet(0);
    MakeFailVellSet(vs,"remote MPI node did not return a Result object");
    retcode |= RES_FAIL;
  }
  else
    resref = objref;
  
  retcode = cacheResult(resref,req,retcode);
  
  return exitExecute(retcode);
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
  Node::clearCache(recursive);
  MeqMPI::HdrNodeOperation header = { nodeIndex(),recursive,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_CLEAR_CACHE,remote_proc_,header);
}

void MPIProxy::holdCache (bool hold) throw()
{
  Node::holdCache(hold);
//// NB: for now, do not send message across MPI. Let remote
//// nodes hold their caches, but we don't want the message overhead
//  MeqMPI::HdrNodeOperation header = { nodeIndex(),hold,0 };
//  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_HOLD_CACHE,remote_proc_,header);
}
    
void MPIProxy::propagateStateDependency ()
{
  Node::propagateStateDependency();
  MeqMPI::HdrNodeOperation header = { nodeIndex(),0,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_PROPAGATE_STATE_DEP,remote_proc_,header);
}

void MPIProxy::publishParentalStatus ()
{
  Node::publishParentalStatus();
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
  Node::setPublishingLevel(level);
  MeqMPI::HdrNodeOperation header = { nodeIndex(),level,0 };
  MeqMPI::self->postCommand(MeqMPI::TAG_NODE_SET_PUBLISHING_LEVEL,remote_proc_,header);
}


}

#include "config.h"
#ifdef HAVE_MPI

#include <TimBase/Thread.h>
#include <TimBase/Debug.h>
#include <DMI/Record.h>
#include <DMI/List.h>
#include <MeqMPI/AID-MeqMPI.h>
#include <MeqMPI/MeqMPI.h>
#include <MEQ/Forest.h>
#include <MeqMPI/TID-MeqMPI.h>

namespace Meq
{

// processes an INIT message
void MeqMPI::procInit (int source,const char *msgbuf,int msgsize)
{
  FailWhen(!comm_rank(),"INIT received at main server");
  // decode the message
  ObjRef ref;
  HdrReplyExpected header;
  decodeMessage(ref,&header,sizeof(header),msgbuf,msgsize);
  const DMI::Record &rec = ref.as<DMI::Record>();
  // init debug levels
  std::vector<string> argv_vec;
  rec["Argv"].get_vector(argv_vec);
  int argc = argv_vec.size();
  const char *argv[argc];
  for( int i=0; i<argc; i++ )
    argv[i] = argv_vec[i].c_str();
  Debug::initLevels(argc,argv);
  // init multithreading
  int mt = rec["mt"].as<int>();
  if( mt<1 )
    mt = 1;
  if( !MTPool::enabled() )
    MTPool::start(mt*2,mt);
  // post a reply
  if( header.endpoint )
    postReply(source,header.endpoint);
}


// processes a CREATE_NODES message
void MeqMPI::procCreateNodes (int source,const char *msgbuf,int msgsize)
{
  FailWhen(!comm_rank(),"CREATE_NODES received at main server");
  // decode the message
  ObjRef ref;
  HdrReplyExpected header;
  decodeMessage(ref,&header,sizeof(header),msgbuf,msgsize);
  // create nodes
  DMI::Record *prec = new DMI::Record;
  ObjRef out(prec);
  forest().clear();
  DMI::List &batch = ref.as<DMI::List>();
  cdebug(2)<<"batch-creating nodes"<<endl;
  int nn = 0;
  DMI::List::iterator iter;
  for( iter = batch.begin(); iter != batch.end(); iter++ )
  {
    DMI::Record::Ref recref(*iter);
    iter->detach();
    int nodeindex;
    try
    {
      forest().create(nodeindex,recref);
    }
    catch( std::exception &exc )
    {
      postError(exc);
    }
    nn++;
  }
  cdebug(2)<<"batch-created "<<nn<<" nodes"<<endl;
  forest().initAll();
  cdebug(2)<<"initialized "<<nn<<" nodes"<<endl;
  // form a response message
  (*prec)[AidMessage] = Debug::ssprintf("created %d nodes on P%d",nn,comm_rank());
  // post a reply
  postReply(source,header.endpoint,nn,out);
}

int MeqMPI::getNodeList (DMI::Record &list,int content,Meq::Forest &forest)
{
  Thread::Mutex::Lock lock(forest.forestMutex());
  int num = 0;
  // count all valid, local nodes
  for( int i=1; i<=forest.maxNodeIndex(); i++ )
    if( forest.valid(i) && forest.get(i).objectType() != TpMeqMPIProxy )
      num++;
  // create lists (arrays) for all known content
  DMI::Vec *lni=0,*lname=0,*lclass=0,*lstate=0,*lrqid=0,*lprof=0,*lcache=0;
  DMI::List *lchildren=0,*lstepchildren=0;
  if( content&Forest::NL_NODEINDEX )
    list[AidNodeIndex] <<= lni = new DMI::Vec(Tpint,num);
  if( content&Forest::NL_NAME )
    list[AidName] <<= lname = new DMI::Vec(Tpstring,num);
  if( content&Forest::NL_CLASS )
    list[AidClass] <<= lclass = new DMI::Vec(Tpstring,num);
  if( content&Forest::NL_CHILDREN )
  {
    list[AidChildren] <<= lchildren = new DMI::List;
    list[AidStep|AidChildren] <<= lstepchildren = new DMI::List;
  }
  if( content&Forest::NL_CONTROL_STATUS )
  {
    list[FControlStatus] <<= lstate = new DMI::Vec(Tpint,num);
    list[FRequestId] <<= lrqid = new DMI::Vec(TpDMIHIID,num);
  }
  if( content&Forest::NL_PROFILING_STATS )
  {
    list[FProfilingStats] <<= lprof = new DMI::Vec(TpDMIRecord,num);
    list[FCacheStats] <<= lcache = new DMI::Vec(TpDMIRecord,num);
  }
  int i0 = 0;
  // now loop over all nodes
  for( int i=1; i<=forest.maxNodeIndex(); i++ )
    if( forest.valid(i) )
    {
      NodeFace &node = forest.get(i);
      // skip all MPIProxies -- their state is obtained separately
      if( node.objectType() == TpMeqMPIProxy )
        continue;
      if( lni )
        (*lni)[i0] = i;
      if( lname )
        (*lname)[i0] = node.name();
      if( lclass )
        (*lclass)[i0] = node.className();
      Node *pnode = dynamic_cast<Node*>(&node);
      if( pnode )
      {
        if( lstate )
          (*lstate)[i0] = pnode->getControlStatus();
        if( lrqid )
          (*lrqid)[i0] = pnode->currentRequestId();
      }
      DMI::Record::Ref nodestate;
      if( lchildren )
      {
        node.getState(nodestate);
        DMI::Record::Hook hook(*nodestate,FChildren);
        if( hook.exists() )
          lchildren->addBack(hook.ref(true));
        else
          lchildren->addBack(new DMI::List);
        DMI::Record::Hook hook1(*nodestate,FStepChildren);
        if( hook1.exists() )
          lstepchildren->addBack(hook1.ref(true));
        else
          lstepchildren->addBack(new DMI::List);
      }
      if( lprof )
      {
        node.getSyncState(nodestate);
        (*lprof)[i0] = (*nodestate)[FProfilingStats].ref(true);
        (*lcache)[i0] = (*nodestate)[FCacheStats].ref(true);
      }
      i0++;
    }
  FailWhen1(i0<num,"forest inconsistency: too few valid nodes found");
  return num;
}


// processes a GET_NODE_LIST message
void MeqMPI::procGetNodeList (int source,const char *msgbuf,int msgsize)
{
  FailWhen(!comm_rank(),"GET_NODE_LIST received at main server");
  // decode the message
  ObjRef ref;
  HdrGetNodeList header;
  decodeMessage(ref,&header,sizeof(header),msgbuf,msgsize);
  // create node list
  DMI::Record * prec = new DMI::Record;
  ObjRef out(prec);
  int retcode = getNodeList(*prec,header.content,forest());
  // post a reply
  postReply(source,header.endpoint,retcode,out);
}

// processes a SET_FOREST_STATE message
void MeqMPI::procSetForestState (int source,const char *msgbuf,int msgsize)
{
  FailWhen(!comm_rank(),"SET_FOREST_STATE received at main server");
  HdrReplyExpected hdr;
  ObjRef ref;
  decodeMessage(ref,&hdr,sizeof(hdr),msgbuf,msgsize);
  // set the state
  DMI::Record::Ref recref;
  recref.xfer(ref);
  forest().setState(recref);
  if( hdr.endpoint )
    postReply(source,hdr.endpoint);
}

// processes an EVENT message. Only meant to be received at main server
void MeqMPI::procEvent  (int source,const char *msgbuf,int msgsize)
{
  FailWhen(comm_rank(),"EVENT received at a subserver");
  // decode the message
  HdrReplyExpected hdr;
  ObjRef ref;
  decodeMessage(ref,&hdr,sizeof(hdr),msgbuf,msgsize);
  // get event out of record
  const DMI::Record &rec = ref.as<DMI::Record>();
  forest().postEvent(rec[AidType].as<HIID>(),rec[AidData].ref());
  if( hdr.endpoint )
    postReply(source,hdr.endpoint);
}

// processes a NODE_GET_STATE message
void MeqMPI::procNodeGetState (int source,const char *msgbuf,int msgsize)
{
  // decode the message
  ObjRef ref;
  HdrNodeOperation header;
  decodeMessage(ref,&header,sizeof(header),msgbuf,msgsize);
  NodeFace &node = forest().get(header.nodeindex);
  DMI::Record::Ref recref;
  node.getSyncState(recref);
  ref = recref;
  // post a reply
  postReply(source,header.endpoint,0,ref);
}

// processes a NODE_SET_STATE message
void MeqMPI::procNodeSetState (int source,const char *msgbuf,int msgsize)
{
  // decode the message
  ObjRef ref;
  HdrNodeOperation header;
  decodeMessage(ref,&header,sizeof(header),msgbuf,msgsize);
  NodeFace &node = forest().get(header.nodeindex);
  DMI::Record::Ref recref;
  recref = ref;
  node.setState(recref);
  if( header.endpoint )
    postReply(source,header.endpoint);
}

// An MpiExecWorkOrder makes an execute() call on a node
class MpiExecWorkOrder : public MTPool::AbstractWorkOrder
{
  public:
    MpiExecWorkOrder (NodeFace &node,const Request &req,int depth,
                      MeqMPI &mpi,int dest,MeqMPI::ReplyEndpoint *ep)
    : noderef(node,DMI::SHARED),reqref(req),
    meqmpi(mpi),reqdepth(depth),reply_dest(dest),endpoint(ep)
    {}

    virtual void execute (MTPool::Brigade &brigade)      // runs the work order.
    {
      Result::Ref resref;
      int retcode = Node::RES_FAIL;
      try
      {
        NodeFace &node = noderef();
        cdebug1(1)<<brigade.sdebug(1)+" executing request "+reqref->id().toString('.')+" on node "+node.name()+"\n";
        retcode = node.execute(resref,*reqref,reqdepth);
        cdebug1(1)<<brigade.sdebug(1)+" finished request "+reqref->id().toString('.')+" on node "+node.name()+"\n";
      }
      catch( std::exception &exc )
      {
        string str = Debug::ssprintf("caught exception while executing a node: %s",exc.what());
        cdebug(0)<<str<<endl;
        DMI::ExceptionList exclist(exc);
        exclist.add(LOFAR::Exception(str));
        meqmpi.postError(exclist);
      }
      catch(...)
      {
        string str = "caught unknown exception while executing a node";
        cdebug(0)<<str<<endl;
        meqmpi.postError(str);
      }
      // notify client of completed order
      if( endpoint )
      {
        ObjRef objref;
        if( resref.valid() )
        {
          objref = resref;
          resref.detach();
        }
        meqmpi.postReply(reply_dest,endpoint,retcode,objref);
      }
    }

    virtual ~MpiExecWorkOrder() {};

    NodeFace::Ref noderef;
    Request::Ref  reqref;
    MeqMPI & meqmpi;
    int reqdepth;
    int reply_dest;
    MeqMPI::ReplyEndpoint *endpoint;
};

// processes a NODE_EXECUTE message
void MeqMPI::procNodeExecute (int source,const char *msgbuf,int msgsize)
{
  // decode the message
  ObjRef ref;
  HdrNodeOperation header;
  decodeMessage(ref,&header,sizeof(header),msgbuf,msgsize);
  NodeFace &node = forest().get(header.nodeindex);
  cdebug(2)<<"enqueueing execute() request on node "<<node.name()<<endl;
  // enqueue a workorder and wake up worker thread
  Thread::Mutex::Lock lock(MTPool::brigade().cond());
  MTPool::brigade().placeWorkOrder(new MpiExecWorkOrder(node,ref.as<Request>(),header.arg,*this,source,header.endpoint));
  MTPool::brigade().awakenWorker(true);
}

// processes a NODE_SET_PUBLISHING_LEVEL message
void MeqMPI::procNodeSetPublishingLevel (int source,const char *msgbuf,int msgsize)
{
  // decode the message
  ObjRef ref;
  HdrNodeOperation header;
  decodeMessage(ref,&header,sizeof(header),msgbuf,msgsize);
  NodeFace &node = forest().get(header.nodeindex);
  node.setPublishingLevel(header.arg);
  // post a reply
  if( header.endpoint )
    postReply(source,header.endpoint);
}




}

#endif // HAVE_MPI

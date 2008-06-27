#include "config.h"
#ifdef HAVE_MPI

#include <TimBase/Thread.h>
#include <TimBase/Debug.h>
#include <DMI/DynamicTypeManager.h>
#include <DMI/Record.h>
#include <DMI/Exception.h>
#include <MeqMPI/AID-MeqMPI.h>
#include <MeqMPI/MeqMPI.h>
#include <MEQ/Forest.h>
#include <iostream>

namespace Meq
{

InitDebugContext(MeqMPI,"MeqMPI");

MeqMPI * MeqMPI::self = 0;

static char * tag_strings[MeqMPI::TAG_LAST_TAG];

MeqMPI::MeqMPI (int argc,const char *argv[])
{
  if( self )
    Throw("Attempting to create a second MeqMPI, which is a singleton");
  self = this;
  forest_ = 0;
  comm_thread_ = 0;
  comm_thread_running_ = false;
  msgbuf_ = 0;
  msgbuf_size_ = 0;
  meq_mpi_communicator_ = MPI_COMM_WORLD;
  
  MPI_Comm_size(meq_mpi_communicator_,&mpi_num_processors_);
  MPI_Comm_rank(meq_mpi_communicator_,&mpi_our_processor_);
  dprintf(0)("MPI communicator: rank %d, size %d\n",comm_rank(),comm_size());
  
  // init tag strings
  memset(tag_strings,0,sizeof(tag_strings));
  tag_strings[TAG_INIT] = "INIT";
  tag_strings[TAG_HALT] = "HALT";
  tag_strings[TAG_REPLY] = "REPLY";
  tag_strings[TAG_CREATE_NODES] = "CREATE_NODES";
  tag_strings[TAG_GET_NODE_LIST] = "GET_NODE_LIST";
  tag_strings[TAG_SET_FOREST_STATE] = "SET_FOREST_STATE";
  tag_strings[TAG_EVENT] = "EVENT";
  tag_strings[TAG_NODE_INIT] = "NODE_INIT";
  tag_strings[TAG_NODE_GET_STATE] = "NODE_GET_STATE";
  tag_strings[TAG_NODE_SET_STATE] = "NODE_SET_STATE";
  tag_strings[TAG_NODE_EXECUTE] = "NODE_EXECUTE";
  tag_strings[TAG_NODE_PROCESS_COMMAND] = "NODE_PROCESS_COMMAND";
  tag_strings[TAG_NODE_CLEAR_CACHE] = "NODE_CLEAR_CACHE";
  tag_strings[TAG_NODE_HOLD_CACHE] = "NODE_HOLD_CACHE";
  tag_strings[TAG_NODE_PROPAGATE_STATE_DEP] = "NODE_PROPAGATE_STATE_DEP";
  tag_strings[TAG_NODE_PUBLISH_PARENTAL_STAT] = "NODE_PUBLISH_PARENTAL_STAT";
  tag_strings[TAG_NODE_SET_BREAKPOINT] = "NODE_SET_BREAKPOINT";
  tag_strings[TAG_NODE_CLEAR_BREAKPOINT] = "NODE_CLEAR_BREAKPOINT";
  tag_strings[TAG_NODE_SET_PUBLISHING_LEVEL] = "NODE_SET_PUBLISHING_LEVEL";
  
  MPI_Status status;
  // Now, send an init message.
  // The rank-0 process sends an init to everyone else
  if( comm_rank() == 0 )
  {
    DMI::Record &rec = *new DMI::Record;
    ObjRef ref(&rec);
    rec["Argv"] <<= new DMI::Vec(Tpstring,argc);
    for( int i=0; i<argc; i++ )
      rec["Argv"][i] = string(argv[i]);
    rec["mt"] = Meq::MTPool::num_threads();
    // post the message to all rank>0 processes
    postCommand(TAG_INIT,-1,ref);
  }
}

std::string MeqMPI::tagToString (int tag)
{
  if( tag<0 || tag>=TAG_LAST_TAG )
    return "(invalid)";
  if( !tag_strings[tag] )
    return "(unknown)";
  return tag_strings[tag];
}

void MeqMPI::attachForest (Meq::Forest &forest)
{
  forest_ = &forest;
  // on rank>0 machines, attach a postEvent() callback to the forest
  if( comm_rank() > 0 )
    forest.setEventCallback(postForestEvent_static);
}

void MeqMPI::postForestEvent_static (const HIID &type,const ObjRef &data)
{
  self->postEvent(type,data);
}

// initializes MeqMPI layer, launches the communicator thread
Thread::ThrID MeqMPI::initialize ()
{
  FailWhen(comm_thread_.id()!=0,"MPI comm thread already running");
  // launch communicator
  comm_thread_ = Thread::create(commThreadEntrypoint,this);
  dprintf(1)("started MPI comm thread %x\n",int(comm_thread_.id()));
  return comm_thread_;
}

void MeqMPI::stopCommThread ()
{
  // since the comm thread wakes up often to poll, all we need is to set a flag here
  comm_thread_running_ = false;
  if( comm_thread_ )
  {
    dprintf(1)("rejoining MPI comm thread...\n");
    comm_thread_.join();
    dprintf(1)("rejoined MPI comm thread\n");
    comm_thread_ = 0;
  }
}

void MeqMPI::rejoinCommThread ()
{
  if( comm_thread_ )
  {
    dprintf(1)("rejoining MPI comm thread...\n");
    comm_thread_.join();
    dprintf(1)("rejoined MPI comm thread\n");
    comm_thread_ = 0;
  }
}

// helper function: ensures that the given buffer is big enough for the given message
// size, reallocates if an increase is needed
void MeqMPI::ensureBuffer (char * &buf,size_t &bufsize,size_t msgsize)
{
  // if buffer is not big enough, reallocate
  if( bufsize < msgsize )
  {
    delete [] buf;
    bufsize = (msgsize/DEFAULT_BUFFER_INCREMENT+1)*DEFAULT_BUFFER_INCREMENT;
    buf = new char[bufsize];
  }
}


void * MeqMPI::commThreadEntrypoint (void *ptr)
{
  return static_cast<MeqMPI*>(ptr)->runCommThread();
}


// main loop of communicator thread
void * MeqMPI::runCommThread ()
{
  // preallocate default buffer
  msgbuf_ = new char[msgbuf_size_ = DEFAULT_BUFFER_SIZE];
  
  comm_thread_running_ = true;
  
  while( comm_thread_running_ )
  {
    Thread::Mutex::Lock lock;
    // probe for an MPI message -- nonblocking
    MPI_Status status;
    int rcvflag;
    rcvflag = 0;
    int retcode = MPI_Iprobe(MPI_ANY_SOURCE,MPI_ANY_TAG,meq_mpi_communicator_,&rcvflag,&status);
    dprintf(5)("MPI_Iprobe: return value %d, source %d, tag %d (%s), error %d\n",
              retcode,status.MPI_SOURCE,status.MPI_TAG,tagToString(status.MPI_TAG).c_str(),status.MPI_ERROR);
    // handle errors
    if( retcode != MPI_SUCCESS )
    {
      break;
    }
    if( rcvflag )
    {
      lock.release();  // release the sendqueue
      // obtain the message size
      int msgsize;
      retcode = MPI_Get_count(&status,MPI_BYTE,&msgsize);
      if( retcode != MPI_SUCCESS )
      {
        break;
      }
      dprintf(3)("expected messsage size is %d\n",msgsize);
      // ensure we have a message buffer long enough
      ensureBuffer(msgbuf_,msgbuf_size_,msgsize);
      // receive the message
      retcode = MPI_Recv(msgbuf_,msgbuf_size_,MPI_BYTE,MPI_ANY_SOURCE,MPI_ANY_TAG,meq_mpi_communicator_,&status);
      if( retcode != MPI_SUCCESS )
      {
        break;
      }
      dprintf(3)("MPI_Recv: return value %d, source %d, tag %d (%s), error %d, size %d\n",
                retcode,status.MPI_SOURCE,status.MPI_TAG,tagToString(status.MPI_TAG).c_str(),
                 status.MPI_ERROR,msgsize);
      // dispense with message according to tag
      try
      {
        switch( status.MPI_TAG )
        {
          case TAG_INIT:
            procInit(status.MPI_SOURCE,msgbuf_,msgsize);
            break;
        
          case TAG_HALT:
            comm_thread_running_ = false;
            dprintf(3)("HALT command received, exiting thread\n");
            continue;
        
          case TAG_CREATE_NODES:
            procCreateNodes(status.MPI_SOURCE,msgbuf_,msgsize);
            break;
    
          case TAG_GET_NODE_LIST:
            procGetNodeList(status.MPI_SOURCE,msgbuf_,msgsize);
            break;
  
          case TAG_EVENT:
            procEvent(status.MPI_SOURCE,msgbuf_,msgsize);
            break;
    
          case TAG_SET_FOREST_STATE:
            procSetForestState(status.MPI_SOURCE,msgbuf_,msgsize);
            break;
    
          case TAG_NODE_INIT:
            procNodeInit(status.MPI_SOURCE,msgbuf_,msgsize);
            break;
    
          case TAG_NODE_EXECUTE:
            procNodeExecute(status.MPI_SOURCE,msgbuf_,msgsize);
            break;
      
          case TAG_NODE_GET_STATE:
            procNodeGetState(status.MPI_SOURCE,msgbuf_,msgsize);
            break;
            
          case TAG_NODE_SET_STATE:
            procNodeSetState(status.MPI_SOURCE,msgbuf_,msgsize);
            break;
            
          case TAG_NODE_PROCESS_COMMAND:
          case TAG_NODE_CLEAR_CACHE:
          case TAG_NODE_HOLD_CACHE:
          case TAG_NODE_PROPAGATE_STATE_DEP:
          case TAG_NODE_PUBLISH_PARENTAL_STAT:
          case TAG_NODE_SET_BREAKPOINT:
          case TAG_NODE_CLEAR_BREAKPOINT:
          case TAG_NODE_SET_PUBLISHING_LEVEL:
            break;
  
          case TAG_REPLY:
            procReply(msgbuf_,msgsize);
            break;
            
  //        case TAG_LOG_MESSAGE:
  //          break;
        }
      }
      catch( std::exception &exc )
      {
        string str = Debug::ssprintf("MPI process %d caught exception processing message %d (%s): %s",
                                comm_rank(),status.MPI_TAG,tagToString(status.MPI_TAG).c_str(),exc.what());
        cdebug(0)<<str<<endl;
        DMI::ExceptionList exclist(exc);
        exclist.add(LOFAR::Exception(str));
        postError(exclist);
      }
      catch(...)
      {
        string str = Debug::ssprintf("MPI process %d caught unknown exception processing message %d (%s)",
                                comm_rank(),status.MPI_TAG,tagToString(status.MPI_TAG).c_str());
        cdebug(0)<<str<<endl;
        postError(str);
      }
    } // endif (message received)
    // now, check if there's a message in the outgoing queue. If there is, pop it
    // and send
    if( !lock )
      lock.relock(sendqueue_cond_);
    if( !sendqueue_.empty() )
    {
      dprintf(3)("outgoing queue has %d messages\n",sendqueue_.size());
      // pop message from queue, and release lock to let other threads have a go at it
      MarinatedMessage msg = sendqueue_.front();
      sendqueue_.pop_front();
      lock.release();
      dprintf(3)("sending message to dest %d, tag %d (%s), size %d\n",
                msg.dest,msg.tag,tagToString(msg.tag).c_str(),msg.size);
      sendMessage(msg);
      rcvflag = 1;
    }
    // now, if rcvflag is true, we have sent or received something this time 'round,
    // so before going to sleep, let's have another go at things. But if it is false, we
    // can go to sleep on the sendqueue_ condition
    if( !rcvflag )
    {
      if( !lock )
        lock.relock(sendqueue_cond_);
      sendqueue_cond_.wait(0,POLLING_FREQ_NS);
    }
  }
  
  delete [] msgbuf_;
  msgbuf_ = 0;
  return 0;
}

// "Marinates" a message: fills in MarinatedMessage struct with the specified parameters,
// converts supplied BObj into a BlockSet, computes total message size.
// A marinated message may be sent off directly via sendMessage() (only within the communicator thread,
// of course), or placed into the send queue (if sent by another thread)
void MeqMPI::marinateMessage (MarinatedMessage &msg,int dest,int tag,
                              size_t hdrsize,const BObj *pobj)
{
  msg.dest = dest;
  msg.tag = tag;
  msg.header_size = hdrsize;
  msg.size = sizeof(int) + hdrsize;
  // convert object to a BlockSet
  if( pobj )
  {
    pobj->toBlock(msg.blockset);
    // work out total message size
    msg.size += sizeof(size_t)*msg.blockset.size();
    for( BlockSet::const_iterator iter = msg.blockset.begin(); iter != msg.blockset.end(); iter++ )
      msg.size += (*iter)->size();
  }
  else
    msg.blockset.clear();
}

// sends off pre-marinated MPI message contained in msg. Returns true on success, false on error.
bool MeqMPI::sendMessage (MarinatedMessage &msg)
{
  // make sure buffer is sufficient
  ensureBuffer(msgbuf_,msgbuf_size_,msg.size);
  // encode the message 
  if( encodeMessage(msgbuf_,&msg.hdr,msg.header_size,msg.blockset) != msg.size )
  {
    Throw("outgoing message has a size inconsistency");
  } 
  // send
  int retval;
  if( msg.dest<0 )
  {
    for( int i=1; i<comm_size(); i++ )
      retval = MPI_Send(msgbuf_,msg.size,MPI_BYTE,i,msg.tag,meq_mpi_communicator_);
  }
  else
    retval = MPI_Send(msgbuf_,msg.size,MPI_BYTE,msg.dest,msg.tag,meq_mpi_communicator_);
  return retval == MPI_SUCCESS;
}


size_t MeqMPI::encodeMessage (char *buf,const void *hdr,size_t hdrsize,BlockSet &blockset)
{
  // first int in message is ALWAYS number of blocks making up the BObj
  char *ptr = buf;
  int nblocks = *reinterpret_cast<int*>(ptr) = blockset.size();
  ptr += sizeof(int);
  // then, copy over the header
  if( hdrsize )
  {
    memcpy(ptr,hdr,hdrsize);
    ptr += hdrsize;
  }
  // then, get a pointer to array of blocksizes
  size_t *psizes = reinterpret_cast<size_t*>(ptr);
  ptr += sizeof(size_t)*nblocks;
  // and start copying blocks and sizes
  for( BlockSet::iterator iter = blockset.begin(); iter != blockset.end(); iter++ )
  {
    size_t sz = *psizes = (*iter)->size();
    memcpy(ptr,(*iter)->data(),sz);
    iter->detach();
    psizes++;
    ptr += sz;
  }
  return ptr - buf;
}

TypeId MeqMPI::decodeMessage (ObjRef &ref,void *hdr,size_t hdrsize,const char *msg,size_t msgsize)
{
  FailWhen(hdrsize+sizeof(int)>msgsize,"MPI message too short for the given type");
  // first int in message is ALWAYS number of blocks making up the BObj
  const char *ptr = msg,*msgend = msg + msgsize;
  int nblocks = *reinterpret_cast<const uint*>(ptr);
  ptr += sizeof(int);
  // next is the message header
  if( hdrsize )
  {
    memcpy(hdr,ptr,hdrsize);
    ptr += hdrsize;
  }
  // 0 blocks means no BObj attached, so return null type
  if( !nblocks )
    return 0;
  // now get array of block sizes
  FailWhen( msgend - ptr < int(nblocks*sizeof(size_t)),"MPI message too short");
  const size_t *psizes = reinterpret_cast<const size_t*>(ptr);
  ptr += nblocks*sizeof(size_t);
  // allocate & copy into memory blocks
  BlockSet blockset;
  for( int i=0; i<nblocks; i++ )
  {
    FailWhen( msgend - ptr < int(psizes[i]),"MPI message too short");
    SmartBlock *block = new SmartBlock(psizes[i]);
    blockset.pushNew() <<= block;
    memcpy(block->data(),ptr,psizes[i]);
    ptr += psizes[i];
  }
  // create object
  ref = DynamicTypeManager::construct(0,blockset);
  FailWhen(!ref.valid(),"failed to construct object");
  return ref->objectType();
}

// processes a REPLY message:
// dispatches arguments to endpoint described in the header
void MeqMPI::procReply (const char *msgbuf,int msgsize)
{
  // decode the message
  ObjRef ref;
  HdrReply header;
  decodeMessage(ref,&header,sizeof(header),msgbuf,msgsize);
  // if there's an associated reply endpoint, wake it up
  if( header.endpoint )
    header.endpoint->receive(header.retcode,ref);
}

// posts a REPLY message to the given destination and endpoint
void MeqMPI::postReply (int dest,const ReplyEndpoint *endpoint,int retcode,ObjRef &ref)
{
   // lock queue and add a marinated message at the back
  Thread::Mutex::Lock lock(sendqueue_cond_);
  sendqueue_.push_back(MarinatedMessage());
  MarinatedMessage &msg = sendqueue_.back();
  marinateMessage(msg,dest,TAG_REPLY,sizeof(HdrReply),ref.valid()?ref.deref_p():0);
  // detach ref to object after it has been serialized
  ref.detach();
  // fill message header
  msg.hdr.reply.endpoint = const_cast<ReplyEndpoint*>(endpoint);
  msg.hdr.reply.retcode  = retcode;
  // wake up comm thread, if needed
  if( Thread::self() != comm_thread_ )
    sendqueue_cond_.signal();
}

// posts an EVENT message (or passes event to forest, if on main server)
void MeqMPI::postEvent (const HIID &type,const ObjRef &data)
{
  if( comm_rank() == 0 )
    forest().postEvent(type,data);
  else
  {
    DMI::Record *prec = new DMI::Record;
    ObjRef ref(prec);
    (*prec)[AidType] = type;
    (*prec)[AidData] = data;
    // form up message
    Thread::Mutex::Lock lock(sendqueue_cond_);
    sendqueue_.push_back(MarinatedMessage());
    MarinatedMessage &msg = sendqueue_.back();
    marinateMessage(msg,0,TAG_EVENT,sizeof(HdrReplyExpected),ref);
    msg.hdr.repexp.endpoint = 0;
    // detach ref to object after it has been serialized
    ref.detach();
    // wake up comm thread, if needed
    if( Thread::self() != comm_thread_ )
      sendqueue_cond_.signal();
  }
}

// posts an error event
void MeqMPI::postError (const std::exception &exc)
{
  DMI::Record *prec = new DMI::Record;
  ObjRef ref(prec);
  (*prec)[AidError] = exceptionToObj(exc);
  postEvent(AidError,ref);
}

// posts a message event
void MeqMPI::postMessage (const std::string &msg,const HIID &type)
{
  DMI::Record *prec = new DMI::Record;
  ObjRef ref(prec);
  if( type == HIID(AidError) )
    (*prec)[AidError] = msg;
  else
    (*prec)[AidMessage] = msg;
  postEvent(type,ref);
}
    
// posts a command (with a ReplyExpected header) to the given destination. Uses endpoint for 
// the reply. 
void MeqMPI::postCommand (int tag,int dest,ReplyEndpoint &endpoint,ObjRef &ref)
{
   // lock queue and add a marinated message at the back
  Thread::Mutex::Lock lock(sendqueue_cond_);
  sendqueue_.push_back(MarinatedMessage());
  MarinatedMessage &msg = sendqueue_.back();
  marinateMessage(msg,dest,tag,sizeof(HdrReplyExpected),ref.valid() ? ref.deref_p() : 0);
  // detach ref to object after it has been serialized
  ref.detach();
  // fill message header
  msg.hdr.repexp.endpoint = &endpoint;
  // wake up comm thread, if needed
  if( Thread::self() != comm_thread_ )
    sendqueue_cond_.signal();
}

// posts a command (with a ReplyExpected header) to the given destination. Uses endpoint for 
// the reply. 
void MeqMPI::postCommand (int tag,int dest,ObjRef &ref)
{
   // lock queue and add a marinated message at the back
  Thread::Mutex::Lock lock(sendqueue_cond_);
  sendqueue_.push_back(MarinatedMessage());
  MarinatedMessage &msg = sendqueue_.back();
  marinateMessage(msg,dest,tag,sizeof(HdrReplyExpected),ref.valid() ? ref.deref_p() : 0);
  // detach ref to object after it has been serialized
  ref.detach();
  msg.hdr.repexp.endpoint = 0;
  // wake up comm thread, if needed
  if( Thread::self() != comm_thread_ )
    sendqueue_cond_.signal();
}
    
// posts a command (with a ReplyExpected header) to the given destination. Uses endpoint for 
// the reply. 
void MeqMPI::postCommand (int tag,int dest,const void *hdr,size_t hdrsize,ObjRef &ref)
{
  // lock queue and add a marinated message at the back
  Thread::Mutex::Lock lock(sendqueue_cond_);
  sendqueue_.push_back(MarinatedMessage());
  MarinatedMessage &msg = sendqueue_.back();
  marinateMessage(msg,dest,tag,hdrsize,ref.valid() ? ref.deref_p() : 0);
  // detach ref to object after it has been serialized
  ref.detach();
  // fill message header
  memcpy(&msg.hdr,hdr,hdrsize);
  // wake up comm thread, if needed
  if( Thread::self() != comm_thread_ )
    sendqueue_cond_.signal();
}

void MeqMPI::postCommand (int tag,int dest)
{
  ObjRef ref;
  postCommand(tag,dest,ref);
}

// Blocks until a reply has been posted via receive(), presumably by another thread.
// Returns the retcode and the ref passed to receive()
int MeqMPI::ReplyEndpoint::await (ObjRef &ref)
{
  Thread::Mutex::Lock lock(cond_);
  while( !replied_ )
    cond_.wait();
  if( objref_.valid() )
    ref.xfer(objref_);
  return retcode_;
}

// Returns message to an await()er thread
void MeqMPI::ReplyEndpoint::receive (int retcode,ObjRef &ref)
{
  Thread::Mutex::Lock lock(cond_);
  retcode_ = retcode;
  if( ref.valid() )
    objref_.xfer(ref);
  replied_ = true;
  cond_.signal();
}

// Returns message to an await()er thread
void MeqMPI::ReplyEndpoint::receive (int retcode)
{
  Thread::Mutex::Lock lock(cond_);
  retcode_ = retcode;
  replied_ = true;
  cond_.signal();
}

string MeqMPI::sdebug(int,const string &,const char *) const
{
  return ssprintf("MeqMPI[%d]",mpi_our_processor_);
}


} // namespace Meq

#endif // ifdef HAVE_MPI


#ifndef MEQMPI_H
#define MEQMPI_H

#include "config.h"
#ifdef HAVE_MPI

#include "mpi.h"

#include <DMI/BObj.h>
#include <DMI/Record.h>
#include <list>
#include <TimBase/Thread/Condition.h>
#include <MEQ/MTPool.h>
#include <MeqMPI/AID-MeqMPI.h>

#pragma aidgroup MeqMPI
#pragma aids Remote Proc Data Type Error

namespace Meq
{
// initial buffer size
const size_t DEFAULT_BUFFER_SIZE = 1024*1024*1024;

// when reallocated, buffer will be incremented by this value
const size_t DEFAULT_BUFFER_INCREMENT = 1024*1024*1024;

// polling frequency of MPI thread, in NS
static const int POLLING_FREQ_NS = 1000000;


class Forest;

using namespace DMI;


class MeqMPI
{
  public:
    // A ReplyEndpoint object is created whenever we want to send off an MPI message and want to wait for
    // a reply. The calling thread calls await(), the communicator thread calls receive() when a reply has
    // been received
    class ReplyEndpoint
    {
      private:
        Thread::Condition cond_;
        ObjRef objref_;
        bool replied_;
        int  retcode_;

      public:
        ReplyEndpoint ()
        : replied_(false)
        {}

        // Blocks until a reply has been posted via receive(), presumably by another thread.
        // Returns the retcode and the ref passed to receive()
        int await (ObjRef &ref);

        int await ()
        {
          ObjRef ref;
          return await(ref);
        }

        // Returns message to an await()er. Argument ref is transferred.
        void receive (int retcode,ObjRef &ref);

        // Returns message to an await()er without an argument.
        void receive (int retcode=0);
    };
    // Header structures for messages
    // This is used for all messages where a reply is expected
    typedef struct
    {
      ReplyEndpoint *endpoint;
    } HdrReplyExpected;

    // NodeOperation-type messages is associated with a node, so it contains a node index.
    // Somebody on the remote end is waiting for the result of the operation, this entity is identified
    //.by reply_ident (which should be copied directly into the Reply message's header).
    typedef struct
    {
      int nodeindex;
      int arg;
      ReplyEndpoint *endpoint;
    } HdrNodeOperation;

    // node breakpoint message header
    typedef struct
    {
      int nodeindex;
      int bpmask;
      bool oneshot;
      ReplyEndpoint *endpoint;
    } HdrNodeBreakpoint;

    // A Reply message is sent whenever some operation is completed that expects a reply.
    typedef struct
    {
      ReplyEndpoint *endpoint;
      int retcode;
    } HdrReply;

    typedef struct
    {
      int content;
      ReplyEndpoint *endpoint;
    } HdrGetNodeList;

    typedef struct
    {
      int nodeindex;
      int parent_nodeindex;
      bool stepparent;
      bool init_index;
      ReplyEndpoint *endpoint;
    } HdrNodeInit;


  private:

    // a marinated message is a message that's ready to be encoded and sent
    typedef struct
    {
      int dest;                 // MPI destination
      int tag;                  // MPI tag
      size_t header_size;       // size of header
      size_t size;              // full size of message (including blockset storage)
      BlockSet blockset;        // associated BObj, converted into a blockset
      // now, all known message headers are placed here
      union
      {
        HdrReplyExpected repexp;
        HdrNodeOperation node_op;
        HdrReply         reply;
        HdrGetNodeList   getnl;
        HdrNodeInit      nodeinit;
        HdrNodeBreakpoint bp;
      } hdr;
    } MarinatedMessage;

  public:
    // constructs MPI interface
    MeqMPI ();

    virtual ~MeqMPI ()
    {};

    // associates with forest
    void attachForest (Meq::Forest &forest);

    Meq::Forest & forest ()
    { return *forest_; }

    int comm_size () const
    { return mpi_num_processors_; }

    int comm_rank () const
    { return mpi_our_processor_; }

    // static method to build a nodelist from a forest. Also used by MeqServer, hence it
    // is placed here
    static int getNodeList (DMI::Record &list,int content,Meq::Forest &forest);

    // initializes the MeqMPI layer, launches the communicator thread, returns thread ID
    Thread::ThrID initialize (int argc,const char *argv[]);

    // halts and rejoins the communicator thread
    void stopCommThread ();
    // rejoins communicator thread -- blocks until it exits
    void rejoinCommThread ();

    // posts a command (w/o a header) to the given destination.
    // Note that a HdrReply (with endpoint=0) is always inserted
    void postCommand (int tag,int dest);
    void postCommand (int tag,int dest,ObjRef &ref);
    // posts a command (with a ReplyExpected header) to the given destination.
    // Uses endpoint for the reply.
    void postCommand (int tag,int dest,ReplyEndpoint &endpoint,ObjRef &ref);
    // posts a command with the given header, specified as pointer/size
    void postCommand (int tag,int dest,const void *hdr,size_t hdrsize,ObjRef &ref);

    // posts a command with the given header object
    template<class Header>
    void postCommand (int tag,int dest,const Header &hdr,ObjRef &ref)
    {
      postCommand(tag,dest,&hdr,sizeof(hdr),ref);
    }

    template<class Header>
    void postCommand (int tag,int dest,const Header &hdr)
    {
      ObjRef ref;
      postCommand(tag,dest,&hdr,sizeof(hdr),ref);
    }

    // posts a REPLY message to the given destination and endpoint
    void postReply (int dest,const ReplyEndpoint *endpoint,int retcode,ObjRef &ref);
    // posts a REPLY message to the given destination and endpoint
    void postReply (int dest,const ReplyEndpoint *endpoint,int retcode=0)
    { ObjRef ref; postReply(dest,endpoint,retcode,ref); }

    // posts an EVENT message to the main server
    void postEvent (const HIID &type,const ObjRef &data);
    // shortcut to post an event containing a text message
    void postMessage (const std::string &msg,const HIID &type);
    // shortcut to post an error event (from an exception)
    void postError (const std::exception &exc);
    // shortcut to post an error event (with message)
    void postError (const std::string &msg)
    { postMessage(msg,AidError); }

    // "Marinates" a message: fills in MarinatedMessage struct with the specified parameters,
    // converts supplied BObj into a BlockSet, computes total message size.
    // A marinated message may be sent off directly via sendMessage() (only within the communicator thread,
    // of course), or placed into the send queue (if sent by another thread)
    void marinateMessage (MarinatedMessage &msg,int dest,int tag,
                          size_t hdrsize,const BObj *pobj = 0);

    // communicator used for all our MPI calls
    MPI_Comm meq_mpi_communicator_;
    // number of processors in our MPI
    int mpi_num_processors_;
    // our rank
    int mpi_our_processor_;

    // singleton meqmpi object
    static MeqMPI * self;

    // message tags -- these identify message types
    typedef enum
    {
      TAG_INIT                  = 1,
      TAG_HALT,
      // reply message -- used when caller expects a reply
      TAG_REPLY,
      // forest management messagess
      TAG_CREATE_NODES,
      TAG_GET_NODE_LIST,
      TAG_SET_FOREST_STATE,
      // events: these go from subserver to server
      TAG_EVENT,

      // node management messages
      TAG_NODE_GET_STATE,
      TAG_NODE_SET_STATE,
      TAG_NODE_EXECUTE,
      TAG_NODE_PROCESS_COMMAND,
      TAG_NODE_CLEAR_CACHE,
      TAG_NODE_HOLD_CACHE,
      TAG_NODE_PROPAGATE_STATE_DEP,
      TAG_NODE_PUBLISH_PARENTAL_STAT,
      TAG_NODE_SET_BREAKPOINT,
      TAG_NODE_CLEAR_BREAKPOINT,
      TAG_NODE_SET_PUBLISHING_LEVEL,


      TAG_LAST_TAG
    } MpiMessageTags;

    // returns string corresponding to tag
    std::string tagToString (int tag);

    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3F5F195E013F
    LocalDebugContext;

  private:
    // gets/allocates a worker thread brigade, sets lock on brigade's condition var
    MTPool::Brigade * getBrigade (Thread::Mutex::Lock &lock);

    void procInit             (int source,const char *msgbuf,int msgsize);

    void procCreateNodes      (int source,const char *msgbuf,int msgsize);
    void procGetNodeList      (int source,const char *msgbuf,int msgsize);
    void procSetForestState   (int source,const char *msgbuf,int msgsize);
    void procEvent            (int source,const char *msgbuf,int msgsize);

    void procNodeInit         (int source,const char *msgbuf,int msgsize);
    void procNodeGetState     (int source,const char *msgbuf,int msgsize);
    void procNodeSetState     (int source,const char *msgbuf,int msgsize);
    void procNodeExecute      (int source,const char *msgbuf,int msgsize);

    void procNodeSetPublishingLevel (int source,const char *msgbuf,int msgsize);

    // processes a REPLY message
    // (simply dispatches arguments to endpoint described in the header)
    void procReply            (const char *msgbuf,int msgsize);

    // static version shunts through "self"
    static void postForestEvent_static  (const HIID &type,const ObjRef &data);

    // sends off pre-marinated MPI message contained in msg.
    // Returns true on success, false on error.
    // Note that the message is passed in as non-const, as we destroy the blockset
    bool sendMessage (MarinatedMessage &msg);

    // encodes a message into buffer
    size_t encodeMessage (char *buf,const void *hdr,
                          size_t hdrsize,BlockSet &blockset);

    // decodeMessage()
    // This decodes an MPI message from the specified buffer (msg,msgsize)
    // The message header (of size hdrsize) is copied into hdr.
    // The message BObj is attached to ref.
    // Returns type of decoded BObj, or 0 if no object was attached.
    TypeId decodeMessage (ObjRef &ref,void *hdr,size_t hdrsize,const char *msg,size_t msgsize);

    // helper function: ensures that the given buffer is big enough for the given message
    // size, reallocates if an increase is needed
    void ensureBuffer (char * &buf,size_t &bufsize,size_t msgsize);

    // thread entrypoint -- main communication loop runs here
    static void * commThreadEntrypoint (void*);
    void * runCommThread ();

    // INIT-message is formed up in constructor and sent from initialize(), so
    // its data record is stored here
    ObjRef initmsg_;

    // local MeqSubserver object
    Meq::Forest  *forest_;

    Thread::ThrID comm_thread_ ;
    bool comm_thread_running_;
    char * msgbuf_;
    size_t msgbuf_size_;

    std::list<MarinatedMessage> sendqueue_;
    Thread::Condition sendqueue_cond_;

};

} // namespace Meq

#endif // ifdef HAVE_MPI


#endif // include guard

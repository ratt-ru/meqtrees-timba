#ifndef Message_h
#define Message_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include "Common/CheckConfig.h"
#include "DMI/DataRecord.h"
#include "OCTOPUSSY/TID-OCTOPUSSY.h"
#include "OCTOPUSSY/LatencyVector.h"

// CountedRef
#include "DMI/CountedRef.h"
// SmartBlock
#include "DMI/SmartBlock.h"
// NestableContainer
#include "DMI/NestableContainer.h"
// HIID
#include "DMI/HIID.h"
// BlockableObject
#include "DMI/BlockableObject.h"
// OctopussyDebugContext
#include "OCTOPUSSY/OctopussyDebugContext.h"
// MsgAddress
#include "OCTOPUSSY/MsgAddress.h"
// in debug mode, enable latency stats, unless explicitly disabled
#if defined(LOFAR_DEBUG) && !defined(DISABLE_LATENCY_STATS)
#define ENABLE_LATENCY_STATS 1
#endif

#ifdef ENABLE_LATENCY_STATS
  CHECK_CONFIG(Message,LatencyStats,yes);
#else
  CHECK_CONFIG(Message,LatencyStats,no);
#endif

#pragma types #Message
#pragma aid Index

#include "OCTOPUSSY/AID-OCTOPUSSY.h"


class WPQueue;

//##ModelId=3C7B6A2D01F0

class Message : public OctopussyDebugContext,
                	public BlockableObject
{
  public:
      // some predefined priority levels
      // a priority<0 is considered "none"
    //##ModelId=3DB9369D01B2
      static const int PRI_LOWEST  = 0,
                       PRI_LOWER   = 0x10,
                       PRI_LOW     = 0x20,
                       PRI_NORMAL  = 0x100,
                       PRI_HIGH    = 0x200,
                       PRI_HIGHER  = 0x400,
                       PRI_EVENT   = 0x800;
                       
      // message delivery/subscription scope
    //##ModelId=3DB936510032
      typedef enum {
           GLOBAL        = 2,
           HOST          = 1,
           PROCESS       = 0,
           LOCAL         = 0
      } MessageScope;
           
      // message processing results (returned by WPInterface::receive(), etc.)
    //##ModelId=3DB936510104
      typedef enum {  
        ACCEPT   = 0, // message processed, OK to remove from queue
        HOLD     = 1, // hold the message (and block queue) until something else happens
        REQUEUE  = 2, // requeue the message and try again
        CANCEL   = 3  // for input()/timeout()/signal(), cancel the input or timeout
      } MessageResults;
           

  public:
    //##ModelId=3C8CB2CE00DC
      Message();

    //##ModelId=3C7B9C490384
      Message(const Message &right);

      //##ModelId=3C7B9D0A01FB
      explicit Message (const HIID &id1, int pri = PRI_NORMAL);

      //##ModelId=3C7B9D3B02C3
      Message (const HIID &id1, BlockableObject *pload, int flags = 0, int pri = PRI_NORMAL);
      
      //##ModelId=3C7B9D59014A
      Message (const HIID &id1, const ObjRef &pload, int flags = 0, int pri = PRI_NORMAL);
//      Message (const HIID &id1, const ObjRef &pload, int flags = 0, int pri = PRI_NORMAL);

      //##ModelId=3C7BB3BD0266
      Message (const HIID &id1, SmartBlock *bl, int flags = 0, int pri = PRI_NORMAL);

      //##ModelId=3DB936A5029F
      Message (const HIID &id1, const BlockRef &bl, int flags = 0, int pri = PRI_NORMAL);

      //##ModelId=3DB936A7019E
      Message (const HIID &id1, const char *data, size_t sz, int pri = PRI_NORMAL);

    //##ModelId=3DB936A90143
      ~Message();

    //##ModelId=3DB936A901E3
      Message & operator=(const Message &right);


      //##ModelId=3C7B9DDE0137
      Message & operator <<= (BlockableObject *pload);

      //##ModelId=3C7B9DF20014
      Message & operator <<= (ObjRef &pload);

      //##ModelId=3C7B9E0A02AD
      Message & operator <<= (SmartBlock *bl);

      //##ModelId=3C7B9E1601CE
      Message & operator <<= (BlockRef &bl);

      //##ModelId=3C7E32BE01E0
      //##Documentation
      //## Abstract method for cloning an object. Should return pointer to new
      //## object. Flags: DMI::WRITE if writable clone is required, DMI::DEEP
      //## for deep cloning (i.e. contents of object will be cloned as well).
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

      //##ModelId=3C7E32C1022B
      //##Documentation
      //## Virtual method for privatization of an object. If the object
      //## contains other refs, they should be privatized by this method. The
      //## DMI::DEEP flag should be passed on to child refs, for deep
      //## privatization.
      virtual void privatize (int flags = 0, int depth = 0);

      //##ModelId=3C7F56ED007D
      NestableContainer::Hook operator [] (const HIID &id);

      //##ModelId=3C7E4C310348
      NestableContainer::Hook operator [] (int n);

      //##ModelId=3C7E4C3E003A
      NestableContainer::ConstHook operator [] (const HIID &id) const;

      //##ModelId=3C7F56D90197
      NestableContainer::ConstHook operator [] (int n) const;

      //##ModelId=3CB42D0201B4
      NestableContainer::Hook setBranch (const HIID &id, int flags = DMI::WRITE);

      //##ModelId=3C7E443A016A
      void * data ();

      //##ModelId=3C7E446B02B5
      const void * data () const;

      //##ModelId=3C7E443E01B6
      size_t datasize () const;

      //##ModelId=3C960F16009B
      //##Documentation
      //## Returns the class TypeId
      virtual TypeId objectType () const;

      //##ModelId=3C960F1B0373
      //##Documentation
      //## Creates object from a set of block references. Appropriate number of
      //## references are removed from the head of the BlockSet. Returns # of
      //## refs removed.
      virtual int fromBlock (BlockSet& set);

      //##ModelId=3C960F20037A
      //##Documentation
      //## Stores an object into a set of blocks. Appropriate number of refs
      //## added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

    //##ModelId=3DB936AA02FD
      int priority () const;
    //##ModelId=3DB936AB0056
      void setPriority (int value);

    //##ModelId=3DB936AB02F5
      int state () const;
    //##ModelId=3DB936AC006B
      void setState (int value);

    //##ModelId=3DB936AC0332
      short hops () const;
    //##ModelId=3DB936AD00DB
      void setHops (short value);

    //##ModelId=3DB936AD03CA
      const MsgAddress& to () const;
    //##ModelId=3DB936AE015E
      void setTo (const MsgAddress& value);

    //##ModelId=3DB936AF0070
      const MsgAddress& from () const;
    //##ModelId=3DB936AF0214
      void setFrom (const MsgAddress& value);

    //##ModelId=3DB936B00161
      const HIID& id () const;
    //##ModelId=3DB936B00306
      void setId (const HIID& value);

    //##ModelId=3DB936B10360
      const ObjRef& payload () const;

    //##ModelId=3DB936B20112
      const BlockRef& block () const;

    //##ModelId=3DB936B202E9
      const MsgAddress& forwarder () const;
    //##ModelId=3DB936B300D8
      void setForwarder (const MsgAddress& value);

    // Additional Public Declarations
    //##ModelId=3DB936A10054
      int flags_; // user-defined flag field
      
    //##ModelId=3DB936B40140
      Message (const HIID &id1, const BlockableObject *pload, int flags = 0, int pri = PRI_NORMAL);
    //##ModelId=3DB936B80024
      Message (const HIID &id1, const SmartBlock *bl, int flags = 0, int pri = PRI_NORMAL);
      
    //##ModelId=3DB936BC0051
      ObjRef &     payload ();
    //##ModelId=3DB936BC0192
      BlockRef &   block   ();
      
      // This accesses the payload as a DataRecord, or throws an exception if it isn't one
    //##ModelId=3DB936BC02B4
      const DataRecord & record () const;
    //##ModelId=3DB936BD00A3
      DataRecord & wrecord ();

      // increments the hop count       
    //##ModelId=3DB936BD01D9
      short addHop ();
      
      // explicit versions of [] for string IDs
    //##ModelId=3DB936BD0306
      NestableContainer::ConstHook operator [] (AtomicID id1) const
      { return (*this)[HIID(id1)]; }
    //##ModelId=3DB936BF005B
      NestableContainer::ConstHook operator [] (const string &id1) const
      { return (*this)[HIID(id1)]; }
    //##ModelId=3DB936C00125
      NestableContainer::ConstHook operator [] (const char *id1) const
      { return (*this)[HIID(id1)]; }
    //##ModelId=3DB936C101D1
      NestableContainer::Hook operator [] (AtomicID id1) 
      { return (*this)[HIID(id1)]; }
    //##ModelId=3DB936C201D2
      NestableContainer::Hook operator [] (const string &id1) 
      { return (*this)[HIID(id1)]; }
    //##ModelId=3DB936C301E7
      NestableContainer::Hook operator [] (const char *id1) 
      { return (*this)[HIID(id1)]; }
      
    //##ModelId=3DB9365101AF
      typedef CountedRef<Message> Ref;
      
#ifdef ENABLE_LATENCY_STATS
    //##ModelId=3DB958F6030D
      LatencyVector latency;
#else
      static DummyLatencyVector latency;    
#endif
      
      // This is a typical debug() method setup. The sdebug()
      // method creates a debug info string at the given level of detail.
    //##ModelId=3DB936C40273
      string sdebug ( int detail = 1,const string &prefix = "",
                const char *name = 0 ) const;
    //##ModelId=3DB936C7012C
      const char * debug ( int detail = 1,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

  protected:
    // Additional Protected Declarations
    //##ModelId=3DB936A1038B
      BlockSet payload_set;
  private:
    // Data Members for Class Attributes

      //##ModelId=3C7B94970023
      int priority_;

      //##ModelId=3C7E33F40330
      int state_;

      //##ModelId=3CC952D7039B
      short hops_;

    // Data Members for Associations

      //##ModelId=3C7B7100015E
      MsgAddress to_;

      //##ModelId=3C7B7106029D
      MsgAddress from_;

      //##ModelId=3C7B718500FB
      HIID id_;

      //##ModelId=3DB958F60344
      ObjRef payload_;

      //##ModelId=3DB963AB022B
      BlockRef block_;

      //##ModelId=3CC9530903D9
      MsgAddress forwarder_;

    // Additional Implementation Declarations
    //##ModelId=3DB93651024F
      typedef struct 
      {  
        int priority,state,flags,idsize,fromsize,tosize,latsize;
        short hops;
        bool has_block;
        TypeId payload_type; 
      }  
      HeaderBlock;
                     
};

//##ModelId=3C7B722600DE

typedef Message::Ref MessageRef;
// Class Message 

//##ModelId=3C7B9D0A01FB
inline Message::Message (const HIID &id1, int pri)
   : priority_(pri),state_(0),hops_(0),id_(id1)
{
}



//##ModelId=3C7F56ED007D
inline NestableContainer::Hook Message::operator [] (const HIID &id)
{
  if( payload_.valid() )
  { FailWhen( !payload_->isNestable(),"payload is not a container" ); }
  else
    payload_.attach(new DataRecord,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  return (*static_cast<NestableContainer*>(
      const_cast<BlockableObject*>(&payload_.deref())))[id];
}

//##ModelId=3C7E4C310348
inline NestableContainer::Hook Message::operator [] (int n)
{
  if( payload_.valid() )
  { FailWhen( !payload_->isNestable(),"payload is not a container" ); }
  else
    payload_.attach(new DataRecord,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  
  return (*static_cast<NestableContainer*>(
      const_cast<BlockableObject*>(&payload_.deref())))[n];
}

//##ModelId=3C7E4C3E003A
inline NestableContainer::ConstHook Message::operator [] (const HIID &id) const
{
  FailWhen( !payload_.valid() || !payload_->isNestable(),"payload is not a container" ); 
  return (*static_cast<const NestableContainer*>(&payload_.deref()))[id];
}

//##ModelId=3C7F56D90197
inline NestableContainer::ConstHook Message::operator [] (int n) const
{
  FailWhen( !payload_.valid() || !payload_->isNestable(),"payload is not a container" ); 
  return (*static_cast<const NestableContainer*>(&payload_.deref()))[n];
}

//##ModelId=3C7E443A016A
inline void * Message::data ()
{
  return block_.valid() ? block_().data() : 0;
}

//##ModelId=3C7E446B02B5
inline const void * Message::data () const
{
  return block_.valid() ? block_->data() : 0;
}

//##ModelId=3C7E443E01B6
inline size_t Message::datasize () const
{
  return block_.valid() ? block_->size() : 0;
}

//##ModelId=3C960F16009B
inline TypeId Message::objectType () const
{
  return TpMessage;
}

//##ModelId=3DB936AA02FD
inline int Message::priority () const
{
  return priority_;
}

//##ModelId=3DB936AB0056
inline void Message::setPriority (int value)
{
  priority_ = value;
}

//##ModelId=3DB936AB02F5
inline int Message::state () const
{
  return state_;
}

//##ModelId=3DB936AC006B
inline void Message::setState (int value)
{
  state_ = value;
}

//##ModelId=3DB936AC0332
inline short Message::hops () const
{
  return hops_;
}

//##ModelId=3DB936AD00DB
inline void Message::setHops (short value)
{
  hops_ = value;
}

//##ModelId=3DB936AD03CA
inline const MsgAddress& Message::to () const
{
  return to_;
}

//##ModelId=3DB936AE015E
inline void Message::setTo (const MsgAddress& value)
{
  to_ = value;
}

//##ModelId=3DB936AF0070
inline const MsgAddress& Message::from () const
{
  return from_;
}

//##ModelId=3DB936AF0214
inline void Message::setFrom (const MsgAddress& value)
{
  from_ = value;
}

//##ModelId=3DB936B00161
inline const HIID& Message::id () const
{
  return id_;
}

//##ModelId=3DB936B00306
inline void Message::setId (const HIID& value)
{
  id_ = value;
}

//##ModelId=3DB936B10360
inline const ObjRef& Message::payload () const
{
  return payload_;
}

//##ModelId=3DB936B20112
inline const BlockRef& Message::block () const
{
  return block_;
}

//##ModelId=3DB936B202E9
inline const MsgAddress& Message::forwarder () const
{
  return forwarder_;
}

//##ModelId=3DB936B300D8
inline void Message::setForwarder (const MsgAddress& value)
{
  forwarder_ = value;
}

//##ModelId=3DB936BC0051
inline ObjRef& Message::payload () 
{
  return payload_;
}

//##ModelId=3DB936BC0192
inline BlockRef& Message::block () 
{
  return block_;
}

//##ModelId=3DB936BD01D9
inline short Message::addHop ()                               
{ 
  return ++hops_; 
}

//##ModelId=3DB936BC02B4
inline const DataRecord & Message::record () const
{
  const DataRecord *rec = dynamic_cast<const DataRecord *>(payload_.deref_p());
  FailWhen(!rec,"payload is not a DataRecord");
  return *rec;
}

//##ModelId=3DB936BD00A3
inline DataRecord & Message::wrecord ()
{
  DataRecord *rec = dynamic_cast<DataRecord *>(payload_.dewr_p());
  FailWhen(!rec,"payload is not a DataRecord");
  return *rec;
}



#endif

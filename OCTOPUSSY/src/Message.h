//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7B7F2F0248.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7B7F2F0248.cm

//## begin module%3C7B7F2F0248.cp preserve=no
//## end module%3C7B7F2F0248.cp

//## Module: Message%3C7B7F2F0248; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\Message.h

#ifndef Message_h
#define Message_h 1

//## begin module%3C7B7F2F0248.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C7B7F2F0248.additionalIncludes

//## begin module%3C7B7F2F0248.includes preserve=yes
#include "OCTOPUSSY/TID-OCTOPUSSY.h"
#include "DMI/DataRecord.h"
//## end module%3C7B7F2F0248.includes

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
//## begin module%3C7B7F2F0248.declarations preserve=no
//## end module%3C7B7F2F0248.declarations

//## begin module%3C7B7F2F0248.additionalDeclarations preserve=yes
#pragma types #Message
#pragma aid Index

#include "OCTOPUSSY/AID-OCTOPUSSY.h"
//## end module%3C7B7F2F0248.additionalDeclarations


//## begin Message%3C7B6A2D01F0.preface preserve=yes
class WPQueue;
//## end Message%3C7B6A2D01F0.preface

//## Class: Message%3C7B6A2D01F0
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C7B70830385;MsgAddress { -> }
//## Uses: <unnamed>%3C7B708B00DD;HIID { -> }
//## Uses: <unnamed>%3C7E4D87012D;NestableContainer { -> }

class Message : public OctopussyDebugContext, //## Inherits: <unnamed>%3C7FA31802FF
                	public BlockableObject  //## Inherits: <unnamed>%3C960F080308
{
  //## begin Message%3C7B6A2D01F0.initialDeclarations preserve=yes
  public:
      // some predefined priority levels
      // a priority<0 is considered "none"
      static const int PRI_LOWEST  = 0,
                       PRI_LOWER   = 0x10,
                       PRI_LOW     = 0x20,
                       PRI_NORMAL  = 0x100,
                       PRI_HIGH    = 0x200,
                       PRI_HIGHER  = 0x400,
                       PRI_EVENT   = 0x800;
                       
      // message delivery/subscription scope
      typedef enum {
           GLOBAL        = 2,
           HOST          = 1,
           PROCESS       = 0,
           LOCAL         = 0
      } MessageScope;
           
      // message processing results (returned by WPInterface::receive(), etc.)
      typedef enum {  
        ACCEPT   = 0, // message processed, OK to remove from queue
        HOLD     = 1, // hold the message (and block queue) until something else happens
        REQUEUE  = 2, // requeue the message and try again
        CANCEL   = 3  // for input()/timeout()/signal(), cancel the input or timeout
      } MessageResults;
           
  //## end Message%3C7B6A2D01F0.initialDeclarations

  public:
    //## Constructors (generated)
      Message();

      Message(const Message &right);

    //## Constructors (specified)
      //## Operation: Message%3C8CB2CE00DC
      explicit Message (const HIID &id1, int pri = PRI_NORMAL);

      //## Operation: Message%3C7B9C490384
      Message (const HIID &id1, BlockableObject *pload, int flags = 0, int pri = PRI_NORMAL);

      //## Operation: Message%3C7B9D0A01FB
      Message (const HIID &id1, const ObjRef &pload, int flags = 0, int pri = PRI_NORMAL);

      //## Operation: Message%3C7B9D3B02C3
      Message (const HIID &id1, SmartBlock *bl, int flags = 0, int pri = PRI_NORMAL);

      //## Operation: Message%3C7B9D59014A
      Message (const HIID &id1, const BlockRef &bl, int flags = 0, int pri = PRI_NORMAL);

      //## Operation: Message%3C7BB3BD0266
      Message (const HIID &id1, const char *data, size_t sz, int pri = PRI_NORMAL);

    //## Destructor (generated)
      ~Message();

    //## Assignment Operation (generated)
      Message & operator=(const Message &right);


    //## Other Operations (specified)
      //## Operation: operator <<=%3C7B9DDE0137
      Message & operator <<= (BlockableObject *pload);

      //## Operation: operator <<=%3C7B9DF20014
      Message & operator <<= (ObjRef &pload);

      //## Operation: operator <<=%3C7B9E0A02AD
      Message & operator <<= (SmartBlock *bl);

      //## Operation: operator <<=%3C7B9E1601CE
      Message & operator <<= (BlockRef &bl);

      //## Operation: clone%3C7E32BE01E0; C++
      //	Abstract method for cloning an object. Should return pointer to new
      //	object. Flags: DMI::WRITE if writable clone is required, DMI::DEEP
      //	for deep cloning (i.e. contents of object will be cloned as well).
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

      //## Operation: privatize%3C7E32C1022B
      //	Virtual method for privatization of an object. If the object
      //	contains other refs, they should be privatized by this method. The
      //	DMI::DEEP flag should be passed on to child refs, for deep
      //	privatization.
      virtual void privatize (int flags = 0, int depth = 0);

      //## Operation: operator []%3C7F56ED007D
      NestableContainer::Hook operator [] (const HIID &id);

      //## Operation: operator []%3C7E4C310348
      NestableContainer::Hook operator [] (int n);

      //## Operation: operator []%3C7E4C3E003A
      NestableContainer::ConstHook operator [] (const HIID &id) const;

      //## Operation: operator []%3C7F56D90197
      NestableContainer::ConstHook operator [] (int n) const;

      //## Operation: setBranch%3CB42D0201B4
      NestableContainer::Hook setBranch (const HIID &id, int flags = DMI::WRITE);

      //## Operation: data%3C7E443A016A
      void * data ();

      //## Operation: data%3C7E446B02B5
      const void * data () const;

      //## Operation: datasize%3C7E443E01B6
      size_t datasize () const;

      //## Operation: objectType%3C960F16009B
      //	Returns the class TypeId
      virtual TypeId objectType () const;

      //## Operation: fromBlock%3C960F1B0373
      //	Creates object from a set of block references. Appropriate number of
      //	references are removed from the head of the BlockSet. Returns # of
      //	refs removed.
      virtual int fromBlock (BlockSet& set);

      //## Operation: toBlock%3C960F20037A
      //	Stores an object into a set of blocks. Appropriate number of refs
      //	added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const;

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: priority%3C7B94970023
      int priority () const;
      void setPriority (int value);

      //## Attribute: state%3C7E33F40330
      int state () const;
      void setState (int value);

      //## Attribute: hops%3CC952D7039B
      short hops () const;
      void setHops (short value);

    //## Get and Set Operations for Associations (generated)

      //## Association: OCTOPUSSY::<unnamed>%3C7B70FF033D
      //## Role: Message::to%3C7B7100015E
      const MsgAddress& to () const;
      void setTo (const MsgAddress& value);

      //## Association: OCTOPUSSY::<unnamed>%3C7B71050151
      //## Role: Message::from%3C7B7106029D
      const MsgAddress& from () const;
      void setFrom (const MsgAddress& value);

      //## Association: OCTOPUSSY::<unnamed>%3C7B71820219
      //## Role: Message::id%3C7B718500FB
      const HIID& id () const;
      void setId (const HIID& value);

      //## Association: OCTOPUSSY::<unnamed>%3C7B9796024D
      //## Role: Message::payload%3C7B97970096
      const ObjRef& payload () const;

      //## Association: OCTOPUSSY::<unnamed>%3C7B9799014D
      //## Role: Message::block%3C7B97990388
      const BlockRef& block () const;

      //## Association: OCTOPUSSY::<unnamed>%3CC9530802FB
      //## Role: Message::forwarder%3CC9530903D9
      const MsgAddress& forwarder () const;
      void setForwarder (const MsgAddress& value);

    // Additional Public Declarations
      //## begin Message%3C7B6A2D01F0.public preserve=yes
          //## Operation: Message%3C7B9C490384
      Message (const HIID &id1, const BlockableObject *pload, int flags = 0, int pri = PRI_NORMAL);
      Message (const HIID &id1, const SmartBlock *bl, int flags = 0, int pri = PRI_NORMAL);
      
      ObjRef &     payload ();
      BlockRef &   block   ();
      
      // This accesses the payload as a DataRecord, or throws an exception if it isn't one
      const DataRecord & record () const;
      DataRecord & wrecord ();
      

      short addHop ();
            
      // explicit versions of [] for string IDs
      NestableContainer::ConstHook operator [] (AtomicID id1) const
      { return (*this)[HIID(id1)]; }
      NestableContainer::ConstHook operator [] (const string &id1) const
      { return (*this)[HIID(id1)]; }
      NestableContainer::ConstHook operator [] (const char *id1) const
      { return (*this)[HIID(id1)]; }
      NestableContainer::Hook operator [] (AtomicID id1) 
      { return (*this)[HIID(id1)]; }
      NestableContainer::Hook operator [] (const string &id1) 
      { return (*this)[HIID(id1)]; }
      NestableContainer::Hook operator [] (const char *id1) 
      { return (*this)[HIID(id1)]; }
      
      typedef CountedRef<Message> Ref;
      
//       typedef struct {
//         WPQueue *wpq;
//         int handle;
//         HIID id;
//         void *data;
//       } TimeoutData;
      
      // This is a typical debug() method setup. The sdebug()
      // method creates a debug info string at the given level of detail.
      string sdebug ( int detail = 1,const string &prefix = "",
                const char *name = 0 ) const;
      const char * debug ( int detail = 1,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

      //## end Message%3C7B6A2D01F0.public
  protected:
    // Additional Protected Declarations
      //## begin Message%3C7B6A2D01F0.protected preserve=yes
      BlockSet payload_set;
      typedef struct {
        size_t idsize;
        int priority;
        int state;
        char to[MsgAddress::byte_size],
             from[MsgAddress::byte_size];
        int num_payload_blocks;
        size_t block_size;
      } MessageBlock;
      //## end Message%3C7B6A2D01F0.protected
  private:
    // Additional Private Declarations
      //## begin Message%3C7B6A2D01F0.private preserve=yes
      //## end Message%3C7B6A2D01F0.private

  private: //## implementation
    // Data Members for Class Attributes

      //## begin Message::priority%3C7B94970023.attr preserve=no  public: int {U} 
      int priority_;
      //## end Message::priority%3C7B94970023.attr

      //## begin Message::state%3C7E33F40330.attr preserve=no  public: int {U} 
      int state_;
      //## end Message::state%3C7E33F40330.attr

      //## begin Message::hops%3CC952D7039B.attr preserve=no  public: short {U} 
      short hops_;
      //## end Message::hops%3CC952D7039B.attr

    // Data Members for Associations

      //## Association: OCTOPUSSY::<unnamed>%3C7B70FF033D
      //## begin Message::to%3C7B7100015E.role preserve=no  public: MsgAddress { -> 1VHgN}
      MsgAddress to_;
      //## end Message::to%3C7B7100015E.role

      //## Association: OCTOPUSSY::<unnamed>%3C7B71050151
      //## begin Message::from%3C7B7106029D.role preserve=no  public: MsgAddress { -> 1VHgN}
      MsgAddress from_;
      //## end Message::from%3C7B7106029D.role

      //## Association: OCTOPUSSY::<unnamed>%3C7B71820219
      //## begin Message::id%3C7B718500FB.role preserve=no  public: HIID { -> 1VHgN}
      HIID id_;
      //## end Message::id%3C7B718500FB.role

      //## Association: OCTOPUSSY::<unnamed>%3C7B9796024D
      //## begin Message::payload%3C7B97970096.role preserve=no  public: BlockableObject { -> 0..1RHgN}
      ObjRef payload_;
      //## end Message::payload%3C7B97970096.role

      //## Association: OCTOPUSSY::<unnamed>%3C7B9799014D
      //## begin Message::block%3C7B97990388.role preserve=no  public: SmartBlock { -> 0..1RHgN}
      BlockRef block_;
      //## end Message::block%3C7B97990388.role

      //## Association: OCTOPUSSY::<unnamed>%3CC9530802FB
      //## begin Message::forwarder%3CC9530903D9.role preserve=no  public: MsgAddress { -> 1VHgN}
      MsgAddress forwarder_;
      //## end Message::forwarder%3CC9530903D9.role

    // Additional Implementation Declarations
      //## begin Message%3C7B6A2D01F0.implementation preserve=yes
      typedef struct {  int priority,state,idsize,fromsize,tosize;
                        short hops;
                        bool has_block;
                        TypeId payload_type; 
                     }  HeaderBlock;
                     
      //## end Message%3C7B6A2D01F0.implementation
};

//## begin Message%3C7B6A2D01F0.postscript preserve=yes
//## end Message%3C7B6A2D01F0.postscript

//## begin MessageRef%3C7B722600DE.preface preserve=yes
//## end MessageRef%3C7B722600DE.preface

//## Class: MessageRef%3C7B722600DE
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C7B7262018F;CountedRef { -> }
//## Uses: <unnamed>%3C7B726503E2;Message { -> }

typedef Message::Ref MessageRef;
//## begin MessageRef%3C7B722600DE.postscript preserve=yes
//## end MessageRef%3C7B722600DE.postscript

// Class Message 

inline Message::Message (const HIID &id1, int pri)
  //## begin Message::Message%3C8CB2CE00DC.hasinit preserve=no
  //## end Message::Message%3C8CB2CE00DC.hasinit
  //## begin Message::Message%3C8CB2CE00DC.initialization preserve=yes
   : priority_(pri),state_(0),hops_(0),id_(id1)
  //## end Message::Message%3C8CB2CE00DC.initialization
{
  //## begin Message::Message%3C8CB2CE00DC.body preserve=yes
  //## end Message::Message%3C8CB2CE00DC.body
}



//## Other Operations (inline)
inline NestableContainer::Hook Message::operator [] (const HIID &id)
{
  //## begin Message::operator []%3C7F56ED007D.body preserve=yes
  if( payload_.valid() )
  { FailWhen( !payload_->isNestable(),"payload is not a container" ); }
  else
    payload_.attach(new DataRecord,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  return (*static_cast<NestableContainer*>(
      const_cast<BlockableObject*>(&payload_.deref())))[id];
  //## end Message::operator []%3C7F56ED007D.body
}

inline NestableContainer::Hook Message::operator [] (int n)
{
  //## begin Message::operator []%3C7E4C310348.body preserve=yes
  if( payload_.valid() )
  { FailWhen( !payload_->isNestable(),"payload is not a container" ); }
  else
    payload_.attach(new DataRecord,DMI::ANON|DMI::WRITE|DMI::PERSIST);
  
  return (*static_cast<NestableContainer*>(
      const_cast<BlockableObject*>(&payload_.deref())))[n];
  //## end Message::operator []%3C7E4C310348.body
}

inline NestableContainer::ConstHook Message::operator [] (const HIID &id) const
{
  //## begin Message::operator []%3C7E4C3E003A.body preserve=yes
  FailWhen( !payload_.valid() || !payload_->isNestable(),"payload is not a container" ); 
  return (*static_cast<const NestableContainer*>(&payload_.deref()))[id];
  //## end Message::operator []%3C7E4C3E003A.body
}

inline NestableContainer::ConstHook Message::operator [] (int n) const
{
  //## begin Message::operator []%3C7F56D90197.body preserve=yes
  FailWhen( !payload_.valid() || !payload_->isNestable(),"payload is not a container" ); 
  return (*static_cast<const NestableContainer*>(&payload_.deref()))[n];
  //## end Message::operator []%3C7F56D90197.body
}

inline void * Message::data ()
{
  //## begin Message::data%3C7E443A016A.body preserve=yes
  return block_.valid() ? block_().data() : 0;
  //## end Message::data%3C7E443A016A.body
}

inline const void * Message::data () const
{
  //## begin Message::data%3C7E446B02B5.body preserve=yes
  return block_.valid() ? block_->data() : 0;
  //## end Message::data%3C7E446B02B5.body
}

inline size_t Message::datasize () const
{
  //## begin Message::datasize%3C7E443E01B6.body preserve=yes
  return block_.valid() ? block_->size() : 0;
  //## end Message::datasize%3C7E443E01B6.body
}

inline TypeId Message::objectType () const
{
  //## begin Message::objectType%3C960F16009B.body preserve=yes
  return TpMessage;
  //## end Message::objectType%3C960F16009B.body
}

//## Get and Set Operations for Class Attributes (inline)

inline int Message::priority () const
{
  //## begin Message::priority%3C7B94970023.get preserve=no
  return priority_;
  //## end Message::priority%3C7B94970023.get
}

inline void Message::setPriority (int value)
{
  //## begin Message::setPriority%3C7B94970023.set preserve=no
  priority_ = value;
  //## end Message::setPriority%3C7B94970023.set
}

inline int Message::state () const
{
  //## begin Message::state%3C7E33F40330.get preserve=no
  return state_;
  //## end Message::state%3C7E33F40330.get
}

inline void Message::setState (int value)
{
  //## begin Message::setState%3C7E33F40330.set preserve=no
  state_ = value;
  //## end Message::setState%3C7E33F40330.set
}

inline short Message::hops () const
{
  //## begin Message::hops%3CC952D7039B.get preserve=no
  return hops_;
  //## end Message::hops%3CC952D7039B.get
}

inline void Message::setHops (short value)
{
  //## begin Message::setHops%3CC952D7039B.set preserve=no
  hops_ = value;
  //## end Message::setHops%3CC952D7039B.set
}

//## Get and Set Operations for Associations (inline)

inline const MsgAddress& Message::to () const
{
  //## begin Message::to%3C7B7100015E.get preserve=no
  return to_;
  //## end Message::to%3C7B7100015E.get
}

inline void Message::setTo (const MsgAddress& value)
{
  //## begin Message::setTo%3C7B7100015E.set preserve=no
  to_ = value;
  //## end Message::setTo%3C7B7100015E.set
}

inline const MsgAddress& Message::from () const
{
  //## begin Message::from%3C7B7106029D.get preserve=no
  return from_;
  //## end Message::from%3C7B7106029D.get
}

inline void Message::setFrom (const MsgAddress& value)
{
  //## begin Message::setFrom%3C7B7106029D.set preserve=no
  from_ = value;
  //## end Message::setFrom%3C7B7106029D.set
}

inline const HIID& Message::id () const
{
  //## begin Message::id%3C7B718500FB.get preserve=no
  return id_;
  //## end Message::id%3C7B718500FB.get
}

inline void Message::setId (const HIID& value)
{
  //## begin Message::setId%3C7B718500FB.set preserve=no
  id_ = value;
  //## end Message::setId%3C7B718500FB.set
}

inline const ObjRef& Message::payload () const
{
  //## begin Message::payload%3C7B97970096.get preserve=no
  return payload_;
  //## end Message::payload%3C7B97970096.get
}

inline const BlockRef& Message::block () const
{
  //## begin Message::block%3C7B97990388.get preserve=no
  return block_;
  //## end Message::block%3C7B97990388.get
}

inline const MsgAddress& Message::forwarder () const
{
  //## begin Message::forwarder%3CC9530903D9.get preserve=no
  return forwarder_;
  //## end Message::forwarder%3CC9530903D9.get
}

inline void Message::setForwarder (const MsgAddress& value)
{
  //## begin Message::setForwarder%3CC9530903D9.set preserve=no
  forwarder_ = value;
  //## end Message::setForwarder%3CC9530903D9.set
}

//## begin module%3C7B7F2F0248.epilog preserve=yes
inline ObjRef& Message::payload () 
{
  return payload_;
}

inline BlockRef& Message::block () 
{
  return block_;
}

inline short Message::addHop ()                               
{ 
  return ++hops_; 
}

inline const DataRecord & Message::record () const
{
  const DataRecord *rec = dynamic_cast<const DataRecord *>(payload_.deref_p());
  FailWhen(!rec,"payload is not a DataRecord");
  return *rec;
}

inline DataRecord & Message::wrecord ()
{
  DataRecord *rec = dynamic_cast<DataRecord *>(payload_.dewr_p());
  FailWhen(!rec,"payload is not a DataRecord");
  return *rec;
}

//## end module%3C7B7F2F0248.epilog


#endif

#ifndef Subscriptions_h
#define Subscriptions_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include <list>

// HIID
#include "DMI/HIID.h"
// MsgAddress
#include "OCTOPUSSY/MsgAddress.h"
// Message
#include "OCTOPUSSY/Message.h"

//##ModelId=3C999C8400AF

class Subscriptions 
{
  public:
    //##ModelId=3DB936DB02BE
      Subscriptions();


      //##ModelId=3C999D010361
      bool add (const HIID& id, const MsgAddress &scope);

      //##ModelId=3C999D40033A
      bool remove (const HIID &id);

      //##ModelId=3C999E0B0223
      void clear ();

      //##ModelId=3C99C0BB0378
      int size () const;

      //##ModelId=3C999D64004D
      bool merge (const Subscriptions &other);

      //##ModelId=3C999D780005
      bool matches (const Message &msg) const;

      //##ModelId=3C99AC2F01DF
      //##Documentation
      //## Stores HIID into raw data block
      size_t pack (void* block, size_t &nleft) const;

      //##ModelId=3C99AC2F022F
      void unpack (const void* block, size_t sz);

      //##ModelId=3C99AC2F027F
      //##Documentation
      //## Returns # of bytes required to store the HIID
      size_t packSize () const;

  private:
    // Additional Implementation Declarations
    //##ModelId=3DB936520168
      typedef struct { HIID mask; MsgAddress scope; } SubElement;
    //##ModelId=3DB9365201A4
      typedef list<SubElement> SubSet;
    //##ModelId=3DB936DB021F
      SubSet subs;
    //##ModelId=3DB9365201E0
      typedef SubSet::iterator SSI;
    //##ModelId=3DB936520227
      typedef SubSet::const_iterator CSSI;

      // this always keep track of the pack-size of the set.
      // it is updated by add() and remove().
    //##ModelId=3DB936DB025A
      size_t pksize;
};

// Class Subscriptions 


//##ModelId=3C99C0BB0378
inline int Subscriptions::size () const
{
  return subs.size();
}

//##ModelId=3C99AC2F027F
inline size_t Subscriptions::packSize () const
{
  return pksize;
}


#endif

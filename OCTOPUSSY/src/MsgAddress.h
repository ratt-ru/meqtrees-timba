#ifndef MsgAddress_h
#define MsgAddress_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include "OCTOPUSSY/AID-OCTOPUSSY.h"

// HIID
#include "DMI/HIID.h"
#pragma aidgroup OCTOPUSSY
#pragma aid Dispatcher Local Publish


//##ModelId=3C8F9A340206
class WPID : public HIID
{
  public:
    //##ModelId=3C8F9AC70027
      WPID();

      //##ModelId=3DB936DB0337
      WPID (AtomicID wpc, AtomicID inst = 0);


      //##ModelId=3C8F9AA503C1
      AtomicID wpclass () const;

      //##ModelId=3C8F9AAB0103
      AtomicID inst () const;

    // Additional Public Declarations
    //##ModelId=3DB936DB02FA
      static const size_t byte_size = 2*sizeof(int);
};

//##ModelId=3C7B6F790197
class MsgAddress : public WPID
{
  public:
    //##ModelId=3C7B6FAE00FD
      MsgAddress();

      MsgAddress (const HIID &id);
      
      //##ModelId=3C8F9B8E0087
      MsgAddress (AtomicID wpc, AtomicID wpinst = 0, AtomicID proc = AidLocal, AtomicID host = AidLocal);

      //##ModelId=3DB936CA0217
      MsgAddress (const WPID& wpid, AtomicID proc = AidLocal, AtomicID host = AidLocal);


      //##ModelId=3C8F9BC10135
      WPID wpid () const;

      //##ModelId=3C7B6FF7033D
      AtomicID & process ();

      //##ModelId=3C90700001B4
      const AtomicID & process () const;

      //##ModelId=3C7B6FFC0330
      AtomicID & host ();

      //##ModelId=3C9070080170
      const AtomicID & host () const;

    // Additional Public Declarations
    //##ModelId=3DB936CA0358
      HIID peerid () const
      { return process()|host(); }
      
    //##ModelId=3DB936CA007D
      static const size_t byte_size = 4*sizeof(int);
};

// Class WPID 

//##ModelId=3C8F9AC70027
inline WPID::WPID()
{
}

//##ModelId=3DB936DB0337
inline WPID::WPID (AtomicID wpc, AtomicID inst)
    : HIID(wpc)
{
  add(inst);
}



//##ModelId=3C8F9AA503C1
inline AtomicID WPID::wpclass () const
{
  return (*this)[0];
}

//##ModelId=3C8F9AAB0103
inline AtomicID WPID::inst () const
{
  return (*this)[1];
}

// Class MsgAddress 

//##ModelId=3C7B6FAE00FD
inline MsgAddress::MsgAddress()
{
  resize(4);
}

inline MsgAddress::MsgAddress (const HIID &id)
{
  FailWhen(id.size()!=4,"invalid address length");
  HIID::operator = (id);
}

//##ModelId=3C8F9B8E0087
inline MsgAddress::MsgAddress (AtomicID wpc, AtomicID wpinst, AtomicID proc, AtomicID host)
    : WPID(wpc,wpinst)
{
  add(proc);
  add(host);
}

//##ModelId=3DB936CA0217
inline MsgAddress::MsgAddress (const WPID& wpid, AtomicID proc, AtomicID host)
    : WPID(wpid)
{
  add(proc);
  add(host);
}



//##ModelId=3C8F9BC10135
inline WPID MsgAddress::wpid () const
{
  return WPID(wpclass(),inst());
}

//##ModelId=3C7B6FF7033D
inline AtomicID & MsgAddress::process ()
{
  return (*this)[2];
}

//##ModelId=3C90700001B4
inline const AtomicID & MsgAddress::process () const
{
  return (*this)[2];
}

//##ModelId=3C7B6FFC0330
inline AtomicID & MsgAddress::host ()
{
  return (*this)[3];
}

//##ModelId=3C9070080170
inline const AtomicID & MsgAddress::host () const
{
  return (*this)[3];
}


#endif

//	f:\lofar\dvl\lofar\cep\cpa\pscf\src

#ifndef HIIDSet_h
#define HIIDSet_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include <set>

// HIID
#include "DMI/HIID.h"

//##ModelId=3BFBAC350085
//##Documentation
//## A set of multiple hierarchical IDs
//## (may include masks, etc.)
class HIIDSet 
{
  public:
    //##ModelId=3BFBAE2403DA
      HIIDSet();

    //##ModelId=3C98D01B036C
      HIIDSet(const HIIDSet &right);

      //##ModelId=3DB9348D0271
      HIIDSet (const HIID& id);

      //##ModelId=3DB9348D0339
      HIIDSet (const void* block, int sz);

    //##ModelId=3DB9348E00CE
      ~HIIDSet();

    //##ModelId=3DB9348E010A
      HIIDSet & operator=(const HIIDSet &right);


      //##ModelId=3C7E15F90113
      void clear ();

      //##ModelId=3C1DF8510016
      HIIDSet & add (const HIID &id);

      //##ModelId=3BFBAE330345
      HIIDSet & add (const HIIDSet &other);

      //##ModelId=3C1DF87E0288
      HIIDSet & operator += (const HIID &id);

      //##ModelId=3BFBAEDF037E
      HIIDSet & operator += (const HIIDSet &other);

      //##ModelId=3BFBAF14023A
      HIIDSet & remove (const HIIDSet &other);

      //##ModelId=3C1DFB650236
      HIIDSet & remove (const HIID &id);

      //##ModelId=3C1DF89A021A
      HIIDSet & operator -= (const HIID &id);

      //##ModelId=3BFBAF2A01E2
      HIIDSet & operator -= (const HIIDSet &other);

      //##ModelId=3BFBAE650315
      bool contains (const HIID& id) const;

      //##ModelId=3C98CFEF00B6
      //##Documentation
      //## Stores HIID into raw data block
      size_t pack (void *block, size_t &nleft) const;

      //##ModelId=3C98CFEF0110
      void unpack (const void* block, size_t sz);

      //##ModelId=3C98CFEF016A
      //##Documentation
      //## Returns # of bytes required to store the HIID
      size_t packSize () const;

  private:
    // Data Members for Associations

      //##ModelId=3C0F8F6202E1
      set<HIID> contents;

    // Additional Implementation Declarations
    //##ModelId=3DB9343C02E2
      typedef set<HIID>::value_type SVal;
    //##ModelId=3DB9343C0328
      typedef set<HIID>::iterator SI;
    //##ModelId=3DB9343C0382
      typedef set<HIID>::const_iterator CSI;
};

// Class HIIDSet 

//##ModelId=3DB9348D0339
//##ModelId=3C98D01B036C
//##ModelId=3DB92529010A
//##ModelId=3DB925290218
inline HIIDSet::HIIDSet (const void* block, int sz)
{
  unpack(block,sz);
}



//##ModelId=3C1DF87E0288
inline HIIDSet & HIIDSet::operator += (const HIID &id)
{
  return add(id);
}

//##ModelId=3BFBAEDF037E
inline HIIDSet & HIIDSet::operator += (const HIIDSet &other)
{
  return add(other);
}

//##ModelId=3C1DF89A021A
inline HIIDSet & HIIDSet::operator -= (const HIID &id)
{
  return remove(id);
}

//##ModelId=3BFBAF2A01E2
inline HIIDSet & HIIDSet::operator -= (const HIIDSet &other)
{
  return remove(other);
}


#endif

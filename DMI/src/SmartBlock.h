//	f:\lofar\dvl\lofar\cep\cpa\pscf\src

#ifndef SmartBlock_h
#define SmartBlock_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

// Debug
#include "Common/Debug.h"
// CountedRef
#include "DMI/CountedRef.h"
// CountedRefTarget
#include "DMI/CountedRefTarget.h"
#include "CountedRef.h"

//##ModelId=3BEAACAB0041
//##Documentation
//## SmartBlock is a block of bytes with a reference count. Optionally,
//## it can be located in shared memory

class SmartBlock : public CountedRefTarget
{
  public:
    //##ModelId=3BEBD44D0103
      SmartBlock();

      //##ModelId=3BFE299902D7
      //##Documentation
      //## Creates a SmartBlock around an existing chunk of memory. By default,
      //## the memory will not be deleted when the SmartBlock is deleted, unless
      //## the DMI::DELETE (=DMI::ANON) flag is set.
      SmartBlock (void* data, size_t size, int flags = DMI::NO_DELETE);

      //##ModelId=3BFA4FCA0387
      //##Documentation
      //## Allocates a SmartBlock from the heap.
      explicit SmartBlock (size_t size, int flags = 0);

      //##ModelId=3BFE303F0022
      //##Documentation
      //## Creates a SmartBlock in shared memory.
      SmartBlock (size_t size, int shm_flags, int flags);

      //##ModelId=3DB934E50248
      //##Documentation
      //## Cloning copy constructor. Must be called explicitly as Smart
      //## Block(other,DMI::CLONE), throws exception otherwise.
      SmartBlock (const SmartBlock &other, int flags);

    //##ModelId=3DB934E6004B
      ~SmartBlock();


      //##ModelId=3BFE37C3022B
      //##Documentation
      //## Universal initializer. Called from various constructors.
      //## If data=0, then allocates block from heap or shared memory (if
      //## DMI::SHMEM is set in flags); will thow excpeiton if DMI::NO_DELETE
      //## or (=DMI::NON_ANON) is set.
      //## If data!=0, then uses existing block and checks for DMI::DELETE
      //## (=DMI::ANON) in flags to see if it must be deleted.
      void init (void* data, size_t size, int flags, int shm_flags);

      //##ModelId=3C639C340295
      //##Documentation
      //## Resizes block. Old data is copied over as much as possible. If
      //## resizing upwards and DMI::ZERO is specified, the empty space is
      //## filled with 0s.
      void resize (size_t newsize, int flags = 0);

      //##ModelId=3C1E0D8D0391
      void destroy ();

      //##ModelId=3BEBBB480178
      bool isShMem () const;

      //##ModelId=3BFE1E3703DD
      void * operator * ();

      //##ModelId=3BFE1E4600BD
      const void * operator * () const;

      //##ModelId=3BFE23B501F4
      CountedRefTarget * clone (int flags = 0, int depth = 0) const;

    //##ModelId=3DB934E6009B
      const void* data () const;

    //##ModelId=3DB934E60145
      size_t size () const;

    //##ModelId=3DB934E601F0
      int getShmid () const;

    // Additional Public Declarations
    //##ModelId=3DB934E6029A
      void * data ();
      
    //##ModelId=3DB934E60308
      const char * cdata () const
      { return static_cast<const char*>(data()); }
        
    //##ModelId=3DB934E603D0
      char * cdata ()
      { return static_cast<char*>(data()); }
      
    //##ModelId=3DB934E70057
      DefineRefTypes(SmartBlock,Ref);
      
    //##ModelId=3DB934E7024B
      virtual string sdebug ( int detail = 1,const string &prefix = "",
                              const char *name = 0 ) const;
  private:
    //##ModelId=3DB934E802CD
      SmartBlock & operator=(const SmartBlock &right);

  private:
    // Data Members for Class Attributes

      //##ModelId=3BEAACB9029A
      void* block;

      //##ModelId=3BEAACBD0318
      size_t datasize;

      //##ModelId=3BEAACC40281
      int shmid;

      //##ModelId=3BFE1E930399
      bool delete_block;

};

DefineRefTypes(SmartBlock,BlockRef);

class SmartBlock;

//##ModelId=3BEBBB480178
//##Documentation
//## This is a reference to a SmartBlock.

// Class SmartBlock 


inline bool SmartBlock::isShMem () const
{
  return shmid != 0;
}

//##ModelId=3BFE1E3703DD
inline void * SmartBlock::operator * ()
{
  return block;
}

//##ModelId=3BFE1E4600BD
inline const void * SmartBlock::operator * () const
{
  return block;
}

//##ModelId=3DB934E6009B
inline const void* SmartBlock::data () const
{
  return block;
}

//##ModelId=3DB934E60145
inline size_t SmartBlock::size () const
{
  return datasize;
}

//##ModelId=3DB934E601F0
inline int SmartBlock::getShmid () const
{
  return shmid;
}

//##ModelId=3DB934E6029A
inline void * SmartBlock::data ()
{
  return block;
}


//##ModelId=3BEA7FF50154
//##Documentation
//## This is a reference to a SmartBlock.
typedef CountedRef<SmartBlock> BlockRef;

#endif

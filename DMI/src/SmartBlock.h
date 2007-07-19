//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#ifndef DMI_SmartBlock_h
#define DMI_SmartBlock_h 1

#include <TimBase/Debug.h>
#include <DMI/DMI.h>
#include <DMI/CountedRef.h>
#include <DMI/CountedRefTarget.h>

namespace DMI
{    
    
//##ModelId=3BEAACAB0041
//##Documentation
//## SmartBlock is a block of bytes with a reference count. Optionally,
//## it can be located in shared memory

class SmartBlock : public CountedRefTarget
{
  ImportDebugContext(DebugDMI);
  
  public:
    //##ModelId=3BEBD44D0103
      SmartBlock();

      //##ModelId=3BFE299902D7
      //##Documentation
      //## Creates a SmartBlock around an existing chunk of memory. By default,
      //## the memory will not be deleted when the SmartBlock is deleted, unless
      //## the DMI::ANON flag is set.
      SmartBlock (void* data, size_t size, int flags = DMI::EXTERNAL);

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
      //## DMI::SHMEM is set in flags); will thow exception if DMI::EXTERNAL
      //## is set. If data!=0, then uses existing block and checks for 
      //## DMI::ANON in flags to see if it must be deleted.
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
      template<class T>
      const T * pdata () const
      { return static_cast<const T*>(data()); }
    //##ModelId=3DB934E603D0
      template<class T>
      T * pdata ()
      { return static_cast<T*>(data()); }
      
      const char * cdata () const
      { return pdata<char>(); }
      char * cdata () 
      { return pdata<char>(); }
        
      
//       template<class T>
//       T * ptr_cast () 
//       { return static_cast<T*>(data()); }
//       
//       template<class T>
//       const T * const_ptr_cast () const
//       { return static_cast<const T*>(data()); }
//       
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

}; // namespace DMI
#endif

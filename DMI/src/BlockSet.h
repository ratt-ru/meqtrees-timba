//	f:\lofar\dvl\lofar\cep\cpa\pscf\src

#ifndef BlockSet_h
#define BlockSet_h 1

#include "Common.h"
#include <deque>

// SmartBlock
#include "DMI/SmartBlock.h"
#include "BlockRef1.h"

//##ModelId=3BEA80A703A9
//##Documentation
//## A deque of block references.
class BlockSet 
{
  public:
    //##ModelId=3BFA4B6501A7
      BlockSet(const BlockSet &right);

      //##ModelId=3C3EBCBA0082
      explicit BlockSet (int num = 0);

      //##ModelId=3DB934480060
      BlockSet (BlockSet& right, int flags);

    //##ModelId=3DB93448029B
      ~BlockSet();

    //##ModelId=3DB9344802F5
      BlockSet & operator=(const BlockSet &right);


      //##ModelId=3C1E1B0B014A
      int size () const;

      //##ModelId=3C3D854D000C
      void clear ();

      //##ModelId=3C974F800237
      const BlockRef & front () const;

      //##ModelId=3C9F331201C8
      const BlockRef & back () const;

      //##ModelId=3BFA537401F6
      //##Documentation
      //## Removes & returns first reference in set
      BlockRef pop ();

      //##ModelId=3C5AB7F40257
      void pop (BlockRef &out);

      //##ModelId=3BFA56540172
      //##Documentation
      //## Removes n refs from the start of a set, and places them into another
      //## BlockSet
      int popMove (BlockSet& outset, int count);

      //##ModelId=3BFB873E0091
      //##Documentation
      //## Adds a BlockRef to the tail of a BlockSet
      int push (const BlockRef &ref);

      //##ModelId=3C3EB55F00FD
      //##Documentation
      //## Adds copies of all refs in the argument set. The flags parameter is
      //## passed to ref.copy().
      int pushCopy (BlockSet &set, int flags = 0);

      //##ModelId=3C5AA4BF0279
      //##Documentation
      //## Adds copy of argument ref.
      int pushCopy (const BlockRef &ref, int flags = 0);

      //##ModelId=3C5AB3880083
      //##Documentation
      //## Adds an empty ref at the end of the set, and returns a reference to
      //## it.
      BlockRef & pushNew ();

      //##ModelId=3BFB89BE02AB
      //##Documentation
      //## Inserts a BlockRef at the head of the BlockSet
      int pushFront (BlockRef ref);

      //##ModelId=3BFB85F30334
      //##Documentation
      //## Copies all refs in the blockset to BlockSet out. The non-const
      //## version supports the DMI::MAKE_READONLY flag, which willdo the  copy
      //## & make the source set read-only.
      int copyAll (BlockSet &out, int flags = 0) const;

      //##ModelId=3C3EBF410288
      int copyAll (BlockSet &out, int flags = 0);

      //##ModelId=3BFB8A3301D6
      int privatizeAll (int flags = 0);

      //##ModelId=3BFB8E980315
      //##Documentation
      //## Initializes a BlockSet cursor for, e.g., copying a BlockSet to a file
      size_t initCursor ();

      //##ModelId=3BFB8EDC0019
      //##Documentation
      //## Gets maxsize bytes of data from the BlockSet cursor and advances the
      //## cursor. Returns the actual # of bytes retrieved (cursor will stop at
      //## block boundaries) in maxsize
      const void * getCursorData (size_t  &size);

      //##ModelId=3BFB8F5E01E3
      //##Documentation
      //## Destroys refs in the set up to (but not including) the current
      //## cursor position. Returns # of refs destroyed.
      int flushToCursor ();

    // Additional Public Declarations
    //##ModelId=3DB934490076
      BlockRef & operator [] (int i);
    //##ModelId=3DB9344901E8
      const BlockRef & operator [] (int i) const;
      
    //##ModelId=3DB9344903A1
      bool empty () const;
      
      // This is a typical debug() method setup. The sdebug()
      // method creates a debug info string at the given level of detail.
      // If detail<0, then partial info is returned: e.g., for detail==-2,
      // then only level 2 info is returned, without level 0 or 1.
      // Other conventions: no trailing \n; if newlines are embedded
      // inside the string, they are followed by prefix.
      // If class name is not specified, a default one is inserted.
      // It is sometimes useful to have a virtual sdebug(). 
    //##ModelId=3DB9344A009F
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      // The debug() method is an alternative interface to sdebug(),
      // which copies the string to a static buffer (see Debug.h), and returns 
      // a const char *. Thus debug()s can't be nested, while sdebug()s can.
    //##ModelId=3DB9344B0164
      const char * debug ( int detail = 1,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
  private:
    // Additional Private Declarations
    //##ModelId=3DB9343A007C
      typedef deque<BlockRef>::iterator DQI;
    //##ModelId=3DB9343A00EA
      typedef deque<BlockRef>::const_iterator CDQI;
      
    //##ModelId=3DB934460361
      DQI cursor_iter;
    //##ModelId=3DB9344603D8
      size_t cursor_offset;
    //##ModelId=3BF90ECC024E
    deque<BlockRef> refs;

      
    //##ModelId=3DB9344C0238
      size_t cursorSize ()   { return (*cursor_iter)->size(); }
      
  private:
    // Data Members for Associations


};

// Class BlockSet 


//##ModelId=3C1E1B0B014A
inline int BlockSet::size () const
{
  return refs.size();
}

//##ModelId=3C974F800237
inline const BlockRef & BlockSet::front () const
{
  return refs.front();
}

//##ModelId=3C9F331201C8
inline const BlockRef & BlockSet::back () const
{
  return refs.back();
}

//##ModelId=3DB934490076
inline BlockRef & BlockSet::operator [] (int i)
{
  return refs[i];
}

//##ModelId=3DB9344901E8
inline const BlockRef & BlockSet::operator [] (int i) const
{
  return refs[i];
}

//##ModelId=3DB9344903A1
inline bool BlockSet::empty () const
{
  return refs.empty();
}


#endif

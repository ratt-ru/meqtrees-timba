//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC810231.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC810231.cm

//## begin module%3C10CC810231.cp preserve=no
//## end module%3C10CC810231.cp

//## Module: BlockSet%3C10CC810231; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\BlockSet.h

#ifndef BlockSet_h
#define BlockSet_h 1

//## begin module%3C10CC810231.additionalIncludes preserve=no
#include "Common.h"
#include <deque>
//## end module%3C10CC810231.additionalIncludes

//## begin module%3C10CC810231.includes preserve=yes
//## end module%3C10CC810231.includes

// SmartBlock
#include "SmartBlock.h"
//## begin module%3C10CC810231.declarations preserve=no
//## end module%3C10CC810231.declarations

//## begin module%3C10CC810231.additionalDeclarations preserve=yes
//## end module%3C10CC810231.additionalDeclarations


//## begin BlockSet%3BEA80A703A9.preface preserve=yes
//## end BlockSet%3BEA80A703A9.preface

//## Class: BlockSet%3BEA80A703A9
//	A deque of block references.
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class BlockSet 
{
  //## begin BlockSet%3BEA80A703A9.initialDeclarations preserve=yes
  //## end BlockSet%3BEA80A703A9.initialDeclarations

  public:
    //## Constructors (generated)
      BlockSet(const BlockSet &right);

    //## Constructors (specified)
      //## Operation: BlockSet%3BFA4B6501A7
      explicit BlockSet (int num = 0);

      //## Operation: BlockSet%3C3EBCBA0082
      BlockSet (BlockSet& right, int flags);

    //## Destructor (generated)
      ~BlockSet();

    //## Assignment Operation (generated)
      BlockSet & operator=(const BlockSet &right);


    //## Other Operations (specified)
      //## Operation: size%3C1E1B0B014A
      int size () const;

      //## Operation: clear%3C3D854D000C
      void clear ();

      //## Operation: pop%3BFA537401F6
      //	Removes & returns first reference in set
      BlockRef pop ();

      //## Operation: pop%3C5AB7F40257
      void pop (BlockRef &out);

      //## Operation: popMove%3BFA56540172
      //	Removes n refs from the start of a set, and places them into another
      //	BlockSet
      int popMove (BlockSet& outset, int count);

      //## Operation: push%3BFB873E0091
      //	Adds a BlockRef to the tail of a BlockSet
      int push (const BlockRef &ref);

      //## Operation: pushCopy%3C3EB55F00FD
      //	Adds copies of all refs in the argument set. The flags parameter is
      //	passed to ref.copy().
      int pushCopy (BlockSet &set, int flags = 0);

      //## Operation: pushCopy%3C5AA4BF0279
      //	Adds copy of argument ref.
      int pushCopy (const BlockRef &ref, int flags = 0);

      //## Operation: pushNew%3C5AB3880083
      //	Adds an empty ref at the end of the set, and returns a reference to
      //	it.
      BlockRef & pushNew ();

      //## Operation: pushFront%3BFB89BE02AB
      //	Inserts a BlockRef at the head of the BlockSet
      int pushFront (BlockRef ref);

      //## Operation: copyAll%3BFB85F30334
      //	Copies all refs in the blockset to BlockSet out. The non-const
      //	version supports the DMI::MAKE_READONLY flag, which willdo the  copy
      //	& make the source set read-only.
      int copyAll (BlockSet &out, int flags = 0) const;

      //## Operation: copyAll%3C3EBF410288
      int copyAll (BlockSet &out, int flags = 0);

      //## Operation: privatizeAll%3BFB8A3301D6
      int privatizeAll (int flags = 0);

      //## Operation: initCursor%3BFB8E980315
      //	Initializes a BlockSet cursor for, e.g., copying a BlockSet to a file
      size_t initCursor ();

      //## Operation: getCursorData%3BFB8EDC0019
      //	Gets maxsize bytes of data from the BlockSet cursor and advances the
      //	cursor. Returns the actual # of bytes retrieved (cursor will stop at
      //	block boundaries) in maxsize
      const void * getCursorData (size_t  &size);

      //## Operation: flushToCursor%3BFB8F5E01E3
      //	Destroys refs in the set up to (but not including) the current
      //	cursor position. Returns # of refs destroyed.
      int flushToCursor ();

    // Additional Public Declarations
      //## begin BlockSet%3BEA80A703A9.public preserve=yes
      // This is a typical debug() method setup. The sdebug()
      // method creates a debug info string at the given level of detail.
      // If detail<0, then partial info is returned: e.g., for detail==-2,
      // then only level 2 info is returned, without level 0 or 1.
      // Other conventions: no trailing \n; if newlines are embedded
      // inside the string, they are followed by prefix.
      // If class name is not specified, a default one is inserted.
      // It is sometimes useful to have a virtual sdebug(). 
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      // The debug() method is an alternative interface to sdebug(),
      // which copies the string to a static buffer (see Debug.h), and returns 
      // a const char *. Thus debug()s can't be nested, while sdebug()s can.
      const char * debug ( int detail = 1,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
      //## end BlockSet%3BEA80A703A9.public
  protected:
    // Additional Protected Declarations
      //## begin BlockSet%3BEA80A703A9.protected preserve=yes
      //## end BlockSet%3BEA80A703A9.protected

  private:
    // Additional Private Declarations
      //## begin BlockSet%3BEA80A703A9.private preserve=yes
      typedef deque<BlockRef>::iterator DQI;
      typedef deque<BlockRef>::const_iterator CDQI;
      
      DQI cursor_iter;
      size_t cursor_offset;
      
      size_t cursorSize ()   { return (*cursor_iter)->size(); }
      
      //## end BlockSet%3BEA80A703A9.private
  private: //## implementation
    // Data Members for Associations

      //## Association: PSCF::DMI::<unnamed>%3BF90ECB0365
      //## Role: BlockSet::refs%3BF90ECC024E
      //## begin BlockSet::refs%3BF90ECC024E.role preserve=no  private: BlockRef {0..1 -> 0..*VHgN}
      deque<BlockRef> refs;
      //## end BlockSet::refs%3BF90ECC024E.role

    // Additional Implementation Declarations
      //## begin BlockSet%3BEA80A703A9.implementation preserve=yes
      //## end BlockSet%3BEA80A703A9.implementation

};

//## begin BlockSet%3BEA80A703A9.postscript preserve=yes
//## end BlockSet%3BEA80A703A9.postscript

// Class BlockSet 


//## Other Operations (inline)
inline int BlockSet::size () const
{
  //## begin BlockSet::size%3C1E1B0B014A.body preserve=yes
  return refs.size();
  //## end BlockSet::size%3C1E1B0B014A.body
}

//## begin module%3C10CC810231.epilog preserve=yes
//## end module%3C10CC810231.epilog


#endif

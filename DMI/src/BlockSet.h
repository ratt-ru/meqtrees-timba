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

#ifndef DMI_BlockSet_h
#define DMI_BlockSet_h 1

#include <DMI/DMI.h>
#include <DMI/SmartBlock.h>

#include <list>
    
namespace DMI
{
    
//##ModelId=3BEA80A703A9
//##Documentation
//## A deque of block references.
class BlockSet 
{
  private:
      typedef std::list<BlockRef,DMI_Allocator<BlockRef> > BlockList;
  
  public:
      typedef BlockList::const_iterator const_iterator;
      typedef BlockList::iterator iterator;
      
    //##ModelId=3BFA4B6501A7
      //##ModelId=3C3EBCBA0082
      BlockSet ()
      : cursize(0) 
      {}
  
      BlockSet(const BlockSet &right,int flags=0)
      { right.copyAll(*this,flags); }

    //##ModelId=3DB93448029B
      ~BlockSet()
      {}

    //##ModelId=3DB9344802F5
      BlockSet & operator = (const BlockSet &right)
      {
        if( &right != this )
          right.copyAll(*this);
        return *this;
      }
      
      const_iterator begin () const
      { return refs.begin(); }
      iterator begin ()
      { return refs.begin(); }
      const_iterator end () const
      { return refs.end(); }
      iterator end ()
      { return refs.end(); }

      //##ModelId=3C1E1B0B014A
      int size () const
      { return cursize; }

      //##ModelId=3C3D854D000C
      void clear ()
      { refs.clear(); cursize=0;  }

      //##ModelId=3C974F800237
      const BlockRef & front () const
      { return refs.front(); }

      //##ModelId=3C9F331201C8
      const BlockRef & back () const
      { return refs.back(); }

      //##ModelId=3BFA537401F6
      //##Documentation
      //## Removes & returns first reference in set
      BlockRef pop ()
      {
        BlockRef out = refs.front();
        refs.pop_front();
        --cursize;
        return out;
      }

      //##ModelId=3C5AB7F40257
      //## Removes & returns first reference in set via out
      void pop (BlockRef &out)
      {
        out.xfer(refs.front());
        refs.pop_front();
        --cursize;
      }

      //##ModelId=3BFB873E0091
      //##Documentation
      //## Adds a BlockRef to the tail of a BlockSet
      int push (const BlockRef &ref)
      {
        refs.push_back(ref);
        return ++cursize;
      }

      //##ModelId=3C5AA4BF0279
      //##Documentation
      //## Adds with copy flags
      int push (const BlockRef &ref, int flags)
      {
        pushNew().copy(ref,flags);
        return size();
      }

      //##ModelId=3C5AB3880083
      //##Documentation
      //## Adds an empty ref at the end of the set, and returns a reference to
      //## it.
      BlockRef & pushNew ()
      {
        refs.push_back(BlockRef());
        ++cursize;
        return refs.back();
      }

      //##ModelId=3BFB89BE02AB
      //##Documentation
      //## Inserts a BlockRef at the head of the BlockSet
      int pushFront (const BlockRef &ref)
      {
        refs.push_front(ref);
        ++cursize;
        return size();
      }

      //##ModelId=3BFB85F30334
      //##Documentation
      //## Copies all refs in the blockset to BlockSet out. 
      int copyAll (BlockSet &out, int flags = 0) const
      { 
        out.clear(); 
        out.pushCopy(*this,flags); 
        return size(); 
      }
      
      //##ModelId=3BFA56540172
      //##Documentation
      //## Removes n refs from the start of a set, and places them into another
      //## BlockSet
      int popMove (BlockSet& outset, int count);

      //##ModelId=3C3EB55F00FD
      //##Documentation
      //## Adds copies of all refs in the argument set. The flags parameter is
      //## passed to ref.copy().
      int pushCopy (const BlockSet &set, int flags = 0);


      //##ModelId=3BFB8A3301D6
      //## Privatizes all refs in the blockset 
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

//    // Additional Public Declarations
//    //##ModelId=3DB934490076
//      BlockRef & operator [] (int i);
//    //##ModelId=3DB9344901E8
//      const BlockRef & operator [] (int i) const;
      
    //##ModelId=3DB9344903A1
      bool empty () const
      { return refs.empty(); }
      
      // This is a typical debug() method setup. The sdebug()
      // method creates a debug info string at the given level of detail.
      // If detail<0, then partial info is returned: e.g., for detail==-2,
      // then only level 2 info is returned, without level 0 or 1.
      // Other conventions: no trailing \n; if newlines are embedded
      // inside the string, they are followed by prefix.
      // If class name is not specified, a default one is inserted.
      // It is sometimes useful to have a virtual sdebug(). 
    //##ModelId=3DB9344A009F
      string sdebug ( int detail = 0,const string &prefix = "",
                      const char *name = 0 ) const;
      // The debug() method is an alternative interface to sdebug(),
      // which copies the string to a static buffer (see Debug.h), and returns 
      // a const char *. Thus debug()s can't be nested, while sdebug()s can.
    //##ModelId=3DB9344B0164
      const char * debug ( int detail = 0,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
      
      ImportDebugContext(DebugDMI);
      
  private:
    // Additional Private Declarations
      BlockList refs;
      int cursize;
      
    //##ModelId=3DB934460361
      BlockList::iterator cursor_iter;
    //##ModelId=3DB9344603D8
      size_t cursor_offset;
    //##ModelId=3BF90ECC024E
      
    //##ModelId=3DB9344C0238
      size_t cursorSize ()   { return (*cursor_iter)->size(); }
      
};


}; // namespace DMI
#endif

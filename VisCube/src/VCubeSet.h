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

#ifndef VCube_VCubeSet_h
#define VCube_VCubeSet_h 1

#include <DMI/BObj.h>
#include <VisCube/VCube.h>
#include <TimBase/Thread/Mutex.h>
#include <deque>
    
#pragma types #VisCube::VCubeSet

namespace VisCube 
{
using namespace DMI;

//##ModelId=3DB964F2008B
//##Documentation
//## A VCubeSet is (surprise, surprise!) a set of VCubes. (More
//## specifically, it is a double-ended queue.) The class provides some extra
//## functionality not available with regular (e.g. STL) containers:
//## 
//## * thread-safe container;
//## * cubes held via counted refs, so may be shared with other objects;
//## * Derived from DMI::BObj, hence a VCubeSet may be sent in
//## Messages, DMI::Records, BOIO'd to disk, etc.
//## 
//## Counted refs allow for both read-only and read-write containment; a
//## VCubeSet may in fact contain a mix of both. See also the setWritable()
//## method below.
class VCubeSet :  public DMI::BObj
{
  private:
    //##ModelId=3DB964F401EB
    std::deque<VCube::Ref> cubes;
    
    //##ModelId=3DF9FDC90196
    typedef std::deque<VCube::Ref>::iterator CI;
    //##ModelId=3DF9FDC901B2
    typedef std::deque<VCube::Ref>::reverse_iterator RCI;
    //##ModelId=3DF9FDC901CF
    typedef std::deque<VCube::Ref>::const_iterator CCI;
    
    //##ModelId=3DF9FDD1036E
    mutable Thread::Mutex mutex_;

  public:
    //##ModelId=3DB964F401F2
    //##Documentation
    //## Creates empty set
    VCubeSet();

    //##ModelId=3DB964F401F3
    //##Documentation
    //## Copy constructor. By default, all cubes are assigned by reference.
    //## flags and 'depth-1' are passed to CountedRef::copy(), hence
    //## if depth>0 or DMI::DEEP is set, then the cube refs are privatized.
    VCubeSet(const VCubeSet &right,int flags=0,int depth=0);

    //##ModelId=3DB964F401FB
    ~VCubeSet();

    //##ModelId=3DB964F401FC
    //##Documentation
    //## Assignment op. Clears all data from set, then assigns other set by
    //## reference. Equivalent to calling assign() below with default
    //## arguments.
    VCubeSet& operator=(const VCubeSet &right);
      
    //##ModelId=3DC694770211
    //##Documentation
    //## Assignment method, used by copy constructor and operator =.  By
    //## default, all cubes are assigned by reference. 
    //## 'flags' and 'depth-1' are passed to CountedRef::copy(), hence
    //## if depth>0 or DMI::DEEP is set, then the cube refs are privatized.
    void assign (const VCubeSet &other, int flags = 0, int depth = 0);
    
    //##ModelId=3DC6751D0277
    //##Documentation
    //## Returns # of cubes in set
    int ncubes () const
    { return cubes.size(); }
    //##ModelId=3DD4CABF021B
    //##Documentation
    //## Alias for ncubes()
    int size () const
    { return ncubes(); }

    //##ModelId=3DB964F40205
    //##Documentation
    //## Returns cube #icube as a const reference.
    //## A negative icube means count from the back (i.e. -1 = last)
    const VCube & cube (int icube=0) const
    { return cubes[ icube>=0 ? icube : ncubes()-icube ].deref(); }
    //##ModelId=3DB964F4020E
    //##Documentation
    //## Returns cube #icube as a non-const reference. 
    //## A negative icube means count from the back (i.e. -1 = last)
    VCube & wcube (int icube=0) 
    { return cubes[ icube>=0 ? icube : ncubes()-icube ].dewr(); }
      
    //##ModelId=3DB964F40216
    //##Documentation
    //## Same as cube(icube)
    const VCube & operator [] (int icube) const
    { return cube(icube); }
    //##ModelId=3DB964F40220
    //##Documentation
    //## Same as wcube(icube)
    VCube & operator () (int icube = 0) 
    { return wcube(icube); }
      
    //##ModelId=3DD23C430260
    //##Documentation
    //## Adds a cube to the back of the set. Ref is copied.
    void push (const VCube::Ref &ref);
    //##ModelId=3DD23CAB01E6
    //##Documentation
    //## Adds a cube to the front of the set. Ref is copied.
    void pushFront (const VCube::Ref &ref);

    //##ModelId=3DD23C840029
    //##Documentation
    //## Same as push(), but ref is transferred.
    void operator <<= (VCube::Ref &ref);
    //##ModelId=3DD23C930309
    //##Documentation
    //## Attaches an anonymous, read/write ref to cube, and adds it to the back
    //## of the set.
    void operator <<= (VCube* cube);

  
    //##ModelId=3DD23C5A0318
    //##Documentation
    //## Pops a cube from the front of the set. Returns ref to popped cube.
    VCube::Ref pop();
    //##ModelId=3DD23CCB0339
    //##Documentation
    //## Pops a cube from the back of the set. Returns ref to popped cube.
    VCube::Ref popBack();

    //##ModelId=3DD23C720071
    //##Documentation
    //## Pops a cube from the front of the set, and attaches it to the 'out'
    //## ref.
    void pop (VCube::Ref &out);
    //##ModelId=3DD23CDB00C2
    //##Documentation
    //## Pops a cube from the back of the set, and attaches it to the 'out'
    //## ref.
    void popBack (VCube::Ref &out);

    //##ModelId=3DD4C8A5012B
    //##Documentation
    //## Removes cube #icube from the set. Returns ref to removed cube.
    //## A negative icube means count from the back (i.e. -1 = last)
    VCube::Ref remove(int icube);
    //##ModelId=3DD4C8AE03D6
    //##Documentation
    //## Removes cube #icube from the set, and attaches it to the 'out' ref.
    //## A negative icube means count from the back (i.e. -1 = last)
    void remove(int icube, VCube::Ref& out);
    
    // DMI::BObj methods
    //##ModelId=3DC672CA0323
    //##Documentation
    //## Standard clone method
    CountedRefTarget* clone(int flags = 0, int depth = 0) const;

    //##ModelId=3DC672E10339
    //##Documentation
    //## Standard fromBlock method
    int fromBlock(BlockSet& set);
    //##ModelId=3DC672EB001E
    //##Documentation
    //## Standard toBlock method
    int toBlock(BlockSet &set) const;
  
    //##ModelId=3DC672DC028C
    //##Documentation
    //## Returns the class TypeId
    TypeId objectType() const
    { return TpVisCubeVCubeSet; }
    
    //##ModelId=3DF9FDD103C7
    Thread::Mutex & mutex () const
    { return mutex_; }
    
    //##ModelId=3DF9FDD20007
  //##Documentation
  //## standard debug info method, depending on level includes:
  //## 0: class name & object address & # of cubes
  //## 1+: list of cube refs at level-1
    string sdebug ( int detail = 1,const string &prefix = "",
                    const char *name = 0 ) const;
    
    //##ModelId=3DF9FDD200D5
    typedef CountedRef<VCubeSet> Ref;

  private:
      
      
    // implementation of header block for from/toBlock conversions
    //##ModelId=3DF9FDC901EB
    class HeaderBlock : public BObj::Header
    {
      public: int ncubes; 
    };
  
};

};
#endif

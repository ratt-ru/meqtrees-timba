#ifndef VisCube_VisCubeSet_h
#define VisCube_VisCubeSet_h 1

#include "DMI/BlockableObject.h"
#include "VisCube/VisCube.h"
#include "Common/Thread/Mutex.h"

class VisCubeSet;

DefineRefTypes(VisCubeSet,VisCubeSetRef);

#pragma types #VisCubeSet

//##ModelId=3DB964F2008B
//##Documentation
//## A VisCubeSet is (surprise, surprise!) a set of VisCubes. (More
//## specifically, it is a double-ended queue.) The class provides some extra
//## functionality not available with regular (e.g. STL) containers:
//## 
//## * thread-safe container;
//## * cubes held via counted refs, so may be shared with other objects;
//## * Derived from BlockableObject, hence a VisCubeSet may be sent in
//## Messages, DataRecords, BOIO'd to disk, etc.
//## 
//## Counted refs allow for both read-only and read-write containment; a
//## VisCubeSet may in fact contain a mix of both. See also the setWritable()
//## method below.
class VisCubeSet :  public BlockableObject

{
  private:
    //##ModelId=3DB964F401EB
    deque<VisCubeRef> cubes;
    
    //##ModelId=3DF9FDC90196
    typedef deque<VisCubeRef>::iterator CI;
    //##ModelId=3DF9FDC901B2
    typedef deque<VisCubeRef>::reverse_iterator RCI;
    //##ModelId=3DF9FDC901CF
    typedef deque<VisCubeRef>::const_iterator CCI;
    
    //##ModelId=3DF9FDD1036E
    mutable Thread::Mutex mutex_;

  public:
    //##ModelId=3DB964F401F2
    //##Documentation
    //## Creates empty set
    VisCubeSet();

    //##ModelId=3DB964F401F3
    //##Documentation
    //## Copy constructor. By default, all cubes are assigned by reference.
    //## flags and 'depth-1' are passed to CountedRef::copy(), hence:
    //## * if depth>0 or DMI::DEEP is set, then the cube refs are privatized.
    //## * DMI::PRIVATIZE implies a depth of 1.
    VisCubeSet(const VisCubeSet &right,int flags=DMI::PRESERVE_RW,int depth=0);

    //##ModelId=3DB964F401FB
    ~VisCubeSet();

    //##ModelId=3DB964F401FC
    //##Documentation
    //## Assignment op. Clears all data from set, then assigns other set by
    //## reference. Equivalent to calling assign() below with default
    //## arguments.
    VisCubeSet& operator=(const VisCubeSet &right);
      
    //##ModelId=3DC694770211
    //##Documentation
    //## Assignment method, used by copy constructor and operator =.  By
    //## default, all cubes are assigned by reference. 
    //## 'flags' and 'depth-1' are passed to CountedRef::copy(), hence:
    //## * if depth>0 or DMI::DEEP is set, then the cube refs are privatized.
    //## * DMI::PRIVATIZE implies a depth of 1.
    void assign (const VisCubeSet &other, int flags = DMI::PRESERVE_RW, int depth = 0);
    
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
    const VisCube & cube (int icube=0) const
    { return cubes[ icube>=0 ? icube : ncubes()-icube ].deref(); }
    //##ModelId=3DB964F4020E
    //##Documentation
    //## Returns cube #icube as a non-const reference. Will fail if that cube
    //## is held via a read-only ref.
    //## A negative icube means count from the back (i.e. -1 = last)
    VisCube & wcube (int icube=0) const
    { return cubes[ icube>=0 ? icube : ncubes()-icube ].dewr(); }
      
    //##ModelId=3DB964F40216
    //##Documentation
    //## Same as cube(icube)
    const VisCube & operator [] (int icube) const
    { return cube(icube); }
    //##ModelId=3DB964F40220
    //##Documentation
    //## Same as wcube(icube)
    VisCube & operator () (int icube = 0) const
    { return wcube(icube); }
      
    //##ModelId=3DC675980286
    //##Documentation
    //## Sets uniform r/w privileges for all cube refs in the set:
    //## * setWritable(False) will change all cube refs to read-only
    //## * setWritable(True) will go through the set, find all readonly refs,
    //## and privatize them for read-write.
    void setWritable(bool writable = True);
    
    //##ModelId=3DD23C430260
    //##Documentation
    //## Adds a cube to the back of the set. Ref is transferred.
    void push(VisCubeRef ref);
    //##ModelId=3DD23CAB01E6
    //##Documentation
    //## Adds a cube to the front of the set. Ref is transferred.
    void pushFront(VisCubeRef ref);

    //##ModelId=3DD23C840029
    //##Documentation
    //## Same as push(). Ref is transferred.
    void operator <<=(VisCubeRef ref);
    //##ModelId=3DD23C930309
    //##Documentation
    //## Attaches an anonymous, read/write ref to cube, and adds it to the back
    //## of the set.
    void operator <<=(VisCube* cube);

  
    //##ModelId=3DD23C5A0318
    //##Documentation
    //## Pops a cube from the front of the set. Returns ref to popped cube.
    VisCubeRef pop();
    //##ModelId=3DD23CCB0339
    //##Documentation
    //## Pops a cube from the back of the set. Returns ref to popped cube.
    VisCubeRef popBack();

    //##ModelId=3DD23C720071
    //##Documentation
    //## Pops a cube from the front of the set, and attaches it to the 'out'
    //## ref.
    void pop(VisCubeRef &out);
    //##ModelId=3DD23CDB00C2
    //##Documentation
    //## Pops a cube from the back of the set, and attaches it to the 'out'
    //## ref.
    void popBack(VisCubeRef &out);

    //##ModelId=3DD4C8A5012B
    //##Documentation
    //## Removes cube #icube from the set. Returns ref to removed cube.
    //## A negative icube means count from the back (i.e. -1 = last)
    VisCubeRef remove(int icube);
    //##ModelId=3DD4C8AE03D6
    //##Documentation
    //## Removes cube #icube from the set, and attaches it to the 'out' ref.
    //## A negative icube means count from the back (i.e. -1 = last)
    void remove(int icube, VisCubeRef& out);
    
    // BlockableObject methods
    //##ModelId=3DC672CA0323
    //##Documentation
    //## Standard clone method
    CountedRefTarget* clone(int flags = 0, int depth = 0) const;
    //##ModelId=3DC672CE034B
    //##Documentation
    //## Standard privatize method. All refs to cubes are privatized with
    //## depth-1
    virtual void privatize(int flags = 0, int depth = 0);
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
    { return TpVisCubeSet; }
    
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
    DefineRefTypes(VisCubeSet,Ref);

  private:
      
      
    // implementation of header block for from/toBlock conversions
    //##ModelId=3DF9FDC901EB
    typedef struct { int ncubes; } HeaderBlock;
  
    //##ModelId=3DF9FDD1038C
    mutable BlockRef hdrblock; // ref to cached block

};

#endif

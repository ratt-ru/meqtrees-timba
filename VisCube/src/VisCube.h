#ifndef _VisCube_VisCube_h 
#define _VisCube_VisCube_h 1
        
#include "UVD/UVD.h"

#include "VisCube/VisTile.h"
#include "DMI/DataRecord.h"
#include "Common/Thread/Mutex.h"

class VisCube;
#pragma types #VisCube

DefineRefTypes(VisCube,VisCubeRef);

//##ModelId=3DB964F200B3
//##Documentation
//## A VisCube is a set of contiguous VisTiles sharing a common format. Thus,
//## in terms of logical data content, it is simply equivalent to a "larger"
//## VisTile. However, physically it is composed of separate tiles occupying
//## different locations in memory. Tiles are held via CountedRefs, and may be
//## shared and/or passed between cubes. This allows for very efficient
//## concatenation and splitting along the time axis (as long as the splitting
//## is done along tile boundaries). 
//## 
//## All tiles in a cube share a common format object. This object is held via
//## a read-only CountedRef within the cube itself (hence multiple cubes may
//## share the same format object).
//## 
//## Cubes may be writable or read-only, thus determining their data access
//## permissions. This is implemented thorugh read-only and writable
//## CountedRefs to tiles. A writable cube may be downgraded to read-only
//## before passing it to some other part of the program, to insure the
//## contents cannot be changed. A read-only cube can be upgraded to writable
//## by write-privatizing its tile refs, which makes private writable copies
//## where necessary. 
//## 
//## A cube can optionally contain a "header" record. This is a DataRecord
//## meant to hold auxiliary information. (The header is also held via a
//## CountedRef, allowing different cubes to share the same header). The layout
//## of this DataRecord is essentially user-defined, apart from a few
//## predefined fields (correlations, frequencies) directly operated on by some
//## methods of the VisCube class.
//## 
//## A _consolidated_ cube is a VisCube composed of exactly one tile. Note that
//## access to an entire column (where the time axis spans the entire cube) as
//## a contiguous array is only possible within a consolidated cube. The
//## consolidate() method will produce such a cube, by physically concatenating
//## the data in all the tiles. Calling a non-const column accessor for an
//## entire column (or an entire TF-plane) will automatically consolidate a
//## cube. Const accessors, on the other hand, have an "on-the-fly" option,
//## which, when used, produces a temporary array filled with copies of data
//## from the tiles. This requires no consolidation.
//## 
//## TODO: 
//## * Rename non-const accessors with a "w" in them
//## * Do we need a move()/pop() method that moves or pops complete tiles
//##   off a VisCube?
//##
class VisCube : public BlockableObject,
                public VisCubeDebugContext
{
  public:
    //##ModelId=3DB964F200B9
      typedef enum { TOP=0,BOTTOM=1 } Direction;
  
    //##ModelId=3DB964F200BE
      typedef VisTile::Format Format;

  public:
    //##ModelId=3DB964F200C2
    //##Documentation
    //## ConstIterator implements iteration over the time axis in a VisCube.
    //## Functionally, it's just a VisTile::ConstIterator that will
    //## automatically jump from tile to tile. Refer to that class for detailed
    //## documentation.
    //## 
    //## An iterator can hold a CountedRef to a cube, thus guaranteeing
    //## automatic clean-up if the caller releases the cube before destroying
    //## the iterator.
    class ConstIterator : virtual public VisTile::ConstIterator  //## Inherits: <unnamed>%3D805A47024A
    {

      public:
        //##ModelId=3DB964F4035E
        //##Documentation
        //## Creates unattached iterator
          ConstIterator();

        //##ModelId=3DB964F4037B
        //##Documentation
        //## Copy constructor. New iterator will point at same tile, same
        //## position.
          ConstIterator(const ConstIterator &right);

        //##ModelId=3DB964F403C3
        //##Documentation
        //## Initializes iterator for given tile via attach(tile) below.
          ConstIterator (const VisCube& cube);

        //##ModelId=3DB964F50021
        //##Documentation
        //## Initializes iterator for given tile via attach(ref) below.
          ConstIterator (const VisCubeRef &cuberef);

        //##ModelId=3DB964F50068
          ~ConstIterator();

        //##ModelId=3DB964F5007B
        //##Documentation
        //## Assignment. Detaches from current tile( if any) and makes copy of
        //## r.h.s. iterator.
          ConstIterator & operator =(const ConstIterator &right);
          
        //##ModelId=3DD38F1F01E6
        //##Documentation
        //## Comparison operator. Note that all iterators pointing past the end
        //## of a cube (as well as all detached or uninitialized iterators) are
        //## equal.
          bool operator == (const ConstIterator &right);
        //##ModelId=3DD38F1F030F
          bool operator != (const ConstIterator &right);
        //##ModelId=3DD38F20006F
        //##Documentation
        //## Prefix increment, same as calling next()
          ConstIterator & operator ++ ();
        //##ModelId=3DD38F2000CA
        //##Documentation
        //## Postfix increment. !NOTE!: for performance reasons, this is
        //## identical to prefix increment.
          ConstIterator & operator ++ (int);


        //##ModelId=3DB964F500C2
        //##Documentation
        //## Detaches from current cube (if any), then initializes iterator for
        //## start of new cube. It is up to the caller to insure that the cube
        //## object remains valid for the lifetime of the iterator.
          void attach (const VisCube& cube);

        //##ModelId=3DB964F50115
        //##Documentation
        //## Detaches from current cube (if any), then initializes iterator for
        //## new cube, keeping  a copy of the cube ref. The internal ref is
        //## released in the destructor. Tthis insures that the cube object
        //## persists for the lifetime of the iterator even if the caller has
        //## released all other refs to it.
          void attach (const VisCubeRef &cuberef);

        //##ModelId=3DB964F5015E
        //##Documentation
        //## True if iterator has gone past the end of the tile (also when
        //## uninitialized)
          bool end () const;

        //##ModelId=3DB964F50172
        //##Documentation
        //## Advances iterator to next timeslot. Will return true as long as
        //## the iterator has not gone past the end of the cube.
          bool next ();

        //##ModelId=3DB964F50186
        //##Documentation
        //## Resets iterator to first timeslot in cube
          void reset ();

        //##ModelId=3DB964F501F7
        //##Documentation
        //## Detaches iterator from current cube, if any. If cube was attached
        //## via a ref, the ref is released at this point.
          void detach ();
          
        //##Documentation
        //## standard debug info method, depending on level includes:
        //## 0: class name & object address
        //## 1+: iteration position, and current cube at same level
        //## 2+: counted ref (if any) at level 1
          string sdebug ( int detail = 1,const string &prefix = "",
                          const char *name = 0 ) const;
          
          const char * debug ( int detail = 1,const string &prefix = "",
                               const char *name = 0 ) const
          { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

      protected:
        //##ModelId=3DB964F5020B
        //##Documentation
        //## internal method: jumps to tile #it, returns True if it's valid
          bool attachTile (int it);
      
        //##ModelId=3DB964F5025C
        //##Documentation
        //## internal method: attaches to cube and inits everything
          void attachCube (VisCube *cube);
          
        //##ModelId=3DB964F402E6
        //##Documentation
        //## counted ref to cube (not always supplied, since the iterator can
        //## refer to the cube via pointer only)
          VisCubeRef cuberef;

        //##ModelId=3DB964F4031C
        //##Documentation
        //## pointer to cube
          VisCube *pcube;
      
        //##ModelId=3DB964F40327
          int itile;
          
        // index of timeslot within cube
          int icubetime;
          
        //##Documentation
        //## keep cube locked while iterating
          Thread::Mutex::Lock cubelock;
          
      private:
        //##Documentation
        //## This hides the base class' attach() methods
          VisTile::ConstIterator::attach;
    };

    //##ModelId=3DB964F200C4
    //##Documentation
    //## A writable iterator. All write-accessor from VisTile::Iterator are
    //## inherited here.
    //## This Iterator may only be attached to a non-const, writable cube. 
    class Iterator : virtual public ConstIterator, //## Inherits: <unnamed>%3D89D3ED01AB
                     	public VisTile::Iterator  //## Inherits: <unnamed>%3D89D3F10298
    {

      public:
        //##ModelId=3DB964F50306
          Iterator();

        //##ModelId=3DB964F50319
          Iterator(const Iterator &right);

        //##ModelId=3DB964F5035C
          Iterator (VisCube& cube);

        //##ModelId=3DB964F503A1
          Iterator (const VisCubeRef &cuberef);

        //##ModelId=3DB964F503E4
          ~Iterator();

        //##ModelId=3DB964F60011
          Iterator & operator=(const Iterator &right);

        //##ModelId=3DB964F60053
          void attach (VisCube& cube);

        //##ModelId=3DB964F60099
          void attach (const VisCubeRef &cuberef);
          
        // override this from VisTile because we cache the times
          void setTime (double x) const;

        //## standard debug info method, see ConstIterator above
          string sdebug ( int detail = 1,const string &prefix = "",
                          const char *name = 0 ) const
          { return ConstIterator::sdebug(detail,prefix,name?name:"I{VisCube}"); }
          
          const char * debug ( int detail = 1,const string &prefix = "",
                               const char *name = 0 ) const
          { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

      protected:
        // Additional Protected Declarations

      private:
        // Additional Private Declarations
        //##ModelId=3DB964F502C8
        //##Documentation
        //## This hides the base class' attach() methods
//          ConstIterator::attach;
          VisTile::Iterator::attach;

    };
    
    typedef ConstIterator const_iterator;
    typedef Iterator iterator;

    //##ModelId=3DB964F60138
    //##Documentation
    //## Creates uninitialized cube with no data or format
    VisCube();

  //##ModelId=3DB964F60139
    //##Documentation
    //## Initializes a cube with a default format, for nc correlations by nf
    //## frequency channels. 
    //## If nt>0, allocates a number of tiles as follows: if tilesize>0 (and a
    //## factor of nt, else fails), sets up nt/tilesize tiles. If tilesize=0,
    //## sets up a single tile of nt timeslots.
    VisCube (int nc, int nf, int nt = 0, int tilesize = 0);
  //##ModelId=3DB964F603A9
    //##Documentation
    //## Initializes a cube with the specified format. A read-only copy of the
    //## ref is made to keep the format (hence different cubes can share the
    //## same format object). See above for meaning of nt and tilesize.
    VisCube (const Format::Ref &form, int nt = 0,int tilesize = 0);

  //##ModelId=3DB964F603D0
    //##Documentation
    //## Copy constructor. Depth and flags are used as follows:
    //## * refs to tiles are copied with the supplied flags and depth-1.
    //##   Thus with depth=0 (default), tile copy is by-reference only. With
    //##   depth>0 or DMI::DEEP or DMI::PRIVATIZE, tile copy is by-value.
    //## * ref to header record is copied with the supplied flags and depth-2.
    //##   Hence with depth<2, header record is copied by reference.
    //##   You need to specify a depth of at least 2 (or DMI::DEEP) to
    //##   copy the top-level record by-value.
    VisCube (const VisCube &right, int flags = DMI::PRESERVE_RW, int depth = 0);

  //##ModelId=3DD374F4021E
    //##Documentation
    //## Makes a copy of a subset of another cube, from timeslot it0 to
    //## timeslot it0+nt-1 (or to end of cube, if nt<0). Partial tile segments,
    //## if any, are copied by value (that is, new tiles are created). Whole
    //## tiles (as well as the header record, if any) are copied by reference 
    //## or by value, as determined by flags and depth. 
    //## See copy constructor (above) for details.
    VisCube (const VisCube &right, int flags, int depth, int it0, int nt = -1);

  //##ModelId=3DB964F60194
    ~VisCube();

  //##ModelId=3DB964F60195
    //##Documentation
    //## Assignment op. Clears data from cube (if any), and assigns other cube
    //## by reference. Equivalent to the copy constructor with flags
    //## DMI::PRESERVE_RW and depth=0.
    VisCube & operator=(const VisCube &right);


    //##ModelId=3DB964F601A3
    //##Documentation
    //## Clears all old data from cube, then initializes a cube with a default
    //## format, for nc correlations by nf frequency channels. 
    //## If nt>0, allocates a number of tiles as follows: if tilesize>0 (and a
    //## factor of nt, else fails), sets up nt/tilesize tiles. If tilesize=0,
    //## sets up a single tile of nt timeslots.
    void init (int nc, int nf, int nt = 0, int tilesize = 0);

    //##ModelId=3DB964F7002B
    //##Documentation
    //## Clears all old data from cube, then initializes a cube with the
    //## specified format. See above for meaning of nt and tilesize.
    void init (const Format::Ref &form, int nt = 0, int tilesize = 0);
    
  //##ModelId=3DB964F601FE
    //##Documentation
    //## True if cube is initialized (i.e. has format)
    bool initialized () const;

    // Additional Public Declarations
    // returns # of tiles
  //##ModelId=3DB964F70029
    //##Documentation
    //## Returns the number of tiles in the cube
    int ntiles () const;
    
  //##ModelId=3DB964F60201
    //##Documentation
    //## returns # of correlations
    int ncorr () const;

  //##ModelId=3DB964F60203
    //##Documentation
    //## returns # of frequency channels
    int nfreq () const;

  //##ModelId=3DB964F60205
    //##Documentation
    //## returns # of timeslots
    int ntime () const;

  //##ModelId=3DB964F60207
    //##Documentation
    //## Returns the type of the icorr'th correlation. This is a shortcut to a
    //## predefined field in the header record.
    int corrtype (int icorr) const;

  //##ModelId=3DB964F60216
    //##Documentation
    //## Returns a const vector of frequencies. This is a shortcut to a
    //## predefined field in the header record.
    const LoVec_double & freq () const;
    //##ModelId=3DB964F60218
    //##Documentation
    //## Returns a writable vector of frequencies. This is a shortcut to a
    //## predefined field in the header record.
    LoVec_double & freq ();

  //##ModelId=3DCBD28D03AD
    //##Documentation
    //## Returns the ichan'th frequency
    double freq (int ichan) const;

  //##ModelId=3DB964F602F0
    //##Documentation
    //## Consolidates cube by concatenating all tiles into one big tile
    void consolidate () const;

  //##ModelId=3DB964F602F2
    //##Documentation
    //## Removes nt timeslots from the top (where = VisCube::TOP, default) or
    //## bottom (VisCube::BOTTOM) of the cube.
    void pop (int nt, int where = VisCube::TOP);

  //##ModelId=3DB964F6030C
    //##Documentation
    //## Copies part of other cube (timeslots it0 through it0+nt-1, or through
    //## end of cube if nt<0) and appends it to the bottom (default) or top
    //## (where=VisCube::TOP) of the cube. Partial tiles are copied by value
    //## (that is, new tiles are allocated to hold the data). Whole tiles
    //## are copied by reference, unless the DMI::DEEP or DMI::PRIVATIZE flag
    //## is specified.
    //## The formats of both cubes must be compatible, unless this cube is
    //## uninitialized, in which case it is initialized with the format of the
    //## other cube.
    void append (const VisCube &other, int it0 = 0, int nt = -1, int where = VisCube::BOTTOM, int flags = DMI::PRESERVE_RW );

  //##ModelId=3DB964F60367
    //##Documentation
    //## Adds tile to bottom (default) or top (where=VisCube::TOP) of cube.
    //## Tile ref is taken over.
    void push (VisTileRef &tileref, int where = VisCube::BOTTOM);

  //##ModelId=3DB964F60382
    //##Documentation
    //## Extends a cube by adding nt timeslots at the bottom (default) or top
    //## (where=VisCube::TOP). if tilesize>0 (and a factor of nt, else fails),
    //## adds up nt/tilesize tiles. If tilesize=0, adds a single tile of nt
    //## timeslots.
    void grow (int nt, int tilesize = 0, int where = VisCube::BOTTOM);

  //##ModelId=3DB964F70052
    //##Documentation
    //## Returns the format of the cube. Note that a format cannot be
    //## manipulated directly (rather attached or changed as a whole), hence
    //## only const accessors are defined.
    const Format & format () const;
    // format by reference
  //##ModelId=3DB964F70054
    //##Documentation
    //## Returns a read-only CountedRef to the format object.
    Format::Ref formatRef () const;

  //##ModelId=3DB964F70056
    //##Documentation
    //## True if cube has a header record attached
    bool hasHeader () const;
  //##ModelId=3DB964F70058
    //##Documentation
    //## Const accessor to header record
    const DataRecord & header () const;
  //##ModelId=3DB964F7005A
    //##Documentation
    //## Non-const accessor to header record
    DataRecord & wheader ();
  //##ModelId=3DB964F7005C
    //##Documentation
    //## Returns a CountedRef to the header record. A copy of the internal ref
    //## is made, using the specified flags.
    DataRecordRef headerRef (int flags=0) const;
    // sets complete header
  //##ModelId=3DB964F7006A
    //##Documentation
    //## Attaches a header record. The existing record (if any) is detached. A
    //## copy is made of the supplied ref.
    void setHeader (const DataRecordRef &href);

    //##ModelId=3DC270F9002D
    //##Documentation
    //## True if cube is writable
    bool isWritable() const;
    //##ModelId=3DC271C20007
    //##Documentation
    //## Upgrades cube to writable (write=True) or downgrades to read-only
    //## (write=False). When upgrading, tiles and header will be privatized for
    //## writing (see CountedRef for an explanation).
    void setWritable(bool write = True);

    //##ModelId=3DD38C3E01E6
    //##Documentation
    //## Returns a const iterator pointing at the beginning of the tile. If
    //## flags are non-0 (which is default), the iterator will be attached to
    //## the tile via a counted ref constructed with the specified flags.
    ConstIterator begin(int flags = DMI::READONLY|DMI::ANON) const;

    //##ModelId=3DD38C7D01B2
    //##Documentation
    //## Like const begin(). but returns a non-const iterator.
    Iterator begin(int flags = DMI::ANONWR);

    //##ModelId=3DD38C96021F
    //##Documentation
    //## Returns an STL-style "end" iterator  (actually just an invalid
    //## iterator), which gives "true" when compared with an iterator that has
    //## gone beyond the end of a tile.
    const ConstIterator & end() const;

    // standard BlockableObject implementation follows
  //##ModelId=3DB964F70078
    //##Documentation
    //## converts cube to blockset
    int toBlock   (BlockSet& set) const;
  //##ModelId=3DB964F70086
    //##Documentation
    //## converts cube from blockset
    int fromBlock (BlockSet& set);
  //##ModelId=3DB964F70094
    //##Documentation
    //## Privatizes the cube:
    //## (1) The writable property is set according to the DMI::WRITE bit in
    //## flags. 
    //## (2) If depth>=1 (or DMI::DEEP is set), privatizes all tile refs. This
    //## insures private copies of all data.
    //## (3) If depth>=2 (or DMI::DEEP is set), privatizes the header record to
    //## a depth of depth-2.
    void privatize (int flags,int depth);
  //##ModelId=3DB964F700AF
    //##Documentation
    //## Clones the cube. Flags and depth are passed to the copy constructor
    //## (see above).
    CountedRefTarget * clone (int flags = 0, int depth = 0) const;

  //##ModelId=3DB964F700CB
    TypeId objectType () const
    { return TpVisCube; }
    
    //##Documentation
    //## Mutex for cube ops
    Thread::Mutex & mutex () const;
    
  //##Documentation
  //## standard debug info method, depending on level includes:
  //## 0: class name & object address
  //## 1: # of timeslots & # of tiles & format @level 1
  //## 2+: format @level2, list of tile refs @level -1, header at level -1 
    string sdebug ( int detail = 1,const string &prefix = "",
                    const char *name = 0 ) const;
    
    DefineRefTypes(VisCube,Ref);

  private:
    // Column caches. This is used for on-the-fly consolidation.
    // That is, when a cube is non-consolidated, and a
    // column accessor is called that requires contiguous data, _and_ the
    // on-the-fly flag is set, then rather than consolidating the tiles,
    // a full array is created, cached here, and returned.
    //##ModelId=3DCBD28C0060
    mutable LoCube_fcomplex  datacube;
    //##ModelId=3DCBD28C0178
    mutable LoCube_int       flagcube;
    //##ModelId=3DCBD28C028D
    mutable LoMat_double     uvwmatrix;
    //##ModelId=3DCBD28D00D8
    mutable LoVec_float      weightvec;
    //##ModelId=3DCBD28D01F1
    mutable LoVec_int        rowflagvec;
    
#ifndef LORRAYS_USE_BLITZ
  #error VisCube requires Blitz arrays
#endif
    // Define templated helper methods for column accessors 
    // These templates here take advantage of Blitz features, hence the 
    // check above.
    
    // Gets const column, using either on-the-fly concatenation or
    // auto-consolidation
    template<class T,int N>
    const blitz::Array<T,N> & getTiledArray (bool on_the_fly,
        blitz::Array<T,N> &cache,
        const blitz::Array<T,N> & (VisTile::*accessor)() const) const;
        
    // Gets column using auto-consolidation
    template<class T,int N>
    blitz::Array<T,N> & getTiledArray (blitz::Array<T,N> &cache,
        blitz::Array<T,N> & (VisTile::*accessor)());
    
    // Gets element at row IT of scalar column
    template<class T>
    T getTileElement (
        const blitz::Array<T,1> & (VisTile::*accessor)() const,int it) const;
    
    // Gets slice at row IT of array column
    template<class T,int N>
    blitz::Array<T,(N-1)> getTileElement(
        const blitz::Array<T,N> & (VisTile::*accessor)() const,int it) const;
    
    // Sets element at row IT of scalar column
    template<class T>
    void setTileElement (
        blitz::Array<T,1> & (VisTile::*accessor)(),
        int it,T value);
    
    // Sets slice at row IT of array column
    template<class T,int N>
    void setTileElement (blitz::Array<T,N> & (VisTile::*accessor)(),
              int it,const blitz::Array<T,N-1> &value);
    
    // helper templates for implementations -- using a single template
    // of <class T,int N> and providing partial specializations just wouldn't 
    // work for me :-(
    template<class T>
    static blitz::Array<T,1> reduceIndex (const blitz::Array<T,2> &arr,int it);
    template<class T>
    static blitz::Array<T,2> reduceIndex (const blitz::Array<T,3> &arr,int it);
    template<class T>
    static blitz::Array<T,3> reduceIndex (const blitz::Array<T,4> &arr,int it);
    
  public:
    // Column accessor section. When new columns are defined, accessors
    // should be added here following the same pattern. For every column,
    // four accessors are defined:
      
    // * <name>Col(): const accessor to entire column, with a "bool on_the_fly"
    //    parameter (default false). If cube is non-conasolidated, then an 
    //    array is constructed & filled on-the-fly (o_t_f = true), else cube 
    //    is consolidated first.
    // * <name>Col(): non-const accessor to entire column. Cube will always
    //    be consolidated first.
    // * <name>(it):  returns cell at row #it
    // * set<Name>(it,value): sets value of cell at row #it
    //
    // The DATA and FLAGS columns have some extra accessors defined (see below).
    // The TIME column is also somewhat special (see below).
      
  //##ModelId=3DD100FB02D8
    const LoCube_fcomplex & dataCol (bool on_the_fly = False) const
            { return getTiledArray(on_the_fly,datacube,&VisTile::data); }
    //##ModelId=3DD100FC0079
    LoCube_fcomplex & wdataCol ()   // will auto-consolidate
            { return getTiledArray(datacube,&VisTile::wdata); }
    //##ModelId=3DD100FC00DD
    LoMat_fcomplex data (int it) const
            { return getTileElement(&VisTile::data,it); }
    //##ModelId=3DD100FC026C
    void setData (int it,const LoMat_fcomplex &value)
            { setTileElement(&VisTile::wdata,it,value); }
    
    //##ModelId=3DD100FD00D7
    const LoCube_int & flagsCol (bool on_the_fly = False) const
            { return getTiledArray(on_the_fly,flagcube,&VisTile::flags); }
    //##ModelId=3DD100FD0274
    LoCube_int & wflagsCol ()              // will auto-consolidate
            { return getTiledArray(flagcube,&VisTile::wflags); }
   //##ModelId=3DD100FD02DE
    LoMat_int flags (int it) const
            { return getTileElement(&VisTile::flags,it); }
    //##ModelId=3DD100FE009B
    void setFlags (int it,const LoMat_int &value)
            { setTileElement(&VisTile::wflags,it,value); } 

    //##ModelId=3DD100FE0309
    const LoMat_double & uvwCol (bool on_the_fly = False) const
            { return getTiledArray(on_the_fly,uvwmatrix,&VisTile::uvw); }
    //##ModelId=3DD100FF00D2
    LoMat_double & wuvwCol ()     // will auto-consolidate
            { return getTiledArray(uvwmatrix,&VisTile::wuvw); }
   //##ModelId=3DD100FF0141
    LoVec_double uvw (int it) const
            { return getTileElement(&VisTile::uvw,it); }
    //##ModelId=3DD100FF02BC
    void setUvw (int it,const LoVec_double &value)
            { setTileElement(&VisTile::wuvw,it,value); }

    //##ModelId=3DD101000160
    const LoVec_float & weightCol (bool on_the_fly = False) const
            { return getTiledArray(on_the_fly,weightvec,&VisTile::weight); }
    //##ModelId=3DD101000324
    LoVec_float & wweightCol ()   // will auto-consolidate
            { return getTiledArray(weightvec,&VisTile::wweight); }
    //##ModelId=3DD101000398
    float weight (int it) const
            { return getTileElement(&VisTile::weight,it); }
    //##ModelId=3DD10101017E
    void setWeight (int it,float value) 
            { setTileElement(&VisTile::wweight,it,value); }

  //##ModelId=3DD101020083
    const LoVec_int & rowflagCol (bool on_the_fly = False) const
            { return getTiledArray(on_the_fly,rowflagvec,&VisTile::rowflag); }
    //##ModelId=3DD10102025C
    LoVec_int & wrowflagCol ()   // will auto-consolidate
            { return getTiledArray(rowflagvec,&VisTile::wrowflag); }
  //##ModelId=3DD1010202D8
    int rowflag (int it) const
            { return getTileElement(&VisTile::rowflag,it); }
    //##ModelId=3DD1010300D3
    void setRowflag (int it,int value) 
            { setTileElement(&VisTile::wrowflag,it,value); }
    
    // Timeslots are somewhat special because they are always cached 
    // inside the cube itself. Therefore,
    // no writable time() vector is provided, instead, you must always
    // use the setTime() method to set the times.
  //##ModelId=3DD101040006
    const LoVec_double & time () const;
  //##ModelId=3DD1010400CB
    double time (int it) const;
  //##ModelId=3DD1010402BE
    void setTime (const LoVec_double &tm);
  //##ModelId=3DD101050085
    void setTime (int it, double tm);
    
// Extra TF-plane accessors for flags & data. These return a temporary 
// array object (rather than making use of any cache)
    
// I've disabled the const on-the-fly version for now, while I think of an
// elegant implementation
//    
//    //##ModelId=3DD10105036C
//    const LoMat_fcomplex tfData (int icorr = 0,bool on_the_fly = False) const;
//    //##ModelId=3DD101070096
//    const LoMat_int tfFlags (int icorr = 0,bool on_the_fly = False) const;

    //##ModelId=3DD10105036C
    LoMat_fcomplex tfData (int icorr = 0); // will auto-consolidate
    //##ModelId=3DD101070096
    LoMat_int tfFlags (int icorr = 0);  // will auto-consolidate
    
  private:
    //##ModelId=3DD100F80278
    //##Documentation
    //## ref to cube header record
      DataRecordRef header_;
  
    //##ModelId=3DD100F8035F
    //##Documentation
    //## Container of tile refs
      mutable deque<VisTileRef> tiles;
    // typedefs for iterators over the tile vector
    //##ModelId=3DD100F7017B
      typedef deque<VisTileRef>::iterator TI;
    //##ModelId=3DD100F70206
      typedef deque<VisTileRef>::const_iterator CTI;
    //##ModelId=3DD100F90358
    //##Documentation
    //## Index: timeslot -> tile #
      mutable vector<int> ts_index;
    //##ModelId=3DD100FA00A2
    //##Documentation
    //## Index: tile # -> # of first timeslot
      mutable vector<int> ts_offset;
      
    //##ModelId=3DD100F90096
    //##Documentation
    //## read-only ref to cube format
      Format::Ref format_;
    
    //##ModelId=3DD100FA03E7
    //##Documentation
    //## is the cube writable?
      bool writable_;
    
    //##ModelId=3DD100F90181
    //##Documentation
    //## # of correlations
      int ncorr_;
    //##ModelId=3DD100F9026C
    //##Documentation
    //## # of frequency channels
      int nfreq_;
      
    //##ModelId=3DD100FA01C9
    //##Documentation
    //## Cache of timeslots (actual timestamp values)
      LoVec_double timeslots;
      
    //##ModelId=3DD100FA02B9
    //##Documentation
    //## If cube is regularly tiled (i.e. all tiles have the same size), then
    //## this is the tile size. If =0, then cube is not regularly tiled.
      int regular_tiling;   
      
      // accessors to tiles correspondint to timeslots
    //##ModelId=3DD1010801CA
    //##Documentation
    //## Helper method -- returns tile corresponding to timeslot it.
      const VisTile & tile (int it) const
      { return tiles[ts_index[it]].deref(); }
      
    //##ModelId=3DD10109004C
    //##Documentation
    //## Helper method -- returns tile corresponding to timeslot it.
      VisTile & tile (int it) 
      { return tiles[ts_index[it]].dewr(); }
      
      // helper method for copy constructor and operator=
    //##ModelId=3DD10109026A
    //##Documentation
    //## Helper method used by copy constructor and assignment op.
    //## See copy constructor for meaning of flags
      void assign (const VisCube &right,int flags,int depth);
          
      // recomputes all tile indices. Called whenever the tiling structure changes
    //##ModelId=3DD1010A0340
    //##Documentation
    //## Recomputes tile indices and cached times. Called after every update of
    //## the cube structure.
      void setupIndexing ();
      
//       // templated helper to retrieve a single element form a subtile
//       template<class T>
//       T getTileElement (int icol,int it,T* =0) const
//       {
//         int itile = ts_index[it];
//         return tiles[itile]->getElement(icol,it-ts_offset[itile],(T*)0);
//       }
//       
//       // templated helper to assign a single element form a subtile
//       template<class T>
//       T setTileElement (int icol,int it,T value)
//       {
//         int itile = ts_index[it];
//         return tiles[itile]().setElement(icol,it - ts_offset[itile],value);
//       }
//       
//       // templated helper to retrieve a full column
//       template<class T>
//       Array<T> getTiledArray (int icol,bool no_consolidate);
      
      
      
      // Header structure for from/toblock operations
    //##ModelId=3DD100F7026C
      typedef struct { int ntiles; bool hasformat,hasheader; } HeaderBlock;
      // cached block
    //##ModelId=3DD100FA03AE
      mutable BlockRef hdrblock;
      
    //##Documentation
    //## Mutex for cube ops
      mutable Thread::Mutex mutex_;
};

//##ModelId=3DD38F1F01E6

// Class VisCube::Iterator 
//##ModelId=3DD38F1F01E6
inline bool VisCube::ConstIterator::operator == (const ConstIterator &right)
{
  if( end() && right.end() )
    return True;
  return pcube == right.pcube && itile == right.itile &&
        VisTile::ConstIterator::operator == (right);
}

//##ModelId=3DD38F1F030F
inline bool VisCube::ConstIterator::operator != (const ConstIterator &right)
{
  return ! ( (*this) == right );
}

//##ModelId=3DD38F20006F
inline VisCube::ConstIterator & VisCube::ConstIterator::operator ++ ()
{
  next();
  return *this;
}

//##ModelId=3DD38F2000CA
inline VisCube::ConstIterator & VisCube::ConstIterator::operator ++ (int)
{
  next();
  return *this;
}
          
//##ModelId=3DB964F5015E
inline bool VisCube::ConstIterator::end () const
{
  return !pcube || itile >= pcube->ntiles();
}

//##ModelId=3DB964F50172
inline bool VisCube::ConstIterator::next ()
{
  icubetime++;
  if( !VisTile::ConstIterator::next() ) // advance tile iter
    return attachTile(itile+1);
  return True;
}

inline void VisCube::Iterator::setTime (double x) const
{
  VisTile::Iterator::setTime(x);
  pcube->timeslots(icubetime) = x;
}

// Class VisCube 


//##ModelId=3DB964F601FE
inline bool VisCube::initialized () const
{
  // cube is considered initialized when we have a valid format
  return format_.valid();
}

//##ModelId=3DB964F60201
inline int VisCube::ncorr () const
{
  return ncorr_;
}

//##ModelId=3DB964F60203
inline int VisCube::nfreq () const
{
  return nfreq_;
}

//##ModelId=3DB964F60205
inline int VisCube::ntime () const
{
  return ts_index.size();
}

//##ModelId=3DB964F60207
inline int VisCube::corrtype (int icorr) const
{
  return header_.deref()[AidCorr][icorr];
}

//##ModelId=3DB964F60216
inline const LoVec_double & VisCube::freq () const
{
// Have to add Lorrays to DMI first:
//  return header_.deref()[AidFreq];
  static LoVec_double dum;
  return dum;  
}

//##ModelId=3DB964F60218
inline LoVec_double & VisCube::freq () 
{
// Have to add Lorrays to DMI first:
//  return header_.deref()[AidFreq];
  static LoVec_double dum;
  return dum;  
}

//##ModelId=3DCBD28D03AD
inline double VisCube::freq (int ichan) const
{
  return header_.deref()[AidFreq][ichan];
}

//##ModelId=3DD101040006
inline const LoVec_double & VisCube::time () const
{
  return timeslots;
}

//##ModelId=3DD1010400CB
inline double VisCube::time (int it) const
{
  return timeslots(it);
}

// inline const VDSID& VisCube::vdsid () const
// {
//   //## begin VisCube::vdsid%3D91BD520232.get preserve=no
//   return vdsid_;
//   //## end VisCube::vdsid%3D91BD520232.get
// }
// 

//##ModelId=3DB964F70029
inline int VisCube::ntiles () const
{
  return static_cast<int>(tiles.size());
}

// accessors for format. Always const, since the format can only be
// changed via add/removeColumn
//##ModelId=3DB964F70052
inline const VisCube::Format & VisCube::format () const
{
  return *format_;
}
// format by reference
//##ModelId=3DB964F70054
inline VisCube::Format::Ref VisCube::formatRef () const
{
  return format_.copy(DMI::READONLY);
}

// accessors for header
// do we have a header?
//##ModelId=3DB964F70056
inline bool VisCube::hasHeader () const
{
  return header_.valid();
}

// const access to header record
//##ModelId=3DB964F70058
inline const DataRecord & VisCube::header () const
{
  return *header_;
}

// non-const access
//##ModelId=3DB964F7005A
inline DataRecord & VisCube::wheader ()
{
  return header_();
}

// access by ref
//##ModelId=3DB964F7005C
inline DataRecordRef VisCube::headerRef (int flags) const
{
  if( !flags )
    flags = DMI::PRESERVE_RW;
  return header_.copy(flags);
}

// sets complete header
//##ModelId=3DB964F7006A
inline void VisCube::setHeader (const DataRecordRef &href)
{
  header_.unlock().copy(href,DMI::PRESERVE_RW).lock();
}

//##ModelId=3DC270F9002D
inline bool VisCube::isWritable() const
{
    return writable_;
}

//##ModelId=3DD38C3E01E6
inline VisCube::ConstIterator VisCube::begin (int flags) const
{
  return flags ? ConstIterator(VisCubeRef(this,flags)) : ConstIterator(*this);
}

//##ModelId=3DD38C7D01B2
inline VisCube::Iterator VisCube::begin (int flags)
{
  FailWhen( !isWritable(),"r/w access violation" );
  return flags ? Iterator(VisCubeRef(this,flags)) : Iterator(*this);
}

//##ModelId=3DD38C96021F
inline const VisCube::ConstIterator & VisCube::end () const
{
  // return an iterator that is invalid by default
  static ConstIterator dum; 
  return dum;
}

// Gets element at row IT of scalar column
template<class T>
inline T VisCube::getTileElement (
    const blitz::Array<T,1> & (VisTile::*accessor)() const,int it) const
{
  int itile = ts_index[it];
  return (tiles[itile].deref().*accessor)()(it - ts_offset[itile]);
}

template<class T>
inline blitz::Array<T,1> VisCube::reduceIndex (const blitz::Array<T,2> &arr,int it)
{
  return arr(blitz::Range::all(),it);
}

template<class T>
inline blitz::Array<T,2> VisCube::reduceIndex (const blitz::Array<T,3> &arr,int it)
{
  return arr(blitz::Range::all(),blitz::Range::all(),it);
}

template<class T>
inline blitz::Array<T,3> VisCube::reduceIndex (const blitz::Array<T,4> &arr,int it)
{ 
  return arr(blitz::Range::all(),blitz::Range::all(),blitz::Range::all(),it);
}
  
// Gets slice at row IT of array column
template<class T,int N>
inline blitz::Array<T,N-1> VisCube::getTileElement (
    const blitz::Array<T,N> & (VisTile::*accessor)() const,int it ) const
{
  int itile = ts_index[it];
  return reduceIndex( (tiles[itile].deref().*accessor)(),it - ts_offset[itile] );
}

// Sets element at row IT of scalar column
template<class T>
inline void VisCube::setTileElement (
    blitz::Array<T,1> & (VisTile::*accessor)(),
    int it,T value)
{
  int itile = ts_index[it];
  blitz::Array<T,1> &vec = (tiles[itile].dewr().*accessor)();
  vec(it - ts_offset[itile]) = value;
}

// Sets slice at row IT of array column
template<class T,int N>
inline void VisCube::setTileElement (
          blitz::Array<T,N> & (VisTile::*accessor)(),
          int it,const blitz::Array<T,N-1> &value)
{
  int itile = ts_index[it];
  reduceIndex( (tiles[itile].dewr().*accessor)(),it - ts_offset[itile] ) = value; 
}
    

inline Thread::Mutex & VisCube::mutex () const
{ 
  return mutex_; 
}

#endif

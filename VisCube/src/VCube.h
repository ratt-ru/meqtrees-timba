//#  VCube.h: a cube of visibilities
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef _VCube_VCube_h 
#define _VCube_VCube_h 1
        
#include <TimBase/Thread/Mutex.h>
#include <DMI/Record.h>
#include <VisCube/VTile.h>
#include <VisCube/AID-VisCube.h>
#include <deque>

#pragma types #VisCube::VCube
#pragma aid Corr Freq

namespace VisCube 
{
using namespace DMI;

//##ModelId=3DB964F200B3
//##Documentation
//## A VCube is a set of contiguous VTiles sharing a common format. Thus,
//## in terms of logical data content, it is simply equivalent to a "larger"
//## VTile. However, physically it is composed of separate tiles occupying
//## different locations in memory. Tiles are held via CountedRefs, and may be
//## shared and/or passed between cubes. This allows for very efficient
//## concatenation and splitting along the time axis (as long as the splitting
//## is done along tile boundaries). 
//## 
//## All tiles in a cube share a common format object. This object is held via
//## a CountedRef within the cube itself (hence multiple cubes may share the 
//## same format object).
//## 
//## Tiles are held via regular copy-on-write references, and thus are copied
//## only when needed.
//## 
//## A cube can optionally contain a "header" record. This is a DMI::Record
//## meant to hold auxiliary information. (The header is also held via a
//## CountedRef, allowing different cubes to share the same header). The layout
//## of this DMI::Record is essentially user-defined, apart from a few
//## predefined fields (correlations, frequencies) directly operated on by some
//## methods of the VCube class.
//## 
//## A _consolidated_ cube is a VCube composed of exactly one tile. Note that
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
//##   off a VCube?
//##
class VCube : public DMI::BObj
{
  public:
    //##ModelId=3DB964F200B9
      typedef enum { TOP=0,BOTTOM=1 } Direction;
  
    //##ModelId=3DB964F200BE
      typedef VTile::Format Format;

  public:
    //##ModelId=3DB964F200C2
    //##Documentation
    //## ConstIterator implements iteration over the time axis in a VCube.
    //## Functionally, it's just a VTile::ConstIterator that will
    //## automatically jump from tile to tile. Refer to that class for detailed
    //## documentation.
    //## 
    //## An iterator can hold a CountedRef to a cube, thus guaranteeing
    //## automatic clean-up if the caller releases the cube before destroying
    //## the iterator.
    class ConstIterator : virtual public VTile::ConstIterator  //## Inherits: <unnamed>%3D805A47024A
    {

      public:
        //##ModelId=3DB964F4035E
        //##Documentation
        //## Creates unattached iterator
          ConstIterator();

        //##ModelId=3DB964F4037B
        //##Documentation
        //## Copy constructor. New iterator will point at same cube, same
        //## position.
          ConstIterator(const ConstIterator &right);

        //##ModelId=3DB964F403C3
        //##Documentation
        //## Initializes iterator for given cube via attach(cube) below.
          ConstIterator (const VCube& cube,int flags=0);

        //##ModelId=3DB964F50068
          ~ConstIterator();

        //##ModelId=3DB964F5007B
        //##Documentation
        //## Assignment. Detaches from current cube (if any) and makes copy of
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
        //## start of new cube. A ref is attached to the object to ensure that
        //## it remains valid through the lifetime of the iterator.
          void attach (const VCube& cube,int flags=0);

        //##ModelId=3DB964F5015E
        //##Documentation
        //## true if iterator has gone past the end of the tile (also when
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
          
        //##ModelId=3DF9FDCD02BB
        //##Documentation
        //## standard debug info method, depending on level includes:
        //## 0: class name & object address
        //## 1+: iteration position, and current cube at same level
        //## 2+: counted ref (if any) at level 1
          string sdebug ( int detail = 1,const string &prefix = "",
                          const char *name = 0 ) const;
          
        //##ModelId=3DF9FDCE0117
          const char * debug ( int detail = 1,const string &prefix = "",
                               const char *name = 0 ) const
          { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

      protected:
        //##ModelId=3DB964F5020B
        //##Documentation
        //## internal method: jumps to tile #it, returns true if it's valid
          bool attachTile (int it);
      
        //##ModelId=3DB964F5025C
        //##Documentation
        //## internal method: attaches to cube and inits everything
          void attachCube (VCube *cube,int flags);
          
        //##ModelId=3DB964F402E6
        //##Documentation
        //## counted ref to cube 
          VCube::Ref cuberef;

        //##ModelId=3DB964F4031C
        //##Documentation
        //## pointer to cube
          VCube *pcube;
      
        //##ModelId=3DB964F40327
          int itile;
          
        // index of timeslot within cube
        //##ModelId=3DF9FDCD01FA
          int icubetime;
          
        //##ModelId=3DF9FDCD02A2
        //##Documentation
        //## keep cube locked while iterating
          Thread::Mutex::Lock cubelock;
          
      private:
        //##ModelId=400E51D501F0
        //##Documentation
        //## This hides the base class' attach() methods
          void attach (const VTile &tile);
    };

    //##ModelId=3DB964F200C4
    //##Documentation
    //## A writable iterator. All write-accessor from VTile::Iterator are
    //## inherited here.
    //## This Iterator may only be attached to a non-const, writable cube. 
    class Iterator : virtual public ConstIterator, //## Inherits: <unnamed>%3D89D3ED01AB
                     	public VTile::Iterator  //## Inherits: <unnamed>%3D89D3F10298
    {

      public:
        //##ModelId=3DB964F50306
          Iterator();

        //##ModelId=3DB964F50319
          Iterator(const Iterator &right);

        //##ModelId=3DB964F5035C
          Iterator (VCube& cube,int flags=0);

        //##ModelId=3DB964F503E4
          ~Iterator();

        //##ModelId=3DB964F60011
          Iterator & operator=(const Iterator &right);

        //##ModelId=3DB964F60053
          void attach (VCube& cube,int flags=0);
          
        // override this from VTile because we cache the times
        //##ModelId=3DF9FDCF0000
          void setTime (double x) const;

        //##ModelId=3DF9FDCF0081
        //## standard debug info method, see ConstIterator above
          string sdebug ( int detail = 1,const string &prefix = "",
                          const char *name = 0 ) const
          { return ConstIterator::sdebug(detail,prefix,name?name:"I{VCube}"); }
          
        //##ModelId=3DF9FDCF01B7
          const char * debug ( int detail = 1,const string &prefix = "",
                               const char *name = 0 ) const
          { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

      protected:
        // Additional Protected Declarations

      private:
        // Additional Private Declarations to hide base class methods
        //##ModelId=400E51D600B5
          void attach (const VTile &tile,int);
        //##ModelId=400E51D601C3
          void attach (const VCube &cube,int);
    };
    
    //##ModelId=3DF9FDC900FF
    typedef ConstIterator const_iterator;
    //##ModelId=3DF9FDC90144
    typedef Iterator iterator;

    //##ModelId=3DB964F60138
    //##Documentation
    //## Creates uninitialized cube with no data or format
    VCube();

  //##ModelId=3DB964F60139
    //##Documentation
    //## Initializes a cube with a default format, for nc correlations by nf
    //## frequency channels. 
    //## If nt>0, allocates a number of tiles as follows: if tilesize>0 (and a
    //## factor of nt, else fails), sets up nt/tilesize tiles. If tilesize=0,
    //## sets up a single tile of nt timeslots.
    VCube (int nc, int nf, int nt = 0, int tilesize = 0);
  //##ModelId=3DB964F603A9
    //##Documentation
    //## Initializes a cube with the specified format. A read-only copy of the
    //## ref is made to keep the format (hence different cubes can share the
    //## same format object). See above for meaning of nt and tilesize.
    VCube (const Format::Ref &form, int nt = 0,int tilesize = 0);

  //##ModelId=3DD374F4021E
    //##Documentation
    //## Copy constructor. Depth and flags are used as follows:
    //## * refs to tiles are copied with the supplied flags and depth-1.
    //##   Thus with depth=0 (default), tile copy is by-reference only. With
    //##   DMI::DEEP, tile copy is by-value.
    //## * ref to header record is copied with the supplied flags and depth-2.
    //##   Hence with depth<2, header record is copied by reference.
    //##   You need to specify a depth of at least 2 (or DMI::DEEP) to
    //##   copy the top-level record by-value.
    VCube (const VCube &right, int flags=0,int depth=0);

  //##ModelId=3DB964F603D0
    //##Documentation
    //## Makes a copy of a subset of another cube, from timeslot it0 to
    //## timeslot it0+nt-1 (or to end of cube, if nt<0). Partial tile segments,
    //## if any, are copied by value (that is, new tiles are created). Whole
    //## tiles (as well as the header record, if any) are copied by reference 
    //## or by value, as determined by flags and depth. 
    //## See copy constructor (above) for details.
    VCube (const VCube &right, int flags, int depth, int it0, int nt = -1);

  //##ModelId=3DB964F60194
    ~VCube();

  //##ModelId=3DB964F60195
    //##Documentation
    //## Assignment op. Clears data from cube (if any), and assigns other cube
    //## by reference. Equivalent to the copy constructor with 0 flags and depth.
    VCube & operator=(const VCube &right);


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
    //## true if cube is initialized (i.e. has format)
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
    //## Removes nt timeslots from the top (where = VCube::TOP, default) or
    //## bottom (VCube::BOTTOM) of the cube.
    void pop (int nt, int where = VCube::TOP);

  //##ModelId=3DB964F6030C
    //##Documentation
    //## Copies part of other cube (timeslots it0 through it0+nt-1, or through
    //## end of cube if nt<0) and appends it to the bottom (default) or top
    //## (where=VCube::TOP) of the cube. Partial tiles are copied by value
    //## (that is, new tiles are allocated to hold the data). Whole tiles
    //## are copied by reference, unless the DMI::DEEP flag is specified.
    //## The formats of both cubes must be compatible, unless this cube is
    //## uninitialized, in which case it is initialized with the format of the
    //## other cube.
    void append (const VCube &other, int it0 = 0, int nt = -1, int where = VCube::BOTTOM, int flags = 0 );

  //##ModelId=3DB964F60367
    //##Documentation
    //## Adds tile to bottom (default) or top (where=VCube::TOP) of cube.
    //## Tile ref is copied
    void push (const VTile::Ref &tileref, int where = VCube::BOTTOM);

  //##ModelId=3DB964F60382
    //##Documentation
    //## Extends a cube by adding nt timeslots at the bottom (default) or top
    //## (where=VCube::TOP). if tilesize>0 (and a factor of nt, else fails),
    //## adds up nt/tilesize tiles. If tilesize=0, adds a single tile of nt
    //## timeslots.
    void grow (int nt, int tilesize = 0, int where = VCube::BOTTOM);

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
    //## true if cube has a header record attached
    bool hasHeader () const;
  //##ModelId=3DB964F70058
    //##Documentation
    //## Const accessor to header record
    const DMI::Record & header () const;
  //##ModelId=3DB964F7005A
    //##Documentation
    //## Non-const accessor to header record
    DMI::Record & wheader ();
  //##ModelId=3DB964F7005C
    //##Documentation
    //## Returns a CountedRef to the header record. A copy of the internal ref
    //## is made, using the specified flags.
    DMI::Record::Ref headerRef (int flags=0) const;
    // sets complete header
  //##ModelId=3DB964F7006A
    //##Documentation
    //## Attaches a header record. The existing record (if any) is detached. A
    //## copy is made of the supplied ref.
    void setHeader (const DMI::Record::Ref &href);

    //##ModelId=3DD38C3E01E6
    //##Documentation
    //## Returns a const iterator pointing at the beginning of the tile. If
    //## flags are non-0 (which is default), the iterator will be attached to
    //## the tile via a counted ref constructed with the specified flags.
    ConstIterator begin(int flags = 0) const;

    //##ModelId=3DD38C7D01B2
    //##Documentation
    //## Like const begin(). but returns a non-const iterator.
    Iterator begin(int flags = 0);

    //##ModelId=3DD38C96021F
    //##Documentation
    //## Returns an STL-style "end" iterator  (actually just an invalid
    //## iterator), which gives "true" when compared with an iterator that has
    //## gone beyond the end of a tile.
    const ConstIterator & end() const;

    // standard DMI::BObj implementation follows
  //##ModelId=3DB964F70078
    //##Documentation
    //## converts cube to blockset
    int toBlock   (BlockSet& set) const;
  //##ModelId=3DB964F70086
    //##Documentation
    //## converts cube from blockset
    int fromBlock (BlockSet& set);
    
  //##ModelId=3DB964F700AF
    //##Documentation
    //## Clones the cube. Flags and depth are passed to the copy constructor
    //## (see above).
    CountedRefTarget * clone (int flags = 0, int depth = 0) const;

  //##ModelId=3DB964F700CB
    TypeId objectType () const
    { return TpVisCubeVCube; }
    
    //##ModelId=3DF9FDD00141
    //##Documentation
    //## Mutex for cube ops
    Thread::Mutex & mutex () const;
    
    //##ModelId=3DF9FDD001AB
  //##Documentation
  //## standard debug info method, depending on level includes:
  //## 0: class name & object address
  //## 1: # of timeslots & # of tiles & format @level 1
  //## 2+: format @level2, list of tile refs @level -1, header at level -1 
    string sdebug ( int detail = 1,const string &prefix = "",
                    const char *name = 0 ) const;
    
    //##ModelId=3DF9FDD003B3
    typedef CountedRef<VCube> Ref;

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
  #error VCube requires Blitz arrays
#endif
    // Define templated helper methods for column accessors 
    // These templates here take advantage of Blitz features, hence the 
    // check above.
    
    // Gets const column, using either on-the-fly concatenation or
    // auto-consolidation
    template<class T,int N>
    const blitz::Array<T,N> & getTiledArray (bool on_the_fly,
        blitz::Array<T,N> &cache,
        const blitz::Array<T,N> & (VTile::*accessor)() const) const;
        
    // Gets column using auto-consolidation
    template<class T,int N>
    blitz::Array<T,N> & getTiledArray (blitz::Array<T,N> &cache,
        blitz::Array<T,N> & (VTile::*accessor)());
    
    // Gets element at row IT of scalar column
    template<class T>
    T getTileElement (
        const blitz::Array<T,1> & (VTile::*accessor)() const,int it) const;
    
    // Gets slice at row IT of array column
    template<class T,int N>
    blitz::Array<T,(N-1)> getTileElement(
        const blitz::Array<T,N> & (VTile::*accessor)() const,int it) const;
    
    // Sets element at row IT of scalar column
    template<class T>
    void setTileElement (
        blitz::Array<T,1> & (VTile::*accessor)(),
        int it,T value);
    
    // Sets slice at row IT of array column
    template<class T,int N>
    void setTileElement (blitz::Array<T,N> & (VTile::*accessor)(),
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
    const LoCube_fcomplex & dataCol (bool on_the_fly = false) const
            { return getTiledArray(on_the_fly,datacube,&VTile::data); }
    //##ModelId=3DF9FDD100E2
    LoCube_fcomplex & wdataCol ()   // will auto-consolidate
            { return getTiledArray(datacube,&VTile::wdata); }
    //##ModelId=3DD100FC00DD
    LoMat_fcomplex data (int it) const
            { return getTileElement(&VTile::data,it); }
    //##ModelId=3DD100FC026C
    void setData (int it,const LoMat_fcomplex &value)
            { setTileElement(&VTile::wdata,it,value); }
    
    //##ModelId=3DD100FD00D7
    const LoCube_int & flagsCol (bool on_the_fly = false) const
            { return getTiledArray(on_the_fly,flagcube,&VTile::flags); }
    //##ModelId=3DF9FDD10127
    LoCube_int & wflagsCol ()              // will auto-consolidate
            { return getTiledArray(flagcube,&VTile::wflags); }
   //##ModelId=3DD100FD02DE
    LoMat_int flags (int it) const
            { return getTileElement(&VTile::flags,it); }
    //##ModelId=3DD100FE009B
    void setFlags (int it,const LoMat_int &value)
            { setTileElement(&VTile::wflags,it,value); } 

    //##ModelId=3DD100FE0309
    const LoMat_double & uvwCol (bool on_the_fly = false) const
            { return getTiledArray(on_the_fly,uvwmatrix,&VTile::uvw); }
    //##ModelId=3DF9FDD1016C
    LoMat_double & wuvwCol ()     // will auto-consolidate
            { return getTiledArray(uvwmatrix,&VTile::wuvw); }
   //##ModelId=3DD100FF0141
    LoVec_double uvw (int it) const
            { return getTileElement(&VTile::uvw,it); }
    //##ModelId=3DD100FF02BC
    void setUvw (int it,const LoVec_double &value)
            { setTileElement(&VTile::wuvw,it,value); }

    //##ModelId=3DD101000160
    const LoCube_float & weightCol (bool on_the_fly = false) const
            { return getTiledArray(on_the_fly,weight,&VTile::weight); }
    //##ModelId=3DF9FDD101DD
    LoVec_float & wweightCol ()   // will auto-consolidate
            { return getTiledArray(weightvec,&VTile::wweight); }
    //##ModelId=3DD101000398
    float weight (int it) const
            { return getTileElement(&VTile::weight,it); }
    //##ModelId=3DD10101017E
    void setWeight (int it,float value) 
            { setTileElement(&VTile::wweight,it,value); }

  //##ModelId=3DD101020083
    const LoVec_int & rowflagCol (bool on_the_fly = false) const
            { return getTiledArray(on_the_fly,rowflagvec,&VTile::rowflag); }
    //##ModelId=3DF9FDD10223
    LoVec_int & wrowflagCol ()   // will auto-consolidate
            { return getTiledArray(rowflagvec,&VTile::wrowflag); }
  //##ModelId=3DD1010202D8
    int rowflag (int it) const
            { return getTileElement(&VTile::rowflag,it); }
    //##ModelId=3DD1010300D3
    void setRowflag (int it,int value) 
            { setTileElement(&VTile::wrowflag,it,value); }
    
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
//    const LoMat_fcomplex tfData (int icorr = 0,bool on_the_fly = false) const;
//    //##ModelId=3DD101070096
//    const LoMat_int tfFlags (int icorr = 0,bool on_the_fly = false) const;

    //##ModelId=3DD10105036C
    LoMat_fcomplex tfData (int icorr = 0); // will auto-consolidate
    //##ModelId=3DD101070096
    LoMat_int tfFlags (int icorr = 0);  // will auto-consolidate
    
  private:
    //##ModelId=3DD100F80278
    //##Documentation
    //## ref to cube header record
      DMI::Record::Ref header_;
  
    //##ModelId=3DD100F8035F
    //##Documentation
    //## Container of tile refs
      mutable std::deque<VTile::Ref> tiles;
    // typedefs for iterators over the tile vector
    //##ModelId=3DD100F7017B
      typedef std::deque<VTile::Ref>::iterator TI;
    //##ModelId=3DD100F70206
      typedef std::deque<VTile::Ref>::const_iterator CTI;
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
      const VTile & tile (int it) const
      { return tiles[ts_index[it]].deref(); }
      
    //##ModelId=3DD10109004C
    //##Documentation
    //## Helper method -- returns tile corresponding to timeslot it.
      VTile & tile (int it) 
      { return tiles[ts_index[it]].dewr(); }
      
      // helper method for copy constructor and operator=
    //##ModelId=3DD10109026A
    //##Documentation
    //## Helper method used by copy constructor and assignment op.
    //## See copy constructor for meaning of flags
      void assign (const VCube &right,int flags,int depth);
          
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
      class HeaderBlock : public BObj::Header
      {
        public: int ntiles; 
                bool hasformat;
                bool hasheader; 
      };
      
    //##ModelId=3DF9FDCF02FC
    //##Documentation
    //## Mutex for cube ops
      mutable Thread::Mutex mutex_;
};

//##ModelId=3DD38F1F01E6

// Class VCube::Iterator 
//##ModelId=3DD38F1F01E6
inline bool VCube::ConstIterator::operator == (const ConstIterator &right)
{
  if( end() && right.end() )
    return true;
  return pcube == right.pcube && itile == right.itile &&
        VTile::ConstIterator::operator == (right);
}

//##ModelId=3DD38F1F030F
inline bool VCube::ConstIterator::operator != (const ConstIterator &right)
{
  return ! ( (*this) == right );
}

//##ModelId=3DD38F20006F
inline VCube::ConstIterator & VCube::ConstIterator::operator ++ ()
{
  next();
  return *this;
}

//##ModelId=3DD38F2000CA
inline VCube::ConstIterator & VCube::ConstIterator::operator ++ (int)
{
  next();
  return *this;
}
          
//##ModelId=3DB964F5015E
inline bool VCube::ConstIterator::end () const
{
  return !pcube || itile >= pcube->ntiles();
}

//##ModelId=3DB964F50172
inline bool VCube::ConstIterator::next ()
{
  icubetime++;
  if( !VTile::ConstIterator::next() ) // advance tile iter
    return attachTile(itile+1);
  return true;
}

//##ModelId=3DF9FDCF0000
inline void VCube::Iterator::setTime (double x) const
{
  VTile::Iterator::set_time(x);
  pcube->timeslots(icubetime) = x;
}

// Class VCube 


//##ModelId=3DB964F601FE
inline bool VCube::initialized () const
{
  // cube is considered initialized when we have a valid format
  return format_.valid();
}

//##ModelId=3DB964F60201
inline int VCube::ncorr () const
{
  return ncorr_;
}

//##ModelId=3DB964F60203
inline int VCube::nfreq () const
{
  return nfreq_;
}

//##ModelId=3DB964F60205
inline int VCube::ntime () const
{
  return ts_index.size();
}

//##ModelId=3DB964F60207
inline int VCube::corrtype (int icorr) const
{
  return header_[AidCorr][icorr];
}

//##ModelId=3DB964F60216
inline const LoVec_double & VCube::freq () const
{
// Have to add Lorrays to DMI first:
//  return header_.deref()[AidFreq];
  static LoVec_double dum;
  return dum;  
}

//##ModelId=3DB964F60218
inline LoVec_double & VCube::freq () 
{
// Have to add Lorrays to DMI first:
//  return header_.deref()[AidFreq];
  static LoVec_double dum;
  return dum;  
}

//##ModelId=3DCBD28D03AD
inline double VCube::freq (int ichan) const
{
  return header_[AidFreq][ichan];
}

//##ModelId=3DD101040006
inline const LoVec_double & VCube::time () const
{
  return timeslots;
}

//##ModelId=3DD1010400CB
inline double VCube::time (int it) const
{
  return timeslots(it);
}

// inline const VDSID& VCube::vdsid () const
// {
//   //## begin VCube::vdsid%3D91BD520232.get preserve=no
//   return vdsid_;
//   //## end VCube::vdsid%3D91BD520232.get
// }
// 

//##ModelId=3DB964F70029
inline int VCube::ntiles () const
{
  return int(tiles.size());
}

// accessors for format. Always const, since the format can only be
// changed via add/removeColumn
//##ModelId=3DB964F70052
inline const VCube::Format & VCube::format () const
{
  return *format_;
}
// format by reference
//##ModelId=3DB964F70054
inline VCube::Format::Ref VCube::formatRef () const
{
  return format_;
}

// accessors for header
// do we have a header?
//##ModelId=3DB964F70056
inline bool VCube::hasHeader () const
{
  return header_.valid();
}

// const access to header record
//##ModelId=3DB964F70058
inline const DMI::Record & VCube::header () const
{
  return *header_;
}

// non-const access
//##ModelId=3DB964F7005A
inline DMI::Record & VCube::wheader ()
{
  return header_();
}

// access by ref
//##ModelId=3DB964F7005C
inline DMI::Record::Ref VCube::headerRef (int flags) const
{
  return header_.copy(flags);
}

// sets complete header
//##ModelId=3DB964F7006A
inline void VCube::setHeader (const DMI::Record::Ref &href)
{
  header_.unlock().copy(href).lock();
}

//##ModelId=3DD38C3E01E6
inline VCube::ConstIterator VCube::begin (int flags) const
{
  return ConstIterator(*this,flags);
}

//##ModelId=3DD38C7D01B2
inline VCube::Iterator VCube::begin (int flags)
{
  return Iterator(*this,flags);
}

//##ModelId=3DD38C96021F
inline const VCube::ConstIterator & VCube::end () const
{
  // return an iterator that is invalid by default
  static ConstIterator dum; 
  return dum;
}

// Gets element at row IT of scalar column
template<class T>
inline T VCube::getTileElement (
    const blitz::Array<T,1> & (VTile::*accessor)() const,int it) const
{
  int itile = ts_index[it];
  return (tiles[itile].deref().*accessor)()(it - ts_offset[itile]);
}

template<class T>
inline blitz::Array<T,1> VCube::reduceIndex (const blitz::Array<T,2> &arr,int it)
{
  return arr(blitz::Range::all(),it);
}

template<class T>
inline blitz::Array<T,2> VCube::reduceIndex (const blitz::Array<T,3> &arr,int it)
{
  return arr(blitz::Range::all(),blitz::Range::all(),it);
}

template<class T>
inline blitz::Array<T,3> VCube::reduceIndex (const blitz::Array<T,4> &arr,int it)
{ 
  return arr(blitz::Range::all(),blitz::Range::all(),blitz::Range::all(),it);
}
  
// Gets slice at row IT of array column
template<class T,int N>
inline blitz::Array<T,N-1> VCube::getTileElement (
    const blitz::Array<T,N> & (VTile::*accessor)() const,int it ) const
{
  int itile = ts_index[it];
  return reduceIndex( (tiles[itile].deref().*accessor)(),it - ts_offset[itile] );
}

// Sets element at row IT of scalar column
template<class T>
inline void VCube::setTileElement (
    blitz::Array<T,1> & (VTile::*accessor)(),
    int it,T value)
{
  int itile = ts_index[it];
  blitz::Array<T,1> &vec = (tiles[itile].dewr().*accessor)();
  vec(it - ts_offset[itile]) = value;
}

// Sets slice at row IT of array column
template<class T,int N>
inline void VCube::setTileElement (
          blitz::Array<T,N> & (VTile::*accessor)(),
          int it,const blitz::Array<T,N-1> &value)
{
  int itile = ts_index[it];
  reduceIndex( (tiles[itile].dewr().*accessor)(),it - ts_offset[itile] ) = value; 
}
    

//##ModelId=3DF9FDD00141
inline Thread::Mutex & VCube::mutex () const
{ 
  return mutex_; 
}

};

#endif

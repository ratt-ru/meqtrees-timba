#ifndef VisCube_VisTile_h
#define VisCube_VisTile_h 1

#define HAVE_BLITZ 1
    
// ColumnarTableTile
#include "VisCube/ColumnarTableTile.h"
    
#include "Common/Lorrays.h"
#include "Common/Thread/Mutex.h"
#include "DMI/TypeInfo.h"



// check for sanity
#if !LORRAYS_USE_BLITZ && !LORRAYS_USE_AIPSPP
  #error No array support defined
#endif
#if LORRAYS_USE_BLITZ && LORRAYS_USE_AIPSPP
  #error Conflicting array support defined
#endif
    
class VisTile;
class VisCube;
#pragma aidgroup VisCube
#pragma type #VisTile

DefineRefTypes(VisTile,VisTileRef);


//##ModelId=3DB964F200EE
//##Documentation
//## VisTile represents one tile (= a number of contiguous timeslots) of
//## visibility data. 
//## VisTile is essentially a ColumnarTableTile with a predefined format. This
//## format defines at least the following columns:
//## 
//## TIME      (double)
//## DATA      (Ncorr x Nfreq fcomplex)
//## FLAGS     (Ncorr x Nfreq int)
//## ROWFLAG   (int)
//## UVW       (3 doubles)
//## WEIGHT    (float)
//## 
//## Accessors methods to column data in array format are provided, as well as
//## iterators.
//## 
//## Note that each tile usually has an associated VisTile::Format (=
//## TableFormat) object. This object is not part of the tile itself (for
//## example, in a VisCube, all tiles share the same format object), and must
//## be explictitly attached to a tile before any column-wise accessors are
//## called.
class VisTile : public ColumnarTableTile  //## Inherits: <unnamed>%3D9978030166
{
  public:
    //##ModelId=3DB964F200F4
    //##Documentation
    //## This enum lists all the possible columns in a visibility dataset.
      typedef enum {
        TIME = 0,
        DATA,
        FLAGS,
        ROWFLAG,
        UVW,
        WEIGHT,
            
        MAXCOL
      } Columns;
        
    friend class VisCube;
    
  public:
    //##ModelId=3DB964F200F9
    //##Documentation
    //## ConstIterator implements iteration over the time axis in a VisTile,
    //## and provides const accessor methods to the data cells for each
    //## timeslot. STL-like semantics are supported:
    //## 
    //## for( VisTile::ConstIterator iter = mytile.begin();     
    //##     iter != mytile.end();
    //##     iter++ )
    //## 
    //## ...as well as alternative iteration methods (see next(), end(),
    //## reset()). An iterator can also hold a CountedRef to a tile, thus
    //## guaranteeing automatic clean-up if the caller releases the tile before
    //## destroying the iterator.
    //## 
    //## Note that for performance reasons, accessors to array columns (data,
    //## flags, uvw) will return sub-arrays that reference the original data.
    //## Theoretically, this can be abused to violate constness, but such
    //## behaviour is severely discouraged and will be persecuted to the full
    //## extent of negative peer pressure.
    class ConstIterator : public VisCubeDebugContext
    {

      public:
        //##ModelId=3DB964F701E6
        //##Documentation
        //## Creates unattached iterator
          ConstIterator();

        //##ModelId=3DB964F701FA
        //##Documentation
        //## Copy constructor. New iterator will point at same tile, same
        //## position.
          ConstIterator(const ConstIterator &right);

        //##ModelId=3DB964F70241
        //##Documentation
        //## Initializes iterator for given tile via attach(tile) below.
          ConstIterator (const VisTile &tile);

        //##ModelId=3DB964F70288
        //##Documentation
        //## Initializes iterator for given tile via attach(ref) below.
          ConstIterator (const VisTileRef &ref);

        //##ModelId=3DB964F702D0
        //##Documentation
        //## Assignment. Detaches from current tile( if any) and makes copy of
        //## r.h.s. iterator.
          ConstIterator & operator=(const ConstIterator &right);
          
          ~ConstIterator();

        //##ModelId=3DD25CA501CD
        //##Documentation
        //## Comparison operator. Note that all iterators pointing past the end
        //## of a tile (as well as all detached or uninitialized iterators) are
        //## equal.
          bool operator == (const ConstIterator &right);
        //##ModelId=3DD25CB20000
          bool operator != (const ConstIterator &right);
        //##ModelId=3DD25CC20012
        //##Documentation
        //## Prefix increment, same as calling next()
          ConstIterator & operator ++ ();
        //##ModelId=3DD25CD90071
        //##Documentation
        //## Postfix increment. !NOTE!: for performance reasons, this is
        //## identical to prefix increment.
          ConstIterator & operator ++ (int);

        //##ModelId=3DB964F70322
        //##Documentation
        //## Detaches from current tile (if any), then initializes iterator for
        //## start of new tile. It is up to the caller to insure that the tile
        //## object remains valid for the lifetime of the iterator.
          void attach (const VisTile &tile);

        //##ModelId=3DB964F70368
        //##Documentation
        //## Detaches from current tile (if any), then initializes iterator for
        //## new tile, keeping  a copy of the tile ref. The internal ref is
        //## released in the destructor. Tthis insures that the tile object
        //## persists for the lifetime of the iterator even if the caller has
        //## released all other refs to it.
          void attach (const VisTileRef &ref);

        //##ModelId=3DB964F703B0
        //##Documentation
        //## Data accessors. Returns data column for current iteration time.
          LoMat_fcomplex data () const;

        //##ModelId=3DB964F703C5
          LoVec_fcomplex fData (int icorr = 0) const;

        //##ModelId=3DB964F80025
          LoMat_int flags () const;

        //##ModelId=3DB964F8003A
          LoVec_int fFlags (int icorr = 0) const;

        //##ModelId=3DB964F80094
          double time () const;

        //##ModelId=3DB964F800A9
          int rowflag () const;

        //##ModelId=3DB964F800BD
          LoVec_double uvw () const;

        //##ModelId=3DB964F800D2
          float weight () const;

        //##ModelId=3DB964F800F1
        //##Documentation
        //## True if iterator has gone past the end of the tile (also when
        //## uninitialized)
          bool end () const;

        //##ModelId=3DB964F8010A
        //##Documentation
        //## Advances iterator to next timeslot. Will return true as long as
        //## the iterator has not gone past the end of the tile.
          bool next ();

        //##ModelId=3DB964F8011E
        //##Documentation
        //## Resets iterator to first timeslot in tile
          void reset ();

        // Additional Public Declarations
        //##ModelId=3DB964F80132
        //##Documentation
        //## Detaches iterator from current tile, if any. If tile was attached
        //## via a ref, the ref is released at this point.
          void detach();
          
        //##ModelId=3DD3CB0003D0
        //##Documentation
        //## standard debug info method, depending on level includes:
        //## 0: class name & object address
        //## 1+: iteration position, and current tile at same level
        //## 2+: counted ref (if any) at level 1
          string sdebug ( int detail = 1,const string &prefix = "",
                          const char *name = 0 ) const;
          
        //##ModelId=3DD3CB0201B1
          const char * debug ( int detail = 1,const string &prefix = "",
                               const char *name = 0 ) const
          { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
          

      protected:
        //##ModelId=3DB964F70134
          VisTile *ptile;
      
        //##ModelId=3DB964F70140
          VisTileRef tileref;
          
          // go with an inefficient implementation for now -- a simple index --
          // since arrays suck anyway. Should be re-written when we have better 
          // arrays.
        //##ModelId=3DB964F70179
          int itime;
        //##ModelId=3DB964F701B0
          int ntime;
          
        //##Documentation
        //## keep a lock on the tile being iterated on
          Thread::Mutex::Lock tilelock;
          
    };

    //##ModelId=3DB964F200FB
    //##Documentation
    //## A writable iterator. This is based on ConstIterator, but adds
    //## write-accessors. This Iterator may only be attached to a non-const,
    //## writable tile. 
    class Iterator : virtual public ConstIterator  //## Inherits: <unnamed>%3D888C1F00C5
    {

      public:
        //##ModelId=3DB964F8019C
          Iterator();
        //##ModelId=3DB964F801BF
          Iterator(const Iterator &right);
        //##ModelId=3DB964F80204
          Iterator (VisTile &tile);
        //##ModelId=3DB964F8025C
          Iterator (const VisTileRef &ref);
        //##ModelId=3DB964F8029F
          Iterator & operator=(const Iterator &right);

        //##ModelId=3DB964F802EF
          void attach (VisTile &tile);
        //##ModelId=3DB964F80334
          void attach (const VisTileRef &ref);

        //##ModelId=3DB964F80377
        //##Documentation
        //## Write-accessors for individual columns follow
          void setTime (double x) const;
        //##ModelId=3DD2905D014B
          void setData (const LoMat_fcomplex &x) const;
        //##ModelId=3DD2905D031D
          void setFlags (const LoMat_int &x) const;
        //##ModelId=3DD2905E0047
          void setUvw (const LoVec_double &x) const;
        //##ModelId=3DB964F803BC
          void setRowflag (int x) const;
        //##ModelId=3DB964F9001A
          void setWeight (float x) const;

        //##ModelId=3DD3CB0302B8
        //##Documentation
        //## standard debug info method, see ConstIterator above
          string sdebug ( int detail = 1,const string &prefix = "",
                          const char *name = 0 ) const
          { return ConstIterator::sdebug(detail,prefix,name?name:"I:VisTile"); }
          
        //##ModelId=3DD3CB04022A
          const char * debug ( int detail = 1,const string &prefix = "",
                               const char *name = 0 ) const
          { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

      private:
        //##ModelId=3DB964F80160
        //##Documentation
        //## This hides ConsIterator's attach() methods
          ConstIterator::attach;

    };
    
      typedef ConstIterator const_iterator;
      typedef Iterator iterator;
      

    //##ModelId=3DB964F900AF
    //##Documentation
    //## Construct empty tile
      VisTile();

    //##ModelId=3DB964F900B0
    //##Documentation
    //## Copy constructor. Default is to copy by reference (i.e. data is
    //## shared). Useful flags are DMI::PRIVATIZE (+DMI::WRITE if needed) to
    //## force a private by-value copy, DMI::READONLY to make a read-only copy,
    //## or DMI::PRESERVE_RW to make a copy that preserves the r/w permissions
    //## of the original.
      VisTile (const VisTile &right,
        //##Documentation
        //## flags|DMI::DEEP are passed to CountedRef::copy() when copying the
        //## data block; this copied-and-privatizes the datablock ref
        int flags = DMI::WRITE,
        //##Documentation
        //## depth is ignored (copy is always deep), but is present here
        //## for consistency
        int depth = 1);

    //##ModelId=3DB964F900BF
    //##Documentation
    //## Initializes an empty tile of NC correlations, NF channels, NT
    //## timeslots, using the makeDefaultFormat() method (below) to obtain a
    //## format.
      VisTile (int nc, int nf, int nt);

    //##ModelId=3DB964F900D5
    //##Documentation
    //## Initializes a tile with NT timeslots, using the given format.
      VisTile (const FormatRef &form, int nt);

    //##ModelId=3DB964F900E4
    //##Documentation
    //## Creates a new tile by appending tile B to tile A. A and B must have
    //## compatible formats.
      VisTile (const VisTile &a, const VisTile &b);

    //##ModelId=3DB964F900F6
      ~VisTile();

    //##ModelId=3DB964F900F7
    //##Documentation
    //## Assigns by value. Tile will have read-write permissions
      VisTile & operator=(const VisTile &right);

    //##ModelId=3DB964F90100
    //##Documentation
    //## Initializes a default tile format for NC correlations and NF frequency
    //## channels.
      static void makeDefaultFormat (Format &form, int nc, int nf);

    //##ModelId=3DB964F90117
    //##Documentation
    //## Initializes an empty tile of NC correlations, NF channels, NT
    //## timeslots, using the makeDefaultFormat() method to obtain a format.
      void init (int nc, int nf, int nt);

    //##ModelId=3DB964F9012E
    //##Documentation
    //## Initializes a tile with NT timeslots, using the given format.
      void init (const FormatRef &form, int nt);

    //##ModelId=3DB964F9013E
    //##Documentation
    //## Resets tile to empty state (no data, no format)
      void reset ();

    //##ModelId=3DB964F9013F
    //##Documentation
    //## Attaches the given format to the tile. Will fail if the tile already
    //## has a different format attached, or if the format is incompatible with
    //## the data layout.
      void applyFormat (const FormatRef &form);

    //##ModelId=3DB964F90147
    //##Documentation
    //## Changes the tile format, usually re-formatting the data in memory
    //## accordingly. This may only be used to insert or remove columns, not to
    //## change column shapes. 
      void changeFormat (const FormatRef &form);

    //##ModelId=3DB964F9014F
    //##Documentation
    //## Copies the data from a segment of the other tile over to a segment of
    //## this tile. A segment is a whole number of rows (=timeslots). Will fail
    //## if the tile formats mismatch, or there is not enough rows in the tile
    //## for the copy.
      void copy (
        //##Documentation
        //## starting timeslot to copy to (within this tile)
        int it0,
        //##Documentation
        //## tile to copy from
        const VisTile &other,
        //##Documentation
        //## starting  timeslot to copy from
        int other_it0 = 0,
        //##Documentation
        //## number of timeslots to copy. If <0 (default), copies until end of
        //## source tile.
        int nt = -1);

    //##ModelId=3DB964F9016D
    //##Documentation
    //## Version of copy() implies it0 = 0
      void copy (const VisTile &other, int other_it0 = 0, int nt = -1);

    //##ModelId=3DB964F90184
    //##Documentation
    //## Adds rows (i.e. timeslots) at the end of the tile. This can re-format
    //## data in memory.
      void addRows (int nr);

    //##ModelId=3DD2594A034B
    //##Documentation
    //## Returns a const iterator pointing at the beginning of the tile. If
    //## flags are non-0 (which is default), the iterator will be attached to
    //## the tile via a counted ref constructed with the specified flags.
    VisTile::ConstIterator begin(int flags = DMI::ANON|DMI::READONLY) const;
      
    //##ModelId=3DD25962035B
    //##Documentation
    //## Like const begin(), but returns a non-const iterator.
    VisTile::Iterator begin(int flags = DMI::ANONWR);
      
    //##ModelId=3DD2598802C0
    //##Documentation
    //## Returns an STL-style "end" iterator  (actually just an invalid
    //## iterator), which gives "true" when compared with an iterator that has
    //## gone beyond the end of a tile.
    const VisTile::ConstIterator &end() const;

      //##ModelId=3DB964F901E6
    //##Documentation
    //## ncorr/nfreq/ntime: return the layout of the tile
      int ncorr () const;
    //##ModelId=3DB964F901E8
      int nfreq () const;
    //##ModelId=3DB964F9018D
      int ntime () const;

      // Standard BlockableObject implementation follows.
      // Note that toBlock() and privatize() are inherited from parent class.
    //##ModelId=3DB964F901CD
      int fromBlock (BlockSet& set);
    //##ModelId=3DB964F901D6
      CountedRefTarget* clone (int flags = 0, int  = 0) const;
    //##ModelId=3DB964F901E4
      TypeId objectType () const { return TpVisTile; }
      
    //##ModelId=3DB964F901EB
      DefineRefTypes(VisTile,Ref);
      
    //##ModelId=3DD3C6CB02E9
    //##Documentation
    //## standard debug info method, depending on level includes:
    //## 0: class name & object address
    //## 1: no. of rows
    //## 2: format (if attached) @level 1
    //## 3: format (if attached) @level 2
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;

  private:
    // These arrays point at the data columns inside the tile.
    // When more columns are defined, corresponding arrays should be added here.
    //##ModelId=3DB964F90080
      LoCube_fcomplex  datacube;
    //##ModelId=3DB964F90088
      LoCube_int       flagcube;
    //##ModelId=3DB964F90090
      LoMat_double     uvwmatrix;
    //##ModelId=3DB964F90097
      LoVec_double     timevec;
    //##ModelId=3DB964F9009F
      LoVec_float      weightvec;
    //##ModelId=3DB964F900A7
      LoVec_int        rowflagvec;
      
    //## mutex for thread-safety, locked for the duration of most tile operations
      Thread::Mutex mutex_; 
      
  public:
    // Individual column accessors, inlined right here for brevity.
    // When more columns are defined, corresponding accessors should be 
    // added here.
      
    //    define some handy macros for column accessors. CheckWR checks
    //    the tile for writability, fails if not writable. 
    //    "wreturn" invokes CheckWR, followed by a return statement. 
    #define CheckWR FailWhen(!isWritable(),"r/w access violation");
    #define wreturn CheckWR; return
    //##ModelId=3DB964F9018F
      const LoVec_double & time () const
      { return timevec; }
    //##ModelId=3DB964F90190
      LoVec_double & wtime ()
      { wreturn timevec; }
    //##ModelId=3DCAA5CC00A5
      double time (int it) const
      { return timevec(it); }

    //##ModelId=3DB964F9019A
      const LoMat_double & uvw () const
      { return uvwmatrix; }
    //##ModelId=3DB964F9019B
      LoMat_double & wuvw ()
      { wreturn uvwmatrix; }

    // get individual uvw cell -- inline implementation at end
    //##ModelId=3DCAA5CC023A
    // Returns UVW coordinates for time it.
      const LoVec_double uvw (int it) const;
    //##ModelId=3DCAA5CC0372
      LoVec_double wuvw (int it);

    //##ModelId=3DB964F901A4
      const LoVec_float & weight () const
      { return weightvec; }
    //##ModelId=3DB964F901A5
      LoVec_float & wweight ()
      { wreturn weightvec; }
    //##ModelId=3DCAA5CD0128
      float weight (int it) const
      { return weightvec(it); }

    //##ModelId=3DB964F901AF
      const LoVec_int & rowflag () const
      { return rowflagvec; }
    //##ModelId=3DB964F901B0
      LoVec_int & wrowflag ()
      { wreturn rowflagvec; }
    //##ModelId=3DCAA5CD02EF
      int rowflag (int it) const
      { return rowflagvec(it); }
    //##ModelId=3DB964F901B9
      const LoCube_fcomplex & data () const
      { return datacube; }
    //##ModelId=3DCAA5CE0084
      LoCube_fcomplex & wdata ()
      { wreturn datacube; }

    //##ModelId=3DB964F901C3
      const LoCube_int & flags () const
      { return flagcube; }
    //##ModelId=3DCAA5CE0232
      LoCube_int & wflags ()
      { wreturn flagcube; }

      // TF-plane accessors -- inline implementation at end
    //##ModelId=3DB964F901C5
      const LoMat_int tfFlags (int icorr = 0) const;
    //##ModelId=3DCAA5CE02C4
      LoMat_int wtfFlags (int icorr = 0);
      
    //##ModelId=3DB964F901BB
      const LoMat_fcomplex tfData (int icorr = 0) const;
    //##ModelId=3DCAA5CE0112
      LoMat_fcomplex wtfData (int icorr = 0);
      
    #undef wreturn
      
  private:
    //##ModelId=3DB964F90070
      int ncorr_;
    //##ModelId=3DB964F90077
      int nfreq_;
      
    //##ModelId=3DB964F901F6
    //##Documentation
    //## Helper method: reinitializes internal arrays to point at column data.
      void initArrays ();
      void initArrays_AIPSPP ();
      void initArrays_Blitz ();
      
    //##ModelId=3DB964F901F8
    //##Documentation
    //## helper method: checks that the given column is of the right type and
    //## dimensionality, fails if not
      void assertColumn (int icol,TypeId type,int ndim) const
      {
        FailWhen( !cdata(icol),
          Debug::ssprintf("column %d not defined",icol));
        FailWhen( format().type(icol) != type || 
                  format().ndims(icol) != ndim,
          Debug::ssprintf("type or shape mismatch in column %d\n",
            "expecting %dD %s, have %dD %s",icol,ndim+1,type.toString().c_str(),
            format().ndims(icol)+1,format().type(icol).toString().c_str()));
      }

// The templates getElement/setElement methods are there for VisCube to use.
            
// (the dummy T* parameter is to help template instantiation. g++-3.1 
// seems to have trouble with the obj.member<T>() syntax (when T is a template
// argument, i.e., when calling a templated member from another template)
// so we add a T* parameter to specify type instead.
      template<class T>
      T getElement (int icol,int it,T* = 0) const
      {
#ifdef USE_DEBUG
        assertColumn(icol,typeIdOf(T),0);
#endif
        return static_cast<const T*>(cdata(icol))[it];
      }
      
      template<class T>
      T setElement (int icol,int it,T value)
      {
#ifdef USE_DEBUG
        assertColumn(icol,typeIdOf(T),0);
#endif
        return static_cast<T*>(cwdata(icol))[it] = value;
      }
};



//##ModelId=3DD25CA501CD
inline bool VisTile::ConstIterator::operator ==(const ConstIterator &right)
{
  if( end() && right.end() )
    return True;
  return ptile == right.ptile && itime == right.itime;
}

//##ModelId=3DD25CB20000
inline bool VisTile::ConstIterator::operator !=(const ConstIterator &right)
{
  return ! ( (*this) == right );
}

//##ModelId=3DD25CC20012
inline VisTile::ConstIterator & VisTile::ConstIterator::operator ++()
{
  next();
  return *this;
}

//##ModelId=3DD25CD90071
inline VisTile::ConstIterator & VisTile::ConstIterator::operator ++(int)
{
  next();
  return *this;
}

//##ModelId=3DB964F703B0
inline LoMat_fcomplex VisTile::ConstIterator::data () const
{
#if LORRAYS_USE_BLITZ
  return ptile->data()(LoRange::all(),LoRange::all(),itime);
#else
  return ptile->data().xyPlane(itime);
#endif
}

//##ModelId=3DB964F703C5
inline LoVec_fcomplex VisTile::ConstIterator::fData (int icorr) const
{
#if LORRAYS_USE_BLITZ
  return ptile->data()(icorr,LoRange::all(),itime);
#else
  return ptile->data()(IPosition(3,icorr,0,itime),IPosition(3,icorr,ptile->nfreq()-1,itime));
#endif
}

//##ModelId=3DB964F80025
inline LoMat_int VisTile::ConstIterator::flags () const
{
#if LORRAYS_USE_BLITZ
  return ptile->flags()(LoRange::all(),LoRange::all(),itime);
#else
  return ptile->flags().xyPlane(itime);
#endif
}

//##ModelId=3DB964F8003A
inline LoVec_int VisTile::ConstIterator::fFlags (int icorr) const
{
#if LORRAYS_USE_BLITZ
  return ptile->flags()(icorr,LoRange::all(),itime);
#else
  return ptile->flags()(IPosition(3,icorr,0,itime),IPosition(3,icorr,ptile->nfreq()-1,itime));
#endif  
}

//##ModelId=3DB964F80094
inline double VisTile::ConstIterator::time () const
{
  return ptile->time(itime);
}

//##ModelId=3DB964F800A9
inline int VisTile::ConstIterator::rowflag () const
{
  return ptile->rowflag(itime);
}

//##ModelId=3DB964F800BD
inline LoVec_double VisTile::ConstIterator::uvw () const
{
  return ptile->uvw(itime);
}

//##ModelId=3DB964F800D2
inline float VisTile::ConstIterator::weight () const
{
  return ptile->weight(itime);
}

//##ModelId=3DB964F800F1
inline bool VisTile::ConstIterator::end () const
{
  return !ptile || itime >= ntime;
}

//##ModelId=3DB964F8010A
inline bool VisTile::ConstIterator::next ()
{
  return ++itime < ntime;
}

//##ModelId=3DB964F8011E
inline void VisTile::ConstIterator::reset ()
{
  itime = 0;
}

// Class VisTile::Iterator 

          
//##ModelId=3DD2905D014B
inline void VisTile::Iterator::setData (const LoMat_fcomplex &x) const
{
#if LORRAYS_USE_BLITZ
  ptile->data()(LoRange::all(),LoRange::all(),itime) = x;
#else
  ptile->data().xyPlane(itime) = x;
#endif
}

//##ModelId=3DD2905D031D
inline void VisTile::Iterator::setFlags (const LoMat_int &x) const
{
#if LORRAYS_USE_BLITZ
  ptile->flags()(LoRange::all(),LoRange::all(),itime) = x;
#else
  ptile->flags().xyPlane(itime) = x;
#endif
}

//##ModelId=3DD2905E0047
inline void VisTile::Iterator::setUvw (const LoVec_double &x) const
{
  ptile->wuvw(itime) = x;
}

//##ModelId=3DB964F80377
inline void VisTile::Iterator::setTime (double x) const
{
  ptile->wtime()(itime) = x;
}

//##ModelId=3DB964F803BC
inline void VisTile::Iterator::setRowflag (int x) const
{
  ptile->wrowflag()(itime) = x;
}

//##ModelId=3DB964F9001A
inline void VisTile::Iterator::setWeight (float x) const
{
  ptile->wweight()(itime) = x;
}

// Class VisTile 


//##ModelId=3DB964F9016D
inline void VisTile::copy (const VisTile &other, int other_it0, int nt)
{
  copy(0,other,other_it0,nt);
}

//##ModelId=3DB964F9018D
inline int VisTile::ntime () const
{
  return nrow();
}

//##ModelId=3DCAA5CC023A
inline const LoVec_double VisTile::uvw (int it) const
{
#if LORRAYS_USE_BLITZ
  return uvwmatrix(LoRange::all(),it);
#else
  return uvwmatrix.column(it);
#endif
}

//##ModelId=3DCAA5CC0372
inline LoVec_double VisTile::wuvw (int it)
{
  CheckWR;
#if LORRAYS_USE_BLITZ
  return uvwmatrix(LoRange::all(),it);
#else
  return uvwmatrix.column(it);
#endif
}

//##ModelId=3DB964F901BB
inline const LoMat_fcomplex VisTile::tfData (int icorr) const
{
#if LORRAYS_USE_BLITZ
  return datacube(icorr,LoRange::all(),LoRange::all());
#else
  return datacube(IPosition(3,icorr,0,0),IPosition(3,icorr,nfreq()-1,ntime()-1));
#endif  
}

//##ModelId=3DCAA5CE0112
inline LoMat_fcomplex VisTile::wtfData (int icorr)
{
  CheckWR;
#if LORRAYS_USE_BLITZ
  return datacube(icorr,LoRange::all(),LoRange::all());
#else
  return datacube(IPosition(3,icorr,0,0),IPosition(3,icorr,nfreq()-1,ntime()-1));
#endif  
}

//##ModelId=3DB964F901C5
inline const LoMat_int VisTile::tfFlags (int icorr) const
{
#if LORRAYS_USE_BLITZ
  return flagcube(icorr,LoRange::all(),LoRange::all());
#else
  return flagcube(IPosition(3,icorr,0,0),IPosition(3,icorr,nfreq()-1,ntime()-1));
#endif  
}

//##ModelId=3DCAA5CE02C4
inline LoMat_int VisTile::wtfFlags (int icorr)
{
  CheckWR;
#if LORRAYS_USE_BLITZ
  return flagcube(icorr,LoRange::all(),LoRange::all());
#else
  return flagcube(IPosition(3,icorr,0,0),IPosition(3,icorr,nfreq()-1,ntime()-1));
#endif  
}

//##ModelId=3DB964F901E6
inline int VisTile::ncorr () const
{
  return ncorr_;
}

//##ModelId=3DB964F901E8
inline int VisTile::nfreq () const
{
  return nfreq_;
}

#undef CheckWR

//##ModelId=3DD2594A034B
inline VisTile::ConstIterator VisTile::begin (int flags) const
{
  return flags ? ConstIterator(VisTileRef(this,flags)) : ConstIterator(*this);
}

//##ModelId=3DD25962035B
inline VisTile::Iterator VisTile::begin (int flags)
{
  FailWhen( !isWritable(),"r/w access violation" );
  return flags ? Iterator(VisTileRef(this,flags)) : Iterator(*this);
}

//##ModelId=3DD2598802C0
inline const VisTile::ConstIterator & VisTile::end () const
{
  // return an iterator that is invalid by default
  static ConstIterator dum; 
  return dum;
}


#endif

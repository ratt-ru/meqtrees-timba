#ifndef ColumnarTableTile_h
#define ColumnarTableTile_h 1

#include "VisCube/TableFormat.h"
#include "VisCube/TID-VisCube.h"
#include "DMI/HIID.h"
#include "DMI/BlockableObject.h"

#pragma type #ColumnarTableTile

class ColumnarTableTile : public BlockableObject  //## Inherits: <unnamed>%3D919C2B03DA
{
  public:
    //##ModelId=3DB964F20016
      typedef TableFormat Format;
    //##ModelId=3DB964F2015D
      DefineRefTypes(Format,FormatRef);
  
    //##ModelId=3DB964F20171
      ColumnarTableTile();

    //##ModelId=3DB964F20172
    //##Documentation
    //## A tile is simply a datablock, so copies are always made by-value
    //## (that is, the datablock ref is copy-privatized)
    //## The depth argument is here for consistency, it's simply ignored.
      ColumnarTableTile (const ColumnarTableTile &other, int flags = DMI::WRITE, int depth = 0);

    //##ModelId=3DB964F2018C
      ColumnarTableTile (const FormatRef &form, int nr = 0, 
                         const HIID &id = HIID());

    //##ModelId=3DB964F201A6
      ColumnarTableTile (const ColumnarTableTile &a, const ColumnarTableTile &b);

    //##ModelId=3DB964F201C0
      ~ColumnarTableTile();

    //##ModelId=3DB964F201C2
      ColumnarTableTile & operator=(const ColumnarTableTile &right);


    //##ModelId=3DB964F201D0
      void init (const FormatRef &form, int nr = 0, 
                 const HIID &id = HIID());

    //##ModelId=3DB964F201EA
      void reset ();

    //##ModelId=3DB964F201EC
      void applyFormat (const FormatRef &form);

    //##ModelId=3DB964F201F9
      void changeFormat (const FormatRef &form);

    //##ModelId=3DB964F20207
      bool hasFormat () const;

    //##ModelId=3DB964F2020A
      bool isWritable () const;

    //##ModelId=3DB964F2020C
      bool defined (int icol) const;

    // returns the tile ID
    //##ModelId=3DF9FDCA03BC
      const HIID & tileId () const;
      
    // sets or changes the tile ID
    //##ModelId=3DF9FDCB008B
      void setTileId (const HIID &id);

    //##ModelId=3DB964F2021A
      const void * column (int icol) const;

    //##ModelId=3DB964F20228
      const void * column (int icol, int irow) const;

    //##ModelId=3DB964F20243
      void * wcolumn (int icol);

    //##ModelId=3DB964F20251
      void * wcolumn (int icol, int irow);

    //##ModelId=3DB964F2026C
      //	Returns size of data for NR rows of column ICOL. If NR not
      //	specified, returns full size of column.
      int columnSize (int icol, int nr = -1) const;

    //##ModelId=3DB964F20288
      void addRows (int nr);

    //##ModelId=3DB964F20295
      void copy (int startrow, const ColumnarTableTile &other, int other_start = 0, int numrows = -1);

    //##ModelId=3DB964F202C9
      void copy (const ColumnarTableTile &other, int other_start = 0, int numrows = -1);


    //##ModelId=3DB964F20341
      int ncol () const;
    //##ModelId=3DB964F20343
      int nrow () const;
      
    //##ModelId=3DB964F20345
      const ColumnarTableTile::FormatRef& formatRef () const;
    //##ModelId=3DB964F20347
      const Format & format () const
      { return *formatRef(); }
      
    //##ModelId=3DB964F202F0
      int fromBlock (BlockSet& set);
    //##ModelId=3DB964F202FE
      int toBlock (BlockSet &set) const;
    //##ModelId=3DB964F2030D
      CountedRefTarget* clone (int flags = 0, int depth = 0);
    //##ModelId=3DB964F20324
      void privatize (int flags = 0, int depth = 0);
    //##ModelId=3DB964F2033F
      TypeId objectType () const;
      
    //##ModelId=3DF9FDCB0203
    //##Documentation
    //## accessor to mutex
      Thread::Mutex & mutex () const;

    //##ModelId=3DD3C52001FE
    //##Documentation
    //## standard debug info method, depending on level includes:
    //## 0: class name & object address
    //## 1: no. of rows
    //## 2: format (if attached) @level 1
    //## 3: format (if attached) @level 2
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      
    //##ModelId=3E53937F03C2
    //##Documentation
    // maximum tile ID length
      static const uint MaxIdSize = 16;
      
  protected:
    // Additional Protected Declarations
    //##ModelId=3DB964F20349
      // Internal methods for fastest access to column data bypassing all 
      // sanity checks (inlined below).
      // The caller is expected to have performed all checks himself
      // (column defined, irow is sane, is writable, etc.)
      
      // compute pointer to data(icol,irow), column pointers passed in explicitly
      const void * cdata (const vector<const void*> &ptrs,int icol,int irow=0) const;
    //##ModelId=3DB964F20371
      void *      cwdata (const vector<const void*> &ptrs,int icol,int irow=0) const;
      
      // computes pointer to data(icol,irow), using current column pointers
    //##ModelId=3DB964F20399
      const void * cdata (int icol,int irow) const;
    //##ModelId=3DB964F203B5
      void *      cwdata (int icol,int irow); 
      
      // returns pointer to data(icol,0)
    //##ModelId=3DB964F203D0
      const void * cdata (int icol) const;
    //##ModelId=3DB964F203DF
      void *      cwdata (int icol); 

  private:
    //##ModelId=3DB964F2011C
      BlockRef datablock;
    //##ModelId=3DB964F20128
      int ncol_;
    //##ModelId=3DB964F20130
      int nrow_;
    //##ModelId=3DB964F20138
      ColumnarTableTile::FormatRef format_;
      
      // tile ID
    //##ModelId=3DF9FDC90314
      HIID id_;
      
      // common "null" block for 0-row representations
    //##ModelId=3DB964F20141
      static BlockRef nullBlock;
      
      // vector of pointers to start of each column
    //##ModelId=3DB964F20150
      vector<const void *> pdata;
      
      // computes offset of each column in block, given format
      // (taking block header + tile id into account)
    //##ModelId=3DB964F30005
      static int computeOffsets (vector<int> &offsets,const Format &format,int nr);
      // computes the pdata vector, given the offsets returned by 
      // computeOffsets, and a pointer to a block
    //##ModelId=3DB964F3002D
      static void applyOffsets (vector<const void *> &ptrs,const vector<int> &offsets,const char *ptr0);
    // helper function to stuff header & ID into a data block
    //##ModelId=3DF9FDCC00FB
      void initBlock (void *data,size_t sz) const;
      
    //##ModelId=3DB964F20021
      typedef struct { int nrow,idsize; bool has_format; } BlockHeader;
      
    //##ModelId=3DF9FDC90364
      mutable Thread::Mutex mutex_;
      
};

//##ModelId=3DB964F20207

// Class ColumnarTableTile 


inline bool ColumnarTableTile::hasFormat () const
{
  return format_.valid();
}

//##ModelId=3DB964F2020A
inline bool ColumnarTableTile::isWritable () const
{
  return !datablock.valid() || datablock.isWritable();
}

//##ModelId=3DF9FDCA03BC
inline const HIID & ColumnarTableTile::tileId () const
{
  return id_;
}

//##ModelId=3DB964F20243
inline void * ColumnarTableTile::wcolumn (int icol)
{
  DbgFailWhen(!isWritable(),"r/w access violation" );
  return const_cast<void*>(column(icol));
}

//##ModelId=3DB964F20251
inline void * ColumnarTableTile::wcolumn (int icol, int irow)
{
  DbgFailWhen(!isWritable(),"r/w access violation" );
  return const_cast<void*>(column(icol,irow));
}

//##ModelId=3DB964F2026C
inline int ColumnarTableTile::columnSize (int icol, int nr) const
{
  return format().cellsize(icol)*(nr<0 ? nrow() : nr);
}

//##ModelId=3DB964F202C9
inline void ColumnarTableTile::copy (const ColumnarTableTile &other, int other_start, int numrows)
{
  copy(0,other,other_start,numrows);
}

//##ModelId=3DB964F2033F
inline TypeId ColumnarTableTile::objectType () const
{
  return TpColumnarTableTile;
}

//##ModelId=3DB964F20341

inline int ColumnarTableTile::ncol () const
{
  return ncol_;
}

//##ModelId=3DB964F20343
inline int ColumnarTableTile::nrow () const
{
  return nrow_;
}

//##ModelId=3DB964F20345

inline const ColumnarTableTile::FormatRef& ColumnarTableTile::formatRef () const
{
  return format_;
}

//##ModelId=3DB964F20349
// computes pointer to data(icol,irow) with no checks.
// vector of column pointers is passed in explicitly
inline const void * ColumnarTableTile::cdata (const vector<const void*> &ptrs,int icol,int irow) const
{ 
  return static_cast<const char*>(ptrs[icol])
            + irow*format().cellsize(icol);
}

// computes writable pointer to data(icol,irow) with no checks
// vector of column pointers is passed in explicitly
//##ModelId=3DB964F20371
inline void * ColumnarTableTile::cwdata (const vector<const void*> &ptrs,int icol,int irow) const
{ 
  return const_cast<void*>(cdata(ptrs,icol,irow)); 
}

// computes pointer to data(icol,irow) with no checks
//##ModelId=3DB964F20399
inline const void * ColumnarTableTile::cdata (int icol,int irow) const
{ 
  return cdata(pdata,icol,irow); 
}

// computes writable pointer to data(icol,irow) with no  checks
//##ModelId=3DB964F203B5
inline void * ColumnarTableTile::cwdata (int icol,int irow) 
{ 
  return cwdata(pdata,icol,irow); 
}
      
//##ModelId=3DB964F203D0
inline const void * ColumnarTableTile::cdata (int icol) const
{
  return pdata[icol];
}

//##ModelId=3DB964F203DF
inline void *       ColumnarTableTile::cwdata (int icol)
{
  return const_cast<void*>(pdata[icol]);
}


//##ModelId=3DF9FDCB0203
inline Thread::Mutex & ColumnarTableTile::mutex () const
{
  return mutex_;
}


#endif



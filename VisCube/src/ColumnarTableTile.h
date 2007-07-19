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

#ifndef VCube_ColumnarTableTile_h
#define VCube_ColumnarTableTile_h 1

#include <VisCube/TableFormat.h>
#include <VisCube/TID-VisCube.h>
#include <DMI/HIID.h>
#include <DMI/BObj.h>

namespace VisCube 
{
using namespace DMI;

#pragma type #VisCube::ColumnarTableTile

class ColumnarTableTile : public DMI::BObj  //## Inherits: <unnamed>%3D919C2B03DA
{
  public:
    //##ModelId=3DB964F20016
      typedef TableFormat Format;
    //##ModelId=3DB964F2015D
  
    //##ModelId=3DB964F20171
      ColumnarTableTile();

    //##ModelId=3DB964F20172
    //##Documentation
    //## A tile is simply a datablock, so copies are always made by-ref
    //## (internally, we make use of COW), unless DMI::DEEP is set.
      ColumnarTableTile (const ColumnarTableTile &other, int flags=0, int depth=0);

    //##ModelId=3DB964F2018C
      ColumnarTableTile (const Format::Ref &form, int nr = 0, 
                         const HIID &id = HIID());

    //##ModelId=3DB964F201A6
      ColumnarTableTile (const ColumnarTableTile &a, const ColumnarTableTile &b);

    //##ModelId=3DB964F201C0
      ~ColumnarTableTile();

    //##ModelId=3DB964F201C2
      ColumnarTableTile & operator=(const ColumnarTableTile &right);


    //##ModelId=3DB964F201D0
      void init (const Format::Ref &form, int nr = 0, 
                 const HIID &id = HIID());

    //##ModelId=3DB964F201EA
      void reset ();

    //##ModelId=3DB964F201EC
      void applyFormat (const Format::Ref &form);

    //##ModelId=3DB964F201F9
      void changeFormat (const Format::Ref &form);

    //##ModelId=3DB964F20207
      bool hasFormat () const;

    //##ModelId=3DB964F2020C
      bool defined (int icol) const;
      
      // makes data block writable by ensuring COW and recomputing offsets
      // if needed; returns true if this was done, or false if nothing
      // was changed (i.e. already writable)
      bool makeWritable ()
      { 
        if( !datablock.valid() || datablock.isDirectlyWritable() )
          return false;
        datablock.privatize(DMI::WRITE);
        setupDataPointers();
        return true;
      }
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
      const ColumnarTableTile::Format::Ref& formatRef () const;
    //##ModelId=3DB964F20347
      const Format & format () const
      { return *formatRef(); }
      
    //##ModelId=3DB964F202F0
      int fromBlock (BlockSet& set);
    //##ModelId=3DB964F202FE
      int toBlock (BlockSet &set) const;
    //##ModelId=3DB964F2030D
      CountedRefTarget* clone (int flags=0, int depth=0) const;
      
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
      void cloneOther (const ColumnarTableTile &other, int flags=0, int depth=0);
  
      // helper function to reset internal data pointers to data block
      void setupDataPointers ();
      
      // computes offset of each column in block, given format
      // (taking block header + tile id into account)
    //##ModelId=3DB964F30005
      static int computeOffsets (std::vector<int> &offsets,const Format &format,int nr);
      // computes the pdata vector, given the offsets returned by 
      // computeOffsets, and a pointer to a block
    //##ModelId=3DB964F3002D
      static void applyOffsets (std::vector<const void *> &ptrs,const std::vector<int> &offsets,const char *ptr0);
    // helper function to stuff header & ID into a data block
    //##ModelId=3DF9FDCC00FB
      void initBlock (void *data,size_t sz) const;
      
    //##ModelId=3DB964F2011C
      BlockRef datablock;
    //##ModelId=3DB964F20128
      int ncol_;
    //##ModelId=3DB964F20130
      int nrow_;
    //##ModelId=3DB964F20138
      Format::Ref format_;
      
      // tile ID
    //##ModelId=400E51D401E8
      HIID id_;
      
      // common "null" block for 0-row representations
    //##ModelId=3DB964F20141
      static BlockRef nullBlock;
      
      // vector of pointers to start of each column
    //##ModelId=3DB964F20150
      std::vector<const void *> pdata;
      
    //##ModelId=3DB964F20021
      class BlockHeader : public BObj::Header
      {
        public: int   nrow;
                int   idsize;
      // phased out since we now have a blockcount (1 for no format, 2 with format)
      //          bool  has_format; 
      };
      
    //##ModelId=3DF9FDC90364
      mutable Thread::Mutex mutex_;
      
};

//##ModelId=3DB964F20207

// Class ColumnarTableTile 


inline bool ColumnarTableTile::hasFormat () const
{
  return format_.valid();
}

//##ModelId=3DF9FDCA03BC
inline const HIID & ColumnarTableTile::tileId () const
{
  return id_;
}

//##ModelId=3DB964F20243
inline void * ColumnarTableTile::wcolumn (int icol)
{
  makeWritable();
  return const_cast<void*>(column(icol));
}

//##ModelId=3DB964F20251
inline void * ColumnarTableTile::wcolumn (int icol, int irow)
{
  makeWritable();
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
  return TpVisCubeColumnarTableTile;
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

inline const ColumnarTableTile::Format::Ref& ColumnarTableTile::formatRef () const
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

};

#endif




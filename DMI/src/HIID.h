//  HIID.h: hierarchical ID class
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#ifndef DMI_HIID_h
#define DMI_HIID_h 1

#include <DMI/DMI.h>
#include <DMI/AtomicID.h>
#include <DMI/Allocators.h>
#include <TimBase/lofar_iostream.h>

#include <vector>
    
#pragma type =DMI::HIID

namespace DMI
{

//##ModelId=3C55652D01B8
typedef std::vector<AtomicID,DMI_Pool_Allocator<AtomicID> > HIID_Base;


//##ModelId=3BE96FE601C5
class HIID : public HIID_Base
{
  public:
    //##ModelId=3BE9774C003C
      HIID ();
  
      HIID (const HIID &other,int extra_size=0);

      //##ModelId=3C5E7527020F
      HIID (AtomicID aid);

      //##ModelId=3C6141BA03B4
      //##Documentation
      //## Constructs HIID from string form, using default separator set ("._")
      //## ("A.B.C.D", "a_b_c_d", etc.)
      HIID (const string &str);
      HIID (const char *str);
      
      //## Constructs HIID from string form, using custom separator.
      //## ("A_B_C_D", etc.)
      //## If allow_literals is true, then if any AtomicID is not found,
      //## the HIID is converted using literal string mapping
      //## (NB: still to be implemented!)
      HIID (const string &str,bool allow_literals,const string &sep_set);

      
      //##ModelId=3DB934880197
      //##Documentation
      //## Creates a HIID from a block of raw bytes
      HIID (const void* block, int sz);

    //##ModelId=3DB9348803AA
      bool operator==(const HIID &right) const;

    //##ModelId=3DB9348901D5
      bool operator!=(const HIID &right) const;
      
      HIID & operator = (const HIID &other);

      void resize (size_type sz)
      {
        if( sz > capacity() )
          reserve(sz);
        HIID_Base::resize(sz);
      }

      //##ModelId=3BE977510397
      HIID & add (const HIID &other);

      //##ModelId=3BE97792003D
      HIID & add (AtomicID aid);

      //##ModelId=3C55695F00CC
      HIID subId (int first, int last = -1) const;

      //##ModelId=3C1A187E018C
      int length () const;

      //##ModelId=3BE9792B0135
      //##Documentation
      //## Does a comparison with another HIID, interpreting the Any ("?") and
      //## Wildcard ("*") AIDs in the conventional way.   Returns true when
      //## there is a match.
      //## NB: Currently, the "*" wildcard should only appear at the end of a
      //## HIID. Anything following the * is ignored for the purposes of this
      //## function.
      bool matches (const HIID &other) const;

      //##ModelId=3C99A0400186
      //##Documentation
      //## Does a comparison with another HIID, interpreting the Any ("?") and
      //## Wildcard ("*") AIDs in the conventional way.   Returns true if this
      //## HIID is a  subset of the other HIID (i.e., when all HIIDs matching _
      //## this_ also match  _other_).
      bool subsetOf (const HIID &other) const;

      //##ModelId=3CBEB7E2034E
      //##Documentation
      //## Returns true if other is a prefix of this.
      bool prefixedBy (const HIID &other) const;

      //##ModelId=3C59522600D6
      //##Documentation
      //## If first atom of HIID is an index, pop and return it, else return 0.
      int popLeadIndex ();

      //##ModelId=3C6B86D5003A
      int popTrailIndex ();

      //##ModelId=3C6B9FDD02FD
      //##Documentation
      //## Removes any leading slashes from HIID, returns # of slashes actually
      //## removed.
      int popLeadSlashes ();

      //##ModelId=3C7A1B6500C9
      //##Documentation
      //## returns position of first slash in HIID, or -1 if none
      int findFirstSlash () const;

      //##ModelId=3CAD7B2901CA
      //##Documentation
      //## Finds first "/" separator, splits off the sub-id. Removes up to and
      //## including the slash, but returns sub-id w/o the slash.
      HIID splitAtSlash ();
      
      // removes N elements from front of vector
      void pop_front (uint n=1);
      // adds N elements to front of vector
      void push_front (AtomicID aid,uint n=1);

      //##ModelId=3C0F8BD5004F
      string toString (char separator = '_',bool mark_lit=true) const;

      //##ModelId=3C5912FE0134
      //##Documentation
      //## Stores HIID into raw data block
      size_t pack (void *block, size_t &nleft) const;

      //##ModelId=3C970F91006F
      void unpack (const void* block, size_t sz);

      //##ModelId=3C591278038A
      //##Documentation
      //## Returns # of bytes required to store the HIID
      size_t packSize () const;

    // Additional Public Declarations
      // define some concatenation operations
    //##ModelId=3DB934890383
      HIID & operator |= (const HIID &other);
    //##ModelId=3DB9348A0118
      HIID & operator |= (AtomicID aid);
    //##ModelId=3DB9348A029E
      HIID & operator |= (int aid);
    //##ModelId=3DB9348B0051
      HIID & operator |= (const char *str);
      
      // a less-than operator
    //##ModelId=3DB9348B01E2
      bool operator < (const HIID &right) const;
      
      // templated constructor (constructs from input iterator)
      template<class In> HIID( In first,In last );
      
    //##ModelId=3DB9348B03E0
      static size_t HIIDSize (int n)  { return n*sizeof(int); }
      
    // prints to stream
    //##ModelId=3E01AD45000B
      void print (std::ostream &str) const
      { str << toString(); }
      
      // prints to cout, with endline. Not inlined, so that it can
      // be called from a debugger
    //##ModelId=3E01BA7A02AF
      void print () const;

      ImportDebugContext(DebugDMI);
      
  private:
    // Additional Implementation Declarations
    //##ModelId=3DB9343C01F1
      typedef HIID_Base::iterator VI;  
    //##ModelId=3DB9343C025F
      typedef HIID_Base::const_iterator CVI;  
      
      // this function reserves initial space for the HIID vector
    //##ModelId=3DB9348C0215
      static size_type ALLOC_STEP () { return 16; }
      
      void reserve (size_type sz = 0)
      { 
        HIID_Base::reserve((1+sz/ALLOC_STEP())*ALLOC_STEP()); 
      }

      // creates from string
    //##ModelId=3DB9348C0305
      void addString (const string &,const string &sep_set = "._",bool allow_literals=false);
      // creates literal id from string
      void makeLiteral (const string &str,int ipos=0);
};

// stream operator
inline std::ostream & operator << (std::ostream &str,const HIID &id)
{ 
  id.print(str);
  return str;
}

// comparison operators for single AtomicIDs
inline bool operator == (const HIID &id1,AtomicID id2)
{ return id1 == HIID(id2); }
inline bool operator != (const HIID &id1,AtomicID id2)
{ return id1 != HIID(id2); }
inline bool operator == (AtomicID id1,const HIID &id2)
{ return id2 == id1; }
inline bool operator != (AtomicID id1,const HIID &id2)
{ return id2 != id1; }

// concatenation operations
//##ModelId=3DB934890383
inline HIID & HIID::operator |= (const HIID &other)
  { return add(other); }

//##ModelId=3DB9348B0051
inline HIID & HIID::operator |= (const char *other)
  { return add(HIID(other)); }

//##ModelId=3DB9348A0118
inline HIID & HIID::operator |= (AtomicID id2)
  { return add(id2); }

//##ModelId=3DB9348A029E
inline HIID & HIID::operator |= (int id2)
  { return add(AtomicID(id2)); }

inline HIID operator | (const HIID &id1,const HIID &id2)
{ HIID ret(id1,id2.size()); return ret|=id2; }

inline HIID operator | (const HIID &id1,const char *id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (const HIID &id1,AtomicID id2)
{ HIID ret(id1,1); return ret|=id2; }

inline HIID operator | (const HIID &id1,int id2)
{ HIID ret(id1,1); return ret|=AtomicID(id2); }

inline HIID operator | (AtomicID id1,const HIID &id2)
{ HIID ret(id1,id2.size()); return ret|=id2; }

inline HIID operator | (AtomicID id1,const char *id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (AtomicID id1,AtomicID id2)
{ HIID ret(id1,1); return ret|=id2; }

inline HIID operator | (AtomicID id1,int id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (int id1,const HIID &id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (int id1,AtomicID id2)
{ HIID ret(id1); return ret|=id2; }

// Class HIID 

//##ModelId=3BE9774C003C
inline HIID::HIID ()
{
  reserve();
}

inline HIID::HIID (const HIID &other,int extra_size)
  : HIID_Base ()
{
  reserve(other.size()+extra_size);
  HIID_Base::operator = (other);
}

inline HIID & HIID::operator = (const HIID &other)
{
  if( other.size() > capacity() )
    reserve(other.size());
  HIID_Base::operator = (other);
  return *this;
}

//##ModelId=3C5E7527020F
inline HIID::HIID (AtomicID aid)
{
  reserve();
  HIID_Base::resize(1);
  front() = aid;
}

//##ModelId=3C6141BA03B4
inline HIID::HIID (const string &str)
{
  reserve();
  addString(str);
}

inline HIID::HIID (const char *str)
{
  reserve();
  if( str )
    addString(str);
}

//##ModelId=3C556A470346
inline HIID::HIID (const string &str,bool allow_literals,const string &sepset)
{
  reserve();
  addString(str,sepset,allow_literals);
}


//##ModelId=3DB9348901D5
inline bool HIID::operator!=(const HIID &right) const
{
  return ! ( (*this) == right );
}

//##ModelId=3BE97792003D
inline HIID & HIID::add (AtomicID aid)
{
  if( size()+1 > capacity() )
    reserve(size()+1);
  push_back(aid);
  return *this;
}

inline HIID & HIID::add (const HIID &other)
{
  if( !other.empty() )
  {
    int n = size(), n1 = other.size();
    resize(n+n1);
    memcpy(&((*this)[n]),&( other.front() ),n1*sizeof(AtomicID));
  }
  return *this;
}

//##ModelId=3C1A187E018C
inline int HIID::length () const
{
  return size();
}

//##ModelId=3CBEB7E2034E
inline bool HIID::prefixedBy (const HIID &other) const
{
  return matches(other|AidWildcard);
}

//##ModelId=3C6B9FDD02FD
inline void HIID::pop_front (uint n)
{
  if( n )
  {
    int nleft = int(size()) - int(n);
    if( nleft<=0 )
      HIID_Base::resize(0);
    else
    {
      memmove(&(front()),&((*this)[n]),nleft*sizeof(AtomicID));
      HIID_Base::resize(nleft);
    }
  }
}

inline void HIID::push_front (AtomicID aid,uint n)
{
  if( n )
  {
    int sz0 = size();
    resize(sz0+n);
    memmove(&(*this)[n],&(front()),sz0);
    iterator iter = begin();
    for( uint i=0; i < n; i++,iter++ )
      *iter = aid;
  }
}

inline int HIID::popLeadSlashes ()
{
  uint n=0;
  while( n < size() && (*this)[n] == AidSlash )
    n++;
  pop_front(n);
// when this was a deque, we did:   
//  {
//    pop_front();
//    n++;
//  }
  return int(n);
}

//##ModelId=3C7A1B6500C9
inline int HIID::findFirstSlash () const
{
  int pos = 0;
  for( const_iterator iter = begin(); iter != end(); iter++,pos++ )
    if( *iter == AidSlash )
      return pos;
  return -1;
}


//##ModelId=3C591278038A
inline size_t HIID::packSize () const
{
  return size()*sizeof(int);
}

template<class In> inline HIID::HIID( In first,In last )
{
  reserve(last-first);
  assign(first,last);
}


};

#endif

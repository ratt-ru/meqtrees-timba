//  HIID.h: hierarchical ID class
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
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

#include <DMI/Common.h>
#include <DMI/DMI.h>
#include <DMI/AtomicID.h>

#include <deque>
#include <Common/lofar_iostream.h>
    
#pragma type =HIID


//##ModelId=3C55652D01B8
typedef std::deque<AtomicID> Vector_AtomicID;

//##ModelId=3BE96FE601C5
class HIID : public Vector_AtomicID
{
  public:
    //##ModelId=3BE9774C003C
      HIID();

      //##ModelId=3C5E7527020F
      HIID (AtomicID aid);

      //##ModelId=3C6141BA03B4
      //##Documentation
      //## Constructs HIID from string form, using '.' separator
      //## ("A.B.C.D", etc.)
      HIID (const string &str);
      HIID (const char *str);
      
      //## Constructs HIID from string form, using custom separator.
      //## ("A_B_C_D", etc.)
      //## The dummy int argument is needed to distinguish from other
      //## constructors
      HIID (const string &str,int,const string &sep_set);

      
      //##ModelId=3DB934880197
      //##Documentation
      //## Creates a HIID from a block of raw bytes
      HIID (const void* block, int sz);

    //##ModelId=3DB9348803AA
      bool operator==(const HIID &right) const;

    //##ModelId=3DB9348901D5
      bool operator!=(const HIID &right) const;


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
      //## Wildcard ("*") AIDs in the conventional way.   Returns True when
      //## there is a match.
      //## NB: Currently, the "*" wildcard should only appear at the end of a
      //## HIID. Anything following the * is ignored for the purposes of this
      //## function.
      bool matches (const HIID &other) const;

      //##ModelId=3C99A0400186
      //##Documentation
      //## Does a comparison with another HIID, interpreting the Any ("?") and
      //## Wildcard ("*") AIDs in the conventional way.   Returns True if this
      //## HIID is a  subset of the other HIID (i.e., when all HIIDs matching _
      //## this_ also match  _other_).
      bool subsetOf (const HIID &other) const;

      //##ModelId=3CBEB7E2034E
      //##Documentation
      //## Returns True if other is a prefix of this.
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

      //##ModelId=3C0F8BD5004F
      string toString (char separator = '.') const;

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
      
  private:
    // Additional Implementation Declarations
    //##ModelId=3DB9343C01F1
      typedef Vector_AtomicID::iterator VI;  
    //##ModelId=3DB9343C025F
      typedef Vector_AtomicID::const_iterator CVI;  
      
      // this function reserves initial space for the HIID vector
      // no-op for now
    //##ModelId=3DB9348C0215
      void reserve ()     {};
      
      // creates from string
    //##ModelId=3DB9348C0305
      void addString ( const string &,const string &sep_set = ".");
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
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (const HIID &id1,const char *id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (const HIID &id1,AtomicID id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (const HIID &id1,int id2)
{ HIID ret(id1); return ret|=AtomicID(id2); }

inline HIID operator | (AtomicID id1,const HIID &id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (AtomicID id1,const char *id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (AtomicID id1,AtomicID id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (AtomicID id1,int id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (int id1,const HIID &id2)
{ HIID ret(id1); return ret|=id2; }

inline HIID operator | (int id1,AtomicID id2)
{ HIID ret(id1); return ret|=id2; }

// Class HIID 

//##ModelId=3BE9774C003C
inline HIID::HIID()
{
  reserve();
}

//##ModelId=3C5E7527020F
inline HIID::HIID (AtomicID aid)
    : Vector_AtomicID(1,aid)
{
  reserve();
}

//##ModelId=3C6141BA03B4
inline HIID::HIID (const string &str)
{
  addString(str);
}

inline HIID::HIID (const char *str)
{
  if( str )
    addString(str);
}

//##ModelId=3C556A470346
inline HIID::HIID (const string &str,int,const string &sepset)
{
  addString(str,sepset);
}


//##ModelId=3DB9348901D5
inline bool HIID::operator!=(const HIID &right) const
{
  return ! ( (*this) == right );
}



//##ModelId=3BE97792003D
inline HIID & HIID::add (AtomicID aid)
{
  push_back(aid);
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
inline int HIID::popLeadSlashes ()
{
  int n=0;
  while( front() == AidSlash )
  {
    pop_front();
    n++;
  }
  return n;
}

//##ModelId=3C591278038A
inline size_t HIID::packSize () const
{
  return size()*sizeof(int);
}

template<class In> inline HIID::HIID( In first,In last )
      : Vector_AtomicID(first,last)
{
  reserve();
}


#endif

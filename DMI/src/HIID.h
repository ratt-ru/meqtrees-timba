//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820355.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820355.cm

//## begin module%3C10CC820355.cp preserve=no
//## end module%3C10CC820355.cp

//## Module: HIID%3C10CC820355; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\HIID.h

#ifndef HIID_h
#define HIID_h 1

//## begin module%3C10CC820355.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C10CC820355.additionalIncludes

//## begin module%3C10CC820355.includes preserve=yes
#include <deque>
//## end module%3C10CC820355.includes

// AtomicID
#include "DMI/AtomicID.h"
//## begin module%3C10CC820355.declarations preserve=no
//## end module%3C10CC820355.declarations

//## begin module%3C10CC820355.additionalDeclarations preserve=yes
#pragma type =HIID
//## end module%3C10CC820355.additionalDeclarations


//## begin Vector_AtomicID%3C55652D01B8.preface preserve=yes
//## end Vector_AtomicID%3C55652D01B8.preface

//## Class: Vector_AtomicID%3C55652D01B8
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C55657503BA;AtomicID { -> }

typedef deque<AtomicID> Vector_AtomicID;
//## begin Vector_AtomicID%3C55652D01B8.postscript preserve=yes
//## end Vector_AtomicID%3C55652D01B8.postscript

//## begin HIID%3BE96FE601C5.preface preserve=yes
//## end HIID%3BE96FE601C5.preface

//## Class: HIID%3BE96FE601C5
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class HIID : public Vector_AtomicID  //## Inherits: <unnamed>%3C5566050230
{
  //## begin HIID%3BE96FE601C5.initialDeclarations preserve=yes
  //## end HIID%3BE96FE601C5.initialDeclarations

  public:
    //## Constructors (generated)
      HIID();

    //## Constructors (specified)
      //## Operation: HIID%3BE9774C003C
      HIID (AtomicID aid);

      //## Operation: HIID%3C5E7527020F
      //	Constructs HIID from string form
      //	("A.B.C.D", etc.)
      HIID (const string &str);

      //## Operation: HIID%3C6141BA03B4
      HIID (const char *str);

      //## Operation: HIID%3C556A470346
      //	Creates a HIID from a block of raw bytes
      HIID (const void* block, int sz);

    //## Equality Operations (generated)
      bool operator==(const HIID &right) const;

      bool operator!=(const HIID &right) const;


    //## Other Operations (specified)
      //## Operation: add%3BE977510397
      HIID & add (const HIID &other);

      //## Operation: add%3BE97792003D
      HIID & add (AtomicID aid);

      //## Operation: subId%3C55695F00CC
      HIID subId (int first, int last = -1) const;

      //## Operation: length%3C1A187E018C
      int length () const;

      //## Operation: matches%3BE9792B0135
      //	Does a comparison with another HIID, interpreting the Any ("?") and
      //	Wildcard ("*") AIDs in the conventional way.   Returns True when
      //	there is a match.
      //	NB: Currently, the "*" wildcard should only appear at the end of a
      //	HIID. Anything following the * is ignored for the purposes of this
      //	function.
      bool matches (const HIID &other) const;

      //## Operation: subsetOf%3C99A0400186
      //	Does a comparison with another HIID, interpreting the Any ("?") and
      //	Wildcard ("*") AIDs in the conventional way.   Returns True if this
      //	HIID is a  subset of the other HIID (i.e., when all HIIDs matching _
      //	this_ also match  _other_).
      bool subsetOf (const HIID &other) const;

      //## Operation: prefixedBy%3CBEB7E2034E
      //	Returns True if other is a prefix of this.
      bool prefixedBy (const HIID &other) const;

      //## Operation: popLeadIndex%3C59522600D6
      //	If first atom of HIID is an index, pop and return it, else return 0.
      int popLeadIndex ();

      //## Operation: popTrailIndex%3C6B86D5003A
      int popTrailIndex ();

      //## Operation: popLeadSlashes%3C6B9FDD02FD
      //	Removes any leading slashes from HIID, returns # of slashes actually
      //	removed.
      int popLeadSlashes ();

      //## Operation: findFirstSlash%3C7A1B6500C9
      //	returns position of first slash in HIID, or -1 if none
      int findFirstSlash () const;

      //## Operation: splitAtSlash%3CAD7B2901CA
      //	Finds first "/" separator, splits off the sub-id. Removes up to and
      //	including the slash, but returns sub-id w/o the slash.
      HIID splitAtSlash ();

      //## Operation: toString%3C0F8BD5004F
      string toString () const;

      //## Operation: pack%3C5912FE0134
      //	Stores HIID into raw data block
      size_t pack (void *block, size_t &nleft) const;

      //## Operation: unpack%3C970F91006F
      void unpack (const void* block, size_t sz);

      //## Operation: packSize%3C591278038A
      //	Returns # of bytes required to store the HIID
      size_t packSize () const;

    // Additional Public Declarations
      //## begin HIID%3BE96FE601C5.public preserve=yes
      // define some concatenation operations
      HIID & operator |= (const HIID &other);
      HIID & operator |= (AtomicID aid);
      HIID & operator |= (int aid);
      HIID & operator |= (const char *str);
      
      // a less-than operator
      bool operator < (const HIID &right) const;
      
      // templated constructor (constructs from input iterator)
      template<class In> HIID( In first,In last );
      
      static size_t HIIDSize (int n)  { return n*sizeof(int); }
      //## end HIID%3BE96FE601C5.public
  protected:
    // Additional Protected Declarations
      //## begin HIID%3BE96FE601C5.protected preserve=yes
      //## end HIID%3BE96FE601C5.protected

  private:
    // Additional Private Declarations
      //## begin HIID%3BE96FE601C5.private preserve=yes
      //## end HIID%3BE96FE601C5.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin HIID%3BE96FE601C5.implementation preserve=yes
      typedef Vector_AtomicID::iterator VI;  
      typedef Vector_AtomicID::const_iterator CVI;  
      
      // this function reserves initial space for the HIID vector
      // no-op for now
      void reserve ()     {};
      
      // creates from string
      void addString ( const string & );
      //## end HIID%3BE96FE601C5.implementation
};

//## begin HIID%3BE96FE601C5.postscript preserve=yes
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
inline HIID & HIID::operator |= (const HIID &other)
  { return add(other); }

inline HIID & HIID::operator |= (const char *other)
  { return add(HIID(other)); }

inline HIID & HIID::operator |= (AtomicID id2)
  { return add(id2); }

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
//## end HIID%3BE96FE601C5.postscript

// Class HIID 

inline HIID::HIID()
  //## begin HIID::HIID%3BE96FE601C5_const.hasinit preserve=no
  //## end HIID::HIID%3BE96FE601C5_const.hasinit
  //## begin HIID::HIID%3BE96FE601C5_const.initialization preserve=yes
  //## end HIID::HIID%3BE96FE601C5_const.initialization
{
  //## begin HIID::HIID%3BE96FE601C5_const.body preserve=yes
  reserve();
  //## end HIID::HIID%3BE96FE601C5_const.body
}

inline HIID::HIID (AtomicID aid)
  //## begin HIID::HIID%3BE9774C003C.hasinit preserve=no
  //## end HIID::HIID%3BE9774C003C.hasinit
  //## begin HIID::HIID%3BE9774C003C.initialization preserve=yes
    : Vector_AtomicID(1,aid)
  //## end HIID::HIID%3BE9774C003C.initialization
{
  //## begin HIID::HIID%3BE9774C003C.body preserve=yes
  reserve();
  //## end HIID::HIID%3BE9774C003C.body
}

inline HIID::HIID (const string &str)
  //## begin HIID::HIID%3C5E7527020F.hasinit preserve=no
  //## end HIID::HIID%3C5E7527020F.hasinit
  //## begin HIID::HIID%3C5E7527020F.initialization preserve=yes
  //## end HIID::HIID%3C5E7527020F.initialization
{
  //## begin HIID::HIID%3C5E7527020F.body preserve=yes
  addString(str);
  //## end HIID::HIID%3C5E7527020F.body
}

inline HIID::HIID (const char *str)
  //## begin HIID::HIID%3C6141BA03B4.hasinit preserve=no
  //## end HIID::HIID%3C6141BA03B4.hasinit
  //## begin HIID::HIID%3C6141BA03B4.initialization preserve=yes
  //## end HIID::HIID%3C6141BA03B4.initialization
{
  //## begin HIID::HIID%3C6141BA03B4.body preserve=yes
  if( str )
    addString(str);
  //## end HIID::HIID%3C6141BA03B4.body
}


inline bool HIID::operator==(const HIID &right) const
{
  //## begin HIID::operator==%3BE96FE601C5_eq.body preserve=yes
  if( size() != right.size() )
    return False;
  for( CVI iter = begin(),oiter = right.begin(); iter != end(); iter++,oiter++ )
    if( *iter != *oiter )
      return False;
  return True;
  //## end HIID::operator==%3BE96FE601C5_eq.body
}

inline bool HIID::operator!=(const HIID &right) const
{
  //## begin HIID::operator!=%3BE96FE601C5_neq.body preserve=yes
  return ! ( (*this) == right );
  //## end HIID::operator!=%3BE96FE601C5_neq.body
}



//## Other Operations (inline)
inline HIID & HIID::add (AtomicID aid)
{
  //## begin HIID::add%3BE97792003D.body preserve=yes
  push_back(aid);
  return *this;
  //## end HIID::add%3BE97792003D.body
}

inline int HIID::length () const
{
  //## begin HIID::length%3C1A187E018C.body preserve=yes
  return size();
  //## end HIID::length%3C1A187E018C.body
}

inline bool HIID::prefixedBy (const HIID &other) const
{
  //## begin HIID::prefixedBy%3CBEB7E2034E.body preserve=yes
  return matches(other|AidWildcard);
  //## end HIID::prefixedBy%3CBEB7E2034E.body
}

inline int HIID::popLeadSlashes ()
{
  //## begin HIID::popLeadSlashes%3C6B9FDD02FD.body preserve=yes
  int n=0;
  while( front() == AidSlash )
  {
    pop_front();
    n++;
  }
  return n;
  //## end HIID::popLeadSlashes%3C6B9FDD02FD.body
}

inline size_t HIID::packSize () const
{
  //## begin HIID::packSize%3C591278038A.body preserve=yes
  return size()*sizeof(int);
  //## end HIID::packSize%3C591278038A.body
}

//## begin module%3C10CC820355.epilog preserve=yes
template<class In> inline HIID::HIID( In first,In last )
      : Vector_AtomicID(first,last)
{
  reserve();
}
//## end module%3C10CC820355.epilog


#endif

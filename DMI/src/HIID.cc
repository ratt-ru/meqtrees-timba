//  HIID.cc: hierarchical ID class
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

#include "HIID.h"

// Class HIID 

namespace DMI
{

//##ModelId=3DB934880197
HIID::HIID (const void* block, int sz)
  : Vector_AtomicID(sz/sizeof(int))
{
  reserve();
  unpack(block,sz);
}


//##ModelId=3BE977510397
HIID & HIID::add (const HIID &other)
{
  if( other.empty() )
    return *this;
  int n = size();
  resize(n+other.size());
  for( const_iterator iter = other.begin(); iter != other.end(); iter++ )
    (*this)[n++] = *iter;
  return *this;
}

//##ModelId=3C55695F00CC
HIID HIID::subId (int first, int last) const
{
  const_iterator iter1 = first >= 0 ? begin()+first : end()-first;
  const_iterator iter2 = last >= 0 ? begin()+(last+1) : end()-(last+1);
  if( iter1 >= iter2 )
    return HIID();
  else
    return HIID(iter1,iter2);
}

//##ModelId=3BE9792B0135
bool HIID::matches (const HIID &other) const
{
  if( this == &other )
    return true;
  
  CVI iter = begin(),
      oiter = other.begin();
  for( ; iter != end() && oiter != other.end(); iter++,oiter++ )
  {
    // hit a wildcard? matches everything till the end...
    if( (*iter).isWildcard() || (*oiter).isWildcard() )
      return true;
    if( !(*iter).matches(*oiter) )  // mismatch at this position - drop out
      return false;
  }
  // got to end of one? Match only if this is simultaneous, or either one
  // ends with wildcard
  return ( iter == end() || (*iter).isWildcard() ) && 
         ( oiter == other.end() || (*oiter).isWildcard() );
}

//##ModelId=3C99A0400186
bool HIID::subsetOf (const HIID &other) const
{
  if( this == &other )
    return true;
  
  CVI iter = begin(),
      oiter = other.begin();
  for( ; iter != end() && oiter != other.end(); iter++,oiter++ )
  {
    if( (*oiter).isWildcard() )       // other is "*" so we're always a subset
      return true;
    if( (*iter).isWildcard()  ||      // we have "*" and they don't => fail
        ((*iter).isAny() && !(*oiter).isAny()) || // we have "?" they don't => fail
        !(*iter).matches(*oiter)  )   // mismatch at this position
      return false;
  }
  // both had to have ended simultaneously (or the other HIID might have
  // an extra wildcard)
  return iter == end() && ( oiter == other.end() || (*oiter).isWildcard() );
}


//##ModelId=3C59522600D6
int HIID::popLeadIndex ()
{
  if( !size() )
    return 0;
  int ret = front().index();
  if( ret<0 ) 
    return 0;
  pop_front(1);
  return ret;
}

//##ModelId=3C6B86D5003A
int HIID::popTrailIndex ()
{
  if( !size() )
    return 0;
  int ret = back().index();
  if( ret<0 ) 
    return 0;
  resize(size()-1);
  return ret;
}

//##ModelId=3CAD7B2901CA
HIID HIID::splitAtSlash ()
{
  HIID subid;
//   while( size() )
//   {
//     if( front() == AidSlash )
//     {
//       pop_front(1);
//       return subid;
//     }
//     subid.push_back(front());
//     pop_front();
//   }
  int pos = findFirstSlash();
  // no slash -- return entire id and clear
  if( pos<0 )
  {
    subid = (*this);
    clear();
  }
  else // copy subid up to and including slash; pop everything including slash
  {
    if( pos )
    {
      subid.resize(pos);
      memcpy(&subid.front(),&front(),pos*sizeof(AtomicID));
    }
    pop_front(pos+1);
  }
  return subid;
}

//##ModelId=3C0F8BD5004F
string HIID::toString (char separator) const
{
  string s("(null)");
  if( size()>0 )
  {
    const_iterator iter = begin();
    s = (*iter).toString();
    bool sep = ( *iter == AidSlash || *iter == AidRange );
    for( iter++; iter != end(); iter++ )
    {
      bool newsep = ( *iter == AidSlash || *iter == AidRange );
      if( !sep && !newsep )
        s += separator;
      s += (*iter).toString();
      sep = newsep;
    }
  }
  return s;
}

//##ModelId=3E01BA7A02AF
void HIID::print () const
{ 
  print(std::cout); 
  std::cout<<endl;
}

//##ModelId=3C5912FE0134
size_t HIID::pack (void *block, size_t &nleft) const
{
  size_t sz = size()*sizeof(AtomicID);
  FailWhen(nleft<sz,"block too small");
// vector is contigous, so just use:
  memcpy(block,&(front()),sz);
//   int *data = static_cast<int*>(block);
//   for( CVI iter = begin(); iter != end(); iter++ )
//     *(data++) = *(iter);
  nleft -= sz;
  return sz;
}

//##ModelId=3C970F91006F
void HIID::unpack (const void* block, size_t sz)
{
  FailWhen(sz%sizeof(AtomicID),"bad block size");
  resize(sz/sizeof(AtomicID));
// vector is contigous, so just use:
  memcpy(&(front()),block,sz);
//  const int *data = reinterpret_cast<const int*>(block);
//  for( VI iter = begin(); iter != end(); iter++ )
//    *iter = *(data++);
}

// Additional Declarations
//##ModelId=3DB9348803AA
bool HIID::operator== (const HIID &right) const
{
  if( this == &right )
    return true;
  if( size() != right.size() )
    return false;
// vector is contigous, so just use:
  return !memcmp(&(front()),&(right.front()),size()*sizeof(AtomicID));
//  for( CVI iter = begin(),oiter = right.begin(); iter != end(); iter++,oiter++ )
//    if( *iter != *oiter )
//      return false;
//  return true;
}

//##ModelId=3DB9348B01E2
bool HIID::operator < (const HIID &right) const
{
  if( this == &right )
    return false;
  
  CVI iter = begin(),
      oiter = right.begin();
  // go up to end of this or other, and return result if a strict != was found
  for( ; iter != end() && oiter != right.end(); iter++,oiter++ )
  {
    if( (*iter) < (*oiter) )
      return true;
    else if( (*iter) > (*oiter) )
      return false;
  }
  // got to end of one or the other and everything is equal -- if there's
  // something left in the other, then we are <
  return oiter != right.end();
}


//##ModelId=3DB9348C0305
void HIID::addString (const string &str,const string &sepset)
{
  size_t totlen = str.length();
  if( !str.length() )
    return;
  size_t p0=0,p1;
  // split string into fields separated by separator char, and create an 
  // AtomicID for each field. "/" and ":" also serve as separators,
  // but they also correspond to their own AtomicIDs
  string sep_set = sepset + "/:";
  while( p0 != string::npos )
  {
    if( p0 == totlen )
    {
      push_back(AidEmpty);
      break;
    }
    else
    {
      p1 = str.find_first_of(sep_set,p0);
      if( p1 != string::npos )
      {
        push_back( p1 != p0 ? AtomicID(str.substr(p0,p1-p0)) : AidEmpty);
        if( str[p1] == '/' )
          push_back( AidSlash );
        else if( str[p1] == ':' )
          push_back( AidRange );
        p0 = p1+1;
      }
      else
      {
        push_back(AtomicID(str.substr(p0)));
        break;
      }
    }
  }
}

};

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
  return HIID(iter1,iter2);
}

//##ModelId=3BE9792B0135
bool HIID::matches (const HIID &other) const
{
  if( this == &other )
    return True;
  
  CVI iter = begin(),
      oiter = other.begin();
  for( ; iter != end() && oiter != other.end(); iter++,oiter++ )
  {
    // hit a wildcard? matches everything till the end...
    if( (*iter).isWildcard() || (*oiter).isWildcard() )
      return True;
    if( !(*iter).matches(*oiter) )  // mismatch at this position - drop out
      return False;
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
    return True;
  
  CVI iter = begin(),
      oiter = other.begin();
  for( ; iter != end() && oiter != other.end(); iter++,oiter++ )
  {
    if( (*oiter).isWildcard() )       // other is "*" so we're always a subset
      return True;
    if( (*iter).isWildcard()  ||      // we have "*" and they don't => fail
        ((*iter).isAny() && !(*oiter).isAny()) || // we have "?" they don't => fail
        !(*iter).matches(*oiter)  )   // mismatch at this position
      return False;
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
  pop_front();
  return ret;
}

//##ModelId=3C6B86D5003A
int HIID::popTrailIndex ()
{
  if( !size() )
    return 0;
  int ret = front().index();
  if( ret<0 ) 
    return 0;
  pop_back();
  return ret;
}

//##ModelId=3C7A1B6500C9
int HIID::findFirstSlash () const
{
  int pos = 0;
  for( const_iterator iter = begin(); iter != end(); iter++,pos++ )
    if( *iter == AidSlash )
      return pos;
  return -1;
}

//##ModelId=3CAD7B2901CA
HIID HIID::splitAtSlash ()
{
  HIID subid;
  while( size() )
  {
    if( front() == AidSlash )
    {
      pop_front();
      return subid;
    }
    subid.push_back(front());
    pop_front();
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
  size_t sz = size()*sizeof(int);
  FailWhen(nleft<sz,"block too small");
  int *data = static_cast<int*>(block);
  for( CVI iter = begin(); iter != end(); iter++ )
    *(data++) = *(iter);
  nleft -= sz;
  return sz;
}

//##ModelId=3C970F91006F
void HIID::unpack (const void* block, size_t sz)
{
  FailWhen(sz%sizeof(int),"bad block size");
  resize(sz/sizeof(int));
  const int *data = reinterpret_cast<const int*>(block);
  for( VI iter = begin(); iter != end(); iter++ )
    *iter = *(data++);
}

// Additional Declarations
//##ModelId=3DB9348803AA
bool HIID::operator== (const HIID &right) const
{
  if( this == &right )
    return True;
  if( size() != right.size() )
    return False;
  for( CVI iter = begin(),oiter = right.begin(); iter != end(); iter++,oiter++ )
    if( *iter != *oiter )
      return False;
  return True;
}

//##ModelId=3DB9348B01E2
bool HIID::operator < (const HIID &right) const
{
  if( this == &right )
    return False;
  
  CVI iter = begin(),
      oiter = right.begin();
  // go up to end of this or other, and return result if a strict != was found
  for( ; iter != end() && oiter != right.end(); iter++,oiter++ )
  {
    if( (*iter) < (*oiter) )
      return True;
    else if( (*iter) > (*oiter) )
      return False;
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


// Detached code regions:
#if 0
// 
//   // advance an iter past first sequence of leading slashes (if any)
//   CVI iter0 = begin();
//   while( iter0 != end() && *iter0 == AidSlash )
//     iter0++;
//   // now, look for next slash
//   CVI iter = iter0;
//   while( iter != end() && *iter != AidSlash )
//     iter++;
//   // got to end? Return copy of ourselves.
//   if( iter == end() )
//   {
// //   HIID ret(iter0,end());
//     clear();
//     return ret;
//   }
//   // else return subsequence
// //  HIID ret(iter0,iter);
// //  erase(begin(),++iter);
//   return ret;

  if( !size() )
    return 0;
  AtomicID ret = front();
  if( ret != AidSlash ) 
    return 0;
  pop_front();
  return ret;

#endif

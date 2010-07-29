//  HIID.cc: hierarchical ID class
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

#include "HIID.h"

// Class HIID 

namespace DMI
{
  
// for literal HIIDs, this is used as a marker in the first element.
const int LITERAL_MARKER      = 0x7FFF0000;
const int LITERAL_MASK        = 0xFFFF0000;
const int LITERAL_LENGTH_MASK = 0x0000FFFF;
const int LITERAL_RATIO       = sizeof(AtomicID)/sizeof(char);


//##ModelId=3DB934880197
HIID::HIID (const void* block, int sz)
{
  unpack(block,sz);
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
  HIID_Base::resize(size()-1);
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
string HIID::toString (char separator,bool mark_lit) const
{
  if( empty() )
    return "(null)";
//   if( front() == LITERAL_MARKER )
//   {
//     string s(mark_lit?"$":"");
//     const char *buf = reinterpret_cast<const char*>(&(*this)[1]);
//     // max buffer size -- actual string may be shorter
//     uint bufsize = (size()-1)*(sizeof(AtomicID)/sizeof(char));
//     if( bufsize && !buf[bufsize-1] )  // buffer is null-terminated
//       return s + string(buf);
//     else // buffer is full
//       return s + string(buf,buf+bufsize);
//   }
//   else
//   {
//     const_iterator iter = begin();
//     string s = (*iter).toString();
//     bool sep = ( *iter == AidSlash || *iter == AidRange );
//     for( iter++; iter != end(); iter++ )
//     {
//       bool newsep = ( *iter == AidSlash || *iter == AidRange );
//       if( !sep && !newsep )
//         s += separator;
//       s += (*iter).toString();
//       sep = newsep;
//     }
//     return s;
//   }
  
  bool sep = true;
  string result;
  for( const_iterator iter = begin(); iter != end(); iter++ )
  {
    if( (iter->id()&LITERAL_MASK) == LITERAL_MARKER ) // process literal string
    {
      if( !sep )
        result += separator;
      int len = iter->id()&LITERAL_LENGTH_MASK;
      int size = (len+LITERAL_RATIO-1)/LITERAL_RATIO;
      iter++;
      if( mark_lit )
        result += "$";
      result += string(reinterpret_cast<const char*>(&(*iter)),len);
      iter += size-1; // skip over the aids forming the literal string
      sep = false;
    }
    else
    {
      bool newsep = ( *iter == AidSlash || *iter == AidRange );
      if( !sep && !newsep )
        result += separator;
      result += (*iter).toString();
      sep = newsep;
    }
  }
  return result;
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
  if( sz )
  {
    memcpy(block,&(front()),sz);
    nleft -= sz;
  }
  return sz;
}

//##ModelId=3C970F91006F
void HIID::unpack (const void* block, size_t sz)
{
  FailWhen(sz%sizeof(AtomicID),"bad block size");
  resize(sz/sizeof(AtomicID));
// vector is contigous, so just use:
  if( sz )
  {
    memcpy(&(front()),block,sz);
  }
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

void HIID::makeLiteral (const string &str,int ipos)
{
  const int ratio = sizeof(AtomicID)/sizeof(char);
  // work out size to hold literal string
  uint len = str.length();
  uint size = (len+LITERAL_RATIO-1)/LITERAL_RATIO; // used to be: ((len%ratio)!=0), but now we always ensure a zero pad
  uint bufsize = size*ratio;
  resize(ipos+size+1);
  // mark [0] as literal, and copy string starting from [1]
  (*this)[ipos] = LITERAL_MARKER|len;
  char *buf = reinterpret_cast<char*>(&(*this)[ipos+1]);
  str.copy(buf,string::npos);
  // pad with nulls, since buf may be bigger
  if( bufsize-len )
    memset(buf+len,0xFF,bufsize-len);
}
    
//##ModelId=3DB9348C0305
void HIID::addString (const string &str,const string &sepset,bool allow_literal)
{
// is string a literal?
//  if( str[0] == '$' )
//  {
//    // FailWhen(!empty(),"can't add literal HIID to existing one");
//    return makeLiteral(str.substr(1),size());
//  }
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
        if( p1 != p0 )
        {
          string name(str.substr(p0,p1-p0));
          int aid;
          if( name[0] == '$' )
          {
            allow_literal = true;
            makeLiteral(strlowercase(name.substr(1)),size());
          }
          else if( AtomicID::findName(aid,name) )
            push_back(AtomicID(aid));
          else if( allow_literal ) // convert to literal form
            makeLiteral(strlowercase(name),size());
          else
            Throw("Unknown AtomicID `"+name+"'");
        }
        else
          push_back(AidEmpty);
        if( str[p1] == '/' )
          push_back( AidSlash );
        else if( str[p1] == ':' )
          push_back( AidRange );
        p0 = p1+1;
      }
      else
      {
        string name(str.substr(p0));
        int aid;
        if( name[0] == '$' )
          makeLiteral(strlowercase(name.substr(1)),size());
        else if( AtomicID::findName(aid,name) )
          push_back(AtomicID(aid));
        else if( allow_literal ) // convert to literal form
          makeLiteral(strlowercase(name),size());
        else
          Throw("Unknown AtomicID `"+name+"'");
        break;
      }
    }
  }
}

};

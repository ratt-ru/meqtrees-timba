//##ModelId=3DB934880197
//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820357.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820357.cm

//## begin module%3C10CC820357.cp preserve=no
//## end module%3C10CC820357.cp

//## Module: HIID%3C10CC820357; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\HIID.cc

//## begin module%3C10CC820357.additionalIncludes preserve=no
//## end module%3C10CC820357.additionalIncludes

//## begin module%3C10CC820357.includes preserve=yes
//## end module%3C10CC820357.includes

// HIID
#include "DMI/HIID.h"
//## begin module%3C10CC820357.declarations preserve=no
//## end module%3C10CC820357.declarations

//## begin module%3C10CC820357.additionalDeclarations preserve=yes
//## end module%3C10CC820357.additionalDeclarations


// Class HIID 

HIID::HIID (const void* block, int sz)
  //## begin HIID::HIID%3C556A470346.hasinit preserve=no
  //## end HIID::HIID%3C556A470346.hasinit
  //## begin HIID::HIID%3C556A470346.initialization preserve=yes
  : Vector_AtomicID(sz/sizeof(int))
  //## end HIID::HIID%3C556A470346.initialization
{
  //## begin HIID::HIID%3C556A470346.body preserve=yes
  reserve();
  unpack(block,sz);
  //## end HIID::HIID%3C556A470346.body
}



//##ModelId=3BE977510397
//## Other Operations (implementation)
HIID & HIID::add (const HIID &other)
{
  //## begin HIID::add%3BE977510397.body preserve=yes
  if( other.empty() )
    return *this;
  int n = size();
  resize(n+other.size());
  for( const_iterator iter = other.begin(); iter != other.end(); iter++ )
    (*this)[n++] = *iter;
  return *this;
  //## end HIID::add%3BE977510397.body
}

//##ModelId=3C55695F00CC
HIID HIID::subId (int first, int last) const
{
  //## begin HIID::subId%3C55695F00CC.body preserve=yes
  const_iterator iter1 = first >= 0 ? begin()+first : end()-first;
  const_iterator iter2 = last >= 0 ? begin()+(last+1) : end()-(last+1);
  return HIID(iter1,iter2);
  //## end HIID::subId%3C55695F00CC.body
}

//##ModelId=3BE9792B0135
bool HIID::matches (const HIID &other) const
{
  //## begin HIID::matches%3BE9792B0135.body preserve=yes
  CVI iter = begin(),
      oiter = other.begin();
  for( ; iter != end() && oiter != other.end(); iter++,oiter++ )
  {
    // hit a wildcard? matches everything till the end...
    if( iter->isWildcard() || oiter->isWildcard() )
      return True;
    if( !(*iter).matches(*oiter) )  // mismatch at this position - drop out
      return False;
  }
  // got to end of one? Match only if this is simultaneous
  return iter == end() && oiter == other.end();
  //## end HIID::matches%3BE9792B0135.body
}

//##ModelId=3C99A0400186
bool HIID::subsetOf (const HIID &other) const
{
  //## begin HIID::subsetOf%3C99A0400186.body preserve=yes
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
  return iter == end() && ( oiter == other.end() || oiter->isWildcard());
  //## end HIID::subsetOf%3C99A0400186.body
}

//##ModelId=3C59522600D6
int HIID::popLeadIndex ()
{
  //## begin HIID::popLeadIndex%3C59522600D6.body preserve=yes
  if( !size() )
    return 0;
  int ret = front().index();
  if( ret<0 ) 
    return 0;
  pop_front();
  return ret;
  //## end HIID::popLeadIndex%3C59522600D6.body
}

//##ModelId=3C6B86D5003A
int HIID::popTrailIndex ()
{
  //## begin HIID::popTrailIndex%3C6B86D5003A.body preserve=yes
  if( !size() )
    return 0;
  int ret = front().index();
  if( ret<0 ) 
    return 0;
  pop_back();
  return ret;
  //## end HIID::popTrailIndex%3C6B86D5003A.body
}

//##ModelId=3C7A1B6500C9
int HIID::findFirstSlash () const
{
  //## begin HIID::findFirstSlash%3C7A1B6500C9.body preserve=yes
  int pos = 0;
  for( const_iterator iter = begin(); iter != end(); iter++,pos++ )
    if( *iter == AidSlash )
      return pos;
  return -1;
  //## end HIID::findFirstSlash%3C7A1B6500C9.body
}

//##ModelId=3CAD7B2901CA
HIID HIID::splitAtSlash ()
{
  //## begin HIID::splitAtSlash%3CAD7B2901CA.body preserve=yes
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
  //## end HIID::splitAtSlash%3CAD7B2901CA.body
}

//##ModelId=3C0F8BD5004F
string HIID::toString () const
{
  //## begin HIID::toString%3C0F8BD5004F.body preserve=yes
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
        s += ".";
      s += (*iter).toString();
      sep = newsep;
    }
  }
  return s;
  //## end HIID::toString%3C0F8BD5004F.body
}

//##ModelId=3C5912FE0134
size_t HIID::pack (void *block, size_t &nleft) const
{
  //## begin HIID::pack%3C5912FE0134.body preserve=yes
  size_t sz = size()*sizeof(int);
  FailWhen(nleft<sz,"block too small");
  int *data = static_cast<int*>(block);
  for( CVI iter = begin(); iter != end(); iter++ )
    *(data++) = *(iter);
  nleft -= sz;
  return sz;
  //## end HIID::pack%3C5912FE0134.body
}

//##ModelId=3C970F91006F
void HIID::unpack (const void* block, size_t sz)
{
  //## begin HIID::unpack%3C970F91006F.body preserve=yes
  FailWhen(sz%sizeof(int),"bad block size");
  resize(sz/sizeof(int));
  const int *data = reinterpret_cast<const int*>(block);
  for( VI iter = begin(); iter != end(); iter++ )
    *iter = *(data++);
  //## end HIID::unpack%3C970F91006F.body
}

// Additional Declarations
//##ModelId=3DB9348B01E2
  //## begin HIID%3BE96FE601C5.declarations preserve=yes
bool HIID::operator < (const HIID &right) const
{
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
void HIID::addString (const string &str)
{
  size_t totlen = str.length();
  if( !str.length() )
    return;
  size_t p0=0,p1;
  // split string into fields separated by '.', and create an 
  // AtomicID for each field. "/" and ":" also serve as separators,
  // but they also correspond to their own AtomicIDs
  while( p0 != string::npos )
  {
    if( p0 == totlen )
    {
      push_back(AidEmpty);
      break;
    }
    else
    {
      p1 = str.find_first_of("./:",p0);
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
  //## end HIID%3BE96FE601C5.declarations
//## begin module%3C10CC820357.epilog preserve=yes
//## end module%3C10CC820357.epilog


// Detached code regions:
#if 0
//## begin HIID::popLeadSubId%3C6BC6DD0068.body preserve=yes
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
//## end HIID::popLeadSubId%3C6BC6DD0068.body

//## begin HIID::popLeadDelim%3C5952AD0261.body preserve=yes
  if( !size() )
    return 0;
  AtomicID ret = front();
  if( ret != AidSlash ) 
    return 0;
  pop_front();
  return ret;
//## end HIID::popLeadDelim%3C5952AD0261.body

#endif

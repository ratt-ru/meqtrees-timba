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
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\HIID.cc

//## begin module%3C10CC820357.additionalIncludes preserve=no
//## end module%3C10CC820357.additionalIncludes

//## begin module%3C10CC820357.includes preserve=yes
//## end module%3C10CC820357.includes

// HIID
#include "HIID.h"
//## begin module%3C10CC820357.declarations preserve=no
//## end module%3C10CC820357.declarations

//## begin module%3C10CC820357.additionalDeclarations preserve=yes
//## end module%3C10CC820357.additionalDeclarations


// Class HIID 

HIID::HIID (const char* block, int size)
  //## begin HIID::HIID%3C556A470346.hasinit preserve=no
  //## end HIID::HIID%3C556A470346.hasinit
  //## begin HIID::HIID%3C556A470346.initialization preserve=yes
  : Vector_AtomicID(size/sizeof(int))
  //## end HIID::HIID%3C556A470346.initialization
{
  //## begin HIID::HIID%3C556A470346.body preserve=yes
  reserve();
  const int *data = (const int*) block;
  for( VI iter = begin(); iter != end(); iter++ )
    *iter = *(data++);
  //## end HIID::HIID%3C556A470346.body
}



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

HIID HIID::subId (int first, int last) const
{
  //## begin HIID::subId%3C55695F00CC.body preserve=yes
  const_iterator iter1 = first >= 0 ? begin()+first : end()-first;
  const_iterator iter2 = last >= 0 ? begin()+(last+1) : end()-(last+1);
  return HIID(iter1,iter2);
  //## end HIID::subId%3C55695F00CC.body
}

bool HIID::matches (const HIID &other) const
{
  //## begin HIID::matches%3BE9792B0135.body preserve=yes
  if( other.length() > length() )  // other is longer - no match then
    return False;
  CVI iter = begin(),
      oiter = other.begin();
  for( ; iter != end() && oiter != other.end(); iter++,oiter++ )
  {
    if( (*iter).isWildcard() || (*oiter).isWildcard() )   // wildcard in either will match
      return True;
    if( (*iter).matches(*oiter) )  // mismatch at this position - drop out
      return False;
  } 
  // got to end of one or the other? Then it's a match if both are at the end.
  return iter == end() && oiter == other.end();
  //## end HIID::matches%3BE9792B0135.body
}

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

AtomicID HIID::popLeadDelim ()
{
  //## begin HIID::popLeadDelim%3C5952AD0261.body preserve=yes
  if( !size() )
    return 0;
  AtomicID ret = front();
  if( ret != AidDot ) 
    return 0;
  pop_front();
  return ret;
  //## end HIID::popLeadDelim%3C5952AD0261.body
}

string HIID::toString () const
{
  //## begin HIID::toString%3C0F8BD5004F.body preserve=yes
  string s("(null)");
  if( size()>0 )
  {
    const_iterator iter = begin();
    s = (*iter).toString();
    for( iter++; iter != end(); iter++ )
      s += "." + (*iter).toString();
  }
  return s;
  //## end HIID::toString%3C0F8BD5004F.body
}

void HIID::copy (char *block) const
{
  //## begin HIID::copy%3C5912FE0134.body preserve=yes
  int *data = (int*) block;
  for( CVI iter = begin(); iter != end(); iter++ )
    *(data++) = *(iter);
  //## end HIID::copy%3C5912FE0134.body
}

// Additional Declarations
  //## begin HIID%3BE96FE601C5.declarations preserve=yes
void HIID::addString (const string &str)
{
  size_t p0=0,p1;
  // split string into fields separated by '.',
  // and create an AtomicID for each field
  while( p0 != string::npos )
  {
    size_t len = p1 = str.find('.',p0);
    if( len != string::npos )
      len -= p0;
    push_back( AtomicID( str.substr(p0,len) ) );
    p0 = p1 == string::npos ? p1 : p1+1;
  }
}
  //## end HIID%3BE96FE601C5.declarations
//## begin module%3C10CC820357.epilog preserve=yes
//## end module%3C10CC820357.epilog

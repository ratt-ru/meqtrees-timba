//  AtomicID.cc: atomic integer ID class
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

#include "AtomicID.h"
#include <ctype.h>

DefineBiRegistry(AtomicID,0,"");

// pull in all auto-generated registry definitions
int aidRegistry_DMI();
static int dum = aidRegistry_DMI();

// define the strlwr function for strings
string strlowercase (const string &in)
{
  string out = in;
  for( string::iterator iter = out.begin(); iter != out.end(); iter++ )
    *iter = tolower(*iter);
  return out;
}

//##ModelId=3BE9709700A7
string AtomicID::toString () const
{
  char s[64];
  // if ID is an index, return that
  int idx = index();
  if( idx>=0 )
  {
    sprintf(s,"%d",idx);
    return s;
  }
  // lookup ID in symbolic name map, return if found
  string name = registry.find(id());
  if( name.length() )
    return name;
  // else return unknown ID
  sprintf(s,"[?%d]",id());
  return s;
}

//##ModelId=3E01BE06024F
void AtomicID::print () const
{
  print(std::cout); 
  std::cout<<endl;
}

//##ModelId=3C68D5ED01F8
int AtomicID::findName (const string &str)
{
  for( size_t i=0; i<str.length(); i++ )
#ifdef __GLIBCPP__
    if( !std::isdigit( str[i] ) )
#else
    if( !isdigit( str[i] ) )
#endif
    {
      int ret = registry.rfind(strlowercase(str));
#ifdef ATOMICID_VERBOSE_REGISTER
      cerr<<"AtomicID::findName("<<str<<")="<<ret<<endl;
#endif
      return ret;
    }
  return atoi(str.c_str());
}

// Additional Declarations

#ifdef ATOMICID_VERBOSE_REGISTER
template <>
Registrar<int,string,AtomicID>::Registrar (const int &key, const string &val)
{
  cerr<<"Registering key "<<key<<"="<<val<<endl;
  AtomicID::registry.add(key,val,strlowercase(val));
}
#else
template <>
Registrar<int,string,AtomicID>::Registrar (const int &key, const string &val)
{
  AtomicID::registry.add(key,val,strlowercase(val));
}
#endif

int __register_extra_aids_ =
   AtomicID::registerId(AidNull.id(),"0") +
   AtomicID::registerId(AidAny.id(),"?") +
   AtomicID::registerId(AidWildcard.id(),"*") +
   AtomicID::registerId(AidSlash.id(),"/") +
   AtomicID::registerId(AidRange.id(),":") +
   AtomicID::registerId(AidEmpty.id(),"_") +
   AtomicID::registerId(AidHash.id(),"#");

int AtomicID::registerId (int key,const char * value)
{
  string val = value;
//  cerr<<"Registering key "<<key<<"="<<val<<endl;
  registry.add(key,val,strlowercase(val));
  return key;
}
      

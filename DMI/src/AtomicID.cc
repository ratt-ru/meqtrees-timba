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

//##ModelId=3E01B4A900A8
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
      int ret = registry.rfind(str);
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
  AtomicID::registry.add(key,val);
}
#endif

static AtomicID::Register
     null(AidNull.id(),"0"),
     any(AidAny.id(),"?"),
     wild(AidWildcard.id(),"*"),
     slash(AidSlash.id(),"/"),
     range(AidRange.id(),":"),
     empty(AidEmpty.id(),"_");

// Class AidIndex 

// Additional Declarations



// Detached code regions:
#if 0
  cerr<<"Registering key "<<key<<"="<<val<<endl;
  AtomicID::registry.add(key,val);

#endif

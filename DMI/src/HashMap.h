//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#ifndef DMI_HashMap_h
#define DMI_HashMap_h 1

#include <DMI/BObj.h>
#include <DMI/BlockSet.h>

#if __GNUC__ >= 3 

#include <ext/hash_map>
#include <string>
    
//// we don't support 3.0 anyway, and everything later than that
//// uses __gnu_cxx
// #if __GNUC_MINOR__ == 0
//   #define DMI_hash_namespace std
// #else
#define DMI_hash_namespace __gnu_cxx
// #endif
        
namespace DMI
{
  using DMI_hash_namespace::hash_map;
};
    
// include implementation of hash for std::strings
// this borrows from include/c++/ext/hash_fun.h in the GCC STL
namespace DMI_hash_namespace
{
  
template<>
struct hash<std::string> : public hash<const char *>
{
  size_t operator () (const std::string &x) const
  { unsigned long __h = 0;
    const char *__s = x.data(), *end = __s + x.length();
    for ( ; __s < end; ++__s )
      __h = 5*__h + *__s;
    return size_t(__h);
  }
};

};
    
#else
// not a gnu compiler
  #error hash_map not implemented in this compiler
#endif

#endif

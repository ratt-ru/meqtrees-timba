#ifndef DMI_HashMap_h
#define DMI_HashMap_h 1

#include <DMI/DMI.h>

#include <ext/hash_map>
#include <string>

#define DMI_hash_namespace __gnu_cxx    
        
namespace DMI
{
  using __gnu_cxx::hash_map;
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
    
    
#endif

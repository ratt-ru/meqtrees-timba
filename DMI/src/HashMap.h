#ifndef DMI_HashMap_h
#define DMI_HashMap_h 1

#include <DMI/BObj.h>
#include <DMI/BlockSet.h>

#if __GNUC__ >= 3 

#include <ext/hash_map>
#include <string>
    
#if __GNUC_MINOR__ == 0
  #define DMI_hash_namespace std
#else
  #define DMI_hash_namespace __gnu_cxx
#endif
        
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

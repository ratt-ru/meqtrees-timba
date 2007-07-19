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

#ifndef DMI_Registry_h
#define DMI_Registry_h 1

#include <TimBase/Debug.h>
#include <DMI/DMI.h>
#include <map>

#ifdef USE_THREADS
#include <TimBase/Thread/Mutex.h>
#define lockMutex LOFAR::Thread::Mutex::Lock _lock(HostClass::_registry_mutex)
#define declareMutex static pthread_mutex_t _registry_mutex
#define defineMutex(Class) pthread_mutex_t Class::_registry_mutex = PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP
#else
#define lockMutex
#define declareMutex
#define defineMutex(Class) 
#endif

// macro: inserts a registry into a class declaration
#define DeclareRegistry(Class,Key,Value)    \
  public: typedef UniRegistry<Key,Value,Class> Registry;    \
          typedef Registrar<Key,Value,Class> Register;    \
          static int addToRegistry(const Key&,const Value&); \
          static const Registry::Map & getRegistryMap () { return *_registry_map; } \
  private: static Registry registry;    \
           static Registry::Map *_registry_map;    \
           friend class UniRegistry<Key,Value,Class>;    \
           friend class Registrar<Key,Value,Class>;    \
           declareMutex;   \

// macro: inserts registry definitions into .cc file
#define DefineRegistry(Class,defval) \
  Class::Registry Class::registry(defval); \
  Class::Registry::Map * Class::_registry_map = 0; \
  defineMutex(Class); \
  int Class::addToRegistry (const Class::Registry::KeyType &key,\
                            const Class::Registry::Value &val) \
  { registry.add(key,val); return 1; }

// macro: inserts a registry into a class declaration
#define DeclareBiRegistry(Class,Key,Value)    \
  public: typedef BiRegistry<Key,Value,Class> Registry;    \
          typedef Registrar<Key,Value,Class> Register;    \
          static int addToRegistry(const Key&,const Value&); \
          static const Registry::Map & getRegistryMap () { return *_registry_map; } \
          static const Registry::RevMap & getRegistryRevMap () { return *_registry_rmap; } \
  private:  static Registry registry;    \
            static Registry::Map *_registry_map;    \
            static Registry::RevMap *_registry_rmap;    \
            friend class BiRegistry<Key,Value,Class>;    \
            friend class UniRegistry<Key,Value,Class>;    \
            friend class Registrar<Key,Value,Class>;    \
            declareMutex;   
            
// macro: inserts registry definitions into .cc file
#define DefineBiRegistry(Class,defkey,defval)    \
  Class::Registry Class::registry(defkey,defval);    \
  Class::Registry::Map * Class::_registry_map = 0;    \
  Class::Registry::RevMap * Class::_registry_rmap = 0;    \
  defineMutex(Class);  \
  int Class::addToRegistry (const Class::Registry::KeyType &key,\
                            const Class::Registry::Value &val) \
  { registry.add(key,val); return 1; }

namespace DMI
{
  
class DebugRegistry 
{
  public:
    LocalDebugContext;
};

//##ModelId=3C5A6FD40213
//##Documentation
//## Registry is a template class for maintaining auto-generated
//## registries (maps). This template should not be invoked directly, but
//## rather through the two macros provided below. To add a registry to
//## your class, you should:
//## 1.  Invoke the macro DeclareRegistry(YourClass,KeyType,ValueType)
//## inside your class declaration. This adds the necessary data members,
//## and declares the Registry type inside your class.
//## 
//## 2. Invoke the macro DefineRegistry(YourClass,defaultValue) somewhere
//## in your .cc file.
//## 
//## You can now use the YourClass::Registry::add() and ::find() methods
//## to manipulate the registry.  Entries may also be added simply by
//## constructing objects of type YourClass::Registry. In this way, you
//## can have the registry populated on strartup via simple static object
//## declarations. See AtomicID for an example.
template <class Key, class Val, class HostClass>
class UniRegistry 
{
  public:
      //##ModelId=3C5E983901C3
      UniRegistry (const Val& defval);

    //##ModelId=3DB934FD0326
      virtual ~UniRegistry();


      //##ModelId=3C5A72C7006A
      //##Documentation
      //## Adds entry to the registry.
      virtual void add (const Key& key, const Val &val,bool overwrite=false);

      //##ModelId=3C5A7307013F
      //##Documentation
      //## Looks up entry, returns default value if not found.
      const Val & find (const Key& key);

    // Additional Public Declarations
    //##ModelId=3DB9343E032B
      typedef Key KeyType;
    //##ModelId=3DB9343E0353
      typedef Val Value;
    //##ModelId=3DB9343E0399
      typedef std::map<Key,Val> Map;
      
      ImportDebugContext(DebugRegistry);
      
  private:
    //##ModelId=3DB934FD0362
      UniRegistry(const UniRegistry< Key,Val,HostClass > &right);

    //##ModelId=3DB934FD03D0
      UniRegistry< Key,Val,HostClass > & operator=(const UniRegistry< Key,Val,HostClass > &right);

  private:
    // Data Members for Class Attributes

      //##ModelId=3C5EA19F005A
      Val default_value;

};

//##ModelId=3C5E8CAC035D
template <class Key, class Val, class HostClass>
class BiRegistry : public UniRegistry<Key, Val, HostClass>
{
  public:
      //##ModelId=3C5E985C02A0
      BiRegistry (const Key& defkey, const Val& defval);

    //##ModelId=3DB934460180
      virtual ~BiRegistry();


      //##ModelId=3C5E8D9402F3
      void add (const Key& key, const Val &val,bool overwrite=false);
    //##ModelId=3E9D78D20196
      void add (const Key& key, const Val &val,const Val &revval,bool overwrite=false);

      //##ModelId=3C5E8E2D01C6
      const Key & rfind (const Val& val);

      //##ModelId=3C5E8DA00097
      const Key & rfind_more ();

    // Additional Public Declarations
    //##ModelId=3DB934390373
      typedef std::map<Val,Key> RevMap;
      
      ImportDebugContext(DebugRegistry);
      
  private:
    //##ModelId=3DB9344601A8
      BiRegistry(const BiRegistry< Key,Val,HostClass > &right);

    //##ModelId=3DB934460220
      BiRegistry< Key,Val,HostClass > & operator=(const BiRegistry< Key,Val,HostClass > &right);

    // Additional Private Declarations
    //##ModelId=3DB934460125
      typename RevMap::const_iterator riter;
  private:
    // Data Members for Class Attributes

      //##ModelId=3C5EA181038C
      Key default_key;

};

//##ModelId=3C5E8E9D011D

template <class Key, class Val, class HostClass>
class Registrar 
{
  public:
      //##ModelId=3C5E8EC40246
      Registrar (const Key &key, const Val &val);
  
      ImportDebugContext(DebugRegistry);

  private:
    //##ModelId=3DB934E303C2
      Registrar();

    //##ModelId=3DB934E303D6
      Registrar(const Registrar< Key,Val,HostClass > &right);

    //##ModelId=3DB934E40020
      Registrar< Key,Val,HostClass > & operator=(const Registrar< Key,Val,HostClass > &right);

};

// Parameterized Class UniRegistry 

// Parameterized Class BiRegistry 

// Parameterized Class Registrar 

// Parameterized Class UniRegistry 

//##ModelId=3DB934FD0362
template <class Key, class Val, class HostClass>
UniRegistry<Key,Val,HostClass>::UniRegistry (const Val& defval)
  : default_value(defval)
{
  lockMutex;
  #define MapPtr HostClass::_registry_map
  if( !MapPtr )
    MapPtr = new Map;
}


//##ModelId=3DB934FD0326
template <class Key, class Val, class HostClass>
UniRegistry<Key,Val,HostClass>::~UniRegistry()
{
}



//##ModelId=3C5A72C7006A
template <class Key, class Val, class HostClass>
void UniRegistry<Key,Val,HostClass>::add (const Key& key, const Val &val,bool overwrite)
{
  lockMutex;
  if( !MapPtr )
    MapPtr = new Map;

  typename Map::iterator iter = MapPtr->find(key);
  cdebug(1)<<"registering "<<key<<"="<<val<<std::endl;
  
  if( iter == MapPtr->end() )
    MapPtr->insert(std::make_pair(key,val));
  else if( iter->second != val )
  {
    if( overwrite )
      iter->second = val;
    else
    {
      std::cerr<<"Error: conflicting registry definitions for key "<<key<<": "<<
        iter->second<<" and "<<val<<std::endl;
      Throw("Conflicting registry definition");
    }
  }
}

//##ModelId=3C5A7307013F
template <class Key, class Val, class HostClass>
const Val & UniRegistry<Key,Val,HostClass>::find (const Key& key)
{
  lockMutex;
  if( !MapPtr )
    return default_value;
  typename Map::const_iterator iter = MapPtr->find(key);
  if( iter == MapPtr->end() )
    return default_value;
  return iter->second;
}

// Parameterized Class BiRegistry 

//##ModelId=3DB9344601A8
template <class Key, class Val, class HostClass>
BiRegistry<Key,Val,HostClass>::BiRegistry (const Key& defkey, const Val& defval)
  : UniRegistry<Key,Val,HostClass>(defval),default_key(defkey)
{
  #define RevMapPtr HostClass::_registry_rmap
  lockMutex;
  if( !RevMapPtr )
    RevMapPtr = new RevMap;
  riter = RevMapPtr->end();
}


//##ModelId=3DB934460180
template <class Key, class Val, class HostClass>
BiRegistry<Key,Val,HostClass>::~BiRegistry()
{
}



//##ModelId=3C5E8D9402F3
template <class Key, class Val, class HostClass>
void BiRegistry<Key,Val,HostClass>::add (const Key& key, const Val &val,bool overwrite)
{
  lockMutex;
  UniRegistry<Key,Val,HostClass>::add(key,val,overwrite);
  cdebug(1)<<"registering "<<key<<"="<<val<<std::endl;
  if( !RevMapPtr )
    RevMapPtr = new RevMap;
  RevMapPtr->insert(make_pair(val,key));
}

//##ModelId=3E9D78D20196
template <class Key, class Val, class HostClass>
void BiRegistry<Key,Val,HostClass>::add (const Key& key, const Val &val,const Val &revval,bool overwrite)
{
  lockMutex;
  UniRegistry<Key,Val,HostClass>::add(key,val,overwrite);
  cdebug(1)<<"registering "<<key<<"="<<val<<std::endl;
  if( !RevMapPtr )
    RevMapPtr = new RevMap;
  RevMapPtr->insert(make_pair(revval,key));
}

//##ModelId=3C5E8E2D01C6
template <class Key, class Val, class HostClass>
const Key & BiRegistry<Key,Val,HostClass>::rfind (const Val& val)
{
  lockMutex;
  if( !RevMapPtr )
    return default_key;
  riter = RevMapPtr->find(val);
  if( riter == RevMapPtr->end() )
    return default_key;
  else
    return riter->second;
}

//##ModelId=3C5E8DA00097
template <class Key, class Val, class HostClass>
const Key & BiRegistry<Key,Val,HostClass>::rfind_more ()
{
#ifdef USE_THREADS
  Throw("rfind_more not supported in MT environment");
#endif
  lockMutex;
  if( !RevMapPtr )
    return default_key;
  if( riter == RevMapPtr->end() || ++riter == RevMapPtr->end() )
    return default_key;
  return riter->second;
}

// Parameterized Class Registrar 

//##ModelId=3DB934E303D6
//##ModelId=3DB925C4020D
template <class Key, class Val, class HostClass>
Registrar<Key,Val,HostClass>::Registrar (const Key &key, const Val &val)
{
  HostClass::registry.add(key,val);
}


#undef MapPtr
#undef RevMapPtr

}; // namespace DMI

#endif

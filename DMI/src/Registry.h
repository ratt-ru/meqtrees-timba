//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C5A7367022E.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C5A7367022E.cm

//## begin module%3C5A7367022E.cp preserve=no
//## end module%3C5A7367022E.cp

//## Module: Registry%3C5A7367022E; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\Registry.h

#ifndef Registry_h
#define Registry_h 1

//## begin module%3C5A7367022E.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C5A7367022E.additionalIncludes

//## begin module%3C5A7367022E.includes preserve=yes
#ifdef USE_THREADS
#include "Common/Thread.h"
#define lockMutex Thread::Mutex::Lock _lock(HostClass::_registry_mutex)
#define declareMutex static pthread_mutex_t _registry_mutex
#define defineMutex(Class) pthread_mutex_t Class::_registry_mutex = PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP
#else
#define lockMutex
#define declareMutex
#define defineMutex(Class) 
#endif
//## end module%3C5A7367022E.includes

//## begin module%3C5A7367022E.declarations preserve=no
//## end module%3C5A7367022E.declarations

//## begin module%3C5A7367022E.additionalDeclarations preserve=yes
//## end module%3C5A7367022E.additionalDeclarations


//## begin UniRegistry%3C5A6FD40213.preface preserve=yes
// macro: inserts a registry into a class declaration
#define DeclareRegistry(Class,Key,Value) public: typedef UniRegistry<Key,Value,Class> Registry; typedef Registrar<Key,Value,Class> Register; private: static Registry registry; static Registry::Map *_registry_map; friend class Registry; friend class Register; declareMutex;

// macro: inserts registry definitions into .cc file
#define DefineRegistry(Class,defval) Class::Registry Class::registry(defval); Class::Registry::Map * Class::_registry_map = 0; defineMutex(Class);

// macro: inserts a registry into a class declaration
#define DeclareBiRegistry(Class,Key,Value) public: typedef BiRegistry<Key,Value,Class> Registry; typedef Registrar<Key,Value,Class> Register; private: static Registry registry; static Registry::Map *_registry_map; static Registry::RevMap *_registry_rmap; friend class Registry; friend class UniRegistry<Key,Value,Class>; friend class Register; declareMutex;
// macro: inserts registry definitions into .cc file
#define DefineBiRegistry(Class,defkey,defval) Class::Registry Class::registry(defkey,defval); Class::Registry::Map * Class::_registry_map = 0; Class::Registry::RevMap * Class::_registry_rmap = 0; defineMutex(Class);

//## end UniRegistry%3C5A6FD40213.preface

//## Class: UniRegistry%3C5A6FD40213; protected; Parameterized Class
//	Registry is a template class for maintaining auto-generated
//	registries (maps). This template should not be invoked directly, but
//	rather through the two macros provided below. To add a registry to
//	your class, you should:
//	1.  Invoke the macro DeclareRegistry(YourClass,KeyType,ValueType)
//	inside your class declaration. This adds the necessary data members,
//	and declares the Registry type inside your class.
//
//	2. Invoke the macro DefineRegistry(YourClass,defaultValue) somewhere
//	in your .cc file.
//
//	You can now use the YourClass::Registry::add() and ::find() methods
//	to manipulate the registry.  Entries may also be added simply by
//	constructing objects of type YourClass::Registry. In this way, you
//	can have the registry populated on strartup via simple static object
//	declarations. See AtomicID for an example.
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



template <class Key, class Val, class HostClass>
class UniRegistry 
{
  //## begin UniRegistry%3C5A6FD40213.initialDeclarations preserve=yes
  //## end UniRegistry%3C5A6FD40213.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: UniRegistry%3C5E983901C3
      UniRegistry (const Val& defval);

    //## Destructor (generated)
      virtual ~UniRegistry();


    //## Other Operations (specified)
      //## Operation: add%3C5A72C7006A
      //	Adds entry to the registry.
      virtual void add (const Key& key, const Val &val);

      //## Operation: find%3C5A7307013F
      //	Looks up entry, returns default value if not found.
      const Val & find (const Key& key);

    // Additional Public Declarations
      //## begin UniRegistry%3C5A6FD40213.public preserve=yes
      typedef Key KeyType;
      typedef Val Value;
      typedef map<Key,Val> Map;
      //## end UniRegistry%3C5A6FD40213.public
  protected:
    // Additional Protected Declarations
      //## begin UniRegistry%3C5A6FD40213.protected preserve=yes
      //## end UniRegistry%3C5A6FD40213.protected

  private:
    //## Constructors (generated)
      UniRegistry(const UniRegistry< Key,Val,HostClass > &right);

    //## Assignment Operation (generated)
      UniRegistry< Key,Val,HostClass > & operator=(const UniRegistry< Key,Val,HostClass > &right);

    // Additional Private Declarations
      //## begin UniRegistry%3C5A6FD40213.private preserve=yes
      //## end UniRegistry%3C5A6FD40213.private

  private: //## implementation
    // Data Members for Class Attributes

      //## Attribute: default_value%3C5EA19F005A
      //## begin UniRegistry::default_value%3C5EA19F005A.attr preserve=no  private: Val {U} 
      Val default_value;
      //## end UniRegistry::default_value%3C5EA19F005A.attr

    // Additional Implementation Declarations
      //## begin UniRegistry%3C5A6FD40213.implementation preserve=yes
      //## end UniRegistry%3C5A6FD40213.implementation

};

//## begin UniRegistry%3C5A6FD40213.postscript preserve=yes
//## end UniRegistry%3C5A6FD40213.postscript

//## begin BiRegistry%3C5E8CAC035D.preface preserve=yes
//## end BiRegistry%3C5E8CAC035D.preface

//## Class: BiRegistry%3C5E8CAC035D; Parameterized Class
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



template <class Key, class Val, class HostClass>
class BiRegistry : public UniRegistry<Key, Val, HostClass>  //## Inherits: <unnamed>%3C5E8E46012C
{
  //## begin BiRegistry%3C5E8CAC035D.initialDeclarations preserve=yes
  //## end BiRegistry%3C5E8CAC035D.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: BiRegistry%3C5E985C02A0
      BiRegistry (const Key& defkey, const Val& defval);

    //## Destructor (generated)
      virtual ~BiRegistry();


    //## Other Operations (specified)
      //## Operation: add%3C5E8D9402F3
      void add (const Key& key, const Val &val);

      //## Operation: rfind%3C5E8E2D01C6
      const Key & rfind (const Val& val);

      //## Operation: rfind_more%3C5E8DA00097
      const Key & rfind_more ();

    // Additional Public Declarations
      //## begin BiRegistry%3C5E8CAC035D.public preserve=yes
      typedef map<Val,Key> RevMap;
      //## end BiRegistry%3C5E8CAC035D.public
  protected:
    // Additional Protected Declarations
      //## begin BiRegistry%3C5E8CAC035D.protected preserve=yes
      //## end BiRegistry%3C5E8CAC035D.protected

  private:
    //## Constructors (generated)
      BiRegistry(const BiRegistry< Key,Val,HostClass > &right);

    //## Assignment Operation (generated)
      BiRegistry< Key,Val,HostClass > & operator=(const BiRegistry< Key,Val,HostClass > &right);

    // Additional Private Declarations
      //## begin BiRegistry%3C5E8CAC035D.private preserve=yes
      typename RevMap::const_iterator riter;
      //## end BiRegistry%3C5E8CAC035D.private
  private: //## implementation
    // Data Members for Class Attributes

      //## Attribute: default_key%3C5EA181038C
      //## begin BiRegistry::default_key%3C5EA181038C.attr preserve=no  private: Key {U} 
      Key default_key;
      //## end BiRegistry::default_key%3C5EA181038C.attr

    // Additional Implementation Declarations
      //## begin BiRegistry%3C5E8CAC035D.implementation preserve=yes
      //## end BiRegistry%3C5E8CAC035D.implementation

};

//## begin BiRegistry%3C5E8CAC035D.postscript preserve=yes
//## end BiRegistry%3C5E8CAC035D.postscript

//## begin Registrar%3C5E8E9D011D.preface preserve=yes
//## end Registrar%3C5E8E9D011D.preface

//## Class: Registrar%3C5E8E9D011D; Parameterized Class
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C5FA31301BE;UniRegistry { -> }

template <class Key, class Val, class HostClass>
class Registrar 
{
  //## begin Registrar%3C5E8E9D011D.initialDeclarations preserve=yes
  //## end Registrar%3C5E8E9D011D.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: Registrar%3C5E8EC40246
      Registrar (const Key &key, const Val &val);

    // Additional Public Declarations
      //## begin Registrar%3C5E8E9D011D.public preserve=yes
      //## end Registrar%3C5E8E9D011D.public

  protected:
    // Additional Protected Declarations
      //## begin Registrar%3C5E8E9D011D.protected preserve=yes
      //## end Registrar%3C5E8E9D011D.protected

  private:
    //## Constructors (generated)
      Registrar();

      Registrar(const Registrar< Key,Val,HostClass > &right);

    //## Assignment Operation (generated)
      Registrar< Key,Val,HostClass > & operator=(const Registrar< Key,Val,HostClass > &right);

    // Additional Private Declarations
      //## begin Registrar%3C5E8E9D011D.private preserve=yes
      //## end Registrar%3C5E8E9D011D.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin Registrar%3C5E8E9D011D.implementation preserve=yes
      //## end Registrar%3C5E8E9D011D.implementation

};

//## begin Registrar%3C5E8E9D011D.postscript preserve=yes
//## end Registrar%3C5E8E9D011D.postscript

// Parameterized Class UniRegistry 

// Parameterized Class BiRegistry 

// Parameterized Class Registrar 

// Parameterized Class UniRegistry 

template <class Key, class Val, class HostClass>
UniRegistry<Key,Val,HostClass>::UniRegistry (const Val& defval)
  //## begin UniRegistry::UniRegistry%3C5E983901C3.hasinit preserve=no
  //## end UniRegistry::UniRegistry%3C5E983901C3.hasinit
  //## begin UniRegistry::UniRegistry%3C5E983901C3.initialization preserve=yes
  : default_value(defval)
  //## end UniRegistry::UniRegistry%3C5E983901C3.initialization
{
  //## begin UniRegistry::UniRegistry%3C5E983901C3.body preserve=yes
  lockMutex;
  #define MapPtr HostClass::_registry_map
  if( !MapPtr )
    MapPtr = new Map;
  //## end UniRegistry::UniRegistry%3C5E983901C3.body
}


template <class Key, class Val, class HostClass>
UniRegistry<Key,Val,HostClass>::~UniRegistry()
{
  //## begin UniRegistry::~UniRegistry%3C5A6FD40213_dest.body preserve=yes
  //## end UniRegistry::~UniRegistry%3C5A6FD40213_dest.body
}



//## Other Operations (implementation)
template <class Key, class Val, class HostClass>
void UniRegistry<Key,Val,HostClass>::add (const Key& key, const Val &val)
{
  //## begin UniRegistry::add%3C5A72C7006A.body preserve=yes
  lockMutex;
  if( !MapPtr )
    MapPtr = new Map;

  typename Map::const_iterator iter = MapPtr->find(key);
  
  if( iter != MapPtr->end() && iter->second != val )
  {
    cerr<<"Error: conflicting registry definition for key "<<key<<endl;
    Throw("Error: duplicate registry definition");
  }
  MapPtr->insert(make_pair(key,val));
  
  //## end UniRegistry::add%3C5A72C7006A.body
}

template <class Key, class Val, class HostClass>
const Val & UniRegistry<Key,Val,HostClass>::find (const Key& key)
{
  //## begin UniRegistry::find%3C5A7307013F.body preserve=yes
  lockMutex;
  if( !MapPtr )
    return default_value;
  
  typename Map::const_iterator iter = MapPtr->find(key);
  
  return iter == MapPtr->end() ? default_value : iter->second;
  //## end UniRegistry::find%3C5A7307013F.body
}

// Additional Declarations
  //## begin UniRegistry%3C5A6FD40213.declarations preserve=yes
  //## end UniRegistry%3C5A6FD40213.declarations

// Parameterized Class BiRegistry 

template <class Key, class Val, class HostClass>
BiRegistry<Key,Val,HostClass>::BiRegistry (const Key& defkey, const Val& defval)
  //## begin BiRegistry::BiRegistry%3C5E985C02A0.hasinit preserve=no
  //## end BiRegistry::BiRegistry%3C5E985C02A0.hasinit
  //## begin BiRegistry::BiRegistry%3C5E985C02A0.initialization preserve=yes
  : UniRegistry<Key,Val,HostClass>(defval),default_key(defkey)
  //## end BiRegistry::BiRegistry%3C5E985C02A0.initialization
{
  //## begin BiRegistry::BiRegistry%3C5E985C02A0.body preserve=yes
  #define RevMapPtr HostClass::_registry_rmap
  lockMutex;
  if( !RevMapPtr )
    RevMapPtr = new RevMap;
  riter = RevMapPtr->end();
  //## end BiRegistry::BiRegistry%3C5E985C02A0.body
}


template <class Key, class Val, class HostClass>
BiRegistry<Key,Val,HostClass>::~BiRegistry()
{
  //## begin BiRegistry::~BiRegistry%3C5E8CAC035D_dest.body preserve=yes
  //## end BiRegistry::~BiRegistry%3C5E8CAC035D_dest.body
}



//## Other Operations (implementation)
template <class Key, class Val, class HostClass>
void BiRegistry<Key,Val,HostClass>::add (const Key& key, const Val &val)
{
  //## begin BiRegistry::add%3C5E8D9402F3.body preserve=yes
  lockMutex;
  UniRegistry<Key,Val,HostClass>::add(key,val);
  if( !RevMapPtr )
    RevMapPtr = new RevMap;
  RevMapPtr->insert(make_pair(val,key));
  //## end BiRegistry::add%3C5E8D9402F3.body
}

template <class Key, class Val, class HostClass>
const Key & BiRegistry<Key,Val,HostClass>::rfind (const Val& val)
{
  //## begin BiRegistry::rfind%3C5E8E2D01C6.body preserve=yes
  lockMutex;
  if( !RevMapPtr )
    return default_key;
  
  riter = RevMapPtr->find(val);
  
  return riter == RevMapPtr->end() ? default_key : riter->second;
  //## end BiRegistry::rfind%3C5E8E2D01C6.body
}

template <class Key, class Val, class HostClass>
const Key & BiRegistry<Key,Val,HostClass>::rfind_more ()
{
  //## begin BiRegistry::rfind_more%3C5E8DA00097.body preserve=yes
#ifdef USE_THREADS
  Throw("rfind_more not supported in MT environment");
#endif
  lockMutex;
  if( !RevMapPtr )
    return default_key;
  if( riter == RevMapPtr->end() || ++riter == RevMapPtr->end() )
    return default_key;
  return riter->second;
  //## end BiRegistry::rfind_more%3C5E8DA00097.body
}

// Additional Declarations
  //## begin BiRegistry%3C5E8CAC035D.declarations preserve=yes
  //## end BiRegistry%3C5E8CAC035D.declarations

// Parameterized Class Registrar 

template <class Key, class Val, class HostClass>
Registrar<Key,Val,HostClass>::Registrar (const Key &key, const Val &val)
  //## begin Registrar::Registrar%3C5E8EC40246.hasinit preserve=no
  //## end Registrar::Registrar%3C5E8EC40246.hasinit
  //## begin Registrar::Registrar%3C5E8EC40246.initialization preserve=yes
  //## end Registrar::Registrar%3C5E8EC40246.initialization
{
  //## begin Registrar::Registrar%3C5E8EC40246.body preserve=yes
  HostClass::registry.add(key,val);
  //## end Registrar::Registrar%3C5E8EC40246.body
}


// Additional Declarations
  //## begin Registrar%3C5E8E9D011D.declarations preserve=yes
  //## end Registrar%3C5E8E9D011D.declarations

//## begin module%3C5A7367022E.epilog preserve=yes
#undef MapPtr
#undef RevMapPtr
//## end module%3C5A7367022E.epilog


#endif

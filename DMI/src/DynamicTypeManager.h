//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC8202B5.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC8202B5.cm

//## begin module%3C10CC8202B5.cp preserve=no
//## end module%3C10CC8202B5.cp

//## Module: DynamicTypeManager%3C10CC8202B5; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DynamicTypeManager.h

#ifndef DynamicTypeManager_h
#define DynamicTypeManager_h 1

//## begin module%3C10CC8202B5.additionalIncludes preserve=no
#include  "DMI/Common.h"
#include <map>
//## end module%3C10CC8202B5.additionalIncludes

//## begin module%3C10CC8202B5.includes preserve=yes
//## end module%3C10CC8202B5.includes

// Registry
#include "DMI/Registry.h"
// BlockSet
#include "DMI/BlockSet.h"
// BlockableObject
#include "DMI/BlockableObject.h"
//## begin module%3C10CC8202B5.declarations preserve=no
//## end module%3C10CC8202B5.declarations

//## begin module%3C10CC8202B5.additionalDeclarations preserve=yes
//## end module%3C10CC8202B5.additionalDeclarations


//## begin DynamicTypeManager%3BE96C040003.preface preserve=yes
//## end DynamicTypeManager%3BE96C040003.preface

//## Class: DynamicTypeManager%3BE96C040003; Class Utility
//	This utility class contains static functions and members for
//	run-time maintenance of maps of "virtual constructors". Virtual
//	constructors are used to convert data blocks back into Blockable
//	Objects.
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: 1..1



//## Uses: <unnamed>%3BE96CE70063;BlockableObject { -> }
//## Uses: <unnamed>%3BF905650030;BlockSet { -> }
//## Uses: <unnamed>%3C5A78A401D0;UniRegistry { -> }

class DynamicTypeManager 
{
  //## begin DynamicTypeManager%3BE96C040003.initialDeclarations preserve=yes
  //## end DynamicTypeManager%3BE96C040003.initialDeclarations

  public:
    //## begin DynamicTypeManager::PtrConstructor%3BF559FF0375.preface preserve=yes
    //## end DynamicTypeManager::PtrConstructor%3BF559FF0375.preface

    //## Class: PtrConstructor%3BF559FF0375
    //	This defines a pointer to a "constructor" function for constructing
    //	a particular type of object
    //## Category: PSCF::DMI%3BEAB1F2006B; Global
    //## Subsystem: DMI%3C10CC810155
    //## Persistence: Transient
    //## Cardinality/Multiplicity: n



    typedef BlockableObject * (*PtrConstructor)(int n=0);

    //## begin DynamicTypeManager::PtrConstructor%3BF559FF0375.postscript preserve=yes
    //## end DynamicTypeManager::PtrConstructor%3BF559FF0375.postscript


    //## Other Operations (specified)
      //## Operation: construct%3BE96C5F03A7
      //	Reconstructs an object from a data block, by calling the
      //	"constructor function" for that type to create an empty object, and
      //	then filling it via BlockableObject::fromBlock().
      static BlockableObject * construct (TypeId tid, BlockSet& bset, int n = 0);

      //## Operation: construct%3BE96C7402D5
      //	Constructs a default object of the given type (simply calls the
      //	"constructor" function from the constructor map).
      static BlockableObject * construct (TypeId tid, int n = 0);

      //## Operation: isRegistered%3BF905EE020E
      //	Checks if a type is registered
      static bool isRegistered (TypeId tid);

  public:
    // Additional Public Declarations
      //## begin DynamicTypeManager%3BE96C040003.public preserve=yes
      //## end DynamicTypeManager%3BE96C040003.public

  protected:
    // Additional Protected Declarations
      //## begin DynamicTypeManager%3BE96C040003.protected preserve=yes
      //## end DynamicTypeManager%3BE96C040003.protected

  private:
    // Additional Private Declarations
      //## begin DynamicTypeManager%3BE96C040003.private preserve=yes
      DeclareRegistry(DynamicTypeManager,int,PtrConstructor);
      //## end DynamicTypeManager%3BE96C040003.private
  private: //## implementation
    // Additional Implementation Declarations
      //## begin DynamicTypeManager%3BE96C040003.implementation preserve=yes
      //## end DynamicTypeManager%3BE96C040003.implementation

};

//## begin DynamicTypeManager%3BE96C040003.postscript preserve=yes
//## end DynamicTypeManager%3BE96C040003.postscript

// Class Utility DynamicTypeManager 

//## begin module%3C10CC8202B5.epilog preserve=yes
//## end module%3C10CC8202B5.epilog


#endif

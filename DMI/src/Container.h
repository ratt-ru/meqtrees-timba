//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC830067.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC830067.cm

//## begin module%3C10CC830067.cp preserve=no
//## end module%3C10CC830067.cp

//## Module: NestableContainer%3C10CC830067; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\NestableContainer.h

#ifndef NestableContainer_h
#define NestableContainer_h 1

//## begin module%3C10CC830067.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC830067.additionalIncludes

//## begin module%3C10CC830067.includes preserve=yes
//## end module%3C10CC830067.includes

// HIIDSet
#include "HIIDSet.h"
// BlockableObject
#include "BlockableObject.h"
//## begin module%3C10CC830067.declarations preserve=no
//## end module%3C10CC830067.declarations

//## begin module%3C10CC830067.additionalDeclarations preserve=yes
//## end module%3C10CC830067.additionalDeclarations


//## begin NestableContainer%3BE97CE100AF.preface preserve=yes
//## end NestableContainer%3BE97CE100AF.preface

//## Class: NestableContainer%3BE97CE100AF; Abstract
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BFBAF8303C0;HIIDSet { -> }

class NestableContainer : public BlockableObject  //## Inherits: <unnamed>%3BFCD87C0106
{
  //## begin NestableContainer%3BE97CE100AF.initialDeclarations preserve=yes
  //## end NestableContainer%3BE97CE100AF.initialDeclarations

  public:

    //## Other Operations (specified)
      //## Operation: hasFragment%3BE9828D0266
      virtual Bool hasFragment (HIID frag) = 0;

      //## Operation: selectFragment%3BE982760231
      virtual Bool selectFragment (const HIIDSet &frag) = 0;

      //## Operation: clearSelection%3BFBDC0D025A
      virtual void clearSelection () = 0;

      //## Operation: selectionToBlock%3BFBDC1D028F
      virtual int selectionToBlock (BlockSet& set) = 0;

      //## Operation: isNestable%3BFCD8180044
      Bool isNestable ();

    // Additional Public Declarations
      //## begin NestableContainer%3BE97CE100AF.public preserve=yes
      //## end NestableContainer%3BE97CE100AF.public

  protected:
    // Additional Protected Declarations
      //## begin NestableContainer%3BE97CE100AF.protected preserve=yes
      //## end NestableContainer%3BE97CE100AF.protected

  private:
    // Additional Private Declarations
      //## begin NestableContainer%3BE97CE100AF.private preserve=yes
      //## end NestableContainer%3BE97CE100AF.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin NestableContainer%3BE97CE100AF.implementation preserve=yes
      //## end NestableContainer%3BE97CE100AF.implementation

};

//## begin NestableContainer%3BE97CE100AF.postscript preserve=yes
//## end NestableContainer%3BE97CE100AF.postscript

// Class NestableContainer 


//## Other Operations (inline)
inline Bool NestableContainer::isNestable ()
{
  //## begin NestableContainer::isNestable%3BFCD8180044.body preserve=yes
  //## end NestableContainer::isNestable%3BFCD8180044.body

  return True;

}

// Class NestableContainer 

// Additional Declarations
  //## begin NestableContainer%3BE97CE100AF.declarations preserve=yes
  //## end NestableContainer%3BE97CE100AF.declarations

//## begin module%3C10CC830067.epilog preserve=yes
//## end module%3C10CC830067.epilog


#endif

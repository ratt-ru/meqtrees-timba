//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC81019B.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC81019B.cm

//## begin module%3C10CC81019B.cp preserve=no
//## end module%3C10CC81019B.cp

//## Module: BlockableObject%3C10CC81019B; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: f:\lofar8\oms\LOFAR\cep\cpa\pscf\src\BlockableObject.h

#ifndef BlockableObject_h
#define BlockableObject_h 1

//## begin module%3C10CC81019B.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC81019B.additionalIncludes

//## begin module%3C10CC81019B.includes preserve=yes
//## end module%3C10CC81019B.includes

// CountedRef
#include "CountedRef.h"
// CountedRefTarget
#include "CountedRefTarget.h"
// TypeId
#include "TypeId.h"
// BlockSet
#include "BlockSet.h"
//## begin module%3C10CC81019B.declarations preserve=no
//## end module%3C10CC81019B.declarations

//## begin module%3C10CC81019B.additionalDeclarations preserve=yes
#pragma typegroup Global
#pragma types -ObjRef
//## end module%3C10CC81019B.additionalDeclarations


//## begin BlockableObject%3BB1F71F03C9.preface preserve=yes
//## end BlockableObject%3BB1F71F03C9.preface

//## Class: BlockableObject%3BB1F71F03C9; Abstract
//	Base class for most data objects in the system. Defines interfaces
//	for serializing an object (i.e., converting to raw data), and
//	optional interfaces for nesting containers, and for data persistency.
//
//	This class also contains static functions for run-time maintenance
//	of maps of "virtual constructors".
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BEBD67F03AB;BlockSet { -> }
//## Uses: <unnamed>%3BFE633D01AC;CountedRef { -> }
//## Uses: <unnamed>%3C14C5360107;TypeId { -> }

class BlockableObject : public CountedRefTarget  //## Inherits: <unnamed>%3C0CEB760044
{
  //## begin BlockableObject%3BB1F71F03C9.initialDeclarations preserve=yes
  //## end BlockableObject%3BB1F71F03C9.initialDeclarations

  public:
    //## Destructor (generated)
      virtual ~BlockableObject();


    //## Other Operations (specified)
      //## Operation: fromBlock%3BB1F88402F0
      //	Creates object from a set of block references. Appropriate number of
      //	references are removed from the head of the BlockSet. Returns # of
      //	refs removed.
      virtual int fromBlock (BlockSet& set) = 0;

      //## Operation: toBlock%3BB1F89B0054
      //	Stores an object into a set of blocks. Appropriate number of refs
      //	added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const = 0;

      //## Operation: objectType%3BFA274900ED
      //	Returns the class TypeId
      virtual TypeId objectType () const = 0;

      //## Operation: isNestable%3BFA7DBF00D7
      //	Returns True if the class realizes the NestableContainerInterface.
      //	Default implementation: False
      virtual bool isNestable () const;

      //## Operation: isPersistent%3BFA7DC8017B
      //	Returns True if the class realizes the Persistency Interface.
      //	Default implementation: False.
      virtual bool isPersistent ();

      //## Operation: clone%3BFE5FE103C5
      //	Clones the object. Default implementation creates a clone via a to
      //	Block() - BlockSet::privatizeAll() - fromBlock() sequence, so if
      //	your to/fromBlock is efficient enough, you don't need to provide
      //	your own clone().
      CountedRefTarget * clone (int flags = 0);

    // Additional Public Declarations
      //## begin BlockableObject%3BB1F71F03C9.public preserve=yes
      DefineRefTypes(BlockableObject,Ref);
      //## end BlockableObject%3BB1F71F03C9.public
  protected:
    // Additional Protected Declarations
      //## begin BlockableObject%3BB1F71F03C9.protected preserve=yes
      //## end BlockableObject%3BB1F71F03C9.protected

  private:
    // Additional Private Declarations
      //## begin BlockableObject%3BB1F71F03C9.private preserve=yes
      //## end BlockableObject%3BB1F71F03C9.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin BlockableObject%3BB1F71F03C9.implementation preserve=yes
      //## end BlockableObject%3BB1F71F03C9.implementation

};

//## begin BlockableObject%3BB1F71F03C9.postscript preserve=yes
DefineRefTypes(BlockableObject,ObjRef);

#define newAnon(type) ObjRef(new type,DMI::ANON|DMI::WRITE)
//## end BlockableObject%3BB1F71F03C9.postscript

// Class BlockableObject 

inline BlockableObject::~BlockableObject()
{
  //## begin BlockableObject::~BlockableObject%3BB1F71F03C9_dest.body preserve=yes
  //## end BlockableObject::~BlockableObject%3BB1F71F03C9_dest.body
}



//## Other Operations (inline)
inline bool BlockableObject::isNestable () const
{
  //## begin BlockableObject::isNestable%3BFA7DBF00D7.body preserve=yes
  //## end BlockableObject::isNestable%3BFA7DBF00D7.body

  return False;
}

inline bool BlockableObject::isPersistent ()
{
  //## begin BlockableObject::isPersistent%3BFA7DC8017B.body preserve=yes
  //## end BlockableObject::isPersistent%3BFA7DC8017B.body

  return False;

}

//## begin module%3C10CC81019B.epilog preserve=yes
//## end module%3C10CC81019B.epilog


#endif

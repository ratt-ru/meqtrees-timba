//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC81019D.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC81019D.cm

//## begin module%3C10CC81019D.cp preserve=no
//## end module%3C10CC81019D.cp

//## Module: BlockableObject%3C10CC81019D; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\BlockableObject.cc

//## begin module%3C10CC81019D.additionalIncludes preserve=no
//## end module%3C10CC81019D.additionalIncludes

//## begin module%3C10CC81019D.includes preserve=yes
//## end module%3C10CC81019D.includes

// DynamicTypeManager
#include "DMI/DynamicTypeManager.h"
// BlockableObject
#include "DMI/BlockableObject.h"
//## begin module%3C10CC81019D.declarations preserve=no
//## end module%3C10CC81019D.declarations

//## begin module%3C10CC81019D.additionalDeclarations preserve=yes
//## end module%3C10CC81019D.additionalDeclarations


// Class BlockableObject 


//## Other Operations (implementation)
CountedRefTarget * BlockableObject::clone (int flags, int depth) const
{
  //## begin BlockableObject::clone%3BFE5FE103C5.body preserve=yes
  BlockSet bset;
  toBlock(bset);
  if( flags&DMI::DEEP || depth>0 )
    bset.privatizeAll(flags);
  return DynamicTypeManager::construct(objectType(),bset);
  //## end BlockableObject::clone%3BFE5FE103C5.body
}

void BlockableObject::privatize (int flags, int depth)
{
  //## begin BlockableObject::privatize%3CAB088100C3.body preserve=yes
  BlockSet bset;
  toBlock(bset);
  if( flags&DMI::DEEP || depth>0 )
    bset.privatizeAll(flags);
  fromBlock(bset);
  //## end BlockableObject::privatize%3CAB088100C3.body
}

// Additional Declarations
  //## begin BlockableObject%3BB1F71F03C9.declarations preserve=yes
  //## end BlockableObject%3BB1F71F03C9.declarations

//## begin module%3C10CC81019D.epilog preserve=yes
//## end module%3C10CC81019D.epilog

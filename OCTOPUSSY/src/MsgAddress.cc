//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7B7F2F0380.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7B7F2F0380.cm

//## begin module%3C7B7F2F0380.cp preserve=no
//## end module%3C7B7F2F0380.cp

//## Module: MsgAddress%3C7B7F2F0380; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\MsgAddress.cc

//## begin module%3C7B7F2F0380.additionalIncludes preserve=no
//## end module%3C7B7F2F0380.additionalIncludes

//## begin module%3C7B7F2F0380.includes preserve=yes
//## end module%3C7B7F2F0380.includes

// MsgAddress
#include "OCTOPUSSY/MsgAddress.h"
//## begin module%3C7B7F2F0380.declarations preserve=no
//## end module%3C7B7F2F0380.declarations

//## begin module%3C7B7F2F0380.additionalDeclarations preserve=yes
//## end module%3C7B7F2F0380.additionalDeclarations


// Class MsgAddress 

// Additional Declarations
  //## begin MsgAddress%3C7B6F790197.declarations preserve=yes
  //## end MsgAddress%3C7B6F790197.declarations

// Class WPID 

// Additional Declarations
  //## begin WPID%3C8F9A340206.declarations preserve=yes
  //## end WPID%3C8F9A340206.declarations

//## begin module%3C7B7F2F0380.epilog preserve=yes
//## end module%3C7B7F2F0380.epilog


// Detached code regions:
#if 0
//## begin MsgAddress::MsgAddress%3C7B6F790197_copy.initialization preserve=yes
    : HIID(right)
//## end MsgAddress::MsgAddress%3C7B6F790197_copy.initialization

//## begin MsgAddress::operator=%3C7B6F790197_assign.body preserve=yes
  *static_cast<HIID*>(this) = static_cast<const HIID&>(right);
  return *this;
//## end MsgAddress::operator=%3C7B6F790197_assign.body

//## begin MsgAddress::MsgAddress%3C7B6FAE00FD.initialization preserve=yes
    : HIID(3)
//## end MsgAddress::MsgAddress%3C7B6FAE00FD.initialization

//## begin MsgAddress::MsgAddress%3C7B6FAE00FD.body preserve=yes
  (*this)[0] = host;
  (*this)[1] = proc;
  (*this)[2] = wp;
//## end MsgAddress::MsgAddress%3C7B6FAE00FD.body

//## begin MsgAddress::wp%3C7B6FED02B7.body preserve=yes
  return (*this)[2];
//## end MsgAddress::wp%3C7B6FED02B7.body

#endif

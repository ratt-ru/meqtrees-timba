//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC82005C.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC82005C.cm

//## begin module%3C10CC82005C.cp preserve=no
//## end module%3C10CC82005C.cp

//## Module: DataRecord%3C10CC82005C; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DataRecord.cc

//## begin module%3C10CC82005C.additionalIncludes preserve=no
//## end module%3C10CC82005C.additionalIncludes

//## begin module%3C10CC82005C.includes preserve=yes
//## end module%3C10CC82005C.includes

// DataRecord
#include "DataRecord.h"
//## begin module%3C10CC82005C.declarations preserve=no
//## end module%3C10CC82005C.declarations

//## begin module%3C10CC82005C.additionalDeclarations preserve=yes
//## end module%3C10CC82005C.additionalDeclarations


// Class DataRecord 

DataRecord::DataRecord()
  //## begin DataRecord::DataRecord%3BB3112B0027_const.hasinit preserve=no
  //## end DataRecord::DataRecord%3BB3112B0027_const.hasinit
  //## begin DataRecord::DataRecord%3BB3112B0027_const.initialization preserve=yes
  //## end DataRecord::DataRecord%3BB3112B0027_const.initialization
{
  //## begin DataRecord::DataRecord%3BB3112B0027_const.body preserve=yes
  //## end DataRecord::DataRecord%3BB3112B0027_const.body
}

DataRecord::DataRecord(const DataRecord &right)
  //## begin DataRecord::DataRecord%3BB3112B0027_copy.hasinit preserve=no
  //## end DataRecord::DataRecord%3BB3112B0027_copy.hasinit
  //## begin DataRecord::DataRecord%3BB3112B0027_copy.initialization preserve=yes
  //## end DataRecord::DataRecord%3BB3112B0027_copy.initialization
{
  //## begin DataRecord::DataRecord%3BB3112B0027_copy.body preserve=yes
  //## end DataRecord::DataRecord%3BB3112B0027_copy.body
}


DataRecord::~DataRecord()
{
  //## begin DataRecord::~DataRecord%3BB3112B0027_dest.body preserve=yes
  //## end DataRecord::~DataRecord%3BB3112B0027_dest.body
}


DataRecord & DataRecord::operator=(const DataRecord &right)
{
  //## begin DataRecord::operator=%3BB3112B0027_assign.body preserve=yes
  //## end DataRecord::operator=%3BB3112B0027_assign.body
}



//## Other Operations (implementation)
DataFieldRef & DataRecord::field (const HIID &id)
{
  //## begin DataRecord::field%3BFBF49D00A1.body preserve=yes
  //## end DataRecord::field%3BFBF49D00A1.body
}

DataFieldRef & DataRecord::operator [] (const HIID &id)
{
  //## begin DataRecord::operator []%3BFBF55C02A4.body preserve=yes
  //## end DataRecord::operator []%3BFBF55C02A4.body
}

Bool DataRecord::add (const HIID &id, DataFieldRef &ref)
{
  //## begin DataRecord::add%3BFBF5B600EB.body preserve=yes
  //## end DataRecord::add%3BFBF5B600EB.body
}

Bool DataRecord::remove (const HIID &id)
{
  //## begin DataRecord::remove%3BB311C903BE.body preserve=yes
  //## end DataRecord::remove%3BB311C903BE.body
}

Bool DataRecord::replace (const HIID &id, DataFieldRef &ref)
{
  //## begin DataRecord::replace%3BFCD4BB036F.body preserve=yes
  //## end DataRecord::replace%3BFCD4BB036F.body
}

Bool DataRecord::enableWrite (const HIID &id)
{
  //## begin DataRecord::enableWrite%3BFCF8C00234.body preserve=yes
  //## end DataRecord::enableWrite%3BFCF8C00234.body
}

// Additional Declarations
  //## begin DataRecord%3BB3112B0027.declarations preserve=yes
  //## end DataRecord%3BB3112B0027.declarations

//## begin module%3C10CC82005C.epilog preserve=yes
//## end module%3C10CC82005C.epilog

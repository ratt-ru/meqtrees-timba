//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820126.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820126.cm

//## begin module%3C10CC820126.cp preserve=no
//## end module%3C10CC820126.cp

//## Module: DataField%3C10CC820126; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DataField.cc

//## begin module%3C10CC820126.additionalIncludes preserve=no
//## end module%3C10CC820126.additionalIncludes

//## begin module%3C10CC820126.includes preserve=yes
//## end module%3C10CC820126.includes

// DataField
#include "DataField.h"
//## begin module%3C10CC820126.declarations preserve=no
//## end module%3C10CC820126.declarations

//## begin module%3C10CC820126.additionalDeclarations preserve=yes
//## end module%3C10CC820126.additionalDeclarations


// Class DataField 

DataField::DataField()
  //## begin DataField::DataField%3BB317D8010B_const.hasinit preserve=no
  //## end DataField::DataField%3BB317D8010B_const.hasinit
  //## begin DataField::DataField%3BB317D8010B_const.initialization preserve=yes
  : mytype(0),selected(False),writable(False)
  //## end DataField::DataField%3BB317D8010B_const.initialization
{
  //## begin DataField::DataField%3BB317D8010B_const.body preserve=yes
  //## end DataField::DataField%3BB317D8010B_const.body
}

DataField::DataField(const DataField &right)
  //## begin DataField::DataField%3BB317D8010B_copy.hasinit preserve=no
  //## end DataField::DataField%3BB317D8010B_copy.hasinit
  //## begin DataField::DataField%3BB317D8010B_copy.initialization preserve=yes
  //## end DataField::DataField%3BB317D8010B_copy.initialization
{
  //## begin DataField::DataField%3BB317D8010B_copy.body preserve=yes
  //## end DataField::DataField%3BB317D8010B_copy.body
}

DataField::DataField (TypeId tid, int num, bool writable)
  //## begin DataField::DataField%3BFA54540099.hasinit preserve=no
  //## end DataField::DataField%3BFA54540099.hasinit
  //## begin DataField::DataField%3BFA54540099.initialization preserve=yes
  //## end DataField::DataField%3BFA54540099.initialization
{
  //## begin DataField::DataField%3BFA54540099.body preserve=yes
  //## end DataField::DataField%3BFA54540099.body
}


DataField::~DataField()
{
  //## begin DataField::~DataField%3BB317D8010B_dest.body preserve=yes
  //## end DataField::~DataField%3BB317D8010B_dest.body
}


DataField & DataField::operator=(const DataField &right)
{
  //## begin DataField::operator=%3BB317D8010B_assign.body preserve=yes
  //## end DataField::operator=%3BB317D8010B_assign.body
}



//## Other Operations (implementation)
int DataField::len ()
{
  //## begin DataField::len%3BFCF8E101C3.body preserve=yes
  //## end DataField::len%3BFCF8E101C3.body
}

const void* DataField::get (int n, TypeId check)
{
  //## begin DataField::get%3BFCF8E50287.body preserve=yes
  //## end DataField::get%3BFCF8E50287.body
}

const void* DataField::operator [] (int n)
{
  //## begin DataField::operator []%3BFCFA1503B1.body preserve=yes
  //## end DataField::operator []%3BFCFA1503B1.body
}

void* DataField::getWr (int n, TypeId check)
{
  //## begin DataField::getWr%3BFCFA2902FB.body preserve=yes
  //## end DataField::getWr%3BFCFA2902FB.body
}

ObjRef DataField::objref (int n)
{
  //## begin DataField::objref%3C0E4619019A.body preserve=yes
  //## end DataField::objref%3C0E4619019A.body
}

// Additional Declarations
  //## begin DataField%3BB317D8010B.declarations preserve=yes
  //## end DataField%3BB317D8010B.declarations

//## begin module%3C10CC820126.epilog preserve=yes
//## end module%3C10CC820126.epilog

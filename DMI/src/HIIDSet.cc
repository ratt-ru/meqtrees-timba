//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC8203CF.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC8203CF.cm

//## begin module%3C10CC8203CF.cp preserve=no
//## end module%3C10CC8203CF.cp

//## Module: HIIDSet%3C10CC8203CF; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\CEP\CPA\PSCF\src\HIIDSet.cc

//## begin module%3C10CC8203CF.additionalIncludes preserve=no
//## end module%3C10CC8203CF.additionalIncludes

//## begin module%3C10CC8203CF.includes preserve=yes
//## end module%3C10CC8203CF.includes

// HIIDSet
#include "HIIDSet.h"
//## begin module%3C10CC8203CF.declarations preserve=no
//## end module%3C10CC8203CF.declarations

//## begin module%3C10CC8203CF.additionalDeclarations preserve=yes
//## end module%3C10CC8203CF.additionalDeclarations


// Class HIIDSet 

HIIDSet::HIIDSet()
  //## begin HIIDSet::HIIDSet%3BFBAC350085_const.hasinit preserve=no
  //## end HIIDSet::HIIDSet%3BFBAC350085_const.hasinit
  //## begin HIIDSet::HIIDSet%3BFBAC350085_const.initialization preserve=yes
  //## end HIIDSet::HIIDSet%3BFBAC350085_const.initialization
{
  //## begin HIIDSet::HIIDSet%3BFBAC350085_const.body preserve=yes
  //## end HIIDSet::HIIDSet%3BFBAC350085_const.body
}

HIIDSet::HIIDSet(const HIIDSet &right)
  //## begin HIIDSet::HIIDSet%3BFBAC350085_copy.hasinit preserve=no
  //## end HIIDSet::HIIDSet%3BFBAC350085_copy.hasinit
  //## begin HIIDSet::HIIDSet%3BFBAC350085_copy.initialization preserve=yes
    : contents( right.contents )
  //## end HIIDSet::HIIDSet%3BFBAC350085_copy.initialization
{
  //## begin HIIDSet::HIIDSet%3BFBAC350085_copy.body preserve=yes
  //## end HIIDSet::HIIDSet%3BFBAC350085_copy.body
}

HIIDSet::HIIDSet (const HIID& id)
  //## begin HIIDSet::HIIDSet%3BFBAE2403DA.hasinit preserve=no
  //## end HIIDSet::HIIDSet%3BFBAE2403DA.hasinit
  //## begin HIIDSet::HIIDSet%3BFBAE2403DA.initialization preserve=yes
  //## end HIIDSet::HIIDSet%3BFBAE2403DA.initialization
{
  //## begin HIIDSet::HIIDSet%3BFBAE2403DA.body preserve=yes
  add(id);
  //## end HIIDSet::HIIDSet%3BFBAE2403DA.body
}


HIIDSet::~HIIDSet()
{
  //## begin HIIDSet::~HIIDSet%3BFBAC350085_dest.body preserve=yes
  //## end HIIDSet::~HIIDSet%3BFBAC350085_dest.body
}


HIIDSet & HIIDSet::operator=(const HIIDSet &right)
{
  //## begin HIIDSet::operator=%3BFBAC350085_assign.body preserve=yes
  contents = right.contents;
  return *this;
  //## end HIIDSet::operator=%3BFBAC350085_assign.body
}



//## Other Operations (implementation)
void HIIDSet::clear ()
{
  //## begin HIIDSet::clear%3C7E15F90113.body preserve=yes
  contents.clear();
  //## end HIIDSet::clear%3C7E15F90113.body
}

HIIDSet & HIIDSet::add (const HIID &id)
{
  //## begin HIIDSet::add%3C1DF8510016.body preserve=yes
  contents.insert(id);
  return *this;
  //## end HIIDSet::add%3C1DF8510016.body
}

HIIDSet & HIIDSet::add (const HIIDSet &other)
{
  //## begin HIIDSet::add%3BFBAE330345.body preserve=yes
  for( CSI iter = other.contents.begin(); iter != other.contents.end(); iter++ )
    contents.insert(*iter);
  return *this;
  //## end HIIDSet::add%3BFBAE330345.body
}

HIIDSet & HIIDSet::remove (const HIIDSet &other)
{
  //## begin HIIDSet::remove%3BFBAF14023A.body preserve=yes
  for( CSI iter = other.contents.begin(); iter != other.contents.end(); iter++ )
    remove(*iter);
  return *this;
  //## end HIIDSet::remove%3BFBAF14023A.body
}

HIIDSet & HIIDSet::remove (const HIID &id)
{
  //## begin HIIDSet::remove%3C1DFB650236.body preserve=yes
  contents.erase(id);
  return *this;
  //## end HIIDSet::remove%3C1DFB650236.body
}

bool HIIDSet::contains (const HIID& id) const
{
  //## begin HIIDSet::contains%3BFBAE650315.body preserve=yes
  for( CSI iter = contents.begin(); iter != contents.end(); iter++ )
    if( id.matches(*iter) )
      return True;
  return False;
  //## end HIIDSet::contains%3BFBAE650315.body
}

size_t HIIDSet::pack (void* block) const
{
  //## begin HIIDSet::pack%3C98CFEF00B6.body preserve=yes
  int sz = sizeof(int)*(1 + contents.size());
  int *bl =  static_cast<int*>(block);
  char *data = static_cast<char*>(block) + sz; // skip to beginning of HIID storage
  // first int is size of set
  *(bl++) = contents.size();
  // go thru HIIDs, packing them in
  for( CSI iter = contents.begin(); iter != contents.end(); iter++ )
  {
    int sz1 = iter->pack(data);
    data += *(bl++) = sz1;
    sz += sz1;
  }
  return sz;
  //## end HIIDSet::pack%3C98CFEF00B6.body
}

void HIIDSet::unpack (const void* block, size_t sz)
{
  //## begin HIIDSet::unpack%3C98CFEF0110.body preserve=yes
  const int *bl = static_cast<const int*>(block);
  int n = *(bl++);
  const char *data = static_cast<const char*>(block) += sizeof(int)*(n+1); // skip to beginning of HIID storage
  sz -= sizeof(int)*(n+1);   // remaining size
  for( int i=0; i<n; i++,bl++ )
  {
    size_t sz1 = *bl;  // size of next HIID
    FailWhen(sz<sz1,"corrupt block");
    contents.insert( HIID(data,sz1) );
    data += sz1; 
  }
  FailWhen(sz,"corrupt block");
  //## end HIIDSet::unpack%3C98CFEF0110.body
}

size_t HIIDSet::packSize () const
{
  //## begin HIIDSet::packSize%3C98CFEF016A.body preserve=yes
  int sz = sizeof(int)*(1 + contents.size());
  for( CSI iter = contents.begin(); iter != contents.end(); iter++ )
    sz += iter->packSize();
  return sz;
  //## end HIIDSet::packSize%3C98CFEF016A.body
}

// Additional Declarations
  //## begin HIIDSet%3BFBAC350085.declarations preserve=yes
  //## end HIIDSet%3BFBAC350085.declarations

//## begin module%3C10CC8203CF.epilog preserve=yes
//## end module%3C10CC8203CF.epilog

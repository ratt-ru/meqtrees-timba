//##ModelId=3BFBAE2403DA
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
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\HIIDSet.cc

//## begin module%3C10CC8203CF.additionalIncludes preserve=no
//## end module%3C10CC8203CF.additionalIncludes

//## begin module%3C10CC8203CF.includes preserve=yes
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

#include "DMI/Packer.h"
//## end module%3C10CC8203CF.includes

// HIIDSet
#include "DMI/HIIDSet.h"
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

//##ModelId=3C98D01B036C
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

//##ModelId=3DB9348D0271
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


//##ModelId=3DB9348E00CE
HIIDSet::~HIIDSet()
{
  //## begin HIIDSet::~HIIDSet%3BFBAC350085_dest.body preserve=yes
  //## end HIIDSet::~HIIDSet%3BFBAC350085_dest.body
}


//##ModelId=3DB9348E010A
HIIDSet & HIIDSet::operator=(const HIIDSet &right)
{
  //## begin HIIDSet::operator=%3BFBAC350085_assign.body preserve=yes
  contents = right.contents;
  return *this;
  //## end HIIDSet::operator=%3BFBAC350085_assign.body
}



//##ModelId=3C7E15F90113
//## Other Operations (implementation)
void HIIDSet::clear ()
{
  //## begin HIIDSet::clear%3C7E15F90113.body preserve=yes
  contents.clear();
  //## end HIIDSet::clear%3C7E15F90113.body
}

//##ModelId=3C1DF8510016
HIIDSet & HIIDSet::add (const HIID &id)
{
  //## begin HIIDSet::add%3C1DF8510016.body preserve=yes
  contents.insert(id);
  return *this;
  //## end HIIDSet::add%3C1DF8510016.body
}

//##ModelId=3BFBAE330345
HIIDSet & HIIDSet::add (const HIIDSet &other)
{
  //## begin HIIDSet::add%3BFBAE330345.body preserve=yes
  for( CSI iter = other.contents.begin(); iter != other.contents.end(); iter++ )
    contents.insert(*iter);
  return *this;
  //## end HIIDSet::add%3BFBAE330345.body
}

//##ModelId=3BFBAF14023A
HIIDSet & HIIDSet::remove (const HIIDSet &other)
{
  //## begin HIIDSet::remove%3BFBAF14023A.body preserve=yes
  for( CSI iter = other.contents.begin(); iter != other.contents.end(); iter++ )
    remove(*iter);
  return *this;
  //## end HIIDSet::remove%3BFBAF14023A.body
}

//##ModelId=3C1DFB650236
HIIDSet & HIIDSet::remove (const HIID &id)
{
  //## begin HIIDSet::remove%3C1DFB650236.body preserve=yes
  contents.erase(id);
  return *this;
  //## end HIIDSet::remove%3C1DFB650236.body
}

//##ModelId=3BFBAE650315
bool HIIDSet::contains (const HIID& id) const
{
  //## begin HIIDSet::contains%3BFBAE650315.body preserve=yes
  for( CSI iter = contents.begin(); iter != contents.end(); iter++ )
    if( id.matches(*iter) )
      return True;
  return False;
  //## end HIIDSet::contains%3BFBAE650315.body
}

//##ModelId=3C98CFEF00B6
size_t HIIDSet::pack (void *block, size_t &nleft) const
{
  //## begin HIIDSet::pack%3C98CFEF00B6.body preserve=yes
  return SeqPacker<set<HIID> >::pack(contents,block,nleft);
  //## end HIIDSet::pack%3C98CFEF00B6.body
}

//##ModelId=3C98CFEF0110
void HIIDSet::unpack (const void* block, size_t sz)
{
  //## begin HIIDSet::unpack%3C98CFEF0110.body preserve=yes
  SeqPacker<set<HIID> >::unpack(contents,block,sz);
  //## end HIIDSet::unpack%3C98CFEF0110.body
}

//##ModelId=3C98CFEF016A
size_t HIIDSet::packSize () const
{
  //## begin HIIDSet::packSize%3C98CFEF016A.body preserve=yes
  return SeqPacker<set<HIID> >::packSize(contents);
  //## end HIIDSet::packSize%3C98CFEF016A.body
}

// Additional Declarations
  //## begin HIIDSet%3BFBAC350085.declarations preserve=yes
  //## end HIIDSet%3BFBAC350085.declarations

//## begin module%3C10CC8203CF.epilog preserve=yes
//## end module%3C10CC8203CF.epilog

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

#ifndef DMI_DynamicTypeManager_h
#define DMI_DynamicTypeManager_h 1

#include <DMI/DMI.h>
#include <DMI/Registry.h>
#include <DMI/BlockSet.h>
#include <DMI/BObj.h>
#include <map>

namespace DMI
{
    
//##ModelId=3BE96C040003
//##Documentation
//## This utility class contains static functions and members for
//## run-time maintenance of maps of "virtual constructors". Virtual
//## constructors are used to convert data blocks back into Blockable
//## Objects.

class DynamicTypeManager 
{
  ImportDebugContext(DebugDMI);
  public:
    //##ModelId=3DB9343C01AB
    //##Documentation
    //## This defines a pointer to a "constructor" function for constructing
    //## a particular type of object
    typedef BObj * (*PtrConstructor)(int n);
  
    //## Reconstructs an object from a data block set, by calling the
    //## "constructor function" for that type to create an empty object, and
    //## then filling it via DMI::BObj::fromBlock().
    //## If tid is 0, then the tid will be taken from the block header.
    static ObjRef construct (TypeId tid, BlockSet& bset);
    
    //## Reconstructs N objects from a data block set, by calling the
    //## "constructor function" for that type to create an empty object, and
    //## then filling it via DMI::BObj::fromBlock().
    //## If tid is 0, then the tid will be taken from the block header.
    //## An array of objects is allocated with new [].
    static BObj * construct (TypeId tid, BlockSet& bset, int n);

    //##ModelId=3BE96C7402D5
    //##Documentation
    //## Constructs a default object of the given type (simply calls the
    //## "constructor" function from the constructor map).
    static BObj * construct (TypeId tid, int n = 0);

    //##ModelId=3BF905EE020E
    //##Documentation
    //## Checks if a type is registered
    static bool isRegistered (TypeId tid);

  private:
    // Additional Private Declarations
    //##ModelId=3DB934870196
    DeclareRegistry(DynamicTypeManager,int,PtrConstructor);
};

// Class Utility DynamicTypeManager 

};
#endif

//  BObj.h: abstract prototype for blockable objects
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#ifndef DMI_BObj_h
#define DMI_BObj_h 1

#include <DMI/DMI.h>
#include <DMI/CountedRef.h>
#include <DMI/CountedRefTarget.h>
#include <DMI/TypeId.h>
#include <DMI/BlockSet.h>

#pragma type -DMI::ObjRef

namespace DMI
{

//##ModelId=3BB1F71F03C9
//##Documentation
//## Base class for most data objects in the system. Defines interfaces
//## for serializing an object (i.e., converting to raw data), and
//## optional interfaces for nesting containers, and for data persistency.
//## 
//## This class also contains static functions for run-time maintenance
//## of maps of "virtual constructors".

class BObj : public CountedRefTarget
{
  public:
    //##ModelId=3DB9344C035B
      virtual ~BObj();


      //##ModelId=3BB1F88402F0
      //##Documentation
      //## Creates object from a set of block references. Appropriate number of
      //## references are removed from the head of the BlockSet. Returns # of
      //## refs removed.
      virtual int fromBlock (BlockSet& set) = 0;

      //##ModelId=3BB1F89B0054
      //##Documentation
      //## Stores an object into a set of blocks. Appropriate number of refs
      //## added to tail of BlockSet. Returns # of block refs added.
      virtual int toBlock (BlockSet &set) const = 0;

      //##ModelId=3BFA274900ED
      //##Documentation
      //## Returns the class TypeId
      virtual TypeId objectType () const = 0;

      //##ModelId=3BFA7DBF00D7
      //##Documentation
      //## Returns true if the class realizes the DMI::ContainerInterface.
      //## Default implementation: false
      virtual bool isNestable () const;

      //##ModelId=3BFA7DC8017B
      //##Documentation
      //## Returns true if the class realizes the Persistency Interface.
      //## Default implementation: false.
      virtual bool isPersistent ();

      //##ModelId=3BFE5FE103C5
      //##Documentation
      //## Clones the object. Default implementation creates a clone via a to
      //## Block() - fromBlock() -privatize() sequence, so if your to/fromBlock
      //## is efficient enough, you don't need to provide your own clone().
      virtual CountedRefTarget * clone (int flags = 0, int depth = 0) const;

    // Additional Public Declarations
    //##ModelId=3DB9344D015D
      typedef CountedRef<BObj> Ref;
      
      // Provide a default print for the BO hierarchy
      // Default version simply prints objectType()
    //##ModelId=3E9BD915025A
      virtual void print (std::ostream &str) const;
};

//##ModelId=3DB963E102B7
typedef BObj::Ref ObjRef;

#define newAnon(type) ObjRef(new type,DMI::ANON|DMI::WRITE)

//##ModelId=3DB9344C035B
inline BObj::~BObj()
{
}

//##ModelId=3BFA7DBF00D7
inline bool BObj::isNestable () const
{
  return false;
}

//##ModelId=3BFA7DC8017B
inline bool BObj::isPersistent ()
{
  return false;
}

};
#endif

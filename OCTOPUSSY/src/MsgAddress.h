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

#ifndef OCTOPUSSY_MsgAddress_h
#define OCTOPUSSY_MsgAddress_h 1

#include <DMI/DMI.h>
#include <DMI/HIID.h>
#include <OCTOPUSSY/AID-OCTOPUSSY.h>

#pragma aidgroup OCTOPUSSY
#pragma aid Dispatcher Local Publish

namespace Octopussy
{
using namespace DMI;

//##ModelId=3C8F9A340206
class WPID : public HIID
{
  public:
    //##ModelId=3C8F9AC70027
      WPID();

      //##ModelId=3DB936DB0337
      WPID (AtomicID wpc, AtomicID inst = 0);


      //##ModelId=3C8F9AA503C1
      AtomicID wpclass () const;

      //##ModelId=3C8F9AAB0103
      AtomicID inst () const;
      
      string toString (char separator = '.') const
      { return HIID::toString(separator); }

    // Additional Public Declarations
    //##ModelId=3DB936DB02FA
      static const size_t byte_size = 2*sizeof(int);
};

//##ModelId=3C7B6F790197
class MsgAddress : public WPID
{
  public:
    //##ModelId=3C7B6FAE00FD
      MsgAddress();

      MsgAddress (const HIID &id);
      
      //##ModelId=3C8F9B8E0087
      MsgAddress (AtomicID wpc, AtomicID wpinst = 0, AtomicID proc = AidLocal, AtomicID host = AidLocal);

      //##ModelId=3DB936CA0217
      MsgAddress (const WPID& wpid, AtomicID proc = AidLocal, AtomicID host = AidLocal);


      //##ModelId=3C8F9BC10135
      WPID wpid () const;

      //##ModelId=3C7B6FF7033D
      AtomicID & process ();

      //##ModelId=3C90700001B4
      const AtomicID & process () const;

      //##ModelId=3C7B6FFC0330
      AtomicID & host ();

      //##ModelId=3C9070080170
      const AtomicID & host () const;

    // Additional Public Declarations
    //##ModelId=3DB936CA0358
      HIID peerid () const
      { return process()|host(); }
      
    //##ModelId=3DB936CA007D
      static const size_t byte_size = 4*sizeof(int);
};

// Class WPID 

//##ModelId=3C8F9AC70027
inline WPID::WPID()
{
}

//##ModelId=3DB936DB0337
inline WPID::WPID (AtomicID wpc, AtomicID inst)
    : HIID(wpc)
{
  add(inst);
}



//##ModelId=3C8F9AA503C1
inline AtomicID WPID::wpclass () const
{
  return (*this)[0];
}

//##ModelId=3C8F9AAB0103
inline AtomicID WPID::inst () const
{
  return (*this)[1];
}

// Class MsgAddress 

//##ModelId=3C7B6FAE00FD
inline MsgAddress::MsgAddress()
{
  resize(4);
}

inline MsgAddress::MsgAddress (const HIID &id)
{
  FailWhen(id.size()!=4,"invalid address length");
  HIID::operator = (id);
}

//##ModelId=3C8F9B8E0087
inline MsgAddress::MsgAddress (AtomicID wpc, AtomicID wpinst, AtomicID proc, AtomicID host)
    : WPID(wpc,wpinst)
{
  add(proc);
  add(host);
}

//##ModelId=3DB936CA0217
inline MsgAddress::MsgAddress (const WPID& wpid, AtomicID proc, AtomicID host)
    : WPID(wpid)
{
  add(proc);
  add(host);
}



//##ModelId=3C8F9BC10135
inline WPID MsgAddress::wpid () const
{
  return WPID(wpclass(),inst());
}

//##ModelId=3C7B6FF7033D
inline AtomicID & MsgAddress::process ()
{
  return (*this)[2];
}

//##ModelId=3C90700001B4
inline const AtomicID & MsgAddress::process () const
{
  return (*this)[2];
}

//##ModelId=3C7B6FFC0330
inline AtomicID & MsgAddress::host ()
{
  return (*this)[3];
}

//##ModelId=3C9070080170
inline const AtomicID & MsgAddress::host () const
{
  return (*this)[3];
}


};
#endif

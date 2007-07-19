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

#ifndef OCTOPUSSY_Subscriptions_h
#define OCTOPUSSY_Subscriptions_h 1

#include <DMI/DMI.h>
#include <DMI/HIID.h>
#include <OCTOPUSSY/MsgAddress.h>
#include <OCTOPUSSY/Message.h>
#include <list>

namespace Octopussy
{
using namespace DMI;

//##ModelId=3C999C8400AF

class Subscriptions 
{
  public:
    //##ModelId=3DB936DB02BE
      Subscriptions();


      //##ModelId=3C999D010361
      bool add (const HIID& id, const MsgAddress &scope);

      //##ModelId=3C999D40033A
      bool remove (const HIID &id);

      //##ModelId=3C999E0B0223
      void clear ();

      //##ModelId=3C99C0BB0378
      int size () const;

      //##ModelId=3C999D64004D
      bool merge (const Subscriptions &other);

      //##ModelId=3C999D780005
      bool matches (const Message &msg) const;

      //##ModelId=3C99AC2F01DF
      //##Documentation
      //## Stores HIID into raw data block
      size_t pack (void* block, size_t &nleft) const;

      //##ModelId=3C99AC2F022F
      void unpack (const void* block, size_t sz);

      //##ModelId=3C99AC2F027F
      //##Documentation
      //## Returns # of bytes required to store the HIID
      size_t packSize () const;

  private:
    // Additional Implementation Declarations
    //##ModelId=3DB936520168
      typedef struct { HIID mask; MsgAddress scope; } SubElement;
    //##ModelId=3DB9365201A4
      typedef std::list<SubElement> SubSet;
    //##ModelId=3DB936DB021F
      SubSet subs;
    //##ModelId=3DB9365201E0
      typedef SubSet::iterator SSI;
    //##ModelId=3DB936520227
      typedef SubSet::const_iterator CSSI;

      // this always keep track of the pack-size of the set.
      // it is updated by add() and remove().
    //##ModelId=3DB936DB025A
      size_t pksize;
};

// Class Subscriptions 


//##ModelId=3C99C0BB0378
inline int Subscriptions::size () const
{
  return subs.size();
}

//##ModelId=3C99AC2F027F
inline size_t Subscriptions::packSize () const
{
  return pksize;
}


};
#endif

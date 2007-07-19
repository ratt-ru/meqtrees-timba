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

#ifndef OCTOPUSSY_ListenerWP_h
#define OCTOPUSSY_ListenerWP_h 1

#include <OCTOPUSSY/WorkProcess.h>
    
namespace Octopussy
{

#pragma aid ListenerWP 

//##ModelId=3CA044DE02AB
class ListenerWP : public WorkProcess
{
  public:
      //##ModelId=3CA0451401B9
      ListenerWP ();

    //##ModelId=3DB9369A0073
      ~ListenerWP();


      //##ModelId=3CA045020054
      virtual void init ();


      //##ModelId=3CA0450C0103
      virtual int receive (Message::Ref &mref);


  private:
    //##ModelId=3DB9369B0043
      ListenerWP(const ListenerWP &right);

    //##ModelId=3DB9369B016F
      ListenerWP & operator=(const ListenerWP &right);

};

};
#endif

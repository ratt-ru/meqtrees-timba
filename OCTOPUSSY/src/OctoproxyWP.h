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

#ifndef OCTOPROXYWP_H_HEADER_INCLUDED_C75F583E
#define OCTOPROXYWP_H_HEADER_INCLUDED_C75F583E

#include <OCTOPUSSY/WorkProcess.h>
#include <OCTOPUSSY/Message.h>

namespace Octopussy
{
using namespace DMI;

namespace Octoproxy 
{

//##ModelId=3E08FF0D035E
class ProxyWP : public WorkProcess
{
  public:
    //##ModelId=3E08FFD30196
    ProxyWP(AtomicID wpid);
  
  
  protected:

  private:

    //##ModelId=3E08FF12002C
    ProxyWP();

    //##ModelId=3E08FF120032
    ProxyWP& operator=(const ProxyWP& right);
    //##ModelId=3E08FF12002E
    ProxyWP(const ProxyWP& right);


};

} // namespace Octoproxy



};
#endif /* OCTOPROXYWP_H_HEADER_INCLUDED_C75F583E */

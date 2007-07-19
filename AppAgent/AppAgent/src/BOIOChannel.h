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

#ifndef APPAGENT_SRC_BOIOCHANNEL_H_HEADER_INCLUDED_D0F0C734
#define APPAGENT_SRC_BOIOCHANNEL_H_HEADER_INCLUDED_D0F0C734
    
#include <AppAgent/FileChannel.h>
#include <AppAgent/AID-AppAgent.h>
#include <DMI/BOIO.h>
    
#pragma aid BOIO File Name Mode Event Data

namespace AppAgent
{    
    
namespace AppEvent
{
  const HIID
              FBOIOFileName   = AidBOIO|AidFile|AidName,
              FBOIOFileMode   = AidBOIO|AidFile|AidMode;
};
    

//##ModelId=3E53C56B02DD
class BOIOChannel : public FileChannel
{
  public:
    //##ModelId=3E53C59D00EB
    //##Documentation
    virtual int  init (const DMI::Record &data);

    //##ModelId=3E53C5A401E1
    //##Documentation
    virtual void close (const string &str="");

    //##ModelId=3E53C5C2003E
    //##Documentation
    //## Posts an event on behalf of the application.
    virtual void postEvent (const HIID &id,
                            const ObjRef &data = ObjRef(),
                            AtomicID category = AidNormal,
                            const HIID &destination = HIID() );
    //##ModelId=3E8C252801E8
    //##Documentation
    //## Checks whether a specific event is bound to any output. Returns
    //## true if an output file is open.
    virtual bool isEventBound (const HIID &id,AtomicID category);

    //##ModelId=3E53C5CE0339
    virtual string sdebug (int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3E54E815039B
    LocalDebugContext;
    
  protected:
    //##ModelId=3EC23EF30079
    virtual int refillStream();

  private:
    //##ModelId=3E54BD23023F
    mutable BOIO boio;
  
};

};
#endif /* APPAGENT_SRC_BOIOCHANNEL_H_HEADER_INCLUDED_D0F0C734 */

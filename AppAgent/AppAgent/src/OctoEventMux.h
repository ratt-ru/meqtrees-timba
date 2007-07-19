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

#ifndef OCTOAGENT_SRC_EVENTMULTIPLEXER_H_HEADER_INCLUDED_B481AF8F
#define OCTOAGENT_SRC_EVENTMULTIPLEXER_H_HEADER_INCLUDED_B481AF8F
    
#include <OCTOPUSSY/Message.h>
#include <OCTOPUSSY/WorkProcess.h>
#include <AppAgent/OctoChannel.h>
    
namespace AppAgent
{    

class EventFlag;
    
//##ModelId=3E26BABA0069
class OctoEventMux : public Octopussy::WorkProcess
{
  public:
      
    //##ModelId=3E26BE240137
    explicit OctoEventMux (AtomicID wpid);
  
    //##ModelId=3E26BE670240
    virtual ~OctoEventMux ();
  
    //##ModelId=3E50F5040362
    EventFlag & eventFlag();
    
    //##ModelId=3E535889025A
    OctoChannel & newChannel ();

    //##ModelId=3E428F93013E
    OctoEventMux& addChannel  (OctoChannel::Ref &channel);
    //##ModelId=3E26BE760036
    OctoEventMux&  addChannel (OctoChannel* channel,int flags = DMI::ANONWR);
    //##ModelId=3E428F70021D
    OctoEventMux&  addChannel (OctoChannel& channel,int flags = DMI::WRITE);
    
    //##ModelId=3E428F7002D6
    OctoEventMux&  operator <<= (OctoChannel* channel)
    { return addChannel(channel,DMI::ANONWR); }
    //##ModelId=3E428F700392
    OctoEventMux&  operator <<= (OctoChannel& channel)
    { return addChannel(channel,DMI::ANONWR); }
    
    //##ModelId=3E50E02C024B
    void init();
    //##ModelId=3E50E292002B
    void close();
    
    //##ModelId=3E26D2D6021D
    int   getEvent (HIID& id,ObjRef& data,
                    const HIID& mask,int wait,
                    HIID &source,int channel_id);
    //##ModelId=3E3FC3A601B0
    int   hasEvent (const HIID& mask,HIID &out,int channel_id);
    
    //##ModelId=3E26E30E01C5
    string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    
    //##ModelId=3E26E70701D5
    const char * debug ( int detail = 1,const string &prefix = "",
                         const char *name = 0 ) const
    { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

    //##ModelId=3E53599A0049
    LocalDebugContext;
    
    //##ModelId=3E9BD63F0297
    DefineRefTypes(OctoEventMux,Ref);
    
  protected:
    //##ModelId=3E47C84502CD
    virtual void notify ();
    //##ModelId=3E47CFA70203
    virtual void stop();


  private:
    //##ModelId=3E26BE6701CD
    OctoEventMux (const OctoEventMux& right);
    //##ModelId=3E26BE670273
    OctoEventMux& operator=(const OctoEventMux& right);
    //##ModelId=3E428FC40127
    OctoEventMux();
      
    //##ModelId=3E3FC3A7000B
    int checkQueue (const HIID& mask,int wait,int channel_id);

    //##ModelId=3E428C4D0239
    std::vector<OctoChannel::Ref> channels;
    //##ModelId=3E3FC3A50362
    int assigned_channel;
    //##ModelId=3E3FC3A6004B
    HIID assigned_event;
    //##ModelId=3F5F4364023A
    HIID assigned_source;
    //##ModelId=3E50E2D3025D
    ObjRef assigned_data;
    //##ModelId=3E50E2D801A4
    const Octopussy::Message * pheadmsg;
    
    //##ModelId=3E47C785025B
    EventFlag::Ref eventFlag_;
    //##ModelId=3E47BE2D0131
    int ef_channel_num;
};

//##ModelId=3E50F5040362
inline EventFlag & OctoEventMux::eventFlag()
{
  return eventFlag_.dewr();
}


};
#endif /* OCTOAGENT_SRC_OCTOMULTIPLEXER_H_HEADER_INCLUDED_B481AF8F */

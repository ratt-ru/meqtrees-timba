//#  EventGenerator.h: class to generate DMI events
//#
//#  Copyright (C) 2002-2004
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef MEQ_EVENTGENERATOR_H
#define MEQ_EVENTGENERATOR_H 1

#include <DMI/Events.h>
#include <list>

namespace Meq
{
    
class EventGenerator
{
  private:  
    //## list of event recepients for when result is available
    typedef std::list<EventSlot> SlotList;
    SlotList slots_;
    
  public:
    //##Documentation
    //## sends event to all event slots
    int generateEvent (const ObjRef::Copy &data = ObjRef(),void *ptr=0) const
    {
      SlotList::const_iterator iter = slots_.begin();
      for( ; iter != slots_.end(); iter++ )
        iter->receive(data.copy(DMI::READONLY),ptr);
      return 0;  
    }
     
    //##Documentation
    //## adds an event slot to which generated results will be published
    void addSlot    (const EventSlot &slot);
  
    //##Documentation
    //## removes subscription for specified event slot
    void removeSlot (const EventSlot &slot);
    
    //##Documentation
    //## removes all subscriptions for specified recepient
    void removeSlot (const EventRecepient *recepient);
    
    //##Documentation
    //## checks if any event slots are subscribed
    bool active () const
    { return !slots_.empty(); }

};

} // namespace Meq

#endif

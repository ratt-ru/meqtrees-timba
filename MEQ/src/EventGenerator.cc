#include "EventGenerator.h"

namespace Meq
{
            
//## adds an event slot to which generated results will be published
void EventGenerator::addSlot (const EventSlot &slot)
{
  SlotList::const_iterator iter = 
        std::find(slots_.begin(),slots_.end(),slot);
  if( iter == slots_.end() )
    slots_.push_back(slot);
}

//## removes subscription for specified event slot
void EventGenerator::removeSlot (const EventSlot &slot)
{
  SlotList::iterator iter = slots_.begin();
  while( iter != slots_.end())
  {
    if( slot.evId() == iter->evId() && slot.recepient() == iter->recepient() )
      slots_.erase(iter++);
    else
      iter++;
  }
}

//##Documentation
//## removes all subscriptions for specified recepient
void EventGenerator::removeSlot (const EventRecepient *recepient)
{
  SlotList::iterator iter = slots_.begin();
  while( iter != slots_.end())
  {
    if( recepient == iter->recepient() )
      slots_.erase(iter++);
    else
      iter++;
  }
}

}

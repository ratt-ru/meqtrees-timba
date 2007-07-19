//#  EventRecepient.h: abstract interface for an object that can receive events
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
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

#ifndef DMI_EVENTS_H
#define DMI_EVENTS_H 1

#include <DMI/HIID.h>
#include <DMI/BObj.h>

namespace DMI
{

class EventIdentifier
{
  private:
    HIID   id_;
    ObjRef ref_;
    void * ptr_;
    
  public:
      EventIdentifier (const HIID &id1,const ObjRef &ref1,void *ptr1=0)
      : id_(id1),
        ref_(ref1,DMI::LOCK),
        ptr_(ptr1) 
      {}
  
      EventIdentifier (const HIID &id1=HIID(),void *ptr1=0)
      : id_(id1),ptr_(ptr1) 
      {}
      
      EventIdentifier (const EventIdentifier &other)
      : id_(other.id_),
        ref_(other.ref_,DMI::LOCK),
        ptr_(other.ptr_) 
      { 
        ref_.lock(); 
      }
      
      EventIdentifier & operator = (const EventIdentifier &other)
      {
        if( this != &other )
        {
          id_ = other.id_;
          ref_.unlock().copy(other.ref_).lock();
          ptr_ = other.ptr_;
        }
        return *this;
      }
      
      const HIID & id () const
      { return id_; }
      
      const ObjRef & ref () const
      { return ref_; }
      
      void * ptr () const
      { return ptr_; }
      
      bool operator == (const EventIdentifier &other) const
      { return id_ == other.id_; }
      
      bool operator != (const EventIdentifier &other) const
      { return id_ != other.id_; }
      
};

class EventRecepient
{
  public:
    virtual int receiveEvent (const EventIdentifier &evid,
                              const ObjRef::Xfer &evdata,
                              void *ptr) =0;
};

class EventSlot
{
  private:
    EventIdentifier evid_;
    mutable EventRecepient *recepient_;
      
  public:
    EventSlot (EventRecepient *recpt)
    : recepient_(recpt) {}
    
    EventSlot (const EventIdentifier &evid,EventRecepient *recpt)
    : evid_(evid),recepient_(recpt) {}
    
    EventSlot (const HIID &evid_id,EventRecepient *recpt)
    : evid_(evid_id),recepient_(recpt) {}
    
    int receive (const ObjRef::Xfer &data = ObjRef(),void *ptr=0) const
    { return recepient_->receiveEvent(evid_,data,ptr); }
    
    const EventIdentifier & evId () const
    { return evid_; }
    
    const EventRecepient * recepient () const
    { return recepient_; }
    
    bool operator == (const EventSlot &other) const
    { return evid_ == other.evid_ && recepient_ == other.recepient_; }
    
    bool operator != (const EventSlot &other) const
    { return ! (*this).operator == (other); }
    
};

};    
#endif

//  AppEventSink.cc: abstract interface for an event agent
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

#include "AppEventSink.h"
#include "AID-AppAgent.h"

//##ModelId=3E4100E40257
AppEventSink::AppEventSink(const HIID &initf)
  : AppAgent(initf)
{
}

//##ModelId=3E4143B200F2
bool AppEventSink::init(const DataRecord &)
{
  return True;
}


    
//##ModelId=3E394D4C02BB
int AppEventSink::getEvent (HIID &,ObjRef &,const HIID &,int wait)
{ 
  if( wait == NOWAIT )
    return WAIT; 
  Throw("waiting for an event here would block indefinitely");
}

//##ModelId=3E394D4C02C1
int AppEventSink::hasEvent (const HIID &) const
{ 
  return WAIT; 
}


//##ModelId=3E394D4C02C9
void AppEventSink::postEvent (const HIID &, const ObjRef &)
{
}

void AppEventSink::flush ()
{
}

//##ModelId=3E3E744E0258
int AppEventSink::getEvent (HIID &id, DataRecord::Ref &data, const HIID &mask, int wait)
{
  ObjRef ref;
  int res = getEvent(id,ref,mask,wait);
  if( res == SUCCESS && ref.valid() )
    data = ref.ref_cast<DataRecord>();
  return res;
}

//##ModelId=3E3E747A0120
void AppEventSink::postEvent(const HIID &id, const DataRecord::Ref & data)
{
  if( data.valid() )
  {
    ObjRef ref(data.ref_cast<BlockableObject>(),DMI::COPYREF|DMI::PRESERVE_RW);
    postEvent(id,ref);
  }
  else
    postEvent(id);
}

//##ModelId=3E3FD6180308
void AppEventSink::postEvent(const HIID &id, const string &text)
{
  DataRecord::Ref ref;
  ref <<= new DataRecord;
  ref()[AidText] = text;
  postEvent(id,ref);
}


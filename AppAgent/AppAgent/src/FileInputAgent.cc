//  VisFileInputHeader.cc: common base class for VisInputAgents that read files
    
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

#include "FileInputAgent.h"
#include "AID-VisAgent.h"

namespace VisAgent
{
  
using namespace AppEvent;
  
static int dum = aidRegistry_VisAgent();


//##ModelId=3F5F43650356
DMI::Record & FileInputAgent::initHeader ()
{
  DMI::Record *hdr;
  header_ <<= hdr = new DMI::Record;
  return *hdr;
}

//##ModelId=3F5F436503B9
int FileInputAgent::hasHeader ()
{
  if( suspended() ) 
    return sink().waitOtherEvents(NOWAIT);
  else if( fileState() == HEADER )
    return SUCCESS;
  else if( fileState() == DATA )
    return OUTOFSEQ;
  else 
    return CLOSED;
}

//##ModelId=3F5F4365036A
int FileInputAgent::getHeader (DMI::Record::Ref &hdr,int wait)
{
  // is the file state correct for a header?
  int res = hasHeader();
  if( res == SUCCESS )
  {
    hdr.copy(header_);
    setFileState(DATA);
    return SUCCESS;
  }
  else if( res == CLOSED )
    return CLOSED;
  else
  {
    return sink().waitOtherEvents(wait);
  }
}

//##ModelId=3F5F436503CF
int FileInputAgent::hasTile   ()
{
  if( suspended() )
    return sink().waitOtherEvents(NOWAIT);
  else if( fileState() == HEADER )
    return OUTOFSEQ;
  else if( fileState() == DATA )
    return SUCCESS;
  else 
    return CLOSED;
}

//##ModelId=3E2C299201D6
int FileInputAgent::state() const
{
  switch( fileState() )
  {
    case HEADER:
    case DATA:        return AppState::RUNNING;
    case FILECLOSED:  return AppState::INIT;
    case ENDFILE:     return AppState::CLOSED;
    default:          return AppState::ERROR;
  }
}

//##ModelId=3E2C2999029A
string FileInputAgent::stateString() const
{
  return fileState() == FILEERROR 
         ? "ERROR " + errorString()
         :  "OK (" + fileStateString() + ")";
}



}


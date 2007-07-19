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

#ifndef _VISAGENT_VISAGENTVOCABULARY_H
#define _VISAGENT_VISAGENTVOCABULARY_H

#include <AppAgent/FileChannel.h>    
#include <AppAgent/AID-AppAgent.h>
#include <VisCube/VisVocabulary.h>
    
#pragma aidgroup AppAgent
#pragma aid Vis Input Output Agent Parameters 
#pragma aid Data Header Footer Tile Suspend Resume
    
namespace AppAgent
{    
    
namespace VisData
{
  using VisVocabulary::FVDSID;
  
  const AtomicID VisEventPrefix = AidVis;
  
  // these are used as event types below, and also as channel state
  const int HEADER  = -AidHeader_int;
  const int DATA    = -AidData_int;
  const int FOOTER  = -AidFooter_int;
  
  const HIID  _VisEventMask = VisEventPrefix|AidWildcard;

  inline const HIID & VisEventMask () 
  { return _VisEventMask; }
  
  inline HIID VisEventHIID (int type,const HIID &instance)
  { return VisEventPrefix|AtomicID(-type)|instance; }
  
  inline HIID VisEventMask (int type)
  { return VisEventHIID(type,AidWildcard); }
  
  inline int VisEventType  (const HIID &event)
  { return -( event[1].id() ); }
  
  inline HIID VisEventInstance (const HIID &event)
  { return event.subId(2); }
  
  const HIID 
       // suspend/resume events
       SuspendEvent    = AidVis|AidSuspend,
       ResumeEvent     = AidVis|AidResume;
      
  inline string codeToString (int code)
  { return AtomicID(-code).toString(); }
};

};    
#endif

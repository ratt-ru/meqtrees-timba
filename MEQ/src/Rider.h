//#  Rider.h: namespace providing helper functions for managing Request riders
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
#ifndef MEQ_RIDER_H_HEADER_INCLUDED_E5514413
#define MEQ_RIDER_H_HEADER_INCLUDED_E5514413

#include <MEQ/Request.h>
#include <MEQ/MeqVocabulary.h>
#include <DMI/Record.h>
#include <DMI/Vec.h>

namespace Meq
{

//## This namespace provides utility functions for manipulating
//## the request rider.
namespace Rider
{   
  
//## bitwise flags for methods below. Note that they are cumulative
typedef enum {
  NEW_RIDER     = 0x01,
  NEW_GROUPREC  = 0x02,
  NEW_CMDREC    = 0x04,
  NEW_ALL       = 0x07
} RiderFlags;

//## Clears the rider from the request, if any.
//## Reqref will be COWed as needed.
void clear (Request::Ref &reqref);

//## Inits (if necessary) and returns the rider.
//## Reqref will be COWed as needed.
//## If the NEW_RIDER flag is given, always creates a new rider.
DMI::Record & getRider (Request::Ref &reqref,int flags=0);

//## Inits (if necessary) and returns the group command record for 'group'.
//## Reqref will be COWed as needed.
//## If the NEW_RIDER flag is given, always creates a new rider.
//## If the NEW_GROUPREC flag is given, always creates a new GCR.
DMI::Record & getGroupRec (Request::Ref &reqref,const HIID &group,int flags=0);

//## Inits (if necessary) and returns the command_all subrecord for the given group.
//## Reqref will be COWed as needed.
//## If the NEW_RIDER flag is given, always creates a new rider.
//## If the NEW_GROUPREC flag is given, always creates a new GCR.
//## If the NEW_CMDREC flag is given, always creates a new command subrecord.
DMI::Record & getCmdRec_All (Request::Ref &reqref,const HIID &group,int flags=0);

//## Inits (if necessary) and returns the command_by_nodeindex subrecord for 
//## the given group. Reqref will be COWed as needed.
//## If the NEW_RIDER flag is given, always creates a new rider.
//## If the NEW_GROUPREC flag is given, always creates a new GCR.
//## If the NEW_CMDREC flag is given, always creates a new command subrecord.
DMI::Record & getCmdRec_ByNodeIndex (Request::Ref &reqref,const HIID &group,int flags=0);

//## Inits (if necessary) and returns the command_by_list subrecord (field) for 
//## the given group. Reqref will be COWed as needed.
//## If the NEW_RIDER flag is given, always creates a new rider.
//## If the NEW_GROUPREC flag is given, always creates a new GCR.
//## If the NEW_CMDREC flag is given, always creates a new command subrecord.
DMI::Vec & getCmdRec_ByList (Request::Ref &reqref,const HIID &group,int flags=0);

//## Inits (if necessary) and returns a subrecord for rec[field]
DMI::Record & getOrInit (DMI::Record &rec,const HIID &field);


};

};
#endif

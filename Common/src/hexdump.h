//#  hexdump.h: create hexdump of given datablock
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

#ifndef COMMON_HEXDUMP_H
#define COMMON_HEXDUMP_H

#include <lofar_config.h>
#include <Common/LofarTypes.h>
#include <Common/lofar_string.h>


namespace LOFAR
{

void hexdump (						 	 const void* buf, int32	nrBytes);
void hexdump (FILE*				aFile, 	 const void* buf, int32	nrBytes);
void hexdump (char*				aChrPtr, const void* buf, int32	nrBytes);
void hexdump (string&			aString, const void* buf, int32	nrBytes);

} // namespace LOFAR

#endif

//# LofarTypes.h
//#
//#  Copyright (C) 2002-2003
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

#ifndef COMMON_LOFARTYPES_H
#define COMMON_LOFARTYPES_H

#include <Common/LofarTypedefs.h>
#include <lofar_config.h>

//# Make sure we include <sys/types.h> or <qglobal.h> if availabe. These files
//# contain a number of typedefs for commonly used primitive data types. Some
//# of these will clash with our typedefs -- more specifically ushort, uint,
//# and ulong -- so we will use the ones in <sys/types.h> or <qglobal.h>
#if defined(HAVE_QT)
# include <qglobal.h>    // contains typedef for uchar as well
#else
# include <sys/types.h>
#endif

namespace LOFAR
{
  //# Make the type names defined in LofarTypedefs.h available in the
  //# namespace LOFAR. 

#if defined(HAVE_QT)
  using ::uchar;
#else
  using TYPES::uchar;
#endif
  using ::ushort;
  using ::uint;
  using ::ulong;
  using TYPES::longlong;
  using TYPES::ulonglong;
  using TYPES::ldouble;
  using TYPES::fcomplex;
  using TYPES::dcomplex;
 
  using TYPES::int8;
  using TYPES::uint8;
  using TYPES::int16;
  using TYPES::int32;
  using TYPES::int64;
  using TYPES::uint16;
  using TYPES::uint32;
  using TYPES::uint64;
}

#ifdef MAKE_LOFAR_SYMBOLS_GLOBAL
#include <Common/lofar_global_symbol_warning.h>

//# Make the type names defined in LofarTypedefs.h available in the
//# global name space.

using LOFAR::uchar;
using LOFAR::ushort;
using LOFAR::uint;
using LOFAR::ulong;
using LOFAR::longlong;
using LOFAR::ulonglong;
using LOFAR::ldouble;
using LOFAR::fcomplex;
using LOFAR::dcomplex;

using LOFAR::int8;
using LOFAR::int16;
using LOFAR::int32;
using LOFAR::int64;
using LOFAR::uint8;
using LOFAR::uint16;
using LOFAR::uint32;
using LOFAR::uint64;

#endif // #ifdef MAKE_LOFAR_SYMBOLS_GLOBAL

#endif

//# LofarTypedefs.h
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

#ifndef COMMON_LOFARTYPEDEFS_H
#define COMMON_LOFARTYPEDEFS_H

#include <complex>
#include <unistd.h>

namespace LOFAR {

  // Define shorthands for various data types and define integer data
  // types with a guaranteed length.
  // The types are in a namespace to prevent pollution of the global
  // namespace.

  namespace TYPES {

    // Convenience shortcuts.
    typedef unsigned char        uchar;
    typedef unsigned short       ushort;
    typedef unsigned int         uint;
    typedef unsigned long        ulong;
    typedef long long            longlong;
    typedef unsigned long long   ulonglong;
    typedef long double          ldouble;
    typedef std::complex<float>  fcomplex;
    typedef std::complex<double> dcomplex;
 
    // Fixed data sizes.
    typedef char                int8;
    typedef unsigned char       uint8;
    typedef short               int16;
    typedef int                 int32;
    typedef long long           int64;
    typedef unsigned short     uint16;
    typedef unsigned int       uint32;
    typedef unsigned long long uint64;
  }
}


#endif

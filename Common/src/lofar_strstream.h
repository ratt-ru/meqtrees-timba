//  lofar_strstream.h:
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

#ifndef COMMON_STRSTREAM_H
#define COMMON_STRSTREAM_H

// The strstream classes are considered deprecated. The are not supported
// anymore in GCC 3.3 and higher.
#ifdef __DEPRECATED
#warning The file lofar_strstream.h is deprecated. \
         You should use lofar_sstream.h instead.
#endif

// strstream.h is only available in the old STL (version 2, which comes
// by default with gcc-2.95.x -- this does not define __GLIBCPP__), and in 
// STL version 3 supplied with gcc-3.1, where it's provided for backwards
// compatibility.
// In the STLv3 snapshot we use with gcc-2.95, strstream.h is not available.
#if !defined(__GLIBCPP__) || __GNUC__ >= 3 && __GNUC_MINOR__ <= 1
#include <strstream.h>
#endif

#include <sstream>

namespace LOFAR 
{
  using std::istringstream;
  using std::ostringstream;
}

#ifdef MAKE_LOFAR_SYMBOLS_GLOBAL
#include <Common/lofar_global_symbol_warning.h>
using LOFAR::istringstream;
using LOFAR::ostringstream;
#endif

#endif

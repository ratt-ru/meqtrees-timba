//#  lofar_global_symbol_warning.h: one line description
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

#ifndef COMMON_LOFAR_GLOBAL_SYMBOL_WARNING_H
#define COMMON_LOFAR_GLOBAL_SYMBOL_WARNING_H

#ifdef __DEPRECATED
#warning Making LOFAR symbols available in the global namespace is \
deprecated. Please change your code as follows: 1) all declarations in the \
header files should be put in the namespace LOFAR; 2) all implementations in \
the source files should either be put in the namespace LOFAR, or should \
contain the using directive "using namespace LOFAR". To disable this warning \
use -Wno-deprecated.
#endif

#endif

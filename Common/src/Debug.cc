//  Debug.cc:
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

#include <stdio.h>
#include <stdarg.h>
#include <sys/time.h>
#include <fstream>

// For backward compatibility
#define MAKE_LOFAR_SYMBOLS_GLOBAL

#ifdef USE_THREADS
#include "Common/Thread.h"
#endif

// Debug
#include "Debug.h"

namespace Debug
{
  using namespace std;
}

#include <Common/backward/Debug.cc>

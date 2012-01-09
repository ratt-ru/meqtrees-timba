//# CUDAPointSourceVisibilityCommon.h: The point source DFT component for a station
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id: CUDAPointSourceVisibility.h 5418 2007-07-19 16:49:13Z oms $

#ifndef MEQNODES_CUDAPOINTSOURCEVISIBILITYCOMMON_H
#define MEQNODES_CUDAPOINTSOURCEVISIBILITYCOMMON_H

#ifndef STRIP_CUDA
#include <cuda_runtime.h>

typedef double3 lmn_t;

//typedef double2 complex_type;
//typedef double  real_type;


//typedef float2 complex_type;
//typedef float  real_type;

#endif

#define MULTI_SRC_PER_THREAD
#define SHARED_MEMORY

#endif

//# PerfProfile.cc: Profiling code.
//#
//# Copyright (C) 2002
//# ASTRON (Netherlands Foundation for Research in Astronomy)
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
//# $Id$

#include <Common/Profiling/PerfProfile.h>

namespace LOFAR 
{

#if defined(HAVE_MPICH) && defined(HAVE_MPI_PROFILER)
#include <mpi.h>

  const char* const PerfProfile::m_colors[] = {
    "blue",
    "red",
    "green",
    "purple",
    "yellow",
    "orange",
    "brown",
    "grey",
    "pink",
  };

  int           PerfProfile::m_nr_colors  = sizeof(PerfProfile::m_colors) / sizeof(char*);
  int           PerfProfile::iInitialized = 0;
  int           PerfProfile::iStop        = 0;
  unsigned char PerfProfile::debugMask    = 0;

#endif

  void PerfProfile::init(int* argc, char*** argv, unsigned char theDebugMask)
  {
#if defined(HAVE_MPICH) && defined(HAVE_MPI_PROFILER)
    // check if MPI already initialized
    (void)MPI_Initialized(&iInitialized);

    if (!iInitialized)
    {
      MPI_Init(argc, argv);
    }

    int iStart = MPE_Log_get_event_number();
    iStop  = MPE_Log_get_event_number();
    MPE_Describe_state(iStart, iStop, "Total runtime", "red");
    MPE_Start_log();
    MPE_Log_event(iStart, 0, "start");

    debugMask = theDebugMask;

#else
    // keep the compiler happy :-)
    argc=argc; argv=argv;
#endif
  }

  void PerfProfile::finalize()
  {
#if defined(HAVE_MPICH) && defined(HAVE_MPI_PROFILER)
    MPE_Log_event(iStop, 0, "stop");
    if (!iInitialized)
    {
      MPI_Finalize();
    }
#endif
  }

} // namespace LOFAR

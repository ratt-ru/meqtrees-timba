//# PerfProfile.h: profile class based on MPICH MPE library
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

#ifndef COMMON_PERFPROFILE_H
#define COMMON_PERFPROFILE_H

#include <lofar_config.h>

#if defined(HAVE_MPICH) && defined(HAVE_MPI_PROFILER)
#define MPICH_SKIP_MPICXX
#include <mpe.h>
#endif

#include <Common/lofar_string.h>
#include <cstdio>

namespace LOFAR
{

  /**
   *
   * The interface of the PerfProfile class is defined by the following functions and macros.
   *
   * -- Initialize the profiling functionality, this involves calling MPI_Init() if it had
   * -- not been called already
   * static void PerfProfile::init(int argc, char** argv);
   *
   * -- Finalize profiling functionality. This involves calling MPI_Finalize if it had not
   * -- been called already.
   * static void PerfProfile::finalize();
   *
   * -- Profile a region of code from the occurence of the macro call until the current
   * -- scope is exited. E.g.:
   * -- int test()
   * -- {
   * --     PERFPROFILE(__PRETTY_FUNCTION__);
   * --     // operations
   * -- }
   * -- Will time the duration of this function from beginning to when it exits its scope.
   *
   * #define PERFPROFILE(tag)
   *
   * The other methods are not to be used directly.
   *
   * When HAVE_MPICH and HAVE_MPI_PROFILER are not defined together the methods 'init'
   * and 'finalize' are no-ops and the macro PERFPROFILE(tag) evaluates to an empty string
   * thus disabling the profiling.
   *
   **/

#define PP_LEVEL_0 (1 << 0)
#define PP_LEVEL_1 (1 << 1)
#define PP_LEVEL_2 (1 << 2)
#define PP_LEVEL_3 (1 << 3)
#define PP_LEVEL_4 (1 << 4)
#define PP_LEVEL_5 (1 << 5)
#define PP_LEVEL_6 (1 << 6)
#define PP_LEVEL_7 (1 << 7)

  class PerfProfile
  {
  public:
    static void init(int* argc, char*** argv, unsigned char debugMask);
    static void finalize();

#if defined(HAVE_MPICH) && defined(HAVE_MPI_PROFILER)
    inline PerfProfile(int start, int stop) : m_stop(stop), m_debugLevel(PP_LEVEL_0)
    {
      if (m_debugLevel & debugMask)
      {
        MPE_Start_log();
        MPE_Log_event(start, start, (char*)0);
      }
    }

    inline PerfProfile(int start, int stop, unsigned char debugLevel)
      : m_stop(stop), m_debugLevel(debugLevel)
    {
      if (m_debugLevel & debugMask)
      {
        MPE_Start_log();
        MPE_Log_event(start, start, (char*)0);
      }
    }

    inline ~PerfProfile()
    {
      if (m_debugLevel & debugMask)
      {
        MPE_Log_event(m_stop, m_stop, (char*)0);
      }
    }

    static int get_second_event_number(int start, const char* tag, unsigned char debugLevel)
    {
      static int cur_color_index = 0;
      int stop = 0;

      if (debugLevel & debugMask)
      {
        stop = MPE_Log_get_event_number();
        MPE_Describe_state(start, stop, (char*)tag,
                           (char*)PerfProfile::m_colors[cur_color_index]);
        cur_color_index = (cur_color_index + 1 ) % PerfProfile::m_nr_colors;
      }

      return stop;
    }

  private:
    int m_stop;
    string m_tag;
    unsigned char m_debugLevel;

    static const char* const m_colors[];
    static int m_nr_colors;
    static int iInitialized;
    static int iStop;
    static unsigned char debugMask;
#endif
  };

#if defined(HAVE_MPICH) && defined(HAVE_MPI_PROFILER)

#define PERFPROFILE(tag) \
    static int _mpe_entry_ = MPE_Log_get_event_number(); \
    static int _mpe_exit_  = PerfProfile::get_second_event_number(_mpe_entry_, (tag), (PP_LEVEL_0)); \
    PerfProfile _mpe_profile_(_mpe_entry_, _mpe_exit_) /* intentionally missing semicolon */

#define PERFPROFILE_L(tag, level) \
    static int _mpe_entry_ = MPE_Log_get_event_number(); \
    static int _mpe_exit_  = PerfProfile::get_second_event_number(_mpe_entry_, (tag), (level)); \
    PerfProfile _mpe_profile_(_mpe_entry_, _mpe_exit_, (level)) /* intentionally missing semicolon */

#else
#define PERFPROFILE(tag)
#define PERFPROFILE_L(tag, level)
#endif

} // namespace LOFAR

#endif

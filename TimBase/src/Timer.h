//# Timer.h: Accurate timer
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
//# $Id$

#ifndef COMMON_TIMER_H
#define COMMON_TIMER_H

#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>


namespace LOFAR {

  // Low-overhead and high-resolution interval timer for use on i386 and x86_64
  // platforms, using the processor's timestamp counter that is incremented each
  // cycle.  Put timer.start() and timer.stop() calls around the piece of
  // code to be timed; make sure that start() and stop() calls alternate.
  // A timer can be started and stopped multiple times; both the average and
  // total time, as well as the number of iterations are printed.
  // The measured time is real time (as opposed to user or system time).
  // The timer can be used to measure 10 nanosecond to a century time intervals.

  class NSTimer {
    public:
        NSTimer  (const char *name = 0);
        ~NSTimer ();

        void                   start ();
        void                   stop  ();
        void                   reset ();
        
        void                   add (const NSTimer &other);
        
        std::ostream           &print(std::ostream &);
        
        bool                   isRunning () const
        { return running; }
        
        long long              totalTime () const
        { return total_time; }
        
        int                    shotCount () const
        { return count; }
        
        long long              averageTime () const
        { return total_time/count; }
        
        double                 faverageTime () const
        { return total_time/double(count); }
        
        static double          cpuSpeedInMHz ()
        { return CPU_speed_in_MHz; }

    private:
        void                   print_time(std::ostream &, const char *which, double time) const;

        long long              total_time;
        unsigned long long     count;
        std::string            name;
        bool                   running;

        static double          CPU_speed_in_MHz, get_CPU_speed_in_MHz();
  };


  std::ostream &operator << (std::ostream &, class NSTimer &);


  inline void NSTimer::reset()
  {
    total_time = 0;
    count      = 0;
    running    = false;
  }


  inline NSTimer::NSTimer(const char *nm)
    :
    name(nm != 0 ? nm : "" )
  {
    reset();
  }


  inline NSTimer::~NSTimer()
  {
  }


  inline void NSTimer::start()
  {
#if (defined __GNUC__ || defined __INTEL_COMPILER) && (defined __i386 || defined __x86_64)
    asm volatile
    (
        "rdtsc\n\t"
        "subl %%eax, %0\n\t"
        "sbbl %%edx, %1"
    :
        "=m" ((reinterpret_cast<int *>(&total_time))[0]),
        "=m" ((reinterpret_cast<int *>(&total_time))[1])
    :
    :
        "eax", "edx"
    );
    running = true;
#endif
  }


  inline void NSTimer::stop()
  {
#if (defined __GNUC__ || defined __INTEL_COMPILER) && (defined __i386 || defined __x86_64)
    asm volatile
    (
        "rdtsc\n\t"
        "addl %%eax, %0\n\t"
        "adcl %%edx, %1"
    :
        "=m" ((reinterpret_cast<int *>(&total_time))[0]),
        "=m" ((reinterpret_cast<int *>(&total_time))[1])
    :
    :
        "eax", "edx"
    );
#endif
    running = false;

    ++ count;
  }
  
  inline void NSTimer::add (const NSTimer &other)
  {
    total_time += other.total_time;
    count += other.count;
  }
  
}  // end namespace LOFAR


#endif

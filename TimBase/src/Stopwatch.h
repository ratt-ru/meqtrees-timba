//  Stopwatch.h: timer class
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

#ifndef COMMON_STOPWATCH_H
#define COMMON_STOPWATCH_H

//# Includes
#include <sys/times.h>
#include <Common/lofar_string.h>

namespace LOFAR
{

  // This class functions as a timer.
  // It can give the user, system and elapsed time spent.

  //##ModelId=3DB95464020D
  class Stopwatch 
  {
  private:
    //##ModelId=3DB9546402F8
    struct tms tms;
    //##ModelId=3DB9546402FA
    clock_t tick;
    //##ModelId=3DB9546402FB
    clock_t last_tick;
      
    //##ModelId=3DB9546402FC
    double fire_secs;
    //##ModelId=3DB9546402FE
    int namewidth;
  
    //##ModelId=3DB9546402FF
    static double scale; // seconds per tick
    //##ModelId=3DB954640301
    static struct tms dummy_tms;
      
  
  public:
    //##ModelId=3DB954640213
    typedef enum { USER=1,SYSTEM=2,REAL=4,ALL=7 } Components;
      
    // resets the stopwatch
    //##ModelId=3DB954640302
    void reset ()
    { 
      tick = times(&tms); 
      last_tick = static_cast<clock_t>(tick + fire_secs/scale); 
    }

    //##ModelId=3DB954640304
    Stopwatch (double secs=0)
      : fire_secs(secs),namewidth(8)
    { reset(); }
      
    // returns elapsed time, and optionally resets stopwatch
    //##ModelId=3DB954640306
    Stopwatch delta (bool do_reset=true);
      
    // converts to formatted string (user/system/real time)
    // If nop is specified, also includes rate in ops/second
    //##ModelId=3DB954640308
    string toString (long long nops=0,int opts=ALL,const char *format="%10.3f") const;
      
    // returns elapsed time as a string, and optionally resets stopwatch
    //##ModelId=3DB95464030D
    string sdelta (long long nops=0,bool do_reset=true,int opts=ALL)
    { return delta(do_reset).toString(nops,opts); }
      
    // returns elapsed times in specific format
    //##ModelId=3DB954640311
    string sdelta (const char *format,bool do_reset,int opts=ALL)
    { return delta(do_reset).toString(0,opts,format); }
      
    // returns elapsed time as a string, and optionally resets stopwatch
    // value is preceded by name, formatted with namewidth characters
    //##ModelId=3DB954640315
    string dump (const string &name,long long nops=0,bool do_reset=true,int opts=ALL);
      
    // returns formatted headers for either of the two string forms
    //##ModelId=3DB95464031A
    static string header (long long nops=0);
      
    // gets/sets the name width
    //##ModelId=3DB95464031D
    int nameWidth () const      { return namewidth; }
    //##ModelId=3DB95464031F
    void setNameWidth (int x)   { namewidth = x; }
      
    // returns time components in seconds
    //##ModelId=3DB954640321
    double user () const    { return tms.tms_utime*scale; }
    //##ModelId=3DB954640323
    double sys  () const    { return tms.tms_stime*scale; }
    //##ModelId=3DB954640325
    double real () const    { return tick*scale; }
      
    // returns elapsed time in seconds
    //##ModelId=3DB954640327
    bool fired () const { return times(&dummy_tms) >= last_tick; };
  };

} // namespace LOFAR

#endif

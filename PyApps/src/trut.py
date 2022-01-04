#!/usr/bin/env python3

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import getopt
import sys

from Timba import Trut

if __name__ == '__main__':
  
  # strip off debug level options
  args = [ arg for arg in sys.argv[1:] if not arg.startswith('-d') ];
  # parse other options
  opts,files = getopt.getopt(args,"cv:p:l:j:h",["help"]);
  opts = dict(opts);
  
  if "-h" in opts or "--help" in opts or not files:
    print("""
    TRUT: Timba Reduction & Unit Testing
    
    Usage: trut [-jN] [-vN] [-lN] [-pN] [-c] [-dContext=level] [trutfiles...]
    
      -jN: run up to N tests in parallel (set to # of CPUs).
      -vN: set console verbosity level (default is 21 -- try increments of 10).
      -lN: set trut.log verbosity level (default is 41).
      -pN: set persistence level (default is 0). Use >0 to keep running when tests fail.
      -c:  rerun all tests, ignoring cached test results
      -dContext=level: enable debug messages from given Python context
      
    If no trutfiles are specified, all TRUT files in the current directory tree will be found & used.
   """);
    sys.exit(1);
  
  verbose = int(opts.get('-v',21));
  log     = int(opts.get('-l',41));
  persist = int(opts.get('-p',0));
  maxjobs = int(opts.get('-j',0));
  cache   = '-c' not in opts;
  
  if Trut.run_files(files,verbosity=verbose,log_verbosity=log,persist=persist,maxjobs=maxjobs,cache=cache):
    sys.exit(0);
  else:
    sys.exit(1);
  

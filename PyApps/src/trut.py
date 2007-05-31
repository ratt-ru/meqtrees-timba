#!/usr/bin/python

import getopt
import sys

from Timba import Trut

if __name__ == '__main__':
  
  # strip off debug level options
  args = [ arg for arg in sys.argv[1:] if not arg.startswith('-d') ];
  # parse other options
  opts,files = getopt.getopt(args,"v:p:l:j:h",["help"]);
  opts = dict(opts);
  
  if "-h" in opts or "--help" in opts or not files:
    print """
    TRUT: Timba Reduction & Unit Testing
    
    Usage: trut [-jN] [-vN] [-lN] [-pN] [-dContext=level] [trutfiles...]
    
      -jN: run up to N tests in parallel (set to # of CPUs).
      -vN: set console verbosity level (default is 21 -- try increments of 10).
      -lN: set trut.log verbosity level (default is 41).
      -pN: set persistence level (default is 0). Use >0 to keep running when tests fail.
      -dContext=level: enable debug messages from given Python context
      
    If no trutfiles are specified, all TRUT files in the current directory tree will be found & used.
   """;
    sys.exit(1);
  
  verbose = int(opts.get('-v',21));
  log     = int(opts.get('-l',41));
  persist = int(opts.get('-p',0));
  maxjobs = int(opts.get('-j',0));
  
  if Trut.run_files(files,verbosity=verbose,log_verbosity=log,persist=persist,maxjobs=maxjobs):
    sys.exit(0);
  else:
    sys.exit(1);
  

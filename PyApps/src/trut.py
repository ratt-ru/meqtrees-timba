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
    print "Usage: trut [-v<verbosity level>] [-p<persistence level>] [-l<loglevel] [-j<maxjobs>] trutfiles ...."
    sys.exit(1);
  
  verbose = int(opts.get('-v',21));
  log     = int(opts.get('-l',41));
  persist = int(opts.get('-p',0));
  maxjobs = int(opts.get('-j',0));
  
  if Trut.run_files(files,verbosity=verbose,log_verbosity=log,persist=persist,maxjobs=maxjobs):
    sys.exit(0);
  else:
    sys.exit(1);
  

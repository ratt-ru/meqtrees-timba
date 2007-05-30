#!/usr/bin/python

import getopt
import sys

from Timba import Trut

if __name__ == '__main__':
  
  # strip off debug level options
  args = [ arg for arg in sys.argv[1:] if not arg.startswith('-d') ];
  # parse other options
  opts,files = getopt.getopt(args,"v:p:d");
  opts = dict(opts);
  
  if not files:
    print "Usage: trut.py [-v<verbosity level>] [-p<persistence level>] [-l<loglevel] trutfiles ...."
    sys.exit(1);
  
  verbose = int(opts.get('-v',21));
  log     = int(opts.get('-l',40));
  persist = int(opts.get('-p',0));
  
  if Trut.run_files(files,verbosity=verbose,log_verbosity=log,persist=persist):
    sys.exit(0);
  else:
    sys.exit(1);
  

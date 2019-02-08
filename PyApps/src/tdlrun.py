#!/usr/bin/python

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

import sys
import os.path
import getopt
import inspect
import Timba.utils
from Timba import octopussy
from optparse import OptionParser


def main ():
  
  for optstr in (options.debug or []):
    opt = optstr.split("=") + ['1'];
    context,level = opt[:2];
    debuglevels[context] = int(level);
  Timba.utils.verbosity.disable_argv(); # tell verbosity class to not parse its argv
  for optstr in (options.verbose or []):
    opt = optstr.split("=") + ['1'];
    context,level = opt[:2];
    Timba.utils.verbosity.set_verbosity_level(context,level);

  if not args:
    parser.print_help();
    sys.exit(1);

  if debuglevels:
    octopussy.set_debug(debuglevels);

  script = args[0];
  tdljob = (len(args)>1 and args[1]) or None;
  
  from Timba.Apps import meqserver
  from Timba.TDL import Compile
  from Timba.TDL import TDLOptions
  
  # this starts a kernel. 
  if options.compile_only:
    mqs = None;
  else:
    mqs = meqserver.default_mqs(wait_init=10,extra=["-mt",options.mt]);
  
  TDLOptions.config.read(options.config);
  TDLOptions.init_options(script);
  
  print(("************************ Compiling TDL script",script));
  # this compiles a script as a TDL module. Any errors will be thrown as
  # and exception, so this always returns successfully
  (mod,ns,msg) = Compile.compile_file(mqs,script);
  
  if options.compile_only:
    print(msg);
    sys.exit(0);
  
  # if a solve job is not specified, try to find one
  if tdljob:
    jobfunc = getattr(mod,tdljob,None);
    if not jobfunc:
      print(("Cannot find TDL job named",tdljob));
      sys.exit(1);
  else:
    # does the script define an explicit job list?
    joblist = getattr(mod,'_tdl_job_list',[]);
    if not joblist:
      joblist = []; 
      # try to build it from implicit function names
      for (name,func) in list(mod.__dict__.items()):
        if name.startswith("_tdl_job_") and callable(func):
          joblist.append(func);
    # does the script define a testing function?
    testfunc = getattr(mod,'_test_forest',None);
    if testfunc:
      joblist.insert(0,testfunc);
    if not joblist:
      print(("No TDL jobs found in script",script));
      sys.exit(1);
    jobfunc = joblist[0];
    tdljob = jobfunc.__name__;
  
  # this runs the appropriate job. wait=True is needed to wait
  print(("************************ Running TDL job",tdljob));
  # check if job takes a "wait" argument
  (fargs,fvarargs,fvarkw,fdefaults) = inspect.getargspec(jobfunc);
  if 'wait' in fargs or fvarkw:
    jobopts = dict(wait=True);
  else:
    jobopts = {};
  jobfunc(mqs,None,**jobopts);

if __name__ == '__main__':
  debuglevels = {};
  
  # tell verbosity class to not parse argv -- we do it ourselves here
  Timba.utils.verbosity.disable_argv(); 
  # parse options is the first thing we should do
  usage="Usage: %prog [options] <TDLSCRIPT> [<TDLJOB>]";
  parser = OptionParser(usage=usage)
  parser.add_option("-m", "--mt",dest="mt",type="int",
                    default=1,
                    help="run meqserver with multiple threads (-mt option to meqserver)");
  parser.add_option("-c", "--config",dest="config",type="string",
                    default=".tdl.conf",
                    help="configuration file to use instead of .tdl.conf");
  parser.add_option("-C", "--compile-only",dest="compile_only",action="store_true",
                    help="compile script only, do not run");
  parser.add_option("-p", "--profile",dest="profile",metavar="FILE",type="string",default="",
                    help="run Python profiler, dump info to given file");
  parser.add_option("-d", "--debug",dest="debug",type="string",action="append",metavar="Context=Level",
                    help="(for debugging C++ code) sets debug level of the named C++ context. May be used multiple times.");
  parser.add_option("-v", "--verbose",dest="verbose",type="string",action="append",metavar="Context=Level",
                    help="(for debugging Python code) sets verbosity level of the named Python context. May be used multiple times.");
  (options,args) = parser.parse_args();
  
  if options.profile:
    import profile
    profile.run('main()',options.profile);
  else:
    main();


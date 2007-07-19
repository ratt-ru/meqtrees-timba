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

if __name__ == '__main__':
  
  optionlist,args = getopt.getopt(sys.argv[1:],'m:');

  if not args:
    print "Usage:",__file__," [-m num_threads] tdlscript [tdljob] [debug flags]";
    print "If TDL job is not specified, the first TDL job will be executed";
    sys.exit(1);

  script = args[0];
  args = [ x for x in args if not x.startswith("-") ];
  tdljob = (len(args)>1 and args[1]) or None;
  opts = dict(optionlist);
  num_threads = opts.get('-m','1');
  
  from Timba.Apps import meqserver
  from Timba.TDL import Compile
  from Timba.TDL import TDLOptions
  
  # this starts a kernel. 
  mqs = meqserver.default_mqs(wait_init=10,extra=["-mt",num_threads]);
  
  TDLOptions.config.read(".tdl.conf");
  TDLOptions.init_options(script);
  
  print "************************ Compiling TDL script",script;
  # this compiles a script as a TDL module. Any errors will be thrown as
  # and exception, so this always returns successfully
  (mod,ns,msg) = Compile.compile_file(mqs,script);
  
  # if a solve job is not specified, try to find one
  if tdljob:
    jobfunc = getattr(mod,tdljob,None);
    if not jobfunc:
      print "Cannot find TDL job named",tdljob;
      sys.exit(1);
  else:
    # does the script define an explicit job list?
    joblist = getattr(mod,'_tdl_job_list',[]);
    if not joblist:
      joblist = []; 
      # try to build it from implicit function names
      for (name,func) in mod.__dict__.iteritems():
        if name.startswith("_tdl_job_") and callable(func):
          joblist.append(func);
    # does the script define a testing function?
    testfunc = getattr(mod,'_test_forest',None);
    if testfunc:
      joblist.insert(0,testfunc);
    if not joblist:
      print "No TDL jobs found in script",script;
      sys.exit(1);
    jobfunc = joblist[0];
    tdljob = jobfunc.__name__;
  
  # this runs the appropriate job. wait=True is needed to wait
  print "************************ Running TDL job",tdljob;
  # check if job takes a "wait" argument
  (fargs,fvarargs,fvarkw,fdefaults) = inspect.getargspec(jobfunc);
  if 'wait' in fargs or fvarkw:
    jobopts = dict(wait=True);
  else:
    jobopts = {};
  jobfunc(mqs,None,**jobopts);


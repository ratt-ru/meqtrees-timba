#!/usr/bin/python

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


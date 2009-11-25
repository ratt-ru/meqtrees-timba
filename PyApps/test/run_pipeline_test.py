#!/usr/bin/python
#
# This shows how to run a TDL script in a pipeline (aka batch-mode, aka headless mode)
#
if __name__ == '__main__':
  from Timba.Apps import meqserver
  from Timba.TDL import Compile
  from Timba.TDL import TDLOptions

  # This starts a meqserver. Note how we pass the "-mt 2" option to run two threads.
  # A proper pipeline script may want to get the value of "-mt" from its own arguments (sys.argv).
  print "Starting meqserver";
  mqs = meqserver.default_mqs(wait_init=10,extra=["-mt","2"]);

  # Once we're connected to a server, some cleanup is required before we can exit the script.
  # Since we want to perform this cleanup regardless of whether the script ran to completion
  # or was interrupted by an exception midway through, we use a try...finally block.
  try:

    # This loads a config file.
    # A good starting point for a config file is .tdl.conf or meqtree.log in your current directory, make a copy
    # and start editing.
    # Note that a config file may contain multiple sections -- see below.
    print "Loading config";
    TDLOptions.config.read("pipeline.tdl.conf");

    # This compiles a script as a TDL module. Any errors will be thrown as an exception (and cause your script to stop).
    #
    # It is at this point that the config file loaded above takes effect. The default config section for
    # a script called /foo/bar.py is simply "[bar]", so in our case the default section is "[pipeline_test]".
    # TDL will automatically strip off the directory name and the .py suffix from the script filename to
    # obtain a section name. See below for examples of using non-default sections.
    #
    # compile_file() returns a tuple of three values, the first of which will be needed below.
    print "Compiling TDL script";
    script = "pipeline_test.py";
    mod,ns,msg = Compile.compile_file(mqs,script);

    # 'mod' now refers to a Python object that is the compiled module. To execute the _test_forest job within that
    # module, we do as follows:
    print "Running TDL job";
    mod._test_forest(mqs,None,wait=True);
    # The wait=True argument causes the thing to not return until the job has been completed.
    # None for the second argument tells it that we're running headless (without a GUI parent.)

    ### Now for some variations

    # This shows how to use a different section in the config file.
    print "Recompiling and running for test_a";
    mod,ns,msg = Compile.compile_file(mqs,script,config="test_a");
    # and this shows how to locate and call a "TDL Job" by its job ID
    TDLOptions.get_job_func('job1')(mqs,None,wait=True);

    print "Recompiling and running for test_b";
    mod,ns,msg = Compile.compile_file(mqs,script,config="test_b");
    # we can also find jobs by their long names
    TDLOptions.get_job_func('Run job 2')(mqs,None,wait=True);

    # finally, this is expected to fail
    print "Trying to call a non-existing TDL job 'job3'";
    try:
      TDLOptions.get_job_func('job3')(mqs,None,wait=True);
    except NameError:
      print "Indeed, 'job3' does not exist."

    # This shows how to change configuration on-the-fly.
    # TDLOptions.set_option() changes the value of a configuration variable "in memory".
    # Note that compile_file() normally rereads the config file, which would defeat the point of any
    # on-the-fly changes. To get around this, we can manage the config manually as follows:
    print "Recompiling and running for a=5, t=[-1,1]";
    # this loads initial config from section [test_b]. The save=False argument tells the system to not
    # write the changes we make below to the .tdl.conf file
    TDLOptions.init_options("test_b",save=False);
    # this makes some changes to the loaded config
    TDLOptions.set_option("a",5);
    TDLOptions.set_option("t0",-1);
    TDLOptions.set_option("t1",1);
    # this compiles the script. config=None tells it to NOT reload the config file, but to use whatever we have set up above.
    mod,ns,msg = Compile.compile_file(mqs,script,config=None);
    mod._test_forest(mqs,None,wait=True);

    # Make another change to the current config and recompile. Again config=None is necessary,
    TDLOptions.set_option("b",-5);
    mod,ns,msg = Compile.compile_file(mqs,script,config=None);
    mod._test_forest(mqs,None,wait=True);

    # Since "a" and "b" are compile-time options, we always need to recompile for them to take effect.
    # By contrast, runtime options ('t0' and 't1') can be changed without recompiling:
    print "Rerunning for t=[-5,5]";
    TDLOptions.set_option("t0",-5);
    TDLOptions.set_option("t1",5);
    mod._test_forest(mqs,None,wait=True);

    # and changed some more...
    print "Rerunning for t=[-10,10]";
    TDLOptions.set_option("t0",-10);
    TDLOptions.set_option("t1",10);
    TDLOptions.set_option("pipeline_test_constants.c0",10);
    mod._test_forest(mqs,None,wait=True);

  ### Cleanup time
  finally:
    print "Stopping meqserver";
    # this halts the meqserver
    meqserver.stop_default_mqs();
    # now we can exit
    print "Bye!";

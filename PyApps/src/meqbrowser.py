#!/usr/bin/python

import sys

# first things first: setup app defaults from here and from
# command line (this has to go first, as other modules being imported
# may depend on app_defaults settings)
import app_defaults

import qt_threading
import octopussy
import meqserver

#-------- update default debuglevels
app_defaults.debuglevels.update({
  'MeqNode'      :2,
  'MeqForest'    :2,
  'MeqSink'      :2,
  'MeqSpigot'    :2,
  'MeqVisHandler':2,
  'MeqServer'    :2,
  'meqserver'    :1  
});

#-------- update default arguments
app_defaults.args.update({'launch':None,'spawn':None,
                         'verbose':2,'wp_verbose':0 });

def meqbrowse (debug={},no_threads=False,**kwargs):
  app_defaults.parse_argv(sys.argv[1:]);
  args = app_defaults.args;
  
  # start octopussy if needed
  if not octopussy.is_initialized():
    octopussy.init(gw=True);
  if not octopussy.is_running():
    octopussy.start(wait=True);
  if debug is None:
    pass;
  else:
    octopussy.set_debug(app_defaults.debuglevels);
    if isinstance(debug,dict):
      octopussy.set_debug(debug);
  # start meqserver
  print args;
  args['gui'] = True;
  mqs = meqserver.meqserver(no_threads=no_threads,**args);

  mqs.run_gui();  
  mqs.disconnect();
  octopussy.stop();
  
if __name__ == '__main__':
  meqbrowse(no_threads=True);
  
#  thread = qt_threading.QThreadWrapper(meqbrowse);
#  print 'starting main thread:';
#  thread.start();
#  thread.join();
#  print 'main thread rejoined, exiting';


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

def _run_meqbrowse (debug={},**kwargs):
  # start meqserver, overriding default args with any kwargs
  args = app_defaults.args;
  args['gui'] = True;
  args.update(kwargs);
  print 'starting a meqserver with args:',args;
  mqs = meqserver.meqserver(**args);
  mqs.run_gui();

def meqbrowse (debug={},**kwargs):
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
  # start meqserver in thread
  thread = qt_threading.QThreadWrapper(_run_meqbrowse,args=(debug,),kwargs=kwargs);
  thread.start();
  thread.join();
  print "===== calling octopussy.stop() =====";
  octopussy.stop();
  
if __name__ == '__main__':
  meqbrowse();
  


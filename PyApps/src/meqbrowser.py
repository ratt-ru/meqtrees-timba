#!/usr/bin/python -O

if __name__ == "__main__":
  print "Welcome to the MeqTree Browser!";
  print "Please wait while the GUI starts up.";

import sys

# first things first: setup app defaults from here and from
# command line (this has to go first, as other modules being imported
# may depend on app_defaults settings)
from Timba.Apps import app_defaults
from Timba.Apps import config

config.init('meqbrowser');

from Timba import qt_threading
from Timba import octopussy
from Timba.Apps import meqserver

#from Timba.GUI import app_proxy_gui
#from Timba.GUI.pixmaps import pixmaps
#app_proxy_gui.set_splash_screen(pixmaps.trees_splash.pm,"Starting MeqTimba Brower");


def importPlugin (name):
  name = 'Timba.Plugins.'+name;
  try:
    __import__(name,globals(),locals(),[]);
  except Exception,what:
    print 'error importing',name,':',what;
    print 'This plugin will not be available.';
    
### import plug-ins
importPlugin('node_execute');
importPlugin('array_browser');
importPlugin('array_plotter');
importPlugin('histogram_plotter');
importPlugin('result_plotter');
importPlugin('collections_plotter');
importPlugin('history_plotter');
importPlugin('parm_plotter');
importPlugin('parmfiddler');
importPlugin('TableInspector');
importPlugin('stream_control');

#-------- update default debuglevels
app_defaults.debuglevels.update({
#  'MeqNode'      :2,
#  'MeqForest'    :2,
#  'MeqSink'      :2,
#  'MeqSpigot'    :2,
#  'MeqVisHandler':2,
#  'MeqServer'    :2,
#  'meqserver'    :1,
#  'gwclientwp'   :1,
#  'gwserverwp'   :1,
});

#-------- update default arguments
app_defaults.args.update({'launch':None,'spawn':None,'threads':True,
                         'verbose':2,'wp_verbose':0 });

def meqbrowse (debug={},**kwargs):
  app_defaults.parse_argv(sys.argv[1:]);
  args = app_defaults.args;
  print app_defaults.debuglevels;
  if debug is None:
    pass;
  else:
    octopussy.set_debug(app_defaults.debuglevels);
    if isinstance(debug,dict):
      octopussy.set_debug(debug);
  # start octopussy if needed
  if not octopussy.is_initialized():
    octopussy.init(gw=True);
  if not octopussy.is_running():
    octopussy.start(wait=True);
  # start meqserver
  args['gui'] = True;
  mqs = meqserver.meqserver(**args);

#   try:
#     import psyco
#     psyco.log('psyco.log');
#     psyco.profile();
#     print "****** psyco enabled.";
#   except:
#     print "****** You do not have the psyco package installed.";
#     print "****** Proceeding anyway, things will run some what slower.";
#     pass;
  
  mqs.run_gui();  
  mqs.disconnect();
  octopussy.stop();
  
if __name__ == '__main__':
  meqbrowse();
  
#  thread = qt_threading.QThreadWrapper(meqbrowse);
#  print 'starting main thread:';
#  thread.start();
#  thread.join();
#  print 'main thread rejoined, exiting';


# Default debug levels.
# these may be overwritten/added to by other modules.
# note that the "-debug" option sets a maximum that is applied here.
debuglevels = {};

# default arguments to app_proxy and derivatives
args = {
  'launch':True,'spawn':None,
  'verbose':0,'wp_verbose':0,
  'gui':False
};

# if this is false, then all gui definitions are omitted at startup, and
# a gui can't be enabled later (set via the "-nogui" option)
include_gui = True;

def parse_argv (argv):
  for arg in argv:
    if arg == "-spawn":
      (args['launch'],args['spawn']) = (None,True);
      
    elif arg == "-launch":
      (args['launch'],args['spawn']) = (True,None);
      
    elif arg == "-wait":
      (args['launch'],args['spawn']) = (None,None);
      
    elif arg == "-gui":
      args['gui'] = True;
      
    elif arg == "-nogui":
      global include_gui;
      include_gui = False;
      
    elif arg.startswith("-verbose="):     # -verbose=Level[,WPLevel]
      verb = arg.split('=',2)[1];
      verb = map(int,verb.split(',',2));
      if len(verb) == 1:
        verb = [verb,0];
      (args['verbose'],args['wp_verbose']) = verb;
      
    elif arg.startswith("-debug="):       # -debug=MaxDebug
      maxlev = int(arg.split('=',2)[1]);
      for k in debuglevels.keys():
        debuglevels[k] = min(debuglevels[k],maxlev);

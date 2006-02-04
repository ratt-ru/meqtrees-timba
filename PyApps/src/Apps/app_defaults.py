from Timba import dmi

import re
import sys

# Default debug levels.
# these may be overwritten/added to by other modules.
# note that the "-debug" option sets a maximum that is applied here.
debuglevels = {};

# default arguments to app_proxy and derivatives
args = dmi.record({
  'launch':False,'spawn':True,'opt':False,
  'verbose':0,'wp_verbose':0,
  'threads':True,
  'gui':False,
  'extra':(),
});

# if this is false, then all gui definitions are omitted at startup, and
# a gui can't be enabled later (set via the "-nogui" option)
include_gui = True;

def parse_argv (argv):
  dbgre = re.compile('-d(.+)=([0-9]+)');

  for i in range(len(argv)):
    arg = argv[i]
    
    if arg ==  "--":
      args.extra = argv[i+1:];
      return;
      
    elif arg == "-spawn":
      args.launch = None
      args.spawn = args.spawn or True;

    elif arg == "-nospawn":
      args.spawn = None;
      
    elif arg.startswith("-mqs="):     
      args.spawn = arg.split('=',2)[1];
      
    elif arg == "-launch":
      args.launch = True
      args.spawn = None;
      
    elif arg == "-wait":
      args.launch = args.spawn = None;
      
    elif arg == "-gui":
      args['gui'] = True;
      
    elif arg == "-opt":
      args['opt'] = True;
      
    elif arg == "-nothreads":
      args['threads'] = False;
      
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
    
    else:
      m = dbgre.match(arg);    
      if m:
        print 'will set debug level ',m.group(1),' to ',m.group(2);
        debuglevels[m.group(1)] = int(m.group(2));

parse_argv(sys.argv);

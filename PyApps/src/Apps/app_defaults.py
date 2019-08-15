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

from Timba import dmi

import re
import sys

# Default debug levels.
# these may be overwritten/added to by other modules.
# note that the "-debug" option sets a maximum that is applied here.
debuglevels = {};

# default arguments to app_proxy and derivatives
args = dmi.record({
  'spawn':True,'opt':False,
  'verbose':0,'wp_verbose':0,
  'threads':True,
  'gui':False,'checkrefs':False
});

# if this is false, then all gui definitions are omitted at startup, and
# a gui can't be enabled later (set via the "-nogui" option)
include_gui = True;
  

def parse_argv (argv):
  dbgre = re.compile('-d(.+)=([0-9]+)');
  # list of unparsed arguments
  remain = [];

  for i,arg in enumerate(argv):
    
    if arg ==  "--":
      args.extra = argv[i+1:];
      return remain;
      
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
      
    elif arg == "-checkrefs":
      args.checkrefs = True
      
    elif arg == "-wait":
      args.launch = args.spawn = None;
      
    elif arg == "-gui":
      args['gui'] = True;
      
    elif arg == "-opt":
      args['opt'] = True;
      
    elif arg == "-nothreads":
      print("Disabling threads as per user request")
      args['threads'] = False;
      
    elif arg == "-nogui":
      global include_gui;
      include_gui = False;
      
    elif arg.startswith("-verbose="):     # -verbose=Level[,WPLevel]
      verb = arg.split('=',2)[1];
      verb = list(map(int,verb.split(',',2)));
      if len(verb) == 1:
        verb = [verb,0];
      (args['verbose'],args['wp_verbose']) = verb;
      
    elif arg.startswith("-debug="):       # -debug=MaxDebug
      maxlev = int(arg.split('=',2)[1]);
      for k in list(debuglevels.keys()):
        debuglevels[k] = min(debuglevels[k],maxlev);
    
    else:
      m = dbgre.match(arg);    
      if m:
        print('will set debug level ',m.group(1),' to ',m.group(2));
        debuglevels[m.group(1)] = int(m.group(2));
      else:
        remain.append(arg);
        
  return remain;

# parse_argv(sys.argv);

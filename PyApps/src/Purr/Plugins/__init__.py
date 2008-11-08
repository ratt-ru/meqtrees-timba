import sys
import os
import time
import os.path
import re
import sets
import fnmatch
import imp
import traceback

import Purr
import Purr.Render
from Purr import dprint,dprintf

def loadPlugins (paths):
  global bad_plugins;
  bad_plugins = {};
  # find potential plugin files
  modfiles = sets.Set();
  for path in paths:
    files = sets.Set(fnmatch.filter(os.listdir(path),"*.py"));
    files.discard('__init__.py');
    modfiles.update([ os.path.join(path,file) for file in files ]);
  dprintf(1,"%d plugins found\n",len(modfiles));
  # try to import them
  for fullpath in modfiles:
    modfile = os.path.basename(fullpath);
    modname,ext = os.path.splitext(modfile);
    # try to find the module via the imp mechanism
    try:
      fp,pathname,desc = imp.find_module(modname,paths);
    except:
      err = sys.exc_info()[1];
      dprintf(1,"Error finding module for plugin %s: %s\n",fullpath,err);
      bad_plugins[modname] = err;
      continue;
    # try to import the module
 #   setattr(modname,"plugin_mtime",os.path.getmtime(pathname));
    try:
      try:
        imp.acquire_lock();
        module = imp.load_module('Purr.Plugins.%s'%modname,fp,pathname,desc);
      finally:
        imp.release_lock();
        if fp:
          fp.close();
    except:
      err = sys.exc_info()[1];
      dprintf(1,"Error importing module %s: %s\n",pathname,err);
      bad_plugins[modname] = err;
      continue;
    # ok, we have a module, check for vital properties
    dprintf(1,"Imported plugin module '%s' from %s\n",modname,pathname);
  dprintf(1,"%d renderers now available\n",Purr.Render.numRenderers());
  
  
# this collects a list of plugins that have failed to load
bad_plugins = None;

if bad_plugins is None:
  loadPlugins(__path__);

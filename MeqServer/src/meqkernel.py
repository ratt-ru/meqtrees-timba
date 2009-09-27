#!/usr/bin/python
# -*- coding: utf-8 -*-
# standard python interface module for meqserver

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
import traceback
import os.path

# this ensures that C++ symbols (RTTI, DMI registries, etc.) are
# shared across dynamically-loaded modules

try:
  import dl
except:
  import DLFCN
  dl = DLFCN

sys.setdlopenflags(dl.RTLD_NOW | dl.RTLD_GLOBAL);

# sys.argv is not present when embedding a Python interpreter, but some
# packages (i.e. numarray) seem to fall over when it is not found. So we
# inject it
if not hasattr(sys,'argv'):
  setattr(sys,'argv',['meqkernel']);

# now import the rest
from Timba import dmi
from Timba import utils
import meqserver_interface
import sys
import imp
import os.path


_dbg = utils.verbosity(0,name='meqkernel');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

_header_handlers = [];
_footer_handlers = [];

def reset ():
  global _header_handlers;
  global _footer_handlers;
  _header_handlers = [];
  _footer_handlers = [];
  
# helper function to set node state  
def set_state (node,**fields):
  """helper function to set the state of a node specified by name or
  nodeindex""";
  rec = dmi.record(state=dmi.record(fields));
  if isinstance(node,str):
    rec.name = node;
  elif isinstance(node,int):
    rec.nodeindex = node;
  else:
    raise TypeError,'illegal node argumnent';
  # pass command to kernel
  meqserver_interface.mqexec('Node.Set.State',rec,True); # True=silent
  
  
def process_vis_header (header):
  global _header_handlers;
  _dprint(0,"calling",len(_header_handlers),"header handlers");
  for handler in _header_handlers:
    handler(header);


def process_vis_footer (footer):
  """standard method called whenever a vis-footer is received.
  Comment out to disable.
  """
  global _footer_handlers;
  _dprint(0,"calling",len(_footer_handlers),"footer handlers");
  for handler in _footer_handlers:
    handler(footer);

_imported_modules = {};
_imported_scripts = {};
_import_counter = 0;

def force_module_reload ():
  """Increments the import counter, which will force the
  _import_script_or_module function below to reload its modules.
  Normally this should be called before starting to build a forest,
  so that any changes in Python code (for PyNodes, etc.) are reloaded.
  """;
  global _import_counter;
  _dprint(0,"forcing future reload of Python modules");
  _import_counter += 1;

def _import_script_or_module (script,modname=None,force_reload=False):
  """Imports the specified script or module. 
  If 'script' ends with .py, treats it as a filename and looks through
  various include paths (and the current directory). Otherwise, treats
  it as a module name.
  If module is already imported, it will only be reloaded if force_reload
  is True, or force_module_reload() has been called since it was imported.
  Return value is imported module object.
  """
  global _imported_modules;
  global _imported_scripts;
  global _import_counter;
  # replace ".py[oc]" with ".py"
  if script.endswith(".pyo") or script.endswith(".pyc"):
    script = script[0:-1];
  # if a filename with a known suffix is supplied, try to import as file
  for suffix,mode,filetype in imp.get_suffixes():
    if script.endswith(suffix):
      # expand "~" and "$VAR" in filename
      script = filename = os.path.expandvars(os.path.expanduser(script));
      # now, if script is a relative pathname (doesn't start with '/'), try to 
      # find it in various paths
      if not os.path.isabs(script):
        for dd in ["./"] + sys.path:
          filename = os.path.join(dd,script);
          if os.path.isfile(filename):
            break;
        else:
          raise ValueError,"script not found anywhere in path: "+script;
      # open the script file
      infile = file(filename,'r');
      # now import the script as a module
      if modname is None:
        modname = filename.replace("/","_").replace(".","_");
      _dprint(0,"importing ",modname," from script",filename);
      # add directory of script to path, so that relative import statements within the script work
      oldpath = list(sys.path);
      sys.path.insert(0,os.path.dirname(filename));
      try:
	# check if script is already imported  
	module = None;
	if force_reload:
	  _dprint(0,"force_reload=True,",modname,"will be reloaded");
	elif filename in _imported_scripts:
	  module,count = _imported_scripts[filename];
	  if count == _import_counter:
	    _dprint(0,modname,"already imported, will not be reloaded");
	  else:
	    _dprint(0,modname,"already imported but is stale, will be reloaded");
	    module = None;
	else:
	  _dprint(0,modname,"hasn't been imported yet");
	if module is None:
	  try:
	    imp.acquire_lock();
	    module = imp.load_source(modname,filename,infile);
	    _imported_scripts[filename] = (module,_import_counter);
	  finally:
	    imp.release_lock();
	    infile.close();
      finally:
	sys.path = oldpath;
      break;
  # else (no known suffix found) treat as module name
  else:
    _dprint(0,"importing module",script);
    module = __import__(script);
    # since __import__ returns the top-level package, use this
    # code from the Python docs to get to the ultimate module
    components = script.split('.')
    for comp in components[1:]:
      module = getattr(module,comp);
    # see if module needs to be reloaded (we don't have to do it when
    # using load_source(), as that does an implicit reload).
    if module in _imported_modules:
      if not force_reload and _imported_modules[module] == _import_counter:
        _dprint(0,"module already imported, reusing");
      else:
        _dprint(0,"module already imported but stale (or force_reload=True), reloading");
        reload(module);
    else:
      _dprint(0,"this is the first time it has been imported");
  # add to dict of imported modules
  _imported_modules[module] = _import_counter;
  return module;

_initmod = None;

# sets the verbosity level
def set_verbose (level):
  _dbg.set_verbose(level);

def process_init (rec):
  # reset internals
  reset();
  # do we have an init-script in the header?
  _dprint(0,rec);
  try: script = rec.python_init;
  except AttributeError:
    _dprint(0,"no init-script specified, ignoring");
    return;
  try:
    global _initmod;
    # import specified file or module
    _initmod = _import_script_or_module(script,force_reload=True);
  except: # catch-all for any errors during import
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'importing init-module',script);
    traceback.print_exc();
    raise;
  # add standard names from script, if found
  global _header_handlers;
  global _footer_handlers;
  for nm,lst in (('process_vis_header',_header_handlers),('process_vis_footer',_footer_handlers)):
    handler = getattr(_initmod,nm,None);
    _dprint(0,'found handler',nm,'in script');
    if handler:
      lst.append(handler);
  return None;


def create_pynode (node_baton,node_name,class_name,module_name):
  """This creates a "pynode" instance of the given class residing
  in the given module, and associates it with the given node_baton
  object. The baton can be used later to obtain node state, etc.
  Note that class may be specified as "package.module.class", in which
  case the module_name argument should be empty.
  """
  _dprint(0,"creating pynode of class",class_name,"module",module_name);
  # if module is empty, it had better be included in the class name, using
  # the '.' notation
  if not module_name:
    components = class_name.split('.');
    if len(components) < 2:
      raise ValueError,"create_pynode: if module is not specified separately, class name must have form 'module.class'";
    class_name = components[-1];
    module_name = '.'.join(components[0:-1]);
  # now, import the module
  try:
    module = _import_script_or_module(module_name);
  except: # catch-all for any errors during import
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'importing module',module_name);
    traceback.print_exc();
    raise;
  # get the class
  class_obj = getattr(module,class_name,None);
  if class_obj is None:
    raise ValueError,"create_pynode: class "+class_name+" not found in "+module_name;
  # create and return pynode object
  return class_obj(node_name,node_baton);

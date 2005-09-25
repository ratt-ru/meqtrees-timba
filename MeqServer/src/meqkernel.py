#!/usr/bin/python

# standard python interface module for meqserver
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
  meqserver_interface.mqexec('Node.Set.State',rec);
  
  
def process_vis_header (header):
  for handler in _header_handlers:
    handler(header);


def process_vis_footer (footer):
  """standard method called whenever a vis-footer is received.
  Comment out to disable.
  """
  for handler in _footer_handlers:
    handler(footer);

# def process_vis_tile (tile):
#   """standard method called whenever a tile is received.
#   Comment out to disable. Since tiles currently have no Python representation,
#   this method is useless.
#   """
#   pass;

_initmod = None;

# sets the verbosity level
def set_verbose (level):
  _dbg.set_verbose(level);

def process_init (rec):
  # reset internals
  reset();
  # do we have an init-script in the header?
  try: script = rec.input.python_init;
  except AttributeError:
    _dprint(0,"no init-script specified, ignoring");
    return;
  try:
    # expand "~" and "$VAR" in filename
    script = filename = os.path.expandvars(os.path.expanduser(script));
    # now, if script is a relative pathname (doesn't start with '/'), try to find it in
    # various paths
    if not os.path.isabs(script):
      for dd in ["./"] + sys.path:
        filename = os.path.join(dd,script);
        if os.path.isfile(filename):
          break;
      else:
        raise ValueError,"script not found anywhere in path: "+script;
    _dprint(0,"opening init-script",filename);
    # open the script file
    infile = file(filename,'r');
    # now import the script as a module
    global _initmod;
    modname = '__initscript';
    try:
      imp.acquire_lock();
      _initmod = imp.load_module(modname,infile,filename,('.py','r',imp.PY_SOURCE));
    finally:
      imp.release_lock();
      infile.close();
    # add standard names from script, if found
    global _header_handlers;
    global _footer_handlers;
    for nm,lst in (('process_vis_header',_header_handlers),('process_vis_footer',_footer_handlers)):
      handler = getattr(_initmod,nm,None);
      _dprint(0,'found handler',nm,'in script');
      if handler:
        lst.append(handler);
    return None;
  except: # catch-all for any errors during import
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'importing init-module',filename);
    raise;

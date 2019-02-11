# -*- coding: utf-8 -*-
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

import Timba
from Timba.dmi import *
from Timba.utils import *
from Timba import TDL
from Timba.Meq import meqds
import Timba.TDL.Settings
from Timba.TDL import TDLOptions

import imp
import sys
import re
import traceback
import os
import os.path
import inspect

_dbg = verbosity(0,name='tdlc');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# this holds a list or set of all modules imported from TDL scripts
_tdlmodlist = [];
# this hold the set of all modules imported before a script is compiled
_prior_compile_modules = set();
# this is the currently imported filename
_current_filename = None;


def _update_modlist ():
  """updates the list of modules imported since _prior_compile_modules
  was set up. Stores this in _tdlmodlist""";
  global _tdlmodlist;
  global _prior_compile_modules;
  _tdlmodlist = set(sys.modules.keys()) - _prior_compile_modules;
  modlist = list(_tdlmodlist);
  modlist.sort();
  _dprint(1,'TDL run imported',len(_tdlmodlist),"modules:",modlist);
  _tdlmodlist = set([name for name in _tdlmodlist
                          if name != "six" and not name.startswith("six.") 
                             and not getattr(sys.modules[name],'_tdl_no_reimport',False)]);
  modlist = list(_tdlmodlist);
  modlist.sort();
  _dprint(1,'of which',len(_tdlmodlist),"modules are re-importable:",modlist);

# this is information about ourselves
_MODULE_FILENAME = Timba.utils.extract_stack()[-1][0];
_MODULE_DIRNAME = os.path.dirname(_MODULE_FILENAME);


def last_imported_file ():
  global _current_filename;
  return _current_filename;

class CompileError (RuntimeError):
  def __init__ (self,*errlist):
    self.errlist = errlist;

def import_tdl_module (filename,text=None,config=0):
  """Imports a TDL module.
  Parameters:
    filename: script location
    text: text of module. If none, file will be re-read.

  Return value:
    a tuple of (module,text), where module is the newly-imported
    TDL module, and text is the module text.

  Exceptions thrown:
    Any import error results in an exception. This is always
    a TDL.CumulativeError exception containing an error list.
    Other exceptions may indicate an internal failure.
  """;
  _dprint(1,"importing",filename);
  global _current_filename;
  _current_filename = filename;
  # initialize global nodescope (and repository)
  meqds.clear_forest();
  try:
    reload(Timba.TDL.Settings);
    # reset TDL script options, unless config=None ('0' is used as default, causing the filename to be substituted)
    TDLOptions.init_script(filename);
    if config is not None:
      TDLOptions.init_options(config or filename);
    # remove .pyo file as that can have cached paths and directories may have changed
    # (see bug 677)
    try:
      os.unlink(os.path.splitext(filename)[0]+'.pyo');
    except:
      pass;
    # open file
    infile = open(filename,'r');
    if text is None:
      text = infile.read();
      infile.seek(0);
    # infile is now an open input file object, and text is the script

    # flush all modules imported via previous TDL run
    global _tdlmodlist;
    _dprint(1,'clearing out TDL-imported modules',_tdlmodlist);
    for m in _tdlmodlist:
      try: del sys.modules[m];
      except KeyError: pass;
    # remember which modules are imported
    global _prior_compile_modules;
    _prior_compile_modules = set(sys.modules.keys());
    modname = '__tdlruntime';
    try:
      TDLOptions.enable_save_config(False);
      imp.acquire_lock();
      _tdlmod = imp.load_source(modname,filename,infile);
    finally:
      TDLOptions.enable_save_config(True);
      TDLOptions.save_config();
      imp.release_lock();
      infile.close();
      _update_modlist();
    return (_tdlmod,text);

  # CumulativeError exceptions returned as is
  except TDL.CumulativeError:
    _dprint(0,'cumulative error importing TDL file:',filename);
    traceback.print_exc();
    args = sys.exc_info()[1].args;
    _dprint(0,'number of errors in list:',len(args));
    _dprint(1,'errors are: {',args,'}');
    raise;
  # Other exceptions wrapped in a CumulativeError, and
  # location information is added in
  except:
    (etype,exc,tb) = sys.exc_info();
    _dprint(0,'exception importing TDL file:',filename);
    traceback.print_exception(etype,exc,tb);
    # use TDL add_error() to process the error, since this automatically
    # adds location information
    ns = TDL.NodeScope();
    ns.AddError(exc,traceback.extract_tb(tb),error_limit=None);
    # re-raise as a CumulativeError
    raise TDL.CumulativeError(*ns.GetErrors());

def run_forest_definition (mqs,filename,tdlmod,text,
                           parent=None,wait=True,
                           predef_args={},define_args={},postdef_args={}):
  """Compiles a TDL script and sends it to meqserver given by mqs.
  Parameters:
    mqs:      a meqserver object (None to run without a meqserver)
    filename: the filename of the script (used for error reporting)
    tdlmod:   the imported TDL module, as returned by import_tdl_module()
    text:     script text for putting into forest
    parent:   parent widget passed to TDL script (if a GUI is running)
    wait:     if True, waits for forest to build before returning
    predef_args: dict of extra arguments for _tdl_predefine()
    define_args: dict of extra arguments for _define_forest()
    postdef_args: dict of extra arguments for _tdl_postdefine()

  Return value:
    a tuple of (module,ns,message), where module is the newly-imported
    TDL module, ns is a NodeScope object, and message is an
    informational message.

  Exceptions thrown:
    Any compilation error results in an exception. This is always
    a TDL.CumulativeError exception containing an error list.
    Other exceptions may indicate an internal failure.
  """;
  _dprint(1,"defining forest");
  try:
    TDLOptions.enable_save_config(False);
    ns = TDL.NodeScope();
    # module here, call functions
    errlist = [];
    # find define_forest func
    define_func = getattr(tdlmod,'_define_forest',None);
    if not callable(define_func):
      raise TDL.TDLError("No _define_forest() function found",filename=filename,lineno=1);
    # now find predefine function and call it
    predefine_func = getattr(tdlmod,'_tdl_predefine',None);
    if callable(predefine_func):
      predef_result = predefine_func(mqs,parent,**predef_args);
      _update_modlist();
    else:
      predef_result = None;
    # inspect the define function to support older scripts that only
    # defined a define_forest(ns), i.e., with a single argument
    (fargs,fvarargs,fvarkw,fdefaults) = inspect.getargspec(define_func);
    if not fargs:
      raise TDL.TDLError("invalid _define_forest() function: must have at least a single argument ('ns')",filename=filename,lineno=1);
    # function must have either a single argument, or allow keyword arguments
    if len(fargs) > 1 and not fvarkw:
      raise TDL.TDLError("invalid _define_forest() function: must have a **kwargs parameter",filename=filename,lineno=1);
    # if no support for keyword arguments, pass an empty dict, else use valid dict
    if fvarkw:
      args = define_args.copy();
      args['parent'] = parent;
      if isinstance(predef_result,dict):
        args.update(predef_result);
    else:
      args = {};
    # call the define function
    define_func(ns,**args);
    _update_modlist();
    # resolve the nodescope
    ns.Resolve();
    # do we have an error list? show it
    errlist = ns.GetErrors();
    if errlist:
      raise TDL.CumulativeError(*errlist);
    allnodes = ns.AllNodes();
    num_nodes = len(allnodes);
    # no nodes? return
    if not num_nodes:
      return (tdlmod,ns,"TDL script successfully compiled, but no nodes were defined.");
    # try to run stuff
    if mqs is not None:
      meqds.clear_forest();
      # is a forest state defined? send it on then
      fst = getattr(Timba.TDL.Settings,'forest_state',record());
      # add in source code
      fst.tdl_source = record(**{os.path.basename(filename):text});
      mqs.meq('Set.Forest.State',record(state=fst,get_forest_status=0));
      if num_nodes:
        mqs.meq('Create.Node.Batch',
            record(script_name=os.path.basename(filename),
            batch=[nr.initrec() for nr in iter(allnodes.values())]));
#        mqs.meq('Init.Node.Batch',record(name=list(ns.RootNodes().iterkeys())),wait=wait);
        msg = """TDL script successfully compiled. %d node definitions
  (of which %d are root nodes) sent to meqserver.""" \
          % (num_nodes,len(ns.RootNodes()));
      else:
        msg = "TDL script successfully compiled, but no nodes were defined.";
    else:
      msg = "TDL script successfully compiled, %d nodes were defined."%num_nodes;

    # call the post-define function
    postdefine_func = getattr(tdlmod,'_tdl_postdefine',None);
    if callable(postdefine_func):
      res = postdefine_func(mqs,parent,**postdef_args);
      _update_modlist();
      if isinstance(res,str):
        msg += "\n" + res;

    TDLOptions.enable_save_config(True);
    TDLOptions.save_config();
    return (tdlmod,ns,msg);
  # CumulativeError exceptions returned as is
  except TDL.CumulativeError:
    _update_modlist();
    TDLOptions.enable_save_config(True);
    TDLOptions.save_config();
    _dprint(0,'cumulative error compiling TDL script:',filename);
    traceback.print_exc();
    args = sys.exc_info()[1].args;
    _dprint(0,'number of errors in list:',len(args));
    _dprint(1,'errors are: {',args,'}');
    raise;
  # Other exceptions wrapped in a CumulativeError, and
  # location information is added in
  except:
    _update_modlist();
    TDLOptions.enable_save_config(True);
    TDLOptions.save_config();
    (etype,exc,tb) = sys.exc_info();
    _dprint(0,'exception defining forest from TDL file:',filename);
    traceback.print_exception(etype,exc,tb);
    # use TDL add_error() to process the error, since this automatically
    # adds location information
    ns.AddError(exc,traceback.extract_tb(tb),error_limit=None);
    # re-raise as a CumulativeError
    raise TDL.CumulativeError(*ns.GetErrors());



def compile_file (mqs,filename,text=None,parent=None,wait=True,config=0,
                  predef_args={},define_args={},postdef_args={}):
  """imports TDL module and runs forest definition.
  Basically a compound of the above two functions.""";
  (tdlmod,text) = import_tdl_module(filename,text=text,config=config);
  return run_forest_definition(mqs,filename,tdlmod,text,wait=wait,
                  predef_args=predef_args,define_args=define_args,postdef_args=postdef_args);



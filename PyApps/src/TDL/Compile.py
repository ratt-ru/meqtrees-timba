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
import sets
import os
import os.path
import inspect

_dbg = verbosity(0,name='tdlc');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# this holds a list of all modules imported from TDL scripts
_tdlmodlist = [];

# this is information about ourselves
_MODULE_FILENAME = Timba.utils.extract_stack()[-1][0];
_MODULE_DIRNAME = os.path.dirname(_MODULE_FILENAME);

class CompileError (RuntimeError):
  def __init__ (self,*errlist):
    self.errlist = errlist;

def import_tdl_module (filename,text=None):
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
  # initialize global nodescope (and repository)
  try:
    reload(Timba.TDL.Settings);
    # reset TDL script options
    TDLOptions.init_options(filename);
    # open file
    infile = file(filename,'r');
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
    prior_mods = sets.Set(sys.modules.keys());
    modname = '__tdlruntime';
    try:
      imp.acquire_lock();
      _tdlmod = imp.load_source(modname,filename,infile);
    finally:
      imp.release_lock();
      infile.close();
      _tdlmodlist = sets.Set(sys.modules.keys()) - prior_mods;
      _dprint(1,'TDL run imported',_tdlmodlist);
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
                           parent=None,
                           predef_args={},define_args={},postdef_args={}):
  """Compiles a TDL script and sends it to meqserver given by mqs.
  Parameters:
    mqs:      a meqserver object
    filename: the filename of the script (used for error reporting)
    tdlmod:   the imported TDL module, as returned by import_tdl_module()
    text:     script text for putting into forest
    parent:   parent widget passed to TDL script (if a GUI is running)
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
      return (tdlmod,ns,"Script has run successfully, but no nodes were defined.");
    # try to run stuff
    meqds.clear_forest();
    # is a forest state defined? send it on then
    fst = getattr(Timba.TDL.Settings,'forest_state',record());
    # add in source code
    fst.tdl_source = record(**{os.path.basename(filename):text});
    mqs.meq('Set.Forest.State',record(state=fst,get_forest_status=0));
    if num_nodes:
      mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),allnodes.itervalues())));
      mqs.meq('Init.Node.Batch',record(name=list(ns.RootNodes().iterkeys())));
      msg = """Script has run successfully. %d node definitions 
(of which %d are root nodes) sent to the kernel.""" \
        % (num_nodes,len(ns.RootNodes()));
    else:  
      msg = "Script has run successfully, but no nodes were defined.";    
    ## do not request frest state here, let the GUI do it for us
    ## this ensures that bookmarks show up only after all nodes are available
    # mqs.meq('Get.Forest.State',record(sync=2));
    
    # call the post-define function
    postdefine_func = getattr(tdlmod,'_tdl_postdefine',None);
    if callable(postdefine_func):
      res = postdefine_func(mqs,parent,**postdef_args);
      if isinstance(res,str):
        msg += "\n" + res;

    return (tdlmod,ns,msg);
  # CumulativeError exceptions returned as is  
  except TDL.CumulativeError:
    _dprint(0,'cumulative error defining forest from TDL file:',filename);
    traceback.print_exc();
    args = sys.exc_info()[1].args;
    _dprint(0,'number of errors in list:',len(args));
    _dprint(1,'errors are: {',args,'}');
    raise;
  # Other exceptions wrapped in a CumulativeError, and
  # location information is added in
  except:
    (etype,exc,tb) = sys.exc_info();
    _dprint(0,'exception defining forest from TDL file:',filename);
    traceback.print_exception(etype,exc,tb);
    # use TDL add_error() to process the error, since this automatically
    # adds location information
    ns.AddError(exc,traceback.extract_tb(tb),error_limit=None);
    # re-raise as a CumulativeError
    raise TDL.CumulativeError(*ns.GetErrors());
    
    
def compile_file (mqs,filename,text=None,parent=None,
                  predef_args={},define_args={},postdef_args={}):
  """imports TDL module and runs forest definition.
  Basically a compound of the above two functions.""";
  (tdlmod,text) = import_tdl_module(filename,text=text);
  return run_forest_definition(mqs,filename,tdlmod,text,
                  predef_args=predef_args,define_args=define_args,postdef_args=postdef_args);



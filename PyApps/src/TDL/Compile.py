from Timba.dmi import *
from Timba.utils import *
from Timba import TDL
from Timba.Meq import meqds
import Timba.TDL.Settings

import imp
import sys
import re
import traceback
import sets
import os
import os.path

_dbg = verbosity(0,name='tdlc');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# this holds a list of all modules imported from TDL scripts
_tdlmodlist = [];

# this is information about ourselves
_MODULE_FILENAME = traceback.extract_stack()[-1][0];
_MODULE_DIRNAME = os.path.dirname(_MODULE_FILENAME);

class CompileError (RuntimeError):
  def __init__ (self,*errlist):
    self.errlist = errlist;

def compile_file (mqs,filename,text=None,parent=None,
                  predef_args={},define_args={},postdef_args={}):
  """Compiles a TDL script and sends it to meqserver given by mqs.
  Parameters:
    mqs:      a meqserver object
    filename: script location
    text:     script text for putting into forest (if None, will be read from file)
    parent:   parent widget passed to TDL script (if a GUI is running)
    predef_args: dict of extra arguments for _tdl_predefine()
    define_args: dict of extra arguments for _define_forest()
    postdef_args: dict of extra arguments for _tdl_postdefine()
    busy_callback: this function is called whenever the compiler gets busy.
              Normal use is to set an hourglass cursor in GUIs.
    free_callback: this function is called whenever the compiler is no longer busy.
              Normal use is to restore normal cursor in GUIs.
              
          
  Return value:
    a tuple of (module,ns,message), where module is the newly-imported 
    TDL module, ns is the global NodeScope object, and message is an 
    informational message.
  Exceptions thrown:
    Any compilation error results in an exception. This is either a 
    TDL.CumulativeError containing an error list, or a regular exception
  """;
  _dprint(1,"compiling",filename);
  reload(Timba.TDL.Settings);
  # initialize global nodescope (and repository)
  ns = TDL.NodeScope();
  try:
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
    
    # module here, call functions
    errlist = [];
    # find define_forest func
    define_func = getattr(_tdlmod,'_define_forest',None);
    if not callable(define_func):
      raise TDL.TDLError("No _define_forest() function found",filename=filename,lineno=1);
    # now find predefine function and call it
    predefine_func = getattr(_tdlmod,'_tdl_predefine',None);
    if callable(predefine_func):
      predef_result = predefine_func(mqs,parent,**predef_args);
    else:
      predef_result = None;
    # call the define function
    args = define_args.copy();
    if isinstance(predef_result,dict):
      args.update(predef_result);
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
      return (_tdlmod,ns,"Script has run successfully, but no nodes were defined.");
    # try to run stuff
    meqds.clear_forest();
    mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),allnodes.itervalues())));
    mqs.meq('Init.Node.Batch',record(name=list(ns.RootNodes().iterkeys())));

    # is a forest state defined?
    fst = getattr(Timba.TDL.Settings,'forest_state',record());
    # add in source code
    fst.tdl_source = record(**{os.path.basename(filename):text});
    mqs.meq('Set.Forest.State',record(state=fst));

    msg = """Script has run successfully. %d node definitions 
(of which %d are root nodes) sent to the kernel.""" \
      % (num_nodes,len(ns.RootNodes()));
    
    # call the post-define function
    postdefine_func = getattr(_tdlmod,'_tdl_postdefine',None);
    if callable(postdefine_func):
      res = postdefine_func(mqs,parent,**postdef_args);
      if isinstance(res,str):
        msg += "\n" + res;

    return (_tdlmod,ns,msg);
  # CumulativeError exceptions returned as is  
  except TDL.CumulativeError:
    _dprint(0,'cumulative error compiling TDL file:',filename);
    traceback.print_exc();
    args = sys.exc_info()[1].args;
    _dprint(0,'number of errors in list:',len(args));
    _dprint(1,'errors are: {',args,'}');
    raise;
  # Other exceptions wrapped in a CumulativeError, and
  # location information is added in
  except:
    (etype,exc,tb) = sys.exc_info();
    _dprint(0,'exception compiling TDL file:',filename);
    traceback.print_exception(etype,exc,tb);
    # use TDL add_error() to process the error, since this automatically
    # adds location information
    ns.AddError(exc,traceback.extract_tb(tb),error_limit=None);
    # re-raise as a CumulativeError
    raise TDL.CumulativeError(*ns.GetErrors());
    
#     # create new error object, with type: args message
#     try:
#       args = str(exc.args[0]);
#       err = etype("%s: %s"%(etype.__name__,args));
#     except AttributeError:
#       err = etype(etype.__name__);
#     # figure out where it was raised
#     tb = traceback.extract_tb(tb);
#     internal = ( os.path.dirname(tb[-1][0]) == _MODULE_DIRNAME );
#     # get location info from original exception
#     filename = getattr(exc,'filename',None);
#     lineno   = getattr(exc,'lineno',None);
#     offset   = getattr(exc,'offset',0) or 0;
#     # if not provided, get from traceback
#     _dprint(0,'file',filename,'exception is internal:',internal);
#     if filename is None and not internal:
#       filename = tb and tb[-1][-0];
#       lineno = tb[-1][1];
#       offset = 0;
#     # put into error object
#     setattr(err,'filename',filename);
#     setattr(err,'lineno',lineno);
#     setattr(err,'offset',offset);
#     raise TDL.CumulativeError(err);

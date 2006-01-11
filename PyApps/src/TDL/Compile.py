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


class CompileError (RuntimeError):
  def __init__ (self,*errlist):
    self.errlist = errlist;

def compile_file (mqs,filename,text=None):
  """Compiles a TDL script and sends to meqserver given by mqs.
  Parameters:
    mqs:      a meqserver object
    filename: script location
    text:     script text for putting into forest (if None, will be read from file)
  Return value:
    a tuple of (module,message), where module is the newly-imported TDL module,
    and message is an informational message.
  Exceptions thrown:
    Any compilation error results in an esception. This is either a 
    CompileError containing an error list, or a standard python exception.
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
      raise CompileError(TDL.TDLError("No _define_forest() function found",filename=filename,lineno=1));
    define_func(ns);
    ns.Resolve();
    # do we have an error list? show it
    errlist = ns.GetErrors();
    if errlist:
      raise CompileError(*errlist);
    allnodes = ns.AllNodes();
    num_nodes = len(allnodes);
    # no nodes? return
    if not num_nodes:
      return (_tdlmod,"Script has run successfully, but no nodes were defined.");
    # try to run stuff
    meqds.clear_forest();
    mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),allnodes.itervalues())));
    mqs.meq('Resolve.Batch',record(name=list(ns.RootNodes().iterkeys())));

    # is a forest state defined?
    fst = getattr(Timba.TDL.Settings,'forest_state',record());
    # add in source code
    fst.tdl_source = record(**{os.path.basename(filename):text});
    mqs.meq('Set.Forest.State',record(state=fst));

    msg = """Script has run successfully. %d node definitions 
      (of which %d are root nodes) sent to the kernel.
      """ % (num_nodes,len(ns.RootNodes()));

    return (_tdlmod,msg);
    
  # compile errors rethrown directly
  except CompileError:
    raise;
  # this exception gives us an error list directly
  except TDL.CumulativeError,value:
    _dprint(0,'exception',sys.exc_info(),'compiling TDL file',filename);
    errlist = value.args;
    raise CompileError(*errlist);
  # all other errors explicitly added to list    
  except:
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'compiling TDL file',filename);
    # add error to list in nodecope
    ns.Repository().add_error(excvalue,tb=traceback.extract_tb(tb));
    raise CompileError(*ns.GetErrors());

#!/usr/bin/python

from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
from Timba.Meq import meqds
from Timba import TDL

from qt import *
import imp
import sys
import traceback

_dbg = verbosity(0,name='tdlgui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


def run_tdl_script (pathname,parent):
  # open file first
  try:
    ff = file(pathname,'r');
  except IOError:
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'opening TDL file',pathname);
    QMessageBox.warning(parent,"Error loading TDL script",
      """<p>Cannot open file <tt>%s</tt>:</p>
      <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
      QMessageBox.Ok);
    return;
  # import module
  modname = '__tdlruntime';
  try:
    imp.acquire_lock();
    mod = imp.load_source(modname,pathname,ff);
  except:
    imp.release_lock();
    ff.close();
    traceback.print_exc();
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'importing TDL file',pathname);
    QMessageBox.warning(parent,"Error loading TDL script",
      """<p>Error during import of <tt>%s</tt>:</p>
      <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
      QMessageBox.Ok);
    return;
  imp.release_lock();
  ff.close();
  mqs = meqds.mqs();
  # module here, call functions
  try:
    ns = TDL.NodeScope();
    mod.define_forest(ns);
    delattr(mod,'define_forest');  # delete so it doesn't confuse the next import
    ns.Resolve();
  except:
    traceback.print_exc();
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'in define_forest() of TDL file',pathname);
    QMessageBox.warning(parent,"Error running TDL script",
      """<p>Error defining forest in <tt>%s</tt>:</p>
      <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
      QMessageBox.Ok);
    return;
  num_nodes = len(ns.AllNodes());
  # no nodes? return
  if not num_nodes:
    QMessageBox.warning(parent,"TDL script executed",
      """<p>Executed TDL script <tt>%s</tt>, but no nodes were defined.</p>""",
      QMessageBox.Ok);
    return;
  # try to run stuff
  mqs.meq('Clear.Forest');
  mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),ns.AllNodes().itervalues())));
  mqs.meq('Resolve.Batch',record(name=list(ns.RootNodes().iterkeys())));
  
  ### NB: presume this was successful for now
  
  # if a forest state is defined, set it
  fst = getattr(mod,'forest_state',None);
  if fst:
    mqs.meq('Set.Forest.State',record(state=fst));
    delattr(mod,'forest_state');  # delete so it doesn't confuse the next import
    
  # does the script define a testing function?
  testfunc = getattr(mod,'test_forest',None);
  # no, show status and return
  if not callable(testfunc):
    QMessageBox.information(parent,"TDL script executed",
      """<p>Executed TDL script <tt>%s</tt>. %d node definition (of which %d are root nodes) were sent to the kernel.
      </p>""" % (pathname,num_nodes,len(ns.RootNodes())),
      QMessageBox.Ok);
    return;
  # yes, offer to run the test
  delattr(mod,'test_forest');  # delete so it doesn't confuse the next import
  if QMessageBox.information(parent,"TDL script executed",
       """<p>Executed TDL script <tt>%s</tt>.</p>
       <p>%d nodes (%d roots) were defined.</p>
       <p>This script provides a built-in test, would you like to run this now?</p>
       """ % (pathname,num_nodes,len(ns.RootNodes())),
       "Run test","Skip test") != 0:
    return;
  # run test
  try:
    testfunc(mqs);
  except:
    traceback.print_exc();
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'in test_forest() of TDL file',pathname);
    QMessageBox.warning(parent,"Error testing TDL script",
      """<p>Error running tests in <tt>%s</tt>:</p>
      <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
      QMessageBox.Ok);

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

from Timba.Apps import meqserver
from Timba.Apps import app_defaults
from Timba.TDL import Compile
from Timba.Meq import meqds
from Timba.utils import *
from Timba import dmi
from Timba import octopussy

import sys
import traceback
import time
import pickle
import os
import Timba.array

_dbg = verbosity(0,name='assayer');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

MISMATCH = 1;
MISSING_DATA = 2;
TIMING_ERROR = 9;
OTHER_ERROR = 99;


class AssayError (RuntimeError):
  pass;

class AssaySetupError (AssayError):
  pass;
  
class DataMismatch (AssayError):
  pass;

import io
class logger (io.FileIO):
  def __init__ (self,filename):
    super(logger, self).__init__(filename,'w');
    
  def prefix (self):
    return time.strftime("%d/%m/%y %H:%M:%S: ",time.localtime())
  
  def log (self,*args):
    """prints arguments to log, a-la print(). Trailing newline added.""";
    self.write(self.prefix());
    self.write(' '.join(args));
    self.write('\n');
  
  def logf (self,format,*args):
    """printf's arguments to log. Trailing newline added.""";
    return self.log(format%args);
    
  def logs (self,*args):
    """prints lines to log. Arguments must be strings. No newlines added.""";
    prefix = self.prefix();
    return self.writelines([prefix+line for line in args]);
    
  def logsp (self,prefix,*args):
    """prints lines to log, with prefix. Arguments must be strings. No newlines added.""";
    prefix = self.prefix() + prefix;
    return self.writelines([prefix+line for line in args]);
    
class assayer (object):
  def __init__ (self,name,log=True,nokill=None):
    # parse command line
    self.recording = "-assayrecord" in sys.argv;
    self._assay_runtime = "-noruntime" not in sys.argv;
    self._subset_tests = None;    # all tests by default
    # "-assay" limits number of tests
    for i in range(len(sys.argv)):
      if sys.argv[i] == "-assay":
        if i >=  len(sys.argv)-1:
          raise AssaySetupError("-assay argument must be followed by a comma-separated list of test names");
        self._subset_tests = sys.argv[i+1].split(",");
    # if nokill is not explicitly specified, leave kernel running when recording
    if nokill is None:
      nokill = self.recording;
    self.name = name;
    if app_defaults.args.spawn:
      self.mqs = meqserver.default_mqs(wait_init=10,debug=False);
    else:
      self.mqs = meqserver.default_mqs(wait_init=True,debug=False);
    self.mqs.whenever("*",self._kernel_event_handler);
    self.mqs.whenever("node.result",self._node_snapshot_handler);
    self.tdlmod = self.logger = self.testname = None;
    self.watching = [];
    self.testname = None;
    self.default_tol = 1e-5;    # default comparison tolerance
    self.time_tol    = .5;      # default runtime tolerance
    self.hostname = os.popen('hostname').read().rstrip();
    self._assay_stat = 0;
    # open log and dump initial messages
    if log:
      self.logger = logger(self.name+".assaylog");
      self.logf("start of log for assayer %s",self.name);
    if self._subset_tests:
      self.log("will only run the following tests:",*self._subset_tests); 
  def log (self,*args):
    _dprint(1,*args+('\n',));
    if self.logger:
      self.logger.log(*args);
      
  def logf (self,*args):
    _dprintf(1,args[0]+"\n",*args[1:]);
    if self.logger:
      self.logger.logf(*args);
  
  def logs (self,*args):
    _dprint(1,*args+('\n',));
    if self.logger:
      self.logger.logs(*args);
      
  def logexc (self):
    exc_info = sys.exc_info();
    exc_lines = traceback.format_exception(*exc_info);
    _dprint(1,*exc_lines);
    if self.logger:
      self.logger.log("EXCEPTION:",str(exc_info[0]));
      self.logger.logsp("    ",*exc_lines);

  def set_default_tolerance (self,tol):
    self.default_tol = tol;
      
  def set_time_tolerance (self,tol):
    self.time_tol = tol;
    
  def compile (self,script):
    try:
      self.script = script;
      _dprint(0,"compiling",script);
      (self.tdlmod,ns,msg) = Compile.compile_file(self.mqs,script);
      _dprintf(0,"compiled %s: %s",script,msg);
      lines = ["compiled TDL script %s: "%script]+msg.rstrip().split('\n');
      self.logs(*[ s+'\n' for s in lines ]);
    except:
      self.logexc();
      raise;
      
  def init_test (self,name):
    try:
      if self.testname is not None:
        self.finish_test();
      # check if test is to be ignored
      if self._subset_tests:
        self._ignore_test = name not in self._subset_tests;
      else:
        self._ignore_test = False;
      self._assay_stat = 0;
      self.watching = [];
      self.testname = name;
      if self._ignore_test:
        self.logf("IGNORE: test '%s', not listed in -assay arguments",name);
        return;
      else:
        self.logf("START: test '%s'",name);
      if not self.tdlmod:
        raise AssaySetupError("FAIL: can't init_test because no script is compiled");
      # load assay data for the sake of per-host timings
      self.datafile = '.'.join((self.name,name,'data-assay'));
      if not self._load_assay_data(self.datafile):
        if self.recording:
          self._recorded_time = {};
        else:
          raise AssaySetupError("FAIL: no assay data "+self.datafile);
      if self.recording:
        self.log("RECORDING assay data, no comparisons will be done");
        self._sequences = {};
        self._inspections = {};
    except:
      self.logexc();
      raise;
      
  def _add_watch (self,node,desc,functional, \
                  conditional=None,tolerance=None):
    """Helper method for adding a node watcher.
    node:        node name
    desc:        textual description (e.g. same as field name, if watching a field) 
    functional:  a callable taking one parameter (nodestate), and returning 
                 the value to watch.
    conditional: a callable taking one parameter (nodestate), and returning 
                 True if the given snapshot is to be used in the watch. If None,
                 all snapshots are watched.
    tolerance:   comparison tolerance (None for default).
    """;
    try:
      if self._ignore_test:
        return;
      if tolerance is None:
        tolerance = self.default_tol;
      if self.testname is None:
        raise AssaySetupError("can't watch nodes: no test specified");
      self.watching.append((node,desc,functional,conditional,tolerance));
      self.logf("will watch node '%s' %s",node,desc);
    except:
      self.logexc();
      raise;

  def watch (self,nodespec,tolerance=None,
             functional=None,conditional=None,rqtype=None,desc=None):
    """Adds a node watcher.
    nodespec:    A node name or a string of the form "node/a.b.c".
                 In the former case, the entire node state is watched, in the 
                 latter case, only field a.b.c will be extracted.
    tolerance:   comparison tolerance, None for default.
    functional:  if not None, then must be a callable taking one parameter.
                 The node state (or subfield) specified by nodespec is then
                 passed to the functional to generate the actual value to watch.
                 This is useful to, e.g., reduce large arrays to their mean.
    desc:        textual description. If None, then one is generated based on
                 nodespec. Note that each watcher must have a unique description,
                 so you may want to provide one explicitly.
    conditional: a callable taking one parameter (nodestate), and returning 
                 True if the given snapshot is to be used in the watch. If None,
                 all snapshots are watched.
    rqtype:      shorthand for conditioning on request type. If not None, 
                 then generates an extra conditional that compares 
                 nodestate.cache.request_id[0] to the given rqtype.
    """;
    try:
      if self._ignore_test:
        return;
      # parse nodespec and generate description if needed. func
      # will be a callable returning the subfield, or the entire node state
      ns = nodespec.split("/",1);
      if len(ns) == 1:
        func = lambda st:st;
        desc = desc or '';
      else:
        func = lambda st:extract_value(st,ns[1].split("."));
        desc = desc or ns[1];
      # generate compound functional
      if functional is None:
        func1 = func;
      else:
        func1 = lambda st:functional(func(st));
      # generate a conditional if rqtype is supplied
      if rqtype is not None:
        if conditional is not None:
          conditional = lambda st:conditional(st) and st.cache.request_id[0]==dmi.hiid(rqtype);
        else:
          conditional = lambda st:st.cache.request_id[0]==dmi.hiid(rqtype);
      # call watch
      self._add_watch(ns[0],desc,func1,tolerance=tolerance,conditional=conditional);
    except:
      self.logexc();
      raise;
    
  def run (self,procname="_test_forest",**kwargs):
    try:
      if self._ignore_test:
        return;
      if self.tdlmod is None:
        raise AssaySetupError("no TDL script compiled");
      self._assay_stat = 0;
      # check that procedure exists
      proc = getattr(self.tdlmod,procname,None);
      if not callable(proc):
        raise AssaySetupError("no "+procname+"() in compiled script");
      # now, enable publishing for specified watch nodes
      if self.watching:
        for w in self.watching:
          self.mqs.publish(w[0]);
      # run the specified procedure
      self.logf("running %s(), test %s",procname,self.testname);
      dt = time.time();
      _dprint(0,"running",procname);
      retval = proc(self.mqs,None,**kwargs);
      _dprint(0,procname,"finished");
      self._assay_time(time.time() - dt);
      # inspect return value
      if self.recording:
        self._inspections['retval'] = normalize_value(retval);
        self.logf("recorded %s() return value",procname);
      else:
        try:
          expected = self._inspections.get('retval');
        except KeyError:
          self._assay_stat = MISSING_DATA;
          self.logf("ERROR: no assay data recorded for return value");
        else:
          try:
            compare_value(expected,retval,self.default_tol,field=procname+"()");
          except Exception as exc:
            self._assay_stat = MISMATCH;
            self.logf("ERROR: assay fails on %s() return value",procname);
            self.log("  error is: ",exc.__class__.__name__,*list(map(str,exc.args)));
          else:
            self.logf("%s() return value ok",procname);
    except:
      self._assay_stat = OTHER_ERROR;
      self.logexc();
      raise;
    # return assay status
    if self.logger:
      self.logger.flush();
    return self._assay_stat;
    
  def finish_test (self):
    if self._ignore_test:
      self._ignore_test = False;
      self.testname = None;
      self.watching = [];
      return 0;
    # check that all expected sequences have run their course
    if not self.recording:
      for (node,desc,func,cond,tol) in self.watching:
        seq = self._sequences.get((node,desc),None);
        if seq:
          self.logf("ERROR: sequence not completed (%d entries remain) for node '%s' %s",len(seq),node,desc);
          self._assay_stat = MISMATCH;
    # check final status
    if not self._assay_stat:
      if self.recording:
        self._record_assay_data(self.datafile);
        self.logf("SUCCESS: test '%s' assay data recorded to %s",self.testname,self.datafile);
      else:
        self.logf("SUCCESS: test '%s' completed successfully",self.testname);
    else: 
      self.logf("FAIL: test '%s', code %d",self.testname,self._assay_stat);
    if self.logger:
      self.logger.flush();
    self.testname = None;
    self.watching = [];
    return self._assay_stat;
    
  def finish (self):
    if self.testname is not None:
      self.finish_test();
    self.logger = None;
    # in recording mode, pause before exiting
    if self.recording and "-nopause" not in sys.argv:
      self.mqs.disconnect();
      octopussy.stop();
      if self._assay_stat:
        print("""\n*** ERROR ***: Assay data recording failed, please review the log.\n""");
      a = input("""\n\n
Since you're running the assayer in recording mode, we have disconnected 
from the meqserver without stopping it. You may wish to run the browser to
ensure that tree state is correct. Run the browser now (Y/n)? """).rstrip();
      if not a or a[0].lower() == 'y':
        os.system("meqbrowser.py");
      print("""\n\nReminder: you may need to kill the meqserver manually.""");
    else:
      meqserver.stop_default_mqs();
    self.mqs = None;
    return self._assay_stat;
    
  def inspect (self,nodespec,tolerance=None):
    try:
      self.inspect_node(*nodespec.split("/"));
    except:
      self.logexc();
      raise;
  
  def inspect_node (self,node,field,tolerance=None):
    try:
      if self._ignore_test:
        return;
      field = tuple(field.split('.'));
      nodestate = self.mqs.getnodestate(node,wait=2);
      val = extract_value(nodestate,field);
      if self.recording:   # collect value
        self._inspections[(node,field)] = normalize_value(val);
        self.logf("recorded inspection for node '%s' %s",node,'.'.join(field));
      else:                # assay value
        if tolerance is None:
          tolerance = self.default_tol;
        try:
          expected = self._inspections.get((node,field),None);
        except KeyError:
          self._assay_stat = MISSING_DATA;
          self.logf("ERROR: no assay data recorded for node '%s' %s",node,'.'.join(field));
          return;
        try:
          compare_value(expected,val,tolerance,field=node+'/'+'.'.join(field));
        except Exception as exc:
          self._assay_stat = MISMATCH;
          self.logf("ERROR: assay fails on node '%s' %s",node,'.'.join(field));
          self.log("  error is: ",exc.__class__.__name__,*list(map(str,exc.args)));
          return False;
        else:
          self.logf("node '%s' %s ok",node,'.'.join(field));
          return True;
    except:
      self.logexc();
      self._assay_stat = OTHER_ERROR;
      self.logf("failed to inspect node '%s' %s",node,'.'.join(field));
      self.log("assay will fail");
      return False;
    
  def _assay_time (self,dt):
    if self.recording:
      self._recorded_time[self.hostname] = dt;
      self.logf("runtime is %.2f seconds (none recorded)",dt);
    else:
      # see if we have a timing for this host
      t0 = self._recorded_time.get(self.hostname,None);
      if t0 is None:
        self.logf("runtime is %.2f seconds (none recorded)",dt);
        self.logf("WARNING: no expected runtime recorded for host %s",self.hostname);
        self.log("   you may want to re-run this test with -assayrecord");
        return;
      else:
        self.logf("runtime is %.2f seconds vs. %.2f recorded",dt,t0);
      if self._assay_stat or not self._assay_runtime:
        return;
      t0 = max(t0,1e-10);
      dt = max(dt,1e-10);
      if dt > 2 and dt > t0*(1+self.time_tol):
        self.logf("ERROR: runtime too slow by factor of %g",dt/t0)
        self.log("assay will fail");
        self._assay_stat = TIMING_ERROR;
      elif dt > 2 and dt < t0*(1-self.time_tol):
        self.logf("SURPISE: runtime faster by a factor of %g",t0/dt);
        
      
  def _load_assay_data (self,fname):
    # catch file-open errors and return none
    try:
      pfile = open(fname,"r");
    except:
      return None;
    # load stuff
    unpickler = pickle.Unpickler(pfile);
    name = unpickler.load();
    if name != self.testname:
      raise AssaySetupError("test name in data file "+fname+" does not match");
    self._recorded_time = unpickler.load();
    self._sequences = unpickler.load();
    self._inspections = unpickler.load();
    self.logf("loaded assay data from file %s",fname);
    for (host,t0) in self._recorded_time.items():
      self.logf("  host %s recorded runtime is %.2f seconds",host,t0);
    return True;
      
  def _record_assay_data (self,fname):
    if not self.recording or not self.testname:
      return;
    pfile = open(fname,"w");
    pickler = pickle.Pickler(pfile);
    pickler.dump(self.testname);
    pickler.dump(self._recorded_time);
    pickler.dump(self._sequences);
    pickler.dump(self._inspections);

  def _node_snapshot_handler (self,msg):
    try: 
      # self.log("got node snapshot",str(msg));
      nodestate = getattr(msg,'payload',None);
      name = nodestate.name;
      # are we watching this node?
      for (node,desc,functional,conditional,tolerance) in self.watching:
        if node == name:
          _dprint(5,"nodestats is",nodestate);
          # extract rqid (for labels)
          try:
            rqid = "(rqid %s)" % str(nodestate.cache.request_id);
          except:
            rqid = "(no rqid)";
          # apply functional to extract value
          _dprint(3,"extracting value for snapshot",name,rqid);
          value = functional(nodestate);
          # check conditional, if defined
          use = True;
          if conditional is not None:
            try: 
              use = conditional(nodestate);
              _dprint(3,"conditional returns",use);
            except: 
              _dprint(3,"conditional failed with exception, ignoring result");
              if _dbg.verbose>2:
                traceback.print_exc();
              use = False;
          # if failed condition, return
          if not use:
            return;
          _dprint(4,"value is",value);
          if self.recording:   # collect value
            seq = self._sequences.setdefault((node,desc),[]);
            seq.append(normalize_value(value));
            self.logf("recorded value #%d for node '%s' %s %s",len(seq),name,desc,rqid);
          else:                # assay value
            # look for sequence data
            try:
              seq = self._sequences[(node,desc)];
            except:
              self._assay_stat = MISSING_DATA;
              self.logf("ERROR: no recorded sequence for node '%s' %s",node,desc);
              return;
            # get first item from sequence
            if not seq:
              self._assay_stat = MISSING_DATA;
              self.logf("ERROR: end of recorded sequence on node '%s' %s %s",node,desc,rqid);
              return;              
            expected = seq.pop(0);
            try:
              compare_value(expected,value,tolerance,field=node+'/'+desc);
            except Exception as exc:
              self._assay_stat = MISMATCH;
              self.logf("ERROR: assay fails on node '%s' %s %s",node,desc,rqid);
              self.log("  error is: ",exc.__class__.__name__,*list(map(str,exc.args)));
            else:
              self.logf("node '%s' %s %s ok",node,desc,rqid);
    except:
      self.logexc();
      self._assay_stat = OTHER_ERROR;
      self.log("assay will fail");

  def _kernel_event_handler (self,msg):
    try:
      value = getattr(msg,'payload',None);
      if isinstance(value,dmi.record):
        for f in ("text","message","error"):
          if value.has_field(f):
            self.logf("meqserver %s: %s",f,value[f]);
    except:
      self.logexc();
      self.log("last error non-fatal, assay will continue");

def normalize_value (value):
  """helper function to convert a value from dmi types to standard python""";
  if isinstance(value,dmi.record):
    res = {};
    for field,val1 in value.items():
      res[field] = normalize_value(val1);
    return res;
  elif isinstance(value,(list,tuple)):
    res = [];
    for val1 in value:
      res.append(normalize_value(val1));
    return res;
  elif isinstance(value,dmi.array_class):
    cp = value.copy();
    cp.__class__ = dmi.array_class;
    return cp;    # returns normal Timba.array
  else:
    return value;

def extract_value (record,field):
  """helper function to recursively extract a sequence of fields""";
  _dprint(6,'extract',field,'from',record);
  value = record;
  for f in field:
    value = value[f];
  return value;

_numtypes = (int,int,float,complex);
_seqtypes = (list,tuple);

def compare_value (a,b,tol=1e-6,field=None): 
  try:
    if isinstance(a,_numtypes):
      diff = abs(a-b);
      scale = (abs(a)+abs(b))/2;
      if scale:
        diff = diff/scale;  # relative difference
      if diff <= tol:
        return True;
      raise DataMismatch(field,a,b,"rd %g"%diff);
    elif isinstance(a,dict):
      if len(a) != len(b):
        raise DataMismatch(field,"lengths",len(a),len(b));
      for (key,value) in a.items():
        try:
          val2 = b[key];
        except KeyError:
          raise KeyError(field,"missing field",key);
        compare_value(value,b[key],tol,field=field+'.'+key);
      return True;
    elif isinstance(a,(list,tuple)):
      if len(a) != len(b):
        raise DataMismatch(field,"lengths",len(a),len(b));
      iterb = iter(b);
      n = 0;
      for value in a:
        compare_value(value,next(iterb),tol,field="%s[%d]"%(field,n));
        n+=1;
      return True;
    elif isinstance(a,dmi.array_class):
      if a.shape != b.shape:
        raise DataMismatch(field,"shapes",a.shape,b.shape);
      diff = abs(a-b)
      scale = (abs(a)+abs(b))/2;
      ## KLUDGE START
      ## this is replaced by 
      # with Timba.array.errstate(divide="ignore"):
      #   maxdiff = Timba.array.where(scale!=0,diff/scale,diff).max();  # max relative difference
      ## as of Python 2.5. But for 2.4, we have to do:
      est = Timba.array.errstate(divide="ignore");
      est.__enter__();
      try:
        maxdiff = Timba.array.where(scale!=0,diff/scale,diff).max();
      finally:
        est.__exit__(None,None,None);
      ## KLUDGE END
      # diff = abs(a-b).max();
      # maxdiff = max(abs(a).max(),abs(b).max())*tol;
      if maxdiff <= tol:
        return True;
      raise DataMismatch(field,"rd %g max %g"%(maxdiff,tol));
    else:
      if a == b:
        return True;
      raise DataMismatch(field,str(a)[:32],str(b)[:32]);
  except DataMismatch:
    raise;
  except:
    _dprint(2,'compare_value() fails on',a,b);
    excinfo = sys.exc_info();
    if _dbg.verbose > 1:
      traceback.print_exception(*excinfo);
    raise excinfo[0](field,*excinfo[1].args);

import sys
import re
import traceback
import os
import os.path
import signal

import Trut
from Trut import _dprint,_dprintf

# setup some regexes for File
_re_comment   = re.compile("#.*$");
_re_indent    = re.compile("^(\s*)(\S.*)$");
_re_option    = re.compile("^(\w+)\s*=\s*(\S.*)$");
_re_directive = re.compile("^(\w+)\s+(\S.*)?$");

class File (Trut.Unit):
  Directives = {};
  
  def __init__ (self,name,maxjobs=1,parent=None):
    """inits a File test unit. A File unit parses a TRUT file and
    executes units found in that file.
    'jobs': number of top-level units to run in parallel
    """
    Trut.Unit.__init__(self,name,parent=parent);
    self._old_path = None;
    # max number of parallel jobs to fork off
    self._max_jobs = maxjobs;
    # dict of child jobs
    self._child_jobs = {};
    # flag -- we are a child process
    self._we_are_child = False;
    # if a top-level unit is passed off to a child process, we have to ignore commands related to
    # it, until we get to this indent level
    self._ignore_until_indent = None;
    
  def _new_topunit (self,testunit,indent):
    setattr(testunit,'_indent',indent);
    setattr(testunit,'_subindent',None);
    self.top_unit = testunit;
  
  def _check_indent (self,indent):
    """called to process an option/directive with a given indent level.
    Ends all stanzas of a higher/same indent, then checks if the current
    stanza already has a subindent. If not, sets the subindent. If yes, 
    verifies that the subindent matches."""; 
    while indent <= self.top_unit._indent:
      self.exec_top_unit();
      if self.top_unit == self.parent:
        raise Trut.UnexpectedError,"oops, check_indent f*cked up""";
    if self.top_unit._subindent is None:
      self.top_unit._subindent = indent;
    elif self.top_unit._subindent != indent:
      raise Trut.ParseError,"indentation level does not match any previous indentation";
    
  def exec_top_unit (self):
    try:
      self.top_unit.execute();
    except:
      excinfo = sys.exc_info();
      self.log_exc(level=0,*excinfo);
      self.top_unit.fail(excinfo[1]);
    try:
      self.top_unit.cleanup();
    except:
      excinfo = sys.exc_info();
      self.log_exc(level=0,*excinfo);
      self.top_unit.fail(excinfo[1]);
    excinfo = None;
    clsname,name = self.top_unit.__class__.__name__,self.top_unit.name;
    _dprint(3,os.getpid(),"finished directive",clsname,name,"fail is",self.failed);
    self.top_unit = self.top_unit.parent;
    # if we are a child process, and we're finished with this unit, exit
    if self._we_are_child and self.top_unit == self:
      sys.exit(self.failed);
      
  def _start_directive (self,name,value,indent,ignore=False):
    _dprint(3,os.getpid(),"starting directive",name,value);
    # find class by that name
    tu_class = self.top_unit.Directives.get(name,None);
    if not callable(tu_class):
      raise Trut.ParseError,"unknown directive '%s'"%name;
    # create test unit
    self.top_unit = tu = tu_class(value,parent=self.top_unit);
    self._new_topunit(tu,indent);
    
  def _process_directive (self,name,value,indent):
    # only top-level directives can be split off into jobs. Also, no jobs will be
    # split off if the max_jobs value is < 2. So under these conditions, we start
    # the directive directly within this process
    if self._we_are_child or self.top_unit != self or self._max_jobs < 2:
      return self._start_directive(name,value,indent);
    # if the max number of jobs is already running, wait for one to finish
    while len(self._child_jobs) >= self._max_jobs:
      _dprint(2,os.getpid(),"waiting for a child to finish");
      pid,status = os.wait();
      self._reap_child_process(pid,status);
    # create temporary log files for child process
    loggers = self._allocate_tmp_loggers();
    pid = os.fork();
    if pid:  # parent branch
      _dprint(2,os.getpid(),"forked off child",pid,"for",name,value);
      self._child_jobs[pid] = loggers;
      # ignore everything related to this directive
      self._ignore_until_indent = indent;
    else:    # child branch
      self._we_are_child = True;
      self._child_jobs = {};
      self._set_tmp_loggers(loggers);
      self._start_directive(name,value,indent);
      
  def _reap_child_process (self,pid,status):
    _dprint(2,os.getpid(),"child",pid,"exited with status",status);
    if pid not in self._child_jobs:
      raise RuntimeError,"unexpected child pid "+str(pid);
    loggers = self._child_jobs.pop(pid);
    self._merge_tmp_loggers(loggers);
    # fail if child did not return 0
    if status:
      self.fail("child process returns status %d"%status);

  def execute (self):
    # log a message about running the tests, at level 10 (i.e. the "error"
    # level of the child units)
    self.log('start',level=10);
    self._new_topunit(self,-1);
    # cd to directory of file
    dirname = os.path.dirname(self.name);
    os.chdir(dirname);
    _dprint(1,"changing directory to",dirname);
    self._old_path = sys.path;
    sys.path.append('.');
    _dprint(1,"running trut file",self.name);
    # parse file
    try:
      for line in file(os.path.basename(self.name)):
        # check for fails
        if self.giveup():
          break;
        # strip comments
        line = line.rstrip();
        line = _re_comment.sub('',line);
        _dprint(2,os.getpid(),"line is:",line);
        # find initial whitespace
        match_indent = _re_indent.match(line);
        if not match_indent:  # empty line
          _dprint(3,os.getpid(),"empty line");
          continue;
        # get current indent level
        indent = len(match_indent.group(1).replace('\t',' '*8));
        # get the remaining text, strip trailing space
        line = match_indent.group(2);
        _dprint(3,os.getpid(),"indent level",indent);
        # if this section is being processed by a child process, ignore
        if self._ignore_until_indent is not None and indent > self._ignore_until_indent:
          _dprint(3,os.getpid(),"ignoring line -- handled by child process""");
          continue;
        # check indent level and close all relevant stanzas
        self._check_indent(indent);
        # check for an Option = Value string
        match = _re_option.match(line);
        if match:
          option = match.group(1);
          value = match.group(2).rstrip();
          _dprint(3,os.getpid(),"option",option,"=",value);
          # the top stanza is the one to which this option pertains
          self.top_unit.set_option(option,value);
          continue;
        # check for directive
        match = _re_directive.match(line);
        if match:
          name = match.group(1);
          value = match.group(2).rstrip();
          self._process_directive(name,value,indent);
      # execute any remaining test units
      while self.top_unit != self and not self.giveup():
        self.exec_top_unit();
      # wait for child jobs to finish before reporting success or failure
      self._reap_all_children();
      # failure deferred due to persistency will be reported here
      self.success("finish");
    # catch exceptions and fail
    except:
      errtype,err,tb = sys.exc_info();
       # re-raise if exiting
      if isinstance(err,SystemExit):
        raise err;
      # log
      self.log_exc(errtype,err,tb,level=0);
      tb = None;  # avoids garbage collection delay
      # kill children if interrupted
      if isinstance(err,KeyboardInterrupt):
        for pid in self._child_jobs.iterkeys():
          os.kill(pid,signal.SIGINT);
      self.fail(err);
      if self._we_are_child:
        sys.exit(2);
    # wait for any child jobs to finish
    self._reap_all_children();
  
  def _reap_all_children(self):
    while self._child_jobs:
      _dprint(3,os.getpid(),"waiting for all children to finish");
      pid,status = os.wait();
      self._reap_child_process(pid,status);
      
  def cleanup (self):
    if self._old_path is not None:
      sys.path = self._old_path;
    self.success();


File.Directives['TrutFile'] = File;
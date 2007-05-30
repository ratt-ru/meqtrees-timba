import sys
import re
import traceback
import os
import os.path

import Trut
from Trut import _dprint,_dprintf

# setup some regexes for File
_re_comment   = re.compile("#.*$");
_re_indent    = re.compile("^(\s*)(\S.*)$");
_re_option    = re.compile("^(\w+)\s*=\s*(\S.*)$");
_re_directive = re.compile("^(\w+)\s+(\S.*)?$");

class File (Trut.Unit):
  Directives = {};
  
  def __init__ (self,name,jobs=1,parent=None):
    """inits a File test unit. A File unit parses a TRUT file and
    executes units found in that file.
    'jobs': number of top-level units to run in parallel
    """
    Trut.Unit.__init__(self,name,parent=parent);
    self._old_path = None;
    # number of parallel jobs to fork off
    self._jobs = jobs;
    
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
      err = sys.exc_info()[1];
      traceback.print_exc();
      self.top_unit.fail(err);
    try:
      self.top_unit.cleanup();
    except:
      err = sys.exc_info()[1];
      traceback.print_exc();
      self.top_unit.fail(err);
    self.top_unit = self.top_unit.parent;

  def execute (self):
    # log a message about running the tests, at level 10 (i.e. the "error"
    # level of the child units)
    self.log('',level=10);
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
        _dprint(2,"line is:",line);
        # find initial whitespace
        match_indent = _re_indent.match(line);
        if not match_indent:  # empty line
          _dprint(3,"empty line");
          continue;
        # get current indent level
        indent = len(match_indent.group(1).replace('\t',' '*8));
        # get the remaining text, strip trailing space
        line = match_indent.group(2);
        _dprint(3,"indent level",indent);
        # check indent level and close all relevant stanzas
        self._check_indent(indent);
        # check for an Option = Value string
        match = _re_option.match(line);
        if match:
          option = match.group(1);
          value = match.group(2).rstrip();
          _dprint(3,"option",option,"=",value);
          # the top stanza is the one to which this option pertains
          self.top_unit.set_option(option,value);
          continue;
        # check for directive
        match = _re_directive.match(line);
        if match:
          name = match.group(1);
          value = match.group(2).rstrip();
          _dprint(3,"directive",name,"=",value);
          # find class by that name
          tu_class = self.top_unit.Directives.get(name,None);
          if not callable(tu_class):
            raise Trut.ParseError,"unknown directive '%s'"%name;
          # create test unit
          self.top_unit = tu = tu_class(value,parent=self.top_unit);
          self._new_topunit(tu,indent);
      # execute any remaining test units
      while self.top_unit != self and not self.giveup():
        self.exec_top_unit();
      # failure deferred due to persistency will be reported here
      self.success();
    # catch exceptions and fail
    except:
      err = sys.exc_info()[1];
      traceback.print_exc();
      self.fail(err);
      
  def cleanup (self):
    if self._old_path is not None:
      sys.path = self._old_path;
    self.success();


File.Directives['TrutFile'] = File;
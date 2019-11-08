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

import sys
import traceback
import os
import os.path
import time

from Timba import dmi

import Trut

from Trut import _dprint,_dprintf

from . import TrutTDL

class TrutLogger (object):
  def __init__ (self,logfile,verbose=0,console=False):
    """Creates a logger. 'logfile' can be a filename or a file object. 'verbosity' specifies
    the verbosity level."""
    if logfile is None:
      raise TypeError("'logfile' should be a filename or a file object");
    self.set_file(logfile);
    self.verbose = verbose;
    self._is_console = console;
    
  def log (self,message,status="",level=0,progress=False):
    """writes message and optional status, if the specified level is <= the verbosity
    level we were created with.""";
    if level > self.verbose:
      return;
    # progress messages only go to consoles
    if progress:
      if self._is_console:
        self.fileobj.write("%-70.70s\r"%message);
        self.fileobj.flush();
    # normal messages go according to level
    else:
      _dprint(5,os.getpid(),"logging to file",self.fileobj,level,message,status);
      if status:
        self.fileobj.write("%-70s [%s]\n"%(message,status));
      else:
        self.fileobj.write("%-80s\n"%message);
        
  def log_exc (self,exctype,excvalue,exctb,level=0):
    """writes exception, if the specified level is <= the verbosity level we were created with.""";
    # STDERR.write("***exc %s %d %d\n"%(exctype,level,self.verbose));
    if level <= self.verbose:
      _dprint(5,os.getpid(),"logging to file",self.fileobj,excvalue);
      traceback.print_exception(exctype,excvalue,exctb,limit=None,file=self.fileobj);

  def allocate_tmp_file (self):
    """allocates a temporary file based on the current logfile. Returns None if we were created with a
    file object and not a filename.""";
    if not self.filename:
      return None;
    # flush current buffers
    self.fileobj.flush();
    # make temp file
    tmpfile = os.tmpfile();
    return tmpfile;

  def set_file (self,logfile):
    """changes the current logfile. If logfile=None, does nothing""";
    if logfile is not None:
      if isinstance(logfile,str):
        self.filename = logfile;
        self.fileobj = open(logfile,'w');
      elif isinstance(logfile,file):
        self.filename = None;
        self.fileobj = logfile;
      else:
        raise TypeError("'logfile' should be a filename or a file object");
      
  def merge_file (self,logfile):
    """merges the given file into our log.""";
    _dprint(2,"merging in logfile",logfile);
    if logfile is None:
      return None;
    import six, io
    if isinstance(logfile,str):
      self.fileobj.writelines(open(logfile,'r'));
    elif isinstance(logfile, file if six.PY2 else io.IOBase):
      # logfile.seek(0);
      # for line in logfile:
      #   _dprint(0,os.getpid(),"merging from",logfile,line);
      logfile.seek(0);
      self.fileobj.writelines(logfile);
    else:
      raise TypeError("'logfile' should be a filename or a file object");

STDERR = sys.stderr;

class TrutBatchRun (Trut.Unit):
  def __init__ (self,name="",persist=0,loggers=[]):
    Trut.Unit.__init__(self,name);
    self.loggers = list(loggers);
    self.persist = persist;
    
  def add_loggers (self,*loggers):
    self.loggers += list(loggers);
  
  def remove_loggers (self,*loggers):
    for log in loggers:
      if log in self.loggers:
        self.loggers.remove(log);
    
  def log_message (self,message,status,level=1,progress=False):
    _dprint(5,os.getpid(),"logging message",level,message,status);
    for logger in self.loggers:
      logger.log(message,status,level=level,progress=progress);
      
  def log_exc (self,exctype,excvalue,exctb,level=1):
    _dprint(5,os.getpid(),"logging exception",excvalue);
    for logger in self.loggers:
      logger.log_exc(exctype,excvalue,exctb,level=level);
      
  def _allocate_tmp_loggers (self):
    """returns a set of temporary logfiles for use by child jobs""";
    return [ logger.allocate_tmp_file() for logger in self.loggers ];
  
  def _set_tmp_loggers (self,tmplogs):
    """switches loggers to temporary logfiles for use by child jobs. The tmplogs
    argument should be the return value of _allocate_tmp_loggers(), above.""";
    if tmplogs:
      if len(tmplogs) != len(self.loggers):
        raise ValueError("length of tmplogs argument does not match number of loggers");
      for tmplog,logger in zip(tmplogs,self.loggers):
        logger.set_file(tmplog);
  
  def _merge_tmp_loggers (self,tmplogs):
    """merges in temporary logfiles filled in by child jobs. The tmplogs argument 
    should be the return value of _allocate_tmp_loggers(), above.""";
    if tmplogs:
      if len(tmplogs) != len(self.loggers):
        raise ValueError("length of tmplogs argument does not match number of loggers");
      for tmplog,logger in zip(tmplogs,self.loggers):
        logger.merge_file(tmplog);
        
class FileMultiplexer (object):
  """A FileMultiplexer implements the write(str) method that is required
  of an object that can be assigned to sys.stdout or sys.stderr. We use it
  to redirect the program output to the required loggers.
  """;
  def __init__ (self,*files):
    self.files = files;
  def write (self,string):
    for f in self.files:
      f.write(string);

def run_files (files,verbosity=10,log_verbosity=40,persist=1,maxjobs=1,cache=True):
  errlog = TrutLogger(sys.stderr,verbosity,console=True);
  brieflog = TrutLogger('Trut.log',log_verbosity);
  full_log = TrutLogger('Trut.full.log',999999);
  # create a batch run unit
  batchrun = TrutBatchRun(persist=persist,loggers=[errlog,brieflog,full_log]);
  # get absolute name for all files
  files = [ os.path.abspath(filename) for filename in files ];
  # read test cache. This is simply a list of all the trut files that were
  # tested successfully. If a cache exists and is less than an hour old, the
  # successful tests will not be rerun (unless we're called with cache=False) 
  testcache = os.path.join(os.getcwd(),".trut.cache");
  usecache = cache;
  try:
    cache = {};
    for line in open(testcache).readlines():
      filename,rtime = line.split(' ');
      cache[filename] = int(rtime);
  except:
    if usecache:
      errlog.log("No recent test results found in cache, all tests will be run",level=1);
  else:
    if usecache:
      errlog.log("Cache contains %d successful test(s). Recently (<1 hour) successful tests will be skipped."%len(cache),level=1);
      errlog.log("Use the '-c' option to rerun all tests regardless of cache.",level=1);
  # execute each file in turn, break out on error (unless persist=True)
  for filename in files:
    trutfile = Trut.File(filename,parent=batchrun,maxjobs=maxjobs);
    # check cache, skip file if found (and recent)
    if usecache and filename in cache:
      if cache[filename] > time.time() - 3600:
        trutfile.success("(skipped)");
        continue;
      else:
        del cache[filename];
    # make loggers local to that directory
    dirname = os.path.dirname(os.path.abspath(filename));
    log1 = os.path.join(dirname,'trut.log');
    log2 = os.path.join(dirname,'trut.full.log');
    local_brieflog = TrutLogger(log1,log_verbosity);
    local_full_log = TrutLogger(log2,log_verbosity)
    batchrun.add_loggers(local_brieflog,local_full_log);
    # replace stdout and stderr by the full logger's file object
    old_streams = sys.stdout,sys.stderr;
    sys.stdout = sys.stderr = FileMultiplexer(full_log.fileobj,local_full_log.fileobj);
    # execute file
    trutfile.execute();
    # restore old stdout/stderr
    sys.stdout,sys.stderr = old_streams;
    # remove local loggers
    batchrun.remove_loggers(local_brieflog,local_full_log);
    # check for fails
    if trutfile.failed:
      if filename in cache:
        del cache[filename];
      errlog.log("%s/trut[.full].log will contain more details of the failure"%dirname,level=1);
    else:
      cache[filename] = time.time();
    if batchrun.giveup():
      break;
  # cache successful tests
  if cache:
    open(testcache,'w').writelines(["%s %d\n"%cc for cc in cache.items()]);
  # this will print a fail/success message
  result = batchrun.success();
  if not result:
    errlog.log("Trut[.full].log will contain more details of the failure",level=1);
  return result;

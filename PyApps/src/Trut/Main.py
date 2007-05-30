import sys
import traceback
import os
import os.path
import sets

from Timba import dmi

import Trut

from Trut import _dprint,_dprintf

import TrutTDL

class TrutLogger (object):
  def __init__ (self,logfile,verbose=0,console=False):
    """Creates a logger. 'logfile' can be a filename or a file object. 'verbosity' specifies
    the verbosity level."""
    if logfile is None:
      raise TypeError,"'logfile' should be a filename or a file object";
    self.set_file(logfile);
    self.verbose = verbose;
    self._is_console = console;
    
  def log (self,message,status="",level=0,progress=False):
    """writes message and optional status, if the specified level is <= the verbosity
    level we were created with.""";
    # progress messages only go to consoles
    if progress:
      if self._is_console:
        self.fileobj.write("%-70.70s\r"%message);
        self.fileobj.flush();
    # normal messages go according to level
    elif level <= self.verbose:
      _dprint(5,os.getpid(),"logging to file",self.fileobj,level,message,status);
      if status:
        self.fileobj.write("%-70s [%s]\n"%(message,status));
      else:
        self.fileobj.write("%-80s\n"%message);
        
  def log_exc (self,exctype,excvalue,exctb,level=0):
    """writes exception, if the specified level is <= the verbosity level we were created with.""";
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
        self.fileobj = file(logfile,'w');
      elif isinstance(logfile,file):
        self.filename = None;
        self.fileobj = logfile;
      else:
        raise TypeError,"'logfile' should be a filename or a file object";
      
  def merge_file (self,logfile):
    """merges the given file into our log.""";
    _dprint(2,"merging in logfile",logfile);
    if logfile is None:
      return None;
    if isinstance(logfile,str):
      self.fileobj.writelines(file(logfile,'r'));
    elif isinstance(logfile,file):
      # logfile.seek(0);
      # for line in logfile:
      #   _dprint(0,os.getpid(),"merging from",logfile,line);
      logfile.seek(0);
      self.fileobj.writelines(logfile);
    else:
      raise TypeError,"'logfile' should be a filename or a file object";

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
      
  def log_exc (self,exctype,excvalue,exctb,level=0):
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
        raise ValueError,"length of tmplogs argument does not match number of loggers";
      for tmplog,logger in zip(tmplogs,self.loggers):
        logger.set_file(tmplog);
  
  def _merge_tmp_loggers (self,tmplogs):
    """merges in temporary logfiles filled in by child jobs. The tmplogs argument 
    should be the return value of _allocate_tmp_loggers(), above.""";
    if tmplogs:
      if len(tmplogs) != len(self.loggers):
        raise ValueError,"length of tmplogs argument does not match number of loggers";
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

def run_files (files,verbosity=10,log_verbosity=40,persist=1,maxjobs=1):
  errlog = TrutLogger(sys.stderr,verbosity,console=True);
  brieflog = TrutLogger('Trut.log',log_verbosity);
  full_log = TrutLogger('Trut.full.log',999999);
  # create a batch run unit
  batchrun = TrutBatchRun(persist=persist,loggers=[errlog,brieflog,full_log]);
  # get absolute name for all files
  files = [ os.path.abspath(file) for file in files ];
  # execute each file in turn, break out on error (unless persist=True)
  for filename in files:
    trutfile = Trut.File(filename,parent=batchrun,maxjobs=maxjobs);
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
      errlog.log("%s/trut[.full].log will contain more details of the failure"%dirname,level=1);
    if batchrun.giveup():
      break;
    
  # this will print a fail/success message
  result = batchrun.success();
  if not result:
    errlog.log("Trut[.full].log will contain more details of the failure",level=1);
  return result;

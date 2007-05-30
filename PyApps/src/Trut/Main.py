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
  def __init__ (self,logfile,verbose=0):
    """Creates a logger. 'logfile' can be a filename or a file object. 'verbosity' specifies
    the verbosity level."""
    if logfile is None:
      raise TypeError,"'logfile' should be a filename or a file object";
    self.set_file(logfile);
    self.verbose = verbose;
    
  def log (self,message,status="",level=0):
    """writes message and optional status, if the specified level is <= the verbosity
    level we were created with""";
    if level <= self.verbose:
      if status:
        self.fileobj.write("%-70s [%s]\n"%(message,status));
      else:
        self.fileobj.write(message+"\n");

  def allocate_tmp_file (self):
    """allocates a temporary file based on the current logfile. Returns None if we were created with a
    file object and not a filename.""";
    if not self.filename:
      return None;
    dirname,fname = os.path.split(os.path.abspath(self.filename));
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
    
  def log_message (self,message,status,level=1):
    _dprint(5,"logging message",level,message,status);
    for logger in self.loggers:
      logger.log(message,status,level);
      
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



def run_files (files,verbosity=10,log_verbosity=40,persist=1,maxjobs=1):
  batchrun = TrutBatchRun(persist=persist,
                loggers=[ TrutLogger(sys.stderr,verbosity),
                          TrutLogger('Trut.log',log_verbosity),
                          TrutLogger('Trut.full.log',999999) ]
              );
  # execute each file in turn, break out on error (unless persist=True)
  for filename in files:
    trutfile = Trut.File(filename,parent=batchrun,maxjobs=maxjobs);
    # make loggers local to that directory
    dirname = os.path.dirname(os.path.abspath(filename));
    loggers = [ TrutLogger(os.path.join(dirname,'trut.log'),log_verbosity),
                TrutLogger(os.path.join(dirname,'trut.full.log'),999999) ];
    batchrun.add_loggers(*loggers);
    trutfile.execute();
    batchrun.remove_loggers(*loggers);
    if batchrun.giveup():
      break;
    
  # this will print a fail/success message
  return batchrun.success();

import sys
import traceback
from Timba import dmi

import Trut

from Trut import _dprint,_dprintf

import TrutTDL

class TrutLogger (object):
  def __init__ (self,fileobj,verbose=0):
    self.fileobj = fileobj;
    self.verbose = verbose;
  def log (self,message,status="",level=0):
    if level <= self.verbose:
      if status:
        self.fileobj.write("%-70s [%s]\n"%(message,status));
      else:
        self.fileobj.write(message+"\n");

class TrutBatchRun (Trut.Unit):
  def __init__ (self,name="",persist=0,loggers=[]):
    Trut.Unit.__init__(self,name);
    self.loggers = loggers;
    self.persist = persist;
    
  def log_message (self,message,status,level=1):
    _dprint(5,"logging message",level,message,status);
    for logger in self.loggers:
      logger.log(message,status,level);



def run_files (files,verbosity=10,log_verbosity=40,persist=1,jobs=1):
  batchrun = TrutBatchRun(persist=persist,
                loggers=[ TrutLogger(sys.stderr,verbosity),
                          TrutLogger(file('trut.log','w'),log_verbosity),
                          TrutLogger(file('trut.full.log','w'),999999) ]
              );
  # execute each file in turn, break out on error (unless persist=True)
  for filename in files:
    Trut.File(filename,parent=batchrun,jobs=jobs).execute();
    if batchrun.giveup():
      break;
    
  # this will print a fail/success message
  return batchrun.success();

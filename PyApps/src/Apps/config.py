#!/usr/bin/python

from ConfigParser import *
import os

_system_files = [ "/usr/local/Timba/%s.conf","/usr/Timba/%s.conf" ];
_user_file = os.environ['HOME']+"/.%s.conf";

class Config (object):
  def __init__ (self,name,section="DEFAULT"):
    self.defsection = section;
    self.syscp = ConfigParser();
    self.syscp.read([ ff%name for ff in _system_files]);
    self.usercp = ConfigParser();
    self.usercp.read([_user_file%name]);
    
  def _get (self,method,option,default=None,section=None,save=True):
    section = section or self.defsection;
    # try user defaults
    try:
      return getattr(self.usercp,method)(section,option);
    except (NoSectionError,NoOptionError):
      pass; 
    # try systemwide
    try:
      return getattr(self.syscp,method)(section,option);
    except (NoSectionError,NoOptionError):
      if default is not None:
        try: self.usercp.add_section(section);
        except DuplicateSectionError: pass;
        self.usercp.set(section,option,default);
        if save:
          self.usercp.write(file(_user_file,"w"));
        return default;
      # no default, so re-raise the error 
      raise;
  
  def set (self,option,value,section=None,save=True):
    section = section or self.defsection;
    # try user defaults
    try:
      self.usercp.add_section(section);
    except DuplicateSectionError: pass;
    self.usercp.set(section,option,default);
    if save:
      self.usercp.write(file(_user_file,"w"));

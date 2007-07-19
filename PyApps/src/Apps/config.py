#!/usr/bin/python

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

from ConfigParser import *
import os
import sys

_system_files = [ 
  "/usr/local/Timba/timba.conf",
  "/usr/Timba/timba.conf",
  "/etc/timba.conf" ];

_user_file = os.environ['HOME']+"/.timba.conf";

class DualConfigParser (object):
  """A dual config parser taking into account both system-wide files
  and user defaults. Any changes are stored in the user defaults."""
  def __init__ (self,section):
    self.defsection = section;
    self.syscp = ConfigParser();
    self.syscp.read(_system_files);
    self.usercp = ConfigParser();
    self.usercp.read([_user_file]);
    if not self.syscp.has_section(section):
      self.syscp.add_section(section);
    if not self.usercp.has_section(section):
      self.usercp.add_section(section);
    
  def _get (self,method,option,default=None,section=None):
    section = section or self.defsection;
    # try user defaults
    try:
      return getattr(self.usercp,method)(section,option);
    except (NoSectionError,NoOptionError):
      error = sys.exc_info()[1]; 
    # try systemwide
    try:
      return getattr(self.syscp,method)(section,option);
    except (NoSectionError,NoOptionError):
      if default is not None:
        self.syscp.set(section,option,str(default));
        return default;
      # no default, so re-raise the error 
      raise error;
      
  def has_option (self,option,section=None):
    section = section or self.defsection;
    return self.syscp.has_option(section,option) or \
      self.usercp.has_option(section,option);
  
  def get (self,option,default=None,section=None):
    return self._get('get',option,default,section);
  def getint (self,option,default=None,section=None):
    return self._get('getint',option,default,section);
  def getfloat (self,option,default=None,section=None):
    return self._get('getfloat',option,default,section=None);
  def getbool (self,option,default=None,section=None):
    return self._get('getboolean',option,default,section);
  
  def set (self,option,value,section=None,save=True):
    section = section or self.defsection;
    value = str(value);
    # try to get option first, and do nothing if no change
    try:
      if self.get(option,section=section) == value:
        return;
    except (NoSectionError,NoOptionError):
      pass;
    # save to user section
    try:
      self.usercp.add_section(section);
    except DuplicateSectionError: pass;
    self.usercp.set(section,option,value);
    if save:
      self.usercp.write(file(_user_file,"w"));
      
Config = None; 
      
def init (name):
  global Config;
  Config = DualConfigParser(name);

if __name__ == '__main__':
  conf = Config('test');
  print 'test1:',conf.get('test1',1);
  print 'test2:',conf.getint('test2',2);
  print 'test3:',conf.getfloat('test3',3.0);
  try:
    print 'test4:',conf.get('test4');
  except:
    print 'test4:',sys.exc_info();
  try:
    print 'test5:',conf.get('test5');
  except:
    print 'test5:',sys.exc_info();
  conf.set('test6','abc');
  conf.set('test7',1);
  conf.set('test8',1.0);
  conf.set('test9',True);
  print 'has test1:',conf.has_option('test1');
  print 'has test4:',conf.has_option('test4');

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

import Trut
import sys
from Trut import _dprint,_dprintf


class TDLScript (Trut.Unit):
  Directives = {};
  """The 'TDL' directive describes a TDL script that will be compiled and, optionally, run""";
  def __init__ (self,name,parent=None):
    if not isinstance(parent,Trut.File):
      raise Trut.ParseError("'TDL' directive must be at global level");
    Trut.Unit.__init__(self,name,parent=parent);
    self._mqs = None;
    self._module = None;  # compiled module
    self._compile_failed = False;
    
  def execute (self):
    # at end of stanza, we compile the script if not yet done so
    if not self._module:
      self.compile_script();
  
  def cleanup (self):
    # terminate meqserver
    if self._mqs:
      _dprint(1,"halting meqserver");
      self._mqs.halt();
      
  def giveup (self):
    """giveup testing if compile failed, or if Unit wants to give up (due to earlier
    errors and no persistency)
    """;
    return self._compile_failed or Trut.Unit.giveup();
  
  def compile_script (self,need_mqs=False):
    """compiles the script, if not already compiled.
    If need_mqs=True, starts a meqserver and builds the tree as well""";
    if not self._module:
      self._compile_failed = True;  # will reset to False if all goes well\
      self.log_progress("compile");
      # start meqserver if required
      if ( need_mqs or int(self.get_option("start_meqserver",0)) ) and not self._mqs:
        from Timba.Apps import meqserver
        # get multithreading option
        mt = int(self.get_option("multithreaded",0));
        if mt>1:
          extra = [ "-mt",str(mt) ];
        else:
          extra = []
        _dprint(1,"starting meqserver",extra);
        self._mqs = meqserver.default_mqs(wait_init=10,extra=extra);
      from Timba.TDL import Compile
      from Timba.TDL import TDLOptions
      # load config file
      tdlconf = self.get_option("tdlconf",".tdl.conf");
      TDLOptions.config.read(tdlconf);
      TDLOptions.init_options(self.name,save=False);
      # compile TDL module
      _dprint(1,"compiling TDL script",self.name);
      try:
        (self._module,ns,msg) = Compile.compile_file(self._mqs,self.name);
      except:
        excinfo = sys.exc_info();
        self.log_exc(level=2,*excinfo);
        self.fail("compile failed");
        excinfo = None;
        return;
      # success
      self.log(msg,level=2);
      self.success("compile");
      self._compile_failed = False;
    pass;
  
class TDLJob (Trut.Unit):
  """The 'Job' directive describes a TDL job to be run.
  It should appear inside a TDLScript stanza""";
  def __init__ (self,name,parent=None):
    if not isinstance(parent,TDLScript):
      raise Trut.ParseError("misplaced 'Job' directive");
    Trut.Unit.__init__(self,name,parent=parent);
    
  def execute (self):
    self.parent.compile_script(need_mqs=True);
    if self.parent.giveup():
      self.success("SKIP");
      return;
    _dprint(1,"running TDL job",self.name);
    jobfunc = getattr(self._module,self.name,None);
    if not callable(jobfunc):
      self.fail("TDL job not found");
    jobfunc(self._mqs,None,wait=True);

Trut.File.Directives['TDL'] = TDLScript;
TDLScript.Directives['Job'] = TDLJob;

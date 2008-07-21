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

from Timba.TDL import *
import Meow
from Meow import Context
from Meow import Jones,ParmGroup,Bookmarks
from Meow.Parameterization import resolve_parameter

class DiagAmplPhase (object):
##  def __init__ (self):
##    self.options = [];
  def __init__ (self,label='',solve_source=None):
    self.tdloption_namespace = label+".diagamplphase";
    subset_opt = TDLOption('subset',"Apply this Jones term to a subset of sources",
        [None],more=str,namespace=self,doc="""Selects a subset of sources to which this 
        Jones term is applied. 'None' applies to all sources.
        You may specify individual indices (0-based) separated by commas or spaces, or ranges, e.g. "M:N" (M to N inclusive), or ":M" (0 to M), or "N:" (N to last).
        Example subset: ":3 5 8 10:12 16:".""");
    self._subset_parser = Meow.Utils.ListOptionParser(minval=0,name="sources");
    subset_opt.set_validator(self._subset_parser.validator);
    self.options = [ subset_opt ];
    self.subset = None;
    self.solve_source=solve_source;

  def compile_options (self):
    return self.options;

##  def compute_jones (self,nodes,stations=None,tags=None,label='',**kw):
##    stations = stations or Context.array.stations();
##    g_ampl_def = Meow.Parm(1);
##    g_phase_def = Meow.Parm(0);
##    nodes = Jones.gain_ap_matrix(nodes,g_ampl_def,g_phase_def,tags=tags,series=stations);

##    # make parmgroups for phases and gains
##    self.pg_phase = ParmGroup.ParmGroup(label+"_phase",
##                    nodes.search(tags="solvable phase"),
##                    table_name="%s_phase.mep"%label,bookmark=4);
##    self.pg_ampl  = ParmGroup.ParmGroup(label+"_ampl",
##                    nodes.search(tags="solvable ampl"),
##                    table_name="%s_ampl.mep"%label,bookmark=4);

##    # make solvejobs
##    ParmGroup.SolveJob("cal_"+label+"_phase","Calibrate %s phases"%label,self.pg_phase);
##    ParmGroup.SolveJob("cal_"+label+"_ampl","Calibrate %s amplitudes"%label,self.pg_ampl);

##    return nodes;

  def compute_jones (self,nodes,sources,stations=None,tags=None,label='',**kw):
    stations = stations or Context.array.stations();
    # figure out which sources to apply to
    if self.subset:
      srclist = self._subset_parser.parse_list(self.subset);
      sources = [ sources[i] for i in srclist ];
      
    g_ampl_def = Meow.Parm(1);
    g_phase_def = Meow.Parm(0);
    # loop over sources
    #print "tags",tags
    for srci,src in enumerate(sources):
      #print  srci,src,self.solve_source,(srci==self.solve_source)
      if (self.solve_source or self.solve_source==0) and not(srci==self.solve_source):
        #print "not solvable",src;
        jones = Jones.gain_ap_matrix(nodes(src),g_ampl_def,g_phase_def,tags=tags,series=stations,solvable=False);
      else:
        #print "solvable",src,self.solve_source;
        jones = Jones.gain_ap_matrix(nodes(src),g_ampl_def,g_phase_def,tags=tags,series=stations);
    
    # make parmgroups for phases and gains
    self.pg_phase = ParmGroup.ParmGroup(label+"_phase",
                    nodes.search(tags="solvable phase"),
                    table_name="%s_phase.mep"%label,bookmark=4);
    self.pg_ampl  = ParmGroup.ParmGroup(label+"_ampl",
                    nodes.search(tags="solvable ampl"),
                    table_name="%s_ampl.mep"%label,bookmark=4);
    # make parmgroups for phases and gains
    self.pg_phasen = ParmGroup.ParmGroup(label+"_phase_other",
                    nodes.search(tags="nonsolvable phase"),
                    table_name="%s_phase.mep"%label,bookmark=4);
    self.pg_ampln  = ParmGroup.ParmGroup(label+"_ampl_other",
                    nodes.search(tags="nonsolvable ampl"),
                    table_name="%s_ampl.mep"%label,bookmark=4);


##    # make solvejobs
##    ParmGroup.SolveJob("cal_"+label+"_phase","Calibrate %s phases"%label,self.pg_phase);
##    ParmGroup.SolveJob("cal_"+label+"_ampl","Calibrate %s amplitudes"%label,self.pg_ampl);
    return nodes;



class FullRealImag (object):
  def __init__ (self,label=''):
    self.tdloption_namespace = label+".fullrealimag";
    subset_opt = TDLOption('subset',"Apply this Jones term to a subset of sources",
        [None],more=str,namespace=self,doc="""Selects a subset of sources to which this 
        Jones term is applied. 'None' applies to all sources.
        You may specify individual indices (0-based) separated by commas or spaces, or ranges, e.g. "M:N" (M to N inclusive), or ":M" (0 to M), or "N:" (N to last).
        Example subset: ":3 5 8 10:12 16:".""");
    self._subset_parser = Meow.Utils.ListOptionParser(minval=0,name="sources");
    subset_opt.set_validator(self._subset_parser.validator);
    self.options = [ subset_opt ];
    self.subset = None;

  def compile_options (self):
    return self.options;

  def compute_jones (self,jones,sources,stations=None,tags=None,label='',**kw):
    stations = stations or Context.array.stations();
    # figure out which sources to apply to
    if self.subset:
      print "SUBSET",self.subset
      srclist = self._subset_parser.parse_list(self.subset);
      print "srclist",srclist;
      sources = [ sources[i] for i in srclist ];
    # create parm definitions for each jones element
    tags = NodeTags(tags) + "solvable";
    diag_real = Meq.Parm(1,tags=tags+"diag real");
    diag_imag = Meq.Parm(0,tags=tags+"diag imag");
    offdiag_real = Meq.Parm(0,tags=tags+"offdiag real");
    offdiag_imag = Meq.Parm(0,tags=tags+"offdiag imag");
    # loop over sources
    for src in sources:
      # now loop to create nodes
      for p in stations:
        jj = jones(src,p);
        jj << Meq.Matrix22(
          jj("xx") << Meq.ToComplex(
              jj("rxx") << diag_real,
              jj("ixx") << diag_imag
          ),
          jj("xy") << Meq.ToComplex(
              jj("rxy") << offdiag_real,
              jj("ixy") << offdiag_imag
          ),
          jj("yx") << Meq.ToComplex(
              jj("ryx") << offdiag_real,
              jj("iyx") << offdiag_imag
          ),
          jj("yy") << Meq.ToComplex(
              jj("ryy") << diag_real,
              jj("iyy") << diag_imag
          )
        );
    # make parmgroups for diagonal and off-diagonal terms
    self.pg_diag  = ParmGroup.ParmGroup(label+"_diag",
            [ jones(src,p,zz) for src in sources for p in stations 
                              for zz in "rxx","ixx","ryy","iyy" ],
            table_name="%s_diag.mep"%label,bookmark=False);
    self.pg_offdiag  = ParmGroup.ParmGroup(label+"_offdiag",
            [ jones(src,p,zz) for src in sources for p in stations 
                              for zz in "rxy","ixy","ryx","iyx" ],
            table_name="%s_offdiag.mep"%label,bookmark=False);

    # make bookmarks
    Bookmarks.make_node_folder("%s diagonal terms"%label,
      [ jones(src,p,zz) for src in sources  
        for p in stations for zz in "xx","yy" ],sorted=True);
    Bookmarks.make_node_folder("%s off-diagonal terms"%label,
      [ jones(src,p,zz) for src in sources  
        for p in stations for zz in "xy","yx" ],sorted=True);

##    # make solvejobs
##    ParmGroup.SolveJob("cal_"+label+"_diag","Calibrate %s diagonal terms"%label,self.pg_diag);
##    ParmGroup.SolveJob("cal_"+label+"_offdiag","Calibrate %s off-diagonal terms"%label,self.pg_offdiag);

    return jones;

# MXM_demo_solve.py:

# Demonstrates the following MeqTree features:
# Simple Tree to solve a parameter 

# Tips:
#For more parameter options, see demo_parm.py


 
#********************************************************************************
# Initialisation:
#********************************************************************************

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
from Timba.Meq import meq
from PyParmTable import *

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []

old_table='sources.mep'
parmname = '*';
global t;

def _define_forest (ns, **kwargs):
   """Definition of ParmTable"""
   global t;

   # create a ParmTable, you have to do this in define_forest since the class creates some trees it needs for plotting etcetera.
   # parmname can be any pattern, if fit =True, also some solvertree will be created, this allows to fit lower ranked funklets.
   t=ParmTable(name= old_table,ns = ns,parms = parmname,fit=True);
   # after you have created the ParmTable some new root nodes and bookmarks are available.
   
   return True



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************


def _tdl_job_table1_inspector (mqs, parent):
   #start the inspector, open the Inspector bookmarks to see the results of plotting and fitting
   result = t.Inspector(mqs,parent);
       

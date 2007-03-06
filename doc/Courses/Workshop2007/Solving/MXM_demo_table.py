# MXM_demo_solve.py:

# Demonstrates the following MeqTree features:
# Simple Tree to solve a parameter 

# Tips:
#For more parameter options, see demo_parm.py


 
#********************************************************************************
# Initialisation:
#********************************************************************************

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
       

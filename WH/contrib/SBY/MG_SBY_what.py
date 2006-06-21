# MG_SBY_resample.py


#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
#********************************************************************************


#% $Id$ 

#
# Copyright (C) 2006
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Trees import TDL_Cohset
from Timba.Contrib.JEN import MG_JEN_Cohset
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Trees import JEN_inarg

from Timba.LSM.LSM import *

Settings.forest_state.cache_policy = 1;

Settings.orphans_are_roots = True;


######## initialization of the MG dict
MG=JEN_inarg.init('MG_SBY_what')
MG_JEN_exec.inarg_ms_name(MG)
MG_JEN_exec.inarg_tile_size(MG)
MG_JEN_Cohset.inarg_parmtable(MG)
#JEN_inarg.define(MG,'tile_size',10)
JEN_inarg.define(MG,'ms_name','what1.ms')
JEN_inarg.define(MG,'polrep','linear')
JEN_inarg.define(MG,'stations',range(15))
JEN_inarg.define(MG,'label','foo')
#JEN_inarg.define(MG,'predict_column','CORRECTED_DATA')
#JEN_inarg.define(MG,'output_col','CORRECTED_DATA')


inarg = MG_JEN_exec.stream_control(_getdefaults=True, slave=True)
print inarg['./MG_JEN_exec.stream_control()'].keys()
JEN_inarg.modify(inarg,
                 tile_size=20,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 ms_name='what1.ms',
                 )
JEN_inarg.modify(inarg,
                 channel_start_index=3,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 channel_end_index=9,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 channel_increment=1,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 stations=range(15),
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 predict_col='CORRECTED_DATA',
                 _JEN_inarg_option=None)

inarg['./MG_JEN_exec.stream_control()']['ms_name']="what1.ms"
inarg['./MG_JEN_exec.stream_control()']['tile_size']=20
print inarg['./MG_JEN_exec.stream_control()']['ms_name']


JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)
JEN_inarg.modify(inarg,
                 _JEN_inarg_option=None)
JEN_inarg.attach(MG, inarg)



#----------------------------------------------------------------------------------


inarg = MG_JEN_Cohset.Jones(_getdefaults=True, slave=True)
JEN_inarg.modify(inarg,
                 Jsequence=['JJones'],
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 parmtable='fullwhat.mep',
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 tdeg_Jreal=0,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 fdeg_Jreal=0,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 subtile_size_Jreal=5,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
		   all4_always=[14],
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 diagonal_only=True,
                 _JEN_inarg_option=None)
JEN_inarg.attach(MG, inarg)


inarg = MG_JEN_Cohset.predict(_getdefaults=True, slave=True)
JEN_inarg.modify(inarg,
                 _JEN_inarg_option=None)
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.insert_solver(_getdefaults=True, slave=True)
JEN_inarg.modify(inarg,
                 solvegroup=['JJones'],
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 num_cells=False,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 rmin=1,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 rmax=1500,
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 num_iter=15,
                 _JEN_inarg_option=None)
JEN_inarg.attach(MG, inarg)

#-------------------------------------------------------------------------

inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)
JEN_inarg.modify(inarg,
                 ms_name='what1.ms',
                 _JEN_inarg_option=None)
JEN_inarg.modify(inarg,
                 _JEN_inarg_option=None)
JEN_inarg.attach(MG, inarg)


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)



print MG
def _define_forest (ns):
   global MG
   
   # create Cohset
   cohset=TDL_Cohset.Cohset(label=MG['label'],polrep=MG['polrep'],stations=MG['stations'])
   cohset.display()
   splist=MG_JEN_Cohset.make_spigots(ns,cohset, MS_corr_index=[0,1,2,3], stations=MG['stations'])
  
   # create the Jones set
   #jset=MG_JEN_Cohset.Jones(Jsequence=['JJones'],_inage=MG)
   #print "Jones set are"
   #for jnode in jset:
   # print jnode.name

   # load the LSM
   lsm=LSM()
   lsm.load("cyga.lsm",ns)
   # get the PUnits (two)
   plist=lsm.queryLSM(count=2)
   punit=plist[0]
   sp=punit.getSP()
   sp.ParmSet.parmtable('foo.mep')
   sp.display()
   jset=MG_JEN_Cohset.Jones(ns,Sixpack=sp, stations=MG['stations'], Jsequence=['JJones'], all4_always='WSRT/WHAT', _inarg=MG)
   predicted=MG_JEN_Cohset.predict(ns,Sixpack=sp,Joneset=jset, stations=MG['stations'], _inarg=MG)

   punit=plist[1]
   sp=punit.getSP()
   sp.ParmSet.parmtable('foo.mep')
   jset1=MG_JEN_Cohset.Jones(ns,Sixpack=sp, stations=MG['stations'], Jsequence=['JJones'], all4_always='WSRT/WHAT',_inarg=MG)
   predicted1=MG_JEN_Cohset.predict(ns,Sixpack=sp,Joneset=jset1, stations=MG['stations'], _inarg=MG)
   predicted.add(ns,predicted1)

   MG_JEN_Cohset.insert_solver(ns,measured=cohset,predicted=predicted, redun=False, num_cells=None,stations=MG['stations'],\
                           _inarg=MG)



   # make the sinks
   sinklist=MG_JEN_Cohset.make_sinks(ns,cohset, _inarg=MG)
 
   ns.Resolve()



### this is a copy from oleg
def create_inputrec(msname, tile_size=1500,short=False):
    rec = record();
    rec.ms_name          = msname
    rec.data_column_name = 'DATA'
    rec.tile_size        = tile_size
    rec.selection = record(channel_start_index=0,
                             channel_end_index=9,
                             channel_increment=1,
#                             selection_string='ANTENNA1<6 && ANTENNA2<6')
#                             selection_string='TIME_CENTROID < 4472026000')
                             selection_string='')
    #rec.selection.selection_string = 'TIME_CENTROID < 4472026000';
    rec = record(ms=rec);
    rec.python_init='MAB_read_msvis_header.py';
    return rec;



def _test_forest (mqs, parent):
    global MG
    # execute the tree
    MG_JEN_exec.spigot2sink(mqs, parent,ctrl=MG)


def _tdl_job_ev_parms_over_reference_domain (mqs,parent):
  """Executes the 'verifier' node over the saved reference domain.
Assuming this is successful, you may examine the children of the verifier
node to compare past and current solutions.""";
  global MG
  msname   = 'what1.ms'
  inputrec = create_inputrec(msname,tile_size=4500)
  req = meq.request();
  req.input  = inputrec;
  mqs.clearcache('Cohset_fullDomainMux');
  mqs.execute('Cohset_fullDomainMux',req,wait=(parent is None));
  pass

# These test routines do not require the meqbrowser, or even the meqserver.
# Just run them by enabling the required one (if 1:), and invoking python:
#      > python MG_JEN_template.py

if __name__ == '__main__':
 ns=NodeScope()
 _define_forest(ns)


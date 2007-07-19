# MG_JEN_cps.py

# Short description:
#   Script for reducing Central Point Source (cps) data:

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 21 jan 2006: creation (starting from MG_JEN_Cohset.py

# Copyright: The MeqTree Foundation 

#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble *********************************************
#********************************************************************************
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
# from Timba.Meq import meq

from numarray import *
from copy import deepcopy

from Timba.Contrib.JEN.util import JEN_inarg
from Timba.Contrib.JEN.util import JEN_inargGui
from Timba.Contrib.JEN.util import TDL_Cohset
from Timba.Contrib.JEN.util import TDL_Joneset
# from Timba.Contrib.JEN.util import TDL_MSauxinfo
# from Timba.Contrib.JEN.util import TDL_Sixpack

from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Cohset
from Timba.Contrib.JEN import MG_JEN_Sixpack

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

# from Timba.Contrib.JEN import MG_JEN_twig
# from Timba.Contrib.JEN import MG_JEN_dataCollect
# from Timba.Contrib.JEN import MG_JEN_historyCollect
# from Timba.Contrib.JEN import MG_JEN_flagger


try:
    from qt import *
except:
    pass;


#********************************************************************************
#********************************************************************************
#****************** PART II: Definition of importable functions *****************
#********************************************************************************
#********************************************************************************



def predefine_inargs():
   """Modify the default inarg record (MG) to predefined inarg record files"""
   global MG
   print '\n** Predefining',MG['script_name'],'inarg records...\n'
   cps_inspect_DATA(deepcopy(MG), trace=True)
   cps_inspect_CORRECTED_DATA(deepcopy(MG), trace=True)
   cps_GJones(deepcopy(MG), trace=True)
   cps_Gphase(deepcopy(MG), trace=True)
   cps_Ggain(deepcopy(MG), trace=True)
   cps_GDJones(deepcopy(MG), trace=True)
   cps_JJones(deepcopy(MG), trace=True)
   cps_BJones(deepcopy(MG), trace=True)
   cps_DJones(deepcopy(MG), trace=True)
   cps_stokesI(deepcopy(MG), trace=True)
   print '\n** Predefined',MG['script_name'],'inarg records (incl. protected)\n'
   return True

def describe_inargs():
   """Collate descriptions of all available predefined inarg record(s)"""
   ss = JEN_inarg.describe_inargs_start(MG)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_inspect_DATA', cps_inspect_DATA.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_inspect_CORRECTED_DATA',
                                         cps_inspect_CORRECTED_DATA.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_GJones', cps_GJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_Gphase', cps_Gphase.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_Ggain', cps_Ggain.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_GDJones', cps_GDJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_JJones', cps_JJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_BJones', cps_BJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_DJones', cps_DJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_cps_stokesI', cps_stokesI.__doc__)
   return JEN_inarg.describe_inargs_end(ss, MG)

#--------------------------------------------------------------------

def cps_GJones(inarg, trace=True):
   """Predefined inarg record for solving for GJones on a Central Point Source"""
   filename = 'MG_JEN_cps_GJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_GJones.__doc__)
   JEN_inarg.modify(inarg,
                    Jsequence=['GJones'],
                    solvegroup=['GJones'],
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.per_timeslot(inarg)
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def cps_Gphase(inarg, trace=True):
   """Predefined inarg record for solving for Gphase on a Central Point Source"""
   filename = 'MG_JEN_cps_Gphase'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_Gphase.__doc__)
   JEN_inarg.modify(inarg,
                    Jsequence=['GJones'],
                    solvegroup=['Gphase'],
                    condeq_unop='Arg',
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.per_timeslot(inarg)
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def cps_Ggain(inarg, trace=True):
   """Predefined inarg record for solving for Ggain on a Central Point Source"""
   filename = 'MG_JEN_cps_Ggain'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_Ggain.__doc__)
   JEN_inarg.modify(inarg,
                    Jsequence=['GJones'],
                    solvegroup=['Ggain'],
                    condeq_unop='Abs',
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.per_timeslot(inarg)
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def cps_GDJones(inarg, trace=True):
   """Predefined inarg record for solving for GDJones on a Central Point Source"""
   filename = 'MG_JEN_cps_GDJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_GDJones.__doc__)
   JEN_inarg.modify(inarg,
                    Jsequence=['GJones','DJones_WSRT'],
                    solvegroup=['GJones','DJones'],
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.callback_punit(inarg, 'QU')
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def cps_JJones(inarg, trace=True):
   """Predefined inarg record for solving for JJones on a Central Point Source"""
   filename = 'MG_JEN_cps_JJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_JJones.__doc__)
   JEN_inarg.modify(inarg,
                    Jsequence=['JJones'],
                    solvegroup=['JJones'],
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.callback_punit(inarg, 'QUV')
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def cps_BJones(inarg, trace=True):
   """Predefined inarg record for solving for BJones on a Central Point Source"""
   filename = 'MG_JEN_cps_BJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_BJones.__doc__)
   JEN_inarg.modify(inarg,
                    data_column_name='CORRECTED_DATA',
                    Jsequence=['BJones'],
                    solvegroup=['BJones'],
                    tdeg_Breal=1, fdeg_Breal=6,
                    tdeg_Bimag='@tdeg_Breal',
                    fdeg_Bimag='@fdeg_Breal',
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def cps_DJones(inarg, trace=True):
   """Predefined inarg record for solving for DJones on a Central Point Source"""
   filename = 'MG_JEN_cps_DJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_DJones.__doc__)
   JEN_inarg.modify(inarg,
                    data_column_name='CORRECTED_DATA',
                    Jsequence=['DJones_WSRT'],
                    solvegroup=['DJones'],
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.callback_punit(inarg, 'QU')
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def cps_stokesI(inarg, trace=True):
   """Predefined inarg record for solving for stokesI on a Central Point Source"""
   filename = 'MG_JEN_cps_stokesI'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_stokesI.__doc__)
   JEN_inarg.modify(inarg,
                    data_column_name='CORRECTED_DATA',
                    solvegroup=['stokesI'],
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def cps_inspect_DATA(inarg, trace=True):
   """Predefined inarg record for inspecting the MS DATA column"""
   filename = 'MG_JEN_cps_inspect_DATA'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_inspect_DATA.__doc__)
   JEN_inarg.modify(inarg,
                    insert_solver=False,
                    tile_size=1,
                    predict_column=None,
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def cps_inspect_CORRECTED_DATA(inarg, trace=True):
   """Predefined inarg record for inspecting a MS CORRECTED_DATA column"""
   filename = 'MG_JEN_cps_inspect_CORRECTED_DATA'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, cps_inspect_CORRECTED_DATA.__doc__)
   JEN_inarg.modify(inarg,
                    insert_solver=False,
                    tile_size=1,
                    data_column_name='CORRECTED_DATA',
                    predict_column=None,
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True







#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************
#********************************************************************************

def _description():
    """
    Description of the input argument record: MG_JEN_cps_xxx.inarg
    (to be used with the MeqTree TDL stript MG_JEN_cps.py) 
    
    ....

    --------------------------------------------------------------------------
    General description of the MeqTree TDL script MG_JEN_cps.py:

    The MG_JEN_cps.py script is the basis for a range of uv-data operations
    that require only a Central Point Source (cps) as a selfcal model. This is
    particularly useful for reducing calibrator observations, i.e. fields with
    a strong point source with known parameters, in the centre of the field.
    But it can also be used for initial calibration of observations that have
    significant other sources in the field (but a dominating point-like source
    in the centre.


    * The selfcal model is a point source in the centre of the field.
        A range of source models for standard calibrators (e.g. 3c147 etc)
        is available, and also some customised source models (for experimentation)

    * uvplane_effect=True: All instrumental MeqParms have qualifier q=uvp.
        The uv-data are read from the MS DATA column
        and written to the MS CORRECTED_DATA column

    * In order to minimises contamination from other sources on the solution:
        - It solves for MeqParms that vary slowly in time, over large domains.
        - The short baselines are ignored (e.g. rmin=150m)


    Different operations may be specified by loading (and editing) socalled
    'inarg' records from files (like this one). These contain input arguments
    for generating a suitable MeqTree forest for the desired operation.


    --------------------------------------------------------------------------
    Brief descriptions of the various sub-modules:

    """
    return True

def default_inarg ():
    """This default inarg record does nothing specific in its present form.
    Of course it may be edited to create (or modify) a wide range of Local
    Sky Models. But it is often more convenient to use one of the predefined
    inarg records for this TDL script as a starting point (use Open).
    """
    return True



#----------------------------------------------------------------------------------------------------
# Intialise the MG control record with some overall arguments 
#----------------------------------------------------------------------------------------------------

MG = JEN_inarg.init('MG_JEN_cps', description=_description.__doc__,
                    inarg_specific=default_inarg.__doc__)
JEN_inarg.available_inargs(MG, describe_inargs())


JEN_inarg.define (MG, 'insert_solver', tf=True,
                  help='if True, insert a solver')
JEN_inarg.define (MG, 'insert_flagger', tf=False,
                  help='if True, insert a flagger')

# Define some overall arguments:
MG_JEN_Cohset.inarg_Cohset_common (MG, last_changed='d30jan2006')
JEN_inarg.modify(MG,
                 # A uvplane effect (q=uvp) is valid for the entire field
                 # (These are used by Cohset.precorrect()....
                 # parmtable name...?
                 uvplane_effect=True,
                 # Use large 'snippet' domains to minimise peeling contamination: 
                 # tile_size=100,
                 _JEN_inarg_option=None)     


#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

inarg = MG_JEN_exec.stream_control(_getdefaults=True, slave=True)
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)  
JEN_inarg.attach(MG, inarg)


#----------------------------------------------------------------------------------------------------
# Operations on the raw uv-data:
#----------------------------------------------------------------------------------------------------

JEN_inarg.separator(MG, 'operations on input uv-data')

# inarg = MG_JEN_Cohset.insert_flagger(_getdefaults=True) 
# JEN_inarg.attach(MG, inarg)
   

#----------------------------------------------------------------------------------------------------
# Insert a solver:
#----------------------------------------------------------------------------------------------------

JEN_inarg.separator(MG, 'insert a solver')

# inarg = MG_JEN_Sixpack.newstar_source(_getdefaults=True) 
inarg = MG_JEN_Sixpack.get_Sixpack(_getdefaults=True) 
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.Jones(_getdefaults=True, slave=True) 
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.predict(_getdefaults=True, slave=True)  
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.insert_solver(_getdefaults=True, slave=True) 
JEN_inarg.attach(MG, inarg)
                 
#----------------------------------------------------------------------------------------------------
# Operations on the processed uv-data:
#----------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)   
JEN_inarg.attach(MG, inarg)
                 




#====================================================================================
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)



#********************************************************************************
#********************************************************************************
#***************** PART IV: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _tdl_predefine (mqs, parent, **kwargs):
    res = True
    if parent:
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        rr = []
        rr.append(dict(prompt='predefine inargs', callback=predefine_inargs))
        try:
            igui = JEN_inargGui.ArgBrowser(parent, externalMenuItems=rr)
            igui.input(MG, set_open=False)
            res = igui.exec_loop()
            if res is None:
                raise RuntimeError("Cancelled by user");
        finally:
            QApplication.restoreOverrideCursor()
    return res




#**************************************************************************

def _define_forest (ns, **kwargs):
    """See _description()"""

    # The MG may be passed in from _tdl_predefine():
    # In that case, override the global MG record.
    global MG
    if len(kwargs)>1: MG = kwargs

    # Perform some common functions, and return an empty list (cc=[]):
    cc = MG_JEN_exec.on_entry (ns, MG)

    # Make MeqSpigot nodes that read the MS:
    global Cohset
    Cohset = TDL_Cohset.Cohset(label=MG['script_name'],
                               polrep=MG['polrep'],
                               stations=MG['stations'])
    MG_JEN_Cohset.make_spigots(ns, Cohset, _inarg=MG)


    if False and MG['insert_flagger']:
        MG_JEN_Cohset.insert_flagger (ns, Cohset, **MG)
        MG_JEN_Cohset.visualise (ns, Cohset)
        MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')


    if MG['insert_solver']:
        # Sixpack = MG_JEN_Sixpack.newstar_source(ns, _inarg=MG)
        Sixpack = MG_JEN_Sixpack.get_Sixpack(ns, _inarg=MG)
        Joneset = MG_JEN_Cohset.Jones(ns, Sixpack=Sixpack, _inarg=MG)
        predicted = MG_JEN_Cohset.predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG)
        MG_JEN_Cohset.insert_solver (ns, measured=Cohset, predicted=predicted, _inarg=MG)

    # Make MeqSink nodes that write the MS:
    sinks = MG_JEN_Cohset.make_sinks(ns, Cohset, _inarg=MG)
    cc.extend(sinks)

    # Finished: 
    return MG_JEN_exec.on_exit (ns, MG, cc)




#********************************************************************************
#********************************************************************************
#*******************  PART V: Forest execution routine(s) ***********************
#********************************************************************************
#********************************************************************************



def _tdl_job_execute (mqs, parent):
   """Execute the tree""" 
   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG)
   return True

def _tdl_job_execute_plus (mqs, parent):
   """Execute the tree, followed by fullDomainMux()""" 
   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG)
   MG_JEN_exec.fullDomainMux(mqs, parent, ctrl=MG)
   return True


def _tdl_job_fullDomainMux (mqs, parent):
   """Special for post-visualisation""" 
   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.fullDomainMux(mqs, parent, ctrl=MG)
   return True


#------------------------------------------------------------------------------

def _tdl_job_display_Cohset (mqs, parent):
   """Display the Cohset object used to generate this tree""" 
   Cohset.display(MG['script_name'], full=True)
   return True

def _tdl_job_display_Cohset_ParmSet (mqs, parent):
   """Display the Cohset.ParmSet object used to generate this tree""" 
   Cohset.ParmSet.display(MG['script_name'], full=True)
   return True

def _tdl_job_display_Cohset_Joneset (mqs, parent):
   """Display the Cohset.Joneset() object used to generate this tree""" 
   Cohset.Joneset().display(MG['script_name'], full=True)
   return True




#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routine(s) ***********************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
    print '\n*******************\n** Local test of:',MG['script_name'],':\n'

    # This is the default:
    if 0:
       MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest, recurse=3)

    # This is the place for some specific tests during development.
    ns = NodeScope()
    nsim = ns.Subscope('_')
    stations = range(0,3)
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    cs = TDL_Cohset.Cohset(label='test', scops=MG['script_name'], ifrs=ifrs)

    if 1:
        igui = JEN_inargGui.ArgBrowser()
        igui.input(MG, set_open=False)
        igui.launch()
       
    if 0:   
       cs.display('initial')
       
    if 0:
       cs.spigots (ns)

    if 0:
       punit = 'unpol'
       # punit = '3c147'
       # punit = 'RMtest'
       Sixpack = punit2Sixpack(ns, punit)

           
    if 0:
        display_first_subtree(cs)
        cs.display('final result')

    # ............
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************





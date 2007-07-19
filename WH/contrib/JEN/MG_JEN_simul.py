# MG_JEN_simul.py

# Short description:
#   Script for putting simulated visibilities into an existing MS:

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 27 feb 2006: creation (starting from MG_JEN_cps.py
# - 02 apr 2006: completely reworked it

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

import os

from numarray import *
from copy import deepcopy

from Timba.Contrib.JEN.util import JEN_inarg
from Timba.Contrib.JEN.util import JEN_inargGui
from Timba.Contrib.JEN.util import TDL_Cohset
from Timba.Contrib.JEN.util import TDL_Joneset

from Timba.LSM.LSM import *
from Timba.LSM.LSM_GUI import *

from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Cohset
# from Timba.Contrib.JEN import MG_JEN_Sixpack
from Timba.Contrib.JEN import MG_JEN_lsm

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state


try:
    from qt import *
except:
    pass;


#********************************************************************************
#********************************************************************************
#****************** PART II: Definition of importable functions *****************
#********************************************************************************
#********************************************************************************




#===============================================================================
# Predefined inarg records:
#===============================================================================

def predefine_inargs():
   """Modify the default inarg record (MG) to predefined inarg record files"""
   global MG
   print '\n** Predefining',MG['script_name'],'inarg records...\n'
   simul_GJones(deepcopy(MG), trace=True)
   simul_BJones(deepcopy(MG), trace=True)
   simul_DJones(deepcopy(MG), trace=True)
   simul_JJones(deepcopy(MG), trace=True)
   simul_EJones(deepcopy(MG), trace=True)
   simul_stokesI(deepcopy(MG), trace=True)
   print '\n** Predefined',MG['script_name'],'inarg records (incl. protected)\n'
   return True


def describe_inargs():
   """Collate descriptions of all available predefined inarg record(s)"""
   ss = JEN_inarg.describe_inargs_start(MG)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_simul_GJones', simul_GJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_simul_BJones', simul_BJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_simul_DJones', simul_DJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_simul_JJones', simul_JJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_simul_EJones', simul_EJones.__doc__)
   ss = JEN_inarg.describe_inargs_append(ss, 'MG_JEN_simul_stokesI', simul_stokesI.__doc__)
   return JEN_inarg.describe_inargs_end(ss, MG)

#--------------------------------------------------------------------

def simul_GJones(inarg, trace=True):
   """Predefined inarg record for simulating with GJones corruption"""
   filename = 'MG_JEN_simul_GJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, simul_GJones.__doc__)
   JEN_inarg.modify(inarg,
                    Jsequence=['GJones'],
                    _JEN_inarg_option=dict(trace=trace, qual='simul_uvp'))     
   JEN_inarg.modify(inarg,
                    Jsequence=['GJones'],
                    _JEN_inarg_option=dict(trace=trace, qual='solve_uvp'))     
   JEN_inarg.modify(inarg,
                    insert_solver=True,
                    solvegroup=['GJones'],
                    parmtable='simul_GJones',
                    num_iter=2,
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True

#--------------------------------------------------------------------

def simul_BJones(inarg, trace=True):
   """Predefined inarg record for simulating with BJones corruption"""
   filename = 'MG_JEN_simul_BJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, simul_BJones.__doc__)
   JEN_inarg.modify(inarg,
                    Jsequence=['BJones'],
                    _JEN_inarg_option=dict(trace=trace, qual='simul_uvp'))     
   JEN_inarg.modify(inarg,
                    Jsequence=['BJones'],
                    _JEN_inarg_option=dict(trace=trace, qual='solve_uvp'))     
   JEN_inarg.modify(inarg,
                    insert_solver=True,
                    solvegroup=['BJones'],
                    parmtable='simul_BJones',
                    num_iter=2,
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True


#--------------------------------------------------------------------

def simul_JJones(inarg, trace=True):
   """Predefined inarg record for simulating with JJones corruption"""
   filename = 'MG_JEN_simul_JJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, simul_JJones.__doc__)
   JEN_inarg.modify(inarg,
                    Jsequence=['JJones'],
                    _JEN_inarg_option=dict(trace=trace, qual='simul_uvp'))     
   JEN_inarg.modify(inarg,
                    Jsequence=['JJones'],
                    _JEN_inarg_option=dict(trace=trace, qual='solve_uvp'))     
   JEN_inarg.modify(inarg,
                    insert_solver=True,
                    solvegroup=['JJones'],
                    parmtable='simul_JJones',
                    num_iter=2,
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True


#--------------------------------------------------------------------

def simul_DJones(inarg, trace=True):
   """Predefined inarg record for simulating with DJones corruption"""
   filename = 'MG_JEN_simul_DJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, simul_DJones.__doc__)
   JEN_inarg.modify(inarg,
                    Jsequence=['DJones_WSRT'],
                    _JEN_inarg_option=dict(trace=trace, qual='simul_uvp'))     
   JEN_inarg.modify(inarg,
                    Jsequence=['DJones_WSRT'],
                    _JEN_inarg_option=dict(trace=trace, qual='solve_uvp'))     
   JEN_inarg.modify(inarg,
                    insert_solver=True,
                    solvegroup=['DJones'],
                    parmtable='simul_DJones',
                    num_iter=2,
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.callback_punit(inarg, 'QU')
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True


#--------------------------------------------------------------------

def simul_EJones(inarg, trace=True):
   """Predefined inarg record for simulating with EJones corruption"""
   filename = 'MG_JEN_simul_EJones'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, simul_EJones.__doc__)
   JEN_inarg.modify(inarg,
                    test_pattern='grid',
                    insert_solver=True,
                    use_same_LSM=False,
                    saveAs='<automatic>',
                    solvegroup=['EJones'],
                    # parmtable='simul_EJones',
                    num_iter=2,
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.modify(inarg,
                    taper=None,
                    _JEN_inarg_option=dict(trace=trace, qual='simul'))     
   JEN_inarg.modify(inarg,
                    taper=None,
                    _JEN_inarg_option=dict(trace=trace, qual='solve'))     
   JEN_inarg.modify(inarg,
                    Jsequence=['EJones_WSRT'],
                    _JEN_inarg_option=dict(trace=trace, qual='simul_imp'))     
   JEN_inarg.modify(inarg,
                    Jsequence=['EJones_WSRT'],
                    _JEN_inarg_option=dict(trace=trace, qual='solve_imp'))     
   JEN_inarg.save(inarg, filename, trace=trace)
   JEN_inarg.save(inarg, filename, protected=True, trace=trace)
   return True


#--------------------------------------------------------------------

def simul_stokesI(inarg, trace=True):
   """Predefined inarg record for simulating with EJones corruption,
   and solving for the stokesI fluxes of the 3x3 test-sources."""
   filename = 'MG_JEN_simul_stokesI'
   if trace: print '\n** predefine inarg record:',filename
   JEN_inarg.specific(inarg, simul_stokesI.__doc__)
   JEN_inarg.modify(inarg,
                    test_pattern='grid',
                    # relpos='tlq',
                    insert_solver=True,
                    use_same_LSM=False,
                    saveAs='<automatic>',
                    solvegroup=['stokesI'],
                    # parmtable='simul_stokesI',
                    num_iter=2,
                    _JEN_inarg_option=dict(trace=trace))     
   JEN_inarg.modify(inarg,
                    taper=1.0,
                    _JEN_inarg_option=dict(trace=trace, qual='simul'))     
   JEN_inarg.modify(inarg,
                    taper=None,
                    _JEN_inarg_option=dict(trace=trace, qual='solve'))     
   JEN_inarg.modify(inarg,
                    Jsequence=['EJones_WSRT'],
                    _JEN_inarg_option=dict(trace=trace, qual='simul_imp'))     
   JEN_inarg.modify(inarg,
                    Jsequence=['stokesI_WSRT'],
                    _JEN_inarg_option=dict(trace=trace, qual='solve_imp'))     
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
    -------------------------------------------------------------
    General description of the MeqTree TDL script MG_JEN_simul.py
    -------------------------------------------------------------

    The MG_JEN_simul.py script is used to put simulated visibilities into the
    CORRECTED_DATA column of an existing Measurement Set (MS). The original DATA
    in the MS are untouched. The advantage of this approach is that it is not
    necessary to specify pointing centre, uv-coverage, spectral-window etc.

    * The input source model is either an existing Local Sky Model (LSM),
    or a 'punit' point source in the centre of the field.

    * The nominal source visibilities may be corrupted by:
      - various (uv-plane) Jones matrices
      - image-plane effects from EJones and IJones (MIM)
      - ifr-based errors (additive, multiplicative)
      - noise

    * Optionally, the simulated visibilities may be added to the existing uv-data,
    either from the DATA column or the CORRECTED_DATA column of the MS

    * Optionally, a parallel solver branch may be inserted, which uses the simulated
    uv-data to solve for instrumental parameters. The latter may be compared with
    the simulated instrumental parameters.

    Different types of simulations may be specified by loading (and editing) socalled
    'inarg' records from files (like this one). These contain input arguments
    for generating a suitable MeqTree forest for the desired operation.
    """
    return True

#------------------------------------------------------------------------------------------------

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

MG = JEN_inarg.init('MG_JEN_simul', description=_description.__doc__,
                    inarg_specific=default_inarg.__doc__)
JEN_inarg.available_inargs(MG, describe_inargs())

# Define some overall arguments:
MG_JEN_Cohset.inarg_Cohset_common (MG, last_changed='d30jan2006')
JEN_inarg.modify(MG,
                 uvplane_effect=True,
                 tile_size=1,
                 _JEN_inarg_option=None)     

JEN_inarg.define (MG, 'add_to_existing', tf=False,
                  help='if True, add to existing uv-data (from MS column)')

JEN_inarg.define (MG, 'stddev_noise_Jy', 0.01, choice=[0,0.001,0.003,0.01,0.03,0.1,0.3,1,3],
                  help='stddev of gaussian noise, to be added')

JEN_inarg.define (MG, 'insert_solver', tf=True,
                  help='if True, insert a solver')

MG['external_uvp_Joneset'] = False

#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

JEN_inarg.separator(MG, 'uv-data (MS) stream_control')

inarg = MG_JEN_exec.stream_control(_getdefaults=True, slave=True)
JEN_inarg.modify(inarg,
                 data_column_name='CORRECTED_DATA',
                 channel_start_index=0,                         # <-------- !!
                 channel_end_index=-1,                          # <-------- !!
                 _JEN_inarg_option=None)     
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)  
JEN_inarg.attach(MG, inarg)


#----------------------------------------------------------------------------------------------------

JEN_inarg.separator(MG, 'uv-data simulation (LeafSet)')
qual = 'simul'

inarg = MG_JEN_lsm.get_lsm(_getdefaults=True, _qual=qual, simul=True)
JEN_inarg.attach(MG, inarg)

if MG['external_uvp_Joneset']:
    inarg = MG_JEN_Cohset.Jones(_getdefaults=True, _qual=qual+'_uvp', slave=True, simul=True) 
    JEN_inarg.attach(MG, inarg)
    inarg = MG_JEN_Cohset.predict_lsm(_getdefaults=True, slave=True, _qual=qual, simul=True)  
    JEN_inarg.attach(MG, inarg)
else:
    inarg = MG_JEN_Cohset.predict_lsm(_getdefaults=True, uvp_Joneset=True,
                                      slave=True, _qual=qual, simul=True)  
    JEN_inarg.attach(MG, inarg)
    
#----------------------------------------------------------------------------------------------------

JEN_inarg.separator(MG, 'solver-branch (ParmSet)')
qual = 'solve'

JEN_inarg.define (MG, 'use_same_LSM', tf=True,
                  help='if True, use same (simul) LSM for solving too')

inarg = MG_JEN_lsm.get_lsm(_getdefaults=True, _qual=qual, slave=True)
JEN_inarg.attach(MG, inarg)

if MG['external_uvp_Joneset']:
    inarg = MG_JEN_Cohset.Jones(_getdefaults=True, slave=True, _qual=qual+'_uvp') 
    JEN_inarg.attach(MG, inarg)
    inarg = MG_JEN_Cohset.predict_lsm(_getdefaults=True, slave=True, _qual=qual)  
    JEN_inarg.attach(MG, inarg)
else:
    inarg = MG_JEN_Cohset.predict_lsm(_getdefaults=True, uvp_Joneset=True,
                                      slave=True, _qual=qual)  
    JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.insert_solver(_getdefaults=True, slave=True) 
JEN_inarg.modify(inarg,
                 correct_after=False,
                 subtract_after=True,
                 _JEN_inarg_option=None)     
JEN_inarg.attach(MG, inarg)


#----------------------------------------------------------------------------------------------------

JEN_inarg.separator(MG, 'finishing touches')

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

    #------------------------------------------------------------------
    # Part I: Create the main Cohset from spigots:
    #------------------------------------------------------------------

    # Make MeqSpigot nodes that read the MS:
    global Cohset
    Cohset = TDL_Cohset.Cohset(label=MG['script_name'],
                               polrep=MG['polrep'],
                               stations=MG['stations'])
    MG_JEN_Cohset.make_spigots(ns, Cohset, _inarg=MG)


    #------------------------------------------------------------------
    # Part II: Insert (replace/add) the simulated uv-data:
    #------------------------------------------------------------------

    nsim = ns.Subscope('_')
    qual = 'simul'

    # Get/create/modify an LSM:
    lsm = MG_JEN_lsm.get_lsm(nsim, _inarg=MG, _qual=qual, simul=True)

    # Predict nominal/corrupted visibilities: 
    if MG['external_uvp_Joneset']:
        # Make an external Joneset for uv-plane effects:
        Joneset = MG_JEN_Cohset.Jones(nsim, simul=True, _inarg=MG, _qual=qual+'_uvp')
        predicted = MG_JEN_Cohset.predict_lsm (nsim, lsm=lsm, Joneset=Joneset, 
                                               simul=True, _inarg=MG, _qual=qual)
    else:
        predicted = MG_JEN_Cohset.predict_lsm (nsim, lsm=lsm, uvp_Joneset=True, 
                                               simul=True, _inarg=MG, _qual=qual)
        
    # Replace/add the uv-data with/to the predicted visibilities: 
    if MG['add_to_existing']:
        Cohset.add(nsim, predicted)
    else:
        Cohset.replace(nsim, predicted)

    # Opionally, add (gaussian) noise:
    if MG['stddev_noise_Jy']>0:
        Cohset.addNoise(nsim, stddev=MG['stddev_noise_Jy'])

    MG_JEN_Cohset.visualise (nsim, Cohset)
    MG_JEN_Cohset.visualise (nsim, Cohset, type='spectra')


    #------------------------------------------------------------------
    # Part III: Optionally, insert a parallel solver branch:
    #------------------------------------------------------------------

    if MG['insert_solver']:
        qual = 'solve'

        if MG['use_same_LSM']:
            # Use the LSM that was used for simulation
            lsm2 = lsm
        else:
            # Optionally, get/create/modify a different LSM:
            lsm2 = MG_JEN_lsm.get_lsm(ns, _inarg=MG, _qual=qual, slave=True)

        # Predict nominal/corrupted visibilities: 
        if MG['external_uvp_Joneset']:
            # Make an external Joneset for uv-plane effects:
            Joneset = MG_JEN_Cohset.Jones(ns, _inarg=MG, _qual=qual+'_uvp')
            predicted = MG_JEN_Cohset.predict_lsm (ns, lsm=lsm2, Joneset=Joneset,
                                                   _inarg=MG, _qual=qual)
        else:
            predicted = MG_JEN_Cohset.predict_lsm (ns, lsm=lsm2, uvp_Joneset=True,
                                                   _inarg=MG, _qual=qual)

        Sohset = Cohset.copy(label='solve_branch')
        MG_JEN_Cohset.insert_solver (ns, measured=Sohset, predicted=predicted, _inarg=MG)
        # Sohset.display('Sohset after insert_solver', full=True)
        # Cohset.display('Cohset after insert_solver', full=True)
    
        # Splice the Sohset branch back into Cohset:
        Cohset.splice(ns, Sohset)


    #------------------------------------------------------------------
    # Part IV: Finishing touches:
    #------------------------------------------------------------------

    global parmlist
    parmlist = Cohset.ParmSet.NodeSet.nodenames()

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

TDLRuntimeOption('num_iter', 'number of solver iterations',
                  [2,3,5,10], default=3)


def _tdl_job_execute (mqs, parent):
   """Execute the tree""" 
   # Start the sequence of requests issued by MeqSink:
   Cohset.TDLRuntimeOption('num_iter', num_iter)
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG)
   return True


def _tdl_job_execute_plus (mqs, parent):
   """Execute the tree, followed by the fullDomain version""" 
   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG)
   _tdl_job_fullDomainMux(mqs, parent)
   return True



def _tdl_job_fullDomainMux (mqs, parent):
   """Special for post-visualisation""" 
   global parmlist
   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.fullDomainMux(mqs, parent, ctrl=MG, parmlist=parmlist)
   return True


#------------------------------------------------------------------------------

def _tdl_job_make_dirty_image (mqs,parent,**kw):
   """Make an AIPS++ image (edit make_image.g first), and display it."""
   os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g']);
   pass

#------------------------------------------------------------------------------

def _tdl_job_display_Cohset (mqs, parent):
   """Display the Cohset object used to generate this tree""" 
   Cohset.display(MG['script_name'], full=False)
   return True

def _tdl_job_display_Cohset_ParmSet (mqs, parent):
   """Display the Cohset.ParmSet object used to generate this tree""" 
   Cohset.ParmSet.display(MG['script_name'], full=False)
   return True

def _tdl_job_display_Cohset_Joneset (mqs, parent):
   """Display the Cohset.Joneset() object used to generate this tree""" 
   Cohset.Joneset().display(MG['script_name'], full=False)
   return True

#------------------------------------------------------------------------------

def _tdl_job_display_full_Cohset (mqs, parent):
   """Display (full) the Cohset object used to generate this tree""" 
   Cohset.display(MG['script_name'], full=True)
   return True

def _tdl_job_display__full_Cohset_ParmSet (mqs, parent):
   """Display (full) the Cohset.ParmSet object used to generate this tree""" 
   Cohset.ParmSet.display(MG['script_name'], full=True)
   return True

def _tdl_job_display_full_Cohset_Joneset (mqs, parent):
   """Display (full) the Cohset.Joneset() object used to generate this tree""" 
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
        display_first_subtree(cs)
        cs.display('final result')

    # ............
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************





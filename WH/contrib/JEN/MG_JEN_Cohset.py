# MG_JEN_Cohset.py

# Short description:
#   Functions dealing with sets (all ifrs) of 2x2 cohaerency matrices 

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 05 sep 2005: adapted to Cohset/Joneset objects
# - 25 nov 2005: MS_corr_index argument to .make_spigots()
# - 05 dec 2005: included TDL_MSauxinfo services
# - 07 dec 2005: converted to JEN_inarg
# - 09 dec 2005: introduced Cohset.Condeq(), .coh()
# - 20 dec 2005: separate solver_subtree()
# - 29 dec 2005: redundancy calibration
# - 01 jan 2006: implement chain and master solver schemes
# - 03 jan 2006: resampling: move argument num_cells to insert_solver
# - 11 jan 2006: make function MSauxinfo()
# - 14 jan 2006: referenced values prepended with @/@@
# - 21 jan 2006: condeq_corr cats (corrI etc)
# - 05 feb 2006: punit='uvp'
# - 08 mar 2006: adopted Cohset._rider()
# - 09 mar 2006: included new TDL_ParmSet, removed TDL_Parmset and TDL_Leafset
# - 11 mar 2006: adopted TDL_Cohset.condeq_corrs()
# - 16 mar 2006: added KJones()
# - 20 mar 2006: added predict_lsm()
# - 22 mar 2006: implemented bookfolders
# - 31 mar 2006: added EJones_WSRT
# - 26 apr 2006: LeafSet into ParmSet object

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

from Timba.Contrib.JEN.util import JEN_inarg
from Timba.Contrib.JEN.util import JEN_inargGui
from Timba.Contrib.JEN.util import JEN_bookmarks

from Timba.Contrib.JEN.util import TDL_Cohset
from Timba.Contrib.JEN.util import TDL_Joneset
from Timba.Contrib.JEN.util import TDL_Leaf
from Timba.Contrib.JEN.util import TDL_MSauxinfo
# from Timba.Contrib.JEN.util import TDL_Sixpack

from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Sixpack

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

# from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN import MG_JEN_historyCollect
from Timba.Contrib.JEN import MG_JEN_flagger


try:
    from qt import *
    # from qt import QApplication,QCursor,Qt,QObject
except:
    pass;


#********************************************************************************
#********************************************************************************
#****************** PART II: Definition of importable functions *****************
#********************************************************************************
#********************************************************************************


#======================================================================================
# Make spigots and sinks (plus some common services)
#======================================================================================


def make_spigots(ns=None, Cohset=None, **inarg):
    """Make spigot nodes in the given Cohset object"""

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::make_spigots()', version='25dec2005',
                            description=make_spigots.__doc__)
    JEN_inarg.define (pp, 'input_col', 'DATA', hide=True,
                      choice=['DATA','PREDICT','RESIDUALS'],
                      help='name of the logical (VisTile) input column')
    JEN_inarg.define (pp, 'MS_corr_index', [0,1,2,3],
                      choice=[[0,1,2,3],[0,-1,-1,1],[0,-1,-1,3]],
                      # choice=[[0,-1,-1,1],[0,-1,-1,3],'@@'],
                      help='correlations to be used: \n'+
                      '- [0,1,2,3]:   all corrs available, use all \n'+
                      '- [0,-1,-1,1]: only XX/YY (or RR/LL) available \n'+
                      '- [0,-1,-1,3]: all available, but use only XX/YY or RR/LL')
    JEN_inarg.define (pp, 'visu', tf=True,
                      help='if True, visualise the input uv-data')
    JEN_inarg.define (pp, 'flag', tf=False,
                      help='if True, insert a flagger for the input uv-data')
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Make MeqSpigots:
    Cohset.spigots(ns, MS_corr_index=pp['MS_corr_index'])
    spigots = Cohset.cohs()

    # Create the nodes expected by read_MS_auxinfo.py
    stations = Cohset.station_index()
    MSauxinfo().create_nodes(ns, stations=stations)
    # MSauxinfo().display(funcname)

    # Append the initial (spigot) Cohset to the forest state object:
    # MG_JEN_forest_state.object(Cohset, funcname)

    # Optional: visualise the spigot (input) data:
    if pp['visu']:
	visualise (ns, Cohset)
	visualise (ns, Cohset, type='spectra')
        
    # Optional: flag the spigot (input) data:
    if pp['flag']:
       insert_flagger (ns, Cohset, scope='spigots',
                       unop=['Real','Imag'], visu=False)
       if pp['visu']: visualise (ns, Cohset)

    # Return a list of spigot nodes:
    return spigots


#--------------------------------------------------------------------------



def make_sinks(ns=None, Cohset=None, **inarg):
    """Make sink nodes in the given Cohset object"""

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::make_sinks()', version='25dec2005',
                            description=make_sinks.__doc__)
    JEN_inarg.define (pp, 'output_col', 'PREDICT',
                      choice=['PREDICT','RESIDUALS','DATA'],
                      help='name of the logical (VisTile) output column')
    JEN_inarg.define (pp, 'visu_array_config', tf=True,
                      help='if True, visualise the array config (from MS)')
    JEN_inarg.define (pp, 'visu', tf=True,
                      help='if True, visualise the output uv-data')
    JEN_inarg.define (pp, 'flag', tf=False,
                      help='if True, insert a flagger for the output uv-data')
    JEN_inarg.define (pp, 'fullDomainMux', tf=True,
                      help='if True, attach an extra VisDataMux')
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Change the scope (name) for visualisation etc:
    Cohset.scope('sinks')

    # Insert a master reqseq for solvers, if required:
    solvers = Cohset._rider('master_reqseq')
    if len(solvers)>0:
        Cohset.graft(ns, solvers, name='master_reqseq')

    # Insert the end of the solver chain, if required:
    solver = Cohset._rider('chain_solvers')
    if len(solver)>0:
        Cohset.graft(ns, solver[0], name='chain_solvers')

    # Optional: flag the sink (output) data:
    # NB: Not very useful, unless residual uv-data....
    if pp['flag']:
        insert_flagger (ns, Cohset, scope='sinks',
                        unop=['Real','Imag'], visu=False)

    # Optional: visualise the sink (output) data:
    # But only if there are no dcoll/hcoll nodes to be inserted
    # (assume that the latter visualise the current status...?)
    ncoll = len(Cohset._rider('dcoll'))               
    ncoll += len(Cohset._rider('hcoll'))               
    if pp['visu'] and ncoll==0:
        visualise (ns, Cohset)
        visualise (ns, Cohset, type='spectra')


    #----------------------------------------------------------------------
    # Make an extra VisDataMux for post-visualisation of the full domain:
    if pp['fullDomainMux']:
        bookfolder = 'fullDomainMux'

        # Attach some test-nodes:
        start = []
        if True:
            bookpage = 'fDMux_test'
            node = TDL_Leaf.MeqFreqTime(ns, mean=0.0)
            start.append(node)
            JEN_bookmarks.create(node, page=bookpage, folder=bookfolder)
            if True:
                # The same with the full time: truncation problems?
                node = TDL_Leaf.MeqFreqTime(ns)
                start.append(node)
                JEN_bookmarks.create (node, page=bookpage, folder=bookfolder)

        # NB: Do NOT include nodes that lead to spigots or solvers!!!!
        #     Just stick to MeqParms etc

        # Bundle the MeqParms per parmgroup:
        post = []
        post.append(Cohset.ParmSet.NodeSet.bookmark_subtree(ns, folder=bookfolder))
        post.append(Cohset.ParmSet.LeafSet.NodeSet.bookmark_subtree(ns, folder=bookfolder))    
        # post.append(Cohset.ParmSet.NodeSet.dataCollect(ns, folder=bookfolder))    
        # post.append(Cohset.ParmSet.LeafSet.NodeSet.dataCollect(ns, folder=bookfolder))    
        if True:
            # Compare corresponding nodes/groups in ParmSet and its LeafSet:
            node = Cohset.ParmSet.NodeSet.compare (ns, Cohset.ParmSet.LeafSet.NodeSet,
                                                   # group=None, binop='Subtract',
                                                   bookpage='fDMux_Parm-Leaf',
                                                   folder=bookfolder, trace=False)
            post.append(node)

        # Make the VisDataMux:
        Cohset.fullDomainMux(ns, start=start, post=post)
    #----------------------------------------------------------------------


    # Attach array visualisation nodes:
    start = []
    if pp['visu_array_config']: 
        dcoll = MSauxinfo().dcoll(ns)
        # MSauxinfo().display(funcname)
        for i in range(len(dcoll)):
            JEN_bookmarks.bookmark(dcoll[i], page='MSauxinfo_array_config')
        start.extend(dcoll)

    # Attach any collected hcoll/dcoll nodes:
    post = []
    post.extend(Cohset._rider('dcoll'))               
    post.extend(Cohset._rider('hcoll'))

    # Make MeqSinks
    Cohset.sinks(ns, start=start, post=post, output_col=pp['output_col'])
    sinks = Cohset.cohs()

    # Cohset.display(funcname, full=True)
    # Cohset.ParmSet.display(funcname, full=True)

    # Append the final Cohset to the forest state object:
    # MG_JEN_forest_state.object(Cohset, funcname)
    # MG_JEN_forest_state.object(Cohset.ParmSet, funcname)
    
    # Return a list of sink nodes:
    return sinks



#======================================================================================
# Prediction:
#======================================================================================

#--------------------------------------------------------------------------------------
# Make a Joneset from the specified sequence of Jones matrices:

def Jones(ns=None, Sixpack=None, simul=False, slave=False, KJones=None, **inarg):
    """Make a Joneset by creating and multiplying a sequence of one ore more Jonesets"""

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::Jones()', version='25dec2005',
                            description=Jones.__doc__)
    # Arguments that should be common to all Jonesets in the sequence:
    MG_JEN_Joneset.inarg_Joneset_common(pp, slave=slave)
    MG_JEN_Joneset.inarg_Joneset_ParmSet(pp, slave=slave)
    jseq_name = 'Jsequence'
    JEN_inarg.define (pp, jseq_name, [],
                      choice=[['GJones'],['BJones'],['FJones'],['KJones'],
                              ['DJones_WSRT'],['GJones','DJones_WSRT'],
                              ['EJones_WSRT'],['GJones','EJones_WSRT'],
                              ['JJones'],[]],
                      help='sequence of Jones matrices to be used')
    # Include default inarg records for various Jones matrix definition functions:
    qual = JEN_inarg.qualifier(pp)
    JEN_inarg.nest(pp, MG_JEN_Joneset.GJones(_getdefaults=True, _qual=qual, simul=simul, slave=True))
    JEN_inarg.nest(pp, MG_JEN_Joneset.FJones(_getdefaults=True, _qual=qual, simul=simul, slave=True))
    JEN_inarg.nest(pp, MG_JEN_Joneset.BJones(_getdefaults=True, _qual=qual, simul=simul, slave=True))
    JEN_inarg.nest(pp, MG_JEN_Joneset.KJones(_getdefaults=True, _qual=qual, simul=simul, slave=True))
    JEN_inarg.nest(pp, MG_JEN_Joneset.DJones_WSRT(_getdefaults=True, _qual=qual, simul=simul, slave=True))
    JEN_inarg.nest(pp, MG_JEN_Joneset.EJones_WSRT(_getdefaults=True, _qual=qual, simul=simul, slave=True))
    JEN_inarg.nest(pp, MG_JEN_Joneset.JJones(_getdefaults=True, _qual=qual, simul=simul, slave=True))

    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Check the Jones sequence:
    if not isinstance(pp[jseq_name], (list,tuple)):
        pp[jseq_name] = [pp[jseq_name]]
    if KJones:
        # If KJones==True, make sure that it is part of the sequence:
        if not 'KJones' in pp[jseq_name]:
            pp[jseq_name].append('KJones')
    if len(pp[jseq_name])==0: return None             # not needed
    if pp[jseq_name]==None: return None               # not needed

    # Make sure that there is a valid source/patch Sixpack:
    # This is just for the punit-name, and (RA,Dec) for KJones...
    if not Sixpack:
        Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit='uvp')
    punit = Sixpack.label()
    
    # Create a sequence of Jonesets for the specified punit:
    jseq = TDL_Joneset.Joneseq()
    for jones in pp[jseq_name]:
        if jones=='GJones':
            jseq.append(MG_JEN_Joneset.GJones (ns, Sixpack=Sixpack, simul=simul, _inarg=pp, _qual=qual))
        elif jones=='BJones':
            jseq.append(MG_JEN_Joneset.BJones (ns, Sixpack=Sixpack, simul=simul, _inarg=pp, _qual=qual))
        elif jones=='FJones':
            jseq.append(MG_JEN_Joneset.FJones (ns, Sixpack=Sixpack, simul=simul, _inarg=pp, _qual=qual)) 
        elif jones=='JJones':
            jseq.append(MG_JEN_Joneset.JJones (ns, Sixpack=Sixpack, simul=simul, _inarg=pp, _qual=qual))
        elif jones=='DJones_WSRT':
            jseq.append(MG_JEN_Joneset.DJones_WSRT (ns, Sixpack=Sixpack, simul=simul, _inarg=pp, _qual=qual))
        elif jones=='EJones_WSRT':
            jseq.append(MG_JEN_Joneset.EJones_WSRT (ns, Sixpack=Sixpack, MSauxinfo=MSauxinfo(),
                                                    simul=simul, _inarg=pp, _qual=qual))
        elif jones=='KJones':
            jseq.append(MG_JEN_Joneset.KJones (ns, Sixpack=Sixpack, MSauxinfo=MSauxinfo(),
                                               _inarg=pp, _qual=qual))
        else:
            print '** jones not recognised:',jones,'from:',pp[jseq_name]
               
    # Matrix-multiply the collected jones matrices in jseq to a 2x2 Joneset:
    # MG_JEN_forest_state.object(jseq, funcname)
    Joneset = jseq.make_Joneset(ns)
    # MG_JEN_forest_state.object(Joneset, funcname)
    return Joneset
    


#------------------------------------------------------------------------------

def predict (ns=None, Sixpack=None, Joneset=None, slave=False, **inarg):
    """Obsolete (upward compatibility) version of .predict_cps()"""
    return predict_cps (ns, Sixpack, Joneset=Joneset, slave=slave, **inarg)



def predict_cps (ns=None, Sixpack=None, Joneset=None, slave=False, **inarg):
    """Make a Cohset with predicted uv-data for the Central Point Source (cps)
    defined by Sixpack. If a Joneset with instrumental effects is supplied,
    corrupt the predicted uv-data."""

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::predict_cps()', version='20mar2006',
                            description=predict.__doc__)
    MG_JEN_Joneset.inarg_Joneset_common(pp, slave=slave)
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Make sure that there is a valid source/patch Sixpack:
    if not Sixpack:
        Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit='uvp')

    # Create a Cohset object for the 2x2 cohaerencies of the given ifrs:
    Cohset = TDL_Cohset.Cohset(label='predict_cps', origin=funcname, **pp)

    Cohset.punit2coh(ns, Sixpack, Joneset)

    # Finished:
    MG_JEN_forest_state.object(Sixpack, funcname)
    Cohset._history(funcname+' using '+Sixpack.oneliner())
    Cohset._history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history (funcname)
    # MG_JEN_forest_state.object(Cohset, funcname)
    return Cohset

#------------------------------------------------------------------------------

def predict_lsm (ns=None, lsm=None, Joneset=None, uvp_Joneset=False,
                 simul=False, slave=False, **inarg):
    """Make a Cohset with the (sum of the) predicted uv-data for the specified sources in
    the given Local Sky Model (lsm). Per source, the data may be corrupted with a Joneset
    that contains at least a KJones matrix (DFT), and zero or more (sky-interpolatable)
    image-plane effects like EJones (station beamshape) or IJones (ionosphere).
    If a Joneset (with uv-plane effects) is supplied, corrupt the sum also.
    (If uvp_Joneset==True, the uv-plane Joneset is generated inside this routine.)"""

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::predict_lsm()', version='20mar2006',
                            description=predict.__doc__)
    qual = JEN_inarg.qualifier(pp)

    JEN_inarg.define(pp, 'nr_lsm_sources', 10000,
                     choice=[1,2,3,5,10,20,100,1000,10000],
                     help='nr of lsm sources to be included (in order of brightness)')
    JEN_inarg.define(pp, 'visu', tf=True,
                     help='if True, visualise the source contribitions')
    MG_JEN_Joneset.inarg_Joneset_common(pp, slave=slave)

    # Arguments for a Joneset for image-plane effects:
    JEN_inarg.nest(pp, Jones(_getdefaults=True, _qual=qual+'_imp',
                             simul=simul, slave=True, KJones=True))

    # Optional: arguments for a Joneset for uv-plane effects:
    if uvp_Joneset:
        JEN_inarg.nest(pp, Jones(_getdefaults=True, _qual=qual+'_uvp',
                                 simul=simul, slave=True))

    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Obtain the Sixpacks of the brightest punits.
    # Turn the point-sources in Cohsets with DFT KJonesets
    plist = lsm.queryLSM(count=pp['nr_lsm_sources'])
    cs = []                                      # list of source Cohsets
    cc_visu = []                                 # list of nodes for visualisation
    for punit in plist: 
        Sixpack = punit.getSixpack()
        punit_name = str(Sixpack.label())
        if Sixpack.ispoint():                    # point source (Sixpack object)
            # Make a new Cohset for this punit:
            cs1 = TDL_Cohset.Cohset(label=punit_name, origin=funcname, **pp)
            # Corrupt with image-plane effects (including KJones/DFT):
            js1 = Jones (ns, Sixpack=Sixpack, MSauxinfo=MSauxinfo(),
                         _inarg=pp, _qual=qual+'_imp', simul=simul, KJones=True)
            cs1.punit2coh(ns, Sixpack, js1, MSauxinfo=MSauxinfo())
            cs.append(cs1)                       # append to list of source Cohsets
            if len(cc_visu)==0:
                klong = cs1.find_keys('longest')[0] # key of longest baseline
            cc_visu.append(cs1[klong])           # visualise  one coh of each source
        else:	                                 # patch (not a Sixpack object!)
            # Not really supported yet.....
            node = Sixpack.root()

    # Add the point-source Cohsets (cs) together into the final predicted Cohset:
    Cohset = TDL_Cohset.Cohset(label='predict_lsm', origin=funcname, **pp)
    Cohset.replace(ns, cs)
    cc_visu.append(Cohset[klong])                # visualise the sum too

    if pp['visu']:
        JEN_bookmarks.create (cc_visu, page='predict_lsm', folder=None)

    # Optionally, corrupt the Cohset visibilities with the instrumental
    # uv_plane effects in the given Joneset of 2x2 station jones matrices:
    if uvp_Joneset:
        Joneset = Jones (ns, _inarg=pp, _qual=qual+'_uvp', simul=simul)
    if Joneset:
        Cohset.corrupt (ns, Joneset=Joneset)

    # Finished:
    MG_JEN_forest_state.object(Sixpack, funcname)
    Cohset._history(funcname+' using '+Sixpack.oneliner())
    Cohset._history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history (funcname)
    # MG_JEN_forest_state.object(Cohset, funcname)
    return Cohset










#======================================================================================
# Insert a solver:
#======================================================================================

# - The 'measured' Cohset is assumed to be the main data stream.
# - The 'predicted' Cohset contains corrupted model visibilities,
#   and the Joneset with which it has been corrupted (if any).

def insert_solver(ns=None, measured=None, predicted=None, slave=False, **inarg):
    """insert one or more solver subtrees in the data stream""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::insert_solver()', version='25dec2005',
                            description=insert_solver.__doc__)
    JEN_inarg.define(pp, 'solver_subtree', None, hide=True,
                     help='solver subtree qualifier(s)')
    inarg_redun(pp, slave=slave)
    inarg_resample(pp, slave=slave)
    inarg_solver_config (pp, slave=True)
    JEN_inarg.define(pp, 'condeq_unop', None, choice=[None,'Abs','Arg'],
                     help='Optional unary operation on Condeq inputs')
    JEN_inarg.define(pp, 'visu', tf=True,
                     help='if True, include full visualisation')
    JEN_inarg.define(pp, 'subtract_after', tf=False,
                     help='if True, subtract predicted from measured')
    JEN_inarg.define(pp, 'correct_after', tf=True,
                     help='if True, correct measured with predicted.Joneset')
    JEN_inarg.define(pp, 'flag_residuals', tf=False,
                     hide=True,                           # Not yet implemented....
                     help='if True, flag the residuals')
    # Include (nest) the inarg record of a subroutine called below:
    JEN_inarg.nest(pp, solver_subtree(_getdefaults=True))
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Make a unique qualifier:
    uniqual = _counter('.insert_solver()', increment=-1)
    punit = predicted.punit()

    # We need a Mohset copy, since it will be modified with condeqs etc
    Mohset = measured.copy(label='measured')
    # Mohset._history(funcname+' input: '+str(pp))  # too much
    Mohset._history(funcname+' measured: '+measured.oneliner())
    Mohset._history(funcname+' predicted: '+predicted.oneliner())

    # Optional: Insert a ReSampler node as counterpart to the ModRes node below.
    # This node resamples the full-resolution (f,t) measured uv-data onto
    # the smaller number of cells of the request from the condeq.
    if pp['num_cells']:
        Mohset.ReSampler(ns, flag_mask=3, flag_bit=4, flag_density=0.1)

    # Make condeq nodes in Mohset:
    if pp['redun']:                              # redundant-spacing calibration
        Mohset.correct(ns, predicted.Joneset())  # correct BOTH sides of the condeq                 
        Mohset.Condeq_redun(ns, unop=pp['condeq_unop'])   # special version of .Condeq()                        
        pp['subtract_after'] = False             # .....??
    else:                                        # normal: measured-predicted
        Mohset.Condeq(ns, predicted, unop=pp['condeq_unop'])        
    Mohset.scope('condeq_'+punit)
    Mohset._history(funcname+' -> '+Mohset.oneliner())

    # Update the measured Cohset with the ParmSet from Mohset.
    # This contains the Joneset/Sixpack MeqParms, which may be re-executed
    # separately for the full (MS) domain for inspection (see .make_sinks())
    measured.updict_from_ParmSet(Mohset.ParmSet)

    # Make a list of one or more MeqSolver subtree(s):
    # Assume that pp contains the relevant (qual) inarg record(s).
    # NB: Note that pp['num_cells'] overrides solver_subtree() default.
    if pp['solver_subtree']:
        if not isinstance(pp['solver_subtree'], (tuple, list)):
            pp['solver_subtree']= [pp['solver_subtree']]
        solver_subtrees = []
        for qual in pp['solver_subtree']:
            sst = solver_subtree(ns, Mohset, _inarg=pp, _qual=qual,
                                 num_cells=pp['num_cells'])
            solver_subtrees.append(sst)
    else:
        sst = solver_subtree(ns, Mohset, _inarg=pp, num_cells=pp['num_cells'])
        solver_subtrees = [sst]

    # Transfer the Mohset solvers (nodenames) to the rider of measured:
    measured._rider('solver', append=Mohset._rider('solver'))

    # Obtain the current list of (full-resolution) hcoll/dcoll nodes, and clear: 
    # NB: These are the ones that get a request BEFORE the solver(s)
    coll_before = []
    coll_before.extend(measured._rider('hcoll', clear=True))
    coll_before.extend(measured._rider('dcoll', clear=True))

    # Optional: subtract the predicted (corrupted) Cohset from the measured data:
    # NB: This should be done BEFORE correct, since predicted contains corrupted values
    if pp['subtract_after']:
        measured.subtract(ns, predicted)
        if pp['flag_residuals']:
            # Insert a flagger that operates on the residuals
            pp['flag_residuals'] = False;                # see below
            pass
        if pp['visu']:
            visualise (ns, measured, errorbars=True, graft=False,
                       bookfolder='subtracted')
        
    # Optional: Correct the measured data with the given Joneset.
    # NB: This should be done AFTER subtract, for the same reason as stated above
    # NB: Correction should be inserted BEFORE the solver reqseq (see below),
    # because otherwise it messes up the correction of the insertion ifr
    # (one of the input Jones matrices is called before the solver....)
    if pp['correct_after']:
        if pp['flag_residuals']:
            # Insert a flagger in a side-branch, in which predicted is subtracted first
            pass
        # The 'predicted' Cohset has kept the Joneset with which it has been
        # corrupted, and which has been affected by the solution for its MeqParms.
        Joneset = predicted.Joneset() 
        if Joneset:                                  # if Joneset available
            measured.correct(ns, Joneset)            # correct 
            if pp['visu']:
                visualise (ns, measured, errorbars=True, graft=False,
                           bookfolder='corrected')

    # Obtain the current list of (full-resolution) hcoll/dcoll nodes, and clear: 
    # NB: These are the ones that get a request AFTER the solver(s)
    coll_after = []
    coll_after.extend(measured._rider('dcoll', clear=True))
    coll_after.extend(measured._rider('hcoll', clear=True))

    # Make the 'full-resolution' reqseq with solver_subtree(s) and dcoll/hcoll nodes:
    cc = coll_before                                 # hcoll/dcoll nodes BEFORE the solver
    if len(coll_before)>1:
        cc = [ns.coll_before_solver(uniqual)(q=punit) << Meq.Composer(children=coll_before)]
        # cc = [ns.coll_before_solver(uniqual)(q=punit) << Meq.ReqMux(children=coll_before)]
        # NB: ReqMux gives error message: nmandatory<=nchildren...?
    cc.extend(solver_subtrees)                       # the solver subtree(s) 
    if len(coll_after)>1:
        coll_after = [ns.coll_after_solver(uniqual)(q=punit) << Meq.Composer(children=coll_after)]
    cc.extend(coll_after)                            # hcoll/dcoll nodes AFTER the solver
    fullres = ns.solver_fullres(uniqual)(q=punit) << Meq.ReqSeq(children=cc)

    # Attach the solver subtree (fullres) to something:
    if pp['master_reqseq']:
        # Collect all solvers for a master reqseq before the sinks
        # (See .make_sinks())
        measured._rider('master_reqseq', append=fullres)
    elif pp['chain_solvers']:
        # Chain the solvers, parallel to the main data-stream:
        measured.chain_solvers(ns, fullres) 
    else:
        # Graft the fullres onto all measured ifr-streams via reqseqs:
        # NB: Since the reqseqs have to wait for the solver to finish,
        #     this synchronises the ifr-streams
        measured.graft(ns, fullres, name='insert_solver')

    # Finished: do some book-keeping:
    # MG_JEN_forest_state.object(Mohset, funcname)
    # MG_JEN_forest_state.object(Mohset.ParmSet, funcname)
    # MG_JEN_forest_state.object(predicted, funcname)
    # MG_JEN_forest_state.object(predicted.ParmSet, funcname)
    MG_JEN_forest_state.history (funcname)
    Mohset.cleanup(ns)                
    return True
    

#-----------------------------------------------------------------------------
# A solver subtree


def solver_subtree (ns=None, Cohset=None, slave=False, **inarg):
    """Make a solver-subtree for the given Condeq Cohset""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::solver_subtree()', version='20dec2005',
                            description=solver_subtree.__doc__)
    MG_JEN_Joneset.inarg_solvegroup(pp, slave=slave)
    JEN_inarg.define(pp, 'rmin', None, choice=[None, 100, 200, 500],  
                     help='if specified, only use baselines>=rmin')
    JEN_inarg.define(pp, 'rmax', None, choice=[None, 500, 1000, 2000],  
                     help='if specified, only use baselines<=rmax')
    inarg_resample(pp, slave=slave)
    JEN_inarg.define(pp, 'num_iter', 5, choice=[1,3,5,10,20],  
                     help='max number of iterations (now also in fitter)')
    JEN_inarg.define(pp, 'epsilon', 1e-4, choice=[1e-3,1e-4, 1e-5],  
                     help='iteration control criterion...')
    JEN_inarg.define(pp, 'epsval', 1e-8, choice=[1e-3,1e-4, 1e-5],  hide=True,
                     help='NEW: WNB version of epsilon....')
    JEN_inarg.define(pp, 'derivative_eps', 1e-8, choice=[1e-3,1e-4, 1e-5], hide=True, 
                     help='NEW: also iteration control...')
    JEN_inarg.define(pp, 'colin_factor', 0.0, choice=[1e-8,0.0],  
                     help='colinearity factor')
    JEN_inarg.define(pp, 'usesvd', tf=True,  
                     help='if True, use Singular Value Decomposition (SVD)')
    JEN_inarg.define(pp, 'setBalanced', tf=False, hide=True,                      
                     help='NEW: if True, add (..) to diagonal, otherwise multiply (1+lambda)')
    JEN_inarg.define(pp, 'debug_level', 10, choice=[10], hide=True,  
                     help='solver debug_level')
    JEN_inarg.define(pp, 'visu', tf=True,   
                     help='if True, include visualisation')
    JEN_inarg.define(pp, 'history', tf=True,   
                     help='if True, include history collection of metrics')
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Make a unique qualifier:
    uniqual = _counter('.solver_subtree()', increment=-1)

    # The solver name must correspond to one or more of the
    # predefined solvegroups of parms in the input Cohset.
    # These are collected from the Jonesets upstream.
    # The solver_name is just a concatenation of such solvegroup names:
    if isinstance(pp['solvegroup'], str):
        pp['solvegroup'] = [pp['solvegroup']]
    solver_name = pp['solvegroup'][0]
    for i in range(len(pp['solvegroup'])):
        if i>0: solver_name = solver_name+pp['solvegroup'][i]
    folder_name = 'solver: '+solver_name

    # Get a list of names of solvable MeqParms for the solver:
    corrs = Cohset.condeq_corrs(pp['solvegroup'])
    # print '\n** corrs (ParmSet):',corrs

    solvable = Cohset.ParmSet.solveparm_names(pp['solvegroup'])
    # print '\n** solvable (ParmSet):',type(solvable),'=\n   ',solvable,'\n'

    dcoll_parm = []
    hcoll_parm = []
    subtree_solvegroups = None
    if pp['visu']:
        bs = Cohset.ParmSet.NodeSet.bookmark_subtree(ns, folder=folder_name)
        # subtree_solvegroups = bs
        dcoll_parm.append(bs)
        # Show the first MeqParm in each parmgroup:
        ss1 = Cohset.ParmSet.solveparm_names(pp['solvegroup'], select='first')
        for s1 in ss1:
            # JEN_bookmarks.bookmark (ns[s1], page='solvable')
            hcoll = MG_JEN_historyCollect.insert_hcoll(ns, s1, graft=False,
                                                       bookpage='hcoll_solvable',
                                                       bookfolder=folder_name)
            hcoll_parm.append(hcoll)

    # Extract a list of condeq nodes for the specified corrs and baseline lengths:
    Cohset.select(rmin=pp['rmin'], rmax=pp['rmax'])
    solver_condeqs = Cohset.cohs(corrs=corrs, ns=ns)

    # Make extra condeq nodes to condition the solution, if required: 
    extra_condeqs = []
    if pp['condition']==None: pp['condition'] = []
    if not isinstance(pp['condition'], (list, tuple)): pp['condition'] = [pp['condition']]
    for key in pp['condition']:
        if isinstance(key, str):
            condeq = Cohset.ParmSet.make_condeq(ns, key)
            if not isinstance(condeq, bool): extra_condeqs.append(condeq)
    solver_condeqs.extend(extra_condeqs)

    # Visualise the condeqs (at solver resolution), if required:
    dcoll_condeq = []
    if False and pp['visu']:
       dcoll_condeq = visualise (ns, Cohset, errorbars=True, graft=False, extra=extra_condeqs)
  
    # Make the MeqSolver node itself:
    punit = Cohset.punit()
    solver = ns.solver(solver_name, q=punit) << Meq.Solver(children=solver_condeqs,
                                                           solvable=solvable,
                                                           num_iter=pp['num_iter'],
                                                           epsilon=pp['epsilon'],
                                                           colin_factor=pp['colin_factor'],
                                                           usesvd=pp['usesvd'],
                                                           last_update=True,
                                                           save_funklets=True,
                                                           debug_level=pp['debug_level'])
    # Keep track of the solver nodes:
    Cohset._rider('solver',append=solver)
    
    # Make a bookmark for the solver plot:
    page_name = 'solver: '+solver_name
    JEN_bookmarks.create (solver, page=page_name, folder=folder_name)
    JEN_bookmarks.create (solver, viewer='ParmFiddler',
                          page=page_name, folder=folder_name)
    if pp['visu']:
        # Optional: also show the solver on the allcorrs page:
        JEN_bookmarks.create (solver, page='allcorrs')

    # Make historyCollect nodes for the solver metrics
    hcoll_nodes = []
    if pp['history'] and pp['visu']:
        # Make a tensor node of solver metrics/debug hcoll nodes:
        hc = MG_JEN_historyCollect.make_hcoll_solver_metrics (ns, solver,
                                                              firstonly=True,
                                                              bookfolder=folder_name,
                                                              name=solver_name)
        hcoll_nodes.append(hc)


    # Make a solver subtree with the solver and its associated hcoll/dcoll nodes:
    # The latter are at solver resolution, which may be lower (resampling)
    # This is necessary in order to give them all the same resampled request (see below)
    subtree_name = 'solver_subtree_'+solver_name  # used in reqseq name
    cc = [solver]                                 # start a list of reqseq children (solver is first)
    if len(hcoll_nodes)>0:                        # append historyCollect nodes
       cc.append(ns.hcoll_solver(solver_name, q=punit) << Meq.Composer(children=hcoll_nodes))
    if len(dcoll_condeq)>0:                       # append dataCollect nodes
       cc.append(ns.dcoll_condeq(solver_name, q=punit) << Meq.Composer(children=dcoll_condeq))
    if len(dcoll_parm)>0:                         # append MeqParm dataCollect nodes
       cc.append(ns.dcoll_parm(solver_name, q=punit) << Meq.Composer(children=dcoll_parm))
    if len(hcoll_parm)>0:                         # append MeqParm historyCollect nodes
       cc.append(ns.hcoll_parm(solver_name, q=punit) << Meq.Composer(children=hcoll_parm))
    if subtree_solvegroups:
        cc.append(subtree_solvegroups) 
    root = ns[subtree_name](q=punit) << Meq.ReqSeq(children=cc, result_index=0)


    # Insert a ModRes node to change (reduce) the number of request cells:
    # NB: This node must be BEFORE the hcoll/dcoll nodes, since these also
    #     require the low-resolution request, of course....
    if pp['num_cells']:
       num_cells = pp['num_cells']                # [ntime, nfreq]
       # NB: Alternatives are up/downsample (see inarg_resample())
       root = ns.modres_solver(solver_name, q=punit) << Meq.ModRes(root, num_cells=num_cells)


    # Finished: do some book-keeping:
    # MG_JEN_forest_state.object(Cohset, funcname)
    MG_JEN_forest_state.history (funcname)
    return root
    


#======================================================================================
# Insert a flagger:
#======================================================================================


def insert_flagger (ns=None, Cohset=None, **inarg):
    """insert a flagger for the coherency matrices in Cohset""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::insert_flagger()', version='25dec2005',
                            description=insert_flagger.__doc__)
    pp.setdefault('sigma', 5.0)              # flagged if exceeds sigma*stddev
    pp.setdefault('unop', 'Abs')             # unop used to make real data
    pp.setdefault('oper', 'GT')              # decision function (GT=Greater Than)
    pp.setdefault('flag_bit', 1)             # affected flag-bit
    pp.setdefault('merge', True)             # if True, merge the flags of 4 corrs
    pp.setdefault('visu', False)             # if True, visualise the result
    pp.setdefault('compare', False)          # ....
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Insert flaggers for all ifrs:
    flagger_scope = 'flag_'+Cohset.scope()
    for key in Cohset.keys():
        s12 = Cohset.stations()[key]
        nsub = ns.Subscope(flagger_scope, s1=s12[0], s2=s12[1])
        coh = MG_JEN_flagger.flagger (nsub, Cohset[key],
                                      sigma=pp['sigma'], unop=pp['unop'], oper=pp['oper'],
                                      flag_bit=pp['flag_bit'], merge=pp['merge'])
        Cohset[key] = coh

    # Visualise the result, if required:
    if pp['visu']:
        visu_scope = 'flagged_'+Cohset.scope()
        visualise (ns, Cohset, scope=visu_scope, type='spectra')

    Cohset.scope('flagged')
    Cohset._history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history (funcname)
    # MG_JEN_forest_state.object(Cohset, funcname)
    return True



#======================================================================================
# Cohset visualisation:
#======================================================================================

def visualise(ns=None, Cohset=None, extra=None, **pp):
    """visualises the 2x2 coherency matrices in Cohset"""

    funcname = 'MG_JEN_Cohset.visualise(): '

    # Input arguments:
    pp.setdefault('type', 'realvsimag')     # plot type (realvsimag or spectra)
    pp.setdefault('errorbars', False)       # if True, plot stddev as crosses around mean
    pp.setdefault('graft', False)           # if True, graft the visu-nodes on the Cohset
    pp.setdefault('paralcorr', False)       # if True, also make plots for parallel corrs only  
    pp.setdefault('crosscorr', False)       # if True, also make plots for cross corrs only  
    pp.setdefault('keypage', True)          # if True, make 'key' bookmarks
    pp.setdefault('bookpage', '<scope>')    # bookmark page to be used for scope... 
    pp.setdefault('bookfolder', None)       # bookmark folder to be used 

    pp['graft'] = False                     # disabled permanently....?

    if pp['bookpage']=='<scope>':
        pp['bookpage'] = Cohset.scope()

    # Use a sub-scope where node-names are prepended with name
    # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
    visu_scope = 'visu_'+Cohset.scope()

    # The dataCollect nodes are visible, and should show the punit:
    dcoll_scope = Cohset.scope()+'_'+Cohset.punit()
  
    # Make separate lists of nodes per (available) corr:
    nodes = {}
    for corr in Cohset.corrs():
        nodes[corr] = Cohset.cohs(corrs=corr, ns=ns, name='visu')
        if extra:
            # Special case (kludge): include some extra nodes
            if not isinstance(extra, (list,tuple)): extra = [extra]
            nodes[corr].extend(extra)

    # Make dcolls per (available) corr, and collect groups of corrs:
    dcoll = dict()
    for corr in Cohset.corrs():
        dc = MG_JEN_dataCollect.dcoll (ns, nodes[corr], 
	                               scope=dcoll_scope, tag=corr,
                                       type=pp['type'], errorbars=pp['errorbars'],
                                       color=Cohset.plot_color()[corr],
                                       style=Cohset.plot_style()[corr],
                                       size=Cohset.plot_size()[corr],
                                       pen=Cohset.plot_pen()[corr])
        if pp['type']=='spectra':
            dcoll[corr] = dc
        elif pp['type']=='realvsimag':
            key = 'allcorrs'
            dcoll.setdefault(key,[])
            dcoll[key].append(dc)
            if pp['crosscorr'] and corr in ['XY','YX','RL','LR']:
                key = 'crosscorr'
                dcoll.setdefault(key,[])
                dcoll[key].append(dc)
            if pp['paralcorr'] and corr in ['XX','YY','RR','LL']:
                key = 'paralcorr'
                dcoll.setdefault(key,[])
                dcoll[key].append(dc)

    # Make the final dcolls:
    dconc = dict()
    sc = []
    for key in dcoll.keys():
       if pp['type']=='spectra':
          # Since spectra plots are crowded, make separate plots for the 4 corrs.
          dc = dcoll[key]                                         # key = corr
          if pp['keypage']:
              JEN_bookmarks.create (dc['dcoll'], page=key, folder=str(Cohset.corrs()))
              JEN_bookmarks.create (dc['dcoll'], page=dcoll_scope, folder='spectra')
          if pp['bookpage'] or pp['bookfolder']:
              JEN_bookmarks.create (dc['dcoll'], page=pp['bookpage'],
                                    folder=pp['bookfolder'])

       elif pp['type']=='realvsimag':
          # For realvsimag plots it is better to plot multiple corrs in the same plot.
          # NB: key = allcorrs, [paralcorr], [crosscorr]
          keypage = pp['keypage']
          if pp['keypage']: keypage=key
          dc = MG_JEN_dataCollect.dconc(ns, dcoll[key], 
                                        scope=dcoll_scope,
                                        tag=key, bookpage=keypage)
          if pp['bookpage'] or pp['bookfolder']:
              JEN_bookmarks.create (dc['dcoll'], page=pp['bookpage'],
                                    folder=pp['bookfolder'])

       dconc[key] = dc                               # atach to output record
       sc.append (dc['dcoll'])                       # step-child for graft below
      

    MG_JEN_forest_state.history (funcname)
  
    if pp['graft']:
        # Make the dcoll nodes children of a (synchronising) MeqReqSeq node
        # that is inserted into the coherency stream(s):
        Cohset.graft(ns, sc, name=visu_scope+'_'+pp['type']) 
        # MG_JEN_forest_state.object(Cohset, funcname+'_'+visu_scope+'_'+pp['type'])
        # Return an empty list to be consistent with the alternative below
        return []

    else:
        # Return a list of dataCollect nodes that need requests:
        Cohset._history(funcname+' -> '+'dconc keys: '+str(dconc.keys()))
        cc = []
        for key in dconc.keys():
           cc.append(dconc[key]['dcoll'])
        Cohset._rider('dcoll', append=cc)                # collect in Cohset
        return cc








#==========================================================================
# Some convenience functions:
#==========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=False):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace:
        print '** MG_JEN_Cohset: _counters(',key,') =',_counters[key]
    return _counters[key]



#--------------------------------------------------------------------------
# Display the subtree of the first ifr in the Cohset

def display_first_subtree (Cohset=None, recurse=3):
    key = Cohset.keys()[0]
    txt = 'coh[0/'+str(Cohset.len())+']'
    txt = txt+': key='+str(key)
    MG_JEN_exec.display_subtree(Cohset[key], txt, full=1, recurse=recurse)
    return


# Make a Sixpack from a punit string

def punit2Sixpack(ns, punit='uvp'):
    Sixpack = MG_JEN_Sixpack.newstar_source (ns, punit=punit)
    return Sixpack





#----------------------------------------------------------------------------------------------------
# inarg_functons (definition of groups of input arguments):
#----------------------------------------------------------------------------------------------------


def inarg_polrep (pp, **kwargs):
    JEN_inarg.inarg_common(kwargs)
    JEN_inarg.define (pp, 'polrep', 'linear',
                      slave=kwargs['slave'], hide=kwargs['hide'],
                      choice=['linear','circular'],
                      help='polarisation representation')
    return True


def inarg_parmtable (pp, **kwargs):
    JEN_inarg.inarg_common(kwargs)
    JEN_inarg.define (pp, 'parmtable', None,
                      slave=kwargs['slave'], hide=kwargs['hide'],
                      help='name of MeqParm table to be used')
    return True


def inarg_stations (pp, **kwargs):
    JEN_inarg.inarg_common(kwargs)
    JEN_inarg.define (pp, 'stations', range(5),
                      slave=kwargs['slave'], hide=kwargs['hide'],
                      choice=[range(7),range(14),range(15),range(2),'range(5)'],
                      help='the (subset of) stations to be used')
    return True


def inarg_redun (pp, **kwargs):
    JEN_inarg.inarg_common(kwargs)
    JEN_inarg.define (pp, 'redun', tf=False, 
                      slave=kwargs['slave'], hide=kwargs['hide'],
                      help='if True, redundant spacing calibration')
    return True



def inarg_solver_config (pp, **kwargs):
    JEN_inarg.inarg_common(kwargs, hide=True)
    JEN_inarg.define (pp, 'chain_solvers', True,
                      slave=kwargs['slave'], hide=kwargs['hide'],
                      help='if True, chain the solvers (recommended)')
    JEN_inarg.define (pp, 'master_reqseq', tf=False,
                      slave=kwargs['slave'], hide=kwargs['hide'],
                      help='if True, use a master reqseq for solver(s)')
    return True



def inarg_resample (pp, **kwargs):
    JEN_inarg.inarg_common(kwargs)
    JEN_inarg.define (pp, 'num_cells', None,
                      slave=kwargs['slave'], hide=kwargs['hide'],
                      choice=[None,[5,2],[2,2],[3,3]],  
                      help='if defined, ModRes argument [ntime,nfreq]')
    if False:
        # The following two are mutually exclusive with num_cells above...
        # Expected: a tuple/list of two integer factors [time,freq] >=0
        # If 0 or 1, no resampling is done in that dimension
        JEN_inarg.define (pp, 'downsample', None,
                          slave=kwargs['slave'], hide=kwargs['hide'],
                          choice=[None,[5,2],[2,2],[3,3]],  
                          help='if defined, ModRes argument (integer) [ntime,nfreq]')
        JEN_inarg.define (pp, 'upsample', None,
                          slave=kwargs['slave'], hide=kwargs['hide'],
                          choice=[None,[5,2],[2,2],[3,3]],  
                          help='if defined, ModRes argument (integer) [ntime,nfreq]')
    return True


def inarg_Cohset_common (pp, last_changed='<undefined>', **kwargs):
    """Some common JEN_inarg definitions for Cohset scripts"""
    # JEN_inarg.inarg_common(kwargs)
    JEN_inarg.define (pp, 'last_changed', last_changed,
                      editable=False, hide=True)
    MG_JEN_exec.inarg_ms_name(pp)
    MG_JEN_exec.inarg_tile_size(pp)
    MG_JEN_Joneset.inarg_Joneset_common(pp)
    MG_JEN_Joneset.inarg_Joneset_ParmSet(pp)

    # MG_JEN_Sixpack.inarg_punit(pp)

    inarg_solver_config (pp)
    inarg_redun(pp)
    inarg_resample(pp)
    return True









#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************
#********************************************************************************

def description ():
    """MG_JEN_Cohset.py contains a number of helper routines for inserting
    functionality for uv-data reduction"""
    return True


#----------------------------------------------------------------------------------------------------
# Intialise the MG control record with some overall arguments 
#----------------------------------------------------------------------------------------------------

MG = JEN_inarg.init('MG_JEN_Cohset', description=description.__doc__)

inarg_Cohset_common (MG, last_changed='d25feb2006')
JEN_inarg.modify(MG,
                 _JEN_inarg_option=None)     


# Simulation control, see below (not editable)
MG['simul'] = False

#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------


inarg = MG_JEN_exec.stream_control(_getdefaults=True, slave=True)
JEN_inarg.attach(MG, inarg)

inarg = make_spigots(_getdefaults=True)    
JEN_inarg.attach(MG, inarg)




#----------------------------------------------------------------------------------------------------
# Operations on the raw uv-data:
#----------------------------------------------------------------------------------------------------

if False:                    
   inarg = insert_flagger(_getdefaults=True)  
   JEN_inarg.attach(MG, inarg)
   


#----------------------------------------------------------------------------------------------------
# Insert a solver:
#----------------------------------------------------------------------------------------------------

#========
if True:                               
   inarg = MG_JEN_Sixpack.newstar_source(_getdefaults=True) 
   JEN_inarg.attach(MG, inarg)

   inarg = Jones(_getdefaults=True, slave=True)  
   JEN_inarg.attach(MG, inarg)

   inarg = predict(_getdefaults=True, slave=True)       
   JEN_inarg.attach(MG, inarg)

   #========
   if True and (not MG['simul']):                                        
       inarg = insert_solver(_getdefaults=True, slave=True) 
       JEN_inarg.attach(MG, inarg)
                 

#----------------------------------------------------------------------------------

# inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)   
inarg = make_sinks(_getdefaults=True)           
JEN_inarg.attach(MG, inarg)
                 




#====================================================================================
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)


#====================================================================================
# The MSauxinfo object contains auxiliary MS info (nodes):
# It is used at various points in this module, e.g. make_sinks()

def MSauxinfo(create=False):
    global msauxinfo
    if create:
        msauxinfo = TDL_MSauxinfo.MSauxinfo(label='MG_JEN_Cohset')
        msauxinfo.station_config_default()           # WSRT (15 stations), incl WHAT
    return msauxinfo
# Create the object:
MSauxinfo(create=True)



#********************************************************************************
#********************************************************************************
#***************** PART IV: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _tdl_predefine (mqs, parent, **kwargs):
    """_tdl_predefine() is a standard TDL name. When a forest script is
    loaded by, e.g., the browser, this method is called prior to
    defining the forest. The method can do anything: run a GUI, read
    config files, etc.
    Parameters:
      mqs:    a meqserver object.
      parent: parent widget (if running in a GUI), or None if no GUI
      kwargs: extra arguments (may be used by assay scripts, etc.)
    If this function returns a dict, this dict is passed as the kwargs
    of _define_forest(). 
    Errors should be indicated by throwing an exception.
    """

    res = True
    if parent:
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        try:
            igui = JEN_inargGui.ArgBrowser(parent)
            igui.input(MG, set_open=False)
            res = igui.exec_loop()
            if res is None:
                raise RuntimeError("Cancelled by user");
        finally:
            QApplication.restoreOverrideCursor()
    return res




#**************************************************************************

def _define_forest (ns, **kwargs):

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
    make_spigots(ns, Cohset, _inarg=MG)


    if False:
        # Optional: insert a flagger to the raw data: 
        insert_flagger (ns, Cohset, **MG)
        visualise (ns, Cohset)
        visualise (ns, Cohset, type='spectra')

    if True:
        # Optional: Insert a solver:
        Sixpack = MG_JEN_Sixpack.newstar_source(ns, _inarg=MG)
        Joneset = Jones(ns, Sixpack=Sixpack, simul=MG['simul'], _inarg=MG)
        predicted = predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG)
        if MG['simul']:
            # Replace the uv-data with the predicted visibilities: 
            Cohset.replace(ns, predicted)
            visualise (ns, Cohset)
            visualise (ns, Cohset, type='spectra')
        else:
            # Insert a solver for a named solvegroup of MeqParms (e.g. 'GJones'):
            insert_solver (ns, measured=Cohset, predicted=predicted, _inarg=MG)

    # Make MeqSink nodes that write the MS:
    sinks = make_sinks(ns, Cohset, _inarg=MG)
    cc.extend(sinks)

    # Finished: 
    return MG_JEN_exec.on_exit (ns, MG, cc)




#********************************************************************************
#********************************************************************************
#*******************  PART V: Forest execution routine(s) ***********************
#********************************************************************************
#********************************************************************************



def _tdl_job_execute (mqs, parent):
   """Execute the forest"""
   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG)
   return True


def _tdl_job_sequence(mqs, parent):
    """Execute the forest for a sequence of requests"""
    for x in range(10):
        MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19,
                               f1=x, f2=x+1, t1=x, t2=x+1,
                               save=False, trace=False, wait=False)
    MG_JEN_exec.save_meqforest(mqs) 
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





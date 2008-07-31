# file: ../JEN/demo/QuickRefUtil.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Utility functions for modules QuickRef.py and all QR_...py 
#
# History:
#   - 03 jun 2008: creation (from QuickRef.py)
#   - 07 jun 2008: added twig() etc
#   - 07 jun 2008: added 4D (L,M)
#   - 07 jun 2008: moved twig() etc to EasyTwig.py
#   - 01 jul 2008: implemented orphan functions
#   - 06 jul 2008: allow list of viewers in .bundle()
#   - 09 jul 2008: improved helpnode() behaviour
#   - 26 jul 2008: changed quickref_help into string etc
#   - 28 jul 2008: moved format_record() etc to EasyFormat.py
#
# Remarks:
#
# Description:
#


 
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
# from Timba.meqkernel import set_state

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []

import Meow.Bookmarks
from Timba.Contrib.JEN.util import JEN_bookmarks

import CollatedHelpRecord

from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN
from Timba.Contrib.JEN.QuickRef import EasyFormat as EF
from Timba.Contrib.JEN.QuickRef import QuickRefNodeHelp as QRNH

import copy
import math
import time
import os
# import random




#===============================================================================
# Test forest:
#===============================================================================

def _define_forest (ns, **kwargs):
    """Just for testing the various utility functions"""

    trace = False
    # trace = True
    cc = []
    
    rootnodename = 'QuickRefUtil'            # The name of the node to be executed...
    global rider
    rider = create_rider()                   # CollatedHelpRecord object
    rider.path(init=rootnodename)

    if True:
        ET.EN.orphans(ns << 1.2, trace=True)
    
    # Make the outer bundle (of node bundles):
    on_exit (ns, rider, nodes=cc, help=__doc__)
    
    if trace:
        rider.show('_define_forest()')

    # Finished:
    ET.EN.bundle_orphans(ns, trace=True)
    return True
   

#********************************************************************************
# Forest exection functions (also used externally from QR_... modules):
#********************************************************************************

TDLRuntimeMenu("Custom Settings:",
               TDLOption('runopt_show_request',"Show each request", [False, True, 'full']),
               TDLOption('runopt_show_bundles',"Show all bundle subtree(s)", False),
               TDLMenu("Printer settings (for hardcopy doc):",
                       TDLOption('runopt_printer',"name of the printer for harcopy",
                                 ['xrxwest','xrxmuller'], more=str),
                       TDLOption('runopt_fontsize',"hardcopy font size",
                                 [7,4,5,6,8], more=int),
                       ),
)
TDLRuntimeMenu("Parameters of the Request domain(s):",
               # None,
               TDLOption('runopt_separator',"",['']),
               TDLOption('runopt_nfreq',"nr of cells in freq direction",
                         [20,21,50,100,1000], more=int),
               TDLOption('runopt_fmin',"min freq (domain edge)",
                         [0.1,0.001,1.0,0.0,-math.pi,100.0,1e8,1.4e9], more=float),
               TDLOption('runopt_fmax',"max freq (domain edge)",
                         [2.0,math.pi,2*math.pi,100.0,2e8,1.5e9], more=float),
               # None,
               TDLOption('runopt_separator',"",['']),
               TDLOption('runopt_ntime',"nr of cells in time direction",
                         [3,1,2,4,5,10,11,21,100,1000], more=int),
               TDLOption('runopt_tmin',"min time (domain edge)",
                         [0.0,1.0,-1.0,-10.0], more=float),
               TDLOption('runopt_tmax',"max time (domain edge)",
                         [2.0,10.0,100.0,1000.0], more=float),
               # None,
               TDLOption('runopt_separator',"",['']),
               TDLMenu("(extra) parameters for execute_sequence",
                       TDLOption('runopt_seq_ntime',"nr of steps in time-sequence",
                                 [1,2,3,5,10], more=int),
                       TDLOption('runopt_seq_tstep',"time-step (fraction of domain-size)",
                                 [0.5,0.1,0.9,1.0,2.0,10.0,-0.5,-1.0], more=float),
                       # None,
                       TDLOption('runopt_separator',"",['']),
                       TDLOption('runopt_seq_nfreq',"nr of steps in freq-sequence",
                                 [1,2,3,5,10], more=int),
                       TDLOption('runopt_seq_fstep',"freq-step (fraction of domain-size)",
                                 [0.5,0.1,0.9,1.0,math.pi,2*math.pi,-0.5,-1.0], more=float),
                       ),
               # None,
               TDLOption('runopt_separator',"",['']),
               TDLMenu("(extra) parameters for axes (L,M):",
                       TDLOption('runopt_nL',"nr of cells in L direction",
                                 [3,1,2,3,5,10,11,21,50,100], more=int),
                       TDLOption('runopt_Lmin',"min L (domain edge)",
                                 [-1.0,-0.1,-0.001,-math.pi,-10.0,-100.0], more=float),
                       TDLOption('runopt_Lmax',"max L (domain edge)",
                                 [1.0,0.1,0.001,math.pi,10.0,100.0], more=float),
                       TDLOption('runopt_separator',"",['']),
                       TDLOption('runopt_nM',"nr of cells in M direction",
                                 [3,1,2,3,5,10,11,21,50,100], more=int),
                       TDLOption('runopt_Mmin',"min M (domain edge)",
                                 [-1.0,-0.1,-0.001,-math.pi,-10.0,-100.0], more=float),
                       TDLOption('runopt_Mmax',"max M (domain edge)",
                                 [1.0,0.1,0.001,math.pi,10.0,100.0], more=float),
                       ),
               # None,
               TDLOption('runopt_separator',"",['']),
               TDLMenu("(extra) parameters for axes (X,Y,Z):",
                       TDLOption('runopt_nX',"nr of cells in X direction",
                                 [3,1,2,3,5,10,11,21,50,100], more=int),
                       TDLOption('runopt_Xmin',"min X (domain edge)",
                                 [-1.0,-0.1,-0.001,-math.pi,-10.0,-100.0], more=float),
                       TDLOption('runopt_Xmax',"max X (domain edge)",
                                 [1.0,0.1,0.001,math.pi,10.0,100.0], more=float),
                       TDLOption('runopt_separator',"",['']),
                       TDLOption('runopt_nY',"nr of cells in Y direction",
                                 [3,1,2,3,5,10,11,21,50,100], more=int),
                       TDLOption('runopt_Ymin',"min Y (domain edge)",
                                 [-1.0,-0.1,-0.001,-math.pi,-10.0,-100.0], more=float),
                       TDLOption('runopt_Ymax',"max Y (domain edge)",
                                 [1.0,0.1,0.001,math.pi,10.0,100.0], more=float),
                       TDLOption('runopt_separator',"",['']),
                       TDLOption('runopt_nZ',"nr of cells in Z direction",
                                 [3,1,2,3,5,10,11,21,50,100], more=int),
                       TDLOption('runopt_Zmin',"min Z (domain edge)",
                                 [-1.0,-0.1,-0.001,-math.pi,-10.0,-100.0], more=float),
                       TDLOption('runopt_Zmax',"max Z (domain edge)",
                                 [1.0,0.1,0.001,math.pi,10.0,100.0], more=float),
                       ),
               # None,
               # TDLOption('runopt_separator',"",['']),
               )

# TDLRuntimeOptionSeparator()


#============================================================================
# Functions related to user-level (from QR_MeqNodes.py)
# This requires a little more thought....
# NB: The problem is that the other TDL options are updated BEFORE opt_user_level
#     This might be related to its place in the tdlconf file, due to the fact
#     that the opt_user_level was at the end of the TDLCompileMenu.....
#============================================================================

optoptrec = record()

def optopt(opt, trace=True):
   """Get the list of options for the specified (opt) TDLOption,
   depending on the current user level"""
   global opt_user_level
   global optoptrec
   if not optoptrec.has_key(opt):
      s = '\n** optopt(): not recognized: '+str(opt)
      raise ValueError,s
   result = optoptrec[opt][opt_user_level]
   if trace:
      print '\n** optopt(',opt,')',opt_user_level,'->',result,'\n'
   return result

def setoptopt(opt, beginner=[], advanced=[], blackbelt=[]):
   global optoptrec
   optoptrec[opt] = record(beginner=beginner, advanced=advanced, blackbelt=blackbelt)
   return True

setoptopt('test',range(2),range(3),range(4))
setoptopt('opt_solving_poly_twig',
          ET.twig_names(['gaussian'],first='gaussian_ft'),
          ET.twig_names(['gaussian','polyparm'],first='gaussian_ft'),
          ET.twig_names(['gaussian','polyparm','noise'],first='gaussian_ft'))

# TDLOption_user_level = TDLOption('opt_user_level',"user level",
#                            ['beginner','advanced','blackbelt'])
opt_user_level = None
def callback_user_level(level):
   global opt_user_level
   was = opt_user_level
   opt_user_level = level
   print '\n** callback_user_level(',level,')',was,'->',opt_user_level,
   print ':',optopt('test')
   print 
   return True

# TDLOption_user_level.when_changed(callback_user_level)



#============================================================================
# Tree execution functions:
#============================================================================

request_counter = 0

def make_request (cells, rqtype=None):
    """Make a request"""
    global request_counter
    request_counter += 1
    rqid = meq.requestid(request_counter)
    if isinstance(rqtype,str):
        # e.g. rqtype='ev' (for sequences, when the domain has changed)....
        rr = meq.request(cells, rqtype=rqtype)
        # return meq.request(cells, rqtype=rqtype, rqid=rqid)
    else:
        rr = meq.request(cells, rqid=rqid)

    if runopt_show_request:
        print '\n** QRU.make_request(',type(cells),'): counter=',request_counter,'-> rqid=',rqid
        print EF.format_record(rr, 'request', full=(runopt_show_request=='full'))
    return rr


#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

def make_cells (axes=['freq','time'], offset=None, trace=False):
    """Make a cells object, using the Runtime options (runopt_...).
    """
    s1 = '** QuickRefUtil('+str(axes)+'): '
    if trace:
        print '\n',s1

    # First some checks:
    raxes = ['freq','time','L','M','X','Y','Z']        # list of recognized axes
    for axis in axes:
        if not axis in raxes:
            s = s1+'**error**  axis not recognized: '+str(axis)
            raise ValueError,s

    # Check the offset-record:
    if not isinstance(offset,dict):
        offset = dict()
    for axis in raxes:
        offset.setdefault(axis,0.0)
    if trace:
        print '--- offset =',offset

    # Make the records for meq.gen_domain() and meq.gen_cells():
    dd = record()
    nn = record()
    if 'freq' in axes:
        dd.freq = (runopt_fmin+offset['freq'], runopt_fmax+offset['freq'])
        nn.num_freq = runopt_nfreq
    if 'time' in axes:
        dd.time = (runopt_tmin+offset['time'], runopt_tmax+offset['time'])
        nn.num_time = runopt_ntime
    if 'L' in axes:
        dd.L = (runopt_Lmin+offset['L'], runopt_Lmax+offset['L'])
        nn.num_L = runopt_nL
    if 'M' in axes:
        dd.M = (runopt_Mmin+offset['M'], runopt_Mmax+offset['M'])
        nn.num_M = runopt_nM
    if 'X' in axes:
        dd.X = (runopt_Xmin+offset['X'], runopt_Xmax+offset['X'])
        nn.num_X = runopt_nX
    if 'Y' in axes:
        dd.Y = (runopt_Ymin+offset['Y'], runopt_Ymax+offset['Y'])
        nn.num_Y = runopt_nY
    if 'Z' in axes:
        dd.Z = (runopt_Zmin+offset['Z'], runopt_Zmax+offset['Z'])
        nn.num_Z = runopt_nZ

    if trace:
        print '--- dd =',dd
        print '--- nn =',nn

    domain = meq.gen_domain(**dd)
    # print type(domain),domain
    cells = meq.gen_cells(domain, **nn)
    return cells

#----------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 1D (freq) domain."""
    return execute_ND (mqs, parent, axes=['freq'], rootnode=rootnode)

def _tdl_job_execute_f (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 1D (freq) domain."""
    return execute_ND (mqs, parent, axes=['freq'], rootnode=rootnode)

def _tdl_job_execute_t (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 1D (time) domain."""
    return execute_ND (mqs, parent, axes=['time'], rootnode=rootnode)

def _tdl_job_execute_L (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 1D (L) domain."""
    return execute_ND (mqs, parent, axes=['L'], rootnode=rootnode)

def _tdl_job_execute_M (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 1D (M) domain."""
    return execute_ND (mqs, parent, axes=['M'], rootnode=rootnode)

def _tdl_job_execute_X (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 1D (X) domain."""
    return execute_ND (mqs, parent, axes=['X'], rootnode=rootnode)

def _tdl_job_execute_Y (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 1D (Y) domain."""
    return execute_ND (mqs, parent, axes=['Y'], rootnode=rootnode)

def _tdl_job_execute_Z (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 1D (Z) domain."""
    return execute_ND (mqs, parent, axes=['Z'], rootnode=rootnode)


#----------------------------------------------------------------------------

def _tdl_job_execute_2D (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 2D domain (freq,time)."""
    return execute_ND (mqs, parent, axes=['freq','time'], rootnode=rootnode)

def _tdl_job_execute_ft (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 2D domain (freq,time)."""
    return execute_ND (mqs, parent, axes=['freq','time'], rootnode=rootnode)

def _tdl_job_execute_LM (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 2D domain (L,M)."""
    return execute_ND (mqs, parent, axes=['L','M'], rootnode=rootnode)

def _tdl_job_execute_XY (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 2D domain (X,Y)."""
    return execute_ND (mqs, parent, axes=['X','Y'], rootnode=rootnode)

#----------------------------------------------------------------------------

def _tdl_job_execute_3D (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 3D domain (freq,time,L)."""
    return execute_ND (mqs, parent, axes=['freq','time','L'], rootnode=rootnode)

def _tdl_job_execute_ftL (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 3D domain (freq,time,L)."""
    return execute_ND (mqs, parent, axes=['freq','time','L'], rootnode=rootnode)

def _tdl_job_execute_XYZ (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 3D domain (X,Y,Z)."""
    return execute_ND (mqs, parent, axes=['X','Y','Z'], rootnode=rootnode)

#----------------------------------------------------------------------------

def _tdl_job_execute_4D (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 4D domain (freq,time,L,M)."""
    return execute_ND (mqs, parent, axes=['freq','time','L','M'], rootnode=rootnode)

def _tdl_job_execute_ftLM (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 4D domain (freq,time,L,M)."""
    return execute_ND (mqs, parent, axes=['freq','time','L','M'], rootnode=rootnode)

def _tdl_job_execute_ftXY (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 4D domain (freq,time,X,Y)."""
    return execute_ND (mqs, parent, axes=['freq','time','X','Y'], rootnode=rootnode)

#----------------------------------------------------------------------------

def _tdl_job_execute_5D (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 5D domain (L,M,X,Y,Z)."""
    return execute_ND (mqs, parent, axes=['L','M','X','Y','Z'], rootnode=rootnode)

def _tdl_job_execute_LMXYZ (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 5D domain (L,M,X,Y,Z)."""
    return execute_ND (mqs, parent, axes=['L','M','X','Y','Z'], rootnode=rootnode)

#----------------------------------------------------------------------------

def _tdl_job_execute_6D_MIM (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 6D (MIM) domain (time,L,M,X,Y,Z)."""
    return execute_ND (mqs, parent, axes=['time','L','M','X','Y','Z'], rootnode=rootnode)

def _tdl_job_execute_tLMXYZ (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 6D (MIM) domain (time,L,M,X,Y,Z)."""
    return execute_ND (mqs, parent, axes=['time','L','M','X','Y','Z'], rootnode=rootnode)

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

def execute_ND (mqs, parent, axes=['freq','time'], rootnode='QuickRefUtil'):
    """Execute the forest with an ND domain, as specified by axes.
    """
    cells = make_cells(axes=axes)
    request = make_request(cells)
    result = mqs.meq('Node.Execute',record(name=rootnode, request=request))
    return result

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

def _tdl_job_execute_sequence (mqs, parent, rootnode='QuickRefUtil'):
    """Execute a sequence, moving the 2D domain.
    """
    if runopt_show_request:
        print '\n** _tdl_job_execute_sequence():'
        print '** runopt_seq_nfreq =',runopt_seq_nfreq, range(runopt_seq_nfreq)
        print '** runopt_seq_ntime =',runopt_seq_ntime, range(runopt_seq_ntime)

    for ifreq in range(runopt_seq_nfreq):
        foffset = (runopt_fmax - runopt_fmin)*ifreq*runopt_seq_fstep
        if runopt_show_request:
            print '\n** ifreq =',ifreq,' foffset =',foffset
        for itime in range(runopt_seq_ntime):
            toffset = (runopt_tmax - runopt_tmin)*itime*runopt_seq_tstep
            if runopt_show_request:
                print '   - itime =',itime,' toffset =',toffset
            cells = make_cells(offset=dict(freq=foffset, time=toffset))
            request = make_request(cells)
            result = mqs.meq('Node.Execute',record(name=rootnode, request=request))
    # Finished:
    print '\n** _tdl_job_execute_sequence(): finished\n'
    return result


    # NB: It executes the entire sequence before showing any plots! (or does it...?)
    # The things I have tried to make it display each result:
    # request = make_request(cells, rqtype='ev')
    # result = mqs.meq('Node.Execute',record(name='QuickRefUtil', request=request), wait=True)
    # time.sleep(1)

#----------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
    s = """** tdl_job_m() does nothing. It is just an artificial separator for TDL Exec menu.
    Since the tdl_jobs are listed alphabetically, its one-letter name (after _job_) must be
    a letter between e(xec) and p(rint). Hence m."""
    print s
    return None

#----------------------------------------------------------------------------

def _tdl_job_print_doc (mqs, parent, rr=None, header='QuickRefUtil'):
    """Print the formatted help from the rider (rr) on the screen
    """
    if rr==None:
        rr = rider             # i.e. the CollatedHelpObject
    print rr.format_html()
    return True

#----------------------------------------------------------------------------

def _tdl_job_print_hardcopy (mqs, parent, rr=None, header='QuickRefUtil'):
    """Print a hardcopy of the formatted help from the rider (rr).
    """
    if rr==None:
        rr = rider             # i.e. the CollatedHelpObject
    filename = 'QuickRef.tmp'
    # filename = header+'.tmp'
    # filename = rr.save(filename)
    filename = rr.save_html(header)
    # command = 'lp -d '+str(filename)
    # print '\n** tdl_job_print_hardcopy(): os.system(',command,')'
    # r = os.system(command)
    command = ['a2ps','-1','-f',str(runopt_fontsize),'-P',runopt_printer,filename]
    print '** tdl_job_print_hardcopy(): os.spawnvp(os.P_NOWAIT,a2ps,',command,')'
    r = os.spawnvp(os.P_NOWAIT,'a2ps',command)
    print '   ->',r,'**\n'
    return True

#----------------------------------------------------------------------------

def _tdl_job_show_doc (mqs, parent, rr=None, header='QuickRefUtil'):
    """Show the formatted help from the rider (rr) on a popup window.
    """
    if rr==None:
        rr = rider             # i.e. the CollatedHelpObject
    print rr.format()
    print rr.format_html()
    print '\n** The proper show_doc (popup) is not yet implemented **\n'
    return True

#----------------------------------------------------------------------------

def _tdl_job_save_doc (mqs, parent, rr=None, filename='QuickRefUtil'):
    """Save the formatted help from the rider (rr) in a file.
    """
    if rr==None:
        rr = rider             # i.e. the CollatedHelpObject
    # filename = rr.save(filename)
    filename = 'QuickRef'      # use standard filename for easy web-browser refresh
    filename = rr.save_html(filename)
    return True





#================================================================================
# Helper functions (called externally from QR_... modules):
#================================================================================




#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def MeqNode (ns, rider,
             meqclass=None, name=None,
             ## quals=None, kwquals=None,              # not a good idea...?
             node=None, children=None, unop=None,
             help=None, show_recurse=False,
             helpnode=False,
             trace=False, **kwargs):
    """
    <function_call>
    node = QuickRefUtil.MeqNode(ns, rider, ...)
    </function_call>
    
    This function is called from many functions in QR_... modules.
    It defines and returns the specified node an an organised way,
    avoiding nodename clashes, and using path and rider.

    Its arguments:
    <li> ns: nodescope
    <li> rider: ColleatedHelpRecord object
    <li> meqclass[=None]: name of the node class (e.g. 'Cos')
    <li> name[=None]: name (string) of the node
    <li> children[=None]: List of child nodes (if any)
    <li> unop[=None]: if string (e.g. Sin) or list (e.g. [Sin,Cos]), it applies the
    given unary operations to all the children first.
    <li> help[=None]: the help-string (if any) is disposed of in two ways: It is attached
    to the quickref_help field of the state record of the new node, and to the
    hierarchical help collected by the rider (for later display).
    <li> node[=None]: if already a node, it is used (i.e. no new node is defined).
    In that case, this function only serves to dispose of the help-string.
    <li> show_recurse[=False]: if True (or int>0, True=1000), a formatted version of the
    subtree below the node (to the required recursion depth) is attached to the help-string.
    <li> trace=[False]:
    <li> **kwargs: any keyword arguments will be passed to the node constructor.
    """


    #........................................................................

    # Optionally, apply a one or more unary math operations (e.g. Abs)
    # on all the children (if any):
    if unop:
        if isinstance(unop,str):
            unop = [unop]
        if isinstance(unop,(list,tuple)): 
            for unop1 in unop:
                if isinstance(children,(list,tuple)):
                    for i,child in enumerate(children):
                        children[i] = ns << getattr(Meq, unop1)(child)
                elif is_node(children):
                    children = ns << getattr(Meq, unop1)(children)


    #........................................................................
    # Condition the help-string (qhelp):
    #........................................................................

    # First make a MeqNode oneliner, for prepending to the MeqNode help:
    qhead = 'MeqNode: ns[\''+str(name)+'\']'

    if is_node(node):
        qhead += ': node='+str(node)

    elif helpnode:
        qhead = '\n\n'
        qhead += '<font color=\"red\">'
        qhead += 'ns[\''+str(name)+'\'] '+str(helpnode)
        qhead += '</font>  '

    else:
        qhead += '  <font color=\"red\">'
        qhead += ' &lt &lt &#32 Meq.'+str(meqclass)         # escape char &lt = <
        qhead += '</font>  '
        qhead += ' ('
        comma = ''
        if isinstance(children,(list,tuple)):
            nc = len(children)
            if nc==0:
                qhead += '(no children)'                    # should not happen...?
            elif nc==1:
                qhead += ' '+str(children[0])+' '
            else:
                qhead += '*['+str(nc)+' children]'
            comma = ', '                                    # used for kwargs below
        
        # Include all the ACTUAL keyword options used:
        for key in kwargs.keys():
            kw = kwargs[key]
            if key in ['children']:
                pass                                        # ignore
            elif key=='solvable' and isinstance(kw,(list,tuple)):
                qhead += comma+str(key)+'=['+str(len(kw))+' MeqParm(s)]'
            else:
                qhead += comma+str(key)+'='+str(kw)
            comma = ', '
        qhead += ')<br>'
    
    # The quickref_help (qhelp) string is a combination of qhead and help:
    qhelp = qhead
    if help:
        qhelp += '-'
        qhelp += rider.check_html_tags(str(help), include_style=False)

    if False:
        qhelp = QRNH.class_help(meqclass)                    # <----- !!
        
    # Optional, show the subtree below to the required depth:
    if show_recurse:
        if is_node(node):
            qhelp += EN.format_tree(node, recurse=show_recurse, mode='html')
        elif isinstance(children,(list,tuple)):
            qhelp += EN.format_tree(children, recurse=show_recurse, mode='html')
 
    # Dispose of the conditioned help (qhelp):
    # kwargs['quickref_help'] = qhelp                         # -> node state record
    # The rider is a CollatedHelpRecord object, which collects the
    # hierarchical help items, using the path string:
    # rider.insert_help(rider.path(temp=name), qhelp) 


    #........................................................................
    # Make the specified MeqNode:
    #........................................................................

    if is_node(node):
        # The node already exists. Just attach the help-string....
        EN.quickref_help(node, append=qhelp) 
      
    elif isinstance(children,(list,tuple)):              
        if isinstance(name,str):
            stub = EN.unique_stub(ns, name)
            node = stub << getattr(Meq,meqclass)(*children, **kwargs)
        else:
            node = ns << getattr(Meq,meqclass)(*children, **kwargs)

    elif is_node(children):
        child = children
        if isinstance(name,str):
            stub = EN.unique_stub(ns, name)
            node = stub << getattr(Meq,meqclass)(child, **kwargs)
        else:
            node = ns << getattr(Meq,meqclass)(child, **kwargs)

    else:                           
        if isinstance(name,str):
            stub = EN.unique_stub(ns, name)
            node = stub << getattr(Meq,meqclass)(**kwargs)
        else:
            node = ns << getattr(Meq,meqclass)(**kwargs)


    #........................................................................

    # Finished:
    if trace:
        nc = None
        if isinstance(children,(list,tuple)):
            nc = len(children)
        print '- QR.MeqNode():',meqclass,name,'(nc=',nc,') ->',str(node)
    return node



#-------------------------------------------------------------------------------
# Make a node that just carries help:
#-------------------------------------------------------------------------------

def helpnode (ns, rider,
              name=None,
              node=None,
              help=None,
              func=None,
              trace=False):
    """
    Syntax:
    <function_call>
    node = QRU.helpnode(ns, rider, name=None, node=None, help=None, func=None)
    </function_call>

    A special version of MeqNode(), for nodes that are only
    used to carry a quickref_help field in their state-record.
    <li> If no name is given, derive a name from the path.
    <li> If a function is specified (func), use its name and docstring.
    <li> If a node is specified, assume that it has a quickref_help field.
    
    Always make a bookmark for the node, with the 'QuickRef Display' viewer.
    """
    
    hh = 'module'
    if func:
        hh = str(func.__module__)
        if getattr(func, 'func_name', None):
            name = str(func.func_name)+'()'
        else:
            ss = hh.split('.')
            name = ss[len(ss)-1]
        hh = '<font color="red">  (see module: '+hh+')</font>'
        help = func.__doc__

    elif not isinstance(name,str):
        name = rider.nodestubname()

    qhelp = rider.html_style()
    qhelp += hh
    qhelp += rider.check_html_tags(help, include_style=False)

    if not is_node(node):
        stub = EN.unique_stub(ns, name)
        node = stub << Meq.Constant(value=-0.123456789,
                                    quickref_help=qhelp)
    else:
        EN.quickref_help(node, append=qhelp)
        # node.initrec().update(record(quickref_help=qhelp))

    # Make a bookmark with a suitable viewer:
    viewer = 'QuickRef Display'                                    # when implemented...
    JEN_bookmarks.create(node, page=name, folder='helpnodes', viewer=viewer)
    return node

#-------------------------------------------------------------------------------
# Entry routine:
#-------------------------------------------------------------------------------


def on_entry(ns, rider, func, trace=False):
    """
    The function QuickRefUtil.on_entry(ns, rider, QR_function) is called upon entry
    of all functions 'QR_function' in QR_... modules. It expects the arguments
    ns (nodescope), rider (CollatedHelpRecord object), and QR_function (a reference
    to the calling function itself.
    It returns a node-stub, which should be used (with qualifiers) to generate
    nodes in the function body. The stub is also used in the complementary function
    QRU.on_exit() to generate a 'parent' node that bundles the relevant nodes
    (in list cc) that are generated.
    """

    name = str(func.func_name)
    ss = name.split('_')
    # path = rider.path(append=ss[len(ss)-1])
    path = rider.path(append=ss[-1])            # the last item

    qhelp = rider.topic_header(path)
    qhelp += rider.check_html_tags(func.__doc__, include_style=False)
    rider.insert_help (path, qhelp, append=False)

    stub = EN.unique_stub(ns, rider.nodestubname())
    
    if trace:
        print '\n** .on_entry():',path,'->',str(stub)
    return stub
   

#-------------------------------------------------------------------------------
# Exit routine, returns a single parent node:
#-------------------------------------------------------------------------------

def on_exit (ns, rider, nodes=None,
             unop=None,
             parentclass='Composer', result_index=0,
             mode=None,            
             show_recurse=True,
             viewer='Result Plotter',
             help=None,                
             trace=False):
    """
    <function_call>
    node = QuickRefUtil.on_exit (ns, rider, nodes=None, ...)
    </function_call>
    
    Returns a single parent node, with bundles the given nodes.
    It also makes bookmarks if required, and controls the attachment of help,
    as quickref_help in node state record(s), and in the proper place (path)
    of the hierarchical help in the CollatedHelpRecord (rider).

    Its arguments:
    <li> ns: nodescope (mandatory)
    <li> rider: CollatedHelpRecord object (mandatory)
    <li> nodes[=None]: a list of 'nodes' to be bundled. The list items can be various things:
    <ul>
    <li> a node: It will be bundled, and bookmarked with the default viewer.
    <li> a string: It will be added to the bundle help
    <li> a record: In addition to a 'node' field, it may contain more detailed instructions for disposal.
    </ul>
    <li> unop[=None]: zero or more unary operations on the bundle nodes
    <li> parentclass[=Composer]: class of the bundle 'parent' node.
    This can be any class that takes an arbitrary nr of children.
    E.g.: Composer, Reqseq, Add, Multiply, etc
    <li> result_index[=0]: Used if parentclass=ReqSeq
    <li> help[=None]: If string, it will be added to the 'bundle help'.
    <li> mode[=None]: convenience/shortcut argument: if specified, it sets suitable
    values for certain other arguments (viewer, show_recurse).
    Example: mode='group': viewer='QuickRef Display', show_recurse=False.
    <li> show_recurse[=False]: If True or int>0, attach a formatted version of the
    parent subtree, to the specified recursion depth (True=1000), to the bundle help.
    <li> viewer[='Result Plotter']: The default viewer to be used by the bookmark(s).
    <li> trace[=False]: If True, print tracing messages (debugging)
    
    NB: This function is called at the exit of all functions in QR_... modules.
    """

    #.......................................................................
    # A mode may be specified, for convenience. (to be developed)

    if not isinstance(mode,str):
        pass
    elif mode=='group':
        viewer = 'QuickRef Display'
        node_help = False
        show_recurse = False

    #.......................................................................
    # Collect the actual nodes into 'bundle'. Deal appropriately with the
    # items that are not nodes:

    bhelp = ''                              # start of bundle help
    bundle = []                             # list of actual nodes
    bookmarks = []                          # list nodes to be bookmarked
    viewers = []                            # corresponding viewers
    for node in nodes:
        if is_node(node):                   # an actual node -> bundle
            bundle.append(node)
            bookmarks.append(node)
            viewers.append(viewer)
        elif isinstance(node,str):          # assume a help-text....
            bhelp += rider.check_html_tags(str(node), include_style=False)
            bhelp += '<br>'
        elif not isinstance(node,dict):
            bhelp += '\n<warning>'  
            bhelp += 'not recognized: '+str(type(node))
            bhelp += '\n</warning>'
        else:                               # a record with detailed instructions
            bundle.append(node['node'])           # 'node' is mandatory field
            # Deal with bookmark field:
            node.setdefault('bookmark',True)      # default behaviour
            if node['bookmark']:                  # inhibit if bookmark=False
                node.setdefault('viewer',viewer)  # default viewer
                vv = node['viewer']
                if isinstance(vv,bool) and vv:    # True -> default viewer
                    vv = [viewer]
                elif isinstance(vv,str):          # viewer specified
                    vv = [vv]
                if isinstance(vv,(list,tuple)): 
                    for v in vv:                  # for one or more viewers
                        bookmarks.append(node['node'])
                        viewers.append(v)
            # Deal with help-field:
            node.setdefault('help',False)
            hh = node['help']
            if isinstance(hh,bool) and hh:        # help=True: node-help
                QRNH.node_help(bundle[-1], rider=rider, trace=False)
            elif isinstance(hh,str):              # help is string
                bundle[-1].initrec().quickref_help = hh


    #.......................................................................
    # Append the contents of the help-argument, if string:
    if isinstance(help,str):
        bhelp += rider.check_html_tags(help, include_style=False)

    #.......................................................................
    # Make the bundle parent node:
    name = rider.nodestubname()
    parent = EN.unique_stub(ns, name)

    # Special case: no nodes to be bundled:
    if len(bundle)==0:
        parent << Meq.Constant(-0.123454321)
        ## bookmark = False                      # just in case

    else:
        if unop and len(bundle)>0:
            # Optionally, apply one or more unary math operations (e.g. Abs)
            # on all the nodes to be bundled:
            if isinstance(unop,str):
                unop = [unop]
            if isinstance(unop,(list,tuple)):
                for unop1 in unop:
                    for i,node in enumerate(bundle):
                        bundle[i] = ns << getattr(Meq, unop1)(node)

        # OK, bundle the given nodes by making them children of the specified parentclass:
        if parentclass=='ReqSeq':
            if not isinstance(result_index,int):
                if result_index=='last':
                    result_index = len(bundle)-1
                else:
                    result_index = 0                 # safe (not recognized...)
            parent << Meq.ReqSeq(children=bundle,
                                 result_index=result_index)

        elif parentclass in ['Add','Multiply']:
            parent << getattr(Meq,parentclass)(children=bundle)

        else:                                        # Assume MeqComposer:
            plot_label = []
            for node in bundle:
                plot_label.append(node.name)
            parent << Meq.Composer(children=bundle,
                                   plot_label=plot_label)


    #.......................................................................
    # Make a meqbrowser bookmark for the nodes in 'bookmarks', if required:
    if len(bookmarks)>0:
        # The rider object has a service for extracting page and folder from path.
        [page, folder] = rider.bookmark(rider.path(), trace=trace)
        if folder or page:
            if True:
                # Temporary, until Meow folder problem (?) is solved....
                # JEN_bookmarks.create(nodes, name, page=page, folder=folder, viewer=viewer)
                JEN_bookmarks.create(bookmarks, name=page, folder=folder, viewer=viewers)
            else:
                # NB: There does not seem to be a Meow way to assign a folder....
                bookpage = Meow.Bookmarks.Page(name, folder=bookfolder)
                for i,node in enumerate(bookmarks):
                    bookpage.add(node, viewer=viewers[i])

    #.......................................................................
    # Deal with the bundle help information (bhelp):
    # (NB: bhelp has been initialized above, with the contents of the help-argument,
    #      and any string-items in the 'nodes' list)

    # Optional, show the bundle parent subtree to the required depth:
    if show_recurse:
        bhelp += EN.format_tree(parent, recurse=show_recurse,
                                full=True, mode='html')

    # Update the CollatedHelpRecord (rider):
    rider.insert_help(rider.path(), bhelp, append=True)  

    # Extract the quickref_help string for the state record of the bundle node:
    # It contains the help for all topics below the current one (using path)
    qhelp = rider.format_html(path=rider.path())  
    parent.initrec().quickref_help = qhelp

    #.......................................................................

    # Show a resulting subtree, if required:
    if is_node(show_recurse):
        print EN.format_tree(show_recurse)
    elif show_recurse:
        print EN.format_tree(parent, recurse=show_recurse)
    elif runopt_show_bundles:
        print '\n** subtree under the bundle parent node (path=',rider.path(),'):'
        print EN.format_tree(parent, recurse=10)
    if trace:
        print '** QRU.on_exit() ->',str(parent),'\n'

    #.......................................................................
    # Shorten the rider path again (last statement)
    rider.path(up=True)               
    return parent





#=================================================================================
# Create the rider:
#=================================================================================

def create_rider(name='rider'):
    """Return a CollatedHelpRecord object, to serve as rider"""
    # import CollatedHelpRecord
    rider = CollatedHelpRecord.CollatedHelpRecord(name)
    rider.path(init=name)
    return rider


#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

    print '\n** Start of standalone test of: QuickRefUtil.py:\n' 
    ns = NodeScope()
    
    if 1:
        rider = create_rider()          # CollatedHelpRecord object

    if 0:
        path = 'aa.bb.cc.dd'
        help = 'xxx'
        rider.insert_help(path=path, help=help, trace=True)

    if 0:
        a = ns.a << 1.0
        b = ns.b << 3.0
        node = ns.test << Meq.Add(a,b)
        ss = EN.format_tree(node, mode='list', trace=True)
        print ss

    if 0:
        ss = """
        the rain in spain
        falls mainly in the plain
        <li>absg
        <li>lhg
        <li>lwbbcc

        the next paragraph

        and the next
        """
        check_html_tags(ss, trace=True)

    if 1:
        ss = rider.check_html_tags(on_entry.__doc__, include_style=True, trace=True)
        # ss = rider.check_html_tags(helpnode.__doc__, include_style=True, trace=True)
        ss = rider.check_html_tags(bundle.__doc__, include_style=True, trace=True)
        # ss = rider.check_html_tags(MeqNode.__doc__, include_style=True, trace=True)
        rider.save_html('QuickRefUtil.html', external=ss)

    print '\n** End of standalone test of: QuickRefUtil.py:\n' 

#=====================================================================================




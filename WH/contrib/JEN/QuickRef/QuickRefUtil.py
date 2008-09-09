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
#   - 14 aug 2008: made a single _tdl_job_execute()
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
                                 [-1.0,-0.1,-0.001,
                                  -math.pi/8.0, -math.pi/4.0,
                                  -math.pi/2.0, -math.pi,
                                  -10.0,-100.0], more=float),
                       TDLOption('runopt_Lmax',"max L (domain edge)",
                                 [1.0,0.1,0.001,
                                  math.pi/8.0, math.pi/4.0,
                                  math.pi/2.0, math.pi,
                                  10.0,100.0], more=float),
                       TDLOption('runopt_separator',"",['']),
                       TDLOption('runopt_nM',"nr of cells in M direction",
                                 [3,1,2,3,5,10,11,21,50,100], more=int),
                       TDLOption('runopt_Mmin',"min M (domain edge)",
                                 [-1.0,-0.1,-0.001,
                                  -math.pi/8.0, -math.pi/4.0,
                                  -math.pi/2.0, -math.pi,
                                  -10.0,-100.0], more=float),
                       TDLOption('runopt_Mmax',"max M (domain edge)",
                                 [1.0,0.1,0.001,
                                  math.pi/8.0, math.pi/4.0,
                                  math.pi/2.0, math.pi,
                                  10.0,100.0], more=float),
                       ),
               # None,
               TDLOption('runopt_separator',"",['']),
               TDLMenu("(extra) parameters for axes (X,Y,Z):",
                       TDLOption('runopt_nX',"nr of cells in X direction",
                                 [3,1,2,3,5,10,11,21,50,100], more=int),
                       TDLOption('runopt_Xmin',"min X (domain edge)",
                                 [-1.0,-0.1,-0.001,-math.pi,
                                  -10.0,-100.0,-1000.0], more=float),
                       TDLOption('runopt_Xmax',"max X (domain edge)",
                                 [1.0,0.1,0.001,math.pi,
                                  10.0,100.0,1000.0], more=float),
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

#-------------------------------------------------------------------------------------

def exec_domains(group=None, first=None):
    """Return a list of valid execution domains, to be used by _tdl_job_execute().
    """
    dd = []
    dd.extend(['1D_freq','1D_time'])
    dd.extend(['2D_ft'])
    dd.extend(['1D_L','1D_M'])
    dd.extend(['2D_LM'])
    dd.extend(['1D_X','1D_Y','1D_Z'])
    dd.extend(['3D_XYZ','3D_LMY','3D_ftY'])
    dd.extend(['4D_ftLM','4D_LMXY'])
    dd.extend(['5D_LMXYZ','5D_ftLMY'])
    dd.extend(['6D_tLMXYZ'])
    if isinstance(first,str):
        dd.insert(0,first)
    return dd

TDLRuntimeOption('runopt_exec_domain',"axes for _tdl_execute domain",
                 exec_domains(), more=str)


#============================================================================
# Functions related to user-level (from QR_MeqNodes.py)
# This requires a little more thought....
# NB: The problem is that the other TDL options are updated BEFORE opt_user_level
#     This might be related to its place in the tdlconf file, due to the fact
#     that the opt_user_level was at the end of the TDLCompileMenu.....
#============================================================================

optoptrec = record()

def optopt(opt, trace=False):
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
    if len(axes)==0:
        s = s1+'**error**  no axes specified'
        raise ValueError,s

    raxes = ['freq','time','L','M','X','Y','Z']        # list of recognized axes
    raxes.extend(['f','t'])                            # recognized aliases
    for i,axis in enumerate(axes):
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
    if ('freq' in axes) or ('f' in axes):
        dd.freq = minmax(runopt_fmin, runopt_fmax, offset['freq'])
        nn.num_freq = runopt_nfreq
    if ('time' in axes) or ('t' in axes):
        dd.time = minmax(runopt_tmin, runopt_tmax, offset['time'])
        nn.num_time = runopt_ntime
    if 'L' in axes:
        dd.L = minmax(runopt_Lmin, runopt_Lmax, offset['L'])
        nn.num_L = runopt_nL
    if 'M' in axes:
        dd.M = minmax(runopt_Mmin, runopt_Mmax, offset['M'])
        nn.num_M = runopt_nM
    if 'X' in axes:
        dd.X = minmax(runopt_Xmin, runopt_Xmax, offset['X'])
        nn.num_X = runopt_nX
    if 'Y' in axes:
        dd.Y = minmax(runopt_Ymin, runopt_Ymax, offset['Y'])
        nn.num_Y = runopt_nY
    if 'Z' in axes:
        dd.Z = minmax(runopt_Zmin, runopt_Zmax, offset['Z'])
        nn.num_Z = runopt_nZ

    if trace:
        print '--- dd =',dd
        print '--- nn =',nn

    domain = meq.gen_domain(**dd)
    # print type(domain),domain
    cells = meq.gen_cells(domain, **nn)
    return cells

#----------------------------------------------------------------------------

def minmax (vmin, vmax, offset=0.0):
    """
    Helper function to make sure that vmin and vmax are not the same.
    (the bowser cannot handle that, and dies ignominiously....)
    Called fom make_cells().
    """
    delta = 0.0
    if vmin==vmax:
        delta = max(abs(vmin),abs(vmax))*0.000001
        if delta==0.0:
            delta = 0.000001
    mm = (vmin-delta+offset, vmax+delta+offset)
    return mm

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------


def _tdl_job_execute_MS (mqs, parent, vdm_node='VisDataMux', trace=True):
    """
    Execute an MS (see Meow.MSUtils.py)
    """
    
    # Create inputrec:
    rec = record()
    rec.ms_name          = '3C286-10705290.MS',        # QuickRef MS filename
    rec.data_column_name = 'DATA'
    # rec.tile_segments    = tile_segments;
    # rec.tile_size        = tile_size;
    # rec.tile_size = tiling;
    # rec.selection = self.subset_selector.create_selection_record();
    # rec.apply_hanning = self.ms_apply_hanning;
    # Form top-level record
    inputrec = record(ms=rec)
    # inputrec.python_init = 'Meow.ReadVisHeader';
    # inputrec.mt_queue_size = ms_queue_size;

    # Create outputrec:
    rec = record()
    # rec.write_flags = self.ms_write_flags;
    # rec.data_column = self.output_column;
    # outputrec = record(ms=rec,mt_queue_size=ms_queue_size);
    outputrec = record(ms=rec)

    # Create_io_request, and execute:
    req = meq.request()
    req.input = inputrec
    req.output = outputrec
    result = mqs.execute(vdm_node, req, wait=False)

    if trace:
        print '\n** _tdl_job_execute_MS(',vdm_node,') ->',result,'\n'
        print '  req.input =',req.input
        print '  req.output =',req.output
        print
    return result

#----------------------------------------------------------------------------

def _tdl_job_execute (mqs, parent, rootnode='QuickRefUtil', trace=True):
    """
    Execute the forest with the domain (axes) specified by runopt_exec_domain.
    """
    domain = runopt_exec_domain                    # see TDLRuntimeOptions
    aa = domain.split('_')
    if len(aa)>1:
        aa = aa[1]
    else:
        aa = aa[0]
    axes = []
    for axis in ['freq','f','time','t','L','M','X','Y','Z']:
        if axis in aa:
            axes.append(axis)

    cells = make_cells(axes=axes)
    request = make_request(cells)
    result = mqs.meq('Node.Execute',record(name=rootnode, request=request))

    if trace:
        print '\n** _tdl_job_execute('+str(domain)+'):',aa,axes,'->',result,'\n'
    return result


#----------------------------------------------------------------------------

def _tdl_job_execute_sequence (mqs, parent, rootnode='QuickRefUtil'):
    """Execute a sequence, moving the 2D domain.
    """
    if runopt_show_request:
        print '\n** _tdl_job_execute_sequence():'
        print '** runopt_seq_nfreq =',runopt_seq_nfreq, range(runopt_seq_nfreq)
        print '** runopt_seq_ntime =',runopt_seq_ntime, range(runopt_seq_ntime)

    df = (runopt_fmax - runopt_fmin) 
    if df==0.0:
        df = 0.000001
    dt = (runopt_tmax - runopt_tmin)
    if dt==0.0:
        dt = 0.000001

    for ifreq in range(runopt_seq_nfreq):
        foffset = df*ifreq*runopt_seq_fstep
        if runopt_show_request:
            print '\n** ifreq =',ifreq,' foffset =',foffset
        for itime in range(runopt_seq_ntime):
            toffset = dt*itime*runopt_seq_tstep
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
#----------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
    s = """** tdl_job_m() does nothing. It is just an artificial separator for TDL Exec menu.
    Since the tdl_jobs are listed alphabetically, its one-letter name (after _job_) must be
    a letter between e(xec) and p(rint). Hence m."""
    print s
    return None

#----------------------------------------------------------------------------

def _tdl_job_print_doc (mqs=None, parent=None, rr=None, header='QuickRefUtil'):
    """Print the formatted help from the rider (rr) on the screen
    """
    if rr==None:
        rr = rider             # i.e. the CollatedHelpObject
    print rr.format_html()
    return True

#----------------------------------------------------------------------------

def _tdl_job_print_hardcopy (mqs=None, parent=None, rr=None, header='QuickRefUtil'):
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

def _tdl_job_show_doc (mqs=None, parent=None, rr=None, header='QuickRefUtil'):
    """Show the formatted help from the rider (rr) on a popup window.
    """
    if rr==None:
        rr = rider             # i.e. the CollatedHelpObject
    print rr.format()
    print rr.format_html()
    print '\n** The proper show_doc (popup) is not yet implemented **\n'
    return True

#----------------------------------------------------------------------------

def _tdl_job_save_doc (mqs=None, parent=None, rr=None, filename='QuickRefUtil'):
    """Save the formatted help from the rider (rr) in a html file.
    """
    if rr==None:
        rr = rider             # i.e. the CollatedHelpObject
    # filename = rr.save(filename)
    filename = 'QuickRef'      # use standard filename for easy web-browser refresh
    filename = rr.save_html(filename)
    return True

#----------------------------------------------------------------------------

def save_to_QuickRef_html (rider, filename='QuickRef'):
    """
    Save the formatted help from the rider in the file QuickRef.html.
    This function should be called at the end of each QR_ module...
    """
    return rider.save_html(filename)





#================================================================================
# Helper functions (called externally from QR_... modules):
#================================================================================

#-------------------------------------------------------------------------------
# Entry routine:
#-------------------------------------------------------------------------------


def on_entry(ns, rider, func, stubname=None, trace=False):
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
    path = rider.path(append=ss[-1])            # the last item (!)

    qhelp = rider.topic_header(path)
    qhelp += rider.check_html_tags(func.__doc__, include_style=False)
    rider.insert_help (path, qhelp, append=False)

    # Make a node-stub, for the topic nodes:
    if not isinstance(stubname,str):
        # If no stubname given, make one automatically:
        stubname = rider.nodestubname(short=True)
    stub = EN.unique_stub(ns, stubname)
    
    if trace:
        print '\n** .on_entry():',path,'->',str(stub)
    return stub
   
#-------------------------------------------------------------------------------
# Get TDL option value: 
#-------------------------------------------------------------------------------

def getopt (globals, name, rider=None, severe=True, trace=False):
   """
   Helper function to read the named TDL option value, and return it.
   The globals argument is the result of globals() in the calling module.
   If severe==True, throw an exception when not recognized.
   If a rider is given, a suitable message is inserted into the hierarchical help.
   """
   # trace = True

   # Read the value from globals (If the name does not exist, notrec is returned):
   notrec = '_UnDef_'
   value = globals.get(name, notrec)

   qhelp = ''
   qhelp += '<font color="red" size=2>'
   qhelp += '** TDLOption: '+str(name)+' = '
   if isinstance(value,str):
       qhelp += '"'+str(value)+'"'
   else:
       qhelp += str(value)
   
   if value==notrec:            
       qhelp += '<font color="red" size=5>'
       s = ' (option "'+name+'" not recognized)'
       qhelp += s
       qhelp += '</font>'
       trace = True
       if severe:
           raise ValueError,s

   qhelp += '</font>'
   qhelp += '<br>'

   if rider:
       path = rider.path()   
       rider.insert_help (path, qhelp, append=True)

   if trace:
      print '\n**',qhelp,'\n'
   return value






#-------------------------------------------------------------------------------
# Exit routine, returns a single parent node:
#-------------------------------------------------------------------------------

def on_exit (ns, rider, nodes=None,
             unop=None,
             parentclass='Composer', result_index=0,
             mode=None,            
             show_recurse=False,
             show_forest_state=False,
             show_bookmarks=False,
             show_bundle=False,
             bookmark_bundle_help=True,
             viewer='Result Plotter',
             node_help=True,
             help=None,
             trace=False):
    """
    <function_code>
    node = QuickRefUtil.on_exit (ns, rider, nodes=None, ...)
    </function_code>
    
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
    <li> node_help[=True]: If True, attach help to each node, and show in bundle-help. 
    <li> mode[=None]: convenience/shortcut argument: if specified, it sets suitable
    values for certain other arguments (viewer, show_recurse).
    Example: mode='group': viewer='QuickRef Display', show_recurse=False.
    <li> show_recurse[=False]: If True or int>0, attach a formatted version of the
    parent subtree, to the specified recursion depth (True=1000), to the bundle help.
    <li> show_bookmarks[=False]: If True, show the list of bookmarks/viewers 
    <li> show_forest_state[=False]: If True, bookmark the forest state record 
    <li> viewer[='Result Plotter']: The default viewer to be used by the bookmark(s).
    <li> bookmark_bundle_help[=True]: Also bookmark the bundle help (with QuickRef Display)
    <li> trace[=False]: If True, print tracing messages (debugging)
    
    NB: This function is called at the exit of all functions in QR_... modules.
    """

    #.......................................................................
    # A mode may be specified, for convenience. (to be developed)

    if not isinstance(mode,str):
        pass
    elif mode=='group':
        # Used for 'bundle of bundles':
        viewer = 'QuickRef Display'         # default viewer
        node_help = False
        bookmark_bundle_help = False
        show_recurse = False
        show_forest_state = False

    #.......................................................................
    # Collect the actual nodes into 'bundle'. Deal appropriately with the
    # items that are not nodes (e.g. strings or dicts):

    bhelp = ''                              # start of bundle help
    bundle = []                             # list of actual nodes
    bookmarks = []                          # list nodes to be bookmarked
    viewers = []                            # corresponding viewers
    for node in nodes:
        if is_node(node):                   # an actual node -> bundle
            bundle.append(node)

            if node.initrec().has_key('qbookmark') and (not node.initrec()['qbookmark']):
                pass                        # A bookmark may be inhibited by: qbookmark=False
            else:                           # assign a bookmark for this node
                bookmarks.append(node)
                viewers.append(viewer)                            # default viewer
                key = 'qviewer'
                if node.initrec().has_key(key):                   # viewer specified
                    vv = node.initrec()[key]
                    if not vv==None:
                        viewers[-1] = vv                          # replace viewer(s)

        elif isinstance(node,str):                            # assume a bundle help-text....(??)
            bhelp += rider.check_html_tags(str(node), include_style=False)
            bhelp += '<br>'

        else:               
            bhelp += '\n<warning>'  
            bhelp += 'not recognized: '+str(type(node))
            bhelp += '\n</warning>'


    #.......................................................................
    # Add help to nodes in the bundle. The specific and semi-specific parts
    # are contained in the node state fields qhelp, qspecific and qsemispec:

    if node_help:
        # nn = bundle                   # do for all the nodes in the bundle
        nn = bookmarks                # do for the bookmarked nodes only (better)
        for i,node in enumerate(nn):
            QRNH.node_help(nn[i], rider=rider, trace=False)

    #.......................................................................
    # Append the contents of the help-argument, if string:
    if isinstance(help,str):
        bhelp += rider.check_html_tags(help, include_style=False)

    #.......................................................................
    # Make the bundle parent node:
    name = rider.nodestubname()
    prefix = rider.topic_header(mode='prefix')
    name = prefix+name       
    parent = EN.unique_stub(ns, name)

    if len(bundle)==0:
        # Special case: no nodes to be bundled:
        parent << Meq.Constant(-0.123454321, qdummynode=True)

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
            if False:
                comment = """The bundle-parent node, shown for the value of its result_index,
                i.e. the index of the child whose result is passed on."""
                QRNH.node_help(parent, rider=rider, comment=comment, trace=False)

        elif parentclass in ['Add','Multiply']:
            parent << getattr(Meq,parentclass)(children=bundle)

        else:                                        # Assume MeqComposer:
            plot_label = []
            for node in bundle:
                plot_label.append(node.name)
            parent << Meq.Composer(children=bundle,
                                   plot_label=plot_label)


    # Optional, show the bundle parent subtree to the required depth:
    if show_recurse:
        if is_node(show_recurse):
            bhelp += '\n<br>'
            bhelp += EN.format_tree(show_recurse, recurse=True,
                                    full=True, mode='html')
        else:
            bhelp += '\n<br>** The resulting bundle subtree:<br>'
            bhelp += EN.format_tree(parent, recurse=show_recurse,
                                    full=True, mode='html')
    elif show_bundle:
        bhelp += '\n<br>** The following nodes are bundled by parent node: '+str(parent)+':<br>'
        for i,node in enumerate(bundle):
            bhelp += ' - '+str(node)+'<br>'
    bhelp += '<br>'


    #.......................................................................
    # Make a meqbrowser bookmark for the nodes in 'bookmarks', if required:
    if len(bookmarks)>0:
        # The rider object has a service for extracting page and folder from path.
        [page, folder] = rider.bookmark(rider.path(), trace=trace)
        if folder or page:

            if bookmark_bundle_help:
                # Append an extra bookmark with the bundle help...
                bookmarks.append(parent)
                viewers.append('QuickRef Display')

            # Deal with multiple viewers:
            ii = range(len(viewers))
            for i in ii:
                vv = viewers[i]
                if isinstance(vv,(list,tuple)):
                    for v1 in vv[1:]:
                        viewers.append(v1)                 # other viewer
                        bookmarks.append(bookmarks[i])     # copy the node
                    viewers[i] = vv[0]                     # replace with first viewer

            # Check that all viewers are strings:
            for i,v in enumerate(viewers):
                if not isinstance(v,str):                  # if not a string (e.g. True)
                    viewers[i] = viewer                    # ..use default viewer

            if show_bookmarks:
                bhelp += '\n<br>** The following nodes are bookmarked:'
                if page:
                    bhelp += ' on page: '+str(page)
                if folder:
                    bhelp += ' in folder: '+str(folder)
                bhelp += ':<br>'
                for i,node in enumerate(bookmarks):
                    bhelp += ' - '+str(node)+'   (viewer='+str(viewers[i])+')<br>'
                bhelp += '<br>'

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
    # Dispose of the accumulated bundle help information (bhelp):

    # Update the CollatedHelpRecord (rider):
    rider.insert_help(rider.path(), bhelp, append=True)  

    # Extract the quickref_help string for the state record of the bundle node:
    # It contains the help for all topics below the current one (using path)
    parent.initrec().quickref_help = rider.format_html(path=rider.path())

    #.......................................................................
    # Progress messages (debugging):

    # Show a resulting subtree, if required:
    if runopt_show_bundles:
        # Debugging only (see the generic runtime menu)
        print '\n** subtree under the bundle parent node (path=',rider.path(),'):'
        print EN.format_tree(parent, recurse=10)

    if trace:
        print '** QRU.on_exit() ->',str(parent),'\n'

    #.......................................................................
    # The LAST statement: Shorten the rider path again (last statement)
    rider.path(up=True)
    # Return the bundle parent node: 
    return parent




#-------------------------------------------------------------------------------
# Make a node that just carries help:
#-------------------------------------------------------------------------------

def helpnode (ns, rider,
              name=None,
              node=None,
              help=None,
              func=None,
              folder='helpnodes',
              trace=False):
    """
    A help-node is a dummy node with a quickref_help field.

    <function_code>
    node = QRU.helpnode(ns, rider, name=None, node=None, help=None, func=None)
    </function_code>

    A special version of MeqNode(), for nodes that are only
    used to carry a quickref_help field in their state-record.
    <li> If no name is given, derive a name from the path.
    <li> If a function is specified (func), use its name and docstring.
    <li> If a node is specified, assume that it has a quickref_help field.
    
    Always make a bookmark for the node, with the 'QuickRef Display' viewer.
    """

    qspec = 'This is a dummy node that carries a quickref_help field'
    
    hh = 'module'
    if func:
        hh = str(func.__module__)
        if getattr(func, 'func_name', None):
            name = str(func.func_name)+'()'
            qspec += ' for the function: '+name
            name = 'help_on_function__'+name
        else:
            ss = hh.split('.')
            name = ss[len(ss)-1]
            qspec += ' for: '+name
            name = 'help_on__'+name
        hh = '<font color="red">  (see module: '+hh+')</font>'
        help = func.__doc__

    elif not isinstance(name,str):
        name = rider.nodestubname()
        qspec += ' for: '+name
        name = 'help_on__'+name

    else:
        qspec += ' for: '+name
        name = 'help_on__'+name

    # Make a dummy node, if necessary:
    if not is_node(node):
        stub = EN.unique_stub(ns, name)
        node = stub << Meq.Constant(value=-0.123456789, qdummynode=True)

    # Attach qhelp to the node:
    qhelp = rider.html_style()
    qhelp += hh
    qhelp += rider.check_html_tags(help, include_style=False)
    node.initrec().quickref_help = qhelp
    node.initrec().qspecific = qspec             # specific node-help

    # Make a bookmark with a suitable viewer:
    viewer = 'QuickRef Display'           
    node.initrec().qviewer = viewer
    JEN_bookmarks.create(node, page=name, folder=folder, viewer=viewer)
    return node

#---------------------------------------------------------------------------

def how_to_use_this_module (ns, rider, name='QuickRef', topic=None):
    """
    Make a 'how-to' help-node for this QuickRef module.
    Called from define_forest() in each QR module.
    """
    ss = '<br><br>QuickRef module: <font size="10"><b>'+str(name)+'</b></font>: '
    if isinstance(topic,str):
        ss += topic
    if 'QR_' in name:
        ss += '<br><br>(It may be called from the module QuickRef.py. But it may also be used stand-alone)'

    ss += """
    <br><br>QuickRef modules offer MeqTree documentation,
    <i>and live demonstrations</i>, in the form of user-selectable 'topics'.
    For each selected topic, a <i>view</i> is generated in the form of a
    bookmarked page.
    Each <i>view</i> shows the results of a few selected MeqNodes
    in the little subtree that illustrates the topic.
    In addition, each <i>view</i> includes a text panel that shows the
    available documentation for the topic, complete with a full
    description of the relevant MeqNodes.
    The documentation for all the selected topics is collected in a
    single hierarchical document, which may be printed or browsed
    as a whole (see below).

    Using a QuickRef module has the following steps:
    
    <li> <b>Load</b> its TDL script into the meqbrowser (unless you
    are reading a hardcopy of the documentation, you have already done
    that).

    <li> Use the 'TDL Options' menu to <b>select one or more
    topics</b>, and to customize their parameter values (if any).

    <li> Use the <b>compile</b> button (or the blue button) to compile
    the tree, i.e. to generate the C++ nodes that are to be executed.

    <ol><i>
    <li> The tree will appear in the leftmost panel of the browser. It
    may be browsed, and the state of individual nodes may be
    inspected (before and after execution). 
    </i></ol>

    <li> Use the <b>bookmarks</b> menu to select one or more
    <i>views</i>. Note the text panel that explains its topic, and gives
    information about its MeqNodes etc.
    
    Use the 'TDL Exec' menu to execute the tree in various ways:
    
    <li> <b>execute</b>: A single request will be given to the root node of
    the tree. The parameters of the request domain may be modified
    with the 'runtime options' menu at the top of the popup execute
    panel.

    <li> <b>execute sequence</b>: Execute a sequence of requests. The
    sequence parameters may be modified with the 'runtime options'.

    <li> Specific QuickRef modules may have other execution modes.

    <ol><i>
    <li>The <i>views</i> will now show the results of those MeqNodes
    that illustrate the topic.  Use the right-click menu to inspect
    the various panels in detail.
    </i></ol>

    Below the separator <b>m</b>, the 'TDL Exec' menu offers a number of
    ways to manipulate the hierarchical documentation for the selected
    topics:

    <li> <b>print hardcopy</b>: This is a convenient way of making
    hardcopy subsets of the MeqTree documentation that may be perused
    in the train, in bed, in the woods etc.  The printer name may be
    modified with the 'runtime options' menu.

    <li> <b>save doc to QuickRef html</b>: The resulting file
    QuickRef.html may be opened with an html browser. In this mode,
    the various html links (e.g. to the meqwiki pages) actually work,
    and any supporting images are displayed (this is not the case in
    the meqbrowser panels, at least until we move from Qt3 to Qt4).

    <li> <b>show doc</b>: show the (html) documentation on the screen
    (debugging only)

    Enjoy.
    """
    return helpnode (ns, rider,
                     name='how_to_use_this_module',
                     help=ss, folder=None,
                     trace=False)


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




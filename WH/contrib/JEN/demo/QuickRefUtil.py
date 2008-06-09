# file: ../JEN/demo/QuickRefUtil.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Utility functions for modules QuickRef.py and all QR_...py 
#
# History:
#   - 03 june 2008: creation (from QuickRef.py)
#   - 07 jun 2008: added twig() etc
#   - 07 jun 2008: added 4D (L,M)
#   - 07 jun 2008: moved twig() etc to EasyTwig.py
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

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []

import Meow.Bookmarks
from Timba.Contrib.JEN.util import JEN_bookmarks

import EasyTwig as ET

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
    path = rootnodename                      # Root of the path-string
    global rider
    rider = create_rider()                   # CollatedHelpRecord object
    
    # Make the outer bundle (of node bundles):
    bundle (ns, path, nodes=cc, help=__doc__, rider=rider)
    
    if trace:
        rider.show('_define_forest()')

    # Finished:
    return True
   


#********************************************************************************
# Forest exection functions (also used externally from QR_... modules):
#********************************************************************************

TDLRuntimeMenu("Printer settings (for hardcopy doc):",
               TDLOption('runopt_printer',"name of the printer for harcopy",
                         ['xrxkantine'], more=str),
               TDLOption('runopt_fontsize',"hardcopy font size",
                         [7,4,5,6,8], more=int),
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
               TDLMenu("(extra) parameters for execute_seqence",
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
               TDLMenu("(extra) parameters for execute_4D:",
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
          ET.twig_names(['gaussian'],first='gaussianft'),
          ET.twig_names(['gaussian','polynomial'],first='gaussianft'),
          ET.twig_names(['gaussian','polynomial','noise'],first='gaussianft'))

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
        return meq.request(cells, rqtype=rqtype)
        # return meq.request(cells, rqtype=rqtype, rqid=rqid)
    else:
        return meq.request(cells, rqid=rqid)

#----------------------------------------------------------------------------

def make_cells (axes=['freq','time'], offset=None, trace=False):
    """Make a cells object, using the Runtime options (runopt_...).
    """
    s1 = '** QuickRefUtil('+str(axes)+'): '
    if trace:
        print '\n',s1

    # First some checks:
    raxes = ['freq','time','L','M']                 # list of recognized axes
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

    if trace:
        print '--- dd =',dd
        print '--- nn =',nn

    cells = meq.gen_cells(meq.gen_domain(**dd), **nn)
    return cells

#----------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 1D (freq) domain.
    """
    return execute_ND (mqs, parent, axes=['freq'], rootnode=rootnode)

#----------------------------------------------------------------------------

def _tdl_job_execute_2D (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 2D domain (freq,time).
    """
    return execute_ND (mqs, parent, axes=['freq','time'], rootnode=rootnode)

#----------------------------------------------------------------------------

def _tdl_job_execute_3D (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 3D domain (freq,time,L).
    """
    return execute_ND (mqs, parent, axes=['freq','time','L'], rootnode=rootnode)

#----------------------------------------------------------------------------

def _tdl_job_execute_4D (mqs, parent, rootnode='QuickRefUtil'):
    """Execute the forest with a 4D domain (freq,time,L,M).
    """
    return execute_ND (mqs, parent, axes=['freq','time','L','M'], rootnode=rootnode)

#----------------------------------------------------------------------------

def execute_ND (mqs, parent, axes=['freq','time'], rootnode='QuickRefUtil'):
    """Execute the forest with an ND domain, as specified by axes.
    """
    cells = make_cells(axes=axes)
    request = make_request(cells)
    result = mqs.meq('Node.Execute',record(name=rootnode, request=request))
    return result

#----------------------------------------------------------------------------

def _tdl_job_execute_sequence (mqs, parent, rootnode='QuickRefUtil'):
    """Execute a sequence, moving the 2D domain.
    """
    print '\n** _tdl_job_execute_sequence():'
    print '** runopt_seq_nfreq =',runopt_seq_nfreq, range(runopt_seq_nfreq)
    print '** runopt_seq_ntime =',runopt_seq_ntime, range(runopt_seq_ntime)
    for ifreq in range(runopt_seq_nfreq):
        foffset = (runopt_fmax - runopt_fmin)*ifreq*runopt_seq_fstep
        print '\n** ifreq =',ifreq,' foffset =',foffset
        for itime in range(runopt_seq_ntime):
            toffset = (runopt_tmax - runopt_tmin)*itime*runopt_seq_tstep
            print '   - itime =',itime,' toffset =',toffset
            cells = make_cells(offset=dict(freq=foffset, time=toffset))
            request = make_request(cells)
            result = mqs.meq('Node.Execute',record(name=rootnode, request=request))
    # Finished:
    print '\n** _tdl_job_execute_sequence(): finished\n'
    return result


    # NB: It executes the entire sequence before showing any plots!
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
    print rr.format()
    return True

#----------------------------------------------------------------------------

def _tdl_job_print_hardcopy (mqs, parent, rr=None, header='QuickRefUtil'):
    """Print a hardcopy of the formatted help from the rider (rr).
    """
    if rr==None:
        rr = rider             # i.e. the CollatedHelpObject
    filename = 'QuickRef.tmp'
    filename = rr.save(filename)
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
    print '\n** The proper show_doc (popup) is not yet implemented **\n'
    return True

#----------------------------------------------------------------------------

def _tdl_job_save_doc (mqs, parent, rr=None, filename='QuickRefUtil'):
    """Save the formatted help from the rider (rr) in a file.
    """
    if rr==None:
        rr = rider             # i.e. the CollatedHelpObject
    filename = rr.save(filename)
    return True








#================================================================================
# Helper functions (called externally from QR_... modules):
#================================================================================


def add2path (path, name=None, trace=False):
    """Helper function to form the path to a specific bundle.
    NB: This function is called from all QR_... modules!
    """
    s = str(path)
    if isinstance(name,str):
        s += '.'+str(name)
    if trace:
        print '\n** QR.add2path(',path,name,') ->',s
    return s


#-------------------------------------------------------------------------------

def helpnode (ns, path, name=None,
              # quals=None, kwquals=None,
              help=None, rider=None,
              trace=False):
    """A special version of MeqNode(), for nodes that are only
    used to carry a quickref_help field in their state-record.
    """
    if not isinstance(name,str):
        ss = path.split('.')
        nss = len(ss)
        name = ss[nss-1]
        if nss>1:
            name = ss[nss-2]+'_'+ss[nss-1]

    node = MeqNode (ns, path, meqclass='Constant',
                    name='helpnode'+'_'+name,
                    # quals=quals, kwquals=kwquals,                # .....??
                    help=help, rider=rider,
                    trace=trace, value=-0.123456789)
    print '\n**',name,':\n',help,'\n'                              # temporary
    viewer = 'QuickRef Browser'                                    # when implemented...
    viewer = 'Record Browser'                                      # temporary
    JEN_bookmarks.create(node, page=name, folder='helpnodes', viewer=viewer)
    return node


#-------------------------------------------------------------------------------

def MeqNode (ns, path,
             meqclass=None, name=None,
             # quals=None, kwquals=None,
             node=None, children=None, unop=None,
             help=None, rider=None,
             trace=False, **kwargs):
    """Define (make) the specified node an an organised way.
    NB: This function is called from all QR_... modules!
    """

    # First replace the dots(.) in the node-name (name): They cause trouble
    # in the browser (and elsewhere?)
    qname = str(name)
    qname = qname.replace('.',',')

    # Condition the help-string: prepend the node name, and make a list of lines:
    if isinstance(help, str):
        # May be multi-line (in triple-quotes, or containing \n): 
        qhelp = help.split('\n')                            # -> list
        qhelp[0] = str(qname)+': '+str(qhelp[0])            # prepend
    else:                                                  # should not happen...?
        qhelp = str(qname)+': '+str(help)                   # ...show something...

    # Dispose of the conditioned help (qhelp):
    kwargs['quickref_help'] = qhelp                        # -> node state record
    if rider:
        # The rider is a CollatedHelpRecord object, which collects the
        # hierarchical help items, using the path string:
        rider.insert_help(add2path(path,name), qhelp) 

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


    # Make the specified node:
    if is_node(node):
        # The node already exists. Just attach the help-string....
        # node = ns << Meq.Identity(node, quickref_help=qhelp)         # confusing...
        # NB: Is there a way to attach it to the existing node itself...?
        # node.initrec.quickref_help = qhelp               # causes error....
        pass
      
    elif isinstance(children,(list,tuple)):              
        if isinstance(name,str):
            stub = ET.unique_stub(ns, name)
            node = stub << getattr(Meq,meqclass)(*children, **kwargs)
        else:
            node = ns << getattr(Meq,meqclass)(*children, **kwargs)

    elif is_node(children):
        child = children
        if isinstance(name,str):
            stub = ET.unique_stub(ns, name)
            node = stub << getattr(Meq,meqclass)(child, **kwargs)
        else:
            node = ns << getattr(Meq,meqclass)(child, **kwargs)

    else:                           
        if isinstance(name,str):
            stub = ET.unique_stub(ns, name)
            node = stub << getattr(Meq,meqclass)(**kwargs)
        else:
            node = ns << getattr(Meq,meqclass)(**kwargs)


    if trace:
        nc = None
        if isinstance(children,(list,tuple)):
            nc = len(children)
        print '- QR.MeqNode():',path,meqclass,name,'(nc=',nc,') ->',str(node)
    return node


#-------------------------------------------------------------------------------

def bundle (ns, path,
            nodes=None, unop=None,
            help=None, rider=None,
            parentclass='Composer', result_index=0,
            bookmark=True, viewer="Result Plotter",
            make_helpnode=False,
            trace=False):
    """Make a single parent node, with the given nodes as children.
    Make bookmarks if required, and collate the help-strings.
    NB: This function is called from all QR_... modules!
    """

    # The name of the bundle (node, page, folder) is the last
    # part of the path string, i.e. after the last dot ('.')
    ss = path.split('.')
    nss = len(ss)
    name = ss[nss-1]
    qname = name
    if nss>1:
        qname = '*'+str(nss-2)+'* '+ss[nss-2]+'_'+ss[nss-1]
      
    # Condition the help-string and update the CollatedHelpRecord (rider):
    if isinstance(help, str):
        if make_helpnode:
            # Special case: make a separate helpnode/bookmark:
            helpnode(ns, path, rider=rider, help=help)
        qhelp = help.split('\n')
        qhelp[0] = qname+': '+qhelp[0]
    else:
        qhelp = qname+': '+str(help)

    if rider:
        rider.insert_help(path, qhelp)            # add qhelp to the rest
        # The relevant subset of help is attached to this bundle node:
        qhelp = rider.subrec(path, trace=trace)   # get (a copy of) the relevant sub-record 
        qhelp = qhelp.cleanup().chrec()           # clean it up (remove order fields etc) 

    # First make a nodestub with an unique name
    parent = ET.unique_stub(ns, name)
    print '---',path,': name=',name,'-> (unique?) parent=',str(parent)

    # Special case: no nodes to be bundled:
    if len(nodes)==0:
        parent << Meq.Constant(-0.123454321, quickref_help=qhelp)
        bookmark = False

    else:
        # Optionally, apply a one or more unary math operations (e.g. Abs)
        # on all the nodes to be bundled:
        if unop and len(nodes)>0:
            if isinstance(unop,str):
                unop = [unop]
            if isinstance(unop,(list,tuple)):
                for unop1 in unop:
                    for i,node in enumerate(nodes):
                        nodes[i] = ns << getattr(Meq, unop1)(node)

        # OK, bundle the given nodes by making them children of the specified parentclass:
        if parentclass=='ReqSeq':
            if not isinstance(result_index,int):
                if result_index=='last':
                    result_index = len(nodes)-1
                else:
                    result_index = 0                 # safe (not recognized...)
            parent << Meq.ReqSeq(children=nodes,
                                 result_index=result_index,
                                 quickref_help=qhelp)

        elif parentclass in ['Add','Multiply']:
            parent << getattr(Meq,parentclass)(children=nodes,
                                               quickref_help=qhelp)
        else:
            # Assume MeqComposer:
            plot_label = []
            for node in nodes:
                plot_label.append(node.name)
            parent << Meq.Composer(children=nodes,
                                   plot_label=plot_label,
                                   quickref_help=qhelp)

    # Make a meqbrowser bookmark for this bundle, if required:
    if bookmark:
        # By default, all nodes in the bundle will be bookmarked.
        # However, a different selection may be passed via the bookmark argument.
        if is_node(bookmark):
            nodes = [bookmark]
        elif isinstance(bookmark,(list,tuple)):
            nodes = bookmark

        # The rider object has a service for extracting page and folder from path.
        [page, folder] = rider.bookmark(path, trace=trace)

        if folder or page:
            if True:
                # Temporary, until Meow folder problem (?) is solved....
                # JEN_bookmarks.create(nodes, name, page=page, folder=folder, viewer=viewer)
                JEN_bookmarks.create(nodes, name=page, folder=folder, viewer=viewer)
            else:
                # NB: There does not seem to be a Meow way to assign a folder....
                bookpage = Meow.Bookmarks.Page(name, folder=bookfolder)
                for node in nodes:
                    bookpage.add(node, viewer=viewer)

    if trace:
        print '** QR.bundle():',path,name,'->',str(parent),'\n'
    return parent



#=================================================================================
# Helper Class, to be used as rider:
#=================================================================================

def create_rider(name='rider'):
    """Return a CollatedHelpRecord object, to serve as rider"""
    import CollatedHelpRecord
    return CollatedHelpRecord.CollatedHelpRecord(name)


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

    print '\n** End of standalone test of: QuickRefUtil.py:\n' 

#=====================================================================================




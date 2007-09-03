# file: ../twigs/Twig.py

# History:
# - 01sep2007: creation (from Executor.py)

# Description:

"""The Twig class makes it easy to generate a MeqTree 'twig', i.e. a smallish
subtree that end MeqLeaves (child-less nodes) like MeqTime and MeqParm etc.
It is expected to be popular for testing.
"""


#======================================================================================

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

import Meow                     # for Meow.Parm

from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN.Grunt import display

# from copy import deepcopy
import math

#======================================================================================

class Twig (object):
    """The Grunt Twig class allows the user to specify and generate
    a MeqTree twig, i.e. a small subtree that ends in child-less nodes
    (MeqLeaves)."""

    def __init__(self, name='Twig',
                 mode=None,
                 namespace='twig'):

        self.name = name
        self._frameclass = 'Grunt.Twig'       # for reporting

        self._OM = OptionManager.OptionManager(self.name, namespace=namespace)
        self._xtor = Executor.Executor('xtor', namespace=namespace)

        # Define the required runtime options:
        self._mode = None
        self._modes = dict()
        self._extra = []
        self.define_options()

        # Keep track of the data type and format
        self._data = dict(complex=False, tensor=False, nelem=1, dims=1)

        # Finished:
        return None


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = self._frameclass+':'
        ss += ' '+str(self.name)
        ss += '  mode='+str(self._mode)
        return ss


    def display(self, txt=None, full=False, recurse=3,
                OM=True, xtor=True, level=0):
        """Print a summary of this object"""
        prefix = '  '+(level*'  ')+'Twig'
        if level==0: print
        print prefix,' '
        print prefix,'** '+self.oneliner()
        if txt: print prefix,'  * (txt='+str(txt)+')'
        #...............................................................
        print prefix,'  *  available twig modes:'
        for mode in self._modes.keys():
            print prefix,'    - '+mode+': '+str(self._modes[mode])
        print prefix,'  *  extra: '+str(self._extra)
        print prefix,'  *  data: '+str(self._data)
        #...............................................................
        print prefix,'  * '+self._OM.oneliner()
        if OM: self._OM.display(full=False, level=level+1)
        #...............................................................
        print prefix,'  * '+self._xtor.oneliner()
        if xtor: self._xtor.display(full=False, level=level+1)
        #...............................................................
        print prefix,'**'
        if level==0: print
        return True




    #===================================================================

    def make_TDLRuntimeOptionMenu (self, **kwargs):
        """Make the TDL menu of run-time options"""
        # if not isinstance(kwargs, dict): kwargs = dict()
        # kwargs.setdefault('include_reset_option', True)
        self._xtor.make_TDLRuntimeOptionMenu(**kwargs)
        # self._OM.make_TDLRuntimeOptionMenu(**kwargs)
        return True
    
    #-------------------------------------------------------------------

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the TDL menu of run-time options"""
        self._xtor.make_TDLCompileOptionMenu(**kwargs)
        self._OM.make_TDLCompileOptionMenu(**kwargs)
        return True
    

    #-------------------------------------------------------------------

    def define_options(self):
        """Define the various compile-time options in its OptionManager object"""

        # Selection of twig mode:
        submenu = 'compile.'
        opt = ['MeqConstant','MeqParm','MeqGrids']
        # opt.extend(['PointSource22'])
        self._OM.define(submenu+'mode', 'MeqGrids',
                        opt=opt,
                        prompt='Twig mode (type)',
                        callback=self._callback_mode,
                        doc = """There are various kinds (modes) of twigs.
                        - MeqConstant: just a Meq.Constant
                        - MeqGrids: a hypercube of Meq.Grid nodes for the
                          selected (in xtor) compile-time dimensions.
                        """)

        # Submenus for the various twig modes:
        self.submenu_mode_MeqConstant()
        self.submenu_mode_MeqParm()
        self.submenu_mode_MeqGrids()

        # Submenus for optional operations on the end result:
        self.submenu_extra_make_tensor()
        # self.submenu_extra_make_list()
        self.submenu_extra_add_noise()
        self.submenu_extra_apply_unary()             # AFTER add_noise()
        self.submenu_extra_insert_flagger()
        self.submenu_extra_insert_modres()
        self.submenu_extra_insert_solver()
        self.submenu_extra_visualize()
        self.submenu_extra_make_bookmark()

        # Select an inital mode:
        self._callback_mode('MeqGrids')
        return True

    #...................................................................

    def _callback_mode (self, mode):
        """Called whenever the twig mode changes."""

        # print '\n** ._callback_mode(',mode,'):',self._modes.keys()

        # First hide/inactivate all mode submenus:
        for key in self._modes.keys():
            self._OM.hide('compile.'+key)

        # And unhide all the extra options:
        for key in self._extra:
            self._OM.show('compile.extra.'+key)

        # Then unhide the selected mode:
        self._mode = '??'
        if mode in self._modes.keys():
            self._mode = mode
            self._OM.show('compile.'+mode)          # Unhide the selected mode submenu
            for key in self._modes[mode]['hide']:   # Hide the relevant extra options
                self._OM.hide('compile.extra.'+key)

        # Indicate the selected mode in the top menu:
        menu = self._OM.TDLMenu('compile')
        if menu:
            menu.set_summary('(mode='+str(self._mode)+')')

        return True
        


    #====================================================================
    #====================================================================
    # Functions for twig modes:
    #====================================================================
    #====================================================================

    def submenu_mode_MeqConstant(self):
        """Define the options for a twig mode"""
        mode = 'MeqConstant'
        submenu = 'compile.'+mode+'.'
        self._OM.define(submenu+'value', 0.0,
                        prompt='value',
                        opt=[0.0,1.0,-1.0,(1+0j)], more=float,
                        doc="""set all domain cells to a constant value
                        """)
        self._modes[mode] = dict(hide=['insert_solver'])
        return True

    #--------------------------------------------------------------------

    def make_twig_for_mode_MeqConstant (self, ns, trace=False):
        """Create a MeqConstant node"""
        submenu = 'compile.'+self._mode+'.'
        value = self._OM[submenu+'value']
        self._data['complex'] = isinstance(value,complex)  # used downstream
        name = str(value)
        node = ns[name] << Meq.Constant(value)
        return self._check_node (node, submenu)


    #====================================================================
    #====================================================================

    def submenu_mode_MeqParm(self):
        """Define the options for a twig mode"""
        mode = 'MeqParm'
        submenu = 'compile.'+mode+'.'
        self._OM.define(submenu+'default', 0.0,
                        prompt='default value',
                        opt=[0.0,1.0,-1.0], more=float,
                        doc="""the default value of the MeqParm
                        """)
        self._OM.define(submenu+'freq_deg', 0,
                        prompt='freq polc',
                        opt=[0,1,2,3,4,5], more=int,
                        doc="""Degree (order) of the freq polynonial that is
                        to be solved for (constant in freq: freq_deg=0).
                        """)
        self._OM.define(submenu+'time_deg', 0,
                        prompt='time polc',
                        opt=[0,1,2,3,4,5], more=int,
                        doc="""Degree (order) of the time polynonial that is
                        to be solved for (constant in time: time_deg=0).
                        """)
        opt = [None,1,2,3,4,5,10]
        # opt.append(dmi.record(time=0,freq=0, l=.., m=..))
        self._OM.define(submenu+'tiling', None,
                        prompt='subtile size',
                        opt=opt,                    # more=str,
                        doc="""The domain (tile) may be split up into subtiles,
                        (for the moment, in the time-direction only)
                        If specified, different solutions are made for each
                        subtile, rather than a single one for the entire domain.
                        """)
        self._OM.define(submenu+'tags', [],
                        prompt='MeqParm tag(s)',
                        opt=[[],['solvable']],      # more=str,
                        doc="""Node tags can be used to search for (groups of)
                        nodes in the nodescope.
                        """)
        self._modes[mode] = dict(hide=['make_tensor'])
        return True

    #--------------------------------------------------------------------

    def make_twig_for_mode_MeqParm (self, ns, trace=False):
        """Create a MeqParm node, using a Meow.Parm definition"""
        submenu = 'compile.'+self._mode+'.'
        time_deg = self._OM[submenu+'time_deg']
        freq_deg = self._OM[submenu+'freq_deg']
        tags = self._OM[submenu+'tags']
        mparm = Meow.Parm(value=self._OM[submenu+'default'],
                          tiling=self._OM[submenu+'tiling'],
                          time_deg=time_deg,
                          freq_deg=freq_deg,
                          tags=tags)
        nodename = 'Meow.Parm[t'+str(time_deg)+',f'+str(freq_deg)+']'
        node = ns[nodename] << mparm.make()
        print '** node =',str(node)
        return self._check_node (node, submenu)



    #====================================================================
    #====================================================================

    def submenu_mode_MeqGrids(self):
        """Define the options for a twig mode"""
        mode = 'MeqGrids'
        submenu = 'compile.'+mode+'.'
        self._OM.define(submenu+'combine', 'Add',
                        prompt='combine with',
                        opt=['Add','Multiply','Composer'],
                        doc="""the MeqGrid nodes of the various dimensions
                        must be combined to a single root node
                        """)
        self._modes[mode] = dict(hide=['insert_solver'])
        return True

    #--------------------------------------------------------------------

    def make_twig_for_mode_MeqGrids (self, ns, trace=False):
        """Create a MeqGrids node"""
        submenu = 'compile.'+self._mode+'.'
        combine = self._OM[submenu+'combine']
        node = self._make_xtor_hypercube(ns, combine=combine)
        return self._check_node (node, submenu)


    def _make_xtor_hypercube(self, ns, combine='Add', name=None, trace=False):
        """Helper function to make a xtor hypercube"""
        # First get a list of the specified dimension leaf nodes/subtrees:
        dd = self._xtor.leafnodes(ns, trace=trace, return_list=True)
        if len(dd)==0:
            raise ValueError,'no compile-time dimensions'
        # Then combine these with the specified operation(s):
        if not isinstance(name, str):
            name = self._xtor.hypercube_name()
        node = ns[name] << getattr(Meq,combine)(*dd)
        return self._check_node (node, '_make_xtor_hypercube()')


    #====================================================================
    #====================================================================
    # Some helper function for checking:
    #====================================================================
    #====================================================================

    def _proceed_with_extra (self, ns, node, name, trace=True):
        """Helper function to decide whether to proceed with 'extra' function"""
        s = '\n** _proceed_with_extra('+str(node)+','+str(name)+'): '
        if not is_node(node):
            s += 'not a valid node'
        elif name in self._modes[self._mode]['hide']:
            s += 'not relevant for mode: '+self._mode
        else:
            return True                 # OK
        # Deal with the problem
        if trace:
            print s,'\n'
        return False

    #--------------------------------------------------------------------

    def _check_node (self, node, txt=None, severe=True, trace=True):
        """Helper function to check the node produced by a function"""
        s = '\n** _check_node('+str(node)+','+str(txt)+'): '
        if not is_node(node):
            s += 'not a valid node'
        else:
            return node                 # OK
        # Deal with the problem:
        print s,'\n'
        if severe:
            raise ValueError,s
        return False


    #====================================================================
    #====================================================================
    # Functions for operations on the end result:
    #====================================================================
    #====================================================================

    def submenu_extra_make_tensor(self):
        """Define the options for an operation on the twig result"""
        name = 'make_tensor'
        submenu = 'compile.extra.'+name+'.'
        opt = [None,'2','3','4','2x2']
        self._OM.define(submenu+'dims', None,
                        prompt='dims',
                        opt=opt, more=str,
                        doc="""duplicate scalar into a tensor node
                        """)
        self._extra.append(name)
        return True

    #--------------------------------------------------------------------

    def extra_make_tensor (self, ns, node, trace=False):
        """Optionally, make a tensor node from the given node"""
        name = 'make_tensor'
        if not self._proceed_with_extra (ns, node, name): return node
        submenu = 'compile.extra.'+name+'.'
        dims = self._OM[submenu+'dims']
        if dims==None:                  # not required
            return node
        try:                            # check for integer value
            dd = eval(dims)
        except:
            if 'x' in dims:             # check for nxm (or more)
                nelem = 1
                dd = dims.split('x')
                for i in range(len(dd)):
                    dd[i] = eval(dd[i])
                    nelem *= dd[i]
                nodename = 'tensor'+str(dd)
            else:                       # dims not recognised
                print 'dims =',dims
                raise ValueError,'invalid dims'
        else:                           # dims is integer 
            nelem = dd
            nodename = 'tensor['+str(nelem)+']'

        # OK, duplicate the input node and make the tensor:
        if nelem>1:
            self._data['tensor'] = (nelem>1)                     # used downstream
            self._data['nelem'] = nelem                          # used downstream
            self._data['dims'] = dims                            # used downstream
            nodes = []
            for i in range(nelem):
                nodes.append(ns['elem_'+str(i)] << Meq.Identity(node))
            node = ns[nodename] << Meq.Composer(children=nodes, dims=dd) 
        return self._check_node (node, submenu)


    #====================================================================
    #====================================================================

    def submenu_extra_apply_unary(self):
        """Define the options for an operation on the twig result"""
        name = 'apply_unary'
        submenu = 'compile.extra.'+name+'.'
        opt = ['Sqr','Sin','Cos','Exp','Abs','Negate','Pow3']    # safe always
        opt.extend(['Sqrt','Log','Invert'])                      # problems <=0
        self._OM.define(submenu+'unop', None,
                        prompt='unary',
                        opt=opt, more=str,
                        doc="""apply an unary operation.
                        """)
        self._extra.append(name)
        return True

    #--------------------------------------------------------------------

    def extra_apply_unary (self, ns, node, trace=False):
        """Optionally, apply an unary operation on the given node"""
        name = 'apply_unary'
        if not self._proceed_with_extra (ns, node, name): return node
        submenu = 'compile.extra.'+name+'.'
        unop = self._OM[submenu+'unop']
        if unop:
            node = ns << getattr(Meq,unop)(node)
        return self._check_node (node, submenu)

    #====================================================================
    #====================================================================

    def submenu_extra_make_bookmark(self):
        """Define the options for an operation on the twig result"""
        name = 'make_bookmark'
        submenu = 'compile.extra.'+name+'.'
        self._OM.define(submenu+'bookpage', 'twig',
                        opt=[None], more=str,
                        prompt='meqbrowser bookpage',
                        doc = """If specified, the leaf nodes generated with the
                        twig functions .leafnode() will be
                        be bookmarked on the same bookpage.
                        """)
        self._OM.define(submenu+'folder', None,
                        opt=[None], more=str,
                        prompt='bookpage folder',
                        doc = """All bookpages may be put into a folder
                        """)
        self._extra.append(name)
        return True

    #--------------------------------------------------------------------

    def extra_make_bookmark (self, ns, node, trace=False):
        """Optionally, bookmark the given node"""
        name = 'make_bookmark'
        if not self._proceed_with_extra (ns, node, name): return node
        submenu = 'compile.extra.'+name+'.'
        bookpage = self._OM[submenu+'bookpage']
        folder = self._OM[submenu+'folder']
        if node and bookpage:
            JEN_bookmarks.create(node, page=bookpage, folder=folder)
        return self._check_node (node, submenu)


    #====================================================================
    #====================================================================

    def submenu_extra_add_noise(self):
        """Define the options for an operation on the twig result"""
        name = 'add_noise'
        submenu = 'compile.extra.'+name+'.'
        self._OM.define(submenu+'stddev', None,
                        prompt='stddev',
                        opt=[0.1,1.0], more=float,
                        doc="""add gaussian noise (if stddev>0)
                        """)
        self._extra.append(name)
        return True

    #--------------------------------------------------------------------

    def extra_add_noise (self, ns, node, trace=False):
        """Optionally, add noise to the given node"""
        name = 'add_noise'
        if not self._proceed_with_extra (ns, node, name): return node
        submenu = 'compile.extra.'+name+'.'
        stddev = self._OM[submenu+'stddev']
        if stddev and stddev>0.0:
            name = '~'+str(stddev)
            noise = ns[name]
            if not noise.initialized():
                noise << Meq.GaussNoise(stddev=stddev)
                name = node.basename + name
                node = ns[name] << Meq.Add(node,noise)
        return self._check_node (node, submenu)


    #====================================================================
    #====================================================================

    def submenu_extra_insert_flagger(self):
        """Define the options for an operation on the twig result"""
        name = 'insert_flagger'
        submenu = 'compile.extra.'+name+'.'
        self._OM.define(submenu+'flag_oper', None,
                        prompt='flag operation',
                        opt=[None,'GT','GE','LE','LT'],
                        doc="""Flag those cells whose values are 'oper' zero.
                        """)
        self._OM.define(submenu+'cliplevel', 1.0,
                        prompt='clip level',
                        opt=[0.0,0.1,0.3,1.0,3.0,10.0], more=float,
                        doc="""Generate some flags by clipping.
                        Suggestion: add some noise first, and then amplify
                        it non-linearly with the unary (Exp) operation.
                        Use a 'local bookpage' (below) for experimentation.
                        """)
        self._OM.define(submenu+'bookpage', None,
                        prompt='local bookpage',
                        opt=[None,'insert_flagger'],
                        doc="""Make a 'local bookpage' with intermediate results
                        of the flagging operation. This is very convenient to see
                        what is going on when setting the clipping-level by hand.
                        """)
        self._extra.append(name)
        return True

    #--------------------------------------------------------------------

    def extra_insert_flagger (self, ns, node, trace=False):
        """Optionally, insert a flagger to generate some flags"""
        name = 'insert_flagger'
        if not self._proceed_with_extra (ns, node, name): return node
        submenu = 'compile.extra.'+name+'.'
        flag_oper = self._OM[submenu+'flag_oper']
        if flag_oper==None:
            return node                               # not required
        clip_level = self._OM[submenu+'cliplevel']
        bookpage = self._OM[submenu+'bookpage']
        cc = [node]                                   # keep for bookpage
        qnode = ns['flagger']
        
        # Flag the cells whose diff values are 'oper' zero (e.g. oper=GT)
        # NB: Assume that ZeroFlagger can have multiple children
        diff = qnode('diff') << Meq.Subtract(node, (ns.clip_level << clip_level)) 
        oper = 'GT'
        zflag = qnode('zflag') << Meq.ZeroFlagger(diff, oper=flag_oper)

        # The new flags are merged with those of the input node:
        node = qnode('mflag') << Meq.MergeFlags(children=[node,zflag])
   
        # Optional: merge the flags of multiple tensor elements of input/output:
        ## if pp.merge: output = ns.Mflag << Meq.MergeFlags(output)

        # Optionally, show the intermediary results. This is very useful
        # when trying to get useful clipping levels:
        if bookpage:
            folder = self._OM['compile.extra.make_bookmark.folder']
            cc.extend([diff,zflag,node])
            JEN_bookmarks.create(cc, page=bookpage, folder=folder)
        return self._check_node (node, submenu)


    #====================================================================
    #====================================================================

    def submenu_extra_insert_modres(self):
        """Define the options for an operation on the twig result"""
        name = 'insert_modres'
        submenu = 'compile.extra.'+name+'.'
        self._OM.define(submenu+'num_cells', None,
                        prompt='nr of cells [nt,nf]',
                        opt=[None,[2,3],[3,2]],
                        doc="""Covert the REQUEST to a lower a resolution.
                        """)
        self._OM.define(submenu+'bookpage', None,
                        prompt='local bookpage',
                        opt=[None,'insert_modres'],
                        doc="""Make a 'local bookpage' for the 'before'
                        and 'after' results of the resampling operation.
                        """)
        self._extra.append(name)
        return True

    #--------------------------------------------------------------------

    def extra_insert_modres (self, ns, node, trace=False):
        """Optionally, modify the cell resolution by resampling"""
        name = 'insert_modres'
        if not self._proceed_with_extra (ns, node, name): return node
        submenu = 'compile.extra.'+name+'.'
        
        num_cells = self._OM[submenu+'num_cells']
        if num_cells==None:
            return node                               # not required
        bookpage = self._OM[submenu+'bookpage']
        cc = [node]                                   # keep for bookpage
        qnode = ns['modres']
        
        highres = qnode('highres') << Meq.Identity(node) 
        lowres = qnode('lowres') << Meq.ModRes(node, num_cells=num_cells) 

        # The new flags are merged with those of the input node:
        node = qnode('reqseq') << Meq.ReqSeq(highres,lowres,
                                             result_index=0)
   
        # Optionally, show the intermediary results.
        if bookpage:
            folder = self._OM['compile.extra.make_bookmark.folder']
            cc.extend([highres,lowres,node])
            JEN_bookmarks.create(cc, page=bookpage, folder=folder)
        return self._check_node (node, submenu)


    #====================================================================
    #====================================================================

    def submenu_extra_insert_solver(self):
        """Define the options for an operation on the twig result"""
        name = 'insert_solver'
        submenu = 'compile.extra.'+name+'.'
        self._OM.define(submenu+'niter', None,
                        prompt='nr of iterations',
                        opt=[None,1,2,3,5,10,20,30,50,100],
                        doc="""Nr of solver iterations.
                        """)
        self._OM.define(submenu+'bookpage', None,
                        prompt='local bookpage',
                        opt=[None,'insert_solver'],
                        doc="""Make a 'local bookpage' for nodes that are relevant
                        for the solving operation (condeq, solver, parm).
                        """)
        self._extra.append(name)
        return True

    #--------------------------------------------------------------------

    def extra_insert_solver (self, ns, node, trace=False):
        """Optionally, insert a solver to generate some flags"""
        name = 'insert_solver'
        if not self._proceed_with_extra (ns, node, name): return node
        submenu = 'compile.extra.'+name+'.'
        niter = self._OM[submenu+'niter']
        if niter==None or niter<1:
            return node                               # not required

        qnode = ns['solver']
        lhs = self._make_xtor_hypercube(ns)           # left-hand side
        condeq = qnode('condeq') << Meq.Condeq(lhs,node)
        parm = ns.Search(tags='solvable', class_name='MeqParm')
        print '** parm =',str(parm[0])
        solver = qnode('solver') << Meq.Solver(condeq, num_iter=niter,
                                               solvable=parm)
        node = qnode('reqseq') << Meq.ReqSeq(children=[solver,node],
                                             result_index=1)
        
        # Optionally, bookmark the various relevant nodes.
        bookpage = self._OM[submenu+'bookpage']
        if bookpage:
            folder = self._OM['compile.extra.make_bookmark.folder']
            cc = [parm[0], lhs, condeq, solver]
            JEN_bookmarks.create(cc, page=bookpage, folder=folder)
        return self._check_node (node, submenu)

    #====================================================================
    #====================================================================

    def submenu_extra_visualize(self):
        """Define the options for an operation on the twig result"""
        name = 'visualize'
        submenu = 'compile.extra.'+name+'.'
        self._OM.define(submenu+'plot_type', None,
                        prompt='make a special plot',
                        opt=[None,'rvsi','time_tracks'], 
                        doc="""Special visualization
                        """)
        self._extra.append(name)
        return True

    #--------------------------------------------------------------------

    def extra_visualize (self, ns, node, trace=False):
        """Optionally, visualize the given node"""
        name = 'visualize'
        if not self._proceed_with_extra (ns, node, name): return node
        submenu = 'compile.extra.'+name+'.'
        plot = self._OM[submenu+'plot_type']
        return self._check_node (node, submenu)
        return node





    #====================================================================
    #====================================================================
    # Make the actual twig subtree:
    #====================================================================
    #====================================================================
    

    def make_twig (self, ns, qual='qual', trace=True):
        """Make the actual twig subtree, according to specifications."""
        if trace:
            print '\n** .make_twig(',qual,'):'

        # Work on a subscope....?
        if qual:
            ns = ns.Subscope('twig')(qual)
        else:
            ns = ns.Subscope('twig')

        # Make the twig subtree for the specified mode:
        node = None
        if self._mode=='MeqConstant':
            node = self.make_twig_for_mode_MeqConstant(ns, trace=trace)
        elif self._mode=='MeqParm':
            node = self.make_twig_for_mode_MeqParm(ns, trace=trace)
        elif self._mode=='MeqGrids':
            node = self.make_twig_for_mode_MeqGrids(ns, trace=trace)

        # Apply optional operation(s) on the end result:
        node = self.extra_make_tensor (ns, node, trace=trace)
        # node = self.extra_make_list (ns, node, trace=trace)
        node = self.extra_add_noise (ns, node, trace=trace)
        node = self.extra_apply_unary (ns, node, trace=trace)     # AFTER add_noise()
        node = self.extra_insert_flagger (ns, node, trace=trace)
        node = self.extra_insert_modres (ns, node, trace=trace)
        node = self.extra_insert_solver (ns, node, trace=trace)
        node = self.extra_visualize (ns, node, trace=trace)

        # Finished:
        node = self._check_node (node, '.make_twig()')
        if trace:
            display.subtree(node)
        node = self.extra_make_bookmark (ns, node, trace=trace)
        return node



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================

twig = None
if 1:
    twig = Twig()
    # twig._xtor.add_dimension('l', unit='rad')
    # twig._xtor.add_dimension('m', unit='rad')
    # twig._xtor.add_extra_dim('x', unit='m')
    # twig._xtor.add_extra_dim('y', unit='m')
    twig.make_TDLCompileOptionMenu()
    # twig.display()


def _define_forest(ns):

    global twig
    if not twig:
        twig = Twig()
        twig.make_TDLCompileOptionMenu()

    cc = []

    dimsum = twig.make_twig(ns)
    cc.append(dimsum)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    twig.make_TDLRuntimeOptionMenu()
    # twig.display('final', full=False)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent):
    """Execute the forest with the specified options (domain etc),
    starting at the named node"""
    return twig._xtor.execute(mqs, parent, start='result')
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the Twig object"""
    twig.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Twig object"""
    twig.display('_tdl_job', full=True)
       


       










#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()


    if 1:
        twig = Twig()
        twig.display('initial')

    if 0:
        twig.make_TDLRuntimeOptionMenu()

    if 1:
        twig.display('final')



#===============================================================


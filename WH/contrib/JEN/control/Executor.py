# file: ../Grunt/Executor.py

# History:
# - 25aug2007: creation
# - 01sep2007: moved to ../JEN/control/

# Description:

"""The Executor class makes it easier for the user to execute trees in
various ways:
- On the runtime side, it allows the specification of multi-dimensional
request(s), and to execute a tree with them.
- On the compile side, it allows the generation of a list of MeqGrid nodes
for (a subset of) the available dimensions (freq,time,etc). The latter
may also be combined into a single node, which thus depends on all these
dimensions.

Everything is controlled via the TDL exec (runtime) and TDL options (compile)
submenus of the meqbrowser. Bookmarks are generated for the result nodes.
All this makes the Executor a powerful tool for studying the behaviour of
all aspects of MeqTrees for various requests. This is useful for debugging
and for learning. It is hoped that it will help to lower the threshold for
learning and using MeqTrees considerably.

The Executor will be built into all the JEN demo scripts, and into all the
test-scripts in the modules of the Grunt framework.

NB: Note that the Executor should not (yet?) be used for trees that have
MeqSpigots and MeqSinks in them.
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

# import Meow

from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN.Grunt import display

# from copy import deepcopy
import math

#======================================================================================

class Executor (object):
    """The Grunt Executor class makes it easy to execute trees in various ways"""

    def __init__(self, name='Executor',
                 namespace='xtor'):

        self.name = name
        self._frameclass = 'Grunt.Executor'       # for reporting

        self._OM = OptionManager.OptionManager(self.name, namespace=namespace)

        # Dimensions control-dict:
        self._dims = dict()
        self._order = []

        # Define the required runtime options:
        self.define_runtime_options()

        self.request_counter = 0                  # see .request()
        
        # Finished:
        return None

    #-----------------------------------------------------------------

    def compile_dims(self):
        """Return a list of the 'active' compile dimensions"""
        return self.dims('compile')

    def runtime_dims(self):
        """Return a list of the 'active' runtime dimensions"""
        return self.dims('runtime')

    def hypercube_name (self, cat='compile'):
        """Return a useful name for the hypercube of dimensions"""
        dims = self.dims(cat)
        name = '#'
        if len(dims)==0: return name
        if len(dims)==1: return name+dims[0]  # full name of only dim
        for dim in dims:   
            name += dim[0]                    # string of first dim letters
        return name

    def dims(self, cat=None):
        """Return a list of the 'active' compile/runtime dimensions"""
        if cat==None:
            return self._order         # a list of all available dimensions        
        dims = []
        for dim in self._order:
            if self._dims[dim][cat]:   # active for cat(egory) 'compile' or 'runtime'
                dims.append(dim)
        return dims                    # a selection of the available dims

    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = self._frameclass+':'
        ss += ' '+str(self.name)
        ss += '  '+str(self._order)
        return ss


    def display(self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = '  '+(level*'  ')+'xtor'
        if level==0: print
        print prefix,' '
        print prefix,'** '+self.oneliner()
        if txt: print prefix,'  * (txt='+str(txt)+')'
        print prefix,'  * dimensions:'
        for dim in self._order:
            print prefix,'    - '+dim+': '+str(self._dims[dim])
        print prefix,'  * compile_dims() -> '+str(self.compile_dims())
        print prefix,'  * runtime_dims() -> '+str(self.runtime_dims())
        print prefix,'  * domain() -> '+str(self.domain())
        #...............................................................
        print prefix,'  * '+self._OM.oneliner()
        if OM: self._OM.display(full=False, level=level+1)
        #...............................................................
        print prefix,'**'
        if level==0: print
        return True




    #===================================================================
    # Run-time options (for making requests, etc):
    #===================================================================

    def make_TDLRuntimeOptionMenu (self, **kwargs):
        """Make the TDL menu of run-time options"""
        # if not isinstance(kwargs, dict): kwargs = dict()
        kwargs.setdefault('include_reset_option', True)
        return self._OM.make_TDLRuntimeOptionMenu(**kwargs)
    
    #-----------------------------------------------------------------------

    def define_runtime_options(self):
        """Define the (basic) runtime options in its OptionManager object.
        More are added in each user call to .add_dimension()."""

        # Individual options in the main menu (i.e. submenu=None):
        submenu = 'runtime.'
        opt = ['freq','time',['freq','time'],'ft','*']
        self._OM.define(submenu+'dims', '*',
                        opt=opt, more=str,
                        prompt='runtime dimension(s)',
                        callback=self._callback_runtime_dims,
                        doc = """The selecte dimensions will be used for
                        generating (a sequence of) multi-dimenional requests. 
                        """)

        self.add_dimension (dim='time', unit='s',
                            start=[0.0,1.0,10.0],
                            size=[1.0,10.0,100.0],
                            num_cells=[11,1,2,5,21,31,51,101])

        self.add_dimension (dim='freq', unit='Hz',
                            start=[0.0,1.0,10.0,100.0],
                            size=[1.0,10.0,100.0],
                            num_cells=[10,1,2,5,20,30,50,100])

        # Finished
        return True

        
    #.....................................................................

    def _callback_runtime_dims (self, dims):
        """Function called whenever TDLOption runtime.dims changes."""
        return self._callback_cat_dims ('runtime', dims)


    def _callback_cat_dims (self, cat, dims, trace=False):
        """Function that does the work for ._callback_runtime/compile_dims().
        It adjusts the activation of options according to 'dims'."""

        if trace:
            print '\n** ._callback_cat_dims(',cat,dims,'):'

        # First hide/inactivate all dimensions:
        alldims = ''
        for dim in self.dims():
            alldims += dim[0]
            self._OM.hide(cat+'.'+dim)
            self._dims[dim][cat] = False
            if trace: print '  --',dim,':',self._dims[dim]
        if dims=='*':
            dims = alldims

        # Then show/activate the selected ones:
        if isinstance(dims, list):           # e.g. dims=['freq','time']
            for dim in dims:
                if self._dims.has_key(dim): 
                    self._OM.show(cat+'.'+dim)
                    self._dims[dim][cat] = True
                    if trace: print '  ---',dim,':',self._dims[dim]

        elif dims in self.dims():            # e.g. dims='freq'
            self._OM.show(cat+'.'+dims)
            self._dims[dims][cat] = True
            if trace: print '  ----',dims,':',self._dims[dims]

        else:
            for dim in self.dims():          # e.g. dims='ftlm'
                for char in dims:
                    if dim[0]==char:
                        self._OM.show(cat+'.'+dim)
                        self._dims[dim][cat] = True
                        if trace: print '  -----',dim,':',self._dims[dim]

        menu = self._OM.TDLMenu(cat)
        if menu:
            menu.set_summary('(dims='+str(dims)+')')

        if trace: print
        return True
        

    #-------------------------------------------------------------------

    def add_dimension (self, dim, unit,
                       start=[1.0,0.0],
                       size=[1.0],
                       num_cells=[10,1,2,5,20,50,100],
                       num_steps=[1,2,5,10,100],
                       step=[1.0,0.5,0.1,-0.1,-0.5,-1.0],
                       offset=[0.0,0.5,1.0,10.0,-1.0]):
        """Generic function to make a dimension-menu"""

        if dim in self._dims.keys():
            raise ValueError, 'duplication of dims'

        # Make a vector or recognised standard units:
        units = self.dim_units(unit)

        # Make a control dict for this dimension:
        self._dims[dim] = dict(compile=True, runtime=True)
        self._order.append(dim)

        submenu = 'runtime.'+dim+'.'
        self._OM.define(submenu+'unit', units[0],
                        prompt=dim+'_unit',
                        opt=units,
                        doc='unit along '+dim+'-axis')
        self._OM.define(submenu+'start', start[0],
                        prompt='domain start',
                        opt=start, more=float,
                        doc='"lower" edge ('+dim+'-unit) of the domain')
        self._OM.define(submenu+'size', size[0],
                        prompt='domain size',
                        opt=size, more=float,
                        doc='domain size ('+dim+'-unit) in '+dim+' dimension')
        self._OM.define(submenu+'num_cells', num_cells[0],
                        prompt='nr of cells',
                        opt=num_cells, more=int,
                        doc='nr of domain cells in '+dim+' dimension')

        self._OM.define(submenu+'num_steps', num_steps[0],
                        prompt='nr of '+dim+' steps',
                        opt=num_steps, more=int,
                        doc='nr of steps in the sequence')
        self._OM.define(submenu+'step', step[0],
                        prompt='step size',
                        opt=step, more=float,
                        doc='size (fraction of domain-size) of a step')
        self._OM.define(submenu+'offset', offset[0],
                        prompt='offset',
                        opt=offset, more=float,
                        doc='offset (fraction of domain-size)')
        return True



    #=========================================================================
    # Forest execution:
    #=========================================================================

    def execute (self, mqs, parent, start='result', trace=True):
        """Execute the forest, starting at the named node (start)"""

        nodename = start
        if is_node(start):
            nodename = start.nodename
        if trace:
            print '\n** .execute():  (nodename =',str(nodename),')'
        if not isinstance(nodename,str):
            s = '\n** Execute: invalid nodename: '+str(nodename)
            raise ValueError,s

        # mode = self._OM['runtime.'+'mode']

        # Set up the sequence control dict:
        ctrl = dict()
        offset = dict()
        for dim in self.runtime_dims():
            rr = dict(count=0, finished=False)
            rr['num_steps'] = self._OM[dim+'.'+'num_steps']
            domain_size = self._OM[dim+'.'+'size']
            rr['step'] = self._OM[dim+'.'+'step']*domain_size
            rr['offset0'] = self._OM[dim+'.'+'offset']*domain_size
            ctrl[dim] = rr
            offset[dim] = rr['offset0']

        # Run the sequence:
        finished = False
        count = 0
        while (not finished):
            count += 1
            if trace:
                print '\n** execute step',count,': offset(s):',offset
                
            # Make a new request and execute with it:
            domain = self.domain (offset, trace=trace)
            cells = self.cells (domain=domain, trace=trace)
            request = self.request (cells=cells, trace=False)
            result = mqs.meq('Node.Execute',record(name=nodename, request=request))

            # Change the offsets and check progress:
            finished = True
            for dim in ctrl.keys():
                rr = ctrl[dim]
                rr['count'] += 1
                if rr['count']<rr['num_steps']:     # not yet finished:  
                    offset[dim] += rr['step']       #   change the offset for this dim
                else:                               # the sequence for this dim is finished:
                    offset[dim] = rr['offset0']     #   reset to starting offset 
                    rr['count'] = 0                 #   reset the count
                    rr['finished'] = True     
                # Continue until finished for ALL runtime dimensions:
                if not rr['finished']: finished = False

        # Finished:
        if trace:
            print '** -> result =',type(result),'\n'
        return result


    #-------------------------------------------------------------------

    def request (self, cells=None, trace=False):
        """Helper function to make a request"""
        if not cells:
            cells = self.cells(trace=trace)
        # request = meq.request(cells, rqtype='ev')      # does not renew the request....
        self.request_counter += 1
        rqid = meq.requestid(self.request_counter)
        if trace:
            print '** rqid(',self.request_counter,') =',rqid
        request = meq.request(cells, rqid=rqid)
        return request

    
    #-------------------------------------------------------------------
    

    def cells (self, domain=None, trace=False):
        """Helper function to make a cells"""
        if not domain:
            domain = self.domain(trace=trace)

        pp = dict()
        for dim in self.runtime_dims():
            pp['num_'+dim] = self._OM[dim+'.'+'num_cells']
        cells = meq.gen_cells(domain, **pp)

        if trace:
            print '** cells: ', pp
            print '** domain(cells) =',str(domain)
            # print '** cells =',cells,'\n'
        return cells


    #-------------------------------------------------------------------


    def domain (self, offset=None, trace=False):
        """Make a domain from the internal information.
        The (optional) offsets are for making sequences.
        """

        pp = dict()
        for dim in self.runtime_dims():
            mult = self.conversion_factor(self._OM[dim+'.'+'unit']) 
            v0 = 0.0
            if offset:
                v0 = offset[dim]
            v1 = v0+self._OM[dim+'.'+'start']*mult
            v2 = v1+self._OM[dim+'.'+'size']*mult
            pp[dim] = (v1,v2)
        domain = meq.gen_domain(**pp)

        if trace:
            print '** domain =',str(domain)
        return domain
       
    
      

    #=========================================================================
    # Convenience functions that deal with units:
    #=========================================================================

    def dim_units (self, unit=None, trace=False):
        """Return a vector of alternative units of the same dimension as
        the specified 'unit'. Make sure that the latter is the first in
        this list, i.e. the default (see add_dimension())
        These units are recognised in .conversion_factor().
        """
        rr = dict(freq=['Hz','kHz','MHz','GHz'],
                  time=['s','min','hr','day'],
                  angle=['rad','deg','arcmin','arcsec'],
                  length=['m','cm','mm','km','micron','nm'])
        uu = None
        for key in rr.keys():
            if unit in rr[key]:
                uu = rr[key]
                if not uu[0]==unit:
                    uu.remove(unit)
                    uu.insert(0,unit)
        if not uu:
            s = '** unit not recognised: '+str(unit)
            print s
            raise ValueError, s
        return uu

    #------------------------------------------------------------------------------

    def conversion_factor (self, unit=None, target=None, trace=False):
        """Helper function to calculate the (multiplicative) unit conversion factor"""
        if unit=='s':                  # default time unit
            mult = 1.0
        elif unit=='min':
            mult = 60.0
        elif unit=='hr':
            mult = 3600.0
        elif unit=='day':
            mult = 60.0*3600.0

        elif unit=='Hz':               # default freq unit
            mult = 1.0
        elif unit=='kHz':
            mult = 1e3
        elif unit=='MHz':
            mult = 1e6
        elif unit=='GHz':
            mult = 1e9

        elif unit=='rad':              # default angle unit
            mult = 1.0
        elif unit=='deg':
            mult = 180.0/math.pi
        elif unit=='deg':
            mult = 180.0/math.pi
        elif unit=='arcmin':
            mult = 60.0*(180.0/math.pi)
        elif unit=='arcsec':
            mult = 3600.0*(180.0/math.pi)

        elif unit=='m':                # default length unit
            mult = 1.0
        elif unit=='km':         
            mult = 1e3
        elif unit=='cm':         
            mult = 1e-2
        elif unit=='mm':         
            mult = 1e-3
        elif unit in ['um','micron']:         
            mult = 1e-6
        elif unit=='nm':         
            mult = 1e-9

        else:
            mult = 1.0                 # default
        return mult




    

    #===================================================================
    #===================================================================
    # Compile-time options (for building trees):
    #===================================================================
    #===================================================================

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the TDL menu of run-time options"""
        self.define_compile_options()
        return self._OM.make_TDLCompileOptionMenu(**kwargs)
    
    
    #-------------------------------------------------------------------

    def define_compile_options(self):
        """Define the various compile-time options in its OptionManager object"""


        # Selection of dimensions:
        submenu = 'compile.'
        opt = ['freq','time',['freq','time'],'ft','*']
        self._OM.define(submenu+'dims', '*',
                        opt=opt, more=str,
                        prompt='compile-time dimension(s)',
                        callback=self._callback_compile_dims,
                        doc = """The selected dimensions will be used in
                        the tree-generating function _define_forest().""")

        # Submenus for all available dimensions:
        for dim in self.dims():
            submenu = 'compile.'+dim+'.'

            opt = ['Sqr','Sin','Cos','Exp','Abs','Negate','Pow3']    # safe always
            opt.extend(['Sqrt','Log','Invert'])                      # problems <=0
            self._OM.define(submenu+'unop', None,
                            prompt='apply unary()', opt=opt,
                            doc='apply unary operation')

            self._OM.define(submenu+'stddev', None,
                            prompt='add stddev noise',
                            opt=[0.1,1.0], more=float,
                            doc='add gaussian noise (if stddev>0)')

        # Overall options:
        submenu = 'compile.'
        self._OM.define(submenu+'bookpage', 'xtor',
                        opt=[None], more=str,
                        prompt='meqbrowser bookpage',
                        doc = """If specified, the leaf nodes for the various
                        dimensions will be bookmarked on this bookpage.""")
        return True

    #....................................................................

    def _callback_compile_dims (self, dims):
        """Function called whenever TDLOption compile.dims changes."""
        return self._callback_cat_dims ('compile', dims, trace=False)


    #====================================================================
    # Functions to be used in _define_forest()
    #====================================================================
    
    def leafnodes (self, ns, return_list=False, 
                  bookpage=None, folder=None, trace=True):
        """Return a dict or list of 'leaf' nodes for the seleced compile-time
        dimensions. The dict fields are named after the dimensions.
        The leaves are usually MeqGrid nodes (like MeqTime), but they
        an also be subtrees with unary operations and added noise etc.
        """
        if trace:
            print '\n** .leafnodes(',type(ns),return_list,'):'
            for dim in self._dims:
                print ' - self._dims[',dim,'] =',self._dims[dim]

        nn = dict()
        dd = []
        for dim in self.compile_dims():
            qnode = ns[dim]
            if not qnode.initialized():
                qnode << Meq.Grid(axis=dim)
            if trace:
                print ' * ',dim,':',str(qnode)
                
            # Optional: add gaussian noise:
            stddev = self._OM['compile.'+dim+'.'+'stddev']
            if stddev:
                noise = ns[dim+'_noise']
                if not noise.initialized():
                    noise << Meq.GaussNoise(stddev=stddev) 
                qnode = ns << Meq.Add(qnode,noise)
                if trace:
                    print '    - stddev =',stddev,' ->',str(qnode)

            # Optional: apply and unary operation
            unop = self._OM['compile.'+dim+'.'+'unop']
            if unop:
                qnode = ns << getattr(Meq,unop)(qnode) 
                if trace:
                    print '    - unop =',unop,' ->',str(qnode)
            
            # Dispose of the finished leaf node/subtree for this dimension 
            nn[dim] = qnode
            dd.append(qnode)
            self._create_bookmark(qnode, bookpage=bookpage, folder=folder)

        # Return either a list or a dict:
        if return_list:
            return dd
        return nn

    #------------------------------------------------------------------------

    def leafnode (self, ns, combine='Add', name=None,
                  bookpage=None, folder=None, trace=True):
        """Combine the node(s) resulting from .leafnodes() into
        a single leaf node (subtree, really), using the specified
        (combine) operation. Optionally, a nodename may be specified.
        Optionally, a bookmark will be generated.
        """
        if trace:
            print '\n** .leafnode(',combine,name,bookpage,'):'

        # First get a list of the specified dimension leaf nodes/subtrees:
        dd = self.leafnodes(ns, trace=trace, return_list=True,
                            bookpage=bookpage, folder=folder)

        # Then combine these with the specified operation(s):
        node = None
        if combine in ['Add','Multiply']:
            node = ns << getattr(Meq,combine)(*dd)
            
        if not node:
            return node
        if trace:
            display.subtree(node)
        self._create_bookmark(node, bookpage=bookpage, folder=folder)
        return node

    #................................................................
        
    def _create_bookmark(self, node, bookpage=None, folder=None):
        """Helper function, called by .leafnode(s)()"""
        bookpage = self._OM['compile.'+'bookpage'] or bookpage
        if node and bookpage:
            JEN_bookmarks.create(node, page=str(bookpage), folder=folder)
        return True

#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================

xtor = None
if 0:
    xtor = Executor()
    xtor.add_dimension('l', unit='rad')
    xtor.add_dimension('m', unit='rad')
    # xtor.add_extra_dim('x', unit='m')
    # xtor.add_extra_dim('y', unit='m')
    xtor.make_TDLCompileOptionMenu()
    # xtor.display()


def _define_forest(ns):

    global xtor
    if not xtor:
        xtor = Executor()
        xtor.make_TDLCompileOptionMenu()

    cc = []

    if True:
        dimsum = xtor.leafnode(ns, 'Add')
    else:
        dd = xtor.leafnodes(ns, return_list=True)
        dimsum = ns['dimsum'] << Meq.Add(*dd)
        JEN_bookmarks.create(dimsum)
    cc.append(dimsum)


    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    xtor.make_TDLRuntimeOptionMenu()
    # xtor.display('final', full=False)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent):
    """Execute the forest with the specified options (domain etc),
    starting at the named node"""
    return xtor.execute(mqs, parent, start='result')
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the Executor object"""
    xtor.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Executor object"""
    xtor.display('_tdl_job', full=True)
       


       










#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()


    if 1:
        xtor = Executor()
        xtor.display('initial')

    if 1:
        xtor.make_TDLRuntimeOptionMenu()

    if 0:
        xtor.domain(trace=True)
        # xtor.cells(trace=True)
        # xtor.request(trace=True)

    if 1:
        xtor.display('final')



#===============================================================


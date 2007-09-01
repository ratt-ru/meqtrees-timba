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

# import Meow

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
        self.mode = None
        self._modes = []
        self.define_options()
        
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
        print prefix,'  *  available modes: '+str(self._modes)
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
    
    #===================================================================

    def define_options(self):
        """Define the various compile-time options in its OptionManager object"""

        submenu = 'compile.'
        opt = ['constant','MeqGrids']
        self._OM.define(submenu+'mode', 'MeqGrids',
                        opt=opt,
                        prompt='Twig mode',
                        callback=self._callback_mode,
                        doc = """There are various kinds (modes) of twigs.""")

        # Submenus for the various twig modes:
        self.define_mode_constant()
        self.define_mode_MeqGrids()


        # Optional operations on the end result:
        opt = ['Sqr','Sin','Cos','Exp','Abs','Negate','Pow3']    # safe always
        opt.extend(['Sqrt','Log','Invert'])                      # problems <=0
        self._OM.define(submenu+'unop', None,
                        prompt='apply unary()', opt=opt,
                        doc='apply unary operation')
        
        self._OM.define(submenu+'stddev', None,
                        prompt='add stddev noise',
                        opt=[0.1,1.0], more=float,
                        doc='add gaussian noise (if stddev>0)')

        self._OM.define(submenu+'bookpage', 'twig',
                        opt=[None], more=str,
                        prompt='meqbrowser bookpage',
                        doc = """If specified, the leaf nodes generated with the
                        twig functions .leafnode() will be
                        be bookmarked on the same bookpage.""")

        return True

    #---------------------------------------------------------------------------

    def _callback_mode (self, mode):
        """Called whenever the twig mode changes."""

        print '\n** ._callback_mode(',mode,'):',self._modes

        # First hide/inactivate all mode submenus:
        self._mode = None
        for key in self._modes:
            self._OM.hide('compile.'+key)

        if mode in self._modes:
            self._OM.show('compile.'+mode)
            self._mode = mode

        menu = self._OM.TDLMenu('compile')
        if menu:
            menu.set_summary('(mode='+str(self._mode)+')')

        return True
        

    #--------------------------------------------------------------------

    def define_mode_constant(self):
        """Define the options for a twig mode"""
        mode = 'constant'
        submenu = 'compile.'+mode+'.'
        self._OM.define(submenu+'value', 0.0,
                        prompt='constant value',
                        opt=[0.0,1.0,-1.0,(1+0j)], more=float,
                        doc='set all domain cells to a constant value')
        self._modes.append(mode)
        return True


    #--------------------------------------------------------------------

    def define_mode_MeqGrids(self):
        """Define the options for a twig mode"""
        mode = 'MeqGrids'
        submenu = 'compile.'+mode+'.'
        self._OM.define(submenu+'combine', 'Add',
                        prompt='combine with',
                        opt=['Multiply','Composer'],
                        # more=str,
                        doc='the MeqGrid nodes are combined to a single root node')
        self._modes.append(mode)
        return True


    #====================================================================
    # Functions to be used in _define_forest()
    #====================================================================
    

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
        dd = self._xtor.leafnodes(ns, trace=trace, return_list=True,
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

    dimsum = twig.leafnode(ns, 'Add')
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


# file: ../twigs/Plugin.py

# History:
# - 06sep2007: creation (from Twig.py)

# Description:

"""The Plugin class makes makes a subtree that takes an input node and
produces a new rootnode. It includes TDLOptions.
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

# import Meow                     # for Meow.Parm

from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN.Grunt import display

# from copy import deepcopy
import math

#======================================================================================

class Plugin (object):
    """The Grunt Plugin class allows the user to specify and generate
    a MeqTree twig, i.e. a small subtree that ends in child-less nodes
    (MeqLeaves)."""

    def __init__(self, name='Plugin',
                 quals=None, kwquals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        # Variables consistent with Meow.Parameterization:
        self.name = name            # the Plugin type-name (qualified below!)
        self.ns = None              # see .on_input()
        self.ns0 = None             # see .on_input()

        # For reporting only:
        self._frameclass = 'Grunt.'+self.name

        # Qualifiers allow the same Plugin to be used multiple
        # times in the same tree. They allow the generation of
        # nodes (and option entries!) with different names.
        self._quals = quals
        if self._quals==None:
            self._quals = []
        elif isinstance(self._quals, str):
            self._quals = [self._quals]
        elif not isinstance(self._quals, list):
            self._quals = []

        # Keyword qualifiers are not supported for the moment...
        self._kwquals = kwquals
        if not isinstance(self._kwquals, dict):
            self._kwquals = dict()

        # Append the qualifiers to self.name:
        for qual in self._quals:
             self.name += '_'+str(qual)

        # The OptionManager (sub)menu to be used:
        self._submenu = submenu+'.'+self.name

        #................................................................

        # The OptionManager may be external:
        if isinstance(OM, OptionManager.OptionManager):
            self._OM = OM                          
            self._external_OM = True
        else:
            self._external_OM = False
            self._OM = OptionManager.OptionManager(self.name, namespace=namespace,
                                                   parentclass=self._frameclass)

        # Define the required runtime options:
        self.define_compile_options()

        # Keep the input node for bookmarks/visualization
        self._input_node = None
        
        # Keep track of the data type and format
        # self._data = dict(complex=False, tensor=False, nelem=1, dims=1)

        # Finished:
        return None


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = self._frameclass+':'
        # ss += ' submenu='+str(self.name)
        ss += ' submenu='+str(self._submenu)
        return ss


    def display(self, txt=None, full=False, recurse=3,
                OM=True, xtor=True, level=0):
        """Print a summary of this object"""
        prefix = '  '+(level*'  ')+'Plugin'
        if level==0: print
        print prefix,' '
        print prefix,'** '+self.oneliner()
        if txt: print prefix,'  * (txt='+str(txt)+')'
        # print prefix,'  * '
        #...............................................................
        print prefix,'  * '+self._OM.oneliner()
        print prefix,'  * external OM: '+str(self._external_OM)
        if not self._external_OM:
            if OM and full: self._OM.display(full=False, level=level+1)
        #...............................................................
        print prefix,'**'
        if level==0: print
        return True




    #===================================================================
    # Generic functions dealing with options:
    #====================================================================

    def on_entry(self, trace=False):
        """Function that should be called at the start of the 
        .define_compile_options() function in a derived class.
        It does some common things.
        """
        s = '** '+self._submenu+': on_entry(): '

        # Progress message: 
        if trace:
            print '\n',s

        # NB: The calling routine aborts if return=False
        return True

    #--------------------------------------------------------------------

    def on_exit(self, trace=False):
        """Function that should be called at the end of the 
        .define_compile_options() function in a derived class.
        It does some common things.
        """
        s = '** '+self._submenu+': on_exit(): '

        # Optionally, change the (automatic) prompt in the menu
        self._OM.set_menu_prompt(self._submenu, '- plugin: '+str(self.name))

        # Progress message: 
        if trace:
            print s,'\n'

        # Make a (sub)submenu of visualization options:
        self.define_visu_options()
        
        return True


    #--------------------------------------------------------------------
    # Helper functions for access to options:
    #--------------------------------------------------------------------

    def optname (self, name, trace=False):
        """Convert an option name to its OM name by prepending self._submenu.
        """ 
        OM_name = self._submenu+'.'+name
        if trace:
            print '** optname(',name,'): -> ',OM_name
        return OM_name

    #.............................................................

    def optval (self, name, trace=True):
        """Get the value of the specified option,
        after converting it to its OM name.
        """
        OM_name = self.optname(name, trace=trace)
        value = self._OM[OM_name]
        if trace:
            print '** optval(',name,'): -> ',OM_name,'=',value
        return value

    #.............................................................

    def has_option (self, name):
        """Check the existence of the specified option.
        after converting it to its OM name.
        """
        OM_name = self.optname(name)
        return self._OM.has_option(OM_name)
        
    #---------------------------------------------------------------------
    #---------------------------------------------------------------------

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the actual TDL menu of compile-time options.
        NB: This is not needed with an external OptionManager.
        """
        if not self._external_OM:
            self._OM.make_TDLCompileOptionMenu(**kwargs)
        return True
    



    #====================================================================
    # Generic functions dealing with subtree generation:
    #====================================================================

    def on_input (self, ns, node, trace=True):
        """Function that should be called at the start of the 
        .make_subtree() function in a derived class.
        It does checks and some common things.
        """
        s = '** '+self._submenu+': on_input('+str(type(ns))+','+str(node)+'): '

        result = True

        # Check the input node:
        self._input_node = None
        if not is_node(node):
            s += 'not a node, but: '+str(type(node))
            result = False                          
        self._input_node = node

        # Check the nodescope, and make the self.ns/ns0 that will be used.
        self.ns0 = ns
        if is_node(ns):
            self.ns = ns.QualScope(self._quals)        
            self.ns0 = ns.QualScope() 
        else:
            self.ns = ns.Subscope(self.name)

        # Progress message: 
        if trace:
            print '\n',s
            print '    self.ns =',str(type(self.ns))
            print '    ',str(self.ns('dummy'))

        # NB: The calling routine aborts if return=False
        return result


    #--------------------------------------------------------------------

    def on_output (self, node, severe=True,
                   internodes=None, trace=True):
        """Function that should be called at the start of the .make_subtree()
        function in a derived class. It does checks and some common things.
        - If severe==True, an error is produced if the node is not valid.
        - The list 'internodes' contains intermediate nodes whose results
        are worth visualizing, as specified by the options.
        """
        s = '\n** '+self._submenu+': on_output('+str(node)+'): '

        # Check the result node of this Plugin:
        if not is_node(node):
            s += 'not a valid node'
            print s,'\n'
            if severe:
                raise ValueError,s
            return False

        # Visualize, as specified by the options:
        node = self.visualize (node, internodes=internodes, trace=trace)

        # Progress message:
        if trace:
            # display.subtree(node) 
            print s,'->',str(node),'\n'
        return node          


    #====================================================================
    # Generic Plugin visualization:
    #====================================================================


    def define_visu_options(self):
        """Define a generic submenu of visualization option(s).
        """
        self._OM.define(self.optname('visu.bookpage'), self.name,
                        prompt='bookpage',
                        opt=[None,self.name], more=str, 
                        doc="""Specify a bookpage for the various bookmarks
                        generated for this Plugin. If bookpage==None,
                        visualization for this Plugin is inhibited.
                        """)
        self._OM.define(self.optname('visu.compare'), 'Subtract',
                        prompt='result vs input',
                        opt=[None,'Subtract','Divide'], more=str, 
                        doc="""Insert and bookmark a side-branch that
                        compares the result with the input. 
                        """)
        self._OM.set_menu_prompt(self._submenu+'.visu', 'visualization')
        return True


    #---------------------------------------------------------------------

    def visualize (self, node, internodes=None, trace=False):
        """Execute the visualization instructions (see .define_visu_options())
        """
        if not self.has_option('visu.bookpage'):
            return node                                 # no visualization options defined
        page = self.optval('visu.bookpage')
        if not page:
            return node                                 # no visualization required
        folder = None

        # Collect a list of nodes to be bookmarked:
        bm = internodes                                 # intermediate results, if any
        if not isinstance(bm,list):
            bm = []
        bm.append(node)                                 # the Plugin result node

        # If required, insert a side-branch to compare result with input:  
        binop = self.optval('visu.compare')
        if binop:
            comp = self.ns['compare'] << getattr(Meq, binop)(node, self._input_node)
            bm.append(comp)
            node = self.ns['reqseq'] << Meq.ReqSeq(node, comp, result_index=0)

        # Make the bookmark(s):
        bm.insert(0,self._input_node)
        print '\n** bm:',page,folder
        for bm1 in bm:
            print '-',str(bm1)
        print 
        JEN_bookmarks.create(bm, page=page, folder=folder)

        # Return the (possibly new) root-node of the Plugin:
        return node






    #====================================================================
    #====================================================================
    # Specific functions (to be re-implemented by a derived class).
    # The following are placeholders that can serve as examples.
    # See also the derived class PluginTest below.
    #====================================================================
    #====================================================================


    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This placeholder function should be reimplemented by a derived class.
        """
        if not self.on_entry (trace=trace):
            return node
        #............................................
        # The specific body
        #............................................
        return self.on_exit(trace=trace)
    

    #--------------------------------------------------------------------

    def make_subtree (self, ns, node, trace=False):
        """Specific: Make the plugin subtree.
        This placeholder function should be reimplemented by a derived class.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return node
        #............................................
        # The specific body
        #............................................
        return self.on_output (node, trace=trace)









#=============================================================================
#=============================================================================
#=============================================================================
#=============================================================================

class PluginTest(Plugin):
    """Class derived from Plugin"""

    def __init__(self,
                 quals=None, kwquals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Plugin.__init__(self, name='PluginTest',
                        quals=quals, kwquals=kwquals,
                        submenu=submenu,
                        OM=OM, namespace=namespace,
                        **kwargs)
        return None

    
    #====================================================================

    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        This placeholder function should be reimplemented by a derived class.
        """
        if not self.on_entry (trace=trace):
            return node
        #..............................................
        self._OM.define(self.optname('unop'), 'Cos',
                        prompt='unary',
                        opt=['Sin','Cos'], more=str,
                        doc="""apply an unary operation.
                        """)
        #..............................................
        return self.on_exit(trace=trace)

    #--------------------------------------------------------------------

    def make_subtree (self, ns, node, trace=True):
        """Specific: Make the plugin subtree.
        This placeholder function should be reimplemented by a derived class.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return node
        #..............................................

        # Read the specified options:
        unop = self.optval('unop')
        if not unop:
            return node                           # do nothing

        # Make the subtree:
        node = self.ns['result'] << getattr(Meq,unop)(node)

        #..............................................
        # Check the new rootnode:
        return self.on_output (node, trace=trace)



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


pgt = None
if 0:
    xtor = Executor.Executor('Executor', namespace='test',
                             parentclass='test')
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('long', unit='rad')
    # xtor.add_dimension('s', unit='rad')
    xtor.make_TDLCompileOptionMenu()

    pgt = PluginTest(quals='hjk')
    pgt.make_TDLCompileOptionMenu()
    # pgt.display()


def _define_forest(ns):

    global pgt,xtor
    if not pgt:
        xtor = Executor.Executor()
        xtor.make_TDLCompileOptionMenu()
        pgt = PluginTest(quals=[1,2])
        pgt.make_TDLCompileOptionMenu()

    cc = []

    node = xtor.leafnode(ns)
    rootnode = pgt.make_subtree(ns, node)
    cc.append(rootnode)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    xtor.make_TDLRuntimeOptionMenu(node=ns.result)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent):
    """Execute the forest with the specified options (domain etc),
    starting at the named node"""
    return xtor.execute(mqs, parent)
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the Plugin object"""
    pgt.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Plugin object"""
    pgt.display('_tdl_job', full=True)
       


       










#===============================================================
# Test routine:
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    OM = None
    if 0:
        OM = OptionManager.OptionManager()

    if 1:
        pgt = PluginTest(OM=OM, quals='yui' )
        pgt.display('initial')

    if 0:
        pgt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        pgt.make_subtree(ns, node, trace=True)

    if 1:
        pgt.display('final', OM=True, full=True)



#===============================================================


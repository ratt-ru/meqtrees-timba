# file: ../twigs/Twig.py

# History:
# - 01sep2007: creation (from Executor.py)
# - 05sep2007: polished the user interface

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

# from Timba.Contrib.JEN.twigs import Plugin

# from copy import deepcopy
import math

#======================================================================================

class Twig (object):
    """The Grunt Twig class allows the user to specify and generate
    a MeqTree twig, i.e. a small subtree that ends in child-less nodes
    (MeqLeaves)."""

    def __init__(self, name='Twig',
                 namespace=None):

        self.name = name
        self._frameclass = 'Grunt.Twig'       # for reporting

        self._OM = OptionManager.OptionManager(self.name, namespace=namespace,
                                               parentclass=self._frameclass)
        self._xtor = Executor.Executor('Executor', namespace=namespace,
                                       parentclass=self._frameclass)

        # Define the compile_time options:
        self._twip = dict()
        self._modify = dict()
        self._demo = dict()
        
        self._plugin_order = []
        self._plugin = dict()

        self.define_compile_options()


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
        ss += '  twig_tip='+str(self._OM['twig_tip'])
        ss += '  user_level='+str(self._OM['user_level'])
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
        print prefix,'  *  user_levels: '+str(self._user_levels)
        print prefix,'  *  available plugins:'
        for key in self._plugin_order:
            rr = self._plugin[key]
            print prefix,'    - '+key+': '+str(rr['plugin'].oneliner())
        #...............................................................
        print prefix,'  *  available twig_tip types:'
        for key in self._twip.keys():
            print prefix,'    - '+key+': '+str(self._twip[key])
        print prefix,'  *  available twig modify options:'
        for key in self._modify.keys():
            print prefix,'    - '+key+': '+str(self._modify[key])
        print prefix,'  *  available demo options:'
        for key in self._demo.keys():
            print prefix,'    - '+key+': '+str(self._demo[key])
        print prefix,'  *  data: '+str(self._data)
        #...............................................................
        print prefix,'  * '+self._OM.oneliner()
        if OM and full: self._OM.display(full=False, level=level+1)
        #...............................................................
        print prefix,'  * '+self._xtor.oneliner()
        if xtor and full: self._xtor.display(full=False, level=level+1)
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

    def define_compile_options(self):
        """Define the various compile-time options in its OptionManager object"""
        submenu = 'compile.'

        opt = ['MeqConstant','MeqParm','MeqGrids']
        # opt.extend(['PointSource22'])
        self._OM.define(submenu+'twig_tip', 'MeqConstant',
                        opt=opt,
                        prompt='select a twig tip',
                        callback=self._callback_twip,
                        doc = """A twig-tip is a node/subtree at the
                        tip of a twig. There are various kinds:
                        - MeqConstant: a MeqConstant node (may be a tensor)
                        - MeqParm: a MeqParm node
                        - MeqGrids: a hypercube of Meq.Grid nodes for the
                          selected (in xtor) compile-time dimensions.
                        """)

        # Submenus for the various twig_tips (twips):
        self.submenu_twig_tip_MeqConstant()
        self.submenu_twig_tip_MeqParm()
        self.submenu_twig_tip_MeqGrids()
        for key in self._twip.keys():
            self._OM.set_menu_prompt ('compile.'+key, 'customize the twig-tip: '+key)

        # Plugins for optional operations on the twig_tip:
        self.add_plugin('PluginMakeTensor', submenu='compile.modify',
                        user_level=0, hide=[])     
        self.add_plugin('PluginAddNoise', submenu='compile.modify',
                        user_level=0, hide=[])   
        self.add_plugin('PluginApplyUnary', submenu='compile.modify',
                        user_level=0, hide=[])          # AFTER add_noise()
        self.add_plugin('PluginFlagger', submenu='compile.modify',
                        user_level=0, hide=[])    

        # Testing Plugins:
        if False:
            self.add_plugin('PluginTemplate', submenu='compile.modify',
                            user_level=0, hide=[])
            if True:
                self.add_plugin('PluginTest', submenu='compile.modify', quals='1st',
                                user_level=0, hide=[])
            if True:
                self.add_plugin('PluginTest', submenu='compile.modify', quals='2nd',
                                user_level=0, hide=[])

        # Plugins for demonstration subtrees:
        self.add_plugin('PluginDemoRedaxes', submenu='compile.demo',
                        user_level=0, hide=[])      
        self.add_plugin('PluginDemoSolver', submenu='compile.demo',
                        user_level=0, hide=[])    
        self.add_plugin('PluginDemoModRes', submenu='compile.demo',
                        user_level=0, hide=[])   

        self._OM.set_menu_prompt ('compile.modify', 'modify the twig result')
        self._OM.set_menu_prompt ('compile.demo', 'select demoes')

        self._define_misc_compile_options()

        # Select an inital twig_tip:
        self._callback_twip('MeqGrids')
        return True

    #...................................................................

    def _callback_twip (self, twip):
        """Called whenever the twig_tip changes."""

        user_level = self._numeric_user_level()
        # print '\n** ._callback_twip(',twip,'): user_level =',user_level

        # First hide/inactivate submenus...
        for key in self._twip.keys():
            self._OM.hide('compile.'+key)
        if self._OM['show_modif']:
            self._OM.hide('compile.modify')
        if self._OM['show_demoes']:
            self._OM.hide('compile.demo')
        
        # ... and all the modify/demo options:
        for key in self._modify.keys():
            self._OM.hide('compile.modify.'+key)
        for key in self._demo.keys():
            self._OM.hide('compile.demo.'+key)

        # Then unhide the selected relevant menus/options:
        if twip in self._twip.keys():
            if user_level>=self._twip[twip]['user_level']: 
                self._OM.show('compile.'+twip)          

                if self._OM['show_modif']:
                    self._OM.show('compile.modify')
                    for key in self._modify.keys():
                        if user_level>=self._modify[key]['user_level']:
                            self._OM.show('compile.modify.'+key)
                    for key in self._twip[twip]['hide']:     
                        self._OM.hide('compile.modify.'+key)

                if self._OM['show_demoes']:
                    self._OM.show('compile.demo')
                    for key in self._demo.keys():
                        if user_level>=self._demo[key]['user_level']:
                            self._OM.show('compile.demo.'+key)
                    for key in self._twip[twip]['hide']:     
                        self._OM.hide('compile.demo.'+key)
        else:
            twip = '??'

        # Indicate the selected twig_tip in the top menu:
        menu = self._OM.TDLMenu('compile')
        if menu:
            menu.set_summary('(twig_tip='+str(twip)+')')
        return True

    
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    def add_plugin(self, name, submenu='compile.modify', quals=[],
                   user_level=0, hide=[]):
        """Create the specified Plugin object, and add it to self._plugin.
        """
        plugin = None
        if name=='PluginTest':
            from Timba.Contrib.JEN.twigs import Plugin
            plugin = Plugin.PluginTest(submenu=submenu, OM=self._OM,
                                       quals=quals)
        elif name=='PluginTemplate':
            from Timba.Contrib.JEN.twigs import PluginTemplate
            plugin = PluginTemplate.PluginTemplate(submenu=submenu, OM=self._OM,
                                                   quals=quals)
        elif name=='PluginApplyUnary':
            from Timba.Contrib.JEN.twigs import PluginApplyUnary
            plugin = PluginApplyUnary.PluginApplyUnary(submenu=submenu, OM=self._OM,
                                                       quals=quals)
        elif name=='PluginFlagger':
            from Timba.Contrib.JEN.twigs import PluginFlagger
            plugin = PluginFlagger.PluginFlagger(submenu=submenu, OM=self._OM,
                                                 quals=quals)
        elif name=='PluginAddNoise':
            from Timba.Contrib.JEN.twigs import PluginAddNoise
            plugin = PluginAddNoise.PluginAddNoise(submenu=submenu, OM=self._OM,
                                                   quals=quals)
        elif name=='PluginMakeTensor':
            from Timba.Contrib.JEN.twigs import PluginMakeTensor
            plugin = PluginMakeTensor.PluginMakeTensor(submenu=submenu, OM=self._OM,
                                                       quals=quals)

        elif name=='PluginDemoSolver':
            from Timba.Contrib.JEN.twigs import PluginDemoSolver
            plugin = PluginDemoSolver.PluginDemoSolver(submenu=submenu, OM=self._OM,
                                                       quals=quals)
        elif name=='PluginDemoModRes':
            from Timba.Contrib.JEN.twigs import PluginDemoModRes
            plugin = PluginDemoModRes.PluginDemoModRes(submenu=submenu, OM=self._OM,
                                                       quals=quals)
        elif name=='PluginDemoRedaxes':
            from Timba.Contrib.JEN.twigs import PluginDemoRedaxes
            plugin = PluginDemoRedaxes.PluginDemoRedaxes(submenu=submenu, OM=self._OM,
                                             quals=quals)

        else:
            s = 'plugin not recognised: '+name
            raise ValueError,s

        if isinstance(quals,str):
            quals = [quals]
        for qual in quals:
            name += '_'+qual
        self._plugin[name] = dict(plugin=plugin,
                                  user_level=user_level, hide=hide) 
        self._plugin_order.append(name)
        return True

    #---------------------------------------------------------------------------

    def insert_plugin_chain (self, ns, node=None, trace=True):
        """Make a chain of subtrees from the entries in self._plugin
        """
        trace = True
        user_level = self._numeric_user_level()
        # if user_level<self._twip[twip]['user_level']:
        #     s = '** user-level='+str(user_level)
        #     s += ' ('+str(self._OM['user_level'])+')'
        #     s += ': too low for twig_tip: '+twip
        #     raise ValueError,s
        if trace:
            print '\n** .insert_plugin_chain(',str(node),'):'

        for key in self._plugin_order:
            rr = self._plugin[key]
            print '\n -',key,':',rr['plugin'].oneliner()
            # if rr['user_level']<user_level:
            node = rr['plugin'].make_subtree(ns, node, trace=trace)
            print '    -> node =',str(node)

        if trace:
            print
        return node


    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    def _define_misc_compile_options(self):
        """Define miscellaneous compile-time options in its OptionManager object"""
        submenu = 'compile.misc'

        self._user_levels = ['greenhorn','harmless','member','advanced','expert','smirnoff']
        opt = self._user_levels
        self._OM.define(submenu+'.user_level', opt[4],
                        opt=opt,
                        prompt='user_level',
                        callback=self._callback_user_level,
                        doc = """The Twig module can be used at various user_levels.
                        The higher levels offer more options, which will only
                        confuse those who are not ready for them.
                        """)
        self._OM.define(submenu+'.show_modif', True,
                        opt=[True, False],
                        prompt='offer modification options',
                        callback=self._callback_show_modif,
                        doc = """If True, show the modification optionsthat
                        are available at the current user_level.
                        """)
        self._OM.define(submenu+'.show_demoes', True,
                        opt=[True, False],
                        prompt='offer demoes',
                        callback=self._callback_show_demoes,
                        doc = """If True, show the demoes that are available
                        at the current user_level.
                        """)

        self.submenu_visualize_twig()
        self.submenu_twig_bookmark()
        self._OM.set_menu_prompt (submenu, 'misc. settings')
        return True
    
    #...................................................................

    def _callback_show_modif (self, show_modif):
        """Called whenever the show_modif switch changes."""
        return self._OM.show('compile.modify', show_modif)

    #...................................................................

    def _callback_show_demoes (self, show_demoes):
        """Called whenever the show_demoes switch changes."""
        return self._OM.show('compile.demo', show_demoes)

    #...................................................................

    def _callback_user_level (self, user_level):
        """Called whenever the user_level changes."""
        return self._callback_twip (self._OM['twig_tip'])

    #...................................................................

    def _numeric_user_level (self):
        user_level = self._OM['misc.user_level']
        if user_level in self._user_levels:
            return self._user_levels.index(user_level)
        return 4


    #====================================================================
    #====================================================================
    # Functions for twips:
    #====================================================================
    #====================================================================

    def submenu_twig_tip_MeqConstant(self):
        """Define the options for a MeqConstant twig_tip"""
        name = 'MeqConstant'
        submenu = 'compile.'+name+'.'
        self._OM.define(submenu+'value', 0.0,
                        prompt='value',
                        opt=[0.0,1.0,-1.0,(1+0j)], more=float,
                        doc="""set all domain cells to a constant value
                        """)
        self._twip[name] = dict(user_level=0, hide=['solver'])
        return True

    #--------------------------------------------------------------------

    def make_twig_tip_MeqConstant (self, ns, trace=False):
        """Create a MeqConstant node"""
        submenu = 'compile.'+self._OM['twig_tip']+'.'
        value = self._OM[submenu+'value']
        self._data['complex'] = isinstance(value,complex)  # used downstream
        name = str(value)
        node = ns[name] << Meq.Constant(value)
        return self._check_node (node, submenu)


    #====================================================================
    #====================================================================

    def submenu_twig_tip_MeqParm(self):
        """Define the options for a MeqParm twig_tip"""
        name = 'MeqParm'
        submenu = 'compile.'+name+'.'
        self._OM.define(submenu+'default', 0.0,
                        prompt='default value',
                        opt=[0.0,1.0,-1.0], more=float,
                        doc="""the default value of the MeqParm
                        """)
        self._OM.define(submenu+'freq_deg', 2,
                        prompt='freq polc',
                        opt=[0,1,2,3,4,5], more=int,
                        doc="""Degree (order) of the freq polynonial that is
                        to be solved for (constant in freq: freq_deg=0).
                        """)
        self._OM.define(submenu+'time_deg', 2,
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
        self._OM.define(submenu+'tags', ['solvable'],
                        prompt='MeqParm tag(s)',
                        opt=[[],['solvable']],      # more=str,
                        doc="""Node tags can be used to search for (groups of)
                        nodes in the nodescope.
                        """)
        self._twip[name] = dict(user_level=2, hide=['make_tensor'])
        return True

    #--------------------------------------------------------------------

    def make_twig_tip_MeqParm (self, ns, trace=False):
        """Create a MeqParm node, using a Meow.Parm definition"""
        submenu = 'compile.'+self._OM['twig_tip']+'.'
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

    def submenu_twig_tip_MeqGrids(self):
        """Define the options for a MeqGrids twig-tip"""
        name = 'MeqGrids'
        submenu = 'compile.'+name+'.'
        self._OM.define(submenu+'combine', 'Add',
                        prompt='combine with',
                        opt=['Add','Multiply','Composer'],
                        doc="""the MeqGrid nodes of the various dimensions
                        must be combined to a single root node
                        """)
        self._twip[name] = dict(user_level=1, hide=['solver'])
        return True

    #--------------------------------------------------------------------

    def make_twig_tip_MeqGrids (self, ns, trace=False):
        """Create a MeqGrids twig-tip"""
        submenu = 'compile.'+self._OM['twig_tip']+'.'
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


    def _proceed_with_modify (self, ns, node, name, trace=True):
        """Helper function to decide whether to proceed with 'modify' function"""
        s = '\n** _proceed_with_(modify/demo)('+str(name)+','+str(node)+'): '
        twip = self._OM['twig_tip']
        if not is_node(node):
            s += 'not a valid node'
        elif name in self._twip[twip]['hide']:
            s += 'not relevant for twip: '+self._OM['twig_tip']
        else:
            return True                 # OK
        # Problem: deal with it:
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
    # Finishing touches on the twig result:
    #====================================================================
    #====================================================================

    def submenu_visualize_twig(self):
        """Define the options for an operation on the twig result"""
        name = 'visualize_twig'
        submenu = 'compile.misc.'+name
        self._OM.define(submenu+'.plot_type', None,
                        prompt='make a special plot',
                        opt=[None,'rvsi','time_tracks'], 
                        doc="""Special visualization
                        """)
        self._modify[name] = dict(user_level=0)
        self._OM.set_menu_prompt(submenu, 'visualize the twig rootnode')
        return True

    #--------------------------------------------------------------------

    def visualize_twig (self, ns, node, trace=False):
        """Optionally, visualize the given node"""
        name = 'visualize_twig'
        if not self._proceed_with_modify (ns, node, name): return node
        submenu = 'compile.misc.'+name
        plot = self._OM[submenu+'.plot_type']
        return self._check_node (node, submenu)
        return node



    #====================================================================
    #====================================================================

    def submenu_twig_bookmark(self):
        """Define the options for an operation on the twig result"""
        name = 'twig_bookmark'
        submenu = 'compile.misc.'+name
        self._OM.define(submenu+'.bookpage', 'twig',
                        opt=[None], more=str,
                        prompt='meqbrowser bookpage',
                        doc = """If specified, the leaf nodes generated with the
                        twig functions .leafnode() will be
                        be bookmarked on the same bookpage.
                        """)
        self._OM.define(submenu+'.folder', None,
                        opt=[None], more=str,
                        prompt='bookpage folder',
                        doc = """All bookpages may be put into a folder
                        """)
        self._OM.set_menu_prompt(submenu, 'bookmark the twig rootnode')
        return True

    #--------------------------------------------------------------------

    def _folder (self):
        """Helper function to get the Twig bookmark folder"""
        return self._OM['compile.misc.twig_bookmark.folder']
        
    #--------------------------------------------------------------------

    def twig_bookmark (self, ns, node, trace=False):
        """Optionally, bookmark the given node"""
        name = 'twig_bookmark'
        submenu = 'compile.misc.'+name+'.'
        bookpage = self._OM[submenu+'bookpage']
        if node and bookpage:
            JEN_bookmarks.create(node, page=bookpage, folder=self._folder())
        return self._check_node (node, submenu)




    #====================================================================
    #====================================================================
    # Make the actual twig subtree:
    #====================================================================
    #====================================================================
    

    def make_twig (self, ns, qual=None, trace=True):
        """Make the actual twig subtree, according to specifications."""
        if trace:
            print '\n** .make_twig(',qual,'):'

        # Work on a subscope....?
        if qual:
            ns = ns.Subscope('twig')(qual)
        else:
            ns = ns.Subscope('twig')

        # Make the twig subtree for the specified twip:
        node = None
        twip = self._OM['twig_tip']
        user_level = self._numeric_user_level()
        if user_level<self._twip[twip]['user_level']:
            s = '** user-level='+str(user_level)
            s += ' ('+str(self._OM['user_level'])+')'
            s += ': too low for twig_tip: '+twip
            raise ValueError,s
        elif twip=='MeqConstant':
            node = self.make_twig_tip_MeqConstant(ns, trace=trace)
        elif twip=='MeqParm':
            node = self.make_twig_tip_MeqParm(ns, trace=trace)
        elif twip=='MeqGrids':
            node = self.make_twig_tip_MeqGrids(ns, trace=trace)

        # Insert the Plugins:
        node = self.insert_plugin_chain (ns, node, trace=True)

        # Finsishing touches:
        node = self.visualize_twig (ns, node, trace=trace)
        node = self.twig_bookmark (ns, node, trace=trace)

        # Finished:
        node = self._check_node (node, '.make_twig()')
        if trace:
            display.subtree(node)
        return node



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================

twig = None
if 1:
    twig = Twig('twiggy')
    # twig._xtor.add_dimension('l', unit='rad')
    # twig._xtor.add_dimension('m', unit='rad')
    # twig._xtor.add_dimension('long', unit='rad')
    # twig._xtor.add_dimension('s', unit='rad')
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
    twig.make_TDLRuntimeOptionMenu(node=ns.result)
    # twig.display('final', full=False)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent):
    """Execute the forest with the specified options (domain etc),
    starting at the named node"""
    return twig._xtor.execute(mqs, parent)
    
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


# file: ../JEN/Grow/Growth.py

# History:
# - 14sep2007: creation (from Plugin.py)

# Description:

"""The Growth class is the base-class from which an entire arboretum of
derived classes for 'growing' subtree onto a given tree, by making the
root node(s) of the given tree the child(ren) of one or more new
layers of rootnode(s). 
The Growyh baselclass conveniently takes care of TDLOption manipulation,
input and output checking, visualization etc.
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

from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN.Grunt import display

# from copy import deepcopy

#======================================================================================

class Growth (object):
    """The Grunt Growth class allows the user to specify and generate
    a MeqTree twig, i.e. a small subtree that ends in child-less nodes
    (MeqLeaves)."""

    def __init__(self, quals=None,
                 name='Growth',
                 submenu='compile',
                 OM=None, namespace=None,
                 has_input=True,
                 toggle=False,
                 ignore=False,                    
                 defer_compile_options=False,
                 **kwargs):

        # For reporting only:
        self._frameclass = 'Growth.'+name

        # Variables consistent with Meow.Parameterization:
        self.ns = None                              # see .on_input()
        self.ns0 = None                             # see .on_input()
        self.make_name_and_submenu (name, submenu, quals)

        # Keep an internal list of nodes to be bookmarked
        # See .bookmark() and .visualize_generic()
        self._bm = []

        # Keep the input node for bookmarks/visualization
        self._input = None
        self._has_input = has_input

        # If toggle=True, provide a toggle widget to its subenu
        self._toggle = toggle

        # The object may be ignored/hidden:
        self._ignore = ignore
        self._visualize = True

        #................................................................

        # The OptionManager may be external:
        if isinstance(OM, OptionManager.OptionManager):
            self._OM = OM                          
            self._external_OM = True
        else:
            self._external_OM = False
            self._OM = OptionManager.OptionManager(self.name, namespace=namespace,
                                                   parentclass=self._frameclass)

        # Initialize a control dict for keeping track of the (result) data type
        # and format. It may be used by Growths to do the correct thing.
        # This dict should be updated when the data type or format changes,
        # using self.datadesc(). It should be passed down a chain of Growths.
        self._datadesc = dict(is_complex=False, nelem=1, dims=[1])

        # Optionally, the plugin options may be preset to the values
        # belonging to a number of standard modes. See .preset_to_mode().
        self._mode = dict()

        # Define the required runtime options:
        if not defer_compile_options:
            self.define_compile_options()
        
        # Finished:
        return None


    #--------------------------------------------------------------------

    def make_name_and_submenu (self, name=None, submenu=None, quals=None):
        """
        Helper function that is called from __init__().
        Make self.name by appending any qualifiers to name.
        Make self._submenu by appending self.name to submenu.
        """
        # The use of self.name is consistent with Meow/Parameterization...
        self.name = name
        
        # Qualifiers allow the same Growth to be used multiple
        # times in the same tree. They allow the generation of
        # nodes (and option entries!) with different names.
        self._quals = quals
        if self._quals==None:
            self._quals = []
        elif isinstance(self._quals, str):
            self._quals = [self._quals]
        elif not isinstance(self._quals, list):
            self._quals = []

        # Append the qualifiers to self.name:
        for qual in self._quals:
             self.name += '_'+str(qual)

        # The OptionManager (sub)menu to be used:
        self._submenu = submenu+'.'+self.name
        return True

    #--------------------------------------------------------------------

    def change_submenu(self, submenu, trace=True):
        """Not yet implemented: Change the submenu, and redefine the options.
        This is done when an existing Growth object is attached to another one.
        """
        # NB: What about the options that have already been defined?
        #     Should they be eradicated from the OM?
        # self._submenu = submenu+'.'+self.name
        # self.define_compile_options()
        # NB: What about options that are defined in other routines?
        return True

    #====================================================================

    def ignore (self, ignore=None):
        """Get/set/reset the internal switch self._ignore.
        - If ignore==None (default), just return the current value of
        the internal switch self._ignore (True/False)
        - If ignore==True, the Growth submenu will hidden, and .grow()
        will just pass on the input.
        - If ignore==False, the Growth submenu will become visible, and
        .grow() will generate new nodes.
        """
        if isinstance(ignore,bool):
            self._ignore = ignore
        self._OM.hide(self._submenu, hide=self._ignore)
        return self._ignore


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = self._frameclass+':'
        ss += ' submenu='+str(self._submenu)
        if self._ignore:
            ss += ' (ignored)'
        return ss


    def display(self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble('Growth', level=level, txt=txt)
        #...............................................................
        print prefix,'  * has_input = '+str(self._has_input)
        print prefix,'  * datadesc: '+str(self.datadesc(trace=False))
        #...............................................................
        print prefix,'  * nodes to be bookmarked (visualize='+str(self._visualize)+'):'
        for node in self._bm:
            print prefix,'     - '+str(node)
        #...............................................................
        print prefix,'  * '+self._OM.oneliner()
        print prefix,'  * external OptionManager: '+str(self._external_OM)
        if not self._external_OM:
            if OM and full: self._OM.display(full=False, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)


    #-------------------------------------------------------------------------

    def display_preamble(self, prefix='Growth', level=0, txt=None):
        """Helper function called by .display(). Also used in reimplemented
        .display() in derived classes"""
        prefix = '  '+(level*'  ')+str(prefix)
        if level==0: print
        print prefix,' '
        print prefix,'** '+self.oneliner()
        if txt: print prefix,'  * (txt='+str(txt)+')'
        return prefix


    def display_postamble(self, prefix, level=0):
        """Helper function called by .display(). Also used in reimplemented
        .display() in derived classes"""
        print prefix,'**'
        if level==0: print
        return True


    #====================================================================
    # Some service(s) available to all classes derived from Growth:
    #====================================================================

    def display_subtree(self, node, recurse=10, trace=False):
        """Display the subtree behind the given node.
        """
        print '\n** ',self.name,': display_subtree(',str(node),'):'
        display.subtree(node, recurse=recurse) 
        return True

    def print_tree(self, recurse=10, trace=False):
        """Display the entire tree
        """
        print '\n** ',self.name,': print_tree(recurse=',recurse,'):'
        self._OM.print_tree(recurse=recurse)
        print
        return True


    #========================================================================
    # Interacion with the data-description record:
    #========================================================================

    def datadesc (self, merge=None, is_complex=None, dims=None, trace=False):
        """Return the data-description record.
        If another datadesc (merge) is specified, update the local one.
        """
        rr = self._datadesc                                 # convenience
        if isinstance(merge, dict):
            if merge['is_complex']: rr['is_complex'] = True
        else:
            if isinstance(is_complex, bool):
                rr['is_complex'] = is_complex
            if dims:
                rr['dims'] = dims
        # Always update the derived quantity nelem (nr of tensor elements):
        rr['nelem'] = 1
        for nd in rr['dims']:
            rr['nelem'] *= nd
        if trace:
            print '** datadesc(',merge,is_complex,dims,'): ',str(self._datadesc)
        return self._datadesc
    

    #===================================================================
    # Generic functions dealing with (compile) options:
    #====================================================================

    def on_entry(self, trace=False):
        """Generic function that should be called at the start of the
        specific function .define_compile_options() in a derived class.
        It does some generic initializing etc.
        """
        s = '** '+self._submenu+': on_entry(): '
        self._done_on_entry = True

        # Progress message: 
        if trace:
            print '\n',s

        # NB: The calling .define_compile_options() aborts if return=False
        return True

    #--------------------------------------------------------------------

    def on_exit(self, trace=False):
        """Generic function that should be called at the end of the 
        specific function .define_compile_options() in a derived class.
        It does some generic finishing touches.
        """
        s = '** '+self._submenu+': on_exit(): '

        # Check whether things have been done in the correct order:
        if not self._done_on_entry:
            raise ValueError
        self._done_on_exit = True

        # Change the (automatic) prompt in the menu
        prompt = '- customize'
        prompt += ': '+str(self.name)
        self._OM.set_menurec(self._submenu, prompt=prompt)

        # Optional: add a toggle widget to the menu:
        if self._toggle:
            self._OM.set_menurec(self._submenu, toggle=True,
                                 callback=self._callback_toggle)

        # Progress message: 
        if trace:
            print s,'\n'

        # Make a (sub)submenu of miscellaneous options:
        self.define_generic_misc_options()
        
        return True


    #....................................................................

    def _callback_toggle (self, selected='selected'):
        """Called whenever the toggle widget before the menu is toggled"""
        menurec = self._OM.set_menurec(self._submenu, selected=selected)
        self._ignore = not selected
        ## self._OM.enable(self._submenu, selected)  NOT a good idea!!
        return True




    #====================================================================
    # Helper functions for access to options:
    #====================================================================

    def optname (self, name, trace=False):
        """Convert an option name to its OM name by prepending self._submenu.
        """ 
        OM_name = self._submenu+'.'+name
        if trace:
            print '** optname(',name,'): -> ',OM_name
        return OM_name

    #.............................................................

    def optval (self, name, test=None, trace=False):
        """Get the value of the specified option, after converting it to its OM name.
        If test is specified, modify the value, if necessary.
        """
        OM_name = self.optname(name, trace=trace)
        value = self._OM[OM_name]

        # The value may be changed for testing-purposes:
        nominal = value
        if isinstance(test, dict):
            if test.has_key(name):
                value = test[name]
                trace = True
                
        if trace:
            print '** optval(',name,'): -> ',OM_name,'=',value,
            if not value==nominal:
                print ' (nominal=',nominal,')',
            print
        return value

    #.............................................................

    def has_option (self, name):
        """Check the existence of the specified option, after converting it to its OM name.
        """
        OM_name = self.optname(name)
        return self._OM.has_option(OM_name)
        
    #.............................................................

    def setval (self, name, value):
        """Set the value of the specified option, after converting it to its OM name.
        """
        if self.has_option(name):
            OM_name = self.optname(name)
            if self._OM.option[OM_name]:
                self._OM.set_value(OM_name, value)
        return True


    #--------------------------------------------------------------------
    # TDLMenu generation:
    #--------------------------------------------------------------------

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the actual TDL menu of compile-time options.
        NB: This call is not needed with an external OptionManager,
        since the menu will be part of that of the parent object.
        """
        if not self._external_OM:
            self._OM.make_TDLCompileOptionMenu(**kwargs)
        return True
    




    #====================================================================
    # Generic functions dealing with subtree generation:
    #====================================================================

    def on_input (self, ns, input=None, severe=True,
                  trace=False):
        """Generic function that should be called at the start of the
        specific function .grow() in a derived class.
        It does various checks, and some common things.
        """
        s = '** '+self._submenu+': on_input('+str(type(ns))+','+str(input)+'): '

        # Check whether things have been done in the correct order:
        if not self._done_on_exit:
            raise ValueError
        self._done_on_input = True

        # Initialize the return value (see below)
        result = True

        # Store and check the input, and initialise the return value
        if self._has_input:
            self._input = input         # keep for later use
            result = self.check_input(self._input, severe=severe, trace=trace)

        # If the ignore switch is set, do nothing (see also .ignore())
        # NB: This should be AFTER setting self._input !!
        if self._ignore:
            result = False              # This will cause .grow() to exit
            if trace:
                print s,'ignored'

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

        # NB: The calling routine .grow() aborts if return=False
        return result


    #--------------------------------------------------------------------

    def check_input (self, input, severe=True, trace=False):
        """Specific function called by the generic function .on_input()
        to check the input to .grow().
        This default version checks whether self._input is a node.
        It should be re-implemented by derived classes whose input is
        expected to be something else (e.g. a Visset22 object, etc).
        This routine should return True (OK) or False (not OK).
        """
        if not is_node(input):
            s = 'input is not a node, but: '+str(type(input))
            if severe:
                raise ValueError,s
            else:
                return False                          
        return True

    #--------------------------------------------------------------------

    def bypass (self, trace=False):
        """Generic function that should be called by .grow() whenever it
        exits prematurely for some reason.
        """
        trace = True

        # Check whether things have been done in the correct order:
        if not self._done_on_input:
            raise ValueError
        self._done_on_output = True

        result = self._input
        if trace:
            print '** '+self._submenu+': bypass() ->',str(result)
        return result

    #--------------------------------------------------------------------

    def on_output (self, result, severe=True, trace=False):
        """Generic function that should be called at the end of the
        specific function .grow() in a derived class.
        It does checks and some generic things.
        - If severe==True, an error is produced if the result is not valid.
        """
        s = '\n** '+self._submenu+': on_output('+str(result)+'): '

        # Check whether things have been done in the correct order:
        if not self._done_on_input:
            raise ValueError
        self._done_on_output = True

        # Check the result node of this Growth:
        result = self.check_result (result, severe=severe, trace=trace)

        # Visualize, as specified by the options:
        result = self.visualize_generic (result, trace=trace)

        # Progress message:
        if trace:
            if is_node(result):
                self.display_subtree(result) 
                print s,'->',str(result),'\n'
            elif gettattr(result, oneliner,None):
                print s,'->',result.oneliner(),'\n'
            else:
                print s,'->',type(result),'\n'
        return result          


    #--------------------------------------------------------------------

    def check_result (self, result, severe=True, trace=False):
        """Specific function called by the generic function .on_result()
        to check the result of .grow().
        This default version checks whether the result is a node.
        It should be re-implemented by derived classes whose result is
        expected to be something else (e.g. a Visset22 object, etc).
        """
        if not is_node(result):
            s = 'result is not a valid node'
            print s,'\n'
            if severe:
                raise ValueError,s
            else:
                return False
        # If OK, just pass on the valid result:
        return result


    #====================================================================
    # Miscellaneous settings
    #====================================================================

    def define_generic_misc_options(self):
        """Define a generic submenu of visualization option(s).
        """
        self._OM.define(self.optname('misc.ignore'), False,
                        prompt='ignore/hide this Growth',
                        opt=[True,False,None],
                        callback=self._callback_ignore,
                        doc="""this is used for testing
                        """)
        self._OM.set_menurec(self._submenu+'.misc', prompt='miscellaneous')

        if len(self._mode.keys())>0:
            self._OM.define(self.optname('misc.mode'), None,
                            prompt='select a standard mode',
                            opt=[None]+self._mode.keys(),
                            callback=self._callback_mode,
                            doc="""The Growth option values may be preset
                            to the values of a number of standard modes.
                            """)

        # Define specific options for this menu (if any):
        self.define_misc_options()

        # Visualization options (generic and specific):
        self.define_generic_visu_options()
        
        # Finished:
        return True

    #--------------------------------------------------------------------

    def define_misc_options(self):
        """Define class-specific options for the misc menu.
        To be reimplemented by derived classes, if necessary.
        """
        return True

    #....................................................................

    def _callback_ignore (self, ignore):
        """Called whenever option 'misc.ignore' changes"""
        # print '\n** _callback_ignore(',ignore,'):',
        was = self._ignore
        value = self.ignore(ignore)
        # print '   -> ',value,' (was',was,')'
        return True

    #....................................................................

    def _callback_mode (self, mode):
        """Called whenever option 'misc.mode' changes"""
        # print '\n** _callback_mode(',mode,'):'
        if mode:
            return self.preset_to_mode(mode)

    def preset_to_mode(self, mode, trace=False):
        """Reset the option values according to the specified mode.
        Placeholder function, to be reimplemented by derived class
        """
        return True


    #====================================================================
    # Generic visualization:
    #====================================================================


    def define_generic_visu_options(self):
        """Generic function to define the generic visualization option(s).
        """
        self._OM.define(self.optname('misc.visu.bookpage'), self.name,
                        prompt='bookpage name',
                        opt=[None,self.name], more=str, 
                        doc="""Specify a bookpage for the various bookmarks
                        generated for this Growth. If bookpage==None,
                        visualization for this Growth object is inhibited.
                        """)

        # Change the default menu prompt to a more instructive one:
        self._OM.set_menurec(self._submenu+'.misc.visu',
                             prompt='visualization')

        # Add a toggle widget to the visu menu:
        self._OM.set_menurec(self._submenu+'.misc.visu', toggle=True,
                             selected=True,
                             callback=self._callback_toggle_visu)

        # Define any specific visualisation options:
        self.define_visu_options()
        return True


    #....................................................................

    def _callback_toggle_visu (self, selected):
        """Called whenever the toggle widget before the visu menu is toggled"""
        # print '\n** callback_toggle_visu(',selected,')'
        menurec = self._OM.set_menurec(self._submenu, selected=selected)
        self._visualize = selected
        return True


    #---------------------------------------------------------------------

    def bookmark (self, node=None, trace=True):
        """Append the given node(s) to the list of nodes to be bookmarked.
        """
        if node:
            nn = node
            if not isinstance(node, (list,tuple)):
                nn = [node]
            for n in nn:
                if trace:
                    print ' .bookmark(',str(n),')'
                if is_node(n):
                    self._bm.append(n)
        # Always return the internal list:
        return self._bm

    #---------------------------------------------------------------------

    def visualize_generic (self, result, trace=False):
        """Generic function for visualization.
        """
        # First do some checks:
        if not self._visualize:
            return result
        if not self.has_option('misc.visu.bookpage'):
            return result                                 # no visualization options defined
        page = self.optval('misc.visu.bookpage')
        if not page:
            return result                                 # no visualization required
        folder = None

        # Do specific visualization (if any):
        result = self.visualize (result, trace=False)

        # Prepend a bookmark for the input node (if required):
        if is_node(self._input):
            if not result==self._input:
                self._bm.insert(0, self._input)           # make it the first one

        # Append a bookmark for the result node (if relevant):
        if is_node(result):
            self.bookmark(result)

        # Make the bookmark(s) for the nodes collected in self._bm:
        if len(self._bm)>0:
            JEN_bookmarks.create(self._bm, page=page, folder=folder)

        # Always return the (possibly 'grown') result:
        return result



    #---------------------------------------------------------------------
    # Class-specific visualization:
    #--------------------------------------------------------------------

    def define_visu_options(self):
        """Specific function for adding visualization option(s) to the
        visualisation submenu. This version is suitable for derived
        classes that have nodes for input and result. It has to be
        re-implemented for classes with other inputs/results.
        """
        if self._has_input:
            self._OM.define(self.optname('misc.visu.compare'), None,
                            prompt='show result vs input',
                            opt=[None,'Subtract','Divide'], more=str, 
                            doc="""Insert and bookmark a side-branch that
                            compares the result with the input. 
                            """)
        if False:
            # Perhaps it is possible to extract all new nodes from the tree....
            self._OM.define(self.optname('misc.visu.allnodes'), False,
                            prompt='bookmark all nodes',
                            opt=[True, False],  
                            doc="""If True, bookmark all new nodes
                            of this Growth, e.g. for debugging.
                            """)
        return True

    #--------------------------------------------------------------------

    def visualize (self, result, trace=False):
        """Specific visualization, as specified in .define_visu_options().
        This default version is suitable for those cases where the input
        and the result are nodes. It has to be reimplemented by derived
        classes that have other types of input/result.
        Note that the result may be modified ('grown') in the process.
        """
        # If required, insert a side-branch to compare the result with the input:  
        if is_node(self._input):
            binop = self.optval('misc.visu.compare')
            if binop:
                comp = self.ns['compare'] << getattr(Meq, binop)(result, self._input)
                self.bookmark(comp)
                node = self.ns['compare_reqseq'] << Meq.ReqSeq(result, comp, result_index=0)
        # Return the (possibly grown) result: 
        return result












    #=====================================================================================
    #=====================================================================================
    # Specific part: Functions to be re-implemented by a derived class.
    # The following are placeholders that can serve as examples.
    # See also the derived class GrowthTest below.
    #=====================================================================================
    #=====================================================================================



    def define_compile_options(self, trace=False):
        """Specific: Define the compile options.
        This placeholder function should be reimplemented by a derived class.
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #............................................
        # ... The specific body ...
        self._OM.define(self.optname('xxx'), 67)
        #............................................
        return self.on_exit(trace=trace)
    

    #--------------------------------------------------------------------

    def grow (self, ns, node, test=None, trace=False):
        """Specific: Generate ('grow') new nodes onto the input,
        using the given nodescope ns.
        This placeholder function should be reimplemented by a derived class.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #............................................
        # ... The specific body ...
        result = node
        #............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)









#=============================================================================
#=============================================================================
#=============================================================================
#=============================================================================

class GrowthTest(Growth):
    """Class derived from Growth"""

    def __init__(self, quals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Growth.__init__(self, quals=quals,
                        name='GrowthTest',
                        submenu=submenu,
                        OM=OM, namespace=namespace,
                        **kwargs)
        return None

    #====================================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = Growth.oneliner(self)
        return ss
    

    def display(self, txt=None, full=False, recurse=3,
                OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble('GrowthTest', level=level, txt=txt)
        #...............................................................
        Growth.display(self, full=full,
                     recurse=recurse,
                     OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)

    
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This placeholder function should be reimplemented by a derived class.
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................
        self._OM.define(self.optname('unop'), 'Cos',
                        prompt='unary',
                        opt=['Sin','Cos'], more=str,
                        doc="""apply an unary operation.
                        """)
        #..............................................
        return self.on_exit(trace=trace)


    #--------------------------------------------------------------------

    def grow (self, ns, node=None, test=None, trace=False):
        """Specific: Make the plugin subtree.
        This placeholder function should be reimplemented by a derived class.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        if test==True:
            test = dict(unop='Cos')

        # Read the specified options:
        unop = self.optval('unop', test=test)

        # Make the subtree:
        node = self.ns['result'] << getattr(Meq,unop)(node)

        #..............................................
        # Finishing touches:
        return self.on_output (node, trace=trace)



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


grt = None
if 0:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('long', unit='rad')
    # xtor.add_dimension('s', unit='rad')
    ## xtor.make_TDLCompileOptionMenu()       # NOT needed (just for testing)

    grt = GrowthTest(quals='hjk')
    grt.make_TDLCompileOptionMenu()
    # grt.display()


def _define_forest(ns):

    global grt,xtor
    if not grt:
        xtor = Executor.Executor()
        # xtor.make_TDLCompileOptionMenu()
        grt = GrowthTest(quals=[1,2])
        grt.make_TDLCompileOptionMenu()

    cc = []

    node = ns << 3.4
    rootnode = grt.grow(ns, node)
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
    """Just display the current contents of the Growth object"""
    grt.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Growth object"""
    grt.display('_tdl_job', full=True)
       
def _tdl_job_print_tree (mqs, parent):
    """Print the tree"""
    grt.print_tree()
       


       










#===============================================================
# Test routine:
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    OM = None
    if 0:
        OM = OptionManager.OptionManager()

    if 0:
        grt = Growth('bbb', OM=OM)
        grt.display('initial')

    if 1:
        grt = GrowthTest('bbb', OM=OM)
        grt.display('initial')

    if 1:
        grt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        test = dict()
        grt.grow(ns, node, test=test, trace=True)

    if 1:
        grt.display('final', OM=True, full=True)

    if 0:
        grt.print_tree(recurse=1)
        grt.print_tree(recurse=2)
        grt.print_tree(recurse=3)
        grt._OM.showtree()

#===============================================================


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
                 **kwargs):

        # For reporting only:
        self._frameclass = 'Growth.'+name

        # Variables consistent with Meow.Parameterization:
        self.ns = None                              # see .on_input()
        self.ns0 = None                             # see .on_input()
        self.make_name_and_submenu (name, submenu, quals)

        # Extra keyword arguments may be supplied to the constructor.
        self._kwargs = kwargs
        if not isinstance(self._kwargs, dict):
            self._kwargs = dict()
        self._kwargs.setdefault('default', dict())
        self._kwargs.setdefault('insist', dict())
        self._kwargs.setdefault('toggle', False)
        self._kwargs.setdefault('ignore', False)
        self._kwargs.setdefault('has_input', True)
        self._kwargs.setdefault('defer_compile_options', False)

        # If toggle=True, provide a toggle widget to its subenu
        self._toggle = self._kwargs['toggle']
        self._toggle_group = []

        # The object may be ignored/hidden:
        self._ignore = self._kwargs['ignore']
        self._visualize = True

        # Keep the input of .grow() for internal use
        self._input = None
        self._has_input = self._kwargs['has_input']

        # Keep the result (of .grow()) for internal use
        self._result = None

        # Switch that indicates whether the mandatory function
        # self.create_Growth_objects() has been called already
        self._created_Growth_objects = False
        self._Growth_objects = dict()

        # Keep an internal list of nodes to be bookmarked
        # See .bookmark() and .visualize_generic()
        self._bm = []

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
        if not self._kwargs['defer_compile_options']:
            self.define_compile_options()
        
        # Finished:
        return None


    #--------------------------------------------------------------------

    def make_name_and_submenu (self, name=None, submenu=None, quals=None):
        """
        Helper function that is called from __init__().
        Make self.name by appending any qualifiers to name.
        Make self._shortname from the capitals of self.name.
        Make self._submenu by appending self.name to submenu.
        """
        # The use of self.name is consistent with Meow/Parameterization...
        self.name = name

        # Make a short name from all chars ubtil the 2nd capital,
        # followed by the subsequent capitals and numbers.
        # So the short name will look like: TApplyU or DemoR
        capitals = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numbers = '01234567890'
        ss = ''
        capcount = 0
        for char in name:
            if (char in capitals):
                capcount += 1
                ss += char
            elif (char in numbers):
                ss += char
            elif capcount==2:
                ss += char
            # print '-',char,capcount,'->',ss
        self._shortname = ss
        
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
             self._shortname += '_'+str(qual)

        # The OptionManager (sub)menu to be used:
        # self._submenu = submenu+'.'+self.name
        self._submenu = submenu+'.'+self._shortname
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
        self._OM.set_menurec(self._submenu, selected=(not self._ignore))
        return self._ignore


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = self._frameclass+':'
        if not self.name==self._shortname:
            ss += ' ('+self._shortname+')'
        ss += ' submenu='+str(self._submenu)
        if self._ignore:
            ss += ' (ignored)'
        return ss


    def display(self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble('Growth', level=level, txt=txt)
        #...............................................................
        print prefix,'  * kwargs ('+str(self._kwargs.keys())+'):'
        for key in self._kwargs.keys():
            rr = self._kwargs[key]
            if not isinstance(rr, dict):
                print prefix,'    - '+key+' = '+str(rr)            
            else:
                for key1 in rr.keys():
                    print prefix,'      - '+key1+' = '+str(rr[key1])            
        #...............................................................
        print prefix,'  * has_input = '+str(self._has_input)
        if self._has_input:
            self.display_value(self._input, 'input', prefix=prefix)
        #...............................................................
        self.display_value(self._result, 'result', prefix=prefix)
        #...............................................................
        print prefix,'  * created_Growth_objects: '+str(self._created_Growth_objects)
        for key in self._Growth_objects.keys():
            G = self._Growth_objects[key]
            print prefix,'    - '+key+': '+str(G.oneliner())
        #...............................................................
        print prefix,'  * datadesc: '+str(self.datadesc(trace=False))
        #...............................................................
        print prefix,'  * nodes to be bookmarked (visualize='+str(self._visualize)+'):'
        for node in self._bm:
            print prefix,'     - '+str(node)
        #...............................................................
        print prefix,'  * has toggle box = '+str(self._toggle)
        if self._toggle:
            for g in self._toggle_group:
                print prefix,'     - '+str(g.oneliner())
        #...............................................................
        print prefix,'  * '+self._OM.oneliner()
        print prefix,'  * external OptionManager: '+str(self._external_OM)
        if not self._external_OM:
            if OM and full: self._OM.display(full=False, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)

    #.........................................................................

    def display_value(self, v, name='<name>', prefix='*'):
        """Helper function"""
        print prefix,'  * '+str(name)+' type = '+str(type(v))
        midfix = '     -' 
        if is_node(v):
            print prefix,midfix,str(v)
            # self.display_subtree(v) 
        elif getattr(v, 'oneliner', None):
            print prefix,midfix,v.oneliner()
        elif isinstance(v, list):
            print prefix,midfix,' list length ='+str(len(v))
        elif isinstance(v, dict):
            print prefix,midfix,' dict keys ='+str(v.keys())
        else:
            print prefix,midfix,'=',str(v)
        return True
    
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
        if level==0:
            print
            if self._OM:
                self._OM.print_tree()
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

        # Define some compile-time options:
        self.define_entry_options()

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

        # This is a menu 'of the first stare'.
        # The stare number is used in OM.print_tree()
        self._OM.set_menurec(self._submenu, stare=1, descr=self.name)

        # Optional: add a toggle widget to the menu:
        if self._toggle:
            self._OM.set_menurec(self._submenu, toggle=True,
                                 callback=self._callback_toggle)

        # Define some exit compile-time options (if any) at the end of the
        # class-specific function .define_compile_options().
        # The class-specific functions may be re-implemented by derived classes.
        self.define_exit_options()              # class-specific

        # Miscellaneous options:
        self.define_generic_misc_options()      # generic
        self.define_misc_options()              # class-specific

        # Visualization options (part of misc menu):
        self.define_generic_visu_options()      # generic
        self.define_visu_options()              # class-specific
        

        # Progress message: 
        if trace:
            print s,'\n'

        return True


    #....................................................................

    def _callback_toggle (self, selected):
        """Called whenever the toggle widget before the menu is toggled"""
        trace = False
        self.select(selected, trace=trace)
        if selected:
            for g in self._toggle_group:
                g.select(not selected, trace=trace)
        return True

    def select(self, select, trace=False):
        """Select/deselect this object (see _callback_toggle())"""
        self._OM.set_menurec(self._submenu, selected=select)
        self._ignore = not select
        ## self._OM.enable(self._submenu, selected)  NOT a good idea!!
        if trace:
            print '\n** ',self.name,' .select(',select,') ignore =',self._ignore
        return True

    def toggle_group (self, append=None, reset=False, trace=False):
        """Interaction with the toggle-group of this object. It contains
        a list of other Growth objects, of which only one at a time may
        be selected. See also _callback_toggle().
        """
        if reset:
            self._toggle_group = []
        if append:
            if not isinstance(append, list): append = [append]
            for g in append:
                if not g==self:
                    self._toggle_group.append(g)  
                    g._toggle_group.append(self)     
        return self._toggle_group

    #====================================================================
    # Helper functions for access to options:
    #====================================================================

    def defopt (self, name, value, opt=None, more=None,
                callback=None, prompt=None, doc=None,
                trace=False):
        """Encapsulation of self._OM.define(). It allows central completion
        of the option name, and the interaction with constructor kwargs.
        If the option name is a field in self._kwargs[default], the default
        value will be changed. If it is a field in self._kwargs[insist], the
        option value will be changed, and the option itself will be disabled.
        """
        disable = None
        for key in ['default','insist']:
            if self._kwargs[key].has_key(name):
                was = value
                new = self._kwargs[key][name]
                value = new
                # print '\n** .defopt(',name,'): =',was,'->',new,' (',key,')\n'
                if key=='insist':
                    disable = True
        self._OM.define(self.optname(name), value, opt=opt, more=more,
                        callback=callback, prompt=prompt, doc=doc,
                        disable=disable)
        return True

    #.............................................................

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
        if not self._created_Growth_objects:
            self.create_Growth_objects()
            self._created_Growth_objects = True
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
        proceed = True

        # Store and check the input, and initialise the return value
        if self._has_input:
            self._input = input         # keep for later use
            proceed = self.check_input(self._input, severe=severe, trace=trace)

        # If the ignore switch is set, do nothing (see also .ignore())
        # NB: This should be AFTER setting self._input !!
        if self._ignore:
            proceed = False              # This will cause .grow() to exit
            if trace:
                print s,'ignored'

        # If things are still OK (proceed==True), make sure that all the
        # necessary Growth objects have been created: 
        if proceed:
            if not self._created_Growth_objects:     # not yet done
                self.create_Growth_objects()         # call the function  
                self._created_Growth_objects = True  # set the switch

        # Check the nodescope, and make the self.ns/ns0 that will be used.
        self.ns0 = ns
        if is_node(ns):
            self.ns = ns.QualScope(self._quals)        
            self.ns0 = ns.QualScope() 
        else:
            self.ns = ns.Subscope(self._shortname)

        # Progress message: 
        if trace:
            print '\n',s
            print '    self.ns =',str(type(self.ns))
            print '    ',str(self.ns('dummy'))

        # NB: The calling routine .grow() aborts if return=False
        return proceed


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

        # Keep the .grow() result for internal use (e.g. in .visualize()):
        self._result = result

        # Visualize (generic AND class-specific), as specified by the options.
        # This function calls the class-specific function .visualize(),
        # which may be reimplemented by derived classes.  
        self.visualize_generic (trace=trace)

        # Progress message:
        if trace:
            if is_node(self._result):
                self.display_subtree(self._result) 
                print s,'->',str(self._result),'\n'
            elif gettattr(self._result, oneliner,None):
                print s,'->',self._result.oneliner(),'\n'
            else:
                print s,'->',type(self._result),'\n'
        return self._result          



    #====================================================================
    # Miscellaneous settings
    #====================================================================

    def define_generic_misc_options(self):
        """Define a generic submenu of visualization option(s).
        """
        self.defopt('misc.ignore', False,
                    prompt='ignore/hide this Growth',
                    opt=[True,False,None],
                    callback=self._callback_ignore,
                    doc="""this is used for testing
                    """)
        self._OM.set_menurec(self._submenu+'.misc',
                             prompt='miscellaneous',
                             stare=2)

        if len(self._mode.keys())>0:
            self.defopt('misc.mode', None,
                        prompt='select a standard mode',
                        opt=[None]+self._mode.keys(),
                        callback=self._callback_mode,
                        doc="""The Growth option values may be preset
                        to the values of a number of standard modes.
                        """)
        self.defopt('misc.help', None,
                    prompt='help on this object',
                    opt=[None,'show','print','derivation_tree'],
                    callback=self._callback_help,
                    doc="""should be self-explanatory
                    """)

        # Finished:
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

    #--------------------------------------------------------------------

    def _callback_help (self, help):
        """Called whenever option 'misc.help' changes"""
        if help=='derivation_tree':
            print self.show_derivation_tree(trace=False)
        elif help:
            print self.help(specific=True, trace=False)
        self.setval ('misc.help', None)
        # self._OM.setval('misc.help', None)
        return True


    def help (self, level=0, specific=True, trace=True):
        """Generic help function, calls reimplemented specific one.
        """
        prefix = self.help_prefix(level)
        ss = '\n'+prefix
        ss += '\n'+prefix+'================================'
        ss += '\n'+prefix+'Help for: '+str(self.oneliner())
        ss += '\n'+prefix+'================================'
        ss += self.help_format(self.grow.__doc__, level=0)
        if specific:
            ss += self.help_format (self.help_specific(), level=level+1)
        print '\n'+prefix+'\n'
        if trace:
            print ss
        return ss

    def help_prefix (self, level=0):
        """Make a prefix string, to be used when formatting help strings."""
        return '**'+(level*'..')+' '

    def help_format (self, ss, level=0):
        """Format the given string ss as a help-string. Split it into lines,
        prefix each line accoring to level, and past them together again.
        """
        prefix = self.help_prefix(level)
        sout = ''
        if ss and len(ss)>0:
            sout = '\n'+prefix
            for s in ss.split('\n'):
                sout += '\n'+prefix+s
        return sout

    #--------------------------------------------------------------------------

    def show_derivation_tree(self, trace=True):
        """Return a string that describes the derivation tree of this object.
        """
        prefix = self.help_prefix()
        ss = '\n'+prefix
        ss += '\n'+prefix+'==========================================='
        ss += '\n'+prefix+'Derivation tree for: '+str(self.oneliner())
        ss += '\n'+prefix+'==========================================='
        ss += self.help_format(self.grow.__doc__, level=1)
        ss = self.derivation_tree(ss, level=2)
        if trace:
            print ss
        return ss



    #====================================================================
    # Generic visualization:
    #====================================================================


    def define_generic_visu_options(self):
        """Generic function to define the generic visualization option(s).
        """
        self.defopt('misc.visu.bookpage', self.name,
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

        return True


    #....................................................................

    def _callback_toggle_visu (self, selected):
        """Called whenever the toggle widget before the visu menu is toggled"""
        # print '\n** callback_toggle_visu(',selected,')'
        menurec = self._OM.set_menurec(self._submenu, selected=selected)
        self._visualize = selected
        return True


    #---------------------------------------------------------------------

    def bookmark (self, node=None, prepend=False, trace=False):
        """Append the given node(s) to the list of nodes to be bookmarked.
        """
        if node:
            nn = node
            if not isinstance(node, (list,tuple)):
                nn = [node]
            for n1 in nn:
                if trace:
                    print ' .bookmark(',str(n1),')'
                if is_node(n1) and (not n1 in self._bm):
                    if prepend:
                        self._bm.insert(0,n1)
                    else:
                        self._bm.append(n1)
        # Always return the internal list:
        return self._bm

    #---------------------------------------------------------------------

    def visualize_generic (self, trace=False):
        """The generic visualization function mainly makes bookmarks and
        bookpages for interesting nodes (see also .bookmark()). The power
        of this feature is under-valued at the moment, but this will change...
        This function also call the class-specific function .visualize(),
        which may be re-implemented by derived classes, to do more interesting
        things.
        """
        # First checks whether visualization is required, or possible at all:
        if not self._visualize:
            return True
        if not self.has_option('misc.visu.bookpage'):
            return True                                   # no visualization options defined
        page = self.optval('misc.visu.bookpage')
        if not page:
            return True                                   # no visualization required
        folder = None

        # Do specific visualization (if any). This requires self._result, since
        # the result may be changed in the process, e.g. by inserting new nodes.
        # Since the re-implementer may forget to do this, a check is provided.
        before = self._result
        self._result = self.visualize (self._result, trace=False)
        if True:
            print '\n** .on_output()  .visualize():'
            print '   result type before: ',type(before)
            print '   result type after : ',type(self._result)
            print '   is the same type: ',isinstance(self._result, type(before))
            print

        # Prepend a bookmark for the input node (if required):
        if is_node(self._input):
            if not self._result==self._input:
                self.bookmark(self._input, prepend=True)  # make it the first one

        # Append a bookmark for the result node (if relevant):
        if is_node(self._result):
            self.bookmark(self._result)

        # Make the bookmark(s) for the nodes collected in self._bm:
        if len(self._bm)>0:
            JEN_bookmarks.create(self._bm, page=page, folder=folder)

        # Finished
        return True








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
        #............................................
        return self.on_exit(trace=trace)

    #....................................................................

    def define_entry_options(self):
        """Funcion called by .on_entry() in .define_compile_options().
        May be reimplemented by a derived class
        """
        return True

    #....................................................................

    def define_exit_options(self):
        """Funcion called by .on_exit() in .define_compile_options().
        May be reimplemented by a derived class
        """
        return True


    #--------------------------------------------------------------------

    def create_Growth_objects (self, trace=False):
        """Specific: Create any Growth objects, sharing the OptionManager
        This placeholder function should be reimplemented by a derived class.
        """
        return True

    #--------------------------------------------------------------------

    def grow (self, ns, input, test=None, trace=False):
        """The Growth class is the base-class for an entire arboretum of derived
        classes. Each Growth class has a mandatory .grow(ns, ...) function that
        generates ('grows') new nodes onto its input, using the given nodescope ns.
        The result may be passed on to other Growth objects, etc.
        """
        # Check the input, and make self.ns:
        if not self.on_input (ns, input, trace=trace):
            return self.bypass (trace=trace)
        #............................................
        result = input
        #............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)


    #--------------------------------------------------------------------

    def check_input (self, input, severe=True, trace=False):
        """Specific function called by the generic function .on_input()
        to check the input to .grow().
        It should be re-implemented by derived classes whose input is
        expected to be something else (e.g. a Visset22 object, etc).
        This routine should return True (OK) or False (not OK).
        """
        return True


    #--------------------------------------------------------------------

    def check_result (self, result, severe=True, trace=False):
        """Specific function called by the generic function .on_result()
        to check the result of .grow().
        It should be re-implemented by derived classes whose result is
        expected to be something else (e.g. a Visset22 object, etc).
        """
        # If OK, just pass on the valid result:
        return result

    #--------------------------------------------------------------------

    def derivation_tree (self, ss, level=1):
        """Append the formatted derivation tree of this object to the string ss. 
        This function may be re-implemented by a derived class, by un-commenting
        the two lines below, and replacing Growth with the name of the class
        from which it is derived. 
        """
        # ss += self.help_format(Growth.Growth.grow__doc__, level=level)
        # ss = Growth.Growth.derivation_tree(self, ss, level=level+1)
        return ss

    #--------------------------------------------------------------------

    def help_specific (self):
        """Format a string with specific help for this object, if any.
        This function is called by the generic function .help().
        This placeholder may be re-implemented by derived classes.
        """
        ss = ''
        return ss


    #---------------------------------------------------------------------
    # Class-specific visualization:
    #--------------------------------------------------------------------

    def define_visu_options(self):
        """Specific function for adding visualization option(s) to the
        visualisation submenu. This is a placeholder, which may be
        re-implemented by classes with other inputs/results.
        """
        return True

    #--------------------------------------------------------------------

    def visualize (self, result, trace=False):
        """Specific visualization, as specified in .define_visu_options().
        This is a plceholder, which may be reimplemented by derived
        classes that have other types of input/result.
        """
        return result


    #--------------------------------------------------------------------
    # Class-specific misc settings:
    #--------------------------------------------------------------------

    def define_misc_options(self):
        """Define class-specific options for the misc menu.
        To be reimplemented by derived classes, if necessary.
        """
        return True


    #--------------------------------------------------------------------
    # Interacion with the data-description record:
    #--------------------------------------------------------------------

    def datadesc (self, merge=None, trace=False, **kwargs):
        """Return the data-description record.
        If another datadesc (merge) is specified, update the local one.
        """
        return self._datadesc
    





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
        self.defopt('unop', 'Cos',
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

    if 1:
        grt.print_tree(recurse=1)
        grt.print_tree(recurse=2)
        grt.print_tree(recurse=3)
        grt._OM.showtree()

#===============================================================


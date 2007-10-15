# file: ../JEN/Grow/Growth.py

# History:
# - 14sep2007: creation (from Plugin.py)
# - 05oct2007: change over to OMInterface (OMI)

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

from Timba.Contrib.JEN.control import OMInterface
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

        #------------------------------------------------------------------

        # Extra keyword arguments may be supplied to the constructor.
        # NB: See also OMInterface.py
        self._kwargs = kwargs
        if not isinstance(self._kwargs, dict):
            self._kwargs = dict()

        # Leaf objects require no input, the others do:
        self._kwargs.setdefault('has_input', True)
        self._has_input = self._kwargs['has_input']

        # NB: This is used ONLY by TwigBranch.py, and perhaps not necessary....
        self._kwargs.setdefault('defer_compile_options', False)


        #------------------------------------------------------------------

        self._OMI = OMInterface.OMInterface(quals,
                                            name=name,
                                            submenu=submenu,
                                            OM=OM, namespace=namespace,
                                            **kwargs)

        self._OMI.make_name_and_submenu (name, submenu, quals)

        # Temporary (until all Twig classes have been updated)
        self._OM = self._OMI._OM
        self.name = self._OMI.name
        self._shortname = self._OMI._shortname
        self._quals = self._OMI._quals
        self._submenu = self._OMI._submenu

        #------------------------------------------------------------------

        # Keep the input of .grow() for internal use
        # NB: For multiple inputs (objects), this may be a list.
        self._input = None

        # Keep the result (of .grow()) for internal use
        # NB: For multiple results (objects), this may be a list.
        self._result = None

        # Visualization control:
        self._visualize = True
        self._make_bookmark = dict(input=True, result=True)
        # Keep an internal list of nodes to be bookmarked
        # See .bookmark() and .visualize_generic()
        self._bm = []

        # Switch that indicates whether the mandatory function
        # .create_Growth_objects() has been called already
        self._created_Growth_objects = False
        self._Growth_objects = dict()

        # self._rider....?
        # Initialize a control dict for keeping track of the (result) data type
        # and format. It may be used by Growths to do the correct thing.
        # This dict should be updated when the data type or format changes,
        # using self.datadesc(). It should be passed down a chain of Growths.
        self._datadesc = dict(is_complex=False, nelem=1, dims=[1])

        # Optionally, the plugin options may be preset to the values
        # belonging to a number of standard modes. See .preset_to_mode().
        # Move to OMInterface.py...?
        self._mode = dict()

        # Define the required runtime options:
        if not self._kwargs['defer_compile_options']:
            self.define_compile_options()
        
        # Finished:
        return None



    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = self._frameclass+':'
        if not self._OMI.name==self._OMI._shortname:
            ss += ' ('+self._OMI._shortname+')'
        ss += ' submenu='+str(self._OMI._submenu)
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
            self._OMI.display_value(self._input, 'input', prefix=prefix)
        #...............................................................
        self._OMI.display_value(self._result, 'result', prefix=prefix)
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
        print prefix,'  * '+self._OMI.oneliner()
        if OM: self._OMI.display(full=False, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)


    #-------------------------------------------------------------------------

    def display_preamble(self, prefix='Growth', level=0, txt=None):
        """Helper function called by .display(). Also used in reimplemented
        .display() in derived classes"""
        return self._OMI.display_preamble(prefix=prefix, level=level, txt=txt)


    def display_postamble(self, prefix, level=0):
        """Helper function called by .display(). Also used in reimplemented
        .display() in derived classes"""
        return self._OMI.display_postamble(prefix=prefix, level=level)


    #--------------------------------------------------------------------------

    def display_IO(self, v, name='<name>', full=False, level=0):
        """Helper function to display self._input or self._result.
        """
        prefix = level*'..'
        if level==0:
            print '\n\n'
            print '******************************************'
            print '** display_IO: '+str(name)+' (type= '+str(type(v))+'):'
            print '******************************************'
        if is_node(v):
            self.display_subtree(v) 
        elif getattr(v, 'display', None):
            # v.display(name, full=full, level=level)
            v.display(name, full=full)        # Visset22 has no level argument
        elif isinstance(v, (list,tuple)):
            for (k,v1) in enumerate(v):
                name1 = name+'['+str(k)+']'
                print '\n'+prefix,'----------- '+name1+':'
                self.display_IO(v1, name=name1, full=full, level=level+1)
        elif isinstance(v, dict):
            for key in v.keys():
                print prefix,' - '+str(key)+': '+str(type(v[key]))
        else:
            print prefix,' - '+str(name)+' = '+str(v)
        if level==0:
            print '********************************************'
            print '** end of display_IO: '+str(name)
            print '********************************************'
            print
        return True


    #====================================================================
    # Some service(s) available to all classes derived from Growth:
    #====================================================================

    def display_subtree(self, node, recurse=10, trace=False):
        """Display the subtree behind the given node.
        """
        print '\n** ',self._OMI.name,': display_subtree(',str(node),'):'
        display.subtree(node, recurse=recurse) 
        return True


    def print_tree(self, recurse=10, trace=False):
        """Display the entire tree
        """
        return self._OMI.print_tree(recurse=recurse)


    #===================================================================
    # Generic functions dealing with (compile) options:
    #====================================================================

    def on_entry(self, trace=False):
        """Generic function that should be called at the start of the
        specific function .define_compile_options() in a derived class.
        It does some generic initializing etc.
        """
        s = '** '+self._OMI._submenu+': on_entry(): '
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
        # trace = True
        s = '** '+self._OMI._submenu+': on_exit(): '

        # Check whether things have been done in the correct order:
        if not self._done_on_entry:
            raise ValueError
        self._done_on_exit = True

        # Change the (automatic) prompt in the menu
        prompt = '- customize'
        prompt += ': '+str(self._OMI.name)
        self._OMI.set_menurec(prompt=prompt)

        # This is a menu 'of the first stare'.
        # The stare number is used in OM.print_tree()
        self._OMI.set_menurec(stare=1, descr=self._OMI.name)

        # May be controlled by a 'toggle_box=True' in the constructor.
        # This is picked up by OMInterface.py 
        self._OMI.make_toggle_box(select=True)

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


    #--------------------------------------------------------------------

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the actual TDL menu of compile-time options.
        NB: This call is not needed with an external OptionManager,
        since the menu will be part of that of the parent object.
        """
        if not self._created_Growth_objects:
            self.create_Growth_objects()
            self._created_Growth_objects = True
        self._OMI.make_TDLCompileOptionMenu(**kwargs)
        return True
    


    #====================================================================
    # Generic functions dealing with subtree generation:
    #====================================================================

    def on_input (self, ns, input=None, severe=True, trace=False):
        """
        Generic function that should be called at the start of the
        specific function .grow() in a derived class.
        It does various checks, and some common things.
        """
        s = '** '+self._OMI._submenu+': on_input('+str(type(ns))+','+str(input)+'): '

        # Initialize the return value (see below)
        proceed = True

        # Store and check the input, and initialise the return value
        if self._has_input:
            self._input = input                      # keep for later use
            proceed = self.check_input(self._input, severe=severe, trace=trace)

        # If not selected, do nothing.
        # NB: This should be AFTER setting self._input !!
        if not self._OMI.is_selected():
            proceed = False                          # This will cause .grow() to exit
            if True or trace:
                print s,'not selected (ignored)'

        # If things are still OK (proceed==True):
        if proceed:
            # Make sure that all the necessary Growth objects have been created: 
            if not self._created_Growth_objects:     # not yet done
                self.create_Growth_objects()         # call the function  
                self._created_Growth_objects = True  # set the switch

            # Check whether things have been done in the correct order:
            # NB: Do this here to allow 'defer_compile_options'
            if not self._done_on_exit:
                raise ValueError
            self._done_on_input = True

            # Check the nodescope, and make the self.ns/ns0 that will be used.
            self.ns0 = ns
            if is_node(ns):
                self.ns = ns.QualScope(self._OMI._quals)        
                self.ns0 = ns.QualScope() 
            else:
                self.ns = ns.Subscope(self._OMI._shortname)

        # Progress message: 
        if trace:
            print '\n',s
            if proceed:
                print '    self.ns =',str(type(self.ns))
                print '    ',str(self.ns('dummy'))
            print '   ',self.oneliner()

        # NB: The calling routine .grow() aborts if return=False
        return proceed


    #--------------------------------------------------------------------

    def bypass (self, trace=False):
        """Generic function that should be called by .grow() whenever it
        exits prematurely for some reason.
        """
        # trace = True

        # Check whether things have been done in the correct order:
        if False:
            if not self._done_on_input:
                raise ValueError
            self._done_on_output = True

        result = self._input
        if trace:
            print '** '+self._OMI._submenu+': bypass() ->',str(result)
            print '   ',self.oneliner()
        return result

    #--------------------------------------------------------------------

    def on_output (self, result, severe=True, trace=False):
        """Generic function that should be called at the end of the
        specific function .grow() in a derived class.
        It does checks and some generic things.
        - If severe==True, an error is produced if the result is not valid.
        """
        s = '\n** '+self._OMI._submenu+': on_output('+str(result)+'): '

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
            elif getattr(self._result, 'oneliner', None):
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

        if len(self._mode.keys())>0:
            self._OMI.defopt('misc.mode', None,
                             prompt='select a standard mode',
                             opt=[None]+self._mode.keys(),
                             callback=self._callback_mode,
                             doc="""The Growth option values may be preset
                             to the values of a number of standard modes.
                             """)

        self._OMI.defopt('misc.help_object', None,
                         prompt='help on this object',
                         opt=[None,'show','print',
                              'derivation_tree',
                              'oneliner',
                              'display','display_full',
                              'display_input','display_input_full',
                              'display_result','display_result_full',
                              ],
                         callback=self._callback_help_object,
                         doc="""Various explanations about this object.
                         - show:  show the specific help.
                         - print: print the specific help.
                         - derivation_tree: class inheritance tree.
                         - oneliner: show its one-line summary.
                         - display[_full]: call its .display() function.
                         """)

        self._OMI.defopt('misc.help_tree', None,
                         prompt='help on this tree',
                         opt=[None,'show','print'],
                         callback=self._callback_help_tree,
                         doc="""Show/print a summary of the Growth tree that will
                         result from the currently selected compile options.
                         """)

        self._OMI.set_menurec('misc',
                              prompt='miscellaneous',
                              stare=2)

        # Finished:
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

    def _callback_help_tree (self, help):
        """Called whenever option 'misc.help_tree' changes.
        It gives help on the Meq(sub)Tree resulting from this object.
        """
        if help:
            self.print_tree()
        self.set_value ('misc.help_tree', None)          # reset to None
        return True

    #--------------------------------------------------------------------

    def _callback_help_object (self, help):
        """Called whenever option 'misc.help_object' changes.
        It gives all kinds of help on this Growth object.
        """
        if help=='derivation_tree':
            print self.show_derivation_tree(trace=False)
        elif help=='oneliner':
            print self.oneliner()
        elif help=='display':
            self.display(full=False, OM=False)
        elif help=='display_full':
            self.display(full=True, OM=True)
        elif help=='display_input':
            self.display_IO(self._input, 'input', full=False)
        elif help=='display_input_full':
            self.display_IO(self._input, 'input', full=False)
        elif help=='display_result':
            self.display_IO(self._result, 'result', full=False)
        elif help=='display_result_full':
            self.display_IO(self._result, 'result', full=False)
        elif help:
            print self.help(specific=True, trace=False)
        self.set_value ('misc.help_object', None)        # reset to None
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
        self._OMI.defopt('misc.visu.bookpage', self._OMI.name,
                         prompt='bookpage name',
                         opt=[None,self._OMI.name], more=str, 
                         doc="""Specify a bookpage for the various bookmarks
                         generated for this Growth. If bookpage==None,
                         visualization for this Growth object is inhibited.
                         """)

        # Change the default menu prompt to a more instructive one:
        self._OMI.set_menurec('.misc.visu',
                             prompt='visualization')

        # Add a toggle widget to the visu menu:
        self._OMI.set_menurec('.misc.visu', toggle=True,
                              selected=True,
                              callback=self._callback_toggle_visu)

        return True


    #....................................................................

    def _callback_toggle_visu (self, selected):
        """Called whenever the toggle widget before the visu menu is toggled"""
        # menurec = self._OMI.set_menurec(selected=selected)
        menurec = self._OMI.set_menurec('misc.visu', selected=selected)
        self._visualize = selected
        # print '\n** callback_toggle_visu(',selected,') ->',self._visualize,'\n'
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
        if not self._OMI.has_option('misc.visu.bookpage'):
            return True                                   # no visualization options defined
        page = self._OMI.optval('misc.visu.bookpage')
        if not page:
            return True                                   # no visualization required
        folder = None

        # Do specific visualization (if any). This requires self._result, since
        # the result may be changed in the process, e.g. by inserting new nodes.
        # Since the re-implementer may forget to do this, a check is provided.
        before = self._result
        self._result = self.visualize (self._result, trace=False)
        if False:
            print '\n** .on_output()  .visualize():'
            print '   result type before: ',type(before)
            print '   result type after : ',type(self._result)
            print '   is the same type: ',isinstance(self._result, type(before))
            print

        # Prepend a bookmark for the input node (if required):
        if self._make_bookmark['input']:
            if is_node(self._input):
                if not self._result==self._input:
                    self.bookmark(self._input, prepend=True)  # make it the first one

        # Append a bookmark for the result node (if relevant):
        if self._make_bookmark['result']:
            if is_node(self._result):
                self.bookmark(self._result)

        # Make the bookmark(s) for the nodes collected in self._bm:
        if len(self._bm)>0:
            JEN_bookmarks.create(self._bm, page=page, folder=folder)

        # Finished
        return True




    #====================================================================
    # Interface functions (temporary?) with its OptionManagerInterface (OMI)
    #====================================================================

    def defopt (self, name, value, opt=None, more=None,
                callback=None, prompt=None, doc=None,
                trace=False):
        """
        Encapsulation of self._OM.define(). It allows central completion
        of the option name, and the interaction with constructor kwargs.
        If the option name is a field in self._kwargs[default], the default
        value will be changed. If it is a field in self._kwargs[insist], the
        option value will be changed, and the option itself will be disabled.
        """
        return self._OMI.defopt (name, value, opt=opt, more=more,
                                 callback=callback, prompt=prompt, doc=doc,
                                 trace=trace)

    #.............................................................

    def optname (self, name, trace=False):
        """Convert an option name to its OM name by prepending self._submenu.
        """ 
        return self._OMI.optname (name, trace=trace)

    #.............................................................

    def optval (self, name, test=None, trace=False):
        """Get the value of the specified option, after converting it to its OM name.
        If test is specified, modify the value, if necessary.
        """
        return self._OMI.optval (name, test=test, trace=trace)

    #.............................................................

    def has_option (self, name):
        """Check the existence of the specified option, after converting it to its OM name.
        """
        return self._OMI.has_option (name)
        
    #.............................................................

    def set_value (self, name, value):
        """Set the value of the specified option, after converting it to its OM name.
        """
        return self._OMI.set_value (name, value)





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
        self._OMI.defopt('unop', 'Cos',
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
        unop = self._OMI.optval('unop', test=test)

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
    rootnode = grt.grow(ns, node, trace=False)
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
        grt = Growth('bbb', OM=OM, extra=56)
        grt.display('initial')

    if 1:
        grt = GrowthTest('bbb', OM=OM, extra=78)
        grt.display('initial')

    if 1:
        grt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        test = dict()
        grt.grow(ns, node, test=test, trace=False)

    if 1:
        grt.display('final', OM=True, full=True)

    if 1:
        grt.print_tree(recurse=1)
        grt.print_tree(recurse=2)
        grt.print_tree(recurse=3)

    if 0:
        grt._OM.showtree()

#===============================================================


# file: ../JEN/control/OMInterface.py

# History:
# - 24sep2007: creation (from Growth.py)

# Description:

"""The OMInterface class provides some convenient interface methods between
an object and the OptionManager (which is usually shared with other objects).
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

# from copy import deepcopy

#======================================================================================

class OMInterface (object):
    """The OMInterface class is a specific interface between an object and its
    OptionManager, which is usually shared with other objects.
    """

    def __init__(self, quals=None,
                 name='OMInterface',
                 submenu='compile',
                 slavemenu=None,
                 OM=None, namespace=None,
                 **kwargs):

        # For reporting only:
        self._frameclass = 'Grunt.'+name

        # Make self.name and self._submenu:
        self.make_name_and_submenu (name, submenu, quals,
                                    slavemenu=slavemenu)

        # Extra keyword arguments may be supplied to the constructor.
        self._kwargs = kwargs
        if not isinstance(self._kwargs, dict):
            self._kwargs = dict()
        
        #................................................................

        # Normally, an object like a ParmGroup will define a number of
        # standard options, with standard defaults. When creating such
        # an object, the default values may be modified by providing
        # a named field in the 'default' argument of the constructor
        # (or even as regular keyword arguments with the same name!).
        # The constructor should then pass this to its self._OMInterface,
        # (i.e. this one). This will then modify the 'standard' default
        # value given in .defopt(). This value may then be modified by
        # the user, which is the value that stored in the .tdlconf file.
        # It is also the value that is used by the OM 'reset' operation.

        self._default = dict()
        if self._kwargs.has_key('default') and isinstance(self._kwargs['default'],dict):
            self._default = self._kwargs['default']
        else:
            ignore = ['toggle_box']
            for key in self._kwargs.keys():
                if key in ignore:
                    pass
                elif isinstance(self._kwargs[key],dict):
                    pass
                else:
                    self._default[key] = self._kwargs[key]

        # An option default value may be set to a constant by providing
        # a named field in the 'constant' argument of the constructor.
        # The constructor should then pass this to its self._OMInterface,
        # (i.e. this one) which will deal with it. See .defopt()

        self._constant = dict()
        if self._kwargs.has_key('constant') and isinstance(self._kwargs['constant'],dict):
            self._constant = self._kwargs['constant']

        #................................................................

        # Control of toggle-box(es) before menu(s)
        self._kwargs.setdefault('toggle_box', False)
        self._toggle_box = False
        self._toggle_group = []

        #................................................................

        # The OptionManager may be external:
        if isinstance(OM, OptionManager.OptionManager):
            self._OM = OM                          
            self._external_OM = True
        else:
            self._external_OM = False
            self._OM = OptionManager.OptionManager(self.name, namespace=namespace)
                                                   # parentclass=self._frameclass)

        # Finished:
        return None

    #--------------------------------------------------------------------

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the actual TDL menu of compile-time options.
        NB: This call is not needed with an external OptionManager,
        since the menu will be part of that of the parent object.
        """
        if not self._external_OM:
            self._OM.make_TDLCompileOptionMenu(**kwargs)
        return True
    

    #--------------------------------------------------------------------

    def make_name_and_submenu (self, name=None, submenu=None, quals=None,
                               slavemenu=None):
        """
        Helper function that is called from __init__().
        Make self.name by appending any qualifiers to name.
        Make self._shortname from the capitals of self.name.
        Make self._submenu by appending self.name to submenu.
        """
        # The use of self.name is consistent with Meow/Parameterization...
        self.name = name

        # Make a short (but recognisable) menu-name, to avoid clutter:
        ss = ''
        ncmax = 10
        if len(name)<ncmax:          # name is short already
            ss = name                # use it entirely
        else:
            # Make the short name from all chars until the 2nd capital,
            # followed by the subsequent capitals and numbers.
            # So the short name will look like: TApplyU or DemoR
            capitals = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            numbers = '01234567890'
            capcount = 0
            subcount = 0
            for char in name:
                if (char in capitals):
                    capcount += 1
                    ss += char
                    subcount = 0
                elif (char in numbers):
                    ss += char
                    subcount = 0
                elif capcount==2:
                    ss += char
                elif subcount==0:
                    ss += char
                    subcount += 1
                # print '-',char,capcount,subcount,'->',ss
            if len(ss)==0:
                ss = name[:ncmax]
        self._shortname = ss
        
        # Qualifiers allow the same OMInterface to be used multiple
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

        # If defopt(slavemenu=True), self._slavemenu will be used
        self._slavemenu = slavemenu
        if isinstance(self._slavemenu, str):
            self._slavemenu = slavemenu+'.'+self._shortname
        return True


    #--------------------------------------------------------------------

    def change_submenu(self, submenu, trace=True):
        """Not yet implemented: Change the submenu, and redefine the options.
        This is done when an existing OMInterface object is attached to another one.
        """
        # NB: What about the options that have already been defined?
        #     Should they be eradicated from the OM?
        # self._submenu = submenu+'.'+self.name
        # self.define_compile_options()
        # NB: What about options that are defined in other routines?
        return True


    #===============================================================

    def get_local_option_names(self, submenu=True, slavemenu=False):
        """Get a list of the (full) OM names of the options that
        are specific to this OM interface object"""
        ss = []
        for name in self._OM.order:
            # print '---',name
            if submenu:
                if self._submenu in name:
                    ss.append(name)
            if slavemenu and self._slavemenu:
                if self._slavemenu in name:
                    ss.append(name)
        # print '-> ss =',ss,'\n'
        return ss


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = self._frameclass+':'
        if not self.name==self._shortname:
            ss += ' ('+self._shortname+')'
        ss += ' shortname='+str(self._shortname)
        ss += ' submenu='+str(self._submenu)
        if self._slavemenu:
            ss += ' (slavemenu='+str(self._slavemenu)+')'
        return ss



    def display(self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble('OMI', level=level, txt=txt)
        #...............................................................
        print prefix,'  * kwargs ('+str(len(self._kwargs.keys()))+'):'
        for key in self._kwargs.keys():
            print prefix,'    - '+key+' = '+str(self._kwargs[key])            
        print prefix,'  * external defaults ('+str(len(self._default.keys()))+'):'
        for key in self._default.keys():
            print prefix,'    - '+key+' = '+str(self._default[key])            
        print prefix,'  * external constants ('+str(len(self._constant.keys()))+'):'
        for key in self._constant.keys():
            print prefix,'    - '+key+' = '+str(self._constant[key])            
        #...............................................................
        keys = self.get_local_option_names(submenu=True, slavemenu=False)
        print prefix,'  * local submenu options ('+str(len(keys))+'):'
        if full or len(keys)<20:
            for key in keys:
                rr = self._OM.optrec[key]
                value = self._OM[key]
                s = str(value)
                if not rr['default']==value: s += '  (default='+str(rr['default'])+')'            
                print prefix,'    - '+key+' = '+s
        #...............................................................
        keys = self.get_local_option_names(submenu=False, slavemenu=True)
        print prefix,'  * local slavemenu options ('+str(len(keys))+'):'
        if full or len(keys)<20:
            for key in keys:
                rr = self._OM.optrec[key]
                value = self._OM[key]
                s = str(value)
                if not rr['default']==value: s += '  (default='+str(rr['default'])+')'            
                print prefix,'    - '+key+' = '+s
        #...............................................................
        print prefix,'  * has toggle box = '+str(self._toggle_box)
        print prefix,'  * toggle group ('+str(len(self._toggle_group))+')'
        for g in self._toggle_group:
            print prefix,'     - '+str(g.oneliner())
        #...............................................................
        print prefix,'  * '+self._OM.oneliner()
        print prefix,'  * external OptionManager: '+str(self._external_OM)
        if not self._external_OM:
            if OM and full: self._OM.display(full=False, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)



    #--------------------------------------------------------------------------

    def display_value(self, v, name='<name>', prefix='*'):
        """Helper function to display a value in .display()"""
        print prefix,'  * '+str(name)+' type = '+str(type(v)),
        midfix = '     -' 
        if is_node(v):
            print str(v)
            # self.display_subtree(v) 
        elif getattr(v, 'oneliner', None):
            print
            print prefix,midfix,v.oneliner()
        elif isinstance(v, (list,tuple)):
            print ' (len='+str(len(v))+')'
            for (k,v1) in enumerate(v):
                if getattr(v1, 'oneliner', None):
                    print prefix,midfix,k,':',v1.oneliner()
        elif isinstance(v, dict):
            print ' keys: '+str(v.keys())
        else:
            print '=',str(v)
        return True

    #-------------------------------------------------------------------------

    def display_preamble(self, prefix='OMI', level=0, txt=None):
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
    # Some service(s) available to all classes derived from OMInterface:
    #====================================================================

    def print_tree(self, recurse=10, trace=False):
        """Display the entire tree
        """
        print '\n** ',self.name,': print_tree(recurse=',recurse,'):'
        self._OM.print_tree(recurse=recurse)
        print
        return True


    #====================================================================
    # Helper functions for access to options:
    #====================================================================

    def optname (self, name, slavemenu=False, trace=False):
        """Convert an option name to its OM name by prepending self._submenu.
        If slavemenu==True, use self._slavemenu, rather than self._submenu.
        """
        menu = self.menuname (slavemenu=slavemenu)
        OM_name = menu+'.'+name
        if trace:
            print '** optname(',name,'): -> ',OM_name
        return OM_name


    #.............................................................

    def menuname (self, postfix=None, slavemenu=False):
        """Get the specified menu name, if available"""
        if not slavemenu:
            menu = self._submenu
        elif not self._slavemenu:
            raise ValueError,'** no slavemenu defined'
        else:
            menu = self._slavemenu
        if isinstance(postfix,str):
            if postfix[0]=='.':
                menu += postfix
            else:
                menu += '.'+postfix
        return menu

    #.............................................................

    def defopt (self, name, default, insist='<unset>',
                opt=None, more=None,
                callback=None, prompt=None, doc=None,
                slavemenu=False,
                trace=False):
        """Encapsulation of self._OM.define(). It allows central completion
        of the option name, and the interaction with constructor kwargs.
        - If the option name is a field in self._default, the default value
        will be changed.
        - If it is a field in self._constant, the default value will be changed,
        and the option itself will be disabled (so it cannot be changed).
        See the constructor for the provenance of self._default and self._constant.
        """
        was = default
        if name in self._default.keys():
            new = self._default[name]
            if isinstance(new, dict):
                pass                        # issue a warning message...?
            else:
                default = new
                if trace:
                    print '\n** .defopt(',name,'): =',was,'->',default,'\n'
            
        disable = None
        if name in self._constant.keys():
            disable = True
            default = self._constant[name]
            insist = default
            if trace:
                print '\n** .defopt(',name,'): =',was,'->',default,'\n'

        self._OM.define(self.optname(name, slavemenu=slavemenu),
                        default, insist=insist, opt=opt, more=more,
                        callback=callback, prompt=prompt, doc=doc,
                        disable=disable)
        return True

    #.............................................................

    def optval (self, name, slavemenu=False, test=None, trace=False):
        """Get the value of the specified option,
        after converting it to its OM name.
        If test is specified, modify the value, if necessary.
        """
        OM_name = self.optname(name, slavemenu=slavemenu, trace=trace)
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

    def has_option (self, name, slavemenu=False):
        """Check the existence of the specified option,
        after converting it to its OM name.
        """
        OM_name = self.optname(name, slavemenu=slavemenu)
        return self._OM.has_option(OM_name)
        
    #.............................................................

    def set_value (self, name, value, slavemenu=False):
        """Set the value of the specified option,
        after converting it to its OM name.
        """
        if self.has_option(name, slavemenu=slavemenu):
            OM_name = self.optname(name, slavemenu=slavemenu)
            if self._OM.option[OM_name]:
                self._OM.set_value(OM_name, value)
        return True

    #.............................................................

    def hide (self, hide=True, slavemenu=False):
        """Hide/unhide the specified menu"""
        menu = self.menuname (slavemenu=slavemenu)
        self._OM.hide(menu, hide=hide)
        return True

    #.............................................................

    def select (self, select=True, slavemenu=False):
        """Select/deselect the specified menu"""
        menu = self.menuname (slavemenu=slavemenu)
        self._OM.set_menurec(menu, selected=select)
        return True

    #.............................................................

    def is_selected (self, slavemenu=False):
        """Check whether the specified menu is selected"""
        menu = self.menuname (slavemenu=slavemenu)
        return self._OM.is_selected(menu)

    #.............................................................

    def set_menurec (self, postfix=None,
                     prompt=None, stare=None, descr=None,
                     toggle=None, callback=None, selected=None,
                     slavemenu=False,
                     trace=False):
        """Set values in the specified menurec"""
        menu = self.menuname (postfix=postfix, slavemenu=slavemenu)
        return self._OM.set_menurec(menu, prompt=prompt,
                                    stare=stare, descr=descr,
                                    toggle=toggle, callback=callback,
                                    selected=selected,
                                    trace=trace)

    #--------------------------------------------------------------------

    def make_toggle_box (self, postfix=None, slavemenu=False,
                         select=False, create=True):
        """
        Make a toggle box in front of the specified menu, if required.
        If create==True, make sure that the menurec exists first.
        """
        menu = self.menuname (postfix=postfix, slavemenu=slavemenu)
        # print '\n** .make_toggle_box(',postfix,slavemenu,'): menu =',menu, self._toggle_box, self._kwargs['toggle_box']
        if not self._toggle_box:
            if self._kwargs['toggle_box']:
                self._toggle_box = True
                if create and not self._OM.menurec.has_key(menu): 
                    self.defopt('toggle_box_placeholder',-123)
                return self._OM.set_menurec(menu, toggle=True,
                                            selected=select,
                                            callback=self._callback_toggle)

    #....................................................................

    def _callback_toggle (self, selected):
        """Called whenever the toggle widget before the menu is toggled"""
        trace = False
        if trace:
            print '\n** _callback_toggle(',selected,'):',self.name
        # Special case: if the parent object is a member of a toggle group,
        # one, and only one member of this group must be selected always.
        # This means that it is not possible to deselect the currently
        # selected one, so 'selected' must always be true:
        if len(self._toggle_group)>0:
            selected = True
            # NB: A toggle group contains OMI objects!
            for OMI in self._toggle_group:
                if trace: print ' --',OMI.oneliner()
                OMI.select(False)                   # deselect all group members
        self.select(selected)                       # (de)select itself
        if trace: print '----'
        return True

    #.............................................................

    def toggle_group (self, append=None, reset=False, trace=False):
        """Interaction with the toggle-group of this object. It contains
        a list of other Growth objects, of which only one at a time may
        be selected. See also _callback_toggle().
        """
        if reset:
            self._toggle_group = []
        if append:
            # Append one or more OMI objects (!) to the toggle group
            if not isinstance(append, list): append = [append]
            for g in append:                       # all member objects
                if not g._OMI==self:
                    if not g._OMI in self._toggle_group:     
                        self._toggle_group.append(g._OMI)  
                if not self in g._OMI._toggle_group:     
                    g._OMI._toggle_group.append(self)     
        return self._toggle_group



    #====================================================================
    # Fill with test data:
    #====================================================================

    def test (self, trace=False):
        """Fill the object with test data"""
        self.defopt('a',45, more=float)
        self.defopt('b',49, more=float)
        self.defopt('b',49, slavemenu=True, more=float)
        return True
    

#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


omi = None
if 0:
    omi = OMInterface(quals='hjk',
                      name='Gphase',
                      submenu='compile.submenu',
                      slavemenu='compile.solvermenu',
                      default=dict(a=21, c=6),
                      constant=dict())
                      # constant=dict(a=334))
    omi.test()
    omi._OM.make_TDLCompileOptionMenu()
    # omi.display()


def _define_forest(ns):

    global omi
    if not omi:
        omi = OMInterface(quals=[1,2],
                          submenu='compile.submenu',
                          slavemenu='compile.solvermenu',
                          default=dict(a=21, c=6),
                          constant=dict())
        omi.test()
        omi._OM.make_TDLCompileOptionMenu()

    cc = []

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent):
    """Execute the forest with the specified options (domain etc),
    starting at the named node"""
    return xtor.execute(mqs, parent)
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the OMInterface object"""
    omi.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the OMInterface object"""
    omi.display('_tdl_job', full=True)
       
def _tdl_job_print_tree (mqs, parent):
    """Print the tree"""
    omi.print_tree()
       


       










#===============================================================
# Test routine:
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    OM = None
    if 1:
        OM = OptionManager.OptionManager()

    if 1:
        omi = OMInterface('bbb', OM=OM,
                          submenu='compile.submenu',
                          slavemenu='compile.solvermenu',
                          default=dict(a=21, c=6),
                          constant=dict())
        omi.test()
        omi.display('initial')


    if 1:
        omi.display('final', OM=True, full=True)


#===============================================================


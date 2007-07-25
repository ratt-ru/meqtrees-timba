# file: ../Grunt/OptionsManager.py

# History:
# - 24jul2007: creation

# Description:

# The Grunt OptionsManager class manages the options of a module.


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

# from copy import deepcopy

#======================================================================================

class OptionsManager (object):
    """The Grunt OptionsManager class manages the options of a module"""

    def __init__(self, parent='<parent>', namespace=None):


        self._parent = parent
        self._frameclass = 'Grunt.OptionsManager'

        self.tdloption_namespace = namespace

        self._TDLCompileOptionsMenu = None   
        self._TDLCompileOptionsSubmenu = dict()   
        self._TDLCompileOption = dict()

        self._options_submenu = dict()
        self._option_record = dict()

        # Finished:
        return None


    #-----------------------------------------------------------------------------

    def __getitem__ (self, key):
        """Get the current value of the specified option"""
        if not key[0]=='_':
            return getattr(self, '_'+key)
        return getattr(self, key)

    #-----------------------------------------------------------------------------

    def defopt (self, key, value, submenu=None,
                prompt=None, opt=None, more=None, doc=None,
                callback=None, trace=True):
        """Helper function to deal with (TDL) options of this class
        in an organized way. """

        # A range of options may be specified by a dict:
        if isinstance(value, dict):
            if not isinstance(submenu, str): submenu = key
            for key in value.keys():
                self.defopt(key, value[key], submenu=submenu)
        
        else:
            key = '_'+key
            noexist = -1.234567899
            if not getattr(self, key, noexist)==noexist:
                s = '** clash between attribute and option key: '+key
                raise ValueError,s
            setattr (self, key, value)                      # working values
            self._option_record[key] = dict(reset=value, doc=doc, prompt=prompt,
                                     opt=opt, more=more, callback=callback)
            if not isinstance(submenu, str): submenu = '*'
            if isinstance(submenu, str): 
                self._options_submenu.setdefault(submenu, [])
                self._options_submenu[submenu].append(key)
            if trace:
                print '  ** defopt(',key,value,submenu,')'
        return True

    #---------------------------------------------------------------

    def namespace(self, prepend=None, append=None):
        """Return the namespace string (used for TDL options etc).
        If either prepend or apendd strings are defined, attach them.
        NB: Move to the OptionsManager class?
        """
        if prepend==None and append==None:
            return self.tdloption_namespace                    # just return the namespace
        # Include the namespace in a string:
        ss = ''
        if isinstance(prepend, str): ss = prepend+' '
        if self.tdloption_namespace:
            ss += '{'+str(self.tdloption_namespace)+'}'
        if isinstance(append, str): ss += ' '+append
        return ss
    


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.OptionsManager:'
        ss = self._frameclass+':'
        ss += '  parent='+str(self._parent)
        ss += '  namespace='+str(self.tdloption_namespace)
        return ss


    def display(self, txt=None, full=False, recurse=3):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print '  * (txt='+str(txt)+')'
        #...............................................................
        if full:
            print '  * option definition(s): '
            for key in self._option_record.keys():
                print '    - '+key+': '+str(self._option_record[key])
        #...............................................................
        print '  * option value(s): '
        for key in self._option_record.keys():
            rr = self._option_record[key]
            ss = ' = '+str(getattr(self, key))
            ss += ' ('+str(self[key])+')'
            ss += '  reset='+str(rr['reset']) 
            if not self._TDLCompileOption.has_key(key):
                ss += '   (-)'
            else:
                oo = self._TDLCompileOption[key]
                noexist = -1.23456789
                if getattr(oo, 'value', noexist)==noexist:
                    print '    - '+str(key)+': '+str(self._TDLCompileOption[key])
                else:
                    value = self._TDLCompileOption[key].value
                    ss += '  TDLOption='+str(value)
            print '    - '+key+': '+ss
        #...............................................................
        print '  * submenu(s): '
        for key in self._options_submenu.keys():
            print '    - '+key+': '+str(self._options_submenu[key])
        #..............................................................
        print '  * TDLCompileOptionsMenu: '+str(self._TDLCompileOptionsMenu)
        print '  * TDLCompileOptionsSubmenu(s): '
        for key in self._TDLCompileOptionsSubmenu.keys():
            print '    - '+key+': '+str(self._TDLCompileOptionsSubmenu[key])
        #...............................................................
        print '**\n'
        return True




    #===================================================================
    # TDLOptions:
    #===================================================================

    def TDLMenu(self, key=None):
        """Return the specified TDL (sub) menu"""
        if not isinstance(key,str):
            return self._TDLCompileOptionsMenu
        elif self._TDLCompileOptionsSubmenu.has_key(key):
            return self._TDLCompileOptionsSubmenu[key]
        return None
        
    def TDLOption(self, key=None):
        """Return the specified TDL option"""
        if not key[0]=='_':
            key = '_'+key
        if self._TDLCompileOption.has_key(key):
            return self._TDLCompileOption[key]
        return None
        

    #---------------------------------------------------------------------

    def show(self, key=None, show=True):
        """Show/hide the specified menu/option."""
        return self.hide(key=key, hide=(not show))


    def hide(self, key=None, hide=True):
        """Hide/unhide the specified menu/option."""
        if isinstance(key,bool):
            if self._TDLCompileOptionsMenu:
                self._TDLCompileOptionsMenu.hide(key)
        elif not isinstance(key,str):
            if self._TDLCompileOptionsMenu:
                self._TDLCompileOptionsMenu.hide(hide)
        elif self._TDLCompileOptionsSubmenu.has_key(key):
            if self._TDLCompileOptionsSubmenu[key]:
                self._TDLCompileOptionsSubmenu[key].hide(hide)
        elif self._TDLCompileOption.has_key(key):
            if self._TDLCompileOption[key]:
                self._TDLCompileOption[key].hide(hide)
        return True
        
    #---------------------------------------------------------------------

    def enable(self, key=None, enable=True):
        """Enable/disable the specified menu/option."""
        return self.disable (key=key, disable=(not enable))

    def disable(self, key=None, disable=True):
        """Disable/enable the specified menu/option."""
        if isinstance(key,bool):
            if self._TDLCompileOptionsMenu:
                self._TDLCompileOptionsMenu.disable(key)
        elif not isinstance(key,str):
            if self._TDLCompileOptionsMenu:
                self._TDLCompileOptionsMenu.disable(disable)
        elif self._TDLCompileOptionsSubmenu.has_key(key):
            if self._TDLCompileOptionsSubmenu[key]:
                self._TDLCompileOptionsSubmenu[key].disable(disable)
        elif self._TDLCompileOption.has_key(key):
            if self._TDLCompileOption[key]:
                self._TDLCompileOption[key].disable(disable)
        return True
        


    #=================================================================
    # Option lists:
    #=================================================================

    def TDLCompileOptionsMenu (self, insert=None, **kwargs):
        """Generic function for interaction with its TDLCompileOptions menu."""
        if not isinstance(kwargs, dict): kwargs = dict()
        kwargs.setdefault('trace', False)
        if not self._TDLCompileOptionsMenu:        # create the menu only once
            # First the single items (if any) of the main menu: 
            oolist = self.TDLCompileOptions(**kwargs)
            # Then the various submenus (if any):
            if isinstance(insert, list):
                oolist.extend(insert)
            # Optional: insert a given list of external items:
            kwargs.setdefault('reset', True)
            # Optional (but last): Include a 'reset' menuitem
            if kwargs['reset']:
                oolist.append(self.make_reset_item())
            prompt = self.namespace(prepend='options for: ')
            self._TDLCompileOptionsMenu = TDLCompileMenu(prompt, *oolist)
        return self._TDLCompileOptionsMenu

    #---------------------------------------------------------------------

    def TDLCompileOptions(self, **kwargs):
        """Automatic generation of a list of option objects."""
        if not isinstance(kwargs, dict): kwargs = dict()
        oolist = self.make_submenu('*')
        for key in self._options_submenu.keys():
            if not key=='*':
                oo = self.make_submenu(key)
                oolist.append(oo)
        return oolist
    

    def make_submenu (self, submenu):
        """Automatic generation of an option submenu"""
        keys = self._options_submenu[submenu]
        if not self._TDLCompileOptionsSubmenu.has_key(submenu):
            oolist = []
            for key in keys:
                if not self._TDLCompileOption.has_key(key):
                    rr = self._option_record[key]
                    prompt = rr['prompt'] or key
                    doc = rr['doc'] or '<doc>'
                    opt = [getattr(self,key)]
                    if isinstance(rr['opt'],list):
                        opt.extend(rr['opt'])
                    more = rr['more'] or float                # type(opt[0])
                    oo = TDLOption(key, prompt, opt, more=more,
                                   doc=doc, namespace=self)
                    if not submenu=='*':
                        oo.when_changed(self._callback_submenu)
                    if rr['callback']:
                        oo.when_changed(rr['callback'])
                    self._TDLCompileOption[key] = oo
                oolist.append(self._TDLCompileOption[key])

            # Make the submenu (if required):
            if submenu=='*':
                return oolist
            elif len(oolist)==0:
                return oolist                     #....?
            else:
                prompt = 'submenu: '+submenu
                om = TDLCompileMenu(prompt, *oolist)
                self._TDLCompileOptionsSubmenu[submenu] = om
                self._callback_submenu()
        return self._TDLCompileOptionsSubmenu[submenu]
            
            
    #.....................................................................

    def _callback_submenu(self, dummy=None):
        """Function called whenever any TDLOption in a submenu changes.
        It changes the summary string of the submenu header."""
        for submenu in self._options_submenu.keys():
            if self._TDLCompileOptionsSubmenu.has_key(submenu):
                summ = '('
                first = True
                keys = self._options_submenu[submenu]
                for key in keys:
                    if self._TDLCompileOption.has_key(key):
                        value = self._TDLCompileOption[key].value
                        if not first: summ += ','
                        first = False
                        if value==None:
                            summ += '-' 
                        elif isinstance(value,str):
                            summ += 'str'
                        else:
                            summ += str(value)
                summ += ')'
                self._TDLCompileOptionsSubmenu[submenu].set_summary(summ)
        return True

        
    #.....................................................................

    def set_TDLOption (self, key, value):
        """Helper function to change the value of the specified option.
        If necessary, it calls the relevant callback function."""
        print '\n** set_TDLOption(',key,value,'):'
        if self._TDLCompileOption.has_key(key):
            self._TDLCompileOption[key].set_value(value)
            setattr(self, key, value)
        return True



    #---------------------------------------------------------------------
    # Functions dealing with resetting option values:
    #---------------------------------------------------------------------

    def make_reset_item (self, slave=False):
        """...."""
        key = 'opt_reset'
        if not self._TDLCompileOption.has_key(key):
            doc = """If True, reset all options to their original default values.
            (presumably these are sensible values, supplied by the module designer.)"""
            prompt = self._parent+':  reset to original defaults'
            oo = TDLOption(key, prompt, [False, True], doc=doc, namespace=self)
            oo.when_changed(self._callback_reset)
            if slave: oo.hide()
            self._TDLCompileOption[key] = oo
        return self._TDLCompileOption[key]


    #.....................................................................

    def _callback_reset(self, reset):
        """Function called whenever TDLOption _reset changes."""
        if reset and self._TDLCompileOptionsMenu:
            self.reset_options(trace=True)
            key = 'opt_reset'
            self._TDLCompileOption[key].set_value(False, callback=False,
                                                  save=True)
        return True


    #.....................................................................

    def reset_options(self, trace=False):
        """Helper function to reset the TDLCompileOptions and their local
        counterparts to the original default values (in self._reset). 
        """
        if trace:
            print '\n** _reset_options(): ',self.oneliner()
        for key in self._option_record.keys():
            was = getattr(self,key)
            new = self._option_record[key]['reset']
            setattr(self, key, new)
            if self._TDLCompileOption.has_key(key):
                self._TDLCompileOption[key].set_value(new, save=True)
                new = self._TDLCompileOption[key].value
                if trace:
                    print ' -',key,':',was,' -> ',getattr(self,key),
                    if not new==getattr(self,key):
                        print '** TDLOption =',new,'!?',
            else:
                if trace: print ' -',key,':',was,' -> ',getattr(self,key),
            if trace:
                if not new==was: print '           ** changed **',
                print
        if trace: print
        return True
        

    #=====================================================================
    # Test-routine(s)
    #=====================================================================

    def test(self):
        """..."""
        # Deal with the (TDL) options in an organised way:
        # The various solver constraint options are passed by dict():
        constraint = dict()
        if True:
            # Make sure that some constraint options are always there:
            constraint.setdefault('min', None)
            constraint.setdefault('max', None)
        if True:
            # Temporary: add some constraint options for testing
            constraint.setdefault('sum', 0.1)
            constraint.setdefault('product', -1.1)
            constraint.setdefault('ignore', 0)
        self.defopt('mode', 'solve', opt=['nosolve','solve','simulate'], more=str,
                    doc='The rain in Spain....', callback=self._callback_mode)
        self.defopt('default', 12.9, more=float)
        self.defopt('simuldev', 'expr', more=str)
        self.defopt('tiling', None, submenu='span', opt=[1,2,4,8], more=int)
        self.defopt('time_deg', 1, submenu='span', more=int)
        self.defopt('freq_deg', 2, submenu='span', more=int)
        self.defopt('constraint', constraint, submenu='constraint')
        return True
        
    def _callback_mode (self, mode):
        print '** callback_mode(',mode,')'
        return True



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================

if 0:
    om = OptionsManager()
    om.test()
    om.TDLCompileOptionsMenu()


def _define_forest(ns):

    cc = []

    om.display('final', full=True)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    return True



#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,0,2000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       










#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()


    if 1:
        om = OptionsManager(parent='test')
        om.display('initial')
        om.test()

    if 1:
        om.TDLCompileOptionsMenu(slave=False)

    if 1:
        om.display('final')



#===============================================================


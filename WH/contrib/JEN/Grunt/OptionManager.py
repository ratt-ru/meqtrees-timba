# file: ../Grunt/OptionManager.py

# History:
# - 24jul2007: creation

# Description:

# The Grunt OptionManager class manages the options of a module.


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

class OptionManager (object):
    """The Grunt OptionManager class manages the options of a module"""

    def __init__(self, parent='<parent>', namespace=None):

        self.parent = parent
        self.frameclass = 'Grunt.OptionManager'

        # This field is expected by OMS:
        self.tdloption_namespace = namespace

        self.TDLCompileOptionMenu = None   
        self.TDLCompileOptionSubmenu = dict()   
        self.TDLCompileOption = dict()

        self.TDLRuntimeOptionMenu = None   
        self.TDLRuntimeOptionSubmenu = dict()   
        self.TDLRuntimeOption = dict()

        # Named submenus are defined by a list of option keys:
        self.submenu_compile = dict()
        self.submenu_runtime = dict()

        # Option definition records:
        self.optrec_compile = dict()
        self.optrec_runtime = dict()

        # Finished:
        return None


    #-----------------------------------------------------------------------------

    def __getitem__ (self, key):
        """Get the current value of the specified option (key).
        Note that, internally, the keys are prepended with '_'.
        This should be the ONLY way in which an option value is obtained
        from the OptionManager. This makes sure that the module can also be
        used standalone, i.e. without any TDLOptions/menus."""
        ukey = '_'+key
        if True:
            # Make sure that the internal value is equal to the current value
            # of the TDLOption.value (if it exists).
            # For some reason, this does not happen automatically when the
            # TDLOption value is modified by the user (it used too...).
            if self.TDLCompileOption.has_key(key):
                setattr(self, ukey, self.TDLCompileOption[key].value)
        return getattr(self, ukey)

    #-----------------------------------------------------------------------------

    def modopt (self, key, time='compile', **pp):
        """Helper function to modify field(s) of an existing (key) optrec,
        which has been defined earlier with .defopt(key, ...)."""
        if time=='runtime':
            rr = self.optrec_runtime[key]
        else:
            rr = self.optrec_compile[key]
        if not isinstance(pp, dict): pp = dict()
        pp.setdefault('trace',False)
        keys = ['value','opt','more','prompt','doc','callback']
        for key in keys:
            if pp.has_key(key):
                rr[key] = pp[key]
                # if key=='opt']: self.set_option_list(key, rr[key])
        return True

    #-----------------------------------------------------------------------------

    def defopt (self, key, value, submenu=None, time='compile',
                prompt=None, opt=None, more=None, doc=None,
                callback=None, trace=True):
        """Helper function to deal with (TDL) options of this class
        in an organized way. """

        # A range of options may be specified by a dict:
        if isinstance(value, dict):
            if not isinstance(submenu, str): submenu = key
            for key in value.keys():
                self.defopt(key, value[key], submenu=submenu, time=time)
        
        else:
            ukey = '_'+key                                   # internal name
            noexist = -1.234567899
            if not getattr(self, ukey, noexist)==noexist:
                # NB: This should never happen....
                s = '** clash between attribute and option key: '+ukey
                raise ValueError,s
            setattr (self, ukey, value)                      # working values
            rr = dict(reset=value, doc=doc, prompt=prompt,
                      opt=opt, more=more, callback=callback)
            if not isinstance(submenu, str): submenu = '*'

            if time=='runtime':
                self.optrec_runtime[key] = rr
                if isinstance(submenu, str): 
                    self.submenu_runtime.setdefault(submenu, [])
                    self.submenu_runtime[submenu].append(key)
            else:
                self.optrec_compile[key] = rr
                if isinstance(submenu, str): 
                    self.submenu_compile.setdefault(submenu, [])
                    self.submenu_compile[submenu].append(key)

            if trace:
                print '  ** defopt(',key,ukey,value,submenu,time,')'
        return True


    #---------------------------------------------------------------

    def namespace(self, prepend=None, append=None):
        """Return the namespace string (used for TDL options etc).
        If either prepend or apendd strings are defined, attach them.
        NB: Move to the OptionManager class?
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
        # ss = 'Grunt.OptionManager:'
        ss = self.frameclass+':'
        ss += '  parent='+str(self.parent)
        ss += '  namespace='+str(self.tdloption_namespace)
        return ss


    def display(self, txt=None, full=False, recurse=3):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print '  * (txt='+str(txt)+')'
        #...............................................................
        if full:
            print '  * CompileOption definition(s): '
            for key in self.optrec_compile.keys():
                print '    - '+key+': '+str(self.optrec_compile[key])
            print '  * RuntimeOption definition(s): '
            for key in self.optrec_runtime.keys():
                print '    - '+key+': '+str(self.optrec_runtime[key])
        #...............................................................
        print '  * CompileOption value(s): '
        for key in self.optrec_compile.keys():
            rr = self.optrec_compile[key]
            value = self[key]
            ss = ' = '+str(value)
            if not value==rr['reset']:
                ss += '    (reset='+str(rr['reset'])+'!)' 
            if not self.TDLCompileOption.has_key(key):
                ss += '   (-)'
            else:
                oo = self.TDLCompileOption[key]
                noexist = -1.23456789
                if getattr(oo, 'value', noexist)==noexist:
                    print '    - '+str(key)+': '+str(self.TDLCompileOption[key])
                else:
                    TDLvalue = self.TDLCompileOption[key].value
                    if not value==TDLvalue:
                        ss += '    (TDLOption.value='+str(TDLvalue)+'!)'
            print '    - '+key+ss
        #...............................................................
        print '  * RuntimeOption value(s): '
        for key in self.optrec_runtime.keys():
            rr = self.optrec_runtime[key]
            value = self[key]
            ss = ' = '+str(value)
            if not value==rr['reset']:
                ss += '    (reset='+str(rr['reset'])+'!)'
            if not self.TDLRuntimeOption.has_key(key):
                ss += '   (-)'
            else:
                oo = self.TDLRuntimeOption[key]
                noexist = -1.23456789
                if getattr(oo, 'value', noexist)==noexist:
                    print '    - '+str(key)+': '+str(self.TDLRuntimeOption[key])
                else:
                    TDLvalue = self.TDLRuntimeOption[key].value
                    if not value==TDLvalue:
                        ss += '    (TDLOption.value='+str(TDLvalue)+'!)'
            print '    - '+key+ss
        #...............................................................
        print '  * submenu(s): '
        for key in self.submenu_compile.keys():
            print '    - (compile) '+key+': '+str(self.submenu_compile[key])
        for key in self.submenu_runtime.keys():
            print '    - (runtime) '+key+': '+str(self.submenu_runtime[key])
        #..............................................................
        print '  * TDLCompileOptionMenu: '+str(self.TDLCompileOptionMenu)
        print '  * TDLCompileOptionSubmenu(s): '
        for key in self.TDLCompileOptionSubmenu.keys():
            print '    - '+key+': '+str(self.TDLCompileOptionSubmenu[key])
        print '  * TDLRuntimeOptionMenu: '+str(self.TDLRuntimeOptionMenu)
        print '  * TDLRuntimeOptionSubmenu(s): '
        for key in self.TDLRuntimeOptionSubmenu.keys():
            print '    - '+key+': '+str(self.TDLRuntimeOptionSubmenu[key])
        #...............................................................
        print '**\n'
        return True




    #===================================================================
    #===================================================================

    def TDLMenu (self, key=None, time=None, severe=False, trace=False):
        """Return the specified (key) TDL(sub)menu object (or None).
        If time==None (i.e. not specified), check for a compile menu first,
        and then for a runtime menu.
        If the specified menu is not found, return False.
        But if severe==True, raise an error and stop."""
        
        s = '** TDLMenu('+str(key)+','+str(time)+'): '
        result = False

        if time=='runtime':
            if not isinstance(key,str):
                result = self.TDLRuntimeOptionMenu
            elif self.TDLRuntimeOptionSubmenu.has_key(key):
                result = self.TDLRuntimeOptionSubmenu[key]

        elif time=='compile':
            if not isinstance(key,str):
                result = self.TDLCompileOptionMenu
            elif self.TDLCompileOptionSubmenu.has_key(key):
                result = self.TDLCompileOptionSubmenu[key]

        else:
            if not isinstance(key,str):
                result = self.TDLCompileOptionMenu
            elif self.TDLCompileOptionSubmenu.has_key(key):
                result = self.TDLCompileOptionSubmenu[key]
            elif self.TDLRuntimeOptionSubmenu.has_key(key):
                result = self.TDLRuntimeOptionSubmenu[key]

        # Deal with the result:
        if trace:
            print s,'->',str(result)
        if not result==False:
            return result
        elif severe:
            s += 'not recognized'
            raise ValueError,s
        return result

    def TDLCompileMenu (self, key=None, severe=False, trace=False):
        """Return the specified TDL (sub) menu"""
        return self.TDLMenu (key=key, time='compile', severe=severe, trace=trace)
    
    def TDLRuntimeMenu (self, key=None, severe=False, trace=False):
        """Return the specified TDL (sub) menu"""
        return self.TDLMenu (key=key, time='runtime', severe=severe, trace=trace)
    
    #---------------------------------------------------------------------

    def TDLOption (self, key=None, time=None, severe=False, trace=False):
        """Return the specified TDL option"""
        s = '** TDLOption('+str(key)+','+str(time)+'):'
        # if not key[0]=='_': key = '_'+key
        result = False
        if time=='runtime':
            if self.TDLRuntimeOption.has_key(key):
                result = self.TDLRuntimeOption[key]
        elif time=='compile':
            if self.TDLCompileOption.has_key(key):
                result = self.TDLCompileOption[key]
        else:
            if self.TDLCompileOption.has_key(key):
                result = self.TDLCompileOption[key]
            elif self.TDLRuntimeOption.has_key(key):
                result = self.TDLRuntimeOption[key]
        # Deal with the result:
        if trace:
            print s,'->',str(result)
        if not result==False:
            return result
        elif severe:
            s += 'not recognized'
            raise ValueError,s
        return result

        
    def TDLCompileOption (self, key=None, severe=False, trace=False):
        """Return the specified TDLCompile option"""
        return self.TDLOption (key=key, time='compile', severe=severe, trace=trace)
    
    def TDLRuntimeOption (self, key=None, severe=False, trace=False):
        """Return the specified TDLRuntime option"""
        return self.TDLOption (key=key, time='runtime', severe=severe, trace=trace)
    

    #---------------------------------------------------------------------

    def show(self, key=None, show=True, time=None):
        """Show/hide the specified menu/option."""
        return self.hide(key=key, hide=(not show), time=time)


    def hide(self, key=None, hide=True, time=None):
        """Hide/unhide the specified menu/option."""
        if isinstance(key,bool):
            hide = key
            key = None
        menu = self.TDLMenu(key, time=time)
        if menu: return menu.hide(hide)
        option = self.TDLOption(key, time=time)
        if option: return option.hide(hide)
        return False
        
    #---------------------------------------------------------------------

    def enable(self, key=None, enable=True, time=None):
        """Enable/disable the specified menu/option."""
        return self.disable (key=key, disable=(not enable), time=time)

    def disable(self, key=None, disable=True, time=None):
        """Disable/enable the specified menu/option."""
        if isinstance(key,bool):
            disable = key
            key = None
        menu = self.TDLMenu(key, time=time)
        if menu: return menu.disable(disable)
        option = self.TDLOption(key, time=time)
        if option: return option.disable(disable)
        return False
        
    #---------------------------------------------------------------------

    def set_value (self, key, value, time=None, trace=False):
        """Helper function to change the value of the specified (key) option."""
        option = self.TDLOption(key, time=time, severe=True, trace=trace)
        if not option: return False
        print '** set_value(',key,value,')',self.parent
        option.set_value(value)
        return True

    #---------------------------------------------------------------------

    def set_option_list (self, key, olist,
                         select=None, conserve_selection=True,
                         time=None, trace=False):
        """Helper function to change the option list of the specified (key) option."""
        option = self.TDLOption(key, time=time, severe=True, trace=trace)
        if not option: return False
        option.set_option_list(olist, select=select,
                               conserve_selection=conserve_selection)
        print '** set_option_list(',key,olist,')'
        return True




    #=================================================================
    # 
    #=================================================================

    def make_TDLCompileOptionMenu (self, insert=None, **kwargs):
        """Generic function for interaction with its TDLCompileOptions menu."""
        if not isinstance(kwargs, dict): kwargs = dict()
        kwargs.setdefault('trace', False)
        if not self.TDLCompileOptionMenu:
            # First the single items (if any) of the main menu: 
            oolist = self.make_TDLCompileOptionList(**kwargs)
            # Then the various submenus (if any):
            if isinstance(insert, list):
                oolist.extend(insert)
            # Optional: insert a given list of external items:
            kwargs.setdefault('reset', True)
            # Optional (but last): Include a 'reset' menuitem
            if kwargs['reset']:
                oolist.append(self.make_reset_item())
            prompt = self.namespace(prepend='options for: ', append=self.parent)
            # prompt += self.parent
            self.TDLCompileOptionMenu = TDLCompileMenu(prompt, *oolist)
        return self.TDLCompileOptionMenu

    #---------------------------------------------------------------------

    def make_TDLCompileOptionList(self, **kwargs):
        """Automatic generation of a list of CompileOption objects."""
        if not isinstance(kwargs, dict): kwargs = dict()
        # First make a list of single items for the main menu (*)
        oolist = self.make_TDLCompileOptionSubmenuList(submenu='*')
        # Then append the various submenus (if any):
        for submenu in self.submenu_compile.keys():
            if not submenu=='*':
                oo = self.make_TDLCompileOptionSubmenu(submenu)
                oolist.append(oo)
        # Return the list of Option objects:
        return oolist
    

    def make_TDLCompileOptionSubmenuList (self, submenu):
        """Make a list of Option objects for the specified submenu."""
        keys = self.submenu_compile[submenu]
        oolist = []
        for key in keys:
            if not self.TDLCompileOption.has_key(key):
                ukey = '_'+key
                rr = self.optrec_compile[key]
                prompt = rr['prompt'] or key
                doc = rr['doc'] or '<doc>'
                opt = [getattr(self,ukey)]
                if isinstance(rr['opt'],list):
                    opt.extend(rr['opt'])
                more = rr['more'] or float                # type(opt[0])
                oo = TDLOption(key, prompt, opt, more=more,
                               doc=doc, namespace=self)
                if not submenu=='*':
                    oo.when_changed(self._callback_submenu)
                if rr['callback']:
                    oo.when_changed(rr['callback'])
                self.TDLCompileOption[key] = oo
            oolist.append(self.TDLCompileOption[key])
        return oolist

    #.....................................................................

    def make_TDLCompileOptionSubmenu (self, submenu):
        """Automatic generation of an CompileOption submenu"""
        if not self.TDLCompileOptionSubmenu.has_key(submenu):
            oolist = self.make_TDLCompileOptionSubmenuList(submenu)
            prompt = 'submenu: '+submenu
            om = TDLCompileMenu(prompt, *oolist)
            self.TDLCompileOptionSubmenu[submenu] = om
            self._callback_submenu()
        return self.TDLCompileOptionSubmenu[submenu]
            
            
    #.....................................................................

    def _callback_submenu(self, dummy=None):
        """Function called whenever any TDLOption in a submenu changes.
        It changes the summary string of the submenu header."""
        for submenu in self.submenu_compile.keys():
            if self.TDLCompileOptionSubmenu.has_key(submenu):
                summ = '('
                first = True
                keys = self.submenu_compile[submenu]
                for key in keys:
                    if self.TDLCompileOption.has_key(key):
                        value = self.TDLCompileOption[key].value
                        if not first: summ += ','
                        first = False
                        if value==None:
                            summ += '-' 
                        elif isinstance(value,str):
                            summ += 'str'
                        else:
                            summ += str(value)
                summ += ')'
                self.TDLCompileOptionSubmenu[submenu].set_summary(summ)
        return True


        
    #---------------------------------------------------------------------
    # Functions dealing with resetting option values:
    #---------------------------------------------------------------------

    def make_reset_item (self, slave=False):
        """...."""
        key = 'opt_reset'
        if not self.TDLCompileOption.has_key(key):
            doc = """If True, reset all options to their original default values.
            (presumably these are sensible values, supplied by the module designer.)"""
            prompt = self.parent+':  reset to original defaults'
            oo = TDLOption(key, prompt, [False, True], doc=doc, namespace=self)
            oo.when_changed(self._callback_reset)
            if slave: oo.hide()
            self.TDLCompileOption[key] = oo
        return self.TDLCompileOption[key]


    #.....................................................................

    def _callback_reset(self, reset):
        """Function called whenever TDLOption _reset changes."""
        if reset and self.TDLCompileOptionMenu:
            self.reset_options(trace=True)
            key = 'opt_reset'
            self.TDLCompileOption[key].set_value(False, callback=False,
                                                  save=True)
        return True


    #.....................................................................

    def reset_options(self, trace=False):
        """Helper function to reset the TDLCompileOptions and their local
        counterparts to the original default values (in self._reset). 
        """
        if trace:
            print '\n** _reset_options(): ',self.oneliner()
        for key in self.optrec_compile.keys():
            ukey = '_'+key
            was = getattr(self,ukey)
            new = self.optrec_compile[key]['reset']
            setattr(self, key, new)
            if self.TDLCompileOption.has_key(key):
                self.TDLCompileOption[key].set_value(new, save=True)
                new = self.TDLCompileOption[key].value
                if trace:
                    print ' -',key,':',was,' -> ',getattr(self,ukey),
                    if not new==getattr(self,ukey):
                        print '** TDLOption =',new,'!?',
            else:
                if trace: print ' -',key,':',was,' -> ',getattr(self,ukey),
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
    om = OptionManager()
    om.test()
    om.TDLCompileOptionMenu()


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
        om = OptionManager(parent='test')
        om.display('initial')
        om.test()

    if 1:
        om.make_TDLCompileOptionMenu(slave=False)

    if 1:
        om.display('final')

    if 1:
        keys = [None] + om.submenu_compile.keys()
        for key in keys: om.TDLMenu(key, trace=True)
        for key in keys: om.TDLCompileMenu(key, trace=True)
        for key in keys: om.TDLRuntimeMenu(key, trace=True)

    if 1:
        keys = [None] + om.submenu_runtime.keys()
        for key in keys: om.TDLMenu(key, trace=True)



#===============================================================


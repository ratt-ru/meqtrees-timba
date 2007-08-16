# file: ../Grunt/OptionManager.py

# History:
# - 24jul2007: creation

# Description:

"""The Grunt OptionManager class manages the options of a module,
i.e. the values of the parameters that rule its compile-time and
run-time behaviour. It makes use of Meow options (see ....), and
provides some extra functionality to make things easy for the user.

An empty OptionManager object is created and attached to a module by:
- self._om = OptionManager(self.name, [namespace])

A named (key) option with some (default) value is then defined by
means of the function:
- self._om.define(key1, value1)
- self._om.define(key2, value2)
-   ...
Each defined option (and its attributes, see below) is stored in a
separate record, and an internal variable with the default value is
created inside the OptionManager.
The defined options may be turned into a TDLMenu of TDLOPtions in the
meqbrowser by:
- self._om.make_TDLCompileOptionMenu()
- self._om.make_TDLRuntimeOptionMenu()
It should be realised that the 

The value of an option should ONLY(!) be accessed by the parent module by:
- x = self._om[key]


For each option, a number of attributes may be defined 


    def define (self, key, value, submenu=None, cat='compile',
                prompt=None, opt=None, more=None, doc=None,
                callback=None, trace=True):

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

# from copy import deepcopy

#======================================================================================

class OptionManager (object):
    """The Grunt OptionManager class manages the options of a module"""

    def __init__(self, name='<parent>', namespace=None):

        self.name = name
        self.frameclass = 'Grunt.OptionManager'

        # This field is expected by OMS:
        self.tdloption_namespace = namespace

        # Option definition records:
        self.optrec = dict(compile=None, runtime=None)

        # Keep a list of option categories (e.g. ['compile','runtime']):
        self.cats = self.optrec.keys()

        # Some useful lists of option names (keys):
        self.optrec_keys = dict(compile=[], runtime=[])   
        self.submenu_keys = dict(compile=dict(), runtime=dict())   

        # TDLOption objects:
        self.TDLOptionObj = dict()   
        self.TDLOptionMenu = dict(compile=None, runtime=None)   
        self.TDLOptionSubmenu = dict(compile=dict(), runtime=dict())   

        # Finished:
        return None


    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------

    def keys (self, name=None, trace=False):
        """Helper function to return the specified group of option keys"""
        keys = None
        if not isinstance(name, str):
            keys = []
            for cat in self.cats:
                keys.extend(self.optrec_keys[cat])
        elif name in self.optrec_keys.keys():
            keys = self.optrec_keys[name]
        else:
            for cat in self.cats:
                rr = self.submenu_keys[cat]
                if name in rr.keys():
                    keys = rr[name]
        if keys==None:
            s = '.keys('+name+'): not found' 
            raise ValueError,s
        if trace:
            print '** .keys(',name,')  ->',keys
        return keys
        
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
    

    #-----------------------------------------------------------------------------

    def __getitem__ (self, key):
        """Get the current value of the specified option (key).
        This should be the ONLY way in which an option value is obtained
        from the OptionManager. This makes sure that the module can also be
        used standalone, i.e. without any TDLOptions/menus.
        """
        # The name of the internal variable is prepended with '_': self._<key>
        # This is to avoid name clashes with any object attributes.
        ukey = '_'+key
        if True:
            # Make sure that the internal value is equal to the current value
            # of the TDLOptionObj.value (if it exists).
            # For some reason, this does not happen automatically when the
            # TDLOptionObj value is modified by the user (it used too...).
            if self.TDLOptionObj.has_key(key):
                setattr(self, ukey, self.TDLOptionObj[key].value)
        return getattr(self, ukey)


    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------

    def define (self, key, value, submenu=None, cat='compile',
                prompt=None, opt=None, more=None, doc=None,
                callback=None, trace=True):
        """Helper function to define a named (key) option with its (default) value.
        """

        # A range of options may be specified by a dict:     # <---- ???
        if isinstance(value, dict):
            if not isinstance(submenu, str): submenu = key
            for key in value.keys():
                self.define(key, value[key], submenu=submenu, cat=cat)
        
        else:
            ukey = '_'+key                                   # internal name
            setattr (self, ukey, value)                      # working values
            rr = dict(reset=value, doc=doc, prompt=prompt,
                      opt=opt, more=more, callback=callback)
            if not isinstance(submenu, str): submenu = '*'
            self.optrec[key] = rr
            self.optrec_keys[cat].append(key)
            if isinstance(submenu, str): 
                self.submenu_keys[cat].setdefault(submenu, [])
                self.submenu_keys[cat][submenu].append(key)

            if trace:
                print '  ** define(',key,ukey,value,submenu,cat,')'
        return True

    #-----------------------------------------------------------------------------

    def modify (self, key, cat='compile', **pp):
        """Helper function to modify field(s) of an existing (key) optrec,
        which has been defined earlier with .define(key, ...)."""
        if cat=='runtime':
            rr = self.optrec[key]
        else:
            rr = self.optrec[key]
        if not isinstance(pp, dict): pp = dict()
        pp.setdefault('trace',False)
        keys = ['value','opt','more','prompt','doc','callback']
        for key in keys:
            if pp.has_key(key):
                rr[key] = pp[key]
                # if key=='opt']: self.set_option_list(key, rr[key])
        return True



    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = self.frameclass+':'
        ss += '  name='+str(self.name)
        ss += '  namespace='+str(self.tdloption_namespace)
        for cat in self.cats:
            keys = self.keys(cat)
            n = len(keys)
            if n>0:
                ss += '  n'+cat[0]+'='+str(n)
                ss += '('+keys[0]
                if n>1: ss +='...'
                ss += ')'
        return ss


    def display(self, txt=None, full=False, level=0):
        """Print a summary of this object"""
        prefix = '  '+(level*'  ')+'..'
        print prefix,' '
        print prefix,'** '+self.oneliner()
        if txt: print prefix,'  * (txt='+str(txt)+')'
        #...............................................................
        if full:
            for cat in self.cats:
                print prefix,'  * '+cat+' option definition(s): '
                for key in self.optrec_keys[cat]:
                    print prefix,'    - '+key+': '+str(self.optrec[key])
        #...............................................................
        for cat in self.cats:
            keys = self.optrec_keys[cat]
            print prefix,'  * '+cat+' option values (n='+str(len(keys))+'): '
            for key in keys:
                rr = self.optrec[key]
                value = self[key]
                ss = ' = '+str(value)
                if not value==rr['reset']:
                    ss += '    (reset='+str(rr['reset'])+'!)' 
                if not self.TDLOptionObj.has_key(key):
                    ss += '   (-)'
                else:
                    oo = self.TDLOptionObj[key]
                    noexist = -1.23456789
                    if getattr(oo, 'value', noexist)==noexist:
                        print prefix,'    - '+str(key)+': '+str(self.TDLOptionObj[key])
                    else:
                        TDLvalue = self.TDLOptionObj[key].value
                        if not value==TDLvalue:
                            ss += '    (TDLOptionObj.value='+str(TDLvalue)+'!)'
                print prefix,'    - '+key+ss
        #...............................................................
        print prefix,'  * submenu keys: '
        for cat in self.cats:
            rr = self.submenu_keys[cat]
            for key in rr.keys():
                print prefix,'    - ('+cat+') '+key+': '+str(rr[key])
        #..............................................................
        for cat in self.cats:
            print prefix,'  * TDLOptionMenu['+cat+'] = '+str(self.TDLOptionMenu[cat])
            print prefix,'  * TDLOptionSubmenu['+cat+']:'
            rr = self.TDLOptionSubmenu[cat]
            for key in rr.keys():
                print prefix,'    - ('+cat+') '+key+': '+str(rr[key])
        for cat in self.cats:
            keys = self.optrec_keys[cat]
            n = 0
            for key in keys:
                if self.TDLOptionObj.has_key(key): n += 1
            print prefix,'  * TDLOptionObj('+cat+') (n='+str(n)+'/'+str(len(keys))+'):'
            if full:
                for key in keys:
                    if self.TDLOptionObj.has_key(key):
                        print prefix,'    - '+key+' = '+str(self.TDLOptionObj[key])
                    else:
                        print prefix,'    - '+key+': (not yet created)'
        #...............................................................
        print prefix,'**\n'
        return True




    #===================================================================
    #===================================================================

    def TDLMenu (self, key=None, cat=None, severe=False, trace=False):
        """Return the specified (key) TDL(sub)menu object (or None).
        If cat==None (i.e. not specified), check for a compile menu first,
        and then for a runtime menu.
        If the specified menu is not found, return False.
        But if severe==True, raise an error and stop."""
        
        s = '** TDLMenu('+str(key)+','+str(cat)+'): '
        result = False

        if cat in self.cats:
            if not isinstance(key,str):
                result = self.TDLOptionMenu[cat]
            elif self.TDLOptionSubmenu[cat].has_key(key):
                result = self.TDLOptionSubmenu[cat][key]

        else:
            if not isinstance(key,str):
                result = self.TDLOptionMenu['compile']
            elif self.TDLOptionSubmenu['compile'].has_key(key):
                result = self.TDLOptionSubmenu['compile'][key]
            elif self.TDLOptionSubmenu['runtime'].has_key(key):
                result = self.TDLOptionSubmenu['runtime'][key]

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
        return self.TDLMenu (key=key, cat='compile', severe=severe, trace=trace)
    
    def TDLRuntimeMenu (self, key=None, severe=False, trace=False):
        """Return the specified TDL (sub) menu"""
        return self.TDLMenu (key=key, cat='runtime', severe=severe, trace=trace)
    
    #---------------------------------------------------------------------

    def TDLOption (self, key=None, severe=False, cat=None, trace=False):
        """Return the specified TDL option"""
        s = '** TDLOption('+str(key)+'):'
        result = False
        if self.TDLOptionObj.has_key(key):
            result = self.TDLOptionObj[key]
        # Deal with the result:
        if trace:
            print s,'->',str(result)
        if not result==False:
            return result
        elif severe:
            s += 'not recognized'
            raise ValueError,s
        return result

        
    #---------------------------------------------------------------------

    def show(self, key=None, show=True, cat=None):
        """Show/hide the specified menu/option."""
        return self.hide(key=key, hide=(not show), cat=cat)


    def hide(self, key=None, hide=True, cat=None):
        """Hide/unhide the specified menu/option."""
        if isinstance(key,bool):
            hide = key
            key = None
        menu = self.TDLMenu(key, cat=cat)
        if menu: return menu.hide(hide)
        option = self.TDLOption(key, cat=cat)
        if option: return option.hide(hide)
        return False
        
    #---------------------------------------------------------------------

    def enable(self, key=None, enable=True, cat=None):
        """Enable/disable the specified menu/option."""
        return self.disable (key=key, disable=(not enable), cat=cat)

    def disable(self, key=None, disable=True, cat=None):
        """Disable/enable the specified menu/option."""
        if isinstance(key,bool):
            disable = key
            key = None
        menu = self.TDLMenu(key, cat=cat)
        if menu: return menu.disable(disable)
        option = self.TDLOption(key, cat=cat)
        if option: return option.disable(disable)
        return False
        
    #---------------------------------------------------------------------

    def set_value (self, key, value, cat=None, trace=False):
        """Helper function to change the value of the specified (key) option."""
        option = self.TDLOption(key, cat=cat, severe=True, trace=trace)
        if not option: return False
        print '** set_value(',key,value,')',self.name
        option.set_value(value)
        return True

    #---------------------------------------------------------------------

    def set_option_list (self, key, olist,
                         select=None, conserve_selection=True,
                         cat=None, trace=False):
        """Helper function to change the option list of the specified (key) option."""
        option = self.TDLOption(key, cat=cat, severe=True, trace=trace)
        if not option: return False
        option.set_option_list(olist, select=select,
                               conserve_selection=conserve_selection)
        print '** set_option_list(',key,olist,')'
        return True




    #=================================================================
    # Make TDL menu(s):
    #=================================================================

    def make_TDLOptionMenu (self):
        """Somewhat limited convenience function that defines both types of
        TDLMenus"""
        self.make_TDLCompileOptionMenu()
        self.make_TDLRuntimeOptionMenu()
        return True

    def make_TDLCompileOptionMenu (self, insert=None, **kwargs):
        return self.make_TDLOptionMenu (insert=insert, cat='compile', **kwargs)

    def make_TDLRuntimeOptionMenu (self, insert=None, **kwargs):
        return self.make_TDLOptionMenu (insert=insert, cat='runtime', **kwargs)

    def make_TDLCompileOptionList(self, **kwargs):
        return self.make_TDLOptionList(cat='compile', **kwargs)

    def make_TDLRuntimeOptionList(self, **kwargs):
        return self.make_TDLOptionList(cat='runtime', **kwargs)


    #=================================================================

    def make_TDLOptionMenu (self, insert=None, cat='compile', **kwargs):
        """Generic function for interaction with its TDLOptions menu."""
        if not isinstance(kwargs, dict): kwargs = dict()
        kwargs.setdefault('trace', False)
        if not self.TDLOptionMenu[cat]:
            # First the single items (if any) of the main menu: 
            oolist = self.make_TDLOptionList(cat=cat, **kwargs)
            # Then the various submenus (if any):
            if isinstance(insert, list):
                oolist.extend(insert)
            # Optional: insert a given list of external items:
            kwargs.setdefault('reset', True)
            # Optional (but last): Include a 'reset' menuitem
            if kwargs['reset']:
                oolist.append(self.make_reset_item())
            prompt = self.namespace(prepend='options for: ', append=self.name)
            if len(oolist)==0:
                return None
            elif cat=='runtime':
                self.TDLOptionMenu[cat] = TDLRuntimeMenu(prompt, *oolist)
            else:
                self.TDLOptionMenu[cat] = TDLCompileMenu(prompt, *oolist)
        return self.TDLOptionMenu[cat]

    #---------------------------------------------------------------------

    def make_TDLOptionList(self, cat='compile', **kwargs):
        """Automatic generation of a list of CompileOption objects."""
        if not isinstance(kwargs, dict): kwargs = dict()
        # First make a list of single items for the main menu (*)
        oolist = self.make_TDLOptionSubmenuList(submenu='*', cat=cat)
        # Then append the various submenus (if any):
        for submenu in self.submenu_keys[cat].keys():
            if not submenu=='*':
                if not self.TDLOptionSubmenu[cat].has_key(submenu):
                    solist = self.make_TDLOptionSubmenuList(submenu, cat=cat)
                    prompt = 'submenu: '+submenu
                    if cat=='runtime':
                        om = TDLRuntimeMenu(prompt, *solist)
                    else:
                        om = TDLCompileMenu(prompt, *solist)
                    self.TDLOptionSubmenu[cat][submenu] = om
                    self._callback_submenu()
                oo = self.TDLOptionSubmenu[cat][submenu]
                oolist.append(oo)
        # Return the list of Option objects:
        return oolist
    
    #.....................................................................

    def make_TDLOptionSubmenuList (self, submenu, cat='compile'):
        """Make a list of Option objects for the specified submenu."""
        oolist = []
        if not self.TDLOptionSubmenu[cat].has_key(submenu):
            for key in self.submenu_keys[cat][submenu]:
                ukey = '_'+key
                rr = self.optrec[key]
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
                self.TDLOptionObj[key] = oo
                oolist.append(oo)
        return oolist

            
    #.....................................................................

    def _callback_submenu(self, dummy=None):
        """Function called whenever any TDLOptionObj in a submenu changes.
        It changes the summary string of the submenu header."""

        print '\n** _callback_submenu(',dummy,')\n'         # ...temporary...
        return True
    
        for submenu in self.submenu_compile.keys():
            if self.TDLCompileOptionSubmenu.has_key(submenu):
                summ = '('
                first = True
                keys = self.submenu_compile[submenu]
                for key in keys:
                    if self.TDLOptionObj.has_key(key):
                        value = self.TDLOptionObj[key].value
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

    def make_reset_item (self, slave=False, cat='compile'):
        """...."""
        key = 'reset_'+str(cat)+'_options'
        if not self.TDLOptionObj.has_key(key):
            doc = """If True, reset all options to their original default values.
            (presumably these are sensible values, supplied by the module designer.)"""
            prompt = self.name+':  reset to original defaults'
            oo = TDLOption(key, prompt, [False, True], doc=doc, namespace=self)
            oo.when_changed(self._callback_reset)
            if slave: oo.hide()
            self.TDLOptionObj[key] = oo
        return self.TDLOptionObj[key]


    #.....................................................................

    def _callback_reset(self, reset):
        """Function called whenever TDLOptionObj _reset changes."""
        if reset and self.TDLOptionMenu['compile']:
            self.reset_options(trace=True)
            key = 'opt_reset'
            self.TDLOptionObj[key].set_value(False, callback=False, save=True)
        return True


    #.....................................................................

    def reset_options(self, trace=False):
        """Helper function to reset the TDLOptions and their local
        counterparts to the original default values (in self._reset). 
        """
        if trace:
            print '\n** _reset_options(): ',self.oneliner()
        for key in self.optrec.keys():
            ukey = '_'+key
            was = getattr(self,ukey)
            new = self.optrec[key]['reset']
            setattr(self, key, new)
            if self.TDLOptionObj.has_key(key):
                self.TDLOptionObj[key].set_value(new, save=True)
                new = self.TDLOptionObj[key].value
                if trace:
                    print ' -',key,':',was,' -> ',getattr(self,ukey),
                    if not new==getattr(self,ukey):
                        print '** TDLOptionObj =',new,'!?',
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
        self.define('mode', 'solve', opt=['nosolve','solve','simulate'], more=str,
                    doc='The rain in Spain....', callback=self._callback_mode)
        self.define('default', 12.9, more=float)
        self.define('simuldev', 'expr', more=str)
        self.define('tiling', None, submenu='span', opt=[1,2,4,8], more=int)
        self.define('time_deg', 1, submenu='span', more=int)
        self.define('freq_deg', 2, submenu='span', more=int)
        self.define('constraint', constraint, submenu='constraint')
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
        om = OptionManager(name='test')
        om.display('initial')
        om.test()
        om.display('initial', full=True)

    if 1:
        om.make_TDLCompileOptionMenu(slave=False)

    if 1:
        om.display('final')

    if 1:
        ss = [None]
        ss.extend(om.cats)
        for cat in om.cats:
            ss.extend(om.submenu_keys[cat].keys())
        for s in ss:
            om.keys(s, trace=True)

    if 0:
        keys = [None] + om.submenu_compile.keys()
        for key in keys: om.TDLMenu(key, trace=True)
        for key in keys: om.TDLCompileMenu(key, trace=True)
        for key in keys: om.TDLRuntimeMenu(key, trace=True)

    if 0:
        keys = [None] + om.submenu_runtime.keys()
        for key in keys: om.TDLMenu(key, trace=True)



#===============================================================


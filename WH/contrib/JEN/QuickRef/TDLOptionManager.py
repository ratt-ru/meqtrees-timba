"""
TDLOptionManager.py:
"""

# file: ../JEN/QuickRef/TDLOptionManager.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 15 sep 2008: creation 
#
# Description:
#
# Remarks (for OMS):
#
# -) The callback functions in a TDLMenu object are NOT called
#    when a menu is opened or closed by clicking on its toggle box......
#
# -) It would be nice if a callback would know WHICH option was clicked.
#    The .find_changed() is a little clumsy...
#
# -) TDL Separator (None in TDLOption list) does not work.... ignored for the moment
#    See .add_separator()
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

from Timba.Contrib.JEN.QuickRef import EasyFormat as EF


#******************************************************************************** 

class TDLOptionManager (object):
   """
   Object for managing TDL options in a module.
   """

   def __init__(self, name='modulename', prompt=None, mode='compile'):

      self._name = name
      self._mode = 'compile'                   # alternative: 'runtime'

      # Separator chars are used to build hierarchical names:
      self._keysep = '.'           # separator char used for (defrec) keys                 
      self._symsep = '_'           # separator char used for symbol names 
      # self._symsep = '|'           # separator char used for symbol names 
      # self._symsep = ':'           # separator char used for symbol names 

      # The following field is expected by OMS TDLOption() etc,
      # but it is set when calling the function .TDLMenu() below:
      self.tdloption_namespace = None

      # The menu structure is defined in a definition record first:
      self._menudef = dict()
      self.start_of_submenu(self._name, prompt=prompt, topmenu=True)

      # The definition record is used to generate the actual TDLOption objects.
      self._TDLmenu = None                    # the final TDLMenu 
      self._oblist = dict()                   # record of TDLOption objects

      # Group control:
      self._lastval = dict()                  # last values (see .find_changed())
      self._snapshot = dict()                 # snapshot values (see .make_snapshot())

      # The fields of self._menudef are called keys. They contain dots(.)
      # The option/menu names are derived from keys by .key2symbol(key)
      self._keys = dict()                     # menudef field-names[symbol]

      return None

   #--------------------------------------------------------------------------

   def oneliner (self):
      ss = 'TDLOptionManager: '+str(self._name)
      ss += '  mode='+str(self._mode)
      ss += '  nobj='+str(len(self._oblist))
      ss += '  nkey='+str(len(self._keys.keys()))
      if self.tdloption_namespace:
         ss += ' ('+str(self.tdloption_namespace)+')'
      return ss

   #--------------------------------------------------------------------------

   def show (self, txt=None, full=True):
      """
      """
      ss = '\n'
      ss += '\n** '+self.oneliner()
      if txt:
         ss += '   ('+str(txt)+')'
      ss += '\n * self.tdloption_namespace: '+str(self.tdloption_namespace)
      ss += '\n * self._oblist: '+str(len(self._oblist))
      ss += '\n * self._keys: '+str(len(self._keys.keys()))
      if full:
         for symbol in self.symbols():
            ss += '\n   - '+str(symbol)+' : '+str(self._keys[symbol])
      ss += '\n**\n'
      print ss
      return ss


   #--------------------------------------------------------------------------
   # Option/menu definition functions:
   #--------------------------------------------------------------------------

   def add_option (self, relkey,
                   choice=None,              # 2nd
                   prompt=None,              # 3rd
                   more=True,                # use the type of default (choice[0])
                   hide=False,
                   disable=False,
                   master=None,              # optional: key of 'master' option
                   help=None,
                   callback=None,
                   prepend=False,
                   trace=False):
      """
      Add an TDLOption definition to the menu definitions. Its name is a concatanation
      of the 'current' menu name, and the specified 'relative' key (relkey).
      If master is a valid option key, this option will be slaved to it.
      If prepend=True, prepend it to the already specified list of options.
      """
      # trace = True
      if trace:
         print '\n** .add_option(',relkey,'):'
         
      if self._complete:
         raise ValueError,'** TOM.add_option(): TDLMenu is complete'

      # Make a list of callback functions (may be empty):
      if not callback:
         callback = []
      elif not isinstance(callback,list):
         callback = [callback]
      callback.append(self.callback_update_lastval)

      # Check the choice of option values:
      # (The default is the value used in .revert_to_defaults())
      default = None
      selectable = False
      if choice==None:                       # not specified
         choice = False                      # add un-selected toggle box
         selectable = True
      if isinstance(choice, bool):           # True/False: add toggle box
         default = choice                    # 
         selectable = True
      elif not isinstance(choice, list):     # e.g. numeric, or string, or ..?
         choice = [choice]                   # make a list (necessary?)
         default = choice[0]                 # the first item
      else:
         default = choice[0]                 # the first item

      # If more=True, use the type of default:
      if isinstance(more, bool):
         if more==True:
            if isinstance(default,bool):
               more = bool
            elif isinstance(default,int):
               more = int
            elif isinstance(default,float):
               more = float
            elif isinstance(default,complex):
               more = complex
            else:
               more = None                  # type not recognized...
         else:                       
            more = None

      # Finally, make the option definition record:
      menukey = self._current_submenu['key']
      key = menukey + self._keysep + relkey
      symbol = self.key2symbol(key)
      if not isinstance(help,str):          # no help/doc string specified
         help = '(symbol='+str(symbol)+')'  # 
      optdef = dict(type='option', key=key, symbol=symbol,
                    prompt=(prompt or relkey),
                    help=help,
                    callback=callback,
                    default=default,
                    hide=hide, disable=disable,
                    master=master, slave=[],
                    menukey=menukey,
                    selectable=selectable,
                    choice=choice, more=more)
      self._current_submenu['menu'][key] = optdef
      self.order(key, prepend=prepend, trace=trace)

      # Finished:
      if trace:
         print '\n** .add_option(',relkey,') ->',optdef
         # print '    current_submenu:\n      ',self._current_submenu
         
      # Return the symbol. It can be used in the module, to read the option value:
      return symbol

   #--------------------------------------------------------------------------

   def add_separator (self, trace=False):
      """
      Add an TDLOption separator definition to the menu definitions.
      """
      if self._complete:
         raise ValueError,'** TOM.add_separator(): TDLMenu is complete'
      
      self._current_submenu['sepcount'] += 1
      key = self._current_submenu['key'] + '.separator'
      key += str(self._current_submenu['sepcount'])
      optdef = dict(type='separator', key=key)
      if True:
         # Temporarily disabled...
         print '\n** TOM.add_separator(): Ignored until it works (OMS)....\n'
         return key
      self._current_submenu['menu'][key] = optdef
      self.order(key, trace=trace)

      if trace:
         print '\n** .add_separator() ->',optdef
         print '    current_submenu:\n      ',self._current_submenu
      return key

   #--------------------------------------------------------------------------

   def start_of_submenu (self, relkey,            
                         prompt=None,             # 2nd
                         default=None,            # 3rd
                         nest=None,
                         hide=False,
                         master=None,
                         help=None,
                         topmenu=False,
                         group_control=True,
                         prepend=False,
                         trace=False):
      """
      Add an TDLMenu definition to the menu definitions. Its name is a concatanation
      of the 'current' menu name, and the specified 'relative' key (relkey).
      The self._current_submenu to the new menu.
      """

      if topmenu:                  # topmenu==True ONLY when called from .__init__()
         self._complete = False
         key = relkey
         menukey = ''              # ...?
      else:
         self.check_current_submenu(nest, trace=trace)
         menukey = self._current_submenu['key']
         key = menukey + self._keysep + relkey
         if self._complete:
            raise ValueError,'** TOM.start_of_submenu(): TDLMenu is complete'

      # Make a list of callback functions (may be empty):
      # NB: This does not work, since the callback functions are NOT called
      #     when a menu is opened or closed by clicking on its toggle box......
      callback = [self.callback_update_lastval]

      # The default is the toggle value (see .revert_to_defaults())
      if not isinstance(default,bool):
         default = False          # default: select and open the menu....

      # Finally, make the menu definition record:
      symbol = self.key2symbol(key)
      if not isinstance(help,str):
         help = '(symbol='+str(symbol)+')'
      menudef = dict(type='menu', key=key, symbol=symbol,
                     prompt=(prompt or relkey),
                     help=help,
                     default=default,
                     hide=hide,
                     master=master, slave=[],
                     menukey=menukey,
                     selectable=True,
                     callback=callback,
                     sepcount=0,
                     order=[], menu=dict())

      if topmenu:                  # topmenu==True ONLY when called from .__init__()
         self._menudef = menudef
         self._current_submenu = self._menudef
      else:
         self._current_submenu['menu'][key] = menudef
         self.order(key, prepend=prepend, trace=trace)                 
         self._current_submenu = self._current_submenu['menu'][key]           # go down one level

      # Optional: Insert a 'group control' option:
      if group_control:
         self.group_control(trace=trace)

      # Finished:
      if trace:
         print '\n** .start_of_submenu(',relkey,') -> current_submenu =',self._current_submenu

      # Return the symbol. It may be used in the module...
      return symbol

   #--------------------------------------------------------------------------

   def check_current_submenu(self, nest=None, trace=False):
      """Check whether the current submenu is the expected one.
      The given 'nest' can be None, a string or an integer (pos or neg).
      If not, try to correct the situation.
      Called from .start_of_submenu()
      """
      trace = True
      s = '\n** .check_current_submenu(nest='+str(nest)+'): '

      key = self._current_submenu['key'] 
      s += '(current key='+str(key)+') '

      if nest==None:                        # not specified
         if trace:
            print s,'no nest specified, keep menu:',key
         return True                        # nothing to check
      elif isinstance(nest,int):            # e.g. nest=0 (base menu) etc
         ss = key.split(self._keysep)
         if nest>=0:                        # the absolute level (in the current branch!)
            nest = ss[nest]                 #
            if trace:
               print s,'integer nest (pos: absolute level) converted to:',nest
         else:                              # <0: descend one or more levels
            nest = ss[nest-1]               # a little confusing: ss[-1] would be the current menu
            if trace:
               print s,'integer nest (neg: relative to current level) converted to:',nest
      elif not isinstance(nest,str):
         s += 'nest not a string'
         raise ValueError,s
      
      # Deal with string nest:
      ss = key.split(nest)
      if len(ss)==1:
         s += 'menu not found: ss='+str(ss)
         raise ValueError,s
      elif ss[-1]=='':                      # nest is at the end of key
         if trace:
            print s,'current menu is OK:',key
         return True                        # the current submenu is OK

      # Find the new self._current_submenu record:
      newkey = ss[0]+nest                   # new menu key
      self._current_submenu = self.find_defrec(newkey)
      if trace:
         print s,'-> new current menu:',newkey,'->',self._current_submenu['key']
      return True
      

   #--------------------------------------------------------------------------
   # The following convenience functions may be used for menu=...
   # in the functions .start_of_submenu() and (perhaps) .add_option()
   #--------------------------------------------------------------------------

   def current_menu_key(self, trace=False):
      """Return the (defrec) key of the current submenu"""
      return self._current_submenu['key']

   def current_menu_level(self, trace=False):
      """Return the absolute level of the current submenu"""
      key = self.current_menu_key()
      ss = key.split(self._keysep)
      return len(ss)-1

   def current_menu_symbol(self, trace=False):
      """Return the (global) symbol of the current submenu"""
      return self._current_submenu['symbol']

   #--------------------------------------------------------------------------

   def end_of_submenu (self, check=None, trace=False):
      """
      Revert self._current_submenu to one level higher (done after a menu is complete).
      Subsequent to add_menu() or add_option will now add the new definitions
      to the higher-level menu.
      """
      oldkey = self._current_submenu['key']
      newkey = self.menukey(oldkey)
      if trace:
         print '** .end_of_submenu(): ',oldkey,'->',newkey
      self._current_submenu = self.find_defrec(newkey)
      return newkey

   #--------------------------------------------------------------------------

   def menukey (self, key=None, trace=False):
      """From the given key, derive the key of its menu defrec,
      by removing the part after the last dot (.)
      """
      ss = key.split(self._keysep)
      if len(ss)>1:
         mkey =  key.replace(self._keysep+ss[-1],'')
      else:
         mkey = key
      return mkey

   #--------------------------------------------------------------------------

   def key2symbol(self, key):
      """
      Helper function to convert the given key (i.e. self._menudef field name)
      to the TDLOption symbol used in the module (accessible via globals)
      NB: The reverse function would be unreliable, since not
      all self._keysep chars (e.g. '.') should be replaced by self._symsep chars
      """
      symbol = 'opt'
      if self._mode=='runtime':
         symbol = 'runopt'
      symbol += self._symsep+key.replace(self._keysep,self._symsep)
      return symbol

   #--------------------------------------------------------------------------

   def symbols (self):
      """Return the list of option/menu names (symbols)"""
      return self._keys.keys()

   #--------------------------------------------------------------------------

   def order(self, key=None, prepend=False, trace=False):
      """Helper function to get or update (append/prepend) the order-list
      of the current menu.
      """
      if key:
         if prepend:
            self._current_submenu['order'].insert(0,key)
         else:
            self._current_submenu['order'].append(key) 
      return self._current_submenu['order'] 


   #--------------------------------------------------------------------------
   # Functions dealing with group control:  
   #--------------------------------------------------------------------------

   def group_control (self, trace=False):
      """Add a group-control button to the current submenu.
      """
      choice = ['-','select all','select none','revert to defaults',
                'revert to snapshot','-','help','show defrec']
      choice.extend(['-','make snapshot'])                     # for safety....
      self.add_option ('group_control', choice,
                       prompt='(group control)',
                       help=None, more=None,
                       callback=self.callback_group_control,
                       prepend=True, trace=trace)
      if trace:
         print '\n** .group_control() -> ',self._current_submenu['ctrl']
      return True

   #..........................................................................

   def callback_group_control (self, value):
      """
      Called whenever a group_control option is changed
      """
      trace = False
      # trace = True
      if trace:
         print '\n** .callback_group_control(',value,')\n'

      key = self.find_changed(lookfor=['group_control'], trace=trace)
      if trace:
         print '  changed: key =',key

      if isinstance(key,str):
         menukey = self.menukey(key)
         if trace:
            print '  its menukey =',menukey
         menu = self.find_defrec(menukey, trace=trace)
         if value=='select all':
            self.select_group (menu, True, trace=trace)
         elif value=='select none':
            self.select_group (menu, False, trace=trace)
         elif value=='revert to defaults':
            self.make_snapshot(menu, trace=trace)          # FIRST make snapshot...!?
            self.revert_to_defaults(menu, trace=trace)
         elif value=='make snapshot':
            self.make_snapshot(menu, trace=trace)
         elif value=='revert to snapshot':
            self.revert_to_snapshot(menu, trace=trace)
         elif value=='show defrec':
            print EF.format_record(menu)
         elif value=='-':
            pass
         elif value=='help':
            print '\n   ** help on the use of group control **  \n'
         else:
            print 'value not recognised: ',value,type(value),len(value)
         # Always reset the group control option value to '-':
         self.setopt(key, '-', trace=trace)

      # Finished:
      return None

   #..........................................................................

   def callback_update_lastval (self, value):
      """Called whenever an option value is changed. This is necessary
      to make .find_changed() work properly for .group_control().
      """
      trace = False
      # trace = True
      if trace:
         print '\n** .callback_update_lastval(',value,')\n'
      self.update_lastval()
      return None


   #--------------------------------------------------------------------------
   # Functions dealing with radio-buttons:
   #--------------------------------------------------------------------------

   def radio_buttons (self, trace=False):
      """Make the 'selectable' options and/or submenus of the current submenu
      into mutually exclusive 'radio buttons': One (and only one) of them will
      be selected at all times. 
      """
      # First find the selectable items:
      keys = []
      for key in self._current_submenu['order']:
         rr = self._current_submenu['menu'][key]
         if rr['selectable']:
            keys.append(key)

      # Then make them into radio items:
      for key in keys:
         rr = self._current_submenu['menu'][key]
         rr['radio_group'] = keys
         # The callback should be executed BEFORE .callback_update_lastval():
         rr['callback'].insert(0,self.callback_radio_button)
      
      if trace:
         print '\n** .radio_buttons():',keys
      return True

   #--------------------------------------------------------------------------

   def callback_radio_button(self, value):
      """Called whenever a 'radio button' is changed. Make sure that only one
      TDLOption of its 'radio-group' is selected. See .radion_buttons() above.
      """
      trace = False
      # trace = True
      if trace:
         print '\n** .callback_radio_button(',value,'):'

      key = self.find_changed(trace=trace)
      if trace:
         print '  changed: key =',key

      if isinstance(key,str):
         menukey = self.menukey(key)
         option = self.find_defrec(key, trace=trace)
         keys = option['radio_group']
         # First deselect all items in the 'radio-group':
         for key1 in keys:
            self.setopt(key1, False, callback=False, trace=trace)
         # Then select a single one:
         if value:                     # TDLOption[key] is selected
            self.setopt(key, True, callback=False, trace=trace)
         else:                         # select the first of the keys
            self.setopt(keys[0], True, callback=False, trace=trace)
         # Update self._lastval
         self.update_lastval(trace=trace)
            
      return None


   #==========================================================================
   # Make the TDLMenu (create actual TDLOption objects) from self._menudef:
   #==========================================================================

   def TDLMenu (self, namespace=None, trace=False):
      """Return the complete TDLMenu object. Create it if necessary.""" 
      if self._complete:                         # already created
         return self._TDLMenu                    # just return it

      # Disable any further additions of options or menus:
      self._complete = True
      self._current_submenu = None               # overkill?

      if trace:
         print '\n** _make_TDLMenu(namespace=',namespace,'):'

      # This field is expected by OMS:
      if isinstance(namespace,str):
         self.tdloption_namespace = namespace
         
      # Create the TDLMenu from the self._menudef record:
      menu = self._make_TDLMenu(trace=trace)

      # Add callback function to the ones that have slaves:
      self.callbacks_for_masters(trace=trace)

      self.find_changed()                        # fill self._lastval ....
      return menu

   #--------------------------------------------------------------------------

   def _make_TDLMenu (self, rr=None, level=0, trace=False):
      """
      Recursive routine to generate actual TDLOption/Menu objects.
      The input rr is assumed to be a menu definition record.
      """
      if level==0:
         if trace:
            print '\n** _make_TDLMenu():'
         if not isinstance(rr,dict):
            rr = self._menudef

      prefix = level*'..'

      oblist = []
      for key in rr['order']:
         dd = rr['menu'][key]                   # menu/option definition record
         if trace:
            print prefix,key,':',dd['type']

         if dd['type']=='option':
            tdlob = TDLOption(symbol=dd['symbol'], name=dd['prompt'],
                              value=dd['choice'], more=dd['more'],
                              doc=dd['help'],
                              namespace=self)
            self._keys[dd['symbol']] = dd['key']
            if dd['hide']:
               tdlob.hide()
            if dd['disable']:
               tdlob.disable()
            self._oblist[key] = tdlob

         elif dd['type']=='separator':
            tdlob = None

         elif dd['type']=='menu':
            tdlob = self._make_TDLMenu(dd, level=level+1, trace=trace)  # recursive
         else:
            s = '** option type not recognosed: '+str(dd['type'])
            raise ValueError,s

         # Finishing touches on the TDLOption object:
         if tdlob:
            for callback in dd['callback']:      # assume a list of callback functions
               tdlob.when_changed(callback)
            if isinstance(dd['master'],str):     # assume a valid option key
               # Add its key to the list of slaves of its master option
               master = self.find_defrec(dd['master'])
               master['slave'].append(dd['key'])

         # Append the object (or None) to the list for the menu:
         oblist.append(tdlob)
         

      # Make the TDLMenu object from the accumulated oblist:
      if level>0:
         menu = TDLMenu(rr['prompt'], toggle=rr['symbol'],
                        summary=rr['help'],
                        namespace=self, *oblist)
      elif self._mode=='runtime':
         menu = TDLRuntimeMenu(rr['prompt'], toggle=rr['symbol'],
                               summary=rr['help'],
                               namespace=self, *oblist)
      else:
         menu = TDLCompileMenu(rr['prompt'], toggle=rr['symbol'],
                               summary=rr['help'],
                               namespace=self, *oblist)
      self._keys[rr['symbol']] = rr['key']
      self._oblist[rr['key']] = menu
         
      if trace:
         print prefix,'-> (sub)menu =',rr['symbol'],' (n=',len(oblist),')',str(menu)
         for key1 in ['ctrl','radio']:
            if rr.has_key(key1):
               print prefix,'(',key1,':',rr[key1],')'

      # Return the TDLMenu object:
      return menu



   #==============================================================================
   # Helper functions for option/value/defrec retrieval:
   #==============================================================================

   def callbacks_for_masters(self, trace=False):
      """Add suitable callback functions to 'master' options/menus,
      i.e. the ones that have one or more slaves.
      """
      trace = True
      if trace:
         print '\n** .callbacks_for_masters():'
      for key in self._oblist.keys():
         ob = self._oblist[key]
         defrec = self.find_defrec(key)
         slaves = []                         # temporary
         # slaves = defrec['slaves']
         if len(slaves)>0:
            if trace:
               print '- master:',key,'has',len(slaves),'slaves:',slaves
            ob.when_changed(self.callback_master_has_changed)
      if trace:
         print
      return True

   #-----------------------------------------------------------------------------

   def callback_change_slaves (self, value):
      """Callback called whenever a master option/menu is changed.
      It changes its slaves (option(s)/menu(s)) to the same value.
      """
      trace = False
      trace = True
      if trace:
         print '\n** .callback_change_slaves(',value,'):'
      return True
   

   #-----------------------------------------------------------------------------

   def update_lastval (self, trace=False):
      """
      Update self._lastval with the current values of all TDLOption objects.
      Called from .callback_update_lastval()
      """
      if trace:
         print '\n** .update_lastval():'

      for key in self._oblist.keys():
         ob = self._oblist[key]
         if trace:
            if self._lastval.has_key(key):
               lastval = self._lastval[key]
               if not ob.value==lastval:
                  print '-',key,'=',ob.value,'!= lastval=',lastval
         self._lastval[key] = ob.value

      if trace:
         print '**\n'
      return True


   #==========================================================================
   # Group operations on/below a given menu:
   #==========================================================================

   def select_group (self, menu, tf=None, level=0, trace=False):
      """Select (tf=True) or deselect (tf=False) all selectable options/menus
      below the given menu defrec
      """
      if level==0:
         if trace:
            print '\n** select_group(tf=',tf,'):'
         if not isinstance(menu,dict):
            menu = self._menudef

      # Select/deselect submenus and selectable options: 
      prefix = level*'..'
      for key in menu['order']:
         dd = menu['menu'][key]
         changed = False
         if dd['type']=='menu':
            self.select_group(dd, tf, level=level+1, trace=trace)  # ..first..?
            changed = self.setopt(key, tf, trace=False)
         # elif not dd['type']=='option':
         #    pass         # just in case....
         elif isinstance(dd['choice'],bool):
            # These options have a toggle box
            changed = self.setopt(key, tf, trace=False)
         if trace and changed:
            print prefix,'- changed:',key,'->',tf

      # Finally, select/deselect the menu itself:
      changed = self.setopt(menu['key'], tf, trace=False)
      if trace and changed:
         print '-- changed:',menu['key'],'->',tf
        
      return False

   #--------------------------------------------------------------------------

   def make_snapshot (self, menu=None, level=0, trace=False):
      """
      Below the given menu defrec, copy all the option values to
      self._snapshot. See also .revert_to_snapshot()
      """
      if level==0:
         if trace:
            print '\n** make_snapshot():'
         if not isinstance(menu,dict):
            menu = self._menudef

      prefix = level*'..'
      for key in menu['order']:
         dd = menu['menu'][key]
         if self._oblist.has_key(key):
            ob = self._oblist[key]
            self._snapshot[key] = ob.value
            if trace:
               print prefix,key,': snapshot =',ob.value
         # Recursive:
         if dd['type']=='menu':
            self.make_snapshot(dd, level=level+1, trace=trace)
      return False

   #--------------------------------------------------------------------------

   def revert_to_snapshot (self, menu=None, level=0, trace=False):
      """
      Below the given menu defrec, set all options to the snapshot values.
      See also .make_snapshot()
      """
      if level==0:
         if trace:
            print '\n** revert_to_snapshot():'
         if len(self._snapshot)==0:
            print '\n** .revert_to_snapshot(): no snapshot available yet'
         if not isinstance(menu,dict):
            menu = self._menudef

      prefix = level*'..'
      for key in menu['order']:
         dd = menu['menu'][key]
         if self._oblist.has_key(key):
            if self._snapshot.has_key(key):
               changed = self.setopt(key, self._snapshot[key], trace=False)
               if trace and changed:
                  print prefix,'- changed:',key,'->',self._snapshot[key]
         # Recursive:
         if dd['type']=='menu':
            self.revert_to_snapshot(dd, level=level+1, trace=trace)
      return False

   #--------------------------------------------------------------------------

   def revert_to_defaults (self, menu=None, level=0, trace=False):
      """
      Below the given menu defrec, set all options to the defaults values.
      See also .make_defaults()
      """
      if level==0:
         if trace:
            print '\n** revert_to_defaults():'
         if not isinstance(menu,dict):
            menu = self._menudef

      prefix = level*'..'
      for key in menu['order']:
         dd = menu['menu'][key]
         if dd.has_key('default'):
            default = dd['default']
            changed = self.setopt(key, default, trace=False)
            if trace and changed:
               print prefix,'- changed:',key,'->',default,'(=default)'
         # Recursive:
         if dd['type']=='menu':
            self.revert_to_defaults(dd, level=level+1, trace=trace)
      return False

   #-----------------------------------------------------------------------------

   def hide (self, value=True, menu=None, trace=False):
      """Hide/unhide the specified option/menu"""
      return True


   #================================================================================
   # Helper functions for finding things:
   #================================================================================

   def find_changed (self, lookfor=None, trace=False):
      """Find the key/symbol of the TDLObject whose value has changed
      since the last time this function was called.
      """
      if trace:
         print '\n** .find_changed(',lookfor,'):'

      changed = []
      for key in self._oblist.keys():
         ob = self._oblist[key]
         if self._lastval.has_key(key):
            lastval = self._lastval[key]
            if not ob.value==lastval:
               if trace:
                  print '******* changed:',key,'=',ob.value,' (lastval:',lastval,')'
               changed.append(key)
            elif trace:
               print '-',key,'=',ob.value,' (=lastval:',lastval,')'
               
         self._lastval[key] = ob.value

      # Deal with the result:
      if trace:
         print '  ->',changed

      if len(changed)==1:               # The normal (unambiguous) case
         if trace: print
         return changed[0]

      # Look for changed keys that contain specific substring(s):
      if lookfor:
         if not isinstance(lookfor,list):
            lookfor = [lookfor]
         kk = []
         for key in changed:
            for substring in lookfor:
               if substring in key:
                  kk.append(key)
                  if trace:
                     print '- lookfor:',substring,'-> kk =',kk
         if len(kk)==1:
            if trace: print
            return kk[0]

      # Still no good (zero, or more than one):
      return False


   #--------------------------------------------------------------------------
   
   def find_defrec (self, key, rr=None, level=0, trace=False):
      """
      Find the defenition record with the specified key in self._menudef
      """
      if level==0:
         if trace:
            print '\n** find_defrec(',key,'):'
         if not isinstance(rr,dict):
            rr = self._menudef

      # prefix = level*'..'
      if rr['key']==key:
         return rr
      if key in rr['order']:
         return rr['menu'][key]
      for key1 in rr['order']:
         dd = rr['menu'][key1]
         if dd['type']=='menu':
            result = self.find_defrec(key, dd, level=level+1, trace=trace)
            if isinstance(result,dict):
               return result
      return False

   #----------------------------------------------------------------------------

   def find_symbol(self, substring, severe=True, trace=False):
      """
      Return an existing symbol (option name) that contains the given substring.
      If severe=True, throw an exeption if not found or ambiguous.
      """
      ss = []
      for s in self.symbols():
         if substring in s:
            aa = s.split(substring)
            if aa[-1]=='':              # substring is at the end of s
               ss.append(s)             # accept

      s = '\n** TOM.find_symbol('+substring+'): -> '
      if len(ss)==1:                    # OK
         if trace:
            print s,ss[0],'\n'
         return ss[0]

      # Problem: Found zero items, or more than one:
      s += str(ss)
      if severe:
         raise ValueError,s
      print s,'\n'
      return ss
      

   #================================================================================
   # Interaction (get/set) with option values:
   #================================================================================

   def setopt(self, key, value, callback=False, trace=False):
      """Set the specified option (key) to a new value
      """
      changed = False
      if self._oblist.has_key(key):
         option = self._oblist[key]
         was = option.value
         changed = (not value==was)
         if trace and changed:
            print '- .setopt(',key,value,callback,') changed ->',value,'  (was:',was,')'
         option.set_value(value, callback=callback)
      return changed


   #--------------------------------------------------------------------------

   def getopt(self, name, rider=None, trace=False):
      """Get the current value of the specified (name) TDLOption name/symbol.
      Only a part of the symbol/name is required, as long as it is not ambiguous.
      If rider is defined, make a qhelp string and add it (see QuickRefUtil.py)
      """
      symbol = self.find_symbol(name, severe=True, trace=trace)
      key = self._keys[symbol]
      value = self._oblist[key].value

      if rider:
         # The rider is a concept used in QuickRef modules.
         # It collects information for the documentation, etc.
         # See also QuickRefUtil.getopt()
         qhelp = ''
         qhelp += '<font color="red" size=2>'
         qhelp += '** TDLOption: '+str(symbol)+' = '
         if isinstance(value,str):
            qhelp += '"'+str(value)+'"'
         else:
            qhelp += str(value)
         qhelp += '</font>'
         qhelp += '<br>'
         path = rider.path()   
         rider.insert_help (path, qhelp, append=True)
         
      if trace:
         print '** TOM.getopt(',key,') -> ',value
      return value




#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   node = ns << 1.0

   # Finished:
   return True


#--------------------------------------------------------------------------------
# Functions for executing the tree:
#--------------------------------------------------------------------------------


#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n** Start of standalone test of: TDLOptionManager.py:\n' 


   ns = NodeScope()
   # rider = QRU.create_rider()             # CollatedHelpRecord object

   if 0:
      print EF.format_record(globals(),'globals')

   if 1:
      # Basic testing
      cname = 'module'
      TCM = TDLOptionManager(cname)
      TCM.show('init')

      TCM.add_option('aa', range(4))
      TCM.start_of_submenu('cc')
      TCM.start_of_submenu('dd')
      TCM.start_of_submenu('gg')
      level = TCM.current_menu_level()
      TCM.start_of_submenu('hh', nest=level-1)
      TCM.add_option('bb', range(4))

      if 1:
         menu = TCM.TDLMenu(trace=True)
      TCM.show('finished', full=True)

   

   if 0:
      # Basic testing
      cname = 'module'
      TCM = TDLOptionManager(cname)
      TCM.show('init')

      TCM.add_option('aa', range(4))
      TCM.add_option('bb', range(4))
      # TCM.add_separator(trace=True)

      TCM.start_of_submenu('cc')
      TCM.add_option('aa', range(2,4))
      TCM.add_option('bb', range(1,4))

      TCM.end_of_submenu()
      TCM.add_option('dd', range(4))

      TCM.end_of_submenu()

      if 1:
         menu = TCM.TDLMenu(trace=True)
         print '\n      --> menu=',menu,'\n'

      TCM.show('finished', full=True)
   


   if 0:
      TCM = TDLOptionManager ('TCM')
      TCM.add_option('alltopics', False)
      TCM.add_option('arg1', range(5), more=int)
      
      TCM.start_of_submenu('topic1')
      TCM.add_option('alltopics', False)
      TCM.add_option('arg1', range(5), more=int)
      TCM.add_option('subtopic1', False)
      TCM.add_option('arg1', range(5), more=int)
      TCM.end_of_submenu()
      
      TCM.start_of_submenu('topic2')
      TCM.add_option('alltopics', False)
      TCM.add_option('subtopic2', False)
      TCM.add_option('arg1', range(5), more=int)
      TCM.radio_buttons(trace=True)
      TCM.end_of_submenu()
      
      TCM.start_of_submenu('helpnodes')
      TCM.add_option('allhelpnodes', False)
      TCM.add_option('helpnode_on_entry', False)
      TCM.add_option('helpnode_on_exit', False)
      TCM.add_option('helpnode_helpnode', False)
      TCM.add_option('helpnode_twig', False)
      TCM.add_option('arg1', range(5), more=int)
      TCM.end_of_submenu()
      
      TCM.end_of_submenu()
      TCM.show('before .TDLMenu()')
      itsTDLCompileMenu = TCM.TDLMenu(trace=True)
      TCM.show('after .TDLMenu()')

      if True:
         TCM.find_symbol('subtopic2',trace=True)
         TCM.find_symbol('2_alltopics',trace=True)
         # TCM.find_symbol('alltopics',trace=True)
         # TCM.find_symbol('xxx',trace=True)

      if True:
         TCM.getopt('subtopic2', trace=True)

      if False:
         TCM.find_changed(trace=True)
         TCM.find_changed(trace=True)
   
            
   print '\n** End of standalone test of: TDLOptionManager.py:\n' 

#=====================================================================================






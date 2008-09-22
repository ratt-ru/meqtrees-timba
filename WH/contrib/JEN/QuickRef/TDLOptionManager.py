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
# Remarks:
#
# NB: The callback functions in a TDLMenu object are NOT called
#     when a menu is opened or closed by clicking on its toggle box......
#
# TDL Separator (None in TDLOption list) does not work.... ignored for the moment
# See .add_separator()
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
                   help='not yet supported',
                   callback=None,
                   prepend=False,
                   trace=False):
      """
      Add an TDLOption definition to the menu definitions. Its name is a concatanation
      of the 'current' menu name, and the specified 'relative' key (relkey).
      If prepend=True, prepend it to the already specified list of options.
      """
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
      key = self._current_submenu['key'] + '.' + relkey
      symbol = self.key2symbol(key)
      optdef = dict(type='option', key=key, symbol=symbol,
                    prompt=(prompt or relkey),
                    help=help,
                    callback=callback,
                    default=default,
                    selectable=selectable,
                    choice=choice, more=more)
      self._current_submenu['menu'][key] = optdef
      self.order(key, prepend=prepend, trace=trace)

      # Finished:
      if trace:
         print '\n** .add_option(',relkey,') ->',optdef
         print '    current_submenu:\n      ',self._current_submenu
         
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
                         help='not yet supported',
                         topmenu=False,
                         group_control=True,
                         prepend=False,
                         trace=False):
      """
      Add an TDLMenu definition to the menu definitions. Its name is a concatanation
      of the 'current' menu name, and the specified 'relative' key (relkey).
      Then go 'down' one level, i.e. set self._current_submenu to the new menu. Subsequent to
      add_menu() or add_option will now add the new definitions to the new menu.
      """

      if topmenu:                  # topmenu==True ONLY when called from .__init__()
         self._complete = False
         key = relkey
      else:
         key = self._current_submenu['key'] + '.' + relkey
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
      menudef = dict(type='menu', key=key, symbol=symbol,
                     prompt=(prompt or relkey),
                     help=help,
                     default=default,    
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

   def end_of_submenu (self, radio_buttons=False, trace=False):
      """
      Revert self._current_submenu to one level higher (done after a menu is complete).
      Subsequent to add_menu() or add_option will now add the new definitions
      to the higher-level menu.
      If radio_buttons=True, make the submenu options mutually exclusive 
      """
      if radio_buttons:
         self.radio_buttons(trace=trace)
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
      ss = key.split('.')
      if len(ss)>1:
         mkey =  key.replace('.'+ss[-1],'')
      else:
         mkey = key
      return mkey

   #--------------------------------------------------------------------------

   def key2symbol(self, key):
      """
      Helper function to convert the given key (i.e. self._menudef field name)
      to the TDLOption symbol used in the module (accessible via globals)
      NB: The reverse function would be unreliable, since not
      all underscores (_) should be replaced by dots (.).
      """
      symbol = 'opt'
      if self._mode=='runtime':
         symbol = 'runopt'
      symbol += '_'+key.replace('.','_')
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
                              namespace=self)
            self._keys[dd['symbol']] = dd['key']
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
            for callback in dd['callback']:  # assume a list of callback functions
               tdlob.when_changed(callback)
         oblist.append(tdlob)                # append the object (or None) to the list
         
      # Make the TDLMenu object from the accumulated oblist:
      if level>0:
         menu = TDLMenu(rr['prompt'], toggle=rr['symbol'], namespace=self, *oblist)
      elif self._mode=='runtime':
         menu = TDLRuntimeMenu(rr['prompt'], toggle=rr['symbol'], namespace=self, *oblist)
      else:
         menu = TDLCompileMenu(rr['prompt'], toggle=rr['symbol'], namespace=self, *oblist)
      self._keys[rr['symbol']] = rr['key']
      self._oblist[rr['key']] = menu
         
      if trace:
         print prefix,'-> (sub)menu =',rr['symbol'],' (n=',len(oblist),')',str(menu)
         for key1 in ['ctrl','radio']:
            if rr.has_key(key1):
               print prefix,'(',key1,':',rr[key1],')'

      # Return the TDLMenu object:
      return menu


   #--------------------------------------------------------------------------
   # Helper functions for option/value/defrec retrieval:
   #--------------------------------------------------------------------------

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

   #--------------------------------------------------------------------------

   def find_changed(self, lookfor=None, trace=False):
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

   #--------------------------------------------------------------------------

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

   #--------------------------------------------------------------------------

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
      TOM = TDLOptionManager ()
      TOM.show('init')
      TOM.add_option('aa', range(4))
      TOM.add_option('bb', range(4))
      # TOM.add_separator(trace=True)
      TOM.start_of_submenu('cc')
      TOM.add_option('aa', range(2,4))
      TOM.add_option('bb', range(1,4))
      TOM.end_of_submenu()
      TOM.add_option('dd', range(4))
      TOM.end_of_submenu()
      menu = TOM.TDLMenu(trace=True)
      print '\n -->',menu,'\n'
   


   if 0:
      # TOM version of below:
      TOM = TDLOptionManager ('TOM')
      TOM.add_option('alltopics', False)
      TOM.add_option('arg1', range(5), more=int)
      
      TOM.start_of_submenu('topic1')
      TOM.add_option('alltopics', False)
      TOM.add_option('arg1', range(5), more=int)
      TOM.add_option('subtopic1', False)
      TOM.add_option('arg1', range(5), more=int)
      TOM.end_of_submenu()
      
      TOM.start_of_submenu('topic2')
      TOM.add_option('alltopics', False)
      TOM.add_option('subtopic2', False)
      TOM.add_option('arg1', range(5), more=int)
      TOM.radio_buttons(trace=True)
      TOM.end_of_submenu()
      
      TOM.start_of_submenu('helpnodes')
      TOM.add_option('allhelpnodes', False)
      TOM.add_option('helpnode_on_entry', False)
      TOM.add_option('helpnode_on_exit', False)
      TOM.add_option('helpnode_helpnode', False)
      TOM.add_option('helpnode_twig', False)
      TOM.add_option('arg1', range(5), more=int)
      TOM.end_of_submenu()
      
      TOM.end_of_submenu()
      TOM.show('before .TDLMenu()')
      itsTDLCompileMenu = TOM.TDLMenu(trace=True)
      TOM.show('after .TDLMenu()')

      if True:
         TOM.find_symbol('subtopic2',trace=True)
         TOM.find_symbol('2_alltopics',trace=True)
         # TOM.find_symbol('alltopics',trace=True)
         # TOM.find_symbol('xxx',trace=True)

      if True:
         TOM.getopt('subtopic2', trace=True)

      if False:
         TOM.find_changed(trace=True)
         TOM.find_changed(trace=True)
   
            
   print '\n** End of standalone test of: TDLOptionManager.py:\n' 

#=====================================================================================






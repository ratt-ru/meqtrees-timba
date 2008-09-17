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
#
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
      self._shapshot = dict()                 # snapshot values (see .make_snapshot())

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

   def add_option (self, relkey, choice,
                   prompt=None, help='help', more=None,
                   callback=None,
                   prepend=False, trace=True):
      """
      Add an TDLOption definition to the menu definitions. Its name is a concatanation
      of the 'current' menu name, and the specified 'relative' key (relkey).
      If prepend=True, prepend it to the already specified list of options.
      """
      if self._complete:
         raise ValueError,'** TOM.add_option(): TDLMenu is complete'

      key = self._current_submenu['key'] + '.' + relkey
      symbol = self.key2symbol(key)
      optdef = dict(type='option', key=key, symbol=symbol,
                    prompt=(prompt or symbol), help=help,
                    callback=callback,
                    choice=choice, more=more)
      self._current_submenu['menu'][key] = optdef
      self.order(key, prepend=prepend, trace=trace)

      if trace:
         print '\n** .add_option(',relkey,') ->',optdef
         print '    current_submenu:\n      ',self._current_submenu
      return key

   #--------------------------------------------------------------------------

   def start_of_submenu (self, relkey,
                         prompt=None, help='help',
                         topmenu=False,
                         prepend=False,
                         trace=True):
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

      symbol = self.key2symbol(key)
      menudef = dict(type='menu', key=key, symbol=symbol,
                     prompt=(prompt or symbol), help=help,
                     order=[], menu=dict())

      if topmenu:                  # topmenu==True ONLY when called from .__init__()
         self._menudef = menudef
         self._current_submenu = self._menudef
      else:
         self._current_submenu['menu'][key] = menudef
         self.order(key, prepend=prepend, trace=trace)                 
         self._current_submenu = self._current_submenu['menu'][key]           # go down one level

      if trace:
         print '\n** .start_of_submenu(',relkey,') -> current_submenu =',self._current_submenu
      return key

   #--------------------------------------------------------------------------

   def end_of_submenu (self, ctrl=True, radio=False, trace=True):
      """
      Revert self._current_submenu to one level higher (done after a menu is complete).
      Subsequent to add_menu() or add_option will now add the new definitions
      to the higher-level menu.
      If ctrl=True, add a group control menu item. 
      If radio=True, make the submenu options mutually exclusive 
      """
      if radio:
         self.radio_buttons(trace=trace)
      if ctrl:
         self.group_control(trace=trace)
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
   # Convenience control of (groups of) options:  
   #--------------------------------------------------------------------------

   def group_control (self, trace=False):
      """Add a group-control button to the current submenu.
      """
      self._current_submenu['ctrl'] = self._current_submenu['order']    # ....??
      choice = ['-','select all','select none','revert to defaults',
                'make snapshot','revert to snapshot']
      self.add_option ('group_ctrl', choice,
                       prompt='group control',
                       help=None, more=None,
                       callback=self.callback_group_control,
                       prepend=True, trace=trace)
      if trace:
         print '\n** .group_control() -> ',self._current_submenu['ctrl']
      return True

   #..........................................................................

   def callback_group_control (self, value):
      print '\n** .callback_group_control(',value,')\n'
      key = self.find_changed()
      print 'key=',key
      if isinstance(key,str):
         menukey = self.menukey(key)
         print 'menukey=',menukey
         menu = self.find_defrec(menukey, trace=True)
         # print EF.format_record(menu)
         print '** menu[order] =',menu['order']
         if value=='select all':
            print value
         elif value=='select none':
            print value
         elif value=='revert to defaults':
            print value
         elif value=='make snapshot':
            print value
         elif value=='revert to snapshot':
            print value
         elif value=='-':
            print 'empty'
         else:
            print 'value not recognised: ',value,type(value),len(value)
         if True:
            # Always reset the option value
            print key,self._oblist.keys()
            option = self._oblist[key]
            option.set_value('-', callback=False)
      return None
   
   #--------------------------------------------------------------------------

   def radio_buttons (self, trace=False):
      """Make the already specified options of the current submenu into
      mutually exclusive 'radio buttons'.
      """
      self._current_submenu['radio'] = self._current_submenu['order']
      if trace:
         print '\n** .radio_buttons() -> ',self._current_submenu['radio']
      return True


   #--------------------------------------------------------------------------
   # Make the TDLMenu (create actual TDLOption objects) from self._menudef:
   #--------------------------------------------------------------------------

   def TDLMenu (self, namespace=None, trace=False):
      """Return the complete TDLMenu object. Create it if necessary.""" 
      if self._complete:                         # already created
         return self._TDLMenu                    # just return it
      # Create the TDLMenu from the self._menudef record:
      # This field is expected by OMS:
      if trace:
         print '\n** _make_TDLMenu(namespace=',namespace,'):'
      print EF.format_record(self._menudef,'menudef')
      self.tdloption_namespace = namespace
      self._complete = True                      # disable any further additions
      # self._keys = dict()
      # self._oblist = dict()
      menu = self._make_TDLMenu(trace=trace)
      self.find_changed()                        # save the current values
      return menu

   #--------------------------------------------------------------------------

   def _make_TDLMenu (self, rr=None, level=0, trace=True):
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
            if dd['callback']:
               tdlob.when_changed(dd['callback'])
               print '\n**',dir(tdlob),'\n'
               print '** tdlob.symbol=',tdlob.symbol
            self._oblist[key] = tdlob

         elif dd['type']=='menu':
            tdlob = self._make_TDLMenu(dd, level=level+1, trace=trace)  # recursive
         else:
            s = '** option type not recognosed: '+str(dd['type'])
            raise ValueError,s
         oblist.append(tdlob)
         
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



   # TDLOption('opt_input_twig',"input twig",
   #           ET.twig_names(), more=str),

   # TDLMenu("topic1",
   #        TDLOption('opt_topic1_alltopics',
   #                  "override: include all topic1 sub-topics",False),
   #        TDLOption('opt_topic1_subtopic1', "topic1 subtopic1",False),
   #        toggle='opt_topic1'),



   #--------------------------------------------------------------------------
   # Helper functions for option/value/defrec retrieval:
   #--------------------------------------------------------------------------

   def find_changed(self, trace=False):
      """Find the key/symbol of the TDLObject whose value has changed
      since the last time this function was called.
      """
      if trace:
         print '\n** .find_changed():'

      changed = []
      for key in self._oblist.keys():
         ob = self._oblist[key]
         if trace:
            print '-',key,'=',ob.value
         if self._lastval.has_key(key):
            lastval = self._lastval[key]
            if not ob.value==lastval:
               print '***',key,'=',ob.value,' (was:',lastval,')'
               changed.append(key)
         self._lastval[key] = ob.value

      # Deal with the result:
      if len(changed)==1:
         return changed[0]
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

   def revert_to_snapshot (self, menu=None, level=0, trace=False):
      """
      Below the given menu defrec, set all options to the snapshot values.
      See also .make_snapshot()
      """
      if level==0:
         if trace:
            print '\n** find_defrec(',key,'):'
         if not isinstance(menu,dict):
            menu = self._menudef

      if menu['key']==key:
         return menu
      if key in menu['order']:
         return menu['menu'][key]
      for key1 in menu['order']:
         dd = menu['menu'][key1]
         if dd['type']=='menu':
            result = self.find_defrec(key, dd, level=level+1, trace=trace)
            if isinstance(result,dict):
               return result
      return False

   #--------------------------------------------------------------------------

   def find_symbol(self, substring, severe=True, trace=False):
      """
      Return an existing symbol (option name) that contains the given substring.
      If severe=True, throw an exeption if not found or ambiguous.
      """
      ss = []
      for s in self.symbols():
         if substring in s:
            ss.append(s)
      s = '** TOM.find_symbol('+substring+'): -> '
      if len(ss)==1:
         if trace:
            print s,ss[0]
         return ss[0]
      # Found zero or more than one:
      s += str(ss)
      if severe:
         raise ValueError,s
      print '\n',s,'\n'
      return ss
      

   #--------------------------------------------------------------------------

   def getopt(self, name, rider=None, globals=None, trace=False):
      """Get the current value of the specified (name) TDLOption name/symbol.
      Only a part of the symbol/name is required, as long as it is not ambiguous.
      If rider is defined, make a qhelp string and add it (see QuickRefUtil.py)
      """
      symbol = self.find_symbol(name, severe=True, trace=trace)
      key = self._keys[symbol]
      value = self._oblist[key].value

      if globals:
         ## cutoff = QRU.getopt(globals(),'opt_FITSImage_cutoff',rider)
         # Read the value from globals (If the name does not exist, notrec is returned):
         # NB: Not recommended (perverse coupling)
         notrec = '_UnDef_'
         value = globals.get(symbol, notrec)

      if rider:
         # See QuickRefUtil.py
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

   if 0:
      # Basic testing
      TOM = TDLOptionManager ()
      TOM.show('init')
      TOM.add_option('aa', range(4))
      TOM.add_option('bb', range(4))
      TOM.start_of_submenu('cc')
      TOM.add_option('aa', range(2,4))
      TOM.add_option('bb', range(1,4))
      TOM.end_of_submenu()
      TOM.add_option('dd', range(4))
      TOM.end_of_submenu()
      menu = TOM.TDLMenu(trace=True)
      print '\n -->',menu,'\n'
   


   if True:
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

      TOM.find_changed(trace=True)
      TOM.find_changed(trace=True)
   
            
   print '\n** End of standalone test of: TDLOptionManager.py:\n' 

#=====================================================================================






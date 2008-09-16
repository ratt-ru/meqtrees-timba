"""
QuickRef module: QR_test.py:

Template for the generation of QR_... modules.

Click on the top bookmark ('help_on__how_to_use_this_module')

Instructions for using this template:
- make a copy to a file with a new name (e.g. QR_<name>.py)
- open this file
- replace the word QR_test with QR_<name>
- remove the parts that are marked 'remove'
.   (they generate the general template documentation)
- remove these instructions
- add content.

"""

# file: ../JEN/QuickRef/QR_test.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 01 oct 2008: creation (from QR-template.py)
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

from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN
from Timba.Contrib.JEN.QuickRef import EasyFormat as EF

from Timba.Contrib.JEN.pylab import PyNodeNamedGroups as PNNG
from Timba.Contrib.JEN.pylab import PyNodePlot as PNP

# import math
# import random
import numpy


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
      symbol = self.key2symbol(self._name)
      self._menudef = dict(type='menu', key=self._name,
                           prompt=prompt or symbol,
                           symbol=symbol,
                           order=[], menu=dict())
      self._current_submenu = self._menudef   

      # The definition record is used to generate the actual TDLOption objects.
      self._TDLmenu = None                    # the final TDLMenu 
      self._oblist = dict()                   # record of TDLOption objects
      self._lastval = dict()                  # last values (see .find_changed())

      # The fields of self._menudef are called keys. They contain dots(.)
      # The option/menu names are derived from keys by .key2symbol(key)
      self._keys = dict()                     # menudef field-names[symbol]

      # Set when the final self._TDLMenu is generated.
      # It then inhibits further additions.
      self._complete = False
      
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
         print '** .add_option(',relkey,') ->',optdef
      return key

   #--------------------------------------------------------------------------

   def start_of_submenu (self, relkey,
                         prompt=None, help='help',
                         prepend=False, trace=True):
      """
      Add an TDLMenu definition to the menu definitions. Its name is a concatanation
      of the 'current' menu name, and the specified 'relative' key (relkey).
      Then go 'down' one level, i.e. set self._current_submenu to the new menu. Subsequent to
      add_menu() or add_option will now add the new definitions to the new menu.
      """
      if self._complete:
         raise ValueError,'** TOM.start_of_submenu(): TDLMenu is complete'

      key = self._current_submenu['key'] + '.' + relkey
      symbol = self.key2symbol(key)
      menudef = dict(type='menu', key=key, symbol=symbol,
                     prompt=(prompt or symbol), help=help,
                     order=[], menu=dict())
      self.order(key, prepend=prepend, trace=trace)
      self._current_submenu['menu'][key] = menudef
      self._current_submenu = self._current_submenu['menu'][key]           # go down one level

      if trace:
         print '** .start_of_submenu(',relkey,') ->',self._current_submenu
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
      ss = oldkey.split('.')
      newkey =  oldkey.replace('.'+ss[-1],'')
      if trace:
         print '** .end_of_submenu(): ',oldkey,'->',newkey
         # print self._menudef
      self._current_submenu = self.find_defrec(newkey)
      return newkey

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
      self._current_submenu['ctrl'] = self._current_submenu['order']
      self.add_option ('group_ctrl',
                       [' ','select all','select none','revert to defaults'],
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
      self.find_changed()
      print
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
      if len(changed)==0:
         return False
      elif len(changed)==1:
         return changed[0]
      else:
         return False
         # raise ValueError,'more than one option has changed??'

   #--------------------------------------------------------------------------

   def find_defrec (self, key, rr=None, level=0, trace=False):
      """
      Find the defenition record with the specified key in self._menudef
      """
      if not isinstance(rr,dict):
         rr = self._menudef
      if rr['key']==key:
         return rr
      if key1 in rr['order']:
         return rr['menu'][key1]
      for key1 in rr['order']:
         dd = rr['menu'][key1]
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
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************

new = True

if False:
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

elif new:
   # TOM version of below:
   TOM = TDLOptionManager ('QR_test')
   TOM.add_option('alltopics', False)
   TOM.add_option('input_twig', ET.twig_names(), more=str)

   TOM.start_of_submenu('topic1')
   TOM.add_option('alltopics', False)
   TOM.add_option('subtopic1', False)
   TOM.end_of_submenu()

   TOM.start_of_submenu('topic2')
   TOM.add_option('alltopics', False)
   TOM.add_option('subtopic2', False)
   TOM.radio_buttons(trace=True)
   TOM.end_of_submenu()

   TOM.start_of_submenu('helpnodes')
   TOM.add_option('allhelpnodes', False)
   TOM.add_option('helpnode_on_entry', False)
   TOM.add_option('helpnode_on_exit', False)
   TOM.add_option('helpnode_helpnode', False)
   TOM.add_option('helpnode_twig', False)
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
   
else:
   oo = TDLCompileMenu("QR_test topics:",
                       TDLOption('opt_alltopics',"override: include all topics",True),
                       
                       TDLOption('opt_input_twig',"input twig",
                                 ET.twig_names(), more=str),
                       
                       TDLMenu("topic1",
                               TDLOption('opt_topic1_alltopics',
                                         "override: include all topic1 sub-topics",False),
                               TDLOption('opt_topic1_subtopic1', "topic1 subtopic1",False),
                               toggle='opt_topic1'),
                       
                       TDLMenu("topic2",
                               TDLOption('opt_topic2_alltopics',
                                         "override: include all topic2 sub-topics",False),
                               TDLOption('opt_topic2_subtopic1', "topic2 subtopic1",False),
                               toggle='opt_topic2'),

                       TDLMenu("help",
                               TDLOption('opt_allhelpnodes',"override: include all helpnodes",False),
                               TDLOption('opt_helpnode_on_entry',"help on QuickRefUtil.on_entry()", False),
                               TDLOption('opt_helpnode_on_exit',"help on QuickRefUtil.on_exit()", False),
                               TDLOption('opt_helpnode_helpnode',"help on QuickRefUtil.helpnode()", False),
                               TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                               toggle='opt_helpnodes'),
                       
                       toggle='opt_QR_test')

   # Assign the menu to an attribute, for outside visibility:
   itsTDLCompileMenu = oo



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************

header = 'QR_test'                    # used in exec functions at the bottom

def QR_test (ns, rider):
# def toplevel (ns, rider):
   """
   NB: This text should be replaced with an overall explanation of the
   MeqTree functionality that is covered in this QR module.
   
   This top-level function has the same name as the module. Its role is to
   include the user-specified parts (topics) of QuickRef documentation by calling
   lower-level functions according to the TDLCompileMenu options.
   This function may be called from QuickRef.py, but also from its standalone
   _define_forest() below, or from the local testing function (without the browser).

   The functions in a QR module use utility functions in QuickRefUtil.py (QRU),
   which do the main work of collecting and organising the hierarchical help,
   and of creating and bundling the nodes of the demonstration trees.

   All functions in a QR module have the following general structure:

   <function_code>
      def func (ns, rider):
         ... function doc-string enclosed in triple-quotes
         stub = QRU.on_entry(ns, rider, func)
         cc = []
         ... function body, in which nodes are appended to the list cc ...
         return QRU.on_exit (ns, rider, cc)
   </function_code>

   The first argument of QRU.on_entry() is the function itself, without ().
   It returns a record rr, the fields of which (rr.path and rr.help) are
   used in the function (or rather, passed to other QRU functions).
   
   The last statement (return QRU.on_exit()) bundles the nodes (cc) in a
   convenient way, and returns the resulting parent node of the bundle.
   Its syntax is given below.
   """
   stub = QRU.on_entry(ns, rider, QR_test)
   cc = []
   override = opt_alltopics
   global header

   # Edit this part:
   if override or opt_topic1:
      cc.append(topic1 (ns, rider))
   if override or opt_topic2:
      cc.append(topic2 (ns, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')


#********************************************************************************

def make_helpnodes (ns, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text in the quickref_help field of its state record. A bookmark is
   generated automatically, with the 'QuickRef Display' viewer.
   The help-text is also added to the subset of documentation that is accumulated
   by the rider.
   """
   stub = QRU.on_entry(ns, rider, make_helpnodes)
   
   override = opt_alltopics or opt_allhelpnodes
   cc = []

   # Replace this part:
   if override or opt_helpnode_on_entry:
      cc.append(QRU.helpnode (ns, rider, func=QRU.on_entry))
   if override or opt_helpnode_on_exit:
      cc.append(QRU.helpnode (ns, rider, func=QRU.on_exit))
   if override or opt_helpnode_helpnode:
      cc.append(QRU.helpnode (ns, rider, func=QRU.helpnode))
   if override or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rider, func=ET.twig))

   return QRU.on_exit (ns, rider, cc, mode='group')



#================================================================================
# topic1:
#================================================================================

def topic1 (ns, rider):
   """
   NB: This text should be replaced with an overall explanation of this 'topic'
   of this QR module.

   The 'topic' functions are '2nd-tier' functions, i.e. they are called from the
   top-level function QR_test() above. They usually call one or more functions
   that represent different 'views' (e.g. demonstration trees of particular aspects)
   of this topic. The general structure is:

   <function_code>
     def topic1 (ns, rider):
          stub = QRU.on_entry(ns, rider, topic1)
          cc = []
          override = opt_topic1_alltopics
          if override or opt_topic1_subtopic:
              cc.append(topic1_subtopic (ns, rider))
          return QRU.on_exit (ns, rider, cc)
   </function_code>

   It is sometimes useful to read some general TDLCompileOptions here, and pass
   them to the subtopic functions as extra arguments.
   """
   stub = QRU.on_entry(ns, rider, topic1)
   cc = []
   override = opt_alltopics

   if override or opt_topic1_subtopic1:
      cc.append(topic1_subtopic1 (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')


#================================================================================

def topic1_subtopic1 (ns, rider):
   """
   NB: This text should be replaced with an overall explanation of this subtopic of
   this topic of this QR module.

   A subtopic (topic_subtopic()) demonstrates a particular aspect of a given topic.
   It usually generates a group of 4-9 related nodes that may be displayed on a
   single bookmark page.

   The EasyTwig (ET) module may be used to generate small standard subtrees (twigs)
   that may serve as (user-defined) inputs to a demonstration subtree. Its syntax is
   given as a separate 'helpnode' item above. 
   """
   stub = QRU.on_entry(ns, rider, topic1_subtopic1)
   cc = []

   return QRU.on_exit (ns, rider, cc)




#================================================================================
# topic2:
#================================================================================

def topic2 (ns, rider):
   """
   topic2 covers ....
   """
   stub = QRU.on_entry(ns, rider, topic2)
   cc = []
   override = opt_alltopics

   if override or opt_topic2_subtopic1:
      cc.append(topic2_subtopic1 (ns, rider))
   if override or opt_topic2_subtopic2:
      cc.append(topic2_subtopic2 (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')


#================================================================================

def topic2_subtopic1 (ns, rider):
   """
   topic2_subtopic1 treats ....
   """
   stub = QRU.on_entry(ns, rider, topic2_subtopic1)
   cc = []

   return QRU.on_exit (ns, rider, cc)

#================================================================================

def topic2_subtopic2 (ns, rider):
   """
   topic2_subtopic2 treats ....

   <warning>
   ... text enclosed in 'html' warning tags is rendered like this ...
   </warning>

   <error>
   ... text enclosed in 'html' error tags is rendered like this ...
   </error>

   <remark>
   ... text enclosed in 'html' remark tags is rendered like this ...
   </remark>

   Text enclosed in 'html' function_code tags may be used to include the function body in the help.
   Just copy the entire function body between the tags in the function doc-string (making sure that
   it does not contain any double-quotes). When the function body is modified, just re-copy it.
   (NB: it would be nice if there were a python function that turned the function body into s atring...)

   <function_code>
   stub = QRU.on_entry(ns, rider, topic2_subtopic2)
   cc = []

   twig = ET.twig(ns,'f')

   for q in ['Sin','Cos','Tan']:
      cc.append(stub(q) << getattr(Meq,q)(twig))
      cc.append('** inserted extra help on '+q+' as string items in nodes (cc) **')

   for q in ['Asin','Acos','Atan']:
      cc.append(dict(node=stub(q) << getattr(Meq,q)(twig)))

   bhelp = \"\"\"
   It is also possible to append extra bundle help
   via the .on_exit() help argument.
   \"\"\"
   return QRU.on_exit (ns, rider, cc, help=bhelp)
   </function_code>


   """

   stub = QRU.on_entry(ns, rider, topic2_subtopic2)
   cc = []

   twig = ET.twig(ns,'f')

   for q in ['Sin','Cos','Tan']:
      cc.append(stub(q) << getattr(Meq,q)(twig))
      cc.append('** inserted extra help on '+q+' as string items in nodes (cc) **')

   for q in ['Asin','Acos','Atan']:
      cc.append(dict(node=stub(q) << getattr(Meq,q)(twig)))

   bhelp = """
   It is also possible to append extra bundle help
   via the .on_exit() help argument.
   """
   return QRU.on_exit (ns, rider, cc, help=bhelp)











#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   # TDLRuntimeMenu(":")
   # TDLRuntimeMenu("QR_test runtime options:", QRU)
   # TDLRuntimeMenu(":")

   global rootnodename
   rootnodename = 'QR_test'                 # The name of the node to be executed...
   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider(rootnodename)       # the rider is a CollatedHelpRecord object

   # Make a 'how-to' help-node for the top bookmark:
   QRU.how_to_use_this_module (ns, rider, name='QR_test',
                               topic='template for QR modules')

   # Execute the top-level function, and dispose of the resulting tree:
   if False:
      QRU.on_exit (ns, rider,
                   nodes=[QR_test(ns, rider)],
                   mode='group', finished=True)

   # Finished:
   return True


#--------------------------------------------------------------------------------
# Functions for executing the tree:
#--------------------------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
   """Execute the tree, starting at the specified rootnode,
   with the ND request-domain (axes) specified in the
   TDLRuntimeOptions (see QuickRefUtils.py)"""
   return QRU._tdl_job_execute (mqs, parent, rootnode=rootnodename)


def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode=rootnodename)


if False:
   def _tdl_job_execute_MS (mqs, parent):
      """Execute a Measurement Set (MS)""" 
      return QRU._tdl_job_execute_MS (mqs, parent, vdm_node='VisDataMux')

#--------------------------------------------------------------------------------
# Some functions to dispose of the specified subset of the documentation:
#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   """Dummy tdl job that acts as separator in the TDL exec menu.""" 
   return QRU._tdl_job_m (mqs, parent)



def _tdl_job_print_hardcopy (mqs, parent):
   """
   Print a hardcopy of the specified subset of the help doc on the printer.
   NB: The printer may be customized with the runtime options.
   NB: As an alternative, the file QuickRef.html may be printed from the
   html browser (assuming that the file is updated automatically).
   """
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header=header)



def _tdl_job_save_doc_to_QuickRef_html (mqs, parent):
   """
   NB: This should be done automatically in all QR_ modules...
   """
   return QRU.save_to_QuickRef_html (rider, filename=None)



def _tdl_job_show_doc (mqs, parent):
   """
   Show the specified subset of the help doc in a popup.
   Obselete...?
   """
   return QRU._tdl_job_show_doc (mqs, parent, rider, header=header)




#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_test.py:\n' 


   ns = NodeScope()
   rider = QRU.create_rider()             # CollatedHelpRecord object

   if 0:
      print EF.format_record(globals(),'globals')

   if 0:
      QR_test(ns, 'test', rider=rider)
      if 1:
         print rider.format()
            
   print '\n** End of standalone test of: QR_test.py:\n' 

#=====================================================================================






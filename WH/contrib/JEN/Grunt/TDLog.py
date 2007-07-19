# TDLog.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Gui to log and inspect the Tree Definition process
#
# History:
#    - 04 mar 2007: creation (from MXM ArgBrowser.py)
#
# Full description:
#
#
# To be done:


#================================================================================
# Preamble
#================================================================================

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

import sys
import pickle

from qt import *
from copy import deepcopy

from Timba.TDL import *

# Name of autosave save/restore file (see .save_inarg()):
auto_save_file = 'auto_save.inarg'


#================================================================================
#================================================================================

def help():
    """This is the help for JEN_inargGui.py"""
    return True

#================================================================================
#================================================================================


class MyListViewItem (QListViewItem):

    def set_text_color(self, color=None):
        if color==None: color = 'black'
        self.__text_color = color
    
    def paintCell (self,painter,cg,column,width,align):
        cg1 = QColorGroup(cg)
        cg1.setColor(QColorGroup.Text, QColor(self.__text_color))
        return QListViewItem.paintCell(self,painter,cg1,column,width,align)
      

#================================================================================
#================================================================================

class TDLog(QMainWindow):
    
    def __init__(self, parent=None, externalMenuItems=[]):

        # Attach the (optional) list of external menu item definitions:
        self.__externalMenuItems = externalMenuItems

        if not parent:
            self.__QApp = QApplication(sys.argv)
            QMainWindow.__init__(self, parent, None, Qt.WType_Dialog|Qt.WShowModal)
	else:
	    self.__QApp = parent
            QMainWindow.__init__(self)
	
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)

        fl = Qt.WType_TopLevel|Qt.WStyle_Customize
        fl |= Qt.WStyle_DialogBorder|Qt.WStyle_Title
        self.setWFlags(fl)

        #----------------------------------------------------
        # The basic layout: Stack widgets vertically in vbox
        
        vbox = QVBoxLayout(self)

        #----------------------------------------------------
        # Menubar (at the end...!?):
        self.__menubar = self.menuBar()

        menu = QPopupMenu(self)
        menu.insertItem('open ...', self.open_filter)
        menu.insertItem('open autosaved', self.open_autosaved)
        menu.insertSeparator()     
        menu.insertItem('saveAs ...', self.saveAs_inarg)
        menu.insertItem('save', self.save_inarg)
        menu.insertItem('autosave', self.autosave)
        menu.insertSeparator()     
        # menu.insertItem('print', self.print_inarg)
        menu.insertSeparator()     
        menu.insertItem('close', self.closeGui)
        self.__menubar.insertItem('File', menu)


        menu = QPopupMenu(self)
        self.__menubar.insertSeparator()
        self.__menubar.insertSeparator()
        menu.insertItem('MG scripts', self.viewMGScripts)
        menu.insertItem('MeqTrees', self.viewMeqTrees)
        self.__menubar.insertSeparator()
        # k = menu.insertItem('help', self.viewHelp)
        # menu.setWhatsThis(k, '...text...')    # better: QToolTip...
        self.__menubar.insertItem('Help', menu)


        #----------------------------------------------------
        # The text window:
        self.__tw = None
        # self.__floatw = None
        if True:
            hbox = QHBoxLayout(vbox)
            vtbox = QHBoxLayout(hbox)
            self.__tw = QTextEdit(self)
            self.__tw.setReadOnly(True)
            # self.__tw.resizeContents(1000,500)  # has NO effect....
            vbox.setStretchFactor(self.__tw, 1)
            hbox.addWidget(self.__tw)
            



        #----------------------------------------------------
        # The listview displays the inarg record:
        self.__listview = QListView(self)
        if False:
            # self.setCentralWidget(self.__listview)
            vbox.addWidget(self.__listview)
            vbox.setStretchFactor(self.__listview, 5)

            color = QColor()
            color.setRgb(240,240,255)                      # 0-255
            self.__listview.setPaletteBackgroundColor(color)
            
            self.__listview.addColumn("name", 350)
            self.__listview.addColumn("value",200)
            self.__listview.addColumn("help", 500)
            self.__listview.addColumn("iitd")
            self.__listview.addColumn("order")
            self.__listview.setSorting(4)                  # sort on 'order' 
            self.__listview.setRootIsDecorated(1)
            
            self.__find_item = None
        

        #----------------------------------------------------
        # Buttons to be added at the bottom:
        hbox = QHBoxLayout(vbox)

        b = QPushButton('Resume', self)
        QToolTip.add(b, 'Resume with the inarg record that was autosaved at Proceed')
        QObject.connect(b, SIGNAL("pressed ()"), self.open_autosaved)
        # hbox.addWidget(b)

        b = QPushButton('Open', self)
        QToolTip.add(b, 'Open a new inarg record')
        QObject.connect(b, SIGNAL("pressed ()"), self.open_filter)
        # hbox.addWidget(b)

        b = QPushButton('Save', self)
        QToolTip.add(b, 'Save the current inarg record')
        QObject.connect(b, SIGNAL("pressed ()"), self.save_inarg)
        hbox.addWidget(b)

        b = QPushButton('Proceed', self)
        QToolTip.add(b, 'Proceed with the current inarg record')
        # QObject.connect(b, SIGNAL("pressed ()"), self.exec_with_inarg)
        # hbox.addWidget(b)

        b = QPushButton('Cancel', self)
        QToolTip.add(b, 'Cancel the gui, and do nothing')
        # QObject.connect(b, SIGNAL("pressed ()"), self.cancel_exec)
        hbox.addWidget(b)

        #----------------------------------------------------
        # Message label (i.s.o. statusbar):
        self.__message = QLabel(self)
        font = QFont("times")
        font.setBold(True)
        # self.__message.setFont(font)
        self.__message.setText(' ')
        vbox.addWidget(self.__message)



        #-------------------------------------------------------
        # Initialise:
        self.__popup = None                        # popup object (editing)
        self.clearGui()
        self.__unhide = False                      # if True, show hidden arguments too
        self.__show_CTRL = False                   # if True, show CTRL_records
        # self.show_CTRL(False, refresh=False)
        self.__find_item = None                    # see self.refresh()
        self.__set_open = True                     # see .recurse()
        self.__setOpen = dict()                    # see .recurse()
        self.__result = None                       # output for exec_loop
        self.__inarg = None                        # the current inarg
        self.__inarg_input = None                  # the input inarg (see .revert_inarg())
        self.__other = None                        # another inarg (e.g. for comparison)
        self.__modified = False                    # if True, self.__inarg has been modified
        self.__closed = False
        return None



    def insertExternalMenuItems(self, menu, name='*'):
        """Insert the relevant (menuname) external item(s) in into the given menu.
        The list will have been passed in the constructor (see above).
        (See for instance MG_JEN_cps.py)"""
        menu.insertSeparator()
        # print 'len(emi) =',len(self.__externalMenuItems)
        for i in range(len(self.__externalMenuItems)):
            rr = self.__externalMenuItems[i]
            rr.setdefault('menu', '*')
            rr.setdefault('display', False)
            # print rr
            if rr['menu']==name:
                if rr['display']:
                    menu.insertItem(rr['prompt'], rr['callback'])
                else:
                    menu.insertItem(rr['prompt'], rr['callback'])
        menu.insertSeparator()     
        return True

    def QApp (self):
        """Access to the QApplication"""
        return self.__QApp

    def closeGui (self):
        """Close the gui"""
        self.clearGui()
        # if self.__popup: self.__popup.close()
        # if self.__floatw: self.__floatw.close()
        self.__listview.close()                    #............?
        self.close()
	self.__closed = True;                      #............?
        # clean up any signal connections?
        return True

    def closeEvent (self,ev):
        """Callback function for close"""
        self.__closed = True
    	return QMainWindow.closeEvent(self,ev)

    def clearGui (self):
        """Clear the gui"""
        self.__listview.clear()
        self.__itemdict = []                       # list of itd records
        # self.__setOpen = dict()        
        self.__CTRL_count = 1000                   # for generating unique numbers
        self.__record_count = 2000                 # for generating unique numbers
        self.__sep_count = 5000                    # for generating unique numbers
        self.__item_count = 100000                 # for generating unique numbers
        return True
    
    #---------------------------------------------------------------------------
    # Functions dealing with text-window(s):
    #---------------------------------------------------------------------------



    def tw(self, text=None):
        """Display the given text on the gui text-window"""
        print '.tw(',text,')'
        self.__tw.setText(str(text))
        return False

    def append(self, text=None):
        """Append the given text on the gui text-window"""
        print '.append(',text,')'
        self.__tw.append(str(text))
        return False





#-------------------------------------------------------------------

    def open_inarg(self):
        """Read a saved inarg record from a file, using a file browser"""
        return self.open_browse(file_filter="*.inarg")

    def open_filter(self):
        """Like open_inarg(), but using the file_filter from the current inarg.
        In the case of staring an MG script, this restricts the choice to .inarg
        files that are relevant to this script"""
        ff = JEN_inarg.CTRL(self.__inarg, 'file_filter')
        return self.open_browse(file_filter=ff)

    def open_browse(self, file_filter="*.inarg"):
        """Read a saved inarg record from a file, using a file browser"""
        filename = QFileDialog.getOpenFileName("", file_filter, self)
        filename = str(filename)
        return self.restore_inarg(filename)

    def autosave(self):
        """Save the inarg record into the auto_save_file"""
        self.save_inarg(auto_save_file, override=True)
        return True

    def open_autosaved(self):
        """Recover the inarg record that was saved automatically when pressing
        the 'Proceed' button. This allows continuation from that point"""
        print 'open_autosaved(): before'
        self.restore_inarg(auto_save_file)
        print 'open_autosaved(): after'
        return True

#-------------------------------------------------------------------



    #------------------------------------------------------------------------------------

    def saveAs_inarg(self):
        """Save the (edited) inarg record for later use"""
        filename = ""
        if True:
            # Make a default filename (dangerous?)
            filename = JEN_inarg.CTRL(self.__inarg, 'save_file')
            filename = filename.split('.inarg')[0]       # remove .inarg, if necessary 
            filename = filename.split('_protected')[0]   # remove _protected, if necessary
            filename += '_<qual>'
        filename = QFileDialog.getSaveFileName(filename, "*.inarg", self)
        filename = str(filename)
        print '** self.saveAs(): filename =',filename
        if filename:
            # The current inarge record (saved in savefile)
            # becomes the reference inarg for the one in this new file: 
            savefile = JEN_inarg.CTRL(self.__inarg, 'save_file')
            JEN_inarg.CTRL(self.__inarg, 'reference', savefile)
            # Remove the protection of the new inarg, if any:
            JEN_inarg.CTRL(self.__inarg, 'protected', False)
            self.save_inarg(filename)
        else:
            self.__message.setText('** cancelled: done nothing')
        return True


    #-------------------------------------------------------------------------------

    def save_inarg(self, filename=None, override=False):
        """Save the (edited) inarg record for later use"""

        is_auto_save_file = (filename==auto_save_file)

        if JEN_inarg.CTRL(self.__inarg, 'protected') and (not override):
            s1 = '** Protected: Use saveAs ... to save it under a different name'
            self.__message.setText(s1)
            return False

        if not JEN_inarg.is_OK(self.__inarg):
            s1 = '** Something wrong with the inarg record:    done nothing...'
            self.__message.setText(s1)
            return False

        if filename==None:                           # routine save under same name
            filename = JEN_inarg.CTRL(self.__inarg, 'save_file') 
        else:                                        # save under a different filename
            oldfile = JEN_inarg.CTRL(self.__inarg, 'save_file') 
            JEN_inarg.HISTORY(self.__inarg, 'Derived from: '+oldfile)

        # Make sure that the current inarg has the correct save_file name:
        filename = str(filename)
        filename = filename.split('.inarg')[0]       # remove .inarg, if necessary 
        filename += '.inarg'                         # append .inarg file extension
        if not is_auto_save_file:
            self.savefile_name(filename)             # change the filename

        # Save the file without any setOpen info (causes segmentation violation)
        wasOpen = self.__setOpen                     # keep for restore (see below)               
        self.__setOpen = dict()                      # clear
        
        # Write to file:
        f = open(filename,'wb')
        p = pickle.Pickler(f)
        r = p.dump(self.__inarg)
        f.close()
        self.__message.setText('** saved inarg record to file:   '+filename)

        # Finish up:
        self.__setOpen = wasOpen                     # restore old situation
        return True

    #-------------------------------------------------------------------------------

    def revert_inarg(self):
        """Revert to the original (input) inarg values"""
        self.__inarg = deepcopy(self.__inarg_input)
        self.__setOpen = dict()                      # clear
        self.refresh()
        self.savefile_name()     
        self.__message.setText('** reverted to the original (input) inarg record')
        return True


    def restore_inarg(self, filename=None, other=False):
        """Read a saved inarg record from a file"""
        filename = str(filename)                     # filename is required!
        try:
            f = open(filename,'rb')
        except:
            self.__message.setText('** restore: file does not exist:  '+filename)
            return False
        p = pickle.Unpickler(f)
        inarg = p.load()
        f.close()

        # Make the inarg ready for further processing:
        if other:
            self.__other = inarg
            self.__message.setText('** Read OTHER inarg record from file:   '+filename)
        else:
            self.input(inarg)    
            self.__message.setText('** New current inarg record from file:   '+filename)
        return True


    #-------------------------------------------------------------------------------

    def viewHelp(self):
        ss = help.__doc__
        return self.tw(ss)

    def viewMeqTrees(self):
        return self.tw('MeqTrees are great')

    def viewMGScripts(self):
        return self.tw('MG Scripts are great')



    #-------------------------------------------------------------------------------
    # Input of a inarg record:
    #-------------------------------------------------------------------------------

    def input (self, inarg=None, set_open=True):
        """Input of a new (inarg) record in the gui"""
        if not isinstance(inarg, dict): return False
        self.clearGui()
        self.__inarg = deepcopy(inarg)                          # to be edited
        self.__inarg_input = deepcopy(inarg)                    # unchanged copy

        # Check whether the inarg record is protected:
        if JEN_inarg.CTRL(self.__inarg, 'protected')==None:
            JEN_inarg.CTRL(self.__inarg, 'protected', False)    # just in case
            
        # Deal with the savefile name (in the CTRL_record):
        s1 = '** input of inarg record:  '
        savefile = self.savefile_name()
        self.__message.setText(s1+'  '+savefile)
        print s1+'  '+savefile

        # Transfer the inarg fields recursively:
        self.__set_open = set_open
        self.refresh()

        # Display the description:
        self.viewSpecific()

        # Connect signals and slots, once a signal is detected the according slot is executed
        # QObject.connect(self.__listview, SIGNAL("doubleClicked (QListViewItem * )"), self.itemSelected)
        QObject.connect(self.__listview, SIGNAL("clicked (QListViewItem * )"), self.itemSelected)

        self.show()
        return True

    #--------------------------------------------------------------------------

    def refresh (self, clear=True):
        """Refresh the listview widget from self.__inarg"""
        if clear: self.clearGui()
        self.recurse (self.__inarg, listview=self.__listview)
        if self.__find_item:
            # Find the specified list item (see self.itemSelected())
            item = self.__listview.findItem(self.__find_item, 4)
            self.__listview.ensureItemVisible(item)
            # The problem is that the item is visble at the BOTTOM of the window.
            # It would be better to have it at the top....!
        self.test_OK(judgement=False)
        return True

    #--------------------------------------------------------------------------

    def recurse (self, rr=None, listview=None, level=0, module='<module>',
                 makeitd=True, color=None, trace=False):
        """Recursive input of a hierarchical inarg record"""
        if not isinstance(rr, dict): return False

        # trace = True

        if makeitd:
            # Make sure that there is a CTRL_record for iitd storage:
            rr.setdefault(CTRL_record, dict())
            if not isinstance(rr[CTRL_record], dict): rr[CTRL_record] = dict()
            # Its 'kident' (see above) record is used to store unique identifiers (iitd)
            rr[CTRL_record].setdefault(kident, dict())

        # If an order (list) is supplied, use that. Otherways, use the rr.keys() order.
        # NB: This is NOT sufficient to get the list-items sorted in this order,
        #     because by default they are sorted alphabetically on the first column.
        #     So, a column of unique numbers is generated, and used for sorting...
        order = JEN_inarg.CTRL(rr, 'order', report=False)
        if order==None:
            order = rr.keys()
        else:
            for key in rr.keys():
                if not key in order:
                    order.append(key)
        if trace:
            print 'order =',order
            
        # Create the listview items:
        for key in order:
            self.__item_count += 1                             # overall item count
            if trace:
                print JEN_inarg._prefix(level),self.__item_count,key

            if isinstance(rr[key], dict):   
                if key==CTRL_record:                           # is a CTRL record         
                    self.__CTRL_count += 1                     # increment the counter
                    if self.__show_CTRL:
                        CTRL_ident = str(-self.__CTRL_count)
                        item = MyListViewItem(listview, key, 'CTRL_record', '',
                                              CTRL_ident, str(self.__item_count))
                        item.set_text_color('green')
                        item.setSelectable(False)
                        key1 = CTRL_record+'_'+str(CTRL_ident) # unique name
                        if rr[key].has_key('ERROR'):           # special case
                            # item.set_text_color('orange')
                            self.__setOpen[key1] = True        # set open     
                        elif rr[key].has_key('WARNING'):       # special case
                            # item.set_text_color('orange')
                            self.__setOpen[key1] = True        # set open     
                        if self.__setOpen.has_key(key1):
                            item.setOpen(self.__setOpen[key1]) # open or close    
                        self.recurse (rr[key], listview=item, color='green',
                                      level=level+1, makeitd=False)

                elif key.rfind(sep_record)>-1:                 # is a separator         
                    self.__sep_count += 1                      # increment the counter
                    sep_ident = str(-self.__sep_count)
                    item = MyListViewItem(listview, '*** '+str(rr[key]['txt'])+' ***',
                                          '*********************', '************',
                                          sep_ident, str(self.__item_count))
                    item.set_text_color('magenta')
                    item.setSelectable(False)

                else:
                    skip = JEN_inarg.check_skip(rr, key)
                    skip = False               # Temporary: editing does not work!! 
                    if not skip:
                        # A record (perhaps an inarg sub-record):
                        text = QString(key)
                        iitd = str(-2)
                        self.__record_count += 1                   # increment the counter
                        R_ident = str(-self.__record_count)
                        item = MyListViewItem(listview, text, '', '',
                                              R_ident, str(self.__item_count))
                        item.setSelectable(False)
                        
                        if key=='stream_control':                  # See MG_JEN_Cohset.py
                            # Temporary kludge, until this feature is implemented properly
                            self.__setOpen[key] = True             # set open     
                            
                        color1 = color
                        if not JEN_inarg.is_OK(rr[key]):           # contains an error/warning
                            item.set_text_color('red')
                            # self.__setOpen[key] = True             # set open     
                            self.show_CTRL(True, refresh=False)
                        elif key in ['ERROR','WARNING']:           # special cases
                            self.__setOpen[key] = True             # set open     
                            color1 = 'red'                         # pass down
                            item.set_text_color('red')
                        elif color:                                # color specified (e.g. CTRL)
                            item.set_text_color(color)
                        else:
                            item.set_text_color('blue')            # default: highlight it
                        if self.__set_open and level==0:
                            item.setOpen(True)                     # show its children
                        if self.__setOpen.has_key(key):
                            item.setOpen(self.__setOpen[key])      # open or close    

                        self.recurse (rr[key], listview=item, level=level+1,
                                      module=key, makeitd=makeitd, color=color1)

            elif not makeitd:
                # E.g. the fields inside a CTRL_record:
                item = MyListViewItem(listview, key, str(rr[key]), '',
                                      '', str(self.__item_count))
                item.set_text_color(color)


            else:                                              # rr[key] is a value
                itd = self.make_itd(key, rr[key], ctrl=rr[CTRL_record], module=module)
                nohide = ((not itd['hide']) or self.__unhide)
                if nohide:
                    v = itd['value']                           # current value
                    if isinstance(v, str):
                        nchar = len(v)                         # nr of chars
                        chmax = 20                             # max nr of chars
                        if nchar>chmax:                        # string too long
                            v = '... '+v[(nchar-chmax+1):nchar] # show the LAST bit
                    elif isinstance(v, (list,tuple)):
                        nv = len(v)                            # nr of list elements
                        nmax = 4
                        if nv>nmax:                            # too many elements
                            # Show the LAST few elements
                            v = '(n='+str(nv)+') ... '+str(v[(nv-nmax+1):nv])
                    value = str(v)
                    iitd = str(itd['iitd'])                    # used by selectedItem()
                    rr[CTRL_record][kident][key] = itd['iitd'] # unique local identifier
                    help = ' '                                 # short explanation
                    if itd['help']:
                        help = str(itd['help'])
                        hh = help.split('\n')
                        if len(hh)>1: help = hh[0]+'...'       # first line only
                        nchar = len(help)                      # nr of chars
                        chmax = 40                             # max nr of chars
                        if nchar>chmax:                        # string too long
                            help = help[:chmax]+'...'
                    item = MyListViewItem(listview, key, value, help,
                                          iitd, str(self.__item_count))
                    if itd['hide']:
                      item.set_text_color('grey')
                    else:
                      item.set_text_color(color)
                      

        return True



    #-------------------------------------------------------------------------------
    # (Move to JEN_inarg.py)

    def make_itd(self, key, value, ctrl=None,
                 color='black', hide=False,
                 module='<module>', qual=None,
                 save=True, level=0, trace=False):
        """Make an itd record from the given value and ctrl-record"""
        itd = dict(key=str(key),
                   value=value,                
                   mandatory_type=None,       # mandatory item type 
                   color=color,               # Display color  
                   hide=hide,                 # If True, hide this item
                   help=None,                 # help string
                   choice=None,               # list of choices
                   range=None,                # list [min,max]
                   min=None,                  # Allowed min value
                   max=None,                  # Allowed max value
                   editable=True,             # If True, the value may be edited
                   mutable=True,              # If True, the value may be modified
                   vector=False,              # If True, the value is a vector/list
                   browse=None,               # Extension of files ('e.g *.MS')
                   callback=None,             # see valueChanged()
                   module=module,             # name of the relevant function module
                   qual=None,                 # its qualifier
                   oneliner='<oneliner>',
                   description='<description>',            
                   level=level,               # inarg hierarchy level
                   iitd=-1)                   # sequenc nr in self.__itemdict

        # If ctrl is a record, use its information:
        if isinstance(ctrl, dict):
            # First some overall (script_specific) fields:
            overall = ['color','oneliner','description','qual']
            for field in overall:
                if ctrl.has_key(field):
                    itd[field] = ctrl[field]
            # Then the key-specific keys (see JEN_inarg.define()):
            key_specific = ['choice',
                            'editable','hide','color',
                            'mutable','vector',
                            'mandatory_type','browse',
                            'callback',
                            'range','min','max','help']
            for field in key_specific:
                if ctrl.has_key(field):
                    if ctrl[field].has_key(key):
                        itd[field] = ctrl[field][key]

        # Override some fields, if required:
        if itd['range']:
            if not isinstance(itd['range'], (tuple,list)):
                itd['range'] = 'error: '+str(type(itd['range']))
            elif not len(itd['range'])==2:
                itd['range'] = 'error: len ='+str(len(itd['range']))
            else:
                itd['min'] = itd['range'][0]
                itd['max'] = itd['range'][1]
        if not itd['choice']==None:
            if not isinstance(itd['choice'], (tuple,list)):
                itd['choice'] = [itd['choice']]
        if itd['help']:
            prefix = ''
            if itd['hide']: prefix = '(hidden) '
            itd['help'] = prefix+str(itd['help'])

        # Keep the itemdict for later reference:
        if save:
            itd['iitd'] = len(self.__itemdict)
            self.__itemdict.append(itd)
        if trace:
            print itd
        return itd

    #-------------------------------------------------------------------------------

    def itemSelected(self, item):
        """Deal with a selected listview item"""

        trace = False
        s1 = '.itemSelected(): '

        # Disable (see also below):
        self.__find_item = None

        # If +/- clicked, the item is None:
        if not item:
            print s1,'no item: type =',type(item)
            return False
        
        # Read the (string) values from the columns:
        key = str(item.text(0))            
        # vstring = str(item.text(1))           
        # help = str(item.text(2))              
        iitd = str(item.text(3))          
        unique = str(item.text(4))          
        if self.__popup:
            self.__popup.close()

        # Use the iitd string to get the relevant itemdict record:
        if iitd==' ': iitd = '-1'
        s1 += ' key='+str(key)+' (iitd='+str(iitd)+', unique='+str(unique)+'): '
        try:
            iitd = int(iitd)
        except:
            if trace:
                print s1,'error'
                print sys.exc_info()
            return False

        if iitd>=0:
            # A regular item: launch a popup for editing:
            if trace: print s1,'regular item: launch a popup'
            itd = self.__itemdict[iitd]
            self.__current_iitd = iitd
            self.__find_item = unique
            # Make the popup object:
            self.__popup = Popup(self, name=itd['key'], itd=itd)
            QObject.connect(self.__popup, PYSIGNAL("popupCommit()"), self.popupCommit)
            QObject.connect(self.__popup, PYSIGNAL("popupCancel()"), self.popupCancel)

        elif iitd<-2000:
            # A record (see self.__record_count): open or close it (toggle):
            had = self.__setOpen.has_key(key)
            self.__setOpen.setdefault(key, False)
            was = self.__setOpen[key]
            self.__setOpen[key] = not self.__setOpen[key]   # toggle
            self.__find_item = unique
            if trace: print s1,'record: setOpen[key]:',had,was,'->',self.__setOpen[key]
            self.refresh()
            # Display the description of this module:
            descr = JEN_inarg.description(self.__inarg, module=key)
            self.tw('** Description of module:   '+key+':\n\n   '+descr)

        elif iitd<-1000:
            # A CTRL record (see self.__CTRL_count):
            CTRL_ident = iitd                               # see .recurse()
            key1 = CTRL_record+'_'+str(CTRL_ident)          # unique name
            self.__setOpen.setdefault(key1, False)
            self.__setOpen[key1] = not self.__setOpen[key1] # toggle
            if trace: print s1,'CTRL record: setOpen[key1] ->',self.__setOpen[key1]
            self.__find_item = unique
            self.refresh()

        else:
            print s1,'** iitd not recognised **'
            
        return True

    #-------------------------------------------------------------------------------

    def popupCancel(self):
        """Action upon pressing the popup Cancel button"""
        self.refresh()
        self.__message.setText('** popup cancelled')
        return True

    def popupCommit(self, itd):
        """Action upon pressing the popup OK (Commit) button"""
        # Replace the relevant itemdict with the modified one:
        iitd = self.__current_iitd                # its position in self.__itemdict
        self.__itemdict[iitd] = itd               # replace in self.__itemdict
        self.__modified = True                    # self.__inarg has been modified
        self.replace (self.__inarg, itd, trace=False)
        if itd['callback']:
            print '\n** popupCommit(): callback =',itd['callback'],'\n'
            if itd['key']=='punit':
                self.callback_punit(itd['value'], qual=itd['qual'])
        self.refresh()
        return True

    def callback_punit(self, punit, qual=None):
        """Kludge to modify all NEWSTAR parameters for a predefined punit"""
        from Timba.Contrib.JEN import MG_JEN_Sixpack
        pp = dict(punit=punit)
        MG_JEN_Sixpack.predefined(pp)
        print '** callback_punit(',punit,'): predefined(pp) ->\n   ',pp,'\n'
        pp[option_field] = dict(severe=False, qual=qual)
        JEN_inarg.modify(self.__inarg, **pp)
        return True

    def replace (self, rr=None, itd=None, level=0, trace=False):
        """Replace the modified value in self.__inarg"""
        if not isinstance(rr, dict): return False

        # Search for the correct iitd identifier:
        if rr.has_key(CTRL_record):
            if not rr[CTRL_record].has_key(kident):
                # This may happen if the record has been skipped (See .recurse())
                return True                            # escape, do not recurse
            iitd = rr[CTRL_record][kident]
            for key in iitd.keys():
                if trace: print '-',level,key,':',iitd[key],itd['iitd'],
                if iitd[key]==itd['iitd']:             # found
                    was = rr[key]
                    rr[key] = itd['value']             # replace value
                    if trace: print 'found'
                    self.__message.setText('** replaced:  '+key+': '+str(was)+' -> '+str(rr[key]))
                    return True                        # escape
                if trace: print 

        # If not yet found, recurse:
        for key in rr.keys():
            if isinstance(rr[key], dict):   
                if not key==CTRL_record:             
                    found = self.replace (rr[key], itd=itd,
                                          level=level+1, trace=trace)
                    if found: return True          # escape
        # Not found
        print 'not found'
        return False


    def launch (self):
        """Launch the inargGui"""
        self.show()
        self.__QApp.connect(self.__QApp, SIGNAL("lastWindowClosed()"),
                            self.__QApp, SLOT("quit()"))
        self.__QApp.exec_loop()
        return True

    def exec_loop (self):
    	self.show();
	print "__closed is",self.__closed
	while not self.__closed:
            qApp.processEvents();
	print "__closed is",self.__closed
	return self.__result









#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
# Floating text-editor:
#----------------------------------------------------------------------------
        
class Float(QDialog):
    def __init__(self, parent=None, name='float_name', text=None, readonly=True):
        QDialog.__init__(self, parent, "Test", 0, 0)

        self.setGeometry(200,200,800,700)
        # self.setMinimumWidth(800)
        # self.setMinimumHeight(400)

        # Put in widgets from top to bottom:
        vbox = QVBoxLayout(self,10,5)     

        self.__tw = QTextEdit(self)
        self.__readonly = readonly
        if (self.__readonly):
            self.__tw.setReadOnly(True)
        vbox.addWidget(self.__tw)
        self.__tw.setText(str(text))
        
        hbox = QHBoxLayout(vbox)

        b = QPushButton('Commit', self)
        b.setDisabled(self.__readonly)
        QToolTip.add(b, 'Commit the (edited) text to its inarg record')
        QObject.connect(b, SIGNAL("pressed ()"), self.onCommit)
        hbox.addWidget(b)

        b = QPushButton('Print', self)
        QToolTip.add(b, 'Print the current text')
        QObject.connect(b, SIGNAL("pressed ()"), self.onPrint)
        hbox.addWidget(b)

        b = QPushButton('Cancel', self)
        QToolTip.add(b, 'Cancel this floating text-window')
        QObject.connect(b, SIGNAL("pressed ()"), self.onCancel)
        hbox.addWidget(b)


        # Display the popup:
        self.show()
        return None

    def setText(self, text):
        self.__tw.setText(str(text))
        return True

    def onPrint (self):
        """Action on pressing the Print button"""
        print '\n*** Printing not yet implemented...\n'
        return True

    def onCommit (self):
        """Action on pressing the Commit button"""
        text = str(self.__tw.text())
        # self.emit(PYSIGNAL("floatwCommit()"),(text,))
        return self.closeAll()
	
    def onCancel (self):
        """Action on pressing the Cancel button"""
        # self.emit(PYSIGNAL("floatwCancel()"),(0,))
        return self.closeAll()

    def closeAll (self):
        """Close the floatw, and any associated things"""
        self.close()
        return True
	


#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
# Popup for interaction with an argument value:
#----------------------------------------------------------------------------
        
class Popup(QDialog):
    def __init__(self, parent=None, name='popup_name', itd=None):
        QDialog.__init__(self, parent, "Test", 0, 0)

        # Keep the itemdict (itd) for use in self.textChanged():
        self.__itemdict = itd
        # print '\n** Popup: itd =',itd,'\n'

        # Keep track of the arg value in various ways:
        value = itd['value']
        self.__last_value = value     
        self.__current_value = value  
        self.__input_value = value  
        qsval = QString(str(value))
        # print value,' ->  qsval =',qsval

        # Place-holders (see self.onOpen() and onCancel()):
        self.__lsm = None
        self.__ms = None

        # Put in widgets from top to bottom:
        vbox = QVBoxLayout(self,10,5)     

        # The name (key) of the variable:
        label = QLabel(self)
        label.setText(str(itd['key']))
        vbox.addWidget(label)

        # Use a combobox for editing the vaue:
        self.__combo = QComboBox(self)
        self.__combo.insertItem(qsval)       
        self.__combo.setEditable(itd['editable'])
        if itd['choice']:
            vv = itd['choice']
            for i in range(len(vv)):
                qsval1 = QString(str(vv[i]))
                self.__combo.insertItem(qsval1, i+1)
        vbox.addWidget(self.__combo)
        QObject.connect(self.__combo, SIGNAL("activated(const QString &)"), self.activated)
        QObject.connect(self.__combo, SIGNAL("textChanged(const QString &)"), self.textChanged)
        self.__activated = False
        self.__textChanged = False

        # The value type is updated during editing:
        self.__type = QLabel(self)
        vbox.addWidget(self.__type)
        self.showType (self.__current_value)

        if itd['browse']:
            # Include file browse/open buttons, if required:
            hbox = QHBoxLayout(vbox)

            self.__filter = itd['browse']
            if self.__filter=='*.MS':
                button = QPushButton('Browse', self)
                QToolTip.add(button,'Launch a MS (directory) browser')
                hbox.addWidget(button)
                QObject.connect(button, SIGNAL("pressed ()"), self.onBrowseDir)
            else:
                button = QPushButton('Browse  '+self.__filter, self)
                QToolTip.add(button,'Launch a file-browser')
                hbox.addWidget(button)
                QObject.connect(button, SIGNAL("pressed ()"), self.onBrowse)

            button = QPushButton('Open', self)
            QToolTip.add(button,'Open the selected file, and do something useful')
            hbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onOpen)


        if itd['vector']:
            # Include a clear button, for vector/list editing:
            button = QPushButton('clear list', self)
            QToolTip.add(button,'Revert to the value [] (empty list)')
            vbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onClear)


        # Other information (labels):
        keys = ['help']
        if itd['range']:
            keys.append('range')
        else:
            if itd['min']: keys.append('min')
            if itd['max']: keys.append('max')
        keys.append('module')
        for key in keys:
            if itd.has_key(key) and itd[key]:
                label = QLabel(self)
                label.setText(key+':  '+str(itd[key]))
                if key=='range': QToolTip.add(label,'Allowed range')
                if key=='module': QToolTip.add(label,'Name of inarg (sub-)module')
                vbox.addWidget(label)

        # Status label:
        self.__status = QLabel(self)
        self.__status.setText(' ')
        vbox.addWidget(self.__status)

        # Message label:
        self.__message = QLabel(self)
        self.__message.setText(' ')
        vbox.addWidget(self.__message)

        if True:
            # Make Revert/undo:
            hbox = QHBoxLayout(vbox)

            button = QPushButton('Inspect',self)
            QToolTip.add(button,'Inspect the current value')
            hbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onInspect)

            button = QPushButton('Revert',self)
            QToolTip.add(button,'Revert to the input value')
            hbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onRevert)

            button = QPushButton('Undo',self)
            QToolTip.add(button,'Undo: revert to the last value')
            hbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onUndo)

        if True:
            # Make Cancel/OK buttons:
            hbox = QHBoxLayout(vbox)

            button = QPushButton('Commit',self)
            QToolTip.add(button,'Modify the inarg value, and close this popup')
            hbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onCommit)

            button = QPushButton('Cancel',self)
            QToolTip.add(button,'Close this popup, and do nothing')
            hbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onCancel)

        # Display the popup:
        self.show()
        return None

    #-----------------------------------------------------------------------

    def showType (self, v2):
        """Show the type (and the length, if relevant) of v2"""
        s2 = 'type'+':  '+str(type(v2))+' '
        if isinstance(v2, str): s2 += '[nchar='+str(len(v2))+']'
        if isinstance(v2, (list,tuple)): s2 += '['+str(len(v2))+']'
        self.__type.setText(s2)


    #-------------------------------------------------------------------------
    # Popup buttons:
    #-------------------------------------------------------------------------

    def onCommit (self):
        """Action on pressing the Commit button"""
        self.emit(PYSIGNAL("popupCommit()"),(self.__itemdict,))
        self.__status.setText('... inarg record updated ...')
        return self.closeAll()
	
    def onCancel (self):
        """Action on pressing the Cancel button"""
        self.emit(PYSIGNAL("popupCancel()"),(0,))
        return self.closeAll()

    def closeAll (self):
        """Close the popup, and any associated things"""
        if self.__lsm:                   # Local Sky Model 
            self.__lsm.close_display()   # function does not exist!
            self.__lsm = None
        if self.__ms:
            pass
        self.close()
        return True
	
    def onInspect (self):
        """Action on pressing the Inspect button"""
        v = self.__current_value
        s = '** Inspect: '+str(type(v))+' = '+str(v)
        print '\n',s,'\n'
        self.__status.setText(s)
        return True
	
    def onRevert (self):
        """Action on pressing the Revert button"""
        self.__combo.setCurrentText(QString(str(self.__input_value)))
        self.__status.setText('... Revert: -> input value ...')
        return True
	
    def onUndo (self):
        """Action on pressing the Undo button"""
        self.__combo.setCurrentText(QString(str(self.__last_value)))
        self.__status.setText('... Undo: -> last (valid) value ...')
        return True

    def onClear (self):
        """Action on pressing the clear (vector) button"""
        self.__current_value = []
        self.__combo.setCurrentText(QString(str(self.__current_value)))
        self.__status.setText('... cleared the vector...')
        return True


    def onBrowse (self):
        """Action on pressing the browse button"""
        filename = QFileDialog.getOpenFileName("",self.__filter, self)
        filename = str(filename)
        if len(filename)>2:
            self.__combo.setCurrentText(filename)
            self.__status.setText('... new filename ...')
        else:
            self.__status.setText('... ignored ...')
        return True

    def onBrowseDir (self):
        """Action on pressing the browse button"""
        dirname = QFileDialog.getExistingDirectory("", self)
        dirname = str(dirname)
        if len(dirname)>2:
            self.__combo.setCurrentText(dirname)
            self.__status.setText('... new dirname ...')
        else:
            self.__status.setText('... ignored ...')
        return True

    def onOpen (self):
        """Action on pressing the open button"""
        filename = str(self.__current_value)
        if self.__filter=='*.lsm':
            self.__status.setText('open Local Sky Model:  '+filename)
            self.openLSM (filename)   
        elif self.__filter=='*.MS':
            self.__status.setText('open Measurement Set:  '+filename)
            self.openMS (filename)
        else:
            self.__status.setText('filter not recognised:  '+self.__filter)
        return True

    def openMS (self, filename):
        """Callback function that opens a Measurement Set""" 
        # self.__ms = ...
        # self.__ms.browse()
        return True


    def openLSM (self, filename):
        """Callback function that opens a Local Sky Model""" 
        from Timba.LSM.LSM import *
        from Timba.LSM.LSM_GUI import *
        self.__lsm = LSM()                       # Create an empty global lsm:
        self.__lsm.load(filename)
        print dir(self.__lsm)
        print self.__lsm.__doc__ 
        plist = self.__lsm.queryLSM(count=1000)  # error if called without argument....?
        print '\n** .queryLSM(count=1000) ->',type(plist),len(plist)
        plist = self.__lsm.queryLSM(count=1)
        print '\n** .queryLSM(count=2) ->',type(plist),len(plist)
        for punit in plist: 
            sp = punit.getSP()                   # get_Sixpack()?
            sp.display()
        self.__lsm.display()                     # close to release the 
        return True



    #-------------------------------------------------------------------------
    # Actions if combobox value modified:
    #-------------------------------------------------------------------------

    def activated (self, qsval):
        """Action whenever another combobox item is selected"""

        if self.__textChanged:
            print '** activated():  ignore'
            self.__textChanged = False
            return False

        v2 = self.evaluate(qsval)
        print '** activated():',v2
        self.__activated = True

        if self.__itemdict['vector']:             # special case
            new = self.__current_value
            new.append(v2)
            print 'vector: ',self.__current_value,'(',v2,') ->',new
            v2 = new
            self.__combo.setCurrentText(QString(str(v2)))

        self.accept(v2)
        self.__activated = False
        return True

    #-----------------------------------------------------------------------

    def textChanged (self, qsval):
        """Action whenever the combobox text is modified"""

        if self.__activated:
            print '** textChanged():  ignore'
            self.__activated = False
            return False

        self.__textChanged = True
        v2 = self.evaluate(qsval)
        print '** textChanged():',v2

        # Check the new value (range, min, max, type):
        ok = True
        if not ok:                                # problem....
            self.__message.setText('... ERROR: ...')
            # Revert to the original value:
            self.__combo.setCurrentText(QString(str(self.__input_value)))
            self.__status.setText('... locally reverted ...')
            return False

        self.accept(v2)
        self.__textChanged = False
        return True

#-----------------------------------------------------------------------

    def evaluate (self, qsval):
        """Evaluate the (modified) QString value from the combobox"""
        v1 = str(qsval)                           # qsval is a QString object
        try:
            v2 = eval(v1)                         # covers most things
        except:
            v2 = v1                               # assume string
            # print sys.exc_info();
            # return;
        self.showType(v2)
        return v2

#-----------------------------------------------------------------------

    def accept (self, v2):
        """Accept the new combobox value (v2)"""

        # Update the itemdict(itd) from the ArgBrowser:
        self.__itemdict['value'] = v2
        self.__status.setText('... locally modified ...')

        self.__last_value = self.__current_value
        self.__current_value = v2
        self.showType (v2)
        return True






#============================================================================
# Testing routine:
#============================================================================


if __name__=="__main__":
    from Timba.Contrib.JEN.util import JEN_inarg
    # from Timba.Contrib.JEN.util import JEN_record

    igui = TDLog()
    # igui.show()

    if 0:
        print 'before xxx'
        igui.tw('xxx\nyyy')
        print 'after xxx'
        # igui.tw('yyy')

    if 0:
        igui.test()

    if 1:
        for i in range(30):
            igui.append(i)

    if 1:
        igui.show()
        igui.QApp().connect(igui.QApp(), SIGNAL("lastWindowClosed()"),
                            igui.QApp(), SLOT("quit()"))
        # igui.QApp().exec_loop()

    if 0:
        igui.launch()

    if 1:
        for i in range(5):
            igui.append(i)




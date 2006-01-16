# JEN_inargGui.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Gui for records of input arguments (see JEN_inarg.py)
#
# History:
#    - 05 jan 2006: creation (from MXM ArgBrowser.py)
#    - 10 jan 2006: in workable state
#    - 11 jan 2006: added file browsers and status message 
#    - 12 jan 2006: added hooks for assay  
#
# Full description:
#
#
# To be done:
# - Upward search for argument names/values (now local only)


#================================================================================
# Preamble
#================================================================================

import sys
import pickle

from qt import *
from copy import deepcopy

from Timba.TDL import *
from Timba.Trees import JEN_inarg

# The name of the control-record
CTRL_record = '_JEN_inarg_CTRL_record:'

# The name of an (optional) option field (e.g. see .modify())
option_field = '_JEN_inarg_option'

# Name of record of unique local identification nrs:
kident = 'JEN_inargGUI_ident'

# Name of generic save/restore file (see .save_inarg()):
generic_savefile = 'generic_save_restore.inarg'


#================================================================================
#================================================================================

        

class ArgBrowser(QMainWindow):
    
    def __init__(self, parent=None):

        if not parent:
          self.__QApp = QApplication(sys.argv)
          QMainWindow.__init__(self,parent,None,Qt.WType_Dialog|Qt.WShowModal);
	else:
	  self.__QApp = parent
          QMainWindow.__init__(self);
	
        self.setMinimumWidth(700)
        self.setMinimumHeight(400)

        #----------------------------------------------------
        # The basic layout: Stack widgets vertically in vbox
        
        vbox = QVBoxLayout(self)

        #----------------------------------------------------
        # Statusbar:
        if False:
            # NB: Only works when put before vbox definition,
            #     but then inhibits the vbox....!!?
            #     (Solved by using a QLabel instead, see below)
            self.__statusbar = self.statusBar()
            self.__statusbar.show()
            self.__statusbar.clear()
            self.__statusbar.message("statusbar")


        #----------------------------------------------------
        # The listview displays the inarg record:
        self.__listview = QListView(self)
        # self.setCentralWidget(self.__listview)
        vbox.addWidget(self.__listview)

        color = QColor('darkblue')
        self.__listview.setPaletteForegroundColor(color)
        color = QColor('pink')
        color = QColor('lightgreen')
        color.setRgb(250,255,255)           # 0-255
        self.__listview.setPaletteBackgroundColor(color)

        self.__listview.addColumn("name", 300)
        self.__listview.addColumn("value",200)
        self.__listview.addColumn("help", 500)
        self.__listview.addColumn("iitd")
        self.__listview.setRootIsDecorated(1)

        #----------------------------------------------------
        # Buttons to be added at the bottom:
        hbox = QHBoxLayout(self)
        vbox.addLayout(hbox)
        b_save = QPushButton('Save', self)
        hbox.addWidget(b_save)
        b_exec = QPushButton('Proceed', self)
        hbox.addWidget(b_exec)
        b_cancel = QPushButton('Cancel', self)
        hbox.addWidget(b_cancel)
        QObject.connect(b_save, SIGNAL("pressed ()"), self.save_inarg)
        QObject.connect(b_exec, SIGNAL("pressed ()"), self.exec_with_inarg)
        QObject.connect(b_cancel, SIGNAL("pressed ()"), self.cancel_exec)

        #----------------------------------------------------
        # Message label (i.s.o. statusbar):
        self.__message = QLabel(self)
        font = QFont("times")
        font.setBold(True)
        # self.__message.setFont(font)
        self.__message.setText(' ')
        vbox.addWidget(self.__message)


        #----------------------------------------------------
        # Menubar (at the end...!?):
        self.__menubar = self.menuBar()

        filemenu = QPopupMenu(self)
        # filemenu.insertItem('save',,self,,SLOT(self.save))
        filemenu.insertItem('open', self.open_inarg)
        filemenu.insertItem('saveAs', self.saveAs_inarg)
        filemenu.insertSeparator()     
        filemenu.insertItem('save', self.save_inarg)
        filemenu.insertItem('restore', self.restore_inarg)
        filemenu.insertItem('recover', self.recover_inarg)
        filemenu.insertSeparator()     
        filemenu.insertItem('print', self.print_inarg)
        filemenu.insertSeparator()     
        filemenu.insertItem('close', self.closeGui)
        self.__menubar.insertItem('File', filemenu)

        editmenu = QPopupMenu(self)
        editmenu.insertItem('revert', self.revert_inarg)
        self.__menubar.insertItem('Edit', editmenu)

        viewmenu = QPopupMenu(self)
        viewmenu.insertItem('refresh', self.refresh)
        viewmenu.insertSeparator()     
        viewmenu.insertItem('inarg2pp', self.inarg2pp)
        viewmenu.insertSeparator()     
        self.__item_unhide = viewmenu.insertItem('unhide', self.unhide)
        self.__item_show_CTRL = viewmenu.insertItem('show CTRL', self.show_CTRL)
        self.__menubar.insertItem('View', viewmenu)

        testmenu = QPopupMenu(self)
        testmenu.insertItem('inarg_OK?', self.test_OK)
        testmenu.insertItem('count_@@', self.count_ref)
        testmenu.insertItem('replace_@@', self.replace_ref)
        testmenu.insertSeparator()     
        testmenu.insertItem('assay', self.assay)
        testmenu.insertItem('assay_verbose', self.assay_verbose)
        testmenu.insertItem('assay_record', self.assay_record)
        testmenu.insertSeparator()     
        self.__menubar.insertItem('Test', testmenu)

        helpmenu = QPopupMenu(self)
        self.__menubar.insertSeparator()
        self.__menubar.insertItem('Help', helpmenu)

        #-------------------------------------------------------
        # Initialise:
        self.__popup = None                        # popup object (editing)
        self.clearGui()
        self.__set_open = True                     # see .recurse()
        self.__result = None                       # output for exec_loop
        self.__inarg = None                        # the edited inarg
        self.__inarg_input = None                  # the input inarg (see .revert_inarg())
        self.__savefile = generic_savefile         # used by .save_inarg(None)
        self.__scriptname = None                   # target script for inarg record
        self.__closed = False
        if True:
            # Always restore the generic savefile (but do not show)
            self.restore_inarg(generic_savefile)            
        return None

    # From: ../PyApps/src/GUI/treebrowser.py
    # - redefines the paintCell to change item colors...
    # - to change the font, look at the .paint attribute...?  
    # def paintCell (self,painter,cg,column,width,align):
    #  return QListViewItem.paintCell(self,painter,self._color_group or cg,column,width,align);


    def QApp (self):
        """Access to the QApplication"""
        return self.__QApp

    def closeGui (self):
        """Close the gui"""
        self.save_inarg(generic_savefile)          # save always....            
        self.clearGui()
        if self.__popup: self.__popup.close()
        self.__listview.close()                    #............?
        self.close()
	self.__closed = True;                      #............?
        # clean up any signal connections?
        return True

    def closeEvent (self,ev):
        """Callback function for close"""
        self.__closed = True;
    	QMainWindow.closeEvent(self,ev);


    def clearGui (self):
        """Clear the gui"""
        self.__listview.clear()
        if self.__popup: self.__popup.close()
        self.__itemdict = []                       # list of itd records
        self.__unhide = False                      # if True, show hidden arguments too
        self.__show_CTRL = False                   # if True, show CTRL_records
        return True


#---------------------------------------------------------------------------

    def revert_inarg(self):
        """Revert to the original (input) inarg values"""
        self.__inarg = deepcopy(self.__inarg_input)
        self.refresh()
        self.__message.setText('** reverted to the original (input) inarg record')
        return True

    def unhide(self):
        """Hide/unhide the less important fields"""
        unhide = self.__unhide
        self.clearGui()
        self.__unhide = not unhide
        item = self.__item_unhide
        s1 = '** unhide -> '+str(self.__unhide)+':  '
        if self.__unhide:
            self.__menubar.changeItem(item,'hide')
            self.__message.setText(s1+'show all hidden arguments')
        else:
            self.__menubar.changeItem(item,'unhide')
            self.__message.setText(s1+'hide all hidden arguments')
        self.refresh(clear=False)    
        return True

    def show_CTRL(self):
        """show/hide the CTRL records"""
        show_CTRL = self.__show_CTRL
        self.clearGui()
        self.__show_CTRL = not show_CTRL
        item = self.__item_show_CTRL
        s1 = '** show_CTRL -> '+str(self.__show_CTRL)+':  '
        if self.__show_CTRL:
            self.__menubar.changeItem(item,'hide CTRL')
            self.__message.setText(s1+'show CTRL records')
        else:
            self.__menubar.changeItem(item,'show CTRL')
            self.__message.setText(s1+'hide CTRL records')
        self.refresh(clear=False)    
        return True

    def print_inarg(self):
        """Print the current inarg record"""
        self.__message.setText('** print_inarg: not yet implemented')
        return True

    def test_OK(self):
        """Test whether the current inarg record is OK"""
        ok = JEN_inarg.is_OK(self.__inarg, trace=True)
        s1 = '** test_OK(): '
        if True:
            # See whether there are any unresolved references:
            inarg = deepcopy(self.__inarg)
            JEN_inarg._replace_reference(inarg, trace=True)
            rr = JEN_inarg._count_reference(inarg, trace=True)
            if rr['n']>0:
                ok = False
            s1 += ' (unresolved: '+str(rr)+') '
        if (ok):
            s1 += '      -- ok --'
        else:
            s1 += '      ** NOT OK!! **'
        self.__message.setText(s1)
        return ok

    def count_ref(self):
        """Count the nr of unresolved (@, @@) references"""
        rr = JEN_inarg._count_reference(self.__inarg, trace=True)
        s1 = '** unresolved references:  '
        s1 += '  @='+str(rr['n1'])+'  @@='+str(rr['n2'])
        self.__message.setText(s1)
        return rr

    def replace_ref(self):
        """Resolve any unresolved (@, @@) references"""
        JEN_inarg._replace_reference(self.__inarg, trace=True)
        self.refresh()
        return self.count_ref()

#-------------------------------------------------------------------

    def saveAs_inarg(self):
        """Save the (edited) inarg record for later use"""
        filename = QFileDialog.getSaveFileName("","*.inarg",self)
        self.save_inarg(filename);
        return True

    def open_inarg(self):
        """Read a saved inarg record from a file, using a file browser"""
        filename = QFileDialog.getOpenFileName("","*.inarg",self)
        self.restore_inarg(filename);
        return True

    def save_inarg(self, filename=None):
        """Save the (edited) inarg record for later use"""
        if filename==None:
            filename = self.__savefile
        filename = str(filename)
        f = open(filename,'wb')
        p = pickle.Pickler(f)
        r = p.dump(self.__inarg)
        self.__message.setText('** saved inarg record to file:   '+filename)
        f.close()
        return True

    def recover_inarg(self):
        """Recover the inarg record that was saved when pressing
        the 'Proceed' button. This allows continuation from that point"""
        self.restore_inarg(generic_savefile)
        return True

    def restore_inarg(self, filename=None):
        """Read a saved inarg record from a file"""
        if filename==None:
            filename = self.__savefile
        filename = str(filename)
        try:
            f = open(filename,'rb')
        except:
            self.__message.setText('** restore: file does not exist:  '+filename)
            return False
        p = pickle.Unpickler(f)
        inarg = p.load()
        self.__message.setText('** restored inarg record from file:   '+filename)
        f.close()
        self.input(inarg)    
        return True

    #-------------------------------------------------------------------------------
    # Script execution, using the current inarg record:
    #-------------------------------------------------------------------------------

    def cancel_exec(self):
        """Do nothing"""
        self.emit(PYSIGNAL("cancel_exec()"),(0,))
        self.__result = None
        self.closeGui()
        return True
    
    def exec_with_inarg(self):
        """Execute the relevant function"""
        if not self.test_OK():
            self.__message.setText('** problem with inarg record: done nothing!')
            return False
        # OK: Save the current inarg in the generic file, for later recovery:
        self.save_inarg(generic_savefile)

        # Resolve any references (@, @@):
        # (@@ values do not work inside...)
        JEN_inarg._replace_reference(self.__inarg)

        # NB: The gui has to be closed for it to proceed.
        # In the future, we will want to keep the gui open, so we can redefine
        # the tree with different parameters....
        self.__result = self.__inarg              # see self.exec_loop()
        self.closeGui()
        return True


    def assay(self, switch=None):
        """Assay the relevant script with the current inarg record.
        The result is put into a file: xxx.assaylog"""
        self.__message.setText('** assay('+str(switch)+') not implemented yet')
        # Get script name from self.__scriptname....
        return True

    def assay_verbose(self):
        """Assay the relevant script with the current inarg record
        while printing information"""
        return self.assay(switch='-dassayer=2')

    def assay_record(self):
        """Assay the relevant script with the current inarg record
        and record the result for later comparison (xxx.dataassay)"""
        return self.assay(switch='-assayrecord')

    def inarg2pp (self):
        """Show the resulting pp record as it would be inside the target,
        with all the referenced values replaced"""
        pp = JEN_inarg.inarg2pp(self.__inarg)
        JEN_inarg.getdefaults(pp, check=True, strip=False, trace=True)
        JEN_inarg.display(pp, full=False)
        # NB: Use JEN_inspect.....
        return True

    #-------------------------------------------------------------------------------
    # Input of a inarg record:
    #-------------------------------------------------------------------------------

    def input (self, inarg=None, name=None, set_open=True):
        """Input of a new (inarg) record in the gui"""
        if not isinstance(inarg, dict): return False
        self.clearGui()
        self.__inarg = deepcopy(inarg)                          # to be edited
        self.__inarg_input = deepcopy(inarg)                    # unchanged copy

        # Modify the name (of its main window):
        self.__scriptname = None
        s1 = '** input of inarg record:  '
        if not name:
            if self.__inarg.has_key('script_name'):             # MG_JEN script
                name = self.__inarg['script_name']
                self.__scriptname = name                        # corresponding script
                s1 += 'inarg.script_name =   '
            else:
                name = self.__inarg.keys()[0]
                s1 += '[inarg.keys[0]] =   '
        self.__message.setText(s1+name)
        self.setCaption(name)
        self.__savefile = name + '.inarg'

        # Transfer the inarg fields recursively:
        self.__set_open = set_open
        self.recurse (self.__inarg, listview=self.__listview)

        # Connect signals and slots, once a signal is detected the according slot is executed
        # QObject.connect(self.__listview, SIGNAL("doubleClicked (QListViewItem * )"), self.itemSelected)
        QObject.connect(self.__listview, SIGNAL("clicked (QListViewItem * )"), self.itemSelected)

        self.show()
        return True


    def refresh (self, clear=True):
        """Refresh the listview widget from self.__inarg"""
        if clear: self.clearGui()
        self.recurse (self.__inarg, listview=self.__listview)
        return True


    def recurse (self, rr=None, listview=None, level=0, module='<module>',
                 makeitd=True, trace=False):
        """Recursive input of a hierarchical inarg record"""
        if not isinstance(rr, dict): return False

        if makeitd:
            # Make sure that there is a CTRL_record for iitd storage:
            rr.setdefault(CTRL_record, dict())
            if not isinstance(rr[CTRL_record], dict): rr[CTRL_record] = dict()
            # Its 'kident' (see above) record is used to store unique identifiers (iitd)
            rr[CTRL_record].setdefault(kident, dict())
            
        for key in rr.keys():
            if isinstance(rr[key], dict):   
                if key==CTRL_record:                           # is a CTRL record         
                    if self.__show_CTRL:
                        item = QListViewItem(listview, key, 'CTRL_record')
                        item.setSelectable(False)
                        self.recurse (rr[key], listview=item,
                                      level=level+1, makeitd=False)
                else:
                    text = QString(key)
                    font = QFont("times")
                    font.setBold(True)
                    # text.setFont(font)
                    item = QListViewItem(listview, text)
                    item.setSelectable(False)
                    if self.__set_open and level==0:
                        item.setOpen(True)                     # show its children
                    self.recurse (rr[key], listview=item, level=level+1,
                                  module=key, makeitd=makeitd)

            elif not makeitd:
                # E.g. the fields inside a CTRL_record:
                item = QListViewItem(listview, key, str(rr[key]))

            else:                                              # rr[key] is a value
                itd = self.make_itd(key, rr[key], ctrl=rr[CTRL_record], module=module)
                if not itd['hide']:
                    value = str(itd['value'])                  # current value
                    iitd = str(itd['iitd'])                    # used by selectedItem()
                    rr[CTRL_record][kident][key] = itd['iitd'] # unique local identifier
                    help = ' '                                 # short explanation
                    if itd['help']:
                        help = str(itd['help'])
                        hh = help.split('\n')
                        if len(hh)>1: help = hh[0]+'...'       # first line only
                        hcmax = 40                             # max nr of chars
                        if len(help)>hcmax:
                            help = help[:hcmax]+'...'
                    item = QListViewItem(listview, key, value, help, iitd)
                    # item.setColor(itd['color'])              # <-----??            

        return True



    #-------------------------------------------------------------------------------

    def make_itd(self, key, value, ctrl=None,
                 color='black', hide=False,
                 module='<module>',
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
                   browse=None,               # Extension of files ('e.g *.MS')
                   module=module,             # name of the relevant function module
                   level=level,               # inarg hierarchy level
                   iitd=-1)                   # sequenc nr in self.__itemdict

        # If ctrl is a record, use its information:
        if isinstance(ctrl, dict):
            # First some overall fields:
            overall = ['color']
            for field in overall:
                if ctrl.has_key(field):
                    itd[field] = ctrl[field]
            # Then the key-specific keys (see JEN_inarg.define()):
            key_specific = ['choice',
                            'editable','hide','color',
                            'mandatory_type','browse',
                            'range','min','max','help']
            for field in key_specific:
                if ctrl.has_key(field):
                    if ctrl[field].has_key(key):
                        itd[field] = ctrl[field][key]

        # Override some fields, if required:
        if self.__unhide:                            # see self.unhide()
            itd['hide'] = False
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
            indent = (level*'.')
            itd['help'] = indent+str(itd['help'])

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

        # If +/- clicked, the item is None:
        if not item: return False
        
        # Read the (string) values from the columns:
        key = item.text(0)            
        vstring = item.text(1)           
        help = item.text(2)              
        iitd = item.text(3)          
        if self.__popup:
            self.__popup.close()

        # Use the iitd string to get the relevant itemdict record:
        iitd = str(iitd)
        if iitd==' ': iitd = '-1'
        try:
            iitd = int(iitd)
        except:
            # print sys.exc_info()
            return False
        if iitd>=0:
            itd = self.__itemdict[iitd]
            self.__current_iitd = iitd
            # Make the popup object:
            self.__popup = Popup(self, name=itd['key'], itd=itd)
            QObject.connect(self.__popup, PYSIGNAL("popupOK()"), self.popupOK)
            QObject.connect(self.__popup, PYSIGNAL("popupCancel()"), self.popupCancel)
        return True


    def popupCancel(self):
        """Action upon pressing the popup Cancel button"""
        self.refresh()
        self.__message.setText('** popup cancelled')
        return True

    def popupOK(self, itd):
        """Action upon pressing the popup OK button"""
        # Replace the relevant itemdict with the modified one:
        iitd = self.__current_iitd                # its position in self.__itemdict
        self.__itemdict[iitd] = itd               # replace in self.__itemdict
        self.replace (self.__inarg, itd, trace=False)
        self.refresh()
        return True

    def replace (self, rr=None, itd=None, level=0, trace=False):
        """Replace the modified value in self.__inarg"""
        if not isinstance(rr, dict): return False

        # Search for the correct iitd identifier:
        if rr.has_key(CTRL_record):
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
# Popup for interaction with an argument value:
#----------------------------------------------------------------------------
        
class Popup(QDialog):
    def __init__(self, parent=None, name='popup_name', itd=None):
        QDialog.__init__(self, parent, "Test", 0, 0)

        # Keep the itemdict (itd) for use in self.textChanged():
        self.__itemdict = itd

        vbox = QVBoxLayout(self,10,5)           # ....?

        # The name (key) of the variable:
        label = QLabel(self)
        label.setText(str(itd['key']))
        vbox.addWidget(label)

        # Use a combobox for editing the vaue:
        self.combo = QComboBox(self)
        value = QString(str(itd['value']))
        self.combo.insertItem(value)            # current value
        self.combo_input_value = value          # see self.modified()
        self.combo.setEditable(itd['editable'])
        if itd['choice']:
            vv = itd['choice']
            for i in range(len(vv)):
                value = QString(str(vv[i]))
                self.combo.insertItem(value, i+1)
        vbox.addWidget(self.combo)
        QObject.connect(self.combo, SIGNAL("textChanged(const QString &)"), self.modified)
        QObject.connect(self.combo, SIGNAL("activated(const QString &)"), self.modified)

        # The value type is updated during editing:
        self.type = QLabel(self)
        self.type.setText('type'+':  '+str(type(itd['value'])))
        vbox.addWidget(self.type)

        if itd['browse']:
            # Include a file browser button, if required:
            self.__filter = itd['browse']
            button = QPushButton('browse '+self.__filter, self)
            vbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onBrowse)

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
                vbox.addWidget(label)

        # Status label:
        self.status = QLabel(self)
        self.status.setText(' ')
        vbox.addWidget(self.status)

        # Message label:
        self.message = QLabel(self)
        self.message.setText(' ')
        vbox.addWidget(self.message)

        if True:
            # Make Cancel/OK buttons:
            hbox = QHBoxLayout(self)
            vbox.addLayout(hbox)

            button = QPushButton('OK',self)
            hbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onOK)

            button = QPushButton('Cancel',self)
            hbox.addWidget(button)
            QObject.connect(button, SIGNAL("pressed ()"), self.onCancel)

        # Display the popup:
        self.show()
        return None

    #-------------------------------------------------------------------------
    # Popup buttons:
    #-------------------------------------------------------------------------

    def onOK (self):
        """Action on pressing the OK button"""
        self.emit(PYSIGNAL("popupOK()"),(self.__itemdict,))
        self.status.setText('... inarg record updated ...')
        self.close()
        return True
	
    def onCancel (self):
        """Action on pressing the Cancel button"""
        self.emit(PYSIGNAL("popupCancel()"),(0,))
        self.close()
        return True
	
    def onBrowse (self):
        """Action on pressing the browse button"""
        filename = QFileDialog.getOpenFileName("",self.__filter, self)
        if len(filename)>2:
            self.combo.setCurrentText(filename)
            self.status.setText('... new filename ...')
            self.onOK()
        else:
            self.status.setText('... ignored ...')
        return True

    #-------------------------------------------------------------------------
    # Action if value modified:
    #-------------------------------------------------------------------------

    def modified (self, value):
        """Deal with combo-box signals"""

        # Deal with the modified value:
        v1 = str(value)                           # value is a QString object
        try:
            v2 = eval(v1)                         # covers most things
        except:
            v2 = v1                               # assume string
            # print sys.exc_info();
            # return;

        # Update the itemdict(itd) from the ArgBrowser:
        self.__itemdict['value'] = v2
        self.status.setText('... locally modified ...')
        if value==self.combo_input_value:
            self.status.setText('... locally reverted ...')

        # Report the type
        s2 = 'type'+':  '+str(type(v2))+' '
        if isinstance(v2, str): s2 += '[nchar='+str(len(v2))+']'
        if isinstance(v2, (list,tuple)): s2 += '['+str(len(v2))+']'
        self.type.setText(s2)

        # Check the new value (range, min, max, type):
        ok = True
        if not ok:                                # problem....
            self.message.setText('... ERROR: ...')
            # Revert to the original value:
            self.combo.setCurrentText(self.combo_input_value)
            self.status.setText('... locally reverted ...')
            return False

        return True



#============================================================================
# Testing routine:
#============================================================================


if __name__=="__main__":
    from Timba.Trees import JEN_inarg
    # from Timba.Trees import JEN_record

    # QApp = QApplication(sys.argv)
    igui = ArgBrowser()

    if 0:
        igui.test()

    if 1:
        qual = '<qual>'
        qual = None
        inarg = JEN_inarg.test1(_getdefaults=True, _qual=qual, trace=False)
        igui.input(inarg)
        # JEN_inarg.display(inarg, 'defaults', full=True)

    if 0:
        # Make a separate gui for the result:
        result = JEN_inarg.test1(_inarg=inarg, _qual=qual, bb='override', qq='ignored', nested=False)
        rgui = ArgBrowser()
        rgui.input(result)
        rgui.show()

    if 1:
        igui.launch()

    if 0:
        igui.show()
        igui.QApp().connect(igui.QApp(), SIGNAL("lastWindowClosed()"),
                            igui.QApp(), SLOT("quit()"))
        igui.QApp().exec_loop()


# JEN_inargGui.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Gui for records of input arguments (see JEN_inarg.py)
#
# History:
#    - 05 jan 2006: creation (from MXM ArgBrowser.py)
#
# Full description:

#================================================================================
# Preamble
#================================================================================

import sys
from qt import *
from copy import deepcopy

from Timba.TDL import *

# The name of the control-record
CTRL_record = '_JEN_inarg_CTRL_record:'

# The name of an (optional) option field (e.g. see .modify())
option_field = '_JEN_inarg_option'



#================================================================================
#================================================================================

        

class ArgBrowser(QMainWindow):
    
    def __init__(self, *args):

        # NB: What is the usage of args (list): better to have **args?

        apply(QMainWindow.__init__, (self,) + args)

        if False:
            # Buttons to be added:
            # - unhide (toggle, default=False, yellow if True)
            # - revert (revert to the input values, in self.inarg)
            # - execute (green): executes the corresponding script 
            # - cancel (red)
            # - save as (saves the edited inarg script)
            # - restore (load another inarg script)
            self.v = QVBoxLayout(self,30,5)
            self.button = {}
            keys = ['unhide','revert','execute','cancel','saveAs..','restore']
            # keys = ['unhide']
            for key in keys:
                b = QPushButton(self)
                # print dir(b)
                b.setText(key)
                # b.background('red')
                self.button[key] = b 
                self.v.addWidget(b)
            return None

        # self.listview is the root object
        self.listview = QListView(self)
        self.setCentralWidget(self.listview)
        # print '\n** dir(self): ',dir(self),'\n'
        self.listview.addColumn("nr")
        self.listview.addColumn("name")
        self.listview.addColumn("value")
        self.listview.addColumn("help")
        self.listview.addColumn("type")
        self.listview.setRootIsDecorated(1)
        # print '\n** dir(listview): ',dir(self.listview),'\n'

        self.popup = None
        self.clear()
        return None

    def closeGui (self):
        """Close the gui"""
        self.clear()
        self.listview.close()                    #............?
        if self.popup: self.popup.close()
        self.close()                             #............?
        # clean up any signal connections?
        return True

    def clear (self):
        """Clear the gui"""
        self.listview.clear()
        if self.popup: self.popup.close()
        self.inarg = None                        # edited copy
        self.inarg_input = None                  # input copy
        self.items = []                          # list of listview items
        self.itemdict = []                       # list of itd records
        self.unhide = False                      # if True, hide nothing
        return True


#---------------------------------------------------------------------------

    def revert(self):
        """Revert to the original (input) inarg values"""
        self.recurse(self.inarg_input, self.listview)
        return True

    def unhide(self):
        """Toggle the hiding of less important fields"""
        self.unhide = not self.unhide
        self.recurse(self.inarg, self.listview)    
        return True

    def cancel(self):
        """Do nothing"""
        return False

    def execute(self):
        """Execute the relevant function"""
        return True

    def saveAs(self):
        """Save the (edited) inarg record for later use"""
        return True

    def save(self):
        """Save the (edited) inarg record for later use"""
        return True

    def restore(self):
        """Read in a stored inarg record"""
        return True

    #-------------------------------------------------------------------------------

    def input (self, inarg=None, name=None):
        """Input of a new (inarg) record in the gui"""
        if not isinstance(inarg, dict): return False
        self.clear()
        self.inarg = inarg                                    # to be edited
        self.inarg_input = inarg                              # unchanged

        # Modify the name (of its main window):
        if not name:
            if self.inarg.has_key('script_name'):             # MG_JEN script
                name = self.inarg['script_name']
            else:
                name = self.inarg.keys()[0]
        self.setCaption(name)

        # Transfer the inarg fields recursively:
        self.recurse (self.inarg, listview=self.listview)

        # Connect signals and slots, once a signal is detected the according slot is executed
        QObject.connect(self.listview, SIGNAL("doubleClicked (QListViewItem * )"), self.itemSelected)
        self.show()
        return True


    def recurse (self, rr=None, listview=None, level=0):
        """Recursive input of a hierarchical inarg record"""
        if not isinstance(rr, dict): return False

        # Every level of a hierarchial inarg record may have a CTRL_record:
        ctrl = None
        if rr.has_key(CTRL_record):                            # has a CTRL record
            ctrl = rr[CTRL_record]                             # use it

        for key in rr.keys():
            if isinstance(rr[key], dict):   
                if key==CTRL_record:                           # is a CTRL record         
                    itd = self.make_itd(key, rr[key], hide=False)    
                    if not itd['hide']:
                        item = QListViewItem(listview, ' ', key, 'CTRL_record')
                        self.items.append(item)        
                        self.recurse (rr[key], listview=item, level=level+1)
                else:
                    itd = self.make_itd(key, rr[key], ctrl=ctrl)    
                    if not itd['hide']:
                        item = QListViewItem(listview, ' ', key)
                        # item.setColor(itd['color'])          # <-----??            
                        self.items.append(item)        
                        self.recurse (rr[key], listview=item, level=level+1)

            else:                                              # rr[key] is a value
                itd = self.make_itd(key, rr[key], ctrl=ctrl)
                if not itd['hide']:
                    item = QListViewItem(listview, str(itd['ident']), key, str(rr[key]),
                                         itd['help'], itd['type'])
                    # item.setColor(itd['color'])              # <-----??            
                    self.items.append(item)

        return True

    #-------------------------------------------------------------------------------

    def make_itd(self, key, value, ctrl=None, color='black', hide=False, save=True, trace=True):
        """Make an itd record from the given value and ctrl-record"""
        rr = dict(key=str(key),
                  value=value,                
                  type=str(type(value)),
                  color=color,                 
                  hide=hide,
                  # help=None,
                  help='help-string',
                  # range=None,
                  range=[-1,1],
                  # choice=None,
                  choice=range(4),
                  choiceonly=False,
                  ident=-1)

        # If ctrl is a record, use its information:
        if isinstance(ctrl, dict):
            # First some overall fields:
            overall = ['color']
            for field in overall:
                if ctrl.has_key(field):
                    rr[field] = ctrl[field]
            # Then the key-specific keys (see JEM_inarg.define()):
            key_specific = ['hide','choice','help','range','choiceonly']
            for field in key_specific:
                if ctrl.has_key(field):
                    if ctrl[field].has_key(key):
                        rr[field] = ctrl[field][key]

        # Override some fields, if required:
        if self.unhide:
            rr['hide'] = False

        # Keep the itemdict for later reference:
        if save:
            rr['ident'] = len(self.itemdict)
            self.itemdict.append(rr)
        if trace:
            print rr
        return rr

    #-------------------------------------------------------------------------------

    def itemSelected(self, item):
        """Deal with a selected (double-clicked) listview item"""
        
        # Read the (string) values from the columns:
        ident = item.text(0)                   # string in 1st column 
        key = item.text(1)                     # etc 
        vstring = item.text(2)           
        help = item.text(3)              
        vtype = item.text(4)         
        if self.popup:
            self.popup.close()

        if True:
            ident = str(ident)
            print 'ident =',ident, (ident==' '), ' type =',type(ident)
            if ident==' ': ident = '0'
            ident = int(ident)
            if ident==0: return False          # not editable
            itd = self.itemdict[ident]
        else:
            # Place-holder: make a dummy itd record.
            # We need to use the corresponding self.itemdict item here...
            itd = self.make_itd(key, item.text(1), save=False)    
            itd['type'] = item.text(3)         # override

        # Make the popup object:
        self.popup = Popup(self, name=itd['key'], itd=itd)
        return True




#----------------------------------------------------------------------------
# Popup for interaction with an argument value:
#----------------------------------------------------------------------------
        
class Popup(QDialog):
    def __init__(self, parent=None, name='popup_name', itd=None):
        QDialog.__init__(self, parent, "Test", 0, 0)

        self.v = QVBoxLayout(self,10,5)

        # print '\n** itd: ',itd,'\n'
        
        self.edit = {} 

        # The key field (not editable)
        field = 'key'
        self.edit[field]=QLineEdit(self)
        self.edit[field].setText('key: '+str(itd['key']))
        self.v.addWidget(self.edit[field])

        # The value field (string!):
        field = 'value'
        self.edit[field]=QLineEdit(self)
        self.edit[field].setText(str(itd['value']))
        self.v.addWidget(self.edit[field])

        # Other information fields (not editable):
        fields = ['type','choice','range','help']
        for field in fields:
            if itd.has_key(field) and itd[field]:
                self.edit[field] = QLineEdit(self)
                self.edit[field].setText(field+': '+str(itd[field]))
                self.v.addWidget(self.edit[field])

        # QObject.connect(self.popup, SIGNAL("doubleClicked (QListViewItem * )"), self.function)
        self.show()
        return None

#============================================================================
# Main etc:
#============================================================================


if __name__=="__main__":
    from Timba.Trees import JEN_inarg
    # from Timba.Trees import JEN_record

    app = QApplication(sys.argv)
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

    igui.show()
    app.connect(app, SIGNAL("lastWindowClosed()"),
                app, SLOT("quit()"))
    app.exec_loop()


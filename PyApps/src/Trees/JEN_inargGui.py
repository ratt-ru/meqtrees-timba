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
        apply(QMainWindow.__init__, (self,) + args)
        self.popup=None
        self.listview=QListView(self)
        self.setCentralWidget(self.listview)
        #listview is the root object
        self.listview.addColumn("name")
        self.listview.addColumn("value")
        self.listview.addColumn("type")
        self.listview.setRootIsDecorated(1)
        self.items=[]
        self.itemdict={}
        # self.test()
        return None

    def input (self, rr=None, name=None, listview=None, level=0):
        """Recursive input of a (inarg) record"""
        if not isinstance(rr, dict): return False

        # Top level actions:
        if level==0:
            # Use the internal listview (name?)
            if listview==None: listview = self.listview

        for key in rr.keys():
            v = rr[key]
            vtype = str(type(v))
            # self.itemdict[name]={'value':i}
            if isinstance(v, dict):
                item = QListViewItem(listview, str(key), ' ', vtype)
                self.items.append(item)
                self.input (v, listview=item, level=level+1)
            else:
                if isinstance(v, (list, tuple)):
                    if len(v)>1:
                        vtype += '['+str(len(v))+']'
                item = QListViewItem(listview, str(key), str(v), vtype)

        # Top level actions:
        if level==0:
            # Connect signals and slots, once a signal is detected the according slot is executed
            QObject.connect(listview, SIGNAL("doubleClicked (QListViewItem * )"), self.itemSelected)
            self.show()
        return True


    def itemSelected(self,item):
        name = item.text(0)
        valuestr = item.text(1)
        vtype = item.text(2)
        if self.popup:
            self.popup.close()
        self.popup=Popup(self,name,valuestr,vtype)



    #----------------------------------------------------------------------------------------------

    def test (self):
        """append some items to the listview, the values are always strings"""
        for i in range(10):
            name="nm"+str(i)
            self.itemdict[name]={'value':i}
            self.items.append(QListViewItem( self.listview, str(name), str(i)))
            last=len(self.items)-1
            element=self.items[last]
            for j in range(i):
                #listviewitems can have listviewitems as parents
                name="nm%d"%(i*10+j,)
                self.itemdict[name]={'value':i*10+j}
                self.items.append(QListViewItem( element, "%s"%(name,), "%d"%(i*10+j,) ))
        # Connect signals and slots, once a signal is detected the according slot is executed
        QObject.connect(self.listview,SIGNAL("doubleClicked (QListViewItem * )"),self.itemSelected)
        self.show()





#----------------------------------------------------------------------------
# Popup for interaction with an argument value:
#----------------------------------------------------------------------------
        
class Popup(QDialog):
    def __init__(self, parent, name, value, vtype=None):
        QDialog.__init__(self,parent,"Test",0,0)
        self.v = QVBoxLayout(self,10,5)

        # The name field (not editable)
        self.nameEdit=QLineEdit(self)
        self.nameEdit.setText(name)
        self.v.addWidget(self.nameEdit)

        # The value field (string!):
        self.valueEdit=QLineEdit(self)
        self.valueEdit.setText(value)
        self.v.addWidget(self.valueEdit)

        if vtype:
            # The type field (not editable):
            self.typeEdit=QLineEdit(self)
            self.typeEdit.setText(vtype)
            self.v.addWidget(self.typeEdit)

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
        inarg = JEN_inarg.test1(_getdefaults=True, _qual=qual, trace=True)
        igui.input(inarg)
        JEN_inarg.display(inarg, 'defaults', full=True)

    if 1:
        # Make a separate gui for the result:
        result = JEN_inarg.test1(_inarg=inarg, _qual=qual, bb='override', qq='ignored', nested=False)
        rgui = ArgBrowser()
        rgui.input(result)
        rgui.show()

    igui.show()
    app.connect(app, SIGNAL("lastWindowClosed()"),
                app, SLOT("quit()"))
    app.exec_loop()


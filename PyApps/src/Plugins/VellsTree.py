#!/usr/bin/python
import sys
from qt import *

# some simple classes to create a tree-like structure for viewing and 
# selecting Vells data elements

class VellsElement( QListViewItem ) :
  """ inherits from QListViewItem so that we can store and return keys """
  def __init__( self, parent=None, after=None):
    if after is None:
      QListViewItem.__init__( self, parent)
    else:
      QListViewItem.__init__( self, parent, after )
    self.key = None

  def setKey(self, key):
    """ define a key associated with the QListViewItem """
    self.key = key

  def getKey(self):
    """ return the key associated with the QListViewItem """
    return self.key

class VellsView( QListView) :
  """ inherits from QListView so that we can get keys from VellsElements """
  def __init__( self, parent=None, name=None):
    QListView.__init__( self, parent, name )
    self.connect( self, SIGNAL("clicked(QListViewItem *)"),
                      self.slotFolderSelected )
    self.connect( self, SIGNAL("returnPressed(QListViewItem *)"),
                      self.slotFolderSelected )

  # get and return the key associated with the element we just clicked
  def slotFolderSelected(self,i):
    try:
      result = i.getKey()
      if not result is None:
        self.emit(PYSIGNAL("selected_vells_id"),(result,))
    except:
      pass

def main(args):
  app = QApplication(args)

  m_treeView =  VellsView()
  m_treeView.addColumn("VellsTree")
  m_treeView.setRootIsDecorated( True );
  root = VellsElement( m_treeView, "root" )
  a = VellsElement( root );
  a.setText(0,"A")
  a.setKey("Duck")
  b = VellsElement( root, a)
  b.setText(0,"B")
  b.setKey("Pig")
  c = VellsElement( root, b)
  c.setText(0,"C")
  c.setKey("Ape")
  temp = VellsElement(a);
  temp.setText(0,"foo")
  temp.setKey("Chicken")

  app.setMainWidget( m_treeView)
  m_treeView.show()
  app.exec_loop()

# Admire
if __name__ == '__main__':
    main(sys.argv)


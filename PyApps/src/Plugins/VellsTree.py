#!/usr/bin/python

#
# Copyright (C) 2002-2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

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

    self.addColumn("VellsSelector")
    self.setSorting(-1)
    self.setRootIsDecorated( True );

  # get and return the key associated with the element we just clicked
  def slotFolderSelected(self,i):
    try:
      result = i.getKey()
      if not result is None:
#       print result
        self.emit(PYSIGNAL("selected_vells_id"),(result,))
    except:
      pass

def main(args):
  app = QApplication(args)

  m_treeView =  VellsView()
  root = VellsElement( m_treeView, "result" )
  a = VellsElement( root );
  a.setText(0,"beginning")
  b = VellsElement( root, a)
  b.setText(0,"item 0")
  b.setKey("Pig")
  e = VellsElement(root, b);
  e.setText(0,"item 5")
  e.setKey("Chicken")
  c = VellsElement( root, e)
  c.setText(0,"item 10")
  c.setKey("Ape")
  d = VellsElement(a);
  d.setText(0,"item one")
  d.setKey("Donkey")

  app.setMainWidget( m_treeView)
  rect = QApplication.desktop().geometry();
  m_treeView.move(rect.center() - m_treeView.rect().center())
  m_treeView.show()
  app.exec_loop()

# Admire
if __name__ == '__main__':
    main(sys.argv)


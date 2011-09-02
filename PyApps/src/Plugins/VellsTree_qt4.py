#!/usr/bin/python
# -*- coding: utf-8 -*-

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

from PyQt4 import Qt

# some simple classes to create a tree-like structure for viewing and 
# selecting Vells data elements

#===========================================================================

class VellsElement( Qt.QTreeWidgetItem ) :
  """
  Inherits from QTreeWidgetItem so that we can store and return keys
  """
  def __init__( self, parent=None, after=None):
    if after is None:
      Qt.QTreeWidgetItem.__init__( self, parent)
    else:
      Qt.QTreeWidgetItem.__init__( self, parent, [after] )    # ....?
    self.key = None

  def setKey(self, key):
    """
    define a key associated with the QTreeWidgetItem
    """
    self.key = key

  def getKey(self):
    """
    return the key associated with the QTreeWidgetItem
    """
    return self.key


class VellsView(Qt.QTreeWidget) :
  """
  inherits from QListView so that we can get keys from VellsElements
  """
  def __init__( self, parent=None, name=None):
    Qt.QTreeWidget.__init__( self, parent)
    self.connect( self,
                  Qt.SIGNAL('itemClicked(QTreeWidgetItem*, int)'),
                  self.slotVellSelected )

#   self.setWindowTitle("Element Selector")
    labels = Qt.QStringList()
    labels << self.tr("Element selector")
    self.setHeaderLabels(labels)
    self.header().hide();

    # self.setSorting(-1)
    # self.setRootIsDecorated( True );

  # get and return the key associated with the element we just clicked
  def slotVellSelected(self,i):
    try:
      result = i.getKey()
      if not result is None:
        self.emit(Qt.SIGNAL("selected_vells_id"),result)
    except:
      pass

def main(args):
  app = Qt.QApplication(args)
  m_treeView =  VellsView()
  root = VellsElement( m_treeView, "result" )
  a = VellsElement( root , 'root');
  a.setText(0,"beginning")
  b = VellsElement( root, 'beginning')
  b.setText(0,"item 0")
  b.setKey("Pig")
  e = VellsElement(root, 'pig');
  e.setText(0,"item 5")
  e.setKey("Chicken")
  c = VellsElement( root, 'chicken')
  c.setText(0,"item 10")
  c.setKey("Ape")
  d = VellsElement(a, 'donkey');
  d.setText(0,"item one")
  d.setKey("Donkey")

  rect = Qt.QApplication.desktop().geometry();
  m_treeView.move(rect.center() - m_treeView.rect().center())
  m_treeView.show()
  app.exec_()

# Admire
if __name__ == '__main__':
    main(sys.argv)


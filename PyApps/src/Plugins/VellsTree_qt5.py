#!/usr/bin/env python3
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
#
#  (c) 2013.				 (c) 2011.
#  National Research Council		 Conseil national de recherches
#  Ottawa, Canada, K1A 0R6 		 Ottawa, Canada, K1A 0R6
#
#  This software is free software;	 Ce logiciel est libre, vous
#  you can redistribute it and/or	 pouvez le redistribuer et/ou le
#  modify it under the terms of	         modifier selon les termes de la
#  the GNU General Public License	 Licence Publique Generale GNU
#  as published by the Free		 publiee par la Free Software
#  Software Foundation; either	 	 Foundation (version 3 ou bien
#  version 2 of the License, or	 	 toute autre version ulterieure
#  (at your option) any later	 	 choisie par vous).
#  version.
#
#  This software is distributed in	 Ce logiciel est distribue car
#  the hope that it will be		 potentiellement utile, mais
#  useful, but WITHOUT ANY		 SANS AUCUNE GARANTIE, ni
#  WARRANTY; without even the	 	 explicite ni implicite, y
#  implied warranty of			 compris les garanties de
#  MERCHANTABILITY or FITNESS FOR	 commercialisation ou
#  A PARTICULAR PURPOSE.  See the	 d'adaptation dans un but
#  GNU General Public License for	 specifique. Reportez-vous a la
#  more details.			 Licence Publique Generale GNU
#  					 pour plus de details.
#
#  You should have received a copy	 Vous devez avoir recu une copie
#  of the GNU General Public		 de la Licence Publique Generale
#  License along with this		 GNU en meme temps que ce
#  software; if not, contact the	 logiciel ; si ce n'est pas le
#  Free Software Foundation, Inc.	 cas, communiquez avec la Free
#  at http://www.fsf.org.		 Software Foundation, Inc. au
#						 http://www.fsf.org.
#
#  email:				 courriel:
#  business@hia-iha.nrc-cnrc.gc.ca	 business@hia-iha.nrc-cnrc.gc.ca
#
#  National Research Council		 Conseil national de recherches
#      Canada				    Canada
#  Herzberg Institute of Astrophysics	 Institut Herzberg d'astrophysique
#  5071 West Saanich Rd.		 5071 West Saanich Rd.
#  Victoria BC V9E 2E7			 Victoria BC V9E 2E7
#  CANADA					 CANADA
#
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from qwt.qt.QtGui import QTreeWidget, QTreeWidgetItem, QApplication, QWidget
from qwt.qt.QtCore import Qt, QObject, pyqtSignal


# some simple classes to create a tree-like structure for viewing and 
# selecting Vells data elements

#===========================================================================

class VellsElement( QTreeWidgetItem ) :
  """
  Inherits from QTreeWidgetItem so that we can store and return keys
  """
  def __init__( self, parent=None, after=None):
    if after is None:
      QTreeWidgetItem.__init__( self, parent)
    else:
      QTreeWidgetItem.__init__( self, parent, [after] )    # ....?
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


class VellsView(QTreeWidget) :
  """
  inherits from QListView so that we can get keys from VellsElements
  """
  selected_vells_id = pyqtSignal()

  def __init__( self, parent=None, name=None):
    QTreeWidget.__init__( self, parent)
    self.itemClicked[QTreeWidgetItem, int].connect(self.slotVellSelected)

    self.header().hide();

    # self.setSorting(-1)
    # self.setRootIsDecorated( True );

  # get and return the key associated with the element we just clicked
  def slotVellSelected(self,i):
    try:
      result = i.getKey()
      if not result is None:
        self.selected_vells_id.emit(result)
    except:
      pass

def main(args):
  app = QApplication(args)
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

  rect = QApplication.desktop().geometry();
  m_treeView.move(rect.center() - m_treeView.rect().center())
  m_treeView.show()
  app.exec_()

# Admire
if __name__ == '__main__':
    main(sys.argv)


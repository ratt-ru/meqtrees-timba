# file: ../Grunt/ObjectHistory.py

# History:
# - 31mar2007: creation
# - 08jun2007: remove Meow.QualScope
# - 18jun2007: remove argument ns= from .append() etc

# Description:

# The ObjectHistory class is used to trace the history of (TDL) objects.
# This allows for easier debugging of complex TDL trees.


#======================================================================================

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

from copy import deepcopy

Settings.forest_state.cache_policy = 100


        
#======================================================================================

class ObjectHistory (object):
    """The ObjectHistory class just collects one-line messages"""

    def __init__(self, label='<hist>', parent='<parent>'):

        self._label = str(label)
        self._parent = str(parent)
        self.clear()

        return None

    #-------------------------------------------------------------------

    def clear(self):
        """Clear the object"""
        self._items = []
        self._prefix = []
        self._scope = []
        return True

    def len(self):
        """Return the length of the internal list of items"""
        return len(self._items)

    def label(self):
        """Return its label"""
        return self._label

    def parent(self):
        """Return the name/oneliner of its parent"""
        return self._parent

    def append(self, item, prefix='*'):
        """Append an item (line) to the internal list"""
        self._items.append(item)
        self._prefix.append('  '+str(prefix))
        scope = ''
        # if is_node(item):
        #     scope = str(item.name.split(':'))
        self._scope.append(scope)
        return True

    def subappend(self, item):
        return self.append(item, prefix='   -')

    def subsubappend(self, item):
        return self.append(item, prefix='     .')

    #-------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        ss += '  (len='+str(self.len())+')'
        ss += '  parent='+str(self.parent())
        return ss


    def display(self, full=False, level=0):
        """Print the contents of this object"""
        if level==0: print
        prefix = (level*'   ')
        print prefix+'---- History of object: '+self.parent()
        for k,item in enumerate(self._items):
            prefix1 = prefix + '|' + self._prefix[k]+' '
            postfix = '    (scope='+str(self._scope[k])+')'

            if isinstance(item,str):
                print prefix1+str(item)+postfix

            elif isinstance(item,(list,tuple)):
                print prefix1+str(item)

            elif isinstance(item,dict):
                if full:
                    for key in item.keys():
                        print prefix1+str(key)+' = '+str(item[key])
                else:
                    print prefix1+str(item)

            elif isinstance(item, ObjectHistory):
                if full:
                    item.display(full=full, level=level+1)
                else:
                    print prefix1+item.oneliner()
            else:
                print prefix1+'(?)'+str(item)+postfix

        # print prefix+'----'
        if level==0: print '\n\n'
        return True 

    #-----------------------------------------------------------------

    def test(self):
        self.append('first')
        self.subappend(range(3))
        self.subsubappend(range(2))
        self.append('second','(!)')
        self.subappend(dict(a=1,b=2,c=3))
        self.append('third')
        return True

#=======================================================================
# Test program (standalone):
#=======================================================================

if __name__ == '__main__':

    hist = ObjectHistory('test')
    hist.test()
    print hist.oneliner()

    if 1:
        hist2 = ObjectHistory('hist2')
        hist2.test()
        if 1:
            hist3 = ObjectHistory('hist3')
            hist3.test()
            hist2.append(hist3)
        hist.append(hist2)

    hist.display(full=True)
    hist.display(full=False)


#=======================================================================
# Remarks:

#=======================================================================

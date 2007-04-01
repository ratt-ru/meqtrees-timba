# file: ../Grunt/ObjectHistory.py

# History:
# - 31mar2007: creation

# Description:

# The ObjectHistory class is used to trace the history of (TDL) objects.
# This allows for easier debugging of complex TDL trees.


#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from copy import deepcopy

Settings.forest_state.cache_policy = 100

# Global counter used to generate unique node-names
# unique = -1

        
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
        self._list = []
        return True


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
        prefix = (level*'  ')
        print prefix+'** History of the object: '+self.parent()
        prefix += ' - '
        for item in self._list:
            if isinstance(item,str):
                print prefix+str(item)
            elif isinstance(item, ObjectHistory):
                if full:
                    item.display(full=full, level=level+1)
                else:
                    print prefix+item.oneliner()
            else:
                print prefix+'(?)'+str(item)
        if level==0: print
        return True 

    def len(self):
        """Return the length of the internal list"""
        return len(self._list)

    def label(self):
        """Return its label"""
        return self._label

    def parent(self):
        """Return the name/oneliner of its parent"""
        return self._parent

    def append(self, item):
        """Append an item (line) to the internal list"""
        self._list.append(item)
        return True

    def test(self):
        self.append('first')
        self.append('second')
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
        hist.append(hist2)

    hist.display(full=True)


#=======================================================================
# Remarks:

#=======================================================================

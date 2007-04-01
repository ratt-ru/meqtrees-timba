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
        self._items = []
        self._prefix = []
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

            if isinstance(item,str):
                print prefix1+str(item)

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
                print prefix1+'(?)'+str(item)

        print prefix+'----'
        if level==0: print
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

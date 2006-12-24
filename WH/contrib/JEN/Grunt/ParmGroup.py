# file: ../Grunt/ParmGroup.py

from Timba.TDL import *
# from copy import deepcopy

class ParmGroup (object):
    """Class that represents a group of MeqParm nodes"""

    def __init__(self, ns, name='jones', tags=[], descr=None):
        self._ns = ns                # node-scope (required)
        self._name = name            # name of the parameter group 
        self._descr = descr          # brief description 
        self._tags = tags            # default node tags
        self._nodelist = []          # initialise
        return None

    def name(self):
        """Return the group name""" 
        return self._name

    def descr(self):
        """Return the group description""" 
        return str(self._descr)

    def tags(self):
        """Return the default node tags""" 
        return self._tags

    def append(self, node):
        """Append the given node to the nodelist"""
        self._nodelist.append(node)
        return len(self._nodelist)

    def nodelist(self, append=None, trace=False):
        """Return the list of nodes. Optionally, append the nodelist(s) of
        one or more other ParmGroup objects to the returned list (e.g. for solving)""" 
        nodelist = []
        nodelist.extend(self._nodelist)           # Do NOT modify self._nodelist!!
        if append:
            if not isinstance(append,(list,tuple)): append = [append]
            for pg in append:
                nodelist.extend(pg.nodelist())
        if trace:
            print '\n** nodelist(append=',append,'):'
            for node in nodelist:
                print '-',node
            print
        return nodelist
        
    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' '+str(self._name)
        ss += ' (n='+str(len(self._nodelist))+')'
        return ss

    def display(self, txt=None):
        """Return a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print '** (txt='+str(txt)+')'
        print '** descr: '+self.descr()
        print '** default node tags: '+str(self.tags())
        print '** nodelist: '
        for node in self._nodelist:
            print '  - '+str(node)
        print ' '
        return True

    #-------------------------------------------------------------------

    def compare(self, pg):
        """Compare with the given ParmGroup object"""
        return True



#===============================================================

if __name__ == '__main__':
    ns = NodeScope()
    pg1 = ParmGroup(ns, 'pg1')
    pg1.append(ns << 1.0)
    pg1.append(ns << 2.0)
    pg1.display()
    if True:
        pg2 = ParmGroup(ns, 'pg2')
        pg2.append(ns << 1.0)
        pg2.append(ns << 2.0)
        pg2.display()
        nn = pg1.nodelist(append=pg2, trace=True)
        pg1.display()
        nn = pg2.nodelist(append=pg1, trace=True)
        pg1.display()
        pg2.display()

#===============================================================
    

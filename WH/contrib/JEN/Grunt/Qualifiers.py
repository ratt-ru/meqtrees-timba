# file: ../Grunt/Qualifiers.py

# History:
# - 31dec2006: creation

# Description:

# The Qualifies class encapsulates a list of nodename qualifiers.


#==========================================================================

from Timba.TDL import *
from Timba.Meq import meq
from copy import deepcopy


#==========================================================================

class Qualifiers (object):
    """Class that represents a list of node-name qualifiers"""

    def __init__(self, quals=[], append=None, prepend=None,
                 simulate=False, include=None, exclude=None):

        # The input may be a value, a list, or another Qualifiers object.
        # print type(quals)
        # print type(self)
        if type(quals)==type(self):
            self._quals = quals.get()
        else:
            self._quals = deepcopy(quals)      
            
        self._input = dict(quals=quals, append=append, prepend=prepend,
                           exclude=exclude, simulate=simulate)
        if not isinstance(self._quals,(list,tuple)):
            self._quals = [self._quals]
        self._quals = self.get(append=append, prepend=prepend, exclude=exclude)
        if simulate:
            self._quals = self.get(append='simul')
        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' quals='+str(self._quals)
        return ss

    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        print ' * input =',self._input 
        print '**\n'
        return True

    #------------------------------------------------------------------------

    def get(self, append=None, prepend=None, exclude=None):
        """Return the current list of qualifiers.
        Optionally, append/prepend/exclude the specified qualifiers."""
        quals = deepcopy(self._quals)  
        if not append==None:
            if not isinstance(append,(list,tuple)):
                if not append in quals: quals.append(append)
            else:
                for s in append:
                    # if not s in quals: quals.append(s)
                    quals.append(s)
        if not prepend==None:
            if not isinstance(prepend,(list,tuple)):
                if not prepend in quals: quals.insert(0,prepend)
            else:
                ss = deepcopy(prepend)
                ss.reverse()
                for s in ss:
                    # if not s in quals: quals.insert(0,s)
                    quals.insert(0,s)
        if not exclude==None:
            if not isinstance(exclude,(list,tuple)):
                if exclude in quals: quals.remove(exclude)
            else:
                for s in exclude:
                    if s in quals: quals.remove(s)
        s1 = '.get(append='+str(append)+' prepend='+str(prepend)+' exclude='+str(exclude)+'):' 
        print s1,'->',quals
        return quals

    #------------------------------------------------------------------------

    def concat (self, append=None, prepend=None, exclude=None):
        """Concatenate the qualifiers into a single string, separated by underscores"""
        quals = self.get (append=append, prepend=prepend, exclude=exclude)
        if len(quals)==0: return ''
        for i in range(len(quals)):
            if i==0: s = str(quals[i])
            if i>0: s += '_'+str(quals[i])
        print '.concat() ->',s
        return s
        

#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':

    q = Qualifiers('rr', simulate=False)
    q.display()

    if 1:
        q.get()
        q.get(append='xx')
        q.get(prepend='xx')
        q.get(exclude='xx')
        q.get(append=['xx','yy'])
        q.get(prepend=['xx','yy'])
        q.get(exclude=['xx','yy'])
        q.get(append='rr')
        q.get(prepend='rr')
        q.get(exclude='rr')
        q.get(append=['rr','xx','yy'])
        q.get(prepend=['rr','xx','yy'])
        q.get(exclude=['rr','xx','yy'])

    if 1:
        q.concat(append=[1,1,3])

    if 1:
        q2 = Qualifiers(q)
        q2.display()

#===============================================================
    

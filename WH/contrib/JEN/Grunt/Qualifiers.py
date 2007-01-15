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

    def __init__(self, quals=[], append=None, prepend=None, exclude=None):

        # The input may be a value, a list, or another Qualifiers object.
        # print type(quals)
        # print type(self)
        if type(quals)==type(self):
            self._quals = quals.get()
        else:
            self._quals = deepcopy(quals)      
            
        self._input = dict(quals=quals, append=append, prepend=prepend,
                           exclude=exclude)
        if not isinstance(self._quals,(list,tuple)):
            self._quals = [self._quals]
        self._quals = self.get(append=append, prepend=prepend, exclude=exclude)
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

    def get(self, append=None, prepend=None, exclude=None, merge=None, trace=False):
        """Return the current list of qualifiers.
        Optionally, append/prepend/exclude some extra qualifiers,
        but do this temporarily, i.e. the internal quals are NOT modified."""
        if trace: s1 = '.get(append='+str(append)+' prepend='+str(prepend)+' exclude='+str(exclude)+'):' 
        quals = deepcopy(self._quals)  
        if append: quals = self.append (append, quals, replace=False, trace=False)
        if prepend: quals = self.prepend (prepend, quals, replace=False, trace=False)
        if exclude: quals = self.exclude (exclude, quals, replace=False, trace=False)
        if merge: quals = self.merge (merge, quals, replace=False, trace=False)
        if trace: print s1,'->',quals
        return quals

    #...................................................................
    
    def merge (self, qual=None, quals=None, replace=True, trace=False):
        """Merge the given qual (item or list) with quals (item or list).
        If quals not given, use the internal self._quals.
        Return the result."""
        if trace: s1 = '** .merge('+str(qual)+','+str(quals)+')('+str(self._quals)+')' 
        if quals==None: quals = self._quals
        if not isinstance(quals,(list,tuple)): quals = [quals]
        if not qual==None:
            if not isinstance(qual,(list,tuple)): qual = [qual]
            for item in qual:
                if not item==None:                           # ignore None 
                    if not item in quals: quals.append(item)    # avoid duplication
        if replace: self._quals = quals                      # replace internal
        if trace: print s1,'->',quals,self._quals
        return quals

    #...................................................................
    # NB: At this moment, merge() and append() are identical
    #     because append() avoids duplication....
    #     This may change in the future....?
    #...................................................................
    
    def append (self, qual=None, quals=None, replace=True, trace=False):
        """Apppend the given qual (item or list) to quals (item or list).
        If quals not given, use the internal self._quals.
        Return the result."""
        if trace: s1 = '** .append('+str(qual)+','+str(quals)+')('+str(self._quals)+')' 
        if quals==None: quals = self._quals
        if not isinstance(quals,(list,tuple)): quals = [quals]
        if not qual==None:
            if not isinstance(qual,(list,tuple)): qual = [qual]
            for item in qual:
                if not item==None:                           # ignore None 
                    if not item in quals: quals.append(item)    # avoid duplication
                # quals.append(item)                          # allow duplication
        if replace: self._quals = quals                      # replace internal
        if trace: print s1,'->',quals,self._quals
        return quals

    #...................................................................

    def prepend (self, qual=None, quals=None, replace=True, trace=False):
        """Prepend the given qual (item or list) to quals (item or list).
        If quals not given, use the internal self._quals.
        Return the result."""
        if trace: s1 = '** .prepend('+str(qual)+','+str(quals)+')('+str(self._quals)+')' 
        if quals==None: quals = self._quals
        if not isinstance(quals,(list,tuple)): quals = [quals]
        if not qual==None:
            if not isinstance(qual,(list,tuple)): qual = [qual]
            ss = deepcopy(qual)
            ss.reverse()
            for item in ss:
                if not item==None:                           # ignore None 
                    if not item in quals: quals.insert(0,item)   # avoid duplication
                # quals.insert(0,item)                         # allow duplication
        if replace: self._quals = quals                      # replace internal
        if trace: print s1,'->',quals,self._quals
        return quals

    #...................................................................

    def exclude (self, qual=None, quals=None, replace=True, trace=False):
        """Remove the given qual (item or list) from quals (item or list).
        If quals not given, use the internal self._quals.
        Return the result."""
        if trace: s1 = '** .exclude('+str(qual)+','+str(quals)+')('+str(self._quals)+')' 
        if quals==None: quals = self._quals
        if not isinstance(quals,(list,tuple)): quals = [quals]
        if not qual==None:
            if not isinstance(qual,(list,tuple)): qual = [qual]
            for item in qual:
                while item in quals: quals.remove(item)
        if replace: self._quals = quals                      # replace internal
        if trace: print s1,'->',quals,self._quals
        return quals



    #------------------------------------------------------------------------
    # Some semi-obsolete functions: 
    #------------------------------------------------------------------------

    def concat (self, append=None, prepend=None, exclude=None, merge=None, trace=False):
        """Concatenate the qualifiers into a single string, separated by underscores"""
        quals = self.get (append=append, prepend=prepend, exclude=exclude, merge=merge)
        if len(quals)==0: return ''
        for i in range(len(quals)):
            if i==0: s = str(quals[i])
            if i>0: s += '_'+str(quals[i])
        if trace: print '.concat() ->',s
        return s

    def merge_old(self, other):
        """Merge its quals with those of the other Qualifiers object.
        Return the result, without modifying the internal quals."""
        quals = self.get()
        if isinstance(other,(list,tuple)):
            oq = other
        elif isinstance(other,type(self)):
            oq = other.get()
        for item in oq:
            if not item in quals:
                quals.append(item)
        return quals
        

#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':

    q = Qualifiers(['rr','xx','zz',6])
    q.display()

    if 0:
        q.get(trace=True)
        quals = []
        qual = 'cc'
        qual = ['cc',7]
        q.append(qual, trace=True)
        q.append(qual, quals, trace=True)
        
        q.prepend(qual, trace=True)
        q.prepend(qual, quals, trace=True)

        qual = 'cc'
        q.exclude(qual, trace=True)
        q.exclude(qual, quals, trace=True)
        q.get(trace=True)

    if 1:
        q.get(trace=True)
        q.get(append='xx', trace=True)
        q.get(prepend='xx', trace=True)
        q.get(exclude='xx', trace=True)
        q.get(append=['xx','yy'], trace=True)
        q.get(prepend=['xx','yy'], trace=True)
        q.get(exclude=['xx','yy'], trace=True)
        q.get(append='rr', trace=True)
        q.get(prepend='rr', trace=True)
        q.get(exclude='rr', trace=True)
        q.get(append=['rr','xx','yy'], trace=True)
        q.get(prepend=['rr','xx','yy'], trace=True)
        q.get(exclude=['rr','xx','yy'], trace=True)
        q.get(trace=True)

    if 0:
        q.concat(append=[1,1,3])

    if 0:
        q2 = Qualifiers(q)
        q2.display()

#===============================================================
    

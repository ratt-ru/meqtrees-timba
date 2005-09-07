# file: .../Timba/PyApps/src/Trees/TDL_common.py
#
# Author: J.E.Noordam
#
# Short description:
#   Contains a common superclass to be inherited by TDL objects
#   Also some other functions of common usefulness... 
#
# History:
#    - 05 sep 2005: creation
#    - 10 sep 2005: more or less stable
#
# Remarks:
#

from Timba.TDL import *
from copy import deepcopy

from Timba import utils
_dbg = utils.verbosity(0, name='tutorial')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                  # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed



#***************************************************************************************
# Super class with common inheritable funtions (also used by Cohset)
#***************************************************************************************

class Super:

    def __init__(self, **pp):

        pp.setdefault('label', '<object label>')
        pp.setdefault('type', '<object type>')
        pp.setdefault('origin', '<origin>')

        self.__label = pp['label']
        self.__type = pp['type']
        self.__origin = pp['origin']
        pp.__delitem__('label')
        pp.__delitem__('type')
        pp.__delitem__('origin')

        # self.clear()
        self.__errors = 0
        self.__warnings = 0

        # Start the object history:
        s = self.__origin+': Created '+self.type()+' object with label: '+self.label()
        self.history(s, reset=True)

        # Deal with the extra constructor arguments (if any):
        self.history('inarg = '+str(pp))
        s = s+' inarg = '+str(pp)
        # print '\n**',s,'\n'

        return None

    def __del__(self):
        # print '** Goodbye',self.type().self.name()
        pass

    def label(self, new=None):
        if isinstance(new, str): self.__label = new
        return self.__label
    def type(self): return self.__type
    def errors(self): return self.__errors
    def warnings(self): return self.__warnings
    def ok(self): return (self.__errors==0 and self.__warnings==0)

    def oneliner(self):
        s = '*'
        s = s+' '+str(self.type())+':'
        s = s+' '+str(self.label())
        if self.ok():
            s = s+' (ok)'
        else:
            s = s+' ** NOT OK!! **'
        return s

    def display(self, txt=None, end=True):
        indent1 = 2*' '
        indent2 = 6*' '
        print '\n**',self.type()+'.display(',txt,'):'
        print indent1,self.oneliner()
        print indent1,'* .ok() ->',self.ok(),': .errors() ->',self.errors(), ' .warnings() ->',self.warnings()
        hh = self.history()
        print indent1,'* Object history (',len(hh),' entries):'
        for i in range(len(hh)): print indent2,'*',i,':',hh[i]
        # print indent1,'*'
        if end: self.display_end()

    def display_end(self):
        print '** end of',self.type()+'.display()\n'


    def copy(self, label=None):
        # Return a (re-labelled) 'deep' copy of this jonesset: 
        new = deepcopy(self)                                    # copy() is not enough...
        if label==None: label = '('+self.label()+')'               # Enclose old label in ()
        new.label(label)                                          # re-label (always)
        self.history(append='copied to '+self.type()+': '+new.label())
        new.history(append='copied from '+self.type()+': '+self.label()+' -> '+new.label(),
                    reset=False, indent=True)
        return new

    # Simple mechanisms for storing the object history, including errors/warnings:

    def history(self, append=None, error=None, warning=None, reset=False, indent=False):
        if reset: self.__history = []
        if indent:
            for i in range(len(self.__history)):
                self.__history[i] = '...'+self.__history[i]      # indent the old stuff
        if not append==None:
            self.__history.append(str(append))
        if not error==None:
            self.__errors += 1
            self.__history.append('** ERROR ** '+str(error))
        if not warning==None:
            self.__warnings += 1
            self.__history.append('** WARNING ** '+str(warning))
        return self.__history


    # Some ideas for functions to be added:

    def save(self, filename=None):
        # Save the object in a file... Not very useful?
        pass

    def clear(self):
        # Called from self.__init__() above. Expected to be overwritten.
        pass


#========================================================================
# Helper routines:
#========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=True):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace: print '** Super: _counters(',key,') =',_counters[key]
    return _counters[key]


# Some 'universal' plot styles:

def plot_color(key=None):
    rr = dict(XX='red', XY='magenta', YX='cyan', YY='blue')
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return style[key]
    return False
    
def plot_style(key=None):
    rr = dict(XX='dot', XY='dot', YX='dot', YY='dot')
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return style[key]
    return False

def plot_size(key=None):
    rr = dict(XX=10, XY=7, YX=7, YY=10)
    rr['RR'] = rr['XX']
    rr['RL'] = rr['XY']
    rr['LR'] = rr['YX']
    rr['LL'] = rr['YY']
    if key==None: return rr
    if rr.has_key(key): return rr[key]
    return False





#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    from numarray import *
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    sup = Super(label='initial', type='Super', origin='TDL_common')
    sup.display('initially')

    if 0:
        print '** dir(sup) ->',dir(sup)
        print '** sup.__doc__ ->',sup.__doc__
        print '** sup.__module__ ->',sup.__module__
        print

    if 0:
        # Inherited functions (from Super):
        print '** sup.history() ->',sup.history()
        sup1 = sup.copy()
        sup1.display('copied')


    if 0:
        # Display the final result:
        # k = 0 ; MG_JEN_exec.display_subtree(sup[k], 'sup['+str(k)+']', full=True, recurse=3)
        sup.display('final result')


#============================================================================================









 

